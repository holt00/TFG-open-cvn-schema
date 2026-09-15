# Issue 94 - ORCID API Client

## Summary

Implement a client for the ORCID Public API (v3.0) for targeted
enrichment/fusion lookups by ORCID iD. First data-source issue of TFM epic
phase 2 (`docs/roadmap/tfm/issues/issue-89-epic-tfm-lakehouse-platform.md`).

## Original Goal

Given an ORCID iD, fetch and return the relevant public record data, to
support both cross-source fusion (issue `#97`) and seeding the synthetic CVN
generator (issue `#96`).

## Original Plan

- register a free ORCID "Public API" client (`client_id`/`client_secret`)
- implement OAuth2 client-credentials token retrieval (`/read-public` scope)
- implement lookup functions against `GET /v3.0/{orcid-id}/record` and, as
  needed, narrower endpoints (`/works`, `/employments`, `/educations`)
- handle the documented fair-use rate limits and structured error responses
- keep this client independent of `src/open_cvn/`; it is a new TFM-only data
  source, not part of the TFG parser contract

## Adjustments Made During Implementation

Not applicable yet; no implementation has started.

## Implementation Performed

Not applicable yet; no implementation has started.

## Verification

Planned: a lookup against a known real ORCID iD returns the expected record
fields; a lookup against an invalid iD returns a structured error, not an
unhandled exception. Not yet executed.

## Findings

Not applicable yet.

## Known Limitations

Not applicable yet.

## Impact On Future Issues

Feeds issue `#97` (bronze landing, enrichment lookups) and issue `#96`
(synthetic CVN generator, real seed fields).

## Status

`Planned`
