# Issue 69 - Explore LLM-Assisted Import From CVN PDFs

## Summary

Issue `#69` explores LLM-assisted import for CVN PDFs that cannot be imported by
the deterministic epic `#41` PDF XML extraction path.

This issue is part of the broader TFG objective but is not required for the epic
`#60` MVP.

## Goal

- evaluate whether an LLM can help convert FECYT-generated PDF CVs into Open CVN
  JSON when deterministic embedded XML extraction is unavailable
- keep privacy, reproducibility, and validation constraints explicit
- avoid silently accepting hallucinated curriculum data

## Non-MVP Status

This issue must not block local storage, JSON export, LaTeX export, or PDF export
from the MVP application. It should start only after the deterministic MVP flow is
usable and documented.

## Planned Scope

- research safe LLM-assisted extraction approaches
- define privacy rules for personal CV data
- define prompt/input boundaries using synthetic or anonymized fixtures
- validate any LLM output through `validate_open_cvn_json(...)`
- preserve confidence and provenance metadata
- compare LLM output with deterministic parser output when embedded XML exists
- document risks and whether this direction is viable for the TFG prototype

## Planned Steps

1. review TFG LLM objective and current parser limitations
2. define data privacy and fixture rules
3. choose whether to use local mock outputs before any external API
4. design an Open CVN JSON extraction prompt or structured-output contract
5. validate generated JSON through existing parser/validator paths
6. add tests around deterministic validation of LLM output fixtures
7. document findings, risks, and follow-up recommendations

## Expected Output

- research note or prototype module if approved
- safe synthetic or anonymized fixtures
- validation-first workflow for LLM-produced Open CVN JSON
- documented recommendation for whether LLM import should continue

## Verification

- LLM-produced or mocked JSON must validate through `validate_open_cvn_json(...)`
- invalid LLM output must fail with structured parser errors
- no personal PDF fixtures are committed without explicit approval

## Impact On Later Issues

- may define a future import assistant workflow
- may confirm that deterministic import remains the only safe MVP path

## Status

- Status: planned
