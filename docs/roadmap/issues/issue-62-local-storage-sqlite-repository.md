# Issue 62 - Implement Local Storage With SQLite

## Summary

Issue `#62` implements the local persistence layer for the MVP CV management
application.

This issue is part of epic `#60`.

## Goal

- store Open CVN curriculum documents locally
- keep the MVP usable without external services
- preserve parser validation status and trace metadata
- support later master and derived version management

## Storage Direction

The MVP should use SQLite because it is local, available from Python standard
library support, easy to test, and sufficient for a single-user prototype.

The storage layer should keep Open CVN JSON documents as canonical JSON payloads
inside SQLite while storing enough metadata for listing, selection, and versioning.

## Planned Scope

- create a local SQLite database file
- create schema initialization and schema-version metadata
- store curriculum records with:
  - internal ID
  - display name
  - Open CVN JSON payload
  - schema version
  - policy name and policy version
  - source format or source identifier
  - created and updated timestamps
- store parser issues or import diagnostics where useful
- expose repository functions for create, read, update, list, and delete where
  needed by MVP commands

## Planned Steps

1. define SQLite schema for MVP storage
2. implement database initialization
3. implement repository functions for curriculum documents
4. preserve Open CVN JSON payload exactly enough for export
5. validate or revalidate documents before storage using epic `#41` validators
6. add unit tests with temporary SQLite files
7. document the local storage file and backup expectations

## Detailed Execution Plan

This plan is the accepted execution plan for implementing issue `#62`.
During execution, each work update must identify the active task and, when
applicable, the active subtask. Each task or subtask update should include:

- initial summary of the task or subtask goal
- current task and subtask identifier
- whether the user must modify any file manually
- next step to follow

Unless explicitly requested otherwise, code edits are expected to be performed by
the user. Documentation edits may be applied when the user asks to establish or
update the issue plan.

### Task 1 - Confirm Scope And Constraints

- Subtask 1.1: confirm issue `#62` is limited to local SQLite storage and schema
  initialization.
- Subtask 1.2: confirm issue `#62` does not implement full Open CVN JSON
  import/export behavior, which remains planned for issue `#64`.
- Subtask 1.3: confirm issue `#62` does not implement master or derived version
  management, which remains planned for issue `#63`.
- Subtask 1.4: confirm issue `#62` does not implement LaTeX or PDF export
  behavior.
- Subtask 1.5: confirm `src/generated/` remains untouched.
- Subtask 1.6: confirm `open-cvn store init` is the only CLI placeholder from
  issue `#61` that becomes functional during this issue.

Expected output: final implementation boundary for issue `#62` before code work.

### Task 2 - Define Storage Contract

- Subtask 2.1: create application-level storage types such as
  `CurriculumRecord`, `CurriculumCreate`, `CurriculumUpdate`, and
  `CurriculumDiagnostic`.
- Subtask 2.2: define storage errors such as `StoreNotInitialized`,
  `CurriculumNotFound`, and `InvalidCurriculumDocument`.
- Subtask 2.3: use UUID values for internal curriculum IDs.
- Subtask 2.4: use UTC ISO-8601 strings for `created_at` and `updated_at`
  timestamps.
- Subtask 2.5: keep the public repository API small enough for later issues
  `#63` and `#64` to consume without redesign.

Expected output: stable local storage API contract for the MVP application layer.

### Task 3 - Create SQLite Storage Module

- Subtask 3.1: create `src/open_cvn_app/storage.py`.
- Subtask 3.2: use Python standard-library `sqlite3`; do not add a new database
  dependency.
- Subtask 3.3: implement a connection helper for local store files.
- Subtask 3.4: enable `PRAGMA foreign_keys = ON` for repository connections.
- Subtask 3.5: use `sqlite3.Row` or equivalent row mapping for deterministic
  record loading.
- Subtask 3.6: ensure store initialization creates the parent directory for the
  SQLite file when needed.

Expected output: hand-maintained SQLite module under `src/open_cvn_app/`.

### Task 4 - Implement Schema Initialization

- Subtask 4.1: define an initial application storage schema version, such as
  `SCHEMA_VERSION = "1"`.
- Subtask 4.2: create an `app_metadata` table for schema metadata.
- Subtask 4.3: create a `curricula` table for stored Open CVN documents.
- Subtask 4.4: create a `curriculum_diagnostics` table for parser warnings,
  errors, and import diagnostics.
- Subtask 4.5: create indexes needed for MVP listing and diagnostic lookup.
- Subtask 4.6: implement `initialize_store(path)` as an idempotent operation.
- Subtask 4.7: detect incompatible future schema versions and fail clearly.

Expected output: repeatable SQLite schema initialization for local stores.

### Task 5 - Validate Documents Before Storage

- Subtask 5.1: accept Open CVN documents as `Mapping[str, Any]` values in the
  repository create and update paths.
- Subtask 5.2: call `validate_open_cvn_json(...)` from `src/open_cvn/` before
  storing a document.
- Subtask 5.3: reject validation results with `invalid` or `failed` status.
- Subtask 5.4: allow `valid` and `valid_with_warnings` results to be stored.
- Subtask 5.5: extract `schema_version`, `metadata.policy.name`, and
  `metadata.policy.version` from the validated document.
- Subtask 5.6: serialize the payload with deterministic JSON settings, such as
  `sort_keys=True` and compact separators.

Expected output: invalid Open CVN JSON cannot be stored as a valid curriculum
record.

### Task 6 - Preserve Open CVN JSON Payload Semantics

- Subtask 6.1: store the Open CVN document payload as canonical JSON text inside
  SQLite.
- Subtask 6.2: read stored payloads back as Python mappings.
- Subtask 6.3: verify semantic round-trip equality for representative Open CVN
  JSON documents.
- Subtask 6.4: document that original JSON whitespace and object ordering are not
  preserved, while data content is preserved for export.

Expected output: stored Open CVN JSON remains usable for later issue `#64`
export.

### Task 7 - Implement Curriculum Repository Operations

- Subtask 7.1: implement `create_curriculum(...)`.
- Subtask 7.2: implement `get_curriculum(...)`.
- Subtask 7.3: implement `list_curricula(...)`.
- Subtask 7.4: implement `update_curriculum(...)` for editable metadata such as
  display name.
- Subtask 7.5: implement `replace_curriculum_payload(...)` or equivalent payload
  update behavior.
- Subtask 7.6: implement `delete_curriculum(...)`.
- Subtask 7.7: wrap write operations in transactions and update `updated_at`
  deterministically.

Expected output: MVP CRUD repository for stored curriculum documents.

### Task 8 - Preserve Parser Diagnostics

- Subtask 8.1: convert warnings and errors from `CvnParseResult` into diagnostic
  rows.
- Subtask 8.2: store diagnostic severity, code, message, source location, path,
  and details.
- Subtask 8.3: store diagnostic `path` and `details` as JSON text.
- Subtask 8.4: clear and replace diagnostics when a curriculum payload is
  replaced.
- Subtask 8.5: expose diagnostic loading by curriculum ID.

Expected output: parser validation status and trace metadata remain available
after persistence.

### Task 9 - Wire Store Initialization Into CLI

- Subtask 9.1: replace the issue `#61` placeholder behavior for
  `open-cvn store init`.
- Subtask 9.2: resolve the configured store path through `OpenCvnAppConfig`.
- Subtask 9.3: call `initialize_store(...)` from the CLI handler.
- Subtask 9.4: return a success message with the resolved store path and schema
  version.
- Subtask 9.5: convert storage initialization failures into `AppResult.failed(...)`.
- Subtask 9.6: keep the JSON, versions, LaTeX, and PDF command groups as
  placeholders for their later issues.

Expected output: `open-cvn store init [--path PATH]` creates a real local SQLite
store.

### Task 10 - Add Storage Unit Tests

- Subtask 10.1: create `tests/test_open_cvn_app_storage_unit.py`.
- Subtask 10.2: use `tmp_path` for isolated temporary SQLite files.
- Subtask 10.3: test schema initialization creates the expected tables and
  metadata.
- Subtask 10.4: test schema initialization is idempotent.
- Subtask 10.5: test create, read, list, update, and delete repository behavior.
- Subtask 10.6: test payload round-trip equality with a valid Open CVN fixture.
- Subtask 10.7: test invalid Open CVN JSON is rejected.
- Subtask 10.8: test diagnostic storage and loading.
- Subtask 10.9: test missing curriculum IDs raise or return the documented not
  found behavior.

Expected output: temporary database tests prove the repository behavior.

### Task 11 - Update CLI Tests

- Subtask 11.1: update the existing `store init` CLI test that currently expects
  the issue `#62` placeholder message.
- Subtask 11.2: verify `store init --path <tmp>` creates the SQLite database.
- Subtask 11.3: verify the success output includes the resolved path.
- Subtask 11.4: keep tests for later issue placeholders unchanged where those
  commands are still placeholders.

Expected output: CLI tests reflect the real storage initialization behavior.

### Task 12 - Verify Parser Integration

- Subtask 12.1: use an existing valid Open CVN JSON fixture from
  `tests/fixtures/open_cvn/` or `examples/open_cvn/`.
- Subtask 12.2: store the fixture through the repository and verify
  `validation_status` metadata.
- Subtask 12.3: use invalid JSON or wrong-shape fixtures to verify rejection.
- Subtask 12.4: confirm no parallel parser or validator code is introduced in
  `src/open_cvn_app/`.

Expected output: storage consumes the public epic `#41` parser/validator contract.

### Task 13 - Run Issue Verification

- Subtask 13.1: run targeted storage tests:
  `uv run pytest -n auto tests/test_open_cvn_app_storage_unit.py -v`.
- Subtask 13.2: run targeted CLI tests:
  `uv run pytest -n auto tests/test_open_cvn_app_cli_unit.py -v`.
- Subtask 13.3: run parser integration regression tests:
  `uv run pytest -n auto tests/test_open_cvn_json_import_unit.py tests/test_parser_validator_contract_unit.py -v`.
- Subtask 13.4: run full repository verification:
  `uv run pytest -n auto tests`.
- Subtask 13.5: record any skipped or failed verification with reason.

Expected output: issue `#62` verification evidence.

### Task 14 - Update Persistent Documentation

- Subtask 14.1: update this issue document with actual implementation artifacts,
  deviations, verification, and status.
- Subtask 14.2: update `docs/context/current_status.md` so issue `#62` is recorded
  accurately and issue `#63` becomes the next implementation issue if `#62` is
  completed.
- Subtask 14.3: update `docs/roadmap/cvn_generation_roadmap.md` if it tracks issue
  `#62` status.
- Subtask 14.4: update `docs/pipeline/known_limitations.md` only if a new durable
  limitation is found.
- Subtask 14.5: update `PROJECT_GUIDE.md` only if repository orientation,
  contributor reading order, or the documentation map changes.

Expected output: repository context remains resumable after issue completion.

## Planned Initial SQLite Shape

The first storage schema should remain intentionally small and focused on local
single-user MVP storage:

```text
app_metadata
- key
- value

curricula
- id
- display_name
- payload_json
- schema_version
- policy_name
- policy_version
- source_format
- source_identifier
- validation_status
- created_at
- updated_at

curriculum_diagnostics
- id
- curriculum_id
- severity
- code
- message
- source_location
- path_json
- details_json
- created_at
```

The exact SQL names may change during implementation if a smaller or clearer
schema is found. Any deviation must be recorded in this issue document.

## Definition Of Done

- `src/open_cvn_app/` contains the local SQLite storage module.
- `open-cvn store init [--path PATH]` creates a real local SQLite database.
- The store schema records a schema version.
- Valid Open CVN JSON can be stored and read back without semantic data loss.
- Invalid Open CVN JSON cannot be stored as a valid curriculum record.
- Parser diagnostics can be persisted and loaded.
- Repository create, read, update, list, and delete behavior is covered by tests.
- CLI storage initialization behavior is covered by tests.
- Existing parser/validator contract tests still pass.
- Full repository verification passes or a documented reason is recorded.
- Persistent documentation is updated in the same session as the implementation.

## Expected Output

- storage module under `src/open_cvn_app/`
- SQLite schema initialization
- repository tests
- documented local database behavior

## Verification

- temporary database tests pass
- stored Open CVN JSON can be read back without data loss
- invalid JSON cannot be stored as a valid curriculum record
- full repository verification passes or a reason is documented

## Implementation Notes

- The local storage module is implemented at:
  - `src/open_cvn_app/storage.py`
- The implementation uses Python standard-library `sqlite3`; no new database
  dependency was added.
- The initial store schema version is `1` and is recorded in `app_metadata`.
- Store initialization is idempotent through `initialize_store(path)`.
- Repository operations are exposed through `CurriculumRepository` and cover:
  - `create_curriculum(...)`
  - `get_curriculum(...)`
  - `list_curricula(...)`
  - `update_curriculum(...)`
  - `replace_curriculum_payload(...)`
  - `delete_curriculum(...)`
  - `list_diagnostics(...)`
- Application storage records are represented through dataclasses including:
  - `StoreInfo`
  - `CurriculumCreate`
  - `CurriculumUpdate`
  - `CurriculumRecord`
  - `CurriculumDiagnostic`
- Storage errors are represented through explicit exception types including:
  - `StoreNotInitialized`
  - `IncompatibleStoreSchema`
  - `CurriculumNotFound`
  - `InvalidCurriculumDocument`
- Open CVN documents are validated with `validate_open_cvn_json(...)` from
  `src/open_cvn/` before storage.
- Invalid or failed validation results are rejected before insertion.
- Valid documents are stored as deterministic canonical JSON text using compact
  separators and sorted object keys.
- Parser or import diagnostics can be passed into create and replace operations
  and are stored under `curriculum_diagnostics`.
- Diagnostic `path` and `details` values are serialized as JSON text.
- `open-cvn store init [--path PATH]` now creates a real SQLite store and reports
  the resolved store path plus schema version.
- The other CLI command groups remain placeholders for their later issues.
- `src/generated/` was not modified.

## Implemented SQLite Shape

```text
app_metadata
- key
- value

curricula
- id
- display_name
- payload_json
- schema_version
- policy_name
- policy_version
- source_format
- source_identifier
- validation_status
- created_at
- updated_at

curriculum_diagnostics
- id
- curriculum_id
- severity
- code
- message
- source_location
- path_json
- details_json
- created_at
```

Implemented indexes:

- `idx_curricula_display_name`
- `idx_curricula_updated_at`
- `idx_curriculum_diagnostics_curriculum_id`

## Tests Added Or Updated

- Added `tests/test_open_cvn_app_storage_unit.py`.
- Updated `tests/test_open_cvn_app_cli_unit.py` so `store init` expects real store
  initialization instead of issue `#62` placeholder routing.
- Updated `tests/test_generation_pipeline_json_schema.py` so the JSON Schema CLI
  subprocess test uses the existing xsdata generation lock and does not race with
  generated artifact regeneration under `pytest -n auto`.

The storage tests cover:

- schema initialization and metadata creation
- idempotent initialization
- repository create, read, list, update, replace, delete, and missing-record
  behavior
- Open CVN JSON payload round-trip semantics
- rejection of invalid Open CVN JSON
- diagnostic persistence and replacement

## Verification Performed

- `uv run pytest -n auto tests/test_open_cvn_app_storage_unit.py -v`
  - result: `7 passed in 24.88s`
- `uv run pytest -n auto tests/test_open_cvn_app_cli_unit.py -v`
  - result: `9 passed in 20.66s`
- `uv run pytest -n auto tests/test_open_cvn_json_import_unit.py tests/test_parser_validator_contract_unit.py -v`
  - result: `22 passed in 32.96s`
- `uv run pytest -n auto tests/test_generation_pipeline_json_schema.py::test_json_schema_generator_cli_writes_output -v`
  - result: `1 passed in 62.65s`
- `uv run pytest -n auto tests/test_open_cvn_app_storage_unit.py tests/test_open_cvn_app_cli_unit.py -v`
  - result: `16 passed in 26.62s`
- `uv run open-cvn store init --path /tmp/opencode/open-cvn-issue-62-smoke.sqlite`
  - result: command initialized a SQLite store and reported schema version `1`
- `uv run pytest -n auto tests`
  - result: `386 passed in 371.09s (0:06:11)`

## Deviations From Planned Scope

- No functional deviations.
- The implementation stores deterministic JSON text and does not preserve original
  input whitespace or object ordering. This matches the planned semantic payload
  preservation requirement for later export.
- Verification required a test-infrastructure stabilization in the existing JSON
  Schema CLI subprocess test so it cooperates with the repository's xsdata
  generation lock under xdist.

## New Limitations Found

- No new durable limitations were found.

## Impact On Later Issues

- issue `#63` builds master and derived versions on top of stored documents
- issue `#64` imports and exports through the storage repository

## Status

- Status: completed
