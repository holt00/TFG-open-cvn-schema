# Issue 50 - Add Tests And Documentation For Parser Workflow

## Summary

Issue `#50` adds regression tests and contributor documentation for the parser,
JSON Schema, and agnostic schema workflow delivered by epic `#41`.

This issue is part of epic `#41`.

## Goal

- protect parser behavior for PDF, XML, and JSON inputs
- document parser commands and public API examples
- confirm JSON Schema and UML/conceptual outputs are reproducible where
  generated
- update persistent project documentation after epic `#41` implementation

## Planned Test Coverage

The final test suite should cover:

- conceptual IR extraction if implemented
- UML or diagram generation determinism if implemented
- JSON Schema generation and validity
- valid Open CVN JSON import
- invalid Open CVN JSON import
- valid CVN XML import
- invalid CVN XML import
- PDF with extractable XML when fixture is available
- PDF without extractable XML as structured unsupported case
- parser result and error contract behavior
- trace metadata preservation

## Documentation Targets

Potential documentation updates include:

- epic `#41` issue record
- issue records `#42` through `#50`
- `docs/context/current_status.md`
- `docs/roadmap/cvn_generation_roadmap.md`
- `docs/pipeline/known_limitations.md` if new limitations are found
- parser workflow guide under `docs/development/` if implementation creates one
- `PROJECT_GUIDE.md` if the document map changes

## Planned Steps

1. identify implemented artifacts from issues `#42` through `#49`
2. add focused unit tests for contract-level behavior
3. add integration tests for parser inputs
4. add determinism tests for generated schema or diagrams when applicable
5. add documentation examples for parser usage
6. run full repository verification
7. update epic `#41` and current status documentation

## Accepted Execution Protocol

For every execution step, report:

1. active task number and task name
2. active subtask number and subtask name when a subtask is being executed
3. short initial summary of what the task or subtask will do
4. short final result for the task or subtask
5. whether the user must modify any file manually
6. next step to follow

File-modification rule:

- documentation changes may be performed by the agent when explicitly requested
- code, test, fixture, dependency, generated schema, and generated diagram changes
  should be left for the user unless the user explicitly authorizes the agent to
  edit them
- generated structural code under `src/generated/` must not be edited manually
- generated domain code under `src/models/cvn/generated/` must not be edited
  manually
- generated artifacts such as `schemas/open_cvn.schema.json` and
  `docs/diagrams/*.puml` must be changed only through their documented generator
  commands, not by hand

## Accepted Execution Plan

### Task `1 / 14` - Confirm Issue 50 Scope

- Task summary:
  - confirm that issue `#50` is a regression-test and contributor-documentation
    closure issue for epic `#41`, not a new parser feature issue
- Files involved:
  - `docs/roadmap/issues/issue-41-epic-agnostic-schema-json-parser.md`
  - `docs/roadmap/issues/issue-50-parser-workflow-tests-and-documentation.md`
  - `docs/context/current_status.md`
  - `docs/pipeline/parser_validator_contract.md`
- Subtask `1.1 / 14`:
  - confirm implemented scope from issues `#42` through `#49`
- Subtask `1.2 / 14`:
  - confirm that full XML-to-domain semantic mapping remains outside issue `#50`
    unless a later issue reopens it
- Subtask `1.3 / 14`:
  - confirm that PDF import remains deterministic XML extraction only, with no OCR,
    page-text reconstruction, or LLM fallback
- Subtask `1.4 / 14`:
  - confirm that issue `#50` must close documentation and verification gaps before
    epic `#41` can be treated as stable
- User manual modifications needed:
  - none expected; this task is read-only
- Next step:
  - inventory current parser, schema, diagram, and workflow artifacts

### Task `2 / 14` - Inventory Implemented Artifacts

- Task summary:
  - list the real implementation and documentation artifacts that issue `#50` must
    protect or document
- Files involved:
  - `src/open_cvn/`
  - `src/cvn_codegen/conceptual_model_extractor.py`
  - `src/cvn_codegen/conceptual_model_diagrams.py`
  - `src/cvn_codegen/json_schema_generator.py`
  - `schemas/open_cvn.schema.json`
  - `docs/diagrams/`
  - `examples/open_cvn/`
  - `tests/`
- Subtask `2.1 / 14`:
  - inventory public parser exports from `open_cvn`
- Subtask `2.2 / 14`:
  - inventory JSON import, XML import, PDF extraction, and common import utility
    modules
- Subtask `2.3 / 14`:
  - inventory JSON Schema and Open CVN example artifacts
- Subtask `2.4 / 14`:
  - inventory conceptual IR and PlantUML diagram generation artifacts
- Subtask `2.5 / 14`:
  - inventory existing tests covering parser contract, PDF extraction, JSON import,
    XML import, schema generation, examples, conceptual extraction, and diagrams
- User manual modifications needed:
  - none expected; this task is read-only
- Next step:
  - perform coverage-gap audit against the issue `#50` planned coverage list

### Task `3 / 14` - Audit Coverage Gaps

- Task summary:
  - compare current tests with the required issue `#50` coverage matrix and decide
    whether new tests are needed
- Files involved:
  - `tests/test_parser_validator_contract_unit.py`
  - `tests/test_pdf_xml_extraction_unit.py`
  - `tests/test_open_cvn_json_import_unit.py`
  - `tests/test_cvn_xml_import_unit.py`
  - `tests/test_generation_pipeline_json_schema.py`
  - `tests/test_generation_pipeline_conceptual_model.py`
  - `tests/test_generation_pipeline_conceptual_diagrams.py`
  - `tests/test_open_cvn_json_format_examples.py`
- Subtask `3.1 / 14`:
  - audit conceptual IR extraction coverage
- Subtask `3.2 / 14`:
  - audit UML or PlantUML generation determinism coverage
- Subtask `3.3 / 14`:
  - audit JSON Schema generation, validity, and artifact-drift coverage
- Subtask `3.4 / 14`:
  - audit valid and invalid Open CVN JSON import coverage
- Subtask `3.5 / 14`:
  - audit valid and invalid CVN XML import coverage
- Subtask `3.6 / 14`:
  - audit PDF with extractable XML and PDF without extractable XML coverage
- Subtask `3.7 / 14`:
  - audit parser result, error contract, and trace metadata preservation coverage
- Subtask `3.8 / 14`:
  - record each gap as either `covered`, `needs test`, `needs documentation`, or
    `out of scope`
- User manual modifications needed:
  - none for audit itself; test changes may be needed after gaps are confirmed
- Next step:
  - define the test additions or confirmations needed for contract-level behavior

### Task `4 / 14` - Strengthen Parser Contract Tests

- Task summary:
  - ensure the public parser result envelope, errors, warnings, and trace rules are
    regression-tested after issues `#48` and `#49`
- Files involved if test edits are authorized:
  - `tests/test_parser_validator_contract_unit.py`
  - `src/open_cvn/parser_contract.py` only if a test exposes a contract defect
- Subtask `4.1 / 14`:
  - verify public imports from `open_cvn` remain stable
- Subtask `4.2 / 14`:
  - verify enum values remain stable lowercase strings
- Subtask `4.3 / 14`:
  - verify result invariants for `valid`, `valid_with_warnings`, `invalid`, and
    `failed`
- Subtask `4.4 / 14`:
  - verify error-bearing results cannot use successful validation statuses
- Subtask `4.5 / 14`:
  - verify warning-bearing results use warning severity
- Subtask `4.6 / 14`:
  - verify trace metadata serializes source identity, source path, extraction
    source, CVN codes, XML paths, schema version, and policy values
- User manual modifications needed:
  - test/code edits needed only if audit finds missing coverage or failing behavior;
    by default the user owns those edits unless explicitly delegated
- Next step:
  - confirm parser input integration tests for JSON, XML, and PDF

### Task `5 / 14` - Strengthen Parser Input Integration Tests

- Task summary:
  - verify all supported input families behave through the public parser API, not
    only through internal helpers
- Files involved if test edits are authorized:
  - `tests/test_open_cvn_json_import_unit.py`
  - `tests/test_cvn_xml_import_unit.py`
  - `tests/test_pdf_xml_extraction_unit.py`
  - `tests/fixtures/open_cvn/`
  - `tests/fixtures/cvn_xml/`
- Subtask `5.1 / 14`:
  - verify Open CVN JSON path, inline string, bytes, and mapping inputs
- Subtask `5.2 / 14`:
  - verify malformed JSON returns `invalid_json`
- Subtask `5.3 / 14`:
  - verify schema failures return `json_schema_validation_failure`
- Subtask `5.4 / 14`:
  - verify runtime model failures return `pydantic_validation_failure` when schema
    permits the document to reach runtime validation
- Subtask `5.5 / 14`:
  - verify CVN XML path, inline string, and bytes inputs
- Subtask `5.6 / 14`:
  - verify malformed XML returns `invalid_xml`
- Subtask `5.7 / 14`:
  - verify well-formed non-CVN XML returns `xml_semantically_unmappable`
- Subtask `5.8 / 14`:
  - verify PDF embedded XML, PDF XML metadata, unreadable PDF, unsupported input,
    and PDF-without-XML cases
- User manual modifications needed:
  - test/fixture edits needed only if gaps are confirmed; by default the user owns
    those edits unless explicitly delegated
- Next step:
  - confirm trace preservation across parser paths

### Task `6 / 14` - Strengthen Trace Metadata Tests

- Task summary:
  - make trace preservation an explicit regression target for PDF, XML, and JSON
    import paths
- Files involved if test edits are authorized:
  - `tests/test_open_cvn_json_import_unit.py`
  - `tests/test_cvn_xml_import_unit.py`
  - `tests/test_pdf_xml_extraction_unit.py`
  - `tests/test_parser_validator_contract_unit.py`
- Subtask `6.1 / 14`:
  - verify Open CVN JSON trace preserves `schema_version`, `metadata.policy.name`,
    and `metadata.policy.version`
- Subtask `6.2 / 14`:
  - verify XML trace preserves deterministic XML paths
- Subtask `6.3 / 14`:
  - verify XML trace preserves detected CVN code-like values
- Subtask `6.4 / 14`:
  - verify PDF trace preserves original PDF identity and extracted XML source
- Subtask `6.5 / 14`:
  - verify error results keep trace metadata without leaking personal payloads
- User manual modifications needed:
  - test edits needed only if current tests do not already cover these assertions;
    by default the user owns those edits unless explicitly delegated
- Next step:
  - confirm generated schema and conceptual artifact reproducibility

### Task `7 / 14` - Verify Generated Artifact Determinism

- Task summary:
  - prove generated JSON Schema and PlantUML source artifacts are reproducible or
    clearly document why a check is not applicable
- Files involved if test edits or regeneration are authorized:
  - `src/cvn_codegen/json_schema_generator.py`
  - `schemas/open_cvn.schema.json`
  - `src/cvn_codegen/conceptual_model_diagrams.py`
  - `docs/diagrams/`
  - `tests/test_generation_pipeline_json_schema.py`
  - `tests/test_generation_pipeline_conceptual_diagrams.py`
- Subtask `7.1 / 14`:
  - verify JSON Schema generator writes deterministic bytes for the same inventory
- Subtask `7.2 / 14`:
  - verify committed `schemas/open_cvn.schema.json` has no drift after canonical
    regeneration
- Subtask `7.3 / 14`:
  - verify generated schema declares Draft 2020-12 and contains expected `$defs`
- Subtask `7.4 / 14`:
  - verify PlantUML generation writes deterministic `.puml` sources for canonical
    diagrams
- Subtask `7.5 / 14`:
  - verify rendered PNGs remain optional derived review artifacts, not mandatory
    repository outputs
- User manual modifications needed:
  - generated artifact or test edits needed only if drift or gaps are found; by
    default the user owns those edits unless explicitly delegated
- Next step:
  - create or update contributor-facing parser workflow documentation

### Task `8 / 14` - Document Parser Workflow For Contributors

- Task summary:
  - provide runnable parser usage guidance and examples without requiring readers
    to inspect tests or chat history
- Files involved if documentation edits are authorized:
  - preferred new guide: `docs/development/parser_workflow.md`
  - existing contract doc: `docs/pipeline/parser_validator_contract.md`
  - `PROJECT_GUIDE.md` if the document map changes
  - `docs/context/project_context_index.md` if the document map changes
- Subtask `8.1 / 14`:
  - document public imports from `open_cvn`
- Subtask `8.2 / 14`:
  - document parsing Open CVN JSON from path, string, bytes, and mapping inputs
- Subtask `8.3 / 14`:
  - document validating already-loaded Open CVN JSON mappings
- Subtask `8.4 / 14`:
  - document parsing direct CVN XML and interpreting trace-only output
- Subtask `8.5 / 14`:
  - document extracting XML from CVN PDFs and handing `data["xml_text"]` to
    `parse_cvn_xml(...)`
- Subtask `8.6 / 14`:
  - document structured error handling for `invalid_json`,
    `json_schema_validation_failure`, `pydantic_validation_failure`,
    `invalid_xml`, `xml_semantically_unmappable`, `unreadable_file`,
    `unsupported_input_format`, and `pdf_without_extractable_xml`
- Subtask `8.7 / 14`:
  - document commands for targeted parser tests and full suite verification
- User manual modifications needed:
  - documentation edits may be performed by the agent when explicitly requested;
    otherwise the user owns them
- Next step:
  - align regeneration workflow and project maps with parser workflow docs

### Task `9 / 14` - Align Workflow And Project Documentation

- Task summary:
  - ensure repository entry points mention parser workflow, schema regeneration,
    diagrams, and verification in the correct places
- Files involved if documentation edits are authorized:
  - `docs/development/regeneration_workflow.md`
  - `PROJECT_GUIDE.md`
  - `docs/context/project_context_index.md`
  - `README.md` only if the top-level human entry point changes
- Subtask `9.1 / 14`:
  - add parser workflow guide to document maps if a new guide is created
- Subtask `9.2 / 14`:
  - ensure regeneration workflow mentions conceptual diagrams, JSON Schema, parser
    tests, and full suite verification after epic `#41`
- Subtask `9.3 / 14`:
  - ensure `PROJECT_GUIDE.md` points to parser contract/workflow docs when useful
    for contributors
- Subtask `9.4 / 14`:
  - ensure `docs/context/project_context_index.md` reflects completed issues
    `#49` and `#50` when issue `#50` closes
- Subtask `9.5 / 14`:
  - update `README.md` only if human onboarding changes materially
- User manual modifications needed:
  - documentation edits may be performed by the agent when explicitly requested;
    otherwise the user owns them
- Next step:
  - update limitation records if new durable limitations are found

### Task `10 / 14` - Update Known Limitations If Needed

- Task summary:
  - record only durable limitations found during test/documentation work, not
    temporary local setup failures
- Files involved if documentation edits are authorized:
  - `docs/pipeline/known_limitations.md`
  - issue `#50` document
- Subtask `10.1 / 14`:
  - confirm existing limitation for trace-only CVN XML import remains accurate
- Subtask `10.2 / 14`:
  - confirm existing limitation for JSON Schema-before-Pydantic validation remains
    accurate
- Subtask `10.3 / 14`:
  - add a new limitation only if verification reveals an unrecorded parser,
    schema, diagram, or workflow boundary
- Subtask `10.4 / 14`:
  - link any new limitation back to issue `#50` and expected future follow-up
- User manual modifications needed:
  - none unless a new limitation is found and the user wants to own the docs edit
- Next step:
  - run targeted verification commands

### Task `11 / 14` - Run Targeted Verification

- Task summary:
  - execute the smallest useful verification commands for issue `#50` scope before
    full-suite execution
- Commands:
  - `uv run pytest -n auto tests/test_parser_validator_contract_unit.py tests/test_pdf_xml_extraction_unit.py tests/test_open_cvn_json_import_unit.py tests/test_cvn_xml_import_unit.py -v`
  - `uv run pytest -n auto tests/test_json_schema_generator_unit.py tests/test_generation_pipeline_json_schema.py tests/test_open_cvn_json_format_examples.py -v`
  - `uv run pytest -n auto tests/test_conceptual_model_extractor_unit.py tests/test_generation_pipeline_conceptual_model.py tests/test_conceptual_model_diagrams_unit.py tests/test_generation_pipeline_conceptual_diagrams.py -v`
- Subtask `11.1 / 14`:
  - run targeted parser contract and parser input tests
- Subtask `11.2 / 14`:
  - run targeted JSON Schema and Open CVN JSON example tests
- Subtask `11.3 / 14`:
  - run targeted conceptual model and diagram tests
- Subtask `11.4 / 14`:
  - record exact commands and results in issue `#50`
- Subtask `11.5 / 14`:
  - if any command fails, classify failure as test gap, implementation bug,
    environment issue, or documented limitation before editing files
- User manual modifications needed:
  - none to run commands; code/test edits may be needed if verification fails and
    the user does not delegate them
- Next step:
  - run regeneration drift checks when safe

### Task `12 / 14` - Run Regeneration Drift Checks

- Task summary:
  - confirm canonical generated schema and diagram sources are reproducible through
    documented commands
- Commands:
  - `uv run python -m cvn_codegen.json_schema_generator`
  - `uv run python -m cvn_codegen.conceptual_model_diagrams --output-dir docs/diagrams`
- Subtask `12.1 / 14`:
  - regenerate canonical JSON Schema and inspect whether `schemas/open_cvn.schema.json`
    changes
- Subtask `12.2 / 14`:
  - regenerate canonical PlantUML sources and inspect whether `docs/diagrams/*.puml`
    changes
- Subtask `12.3 / 14`:
  - if generated artifacts change, stop and report drift before deciding whether
    the user or agent should keep regenerated outputs
- Subtask `12.4 / 14`:
  - record commands and drift/no-drift result in issue `#50`
- User manual modifications needed:
  - generated artifacts may change through commands; user approval is required
    before keeping drift unless explicitly delegated
- Next step:
  - run full repository verification

### Task `13 / 14` - Run Full Repository Verification

- Task summary:
  - prove issue `#50` closure does not regress earlier pipeline or parser work
- Command:
  - `uv run pytest -n auto tests`
- Subtask `13.1 / 14`:
  - run the full test suite
- Subtask `13.2 / 14`:
  - record exact command, pass/fail status, count, and duration
- Subtask `13.3 / 14`:
  - if full suite cannot be run, record the exact reason and strongest substitute
    verification already executed
- Subtask `13.4 / 14`:
  - confirm no manual edits were made under `src/generated/` or
    `src/models/cvn/generated/`
- User manual modifications needed:
  - none unless verification exposes failures requiring code, tests, fixtures, or
    documentation changes
- Next step:
  - update issue, epic, roadmap, and current status documentation

### Task `14 / 14` - Close Issue 50 And Epic 41 Documentation

- Task summary:
  - record final issue `#50` outcome and align persistent project state after all
    tests and docs are complete
- Files involved if documentation edits are authorized:
  - `docs/roadmap/issues/issue-50-parser-workflow-tests-and-documentation.md`
  - `docs/roadmap/issues/issue-41-epic-agnostic-schema-json-parser.md`
  - `docs/context/current_status.md`
  - `docs/roadmap/cvn_generation_roadmap.md`
  - `docs/pipeline/known_limitations.md` only if new limitations were found
  - `PROJECT_GUIDE.md` and `docs/context/project_context_index.md` if document maps
    changed
- Subtask `14.1 / 14`:
  - update issue `#50` with implemented outcome, artifacts changed, verification,
    deviations, limitations, and status
- Subtask `14.2 / 14`:
  - update epic `#41` with completed child issue status and final parser/schema
    workflow summary
- Subtask `14.3 / 14`:
  - update `docs/context/current_status.md` with issue `#50` closure and next
    planned roadmap direction
- Subtask `14.4 / 14`:
  - update `docs/roadmap/cvn_generation_roadmap.md` if issue or epic status
    changes
- Subtask `14.5 / 14`:
  - update document maps if new parser workflow documentation was created
- Subtask `14.6 / 14`:
  - keep issue `#50` open if required verification did not pass or was not run
- User manual modifications needed:
  - documentation edits may be performed by the agent when explicitly requested;
    code/test/generated artifact edits remain user-owned unless delegated
- Next step:
  - proceed to post-epic application/import-export roadmap only after issue `#50`
    verification and documentation closure are accepted

## Completion Criteria

- implemented artifacts from issues `#42` through `#49` are inventoried
- coverage matrix for parser, schema, conceptual, and diagram workflow is audited
- parser contract tests protect result invariants and structured errors
- parser input tests cover valid and invalid JSON, XML, and PDF paths
- trace preservation is tested for JSON, XML, and PDF paths
- JSON Schema generation is deterministic and validates expected Open CVN examples
- conceptual IR and PlantUML generation determinism are tested or documented
- contributor parser workflow documentation exists or current docs fully cover it
- targeted verification commands pass or failures are documented with next actions
- full repository verification passes with `uv run pytest -n auto tests`, or the
  strongest substitute verification and blocker are recorded
- issue `#50`, epic `#41`, current status, roadmap, and limitation docs are updated
  as needed
- no generated structural or generated domain code is manually edited

## Expected Output

- parser and schema test coverage
- contributor documentation for parser workflow
- verification record for epic `#41`
- documented limitations and follow-up work

## Implementation Outcome

- Issue `#50` audited the completed epic `#41` parser, schema, conceptual model,
  and diagram workflow after issues `#42` through `#49`.
- Existing regression coverage was confirmed for:
  - conceptual IR extraction
  - PlantUML generation determinism
  - JSON Schema generation and Open CVN example validation
  - valid and invalid Open CVN JSON import
  - valid and invalid CVN XML import
  - PDF extraction with embedded XML and XML metadata
  - PDF without extractable XML
  - parser result and error contract invariants
  - trace metadata preservation for JSON, XML, and PDF paths
- A missing direct regression assertion for the `pydantic_validation_failure` JSON
  path was added to:
  - `tests/test_open_cvn_json_import_unit.py`
- Contributor parser workflow documentation was added at:
  - `docs/development/parser_workflow.md`
- Documentation maps were updated so future sessions can find the parser workflow
  guide.

## Implementation Adjustments

- No new parser behavior was added. The only test change covers existing runtime
  behavior for syntactically valid JSON whose loaded value is not an object.
- Regeneration drift checks were executed against temporary outputs under
  `/tmp/opencode` to avoid changing canonical artifacts while comparing outputs.
- No new durable limitations were found; the existing trace-only CVN XML import
  and JSON Schema-before-Pydantic validation limitations remain accurate.

## Artifacts Changed

- `docs/development/parser_workflow.md`
- `tests/test_open_cvn_json_import_unit.py`
- `PROJECT_GUIDE.md`
- `AGENTS.md`
- `docs/context/project_context_index.md`
- `docs/development/regeneration_workflow.md`
- `docs/roadmap/issues/issue-50-parser-workflow-tests-and-documentation.md`
- `docs/roadmap/issues/issue-41-epic-agnostic-schema-json-parser.md`
- `docs/context/current_status.md`
- `docs/roadmap/cvn_generation_roadmap.md`

## Verification Performed

- Targeted parser workflow verification passed with:
  `uv run pytest -n auto tests/test_parser_validator_contract_unit.py tests/test_pdf_xml_extraction_unit.py tests/test_open_cvn_json_import_unit.py tests/test_cvn_xml_import_unit.py -v`
- Targeted parser verification result:
  `36 passed in 16.61s`
- Targeted JSON Schema and Open CVN example verification passed with:
  `uv run pytest -n auto tests/test_json_schema_generator_unit.py tests/test_generation_pipeline_json_schema.py tests/test_open_cvn_json_format_examples.py -v`
- Targeted JSON Schema and example verification result:
  `21 passed in 92.86s (0:01:32)`
- Targeted conceptual model and diagram verification passed with:
  `uv run pytest -n auto tests/test_conceptual_model_extractor_unit.py tests/test_generation_pipeline_conceptual_model.py tests/test_conceptual_model_diagrams_unit.py tests/test_generation_pipeline_conceptual_diagrams.py -v`
- Targeted conceptual and diagram verification result:
  `19 passed in 90.61s (0:01:30)`
- Temporary JSON Schema drift check passed with:
  `uv run python -m cvn_codegen.json_schema_generator --output-path /tmp/opencode/issue50-schema/open_cvn.schema.json`
- Temporary PlantUML drift check passed with:
  `uv run python -m cvn_codegen.conceptual_model_diagrams --output-dir /tmp/opencode/issue50-diagrams`
- Drift check result:
  - `schemas/open_cvn.schema.json` matched the temporary regenerated schema
  - canonical `.puml` files under `docs/diagrams/` matched the temporary
    regenerated PlantUML sources
  - `docs/diagrams/README.md` and rendered `.png` files are non-generated or
    optional review artifacts and were not emitted to the temporary directory
- Full-suite verification passed with:
  `uv run pytest -n auto tests`
- Full-suite verification result:
  `370 passed in 287.52s (0:04:47)`

## Verification

- targeted parser/schema tests pass
- full repository verification passes with `uv run pytest -n auto tests`
- documentation records exact commands and results

## Impact On Later Issues

- epic `#51` can consume a documented and tested parser/schema foundation
- future application work should not need to rediscover parser contracts

## Status

- Status: completed
