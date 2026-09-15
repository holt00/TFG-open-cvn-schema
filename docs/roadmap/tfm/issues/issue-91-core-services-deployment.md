# Issue 91 - Core Services Deployment

## Summary

Deploy MinIO, PostgreSQL, and Airflow via Helm onto the k3s cluster from
issue `#90`. Second issue of the TFM epic (`docs/roadmap/tfm/issues/issue-89-epic-tfm-lakehouse-platform.md`,
phase 0).

## Original Goal

Have the three baseline services running and reachable, ready for the
Iceberg/Spark wiring and ingestion work that build on them.

## Original Plan

- Helm-install MinIO; create the working bucket(s) for the lakehouse
  (bronze/silver/gold prefixes or separate buckets, decided here)
- Helm-install PostgreSQL; decide whether Airflow metadata and the later
  materialized gold tables (issue `#99`) share one instance/different
  schemas or use separate instances
- Helm-install Airflow with `KubernetesExecutor`, pointed at this cluster
- record the Helm values used for each, under `infra/` (per the epic's
  proposed repository layout)

## Adjustments Made During Implementation

Not applicable yet; no implementation has started.

## Implementation Performed

Not applicable yet; no implementation has started.

## Verification

Planned: MinIO console/API reachable and a test object can be written and
read; PostgreSQL accepts a connection; Airflow UI is reachable and the
scheduler reports healthy. Not yet executed.

## Findings

Not applicable yet.

## Known Limitations

Not applicable yet.

## Impact On Future Issues

Issue `#92` (Iceberg Catalog On MinIO) needs the MinIO bucket created here.
Issues `#97` and `#99` (the DAGs) need Airflow. Issue `#100` (Superset) and
issue `#99` (gold materialization) need PostgreSQL.

## Status

`Planned`
