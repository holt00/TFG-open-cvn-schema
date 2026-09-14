# Issue 98 - Bronze -> Silver: Validation & Entity Resolution

## Summary

Full validation, normalization, and cross-source entity resolution from
bronze to silver. First issue of TFM epic phase 3, and the HA01
("adquisición, fusión y análisis de múltiples fuentes") centerpiece of the
whole platform.

## Original Goal

Produce a clean, validated, deduplicated silver layer from the raw bronze
data landed in issue `#97`.

## Original Plan

- implement `src/tfm_lakehouse/spark_jobs/bronze_to_silver.py`
- CVN-side: full validation reusing `src/open_cvn/parser_contract.py`
  rather than reimplementing it
- ORCID-side: rule-based checks (required fields present, ORCID iD checksum
  valid)
- normalize both sources into a common shape
- implement entity resolution: ORCID-iD-first matching between a CVN record
  and an ORCID record when both declare/carry the same iD; fallback
  normalized name/affiliation matching when no iD match is available
  (deterministic only, no ML-based resolution, per the epic)
- write the resulting silver Iceberg tables through the catalog from issue
  `#92`

## Adjustments Made During Implementation

Not applicable yet; no implementation has started.

## Implementation Performed

Not applicable yet; no implementation has started.

## Verification

Planned: known synthetic CVN/ORCID pairs sharing an ORCID iD resolve to a
single merged entity; pairs without a shared iD but matching name/affiliation
resolve via the fallback rule; unrelated records remain unmerged. Not yet
executed.

## Findings

Not applicable yet.

## Known Limitations

Not applicable yet. Per the epic, ML-based or probabilistic entity
resolution is explicitly out of scope.

## Impact On Future Issues

Issue `#99` (Silver -> Gold) consumes this silver output.

## Status

`Planned`
