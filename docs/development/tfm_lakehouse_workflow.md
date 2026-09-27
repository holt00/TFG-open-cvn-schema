# TFM Lakehouse Workflow

## Purpose

This document is the contributor-facing entry point for standing up the TFM
lakehouse platform from nothing and running it end to end: cluster bring-up,
core services, the Iceberg/Spark wiring, both DAGs, and the Superset
dashboard. It is the TFM counterpart of `docs/development/regeneration_workflow.md`.

It covers the implemented platform after issues `#90`-`#101` (issue `#102`,
hardening). Every command below is copy-pasteable from the repository root
unless stated otherwise. Commands marked **[sudo]** need root; commands
marked **[manual]** cannot be scripted from inside this document (an
interactive shell restart, a browser step, a multi-hour download).

## Canonical Prerequisites

- WSL2 (Linux) with systemd enabled (`/etc/wsl.conf`: `[boot]` /
  `systemd=true`, then `wsl --shutdown` from Windows and reopen the shell --
  **[manual]**). k3s and every image build below assume this environment;
  see `infra/k3s/README.md` for the exact reasoning.
- Docker (for building the custom images) and `kubectl`/`helm` on `PATH`
  once installed below.
- `uv` for the repository's own Python environment (`docs/development/setup.md`).
- **The checked-out repository path is not portable as shipped.**
  `dags/ingest_validate.py` and `dags/transform_publish.py` both hardcode
  `REPO_ROOT = "/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema"` for their
  hostPath mounts (issue `#97`'s deliberate choice, D2: no image rebuild, no
  `sudo` import, on code edits). **On any other machine or checkout path,
  edit `REPO_ROOT` in both files before delivering them** (Complete
  Workflow, steps 5 and 6) -- a stale path fails every task pod silently
  looking for `/repo/src`, `/repo/data`, etc. This is a real reproducibility
  gap, not yet automated; see Known Limitations To Preserve.

## Environment Setup

Install the repository's own environment (needed for tests and any local
inspection of `src/tfm_lakehouse/`; the cluster-side code runs inside its
own images, not this environment):

```bash
uv sync --group codegen --group testing
uv pip install -e .
```

## Complete Workflow

### 0. k3s cluster bring-up (issue `#90`)

```bash
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="--flannel-backend=host-gw --write-kubeconfig-mode=644" sh -   # [sudo, self-elevating]
mkdir -p ~/.kube
cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
chmod 600 ~/.kube/config
export KUBECONFIG=~/.kube/config   # add to ~/.bashrc to persist across shells
kubectl create namespace tfm-lakehouse
kubectl config set-context --current --namespace=tfm-lakehouse
helm repo add apache-airflow https://airflow.apache.org
helm repo add superset https://apache.github.io/superset
helm repo update
```

`--flannel-backend=host-gw` avoids a known VXLAN/UDP issue under WSL2's
virtualized networking. MinIO/PostgreSQL are **not** `helm repo add`ed --
their chart is pulled by OCI reference below, since `charts.bitnami.com` is
OCI-only. Full detail and verification steps: `infra/k3s/README.md`.

### 1. Core services: MinIO, PostgreSQL, Airflow (issue `#91`)

Credentials as Secrets first, nothing committed:

```bash
kubectl create secret generic minio-root-credentials -n tfm-lakehouse \
  --from-literal=root-user="<choose a username>" \
  --from-literal=root-password="$(openssl rand -base64 24 | tr -d '/+=' | cut -c1-32)"
kubectl create secret generic postgresql-gold-credentials -n tfm-lakehouse \
  --from-literal=postgres-password="$(openssl rand -base64 24 | tr -d '/+=' | cut -c1-32)" \
  --from-literal=password="$(openssl rand -base64 24 | tr -d '/+=' | cut -c1-32)"
```

```bash
helm install minio oci://registry-1.docker.io/bitnamicharts/minio --version 17.0.21 \
  -f infra/helm-values/minio-values.yaml -n tfm-lakehouse
helm install postgresql oci://registry-1.docker.io/bitnamicharts/postgresql --version 18.11.3 \
  -f infra/helm-values/postgresql-values.yaml -n tfm-lakehouse
helm install airflow apache-airflow/airflow --version 1.22.0 \
  -f infra/helm-values/airflow-values.yaml -n tfm-lakehouse
```

Verify (round-trip, port-forward, `airflow db check`) and every pinned
client-image tag: `infra/helm-values/README.md`. Airflow's *own embedded*
metadata PostgreSQL keeps the chart default plaintext `postgres`/`postgres`
-- accepted only because this cluster is never internet-exposed.

### 2. Iceberg catalog config + Spark images (issues `#92`, `#93`, `#98`, `#99`)

Pinned versions: Spark `3.5.9`, `iceberg-spark-runtime-3.5_2.12:1.11.0`,
`hadoop-aws:3.3.4`, `aws-java-sdk-bundle:1.12.262` (full rationale:
`infra/spark-conf/README.md`).

```bash
# from an unpacked spark-3.5.9-bin-hadoop3/ directory
./bin/docker-image-tool.sh -r tfm-lakehouse -t 3.5.9-iceberg1.11.0-base \
  -p kubernetes/dockerfiles/spark/bindings/python/Dockerfile build

# from the repository root
docker build -f infra/spark-conf/Dockerfile -t tfm-lakehouse/spark-py:3.5.9-iceberg1.11.0 .
docker save tfm-lakehouse/spark-py:3.5.9-iceberg1.11.0 | sudo k3s ctr images import -   # [sudo]

docker build -f infra/spark-conf/Dockerfile.silver -t tfm-lakehouse/spark-py:3.5.9-iceberg1.11.0-silver .
docker save tfm-lakehouse/spark-py:3.5.9-iceberg1.11.0-silver | sudo k3s ctr images import -   # [sudo]

docker build -f infra/spark-conf/Dockerfile.gold -t tfm-lakehouse/spark-py:3.5.9-iceberg1.11.0-gold .
docker save tfm-lakehouse/spark-py:3.5.9-iceberg1.11.0-gold | sudo k3s ctr images import -   # [sudo]

kubectl apply -f infra/spark-conf/spark-rbac.yaml
```

`transform_publish` runs all three of its jobs (`bronze_to_silver`,
`silver_to_gold`, `publish_gold_to_postgres`) on the `-gold` image alone
(its own docstring: "One image runs all three"), so only that last image is
actually required going forward; the base and `-silver` images are
intermediate build layers, not separately deployed.

### 3. Ingest image (issue `#97`)

```bash
docker build -f infra/ingest/Dockerfile -t tfm-lakehouse/ingest:py3.14 .
docker save tfm-lakehouse/ingest:py3.14 | sudo k3s ctr images import -   # [sudo]
```

### 4. ORCID bulk raw archive (issue `#95` prerequisite for `ingest_validate`)

`ingest_validate`'s `fetch_orcid_bulk_subset` task extracts its own filtered
subset from a **local** archive on first run (about 81 minutes, then cached
behind a completion marker so later runs skip it) -- it never downloads.
The archive itself is a **[manual]** one-time download, not scripted here,
because it is 46.3 GB and streaming it took an estimated 7 hours in issue
`#95` against a manual download's few minutes on a faster connection:

```bash
mkdir -p data/orcid_bulk/raw
curl -L -o data/orcid_bulk/raw/ORCID_2025_10_summaries.tar.gz \
  https://ndownloader.figshare.com/files/58834837   # [manual, ~46.3 GB]
md5sum data/orcid_bulk/raw/ORCID_2025_10_summaries.tar.gz
# expect 210edf71f4a2bb44dd33aaa3037b3f17 (the task itself verifies this again on extraction)
```

Without this file (and without an already-extracted, complete
`data/orcid_bulk/filtered/`), the task raises
`BronzeSourceNotReadyError: no ORCID subset marker and no archive at ...;
download it first (issue #95)` rather than failing silently or fetching
unexpectedly.

### 5. Deliver and trigger `ingest_validate` (issue `#97`)

```bash
P=$(kubectl get pod -n tfm-lakehouse -l component=dag-processor -o name | head -1)
kubectl cp dags/ingest_validate.py tfm-lakehouse/${P#pod/}:/opt/airflow/dags/ingest_validate.py -c dag-processor
kubectl exec -n tfm-lakehouse ${P#pod/} -c dag-processor -- airflow dags list-import-errors
kubectl exec -n tfm-lakehouse ${P#pod/} -c dag-processor -- airflow dags unpause ingest_validate
```

Unpausing fires the latest missed daily cron run immediately (Airflow 3
with `catchup=False`); harmless here (idempotent per run id), but know it
before unpausing. For a controlled first run instead:

```bash
kubectl exec -n tfm-lakehouse ${P#pod/} -c dag-processor -- \
  airflow dags trigger ingest_validate --run-id my-run-1 \
  --conf '{"count": 1000, "bulk_max_records": 20000}'
kubectl exec -n tfm-lakehouse ${P#pod/} -c dag-processor -- \
  airflow dags state ingest_validate my-run-1
```

Key params (all optional, chosen defaults in the DAG file): `count`
(synthetic CVNs), `seed`, `orcid_link_ratio`, `enrichment_sample_size`,
`bulk_max_records` (0 lands the whole subset), `rejection_threshold`,
`force_refetch`, `force_bulk_landing`.

### 6. Deliver and trigger `transform_publish` (issue `#99`)

Same delivery pattern, `bronze_to_silver >> silver_to_gold >>
publish_gold_to_postgres`, manual trigger only (no schedule):

```bash
P=$(kubectl get pod -n tfm-lakehouse -l component=dag-processor -o name | head -1)
kubectl cp dags/transform_publish.py tfm-lakehouse/${P#pod/}:/opt/airflow/dags/transform_publish.py -c dag-processor
kubectl exec -n tfm-lakehouse ${P#pod/} -c dag-processor -- airflow dags list-import-errors
kubectl exec -n tfm-lakehouse ${P#pod/} -c dag-processor -- airflow dags unpause transform_publish
kubectl exec -n tfm-lakehouse ${P#pod/} -c dag-processor -- \
  airflow dags trigger transform_publish --run-id my-run-1
kubectl exec -n tfm-lakehouse ${P#pod/} -c dag-processor -- \
  airflow dags state transform_publish my-run-1
```

Key params (optional): `executors`/`executor_memory`/`executor_memory_overhead`/
`shuffle_partitions` (`bronze_to_silver`), `rejection_threshold`,
`ground_truth_run_id` (evaluates entity resolution against a synthetic
manifest under `data/bronze_runs/`, empty skips it), `org_threshold`,
`gold_executors`/`gold_executor_memory`/`gold_shuffle_partitions`
(`silver_to_gold`/publish), `max_year`, `max_entities_per_doi`. Expect
roughly 6-10 minutes warm (issue `#98`/`#99`/`#102` observed 220-360s for
`bronze_to_silver`, 70-110s for `silver_to_gold`, 60-80s for the publish).

### 7. Superset dashboard (issue `#100`)

```bash
docker build -f infra/superset/Dockerfile -t tfm-lakehouse/superset:6.1.0-pg infra/superset
docker save tfm-lakehouse/superset:6.1.0-pg | sudo k3s ctr images import -   # [sudo]
```

Secrets, the read-only `superset_ro` role on the `gold` database, install
(`--timeout 15m` is required -- the chart's own PostgreSQL takes about 2
minutes to boot and the default 5-minute Helm timeout marks a healthy
install `failed`), admin creation, and the dashboard-as-code import: see
`infra/superset/README.md` and `infra/helm-values/README.md` for the exact
commands (they read two generated Secrets, not worth retyping here since a
wrong copy-paste would create a different password than the one Superset
actually has).

Access:

```bash
kubectl port-forward -n tfm-lakehouse svc/superset 8088:8088
```

then `http://localhost:8088`, login `admin` / the `superset-secrets`
Secret's `admin-password` key.

### 8. Spark performance benchmark (issue `#101`, optional)

Not reproduced here. See `docs/benchmark/README.md`'s "Reproduce It"
section: an isolated, hours-long campaign (three data scales, Airflow and
Superset scaled to zero replicas first) that never touches the production
tables this workflow just built.

## Workflow Stages

The implemented platform stages are:

1. k3s cluster bring-up (`#90`)
2. core services: MinIO, dedicated PostgreSQL, Airflow (`#91`)
3. Iceberg Hadoop-catalog configuration on MinIO (`#92`)
4. Spark job execution from Airflow, proven end to end (`#93`)
5. ORCID API client, anonymous tier (`#94`)
6. ORCID bulk data file pipeline, country-filtered subset (`#95`)
7. synthetic CVN generator, ORCID-seeded (`#96`)
8. bronze landing and the `ingest_validate` DAG (`#97`)
9. bronze -> silver validation and entity resolution (`#98`)
10. silver -> gold indicators, PostgreSQL publish, `transform_publish` DAG (`#99`)
11. Superset dashboard over the published gold schema (`#100`)
12. Spark performance benchmark, isolated from production (`#101`)
13. hardening: fragility fixes and this document (`#102`)

## Repository Boundaries

- `infra/` holds Kubernetes manifests, Helm values, and Dockerfiles. Do not
  hand-edit a running cluster's config outside these files; a values change
  belongs in `infra/helm-values/*.yaml` and is applied with `helm upgrade`.
- **A `helm upgrade` to any one Airflow component's values rolls every
  Airflow component together** (a shared config-checksum annotation across
  pod templates), not just the one edited -- expect a scheduler/api-server/
  triggerer restart on any `airflow-values.yaml` change, not only on a
  scheduler-specific one.
- `src/tfm_lakehouse/` holds hand-maintained ingestion, transformation, and
  entity-resolution code, shared between the DAGs' task entry points and the
  Spark jobs under `src/tfm_lakehouse/spark_jobs/`.
- `dags/` holds Airflow DAG sources, delivered to the `dag-processor` pod's
  DAGs PVC with `kubectl cp` (issue `#91`'s decision: no `gitSync`), never
  edited in place inside the pod.
- Production Iceberg tables (`lakehouse.silver`, `lakehouse.gold`), the
  PostgreSQL `gold` schema, and the Superset dashboard are what steps 5-7
  above write to. The benchmark (`#101`) and any ad hoc verification should
  use its own isolated namespaces/schemas instead, per that issue's D5.

## Verification Matrix

```bash
uv run pytest -n auto tests
```

This is the default local verification command (the same one the TFG's own
`regeneration_workflow.md` documents) and covers, for the TFM lakehouse
portion: bronze landing and checks, silver validation/resolution/schemas
(including tests that run inside the Spark image, skipped without Docker),
gold indicator computation and the publish job, DAG structure for both
DAGs, the Superset dashboard-export drift guard, and the benchmark's own
unit tests. `tests/spark_image.py` bounds concurrent Spark-in-Docker
containers to four (`SPARK_TEST_SLOTS` to change it).

Live-cluster health, not covered by the test suite, comes from actually
running both DAGs (Complete Workflow, steps 5 and 6) and checking:

```bash
kubectl get pods -n tfm-lakehouse
```

for `CrashLoopBackOff`/`Error`/unexpectedly high `RESTARTS`, and

```bash
kubectl exec -n tfm-lakehouse <a dag-processor pod> -c dag-processor -- \
  airflow dags state <ingest_validate|transform_publish> <run-id>
```

for `success`, not `failed`.

## Known Limitations To Preserve

- `dags/ingest_validate.py` and `dags/transform_publish.py` hardcode
  `REPO_ROOT` to this machine's checkout path; edit both before delivering
  them from a different machine or path (Canonical Prerequisites, above).
- Bitnami-sourced chart images (MinIO, both PostgreSQL instances, Superset's
  subcharts) are pinned to the frozen `bitnamilegacy` registry, receiving no
  further security patches.
- The `ingest_validate`/`transform_publish` DAGs mount code and data from
  the checkout with hostPath -- single-node only, by design (issue `#97`
  D2).
- Superset is deployed from a Helm chart its own maintainers have
  deprecated; the official path is now a `v1alpha1` Kubernetes Operator.
- A scheduler restart can crash-loop permanently on a stale orphaned-task
  row (upstream apache/airflow issue `#67813`, unfixed); recovery is a
  documented operational DB fix, not a code change. See "A Scheduler
  Restart Can Permanently Crash-Loop..." in `known_limitations.md`.
- **On a fresh cluster, if `publish_gold_to_postgres` fails with
  `password authentication failed for user "gold" ... Role "gold" does
  not exist"` even though `bronze_to_silver`/`silver_to_gold` succeeded**:
  the PostgreSQL pod's first boot was interrupted mid-`initdb` (core
  services cold-starting together is enough contention to trigger this)
  and never created the role; it will not self-heal. Confirm with
  `kubectl logs postgresql-0 --previous`, then recover by deleting the
  pod and its PVC (`data-postgresql-0`) to force a clean reinit, and
  re-run the failed DAG.
- At the fixed per-executor memory sizing, 1 executor (and, at larger
  scales, 2) is a deterministic OOM ceiling for the silver job; more
  executors do not reliably reduce runtime on this single-node cluster
  (issue `#101`'s headline finding).

See `docs/pipeline/known_limitations.md` for the authoritative, complete
limitation register (this list is the subset most likely to block a
from-scratch reproduction).
