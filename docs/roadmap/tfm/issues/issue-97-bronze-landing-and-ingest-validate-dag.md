# Issue 97 - Bronze Landing & `ingest_validate` DAG

## Summary

Wire issues `#94`, `#95`, and `#96` together into one Airflow DAG that lands
both data sources into MinIO bronze with provenance metadata and a
landing-time structural check. Closing issue of TFM epic phase 2.

## Original Goal

One working, scheduled ingestion pipeline covering both CVN and ORCID
sources, ready for the transform stage.

## Original Plan

- build the `ingest_validate` Airflow DAG with tasks
  `fetch_orcid_bulk_subset` (issue `#95`), `fetch_orcid_api_enrichment`
  (issue `#94`), `generate_synthetic_cvn` (issue `#96`), and
  `validate_and_land_bronze`
- land outputs into MinIO bronze, partitioned by source and ingestion date
- attach provenance metadata to every landed record (source, retrieval
  time), extending the same idea as the TFG's `cvn_trace` /
  `x-open-cvn-*` conventions rather than inventing a new provenance model
- implement the landing-time structural check: well-formed/schema-valid for
  CVN (lighter than issue `#98`'s full semantic validation), required-field
  presence for ORCID

## Adjustments Made During Implementation

Not applicable yet; no implementation has started.

## Implementation Performed

Not applicable yet; no implementation has started.

## Verification

Planned: the DAG runs end-to-end on a schedule/manual trigger; bronze
contains both sources landed with provenance metadata attached. Not yet
executed.

## Findings

Not applicable yet.

## Known Limitations

Not applicable yet.

## Impact On Future Issues

Issue `#98` (Bronze -> Silver) consumes this DAG's bronze output.

## Status

`Planned`
