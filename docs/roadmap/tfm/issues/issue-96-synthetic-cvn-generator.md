# Issue 96 - Synthetic CVN Generator

## Summary

Generate schema-valid Open CVN JSON curricula, seeded with real ORCID
fields. Third data-source issue of TFM epic phase 2.

## Original Goal

Produce a configurable volume of realistic, schema-valid synthetic CVN
documents, without sourcing real personal CVN data (rejected in the epic on
privacy/consent grounds).

## Original Plan

- reuse `schemas/open_cvn.schema.json` as the validation target and the
  small set of `examples/open_cvn/` documents as structural seed templates
  (both TFG artifacts, not rebuilt)
- take real public fields (names, works, affiliations, dates) from issue
  `#94` and/or `#95`'s ORCID data as seed data for each generated curriculum
- generate synthetic Open CVN JSON documents at a configurable volume
- validate every generated document against the schema, reusing
  `src/open_cvn/parser_contract.py`'s `validate_open_cvn_json(...)` rather
  than reimplementing validation

## Adjustments Made During Implementation

Not applicable yet; no implementation has started.

## Implementation Performed

Not applicable yet; no implementation has started.

## Verification

Planned: every generated document passes `validate_open_cvn_json(...)`;
generated documents at a given seed volume vary realistically rather than
being near-duplicates. Not yet executed.

## Findings

Not applicable yet.

## Known Limitations

Not applicable yet. Per the epic, sourcing additional real CVN documents
beyond the existing small TFG example set remains explicitly out of scope.

## Impact On Future Issues

Feeds issue `#97` (bronze landing) as the CVN source, and issue `#101`
(benchmark), which needs a scalable synthetic volume.

## Status

`Planned`
