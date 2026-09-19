# Ingestion image (issue #97)

Container image for the tasks of the `ingest_validate` Airflow DAG
(`dags/ingest_validate.py`). See
`docs/roadmap/tfm/issues/issue-97-bronze-landing-and-ingest-validate-dag.md`
for the decision record behind it (decisions D1, D2, and D10).

## Why a separate image

The Airflow pods run Python 3.13, and this repository requires Python `>=3.14`,
so `tfm_lakehouse` cannot run inside Airflow's own workers. Every DAG task is
therefore a `KubernetesPodOperator` pod running this image.

## What is in the image, and what is not

- In the image: Python 3.14 and the project's runtime dependencies, installed
  from `uv.lock` (`uv sync --frozen --no-dev --no-install-project`), including
  `boto3` (added in issue `#97` to write to MinIO).
- **Not** in the image: the code (`src/`), the JSON Schema (`schemas/`), and
  the data (`data/`). The DAG mounts them from the repository checkout with
  `hostPath` at `/repo/src` (read-only), `/repo/schemas` (read-only), and
  `/repo/data` (read-write). `schemas/` is needed because
  `validate_open_cvn_json` resolves `schemas/open_cvn.schema.json` relative to
  the repository root. Editing code therefore needs no rebuild.

This only works because k3s is a single node on the same machine as the
repository checkout. See the issue's Known Limitations.

## Build and load into k3s

Run from the repository root. The root `.dockerignore` keeps `data/` (about
46 GB) out of the build context; do not remove it.

```bash
docker build -f infra/ingest/Dockerfile -t tfm-lakehouse/ingest:py3.14 .
docker save tfm-lakehouse/ingest:py3.14 | sudo k3s ctr images import -
sudo k3s ctr images ls | grep ingest
```

The import needs `sudo`, exactly as for the Spark image of issue `#93`. The
image only has to be rebuilt when `pyproject.toml`/`uv.lock` change, not when
the code does. The DAG uses `imagePullPolicy: IfNotPresent`.

## Local smoke test

```bash
docker run --rm -v "$PWD/src:/repo/src:ro" -v "$PWD/schemas:/repo/schemas:ro" \
  tfm-lakehouse/ingest:py3.14 \
  python -c "import tfm_lakehouse.synthetic_cvn, boto3; print('ok')"
```

## Running the DAG (issue #97)

The DAG file is delivered to the `dag-processor` pod's DAGs PVC (not
`scheduler`, which does not mount it) and a new DAG starts paused:

```bash
P=$(kubectl get pod -n tfm-lakehouse -l component=dag-processor -o name | head -1)
kubectl cp dags/ingest_validate.py tfm-lakehouse/${P#pod/}:/opt/airflow/dags/ingest_validate.py -c dag-processor
kubectl exec -n tfm-lakehouse ${P#pod/} -c dag-processor -- airflow dags list-import-errors
kubectl exec -n tfm-lakehouse ${P#pod/} -c dag-processor -- airflow dags unpause ingest_validate
```

Unpausing a cron-scheduled Airflow 3 DAG creates the latest missed run at once
(the `00:00` run of the same day), see `docs/pipeline/known_limitations.md`.

Trigger a run by hand, with the parameters you want (all optional; the defaults
are in the DAG file), and watch it:

```bash
kubectl exec -n tfm-lakehouse ${P#pod/} -c dag-processor -- \
  airflow dags trigger ingest_validate --run-id my-run-1 \
  --conf '{"count": 1000, "bulk_max_records": 20000}'
kubectl exec -n tfm-lakehouse ${P#pod/} -c dag-processor -- \
  airflow tasks states-for-dag-run ingest_validate my-run-1
```

Parameters: `count`, `seed`, `orcid_link_ratio` (synthetic CVN);
`enrichment_sample_size` (ORCID API lookups); `bulk_max_records` (0 lands the
whole ~42 GB subset); `rejection_threshold`; `force_refetch` (extract the ORCID
subset again, about 81 minutes); `force_bulk_landing`. Airflow does not accept
the same run id twice, but clearing and re-running the tasks of a run replaces
that run's own partitions instead of duplicating them.

Each task is a pod in `tfm-lakehouse` running one
`python -m tfm_lakehouse.bronze.tasks <command>` and printing a `TASK_SUMMARY`
line; the tasks can also be run from the host with the same command, pointing
`BRONZE_S3_ENDPOINT` at a `kubectl port-forward` of the `minio` Service and
`TFM_DATA_DIR` at the checkout's `data/`.

## Checking what landed

Bronze is `s3://lakehouse/bronze/source=<source>/ingestion_date=<date>/run_id=<id>/`
with `part-NNNNN.jsonl` shards and a `_manifest.json` (the completeness signal).
Rejected records are under `s3://lakehouse/bronze/_rejected/` with the same
layout. Spark readers skip `_`-prefixed paths, so read one source at a time:

```python
spark.read.json("s3a://lakehouse/bronze/source=synthetic_cvn/")
```

Reading all of `bronze/` at once works but collapses `payload` to `string`
(ORCID bulk payloads are XML strings). To remove a run's data, delete the objects
under its `run_id=` prefixes, in `bronze/` and in `bronze/_rejected/`.

Every task fails loudly when its input is missing: the synthetic and API tasks
need the ORCID subset (`data/orcid_bulk/_subset_complete.json`), and the landing
task needs the synthetic and API tasks of the same run
(`data/bronze_runs/<run_id>/`).
