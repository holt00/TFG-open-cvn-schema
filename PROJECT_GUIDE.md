# Project Guide

## Purpose

This file is the human entry point for understanding the repository.
It summarizes the project purpose, the current implementation focus, the
documentation structure, and the repository rules that matter to contributors
and maintainers.

## What This Repository Is

This repository contains a Trabajo de Fin de Grado focused on defining an open
data schema for representing academic and research CVs in Spain, taking the
CVN format as the starting point.

The long-term goal is not only to mirror the official CVN package, but to make
curriculum data easier to validate, transform, store, and export through open
tooling.

## Current Technical Scope

The repository is currently centered on the generation pipeline that turns the
official CVN XML/XSD package into reproducible Python artifacts.

Current and planned layers are:

1. structural bindings generated from the official CVN XML/XSD package
2. normalized metadata extracted from the official supporting XML documents
3. semantic mapping rules that recover domain meaning from the structural layer
4. domain-oriented Pydantic models built over normalized metadata

This means the repository is currently implementing the technical foundation
for the future parser, validator, JSON-oriented schema, and downstream export
work. It is not yet the full end-user CV tooling envisioned by the TFG.

## Recommended Reading Order For Humans

When you need to understand the project state before making changes, read these
files in order:

1. `PROJECT_GUIDE.md`
2. `docs/context/project_context_index.md`
3. `docs/context/current_status.md`
4. the relevant issue document under `docs/roadmap/issues/`
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

## Documentation Map

### Entry Points

- `README.md`: high-level repository overview
- `PROJECT_GUIDE.md`: human-oriented project entry point
- `AGENTS.md`: operational rules and document map for agents
- `CONTRIBUTING.md`: contributor onboarding and documentation obligations

### Current State And Context

- `docs/context/project_context_index.md`: documentation index and reading map
- `docs/context/current_status.md`: latest implementation state and next steps

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
- `schemas/open_cvn.schema.json`: generated issue `#45` JSON Schema artifact
- `examples/open_cvn/`: representative issue `#46` Open CVN JSON examples
- `docs/pipeline/known_limitations.md`: structural limitations, source-package
  inconsistencies, and follow-up implications
- `docs/adr/`: architecture decision records

### Roadmap And Issue History

- `docs/roadmap/cvn_generation_roadmap.md`: roadmap from issue `#8` through
  issue `#17`
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

### Development Reference

- `docs/development/setup.md`: environment and execution commands
- `docs/development/regeneration_workflow.md`: complete CVN regeneration and
  verification workflow
- `docs/development/code_style.md`: code style, typing, and conventions
- `docs/documentation/documentation_conventions.md`: documentation taxonomy,
  cross-linking rules, and update protocol

### Source Package Analysis

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

1. read `docs/context/current_status.md`
2. read the last completed issue document
3. read the next issue document from the roadmap
4. review `docs/pipeline/known_limitations.md`
5. only then start implementation work
