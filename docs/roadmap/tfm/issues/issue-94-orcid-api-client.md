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

**Registration blocker found (2026-09-18):** the original plan assumed a
free, individually-registrable ORCID Public API client (`client_id` /
`client_secret`, OAuth2 client-credentials, `/read-public` scope). Checking
the actual registration form (`orcid.org` -> Developer Tools -> register a
public API client) showed it asks for the app to be described as a tool
used by a registered ORCID member organization; a personal TFM project does
not fit that description. Cross-referenced ORCID documentation states
individuals can hold Public API credentials independent of membership, so
the eligibility gate may be inconsistently enforced or have tightened since
that documentation was written; either way, the live form blocked
registration at the time of checking, so pursuing it further (or asking the
university to sponsor a Member API key) was judged disproportionate effort
for what this issue needs.

**Decision: use the ORCID Public API's anonymous (unauthenticated) tier
instead of the registered tier.** `GET` requests to
`https://pub.orcid.org/v3.0/{orcid-id}/record` (and the narrower `/works`,
`/employments`, `/educations` endpoints) return public data with no token
and no `client_id`, given only an `Accept: application/json` header. This is
documented ORCID behavior (the token is an optional rate-limit booster, not
an access requirement), and it fully covers this issue's use case: single,
targeted iD lookups for issue `#96` (synthetic CVN seed fields) and issue
`#97` (bronze-layer enrichment), not bulk registry crawling.

Trade-off accepted: the anonymous tier caps at 25k reads/day and 12
requests/second per IP address, versus 100k reads/day per `client_id` on the
registered tier. Acceptable because both consuming issues (`#96`, `#97`) do
low-volume, per-record lookups, not sustained high-throughput polling; issue
`#95` (ORCID bulk data file pipeline) already covers the high-volume,
whole-registry case through the separate annual public data file, which
also requires no key.

Scope impact on the original plan:

- dropped entirely: OAuth2 client-credentials token retrieval, token
  caching/expiry handling, and `client_id`/`client_secret` env-var
  configuration -- none of it is needed for the anonymous tier
- kept: lookup functions against `/record`, `/works`, `/employments`,
  `/educations`; structured error handling instead of raw exceptions;
  independence from `src/open_cvn/`
- added: ORCID iD checksum validation (ISO 7064 MOD 11-2) before making a
  network call, to fail fast on malformed input
- added: bounded retry with backoff on HTTP 429, since there is no
  registered `client_id` to fall back to for a higher quota if the
  anonymous cap is hit
- escape hatch, not scheduled: if TFM throughput ever needs more than 25k
  reads/day, revisit registered Public API client registration (re-check
  the exact form wording, since the org-affiliation gate was only observed,
  not confirmed against ORCID's written policy) or a university-sponsored
  Member API key; out of scope for this issue as currently understood

Revised task breakdown:

1. dependency + package scaffold: add `requests` to `pyproject.toml`;
   new `src/tfm_lakehouse/orcid_client/` package (`client.py`, `models.py`,
   `exceptions.py`), kept separate from `src/open_cvn/` per the original
   plan's independence constraint
2. ORCID iD validation: MOD 11-2 checksum check ahead of any network call
3. record lookup functions: `get_record`, `get_works`, `get_employments`,
   `get_educations` against `pub.orcid.org/v3.0/`, unauthenticated,
   `Accept: application/json`
4. error handling: typed exceptions (e.g. `OrcidNotFoundError`,
   `OrcidApiError`) wrapping non-2xx responses with status + body, instead
   of raw HTTP-library exceptions; bounded retry/backoff on HTTP 429
5. tests: `tests/test_orcid_client.py` with mocked HTTP for unit coverage
   (checksum rejection, 404, 429/backoff, malformed responses), plus one
   optional live smoke test gated behind an `ORCID_LIVE_TEST=1` env var
   against a known public demo iD (`0000-0002-1825-0097`, the "Josiah
   Carberry" ORCID test record), skipped by default so CI does not depend
   on network access
6. documentation: this issue document, `docs/context/tfm/current_status.md`,
   `docs/roadmap/tfm/tfm_roadmap.md` status flip, and a `PROJECT_GUIDE.md`
   entry for the new `src/tfm_lakehouse/orcid_client/` path

## Implementation Performed

- added `requests>=2.32` to `pyproject.toml`'s dependencies
- new package `src/tfm_lakehouse/orcid_client/`:
  - `client.py`: `validate_orcid_id` (ISO 7064 MOD 11-2 checksum) and
    `OrcidClient`, hitting `pub.orcid.org/v3.0/{orcid-id}/{record,works,
    employments,educations}` unauthenticated via a `requests.Session` with
    `Accept: application/json`; bounded retry with `Retry-After`-aware
    backoff on HTTP 429
  - `exceptions.py`: `OrcidError` (base), `OrcidValidationError`,
    `OrcidApiError` (carries `status_code`/`body`), `OrcidNotFoundError`
  - deliberately no `models.py`: methods return the parsed JSON body
    directly rather than a typed wrapper, since no consuming issue (`#96`,
    `#97`) has defined which fields it needs yet -- adding a typed layer
    now would be inventing scope ahead of that
- `tests/test_orcid_client_unit.py`: 12 tests, HTTP mocked via
  `unittest.mock` (no new test dependency) -- checksum accept/reject,
  200/404/500 handling, 429-then-success retry, retry exhaustion, and that
  each of the four methods hits the right path
- `tests/test_orcid_client_live_smoke.py`: one test against the real,
  unauthenticated ORCID API, gated behind `ORCID_LIVE_TEST=1` so CI does
  not depend on network access

## Verification

- `uv run pytest tests/test_orcid_client_unit.py -q` -- 12 passed
- `uv run pytest tests/test_orcid_client_live_smoke.py -q` -- 1 skipped
  (confirms the default/CI path makes no network call)
- `ORCID_LIVE_TEST=1 uv run pytest tests/test_orcid_client_live_smoke.py -q`
  -- 1 passed: a real, credential-less `GET` against
  `pub.orcid.org/v3.0/0000-0002-1825-0097/record` (the public "Josiah
  Carberry" ORCID demo record) returned the expected `orcid-identifier.path`,
  confirming the anonymous-tier pivot actually works end to end, not just
  against mocks

## Findings

ORCID Public API client registration, as currently presented on ORCID's
registration form, appears to require describing the application as a tool
for use by a registered ORCID member organization; a personal academic
project (this TFM) does not fit that description, blocking the
client-credentials path assumed in the original plan. This contradicts
ORCID's own documentation, which states individuals can hold Public API
credentials independent of membership -- the discrepancy was not resolved
further since the anonymous tier makes it moot for this issue's scope.

## Known Limitations

The anonymous ORCID API tier is capped at 25k reads/day and 12 requests/
second per IP address (versus 100k reads/day per `client_id` on the
registered tier). If a later TFM issue needs sustained high-volume ORCID
lookups beyond that cap, registered-client access or a university-sponsored
Member API key will need to be revisited; not required for issues `#94`,
`#96`, or `#97` as currently scoped.

## Impact On Future Issues

Feeds issue `#97` (bronze landing, enrichment lookups) and issue `#96`
(synthetic CVN generator, real seed fields).

## Status

`Completed`
