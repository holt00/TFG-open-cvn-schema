# Issue 60 - Epic: CV Management Application

## Summary

Epic `#60` defines the MVP application layer built on top of the completed epic
`#41` Open CVN schema, JSON Schema, and parser/validator foundation.

The MVP goal is not to deliver a complete polished CV management product. It is a
small but usable prototype that proves the TFG workflow end to end:

```text
Open CVN JSON or CVN PDF/XML input
-> validated Open CVN document
-> local storage
-> master curriculum and derived versions
-> basic editing/selection
-> JSON export
-> LaTeX export
-> optional local PDF artifact generation
```

The implementation should prefer a simple CLI or minimal local interface before
any heavy UI framework. A later issue may add a desktop or web UI if the MVP
foundation is stable.

## TFG Alignment

This epic addresses the application-oriented TFG phases:

1. local curriculum storage
2. JSON export
3. LaTeX export
4. PDF generation from LaTeX
5. user-facing management of master and derived curriculum versions

## Initial Scope

The MVP application should include:

- internal application logic built on the parser/validator from epic `#41`
- import and export of Open CVN JSON
- export to LaTeX using Jinja templates
- LaTeX compilation into PDF
- a local path or lightweight preview handoff for generated PDFs
- SQLite persistence
- one master curriculum containing all known data
- multiple derived curriculum versions with more or fewer data depending on the
  target purpose
- ability to customize a derived version from the master curriculum by editing
  the original or cloning it
- ability to add or remove fields and CVN codes in derived versions

## MVP Boundaries

The MVP must provide the smallest useful application workflow:

- create or open a local curriculum store
- import a valid Open CVN JSON document
- optionally import direct CVN XML or CVN PDF when parser support is sufficient
- persist one master curriculum
- create at least one derived version from the master curriculum
- include or exclude sections or entries in a derived version
- export master or derived versions as Open CVN JSON
- render a simple LaTeX document from a stored curriculum version
- optionally compile LaTeX into PDF when a local TeX engine is installed
- document commands, limitations, and manual fallback steps

The MVP may intentionally omit:

- rich GUI editing
- field-by-field validation UX
- multi-user synchronization
- cloud storage
- complete semantic CVN XML-to-domain conversion
- automatic LLM reconstruction from arbitrary PDFs
- advanced template customization
- guaranteed PDF preview integration across all platforms

## Dependency On Epic `#41`

The MVP must consume epic `#41` artifacts instead of redefining them:

- use `parse_open_cvn_json(...)`, `validate_open_cvn_json(...)`,
  `parse_cvn_xml(...)`, and `parse_cvn_pdf(...)` from `src/open_cvn/`
- validate Open CVN JSON against `schemas/open_cvn.schema.json`
- preserve parser trace metadata and structured errors
- treat CVN XML import as trace-only until a later issue defines full semantic
  XML-to-domain mapping
- keep Open CVN JSON root shape from issue `#46`:
  `schema_version`, `metadata`, `curriculum`, and `extensions`
- keep generated structural and generated domain code untouched by manual edits

## Child Issues

The MVP is split into these child issues:

- issue `#61`: `docs/roadmap/issues/issue-61-application-mvp-scope-and-cli-shell.md`
- issue `#62`: `docs/roadmap/issues/issue-62-local-storage-sqlite-repository.md`
- issue `#63`: `docs/roadmap/issues/issue-63-master-and-derived-curriculum-versions.md`
- issue `#64`: `docs/roadmap/issues/issue-64-open-cvn-json-import-export-workflow.md`
- issue `#65`: `docs/roadmap/issues/issue-65-curriculum-editing-and-selection-mvp.md`
- issue `#66`: `docs/roadmap/issues/issue-66-latex-export-from-open-cvn.md`
- issue `#67`: `docs/roadmap/issues/issue-67-pdf-generation-and-preview-handoff.md`
- issue `#68`: `docs/roadmap/issues/issue-68-application-mvp-tests-and-documentation.md`
- issue `#69`: `docs/roadmap/issues/issue-69-llm-assisted-import-spike.md`

Issues `#61` through `#68` define the MVP delivery path. Issue `#69` is a
post-MVP exploratory spike aligned with the TFG LLM objective, but it must not
block the local storage and export prototype.

## Deferred Planning Notes

The MVP chooses these initial decisions:

- application type: CLI-first local application
- persistence: SQLite file for local storage
- Open CVN exchange: JSON files validated through epic `#41`
- LaTeX templating: Jinja templates over Open CVN JSON data
- PDF generation: optional local compiler invocation with graceful fallback when
  no TeX engine is installed
- preview: open or report generated PDF path, not embedded viewer in MVP
- editing workflow: coarse section/entry include-exclude and limited JSON-patch or
  field override workflow before full GUI editing

The epic should later revisit:

- UI framework
- migration strategy beyond the initial SQLite schema version
- full field-level editing UX
- curated XML-to-domain mapping
- advanced template packs
- cross-platform PDF preview integration
- LLM-assisted import after deterministic import is stable

## Dependencies

- epic `#41` for the agnostic schema, JSON Schema, and parser/validator contract
- `docs/development/parser_workflow.md` for parser usage examples
- `docs/pipeline/open_cvn_json_format.md` for canonical JSON shape
- `docs/pipeline/known_limitations.md` for current parser and schema limits

## Out Of Scope For Now

- production-grade GUI
- user authentication
- cloud synchronization
- full FECYT PDF reconstruction without embedded XML
- complete CVN XML semantic mapping
- fully polished LaTeX design
- guaranteed PDF generation on machines without a TeX installation

## Expected MVP Output

- CLI-first application entry point
- local SQLite-backed curriculum store
- master curriculum persistence
- derived curriculum versions
- Open CVN JSON import/export
- basic version selection or editing workflow
- LaTeX export from stored Open CVN data
- optional PDF generation with clear unsupported behavior
- tests for storage, import/export, versioning, and LaTeX rendering
- user documentation for running the prototype

## Implementation Notes

- Issues `#61` through `#68` now complete the local application MVP delivery path.
- The implemented MVP provides:
  - CLI-first application shell through `open-cvn`
  - local SQLite store initialization and repository behavior
  - master curriculum assignment
  - derived curriculum versions
  - section and entry include/exclude selection
  - Open CVN JSON import and export through the public parser/validator contract
  - deterministic LaTeX export
  - optional PDF generation with structured missing-compiler behavior
  - user-facing MVP workflow documentation
- The issue `#68` closure guide exists at:
  - `docs/development/application_mvp_workflow.md`
- Post-MVP issue `#69` remains the planned LLM-assisted import spike and does not
  block the local storage and export MVP.

## Verification Performed For MVP Closure

- Issue `#68` added end-to-end application workflow tests in:
  - `tests/test_open_cvn_app_mvp_workflow.py`
- Application MVP regression verification passed with:
  - `uv run pytest -n auto tests/test_open_cvn_app_mvp_workflow.py tests/test_open_cvn_app_cli_unit.py tests/test_open_cvn_app_storage_unit.py tests/test_open_cvn_app_versioning_unit.py tests/test_open_cvn_app_editing_unit.py tests/test_open_cvn_app_latex_unit.py tests/test_open_cvn_app_pdf_unit.py -v`
  - result: `72 passed in 90.20s (0:01:30)`
- Full repository verification passed with:
  - `uv run pytest -n auto tests`
  - result: `442 passed in 359.41s (0:05:59)`

## Verification Strategy

- unit tests for storage repositories and versioning logic
- parser integration tests using existing Open CVN JSON examples
- snapshot or deterministic-output tests for LaTeX rendering
- CLI smoke tests for create/import/export/version commands
- PDF generation tests that skip or assert structured unsupported behavior when no
  TeX engine is available
- full repository verification with `uv run pytest -n auto tests`

## Status

- Status: completed
- Issues `#61` through `#68` complete the local application MVP.
- Issue `#69` remains post-MVP exploratory work.
