# PDF Generation Workflow

## Purpose

This document describes the issue `#67` MVP workflow for compiling stored Open CVN
curriculum versions from LaTeX into PDF.

PDF generation is optional. The application can still import, store, edit, export
JSON, and render LaTeX when no local TeX distribution is installed.

## Command

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

1. `latexmk`
2. `pdflatex`

`latexmk` is preferred because it automates multi-pass LaTeX compilation.
`pdflatex` is used as a fallback and runs two passes for basic references.

The project does not install TeX as a Python dependency. Install a TeX
distribution separately, for example TeX Live, MiKTeX, or MacTeX, and ensure
`latexmk` or `pdflatex` is on `PATH`.

## Missing Compiler Behavior

When no supported compiler is installed, the command fails with structured output
similar to:

```text
PDF generation unavailable.
No supported TeX compiler found. Install one of: latexmk, pdflatex.
```

This is expected behavior for environments without TeX. It should not break the
rest of the application workflow or automated tests.

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
timeouts, missing compiler behavior, and preview handoff. A local TeX installation
is not required for automated verification.
