# TFM Roadmap

## Purpose

This is the active roadmap for the TFM (Trabajo de Fin de Master). It is the
TFM counterpart of `docs/roadmap/tfg/cvn_generation_roadmap.md`, which now holds
the complete, closed TFG (Trabajo de Fin de Grado) roadmap (issues `#8`
through `#71`, all `Completed`) and is no longer updated.

## The TFM Builds On The TFG

This is not a new project starting from an empty repository. The TFM
continues directly on top of the TFG deliverables:

- the CVN XML/XSD to Pydantic generation pipeline: structural bindings
  (`src/generated/`), normalization
  (`src/cvn_codegen/normalization.py`), semantic policy
  (`src/cvn_codegen/semantic_policy.py`), and domain model generation
  (`src/cvn_codegen/domain_model_generator.py`, output in
  `src/models/cvn/generated/`)
- the agnostic conceptual model layer and generated PlantUML diagrams
  (`src/cvn_codegen/conceptual_model_extractor.py`, `docs/diagrams/`)
- the generated JSON Schema and canonical Open CVN JSON document format
  (`schemas/open_cvn.schema.json`, `docs/pipeline/open_cvn_json_format.md`)
- the unified parser/validator contract with PDF, XML, and JSON import paths
  (`src/open_cvn/`, `docs/pipeline/parser_validator_contract.md`)
- the local CLI CV management application: SQLite storage, master/derived
  curriculum versions, LaTeX export, optional PDF generation, and opt-in
  LLM-assisted PDF import (`src/open_cvn_app/`)
- the written, signed, and defended TFG memoria (`docs/memoria/TFG.pdf`)

A full walkthrough of how that foundation actually works, stage by stage, is
in `docs/pipeline/cvn_pydantic_generation_pipeline.md` and
`docs/development/regeneration_workflow.md`; the condensed version lives in
`docs/context/tfm/current_status.md`. Known limitations of that foundation are
tracked in `docs/pipeline/known_limitations.md` and remain valid input for TFM
planning; do not silently rediscover them.

## Roadmap Rules

Same rules as the TFG roadmap, carried forward:

- follow issue order unless the user explicitly requests otherwise
- keep generated and hand-maintained code separated
- document implementation deviations from the original plan
- prefer reproducible artifacts over implicit knowledge
- record structural or documentation-map changes as a hotfix record, the same
  way the TFG did

## Epic Scope

**Defined.** Epic: "Diseño de una arquitectura lakehouse escalable para la
integración y análisis de información curricular académica." Full detail,
including the technology stack decision record, data-source strategy, phased
plan, scope cut list, and the repository standards that apply, is in
`docs/roadmap/tfm/issues/issue-89-epic-tfm-lakehouse-platform.md`. That document is self-contained;
read it before starting any implementation.

In one paragraph: a self-hosted Kubernetes (k3s) lakehouse ingesting CVN
(synthetic, schema-valid, ORCID-seeded) and ORCID (real, via API for
enrichment and a filtered bulk-file subset for volume) data into MinIO,
organized bronze/silver/gold with Iceberg (Hadoop catalog), processed with
Spark (`spark-submit`, no Operator) orchestrated by Airflow, with entity
resolution across sources, 2-3 gold-layer indicators materialized to
PostgreSQL and shown in Superset, and one bounded Spark performance
benchmark. Hard constraints: 6 ECTS (half the TFG's 12), 20 days including
the memoria (deadline computed in the epic document), ~120-140 available
hours, 50-page memoria maximum, written as living Markdown converted to
LaTeX at the end, the same way the TFG was documented.

Filed as GitHub issue `#89`; the file is named
`docs/roadmap/tfm/issues/issue-89-epic-tfm-lakehouse-platform.md` and every
cross-reference to it (this file, `docs/context/tfm/current_status.md`, and
the repository entry points) uses that name.

As each phase from the epic's "Original Plan" begins, file it as its own
numbered child issue (the real next available GitHub issue number at that
time) and add a row for it below, the same pattern the TFG used (epic `#8`
with child issues `#11`-`#17` etc.).

## Issue Status Overview

| Issue | Title | Status | Notes |
| --- | --- | --- | --- |
| `#89` | Epic: TFM lakehouse platform for curricular data integration and analysis | Planned | See `docs/roadmap/tfm/issues/issue-89-epic-tfm-lakehouse-platform.md`; scope and stack defined, implementation not started |

## Required Companion Documents

- TFG architecture (still current for the inherited pipeline):
  `docs/pipeline/cvn_pydantic_generation_pipeline.md`
- TFG limitations register: `docs/pipeline/known_limitations.md`
- TFM current state: `docs/context/tfm/current_status.md`
- TFG closed roadmap (historical): `docs/roadmap/tfg/cvn_generation_roadmap.md`
- TFG closed status log (historical): `docs/context/tfg/current_status.md`
