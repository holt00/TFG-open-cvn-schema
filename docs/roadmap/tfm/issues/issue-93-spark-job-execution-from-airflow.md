# Issue 93 - Spark Job Execution From Airflow

## Summary

Build a Spark image and prove `spark-submit` can be launched from Airflow
against the k3s cluster, reading and writing Iceberg tables through the
catalog from issue `#92`. Second issue of TFM epic phase 1.

## Original Goal

An end-to-end proof that Spark, Iceberg, and Airflow work together on this
cluster, before any real ingestion or transform logic is built on top of it.

## Original Plan

- build a Spark container image with PySpark and the Iceberg/S3A
  dependencies from issue `#92`
- write a minimal Airflow task that runs `spark-submit` in Kubernetes mode
  (no Spark Operator, per the epic's stack decision)
- write a trivial Spark job that writes a test Iceberg table and reads it
  back, to prove the whole chain works

## Adjustments Made During Implementation

Not applicable yet; no implementation has started.

## Implementation Performed

Not applicable yet; no implementation has started.

## Verification

Planned: the test Airflow DAG run completes successfully, and the test
Iceberg table is queryable afterward via Spark SQL. Not yet executed.

## Findings

Not applicable yet.

## Known Limitations

Not applicable yet.

## Impact On Future Issues

Issues `#97` and `#99` (the real ingestion/transform DAGs) build directly on
the Spark-from-Airflow pattern proven here.

## Status

`Planned`
