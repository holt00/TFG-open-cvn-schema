# Issue 99 - Silver -> Gold: Indicators & `transform_publish` DAG

## Summary

Compute the final research indicators and publish them to both Iceberg and
PostgreSQL, and wire the `transform_publish` DAG. Closing issue of TFM epic
phase 3.

## Original Goal

Have gold-layer indicator tables available for BI (issue `#100`) and the
memoria's evaluation chapter, materialized somewhere Superset can query with
no extra query-engine dependency.

## Original Plan

- finalize the exact 2-3 indicators from the epic's candidates (publications
  per researcher per year, co-authorship/collaboration pairs, career
  trajectory/affiliation timeline); per the epic's scope cut list, reduce to
  1 indicator first if the time budget is tight
- implement `src/tfm_lakehouse/spark_jobs/silver_to_gold.py` computing them
  from issue `#98`'s silver tables
- publish gold to Iceberg
- materialize gold to PostgreSQL as the final publish step (so Superset,
  issue `#100`, never needs to query Iceberg/Spark directly)
- build the `transform_publish` Airflow DAG wiring
  `bronze_to_silver` (issue `#98`) -> `silver_to_gold` -> `publish_gold_to_postgres`

## Adjustments Made During Implementation

Not applicable yet; no implementation has started.

## Implementation Performed

Not applicable yet; no implementation has started.

## Verification

Planned: the DAG runs end-to-end; gold tables are populated and match
expected values on a small known synthetic dataset. Not yet executed.

## Findings

Not applicable yet.

## Known Limitations

Not applicable yet.

## Impact On Future Issues

Issue `#100` (Superset Dashboard) queries the PostgreSQL tables materialized
here. Issue `#101` (benchmark) measures this job's (and issue `#98`'s)
runtime.

## Status

`Planned`
