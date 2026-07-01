# Issue 16 - Add Automated Tests For The Generation Pipeline

## Summary

Issue `#16` expands the current smoke and unit tests into a reproducible test
suite for the full structural, normalization, semantic-policy, domain-generator,
and end-to-end CVN generation workflow.

## Corrected Prerequisite Chain

Issue `#16` starts from completed upstream work, not from the older core-only
roadmap assumption.

Implemented upstream prerequisites are:

1. auxiliary structural generation targets from hotfix `#4`
2. enriched normalization with deterministic auxiliary-reference resolution from
   hotfix `#5`
3. dynamic reference-table enum evidence from hotfix `#7`
4. semantic policy from issue `#14`
5. wrapper type traceability in normalized handoff from hotfix `#8`
6. domain model generator and generated domain artifacts from issue `#15`
7. CI test execution under `tests/` from issue `#25`

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

## Accepted Execution Protocol

The user accepted this execution plan before implementation starts.

At every execution step, the implementer must report:

1. current task number and task name
2. current subtask number and subtask name, when a subtask is being executed
3. short initial summary of what the task or subtask will do
4. short final result for the task or subtask
5. whether the user must modify any file manually
6. next step to follow

File-modification rule:

- documentation changes may be performed when explicitly requested
- code changes should be left for the user unless the user explicitly authorizes
  the agent to edit code
- generated code under `src/generated/` must not be edited manually
- generated domain output under `src/models/cvn/generated/` must be changed only
  by the generator, not by manual edits

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
11. wrapper-handoff tests for hotfix `#8`
12. generated-output importability and determinism tests

## Accepted Execution Plan

### Task `1 / 18` - Register Plan In Issue Documentation

- Task summary:
  - record the accepted issue `#16` execution plan and remove stale conflict
    markers from the issue document
- Files involved:
  - `docs/roadmap/issues/issue-16-generation-pipeline-tests.md`
- Subtask `1.1 / 18`:
  - remove `<<<<<<<`, `=======`, and `>>>>>>>` markers and duplicated sections
- Subtask `1.2 / 18`:
  - preserve the corrected prerequisite chain and minimum coverage matrix
- Subtask `1.3 / 18`:
  - insert the accepted execution protocol and task list
- User manual modifications needed:
  - none expected for this documentation update
- Next step:
  - verify baseline before test implementation

### Task `2 / 18` - Verify Baseline

- Task summary:
  - prove the current repository test suite is stable before adding issue `#16`
    coverage
- Commands:
  - `uv run pytest -n auto tests`
- Subtask `2.1 / 18`:
  - run the full repository test suite with the documented command
- Subtask `2.2 / 18`:
  - record exact failures if the baseline fails
- Subtask `2.3 / 18`:
  - fix or defer baseline failures only after user approval if code changes are
    required
- User manual modifications needed:
  - none unless verification exposes required code changes
- Next step:
  - create reusable canonical pipeline fixtures

### Task `3 / 18` - Create Pipeline Fixtures

- Task summary:
  - define reusable test helpers for canonical package paths, auxiliary bundles,
    normalization runs, and temporary generated output
- Expected test location:
  - `tests/conftest.py` when helpers are shared across multiple files
- Subtask `3.1 / 18`:
  - expose canonical XML and XSD paths under
    `docs/CvnXML_v1.4.3_2.1_17012025/`
- Subtask `3.2 / 18`:
  - expose `ReferenceTables.xml`, `Subtype_Spa.xml`, `Entity.xml`, and
    `Thesaurus.xml` paths
- Subtask `3.3 / 18`:
  - add helper for `build_auxiliary_source_bundle(...)`
- Subtask `3.4 / 18`:
  - add helper for canonical `build_normalization_result(...)` with auxiliary
    sources and optional structural type evidence
- Subtask `3.5 / 18`:
  - add helper for temporary domain-generation output paths
- User manual modifications needed:
  - test helper file should be edited by the user unless explicit code-edit
    approval is given
- Next step:
  - add structural generation tests

### Task `4 / 18` - Add Structural Generation Tests

- Task summary:
  - verify every structural generation target can generate importable Python
    packages
- Expected test location:
  - `tests/test_generation_pipeline_structural.py`
- Subtask `4.1 / 18`:
  - test core targets: `cvn`, `specification_manual`, and `tree_model`
- Subtask `4.2 / 18`:
  - test auxiliary targets: `reference_tables`, `subtypes`, `entity`, and
    `thesaurus`
- Subtask `4.3 / 18`:
  - assert generated output directories contain Python files
- Subtask `4.4 / 18`:
  - assert generated packages import after generation
- Subtask `4.5 / 18`:
  - ensure tests never manually edit `src/generated/`
- User manual modifications needed:
  - test file should be created by the user unless explicit code-edit approval is
    given
- Next step:
  - add real parse smoke tests

### Task `5 / 18` - Add Real Parse Smoke Tests

- Task summary:
  - verify generated bindings can parse real canonical XML inputs or report known
    documented mismatches
- Expected test location:
  - `tests/test_generation_pipeline_parse_smoke.py`
- Subtask `5.1 / 18`:
  - parse `SpecificationManual.xml` successfully
- Subtask `5.2 / 18`:
  - parse `ReferenceTables.xml`, `Subtype_Spa.xml`, `Entity.xml`, and
    `Thesaurus.xml` successfully
- Subtask `5.3 / 18`:
  - assert `CVNTreeModel.xml` behavior as a known XML/XSD mismatch, not an
    unexpected failure
- Subtask `5.4 / 18`:
  - connect expected mismatch text to `docs/pipeline/known_limitations.md`
- User manual modifications needed:
  - test file should be created by the user unless explicit code-edit approval is
    given
- Next step:
  - add normalization integration tests

### Task `6 / 18` - Add Real Normalization Integration Tests

- Task summary:
  - verify canonical normalization outputs remain stable when auxiliary sources
    and structural type evidence are provided
- Expected test location:
  - `tests/test_generation_pipeline_normalization_integration.py`
- Subtask `6.1 / 18`:
  - assert normalized count baseline: total `1457`, manual-only `27`, tree-only
    `1`, overlap `1429`
- Subtask `6.2 / 18`:
  - assert documented mismatch categories remain present
- Subtask `6.3 / 18`:
  - assert `reference_resolution` metadata is attached when auxiliary inputs are
    provided
- Subtask `6.4 / 18`:
  - assert `structural_type_evidence` is attached when `CVN.xsd` and `Common.xsd`
    are provided
- User manual modifications needed:
  - test file should be created by the user unless explicit code-edit approval is
    given
- Next step:
  - add auxiliary reference regression tests

### Task `7 / 18` - Add Auxiliary Reference Regression Tests

- Task summary:
  - lock representative source-package reference classifications used downstream
    by semantic policy and generator tests
- Expected test location:
  - `tests/test_generation_pipeline_reference_regressions.py`
- Subtask `7.1 / 18`:
  - test `CVN_SEX_A` as direct compact table with eligible enum evidence
- Subtask `7.2 / 18`:
  - test `CVN_ENTITY_TYPE` as direct compact table with delegate/open evidence
    and enum ineligibility
- Subtask `7.3 / 18`:
  - test `CVN_KNOW_A` as subtype-backed and strict-enum ineligible
- Subtask `7.4 / 18`:
  - test `ENTITY@Entity.xsd` as side-package registry reference
- Subtask `7.5 / 18`:
  - test `THESAURUS@thesaurus.xsd` as side-package vocabulary reference
- Subtask `7.6 / 18`:
  - test `UNESCO_CODES` as hierarchical thematic reference
- Subtask `7.7 / 18`:
  - test `CVN_AGENCY_C` as unresolved manual-only reference
- Subtask `7.8 / 18`:
  - test `CVN_INTERVENTION_A` and `CVN_PRUEBA` as under-traced tables
- User manual modifications needed:
  - test file should be created by the user unless explicit code-edit approval is
    given
- Next step:
  - add semantic policy integration tests

### Task `8 / 18` - Add Semantic Policy Integration Tests

- Task summary:
  - verify real normalized entries become expected `SemanticFieldPolicy` outputs
    before generator assertions run
- Expected test location:
  - `tests/test_generation_pipeline_semantic_integration.py`
- Subtask `8.1 / 18`:
  - build semantic policies from canonical normalized entries
- Subtask `8.2 / 18`:
  - assert deterministic `SemanticPolicyBundle` lookup behavior
- Subtask `8.3 / 18`:
  - assert representative domain shapes and enum decisions for real cases
- Subtask `8.4 / 18`:
  - assert trace preservation through CVN `code`, `xml_path`,
    `reference_resolution.trace`, and `SemanticDecisionTrace`
- User manual modifications needed:
  - test file should be created by the user unless explicit code-edit approval is
    given
- Next step:
  - add override policy contract tests

### Task `9 / 18` - Add Override Policy Contract Tests

- Task summary:
  - protect deterministic override precedence and review behavior independent
    from generator output
- Expected test location:
  - `tests/test_generation_pipeline_semantic_integration.py` or
    `tests/test_semantic_policy_unit.py` if purely unit-level
- Subtask `9.1 / 18`:
  - test precedence for `code + xml_path`, `code`, and `xml_path`
- Subtask `9.2 / 18`:
  - test precedence for `reference_resolution.semantic_kind` and
    `reference_resolution.serialization_pattern`
- Subtask `9.3 / 18`:
  - test precedence for `manual_type`, wrapper policy, presence/cardinality, and
    defaults
- Subtask `9.4 / 18`:
  - test same-priority override conflicts produce
    `PolicyConfidence.REQUIRES_REVIEW`
- User manual modifications needed:
  - test file should be edited by the user unless explicit code-edit approval is
    given
- Next step:
  - add naming policy contract tests

### Task `10 / 18` - Add Naming Policy Contract Tests

- Task summary:
  - protect Spanish-first deterministic naming behavior used by generated domain
    artifacts
- Expected test location:
  - `tests/test_generation_pipeline_semantic_integration.py` or
    `tests/test_semantic_policy_unit.py` if purely unit-level
- Subtask `10.1 / 18`:
  - test ASCII normalization and punctuation removal
- Subtask `10.2 / 18`:
  - test `snake_case` field names
- Subtask `10.3 / 18`:
  - test `PascalCase` class names
- Subtask `10.4 / 18`:
  - test acronym preservation for `CVN`, `UNESCO`, `ORCID`, `DOI`, `ISBN`,
    `ISSN`, and `H`
- Subtask `10.5 / 18`:
  - test deterministic collision fallback
- Subtask `10.6 / 18`:
  - assert CVN source identifiers remain literal in trace metadata
- User manual modifications needed:
  - test file should be edited by the user unless explicit code-edit approval is
    given
- Next step:
  - add wrapper handoff tests

### Task `11 / 18` - Add Wrapper Handoff Tests

- Task summary:
  - verify hotfix `#8` wrapper evidence flows from normalization into semantic
    policy and domain generation without generator-side raw XSD rediscovery
- Expected test location:
  - `tests/test_generation_pipeline_wrapper_handoff.py`
- Subtask `11.1 / 18`:
  - test terminal `FlexibleDatesType` maps to `FlexibleDateValue`
- Subtask `11.2 / 18`:
  - test terminal `OfficialIdType` maps to `OfficialIdValue`
- Subtask `11.3 / 18`:
  - test terminal `EntityTypeType` maps to `EntityTypeValue`
- Subtask `11.4 / 18`:
  - test terminal `EntityNameType` maps to `EntityNameValue`
- Subtask `11.5 / 18`:
  - test ancestor-only wrapper trace does not become terminal wrapper field
- Subtask `11.6 / 18`:
  - assert `structural_type_evidence` is the consumed handoff data
- User manual modifications needed:
  - test file should be created by the user unless explicit code-edit approval is
    given
- Next step:
  - add canonical generator contract tests

### Task `12 / 18` - Add Generator Canonical Contract Tests

- Task summary:
  - verify the domain generator consumes `SemanticPolicyBundle` outputs and emits
    distinct shapes per semantic class
- Expected test location:
  - `tests/test_generation_pipeline_domain_generation.py`
- Subtask `12.1 / 18`:
  - build canonical normalization and semantic policy index
- Subtask `12.2 / 18`:
  - call `build_domain_generation_result(...)`
- Subtask `12.3 / 18`:
  - assert eligible strict enum cases produce enum specs
- Subtask `12.4 / 18`:
  - assert ineligible or reviewed controlled references do not produce strict
    enums
- Subtask `12.5 / 18`:
  - assert non-enum controlled references map to the correct shared components
- Subtask `12.6 / 18`:
  - assert `cvn_trace` metadata is preserved in field specs
- User manual modifications needed:
  - test file should be created by the user unless explicit code-edit approval is
    given
- Next step:
  - add generated output importability tests

### Task `13 / 18` - Add Generated Output Importability Tests

- Task summary:
  - prove generated Python output can be written to a temporary directory,
    imported, and instantiated
- Expected test location:
  - `tests/test_generation_pipeline_domain_generation.py` or
    `tests/test_generation_pipeline_e2e.py`
- Subtask `13.1 / 18`:
  - generate rendered domain files into a temporary output directory
- Subtask `13.2 / 18`:
  - import the generated package from the temporary directory
- Subtask `13.3 / 18`:
  - import `enums`, `manual_only`, and at least one `cvn_item_*` module
- Subtask `13.4 / 18`:
  - instantiate a representative generated model
- Subtask `13.5 / 18`:
  - assert trace metadata includes `code`, `xml_paths`, `domain_shape_kind`, and
    `enum_eligibility`
- User manual modifications needed:
  - test file should be edited by the user unless explicit code-edit approval is
    given
- Next step:
  - add determinism tests

### Task `14 / 18` - Add Determinism Tests

- Task summary:
  - prove repeated generation from identical inputs produces identical files
- Expected test location:
  - `tests/test_generation_pipeline_domain_generation.py` or
    `tests/test_generation_pipeline_e2e.py`
- Subtask `14.1 / 18`:
  - run generation twice into separate temporary directories
- Subtask `14.2 / 18`:
  - compare generated relative file paths
- Subtask `14.3 / 18`:
  - compare generated file bytes
- Subtask `14.4 / 18`:
  - assert generated output remains ASCII-only when current generator policy keeps
    that guarantee
- User manual modifications needed:
  - test file should be edited by the user unless explicit code-edit approval is
    given
- Next step:
  - add end-to-end pipeline test

### Task `15 / 18` - Add End-To-End Pipeline Test

- Task summary:
  - test the real pipeline from canonical source package through generated domain
    imports
- Expected test location:
  - `tests/test_generation_pipeline_e2e.py`
- Subtask `15.1 / 18`:
  - start from canonical XML and XSD paths
- Subtask `15.2 / 18`:
  - build auxiliary bundle and enriched normalization result
- Subtask `15.3 / 18`:
  - build semantic policies and domain generation result
- Subtask `15.4 / 18`:
  - render and write generated domain files to a temporary directory
- Subtask `15.5 / 18`:
  - import generated package and representative modules
- Subtask `15.6 / 18`:
  - assert stable high-level counts such as normalized entry count and generated
    file count when still valid
- User manual modifications needed:
  - test file should be created by the user unless explicit code-edit approval is
    given
- Next step:
  - adjust existing tests to avoid duplication or fragility

### Task `16 / 18` - Adjust Existing Tests

- Task summary:
  - keep unit tests focused and move repeated setup into shared fixtures where
    useful
- Expected files:
  - `tests/conftest.py`
  - existing `tests/test_*` files only when needed
- Subtask `16.1 / 18`:
  - identify duplicated canonical path and helper setup
- Subtask `16.2 / 18`:
  - move shared setup to fixtures without changing test meaning
- Subtask `16.3 / 18`:
  - keep semantic-policy unit tests separate from generator tests
- Subtask `16.4 / 18`:
  - keep integration tests focused on real canonical pipeline behavior
- User manual modifications needed:
  - test files should be edited by the user unless explicit code-edit approval is
    given
- Next step:
  - run final verification

### Task `17 / 18` - Run Final Verification

- Task summary:
  - prove issue `#16` coverage passes locally and under the CI command from issue
    `#25`
- Commands:
  - `uv run pytest -n auto tests/test_generation_pipeline_structural.py tests/test_generation_pipeline_parse_smoke.py tests/test_generation_pipeline_normalization_integration.py tests/test_generation_pipeline_reference_regressions.py tests/test_generation_pipeline_semantic_integration.py tests/test_generation_pipeline_wrapper_handoff.py tests/test_generation_pipeline_domain_generation.py tests/test_generation_pipeline_e2e.py -v`
  - `uv run pytest -n auto tests`
  - `uv run python -m cvn_codegen.domain_model_generator` if canonical generated
    output must be refreshed or verified
- Subtask `17.1 / 18`:
  - run targeted issue `#16` tests
- Subtask `17.2 / 18`:
  - run full repository test suite
- Subtask `17.3 / 18`:
  - run canonical domain generator verification when needed
- Subtask `17.4 / 18`:
  - record exact command output and failures
- User manual modifications needed:
  - none unless verification exposes required code or test fixes
- Next step:
  - update closure documentation

### Task `18 / 18` - Update Closure Documentation

- Task summary:
  - close issue `#16` with implementation details, verification results,
    limitations, and issue `#17` handoff
- Files involved:
  - `docs/roadmap/issues/issue-16-generation-pipeline-tests.md`
  - `docs/context/current_status.md`
  - `docs/roadmap/cvn_generation_roadmap.md`
  - `docs/pipeline/known_limitations.md` only if a new limitation is found
  - `PROJECT_GUIDE.md` only if human-facing orientation changes
- Subtask `18.1 / 18`:
  - record implementation performed
- Subtask `18.2 / 18`:
  - record verification commands and exact results
- Subtask `18.3 / 18`:
  - record findings and limitations
- Subtask `18.4 / 18`:
  - update issue status when implementation is verified
- Subtask `18.5 / 18`:
  - update roadmap and current status if issue state changes
- Subtask `18.6 / 18`:
  - leave explicit handoff checklist for issue `#17`
- User manual modifications needed:
  - none expected for documentation updates when explicitly requested
- Next step:
  - start issue `#17` only after issue `#16` is implemented and verified

## Representative Regression Cases Required

The test suite must include explicit coverage for these documented cases:

- `000.010.000.020` / `Nombre` as plain text and enum-ineligible
- `CVN_SEX_A` as compact direct table and strict-enum eligible from dynamic
  evidence
- `CVN_ENTITY_TYPE` as compact direct table and strict-enum ineligible due to
  delegate/open evidence
- `CVN_KNOW_A` as subtype-backed reference family
- `ENTITY@Entity.xsd` as side-package registry reference
- `THESAURUS@thesaurus.xsd` as side-package thesaurus or vocabulary reference
- `UNESCO_CODES` as hierarchical thematic reference
- `CVN_AGENCY_C` as unresolved manual-only reference
- `CVN_INTERVENTION_A` and `CVN_PRUEBA` as under-traced tables
- `FlexibleDatesType`, `OfficialIdType`, `EntityTypeType`, and `EntityNameType`
  as wrapper handoff cases

## Minimum Coverage Goals

1. structural parsing smoke tests for generated bindings
2. normalization tests using real XML inputs
3. regression tests for `choice` and recursion-related cases where relevant
4. semantic-class-driven mapping tests, including enum-vs-open behavior
5. generator tests proving distinct domain shapes per semantic class
6. end-to-end generation tests for importable domain outputs
7. determinism tests for generated domain files

## Known Inputs From Earlier Issues

- issue `#12` already added runner smoke tests
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
- issue `#14` provides semantic policy and validation inventory
- issue `#15` provides domain generator and generated domain output
- known XML/XSD mismatches must be asserted as documented behavior rather than
  treated as surprising failures

## CI Impact

- issue `#25` already provides pull-request execution of all tests under
  `tests/`
- new structural, normalization, semantic-policy, generator, wrapper, and
  end-to-end tests must remain under `tests/` so CI picks them up automatically
  without workflow changes

## Adjustments Made During Implementation

- Pre-implementation planning is aligned with the semantic-policy contract from
  issue `#14`, the domain generator contract from issue `#15`, and the wrapper
  handoff from hotfix `#8`.
- The test scope separates semantic-policy verification from domain-generator
  verification so failures can be attributed to the correct layer.
- The accepted execution protocol and detailed 18-task implementation plan have
  been recorded before test implementation begins.
- Existing runner smoke tests and new structural generation tests both regenerate
  `src/generated/*`; full-suite multicore execution exposed a race between those
  tests. A test-only file lock now serializes xsdata generation tests while
  preserving `pytest -n auto` for the rest of the suite.
- `CVN_SEX_A` remains a compact enum-like table with eligible enum evidence, but
  its current serialization pattern is `UNKNOWN_PRESENT_BUT_RESOLVED` rather than
  `FILTER_VALUE`; tests assert the implemented normalized contract.
- Domain generation result entries may repeat when one normalized code appears in
  multiple generation units, so generator tests assert unique normalized codes
  separately from per-unit entry occurrences.

## Implementation Performed

- Shared canonical pipeline fixtures were added in `tests/conftest.py` for:
  - repository root and canonical source package paths
  - XML and XSD path lookup
  - auxiliary source bundle construction
  - XSD-enriched canonical normalization result construction
  - temporary domain-generation output directories
- A test-only xsdata generation lock was added in
  `tests/xsdata_generation_lock.py` and used by both:
  - `tests/test_xsdata_runner_smoke.py`
  - `tests/test_generation_pipeline_structural.py`
- New issue `#16` pipeline tests were added under `tests/`:
  - `tests/test_generation_pipeline_structural.py`
  - `tests/test_generation_pipeline_parse_smoke.py`
  - `tests/test_generation_pipeline_normalization_integration.py`
  - `tests/test_generation_pipeline_reference_regressions.py`
  - `tests/test_generation_pipeline_semantic_integration.py`
  - `tests/test_generation_pipeline_wrapper_handoff.py`
  - `tests/test_generation_pipeline_domain_generation.py`
  - `tests/test_generation_pipeline_e2e.py`
  - `tests/test_generation_pipeline_source_coverage.py`
- The implemented coverage validates:
  - manual, tree, auxiliary catalog, semantic policy, and domain-generation
    source coverage from canonical inputs to code-level artifacts
  - core and auxiliary structural generation targets
  - real XML parse smoke behavior, including documented `CVNTreeModel.xml`
    mismatch behavior
  - canonical normalization baseline and enriched auxiliary-reference resolution
  - representative auxiliary reference classifications
  - semantic policy decisions before generator behavior
  - override precedence, naming, trace preservation, and wrapper handoff behavior
  - generator domain-shape mapping, importability, rendered output determinism,
    and ASCII output
  - end-to-end generation from canonical XML/XSD inputs to importable temporary
    domain output

## Verification

- Targeted issue `#16` verification passed with:
  - `uv run pytest -n auto tests/test_generation_pipeline_structural.py tests/test_generation_pipeline_parse_smoke.py tests/test_generation_pipeline_normalization_integration.py tests/test_generation_pipeline_reference_regressions.py tests/test_generation_pipeline_semantic_integration.py tests/test_generation_pipeline_wrapper_handoff.py tests/test_generation_pipeline_domain_generation.py tests/test_generation_pipeline_e2e.py -v`
  - result: `61 passed in 146.76s (0:02:26)`
- Full repository verification initially exposed an xdist race between xsdata
  generation tests. After adding the test-only generation lock, the affected
  smoke and structural tests passed with:
  - `uv run pytest -n auto tests/test_xsdata_runner_smoke.py tests/test_generation_pipeline_structural.py -v`
  - result: `17 passed in 141.50s (0:02:21)`
- Final full repository verification passed with:
  - `uv run pytest -n auto tests`
  - result: `289 passed in 280.75s (0:04:40)`
- After adding the explicit source-coverage audit test, focused verification
  passed with:
  - `uv run pytest -n auto tests/test_generation_pipeline_source_coverage.py -v`
  - result: `5 passed in 90.15s (0:01:30)`
- Final full repository verification after the source-coverage audit passed with:
  - `uv run pytest -n auto tests`
  - result: `294 passed in 277.77s (0:04:37)`

## Findings

- Existing unit tests cover many semantic-policy and generator internals, but
  issue `#16` must add real-pipeline integration and end-to-end regression
  coverage.
- Semantic-policy behavior must remain tested before generator-output behavior so
  failures are not misattributed.
- Generated-domain importability and determinism are first-class pipeline
  requirements after issue `#15`.
- Tests that execute structural regeneration must be serialized across xdist
  workers because they clean and rewrite shared `src/generated/*` directories.
- The generator result distinguishes semantic-policy uniqueness from per-output
  generation-unit occurrences; tests should assert both concepts separately.
- End-to-end pipeline testing can safely render generated domain output to a
  temporary package for importability checks without modifying the committed
  canonical generated domain output.
- Explicit source-coverage auditing confirms all `SpecificationManual.xml` items,
  all unique `CVNTreeModel.xml` codes, all normalized codes, loaded reference
  tables, subtype items, entity registry items, thesaurus items, and generated
  core `AuxTable.xsd` enums are represented in code-level artifacts.

## Known Limitations

- `CVNTreeModel.xml` still has a documented XML/XSD mismatch.
- `Subtype_Spa.xml` still lacks a strict per-table bridge such as `CVN_KNOW_A`
  to subtype records.
- `CVN_AGENCY_C` remains unresolved from the source package alone.
- `CVN_INTERVENTION_A` and `CVN_PRUEBA` remain technically present but
  under-traced.
- Wrapper-aware field attachment requires normalization runs that provide
  `CVN.xsd` and `Common.xsd`; canonical generation provides those inputs.

## Impact On Future Issues

- Issue `#17` must document how to run semantic-policy tests separately from
  structural, normalization, generator, wrapper, and end-to-end tests.
- Issue `#17` must document `SemanticPolicyBundle` as the semantic source of
  truth for domain generation.
- CI workflow from issue `#25` does not need changes if new tests remain under
  `tests/`.
- Issue `#17` should document the canonical full-suite command as the main
  workflow verification entry point and mention that xsdata-regeneration tests
  are serialized internally under xdist.

## Status

- Status: completed
