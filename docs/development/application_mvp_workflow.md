# Application MVP Workflow

## Purpose

This guide describes the issue `#68` end-to-end workflow for the local Open CVN
management MVP.

The MVP proves this path:

```text
Open CVN JSON input
-> validated local SQLite storage
-> master curriculum
-> derived curriculum version
-> section or entry selection
-> Open CVN JSON export
-> LaTeX export
-> optional PDF generation
```

## Setup

Synchronize the environment and install the project in editable mode:

```bash
uv sync --group codegen --group testing
uv pip install -e .
```

Check that the CLI is available:

```bash
uv run open-cvn --help
```

## Initialize A Local Store

Create a local SQLite store:

```bash
uv run open-cvn store init --path /tmp/open-cvn-demo.sqlite
```

The store is a single-user local SQLite file. Back it up like any other local data
file if it contains useful curriculum data.

## Import Open CVN JSON As Master

Import a valid Open CVN JSON document and assign it as the master curriculum:

```bash
uv run open-cvn json import examples/open_cvn/research_entry.json \
  --store /tmp/open-cvn-demo.sqlite \
  --as-master
```

The import path uses the public Open CVN parser and validator. Invalid JSON is
rejected before storage.

## Create A Derived Version

Create a derived version named `public` from the master curriculum:

```bash
uv run open-cvn versions derive public --store /tmp/open-cvn-demo.sqlite
```

List available versions:

```bash
uv run open-cvn versions list --store /tmp/open-cvn-demo.sqlite
```

## Discover Sections And Entries

List curriculum sections in the derived version:

```bash
uv run open-cvn versions sections public --store /tmp/open-cvn-demo.sqlite
```

List entries in a repeated section:

```bash
uv run open-cvn versions entries public research --store /tmp/open-cvn-demo.sqlite
```

Selectors use JSON Pointer-style paths under `/curriculum`, for example:

```text
/curriculum/research
/curriculum/research/0
```

## Customize Derived Content

Exclude one entry from the derived version:

```bash
uv run open-cvn versions exclude public /curriculum/research/0 \
  --store /tmp/open-cvn-demo.sqlite
```

Include it again if needed:

```bash
uv run open-cvn versions include public /curriculum/research/0 \
  --store /tmp/open-cvn-demo.sqlite
```

Set optional derived-version metadata:

```bash
uv run open-cvn versions metadata public \
  --store /tmp/open-cvn-demo.sqlite \
  --display-name "Public CV" \
  --purpose "grant application"
```

Field-level edits are intentionally unsupported in the MVP. Use section or entry
include/exclude selection instead.

## Export Open CVN JSON

Export the master version:

```bash
uv run open-cvn json export /tmp/master.json \
  --store /tmp/open-cvn-demo.sqlite \
  --version master
```

Export the derived version:

```bash
uv run open-cvn json export /tmp/public.json \
  --store /tmp/open-cvn-demo.sqlite \
  --version public
```

Exported JSON is deterministic, revalidable Open CVN JSON.

## Export LaTeX

Export the derived version to LaTeX:

```bash
uv run open-cvn latex export /tmp/public.tex \
  --store /tmp/open-cvn-demo.sqlite \
  --version public
```

The template is an MVP technical proof. It is deterministic and escapes common
LaTeX-sensitive text, but it is not a final CV design.

More details:

- `docs/development/latex_export_workflow.md`

## Generate PDF Optionally

Generate a PDF from the derived version when a supported TeX compiler is installed:

```bash
uv run open-cvn pdf generate /tmp/public.pdf \
  --store /tmp/open-cvn-demo.sqlite \
  --version public
```

Open the generated PDF with the platform default viewer:

```bash
uv run open-cvn pdf generate /tmp/public.pdf \
  --store /tmp/open-cvn-demo.sqlite \
  --version public \
  --open
```

PDF generation looks for `latexmk` first and `pdflatex` second. If neither exists,
the command reports structured unavailable behavior similar to:

```text
PDF generation unavailable.
No supported TeX compiler found. Install one of: latexmk, pdflatex.
```

This is expected on machines without a TeX distribution. JSON and LaTeX workflows
still work.

More details:

- `docs/development/pdf_generation_workflow.md`

## Verification Commands

Run the MVP workflow tests:

```bash
uv run pytest -n auto tests/test_open_cvn_app_mvp_workflow.py -v
```

Run all application MVP tests:

```bash
uv run pytest -n auto \
  tests/test_open_cvn_app_mvp_workflow.py \
  tests/test_open_cvn_app_cli_unit.py \
  tests/test_open_cvn_app_storage_unit.py \
  tests/test_open_cvn_app_versioning_unit.py \
  tests/test_open_cvn_app_editing_unit.py \
  tests/test_open_cvn_app_latex_unit.py \
  tests/test_open_cvn_app_pdf_unit.py \
  -v
```

Run the full repository test suite:

```bash
uv run pytest -n auto tests
```

## MVP Limits

- The application is CLI-first and has no GUI.
- The store is local, single-user SQLite storage.
- Field-level edits are not supported; derived versions use section or entry
  include/exclude selection.
- CVN XML import remains trace-only for plausible XML and does not perform full
  semantic XML-to-domain mapping.
- PDF generation requires an external TeX distribution and is optional.
- PDF preview is best-effort and only runs when `--open` is explicitly passed.
- LLM-assisted reconstruction from arbitrary PDFs is deferred to issue `#69`.
