# Issue 89 - Epic: TFM Lakehouse Platform For Curricular Data Integration And Analysis

## Filename And Numbering Note

This document previously used `issue-TBD-epic-tfm.md` as a placeholder
filename while no GitHub issue existed for the TFM epic (a deliberate,
recorded deviation from the repository's normal issue-file naming convention
`docs/roadmap/<tfg|tfm>/issues/issue-<number>-<slug>.md`, see
`docs/documentation/documentation_conventions.md`). GitHub issue `#89` has
now been filed for the TFM epic, and this file was renamed to
`docs/roadmap/tfm/issues/issue-89-epic-tfm-lakehouse-platform.md` accordingly,
with every cross-reference updated in
`docs/roadmap/tfm/tfm_roadmap.md`, `docs/context/tfm/current_status.md`, and the
repository entry-point files (`README.md`, `PROJECT_GUIDE.md`, `AGENTS.md`,
`docs/context/project_context_index.md`).

This document was written to be fully self-contained: the planning session
that produced it will not persist, so every decision below includes its
rationale, not just its conclusion.

## Summary

Provisional title: **"Diseño de una arquitectura lakehouse escalable para la
integración y análisis de información curricular académica."**

The TFM evolves Open CVN from a local, single-user schema/tooling project
(the TFG) into a small but real, self-hosted **lakehouse platform** that
ingests curricular and research-career data from multiple sources (CVN and
ORCID), organizes it through bronze/silver/gold layers with preserved
provenance, processes it with distributed compute, resolves duplicate/
inconsistent identities across sources, and produces a handful of research
indicators on a BI dashboard, with an accompanying performance benchmark.

Everything below was decided in a planning conversation and is recorded here
because that conversation itself will not be available to future sessions.

## Relationship To The TFG

The TFM is not a new, independent project. It is built directly on top of
the TFG (Trabajo de Fin de Grado) work already completed in this repository
(issues `#11`-`#71`, all `Completed`; full record in
`docs/roadmap/tfg/cvn_generation_roadmap.md` and
`docs/context/tfg/current_status.md`, both frozen/closed).

For a reader with no TFG context, in one paragraph: the TFG took the official
Spanish CVN (Curriculum Vitae Normalizado) XML/XSD package and built, layer
by layer: (1) reproducible structural Pydantic bindings generated straight
from the official schemas (`src/generated/`), (2) a normalization layer that
cross-indexes every field by CVN code and resolves it against auxiliary
reference catalogs (`src/cvn_codegen/normalization.py`), (3) a semantic
policy layer turning that evidence into deterministic typing/naming
decisions (`src/cvn_codegen/semantic_policy.py`), (4) a domain model
generator emitting the final Pydantic models
(`src/models/cvn/generated/`), (5) an agnostic conceptual model layer
feeding generated PlantUML diagrams and a generated JSON Schema
(`docs/diagrams/`, `schemas/open_cvn.schema.json`), (6) the canonical **Open
CVN JSON** document format with a unified parser/validator contract
supporting PDF, XML, and JSON import (`src/open_cvn/`), and (7) a local CLI
application on top of all of that (`src/open_cvn_app/`). The TFG memoria is
written, signed, and defended (`docs/memoria/TFG.pdf`).

Specific TFG artifacts the TFM reuses directly, not rebuilds:

- `schemas/open_cvn.schema.json` and `docs/pipeline/open_cvn_json_format.md`:
  the canonical Open CVN JSON shape becomes the CVN-side contract for the
  lakehouse's bronze→silver validation gate, and the template the synthetic
  CVN generator (below) must produce schema-valid output against.
- `src/open_cvn/parser_contract.py` (`validate_open_cvn_json`, etc.): reused
  as-is, or wrapped, for CVN-side ingestion validation instead of
  reimplementing JSON Schema + Pydantic validation.
- the `cvn_trace` / `x-open-cvn-*` provenance conventions established in the
  TFG's semantic policy and JSON Schema work: the lakehouse's own
  "conservar procedencia" requirement (below) extends the same idea
  (source artifact, source field code, resolution trace) into the bronze/
  silver/gold layering, rather than inventing a new provenance model.
- `examples/open_cvn/` example documents: used as structural seed templates
  for the synthetic CVN generator (below), not as bulk source data (there
  are only a few of them).

The existing local CLI app (`src/open_cvn_app/`) is **not** part of the
TFM's required deliverable. It is a single-user tool; this epic builds a
platform. It may remain as one illustrative downstream consumer of the
lakehouse's Open-CVN-shaped data, but that is optional and out of scope
unless explicitly added later.

## Academic Constraints

These are hard constraints on scope, decided with the user, and must not be
silently relaxed by a future session:

- **ECTS**: the TFG was 12 ECTS; the TFM is **6 ECTS**, i.e. roughly half.
  The TFM's scope must be proportionally *smaller* than the TFG's, not
  larger, even though the subject matter (a lakehouse platform) sounds more
  ambitious on paper. Any scope addition must be matched by an equivalent
  cut elsewhere in this document's "Scope Priority / Cut List" section.
- **Programme**: Master's degree in "Big Data and Cloud Computing." The
  "Learning Outcomes Targeted" section below maps this epic's technical
  choices to the programme's own outcome codes.
- **Deadline**: the TFM, **implementation and memoria included**, must be
  finished within **20 days** of this epic being defined. This epic was
  written on **2026-09-14**, which places the target completion date at
  approximately **2026-10-04**. If a future session resumes this work on a
  different actual start date, recompute the 20-day deadline from that real
  start date and update this section.
- **Available effort**: most days give roughly 5-6 hours of work; some days
  give a full working day. Budget roughly **120-140 total hours** across the
  20 days, not more.
- **Memoria**: **50 pages maximum**. Written using the same strategy as the
  TFG: living Markdown documentation kept up to date as work happens
  (session-by-session entries in `docs/context/tfm/current_status.md`, this
  epic, and its child issue documents), later converted into the LaTeX
  memoria, rather than writing the memoria as a separate late-stage task.
  See `docs/memoria/estructura_memoria_tfg.md` for how the TFG structured
  this same living-documentation-to-LaTeX process; a TFM-equivalent
  structure document should be created under `docs/memoria/` (or a
  TFM-specific subfolder, decide at that time) once memoria drafting starts,
  but is not needed before implementation begins.

## Learning Outcomes Targeted

Taken from the original brief the user supplied; mapped explicitly to this
epic's technical decisions so the memoria's evaluation chapter can point at
concrete evidence for each one:

| Outcome | Description | Covered by |
| --- | --- | --- |
| `CN02` | Arquitecturas de tratamiento masivo, almacenamiento y pipelines | k3s cluster, MinIO, Iceberg bronze/silver/gold layering |
| `HA01` | Adquisición, fusión y análisis de múltiples fuentes | ORCID (API + bulk file) and CVN (synthetic) ingestion, entity resolution/fusion by ORCID iD |
| `HA02` | Procesamiento distribuido y optimización de recursos | Spark on Kubernetes; the executor-count benchmark |
| `HA03` | Orquestación ETL y almacenamiento escalable | Airflow DAGs; Iceberg tables |
| `CP01` | Planificación y despliegue de una solución Big Data | this epic's phased plan; Helm-based k3s deployment |
| `CP04` | Proyecto profesional original de Big Data | the platform end-to-end, plus the evaluation/benchmark chapter |

## Original Goal

Build a self-hosted, Kubernetes-based lakehouse that ingests CVN (synthetic,
schema-valid) and ORCID (real, public) data, lands it with provenance,
processes it distributedly through bronze/silver/gold layers with identity
resolution across sources, publishes a small set of research indicators to a
BI dashboard, and includes a bounded performance benchmark; document the
whole process as a 50-page-max memoria written incrementally, the same way
the TFG was documented.

## Technology Stack Decision Record

Every choice below was discussed and decided with the user; alternatives
considered and rejected are listed so a future session does not re-litigate
them without cause.

| Layer | Decision | Rejected / deferred alternative | Why |
| --- | --- | --- | --- |
| Cluster substrate | **Kubernetes (k3s)**, single local machine, multiple pods | Docker Swarm | Swarm is simpler but absent from the Big Data ecosystem's official tooling; k8s is the expected skill for a "Cloud Computing" programme and every other chosen component ships first-class k8s support |
| Deployment scope | **Local cluster only** | Multi-node / real cloud VMs via Terraform | Time budget (20 days); real cloud deployment and cost analysis documented as future work |
| Object storage | **MinIO** | - | S3-compatible, self-hosted, the natural data-lake substrate; user's own original suggestion |
| Table format | **Apache Iceberg** | Delta Lake (OSS) | Vendor-neutral (Apache governance), wide engine support, real lakehouse semantics (schema evolution, time travel); user confirmed "if easier and does not break minimum requirements" |
| Iceberg catalog | **Hadoop (path-based) catalog** rooted at a MinIO path (`s3a://.../warehouse`) | Hive Metastore, REST catalog, Nessie | No extra catalog service to deploy/debug within the time budget; Nessie's versioned-catalog story documented as future work |
| Distributed processing | **Apache Spark**, `spark-submit` in Kubernetes mode, launched from Airflow | Spark Kubernetes Operator | Avoids installing/operating extra CRDs; still genuinely distributed, still satisfies HA02 |
| Interactive query layer | **Spark SQL only**, for now | Trino | Documented future work; Trino was in the original brief but dropped to control scope |
| Orchestration | **Apache Airflow**, official Helm chart, `KubernetesExecutor` | Celery/Redis-based executor | User's original suggestion; `KubernetesExecutor` avoids standing up Celery+Redis as extra services |
| BI / indicators | **Apache Superset**, connected to **PostgreSQL** | Superset connected directly to Iceberg/Spark (via Trino or Spark Thrift Server) | Avoids needing Trino or a Spark Thrift Server just for BI; gold-layer tables are small and aggregated by the time they're published, so materializing them into Postgres as the last publish step keeps Superset a zero-glue, native-connector deployment |
| Observability / benchmark capture | Spark job logs / Spark History Server UI export | Prometheus + Grafana | Documented future work; full observability stack not worth the setup time for one bounded benchmark |
| Data quality (CVN side) | Reuse `src/open_cvn/parser_contract.py` (`validate_open_cvn_json`) at bronze→silver | New validation library (Great Expectations, Soda) | Avoids adding a whole new dependency for something the TFG already solved; also a deliberate TFG/TFM continuity point |
| Data quality (ORCID side) | Simple rule-based checks (required fields present, ORCID iD checksum valid) | - | Proportionate to scope |

## Data Sources, Volume Strategy, And An Ethics/Privacy Note

**ORCID** — real data, two complementary mechanisms:

1. **Public API (v3.0)**, for targeted enrichment/fusion (HA01): free
   "Public API" client registration at ORCID, OAuth2 client-credentials grant
   for a `/read-public`-scoped token, then `GET /v3.0/{orcid-id}/record` (or
   narrower endpoints: `/works`, `/employments`, `/educations`). Used to look
   up a specific ORCID iD already known from another source (e.g. one
   declared inside a synthetic CVN record), demonstrating cross-source
   fusion.
2. **Public Data File**, for real volume: ORCID publishes an annual full
   public-record snapshot (tens of millions of records, XML/JSON). Download
   once, filter/sample to a manageable working subset (e.g. records with a
   Spain-affiliated employment/education entry, or a field/keyword filter)
   for the day-to-day pipeline. Processing the full file at web scale is
   documented future work, not required here. Verify the current official
   download location/format at implementation time (it has moved hosting
   providers over the years); do not hardcode a URL into pipeline code
   without checking it still resolves.

This split matters because it solves the volume problem with **real** data
instead of needing to synthesize everything, and it is a stronger `HA02`/
`CN02` story than distributing purely synthetic data.

**CVN** — synthetic, deliberately not scraped:

Real, completed CVN documents are personal/professional data typically used
for private grant or evaluation submissions, not published openly the way an
ORCID profile is. There is no legitimate public corpus of "real CVNs" to
harvest at volume, and attempting to gather many of them would mean handling
real people's personal data without consent, a genuine privacy/legal problem
for a repository that is public on GitHub and defended publicly. This
epic explicitly rejects that approach.

Instead: generate synthetic Open CVN JSON documents that are schema-valid
against `schemas/open_cvn.schema.json`, using the small number of TFG example
documents (`examples/open_cvn/`) as structural seed templates, and **fed with
real public fields from the ORCID dataset** (names, works, affiliations,
dates) so the synthetic curricula are realistic rather than arbitrary. This
also naturally creates ORCID-iD linkage between the synthetic CVN records and
the real ORCID records, which is exactly the join key the entity-resolution
step needs.

If a future session still wants to source additional real CVN data, that
must be re-evaluated explicitly against consent/privacy constraints before
being added to this plan; it is not assumed here.

## Proposed Repository Layout For TFM Code

Not yet created; propose and confirm/adjust at the start of Phase 0 (below),
but stated now so a fresh session has a concrete target instead of having to
invent conventions from scratch:

- `infra/`: Helm values files and any raw Kubernetes manifests for MinIO,
  PostgreSQL, Airflow, Superset, and the Spark submission image/build.
- `airflow/dags/`: Airflow DAG definitions (`ingest_validate.py`,
  `transform_publish.py`), kept separate from `src/` because they need to be
  synced into the Airflow scheduler pod rather than pip-installed.
- `src/tfm_lakehouse/`: hand-maintained Python business logic shared by DAGs
  and Spark jobs, mirroring the TFG's `src/cvn_codegen/` convention:
  - `src/tfm_lakehouse/ingestion/`: `orcid_api.py`, `orcid_bulk.py`,
    `synthetic_cvn_generator.py`
  - `src/tfm_lakehouse/spark_jobs/`: `bronze_to_silver.py`,
    `silver_to_gold.py` (these are the actual `spark-submit` entry points)
  - `src/tfm_lakehouse/dedup/`: entity resolution logic (ORCID-iD-first,
    normalized name/affiliation fallback)
- `tests/`: continues to hold all automated tests, following the existing
  repository convention (see "Repository Standards" below); prefix new test
  files clearly, e.g. `test_tfm_*.py`, to keep TFG and TFM tests visually
  distinguishable inside the shared `tests/` directory.
- `docs/pipeline/tfm_lakehouse_architecture.md`: to be created once Phase 0
  starts, mirroring `docs/pipeline/cvn_pydantic_generation_pipeline.md`'s
  role for the TFG.

## Original Plan

Phased, time-boxed to the 20-day / 120-140h budget. Each phase should end
with a working, smoke-tested increment, not a partial one; if a phase
overruns, consult the "Scope Priority / Cut List" below before extending the
timeline.

| Phase | Days (of 20) | Goal | Child issues |
| --- | --- | --- | --- |
| 0. Cluster + core infra | 1-2 | k3s running; core services deployed | `#90` k3s cluster bring-up; `#91` core services deployment (MinIO, PostgreSQL, Airflow) |
| 1. Iceberg + Spark wiring | 3-4 | Prove the lakehouse's core mechanism works | `#92` Iceberg catalog on MinIO; `#93` Spark job execution from Airflow |
| 2. Ingestion | 5-7 | Real + synthetic data landing in bronze with provenance | `#94` ORCID API client; `#95` ORCID bulk data file pipeline; `#96` synthetic CVN generator; `#97` bronze landing & `ingest_validate` DAG |
| 3. Transform | 8-11 | Bronze -> silver -> gold, with dedup | `#98` bronze -> silver: validation & entity resolution; `#99` silver -> gold: indicators & `transform_publish` DAG |
| 4. BI + benchmark | 12-14 | Visible indicators + one performance result | `#100` Superset dashboard; `#101` Spark performance benchmark |
| 5. Hardening | 15-16 | Reduce risk of a broken demo | `#102` hardening |
| 6. Memoria assembly | throughout, concentrated 16-20 | 50-page memoria, defensible | `#103` memoria assembly |

Every phase above has been broken down and filed as its own numbered child
issue, `#90` through `#103` (the same pattern the TFG used: epic `#8` with
child issues `#11`-`#17` etc.), each with the full mandatory-section
contract. See `docs/roadmap/tfm/tfm_roadmap.md`'s "Issue Status Overview"
for the complete list with dependencies, and the individual issue files
under `docs/roadmap/tfm/issues/` for full detail per issue. Phases were
broken down further than the table above where a phase bundled multiple
independently-buildable deliverables (e.g. phase 2's three data sources plus
the DAG wiring became four separate issues, `#94`-`#97`); see each issue's
own "Original Plan" for what it individually covers.

## Scope Priority / Cut List

Decided in advance so that if the 20-day/120-140h budget is at risk, the
decision of what to drop is already made and does not need to be re-litigated
under time pressure.

1. **Never cut** (this is the epic's minimum bar): the k3s cluster with
   MinIO and Iceberg bronze/silver/gold layering with preserved provenance;
   the Spark ETL; Airflow orchestration; ORCID (API + bulk subset) and CVN
   (synthetic) ingestion; entity resolution/dedup; at least one working
   indicator; the memoria.
2. **Cut second**: reduce to 1 indicator instead of 2-3; reduce the benchmark
   to 1 data scale instead of 2-3.
3. **Cut first** (no learning-outcome dependency rides on this alone):
   Superset entirely. If dropped, present the same indicator(s) as a static
   table/chart pulled from the PostgreSQL gold tables directly in the
   memoria's evaluation chapter instead of a live dashboard.

## Repository Standards That Must Be Followed

The full contracts live in `docs/documentation/project_contracts.md` and
`docs/documentation/documentation_conventions.md`; restated here so this
epic is self-contained. All new TFM code and documentation must follow these,
exactly as the TFG did:

- **Python typing**: type hints wherever reasonably possible; explicit return
  types for public functions; keep generated/structural types separate from
  hand-maintained semantic types (not directly applicable to most TFM code,
  but the ingestion/dedup/indicator logic should still be typed).
- **Python docstrings**: concise, English, Google-style (`Args:`, `Returns:`,
  `Raises:`); comments stay rare, only for non-obvious logic.
- **Logging**: use `logging`, not `print`, for operational output;
  `logger = logging.getLogger(__name__)`; f-strings only, never `%`-style
  formatting.
- **Naming**: `snake_case` for variables/functions/modules, `PascalCase` for
  classes, `UPPER_SNAKE_CASE` for constants.
- **Testing**: automated tests live under `tests/`; the standard entry point
  (`uv run pytest -n auto tests`) must keep working; CI (`.github/workflows/
  pr-tests.yml`) must keep passing; known failures from source-data
  inconsistencies get documented as limitations, not hidden.
- **Generated-vs-hand-maintained boundary**: keep the same discipline the TFG
  used — anything produced by a generator/pipeline step is not hand-edited;
  hand-maintained logic stays clearly separated from generated/derived
  output.
- **Documentation update protocol**: at the end of every TFM issue's work
  session, update, in the same session: (1) that issue's document, (2)
  `docs/context/tfm/current_status.md` (never the closed
  `docs/context/tfg/current_status.md`), (3) `docs/pipeline/known_limitations.md`
  if a new limitation appeared, (4) `docs/roadmap/tfm/tfm_roadmap.md` if roadmap
  state changed (never the closed
  `docs/roadmap/tfg/cvn_generation_roadmap.md`), (5) `PROJECT_GUIDE.md` if
  human-facing entry guidance changed. This is how the memoria stays
  writable from living documentation instead of reconstructed from memory at
  the end.
- **Issue documents**: every TFM issue file must include the same ten
  mandatory sections used throughout this repository: `Summary`,
  `Original Goal`, `Original Plan`, `Adjustments Made During Implementation`,
  `Implementation Performed`, `Verification`, `Findings`,
  `Known Limitations`, `Impact On Future Issues`, `Status`.
- **Deviation recording**: any deviation from this epic's plan must be
  recorded, with its reason, in the relevant child issue's "Adjustments Made
  During Implementation" section — the same discipline the TFG used
  throughout its own 30 issue documents.
- **Structural/documentation-map changes**: recorded as a hotfix document
  under `docs/roadmap/tfm/hotfixes/` (TFM, active) or
  `docs/roadmap/tfg/hotfixes/` (TFG, closed, `hotfix-1` through `hotfix-8`),
  the same convention used throughout the repository.
- **Frozen TFG documents**: never add entries to
  `docs/context/tfg/current_status.md`, `docs/roadmap/tfg/cvn_generation_roadmap.md`,
  the TFG issue files (`#11`-`#71`), or the TFG hotfix files (`#1`-`#8`).
  TFM work is logged exclusively in `docs/context/tfm/current_status.md` and
  `docs/roadmap/tfm/tfm_roadmap.md`.
- **Mandatory reading order for any session resuming this work**:
  `AGENTS.md` -> `PROJECT_GUIDE.md` ->
  `docs/context/project_context_index.md` ->
  `docs/context/tfm/current_status.md` -> this epic document -> the current
  child issue document (once one exists).

## Adjustments Made During Implementation

Not applicable yet; no implementation has started.

## Implementation Performed

Not applicable yet; no implementation has started.

## Verification

Not applicable yet. Planned approach: each phase in "Original Plan" ends
with an explicit smoke test before the next phase starts (stated per-phase
above); the final acceptance check is a full pipeline run (ingest ->
transform -> publish -> dashboard/report) plus a reproducible benchmark run,
both runnable from a documented quickstart.

## Findings

Not applicable yet.

## Known Limitations

Deliberately out of scope for this TFM, and explicitly deferred to future
work rather than silently omitted:

- Trino (or any federated/interactive query layer beyond Spark SQL)
- Prometheus/Grafana or any dedicated observability stack
- Terraform-provisioned multi-node or real cloud deployment; local k3s only
- A Hive Metastore, REST catalog, or Nessie versioned catalog; Hadoop
  path-based catalog only
- Processing the full ORCID public data file at web scale; a filtered subset
  only
- Additional data sources beyond CVN and ORCID (institutional repositories,
  OpenAlex, Crossref, etc.)
- ML-based or probabilistic entity resolution; deterministic
  ORCID-iD-first, name/affiliation-fallback matching only
- Sourcing additional real CVN documents beyond the existing small TFG
  example set, due to the privacy/consent concerns documented above

## Impact On Future Issues

Every phase has been broken down and filed as child issues `#90` through
`#103` (see "Original Plan" above and `docs/roadmap/tfm/tfm_roadmap.md`).
The "Scope Priority / Cut List" section governs what each child issue may
drop if the time budget is at risk.

## Status

`Planned`. Scope, stack, data strategy, phased plan, and standards are
defined and agreed with the user. Filed as GitHub issue `#89`; this file and
every cross-reference to it use the real number. No implementation has
started.
