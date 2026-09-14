# Current Status (TFM)

## Purpose

This file is the active implementation log for the TFM (Trabajo de Fin de
Master). It is the TFM counterpart of `docs/context/current_status.md`, which
now holds the complete, closed TFG (Trabajo de Fin de Grado) log and is no
longer updated. Read this file, not the TFG one, to find the current state of
the project.

## How The TFM Relates To The TFG

The TFM builds on top of the finished TFG rather than starting over. Nothing
described in the TFG documentation below is being redone; the TFM extends it.

### What The TFG Delivered

The TFG (issues `#11` through `#71`, roadmap in
`docs/roadmap/cvn_generation_roadmap.md`, full log in
`docs/context/current_status.md`) delivered, in this repository:

1. **Structural generation layer**: reproducible Pydantic bindings generated
   with `xsdata` from the official CVN XML/XSD package (`CVN.xsd`,
   `SpecificationManual.xsd`, `CVNTreeModel_v1.0.xsd`, and the auxiliary
   `ReferenceTables`, `Subtypes`, `Entity`, `Thesaurus` families), under
   `src/generated/`, driven by `src/cvn_codegen/xsdata_runner.py`. This layer
   is never edited by hand and is fully reproducible from canonical source
   inputs.
2. **Normalization layer**: `src/cvn_codegen/normalization.py` and related
   modules parse `SpecificationManual.xml` and `CVNTreeModel.xml`, cross-index
   every CVN field by its `code`, and resolve manual reference-table mentions
   against the auxiliary catalog families, producing typed
   `NormalizedCodeEntry` records with full source traceability.
3. **Semantic policy layer**: `src/cvn_codegen/semantic_policy.py` maps
   normalized metadata to deterministic domain-modeling decisions (types,
   naming, strict-enum eligibility, wrapper treatment, overrides), evidence-
   backed rather than hardcoded per table.
4. **Domain model generation**: `src/cvn_codegen/domain_model_generator.py`
   emits the final hand-consumable Pydantic domain models under
   `src/models/cvn/generated/` (105 generated files as of TFG closure), plus
   shared components in `src/models/cvn/components.py`.
5. **Conceptual model layer and diagrams**: an agnostic conceptual
   intermediate representation (`src/cvn_codegen/conceptual_model_extractor.py`)
   decoupled from generated Python class names, rendered as PlantUML diagrams
   under `docs/diagrams/`.
6. **JSON Schema and the canonical Open CVN JSON format**: a generated JSON
   Schema Draft 2020-12 artifact (`schemas/open_cvn.schema.json`) and the
   canonical Open CVN JSON document shape (`schema_version`, `metadata`,
   `curriculum`, `extensions`), documented in
   `docs/pipeline/open_cvn_json_format.md` with examples under
   `examples/open_cvn/`.
7. **Unified parser/validator contract**: the public `src/open_cvn/` package
   (`parser_contract.py`) with deterministic CVN PDF-to-XML extraction, CVN
   XML import (including semantic partial mapping into Open CVN JSON), and
   Open CVN JSON import/validation, documented in
   `docs/pipeline/parser_validator_contract.md` and
   `docs/development/parser_workflow.md`.
8. **Local CV management application**: a CLI-first application
   (`src/open_cvn_app/`) with SQLite storage, master/derived curriculum
   versioning, Open CVN JSON import/export, LaTeX export, optional PDF
   generation, and an opt-in, deterministic-first LLM-assisted PDF import
   fallback, documented in `docs/development/application_mvp_workflow.md`,
   `docs/development/latex_export_workflow.md`,
   `docs/development/pdf_generation_workflow.md`, and
   `docs/development/llm_import_workflow.md`.
9. **The written and defended TFG memoria**: `docs/memoria/TFG.pdf` /
   `TFG_signed.pdf`, covering the full academic writeup (motivation, state of
   the art, CVN ecosystem analysis, architecture, methodology, pipeline
   walkthrough, evaluation, conclusions), plus the defense slides in
   `docs/defensa/`.

Known, documented limitations of that foundation are tracked in
`docs/pipeline/known_limitations.md` and remain valid input for TFM planning.

### What The TFM Adds

The TFM scope has not been defined yet. A placeholder epic exists at
`docs/roadmap/issues/issue-TBD-epic-tfm.md` and will be filled in, numbered,
and expanded once the TFM objective is agreed with the user. Until then, this
file records only repository-reorientation work, not TFM feature work.

## Status Date

- Last updated: 2026-09-14 (repository reoriented from TFG to TFM)

## Entries

### Repository Reorientation: TFG Closed, TFM Started

- the TFG was confirmed complete: memoria written, signed, and defended
  (`docs/memoria/TFG.pdf`, `docs/memoria/TFG_signed.pdf`,
  `docs/defensa/presentacion_tfg.pdf`/`.pptx`)
- `docs/memoria/estructura_memoria_tfg.md` chapter status markers were
  corrected from stale `EN_PROCESO` to `COMPLETADO` to match the actual,
  already-defended state, and a closure banner was added at the top of the
  document
- a `tfg-final` git tag was created at the commit that finalized the TFG
  defense materials, as a permanent reference point for the exact finished-TFG
  state
- the following TFG-era files were frozen in place with an explicit closure
  banner, rather than moved, specifically to avoid breaking the many existing
  cross-references to their paths from the 30 issue documents, 8 hotfix
  documents, and the documentation-contract files:
  - `docs/context/current_status.md` (complete TFG implementation log)
  - `docs/roadmap/cvn_generation_roadmap.md` (complete TFG roadmap)
- new active TFM counterparts were created alongside them instead of
  replacing them:
  - `docs/context/tfm_current_status.md` (this file)
  - `docs/roadmap/tfm_roadmap.md`
  - `docs/roadmap/issues/issue-TBD-epic-tfm.md` (placeholder epic, content
    intentionally not yet defined)
- the repository entry-point and documentation-contract files were updated to
  point new sessions at the TFM files first, while still describing the TFG
  foundation for context:
  `README.md`, `PROJECT_GUIDE.md`, `AGENTS.md`, `CONTRIBUTING.md`,
  `docs/context/project_context_index.md`,
  `docs/documentation/documentation_conventions.md`,
  `docs/documentation/project_contracts.md`
- the transition itself is recorded as
  `docs/roadmap/hotfixes/hotfix-9-tfg-completion-and-tfm-reorientation.md`,
  following this repository's existing convention of recording structural or
  documentation-map changes as a hotfix record
- no TFG source code, generated artifacts, or the TFG memoria's LaTeX content
  were modified beyond the two stale-status corrections above
