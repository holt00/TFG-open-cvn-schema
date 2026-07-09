# Issue 66 - Implement LaTeX Export From Open CVN

## Summary

Issue `#66` implements the MVP LaTeX export path from stored Open CVN curriculum
versions.

This issue is part of epic `#60`.

## Goal

- generate a structured LaTeX document from Open CVN JSON
- support master and derived curriculum versions
- prove the TFG export workflow without requiring a polished final template
- keep output deterministic for tests

## Template Direction

The MVP should use Jinja templates or a similarly simple rendering approach. The
first template should prioritize correctness and stable output over visual polish.

## Planned Scope

- create a LaTeX template directory
- render basic identity, education, research, professional experience,
  achievements, and other sections when present
- escape LaTeX-sensitive text values
- include trace metadata only when useful or behind an option
- output `.tex` files for master or derived versions
- provide deterministic rendering for tests

## Planned Steps

1. choose template dependency and add it if needed
2. define template file location
3. implement Open CVN-to-template context conversion
4. implement LaTeX escaping helpers
5. implement `.tex` export command
6. add deterministic rendering tests using example Open CVN JSON
7. document template limitations and customization points

## Detailed Execution Plan

This plan is the accepted execution plan for implementing issue `#66`.
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

- Subtask 1.1: confirm issue `#66` only exports LaTeX from stored Open CVN
  curriculum versions.
- Subtask 1.2: confirm the exported source document must come from
  `CurriculumRepository.materialize_version(...)`.
- Subtask 1.3: confirm master and derived versions are both supported through the
  existing `--version` CLI option.
- Subtask 1.4: confirm issue `#66` writes `.tex` only and does not compile PDFs.
- Subtask 1.5: confirm PDF generation and preview behavior remain deferred to
  issue `#67`.
- Subtask 1.6: confirm the MVP template prioritizes correctness, deterministic
  output, and testability over visual polish.
- Subtask 1.7: confirm trace metadata is omitted by default unless a later
  explicit option is added.
- Subtask 1.8: confirm `src/generated/` remains untouched.

Expected output: final implementation boundary for issue `#66` before code work.

### Task 2 - Add Template Dependency

- Subtask 2.1: add `jinja2>=3.1` to runtime project dependencies in
  `pyproject.toml`.
- Subtask 2.2: keep Jinja as a runtime dependency because LaTeX export is a user
  application command, not a test-only or code-generation workflow.
- Subtask 2.3: synchronize the environment with
  `uv sync --group codegen --group testing`.
- Subtask 2.4: verify the dependency can be imported from the project
  environment.

Expected output: Jinja is available to the application CLI and tests.

### Task 3 - Define LaTeX Export Module Contract

- Subtask 3.1: create `src/open_cvn_app/latex.py` for hand-maintained LaTeX export
  logic.
- Subtask 3.2: define a small render API such as
  `render_latex_document(document, version_name: str) -> str`.
- Subtask 3.3: define an export helper such as
  `export_latex_document(repository, version, output_path)` if it keeps CLI code
  simpler.
- Subtask 3.4: define small dataclasses only when they make template context or
  CLI results clearer.
- Subtask 3.5: avoid adding a broad export framework until multiple template
  families or formats require it.

Expected output: focused module boundary for rendering and writing LaTeX without
duplicating storage behavior.

### Task 4 - Implement LaTeX Escaping

- Subtask 4.1: implement `escape_latex(value: object) -> str`.
- Subtask 4.2: convert `None` to an empty string.
- Subtask 4.3: convert scalar non-string values with `str(...)`.
- Subtask 4.4: escape LaTeX-sensitive characters including backslash, braces,
  dollar, ampersand, hash, percent, underscore, tilde, and caret.
- Subtask 4.5: register `escape_latex(...)` as a Jinja filter, for example
  `latex`.
- Subtask 4.6: add direct unit tests for escaping representative special
  characters.

Expected output: template variables can be safely rendered into basic LaTeX text
without obvious syntax breakage from user data.

### Task 5 - Build Deterministic Template Context

- Subtask 5.1: convert the Open CVN JSON root into a stable template context.
- Subtask 5.2: include `schema_version`, document language, `version_name`, and
  version metadata when present.
- Subtask 5.3: convert `curriculum.identity` object values into deterministic
  label/value rows.
- Subtask 5.4: convert repeated curriculum sections into section records with
  section name, display title, and entry rows.
- Subtask 5.5: cover MVP sections `education`, `research`,
  `professional_experience`, `achievements`, and `other`.
- Subtask 5.6: preserve source order from the Open CVN JSON document where
  possible.
- Subtask 5.7: for entry `data`, render simple scalar fields directly and use
  deterministic JSON serialization for nested values.
- Subtask 5.8: avoid heavy semantic relabeling heuristics in this issue.

Expected output: templates receive simple, deterministic structures and do not
need to understand raw Open CVN JSON deeply.

### Task 6 - Add MVP LaTeX Template

- Subtask 6.1: create template directory under
  `src/open_cvn_app/templates/latex/`.
- Subtask 6.2: add `basic_cv.tex.jinja` as the initial package template.
- Subtask 6.3: use common LaTeX packages only, avoiding rare dependencies that
  would complicate issue `#67` PDF compilation.
- Subtask 6.4: render a document title from identity data when available and use a
  deterministic fallback otherwise.
- Subtask 6.5: render version metadata near the top of the document.
- Subtask 6.6: render identity fields when present.
- Subtask 6.7: render non-empty repeated sections with stable headings and entry
  lists.
- Subtask 6.8: decide and test a stable empty-section behavior, either omission or
  a fixed placeholder.

Expected output: a simple `.tex` document template proves the export path without
committing to final visual design.

### Task 7 - Configure Jinja Environment

- Subtask 7.1: load templates with `PackageLoader("open_cvn_app",
  "templates/latex")` or an equivalent package-safe loader.
- Subtask 7.2: set `autoescape=False` because HTML autoescaping is not suitable
  for LaTeX output.
- Subtask 7.3: set `trim_blocks=True`, `lstrip_blocks=True`, and
  `keep_trailing_newline=True` for deterministic whitespace.
- Subtask 7.4: use `StrictUndefined` so missing template fields fail during tests
  instead of silently producing incomplete output.
- Subtask 7.5: register the LaTeX escaping filter before loading templates.

Expected output: rendering environment is deterministic and fails clearly on
template/context mismatches.

### Task 8 - Write Deterministic `.tex` Output

- Subtask 8.1: implement a text writing helper that creates parent directories.
- Subtask 8.2: write UTF-8 output.
- Subtask 8.3: normalize the rendered document to exactly one final newline.
- Subtask 8.4: avoid timestamps, random identifiers, local absolute paths, or
  other nondeterministic data inside rendered LaTeX.
- Subtask 8.5: convert `OSError` failures into user-readable CLI errors.

Expected output: repeated exports from the same stored version produce identical
`.tex` files.

### Task 9 - Implement CLI LaTeX Export Command

- Subtask 9.1: replace the issue `#66` placeholder in `_handle_latex_export(...)`.
- Subtask 9.2: keep existing CLI shape:
  `open-cvn latex export OUTPUT [--store PATH] [--version NAME]`.
- Subtask 9.3: resolve the local store path through `OpenCvnAppConfig`.
- Subtask 9.4: materialize the requested version through
  `CurriculumRepository.materialize_version(...)`.
- Subtask 9.5: render the materialized document through the LaTeX module.
- Subtask 9.6: write the output file with deterministic formatting.
- Subtask 9.7: report successful output path, version name, and validation
  status.
- Subtask 9.8: report storage, render, and write failures as
  `AppResult.failed("LaTeX export failed.", error=str(exc))` or an equally
  specific message.

Expected output: users can export master or derived stored versions to `.tex`
from the existing CLI command group.

### Task 10 - Add LaTeX Rendering Unit Tests

- Subtask 10.1: create `tests/test_open_cvn_app_latex_unit.py`.
- Subtask 10.2: test `escape_latex(...)` with representative LaTeX-sensitive
  characters.
- Subtask 10.3: test rendering of `tests/fixtures/open_cvn/valid_minimal.json`.
- Subtask 10.4: test rendering of at least one richer example under
  `examples/open_cvn/`, such as `research_entry.json`.
- Subtask 10.5: assert deterministic rendering by comparing exact text or stable
  key slices where full snapshots would be too brittle.
- Subtask 10.6: assert rendered text ends with one final newline.

Expected output: rendering behavior is covered independently from CLI and storage
plumbing.

### Task 11 - Add CLI LaTeX Export Tests

- Subtask 11.1: update the previous LaTeX placeholder CLI test so it expects real
  export behavior.
- Subtask 11.2: test exporting the master version from a temporary initialized
  store.
- Subtask 11.3: assert the command exits with code `0`.
- Subtask 11.4: assert the output `.tex` file exists and contains expected stable
  LaTeX markers.
- Subtask 11.5: assert successful CLI output includes version name, output path,
  and validation status.
- Subtask 11.6: test exporting a derived version after a selection change and
  verify the rendered content reflects materialized derived data.
- Subtask 11.7: test missing version failure.
- Subtask 11.8: test nested output parent directory creation.

Expected output: CLI tests prove the full storage-to-materialized-version-to-tex
workflow.

### Task 12 - Run Console Smoke Workflow

- Subtask 12.1: initialize a temporary store under `/tmp/opencode/`.
- Subtask 12.2: import an Open CVN JSON example as the master version.
- Subtask 12.3: create a derived version.
- Subtask 12.4: apply at least one include/exclude selection to the derived
  version.
- Subtask 12.5: export the derived version to `.tex` through the console script.
- Subtask 12.6: inspect command output and generated file existence.

Expected output: console-script smoke proves the installed `open-cvn` entry point
works outside pytest helpers.

### Task 13 - Verify Test Suite

- Subtask 13.1: run targeted LaTeX and CLI tests while developing.
- Subtask 13.2: run storage, versioning, and editing regression tests after CLI
  integration.
- Subtask 13.3: run full repository verification with
  `uv run pytest -n auto tests`.
- Subtask 13.4: document any failure that cannot be fixed in the same session with
  cause, affected command, and follow-up.

Expected output: issue `#66` changes are verified against targeted behavior and
repository regression coverage.

### Task 14 - Update Persistent Documentation

- Subtask 14.1: update this issue document with implementation notes,
  verification results, deviations, and final status.
- Subtask 14.2: update `docs/context/current_status.md` with issue `#66` outcome.
- Subtask 14.3: update user-facing workflow documentation for the LaTeX export
  command, creating a focused document only if no suitable app workflow document
  exists.
- Subtask 14.4: update `docs/pipeline/known_limitations.md` only if LaTeX export
  uncovers a durable limitation.
- Subtask 14.5: update `docs/roadmap/cvn_generation_roadmap.md` if issue status
  changes there.

Expected output: repository documentation remains aligned with the implemented
LaTeX export workflow.

### Acceptance Criteria

- Stored master curriculum version renders to `.tex`.
- Stored derived curriculum version renders materialized selection state to
  `.tex`.
- LaTeX-sensitive text values are escaped.
- Output is deterministic and ends with a final newline.
- Existing CLI command shape remains stable.
- Missing store, missing version, render, and write failures report clear errors.
- Tests cover escaping, rendering, CLI export, and derived-version behavior.
- Full repository verification passes or any failure is documented with cause.

## Expected Output

- LaTeX template file or files
- LaTeX rendering module
- CLI export command
- tests for deterministic `.tex` output
- documentation for LaTeX export

## Verification

- a valid stored curriculum renders to `.tex`
- derived version selection affects rendered output
- LaTeX escaping prevents obvious broken output for special characters
- full repository verification passes or a reason is documented

## Implementation Notes

- Added runtime `jinja2>=3.1` dependency for application LaTeX rendering.
- Added package data configuration so LaTeX templates are included with
  `open_cvn_app`.
- Implemented LaTeX rendering in `src/open_cvn_app/latex.py`.
- Added initial template at
  `src/open_cvn_app/templates/latex/basic_cv.tex.jinja`.
- Replaced the issue `#66` CLI placeholder with functional
  `open-cvn latex export OUTPUT [--store PATH] [--version NAME]` behavior.
- The CLI uses `CurriculumRepository.materialize_version(...)`, so master and
  derived exports share the existing versioning and selection behavior.
- Empty repeated sections are omitted by the MVP template.
- Trace metadata remains omitted by default.
- PDF compilation remains deferred to issue `#67`.

## Implemented Artifacts

- `src/open_cvn_app/latex.py`
- `src/open_cvn_app/templates/latex/basic_cv.tex.jinja`
- `src/open_cvn_app/cli.py`
- `tests/test_open_cvn_app_latex_unit.py`
- `tests/test_open_cvn_app_cli_unit.py`
- `docs/development/latex_export_workflow.md`
- `pyproject.toml`

## Implemented Verification

- Dependency synchronization and targeted LaTeX/CLI verification passed with:
  - `uv sync --group codegen --group testing`
  - `uv run pytest -n auto tests/test_open_cvn_app_latex_unit.py tests/test_open_cvn_app_cli_unit.py -v`
  - result: `29 passed in 40.59s`
- Storage, versioning, and editing regression verification passed with:
  - `uv run pytest -n auto tests/test_open_cvn_app_storage_unit.py tests/test_open_cvn_app_versioning_unit.py tests/test_open_cvn_app_editing_unit.py -v`
  - result: `25 passed in 49.19s`
- Console-script smoke verification passed for store initialization, JSON import
  as master, derived creation, derived selection exclusion, and derived LaTeX
  export.
- Full-suite verification passed with:
  - `uv run pytest -n auto tests`
  - result: `424 passed in 357.81s (0:05:57)`

## Implementation Deviations

- The accepted plan allowed adding a focused workflow document if no suitable app
  workflow document existed; `docs/development/latex_export_workflow.md` was added
  for that purpose.
- No new durable pipeline limitation was found, so
  `docs/pipeline/known_limitations.md` was not changed.

## Impact On Later Issues

- issue `#67` compiles `.tex` output into PDF when a local TeX engine exists

## Status

- Status: completed
