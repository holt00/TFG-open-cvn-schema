# Issue 17 - Document And Automate The Complete Workflow

## Summary

Issue `#17` will leave the repository with a clear, reproducible, documented
workflow for regenerating structural bindings, normalized metadata, semantic
policy, domain models, and verification coverage.

## Corrected Prerequisite Chain

Issue `#17` must document the full workflow as it actually exists after issues
`#14`, `#15`, `#16`, `#25`, and hotfixes `#4` through `#8`, not the older
reduced core-only workflow.

The documented workflow must therefore include:

1. auxiliary structural generation stages already added to the repository
2. auxiliary-reference resolution enrichment already added to normalization
3. dynamic reference-table enum evidence from `ReferenceTables.xml`
4. wrapper type traceability in the normalized handoff
5. semantic policy as the source-of-truth handoff into domain generation
6. generated domain artifacts and verification coverage
7. CI coverage for the full test suite

## Original Goal

- document the architecture and automate the complete CVN regeneration workflow

## Original Plan

1. document the architecture and source relationships
2. document the workflow step by step
3. document known limitations and external dependencies
4. provide a clear regeneration entry point
5. update repository documentation
6. leave one obvious workflow for future contributors

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

## Corrected Workflow Stages That Must Be Documented

The final workflow documentation must explicitly include:

1. generation of core structural bindings
2. generation of auxiliary structural bindings
3. normalization of manual and tree metadata
4. auxiliary-source loading and deterministic reference-resolution enrichment
5. XSD-enriched structural type evidence for wrapper handoff
6. semantic policy application over enriched normalized metadata
7. domain-model generation
8. pipeline verification and CI coverage

The semantic policy stage must be documented as the handoff from normalized
metadata to domain generation:

```text
normalized metadata + auxiliary reference resolution + structural type evidence
-> SemanticPolicyBundle
-> domain generator
-> domain-oriented Pydantic artifacts
```

The workflow must make clear that `SemanticPolicyBundle` is the source of truth
for generator semantics. Raw XML, raw XSD, and generated structural bindings may
support validation and traceability, but they are not the source for redefining
semantic policy in later stages.

## Controlled-Reference Source-Of-Truth Order

The workflow documentation must explain the effective source-of-truth order for
controlled references already materialized by normalization logic:

1. explicit side-package references such as `ENTITY@Entity.xsd` and
   `THESAURUS@thesaurus.xsd`
2. direct `ReferenceTables.xml` matches where applicable
3. subtype-backed classification through `Subtype@Subtypes.xsd`
4. hierarchical thematic classification where technical metadata supports it
5. unresolved documented exceptions and under-traced tables

## Expected Documentation Outcome

- one obvious regeneration workflow
- explicit documentation of authoritative inputs and generated outputs
- explicit documentation of known limitations and unresolved external tables
- sufficient guidance for another contributor to rerun the complete workflow
  from a clean checkout
- explicit documentation of repository boundaries between structural fidelity,
  normalization/resolution logic, semantic policy, and domain outputs

## Semantic Policy Documentation Requirements

The final workflow documentation must describe these issue `#14` policy outputs
because issues `#15`, `#16`, and `#17` depend on them:

- `domain_shape_kind`
- `fallback_shape_kind`
- `enum_eligibility`
- `policy_confidence`
- `wrapper_policy`
- `presence_kind`
- `cardinality_kind`
- `normalized_name`
- `naming_confidence`
- `structural_limitation_flags`
- `SemanticDecisionTrace`

The workflow documentation must also explain:

- Spanish-first domain naming and deterministic identifier normalization
- versioned and reviewable override policy
- strict-enum eligibility limits
- open coded-value fallback behavior
- wrapper and `xs:choice` treatment
- preservation of CVN source identifiers in trace metadata
- separation between semantic policy decisions and concrete Python emission
  choices

## Repository Boundaries To Document

- `src/generated/` remains structural fidelity layer generated from canonical
  schemas
- `src/cvn_codegen/` contains hand-maintained loading, normalization,
  resolution, semantic-policy, and generation logic
- `src/models/cvn/` remains the target location for future domain-oriented
  outputs

Traceability documentation should identify these values as the minimum chain
from source metadata to domain output:

- CVN `code`
- `xml_path`
- `reference_resolution.trace`
- `SemanticDecisionTrace`

## Accepted Execution Plan

### Task `1 / 19` - Register Plan In Issue Documentation

- Task summary:
  - record the accepted issue `#17` execution plan and remove stale conflict
    markers from this issue document
- Files involved:
  - `docs/roadmap/issues/issue-17-workflow-documentation.md`
- Subtask `1.1 / 19`:
  - review the current issue document and preserve the valid corrected scope
- Subtask `1.2 / 19`:
  - remove `<<<<<<<`, `=======`, and `>>>>>>>` markers and duplicated sections
- Subtask `1.3 / 19`:
  - insert the accepted execution protocol and 19-task plan
- User manual modifications needed:
  - none expected for this documentation update
- Next step:
  - verify the baseline before workflow documentation work

### Task `2 / 19` - Verify Baseline

- Task summary:
  - prove the current repository test suite and canonical domain-generation entry
    point are stable before documenting the final workflow
- Commands:
  - `uv run pytest -n auto tests`
  - `uv run python -m cvn_codegen.domain_model_generator`
- Subtask `2.1 / 19`:
  - run the full repository test suite with the documented command
- Subtask `2.2 / 19`:
  - run the canonical domain generator command when needed to confirm the
    generation entry point
- Subtask `2.3 / 19`:
  - record exact failures if the baseline fails
- Subtask `2.4 / 19`:
  - stop and ask for direction before code fixes if failures require code changes
- User manual modifications needed:
  - none unless verification exposes required code changes
- Next step:
  - inventory the implemented workflow

### Task `3 / 19` - Inventory The Implemented Workflow

- Task summary:
  - identify the real workflow stages, inputs, outputs, commands, and ownership
    boundaries that issue `#17` must document
- Files to inspect:
  - `docs/context/current_status.md`
  - `docs/roadmap/cvn_generation_roadmap.md`
  - `docs/pipeline/cvn_pydantic_generation_pipeline.md`
  - `docs/pipeline/known_limitations.md`
  - issue records for `#14`, `#15`, `#16`, and `#25`
  - hotfix records `#4` through `#8`
- Subtask `3.1 / 19`:
  - list structural, normalization, semantic-policy, generator, test, and CI
    stages
- Subtask `3.2 / 19`:
  - list authoritative commands and generated artifacts
- Subtask `3.3 / 19`:
  - list documentation files that must be changed
- User manual modifications needed:
  - none expected
- Next step:
  - document authoritative inputs

### Task `4 / 19` - Document Authoritative Inputs

- Task summary:
  - document the canonical source package and input artifacts required for the
    complete regeneration workflow
- Expected documentation targets:
  - `docs/pipeline/cvn_pydantic_generation_pipeline.md`
  - workflow guide created or updated by task `7`
- Subtask `4.1 / 19`:
  - document the canonical package path
    `docs/CvnXML_v1.4.3_2.1_17012025/`
- Subtask `4.2 / 19`:
  - document core XSD inputs: `CVN.xsd`, `Common.xsd`, `AuxTable.xsd`,
    `ISOUtilities.xsd`, `SpecificationManual.xsd`, and
    `CVNTreeModel_v1.0.xsd`
- Subtask `4.3 / 19`:
  - document auxiliary XSD inputs: `ReferenceTables.xsd`, `Subtypes.xsd`,
    `Entity_v1.4.xsd`, and `Thesaurus.xsd`
- Subtask `4.4 / 19`:
  - document XML inputs: `SpecificationManual.xml`, `CVNTreeModel.xml`,
    `ReferenceTables.xml`, `Subtype_Spa.xml`, `Entity.xml`, and `Thesaurus.xml`
- User manual modifications needed:
  - none expected for documentation updates
- Next step:
  - document generated outputs

### Task `5 / 19` - Document Generated Outputs

- Task summary:
  - document which files and packages are generated and which must not be edited
    manually
- Expected documentation targets:
  - `docs/pipeline/cvn_pydantic_generation_pipeline.md`
  - workflow guide created or updated by task `7`
- Subtask `5.1 / 19`:
  - document `src/generated/*` as structural output from xsdata
- Subtask `5.2 / 19`:
  - document `src/models/cvn/generated/*` as domain output from the domain
    generator
- Subtask `5.3 / 19`:
  - document generated enums, `manual_only`, and `cvn_item_*` modules
- Subtask `5.4 / 19`:
  - document trace metadata preserved in generated artifacts
- User manual modifications needed:
  - none expected for documentation updates
- Next step:
  - update architecture documentation

### Task `6 / 19` - Update Pipeline Architecture Documentation

- Task summary:
  - update the pipeline architecture document so it describes the complete
    implemented workflow rather than only the structural baseline
- Files involved:
  - `docs/pipeline/cvn_pydantic_generation_pipeline.md`
- Subtask `6.1 / 19`:
  - add or update a complete workflow section covering all implemented stages
- Subtask `6.2 / 19`:
  - document the command order for structural generation, domain generation, and
    verification
- Subtask `6.3 / 19`:
  - document repository boundaries between `src/generated/`, `src/cvn_codegen/`,
    and `src/models/cvn/`
- Subtask `6.4 / 19`:
  - document the `tree_model` target-specific `--unnest-classes` override
- Subtask `6.5 / 19`:
  - document that xsdata regeneration tests are serialized internally by a
    test-only lock under `pytest -n auto`
- User manual modifications needed:
  - none expected for documentation updates
- Next step:
  - create or update a workflow guide

### Task `7 / 19` - Create Or Update Regeneration Workflow Guide

- Task summary:
  - provide one obvious contributor-facing workflow for regenerating and verifying
    all CVN artifacts from a clean checkout
- Expected documentation target:
  - `docs/development/regeneration_workflow.md`, unless an existing development
    document is a better fit during implementation
- Subtask `7.1 / 19`:
  - document environment setup commands
- Subtask `7.2 / 19`:
  - document structural generation with
    `uv run python -m cvn_codegen.xsdata_runner all`
- Subtask `7.3 / 19`:
  - document canonical domain generation with
    `uv run python -m cvn_codegen.domain_model_generator`
- Subtask `7.4 / 19`:
  - document full verification with `uv run pytest -n auto tests`
- Subtask `7.5 / 19`:
  - document expected generated directories and no-manual-edit rules
- User manual modifications needed:
  - none expected for documentation updates
- Next step:
  - document controlled-reference source-of-truth order

### Task `8 / 19` - Document Controlled-Reference Source Order

- Task summary:
  - document how normalized metadata decides controlled-reference meaning before
    semantic policy consumes it
- Expected documentation targets:
  - `docs/pipeline/cvn_pydantic_generation_pipeline.md`
  - workflow guide created or updated by task `7`
- Subtask `8.1 / 19`:
  - document side-package references such as `ENTITY@Entity.xsd` and
    `THESAURUS@thesaurus.xsd`
- Subtask `8.2 / 19`:
  - document direct `ReferenceTables.xml` matches
- Subtask `8.3 / 19`:
  - document subtype-backed classification through `Subtype@Subtypes.xsd`
- Subtask `8.4 / 19`:
  - document hierarchical thematic classification such as `UNESCO_CODES`
- Subtask `8.5 / 19`:
  - document unresolved and under-traced cases such as `CVN_AGENCY_C`,
    `CVN_INTERVENTION_A`, and `CVN_PRUEBA`
- User manual modifications needed:
  - none expected for documentation updates
- Next step:
  - document the semantic policy contract

### Task `9 / 19` - Document Semantic Policy Contract

- Task summary:
  - document `SemanticPolicyBundle` as the semantic source of truth for domain
    generation
- Expected documentation targets:
  - `docs/pipeline/cvn_pydantic_generation_pipeline.md`
  - workflow guide created or updated by task `7`
- Subtask `9.1 / 19`:
  - document `domain_shape_kind`, `fallback_shape_kind`, `enum_eligibility`, and
    `policy_confidence`
- Subtask `9.2 / 19`:
  - document `wrapper_policy`, `presence_kind`, `cardinality_kind`, and
    `structural_limitation_flags`
- Subtask `9.3 / 19`:
  - document `normalized_name`, `naming_confidence`, and Spanish-first naming
- Subtask `9.4 / 19`:
  - document `SemanticDecisionTrace` and source identifier preservation
- Subtask `9.5 / 19`:
  - document strict-enum eligibility limits, open coded-value fallback, and
    versioned override policy
- User manual modifications needed:
  - none expected for documentation updates
- Next step:
  - document domain generation contract

### Task `10 / 19` - Document Domain Generation Contract

- Task summary:
  - explain how the domain generator consumes `SemanticPolicyBundle` and emits
    deterministic domain-oriented Pydantic artifacts
- Expected documentation targets:
  - `docs/pipeline/cvn_pydantic_generation_pipeline.md`
  - workflow guide created or updated by task `7`
- Subtask `10.1 / 19`:
  - document canonical generator command
- Subtask `10.2 / 19`:
  - document current expected generated file count when still valid
- Subtask `10.3 / 19`:
  - document generated module families such as `enums`, `manual_only`, and
    `cvn_item_*`
- Subtask `10.4 / 19`:
  - document determinism, ASCII output, importability, and trace preservation
- Subtask `10.5 / 19`:
  - document that generator code must not re-derive semantic meaning from raw XML
    or raw XSD
- User manual modifications needed:
  - none expected for documentation updates
- Next step:
  - document wrapper handoff

### Task `11 / 19` - Document Wrapper Handoff

- Task summary:
  - document how XSD-enriched normalization carries wrapper type evidence into
    semantic policy and domain generation
- Expected documentation targets:
  - `docs/pipeline/cvn_pydantic_generation_pipeline.md`
  - workflow guide created or updated by task `7`
  - `docs/pipeline/known_limitations.md` only if wording needs clarification
- Subtask `11.1 / 19`:
  - document that canonical normalization provides `CVN.xsd` and `Common.xsd`
- Subtask `11.2 / 19`:
  - document `StructuralTypeEvidence` as handoff data
- Subtask `11.3 / 19`:
  - document wrapper value components: `FlexibleDateValue`, `OfficialIdValue`,
    `EntityTypeValue`, and `EntityNameValue`
- Subtask `11.4 / 19`:
  - document limitation for normalization calls that omit XSD paths
- User manual modifications needed:
  - none expected for documentation updates
- Next step:
  - document verification matrix

### Task `12 / 19` - Document Verification Matrix

- Task summary:
  - document how to verify the complete workflow locally and through existing CI
- Expected documentation targets:
  - workflow guide created or updated by task `7`
  - `docs/pipeline/cvn_pydantic_generation_pipeline.md`
- Subtask `12.1 / 19`:
  - document full-suite command `uv run pytest -n auto tests`
- Subtask `12.2 / 19`:
  - document targeted test areas: structural, parse smoke, normalization,
    reference regressions, semantic integration, wrapper handoff, domain
    generation, source coverage, and end-to-end tests
- Subtask `12.3 / 19`:
  - document CI workflow from issue `#25` and the stable `tests` check
- Subtask `12.4 / 19`:
  - document xsdata generation test serialization with
    `tests/xsdata_generation_lock.py`
- User manual modifications needed:
  - none expected for documentation updates
- Next step:
  - document known limitations

### Task `13 / 19` - Document Known Limitations

- Task summary:
  - ensure workflow documentation preserves known limitations instead of hiding
    them as unexpected failures
- Expected documentation targets:
  - `docs/pipeline/known_limitations.md`
  - workflow guide created or updated by task `7`
  - `docs/pipeline/cvn_pydantic_generation_pipeline.md`
- Subtask `13.1 / 19`:
  - document `CVNTreeModel.xml` XML/XSD mismatch as expected behavior
- Subtask `13.2 / 19`:
  - document structural `xs:choice`, `minOccurs`, and weak `object` typing
    limitations
- Subtask `13.3 / 19`:
  - document `Subtype_Spa.xml` no strict per-table bridge limitation
- Subtask `13.4 / 19`:
  - document unresolved `CVN_AGENCY_C` and under-traced `CVN_INTERVENTION_A` and
    `CVN_PRUEBA`
- Subtask `13.5 / 19`:
  - document wrapper-aware generation dependency on XSD-enriched normalization
- User manual modifications needed:
  - none expected for documentation updates
- Next step:
  - update human entry points if needed

### Task `14 / 19` - Update Human Entry Documentation If Needed

- Task summary:
  - make any new workflow documentation discoverable from the repository entry
    points
- Files involved when applicable:
  - `README.md`
  - `PROJECT_GUIDE.md`
  - `docs/context/project_context_index.md`
  - `AGENTS.md` only if operational rules or document map change
- Subtask `14.1 / 19`:
  - decide whether the workflow guide changes the human-facing document map
- Subtask `14.2 / 19`:
  - update `PROJECT_GUIDE.md` if the human-facing map changes
- Subtask `14.3 / 19`:
  - update `docs/context/project_context_index.md` if the documentation map
    changes
- Subtask `14.4 / 19`:
  - update `README.md` only if the top-level entry guidance needs it
- Subtask `14.5 / 19`:
  - update `AGENTS.md` only if the agent document map or operational rules change
- User manual modifications needed:
  - none expected for documentation updates
- Next step:
  - update current status

### Task `15 / 19` - Update Current Status

- Task summary:
  - record the completed issue `#17` workflow documentation state and next work
    direction
- Files involved:
  - `docs/context/current_status.md`
- Subtask `15.1 / 19`:
  - add issue `#17` implementation summary
- Subtask `15.2 / 19`:
  - record final commands and verification results
- Subtask `15.3 / 19`:
  - update next planned work after issue `#17`
- Subtask `15.4 / 19`:
  - preserve links to relevant limitations
- User manual modifications needed:
  - none expected for documentation updates
- Next step:
  - update roadmap

### Task `16 / 19` - Update Roadmap

- Task summary:
  - mark issue `#17` as completed and make the documented workflow visible in the
    roadmap
- Files involved:
  - `docs/roadmap/cvn_generation_roadmap.md`
- Subtask `16.1 / 19`:
  - change issue `#17` status from `Next` to `Completed` after verification
- Subtask `16.2 / 19`:
  - summarize the implemented workflow documentation outcome
- Subtask `16.3 / 19`:
  - update future work focus to point at the new post-`#17` epic when task `19`
    creates it
- User manual modifications needed:
  - none expected for documentation updates
- Next step:
  - close issue document

### Task `17 / 19` - Close Issue Documentation

- Task summary:
  - update this issue record with implementation details, verification, findings,
    limitations, and final status
- Files involved:
  - `docs/roadmap/issues/issue-17-workflow-documentation.md`
- Subtask `17.1 / 19`:
  - record implementation performed
- Subtask `17.2 / 19`:
  - record verification commands and exact results
- Subtask `17.3 / 19`:
  - record findings and limitations
- Subtask `17.4 / 19`:
  - record impact on future issues
- Subtask `17.5 / 19`:
  - update status to completed after verification
- User manual modifications needed:
  - none expected for documentation updates
- Next step:
  - run final verification

### Task `18 / 19` - Run Final Verification

- Task summary:
  - prove the documented workflow and repository verification remain stable after
    issue `#17` documentation updates
- Commands:
  - `uv run pytest -n auto tests`
  - `uv run python -m cvn_codegen.domain_model_generator` when generated output
    needs to be refreshed or command behavior must be reconfirmed
- Subtask `18.1 / 19`:
  - run full repository test suite
- Subtask `18.2 / 19`:
  - run canonical domain generator command when needed
- Subtask `18.3 / 19`:
  - inspect docs for conflict markers and stale issue status
- Subtask `18.4 / 19`:
  - record exact command output and failures
- User manual modifications needed:
  - none unless verification exposes required code or generated-output changes
- Next step:
  - create the next epic placeholder

### Task `19 / 19` - Create Placeholder Epic For Remaining Work

- Task summary:
  - create a new epic record for the remaining project work after issue `#17`
    without detailing that epic yet
- Expected files:
  - new issue or epic document under `docs/roadmap/issues/`
  - `docs/roadmap/cvn_generation_roadmap.md`
  - `docs/context/current_status.md`
  - `PROJECT_GUIDE.md` or `docs/context/project_context_index.md` only if the
    documentation map needs the new epic listed immediately
- Subtask `19.1 / 19`:
  - create a minimal placeholder epic with provisional title, general purpose,
    and status `planned`
- Subtask `19.2 / 19`:
  - add a note that details are pending after issue `#17` closure
- Subtask `19.3 / 19`:
  - update roadmap and current-status pointers only enough to make the epic
    discoverable
- User manual modifications needed:
  - none expected for documentation updates
- Next step:
  - stop after placeholder creation unless the user asks to detail the new epic

## Known Limitations

- `CVN_AGENCY_C` remains unresolved from the package alone
- subtype catalog availability does not always expose a strict per-table key for
  direct subtype verification
- `CVN_INTERVENTION_A` and `CVN_PRUEBA` remain technically present but
  under-traced
- structural bindings do not enforce `xs:choice` mutual exclusivity
- generated list defaults do not reliably enforce every `minOccurs` constraint
- known XML/XSD mismatch behavior, such as `CVNTreeModel.xml`, must remain
  documented as validated limitation rather than hidden failure
- wrapper-aware generation requires XSD-enriched normalization when wrapper
  policies are needed

## Adjustments Made During Implementation

- Pre-implementation planning is aligned with the issue `#14` semantic policy
  contract, the issue `#15` generator handoff, the issue `#16` verification
  coverage, and the hotfix `#8` wrapper handoff.
- The future workflow documentation scope treats semantic policy application as
  an explicit pipeline stage and `SemanticPolicyBundle` as the generator semantic
  source of truth.
- The accepted execution protocol and detailed 19-task implementation plan have
  been recorded before workflow documentation implementation begins.
- The issue document was cleaned before implementation so stale conflict markers
  and duplicated sections no longer obscure the accepted scope.

## Implementation Performed

- The accepted 19-task execution plan was recorded in this issue document.
- Stale conflict markers and duplicated sections were removed from this issue
  document.
- The complete regeneration guide was added at
  `docs/development/regeneration_workflow.md`.
- `docs/pipeline/cvn_pydantic_generation_pipeline.md` was updated to document
  the complete workflow, command sequence, controlled-reference source order,
  semantic policy contract, domain generation contract, wrapper handoff, tests,
  and CI behavior.
- `docs/development/setup.md`, `CONTRIBUTING.md`, `PROJECT_GUIDE.md`,
  `AGENTS.md`, and `docs/context/project_context_index.md` were updated so the
  new workflow guide is discoverable.
- `docs/context/current_status.md` and
  `docs/roadmap/cvn_generation_roadmap.md` were updated to reflect the completed
  workflow documentation state.

## Verification

- Baseline verification before workflow documentation passed with:
  - `uv run pytest -n auto tests`
  - result: `294 passed in 297.99s (0:04:57)`
- Canonical domain generator verification passed with:
  - `uv run python -m cvn_codegen.domain_model_generator`
  - result: `Generated 105 files`
- Final verification for the issue `#17` documentation patch remains to be run
  in task `18 / 19`.

## Findings

- Workflow documentation must prevent future contributors from treating raw XML,
  raw XSD, or generated structural bindings as semantic-policy sources after
  issue `#14` establishes `SemanticPolicyBundle`.
- The final workflow needs separate explanations for structural fidelity,
  normalization/resolution, semantic policy, generation, wrapper handoff, and
  verification.
- The issue document previously contained conflict markers and duplicated
  sections; those must remain removed.
- A dedicated regeneration workflow guide is now necessary because setup commands
  alone are not enough to explain the complete post-issue-`#16` pipeline.

## Impact On Future Issues

- Future work should start from `docs/development/regeneration_workflow.md` when
  changing generated artifacts, semantic policy, domain generation, or pipeline
  tests.
- Human-facing and agent-facing document maps now include the regeneration
  workflow guide.
- A new placeholder epic must be created at the end of issue `#17` to represent
  remaining work, with detailed planning deferred until the user requests it.

## Status

- Status: implementation complete; final verification and placeholder follow-up
  epic creation pending
