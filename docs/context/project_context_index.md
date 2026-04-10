# Project Context Index

## Purpose

This document is the single documentation entry point for future sessions.
Anyone resuming work on the repository should start here after reading
`AGENTS.md`.

## Mandatory Reading Order

1. `AGENTS.md`
2. `docs/context/project_context_index.md`
3. `docs/context/current_status.md`
4. `docs/roadmap/issues/<current-issue>.md`
5. Supporting documents linked from the current issue file

## Current Project Snapshot

- Project: open CVN schema and tooling for Spanish academic CV processing
- Current pipeline stage: structural generation from official XSDs completed
- Last documented issues: `#11` and `#12`
- Last documented hotfix: `#1`
- Next planned issue: `#13`
- Canonical source package: `docs/CvnXML_v1.4.3_2.1_17012025/`

## Documentation Map

### Entry Points

- `README.md`: repository overview for humans
- `AGENTS.md`: operational rules for agents and pointer map
- `docs/context/current_status.md`: current project state and next actions

### Architecture And Pipeline

- `docs/pipeline/cvn_pydantic_generation_pipeline.md`: technical architecture
  of the CVN generation pipeline
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
- `docs/roadmap/issues/issue-13-normalization.md`: planned scope of issue `#13`
- `docs/roadmap/issues/issue-14-semantic-mapping-rules.md`: planned scope of
  issue `#14`
- `docs/roadmap/issues/issue-15-domain-model-generator.md`: planned scope of
  issue `#15`
- `docs/roadmap/issues/issue-16-generation-pipeline-tests.md`: planned scope of
  issue `#16`
- `docs/roadmap/issues/issue-17-workflow-documentation.md`: planned scope of
  issue `#17`
- `docs/roadmap/hotfixes/hotfix-1-runner-logging-convention.md`: maintenance
  record for the runner logging convention update

### Development And Contribution

- `docs/development/setup.md`: environment and execution commands
- `docs/development/code_style.md`: code style, typing, and documentation rules
- `docs/documentation/documentation_conventions.md`: documentation taxonomy and
  update protocol
- `CONTRIBUTING.md`: contributor onboarding and documentation obligations

### Supporting Background Material

- `docs/informe_estructura_cvnxml_v1.4.3.md`: structural analysis background
- `docs/propuesta_modelado_uml_ocl_cvn.md`: domain modeling background
- `references/`: external references and tutorial links

## Canonical Source Artifacts

The canonical package used by the generation pipeline is:

```text
docs/CvnXML_v1.4.3_2.1_17012025/
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
- Hotfix `#1`: `docs/roadmap/hotfixes/hotfix-1-runner-logging-convention.md`

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
5. Only then start implementation work
