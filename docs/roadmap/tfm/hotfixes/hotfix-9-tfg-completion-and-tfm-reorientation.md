# Hotfix 9 - TFG Completion And TFM Reorientation

## Summary

This hotfix records the repository reorientation performed when the TFG
(Trabajo de Fin de Grado) was confirmed complete and work began on the TFM
(Trabajo de Fin de Master), which is built on top of it in the same
repository.

## Trigger

The TFG memoria was finished, signed, and defended
(`docs/memoria/TFG.pdf`, `docs/memoria/TFG_signed.pdf`,
`docs/defensa/presentacion_tfg.pdf`/`.pptx`), and the user requested that the
repository clearly separate the finished TFG from the starting TFM: mark all
prior work as finished, reorient the project status toward the TFM, and
document how the TFG foundation works so the TFM can build on it.

## Goal

- close out the TFG's own tracking documents so they accurately reflect that
  the work is finished, not still in progress
- give the TFM its own active status log and roadmap, without breaking the
  large number of existing cross-references into the TFG's documents
- update every repository entry-point document (the files every new session
  is required to read first) to explain the TFG foundation and point toward
  the TFM as the active work
- leave the TFM's actual scope undefined, since it has not been agreed with
  the user yet

## Scope Decision: Freeze In Place, Add New Siblings, Do Not Move

**This decision was reversed by hotfix-10** (see
`docs/roadmap/tfm/hotfixes/hotfix-10-tfg-tfm-documentation-folder-separation.md`),
which physically separated TFG and TFM documentation into `docs/roadmap/tfg/`
and `docs/roadmap/tfm/` subfolders. The paths quoted below are the ones that
were actually true at the time this hotfix was written and decided against
moving; they are intentionally left unchanged here for historical accuracy,
even though they no longer resolve. See hotfix-10 for the current layout.

Before making changes, a repository-wide search was run for references to
`docs/context/current_status.md`, `docs/roadmap/cvn_generation_roadmap.md`,
and the `docs/roadmap/issues/*.md` / `docs/roadmap/hotfixes/*.md` paths. Both
core files are referenced from roughly 30-40 other documents each: every TFG
issue and hotfix record, both documentation-contract files
(`docs/documentation/documentation_conventions.md`,
`docs/documentation/project_contracts.md`), and all repository entry points.

Moving or renaming those files (for example into a `tfg/` subfolder) would
have required rewriting cross-references across dozens of historical,
already-closed documents for no functional benefit, and would risk silently
breaking a reference in one of them. Instead, this hotfix:

- leaves `docs/context/current_status.md`,
  `docs/roadmap/cvn_generation_roadmap.md`,
  `docs/roadmap/issues/*.md` (issues `#8` through `#71`), and
  `docs/roadmap/hotfixes/*.md` (hotfixes `#1` through `#8`) at their existing
  paths, untouched in content except for an explicit closure banner added at
  the top of the two roadmap/status files
- adds new, separate active files for the TFM instead of repurposing the TFG
  ones: `docs/context/tfm_current_status.md` and
  `docs/roadmap/tfm_roadmap.md`
- adds a placeholder epic at `docs/roadmap/issues/issue-TBD-epic-tfm.md`,
  using `TBD` instead of a number since no TFM epic has been filed as a real
  GitHub issue yet (documented as a deliberate naming-convention deviation
  inside that file itself)

## Implementation Performed

- confirmed the TFG defense materials were up to date and committed them
  (`docs/defensa/presentacion_tfg.pdf`/`.pptx`), removing the stray
  `~$presentacion_tfg.pptx` PowerPoint lock file
- tagged the resulting commit `tfg-final` as a permanent reference point for
  the exact finished-TFG repository state
- corrected `docs/memoria/estructura_memoria_tfg.md`: all eight chapter
  `Estado: EN_PROCESO` markers, stale since before the memoria was signed and
  defended, were updated to `Estado: COMPLETADO`, and a closure banner was
  added at the top of the document pointing forward to the TFM planning
  documents
- added a closure banner to the top of `docs/context/tfg/current_status.md`
  (retitled `# Current Status (TFG, Closed)`) and
  `docs/roadmap/tfg/cvn_generation_roadmap.md` (retitled
  `# CVN Generation Roadmap (TFG, Closed)`), explaining that the file is
  frozen, why it was not moved, and where the active TFM equivalent lives
- created `docs/context/tfm/current_status.md`: the new active status log,
  including a "What The TFG Delivered" section that explains, for a reader
  who has not read the TFG documentation, how the inherited pipeline and
  application actually work, so future TFM sessions do not have to
  reconstruct that from the full TFG log
- created `docs/roadmap/tfm/tfm_roadmap.md`: the new active roadmap, carrying
  forward the same roadmap rules as the TFG roadmap, explicitly stating the
  epic is not yet defined, and explaining how to promote the placeholder epic
  once it is
- created `docs/roadmap/tfm/issues/issue-89-epic-tfm-lakehouse-platform.md`: the placeholder epic,
  with all standard issue-document sections present but marked `TBD` or "not
  applicable yet" per the mandatory section list in
  `docs/documentation/documentation_conventions.md`, plus a
  "Relationship To The TFG" section explaining the inherited architecture
- updated the repository entry-point and documentation-contract files to
  describe the TFG foundation and repoint the mandatory reading order at the
  TFM files: `README.md`, `PROJECT_GUIDE.md`, `AGENTS.md`, `CONTRIBUTING.md`,
  `docs/context/project_context_index.md`,
  `docs/documentation/documentation_conventions.md`,
  `docs/documentation/project_contracts.md`

## Verification

- re-ran the repository-wide search for references to the frozen TFG paths
  after the edits to confirm no existing issue, hotfix, or contract document
  needed a path change (all of them remained valid because the TFG files were
  not moved)
- manually reviewed the updated entry-point files for a consistent reading
  order: `AGENTS.md` -> `PROJECT_GUIDE.md` ->
  `docs/context/project_context_index.md` ->
  `docs/context/tfm/current_status.md` -> the relevant TFM issue document,
  with the TFG documents explicitly kept as background/foundation reading
  rather than removed
- this hotfix is documentation-only; no code, generated artifacts, or tests
  were touched, so the existing `uv run pytest -n auto tests` baseline is
  unaffected

## Findings

- `docs/memoria/estructura_memoria_tfg.md` had drifted from the actual
  project state: it still marked every chapter `EN_PROCESO` even though the
  memoria had already been signed and defended in later commits
  (`fd5ae4a tfg signed`, `6b45ff7 defensa`). Tracking documents like this one
  need an explicit closing pass at project-completion time, not just at
  chapter-completion time.

## Known Limitations

- the TFM epic is intentionally left undefined; `docs/roadmap/tfm/tfm_roadmap.md`
  and `docs/roadmap/tfm/issues/issue-89-epic-tfm-lakehouse-platform.md` have no real scope yet and
  must not be treated as a plan
- because the TFG roadmap/status files were frozen in place rather than
  moved, the repository now has two parallel "current status" files
  (`docs/context/tfg/current_status.md` and `docs/context/tfm/current_status.md`)
  and two parallel roadmap files
  (`docs/roadmap/tfg/cvn_generation_roadmap.md` and
  `docs/roadmap/tfm/tfm_roadmap.md`). Every entry-point document was updated to
  make explicit which one is active, but any future documentation edit must
  keep pointing at the TFM files, not silently drift back to updating the
  closed TFG ones

## Impact On Future Issues

- once the TFM objective is defined, `docs/roadmap/tfm/issues/issue-89-epic-tfm-lakehouse-platform.md`
  must be filled in and renamed to a real numbered issue file, and
  `docs/roadmap/tfm/tfm_roadmap.md`'s "Issue Status Overview" table must be
  populated the same way `docs/roadmap/tfg/cvn_generation_roadmap.md` was
  throughout the TFG
- all future TFM issue and hotfix documents should be added directly under
  `docs/roadmap/tfg/issues/` and `docs/roadmap/tfg/hotfixes/` alongside the existing
  TFG ones (no separate subfolder), following the existing TFG naming
  convention with issue numbers continuing from wherever GitHub assigns them
- the "Documentation Update Protocol" in `AGENTS.md`,
  `docs/documentation/documentation_conventions.md`, and
  `docs/documentation/project_contracts.md` now names
  `docs/context/tfm/current_status.md` and `docs/roadmap/tfm/tfm_roadmap.md` as
  the files to update after TFM work; the TFG equivalents should not receive
  new entries

## Update: Epic Defined And Numbered

Two things this hotfix originally left open have since happened, in later
work on the same branch, and are noted here rather than silently rewriting
the narrative above:

- the TFM epic's scope, technology stack, data strategy, phased plan, and
  applicable standards were defined with the user (see
  `docs/roadmap/tfm/issues/issue-89-epic-tfm-lakehouse-platform.md`)
- that epic was filed as GitHub issue `#89`, and the file (originally
  `issue-TBD-epic-tfm.md`) was renamed to
  `issue-89-epic-tfm-lakehouse-platform.md`, with every cross-reference to it
  updated across the repository

References above to the epic as a scope-less "placeholder" reflect this
hotfix's state at the time it was written, not the current state.

## Update: Documentation Folders Separated (Superseded By Hotfix-10)

The "freeze in place, do not move" decision in "Scope Decision" above was
later reversed at the user's explicit request.
`docs/roadmap/tfm/hotfixes/hotfix-10-tfg-tfm-documentation-folder-separation.md`
physically separated TFG and TFM documentation into `docs/roadmap/tfg/` and
`docs/roadmap/tfm/` (and `docs/context/tfg/` / `docs/context/tfm/`)
subfolders, updating every cross-reference across the repository, including
the ones elsewhere in this hotfix's own "Implementation Performed",
"Verification", "Findings", "Known Limitations", and "Impact On Future
Issues" sections below, which now use the current post-separation paths.
Only the "Scope Decision" section above was deliberately left with its
original, now-stale paths, since accurately explaining that decision
requires the paths that were true when it was made. See hotfix-10 for the
full rationale and the complete new layout.

## Status

`Implemented`
