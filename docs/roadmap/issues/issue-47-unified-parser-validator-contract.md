# Issue 47 - Define Unified Parser And Validator Contract

## Summary

Issue `#47` defines the public parser and validator contract for importing CVN
data from PDF, XML, and JSON inputs.

This issue is part of epic `#41`.

## Goal

- define common input APIs for PDF, XML, and JSON
- define common result and error structures
- keep source-specific extraction separate from domain validation
- prepare implementation work for issues `#48` and `#49`

## Proposed API Direction

The parser should eventually expose functions similar to:

- `parse_cvn_pdf(...)`
- `parse_cvn_xml(...)`
- `parse_open_cvn_json(...)`
- `validate_open_cvn_json(...)`

Names are provisional and should follow repository conventions during
implementation.

## Result Contract

Parser results should include:

- source format
- source path or source identifier when available
- parsed domain object or validated JSON object
- validation status
- warnings
- structured errors
- trace metadata

## Error Contract

Errors should distinguish:

- unsupported input format
- unreadable file
- PDF without extractable XML
- invalid XML
- XML structurally valid but semantically unmappable
- invalid JSON
- JSON schema validation failure
- Pydantic validation failure

## Planned Steps

1. define parser result dataclasses or Pydantic models
2. define structured error codes and messages
3. define public parser function signatures
4. define source-specific responsibilities for PDF, XML, and JSON import
5. define trace preservation rules
6. document examples of success and failure cases
7. add unit tests if implementation is approved

## Accepted Execution Plan

Issue `#47` is a contract-definition issue. It must not implement real PDF
extraction, XML import, Open CVN JSON validation, JSON Schema execution, or
domain mapping. Concrete runtime behavior is deferred to issues `#48` and `#49`.

The accepted public package location for the contract is:

```text
src/open_cvn/
```

### Task 1 - Confirm Scope And Boundaries

Summary:

- confirm that this issue defines the parser and validator contract only
- confirm that concrete parsing and validation implementations remain out of
  scope
- confirm that `src/open_cvn/` is the future public runtime package

Subtasks:

1.1. Re-read issue `#47`, issue `#46` format docs, JSON Schema generation docs,
and current limitations before editing code.

1.2. Record that this issue may create typed structures and public signatures,
but must not parse real PDF, XML, or JSON inputs beyond contract-level stubs.

1.3. Record that `src/generated/` must not be edited.

User file modifications required:

- none during this task

Next step:

- proceed to the public package and type contract design.

### Task 2 - Define Public Package Shape

Summary:

- create the public namespace that later application code and importers will use
- keep it separate from code generation internals

Subtasks:

2.1. Create `src/open_cvn/__init__.py`.

2.2. Create `src/open_cvn/parser_contract.py`.

2.3. Export the accepted contract symbols from `src/open_cvn/__init__.py`.

2.4. Do not move existing `src/cvn_codegen/` logic and do not expose generated
model modules as the parser contract.

User file modifications required:

- code files must be created when implementation begins, unless the user asks the
  agent to write them

Next step:

- define enums and structured issue models inside the contract module.

### Task 3 - Define Source, Status, Severity, And Error Enums

Summary:

- define stable machine-readable constants for all parser and validator outcomes
- make later issues depend on enum values instead of ad hoc strings

Subtasks:

3.1. Define `CvnSourceFormat` with at least:

- `pdf`
- `cvn_xml`
- `open_cvn_json`

3.2. Define `CvnValidationStatus` with at least:

- `not_run`
- `valid`
- `valid_with_warnings`
- `invalid`
- `failed`

3.3. Define `CvnIssueSeverity` with at least:

- `warning`
- `error`

3.4. Define `CvnErrorCode` with at least:

- `unsupported_input_format`
- `unreadable_file`
- `pdf_without_extractable_xml`
- `invalid_xml`
- `xml_semantically_unmappable`
- `invalid_json`
- `json_schema_validation_failure`
- `pydantic_validation_failure`

3.5. Keep enum values lowercase and stable for JSON serialization.

User file modifications required:

- code edits required during implementation if user keeps manual-code ownership

Next step:

- define typed warning/error, trace, and result structures.

### Task 4 - Define Structured Warning And Error Model

Summary:

- create one common issue structure usable by PDF, XML, and JSON paths
- preserve location and diagnostic detail without source-specific exception leaks

Subtasks:

4.1. Define `CvnParseIssue` as a Pydantic model or dataclass.

4.2. Include fields:

- `code`
- `severity`
- `message`
- `source_location`
- `path`
- `details`

4.3. Make `code` use `CvnErrorCode`.

4.4. Make `severity` use `CvnIssueSeverity`.

4.5. Keep `details` open enough for later parser-specific metadata, but avoid
raw exception objects.

User file modifications required:

- code edits required during implementation if user keeps manual-code ownership

Next step:

- define trace metadata carried by every parser result.

### Task 5 - Define Trace Preservation Model

Summary:

- make source trace explicit and portable across PDF, XML, and JSON inputs
- align runtime trace with issue `#46` Open CVN JSON trace rules

Subtasks:

5.1. Define `CvnParseTrace` as a Pydantic model or dataclass.

5.2. Include source-level fields:

- `source_format`
- `source_identifier`
- `source_path`
- `extracted_from`

5.3. Include Open CVN/domain trace fields:

- `cvn_codes`
- `xml_paths`
- `schema_version`
- `policy_name`
- `policy_version`

5.4. Document that trace is metadata and must not change semantic curriculum
values.

5.5. Document that PDF extraction should retain both PDF identity and extracted
XML identity when available.

User file modifications required:

- code edits required during implementation if user keeps manual-code ownership

Next step:

- define unified parser result structure.

### Task 6 - Define Unified Result Contract

Summary:

- create common result envelope for parser and validator functions
- allow successful, warning, invalid, and failed states to share one shape

Subtasks:

6.1. Define `CvnParseResult` as a Pydantic model or dataclass.

6.2. Include fields:

- `source_format`
- `source_identifier`
- `data`
- `validation_status`
- `warnings`
- `errors`
- `trace`

6.3. Define `data` as deliberately broad for issue `#47`, because concrete
domain or JSON object types are finalized by later implementation issues.

6.4. Document expected invariants:

- `errors` not empty means `validation_status` is `invalid` or `failed`
- warnings may coexist with `valid_with_warnings`
- `failed` means processing could not complete
- `invalid` means processing completed enough to classify bad input

6.5. Avoid validating the Open CVN JSON Schema in this issue.

User file modifications required:

- code edits required during implementation if user keeps manual-code ownership

Next step:

- define public function signatures.

### Task 7 - Define Public Parser And Validator Function Signatures

Summary:

- expose stable API entry points without implementing parsing logic yet
- make issues `#48` and `#49` implement behind those signatures

Subtasks:

7.1. Define `parse_cvn_pdf(...) -> CvnParseResult`.

7.2. Define `parse_cvn_xml(...) -> CvnParseResult`.

7.3. Define `parse_open_cvn_json(...) -> CvnParseResult`.

7.4. Define `validate_open_cvn_json(...) -> CvnParseResult`.

7.5. Accept flexible input types for future implementation:

- `Path`
- `str`
- `bytes`
- `Mapping[str, Any]` where applicable

7.6. Each function should raise `NotImplementedError` with a clear message such
as:

```text
Parser implementation is deferred to issue #48/#49.
```

7.7. Do not silently return fake success results from unimplemented functions.

User file modifications required:

- code edits required during implementation if user keeps manual-code ownership

Next step:

- document source-specific responsibilities.

### Task 8 - Document Source-Specific Responsibilities

Summary:

- separate extraction, loading, schema validation, and domain validation concerns
- prevent later issues from mixing PDF extraction with domain validation

Subtasks:

8.1. Document PDF responsibility:

- detect/read PDF input
- extract embedded or recoverable CVN XML when possible
- emit `pdf_without_extractable_xml` when no XML can be extracted
- delegate XML interpretation to XML import path

8.2. Document XML responsibility:

- read CVN XML input
- classify unreadable or invalid XML
- preserve XML paths and CVN trace when possible
- report `xml_semantically_unmappable` when structure exists but cannot map to
  Open CVN/domain representation

8.3. Document JSON responsibility:

- read Open CVN JSON input
- classify invalid JSON separately from schema validation failure
- validate against canonical issue `#46` root shape and issue `#45/#46` schema in
  issue `#49`

8.4. Document validator responsibility:

- validate already-loaded Open CVN JSON-like objects
- distinguish JSON Schema validation failure from Pydantic/runtime validation
  failure

User file modifications required:

- documentation edits required during implementation if user keeps manual-doc
  ownership

Next step:

- write examples of expected success and failure results.

### Task 9 - Document Contract Examples

Summary:

- make contract behavior concrete without implementing parser internals
- give issues `#48` and `#49` regression targets

Subtasks:

9.1. Document successful Open CVN JSON validation result shape.

9.2. Document invalid JSON result shape using `invalid_json`.

9.3. Document JSON Schema failure result shape using
`json_schema_validation_failure`.

9.4. Document PDF-without-XML failure result shape using
`pdf_without_extractable_xml`.

9.5. Document XML semantically unmappable result shape using
`xml_semantically_unmappable`.

9.6. Keep examples deterministic and ASCII-safe.

User file modifications required:

- documentation edits required during implementation if user keeps manual-doc
  ownership

Next step:

- add contract tests that do not test parser implementation.

### Task 10 - Add Contract-Only Tests

Summary:

- verify the public contract is importable, serializable, and stable
- avoid false tests for PDF/XML/JSON implementation that does not exist yet

Subtasks:

10.1. Create `tests/test_parser_validator_contract_unit.py`.

10.2. Test imports from `open_cvn`.

10.3. Test enum values are stable lowercase strings.

10.4. Test `CvnParseIssue` serializes structured error data.

10.5. Test `CvnParseTrace` serializes source and policy trace.

10.6. Test `CvnParseResult` supports success, warning, invalid, and failed
states.

10.7. Test unimplemented public functions raise `NotImplementedError` with the
deferred-implementation message.

10.8. Do not test real PDF extraction, XML parsing, JSON Schema validation, or
Pydantic domain mapping in this issue.

User file modifications required:

- test file edits required during implementation if user keeps manual-code
  ownership

Next step:

- update persistent documentation after contract files and tests exist.

### Task 11 - Update Persistent Documentation

Summary:

- keep repository state aligned with implemented contract
- make future sessions find the contract without chat history

Subtasks:

11.1. Create or update `docs/pipeline/parser_validator_contract.md`.

11.2. Update this issue document with implementation decisions, artifacts,
verification, deviations, and final status.

11.3. Update `docs/context/current_status.md` with issue `#47` outcome and next
planned work.

11.4. Update `docs/roadmap/cvn_generation_roadmap.md` if issue `#47` status
changes.

11.5. Update `PROJECT_GUIDE.md` if the new parser contract document becomes a
human-facing project map entry.

11.6. Update `docs/pipeline/known_limitations.md` only if new limitations are
found.

User file modifications required:

- documentation edits required during implementation if user keeps manual-doc
  ownership

Next step:

- run targeted and full verification.

### Task 12 - Verification

Summary:

- prove the contract is stable without claiming parser implementation exists

Subtasks:

12.1. Run targeted contract tests:

```bash
uv run pytest -n auto tests/test_parser_validator_contract_unit.py -v
```

12.2. Run full suite:

```bash
uv run pytest -n auto tests
```

12.3. Confirm no generated files were manually edited.

12.4. Confirm issue `#48` can implement PDF XML extraction behind
`parse_cvn_pdf(...)`.

12.5. Confirm issue `#49` can implement XML and JSON import validation behind
`parse_cvn_xml(...)`, `parse_open_cvn_json(...)`, and
`validate_open_cvn_json(...)`.

User file modifications required:

- none unless verification exposes failures requiring code or documentation fixes

Next step:

- finalize issue status only after implementation and verification are complete.

### Task 13 - Final Completion Criteria

Summary:

- define what must be true before issue `#47` is considered complete

Completion checklist:

- `src/open_cvn/` exists as public runtime contract package
- parser/validator contract types are importable
- public parser/validator signatures exist but do not implement real parsing
- structured error codes cover all issue `#47` planned input paths
- trace rules align with issue `#46` Open CVN JSON format
- contract documentation exists and includes success/failure examples
- contract-only tests pass
- full repository tests pass
- persistent documentation is updated
- `src/generated/` remains untouched by manual edits

User file modifications required:

- none after all implementation tasks are complete unless user chooses to make
  manual code or doc edits

Next step:

- begin issue `#48` PDF XML extraction implementation after issue `#47` is closed.

## Expected Output

- parser/validator contract documentation
- typed result and error structures if implementation is approved
- tests for contract behavior if implementation is approved

## Implementation Outcome

- public contract package created under:
  - `src/open_cvn/`
- contract types and deferred public functions implemented in:
  - `src/open_cvn/parser_contract.py`
- public exports defined in:
  - `src/open_cvn/__init__.py`
- parser and validator contract documentation added at:
  - `docs/pipeline/parser_validator_contract.md`
- contract-only tests added at:
  - `tests/test_parser_validator_contract_unit.py`

Implemented public functions:

- `parse_cvn_pdf(...)`
- `parse_cvn_xml(...)`
- `parse_open_cvn_json(...)`
- `validate_open_cvn_json(...)`

These functions intentionally raise `NotImplementedError` in issue `#47` because
real parser and validator implementation is deferred to issues `#48` and `#49`.

Implemented public result and diagnostic structures:

- `CvnSourceFormat`
- `CvnValidationStatus`
- `CvnIssueSeverity`
- `CvnErrorCode`
- `CvnParseIssue`
- `CvnParseTrace`
- `CvnParseResult`

## Implementation Deviations

- The accepted plan chose `src/open_cvn/` as the public runtime package instead
  of placing the contract under `src/models/cvn/`.
- The issue remains contract-only; no PDF extraction, XML parsing, JSON Schema
  validation, or domain mapping was implemented.

## Verification Performed

- targeted contract verification passed with:
  `uv run pytest -n auto tests/test_parser_validator_contract_unit.py -v`
- targeted verification result:
  `14 passed in 2.07s`
- full-suite verification passed with:
  `uv run pytest -n auto tests`
- full-suite verification result:
  `348 passed in 857.18s (0:14:17)`

## Verification

- result and error types cover all planned input paths
- API separates extraction from validation
- issue `#48` and issue `#49` can implement against the contract without
  redesigning it

## Impact On Later Issues

- issue `#48` implements PDF XML extraction behind this contract
- issue `#49` implements XML and JSON import validation behind this contract
- epic `#51` consumes this contract in the application layer

## Status

- Status: completed
