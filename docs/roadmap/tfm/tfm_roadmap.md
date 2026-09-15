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

Every phase from the epic's "Original Plan" has been broken down and filed
as its own numbered child issue, `#90` through `#103`, the same pattern the
TFG used (epic `#8` with child issues `#11`-`#17` etc.). They are listed in
execution order below; follow that order unless there is a deliberate reason
to work out of sequence (per the Roadmap Rules above).

## Issue Status Overview

| Issue | Title | Status | Notes |
| --- | --- | --- | --- |
| `#89` | Epic: TFM lakehouse platform for curricular data integration and analysis | Planned | See `docs/roadmap/tfm/issues/issue-89-epic-tfm-lakehouse-platform.md`; scope and stack defined, implementation not started |
| `#90` | k3s cluster bring-up | Completed | `docs/roadmap/tfm/issues/issue-90-k3s-cluster-bring-up.md`; epic phase 0 |
| `#91` | Core services deployment (MinIO, PostgreSQL, Airflow) | Completed | `docs/roadmap/tfm/issues/issue-91-core-services-deployment.md`; epic phase 0; depends on `#90` |
| `#92` | Iceberg catalog on MinIO | Planned | `docs/roadmap/tfm/issues/issue-92-iceberg-catalog-on-minio.md`; epic phase 1; depends on `#91` |
| `#93` | Spark job execution from Airflow | Planned | `docs/roadmap/tfm/issues/issue-93-spark-job-execution-from-airflow.md`; epic phase 1; depends on `#90`, `#91`, `#92` |
| `#94` | ORCID API client | Planned | `docs/roadmap/tfm/issues/issue-94-orcid-api-client.md`; epic phase 2 |
| `#95` | ORCID bulk data file pipeline | Planned | `docs/roadmap/tfm/issues/issue-95-orcid-bulk-data-file-pipeline.md`; epic phase 2 |
| `#96` | Synthetic CVN generator | Planned | `docs/roadmap/tfm/issues/issue-96-synthetic-cvn-generator.md`; epic phase 2; depends on `#94`/`#95` |
| `#97` | Bronze landing & `ingest_validate` DAG | Planned | `docs/roadmap/tfm/issues/issue-97-bronze-landing-and-ingest-validate-dag.md`; epic phase 2; depends on `#90`, `#91`, `#93`, `#94`, `#95`, `#96` |
| `#98` | Bronze -> silver: validation & entity resolution | Planned | `docs/roadmap/tfm/issues/issue-98-bronze-to-silver-validation-and-entity-resolution.md`; epic phase 3; depends on `#92`, `#93`, `#97` |
| `#99` | Silver -> gold: indicators & `transform_publish` DAG | Planned | `docs/roadmap/tfm/issues/issue-99-silver-to-gold-indicators-and-transform-publish-dag.md`; epic phase 3; depends on `#98` |
| `#100` | Superset dashboard | Planned | `docs/roadmap/tfm/issues/issue-100-superset-dashboard.md`; epic phase 4; depends on `#91`, `#99` |
| `#101` | Spark performance benchmark | Planned | `docs/roadmap/tfm/issues/issue-101-spark-performance-benchmark.md`; epic phase 4; depends on `#98` |
| `#102` | Hardening | Planned | `docs/roadmap/tfm/issues/issue-102-hardening.md`; epic phase 5; depends on `#90`-`#101` |
| `#103` | Memoria assembly | Planned | `docs/roadmap/tfm/issues/issue-103-memoria-assembly.md`; epic phase 6; closing issue |

## Required Companion Documents

- TFG architecture (still current for the inherited pipeline):
  `docs/pipeline/cvn_pydantic_generation_pipeline.md`
- TFG limitations register: `docs/pipeline/known_limitations.md`
- TFM current state: `docs/context/tfm/current_status.md`
- TFG closed roadmap (historical): `docs/roadmap/tfg/cvn_generation_roadmap.md`
- TFG closed status log (historical): `docs/context/tfg/current_status.md`
