# Issue 46 - Define Canonical Open CVN JSON Format

## Summary

Issue `#46` defines the canonical Open CVN JSON format that will be validated by
the parser and consumed by later application work.

This issue is part of epic `#41`.

## Goal

- define the root JSON object and versioning strategy
- define how curriculum sections and entries are represented
- define how CVN source traceability survives in JSON
- define extension rules for future schema versions

## Background

The TFG requires a final JSON-based representation suitable for text files and
NoSQL-like storage. The format must be clearer than CVN XML while preserving
traceability to official CVN sources.

## Design Questions

1. What is the root object name and metadata shape?
2. How are curriculum sections grouped?
3. Are entries keyed by stable semantic names, CVN codes, or both?
4. How are repeated entries represented?
5. Where does source trace metadata live?
6. How are controlled references represented?
7. How are unresolved or under-traced CVN references represented?
8. How does the schema allow future extension without breaking old data?

## Planned Steps

1. review conceptual IR from issue `#43`
2. review JSON Schema generation findings from issue `#45`
3. define root metadata fields such as schema version, source, language, and
   generated timestamp policy
4. define section and entry structure
5. define trace metadata conventions
6. define controlled-reference JSON shapes
7. define extension and compatibility rules
8. document examples for representative personal, academic, and research data
9. update JSON Schema generation plan if needed

## Accepted Execution Protocol

The user accepted the execution plan before issue `#46` implementation starts.

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
- generated domain code under `src/models/cvn/generated/` must not be edited
  manually

## Accepted Execution Plan

### Task `1 / 18` - Confirm Issue Scope

- Task summary:
  - confirm the boundaries of issue `#46` before implementation work starts
- Files involved:
  - `docs/roadmap/issues/issue-46-define-canonical-open-cvn-json-format.md`
  - `docs/roadmap/issues/issue-43-agnostic-conceptual-model-extraction-layer.md`
  - `docs/roadmap/issues/issue-45-generate-json-schema-from-domain-models.md`
  - `docs/pipeline/json_schema_generation.md`
  - `schemas/open_cvn.schema.json`
- Subtask `1.1 / 18`:
  - confirm that issue `#46` defines the canonical Open CVN JSON document format
- Subtask `1.2 / 18`:
  - confirm that parser implementation, XML/PDF import, storage, UI, and export
    workflows remain out of scope
- Subtask `1.3 / 18`:
  - decide whether issue `#46` only documents the canonical format or also updates
    the generated JSON Schema artifact from issue `#45`
- User manual modifications needed:
  - none expected for scope confirmation
- Next step:
  - inventory the real evidence sources from issues `#43` and `#45`

### Task `2 / 18` - Inventory Real Evidence Sources

- Task summary:
  - identify the existing artifacts that can support canonical JSON decisions
- Files involved:
  - `src/cvn_codegen/conceptual_model_types.py`
  - `src/cvn_codegen/conceptual_model_extractor.py`
  - `src/cvn_codegen/json_schema_generator.py`
  - `schemas/open_cvn.schema.json`
  - `docs/pipeline/conceptual_model_extraction.md`
  - `docs/pipeline/json_schema_generation.md`
  - `docs/pipeline/known_limitations.md`
- Subtask `2.1 / 18`:
  - review `ConceptualModelInventory` as the conceptual source of truth
- Subtask `2.2 / 18`:
  - review the issue `#45` provisional root fields: `schema_version`,
    `policy_name`, `policy_version`, and `curriculum`
- Subtask `2.3 / 18`:
  - review representative definitions for `core.curriculum`, `identity.person`,
    vocabularies, and shared wrapper values
- Subtask `2.4 / 18`:
  - record active limitations that affect the canonical JSON format, especially
    conservative relationships and non-validating schema trace extensions
- User manual modifications needed:
  - none expected; this task is read-only
- Next step:
  - decide the root object and metadata shape

### Task `3 / 18` - Decide Root Object And Metadata Shape

- Task summary:
  - define the top-level Open CVN JSON object and stable metadata fields
- Files involved if documentation is authorized:
  - `docs/open_cvn_json_format.md` or
    `docs/pipeline/open_cvn_json_format.md`
  - `docs/pipeline/json_schema_generation.md`
- Candidate root fields:
  - `schema_version`
  - `metadata`
  - `curriculum`
  - `extensions`
- Candidate metadata fields:
  - `language`
  - `source`
  - `created_at`
  - `updated_at`
  - `generator`
  - `policy`
- Subtask `3.1 / 18`:
  - decide whether to keep `schema_version` as the root format version field or
    introduce a different name such as `open_cvn_version`
- Subtask `3.2 / 18`:
  - decide whether `policy_name` and `policy_version` remain root fields or move
    under `metadata.policy`
- Subtask `3.3 / 18`:
  - define creation and update timestamp policy, including when generated
    timestamps are allowed or omitted
- Subtask `3.4 / 18`:
  - define language metadata for Spanish-first CVN content without making the
    whole format language-specific
- User manual modifications needed:
  - documentation changes are required only if explicitly authorized; code/schema
    changes remain user-owned unless implementation is authorized
- Next step:
  - define format versioning and compatibility rules

### Task `4 / 18` - Define Versioning And Compatibility Rules

- Task summary:
  - define how Open CVN JSON versions evolve without breaking old data
- Files involved if documentation is authorized:
  - `docs/open_cvn_json_format.md` or
    `docs/pipeline/open_cvn_json_format.md`
- Subtask `4.1 / 18`:
  - define the initial canonical version, expected to start at `0.1.0`
- Subtask `4.2 / 18`:
  - define patch, minor, and major compatibility meaning for the JSON format
- Subtask `4.3 / 18`:
  - define parser expectations for same-major versions, future minor versions, and
    unknown major versions
- Subtask `4.4 / 18`:
  - distinguish Open CVN format versioning from JSON Schema Draft 2020-12
    metadata
- User manual modifications needed:
  - documentation changes are required only if explicitly authorized
- Next step:
  - define curriculum sections and entry layout

### Task `5 / 18` - Define Curriculum Section And Entry Layout

- Task summary:
  - define how curriculum content is grouped into JSON sections and entries
- Files involved if documentation is authorized:
  - `docs/open_cvn_json_format.md` or
    `docs/pipeline/open_cvn_json_format.md`
  - `docs/pipeline/conceptual_model_extraction.md` for source rules only if a
    cross-reference update is needed
- Initial section candidates:
  - `identity`
  - `education`
  - `research`
  - `professional_experience`
  - `achievements`
  - `other`
- Candidate entry fields:
  - `id`
  - `type`
  - `data`
  - `trace`
  - `extensions`
- Subtask `5.1 / 18`:
  - decide whether `curriculum` is grouped by conceptual domain areas from issue
    `#43`
- Subtask `5.2 / 18`:
  - decide whether repeated sections are arrays of entries or keyed objects
- Subtask `5.3 / 18`:
  - define stable entry identifiers and avoid generated Python names such as
    `cvn_item_*`
- Subtask `5.4 / 18`:
  - define how fallback or weakly classified areas are represented without losing
    traceability
- User manual modifications needed:
  - documentation changes are required only if explicitly authorized
- Next step:
  - define repeated-entry ordering and identity rules

### Task `6 / 18` - Define Repeated Entry Rules

- Task summary:
  - define how repeated academic, research, professional, and other curriculum
    entries are represented
- Files involved if documentation is authorized:
  - `docs/open_cvn_json_format.md` or
    `docs/pipeline/open_cvn_json_format.md`
- Subtask `6.1 / 18`:
  - define arrays as the canonical shape for repeated entries
- Subtask `6.2 / 18`:
  - define whether array order preserves source order, chronological order, or only
    document order
- Subtask `6.3 / 18`:
  - define optional `id` or `entry_id` behavior for imported records without a
    stable external identifier
- Subtask `6.4 / 18`:
  - define representative repeated-entry examples for education and research
- User manual modifications needed:
  - documentation changes are required only if explicitly authorized
- Next step:
  - define field representation rules

### Task `7 / 18` - Define Field Representation Rules

- Task summary:
  - define how conceptual attributes become JSON fields
- Files involved if documentation is authorized:
  - `docs/open_cvn_json_format.md` or
    `docs/pipeline/open_cvn_json_format.md`
  - `docs/pipeline/open_cvn_json_mapping.md` if mapping notes are split out
- Subtask `7.1 / 18`:
  - define field naming from stable semantic names rather than CVN XML names or
    generated Python identifiers
- Subtask `7.2 / 18`:
  - define primitive value shapes for text, date-like values, duration-like values,
    numbers, booleans, and unknown values
- Subtask `7.3 / 18`:
  - define wrapper value object usage for `FlexibleDateValue`, `OfficialIdValue`,
    `EntityTypeValue`, and `EntityNameValue`
- Subtask `7.4 / 18`:
  - define the difference between omitted fields and explicit `null`
- Subtask `7.5 / 18`:
  - define how permissive or unknown fields are represented without hiding
    limitations
- User manual modifications needed:
  - documentation changes are required only if explicitly authorized
- Next step:
  - define controlled-reference JSON shapes

### Task `8 / 18` - Define Controlled-Reference JSON Shapes

- Task summary:
  - define how CVN controlled references, code lists, registries, thesauri, and
    unresolved references appear in JSON
- Files involved if documentation is authorized:
  - `docs/open_cvn_json_format.md` or
    `docs/pipeline/open_cvn_json_format.md`
  - `docs/pipeline/open_cvn_json_mapping.md` if mapping notes are split out
- Candidate controlled-reference fields:
  - `code`
  - `label`
  - `source`
  - `raw_value`
  - `uri`
  - `reference_status`
- Representative cases:
  - `CVN_SEX_A`
  - `CVN_ENTITY_TYPE`
  - `CVN_KNOW_A`
  - `ENTITY@Entity.xsd`
  - `THESAURUS@thesaurus.xsd`
  - `UNESCO_CODES`
  - `CVN_AGENCY_C`
- Subtask `8.1 / 18`:
  - define closed enum behavior only when semantic policy marks the source as
    enum-eligible
- Subtask `8.2 / 18`:
  - define open code-list behavior for enum-ineligible or review-required
    reference tables
- Subtask `8.3 / 18`:
  - define registry, thesaurus, hierarchical, subtype-backed, unresolved, and
    under-traced reference shapes
- Subtask `8.4 / 18`:
  - define how labels and raw input values are preserved when codes are missing or
    unresolved
- User manual modifications needed:
  - documentation changes are required only if explicitly authorized
- Next step:
  - define CVN trace metadata placement and shape

### Task `9 / 18` - Define CVN Trace Metadata Rules

- Task summary:
  - define how source CVN identifiers survive in the canonical JSON format
- Files involved if documentation is authorized:
  - `docs/open_cvn_json_format.md` or
    `docs/pipeline/open_cvn_json_format.md`
  - `docs/pipeline/open_cvn_json_mapping.md` if mapping notes are split out
- Candidate trace fields:
  - `cvn_codes`
  - `xml_paths`
  - `source_artifacts`
  - `manual_reference_table`
  - `semantic_kind`
  - `domain_shape_kind`
  - `confidence`
- Subtask `9.1 / 18`:
  - decide when trace lives at entry level, field level, or both
- Subtask `9.2 / 18`:
  - define minimal trace required for round-trip auditability
- Subtask `9.3 / 18`:
  - map issue `#45` non-validating `x-open-cvn-*` schema extensions into runtime
    JSON `trace` objects where useful
- Subtask `9.4 / 18`:
  - define trace as audit metadata rather than business data that changes value
    semantics
- User manual modifications needed:
  - documentation changes are required only if explicitly authorized
- Next step:
  - define extension rules

### Task `10 / 18` - Define Extension Rules

- Task summary:
  - define safe future extension behavior for the Open CVN JSON format
- Files involved if documentation is authorized:
  - `docs/open_cvn_json_format.md` or
    `docs/pipeline/open_cvn_json_format.md`
- Subtask `10.1 / 18`:
  - define the `extensions` object as the canonical location for project- or
    tool-specific metadata
- Subtask `10.2 / 18`:
  - define extension key naming, such as reverse-DNS names or `x-*` keys
- Subtask `10.3 / 18`:
  - define that consumers must ignore unknown extensions unless configured to be
    strict
- Subtask `10.4 / 18`:
  - define that extensions must not override canonical fields
- User manual modifications needed:
  - documentation changes are required only if explicitly authorized
- Next step:
  - write the canonical format specification

### Task `11 / 18` - Write Canonical Format Specification

- Task summary:
  - create or update the authoritative documentation for the canonical Open CVN
    JSON format
- Files involved if documentation is authorized:
  - `docs/open_cvn_json_format.md` or
    `docs/pipeline/open_cvn_json_format.md`
- Required sections:
  - purpose
  - source of truth
  - root object
  - metadata
  - curriculum sections
  - entries
  - fields
  - controlled references
  - trace metadata
  - extensions
  - versioning
  - compatibility
  - examples
  - relationship to issues `#43`, `#45`, and `#49`
  - limitations
- Subtask `11.1 / 18`:
  - define document location and title
- Subtask `11.2 / 18`:
  - write the normative root and section format rules
- Subtask `11.3 / 18`:
  - write field, controlled-reference, trace, and extension rules
- Subtask `11.4 / 18`:
  - write versioning and compatibility rules
- User manual modifications needed:
  - documentation changes are required unless the user authorizes the agent to edit
    them
- Next step:
  - write mapping notes from conceptual/domain evidence to JSON

### Task `12 / 18` - Write Mapping Notes

- Task summary:
  - document how existing conceptual inventory and schema evidence map into the
    canonical JSON format
- Files involved if documentation is authorized:
  - `docs/pipeline/open_cvn_json_mapping.md` or a mapping section inside the
    canonical format specification
- Required mappings:
  - conceptual entity to JSON section or entry
  - conceptual attribute to JSON field
  - conceptual vocabulary to controlled reference
  - schema `x-open-cvn-*` extension to runtime trace metadata
  - wrapper value object to JSON object
  - unresolved or under-traced reference to explicit status
  - XML/Python exclusion rule to stable JSON naming
- Subtask `12.1 / 18`:
  - map `ConceptualModelInventory` records into JSON document concepts
- Subtask `12.2 / 18`:
  - map issue `#45` JSON Schema definitions into canonical runtime examples
- Subtask `12.3 / 18`:
  - document known non-mappings, especially generated Python module names and raw
    XML mechanics
- User manual modifications needed:
  - documentation changes are required unless the user authorizes the agent to edit
    them
- Next step:
  - create representative JSON examples

### Task `13 / 18` - Create Representative JSON Examples

- Task summary:
  - provide concrete JSON examples for implementers and future parser tests
- Files involved if documentation/examples are authorized:
  - `examples/open_cvn/minimal.json`
  - `examples/open_cvn/identity.json`
  - `examples/open_cvn/education_entry.json`
  - `examples/open_cvn/research_entry.json`
  - `examples/open_cvn/controlled_references.json`
  - `examples/open_cvn/trace_and_extensions.json`
- Subtask `13.1 / 18`:
  - create a minimal valid Open CVN JSON document
- Subtask `13.2 / 18`:
  - create a representative identity example using official-id and person fields
- Subtask `13.3 / 18`:
  - create an education or academic-history repeated-entry example
- Subtask `13.4 / 18`:
  - create a research-entry example with repeated content and trace metadata
- Subtask `13.5 / 18`:
  - create controlled-reference examples for closed, open, hierarchical, thesaurus,
    registry, and unresolved cases
- User manual modifications needed:
  - example file changes are required unless the user authorizes the agent to edit
    them
- Next step:
  - align the generated JSON Schema with the canonical format if needed

### Task `14 / 18` - Align JSON Schema Generation With Canonical Format

- Task summary:
  - decide and implement or document the relationship between the issue `#45`
    generated schema and the issue `#46` canonical JSON format
- Files involved if code/schema work is authorized:
  - `src/cvn_codegen/json_schema_generator.py`
  - `schemas/open_cvn.schema.json`
  - `docs/pipeline/json_schema_generation.md`
  - `tests/test_json_schema_generator_unit.py`
  - `tests/test_generation_pipeline_json_schema.py`
- Subtask `14.1 / 18`:
  - compare the canonical root format against the issue `#45` provisional root
- Subtask `14.2 / 18`:
  - if authorized, update the generator root layout while preserving conceptual
    `$defs`
- Subtask `14.3 / 18`:
  - regenerate `schemas/open_cvn.schema.json` if generator changes are authorized
- Subtask `14.4 / 18`:
  - if code changes are not authorized, document the exact delta as a follow-up
    before issue `#49`
- User manual modifications needed:
  - code and generated schema changes should be done by the user unless the user
    explicitly authorizes the agent to edit code/schema artifacts
- Next step:
  - add validation tests for examples and schema behavior if implementation is
    authorized

### Task `15 / 18` - Add Tests For Format Examples And Schema Behavior

- Task summary:
  - verify that the canonical examples and schema behavior match the issue `#46`
    decisions
- Files involved if tests are authorized:
  - `tests/test_open_cvn_json_format_examples.py`
  - `tests/test_json_schema_generator_unit.py`
  - `tests/test_generation_pipeline_json_schema.py`
- Subtask `15.1 / 18`:
  - test that all example files are valid JSON
- Subtask `15.2 / 18`:
  - test that examples validate against `schemas/open_cvn.schema.json` when the
    schema has been aligned to the canonical format
- Subtask `15.3 / 18`:
  - test canonical root fields and metadata policy
- Subtask `15.4 / 18`:
  - test controlled-reference examples for closed enum, open code list, and
    unresolved reference behavior
- Subtask `15.5 / 18`:
  - test that trace metadata remains optional but valid where present
- User manual modifications needed:
  - test changes should be done by the user unless the user explicitly authorizes
    the agent to edit tests
- Next step:
  - run regeneration and verification commands if implementation is authorized

### Task `16 / 18` - Regenerate And Verify Artifacts

- Task summary:
  - run the strongest available verification after documentation, example, schema,
    or test changes
- Commands if schema/test work is authorized:
  - `uv run python -m cvn_codegen.json_schema_generator`
  - `uv run pytest -n auto tests/test_json_schema_generator_unit.py tests/test_generation_pipeline_json_schema.py tests/test_open_cvn_json_format_examples.py -v`
  - `uv run pytest -n auto tests`
- Subtask `16.1 / 18`:
  - regenerate the canonical JSON Schema if generator changes were made
- Subtask `16.2 / 18`:
  - run targeted tests for schema generation and examples
- Subtask `16.3 / 18`:
  - run the full repository test suite when practical
- Subtask `16.4 / 18`:
  - record any skipped verification with the exact reason and strongest executed
    substitute
- User manual modifications needed:
  - none expected for command execution if the agent is authorized to run commands
- Next step:
  - update persistent documentation and roadmap state

### Task `17 / 18` - Update Persistent Documentation

- Task summary:
  - record issue `#46` implementation outcome and keep repository context aligned
- Files involved:
  - `docs/roadmap/issues/issue-46-define-canonical-open-cvn-json-format.md`
  - `docs/context/current_status.md`
  - `docs/roadmap/cvn_generation_roadmap.md`
  - `docs/pipeline/json_schema_generation.md`
  - `docs/pipeline/known_limitations.md` only if a new limitation is found
  - `PROJECT_GUIDE.md` only if human-facing document maps or repository
    orientation change
- Subtask `17.1 / 18`:
  - add implementation summary, artifacts, decisions, deviations, and verification
    to issue `#46`
- Subtask `17.2 / 18`:
  - update current status with issue `#46` outcome and next planned issue `#47`
- Subtask `17.3 / 18`:
  - update roadmap status if issue `#46` is completed
- Subtask `17.4 / 18`:
  - update JSON Schema generation documentation if the provisional root changes or
    remains a known delta
- Subtask `17.5 / 18`:
  - update known limitations only if a durable new limitation is discovered
- Subtask `17.6 / 18`:
  - update `PROJECT_GUIDE.md` only if new document or example paths become
    contributor entry-point knowledge
- User manual modifications needed:
  - documentation changes are required unless the user authorizes the agent to edit
    them
- Next step:
  - verify issue closure criteria

### Task `18 / 18` - Verify Issue Closure

- Task summary:
  - confirm issue `#46` is ready for parser and validation work in later issues
- Closure checks:
  - root object and metadata shape are defined
  - curriculum sections and repeated entries are defined
  - field naming and wrapper value rules are defined
  - controlled-reference and unresolved-reference shapes are defined
  - CVN trace metadata is preserved
  - extension and compatibility rules are defined
  - representative examples exist if implementation is authorized
  - schema alignment or schema delta is recorded before issue `#49`
  - format is not XML-centric
  - no generated structural or generated domain code was manually edited
- Subtask `18.1 / 18`:
  - review the issue `#46` design questions and confirm each has an explicit answer
- Subtask `18.2 / 18`:
  - review representative examples and schema alignment status
- Subtask `18.3 / 18`:
  - confirm issue `#47` and issue `#49` can consume the canonical format without
    redesigning the root shape
- User manual modifications needed:
  - none expected after closure verification; any required manual changes should
    have been recorded earlier
- Next step:
  - proceed to issue `#47` only after the user accepts issue `#46` closure

## Expected Output

- canonical Open CVN JSON format specification under `docs/`
- representative JSON examples
- mapping notes from CVN/domain Pydantic fields to JSON
- decisions for future versioning

## Implementation Summary

- The canonical Open CVN JSON format is documented in:
  `docs/pipeline/open_cvn_json_format.md`
- Mapping notes from the issue `#43` conceptual inventory and issue `#45` schema
  annotations to runtime JSON are documented in:
  `docs/pipeline/open_cvn_json_mapping.md`
- Representative JSON examples are provided under:
  `examples/open_cvn/`
- The issue `#45` JSON Schema generator now emits the issue `#46` canonical root
  shape with:
  - `schema_version`
  - `metadata`
  - `curriculum`
  - `extensions`
- Semantic policy metadata now lives under `metadata.policy` instead of root-level
  `policy_name` and `policy_version` fields.
- The generated JSON Schema artifact remains:
  `schemas/open_cvn.schema.json`
- The schema artifact now identifies issue `#46` as the source issue for the
  canonical root shape.

## Implementation Decisions

- `schema_version` remains the root Open CVN format-version field.
- `metadata` is required and includes `language` and `policy` as required fields.
- `curriculum` is grouped by conceptual domain areas rather than CVN XML
  structures or generated Python modules.
- `identity` is represented as a single object, while education, research,
  professional experience, achievements, and fallback content are represented as
  arrays of entries.
- Repeated-section entries use `type` and `data` as required fields, with optional
  `id`, `trace`, and `extensions`.
- Controlled references use a common shape with `code`, `label`, `source`,
  `raw_value`, `uri`, and `reference_status`.
- Closed enum validation remains limited to enum-eligible vocabularies such as
  `CVN_SEX_A`; enum-ineligible and unresolved references remain open.
- Runtime trace metadata is represented through `trace` objects rather than
  requiring schema-only `x-open-cvn-*` annotations to appear in data files.

## Artifacts Created Or Updated

- `docs/pipeline/open_cvn_json_format.md`
- `docs/pipeline/open_cvn_json_mapping.md`
- `examples/open_cvn/minimal.json`
- `examples/open_cvn/identity.json`
- `examples/open_cvn/education_entry.json`
- `examples/open_cvn/research_entry.json`
- `examples/open_cvn/controlled_references.json`
- `examples/open_cvn/trace_and_extensions.json`
- `src/cvn_codegen/json_schema_generator.py`
- `schemas/open_cvn.schema.json`
- `tests/test_json_schema_generator_unit.py`
- `tests/test_generation_pipeline_json_schema.py`
- `tests/test_open_cvn_json_format_examples.py`

## Verification Performed

- Canonical JSON Schema regeneration passed with:
  `uv run python -m cvn_codegen.json_schema_generator`
- Targeted issue `#46` verification passed with:
  `uv run pytest -n auto tests/test_json_schema_generator_unit.py tests/test_generation_pipeline_json_schema.py tests/test_open_cvn_json_format_examples.py -v`
- Targeted verification result:
  `21 passed in 159.97s (0:02:39)`
- Full-suite verification passed with:
  `uv run pytest -n auto tests`
- Full-suite verification result:
  `334 passed in 890.21s (0:14:50)`

## Verification

- examples are valid JSON and follow the canonical root, section, entry,
  controlled-reference, trace, and extension conventions
- the generated schema validates the canonical root shape defined by issue `#46`
- format is not XML-centric
- traceability to CVN source identifiers remains preserved

## Impact On Later Issues

- issue `#49` imports and validates this JSON format
- epic `#60` stores, edits, and exports this format

## Status

- Status: completed
