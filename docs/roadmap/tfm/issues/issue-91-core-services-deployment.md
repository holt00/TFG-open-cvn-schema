# Issue 91 - Core Services Deployment

## Summary

Deploy MinIO, PostgreSQL, and Airflow via Helm onto the k3s cluster from
issue `#90`. Second issue of the TFM epic (`docs/roadmap/tfm/issues/issue-89-epic-tfm-lakehouse-platform.md`,
phase 0).

## Original Goal

Have the three baseline services running and reachable, ready for the
Iceberg/Spark wiring and ingestion work that build on them.

## Original Plan

Planned in a dedicated planning session before implementation started,
because the MinIO/Bitnami Helm ecosystem changed materially between the
epic being written and this issue starting (see "Task 0" below). Every
open decision the epic left for this issue (bucket layout, Postgres
instance topology, image sourcing) is locked here in advance, choosing the
safest/easiest-to-implement-and-debug option at each fork rather than the
most feature-complete one, since this is infra plumbing, not the object of
study.

Execution convention for this issue: work proceeds task by task in the
order below; each task is announced with what it and its subtasks cover,
and closed out by naming exactly which files (if any) need a human edit —
the user edits values files/code themselves per session convention, this
assistant edits documentation.

### Task 0 - Decisions Locked (research, no files changed)

Research performed (web search, 2026-09-15) found the MinIO/Bitnami
Helm/image supply chain shifted significantly during 2025-2026:

- `minio/minio` and `minio/mc` were pulled from Docker Hub in October 2025
  (pinned historical tags now fail with an auth-shaped error); MinIO's own
  GitHub repo was archived February 2026 (community edition sunset,
  source-only distribution going forward). Quay.io mirrors
  (`quay.io/minio/minio`, `quay.io/minio/mc`) still work unauthenticated,
  and Bitnami itself recommends `bitnami/minio:2025.4.22`-class tags as a
  replacement.
- Bitnami's free catalog shrank hard end-August/September 2025; all
  pre-cutover images moved to the frozen, unpatched `docker.io/bitnamilegacy`
  registry, which remains public (no login) but receives no further
  updates. The Bitnami Helm charts remain pullable by OCI reference
  (`oci://registry-1.docker.io/bitnamicharts/<chart>`, already the plan per
  issue `#90`'s finding), but the image reference bundled in a given chart
  version can no longer be trusted to still resolve without an explicit
  override.

Locked decisions (safest/easiest, chosen to minimize install/debug
surface for a local single-node k3s cluster, not for production
correctness):

| Decision | Locked choice | Why this over the alternative |
| --- | --- | --- |
| MinIO image source | Bitnami OCI chart, pinned chart version, with `image.registry=docker.io`, `image.repository=bitnamilegacy/minio`, `image.tag=<exact tag, verified pullable at Task 2 start>` | Official `minio/minio` image is gone from Docker Hub; `bitnamilegacy` is the one path found that is public, unauthenticated, and pin-stable (won't move under us mid-issue) |
| PostgreSQL image source | Bitnami OCI chart, pinned chart version, with `image.registry=docker.io`, `image.repository=bitnamilegacy/postgresql`, `image.tag=<exact tag, verified pullable at Task 3 start>` | Same reasoning; `bitnamilegacy` avoids the free-tier "latest tag only" ambiguity found for the current Bitnami Secure Images tier |
| Airflow image source | Official `apache-airflow/airflow` chart defaults, no override, chart version pinned | Unaffected by the Bitnami situation; the default images are the actively maintained ones |
| MinIO bucket layout | One bucket, `lakehouse`, with `bronze/` `silver/` `gold/` prefixes | Matches the Iceberg warehouse path convention needed by issue `#92`; one bucket is less IAM/policy surface than three and just as easy to test |
| PostgreSQL instance topology | **Separate** instances: Airflow keeps the Helm chart's own default embedded metadata Postgres (subchart, zero custom wiring); this issue's own dedicated Bitnami PostgreSQL instance holds only the future gold-layer database (`gold`, for issues `#99`/`#100`) | Wiring Airflow to an external Postgres (`postgresql.enabled: false` + manual `data.metadataConnection` + secret cross-referencing) is extra integration surface with a well-known chart default already doing it reliably; two independent, independently-testable instances fail more legibly than one shared instance with custom wiring |
| Airflow DAG delivery mechanism | `dags.persistence.enabled: true` on `local-path` storage class | No git-sync sidecar container, no external git credential/network dependency to debug; DAG files land by `kubectl cp` into the PVC, trivial to verify. Revisit only if issue `#97`/`#99` find this insufficient |

Files touched: none (decision record only, folded into this section).

### Task 1 - Branch (done)

Branch `issue-91-core-services-deployment` created off `development`.
Files touched: none (git operation only).

### Task 2 - MinIO deployment

- 2.1 pin the Bitnami MinIO chart version and the `bitnamilegacy` image tag
  from Task 0; verify both pull without auth
- 2.2 write `infra/helm-values/minio-values.yaml`: standalone mode (no
  distributed erasure coding — single local node), `persistence.storageClass:
  local-path`, `defaultBuckets: lakehouse` (or a post-install `mc mb` step if
  the chart parameter does not cover prefix creation), root credentials
  referencing a pre-created Kubernetes Secret (not committed)
- 2.3 create the Kubernetes Secret holding MinIO root credentials
  (`kubectl create secret ...`, documented, not committed)
- 2.4 `helm install minio oci://registry-1.docker.io/bitnamicharts/minio
  --version <pin> -f infra/helm-values/minio-values.yaml -n tfm-lakehouse`
- 2.5 verify: console/API reachable via port-forward, a test object can be
  written and read back (`mc` or `aws s3 cp`)

Files to modify (user): `infra/helm-values/minio-values.yaml` (new).

### Task 3 - PostgreSQL deployment (dedicated gold-layer instance)

- 3.1 pin the Bitnami PostgreSQL chart version and the `bitnamilegacy` image
  tag from Task 0; verify both pull without auth
- 3.2 write `infra/helm-values/postgresql-values.yaml`: primary-only (no
  read replica), `persistence.storageClass: local-path`, database name
  `gold`, credentials via a pre-created Kubernetes Secret (not committed)
- 3.3 create the Kubernetes Secret holding PostgreSQL credentials
- 3.4 `helm install postgresql
  oci://registry-1.docker.io/bitnamicharts/postgresql --version <pin>
  -f infra/helm-values/postgresql-values.yaml -n tfm-lakehouse`
- 3.5 verify: `psql`/`pg_isready` connects, `gold` database exists

Files to modify (user): `infra/helm-values/postgresql-values.yaml` (new).

### Task 4 - Airflow deployment

- 4.1 pin the `apache-airflow/airflow` chart version (repo already added in
  issue `#90`)
- 4.2 write `infra/helm-values/airflow-values.yaml`: `executor:
  KubernetesExecutor`; keep the chart's default embedded PostgreSQL subchart
  enabled for Airflow's own metadata DB (Task 0 decision — no external-DB
  wiring); `dags.persistence.enabled: true` on `local-path` (Task 0
  decision); `config.core.load_examples: False`; trimmed resource requests
  sized for a local single-node dev machine
- 4.3 `helm install airflow apache-airflow/airflow --version <pin>
  -f infra/helm-values/airflow-values.yaml -n tfm-lakehouse`
- 4.4 verify: webserver UI reachable via port-forward, scheduler reports
  healthy, `KubernetesExecutor` confirmed by triggering a smoke DAG and
  observing a task pod get spawned

Files to modify (user): `infra/helm-values/airflow-values.yaml` (new).

### Task 5 - Secrets convention and values documentation

- 5.1 write `infra/helm-values/README.md`: purpose of each values file, the
  exact pinned chart/image versions actually used, the `kubectl create
  secret` commands for each service's credentials, and the install/verify
  commands for all three services
- 5.2 update `infra/README.md` and `infra/k3s/README.md` with the final
  pinned versions and working install commands (extending the OCI-pull note
  already recorded there from issue `#90`)

Files to modify (user): `infra/helm-values/README.md` (new); this
assistant updates `infra/README.md` / `infra/k3s/README.md` as part of the
documentation protocol in Task 6, since those are documentation, not
values/code.

### Task 6 - Documentation protocol close-out (this assistant, same session)

- 6.1 this issue document: `Adjustments Made During Implementation`,
  `Implementation Performed`, `Verification`, `Findings`, `Known
  Limitations` (including the MinIO/Bitnami supply-chain finding from Task
  0), `Impact On Future Issues`, `Status` -> `Completed`
- 6.2 `docs/context/tfm/current_status.md`: new entry, same style as issue
  `#90`'s
- 6.3 `docs/pipeline/known_limitations.md`: add an entry if the
  MinIO/Bitnami image-sourcing situation is judged a lasting limitation
  worth tracking there
- 6.4 `docs/roadmap/tfm/tfm_roadmap.md`: issue `#91` status row ->
  `Completed`
- 6.5 `PROJECT_GUIDE.md`: only if the documentation map changed (e.g. the
  new `infra/helm-values/README.md` entry)

Files to modify: this assistant, all of the above.

## Adjustments Made During Implementation

- **MinIO chart has a third, separate image reference not covered by
  `image.*`/`clientImage.*`**: the console/object-browser UI runs as its
  own Deployment with its own `console.image.*` parameter. The first
  install attempt left this on the chart's broken default
  (`docker.io/bitnami/minio-object-browser`), which produced an
  `ImagePullBackOff` on the `minio-console` pod while the main `minio` pod
  came up fine. Found via `kubectl describe pod`, fixed by locating and
  pinning `console.image.*` to `bitnamilegacy/minio-object-browser` the
  same way as the other two MinIO images, then `helm upgrade`. Recorded
  here because it is easy to miss: always grep a chart's full default
  `values.yaml` for every `repository:`/`registry:` occurrence before
  assuming a single `image.*` override covers a Bitnami chart.
- **Chart/image version pins were verified against live registries, not
  assumed from web research**: exact latest chart versions (MinIO chart
  `17.0.21`, PostgreSQL chart `18.11.3`, Airflow chart `1.22.0`) and image
  tags (`bitnamilegacy/minio:2025.7.23-debian-12-r5`,
  `bitnamilegacy/minio-client:2025.7.21-debian-12-r3`,
  `bitnamilegacy/minio-object-browser:2.0.2-debian-12-r4`,
  `bitnamilegacy/postgresql:17.6.0-debian-12-r4`) were determined by
  paginating the Docker Hub API for each repository and picking the
  highest semver tag, then confirmed anonymously pullable via a
  `registry-1.docker.io` bearer-token manifest HEAD check, before writing
  any values file.
- **Airflow 3's scheduler pod does not mount the DAGs persistence volume**:
  only `dag-processor` (and `api-server`) do, a change from the Airflow 2
  architecture assumed when this issue was planned. A smoke-test DAG file
  copied into the scheduler pod's `/opt/airflow/dags/` landed on that
  container's ephemeral filesystem and was invisible to `dag-processor`.
  Fixed by copying into the `dag-processor` pod instead. This matters for
  issue `#97`/`#99`: any DAG delivery mechanism must target
  `dag-processor`, not `scheduler`.
- **Newly parsed DAGs default to `is_paused=True`**: triggering the DAG
  manually did create a `DagRun` in `queued` state, but the scheduler did
  not schedule its task until the DAG was explicitly unpaused
  (`airflow dags unpause <dag_id>`). Issues `#97`/`#99` need to either
  unpause their DAGs as a deploy step or set
  `config.core.dags_are_paused_at_creation: 'False'` in
  `airflow-values.yaml` if fully hands-off triggering is required; neither
  was done here since this issue's own smoke-test DAG was manually driven
  and deleted afterward.
- **`airflow dags list-runs` requires the `dag_id` as a positional
  argument, not `-d <dag_id>`**: minor CLI-syntax adjustment discovered
  while verifying; Airflow 3's CLI differs in places from the Airflow 2
  CLI examples found during initial research (e.g. `webserver` component
  renamed to `api-server`).

## Implementation Performed

All three services deployed into the `tfm-lakehouse` namespace on the k3s
cluster from issue `#90`, following the locked Task 0 decisions exactly
(single `lakehouse` MinIO bucket with bronze/silver/gold prefixes;
dedicated PostgreSQL instance for the future `gold` database, separate
from Airflow's own embedded metadata Postgres; Airflow with
`KubernetesExecutor` and PVC-based DAG delivery). Full commands used are
in `infra/helm-values/README.md`, not duplicated here. Values files:
`infra/helm-values/minio-values.yaml`, `postgresql-values.yaml`,
`airflow-values.yaml`. Credentials created as Kubernetes Secrets
(`minio-root-credentials`, `postgresql-gold-credentials`), not committed.

## Verification

All executed, this session:

- **MinIO**: `minio` and `minio-console` Deployments both `Running`;
  `mc ls local` shows the `lakehouse` bucket; a test object was written to
  `lakehouse/bronze/test.txt`, read back with matching content, and
  removed; console UI returned HTTP 200 via port-forward.
- **PostgreSQL**: `postgresql-0` pod `Running`, PVC bound; connected as
  the `gold` user to the `gold` database via `psql` (`\l` listed all four
  databases, `SELECT current_database(), current_user` confirmed
  `gold`/`gold`).
- **Airflow**: all pods (`api-server`, `dag-processor`, `scheduler`,
  `triggerer`, `statsd`, embedded `postgresql`) `Running`;
  `airflow db check` reported a successful connection; `api-server` UI
  returned HTTP 200 via port-forward. `KubernetesExecutor` confirmed
  end-to-end with a throwaway smoke-test DAG (`issue91_smoke_test`, a
  single `BashOperator`, deleted after the test): copied into
  `dag-processor`'s DAGs PVC, parsed with 0 import errors, triggered,
  unpaused, and observed via `kubectl get events` to be scheduled onto a
  real Kubernetes pod (`issue91-smoke-test-echo-hello-948ah3qf`) that was
  created, ran, and completed; `airflow tasks state` confirmed `success`.

## Findings

- The Bitnami free-catalog changes (documented in "Task 0 - Decisions
  Locked" above) are real and already in effect: chart defaults for both
  MinIO and PostgreSQL point at image tags that print a
  `⚠ SECURITY WARNING: Original containers have been substituted` /
  `Unrecognized images` notice from Helm when overridden this way — this
  is expected and matches the plan, not a misconfiguration.
  `bitnamilegacy` pulled without authentication for every image checked
  during this issue.
  Sources: [Bitnami catalog changes issue #35164](https://github.com/bitnami/charts/issues/35164),
  [Bitnami Deprecation Notice 2025 (chkk.io)](https://www.chkk.io/blog/bitnami-deprecation).
- MinIO's own upstream distribution model changed independently of
  Bitnami: `minio/minio`/`minio/mc` were pulled from Docker Hub in October
  2025 and MinIO's GitHub repo was archived in February 2026 (community
  edition sunset). This confirmed the Task 0 choice to route through
  Bitnami's legacy images rather than upstream MinIO images was necessary,
  not just convenient.
  Source: [MinIO Docker Image Changes (minimus.io)](https://www.minimus.io/post/minio-docker-image-changes-how-to-find-a-secure-minio-alternative).
- The official `apache-airflow/airflow` chart already defaults its
  embedded metadata-Postgres subchart to a `bitnamilegacy/postgresql`
  image pin upstream, independently confirming that path is the
  maintained community workaround, not an issue-specific improvisation.

## Known Limitations

- All Bitnami-sourced images (MinIO, its console, its client, and the
  dedicated PostgreSQL instance) are pinned to the frozen
  `bitnamilegacy` registry and will receive no further security patches.
  Acceptable for a local, non-internet-exposed single-node dev cluster per
  the epic's own scope decision; would need re-evaluation (a paid Bitnami
  Secure Images subscription, a self-built image, or a different
  distribution) before any real deployment.
- Two separate PostgreSQL instances now run in the namespace (Airflow's
  own embedded one, plus this issue's dedicated `gold` instance), roughly
  doubling Postgres resource usage compared to a shared-instance design.
  Deliberate Task 0 tradeoff for lower integration/debugging risk over
  resource efficiency; revisit only if the local machine's resources
  become a constraint.
- DAGs deployed under `#97`/`#99` must target the `dag-processor` pod's
  DAGs PVC mount, not the `scheduler` pod, and must be explicitly
  unpaused (or the chart's `dags_are_paused_at_creation` default changed)
  to run without a manual step. See "Adjustments Made During
  Implementation" above.
- No TLS/ingress was configured for any of the three services; all access
  in this issue was via `kubectl port-forward`, consistent with the
  epic's local-only cluster scope.

The first bullet above (Bitnami/`bitnamilegacy` image pinning) is also
recorded as a standing entry in `docs/pipeline/known_limitations.md`
("Infrastructure Limitations (TFM)"), since it affects any future issue
that touches these images, not just this one.

## Impact On Future Issues

Issue `#92` (Iceberg Catalog On MinIO) can now target the `lakehouse`
bucket's prefixes (`s3a://lakehouse/bronze|silver|gold`) created here.
Issues `#97` and `#99` (the DAGs) can deploy against the running Airflow
instance, but must account for the `dag-processor`-mounts-the-PVC and
DAG-starts-paused findings above. Issue `#99` (gold materialization) and
issue `#100` (Superset) should target the dedicated `postgresql`/`gold`
instance and database created here, not Airflow's own metadata database.

## Status

`Completed`
