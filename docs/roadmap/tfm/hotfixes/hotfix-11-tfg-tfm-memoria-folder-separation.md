# Hotfix 11 - TFG/TFM Memoria Folder Separation

## Summary

This hotfix physically separates the TFG (Trabajo de Fin de Grado) memoria
content from the TFM (Trabajo de Fin de Master) memoria planning inside
`docs/memoria/`, moving the former into `docs/memoria/TFG/` and creating
`docs/memoria/TFM/` for the latter, following the same separation pattern
hotfix-10 already applied to `docs/roadmap/` and `docs/context/`.

## Trigger

The user asked explicitly for the TFG memoria to be moved into its own
`docs/memoria/TFG/` subfolder and for a new `docs/memoria/TFM/` subfolder to
be created to hold TFM memoria planning material, then requested that
per-chapter Markdown guide files (main ideas, meant to be referenced and
expanded in place later) be started inside `docs/memoria/TFM/`, using the
newly available `docs/research/tfm/estado_del_arte_tfm.md` state-of-the-art
document as input.

## New Layout

| Old path | New path |
| --- | --- |
| `docs/memoria/estructura_memoria_tfg.md` | `docs/memoria/TFG/estructura_memoria_tfg.md` |
| `docs/memoria/TFG.tex`, `TFG.pdf`, `TFG_signed.pdf`, `TFG.{aux,bbl,blg,loalgorithm,locode,lof,lot,out,toc}` | `docs/memoria/TFG/` (same filenames) |
| `docs/memoria/Léeme.txt` | `docs/memoria/TFG/Léeme.txt` |
| `docs/memoria/bib/`, `chapters/`, `elements/`, `figs/`, `include/` | `docs/memoria/TFG/bib/`, etc. |
| (new) | `docs/memoria/TFM/` -- per-chapter Markdown planning guides for the TFM memoria |

`TFG.pdf` and `TFG_signed.pdf` are gitignored (kept out of git history
deliberately, per the existing `.gitignore` comment); they were moved with a
plain filesystem rename, not `git mv`, and `.gitignore`'s two entries were
updated to the new paths. `Léeme.txt` is untracked (never committed) and was
also moved with a plain rename. Everything else under the old
`docs/memoria/` was tracked and moved with `git mv` to preserve history.

## Implementation Performed

- created `docs/memoria/TFG/` and moved every existing file/directory under
  the old `docs/memoria/` into it (see table above)
- updated `.gitignore`'s two `docs/memoria/TFG*.pdf` entries to
  `docs/memoria/TFG/TFG*.pdf`
- updated every **live, forward-looking** cross-reference across the
  repository to the new `docs/memoria/TFG/...` path: `AGENTS.md`,
  `PROJECT_GUIDE.md`, `README.md`, `docs/context/project_context_index.md`,
  `docs/context/tfm/current_status.md` (only the "what the TFG delivered"
  list item, a live description, not the historical hotfix-9 summary entry
  further down that same file), `docs/roadmap/tfm/tfm_roadmap.md`,
  `docs/roadmap/tfm/issues/issue-89-epic-tfm-lakehouse-platform.md` (also
  updated its now-resolved "a TFM-equivalent structure document should be
  created... decide its exact location at that time" note to state the
  decision actually made), `docs/roadmap/tfm/issues/issue-103-memoria-assembly.md`
  (same resolved-decision update), and `docs/research/tfm/estado_del_arte_tfm.md`
- added forward pointers to the new `docs/memoria/TFM/` folder alongside
  each updated TFG memoria pointer, in the same files, so a reader lands on
  both halves of the split from any entry point
- created `docs/memoria/TFM/` with one Markdown guide file per planned TFM
  memoria chapter (objective, recommended content, recommended elements,
  learning outcomes covered -- the same shape `estructura_memoria_tfg.md`
  used per chapter, but as separate files instead of one combined tracking
  document, at the user's explicit request), grounded in the TFM epic's
  "Learning Outcomes Targeted" table, the actual issue-by-issue record in
  `docs/context/tfm/current_status.md`, and `docs/research/tfm/estado_del_arte_tfm.md`
  as the primary state-of-the-art source; an index file lists the proposed
  chapter table and the redaction principles carried over from the TFG

## Handling Of `estructura_memoria_tfg.md`'s Internal Historical Paths

Unlike hotfix-10's move, this document (now at
`docs/memoria/TFG/estructura_memoria_tfg.md`) is itself part of the closed,
signed-and-defended TFG record: its own top banner already states it "no
debe modificarse salvo para corregir una errata puntual detectada despues
del cierre." It contains roughly fifty internal mentions of
`docs/memoria/...` paths (the chapter-file table, and, more numerously,
narrative build-log entries such as "la compilacion ... genera
`docs/memoria/TFG.pdf` con 63 paginas" recorded at each past revision).
These were **not** rewritten to the new `docs/memoria/TFG/...` paths: they
accurately describe the directory layout that was real at each historical
point they narrate, and rewriting them would misrepresent that history the
same way hotfix-10 avoided rewriting hotfix-9's "Scope Decision" section.
Instead, a short "Nota de reubicacion" paragraph was added directly under
the existing closure banner, stating the file moved and that its internal
`docs/memoria/...` mentions describe the pre-move layout. The TFG chapter
`.tex` sources themselves (already compiled into the signed PDF) were moved
but their content was not touched for the same reason: the signed PDF is a
fixed artifact and its LaTeX source should not silently diverge from it.

## Verification

- `find docs/memoria -maxdepth 2` confirms only `TFG/` and `TFM/` exist
  directly under `docs/memoria/`, with all expected files present in `TFG/`
- re-ran a repository-wide search for the old `docs/memoria/` path (without
  a following `TFG/` or `TFM/`) outside `docs/memoria/TFG/` itself; the only
  remaining hits are the deliberately preserved historical narrative inside
  `docs/memoria/TFG/estructura_memoria_tfg.md` (see above) and the frozen
  TFG-closed documents this repository's own rules forbid editing except for
  a factual erratum (`docs/context/tfg/current_status.md`,
  `docs/roadmap/tfg/issues/issue-71-...md`, and hotfixes `#9`/`#10`, all of
  which narrate a past state under the old layout and remain historically
  accurate as written)
- this hotfix is documentation/file-layout only; no LaTeX chapter content,
  code, generated artifacts, or tests were touched

## Findings

- the university-template `Léeme.txt` file (accented filename) had never
  actually been committed to git, despite living inside the tracked
  `docs/memoria/` directory since the TFG; discovered only because `git mv`
  refused it as an untracked path
- the same filename also turned out to store its accented character in NFD
  (decomposed, `e` + combining acute accent U+0301) rather than NFC
  (precomposed `é`), which silently broke a naive shell-glob/substring match
  on the visually identical string; resolved by reading the exact codepoints
  with Python and renaming by that exact value instead of retyping the
  character

## Known Limitations

- hotfix numbering remains a single sequence shared across `tfg/hotfixes/`
  and `tfm/hotfixes/`, unchanged by this hotfix
- `docs/memoria/TFG/estructura_memoria_tfg.md` now contains internal path
  mentions that no longer match the file's own current location (see
  "Handling Of `estructura_memoria_tfg.md`'s Internal Historical Paths"
  above); this is intentional, not an oversight

## Impact On Future Issues

- issue `#103` (memoria assembly) now has `docs/memoria/TFM/` ready with
  per-chapter planning guides to draft from directly, instead of having to
  create that structure from scratch at assembly time
- any future reference to the TFG memoria's location must use
  `docs/memoria/TFG/`, not `docs/memoria/`

## Status

`Implemented`
