# AGENTS.md - Operational Guide For Repository Agents

## Purpose

This file is the operational entry point for agents working in this repository.
It is not the project knowledge base. Persistent project context has been moved
to versioned documentation under `docs/`.

## Two Projects, One Repository

This repository holds a completed TFG (Trabajo de Fin de Grado) and a TFM
(Trabajo de Fin de Master) now being built on top of it. Before touching
anything, know which one you are in:

- the TFG is closed: issues `#11`-`#71`, hotfixes `#1`-`#8`, roadmap
  `docs/roadmap/cvn_generation_roadmap.md`, status log
  `docs/context/current_status.md`, and the signed/defended memoria under
  `docs/memoria/`. Do not add new entries to the TFG status log or roadmap.
- the TFM is active but its scope is not yet defined: roadmap
  `docs/roadmap/tfm_roadmap.md`, status log
  `docs/context/tfm_current_status.md`, placeholder epic
  `docs/roadmap/issues/issue-TBD-epic-tfm.md`. Do not invent TFM scope; wait
  for the user to define it.

Full detail on this split, including why the TFG files were frozen in place
rather than moved, is in
`docs/roadmap/hotfixes/hotfix-9-tfg-completion-and-tfm-reorientation.md`.

## Mandatory Reading Order

Every new session should read these files in order before making changes:

1. `AGENTS.md`
2. `PROJECT_GUIDE.md`
3. `docs/context/project_context_index.md`
4. `docs/context/tfm_current_status.md` (active TFM state; also explains how
   the inherited TFG foundation works)
5. The relevant issue document under `docs/roadmap/issues/` (a TFM issue once
   defined, or a TFG issue `#11`-`#71` when the task requires understanding
   the existing foundation)

## Repository-Specific Rules

- Treat `docs/CvnXML_v1.4.3_2.1_17012025/` as the canonical source package for
  the CVN generation roadmap
- Do not edit `src/generated/` manually
- Keep hand-maintained pipeline logic in `src/cvn_codegen/`
- Keep future semantic or domain models in `src/models/cvn/`
- Follow issue order unless the user explicitly requests otherwise
- Record implementation deviations from the original issue plan in the issue
  document for that issue
- Update persistent documentation in the same session as the code change
- Do not edit or add new entries to the closed TFG documents
  (`docs/context/current_status.md`,
  `docs/roadmap/cvn_generation_roadmap.md`, TFG issue files `#11`-`#71`, TFG
  hotfix files `#1`-`#8`) except to fix a factual error found after closure
- Log TFM work in `docs/context/tfm_current_status.md` and
  `docs/roadmap/tfm_roadmap.md`, not in their TFG counterparts
- Do not invent or expand TFM scope on your own initiative; the TFM epic
  (`docs/roadmap/issues/issue-TBD-epic-tfm.md`) is a deliberate placeholder
  until the user defines it

## Documentation Map

### Entry Points

- human project guide: `PROJECT_GUIDE.md`
- context index: `docs/context/project_context_index.md`
- current state (TFM, active): `docs/context/tfm_current_status.md`
- current state (TFG, closed): `docs/context/current_status.md`
- TFG memory structure and chapter status traceability (completed):
  `docs/memoria/estructura_memoria_tfg.md`

### Architecture And Limits

- pipeline architecture: `docs/pipeline/cvn_pydantic_generation_pipeline.md`
- conceptual extraction: `docs/pipeline/conceptual_model_extraction.md`
- conceptual diagrams: `docs/diagrams/`
- JSON Schema generation: `docs/pipeline/json_schema_generation.md`
- parser/validator contract: `docs/pipeline/parser_validator_contract.md`
- known limitations: `docs/pipeline/known_limitations.md`
- architecture decisions: `docs/adr/`

### Roadmap And Issue Records

- roadmap overview (TFM, active): `docs/roadmap/tfm_roadmap.md`
- epic (TFM, placeholder, not yet defined):
  `docs/roadmap/issues/issue-TBD-epic-tfm.md`
- roadmap overview (TFG, closed): `docs/roadmap/cvn_generation_roadmap.md`
- epic summary (TFG): `docs/roadmap/issues/issue-08-epic-cvn-automation.md`
- issue `#11`: `docs/roadmap/issues/issue-11-project-infrastructure.md`
- issue `#12`: `docs/roadmap/issues/issue-12-structural-bindings.md`
- issue `#13`: `docs/roadmap/issues/issue-13-normalization.md`
- issue `#14`: `docs/roadmap/issues/issue-14-semantic-mapping-rules.md`
- issue `#15`: `docs/roadmap/issues/issue-15-domain-model-generator.md`
- issue `#16`: `docs/roadmap/issues/issue-16-generation-pipeline-tests.md`
- issue `#17`: `docs/roadmap/issues/issue-17-workflow-documentation.md`
- issue `#25`:
  `docs/roadmap/issues/issue-25-github-actions-ci-pipeline-for-pr-testing-on-main-and-development.md`
- issue `#43`:
  `docs/roadmap/issues/issue-43-agnostic-conceptual-model-extraction-layer.md`
- issue `#45`:
  `docs/roadmap/issues/issue-45-generate-json-schema-from-domain-models.md`
- issue `#46`:
  `docs/roadmap/issues/issue-46-define-canonical-open-cvn-json-format.md`
- issue `#47`:
  `docs/roadmap/issues/issue-47-unified-parser-validator-contract.md`
- issue `#48`:
  `docs/roadmap/issues/issue-48-cvn-pdf-xml-extraction.md`
- issue `#49`:
  `docs/roadmap/issues/issue-49-xml-json-import-validation.md`
- issue `#50`:
  `docs/roadmap/issues/issue-50-parser-workflow-tests-and-documentation.md`
- issue `#60`:
  `docs/roadmap/issues/issue-60-epic-cv-management-application.md`
- issue `#61`:
  `docs/roadmap/issues/issue-61-application-mvp-scope-and-cli-shell.md`
- issue `#62`:
  `docs/roadmap/issues/issue-62-local-storage-sqlite-repository.md`
- issue `#63`:
  `docs/roadmap/issues/issue-63-master-and-derived-curriculum-versions.md`
- issue `#64`:
  `docs/roadmap/issues/issue-64-open-cvn-json-import-export-workflow.md`
- issue `#65`:
  `docs/roadmap/issues/issue-65-curriculum-editing-and-selection-mvp.md`
- issue `#66`:
  `docs/roadmap/issues/issue-66-latex-export-from-open-cvn.md`
- issue `#67`:
  `docs/roadmap/issues/issue-67-pdf-generation-and-preview-handoff.md`
- issue `#68`:
  `docs/roadmap/issues/issue-68-application-mvp-tests-and-documentation.md`
- issue `#69`:
  `docs/roadmap/issues/issue-69-llm-assisted-import-spike.md`
- issue `#70`:
  `docs/roadmap/issues/issue-70-semantic-cvn-xml-import-to-open-cvn-json.md`
- issue `#71`:
  `docs/roadmap/issues/issue-71-limitations-hardening-and-documentation.md`
- hotfix `#1`: `docs/roadmap/hotfixes/hotfix-1-runner-logging-convention.md`
- hotfix `#2`: `docs/roadmap/hotfixes/hotfix-2-human-project-entrypoint.md`
- hotfix `#3`:
  `docs/roadmap/hotfixes/hotfix-3-cvn-source-package-documentation-expansion.md`
- hotfix `#4`:
  `docs/roadmap/hotfixes/hotfix-4-structural-scope-correction-for-auxiliary-source-package-artifacts.md`
- hotfix `#5`:
  `docs/roadmap/hotfixes/hotfix-5-normalization-resolution-layer-for-auxiliary-reference-sources.md`
- hotfix `#6`:
  `docs/roadmap/hotfixes/hotfix-6-roadmap-realignment-for-auxiliary-catalog-semantic-integration.md`
- hotfix `#7`:
  `docs/roadmap/hotfixes/hotfix-7-dynamic-reference-table-enum-eligibility-evaluation.md`
- hotfix `#8`:
  `docs/roadmap/hotfixes/hotfix-8-wrapper-type-traceability-in-normalized-handoff.md`
- hotfix `#9`:
  `docs/roadmap/hotfixes/hotfix-9-tfg-completion-and-tfm-reorientation.md`

### Development Reference

- setup and commands: `docs/development/setup.md`
- complete regeneration workflow: `docs/development/regeneration_workflow.md`
- parser workflow: `docs/development/parser_workflow.md`
- application MVP workflow: `docs/development/application_mvp_workflow.md`
- LaTeX export workflow: `docs/development/latex_export_workflow.md`
- PDF generation workflow: `docs/development/pdf_generation_workflow.md`
- LLM import workflow: `docs/development/llm_import_workflow.md`
- code style and conventions: `docs/development/code_style.md`
- documentation conventions: `docs/documentation/documentation_conventions.md`
- old AGENTS content migration map:
  `docs/documentation/agents_content_migration_map.md`

## Documentation Update Protocol

At the end of any TFM issue implementation, update:

1. the issue document under `docs/roadmap/issues/`
2. `docs/context/tfm_current_status.md` (the active status log; do not add
   entries to the closed `docs/context/current_status.md`)
3. `docs/pipeline/known_limitations.md` if a new limitation was found
4. `docs/roadmap/tfm_roadmap.md` if the issue status changed (do not edit the
   closed `docs/roadmap/cvn_generation_roadmap.md`)
5. `PROJECT_GUIDE.md` when the human-facing project entry guidance, document
   map, contributor reading order, or repository orientation changes

Update `AGENTS.md` only when the document map or operational rules change.
