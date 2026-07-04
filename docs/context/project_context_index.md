# Project Context Index

## Purpose

This document is the single documentation entry point for future sessions.
Humans should normally start with `PROJECT_GUIDE.md` before coming here.
Agents should also read `AGENTS.md` before this file.

## Mandatory Reading Order

### For Humans

1. `PROJECT_GUIDE.md`
2. `docs/context/project_context_index.md`
3. `docs/context/current_status.md`
4. `docs/roadmap/issues/<current-issue>.md`
5. Supporting documents linked from the current issue file

### For Agents

1. `AGENTS.md`
2. `PROJECT_GUIDE.md`
3. `docs/context/project_context_index.md`
4. `docs/context/current_status.md`
5. `docs/roadmap/issues/<current-issue>.md`
6. Supporting documents linked from the current issue file

## Current Project Snapshot

- Project: open CVN schema and tooling for Spanish academic CV processing
- Current pipeline stage: structural generation, metadata normalization,
  semantic policy, and domain generation completed
- Last documented issues: `#11`, `#12`, `#13`, `#14`, `#15`, and `#25`
- Latest documented hotfix records: `#3`, `#4`, `#5`, `#6`, `#7`, `#8`
- Next planned issue: `#16`
- Canonical source package: `docs/CvnXML_v1.4.3_2.1_17012025/`

## Documentation Map

### Entry Points

- `README.md`: repository overview for humans
- `PROJECT_GUIDE.md`: human-oriented project entry point
- `AGENTS.md`: operational rules for agents and pointer map
- `docs/context/current_status.md`: current project state and next actions

### Architecture And Pipeline

- `docs/pipeline/cvn_pydantic_generation_pipeline.md`: technical architecture
  of the CVN generation pipeline
- `docs/pipeline/conceptual_model_extraction.md`: issue `#43` conceptual IR
  extraction layer for later diagram and JSON outputs
- `docs/diagrams/`: issue `#44` generated PlantUML sources and diagram
  regeneration notes
- `docs/pipeline/known_limitations.md`: structural limitations, detected
  discrepancies, and follow-up implications
- `docs/adr/`: architecture decision records

### Roadmap And Issue History

- `docs/roadmap/cvn_generation_roadmap.md`: roadmap from issue `#8` through
  `#17`
- `docs/roadmap/issues/issue-08-epic-cvn-automation.md`: epic summary and
  checkpoints
- `docs/roadmap/issues/issue-11-project-infrastructure.md`: full record of
  issue `#11`
- `docs/roadmap/issues/issue-12-structural-bindings.md`: full record of issue
  `#12`
- `docs/roadmap/issues/issue-13-normalization.md`: full record of issue `#13`
- `docs/roadmap/issues/issue-14-semantic-mapping-rules.md`: full record of
  issue `#14`
- `docs/roadmap/issues/issue-15-domain-model-generator.md`: authoritative record
  of issue `#15`
- `docs/roadmap/issues/issue-16-generation-pipeline-tests.md`: planned scope of
  issue `#16`
- `docs/roadmap/issues/issue-17-workflow-documentation.md`: planned scope of
  issue `#17`
- `docs/roadmap/issues/issue-25-github-actions-ci-pipeline-for-pr-testing-on-main-and-development.md`:
  implementation record for issue `#25`
- `docs/roadmap/issues/issue-43-agnostic-conceptual-model-extraction-layer.md`:
  implementation record for issue `#43`
- `docs/roadmap/hotfixes/hotfix-1-runner-logging-convention.md`: maintenance
  record for the runner logging convention update
- `docs/roadmap/hotfixes/hotfix-2-human-project-entrypoint.md`: maintenance
  record for the human project entry point and update protocol alignment
- `docs/roadmap/hotfixes/hotfix-3-cvn-source-package-documentation-expansion.md`:
  maintenance record for the source-package documentation expansion and
  consistency cleanup
- `docs/roadmap/hotfixes/hotfix-4-structural-scope-correction-for-auxiliary-source-package-artifacts.md`:
  corrective plan for expanding the structural scope of issues `#11` and `#12`
- `docs/roadmap/hotfixes/hotfix-5-normalization-resolution-layer-for-auxiliary-reference-sources.md`:
  corrective plan for extending issue `#13` with auxiliary-reference resolution
- `docs/roadmap/hotfixes/hotfix-6-roadmap-realignment-for-auxiliary-catalog-semantic-integration.md`:
  corrective plan for replanning the pending semantic and workflow issues after
  the analysis of the auxiliary modules recently added in the source bundle sent
  by FECYT
- `docs/roadmap/hotfixes/hotfix-7-dynamic-reference-table-enum-eligibility-evaluation.md`:
  corrective plan for dynamic strict-enum eligibility evaluation across
  `ReferenceTables.xml` without semantic-policy hardcoding
- `docs/roadmap/hotfixes/hotfix-8-wrapper-type-traceability-in-normalized-handoff.md`:
  implemented corrective handoff for exposing wrapper type evidence to downstream
  semantic and domain generation without raw structural rediscovery

### Development And Contribution

- `docs/development/setup.md`: environment and execution commands
- `docs/development/regeneration_workflow.md`: complete CVN regeneration and
  verification workflow
- `docs/development/code_style.md`: code style, typing, and documentation rules
- `docs/documentation/documentation_conventions.md`: documentation taxonomy and
  update protocol
- `CONTRIBUTING.md`: contributor onboarding and documentation obligations

### Supporting Background Material

- `docs/informe_estructura_cvnxml_v1.4.3.md`: structural analysis background
- `docs/cvn_source_package_auxiliary_artifacts.md`: detailed explanation of the
  auxiliary `Entity`, `ReferenceTables/Subtypes`, and `Thesaurus` families in
  the canonical source package
- `docs/cvn_source_package_annex_table_coverage.md`: practical map of Annex I
  tables to core XSDs, side packages, and unresolved manual-only cases
- `docs/cvn_annex_priority_table_families.md`: detailed reference for the
  high-priority Annex I table families that most affect semantic modeling
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
  catalogs, and unresolved references
- `docs/cvn_field_reference_traceability.md`: operational guide from normalized
  CVN fields to tables, catalogs, backing artifacts, and serialization patterns
- `docs/propuesta_modelado_uml_ocl_cvn.md`: domain modeling background
- `references/`: external references and tutorial links

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

## Where To Find The State Of Each Implemented Issue

- Issue `#11`: `docs/roadmap/issues/issue-11-project-infrastructure.md`
- Issue `#12`: `docs/roadmap/issues/issue-12-structural-bindings.md`
- Issue `#13`: `docs/roadmap/issues/issue-13-normalization.md`
- Issue `#25`:
  `docs/roadmap/issues/issue-25-github-actions-ci-pipeline-for-pr-testing-on-main-and-development.md`
- Hotfix `#1`: `docs/roadmap/hotfixes/hotfix-1-runner-logging-convention.md`
- Hotfix `#2`: `docs/roadmap/hotfixes/hotfix-2-human-project-entrypoint.md`
- Hotfix `#3`:
  `docs/roadmap/hotfixes/hotfix-3-cvn-source-package-documentation-expansion.md`
- Hotfix `#4`:
  `docs/roadmap/hotfixes/hotfix-4-structural-scope-correction-for-auxiliary-source-package-artifacts.md`
- Hotfix `#5`:
  `docs/roadmap/hotfixes/hotfix-5-normalization-resolution-layer-for-auxiliary-reference-sources.md`
- Hotfix `#6`:
  `docs/roadmap/hotfixes/hotfix-6-roadmap-realignment-for-auxiliary-catalog-semantic-integration.md`
- Hotfix `#7`:
  `docs/roadmap/hotfixes/hotfix-7-dynamic-reference-table-enum-eligibility-evaluation.md`
- Hotfix `#8`:
  `docs/roadmap/hotfixes/hotfix-8-wrapper-type-traceability-in-normalized-handoff.md`

Each issue document records:

- original goal
- original planned steps
- implementation adjustments made during execution
- artifacts created
- verification performed
- findings and limitations
- impact on later issues

## Resume Work Checklist

When starting a new session:

1. Read `docs/context/current_status.md`
2. Read the last completed issue document
3. Read the next issue document from the roadmap
4. Review `docs/pipeline/known_limitations.md`
5. Review `docs/development/regeneration_workflow.md` when the work touches
   generated artifacts or pipeline verification
6. Only then start implementation work
