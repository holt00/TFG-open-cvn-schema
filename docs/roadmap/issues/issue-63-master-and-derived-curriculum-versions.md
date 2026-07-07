# Issue 63 - Implement Master And Derived Curriculum Versions

## Summary

Issue `#63` implements the MVP versioning model for one master curriculum and
multiple derived curriculum versions.

This issue is part of epic `#60`.

## Goal

- keep a master curriculum with all known validated data
- create derived versions for specific targets
- allow derived versions to include less data than the master
- preserve traceability from derived entries back to master data

## MVP Versioning Model

The MVP should not implement a complex Git-like history. It should store:

- one master curriculum per local store or profile
- derived versions that reference the master curriculum
- version metadata such as name, purpose, created date, and updated date
- selection rules or derived JSON payloads sufficient for export

The preferred MVP approach is selection-based derivation: a derived version stores
which sections or entries from the master are included or excluded. If direct field
overrides are implemented, they must be explicit and auditable.

## Planned Scope

- mark one stored curriculum as master
- create derived version records
- list master and derived versions
- clone a derived version from the master
- include or exclude curriculum sections or entries
- generate an Open CVN JSON document for a derived version
- preserve trace metadata and source references where possible

## Planned Steps

1. define version records in the SQLite schema
2. define derived-version selection model
3. implement master creation or assignment
4. implement derived version creation from master
5. implement include/exclude behavior for sections and entries
6. implement derived Open CVN JSON materialization
7. add tests for master, derived, clone, include, exclude, and export behavior
8. document the MVP versioning model and known limits

## Detailed Execution Plan

This plan is the accepted execution plan for implementing issue `#63`.
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

- Subtask 1.1: confirm issue `#63` is limited to master and derived curriculum
  versioning.
- Subtask 1.2: confirm Open CVN JSON import and export remain planned for issue
  `#64`.
- Subtask 1.3: confirm LaTeX and PDF behavior remain planned for issues `#66`
  and `#67`.
- Subtask 1.4: confirm fine-grained editing remains planned for issue `#65`.
- Subtask 1.5: confirm `src/generated/` remains untouched.
- Subtask 1.6: confirm the MVP stores one master curriculum version per local
  SQLite store.

Expected output: final implementation boundary for issue `#63` before code work.

### Task 2 - Define Versioning Data Model

- Subtask 2.1: add a `curriculum_versions` SQLite table.
- Subtask 2.2: store version identifiers, names, kind, master curriculum link,
  optional source version link, selection JSON, and timestamps.
- Subtask 2.3: support version kinds `master` and `derived`.
- Subtask 2.4: enforce unique version names.
- Subtask 2.5: enforce at most one master version per store, preferably through a
  partial unique index when supported by SQLite.
- Subtask 2.6: link `master_curriculum_id` to `curricula(id)`.
- Subtask 2.7: link `source_version_id` to `curriculum_versions(id)` for cloned
  or derived versions.
- Subtask 2.8: create indexes for name, kind, updated timestamp, and master
  curriculum lookup.

Expected output: stable SQLite versioning model layered over the issue `#62`
curriculum storage table.

### Task 3 - Define Derived Selection Contract

- Subtask 3.1: define application-level versioning records such as
  `CurriculumVersionCreate`, `CurriculumVersionRecord`, `DerivedSelection`,
  `SelectionRule`, and `MaterializedVersion` where needed.
- Subtask 3.2: use JSON Pointer syntax from RFC 6901 for section and entry
  selection paths.
- Subtask 3.3: define the MVP selection modes `include_all` and `include_only`.
- Subtask 3.4: represent selection data as deterministic JSON with
  `included_pointers` and `excluded_pointers` arrays.
- Subtask 3.5: support section pointers such as `/curriculum/education`.
- Subtask 3.6: support entry pointers such as `/curriculum/research/0`.
- Subtask 3.7: validate pointer syntax before storing selection changes.
- Subtask 3.8: validate that pointers resolve against the master document when
  materializing a version or updating selection.

Expected output: auditable selection model without Git-like history or implicit
field overrides.

### Task 4 - Migrate SQLite Schema

- Subtask 4.1: update the application storage schema version from `1` to `2`.
- Subtask 4.2: implement an additive migration from schema version `1` to schema
  version `2`.
- Subtask 4.3: keep initialization idempotent for fresh schema version `2`
  stores.
- Subtask 4.4: keep existing future-schema rejection behavior for unsupported
  schema versions newer than the application.
- Subtask 4.5: preserve existing `curricula` and `curriculum_diagnostics` records
  during migration.
- Subtask 4.6: test migration from an issue `#62`-style schema version `1` store.

Expected output: existing local stores can receive versioning support without data
loss.

### Task 5 - Implement Version Repository Operations

- Subtask 5.1: extend `CurriculumRepository` or introduce a small versioning
  repository in `src/open_cvn_app/storage.py`.
- Subtask 5.2: define versioning errors such as `CurriculumVersionNotFound`,
  `MasterCurriculumNotFound`, `DuplicateCurriculumVersionName`, and
  `InvalidSelectionRule`.
- Subtask 5.3: implement master assignment from an existing stored curriculum.
- Subtask 5.4: reject master assignment when the referenced curriculum does not
  exist.
- Subtask 5.5: enforce one master version per store and fail clearly on
  duplicates unless an explicit replacement operation is later introduced.
- Subtask 5.6: implement master lookup.
- Subtask 5.7: implement version lookup by ID or name.
- Subtask 5.8: implement version listing with deterministic ordering.
- Subtask 5.9: implement derived version creation from master by default.
- Subtask 5.10: implement derived version cloning from another derived version by
  copying its selection state.
- Subtask 5.11: wrap version writes in transactions and update timestamps.

Expected output: repository-level API for creating and listing master and derived
curriculum versions.

### Task 6 - Implement Derived Materialization

- Subtask 6.1: implement materialization of a named or identified version into an
  Open CVN JSON document.
- Subtask 6.2: return the master curriculum payload unchanged for the master
  version, except for any versioning metadata explicitly added to the materialized
  copy.
- Subtask 6.3: load the master curriculum payload for derived versions.
- Subtask 6.4: apply `include_all` selection by removing excluded pointers from a
  deep copy of the master payload.
- Subtask 6.5: apply `include_only` selection by building a canonical Open CVN
  document from included pointers.
- Subtask 6.6: preserve canonical root fields `schema_version`, `metadata`,
  `curriculum`, and `extensions`.
- Subtask 6.7: record versioning metadata under a namespaced extension such as
  `extensions["x-open-cvn.versioning"]`.
- Subtask 6.8: preserve existing entry-level and field-level trace metadata.
- Subtask 6.9: validate materialized Open CVN JSON through
  `validate_open_cvn_json(...)`.
- Subtask 6.10: fail clearly when selection rules produce an invalid Open CVN JSON
  document.

Expected output: derived versions can produce export-ready Open CVN JSON payloads
for later issue `#64`.

### Task 7 - Implement Include And Exclude Selection Edits

- Subtask 7.1: implement exclusion of a JSON Pointer from a derived version.
- Subtask 7.2: implement inclusion of a JSON Pointer in a derived version.
- Subtask 7.3: reject selection edits against the master version.
- Subtask 7.4: reject selection edits for missing versions.
- Subtask 7.5: reject selection pointers that do not resolve against the master
  payload.
- Subtask 7.6: avoid duplicate pointers in stored selection arrays.
- Subtask 7.7: update derived version `updated_at` after selection edits.
- Subtask 7.8: keep serialized selection JSON deterministic.

Expected output: MVP include/exclude behavior for sections and entries without
mutating master curriculum data.

### Task 8 - Wire Versioning Into CLI

- Subtask 8.1: replace the issue `#63` placeholder behavior for
  `open-cvn versions list`.
- Subtask 8.2: replace the issue `#63` placeholder behavior for
  `open-cvn versions derive NAME [--from SOURCE]`.
- Subtask 8.3: add a command for assigning a stored curriculum as master, such as
  `open-cvn versions master CURRICULUM_ID [--store PATH]`.
- Subtask 8.4: add a command for showing a version, such as
  `open-cvn versions show NAME [--store PATH]`, if useful for testable CLI
  behavior.
- Subtask 8.5: add commands for selection edits, such as
  `open-cvn versions exclude NAME POINTER [--store PATH]` and
  `open-cvn versions include NAME POINTER [--store PATH]`.
- Subtask 8.6: format version listing output with name, kind, ID, source, and
  timestamps.
- Subtask 8.7: convert storage and versioning errors into `AppResult.failed(...)`.
- Subtask 8.8: keep JSON import/export, LaTeX, and PDF commands scoped to their
  later issues.

Expected output: CLI can create and manage master and derived version records.

### Task 9 - Add Versioning Unit Tests

- Subtask 9.1: create `tests/test_open_cvn_app_versioning_unit.py`.
- Subtask 9.2: test master assignment from an existing curriculum.
- Subtask 9.3: test single-master enforcement.
- Subtask 9.4: test version listing includes the master version.
- Subtask 9.5: test derived version creation from master.
- Subtask 9.6: test derived version cloning from another derived version.
- Subtask 9.7: test duplicate version names are rejected.
- Subtask 9.8: test missing master and missing source version behavior.
- Subtask 9.9: test section exclusion removes selected data from materialized
  output.
- Subtask 9.10: test entry exclusion removes only the selected entry.
- Subtask 9.11: test selection edits do not mutate the stored master payload.
- Subtask 9.12: test materialized JSON validates through the public Open CVN
  validator.
- Subtask 9.13: test trace metadata survives materialization.
- Subtask 9.14: test schema version `1` stores migrate to schema version `2`.

Expected output: temporary SQLite tests prove master, derived, clone, include,
exclude, migration, and materialization behavior.

### Task 10 - Update CLI Tests

- Subtask 10.1: update the existing `versions list` CLI test that currently
  expects placeholder behavior.
- Subtask 10.2: update the existing `versions derive` CLI test that currently
  expects placeholder behavior.
- Subtask 10.3: test `versions list` against an initialized store.
- Subtask 10.4: test master assignment command.
- Subtask 10.5: test derived version creation command.
- Subtask 10.6: test include and exclude command behavior if those commands are
  added.
- Subtask 10.7: test errors for uninitialized store, missing master, and duplicate
  names.
- Subtask 10.8: keep JSON, LaTeX, and PDF placeholder tests unchanged.

Expected output: CLI tests reflect real issue `#63` versioning behavior.

### Task 11 - Prepare Or Extend Test Fixtures

- Subtask 11.1: reuse `tests/fixtures/open_cvn/valid_minimal.json` where enough.
- Subtask 11.2: add a richer Open CVN JSON fixture only if section or entry
  selection cannot be tested clearly with the existing fixture.
- Subtask 11.3: include stable entry `id` values in any new repeated-section
  fixture where useful.
- Subtask 11.4: keep fixtures deterministic and ASCII unless existing fixture
  content requires otherwise.

Expected output: representative test data for section and entry selection without
overbuilding fixtures.

### Task 12 - Run Issue Verification

- Subtask 12.1: run targeted versioning tests:
  `uv run pytest -n auto tests/test_open_cvn_app_versioning_unit.py -v`.
- Subtask 12.2: run storage and CLI tests:
  `uv run pytest -n auto tests/test_open_cvn_app_storage_unit.py tests/test_open_cvn_app_cli_unit.py -v`.
- Subtask 12.3: run parser integration regressions:
  `uv run pytest -n auto tests/test_open_cvn_json_import_unit.py tests/test_parser_validator_contract_unit.py -v`.
- Subtask 12.4: run a console-script smoke check for the implemented versioning
  commands.
- Subtask 12.5: run full repository verification:
  `uv run pytest -n auto tests`.
- Subtask 12.6: record any skipped or failed verification with reason.

Expected output: issue `#63` verification evidence.

### Task 13 - Update Persistent Documentation

- Subtask 13.1: update this issue document with actual implementation artifacts,
  deviations, verification, and status.
- Subtask 13.2: update `docs/context/current_status.md` so issue `#63` is recorded
  accurately and issue `#64` becomes the next implementation issue if `#63` is
  completed.
- Subtask 13.3: update `docs/roadmap/cvn_generation_roadmap.md` if it tracks issue
  `#63` status.
- Subtask 13.4: update `docs/pipeline/known_limitations.md` only if a new durable
  limitation is found.
- Subtask 13.5: update `PROJECT_GUIDE.md` only if repository orientation,
  contributor reading order, or the documentation map changes.

Expected output: repository context remains resumable after issue completion.

## Planned Versioning SQLite Shape

The issue should add a small versioning layer over the existing issue `#62`
storage schema:

```text
curriculum_versions
- id
- name
- kind
- master_curriculum_id
- source_version_id
- selection_json
- created_at
- updated_at
```

Planned indexes and constraints:

- unique version name
- at most one master version per store
- lookup by kind
- lookup by updated timestamp
- lookup by master curriculum ID

The exact SQL names may change during implementation if a smaller or clearer
schema is found. Any deviation must be recorded in this issue document.

## Planned Selection JSON Shape

The preferred MVP selection model is selection-based derivation. A derived
version should store deterministic JSON similar to:

```json
{
  "mode": "include_all",
  "included_pointers": [],
  "excluded_pointers": []
}
```

Selection pointers should use JSON Pointer syntax from RFC 6901 and target the
Open CVN JSON document, especially `curriculum` sections and repeated entries.
The implementation should not introduce implicit field overrides in issue `#63`.
If overrides become necessary, they must be explicit, auditable, and documented as
a deviation from the preferred MVP selection approach.

## Definition Of Done

- Local store schema supports master and derived curriculum versions.
- Existing issue `#62` schema version `1` stores can migrate to the issue `#63`
  schema without data loss.
- One master version can be assigned from an existing stored curriculum.
- Multiple derived versions can reference the master curriculum.
- Derived versions can be cloned from master or another derived version.
- Include and exclude selection rules can be stored and updated for derived
  versions.
- Materialized derived Open CVN JSON contains selected data only.
- Master curriculum data remains unchanged after derived selection edits.
- Existing trace metadata is preserved where selected data is retained.
- CLI version commands are functional and deterministic.
- Tests cover master, derived, clone, include, exclude, migration, and
  materialization behavior.
- Full repository verification passes or a documented reason is recorded.
- Persistent documentation is updated in the same session as the implementation.

## Expected Output

- versioning service or repository module
- CLI commands for listing and creating versions
- tests for master and derived behavior
- documentation of version semantics

## Verification

- derived version can be created from master
- derived version export contains selected data only
- master data remains unchanged after derived selection edits
- full repository verification passes or a reason is documented

## Implementation Notes

- The versioning implementation extends the existing local storage module at:
  - `src/open_cvn_app/storage.py`
- The application storage schema version is now `2`.
- Existing schema version `1` stores from issue `#62` are migrated additively to
  schema version `2`.
- The implementation uses Python standard-library `sqlite3`; no new database
  dependency was added.
- Version records are represented by dataclasses including:
  - `DerivedSelection`
  - `CurriculumVersionRecord`
  - `MaterializedVersion`
- Versioning errors are represented through explicit exception types including:
  - `CurriculumVersionNotFound`
  - `MasterCurriculumNotFound`
  - `DuplicateCurriculumVersionName`
  - `InvalidSelectionRule`
- Repository operations are exposed through `CurriculumRepository` and cover:
  - `assign_master_curriculum(...)`
  - `get_master_version(...)`
  - `get_version(...)`
  - `list_versions(...)`
  - `create_derived_version(...)`
  - `include_in_version(...)`
  - `exclude_from_version(...)`
  - `materialize_version(...)`
- Selection rules use JSON Pointer-style paths under `/curriculum` for sections
  and entries.
- Selection pointers intentionally reject metadata/root edits in issue `#63` so
  derived versions cannot accidentally invalidate non-curriculum document
  metadata.
- Materialized versions are validated through `validate_open_cvn_json(...)` before
  being returned.
- Materialization records version metadata under
  `extensions["x-open-cvn.versioning"]`.
- `src/generated/` was not modified.

## Implemented SQLite Shape

```text
curriculum_versions
- id
- name
- kind
- master_curriculum_id
- source_version_id
- selection_json
- created_at
- updated_at
```

Implemented constraints and indexes:

- unique `name`
- `kind` check constrained to `master` or `derived`
- partial unique index `idx_curriculum_versions_single_master` for one master
  version per store
- `idx_curriculum_versions_name`
- `idx_curriculum_versions_kind`
- `idx_curriculum_versions_updated_at`
- `idx_curriculum_versions_master_curriculum_id`

## Implemented CLI Behavior

Issue `#63` replaces the previous versioning placeholders with functional
commands:

```text
open-cvn versions list [--store PATH]
open-cvn versions master CURRICULUM_ID [--store PATH]
open-cvn versions show NAME [--store PATH]
open-cvn versions derive NAME [--from SOURCE] [--store PATH]
open-cvn versions include NAME POINTER [--store PATH]
open-cvn versions exclude NAME POINTER [--store PATH]
```

The JSON import/export, LaTeX, and PDF command groups remain scoped to later
issues.

## Tests Added Or Updated

- Added `tests/test_open_cvn_app_versioning_unit.py`.
- Updated `tests/test_open_cvn_app_cli_unit.py` so versioning commands expect real
  behavior instead of issue `#63` placeholders.

The versioning tests cover:

- master assignment from an existing stored curriculum
- single-master enforcement
- derived version creation from master
- derived version cloning from another derived version
- duplicate version name rejection
- missing master behavior
- section exclusion materialization
- entry exclusion materialization
- master immutability after derived selection edits
- trace metadata preservation
- invalid selection pointer rejection
- schema version `1` to schema version `2` migration

## Verification Performed

- `uv run pytest -n auto tests/test_open_cvn_app_versioning_unit.py -v`
  - result: `11 passed in 34.52s`
- `uv run pytest -n auto tests/test_open_cvn_app_storage_unit.py tests/test_open_cvn_app_cli_unit.py -v`
  - result: `18 passed in 32.47s`
- `uv run pytest -n auto tests/test_open_cvn_json_import_unit.py tests/test_parser_validator_contract_unit.py -v`
  - result: `22 passed in 34.91s`
- `uv run open-cvn store init --path /tmp/opencode/open-cvn-issue-63-smoke.sqlite && uv run open-cvn versions list --store /tmp/opencode/open-cvn-issue-63-smoke.sqlite`
  - result: command initialized schema version `2` store and listed no versions
    successfully
- `uv run pytest -n auto tests`
  - result: `399 passed in 431.30s (0:07:11)`

## Deviations From Planned Scope

- The issue implemented CLI include/exclude selection commands directly in issue
  `#63` rather than deferring all selection editing to issue `#65`.
- This was kept within the planned issue `#63` scope because the issue goal
  explicitly included include/exclude behavior for derived versions.
- Issue `#65` can now focus on richer editing and user-facing selection workflows
  over the repository behavior implemented here.
- When a full section is excluded, materialization removes the selected entries;
  the Open CVN validator may normalize the section back to an empty list in the
  returned document. This preserves selected-data semantics while keeping the
  document valid.

## New Limitations Found

- No new durable limitations were found.

## Impact On Later Issues

- issue `#64` can export materialized master or derived Open CVN JSON documents
- issue `#65` can build richer editing and user-facing selection workflows on top
  of the implemented repository selection behavior
- issue `#66` exports selected derived versions to LaTeX

## Status

- Status: completed
