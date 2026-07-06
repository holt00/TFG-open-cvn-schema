# Issue 49 - Implement XML And JSON Import Validation

## Summary

Issue `#49` implements direct CVN XML import and Open CVN JSON import validation
using the parser contract from issue `#47`.

This issue is part of epic `#41`.

## Goal

- import CVN XML into validated domain/Open CVN data
- import Open CVN JSON and validate it against Pydantic and JSON Schema rules
- preserve source traceability and structured validation errors

## Background

The repository already has structural CVN bindings and domain-generation logic,
but the final parser must consume user inputs, not only source package metadata.
This issue starts the parser/validator implementation for direct XML and JSON
inputs.

## XML Import Direction

The XML path should:

1. parse CVN XML using structural bindings where useful
2. map structural CVN values into the domain/Open CVN shape
3. validate mapped data with Pydantic domain models
4. preserve CVN codes and source paths where available
5. report structural or semantic validation failures clearly

## JSON Import Direction

The JSON path should:

1. load JSON safely
2. validate against Open CVN Pydantic models
3. validate against generated JSON Schema when available
4. report schema and Pydantic errors through the common parser contract
5. preserve version and trace metadata

## Planned Steps

1. consume parser result and error contract from issue `#47`
2. implement XML input loading and structural parse path if approved
3. implement XML-to-domain/Open CVN mapping prototype
4. implement JSON loading and validation path
5. integrate JSON Schema artifact from issue `#45`
6. add valid and invalid fixtures
7. add tests for structured errors and trace preservation
8. document parser examples

## Accepted Execution Protocol

For each execution step, the implementer must report:

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

### Task `1 / 21` - Confirm Baseline

- Task summary:
  - confirm the existing parser contract, JSON Schema artifact, examples, and test
    baseline before implementation work starts
- Files involved:
  - `src/open_cvn/parser_contract.py`
  - `schemas/open_cvn.schema.json`
  - `examples/open_cvn/*.json`
  - `tests/test_parser_validator_contract_unit.py`
  - `tests/test_open_cvn_json_format_examples.py`
- Subtask `1.1 / 21`:
  - review the current XML and JSON stubs in `parser_contract.py`
- Subtask `1.2 / 21`:
  - review the generated Open CVN JSON Schema artifact
- Subtask `1.3 / 21`:
  - review representative Open CVN JSON examples
- Subtask `1.4 / 21`:
  - review existing parser contract and JSON format tests
- User manual modifications needed:
  - none expected; this task is read-only
- Next step:
  - design runtime Open CVN validation models

### Task `2 / 21` - Design Runtime Open CVN Models

- Task summary:
  - define the Pydantic runtime model layer used by JSON import validation without
    exposing generated structural or generated domain modules as the public JSON
    contract
- Files involved if code implementation is authorized:
  - `src/open_cvn/open_cvn_models.py`
  - `src/open_cvn/__init__.py` if public exports are needed
- Subtask `2.1 / 21`:
  - model the root fields `schema_version`, `metadata`, `curriculum`, and
    `extensions`
- Subtask `2.2 / 21`:
  - model `metadata.policy.name` and `metadata.policy.version`
- Subtask `2.3 / 21`:
  - model optional metadata fields such as `language`, `source`, `created_at`,
    `updated_at`, and `generator`
- Subtask `2.4 / 21`:
  - model `curriculum.identity` as a single object and repeated curriculum
    sections as entry arrays
- Subtask `2.5 / 21`:
  - model repeated entries with `id`, `type`, `data`, `trace`, and `extensions`
- Subtask `2.6 / 21`:
  - choose open or strict `extra` behavior per model according to issue `#46`
    extension rules
- User manual modifications needed:
  - code files must be modified by the user unless code editing is explicitly
    authorized
- Next step:
  - implement common parser result helpers

### Task `3 / 21` - Implement Common Parser Utilities

- Task summary:
  - create shared helpers for input classification, trace construction, and
    structured issue conversion so XML and JSON paths behave consistently
- Files involved if code implementation is authorized:
  - `src/open_cvn/parser_contract.py`
  - optional helper module such as `src/open_cvn/import_utils.py`
- Subtask `3.1 / 21`:
  - classify `Path`, `str`, `bytes`, and `Mapping` inputs consistently
- Subtask `3.2 / 21`:
  - distinguish existing filesystem paths from inline JSON or XML text
- Subtask `3.3 / 21`:
  - create a common `CvnParseTrace` builder
- Subtask `3.4 / 21`:
  - create reusable `CvnParseIssue` builders for warning and error cases
- Subtask `3.5 / 21`:
  - convert Pydantic validation errors into structured parser issues
- Subtask `3.6 / 21`:
  - convert JSON Schema validation errors into structured parser issues
- User manual modifications needed:
  - code files must be modified by the user unless code editing is explicitly
    authorized
- Next step:
  - add JSON Schema validation dependency and integration

### Task `4 / 21` - Add JSON Schema Validation Dependency

- Task summary:
  - add a runtime JSON Schema validator compatible with the generated Draft
    2020-12 schema artifact
- Files involved if code implementation is authorized:
  - `pyproject.toml`
  - dependency lock files if present after environment sync
- Subtask `4.1 / 21`:
  - add `jsonschema>=4.26` to runtime dependencies
- Subtask `4.2 / 21`:
  - use `Draft202012Validator.check_schema(...)` for schema sanity checks
- Subtask `4.3 / 21`:
  - use `Draft202012Validator(schema).iter_errors(document)` for deterministic
    multi-error collection
- Subtask `4.4 / 21`:
  - avoid optional format extras unless a later validation requirement needs them
- User manual modifications needed:
  - dependency files must be modified by the user unless code editing is
    explicitly authorized
- Next step:
  - implement Open CVN JSON loading

### Task `5 / 21` - Implement Open CVN JSON Loading

- Task summary:
  - implement `parse_open_cvn_json(...)` input loading while preserving the issue
    `#47` result and error contract
- Files involved if code implementation is authorized:
  - `src/open_cvn/parser_contract.py`
  - optional helper module such as `src/open_cvn/json_import.py`
- Subtask `5.1 / 21`:
  - accept JSON from path inputs
- Subtask `5.2 / 21`:
  - accept inline JSON strings
- Subtask `5.3 / 21`:
  - accept JSON bytes
- Subtask `5.4 / 21`:
  - accept already-loaded mappings and route them to `validate_open_cvn_json(...)`
- Subtask `5.5 / 21`:
  - return `invalid_json` for malformed JSON with line and column detail when
    available
- Subtask `5.6 / 21`:
  - return `unreadable_file` for unreadable path input
- Subtask `5.7 / 21`:
  - preserve `schema_version`, `metadata.policy.name`, and
    `metadata.policy.version` in trace metadata
- User manual modifications needed:
  - code files must be modified by the user unless code editing is explicitly
    authorized
- Next step:
  - implement JSON Schema validation

### Task `6 / 21` - Implement JSON Schema Validation

- Task summary:
  - validate loaded Open CVN JSON documents against
    `schemas/open_cvn.schema.json` and normalize validation failures into the
    common parser contract
- Files involved if code implementation is authorized:
  - `src/open_cvn/json_import.py`
  - `schemas/open_cvn.schema.json` only if regeneration is required by a detected
    schema issue
- Subtask `6.1 / 21`:
  - load the canonical schema artifact from a stable repository-relative path
- Subtask `6.2 / 21`:
  - validate the schema artifact against Draft 2020-12 meta-schema
- Subtask `6.3 / 21`:
  - validate JSON documents and collect all schema errors deterministically
- Subtask `6.4 / 21`:
  - map schema failures to `json_schema_validation_failure`
- Subtask `6.5 / 21`:
  - include serializable diagnostics such as validator name, validator value, and
    message in issue details
- User manual modifications needed:
  - code files must be modified by the user unless code editing is explicitly
    authorized
- Next step:
  - implement Pydantic runtime validation

### Task `7 / 21` - Implement Pydantic Runtime Validation

- Task summary:
  - validate JSON documents against Open CVN runtime models after JSON Schema has
    accepted the external document shape
- Files involved if code implementation is authorized:
  - `src/open_cvn/open_cvn_models.py`
  - `src/open_cvn/json_import.py`
  - `src/open_cvn/parser_contract.py`
- Subtask `7.1 / 21`:
  - implement `validate_open_cvn_json(document, *, source_identifier=None)`
- Subtask `7.2 / 21`:
  - reject non-mapping documents through `pydantic_validation_failure`
- Subtask `7.3 / 21`:
  - run JSON Schema validation before Pydantic runtime validation
- Subtask `7.4 / 21`:
  - map Pydantic validation errors to `pydantic_validation_failure`
- Subtask `7.5 / 21`:
  - return `valid` with normalized data and trace when both validation layers pass
- Subtask `7.6 / 21`:
  - return `valid_with_warnings` only when warning issues exist
- User manual modifications needed:
  - code files must be modified by the user unless code editing is explicitly
    authorized
- Next step:
  - implement Open CVN JSON versioning rules

### Task `8 / 21` - Implement Open CVN JSON Versioning Rules

- Task summary:
  - enforce issue `#46` parser expectations for compatible, future, and unknown
    Open CVN JSON versions
- Files involved if code implementation is authorized:
  - `src/open_cvn/open_cvn_models.py`
  - `src/open_cvn/json_import.py`
  - tests covering accepted and rejected versions
- Subtask `8.1 / 21`:
  - accept the initial canonical version `0.1.0`
- Subtask `8.2 / 21`:
  - reject unknown major versions unless a future configuration explicitly allows
    best-effort parsing
- Subtask `8.3 / 21`:
  - emit a warning for newer compatible minor versions if the schema permits them
- Subtask `8.4 / 21`:
  - keep Open CVN format versioning separate from JSON Schema draft metadata
- User manual modifications needed:
  - code files must be modified by the user unless code editing is explicitly
    authorized
- Next step:
  - implement CVN XML loading

### Task `9 / 21` - Implement CVN XML Loading

- Task summary:
  - implement `parse_cvn_xml(...)` input loading, XML well-formedness checks, and
    basic CVN plausibility classification
- Files involved if code implementation is authorized:
  - `src/open_cvn/parser_contract.py`
  - optional helper module such as `src/open_cvn/xml_import.py`
- Subtask `9.1 / 21`:
  - accept XML from path inputs
- Subtask `9.2 / 21`:
  - accept inline XML strings
- Subtask `9.3 / 21`:
  - accept XML bytes
- Subtask `9.4 / 21`:
  - reject mapping input as `unsupported_input_format`
- Subtask `9.5 / 21`:
  - classify unreadable paths as `unreadable_file`
- Subtask `9.6 / 21`:
  - classify malformed XML as `invalid_xml`
- Subtask `9.7 / 21`:
  - classify well-formed but non-CVN XML as `xml_semantically_unmappable`
- User manual modifications needed:
  - code files must be modified by the user unless code editing is explicitly
    authorized
- Next step:
  - implement XML trace extraction

### Task `10 / 21` - Implement XML Trace Extraction

- Task summary:
  - extract portable trace metadata from CVN XML without leaking personal data into
    parser diagnostics
- Files involved if code implementation is authorized:
  - `src/open_cvn/xml_import.py`
  - XML fixture files under `tests/fixtures/` if tests are implemented
- Subtask `10.1 / 21`:
  - extract the root XML path
- Subtask `10.2 / 21`:
  - collect simplified XML paths for relevant elements
- Subtask `10.3 / 21`:
  - detect CVN code-like values from tags, attributes, and text when reliable
- Subtask `10.4 / 21`:
  - deduplicate trace values while preserving deterministic order
- Subtask `10.5 / 21`:
  - avoid copying full personal XML payloads into errors or trace details
- User manual modifications needed:
  - code files and fixtures must be modified by the user unless editing is
    explicitly authorized
- Next step:
  - evaluate structural binding reuse for XML parsing

### Task `11 / 21` - Evaluate XML Structural Binding Reuse

- Task summary:
  - decide whether existing generated structural bindings can safely support the
    XML import path without broad new mapping complexity
- Files involved:
  - `src/generated/cvn/`
  - generated binding smoke tests if existing
  - `src/open_cvn/xml_import.py` if implementation is authorized
- Subtask `11.1 / 21`:
  - identify generated CVN root binding classes and parser support already present
- Subtask `11.2 / 21`:
  - try structural parse on synthetic XML fixtures if implementation is authorized
- Subtask `11.3 / 21`:
  - use structural bindings only if they improve validation without breaking the
    issue `#47` public contract
- Subtask `11.4 / 21`:
  - fall back to ElementTree-based import and document the limitation if binding
    reuse is not reliable enough
- User manual modifications needed:
  - no generated files may be edited manually; code changes require explicit
    authorization
- Next step:
  - implement XML-to-Open-CVN mapping prototype

### Task `12 / 21` - Implement XML-To-Open-CVN Mapping Prototype

- Task summary:
  - create a conservative XML-to-Open-CVN mapping path that preserves trace and
    does not invent unavailable semantic mappings
- Files involved if code implementation is authorized:
  - `src/open_cvn/xml_import.py`
  - `src/open_cvn/open_cvn_models.py`
- Subtask `12.1 / 21`:
  - produce an Open CVN root document with `schema_version`, `metadata`,
    `curriculum`, and `extensions`
- Subtask `12.2 / 21`:
  - set `metadata.source` from XML source identity
- Subtask `12.3 / 21`:
  - preserve import diagnostics under a documented extension key
- Subtask `12.4 / 21`:
  - map identity fields only when source evidence is stable
- Subtask `12.5 / 21`:
  - return `xml_semantically_unmappable` when XML is readable but current semantic
    evidence cannot produce trustworthy Open CVN data
- Subtask `12.6 / 21`:
  - record any mapping shortfall as a known limitation
- User manual modifications needed:
  - code files must be modified by the user unless code editing is explicitly
    authorized
- Next step:
  - document and test PDF-to-XML handoff behavior

### Task `13 / 21` - Integrate PDF-To-XML Handoff

- Task summary:
  - confirm issue `#48` PDF extraction remains extraction-only and document how to
    pass extracted XML into the issue `#49` XML import path
- Files involved if documentation or tests are authorized:
  - `docs/pipeline/parser_validator_contract.md`
  - PDF/XML parser tests
- Subtask `13.1 / 21`:
  - keep `parse_cvn_pdf(...)` return status as `not_run` on successful extraction
- Subtask `13.2 / 21`:
  - document that `data["xml_text"]` can be passed to `parse_cvn_xml(...)`
- Subtask `13.3 / 21`:
  - avoid adding OCR, page text reconstruction, or automatic PDF domain validation
    in this issue
- User manual modifications needed:
  - documentation/test files must be modified by the user unless editing is
    explicitly authorized
- Next step:
  - create valid and invalid fixtures

### Task `14 / 21` - Create Import Fixtures

- Task summary:
  - add deterministic synthetic fixtures for valid and invalid JSON and XML import
    scenarios without real personal data
- Files involved if fixture creation is authorized:
  - `tests/fixtures/open_cvn/`
  - `tests/fixtures/cvn_xml/`
- Subtask `14.1 / 21`:
  - create valid Open CVN JSON fixtures from existing examples
- Subtask `14.2 / 21`:
  - create malformed JSON fixture
- Subtask `14.3 / 21`:
  - create wrong-shape JSON fixture for schema failure
- Subtask `14.4 / 21`:
  - create JSON fixture for runtime Pydantic or version failure
- Subtask `14.5 / 21`:
  - create minimal synthetic CVN-like XML fixture
- Subtask `14.6 / 21`:
  - create malformed XML fixture
- Subtask `14.7 / 21`:
  - create well-formed non-CVN XML fixture
- User manual modifications needed:
  - fixture files must be modified by the user unless editing is explicitly
    authorized
- Next step:
  - add JSON import tests

### Task `15 / 21` - Add Open CVN JSON Import Tests

- Task summary:
  - verify JSON loading, JSON Schema validation, Pydantic validation, structured
    errors, and trace preservation
- Files involved if test implementation is authorized:
  - `tests/test_open_cvn_json_import_unit.py`
  - JSON fixtures under `tests/fixtures/open_cvn/`
- Subtask `15.1 / 21`:
  - test JSON path input
- Subtask `15.2 / 21`:
  - test inline JSON string input
- Subtask `15.3 / 21`:
  - test JSON bytes input
- Subtask `15.4 / 21`:
  - test mapping input
- Subtask `15.5 / 21`:
  - test malformed JSON returns `invalid_json`
- Subtask `15.6 / 21`:
  - test schema failures return `json_schema_validation_failure`
- Subtask `15.7 / 21`:
  - test runtime validation failures return `pydantic_validation_failure`
- Subtask `15.8 / 21`:
  - test valid JSON returns `valid` and preserves trace metadata
- User manual modifications needed:
  - test files must be modified by the user unless editing is explicitly
    authorized
- Next step:
  - add CVN XML import tests

### Task `16 / 21` - Add CVN XML Import Tests

- Task summary:
  - verify XML loading, well-formedness errors, semantic-unmappable errors, and
    trace preservation
- Files involved if test implementation is authorized:
  - `tests/test_cvn_xml_import_unit.py`
  - XML fixtures under `tests/fixtures/cvn_xml/`
- Subtask `16.1 / 21`:
  - test XML path input
- Subtask `16.2 / 21`:
  - test inline XML string input
- Subtask `16.3 / 21`:
  - test XML bytes input
- Subtask `16.4 / 21`:
  - test unreadable XML path returns `unreadable_file`
- Subtask `16.5 / 21`:
  - test malformed XML returns `invalid_xml`
- Subtask `16.6 / 21`:
  - test well-formed non-CVN XML returns `xml_semantically_unmappable`
- Subtask `16.7 / 21`:
  - test XML trace preserves paths and detected CVN codes
- User manual modifications needed:
  - test files must be modified by the user unless editing is explicitly
    authorized
- Next step:
  - update existing parser contract tests

### Task `17 / 21` - Update Existing Parser Contract Tests

- Task summary:
  - replace deferred XML and JSON expectations with concrete issue `#49` behavior
    while preserving issue `#47` result invariants
- Files involved if test implementation is authorized:
  - `tests/test_parser_validator_contract_unit.py`
  - `tests/test_pdf_xml_extraction_unit.py` only if PDF regression coverage needs
    adjustment
- Subtask `17.1 / 21`:
  - remove `NotImplementedError` expectations for XML and JSON functions
- Subtask `17.2 / 21`:
  - keep enum and result invariant tests unchanged unless the public contract
    changes
- Subtask `17.3 / 21`:
  - add contract-level smoke tests for XML and JSON result envelopes
- Subtask `17.4 / 21`:
  - confirm `parse_cvn_pdf(...)` behavior remains unchanged
- User manual modifications needed:
  - test files must be modified by the user unless editing is explicitly
    authorized
- Next step:
  - update parser usage documentation

### Task `18 / 21` - Update Parser Usage Documentation

- Task summary:
  - document concrete XML and JSON import behavior, examples, validation order,
    and known mapping limits
- Files involved if documentation updates are authorized:
  - `docs/pipeline/parser_validator_contract.md`
  - optional usage examples under `docs/` if needed
- Subtask `18.1 / 21`:
  - update JSON success and failure examples
- Subtask `18.2 / 21`:
  - update XML invalid and semantically-unmappable examples
- Subtask `18.3 / 21`:
  - document JSON Schema validation before Pydantic runtime validation
- Subtask `18.4 / 21`:
  - document dependency on the `jsonschema` package
- Subtask `18.5 / 21`:
  - document XML mapping limits if full semantic mapping remains incomplete
- User manual modifications needed:
  - documentation files may be modified by the agent when explicitly requested;
    otherwise user-owned
- Next step:
  - update the issue record

### Task `19 / 21` - Update Issue 49 Record

- Task summary:
  - record final implementation, deviations from the accepted plan, artifacts,
    verification, and remaining risks in the issue document
- Files involved:
  - `docs/roadmap/issues/issue-49-xml-json-import-validation.md`
- Subtask `19.1 / 21`:
  - update status from planned to implemented when implementation is complete
- Subtask `19.2 / 21`:
  - record files created or changed
- Subtask `19.3 / 21`:
  - record implementation adjustments and limitations
- Subtask `19.4 / 21`:
  - record exact verification commands and results
- User manual modifications needed:
  - documentation may be modified by the agent when explicitly requested;
    otherwise user-owned
- Next step:
  - update global project status documentation

### Task `20 / 21` - Update Global Project Documentation

- Task summary:
  - align persistent project state and limitation records with the completed issue
    `#49` implementation
- Files involved if documentation updates are authorized:
  - `docs/context/current_status.md`
  - `docs/pipeline/known_limitations.md`
  - `docs/roadmap/cvn_generation_roadmap.md`
  - `PROJECT_GUIDE.md` only if the human-facing map or orientation changes
- Subtask `20.1 / 21`:
  - update current status with implemented XML and JSON import validation behavior
- Subtask `20.2 / 21`:
  - update known limitations if XML semantic mapping remains partial or binding
    reuse is not viable
- Subtask `20.3 / 21`:
  - update roadmap status if issue `#49` changes state
- Subtask `20.4 / 21`:
  - update `PROJECT_GUIDE.md` only if repository orientation or documentation map
    changes
- User manual modifications needed:
  - documentation may be modified by the agent when explicitly requested;
    otherwise user-owned
- Next step:
  - run verification commands

### Task `21 / 21` - Verify Issue 49 Implementation

- Task summary:
  - run targeted and full verification to prove XML and JSON import validation work
    and no existing parser behavior regressed
- Files involved:
  - test suite under `tests/`
  - generated schema artifact only if regeneration is required
- Subtask `21.1 / 21`:
  - run targeted parser and JSON format tests
- Subtask `21.2 / 21`:
  - run new issue `#49` JSON import tests
- Subtask `21.3 / 21`:
  - run new issue `#49` XML import tests
- Subtask `21.4 / 21`:
  - run the full repository suite with `uv run pytest -n auto tests`
- Subtask `21.5 / 21`:
  - regenerate JSON Schema only if implementation finds schema drift or schema
    artifact defects
- Subtask `21.6 / 21`:
  - confirm no generated source files were manually edited
- User manual modifications needed:
  - none expected after implementation files are in place
- Next step:
  - close issue `#49` documentation with final verification results

## Expected Output

- XML import implementation if approved
- JSON import validation implementation if approved
- fixtures and tests for valid and invalid inputs
- documentation for parser usage

## Verification

- valid XML imports into expected domain/Open CVN shape
- invalid XML produces structured errors
- valid JSON validates against Pydantic and JSON Schema
- invalid JSON produces structured errors
- trace metadata survives import when available

## Implemented Outcome

- Runtime Open CVN JSON validation models were added under `src/open_cvn/`.
- `parse_open_cvn_json(...)` now accepts path, inline JSON string, JSON bytes, and
  mapping inputs.
- `validate_open_cvn_json(...)` validates Open CVN documents against the generated
  Draft 2020-12 schema artifact before applying Pydantic runtime model checks.
- JSON failures are normalized through the issue `#47` contract as:
  - `invalid_json`
  - `json_schema_validation_failure`
  - `pydantic_validation_failure`
- `parse_cvn_xml(...)` now accepts path, inline XML string, and XML bytes inputs.
- CVN XML import performs well-formedness checks, CVN plausibility checks, XML path
  trace extraction, and CVN code-like trace extraction.
- Plausible CVN XML currently maps to a conservative Open CVN trace-only document
  with `extensions["x-open-cvn.import"].mapping_status = "trace_only"`.
- Well-formed XML without CVN evidence returns `xml_semantically_unmappable`.
- Synthetic fixtures and tests were added for valid and invalid JSON/XML import
  cases.

## Implementation Adjustments

- Full semantic XML-to-domain mapping was not implemented in this issue because
  the available runtime layer does not yet expose enough curated mapping behavior
  to convert arbitrary CVN XML records into trustworthy domain entries.
- The XML path uses `xml.etree.ElementTree` for deterministic well-formedness and
  trace extraction instead of generated structural bindings. Generated bindings
  remain available, but this issue keeps XML import conservative rather than
  depending on broad structural-to-domain conversion.
- JSON Schema validation intentionally runs before Pydantic runtime validation.
  Therefore, some malformed or unsupported documents fail at the schema layer
  before runtime model checks execute.

## Artifacts Changed

- `pyproject.toml`
- `uv.lock`
- `src/open_cvn/import_utils.py`
- `src/open_cvn/json_import.py`
- `src/open_cvn/open_cvn_models.py`
- `src/open_cvn/xml_import.py`
- `src/open_cvn/parser_contract.py`
- `tests/fixtures/open_cvn/`
- `tests/fixtures/cvn_xml/`
- `tests/test_open_cvn_json_import_unit.py`
- `tests/test_cvn_xml_import_unit.py`
- `tests/test_parser_validator_contract_unit.py`
- `docs/pipeline/parser_validator_contract.md`

## Verification Performed

- Targeted issue `#49` verification passed with:
  `uv run pytest -n auto tests/test_open_cvn_json_import_unit.py tests/test_cvn_xml_import_unit.py tests/test_parser_validator_contract_unit.py -v`
- Targeted verification result:
  `28 passed in 16.04s`
- Full-suite verification passed with:
  `uv run pytest -n auto tests`
- Full-suite verification result:
  `369 passed in 347.12s (0:05:47)`

## Known Risks

- XML-to-domain mapping may require more semantic decisions than current domain
  generator exposes
- JSON Schema and Pydantic validation errors may need normalization for usability
- sample CVN XML files may include personal data and require synthetic fixtures

## Impact On Later Issues

- completes parser input support with issue `#48`
- epic `#51` consumes XML and JSON import/export behavior

## Status

- Status: implemented
