# Issue 61 - Define Application MVP Scope And CLI Shell

## Summary

Issue `#61` starts epic `#60` by defining the minimal application architecture and
creating a CLI-first shell for the local CV management prototype.

This issue is part of epic `#60`.

## Goal

- define the MVP boundaries for the application layer
- choose a CLI-first local prototype instead of a heavy GUI for the first version
- create the public application package and command entry point
- provide placeholders for later storage, import/export, versioning, LaTeX, and PDF
  commands

## MVP Rationale

The TFG objective requires a tool that proves automated management of academic CV
data. A CLI-first MVP is enough to prove the core workflow while avoiding the cost
of a full interactive UI before storage, versioning, and export behavior are
stable.

## Dependency On Epic `#41`

The CLI must use the public parser/validator package from `src/open_cvn/` for
input validation. It must not parse CVN XML, PDF, or Open CVN JSON through new
parallel code.

## Planned Scope

- create an application package under `src/open_cvn_app/`
- expose a console command such as `open-cvn`
- implement command groups or subcommands for:
  - store initialization
  - JSON import
  - JSON export
  - version listing
  - derived version creation
  - LaTeX export
  - PDF generation or report unsupported behavior
- define a configuration object for local paths and default store location
- keep command behavior deterministic and testable

## Planned Steps

1. review epic `#60`, parser workflow docs, and Open CVN JSON format docs
2. decide CLI framework or standard-library `argparse` usage
3. create `src/open_cvn_app/` with a minimal package structure
4. add CLI command entry point to `pyproject.toml`
5. implement `--help`, `version`, and placeholder command routing
6. define app-level result and error handling conventions
7. add smoke tests for command discovery and help output
8. document the MVP command surface

## Detailed Execution Plan

This plan is the accepted execution plan for implementing issue `#61`.
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

- Subtask 1.1: confirm issue `#61` is limited to the CLI application shell and
  does not implement storage, import/export behavior, versioning, LaTeX rendering,
  or PDF generation.
- Subtask 1.2: confirm epic `#60` dependencies on epic `#41`, including use of
  `parse_open_cvn_json(...)`, `validate_open_cvn_json(...)`, `parse_cvn_xml(...)`,
  and `parse_cvn_pdf(...)` in later issues instead of parallel parser code.
- Subtask 1.3: confirm canonical Open CVN JSON root fields remain
  `schema_version`, `metadata`, `curriculum`, and `extensions`.
- Subtask 1.4: confirm `src/generated/` remains untouched.

Expected output: final implementation boundary for issue `#61` before code work.

### Task 2 - Choose CLI Approach

- Subtask 2.1: use standard-library `argparse` for the MVP CLI shell.
- Subtask 2.2: avoid adding `click`, `typer`, or another CLI dependency because
  issue `#61` only needs deterministic help, subcommands, and smoke-testable
  routing.
- Subtask 2.3: use `[project.scripts]` in `pyproject.toml` for the installed
  `open-cvn` command.

Expected output: recorded CLI framework decision with no new runtime dependency.

### Task 3 - Create Application Package Scaffold

- Subtask 3.1: create `src/open_cvn_app/`.
- Subtask 3.2: create `src/open_cvn_app/__init__.py` with minimal public package
  metadata.
- Subtask 3.3: create `src/open_cvn_app/config.py` for application-level local
  path configuration.
- Subtask 3.4: create `src/open_cvn_app/results.py` for command result and error
  conventions.
- Subtask 3.5: create `src/open_cvn_app/cli.py` for parser construction, command
  routing, and the console-script entry point.

Expected output: importable application package without concrete persistence or
business logic.

### Task 4 - Define Local Configuration Object

- Subtask 4.1: define an app configuration object such as `OpenCvnAppConfig`.
- Subtask 4.2: include `store_path` as the main configurable local path.
- Subtask 4.3: provide a deterministic default store path suitable for local CLI
  usage.
- Subtask 4.4: expand `~` and normalize path values without creating the store.

Expected output: deterministic config object ready for issue `#62` storage work.

### Task 5 - Define Result And Error Conventions

- Subtask 5.1: define a small command result object such as `AppResult`.
- Subtask 5.2: include `exit_code`, `message`, and optional `error` fields.
- Subtask 5.3: keep placeholder commands successful when routing works.
- Subtask 5.4: leave invalid argument handling to `argparse` with exit code `2`.

Expected output: consistent CLI result behavior before real command
implementations exist.

### Task 6 - Implement CLI Entry Point

- Subtask 6.1: implement `build_parser()`.
- Subtask 6.2: implement `run(argv)` for testable command execution.
- Subtask 6.3: implement `main()` for the installed console script.
- Subtask 6.4: ensure `open-cvn --help` works.
- Subtask 6.5: ensure `open-cvn --version` works.
- Subtask 6.6: ensure `open-cvn version` works.

Expected output: executable CLI shell with deterministic help and version output.

### Task 7 - Add Placeholder Command Groups

- Subtask 7.1: add `store init [--path PATH]`, marked as planned for issue `#62`.
- Subtask 7.2: add `json import INPUT [--store PATH]`, marked as planned for
  issue `#64`.
- Subtask 7.3: add `json export OUTPUT [--store PATH] [--version NAME]`, marked
  as planned for issue `#64`.
- Subtask 7.4: add `versions list [--store PATH]`, marked as planned for issue
  `#63`.
- Subtask 7.5: add `versions derive NAME [--from SOURCE] [--store PATH]`, marked
  as planned for issue `#63`.
- Subtask 7.6: add `latex export OUTPUT [--store PATH] [--version NAME]`, marked
  as planned for issue `#66`.
- Subtask 7.7: add `pdf generate OUTPUT [--store PATH] [--version NAME]`, marked
  as planned for issue `#67` and optional PDF support.

Expected output: complete MVP command surface for later issues without real
storage, import/export, rendering, or PDF behavior.

### Task 8 - Register Console Script

- Subtask 8.1: add `[project.scripts]` to `pyproject.toml` if absent.
- Subtask 8.2: register `open-cvn = "open_cvn_app.cli:main"`.
- Subtask 8.3: verify editable install exposes the `open-cvn` command.

Expected output: `uv run open-cvn --help` works after installation.

### Task 9 - Add CLI Smoke Tests

- Subtask 9.1: create `tests/test_open_cvn_app_cli_unit.py`.
- Subtask 9.2: test parser help contains `open-cvn` and the planned command
  groups.
- Subtask 9.3: test `version` command returns the project version.
- Subtask 9.4: test `store init` routes to issue `#62` placeholder behavior.
- Subtask 9.5: test `json import` routes to issue `#64` placeholder behavior.
- Subtask 9.6: test `versions list` routes to issue `#63` placeholder behavior.
- Subtask 9.7: test `latex export` routes to issue `#66` placeholder behavior.
- Subtask 9.8: test `pdf generate` routes to issue `#67` placeholder behavior.
- Subtask 9.9: test installed command discovery when practical through
  `uv run open-cvn --help`.

Expected output: smoke coverage proving command discovery, help output, and
placeholder routing.

### Task 10 - Verify Parser Contract Remains Stable

- Subtask 10.1: run parser contract tests:
  `uv run pytest -n auto tests/test_parser_validator_contract_unit.py`.
- Subtask 10.2: confirm issue `#61` does not introduce parallel parser behavior.
- Subtask 10.3: document any parser-related regression if found.

Expected output: existing epic `#41` public parser contract remains intact.

### Task 11 - Run Issue Verification

- Subtask 11.1: run targeted CLI tests:
  `uv run pytest -n auto tests/test_open_cvn_app_cli_unit.py -v`.
- Subtask 11.2: run console-script smoke check:
  `uv run open-cvn --help`.
- Subtask 11.3: run full repository verification:
  `uv run pytest -n auto tests`.
- Subtask 11.4: record any skipped or failed verification with reason.

Expected output: issue `#61` verification evidence.

### Task 12 - Update Persistent Documentation

- Subtask 12.1: update this issue document with actual implementation artifacts,
  deviations, verification, and status.
- Subtask 12.2: update `docs/context/current_status.md` so issue `#61` is recorded
  as complete and issue `#62` becomes the next implementation issue.
- Subtask 12.3: update `docs/roadmap/cvn_generation_roadmap.md` if it tracks issue
  `#61` status.
- Subtask 12.4: update `docs/pipeline/known_limitations.md` only if a new durable
  limitation is found.
- Subtask 12.5: update `PROJECT_GUIDE.md` only if repository orientation,
  contributor reading order, or the documentation map changes.

Expected output: repository context remains resumable after issue completion.

## Planned MVP Command Surface

```text
open-cvn --help
open-cvn --version
open-cvn version
open-cvn store init [--path PATH]
open-cvn json import INPUT [--store PATH]
open-cvn json export OUTPUT [--store PATH] [--version NAME]
open-cvn versions list [--store PATH]
open-cvn versions derive NAME [--from SOURCE] [--store PATH]
open-cvn latex export OUTPUT [--store PATH] [--version NAME]
open-cvn pdf generate OUTPUT [--store PATH] [--version NAME]
```

## Definition Of Done

- `src/open_cvn_app/` exists as the application package shell.
- `open-cvn` console script is registered in `pyproject.toml`.
- `open-cvn --help` works.
- `open-cvn --version` and `open-cvn version` work.
- Placeholder command groups route deterministically.
- CLI smoke tests pass.
- Existing parser contract tests pass.
- Full repository verification passes or documented reason is recorded.
- Persistent documentation is updated in the same session as the implementation.

## Expected Output

- application package scaffold
- CLI entry point
- command routing placeholders
- smoke tests for CLI startup
- documentation of MVP scope and command shape

## Verification

- `uv run open-cvn --help` works after installation
- CLI smoke tests pass
- existing parser tests still pass
- full repository verification passes or a reason is documented

## Implementation Notes

- The application package scaffold was created under `src/open_cvn_app/`.
- The CLI uses standard-library `argparse`; no new CLI dependency was added.
- The console command is registered through `[project.scripts]` as
  `open-cvn = "open_cvn_app.cli:main"`.
- Application-level configuration is represented by `OpenCvnAppConfig` in
  `src/open_cvn_app/config.py`.
- Command result conventions are represented by `AppResult` in
  `src/open_cvn_app/results.py`.
- `src/open_cvn_app/cli.py` implements `build_parser()`, `run(argv)`, and
  `main()`.
- Placeholder commands route deterministically to later issue messages without
  creating storage, importing JSON, exporting JSON, creating versions, rendering
  LaTeX, or generating PDFs.
- `src/generated/` was not modified.

## Implemented Command Surface

```text
open-cvn --help
open-cvn --version
open-cvn version
open-cvn store init [--path PATH]
open-cvn json import INPUT [--store PATH]
open-cvn json export OUTPUT [--store PATH] [--version NAME]
open-cvn versions list [--store PATH]
open-cvn versions derive NAME [--from SOURCE] [--store PATH]
open-cvn latex export OUTPUT [--store PATH] [--version NAME]
open-cvn pdf generate OUTPUT [--store PATH] [--version NAME]
```

## Tests Added

- `tests/test_open_cvn_app_cli_unit.py`

The tests cover:

- help output and command group discovery
- `version` command output
- placeholder routing for store, JSON import/export, versions, LaTeX, and PDF
  commands

## Verification Performed

- `uv run pytest -n auto tests/test_parser_validator_contract_unit.py`
  - result: `13 passed in 19.62s`
- `uv run pytest -n auto tests/test_open_cvn_app_cli_unit.py -v`
  - result: `9 passed in 15.76s`
- `uv run open-cvn --help`
  - result: command displayed CLI help successfully
- `uv run pytest -n auto tests`
  - result: `379 passed in 334.53s (0:05:34)`

## Deviations From Planned Scope

- No functional deviations.
- The implementation intentionally keeps all operational command behavior as
  placeholders for issues `#62`, `#63`, `#64`, `#66`, and `#67`.

## New Limitations Found

- No new durable limitations were found.

## Impact On Later Issues

- issue `#62` adds local storage behind the CLI
- issue `#64` adds concrete import/export commands
- issue `#66` and issue `#67` add export commands

## Status

- Status: completed
