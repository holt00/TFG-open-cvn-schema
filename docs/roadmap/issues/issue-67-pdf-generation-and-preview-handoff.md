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

## Status

- Status: planned
