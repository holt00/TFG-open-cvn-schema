# PDF Generation Workflow

## Purpose

This document describes the issue `#67` MVP workflow for compiling stored Open CVN
curriculum versions from LaTeX into PDF.

PDF generation is optional. The application can still import, store, edit, export
JSON, and render LaTeX when no local TeX distribution is installed.

## Command

For the complete local application workflow from import to export, see:

```text
docs/development/application_mvp_workflow.md
```

Generate a PDF for the master version:

```bash
uv run open-cvn pdf generate cv.pdf --store open-cvn.sqlite --version master
```

Generate a PDF for a derived version:

```bash
uv run open-cvn pdf generate public-cv.pdf --store open-cvn.sqlite --version public
```

Open the generated PDF with the platform default viewer after compilation:

```bash
uv run open-cvn pdf generate public-cv.pdf --store open-cvn.sqlite --version public --open
```

The `--open` handoff is explicit. Without it, the command reports the generated
PDF path and does not launch a viewer.

## Input Source

PDF generation reads stored curriculum versions through
`CurriculumRepository.materialize_version(...)`.

This means:

- master PDF generation renders the stored master curriculum
- derived PDF generation renders the materialized selection state
- include/exclude edits made through `open-cvn versions include` and
  `open-cvn versions exclude` affect the PDF
- Open CVN validation still runs during version materialization

## Compilation Pipeline

The PDF command reuses the issue `#66` LaTeX renderer. It writes a temporary
`.tex` file in an isolated build directory, runs the selected TeX compiler, and
copies the resulting PDF to the requested output path.

Only the final PDF is intended to remain as a durable artifact. Auxiliary files
such as `.aux`, `.log`, `.fls`, and `.fdb_latexmk` stay in the temporary build
directory.

## Compiler Discovery

The discovery order is:

1. managed `tectonic` cached by Open CVN
2. system `tectonic`
3. `latexmk`
4. `pdflatex`

`tectonic` is preferred because it is distributed as a single executable and can
be cached by the Python application. When no cached managed executable is
available, `open-cvn pdf generate` may download the pinned Tectonic release for
the current platform and store it under:

```text
~/.cache/open-cvn/tectonic/<version>/
```

Set `OPEN_CVN_TECTONIC_CACHE` to override the managed cache directory.

If managed Tectonic is unavailable, the application falls back to system
executables. `latexmk` automates multi-pass LaTeX compilation. `pdflatex` is used
as a final fallback and runs two passes for basic references.

The project does not install TeX as a Python dependency. Install a TeX
distribution separately, for example TeX Live, MiKTeX, or MacTeX, only if the
managed or system `tectonic` route is not suitable for your environment.

## PDF Doctor

Check local PDF generation readiness without compiling a document:

```bash
uv run open-cvn pdf doctor
```

The command reports:

- managed Tectonic cache path
- cached managed Tectonic executable, if present
- system `tectonic`, `latexmk`, and `pdflatex` discovery
- selected engine
- whether managed Tectonic download is supported on the current platform
- next recommended action

`pdf doctor` does not download Tectonic by itself. `pdf generate` performs the
managed download when it needs a managed engine and no cached executable exists.

## Missing Compiler Behavior

When no supported engine is available and managed Tectonic cannot be downloaded or
is not supported for the platform, the command fails with structured output
similar to:

```text
PDF generation unavailable.
No supported TeX compiler found. Install one of: tectonic, latexmk, pdflatex.
```

This is expected behavior for offline or unsupported environments without a
cached managed engine or local TeX executable. It should not break the rest of
the application workflow or automated tests.

## Compiler Failure Diagnostics

Compilation failures report:

- command
- return code
- timeout status
- captured stdout
- captured stderr

The CLI keeps these diagnostics user-readable while tests assert the structured
diagnostic behavior.

## Preview Handoff

Preview handoff uses the platform default viewer through Python's `webbrowser`
module and a local file URI.

Limitations:

- preview is best-effort and platform-dependent
- automated tests mock preview behavior instead of opening real viewers
- `--open` should not be used in unattended CI workflows

## Verification

Issue `#67` tests mock compiler discovery, compiler success, compiler failure,
timeouts, missing compiler behavior, and preview handoff. Issue `#71` adds mocked
coverage for managed Tectonic cache/download behavior and `pdf doctor`. A local
TeX installation and real network access are not required for automated
verification.
