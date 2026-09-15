# Hotfix 10 - TFG/TFM Documentation Folder Separation

## Summary

This hotfix physically separates TFG (Trabajo de Fin de Grado) and TFM
(Trabajo de Fin de Master) documentation into distinct `tfg/`/`tfm/`
subfolders under `docs/roadmap/` and `docs/context/`, reversing the
"freeze in place, do not move" decision made in
`docs/roadmap/tfm/hotfixes/hotfix-9-tfg-completion-and-tfm-reorientation.md`.

## Trigger

The user explicitly requested that the documentation folders be separated
between TFG and TFM, judging the earlier "freeze in place, add new
siblings" approach (same directory, distinguished only by filename or a
closure banner) insufficient, and asked for every document to be checked for
resulting inconsistencies.

## Goal

- physically separate closed TFG documentation from active TFM
  documentation by folder, not just by filename or banner
- update every cross-reference across the repository to the new paths,
  leaving none broken
- correct any stale prose (not just literal paths) that no longer made sense
  once the physical layout changed
- preserve historical accuracy in hotfix-9's own narrative about its
  original "do not move" decision, rather than silently rewriting it to
  pretend that decision used today's paths

## New Layout

| Old path | New path |
| --- | --- |
| `docs/context/current_status.md` | `docs/context/tfg/current_status.md` |
| `docs/context/tfm_current_status.md` | `docs/context/tfm/current_status.md` |
| `docs/roadmap/cvn_generation_roadmap.md` | `docs/roadmap/tfg/cvn_generation_roadmap.md` |
| `docs/roadmap/tfm_roadmap.md` | `docs/roadmap/tfm/tfm_roadmap.md` |
| `docs/roadmap/issues/issue-08-...md` through `issue-71-...md` (29 files) | `docs/roadmap/tfg/issues/` (same filenames) |
| `docs/roadmap/issues/issue-89-epic-tfm-lakehouse-platform.md` | `docs/roadmap/tfm/issues/issue-89-epic-tfm-lakehouse-platform.md` |
| `docs/roadmap/hotfixes/hotfix-1-...md` through `hotfix-8-...md` (8 files) | `docs/roadmap/tfg/hotfixes/` (same filenames) |
| `docs/roadmap/hotfixes/hotfix-9-tfg-completion-and-tfm-reorientation.md` | `docs/roadmap/tfm/hotfixes/hotfix-9-tfg-completion-and-tfm-reorientation.md` |

`docs/context/project_context_index.md` was **not** moved: it is the single
shared documentation index for both projects, not TFG- or TFM-specific.
Hotfix numbering stays a single continuous sequence shared across both
folders (this is hotfix `#10`, following TFG's `#1`-`#8` and TFM's `#9`),
matching how issue numbering already works across the repository.

## Implementation Performed

- created `docs/roadmap/tfg/{issues,hotfixes}/`,
  `docs/roadmap/tfm/{issues,hotfixes}/`, `docs/context/tfg/`, and
  `docs/context/tfm/`, and `git mv`-ed every file per the table above; the
  now-empty `docs/roadmap/issues/` and `docs/roadmap/hotfixes/` directories
  were removed
- ran a repository-wide search for every old path string, then applied the
  full old-path -> new-path mapping across all Markdown files, excluding
  `docs/memoria/` (the signed/defended TFG memoria content, left untouched
  except for a small number of live-doc references inside the planning
  document `docs/memoria/estructura_memoria_tfg.md`, which does point at
  active repository files and was updated for the same reason), the
  canonical `docs/CvnXML_v1.4.3_2.1_17012025/` source package,
  `tfe_descriptions/` (unrelated reference material dropped in the working
  tree), and `initial_prompt.md` (a literal historical transcript, not a
  living document)
- beyond the mechanical path substitution, corrected several places where
  prose had gone stale because of the physical move rather than just a
  changed string:
  - `AGENTS.md`, `PROJECT_GUIDE.md`, `docs/context/project_context_index.md`,
    `CONTRIBUTING.md`: fixed reading-order and update-protocol lines that
    the mechanical substitution had collapsed onto a single (usually TFG)
    path when both a TFG and a TFM variant now exist and need to be named
    separately (e.g. "the issue document under
    `docs/roadmap/tfg/issues/`" was wrong for TFM work; it now
    distinguishes `docs/roadmap/tfm/issues/` for active TFM work from
    `docs/roadmap/tfg/issues/` for closed TFG history)
  - `docs/documentation/documentation_conventions.md`: rewrote "Roadmap And
    Execution History" and "Naming Conventions" to describe the new
    folder-based convention explicitly, instead of a filename-prefix-based
    one
  - `docs/documentation/project_contracts.md`: same correction to the
    "Required roadmap files" and reading/update contracts
  - `docs/roadmap/tfm/issues/issue-89-epic-tfm-lakehouse-platform.md`: fixed
    its own "Repository Standards" section's hotfix-folder reference and
    the illustrative naming-convention example
  - `docs/roadmap/tfm/hotfixes/hotfix-9-tfg-completion-and-tfm-reorientation.md`:
    handled separately, see "Handling Of Hotfix-9's Historical Narrative"
    below, rather than mechanically substituted like the rest

## Handling Of Hotfix-9's Historical Narrative

Hotfix-9's "Scope Decision: Freeze In Place, Add New Siblings, Do Not Move"
section explains, at length, a decision to *not* move these files, using the
paths that were real at the time. Mechanically substituting those paths to
the new locations would have made the section self-contradictory (explaining
why files were left at paths that, post-substitution, would read as already
being the new, moved-to paths). Instead:

- that one section's paths were reverted to the original, now-stale paths,
  with an explicit note at its top stating the decision was reversed and
  pointing to this hotfix
- a new "Update: Documentation Folders Separated (Superseded By Hotfix-10)"
  section was appended to hotfix-9, clarifying that every other section of
  that document (`Implementation Performed`, `Verification`, `Findings`,
  `Known Limitations`, `Impact On Future Issues`) *does* use the new,
  current paths, since those sections are simple pointers rather than
  narratives about the paths themselves

## Verification

- re-ran the repository-wide search for every old path string after all
  edits; the only remaining hits are: intentional historical mentions of the
  old epic placeholder filename (`issue-TBD-epic-tfm.md`) in
  `docs/context/tfm/current_status.md`, this hotfix, and the epic's own
  "Filename And Numbering Note"; hotfix-9's deliberately preserved
  historical "Scope Decision" section; and TFG memoria/roadmap content
  under `docs/roadmap/tfg/issues/issue-17-...md` and
  `docs/roadmap/tfg/cvn_generation_roadmap.md` referring to an unrelated,
  much older TFG placeholder epic (issue `#26`), which predates and has
  nothing to do with the TFM epic
- confirmed `docs/roadmap/issues/` and `docs/roadmap/hotfixes/` no longer
  exist as directories
- this hotfix is documentation-only; no code, generated artifacts, or tests
  were touched

## Findings

- a purely mechanical global find-and-replace was insufficient for this
  kind of structural move: several files had prose written under the
  assumption of a single flat directory (e.g. "the issue document under
  `docs/roadmap/issues/`" as a single catch-all phrase), and blindly
  substituting the directory prefix produced text that was syntactically
  valid but semantically wrong once TFG and TFM issues lived in different
  places. Each mechanically-touched file needed a manual re-read afterward.

## Known Limitations

- hotfix numbering remains a single sequence shared across the now-separate
  `tfg/hotfixes/` and `tfm/hotfixes/` folders; a reader must open both
  folders to see the full hotfix history in order
- `docs/context/project_context_index.md` still lists every individual TFG
  issue/hotfix file by its new path; as with the TFG roadmap itself, this
  list is closed and will not grow, so it was left as an enumerated list
  rather than restructured

## Impact On Future Issues

- all future TFM issue documents are filed under `docs/roadmap/tfm/issues/`,
  and all future TFM hotfix documents under `docs/roadmap/tfm/hotfixes/`
- all future TFM status-log entries go in `docs/context/tfm/current_status.md`
- the TFG folders (`docs/roadmap/tfg/`, `docs/context/tfg/`) remain closed;
  do not add new files to them

## Status

`Implemented`
