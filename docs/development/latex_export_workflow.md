# LaTeX Export Workflow

## Purpose

This document describes the issue `#66` MVP workflow for exporting stored Open CVN
curriculum versions to LaTeX.

The export path is intentionally simple. It proves that a validated Open CVN JSON
document can be stored, materialized as a master or derived version, and rendered
to a deterministic `.tex` file.

## Command

Export the master version:

```bash
uv run open-cvn latex export cv.tex --store open-cvn.sqlite --version master
```

Export a derived version:

```bash
uv run open-cvn latex export public-cv.tex --store open-cvn.sqlite --version public
```

The command writes UTF-8 LaTeX text and creates parent directories for the output
path when needed.

## Input Source

LaTeX export reads stored curriculum versions through
`CurriculumRepository.materialize_version(...)`.

This means:

- master export renders the stored master curriculum
- derived export renders the materialized selection state
- include/exclude edits made through `open-cvn versions include` and
  `open-cvn versions exclude` are reflected in the `.tex` output
- Open CVN validation still runs during version materialization

## Template

The initial template lives at:

```text
src/open_cvn_app/templates/latex/basic_cv.tex.jinja
```

It renders:

- version metadata
- identity fields when present
- non-empty education entries
- non-empty research entries
- non-empty professional experience entries
- non-empty achievement entries
- non-empty other entries

Empty repeated sections are omitted in the MVP template.

## Escaping

Text values are escaped before insertion into LaTeX through the `latex` Jinja
filter implemented in `src/open_cvn_app/latex.py`.

The MVP escaping covers common LaTeX-sensitive characters:

```text
\ { } $ & # % _ ~ ^
```

## Determinism

The renderer avoids timestamps, random identifiers, and local absolute paths in
the generated `.tex` content.

Nested Open CVN values rendered as JSON use sorted keys. Exported files end with
one final newline.

## PDF Generation

PDF compilation from generated LaTeX is implemented by issue `#67` and documented
in:

```text
docs/development/pdf_generation_workflow.md
```

The PDF workflow remains optional because it depends on a local TeX distribution
outside Python dependencies.

## Limitations

The issue `#66` template is not a final CV design. It is a deterministic technical
proof for the export workflow.

The issue `#66` template is still not a final CV design. Issue `#67` compiles the
generated source into PDF when `latexmk` or `pdflatex` is available.
