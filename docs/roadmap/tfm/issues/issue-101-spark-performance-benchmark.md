# Issue 101 - Spark Performance Benchmark

## Summary

Measure the effect of Spark executor count on processing runtime at 2-3
synthetic data scales. Second issue of TFM epic phase 4, and the platform's
one bounded performance evaluation, feeding `CP04`.

## Original Goal

Produce a concrete, reproducible performance datapoint for the memoria's
evaluation chapter, without turning into an open-ended scalability study.

## Original Plan

- pick 2-3 synthetic data scales by replicating/augmenting the synthetic
  CVN + ORCID subset volume from issues `#95`/`#96`
- run the bronze-to-silver Spark job (issue `#98`) at each scale, varying
  the executor count
- capture timings from Spark job logs / the Spark History Server, not a
  dedicated observability stack (Prometheus/Grafana explicitly deferred per
  the epic)
- tabulate and chart the results for the memoria

## Adjustments Made During Implementation

Not applicable yet; no implementation has started.

## Implementation Performed

Not applicable yet; no implementation has started.

## Verification

Planned: each benchmark run completes and its timing is recorded; results
are reproducible on a rerun within a reasonable tolerance. Not yet executed.

## Findings

Not applicable yet.

## Known Limitations

Not applicable yet. Per the epic's scope cut list, reduce to a single data
scale first if the time budget is tight, rather than the full 2-3.

## Impact On Future Issues

Feeds the memoria (issue `#103`) as the evaluation chapter's performance
evidence.

## Status

`Planned`
