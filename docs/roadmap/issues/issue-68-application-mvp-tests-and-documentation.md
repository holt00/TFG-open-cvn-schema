# Issue 68 - Add Application MVP Tests And Documentation

## Summary

Issue `#68` closes the epic `#60` MVP by adding end-to-end tests and user-facing
documentation for the local CV management prototype.

This issue is part of epic `#60`.

## Goal

- prove the MVP workflow works from import to export
- document commands for a user or evaluator
- record known limitations and non-MVP behavior
- update persistent project context after epic `#60`

## Planned Test Coverage

- initialize local store
- import valid Open CVN JSON
- reject invalid Open CVN JSON
- create master curriculum
- create derived version
- include or exclude content in a derived version
- export derived version as Open CVN JSON
- render LaTeX for master or derived version
- handle PDF compiler unavailable case
- run CLI smoke workflow over temporary directories

## Documentation Targets

- application MVP user guide under `docs/development/` or `docs/application/`
- issue `#60` epic record
- issues `#61` through `#68`
- `docs/context/current_status.md`
- `docs/roadmap/cvn_generation_roadmap.md`
- `docs/pipeline/known_limitations.md` if new limitations are found
- `PROJECT_GUIDE.md` if document maps change

## Planned Steps

1. audit implemented application features from issues `#61` through `#67`
2. add focused unit tests for storage, versioning, import/export, and rendering
3. add CLI integration tests over temporary stores
4. add optional PDF behavior tests with mocked compiler paths
5. write user-facing MVP workflow documentation
6. run targeted application tests
7. run full repository verification
8. update epic `#60`, current status, roadmap, and limitation docs

## Detailed Execution Plan

This plan is the accepted execution plan for implementing issue `#68`.
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

- Subtask 1.1: confirm issue `#68` closes the issue `#60` MVP delivery path with
  tests and documentation, not new application features.
- Subtask 1.2: confirm no manual edits are made under `src/generated/`.
- Subtask 1.3: confirm workflow tests use temporary stores and output paths.
- Subtask 1.4: confirm PDF generation remains optional and missing local TeX
  compilers are expected behavior, not a failing MVP condition.
- Subtask 1.5: confirm issue `#69` remains post-MVP exploratory LLM work and does
  not block issue `#68`.

Expected output: final implementation boundary for issue `#68` before test and
documentation work.

### Task 2 - Audit Implemented MVP Surface

- Subtask 2.1: audit issues `#61` through `#67` and confirm completed command
  surface.
- Subtask 2.2: audit `src/open_cvn_app/` modules for CLI, storage, versioning,
  editing, LaTeX, and PDF behavior.
- Subtask 2.3: audit current application test files under `tests/` and record what
  is already covered.
- Subtask 2.4: audit available Open CVN examples and fixtures for workflow tests.
- Subtask 2.5: identify only the remaining issue `#68` gaps so new tests do not
  duplicate unit coverage unnecessarily.

Expected output: coverage and artifact map for the completed application MVP.

### Task 3 - Build MVP Coverage Matrix

- Subtask 3.1: map issue `#68` planned coverage to existing tests and missing
  end-to-end scenarios.
- Subtask 3.2: mark existing coverage for store initialization, JSON import/export,
  versioning, editing, LaTeX rendering, and PDF wrapper behavior.
- Subtask 3.3: mark missing integration coverage for complete import-to-export CLI
  workflow over a temporary store.
- Subtask 3.4: mark missing integration coverage for invalid JSON import not
  polluting storage.
- Subtask 3.5: mark missing isolation coverage for multiple temporary stores or
  nested output paths if not already covered by focused tests.

Expected output: concise test plan for the additional issue `#68` workflow suite.

### Task 4 - Add End-To-End Application Workflow Tests

- Subtask 4.1: create a focused test module such as
  `tests/test_open_cvn_app_mvp_workflow.py`.
- Subtask 4.2: initialize a temporary SQLite store through the CLI behavior.
- Subtask 4.3: import a valid Open CVN JSON example as the master curriculum.
- Subtask 4.4: create a derived version from the master curriculum.
- Subtask 4.5: list sections and repeated entries for the derived version.
- Subtask 4.6: exclude a section or entry from the derived version.
- Subtask 4.7: export the derived version as Open CVN JSON.
- Subtask 4.8: validate the exported JSON with the public Open CVN validator.
- Subtask 4.9: export the derived version to LaTeX and assert deterministic file
  output.
- Subtask 4.10: run PDF generation for the derived version and assert either a
  generated PDF when a compiler is available or the documented missing-compiler
  failure when no supported compiler exists.

Expected output: one workflow test proving the MVP from local store initialization
through JSON, LaTeX, and optional PDF output.

### Task 5 - Add Invalid Import Workflow Tests

- Subtask 5.1: import `tests/fixtures/open_cvn/wrong_shape.json` or an equivalent
  invalid fixture through the CLI workflow.
- Subtask 5.2: assert the command exits with code `1`.
- Subtask 5.3: assert output includes structured parser failure information such as
  `json_schema_validation_failure`.
- Subtask 5.4: assert no curriculum records are stored after the failed import.
- Subtask 5.5: add malformed JSON coverage only if the current focused CLI tests do
  not already make the behavior clear enough.

Expected output: invalid input cannot pollute the local MVP store.

### Task 6 - Add Temporary Store Isolation Workflow Tests

- Subtask 6.1: create two temporary stores in one test or targeted workflow.
- Subtask 6.2: import data into one store only.
- Subtask 6.3: assert version and curriculum listing in the second store remains
  empty.
- Subtask 6.4: export to a nested temporary output path and assert parent
  directories are created when this behavior is not already sufficiently covered.

Expected output: workflow coverage proves stores and generated outputs remain local
and isolated.

### Task 7 - Avoid Duplicate Or Brittle Test Coverage

- Subtask 7.1: keep existing focused unit tests for CLI, storage, versioning,
  editing, LaTeX, and PDF behavior.
- Subtask 7.2: keep new issue `#68` tests focused on cross-component workflow.
- Subtask 7.3: avoid real PDF compiler or viewer requirements in automated tests.
- Subtask 7.4: if an issue `#68` test exposes a real bug, fix the smallest
  blocking bug and add the narrowest regression assertion needed.

Expected output: stable workflow coverage without duplicating every lower-level
test case.

### Task 8 - Write Application MVP User Guide

- Subtask 8.1: create a user-facing guide such as
  `docs/development/application_mvp_workflow.md`.
- Subtask 8.2: document setup expectations and the installed `open-cvn` command.
- Subtask 8.3: document local store initialization and the SQLite file role.
- Subtask 8.4: document importing valid Open CVN JSON and assigning the master
  curriculum.
- Subtask 8.5: document derived-version creation and section or entry selection.
- Subtask 8.6: document Open CVN JSON export for master and derived versions.
- Subtask 8.7: document LaTeX export for master and derived versions.
- Subtask 8.8: document optional PDF generation, compiler requirements, and
  missing-compiler behavior.
- Subtask 8.9: document MVP limits: no GUI, no field-level editing, trace-only XML
  semantic mapping limits, optional PDF preview, local single-user storage, and no
  LLM reconstruction until issue `#69`.

Expected output: evaluator-ready guide for running the local CV management MVP.

### Task 9 - Link Application Documentation

- Subtask 9.1: link the new MVP guide from `PROJECT_GUIDE.md` if the human-facing
  document map changes.
- Subtask 9.2: link the new MVP guide from `docs/context/project_context_index.md`.
- Subtask 9.3: link the new MVP guide from `AGENTS.md` if the operational document
  map changes.
- Subtask 9.4: link the new MVP guide from existing LaTeX or PDF workflow docs
  when it helps users find the full application workflow.

Expected output: new user guide is discoverable from repository entry points.

### Task 10 - Update Issue And Epic Records

- Subtask 10.1: update this issue document with implementation notes, tests added,
  verification results, deviations, and status.
- Subtask 10.2: update issue `#60` to record that issues `#61` through `#68` close
  the local application MVP delivery path.
- Subtask 10.3: keep issue `#69` recorded as post-MVP exploratory work.
- Subtask 10.4: update issue documents `#61` through `#67` only if cross-links or
  issue `#68` closure notes are needed.

Expected output: roadmap issue history accurately records MVP closure.

### Task 11 - Update Persistent Project Context

- Subtask 11.1: update `docs/context/current_status.md` with issue `#68` outcome,
  test results, and next planned work.
- Subtask 11.2: update `docs/roadmap/cvn_generation_roadmap.md` so issue `#68` is
  marked complete and issue `#69` remains the next post-MVP item.
- Subtask 11.3: update `docs/pipeline/known_limitations.md` only if issue `#68`
  uncovers a new durable limitation.
- Subtask 11.4: update `PROJECT_GUIDE.md` when the new application guide changes
  human-facing orientation or document maps.
- Subtask 11.5: update `AGENTS.md` only when operational maps or rules change.

Expected output: future sessions can resume from the documented issue `#68` state.

### Task 12 - Run Targeted Verification

- Subtask 12.1: run the new MVP workflow tests, for example
  `uv run pytest -n auto tests/test_open_cvn_app_mvp_workflow.py -v`.
- Subtask 12.2: run application regression tests covering CLI, storage, versioning,
  editing, LaTeX, and PDF behavior.
- Subtask 12.3: record exact commands and pass/fail results in this issue document.
- Subtask 12.4: document any skipped verification with cause and follow-up.

Expected output: targeted issue `#68` coverage passes.

### Task 13 - Run Full Repository Verification

- Subtask 13.1: run `uv run pytest -n auto tests`.
- Subtask 13.2: record the exact result in this issue document and
  `docs/context/current_status.md`.
- Subtask 13.3: if full verification cannot complete, record the command, failure
  point, cause, and planned follow-up.

Expected output: complete repository test suite passes or has a documented blocker.

### Task 14 - Run Console Script Smoke Workflow

- Subtask 14.1: initialize a smoke store under `/tmp/opencode/`.
- Subtask 14.2: import `examples/open_cvn/research_entry.json` as master.
- Subtask 14.3: create a derived version named `public`.
- Subtask 14.4: exclude `/curriculum/research/0` from the derived version.
- Subtask 14.5: export the derived version as Open CVN JSON.
- Subtask 14.6: export the derived version as LaTeX.
- Subtask 14.7: run PDF generation for the derived version and record either real
  PDF output or expected missing-compiler behavior.

Expected output: installed `open-cvn` command proves the documented MVP workflow
outside direct unit tests.

### Task 15 - Final Documentation Closure

- Subtask 15.1: finalize this issue document with status `completed` after tests
  and documentation updates are complete.
- Subtask 15.2: ensure all new or changed documentation records exact verification
  commands and results.
- Subtask 15.3: ensure no stale references still describe issue `#68` as planned
  once implementation is complete.

Expected output: issue `#68` closes with tests, documentation, verification, and
project context aligned.

## Expected Output

- application MVP test suite
- user guide for local CV management prototype
- verification record for epic `#60`
- documented limitations and follow-up work

## Implementation Notes

- The issue `#68` workflow test suite was added at:
  - `tests/test_open_cvn_app_mvp_workflow.py`
- The new tests cover:
  - full CLI workflow from store initialization to JSON, LaTeX, and optional PDF
    output
  - invalid Open CVN JSON import without polluting local storage
  - isolation between temporary SQLite stores
  - nested export path creation in the MVP workflow
  - missing TeX compiler behavior during PDF generation
- The user-facing application guide was added at:
  - `docs/development/application_mvp_workflow.md`
- The guide documents:
  - setup and CLI discovery
  - local SQLite store initialization
  - Open CVN JSON import as master
  - derived version creation
  - section and entry discovery
  - include/exclude selection
  - Open CVN JSON export
  - LaTeX export
  - optional PDF generation and missing-compiler behavior
  - MVP limitations and issue `#69` LLM deferral
- Documentation entry points were updated to link the new application guide:
  - `PROJECT_GUIDE.md`
  - `AGENTS.md`
  - `docs/context/project_context_index.md`
  - `docs/development/latex_export_workflow.md`
  - `docs/development/pdf_generation_workflow.md`
- `src/generated/` was not modified.

## Tests Added Or Updated

- Added `tests/test_open_cvn_app_mvp_workflow.py`.

The MVP workflow tests cover:

- `store init` over a temporary SQLite path
- valid Open CVN JSON import with `--as-master`
- derived version creation
- section and entry listing
- entry exclusion from a derived version
- derived Open CVN JSON export and revalidation
- derived LaTeX export
- structured missing-compiler PDF behavior
- invalid JSON import leaving curricula and versions empty
- isolation between independent temporary stores

## Verification Performed

- `uv run pytest -n auto tests/test_open_cvn_app_mvp_workflow.py -v`
  - result: `3 passed in 27.66s`
- `uv run pytest -n auto tests/test_open_cvn_app_mvp_workflow.py tests/test_open_cvn_app_cli_unit.py tests/test_open_cvn_app_storage_unit.py tests/test_open_cvn_app_versioning_unit.py tests/test_open_cvn_app_editing_unit.py tests/test_open_cvn_app_latex_unit.py tests/test_open_cvn_app_pdf_unit.py -v`
  - result: `72 passed in 90.20s (0:01:30)`
- Console-script smoke workflow:
  - `uv run open-cvn store init --path /tmp/opencode/open-cvn-issue-68-smoke.sqlite`
  - `uv run open-cvn json import examples/open_cvn/research_entry.json --store /tmp/opencode/open-cvn-issue-68-smoke.sqlite --as-master`
  - `uv run open-cvn versions derive public --store /tmp/opencode/open-cvn-issue-68-smoke.sqlite`
  - `uv run open-cvn versions exclude public /curriculum/research/0 --store /tmp/opencode/open-cvn-issue-68-smoke.sqlite`
  - `uv run open-cvn json export /tmp/opencode/open-cvn-issue-68-public.json --store /tmp/opencode/open-cvn-issue-68-smoke.sqlite --version public`
  - `uv run open-cvn latex export /tmp/opencode/open-cvn-issue-68-public.tex --store /tmp/opencode/open-cvn-issue-68-smoke.sqlite --version public`
  - `uv run open-cvn pdf generate /tmp/opencode/open-cvn-issue-68-public.pdf --store /tmp/opencode/open-cvn-issue-68-smoke.sqlite --version public`
  - result: workflow initialized schema version `2`, imported a master document,
    created a derived version, excluded one research entry, exported valid derived
    JSON, exported valid derived LaTeX, and reported expected missing-compiler PDF
    behavior because no `latexmk` or `pdflatex` executable is installed locally
- `uv run pytest -n auto tests`
  - result: `442 passed in 359.41s (0:05:59)`

## Deviations From Planned Scope

- No functional deviations.
- PDF generation remains optional. The issue `#68` smoke workflow records the
  expected missing-compiler behavior instead of requiring a local TeX installation.

## New Limitations Found

- No new durable limitations were found.

## Verification

- targeted application MVP tests pass
- full repository verification passes with `uv run pytest -n auto tests`
- documentation records exact commands and results

## Impact On Later Issues

- later UI, richer XML mapping, template design, and LLM work can build on a
  documented local application foundation

## Status

- Status: completed
