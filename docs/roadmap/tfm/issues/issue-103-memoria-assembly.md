# Issue 103 - Memoria Assembly

## Summary

Convert the running Markdown log kept throughout the TFM into the final
LaTeX memoria, capped at 50 pages. TFM epic phase 6, and the final issue of
the TFM.

## Original Goal

A complete, defensible TFM memoria, written the same way the TFG's was:
living documentation converted to LaTeX at the end, not drafted from
scratch in a separate late-stage phase.

## Original Plan

- a dedicated state-of-the-art and technology-justification research
  document has been prepared ahead of drafting, as direct input for this
  issue's "Estado del arte" chapter:
  `docs/research/tfm/estado_del_arte_tfm.md`. It extends the epic's (`#89`)
  "Technology Stack Decision Record" table with the comparative rationale a
  state-of-the-art chapter needs against real ecosystem alternatives
  (data warehouse/lake/lakehouse; Iceberg vs Delta Lake vs Hudi; Hadoop vs
  Hive Metastore/REST/Nessie catalogs; MinIO vs HDFS vs cloud-native object
  storage; Kubernetes/k3s vs Docker Swarm; Spark vs Flink/Dask/Ray and the
  Spark Kubernetes Operator; Airflow vs Prefect/Dagster/Luigi; Trino vs Spark
  SQL; Superset vs Metabase/Grafana/proprietary BI; deterministic vs
  probabilistic/ML entity resolution; ORCID/CRIS ecosystem context for the
  synthetic-CVN decision), plus a reference list ready to convert into the
  memoria's bibliography. Use it as the primary source for that chapter
  instead of reconstructing the comparison from memory
- a TFM memoria structure, the TFM equivalent of
  `docs/memoria/TFG/estructura_memoria_tfg.md`, has been started ahead of
  drafting: `docs/memoria/TFM/` holds one Markdown guide file per planned
  chapter (objective, recommended content, recommended elements, learning
  outcomes covered), each meant to be edited in place as drafting
  progresses, the same role `estructura_memoria_tfg.md` played for the TFG
  but split per chapter instead of one combined tracking file. The TFG's own
  memoria content was moved to `docs/memoria/TFG/` at the same time
  (consistent with the `docs/roadmap`/`docs/context` tfg/tfm folder
  separation already in place); see `docs/roadmap/tfm/hotfixes/` for the
  record of that move
- draft chapters from the accumulated record in this issue and its sibling
  issues' `Implementation Performed`/`Findings`/`Verification` sections and
  `docs/context/tfm/current_status.md`, following the TFG's chapter
  structure adapted to the smaller TFM scope
- ensure every one of the six learning outcomes (`CN02`, `HA01`, `HA02`,
  `HA03`, `CP01`, `CP04`, see the epic's "Learning Outcomes Targeted" table)
  has concrete evidence cited in the text
- final review pass against the 50-page cap

## Adjustments Made During Implementation

- **Chapter count and structure changed from a literal copy of the TFG's eight
  chapters to seven, merged differently**, once the actual content was mapped
  out: the TFG dedicates whole chapters to defining CVN and the Open CVN
  format because that definition is its own contribution; the TFM does not
  redefine either, it consumes them as an already-closed TFG deliverable. That
  gap is filled instead with chapters the TFG has no equivalent for
  (infrastructure/cluster bring-up, multi-source ingestion/fusion,
  distributed transformation). The TFG's separate "Antecedentes" and
  "Analisis del ecosistema" chapters are merged into one "Estado del arte y
  decisiones arquitectonicas" chapter, and its separate "Evaluacion" and
  (nonexistent, TFM-only) "Endurecimiento" material are merged into one
  "Visualizacion, evaluacion de rendimiento y endurecimiento" chapter, both
  proportional to the TFM's smaller page/ECTS budget (7 chapters vs 8, roughly
  half the scope for half the credits)
- **the TFM structure/tracking document is split one file per chapter**,
  unlike the TFG's single combined `estructura_memoria_tfg.md`, at the user's
  explicit request, so each chapter's guide and its future in-place drafting
  notes live together in one file instead of one chapter's update touching a
  shared document

## Implementation Performed

Preparatory work (folder structure and per-chapter planning guides), followed
by the first chapter of actual LaTeX drafting.

- **branch `issue-103-memoria-assembly` created** off `issue-102-hardening`
  (which still carries every prior TFM implementation commit, `#90`-`#102`,
  not yet merged to `main`), to keep the memoria-drafting work isolated from
  further implementation work
- **Chapter 1 ("Introducción, motivación y objetivos") drafted** in
  `docs/memoria/TFM/chapters/ch1.tex`, replacing the official template's
  placeholder (`lipsum`) content: contains the context/continuity-with-the-
  TFG section, the problem statement and motivation, the general objective
  and nine specific objectives with a chapter-correspondence table, the
  CVN-synthetic-vs-ORCID-real ethics/privacy note, the six-learning-outcome-
  to-chapter table, and the document-structure summary. Styled using
  `.claude/skills/tfg-mapi-style`, itself analysed against
  `docs/memoria/TFG/chapters/ch1.tex` for register, paragraph structure and
  recurring LaTeX/connector patterns before drafting
- **academic-constraints section removed from chapter 1, by explicit user
  request**: the memoria text must not mention ECTS credits, the project's
  day/hour budget, or the document's page cap -- those are project-
  management conditions, not academic argumentation, and citing them reads
  as the memoria explaining its own writing instructions rather than the
  system built. The same request identified that this removed section was
  also where the single-local-node-vs-real-cloud-cluster deployment
  decision got its (now wrong) justification; that decision still needs
  justifying, moved to chapter 2, and reframed on its own technical merits
  (a local machine avoids the cost of keeping cloud infrastructure running
  while the system is still under active development, and the same
  Helm-based deployment is directly replicable onto a real cloud cluster
  later), not on time pressure. Tracked as a drafting note in
  `docs/memoria/TFM/ch2_estado_del_arte_y_decisiones.md`
- **template personalised**: `docs/memoria/TFM/include/opciones.tex` (author,
  epic `#89`'s provisional title, master's programme name, date) and
  `docs/memoria/TFM/elements/portada.tex` (programme name) filled in;
  `docs/memoria/TFM/bib/ref.bib`'s leftover template demo entries (`RUSSELL`,
  `AlphaZero`) replaced with a real citation to the closed TFG memoria;
  `docs/memoria/TFM/TFM.tex`'s `\input` list rewritten from the template's
  tutorial chapters ("Algunos elementos", "Marcas y ayudas") to the real
  seven-chapter list, chapter 1 active and chapters 2-7 commented out
  pending, the same incremental pattern the TFG's own `TFG.tex` followed
- director/codirector names in `opciones.tex` intentionally left as
  placeholders marked `TODO`, not guessed, pending confirmation by the user

- **`docs/memoria/` split into `TFG/` and `TFM/`** (recorded in full, with its
  own rationale, in `docs/roadmap/tfm/hotfixes/hotfix-11-tfg-tfm-memoria-folder-separation.md`):
  every existing TFG memoria file (`estructura_memoria_tfg.md`, `TFG.tex` and
  its build artifacts, both PDFs, `bib/`, `chapters/`, `elements/`, `figs/`,
  `include/`) moved into `docs/memoria/TFG/` with `git mv` (or a plain
  filesystem rename for the two gitignored PDFs and the never-committed
  `Léeme.txt`); `.gitignore`'s two PDF entries updated to match
- **`docs/memoria/TFM/` created** with:
  - `estructura_memoria_tfg.md`'s TFM equivalent, `estructura_memoria_tfm.md`:
    purpose, how it relates to the rest of the living documentation (points at
    `current_status.md`, `tfm_roadmap.md`, the epic, the state-of-the-art
    document, `tfm_lakehouse_workflow.md`, `known_limitations.md`, and each
    source issue as the primary source of citable figures, not this guide
    itself), redaction principles inherited from the TFG plus TFM-specific
    notes (different programme/learning outcomes, no CVN/Open CVN
    redefinition, tighter page budget, real operational findings expected),
    the 7-chapter table with per-chapter status, a chapter-to-issue-and-
    research-section correspondence table, and a chapter-to-learning-outcome
    correspondence table
  - one guide file per chapter (`ch1_introduccion.md` through
    `ch7_conclusiones.md`), each with: objective, recommended content (the
    concrete ideas to cover, grounded in the actual issues `#89`-`#102` and
    `docs/research/tfm/estado_del_arte_tfm.md`, not generic chapter
    boilerplate), recommended elements (tables/diagrams/figures), learning
    outcomes covered, primary sources, and a "drafting status" section left
    empty for future in-place updates as redaction actually happens (the same
    role `estructura_memoria_tfg.md`'s per-chapter prose played for the TFG,
    but one file per chapter instead of one shared file)
- **every live, forward-looking cross-reference to the old bare
  `docs/memoria/...` path updated** across the repository: `AGENTS.md`,
  `PROJECT_GUIDE.md`, `README.md`, `docs/context/project_context_index.md`,
  `docs/context/tfm/current_status.md` (only its live "what the TFG
  delivered" list item, not the historical hotfix-9 summary entry further
  down that file), `docs/roadmap/tfm/tfm_roadmap.md`, this issue's own
  "Original Plan" (the "decide its exact location at implementation time"
  note updated to state the decision actually made), the epic
  (`issue-89-...md`, same kind of resolved-decision update), and
  `docs/research/tfm/estado_del_arte_tfm.md`'s own bibliography-section
  reference to `estructura_memoria_tfg.md`
- **`hotfix-11` filed** documenting the move, its rationale, and the explicit
  decision to leave `estructura_memoria_tfg.md`'s roughly fifty internal
  historical path mentions (e.g. "la compilacion ... genera
  `docs/memoria/TFG.pdf` con 63 paginas", narrating a past revision)
  unrewritten, since that document is itself part of the closed, signed TFG
  record and rewriting them would misrepresent the directory layout that was
  real at each point they narrate -- the same principle hotfix-10 already
  applied to hotfix-9's own historical narrative. A short relocation note was
  added directly under that document's existing closure banner instead.
  `AGENTS.md`/`PROJECT_GUIDE.md`'s hotfix listings were also backfilled with
  a missing `hotfix-10` entry (a pre-existing gap, unrelated to this issue,
  fixed in passing since it sits directly next to the new `hotfix-11` entry)

## Verification

- `find docs/memoria -maxdepth 2` confirms only `TFG/` and `TFM/` exist under
  `docs/memoria/`, with every expected TFG file present under `TFG/` and all
  8 new TFM files present under `TFM/`
- a repository-wide search for the old bare `docs/memoria/` path (not
  followed by `TFG/` or `TFM/`) outside `docs/memoria/TFG/` itself returns
  only the deliberately preserved historical/frozen files: the TFG's own
  `estructura_memoria_tfg.md` (now inside `docs/memoria/TFG/`, its internal
  narrative left as-is per the finding above), the signed chapter source
  `anexo_d.tex`, `docs/context/tfg/current_status.md`,
  `docs/roadmap/tfg/issues/issue-71-...md`, and hotfixes `#9`/`#10` -- exactly
  the closed-TFG documents this repository's own rules forbid editing except
  for a factual erratum
- the memoria itself has not been drafted or compiled; the 50-page-cap and
  citation-completeness verification in the "Planned" note below remains
  entirely outstanding

Planned, not yet executed: the memoria compiles cleanly (no undefined
references or citations), is at or under 50 pages, and every learning
outcome has a traceable citation.

## Findings

- the university-template `Léeme.txt` file living inside `docs/memoria/`
  since the TFG had never actually been committed to git, discovered only
  because `git mv` refused it as an untracked path
- that same filename stores its accented character in NFD (decomposed form,
  `e` + a combining acute accent, U+0301) rather than the more common
  precomposed NFC form, which silently broke a shell-glob/substring match on
  the visually identical string; resolved by reading the exact Unicode
  codepoints with Python and renaming by that exact value
- a stray `PLANTILLA TFM_ESP.zip` and a `.claude/skills/tfg-mapi-style/`
  skill directory were noticed as untracked files in the repository during
  this work; neither was created by this issue's work and neither was
  touched, staged, or committed -- flagged to the user rather than acted on

## Known Limitations

- `docs/memoria/TFG/estructura_memoria_tfg.md` now contains internal path
  mentions (`docs/memoria/TFG.tex`, `docs/memoria/chapters/ch1.tex`, etc.)
  that no longer match the file's own current location under
  `docs/memoria/TFG/`; this is intentional (see Adjustments, above), not an
  oversight, and is called out in a note directly under that file's own
  closure banner
- the per-chapter TFM guide files' recommended content is this issue's own
  best synthesis of the accumulated record, not yet cross-checked
  figure-by-figure against the live repository the way each source issue's
  own `Implementation Performed` section was; every concrete number the
  actual chapters cite must still be re-verified against the repository at
  drafting time, per this repository's own standing rule (see the TFG's
  `estructura_memoria_tfg.md` for precedent)

## Impact On Future Issues

None; this is the closing issue of the TFM. The per-chapter guide files
under `docs/memoria/TFM/` are this issue's own remaining work, to be edited
in place (not superseded by a new document) as drafting continues.

## Status

`In Progress` -- the folder split and the seven per-chapter planning guides
are done; chapter 1 of the LaTeX memoria is drafted; chapters 2-7 remain to
be written incrementally, one at a time, on `issue-103-memoria-assembly`.
