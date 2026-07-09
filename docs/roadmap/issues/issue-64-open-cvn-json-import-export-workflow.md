# Issue 64 - Implement Open CVN JSON Import And Export Workflow

## Summary

Issue `#64` connects the epic `#41` parser/validator to the MVP application
storage and versioning workflow.

This issue is part of epic `#60`.

## Goal

- import Open CVN JSON into local storage
- export master or derived versions as Open CVN JSON
- preserve validation status, structured parser issues, and trace metadata
- provide CLI commands that prove the storage and exchange workflow

## Dependency On Epic `#41`

Import must call `parse_open_cvn_json(...)` or `validate_open_cvn_json(...)` from
`open_cvn`. It must not validate against a new app-specific JSON shape.

## Planned Scope

- `open-cvn import-json <path>` or equivalent
- `open-cvn export-json <version> <path>` or equivalent
- import from existing examples under `examples/open_cvn/`
- reject invalid input with structured error output
- store accepted documents through issue `#62` repository functions
- export canonical Open CVN JSON with deterministic formatting

## Planned Steps

1. review parser workflow docs and Open CVN JSON examples
2. implement JSON import command
3. route validation errors to user-readable CLI output
4. persist valid imported documents as master or named records
5. implement JSON export command for stored master versions
6. extend export to derived versions after issue `#63`
7. add CLI and repository integration tests
8. document import/export commands

## Detailed Execution Plan

This plan is the accepted execution plan for implementing issue `#64`.
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

- Subtask 1.1: confirm issue `#64` is limited to Open CVN JSON application import
  and export.
- Subtask 1.2: confirm import must use `parse_open_cvn_json(...)` or
  `validate_open_cvn_json(...)` from the public `open_cvn` package.
- Subtask 1.3: confirm no app-specific JSON validator or alternate JSON shape is
  introduced.
- Subtask 1.4: confirm storage must use the issue `#62` and issue `#63`
  repository APIs in `src/open_cvn_app/storage.py`.
- Subtask 1.5: confirm export must support materialized master and derived
  versions through `CurriculumRepository.materialize_version(...)`.
- Subtask 1.6: confirm issue `#64` does not implement curriculum editing,
  LaTeX export, PDF generation, or LLM import behavior.
- Subtask 1.7: confirm `src/generated/` remains untouched.

Expected output: final implementation boundary for issue `#64` before code work.

### Task 2 - Define Stable CLI Behavior

- Subtask 2.1: keep the existing command family names from issue `#61`:
  `open-cvn json import` and `open-cvn json export`.
- Subtask 2.2: extend `open-cvn json import INPUT [--store PATH]` with optional
  `--name NAME` for the stored curriculum display name.
- Subtask 2.3: extend `open-cvn json import INPUT [--store PATH]` with optional
  `--as-master` for assigning the imported curriculum as the master version.
- Subtask 2.4: keep `open-cvn json export OUTPUT [--store PATH] [--version NAME]`
  and use `master` as the default version name.
- Subtask 2.5: define successful import output including display name,
  curriculum ID, validation status, and source path.
- Subtask 2.6: define successful import-with-master output including the assigned
  master version ID.
- Subtask 2.7: define failed import output including validation status and one
  line per structured parser issue with code, severity, path, location, and
  message.
- Subtask 2.8: define successful export output including version name, output
  path, and validation status.

Expected output: deterministic CLI output contract that tests can assert.

### Task 3 - Extend CLI Argument Parsing

- Subtask 3.1: modify `src/open_cvn_app/cli.py` so `json import` accepts
  `--name NAME`.
- Subtask 3.2: modify `src/open_cvn_app/cli.py` so `json import` accepts
  `--as-master`.
- Subtask 3.3: keep `json export` positional `OUTPUT`, `--store`, and `--version`
  behavior unchanged.
- Subtask 3.4: verify `open-cvn --help` still lists the same command groups.

Expected output: parser accepts the issue `#64` import/export surface without
breaking existing commands.

### Task 4 - Add CLI Formatting And JSON Writing Helpers

- Subtask 4.1: add a private helper in `src/open_cvn_app/cli.py` for formatting
  parser issues into deterministic CLI lines.
- Subtask 4.2: include parser issue `code`, `severity`, `path`,
  `source_location`, and `message` in formatted output.
- Subtask 4.3: add a private helper in `src/open_cvn_app/cli.py` for canonical
  JSON export writing.
- Subtask 4.4: write exported JSON with `ensure_ascii=False`, `sort_keys=True`,
  `indent=2`, and a final newline.
- Subtask 4.5: create parent directories for explicit nested export paths.

Expected output: small local helpers keep import/export handlers readable and make
output deterministic.

### Task 5 - Implement JSON Import Command

- Subtask 5.1: replace the issue `#64` placeholder in `_handle_json_import(...)`.
- Subtask 5.2: resolve the local store path through `OpenCvnAppConfig`.
- Subtask 5.3: call `parse_open_cvn_json(...)` with the input path and source
  identifier.
- Subtask 5.4: reject `invalid` and `failed` parse results before storage.
- Subtask 5.5: reject parse results with missing `data` before storage.
- Subtask 5.6: derive the display name from `--name` or the input path stem.
- Subtask 5.7: persist the validated document through
  `CurriculumRepository.create_curriculum(...)`.
- Subtask 5.8: preserve parser warnings as repository diagnostics.
- Subtask 5.9: when `--as-master` is passed, call
  `CurriculumRepository.assign_master_curriculum(...)` for the imported
  curriculum.
- Subtask 5.10: convert `StorageError` failures into `AppResult.failed(...)`.

Expected output: valid Open CVN JSON files import into local SQLite storage.

### Task 6 - Implement JSON Export Command

- Subtask 6.1: replace the issue `#64` placeholder in `_handle_json_export(...)`.
- Subtask 6.2: resolve the local store path through `OpenCvnAppConfig`.
- Subtask 6.3: materialize the requested version through
  `CurriculumRepository.materialize_version(...)`.
- Subtask 6.4: write the materialized Open CVN JSON document to the output path
  with deterministic formatting.
- Subtask 6.5: preserve materialized version metadata under
  `extensions["x-open-cvn.versioning"]` as produced by issue `#63`.
- Subtask 6.6: convert `StorageError` and `OSError` failures into
  `AppResult.failed(...)`.

Expected output: stored master and derived versions export as canonical Open CVN
JSON files.

### Task 7 - Add CLI Import Tests For Valid Documents

- Subtask 7.1: update `tests/test_open_cvn_app_cli_unit.py` so the previous JSON
  import placeholder test expects real import behavior.
- Subtask 7.2: use `tests/fixtures/open_cvn/valid_minimal.json` as the import
  fixture.
- Subtask 7.3: run `json import <fixture> --store <tmp> --name "Imported CV"`.
- Subtask 7.4: assert the command exits with code `0`.
- Subtask 7.5: assert output includes the import success message, curriculum ID,
  and `Validation status: valid`.
- Subtask 7.6: load the temporary store through `CurriculumRepository` and assert
  one curriculum was created.
- Subtask 7.7: assert the stored display name and source identifier match the CLI
  input.

Expected output: CLI test proves a valid Open CVN JSON file is stored.

### Task 8 - Add CLI Import Tests For Master Assignment

- Subtask 8.1: run `json import <fixture> --store <tmp> --as-master`.
- Subtask 8.2: assert the command exits with code `0`.
- Subtask 8.3: assert output includes the master assignment message.
- Subtask 8.4: assert `CurriculumRepository.list_versions()` returns a master
  version linked to the imported curriculum.
- Subtask 8.5: test duplicate master handling by importing another document with
  `--as-master` into a store that already has a master.
- Subtask 8.6: assert duplicate master handling exits with code `1` and reports a
  clear storage error.

Expected output: import can optionally create the master version, and duplicate
master failures are visible.

### Task 9 - Add CLI Import Tests For Invalid Documents

- Subtask 9.1: run `json import tests/fixtures/open_cvn/wrong_shape.json --store
  <tmp>`.
- Subtask 9.2: assert the command exits with code `1`.
- Subtask 9.3: assert stderr includes `Open CVN JSON import failed` and
  `json_schema_validation_failure`.
- Subtask 9.4: assert no curriculum records were stored.
- Subtask 9.5: run `json import tests/fixtures/open_cvn/malformed.json --store
  <tmp>`.
- Subtask 9.6: assert stderr includes `invalid_json`.
- Subtask 9.7: assert no curriculum records were stored for malformed input.

Expected output: invalid and malformed JSON fail with structured error output and
do not pollute storage.

### Task 10 - Add CLI Export Tests For Master Versions

- Subtask 10.1: create a temporary store and store a valid Open CVN JSON document.
- Subtask 10.2: assign the stored curriculum as the master version.
- Subtask 10.3: run `json export <output> --store <tmp> --version master`.
- Subtask 10.4: assert the command exits with code `0`.
- Subtask 10.5: assert the output file exists.
- Subtask 10.6: parse the exported file as JSON and validate it with
  `validate_open_cvn_json(...)`.
- Subtask 10.7: assert validation status is `valid`.
- Subtask 10.8: assert the file uses deterministic pretty JSON and ends with a
  newline.

Expected output: master version export writes a revalidable canonical JSON file.

### Task 11 - Add CLI Export Tests For Derived Versions

- Subtask 11.1: create a temporary store using `examples/open_cvn/research_entry.json`
  or an equivalent multi-entry fixture.
- Subtask 11.2: assign the stored curriculum as master.
- Subtask 11.3: create a derived version named `public`.
- Subtask 11.4: exclude a curriculum pointer such as `/curriculum/research` or a
  repeated entry pointer.
- Subtask 11.5: run `json export <output> --store <tmp> --version public`.
- Subtask 11.6: assert the exported document contains selected data only.
- Subtask 11.7: assert `extensions["x-open-cvn.versioning"]["version_name"]` is
  `public`.
- Subtask 11.8: validate the exported document with `validate_open_cvn_json(...)`.

Expected output: derived version export uses issue `#63` materialization behavior.

### Task 12 - Add CLI Export Failure Tests

- Subtask 12.1: run export against an uninitialized store.
- Subtask 12.2: assert the command exits with code `1` and reports export failure.
- Subtask 12.3: run export for a missing version name in an initialized store.
- Subtask 12.4: assert the command exits with code `1` and reports the missing
  version error.
- Subtask 12.5: run export to a nested output path and assert parent directories
  are created.

Expected output: export failures are deterministic and nested output paths work.

### Task 13 - Run Targeted Verification

- Subtask 13.1: run CLI tests:
  `uv run pytest -n auto tests/test_open_cvn_app_cli_unit.py -v`.
- Subtask 13.2: run storage and versioning regressions:
  `uv run pytest -n auto tests/test_open_cvn_app_storage_unit.py tests/test_open_cvn_app_versioning_unit.py -v`.
- Subtask 13.3: run parser contract regressions:
  `uv run pytest -n auto tests/test_open_cvn_json_import_unit.py tests/test_parser_validator_contract_unit.py -v`.
- Subtask 13.4: record exact results in this issue document.

Expected output: targeted issue `#64` behavior and dependencies pass.

### Task 14 - Run Console Script Smoke Verification

- Subtask 14.1: initialize a temporary smoke store with
  `uv run open-cvn store init --path /tmp/opencode/open-cvn-issue-64-smoke.sqlite`.
- Subtask 14.2: import a representative example with
  `uv run open-cvn json import examples/open_cvn/minimal.json --store /tmp/opencode/open-cvn-issue-64-smoke.sqlite --as-master`.
- Subtask 14.3: export the master version with
  `uv run open-cvn json export /tmp/opencode/open-cvn-issue-64-export.json --store /tmp/opencode/open-cvn-issue-64-smoke.sqlite --version master`.
- Subtask 14.4: record whether the smoke workflow completed successfully.

Expected output: installed console command proves the import/export workflow
outside direct unit tests.

### Task 15 - Run Full Repository Verification

- Subtask 15.1: run `uv run pytest -n auto tests`.
- Subtask 15.2: record the exact pass/fail result in this issue document.
- Subtask 15.3: if full verification cannot be completed, record the skipped
  command and reason.

Expected output: full repository verification passes or a documented reason is
available.

### Task 16 - Update Persistent Documentation

- Subtask 16.1: update this issue document with actual implementation artifacts,
  deviations, verification, and status.
- Subtask 16.2: update `docs/context/current_status.md` so issue `#64` is recorded
  accurately and issue `#65` becomes the next implementation issue if `#64` is
  completed.
- Subtask 16.3: update `docs/roadmap/cvn_generation_roadmap.md` if it tracks issue
  `#64` status.
- Subtask 16.4: update `docs/pipeline/known_limitations.md` only if a new durable
  limitation is found.
- Subtask 16.5: update `PROJECT_GUIDE.md` only if repository orientation,
  contributor reading order, or the documentation map changes.

Expected output: repository context remains resumable after issue completion.

## Planned CLI Shape

```text
open-cvn json import INPUT [--store PATH] [--name NAME] [--as-master]
open-cvn json export OUTPUT [--store PATH] [--version NAME]
```

## Planned Import Output Shape

Successful import without master assignment should report:

```text
Imported Open CVN JSON as curriculum '<display_name>'.
Curriculum ID: <curriculum_id>
Validation status: <validation_status>
Source: <input_path>
```

Successful import with `--as-master` should additionally report:

```text
Assigned master curriculum version 'master' with id <version_id>.
```

Invalid import should report structured parser issues in a user-readable form,
including at least issue code, severity, path, source location, and message.

## Planned Export Output Shape

Successful export should report:

```text
Exported Open CVN JSON version '<version_name>' to <output_path>.
Validation status: <validation_status>
```

Exported JSON should be deterministic:

```text
ensure_ascii=False
sort_keys=True
indent=2
final newline
```

## Definition Of Done

- `open-cvn json import` imports valid Open CVN JSON into local SQLite storage.
- Import uses `parse_open_cvn_json(...)` or `validate_open_cvn_json(...)` from the
  public `open_cvn` package.
- Import does not introduce an app-specific JSON shape or validator.
- Invalid and malformed input fail with structured user-readable CLI output.
- Import can optionally assign the imported curriculum as the master version.
- `open-cvn json export` exports materialized master and derived versions.
- Exported JSON revalidates with `validate_open_cvn_json(...)`.
- Exported JSON uses deterministic formatting.
- Tests cover valid import, invalid import, malformed import, master export,
  derived export, and export failures.
- Console-script smoke verification covers store init, import, and export.
- Full repository verification passes or a documented reason is recorded.
- Persistent documentation is updated in the same session as the implementation.

## Expected Output

- working JSON import command
- working JSON export command
- tests using safe Open CVN JSON fixtures
- documentation for import/export examples

## Verification

- valid Open CVN JSON imports into local storage
- invalid Open CVN JSON fails with structured error output
- exported JSON revalidates with `validate_open_cvn_json(...)`
- full repository verification passes or a reason is documented

## Implementation Notes

- The Open CVN JSON import/export workflow is implemented in:
  - `src/open_cvn_app/cli.py`
- The implementation keeps the existing issue `#61` command family and replaces
  the issue `#64` placeholders with functional behavior:
  - `open-cvn json import INPUT [--store PATH] [--name NAME] [--as-master]`
  - `open-cvn json export OUTPUT [--store PATH] [--version NAME]`
- Import uses `parse_open_cvn_json(...)` from the public `open_cvn` package.
- Import rejects `invalid` and `failed` parser results before storage.
- Import persists valid documents through `CurriculumRepository.create_curriculum(...)`.
- Parser warnings are preserved as repository diagnostics when present.
- `--name` controls the stored curriculum display name; otherwise the input file
  stem is used.
- `--as-master` assigns the imported curriculum as the master version when no
  master exists.
- `--as-master` fails before creating a new curriculum when the store already has
  a master version.
- Export uses `CurriculumRepository.materialize_version(...)`, so both master and
  derived versions use the issue `#63` versioning behavior.
- Export writes deterministic Open CVN JSON using `ensure_ascii=False`,
  `sort_keys=True`, `indent=2`, and a final newline.
- Export creates parent directories for explicit nested output paths.
- Structured parser errors are rendered in CLI output with code, severity, path,
  source location, and message.
- `src/generated/` was not modified.

## Tests Added Or Updated

- Updated `tests/test_open_cvn_app_cli_unit.py`.

The CLI tests now cover:

- valid Open CVN JSON import into SQLite storage
- import display-name selection through `--name`
- optional master assignment through `--as-master`
- duplicate master rejection without creating an extra curriculum
- invalid Open CVN JSON schema failure output
- malformed JSON failure output
- master version export to deterministic JSON
- derived version export through materialized selection behavior
- missing-version export failure
- uninitialized-store export failure
- existing version, LaTeX, PDF, help, and version command regressions

## Verification Performed

- `uv run pytest -n auto tests/test_open_cvn_app_cli_unit.py -v`
  - result: `18 passed in 17.84s`
- `uv run pytest -n auto tests/test_open_cvn_app_storage_unit.py tests/test_open_cvn_app_versioning_unit.py -v`
  - result: `18 passed in 16.82s`
- `uv run pytest -n auto tests/test_open_cvn_json_import_unit.py tests/test_parser_validator_contract_unit.py -v`
  - result: `22 passed in 16.91s`
- Console-script smoke workflow:
  - `uv run open-cvn store init --path /tmp/opencode/open-cvn-issue-64-smoke-1783526641.sqlite`
  - `uv run open-cvn json import examples/open_cvn/minimal.json --store /tmp/opencode/open-cvn-issue-64-smoke-1783526641.sqlite --as-master`
  - `uv run open-cvn json export /tmp/opencode/open-cvn-issue-64-export-1783526641.json --store /tmp/opencode/open-cvn-issue-64-smoke-1783526641.sqlite --version master`
  - result: workflow initialized schema version `2`, imported `minimal`, assigned
    master, exported valid JSON, and parsed the exported JSON successfully
- `uv run pytest -n auto tests`
  - result: `406 passed in 719.75s (0:11:59)`

## Deviations From Planned Scope

- The accepted plan added `--name` and `--as-master` to make import storage and
  master assignment explicit from the CLI.
- Duplicate `--as-master` imports fail before creating a new curriculum. This is a
  stricter behavior than creating the curriculum first and then failing master
  assignment, and avoids orphan imports from a failed one-step command.

## New Limitations Found

- No new durable limitations were found.

## Impact On Later Issues

- issue `#66` can use exported or stored Open CVN JSON for LaTeX rendering
- issue `#68` documents the complete MVP workflow

## Status

- Status: completed
