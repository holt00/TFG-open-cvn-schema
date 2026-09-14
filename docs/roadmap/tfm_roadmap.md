# TFM Roadmap

## Purpose

This is the active roadmap for the TFM (Trabajo de Fin de Master). It is the
TFM counterpart of `docs/roadmap/cvn_generation_roadmap.md`, which now holds
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
`docs/context/tfm_current_status.md`. Known limitations of that foundation are
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

**Not yet defined.** The TFM objective, scope, and technical direction have
not been agreed with the user yet. A placeholder epic record exists at
`docs/roadmap/issues/issue-TBD-epic-tfm.md` so the expected document exists
and is linked from here, but its content is intentionally left as `TBD`.

Do not invent TFM scope, objectives, or a technical plan ahead of the user
defining them. When the epic is defined:

1. fill in `docs/roadmap/issues/issue-TBD-epic-tfm.md` with the real epic
   content (Summary, Original Goal, Original Plan, Integration Checkpoints)
2. rename it to `docs/roadmap/issues/issue-<n>-epic-tfm-<slug>.md` once a real
   GitHub issue number is assigned
3. add the "Issue Status Overview" table to this file, mirroring the format
   used in `docs/roadmap/cvn_generation_roadmap.md`
4. update this file's cross-references accordingly

## Issue Status Overview

| Issue | Title | Status | Notes |
| --- | --- | --- | --- |
| `TBD` | Epic: TFM scope (placeholder) | Not defined | See `docs/roadmap/issues/issue-TBD-epic-tfm.md`; content pending the user's definition of the TFM objective |

## Required Companion Documents

- TFG architecture (still current for the inherited pipeline):
  `docs/pipeline/cvn_pydantic_generation_pipeline.md`
- TFG limitations register: `docs/pipeline/known_limitations.md`
- TFM current state: `docs/context/tfm_current_status.md`
- TFG closed roadmap (historical): `docs/roadmap/cvn_generation_roadmap.md`
- TFG closed status log (historical): `docs/context/current_status.md`
