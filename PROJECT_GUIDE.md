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
- `docs/roadmap/issues/issue-13-normalization.md`: authoritative record and
  planned scope around issue `#13`
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
- `docs/roadmap/hotfixes/hotfix-2-human-project-entrypoint.md`: maintenance
  record for the human project entry point and documentation update protocol
  alignment

### Development Reference

- `docs/development/setup.md`: environment and execution commands
- `docs/development/code_style.md`: code style, typing, and conventions
- `docs/documentation/documentation_conventions.md`: documentation taxonomy,
  cross-linking rules, and update protocol

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
