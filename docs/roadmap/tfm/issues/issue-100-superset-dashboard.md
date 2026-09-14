# Issue 100 - Superset Dashboard

## Summary

Deploy Apache Superset and build a small dashboard on the gold indicators.
First issue of TFM epic phase 4.

## Original Goal

A live BI dashboard presenting the finalized indicators from issue `#99`.

## Original Plan

- Helm-deploy Superset onto the cluster (issue `#90`)
- connect Superset to PostgreSQL (native connector) and the gold tables
  materialized in issue `#99`; no Trino or Spark Thrift Server, per the
  epic's stack decision
- build 2-3 charts, one per finalized indicator

## Adjustments Made During Implementation

Not applicable yet; no implementation has started.

## Implementation Performed

Not applicable yet; no implementation has started.

## Verification

Planned: each chart renders correctly against the gold tables and updates
after a `transform_publish` DAG run. Not yet executed.

## Findings

Not applicable yet.

## Known Limitations

Not applicable yet. Per the epic's scope cut list, this is the first thing
to drop if the time budget is at risk; the fallback is a static table/chart
pulled from PostgreSQL directly in the memoria instead of a live dashboard.

## Impact On Future Issues

None downstream; this is a leaf deliverable. Feeds the memoria (issue
`#103`) as evidence for the evaluation chapter.

## Status

`Planned`
