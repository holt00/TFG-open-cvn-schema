# Issue TBD - Epic: TFM Scope (Placeholder)

## Filename And Numbering Note

This document intentionally uses `TBD` instead of a real issue number. The
TFM (Trabajo de Fin de Master) objective has not been defined by the user
yet, so no GitHub issue has been filed for it. This is a deliberate, recorded
deviation from the repository's normal issue-file naming convention
(`docs/roadmap/issues/issue-<number>-<slug>.md`, see
`docs/documentation/documentation_conventions.md`). Once the TFM objective is
agreed and a real GitHub issue is filed, this file must be renamed to
`docs/roadmap/issues/issue-<n>-epic-tfm-<slug>.md` and every cross-reference
to this filename (currently in `docs/roadmap/tfm_roadmap.md`,
`docs/context/tfm_current_status.md`, and the repository entry-point files)
must be updated to match.

## Summary

This is the placeholder umbrella epic for the TFM. It exists only so that the
expected epic document is present and linked from `docs/roadmap/tfm_roadmap.md`
and the repository entry points; it carries no defined scope yet.

## Relationship To The TFG

The TFM is not a new, independent project. It is built directly on top of the
TFG (Trabajo de Fin de Grado) work already completed in this repository
(issues `#11` through `#71`, all `Completed`; full record in
`docs/roadmap/cvn_generation_roadmap.md` and
`docs/context/current_status.md`).

For a reader who has not read the TFG documentation, in one paragraph: the
TFG took the official Spanish CVN (Curriculum Vitae Normalizado) XML/XSD
package and built, layer by layer, (1) reproducible structural Pydantic
bindings generated straight from the official schemas, (2) a normalization
layer that cross-indexes every field by CVN code and resolves it against
auxiliary reference catalogs, (3) a semantic policy layer that turns that
normalized evidence into deterministic typing and naming decisions, (4) a
domain model generator that emits the final, hand-consumable Pydantic models,
(5) an agnostic conceptual model layer used to generate UML-like diagrams and
a JSON Schema, (6) a canonical "Open CVN JSON" document format with a unified
parser/validator contract supporting PDF, XML, and JSON import, and (7) a
local CLI application on top of all of that, with SQLite storage, versioned
curricula, LaTeX/PDF export, and an opt-in LLM-assisted import fallback. That
entire stack is documented in detail in
`docs/pipeline/cvn_pydantic_generation_pipeline.md`,
`docs/pipeline/parser_validator_contract.md`, and
`docs/development/application_mvp_workflow.md`, and is condensed again in
`docs/context/tfm_current_status.md`.

Whatever the TFM ends up doing, it should be planned as an extension of that
existing foundation, and should read `docs/pipeline/known_limitations.md`
before assuming a gap is undiscovered.

## Original Goal

TBD. To be defined together with the user before any TFM implementation
begins.

## Original Plan

TBD.

## Adjustments Made During Implementation

Not applicable yet; no implementation has started.

## Implementation Performed

Not applicable yet; no implementation has started.

## Verification

Not applicable yet; no implementation has started.

## Findings

Not applicable yet.

## Known Limitations

Not applicable yet. Once TFM work begins, inherited TFG limitations remain
tracked in `docs/pipeline/known_limitations.md` and are not repeated here
unless the TFM's own work introduces new ones.

## Impact On Future Issues

TBD, once the epic and its child issues are defined.

## Status

`Placeholder` - do not treat as planned or started work. Do not invent scope
for this epic; wait for the user to define the TFM objective.
