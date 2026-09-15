# Current Status (TFM)

## Purpose

This file is the active implementation log for the TFM (Trabajo de Fin de
Master). It is the TFM counterpart of `docs/context/tfg/current_status.md`, which
now holds the complete, closed TFG (Trabajo de Fin de Grado) log and is no
longer updated. Read this file, not the TFG one, to find the current state of
the project.

## How The TFM Relates To The TFG

The TFM builds on top of the finished TFG rather than starting over. Nothing
described in the TFG documentation below is being redone; the TFM extends it.

### What The TFG Delivered

The TFG (issues `#11` through `#71`, roadmap in
`docs/roadmap/tfg/cvn_generation_roadmap.md`, full log in
`docs/context/tfg/current_status.md`) delivered, in this repository:

1. **Structural generation layer**: reproducible Pydantic bindings generated
   with `xsdata` from the official CVN XML/XSD package (`CVN.xsd`,
   `SpecificationManual.xsd`, `CVNTreeModel_v1.0.xsd`, and the auxiliary
   `ReferenceTables`, `Subtypes`, `Entity`, `Thesaurus` families), under
   `src/generated/`, driven by `src/cvn_codegen/xsdata_runner.py`. This layer
   is never edited by hand and is fully reproducible from canonical source
   inputs.
2. **Normalization layer**: `src/cvn_codegen/normalization.py` and related
   modules parse `SpecificationManual.xml` and `CVNTreeModel.xml`, cross-index
   every CVN field by its `code`, and resolve manual reference-table mentions
   against the auxiliary catalog families, producing typed
   `NormalizedCodeEntry` records with full source traceability.
3. **Semantic policy layer**: `src/cvn_codegen/semantic_policy.py` maps
   normalized metadata to deterministic domain-modeling decisions (types,
   naming, strict-enum eligibility, wrapper treatment, overrides), evidence-
   backed rather than hardcoded per table.
4. **Domain model generation**: `src/cvn_codegen/domain_model_generator.py`
   emits the final hand-consumable Pydantic domain models under
   `src/models/cvn/generated/` (105 generated files as of TFG closure), plus
   shared components in `src/models/cvn/components.py`.
5. **Conceptual model layer and diagrams**: an agnostic conceptual
   intermediate representation (`src/cvn_codegen/conceptual_model_extractor.py`)
   decoupled from generated Python class names, rendered as PlantUML diagrams
   under `docs/diagrams/`.
6. **JSON Schema and the canonical Open CVN JSON format**: a generated JSON
   Schema Draft 2020-12 artifact (`schemas/open_cvn.schema.json`) and the
   canonical Open CVN JSON document shape (`schema_version`, `metadata`,
   `curriculum`, `extensions`), documented in
   `docs/pipeline/open_cvn_json_format.md` with examples under
   `examples/open_cvn/`.
7. **Unified parser/validator contract**: the public `src/open_cvn/` package
   (`parser_contract.py`) with deterministic CVN PDF-to-XML extraction, CVN
   XML import (including semantic partial mapping into Open CVN JSON), and
   Open CVN JSON import/validation, documented in
   `docs/pipeline/parser_validator_contract.md` and
   `docs/development/parser_workflow.md`.
8. **Local CV management application**: a CLI-first application
   (`src/open_cvn_app/`) with SQLite storage, master/derived curriculum
   versioning, Open CVN JSON import/export, LaTeX export, optional PDF
   generation, and an opt-in, deterministic-first LLM-assisted PDF import
   fallback, documented in `docs/development/application_mvp_workflow.md`,
   `docs/development/latex_export_workflow.md`,
   `docs/development/pdf_generation_workflow.md`, and
   `docs/development/llm_import_workflow.md`.
9. **The written and defended TFG memoria**: `docs/memoria/TFG.pdf` /
   `TFG_signed.pdf`, covering the full academic writeup (motivation, state of
   the art, CVN ecosystem analysis, architecture, methodology, pipeline
   walkthrough, evaluation, conclusions), plus the defense slides in
   `docs/defensa/`.

Known, documented limitations of that foundation are tracked in
`docs/pipeline/known_limitations.md` and remain valid input for TFM planning.

### What The TFM Adds

The TFM scope is now defined: a self-hosted Kubernetes lakehouse ingesting
CVN (synthetic) and ORCID (real) data, processed distributedly with Spark
under Iceberg/MinIO, orchestrated by Airflow, with entity resolution and a
small set of research indicators surfaced in Superset. Full detail,
including the technology stack decision record and rationale, the data
strategy and its privacy reasoning, the phased plan, the scope cut list, and
the repository standards that apply, is in
`docs/roadmap/tfm/issues/issue-89-epic-tfm-lakehouse-platform.md`. That document is written to be
self-contained; read it in full before starting implementation rather than
relying on this summary.

Key constraints, restated because they are easy to lose sight of mid-
implementation: 6 ECTS (half the TFG's 12, so scope must be proportionally
smaller), 20 days total including the memoria, ~120-140 available hours,
50-page memoria maximum written as living Markdown converted to LaTeX at the
end.

## Status Date

- Last updated: 2026-09-15 (issue `#90`, k3s cluster bring-up, completed)

## Entries

### Issue #90 Completed: k3s Cluster Bring-Up

- first TFM implementation issue completed; branch
  `issue-90-k3s-cluster-bring-up`
- local k3s `v1.36.4+k3s1` installed on the WSL2 development machine as a
  systemd service (`--flannel-backend=host-gw`, chosen to avoid a known
  VXLAN/UDP issue under WSL2's virtualized networking rather than the
  default flannel backend); dedicated `tfm-lakehouse` namespace created;
  Helm v4.3.0 installed and the official `apache-airflow` and `superset`
  chart repositories added; a smoke-test pod ran to completion in the
  namespace
- key finding for future issues: the epic's own wording assumed a classic
  `helm repo add bitnami ...` step for MinIO/PostgreSQL, but
  `charts.bitnami.com` is OCI-only as of 2025 — issue `#91` must pull
  those charts by OCI reference instead
  (`oci://registry-1.docker.io/bitnamicharts/<chart>`), pinned to an exact
  version; documented in `infra/k3s/README.md` and the issue file
- repository layout for infra work established: `infra/README.md`,
  `infra/k3s/README.md` (full install/access notes, reproducible), and
  `infra/helm-values/` (empty, for issue `#91` onward); no Terraform, per
  the epic's local-only decision
- full detail, including the kubeconfig write-permission workaround
  (root-owned `/etc/rancher/k3s/k3s.yaml` copied to `~/.kube/config`) and
  every task/subtask performed, is in
  `docs/roadmap/tfm/issues/issue-90-k3s-cluster-bring-up.md`
- `docs/roadmap/tfm/tfm_roadmap.md`'s status row for `#90` updated to
  `Completed`
- next: issue `#91` (Core Services Deployment — MinIO, PostgreSQL,
  Airflow), which depends on this issue

### Epic Broken Down Into 14 Filed Child Issues (#90-#103)

- the epic's seven phases were broken down in a planning conversation with
  the user into 14 issue-sized, independently-buildable deliverables (some
  phases split into multiple issues where they bundled more than one major
  task, e.g. phase 2's three data sources plus DAG wiring became four
  issues)
- all 14 were filed as real GitHub issues, `#90` through `#103`, and written
  up as full issue documents under `docs/roadmap/tfm/issues/`, each
  following the same mandatory-section contract as the TFG issues
- `docs/roadmap/tfm/tfm_roadmap.md`'s "Issue Status Overview" now lists all
  15 TFM issues (`#89` epic plus `#90`-`#103`) with their epic phase and
  dependencies
- the epic (`docs/roadmap/tfm/issues/issue-89-epic-tfm-lakehouse-platform.md`)
  was updated: its phase table now names the real child issue numbers per
  phase instead of describing phases abstractly, and its "Impact On Future
  Issues" section reflects that all child issues are now filed rather than
  pending
- the repository entry-point files (`AGENTS.md`, `PROJECT_GUIDE.md`,
  `docs/context/project_context_index.md`) were updated to list the new
  issues and to stop saying scope/child issues were still pending
- execution order: `#90`/`#91` (infra) -> `#92`/`#93` (Iceberg+Spark) ->
  `#94`-`#97` (ingestion) -> `#98`/`#99` (transform) -> `#100`/`#101`
  (BI+benchmark) -> `#102` (hardening) -> `#103` (memoria, written
  throughout but assembled at the end)
- no implementation has started; every issue is `Planned`

### TFG/TFM Documentation Folders Physically Separated

- at the user's explicit request, TFG and TFM documentation was moved into
  separate folders instead of remaining in the same directory: see
  `docs/roadmap/tfm/hotfixes/hotfix-10-tfg-tfm-documentation-folder-separation.md`
  for the full path mapping and rationale
- `docs/roadmap/issues/` and `docs/roadmap/hotfixes/` no longer exist; TFG
  content moved to `docs/roadmap/tfg/{issues,hotfixes}/`, TFM content to
  `docs/roadmap/tfm/{issues,hotfixes}/`
- `docs/context/current_status.md` moved to `docs/context/tfg/current_status.md`;
  this file itself moved from `docs/context/tfm_current_status.md` to
  `docs/context/tfm/current_status.md`
- `docs/roadmap/cvn_generation_roadmap.md` moved to
  `docs/roadmap/tfg/cvn_generation_roadmap.md`; `docs/roadmap/tfm_roadmap.md`
  moved to `docs/roadmap/tfm/tfm_roadmap.md`
- every cross-reference across the repository was updated, including prose
  (not just literal paths) that had assumed a single flat directory; see
  hotfix-10 for exactly what was corrected and why
- hotfix-9's own historical "Scope Decision: Freeze In Place" section was
  deliberately left describing the old paths, since it explains a decision
  that is now reversed and superseded by hotfix-10, not rewritten to look
  as if it always used today's paths

### TFM Epic Filed As GitHub Issue #89

- the TFM epic was filed on GitHub as issue `#89`
- `docs/roadmap/issues/issue-TBD-epic-tfm.md` was renamed to
  `docs/roadmap/issues/issue-89-epic-tfm-lakehouse-platform.md` (paths as they
  were before hotfix-10 later relocated the whole file into
  `docs/roadmap/tfm/issues/`, see below), and every reference to it across
  the repository was updated to the real number:
  `AGENTS.md`, `PROJECT_GUIDE.md`, `README.md`,
  `docs/context/project_context_index.md`, this file,
  `docs/roadmap/tfm/tfm_roadmap.md`, and
  `docs/roadmap/tfm/hotfixes/hotfix-9-tfg-completion-and-tfm-reorientation.md`
- stale "placeholder / not yet defined" language describing the epic was
  corrected wherever it had been left over from before the epic was defined,
  to avoid contradicting the epic's own now-defined content

### TFM Epic Defined: Lakehouse Platform Scope, Stack, And Constraints

- the TFM epic was fully defined in a planning conversation with the user
  and written up at `docs/roadmap/tfm/issues/issue-89-epic-tfm-lakehouse-platform.md`; see that
  document for complete detail, this entry only indexes the outcome
- confirmed hard constraints: 6 ECTS (vs the TFG's 12), 20 days total
  including the memoria (epic defined 2026-09-14, target completion
  ~2026-10-04), ~120-140 available hours (most days 5-6h, some full days),
  memoria capped at 50 pages, written as living Markdown converted to LaTeX
  at the end (same method as the TFG)
- confirmed technology stack: Kubernetes (k3s, local cluster only for now),
  MinIO, Apache Iceberg with a Hadoop path-based catalog (no Hive
  Metastore/REST catalog/Nessie for now), Apache Spark via `spark-submit`
  (no Spark Operator), Apache Airflow (`KubernetesExecutor`) for
  orchestration, PostgreSQL as the Superset-facing store for materialized
  gold-layer tables, Apache Superset for BI; Trino, Prometheus/Grafana, and
  Terraform/cloud deployment explicitly deferred to documented future work
- confirmed data strategy: ORCID via its Public API (targeted enrichment/
  fusion lookups) plus a filtered subset of its annual Public Data File bulk
  dump (real volume); CVN via schema-valid synthetic generation seeded from
  real ORCID fields, explicitly instead of sourcing real CVN documents at
  volume, due to a privacy/consent concern raised and accepted during
  planning (completed CVNs are personal data with no legitimate public bulk
  source, unlike ORCID profiles)
- confirmed phased plan (0: cluster/infra, 1: Iceberg+Spark wiring, 2:
  ingestion, 3: transform, 4: BI+benchmark, 5: hardening, 6: memoria
  assembly) and an explicit scope priority/cut list, decided in advance so
  time-pressure decisions do not need to be made from scratch later
- the TFM roadmap (`docs/roadmap/tfm/tfm_roadmap.md`) and this file's "What The
  TFM Adds" section were updated to reflect the defined epic
- no implementation has started; the next step is filing the first child
  issue (Phase 0: cluster + core infra) once work actually begins

### Repository Reorientation: TFG Closed, TFM Started

- the TFG was confirmed complete: memoria written, signed, and defended
  (`docs/memoria/TFG.pdf`, `docs/memoria/TFG_signed.pdf`,
  `docs/defensa/presentacion_tfg.pdf`/`.pptx`)
- `docs/memoria/estructura_memoria_tfg.md` chapter status markers were
  corrected from stale `EN_PROCESO` to `COMPLETADO` to match the actual,
  already-defended state, and a closure banner was added at the top of the
  document
- a `tfg-final` git tag was created at the commit that finalized the TFG
  defense materials, as a permanent reference point for the exact finished-TFG
  state
- the following TFG-era files were frozen in place with an explicit closure
  banner, rather than moved, specifically to avoid breaking the many existing
  cross-references to their paths from the 30 issue documents, 8 hotfix
  documents, and the documentation-contract files:
  - `docs/context/tfg/current_status.md` (complete TFG implementation log)
  - `docs/roadmap/tfg/cvn_generation_roadmap.md` (complete TFG roadmap)
- new active TFM counterparts were created alongside them instead of
  replacing them:
  - `docs/context/tfm/current_status.md` (this file)
  - `docs/roadmap/tfm/tfm_roadmap.md`
  - `docs/roadmap/tfm/issues/issue-89-epic-tfm-lakehouse-platform.md` (placeholder epic, content
    intentionally not yet defined)
- the repository entry-point and documentation-contract files were updated to
  point new sessions at the TFM files first, while still describing the TFG
  foundation for context:
  `README.md`, `PROJECT_GUIDE.md`, `AGENTS.md`, `CONTRIBUTING.md`,
  `docs/context/project_context_index.md`,
  `docs/documentation/documentation_conventions.md`,
  `docs/documentation/project_contracts.md`
- the transition itself is recorded as
  `docs/roadmap/tfm/hotfixes/hotfix-9-tfg-completion-and-tfm-reorientation.md`,
  following this repository's existing convention of recording structural or
  documentation-map changes as a hotfix record
- no TFG source code, generated artifacts, or the TFG memoria's LaTeX content
  were modified beyond the two stale-status corrections above
