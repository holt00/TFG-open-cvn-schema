# Spark Performance Benchmark (Issue #101)

How the executor-count benchmark of the TFM lakehouse is run and how to reproduce it. The design
decisions and their reasons are in `docs/roadmap/tfm/issues/issue-101-spark-performance-benchmark.md`
(Task 0, D1-D17); the measured results are in this directory once the campaign has run
(`results.md`, `results.csv`, `results.json`, `benchmark_<job>.png`).

## What Is Measured

The effect of the number of Spark executors on the run time of the three Spark jobs of the
`transform_publish` pipeline, at three data scales:

| job | script | reads | writes |
| --- | --- | --- | --- |
| `silver` | `spark_jobs/bronze_to_silver.py` | the scale's bronze bucket | `lakehouse.bench_silver_<N>x` |
| `gold` | `spark_jobs/silver_to_gold.py` | `lakehouse.bench_silver_<N>x` | `lakehouse.bench_gold_<N>x` |
| `publish` | `spark_jobs/publish_gold_to_postgres.py` | `lakehouse.bench_gold_<N>x` | PostgreSQL schema `bench_<N>x` |

* scales: `1x` = 20,000 ORCID bulk records requested plus 11,000 synthetic CVN documents plus a
  fixed sample of 200 ORCID API records; `2x` and `4x` double and quadruple the first two. The
  sets are nested (the bulk records are the first ones in folder order, the CVNs the first ones of
  a seeded stream).
* executors: 1, 2 and 4, one core each; executor JVM heap 1 GiB, memory overhead 1 GiB for the
  silver job and 512 MiB for the others (as `transform_publish` sizes them), driver 1 GiB.
* nothing of production is touched: no `lakehouse.silver`, `lakehouse.gold`, PostgreSQL schema
  `gold`, `lakehouse` bucket or Superset dashboard is read or written.

## Method

* strong scaling: the data scale is fixed while the executor count varies;
* `spark.scheduler.minRegisteredResourcesRatio=1.0`, so a job never starts on fewer executors than
  requested (Spark's default on Kubernetes is 0.8);
* per (scale, job): one warm-up run (executed, never counted), then three measured runs for every
  executor count in randomized blocks (a seed fixes the order), so a slow drift of the machine is
  not read as an effect of the executor count;
* metric: `app_seconds` of the Spark event log (application start to end), the median of the
  measured runs, with the min-max range; a point whose `(max - min) / median` exceeds 10% is
  flagged; startup (last executor registered), compute (first job start to last job end) and driver
  gaps between jobs are reported separately;
* a run counts only if it succeeded, registered exactly the requested executors, had no failed
  task and left no executor pod behind; the outputs must have identical content digests across
  executor counts (`spark_jobs/table_digest.py`, and a row-hash digest in PostgreSQL for the
  publish);
* derived: speedup `T(1)/T(n)`, efficiency, the Karp-Flatt serial fraction, the size-up exponent
  (log-log slope of time against scale) and the input throughput.

## Reproduce It

Prerequisites: the cluster of issues `#90`-`#93` with the image
`tfm-lakehouse/spark-py:3.5.9-iceberg1.11.0-gold` imported, the ORCID subset in
`data/orcid_bulk/filtered/` (`#95`) and the run `data/bronze_runs/e2e98-big/` (`#98`, only for its
ORCID API sample). All commands run from the repository root.

1. Start the cluster and free the machine for the measurement (Superset and Airflow use several
   GiB and would compete with the executors); write down the replicas to restore them afterwards:

   ```bash
   sudo systemctl start k3s
   kubectl -n tfm-lakehouse scale deploy/superset deploy/airflow-api-server deploy/airflow-dag-processor \
       deploy/airflow-scheduler deploy/airflow-statsd --replicas=0
   kubectl -n tfm-lakehouse scale sts/superset-postgresql sts/superset-redis-master \
       sts/airflow-postgresql sts/airflow-triggerer --replicas=0
   ```

2. Create the event-log bucket once (MinIO keeps its credentials as files inside the pod):

   ```bash
   kubectl -n tfm-lakehouse exec deploy/minio -- sh -c \
     'mc alias set local http://localhost:9000 "$(cat $MINIO_ROOT_USER_FILE)" "$(cat $MINIO_ROOT_PASSWORD_FILE)" >/dev/null;
      mc mb --ignore-existing local/tfm-bench-events; echo -n "" | mc pipe local/tfm-bench-events/logs/.keep'
   ```

3. Land the three scales (about 1 hour; needs the MinIO port-forward and its credentials in the
   environment):

   ```bash
   kubectl -n tfm-lakehouse port-forward svc/minio 19000:9000 &
   export AWS_ACCESS_KEY_ID=$(kubectl -n tfm-lakehouse get secret minio-root-credentials -o jsonpath='{.data.root-user}' | base64 -d)
   export AWS_SECRET_ACCESS_KEY=$(kubectl -n tfm-lakehouse get secret minio-root-credentials -o jsonpath='{.data.root-password}' | base64 -d)
   export BRONZE_S3_ENDPOINT=http://127.0.0.1:19000 TFM_DATA_DIR=$PWD/data
   uv run python -m tfm_lakehouse.benchmark.data 1x 2x 4x
   ```

4. Look at the plan, run a pilot if wanted (run ids from `r901`, never counted), then the campaign
   (108 runs; it resumes if interrupted and stops at the first failed run):

   ```bash
   uv run python -m tfm_lakehouse.benchmark.campaign --dry-run
   uv run python -m tfm_lakehouse.benchmark.campaign --scales 1x --executors 1 4 --repetitions 1 --pilot
   uv run python -m tfm_lakehouse.benchmark.campaign
   ```

   One job on its own: `uv run python -m tfm_lakehouse.benchmark.runner --scale 1x --job silver --executors 2 --sequence 1`.

5. Build the tables and charts from `data/benchmark/runs/*/` (run records, driver logs and Spark
   event logs, all git-ignored):

   ```bash
   uv run python -m tfm_lakehouse.benchmark.report --runs-dir data/benchmark/runs --output-dir docs/benchmark
   ```

6. Clean up: drop the `bench_*` Iceberg namespaces (`mc rm --recursive --force
   local/lakehouse/warehouse/bench_...`), the buckets `tfm-bench-1x`, `-2x`, `-4x` and
   `tfm-bench-events`, the PostgreSQL schemas `bench_<N>x`, and restore the replicas of step 1.

## Code

| module | role |
| --- | --- |
| `src/tfm_lakehouse/benchmark/data.py` | scales and their isolated bronze buckets |
| `src/tfm_lakehouse/benchmark/runner.py` | one job on the cluster: driver pod, waiting, logs, event log, record |
| `src/tfm_lakehouse/benchmark/campaign.py` | the ordered plan and its execution |
| `src/tfm_lakehouse/benchmark/eventlog.py` | Spark event log to run metrics |
| `src/tfm_lakehouse/benchmark/report.py` | statistics, tables and charts |
| `src/tfm_lakehouse/spark_jobs/table_digest.py` | order-independent content digest of Iceberg tables |

Tests: `tests/test_benchmark_unit.py` (no cluster: the cluster is a fake and the event log a trimmed
real one, `tests/fixtures/spark_event_log_sample.jsonl`) and `tests/test_benchmark_digest_spark.py`
(runs in the Spark image, skipped without Docker).

## Limits To State With The Results

* single node: the executors, MinIO, PostgreSQL and k3s share the same 16 CPUs and RAM, and there
  is no network shuffle between machines; the speedup measures parallelism on one machine;
* `Executor CPU Time` in the event log does not include the Python worker processes that parse the
  ORCID XML, so it is not a measure of CPU use of the pipeline;
* the CVN documents seed from the whole ORCID subset while the landed bulk records are the first
  N, so the share of CVN ORCID iDs found in the bulk data (which drives the first entity-resolution
  rule) grows with the scale.
