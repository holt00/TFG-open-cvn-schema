# Issue 16 - Add Automated Tests For The Generation Pipeline

## Summary

Issue `#16` will expand the current smoke tests into a reproducible test suite
for the structural and semantic generation workflow.

## Corrected Prerequisite Chain

Issue `#16` must test pipeline stages that are already broader than the
original core-only roadmap assumed.

The corrected test scope begins from these implemented upstream realities:

1. auxiliary structural generation targets were added by hotfix `#4`
2. enriched normalization with deterministic auxiliary-reference resolution was
   added by hotfix `#5`
3. issue `#14` and issue `#15` are expected to consume those layers rather than
   rediscover them

## Original Goal

- validate the pipeline end-to-end and protect against regressions

## Original Plan

1. add fixtures from the canonical CVN package
2. test parsing of manual and tree-model inputs
3. test normalization
4. test semantic mapping and overrides
5. test generated module imports
6. add at least one end-to-end generation test
7. cover known mismatches and special cases

<<<<<<< Updated upstream
=======
## Corrected Minimum Coverage Matrix

The corrected test plan must include:

1. generation tests for auxiliary structural targets in addition to the core
   schemas
2. normalization-resolution tests for auxiliary references
3. regression coverage for subtype-backed tables
4. regression coverage for side-package registry references
5. regression coverage for side-package thesaurus and hierarchical references
6. regression coverage for unresolved references
7. regression coverage for technically present but under-traced tables
8. semantic policy tests keyed by normalized reference classifications
9. generator tests proving distinct domain shapes per semantic class
10. end-to-end tests proving semantic generation consumes enriched normalization
    metadata correctly

## Semantic Policy Coverage From Issue `#14`

Issue `#16` must test the semantic policy contract as a first-class pipeline
stage, not only the final generated models.

Required semantic-policy coverage includes:

1. `SemanticPolicyBundle` construction and deterministic lookup behavior
2. override precedence for `code + xml_path`, `code`, `xml_path`,
   `reference_resolution.semantic_kind`, `reference_resolution.serialization_pattern`,
   `manual_type`, wrapper policy, presence/cardinality policy, and defaults
3. same-priority override conflicts producing
   `PolicyConfidence.REQUIRES_REVIEW`
4. base type mapping for `Alphanumeric`, controlled `Alphanumeric`, `Date`,
   `Double`, `Boolean`, `Duration`, missing, and unknown manual types
5. enum eligibility decisions for strict, open, registry, thesaurus,
   hierarchical, subtype-backed, unresolved, and under-traced references
6. wrapper policy decisions for `FlexibleDatesType`, `OfficialIdType`,
   `EntityTypeType`, and `EntityNameType`
7. Spanish-first naming normalization, including ASCII normalization,
   `snake_case`, `PascalCase`, acronym preservation, and deterministic collision
   fallback
8. trace preservation through CVN `code`, `xml_path`,
   `reference_resolution.trace`, and `SemanticDecisionTrace`

The test suite should verify semantic policy outputs before generator tests so
generator failures can be separated from semantic-policy failures.

>>>>>>> Stashed changes
## Minimum Coverage Goals

1. structural parsing smoke tests for generated bindings
2. normalization tests using real XML inputs
3. regression tests for `choice` and recursion-related cases where relevant
4. tests for semantic-class-driven mapping decisions, including enum-vs-open
   treatment where relevant
5. end-to-end generation tests for importable domain outputs

## Known Inputs From Earlier Issues

- issue `#12` already added runner smoke tests
- known XML/XSD mismatches must be asserted as documented behavior rather than
  treated as surprising failures
<<<<<<< Updated upstream
=======
- issue `#13` already preserves the validated normalization baseline:
  - total normalized codes: `1457`
  - manual-only codes: `27`
  - tree-only codes: `1`
  - overlapping codes: `1429`
- issue `#13` already reports auxiliary-resolution mismatches including:
  - unresolved manual reference
  - ambiguous auxiliary resolution
  - missing subtype support
  - under-traced reference table

## Representative Regression Cases Required

The corrected test suite should include explicit coverage for documented cases
such as:

- `CVN_SEX_A` as compact direct table
- `CVN_KNOW_A` as subtype-backed reference family
- `ENTITY@Entity.xsd` as side-package registry reference
- `THESAURUS@thesaurus.xsd` as side-package thesaurus reference
- `UNESCO_CODES` as hierarchical thematic reference
- `CVN_AGENCY_C` as unresolved manual-only reference
- `CVN_INTERVENTION_A` and `CVN_PRUEBA` as under-traced tables

Additional policy-level expectations from issue `#14` are:

- `000.010.000.020` / `Nombre` remains plain text and enum-ineligible
- `CVN_SEX_A` remains strict-enum eligible when table evidence is closed and
  stable
- `CVN_ENTITY_TYPE` remains open or review-required because delegate/open
  behavior prevents blind strict-enum generation
- side-package, hierarchical, subtype-backed, unresolved, and under-traced cases
  remain strict-enum ineligible by default

## CI Impact

- issue `#25` already provides pull-request execution of all tests under
  `tests/`
- new auxiliary-generation, normalization-resolution, semantic-policy, and
  generator tests should therefore remain under `tests/` so CI picks them up
  automatically without workflow changes
>>>>>>> Stashed changes

## Adjustments Made During Implementation

- No implementation has been performed yet.
- Pre-implementation planning is now aligned with the semantic-policy contract
  agreed in issue `#14`.
- The future test scope now separates semantic-policy verification from domain
  generator verification.

## Implementation Performed

- None yet. Issue `#16` remains pending until issue `#14` and issue `#15`
  provide implementation artifacts to test.

## Verification

- No code verification has been run for issue `#16`.
- Future verification must include semantic-policy tests, generator tests, and
  end-to-end tests under `tests/` so CI from issue `#25` runs them.

## Findings

- Semantic-policy behavior needs dedicated unit coverage before generated-model
  assertions, otherwise failures may be misattributed to the generator.
- Representative cases from issue `#14` provide the minimum regression inventory
  for controlled-reference behavior.

## Known Limitations

- The final semantic-policy test commands and fixtures cannot be finalized until
  issue `#14` implementation creates concrete modules and public functions.
- Generator-output tests cannot be finalized until issue `#15` defines concrete
  Python artifact shapes.

## Impact On Future Issues

- Issue `#17` must document how to run semantic-policy tests separately from
  structural, normalization, generator, and end-to-end tests.
- CI workflow from issue `#25` does not need changes if new tests remain under
  `tests/`.

## Status

- Status: pending
