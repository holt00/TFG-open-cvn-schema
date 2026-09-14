# Project Guide

## Purpose

This file is the human entry point for understanding the repository.
It summarizes the project purpose, the current implementation focus, the
documentation structure, and the repository rules that matter to contributors
and maintainers.

## What This Repository Is

This repository contains two successive academic projects on the same
system: a Trabajo de Fin de Grado (TFG), now finished, defended, and
delivered, and a Trabajo de Fin de Master (TFM) that is starting now on top
of it. Both are focused on defining an open data schema for representing
academic and research CVs in Spain, taking the CVN format as the starting
point.

The long-term goal is not only to mirror the official CVN package, but to make
curriculum data easier to validate, transform, store, and export through open
tooling.

## What The TFG Already Built (Closed Foundation)

The TFG delivered a complete, working system in this repository, not just a
partial technical base. In order, it built:

1. structural Pydantic bindings generated directly from the official CVN
   XML/XSD package (`src/generated/`)
2. a normalization layer that cross-indexes metadata from the official
   supporting XML documents by CVN code, resolved against auxiliary
   reference catalogs (`src/cvn_codegen/normalization.py`)
3. a semantic policy layer that recovers deterministic domain meaning
   (typing, naming, enum eligibility, overrides) from the normalized
   structural layer (`src/cvn_codegen/semantic_policy.py`)
4. domain-oriented Pydantic models generated over that normalized metadata
   (`src/cvn_codegen/domain_model_generator.py`,
   output in `src/models/cvn/generated/`)
5. an agnostic conceptual model layer feeding generated PlantUML diagrams
   and a generated JSON Schema (`docs/diagrams/`,
   `schemas/open_cvn.schema.json`)
6. the canonical Open CVN JSON document format and a unified
   parser/validator contract supporting PDF, XML, and JSON import
   (`src/open_cvn/`)
7. a local CLI CV management application on top of all of the above: SQLite
   storage, master/derived curriculum versions, LaTeX/PDF export, and an
   opt-in, deterministic-first LLM-assisted PDF import fallback
   (`src/open_cvn_app/`)
8. the TFG memoria itself, written, signed, and defended
   (`docs/memoria/TFG.pdf` / `TFG_signed.pdf`)

The full TFG issue-by-issue record (`#11` through `#71`) is closed and
archived at `docs/roadmap/cvn_generation_roadmap.md` and
`docs/context/current_status.md`. Those files are frozen: read them for
history, but do not add new entries to them.

## Current Technical Scope: The TFM

The TFM builds on top of that finished foundation rather than starting over.
Its concrete scope has not been defined yet; a placeholder epic exists at
`docs/roadmap/issues/issue-TBD-epic-tfm.md` pending that definition with the
user. Until it is defined, treat the repository as "TFG-complete, TFM scope
pending" rather than assuming any particular next technical direction.

## Recommended Reading Order For Humans

When you need to understand the project state before making changes, read these
files in order:

1. `PROJECT_GUIDE.md`
2. `docs/context/project_context_index.md`
3. `docs/context/tfm_current_status.md` (active TFM status; read
   `docs/context/current_status.md` separately for the closed TFG history)
4. the relevant issue document under `docs/roadmap/issues/` (TFM issues once
   defined; TFG issues `#11`-`#71` for historical foundation context)
5. supporting architecture or limitation documents linked from that issue

## Repository Rules And Conventions

- Treat `docs/CvnXML_v1.4.3_2.1_17012025/` as the canonical source package for
  the CVN generation roadmap
- Do not edit `src/generated/` manually
- Keep hand-maintained pipeline logic in `src/cvn_codegen/`
- Keep future semantic or domain models in `src/models/cvn/`
- Follow issue order unless there is a deliberate reason to work out of order
- Record implementation deviations from the original issue plan in the issue
  document for that issue
- Update persistent documentation in the same session as the code change
- Do not edit or add new entries to the closed TFG documents
  (`docs/context/current_status.md`,
  `docs/roadmap/cvn_generation_roadmap.md`, the TFG issue files `#11`-`#71`,
  and the TFG hotfix files `#1`-`#8`) except to fix a factual error found
  after closure; TFM work is logged in
  `docs/context/tfm_current_status.md` and `docs/roadmap/tfm_roadmap.md`
  instead
- Do not invent or expand TFM scope on your own initiative; the TFM epic is a
  deliberate placeholder until the user defines it

## Documentation Map

### Entry Points

- `README.md`: high-level repository overview
- `PROJECT_GUIDE.md`: human-oriented project entry point
- `AGENTS.md`: operational rules and document map for agents
- `CONTRIBUTING.md`: contributor onboarding and documentation obligations

### Current State And Context

- `docs/context/project_context_index.md`: documentation index and reading map
- `docs/context/tfm_current_status.md`: active TFM implementation state and
  next steps; also explains how the inherited TFG foundation works
- `docs/context/current_status.md`: closed TFG implementation log (`#11`-`#71`);
  historical only, no new entries
- `docs/reporte_proceso_desarrollo_tfg.md`: narrative report of the TFG
  development process, initial research, key decisions, implementation flow, and
  limitations
- `docs/memoria/estructura_memoria_tfg.md`: agreed memory structure and chapter
  status traceability for drafting the final TFG report

### Architecture And Limits

- `docs/pipeline/cvn_pydantic_generation_pipeline.md`: architecture of the CVN
  generation workflow
- `docs/pipeline/conceptual_model_extraction.md`: conceptual IR extraction layer
  between generated-domain evidence and later UML or JSON outputs
- `docs/diagrams/`: generated PlantUML sources and regeneration notes for the
  issue `#44` agnostic conceptual diagrams
- `docs/pipeline/json_schema_generation.md`: issue `#45` JSON Schema generation
  approach and regeneration notes
- `docs/pipeline/open_cvn_json_format.md`: issue `#46` canonical Open CVN JSON
  document format
- `docs/pipeline/open_cvn_json_mapping.md`: issue `#46` mapping notes from the
  conceptual inventory and schema annotations to runtime JSON
- `docs/pipeline/parser_validator_contract.md`: issue `#47` public parser and
  validator contract for future PDF, XML, and JSON import work
- `schemas/open_cvn.schema.json`: generated issue `#45` JSON Schema artifact
- `examples/open_cvn/`: representative issue `#46` Open CVN JSON examples
- `docs/pipeline/known_limitations.md`: structural limitations, source-package
  inconsistencies, and follow-up implications
- `docs/adr/`: architecture decision records

### Roadmap And Issue History

- `docs/roadmap/tfm_roadmap.md`: active TFM roadmap; epic not yet defined
- `docs/roadmap/issues/issue-TBD-epic-tfm.md`: TFM epic placeholder, also
  explains the inherited TFG architecture for a reader new to the project
- `docs/roadmap/cvn_generation_roadmap.md`: closed TFG roadmap, issue `#8`
  through issue `#71`, all completed
- `docs/roadmap/issues/issue-08-epic-cvn-automation.md`: epic summary and
  checkpoints
- `docs/roadmap/issues/issue-11-project-infrastructure.md`: authoritative
  record of issue `#11`
- `docs/roadmap/issues/issue-12-structural-bindings.md`: authoritative record
  of issue `#12`
- `docs/roadmap/issues/issue-13-normalization.md`: authoritative record of issue
  `#13`
- `docs/roadmap/issues/issue-14-semantic-mapping-rules.md`: authoritative
  record of issue `#14`
- `docs/roadmap/issues/issue-15-domain-model-generator.md`: authoritative record
  of issue `#15`
- `docs/roadmap/issues/issue-16-generation-pipeline-tests.md`: planned scope of
  issue `#16`
- `docs/roadmap/issues/issue-17-workflow-documentation.md`: planned scope of
  issue `#17`
- `docs/roadmap/issues/issue-25-github-actions-ci-pipeline-for-pr-testing-on-main-and-development.md`:
  authoritative record of issue `#25`
- `docs/roadmap/issues/issue-43-agnostic-conceptual-model-extraction-layer.md`:
  authoritative record of issue `#43`
- `docs/roadmap/issues/issue-46-define-canonical-open-cvn-json-format.md`:
  authoritative record of issue `#46`
- `docs/roadmap/issues/issue-47-unified-parser-validator-contract.md`:
  authoritative record of issue `#47`
- `docs/roadmap/issues/issue-48-cvn-pdf-xml-extraction.md`: authoritative
  record of issue `#48`
- `docs/roadmap/issues/issue-49-xml-json-import-validation.md`: planned scope of
  issue `#49`
- `docs/roadmap/issues/issue-50-parser-workflow-tests-and-documentation.md`:
  authoritative record of issue `#50`
- `docs/roadmap/issues/issue-60-epic-cv-management-application.md`:
  planned MVP application epic after issue `#41`
- `docs/roadmap/issues/issue-61-application-mvp-scope-and-cli-shell.md`:
  planned first issue for the application MVP
- `docs/roadmap/issues/issue-62-local-storage-sqlite-repository.md`: planned
  local SQLite storage issue
- `docs/roadmap/issues/issue-63-master-and-derived-curriculum-versions.md`:
  planned master and derived curriculum versioning issue
- `docs/roadmap/issues/issue-64-open-cvn-json-import-export-workflow.md`:
  authoritative record of the Open CVN JSON application import/export issue
- `docs/roadmap/issues/issue-65-curriculum-editing-and-selection-mvp.md`:
  planned MVP editing and selection issue
- `docs/roadmap/issues/issue-66-latex-export-from-open-cvn.md`: authoritative
  record of the LaTeX export issue
- `docs/roadmap/issues/issue-67-pdf-generation-and-preview-handoff.md`: planned
  optional PDF generation issue
- `docs/roadmap/issues/issue-68-application-mvp-tests-and-documentation.md`:
  planned application MVP tests and documentation issue
- `docs/roadmap/issues/issue-69-llm-assisted-import-spike.md`: planned post-MVP
  LLM import exploration
- `docs/roadmap/issues/issue-70-semantic-cvn-xml-import-to-open-cvn-json.md`:
  authoritative record of semantic CVN XML import into Open CVN JSON
- `docs/roadmap/issues/issue-71-limitations-hardening-and-documentation.md`:
  authoritative record of limitations hardening, documentation, PDF engine, and
  diagram usability work
- `docs/roadmap/hotfixes/hotfix-1-runner-logging-convention.md`: maintenance
  record for the runner logging convention update
- `docs/roadmap/hotfixes/hotfix-2-human-project-entrypoint.md`: maintenance
  record for the human project entry point and documentation update protocol
  alignment
- `docs/roadmap/hotfixes/hotfix-3-cvn-source-package-documentation-expansion.md`:
  maintenance record for the source-package documentation expansion and
  consistency cleanup
- `docs/roadmap/hotfixes/hotfix-4-structural-scope-correction-for-auxiliary-source-package-artifacts.md`:
  corrective plan for extending issues `#11` and `#12` to the auxiliary source
  package families
- `docs/roadmap/hotfixes/hotfix-5-normalization-resolution-layer-for-auxiliary-reference-sources.md`:
  corrective plan for extending issue `#13` with auxiliary-reference resolution
- `docs/roadmap/hotfixes/hotfix-6-roadmap-realignment-for-auxiliary-catalog-semantic-integration.md`:
  corrective plan for replanning issues `#8`, `#14` to `#17`, and the CI impact
  from the auxiliary catalog integration
- `docs/roadmap/hotfixes/hotfix-7-dynamic-reference-table-enum-eligibility-evaluation.md`:
  corrective plan for replacing hardcoded enum decisions with dynamic
  `ReferenceTables.xml` evidence in the normalization-to-semantic handoff
- `docs/roadmap/hotfixes/hotfix-8-wrapper-type-traceability-in-normalized-handoff.md`:
  implemented corrective handoff for exposing wrapper type evidence to semantic
  and domain generation stages without raw structural rediscovery
- `docs/roadmap/hotfixes/hotfix-9-tfg-completion-and-tfm-reorientation.md`:
  implemented record of closing out the TFG documentation and creating the
  active TFM documentation set alongside it

### Development Reference

- `docs/development/setup.md`: environment and execution commands
- `docs/development/regeneration_workflow.md`: complete CVN regeneration and
  verification workflow
- `docs/development/parser_workflow.md`: contributor guide for using and testing
  the public PDF/XML/JSON parser workflow
- `docs/development/application_mvp_workflow.md`: issue `#68` user workflow for
  the local CLI-first CV management MVP
- `docs/development/latex_export_workflow.md`: issue `#66` user workflow for
  exporting stored Open CVN master or derived versions to LaTeX
- `docs/development/pdf_generation_workflow.md`: issue `#67` user workflow for
  optional PDF generation and preview handoff from stored curriculum versions
- `docs/development/llm_import_workflow.md`: issue `#69` user workflow for
  deterministic-first PDF import with opt-in LLM fallback
- `docs/development/code_style.md`: code style, typing, and conventions
- `docs/documentation/documentation_conventions.md`: documentation taxonomy,
  cross-linking rules, and update protocol

### Source Package Analysis

- `docs/reporte_proceso_desarrollo_tfg.md`: consolidated process report for
  explaining the TFG development, including the initial research in
  `docs/research/` and the later implementation phases
- `docs/memoria/estructura_memoria_tfg.md`: planning and traceability document
  for the final TFG memory, including the eight-chapter structure, expected
  content, annexes, and per-chapter drafting status
- `docs/informe_estructura_cvnxml_v1.4.3.md`: detailed analysis of the core CVN
  package structure and usage
- `docs/cvn_source_package_auxiliary_artifacts.md`: detailed explanation of the
  auxiliary `Entity`, `ReferenceTables/Subtypes`, and `Thesaurus` families
- `docs/cvn_source_package_annex_table_coverage.md`: practical mapping of Annex
  I tables to core XSDs, side packages, and unresolved manual-only cases
- `docs/cvn_annex_priority_table_families.md`: detailed reference for the
  high-impact Annex I table families most relevant to semantic mapping work
- `docs/cvn_annex_table_families_batch3.md`: detailed reference for the next
  group of Annex I families covering participation, summons, programme,
  publication, support, and event tables
- `docs/cvn_annex_table_families_batch4.md`: detailed reference for the next
  group of Annex I families covering activity, management, scope, language,
  time, qualification, access, and evaluation tables
- `docs/cvn_annex_table_families_batch5.md`: detailed reference for the next
  group of Annex I families covering subject, stay, dedication, duration,
  formation, teaching, prizes, and thematic tables
- `docs/cvn_annex_table_families_batch6.md`: detailed reference for the next
  group of Annex I families covering region, province, sex, and situation
  tables
- `docs/cvn_annex_table_families_batch7.md`: detailed reference for the next
  group of Annex I families covering agency, collaboration, and cooperation
  tables, including unresolved `CVN_AGENCY_C`
- `docs/cvn_annex_table_families_batch8.md`: detailed reference for the final
  Annex I batch covering intervention, supervision, category, and residual test
  tables
- `docs/cvn_serialization_patterns_reference.md`: explicit reference of the
  serialization patterns used by CVN controlled tables, subtype-backed values,
  catalogs, and unresolved manual references
- `docs/cvn_field_reference_traceability.md`: operational traceability guide
  from normalized CVN fields to tables, side-package catalogs, backing artifacts,
  and serialization patterns

## Canonical Source Artifacts

The canonical package used by the generation pipeline is:

```text
docs/CvnXML_v1.4.3_2.1_17012025/
|- auxiliary catalog families: Entity, ReferenceTables/Subtypes, Thesaurus
|- XML/
|  |- SpecificationManual.xml
|  `- CVNTreeModel.xml
`- XSD/
   |- CVN.xsd
   |- Common.xsd
   |- AuxTable.xsd
   |- ISOUtilities.xsd
   |- SpecificationManual.xsd
   `- CVNTreeModel_v1.0.xsd
```

## Where Implementation History Lives

Each issue document under `docs/roadmap/issues/` records:

- original goal
- original planned steps
- implementation adjustments made during execution
- artifacts created
- verification performed
- findings and limitations
- impact on later issues

## How To Resume Work

When resuming the repository after time away:

1. read `docs/context/tfm_current_status.md` for the active TFM state (it
   also summarizes how the inherited TFG foundation works)
2. if the TFM epic is still a placeholder, stop and get it defined with the
   user before planning implementation; do not invent scope
3. once real TFM issues exist, read the last completed one and the next one
   from `docs/roadmap/tfm_roadmap.md`
4. review `docs/pipeline/known_limitations.md` for inherited TFG limitations
5. only then start implementation work

For deep historical context on how the TFG was actually built, read
`docs/context/current_status.md` and the TFG issue documents under
`docs/roadmap/issues/` (`#11`-`#71`); they are closed but remain the
authoritative record of the foundation the TFM builds on.
