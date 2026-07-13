# Issue 67 - Implement PDF Generation And Preview Handoff

## Summary

Issue `#67` adds optional PDF generation from LaTeX output and a minimal preview
handoff for the MVP application.

This issue is part of epic `#60`.

## Goal

- compile generated LaTeX into PDF when a TeX engine is available
- report structured unsupported behavior when no compiler is installed
- avoid making PDF generation a hard dependency for all tests and environments
- provide a local path or OS handoff for previewing generated PDFs

## MVP Direction

PDF generation should be optional. The core MVP must still work when LaTeX can be
rendered but no local TeX distribution is installed.

## Planned Scope

- detect a supported command such as `latexmk` or `pdflatex`
- compile a generated `.tex` file into a PDF in an output directory
- capture compiler stdout/stderr into diagnostics when compilation fails
- provide a command that reports the generated PDF path
- optionally open the PDF with the platform default viewer when explicitly
  requested
- keep preview handoff out of automated tests unless it can be safely mocked

## Planned Steps

1. define supported TeX compiler discovery order
2. implement compiler availability check
3. implement PDF compilation wrapper
4. implement structured failure for missing compiler
5. implement CLI command for PDF generation
6. optionally implement `--open` preview handoff
7. add tests with mocked compiler behavior
8. document installation requirements and fallback behavior

## Detailed Execution Plan

This plan is the accepted execution plan for implementing issue `#67`.
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

- Subtask 1.1: confirm the CLI shape remains
  `open-cvn pdf generate OUTPUT [--store PATH] [--version NAME] [--open]`.
- Subtask 1.2: confirm PDF generation reads stored curriculum versions through
  `CurriculumRepository.materialize_version(...)`.
- Subtask 1.3: confirm the intermediate LaTeX source is rendered through the
  existing issue `#66` LaTeX rendering path, not a separate template pipeline.
- Subtask 1.4: confirm local TeX tooling remains optional and is not added as a
  Python dependency.
- Subtask 1.5: confirm a missing compiler returns a structured user-facing
  failure rather than breaking unrelated workflows or tests.
- Subtask 1.6: confirm preview handoff is disabled by default and only attempted
  when `--open` is explicitly provided.
- Subtask 1.7: confirm `src/generated/` remains untouched.

Expected output: final implementation boundary for issue `#67` before code work.

### Task 2 - Define PDF Generation Module Contract

- Subtask 2.1: create `src/open_cvn_app/pdf.py` for hand-maintained PDF
  generation logic.
- Subtask 2.2: define small dataclasses for compiler discovery, compiler
  diagnostics, compilation result, and PDF generation result when they keep CLI
  handling clear.
- Subtask 2.3: define focused exceptions such as `PdfGenerationUnavailable`,
  `PdfCompilationError`, and `PdfPreviewError`.
- Subtask 2.4: expose a compact public helper such as
  `generate_pdf_document(repository, version, output_path, open_pdf=False)`.
- Subtask 2.5: avoid creating a broad export framework until multiple PDF
  backends or preview strategies require it.

Expected output: focused module boundary for optional PDF generation without
duplicating storage or LaTeX rendering behavior.

### Task 3 - Implement TeX Compiler Discovery

- Subtask 3.1: use `shutil.which("latexmk")` to detect `latexmk` first.
- Subtask 3.2: use `shutil.which("pdflatex")` as the fallback compiler.
- Subtask 3.3: return compiler name, executable path, and strategy information.
- Subtask 3.4: keep discovery testable by allowing internal injection or
  monkeypatching of the lookup function.
- Subtask 3.5: return structured unavailable behavior when neither compiler is
  found.

Expected output: deterministic compiler selection that prefers `latexmk` and
falls back to `pdflatex` without requiring either in test environments.

### Task 4 - Implement Safe Compiler Invocation

- Subtask 4.1: invoke external compilers with `subprocess.run(...)` and
  `shell=False`.
- Subtask 4.2: pass command arguments as a sequence, not a shell string.
- Subtask 4.3: capture stdout and stderr with text output enabled.
- Subtask 4.4: use a bounded timeout, for example 60 seconds, to avoid hanging
  CLI calls.
- Subtask 4.5: convert timeout failures into structured diagnostics.
- Subtask 4.6: preserve the process environment while setting
  `SOURCE_DATE_EPOCH=0` for more reproducible PDF metadata where supported.

Expected output: compiler execution is safe, testable, bounded, and diagnostic.

### Task 5 - Prepare Temporary Build Directory

- Subtask 5.1: create the parent directory for the requested final PDF path.
- Subtask 5.2: create an isolated temporary build directory for LaTeX source,
  auxiliary files, logs, and compiler output.
- Subtask 5.3: render the materialized curriculum to a `.tex` file inside the
  build directory.
- Subtask 5.4: compile from the build directory so `.aux`, `.log`, `.fls`, and
  `.fdb_latexmk` files do not pollute user output directories.
- Subtask 5.5: copy the generated PDF to the user-requested output path.
- Subtask 5.6: leave only the final PDF as the durable artifact.

Expected output: PDF generation does not leak transient compiler files into the
working tree or requested output directory.

### Task 6 - Implement `latexmk` Strategy

- Subtask 6.1: compile with a command equivalent to
  `latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir BUILD_DIR TEX_FILE`.
- Subtask 6.2: treat a non-zero return code as `PdfCompilationError`.
- Subtask 6.3: include command, return code, stdout, and stderr in diagnostics.
- Subtask 6.4: verify the expected PDF exists after a zero return code.
- Subtask 6.5: report a structured error if the compiler succeeds but the PDF is
  missing.

Expected output: preferred compiler path supports normal multi-pass LaTeX
documents through `latexmk`.

### Task 7 - Implement `pdflatex` Fallback Strategy

- Subtask 7.1: compile with a command equivalent to
  `pdflatex -interaction=nonstopmode -halt-on-error -output-directory BUILD_DIR TEX_FILE`.
- Subtask 7.2: run two passes to support basic references when `latexmk` is not
  available.
- Subtask 7.3: stop immediately when a pass fails.
- Subtask 7.4: include per-pass stdout, stderr, command, and return code in
  diagnostics.
- Subtask 7.5: verify the expected PDF exists after successful passes.

Expected output: common TeX installations without `latexmk` can still produce PDF
artifacts.

### Task 8 - Define Result And Diagnostic Behavior

- Subtask 8.1: successful generation reports output path, version name,
  validation status, and compiler name.
- Subtask 8.2: missing compiler diagnostics name the searched commands:
  `latexmk` and `pdflatex`.
- Subtask 8.3: compiler failures preserve command, return code, stdout, and
  stderr.
- Subtask 8.4: CLI output keeps diagnostics concise enough for users while tests
  can assert the structured data.
- Subtask 8.5: avoid tracebacks for expected missing compiler or failed compiler
  cases.

Expected output: users receive actionable errors and tests can inspect precise
failure causes.

### Task 9 - Implement Preview Handoff

- Subtask 9.1: add `--open` to `open-cvn pdf generate`.
- Subtask 9.2: use a small preview helper around `webbrowser.open(...)` with a
  file URI for the generated PDF.
- Subtask 9.3: do not call preview behavior unless `--open` is explicitly set.
- Subtask 9.4: return structured failure or diagnostic when preview handoff cannot
  launch a viewer.
- Subtask 9.5: mock preview behavior in tests instead of opening real viewers.

Expected output: generated PDFs can be handed off to the platform default viewer
without making preview part of automated test side effects.

### Task 10 - Integrate PDF Command Into CLI

- Subtask 10.1: replace the issue `#67` placeholder in `_handle_pdf_generate(...)`.
- Subtask 10.2: keep existing command shape
  `open-cvn pdf generate OUTPUT [--store PATH] [--version NAME]`.
- Subtask 10.3: add the optional `--open` flag.
- Subtask 10.4: resolve the local store through `OpenCvnAppConfig` and
  `CurriculumRepository` as other app commands do.
- Subtask 10.5: call the PDF generation helper and report successful output path,
  version name, validation status, and compiler.
- Subtask 10.6: catch storage, rendering, filesystem, missing compiler,
  compilation, and preview failures as `AppResult.failed(...)` responses.

Expected output: the existing `pdf generate` command becomes functional while
remaining consistent with earlier CLI groups.

### Task 11 - Add PDF Module Unit Tests

- Subtask 11.1: create `tests/test_open_cvn_app_pdf_unit.py`.
- Subtask 11.2: test compiler discovery prefers `latexmk` over `pdflatex`.
- Subtask 11.3: test compiler discovery uses `pdflatex` when `latexmk` is absent.
- Subtask 11.4: test missing compiler raises or returns structured unavailable
  behavior.
- Subtask 11.5: test mocked successful compilation creates or copies the expected
  PDF output path.
- Subtask 11.6: test compiler failure preserves stdout, stderr, command, and
  return code.
- Subtask 11.7: test timeout handling preserves useful diagnostics.
- Subtask 11.8: test output parent directory creation.
- Subtask 11.9: test `SOURCE_DATE_EPOCH` is included in the compiler environment.
- Subtask 11.10: test preview handoff with a mocked opener.

Expected output: PDF generation logic is covered without requiring a local TeX
installation.

### Task 12 - Add CLI PDF Tests

- Subtask 12.1: replace the existing placeholder PDF CLI test with real behavior.
- Subtask 12.2: test missing compiler CLI behavior with mocked discovery.
- Subtask 12.3: test successful CLI PDF generation with mocked compiler execution.
- Subtask 12.4: test derived-version PDF generation reflects materialized
  selection state.
- Subtask 12.5: test `--open` triggers mocked preview handoff.
- Subtask 12.6: test missing version failure.
- Subtask 12.7: test compiler failure reports useful diagnostics through stderr.
- Subtask 12.8: ensure CLI tests do not depend on `latexmk`, `pdflatex`, or a real
  PDF viewer being installed.

Expected output: CLI coverage proves storage-to-LaTeX-to-PDF orchestration and
optional preview behavior.

### Task 13 - Run Optional Console Smoke Workflow

- Subtask 13.1: initialize a temporary store under `/tmp/opencode/`.
- Subtask 13.2: import an Open CVN JSON example as the master version.
- Subtask 13.3: create a derived version.
- Subtask 13.4: apply at least one include/exclude selection to the derived
  version.
- Subtask 13.5: run `open-cvn pdf generate` for the derived version without
  `--open`.
- Subtask 13.6: verify the generated PDF path exists when a compiler is available.
- Subtask 13.7: if no compiler is available, record the expected missing compiler
  behavior instead of treating it as a repository failure.

Expected output: console-script smoke verifies installed CLI behavior when the
local environment supports it, while preserving optional compiler semantics.

### Task 14 - Update Persistent Documentation

- Subtask 14.1: update this issue document with implementation notes,
  implemented artifacts, verification results, deviations, and final status.
- Subtask 14.2: create or update focused PDF workflow documentation under
  `docs/development/`, such as `docs/development/pdf_generation_workflow.md`.
- Subtask 14.3: document recommended TeX installation path: `latexmk` preferred,
  `pdflatex` fallback, TeX distribution required outside Python dependencies.
- Subtask 14.4: document master and derived PDF generation commands.
- Subtask 14.5: document `--open` preview behavior and its limitations.
- Subtask 14.6: document missing compiler fallback behavior.
- Subtask 14.7: link the PDF workflow from `docs/development/latex_export_workflow.md`.
- Subtask 14.8: update `docs/context/current_status.md` with issue `#67` outcome.
- Subtask 14.9: update `docs/roadmap/cvn_generation_roadmap.md` if issue status
  changes there.
- Subtask 14.10: update `docs/pipeline/known_limitations.md` only if a new durable
  limitation is found.
- Subtask 14.11: update `PROJECT_GUIDE.md` only if the human-facing document map
  changes.

Expected output: repository documentation remains aligned with the implemented
optional PDF generation workflow.

### Task 15 - Verify Test Suite

- Subtask 15.1: run targeted PDF and CLI tests with
  `uv run pytest -n auto tests/test_open_cvn_app_pdf_unit.py tests/test_open_cvn_app_cli_unit.py -v`.
- Subtask 15.2: run application regression tests covering LaTeX, storage,
  versioning, and editing behavior.
- Subtask 15.3: run full repository verification with
  `uv run pytest -n auto tests`.
- Subtask 15.4: document any failure that cannot be fixed in the same session with
  cause, affected command, and follow-up.

Expected output: issue `#67` changes are verified against targeted PDF behavior
and repository regression coverage.

### Acceptance Criteria

- Stored master curriculum version generates a PDF when a supported compiler is
  available.
- Stored derived curriculum version generates a PDF from materialized selection
  state.
- Missing TeX compiler returns structured unsupported behavior and does not break
  unrelated tests or workflows.
- Compiler failures report command, return code, stdout, and stderr.
- Existing CLI command shape remains stable, with `--open` added as an explicit
  optional preview handoff.
- Automated tests cover compiler discovery, missing compiler behavior, mocked
  success, mocked failure, CLI generation, derived-version behavior, and preview
  handoff without requiring a real TeX installation.
- Full repository verification passes or any failure is documented with cause.

## Expected Output

- PDF generation wrapper
- CLI command for PDF generation
- tests for compiler detection and failure handling
- documentation for PDF export and preview limitations

## Verification

- missing compiler does not break full test suite
- mocked compiler success creates expected output path behavior
- compiler failure returns useful diagnostics
- full repository verification passes or a reason is documented

## Impact On Later Issues

- issue `#68` documents end-to-end MVP export workflow
- future UI work can call this wrapper for preview/export actions

## Implementation Notes

- Added optional PDF generation logic in `src/open_cvn_app/pdf.py`.
- Replaced the issue `#67` CLI placeholder with functional
  `open-cvn pdf generate OUTPUT [--store PATH] [--version NAME] [--open]`
  behavior.
- PDF generation reads master or derived curriculum versions through
  `CurriculumRepository.materialize_version(...)`.
- PDF generation reuses the issue `#66` LaTeX renderer instead of adding a second
  template pipeline.
- Compiler discovery prefers `latexmk` and falls back to `pdflatex`.
- `latexmk` uses one delegated multi-pass command; `pdflatex` fallback runs two
  passes.
- Compiler execution uses `subprocess.run(...)` with `shell=False`, captured
  stdout/stderr, bounded timeout, and `SOURCE_DATE_EPOCH=0` in the compiler
  environment.
- Compilation happens in an isolated temporary directory so auxiliary TeX files do
  not remain as durable output artifacts.
- Missing compiler behavior is structured through `PdfGenerationUnavailable`.
- Compiler failures preserve command, return code, timeout status, stdout, and
  stderr through `CompilerRunDiagnostic`.
- The explicit `--open` flag performs best-effort preview handoff through the
  platform default viewer and is mocked in automated tests.

## Implemented Artifacts

- `src/open_cvn_app/pdf.py`
- `src/open_cvn_app/cli.py`
- `tests/test_open_cvn_app_pdf_unit.py`
- `tests/test_open_cvn_app_cli_unit.py`
- `docs/development/pdf_generation_workflow.md`
- `docs/development/latex_export_workflow.md`
- `docs/context/current_status.md`
- `docs/roadmap/cvn_generation_roadmap.md`
- `docs/context/project_context_index.md`
- `PROJECT_GUIDE.md`
- `AGENTS.md`

## Implemented Verification

- Targeted PDF and CLI verification passed with:
  - `uv run pytest -n auto tests/test_open_cvn_app_pdf_unit.py tests/test_open_cvn_app_cli_unit.py -v`
  - result: `40 passed in 52.02s`
- Storage, versioning, editing, and LaTeX regression verification passed with:
  - `uv run pytest -n auto tests/test_open_cvn_app_latex_unit.py tests/test_open_cvn_app_storage_unit.py tests/test_open_cvn_app_versioning_unit.py tests/test_open_cvn_app_editing_unit.py -v`
  - result: `29 passed in 45.92s`
- Console-script smoke verification passed for store initialization, JSON import
  as master, derived creation, derived selection exclusion, and expected
  missing-compiler PDF generation behavior.
- Local environment had neither `latexmk` nor `pdflatex` installed, so real PDF
  compilation smoke was not executed.
- Full-suite verification passed with:
  - `uv run pytest -n auto tests`
  - result: `439 passed in 355.05s (0:05:55)`

## Implementation Deviations

- The accepted plan allowed documenting the local TeX requirement and fallback
  behavior; a focused `docs/development/pdf_generation_workflow.md` document was
  added for that purpose.
- No new durable pipeline limitation was found, so
  `docs/pipeline/known_limitations.md` was not changed.

## Status

- Status: completed
