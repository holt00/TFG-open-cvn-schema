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

- Last updated: 2026-09-19 (issue `#95`, ORCID bulk data file pipeline,
  completed — 301,763 Spain-affiliated records filtered from the 26.08M-record
  ORCID 2025 summaries file)

## Entries

### Issue #95 Completed: ORCID Bulk Data File Pipeline

- sixth TFM implementation issue completed; branch
  `issue-95-orcid-bulk-data-file-pipeline`
- verified the current official location before coding: the ORCID 2025
  Public Data File is on Figshare (12 files, 221.41 GiB / 237.73 GB); only
  the 46.33 GB `ORCID_2025_10_summaries.tar.gz` is used, since its
  employment/education entries carry the country needed for the filter and
  the activities files add nothing this issue needs
- filter: an employment or education entry whose organization country is
  `ES`, on the path confirmed against real entries
  (`employment-summary`/`education-summary` -> `common:organization` ->
  `common:address` -> `common:country`)
- new package `src/tfm_lakehouse/orcid_bulk/`:
  `fetch_orcid_bulk_subset` (HTTP streaming) and
  `fetch_orcid_bulk_subset_from_local_file`, sharing one tar-walk/filter
  core, with MD5 verification against Figshare's checksum
- the archive was downloaded manually (faster connection) into the
  git-ignored `data/orcid_bulk/raw/`; the first streaming attempt projected
  ~7 h at ~1.8 MB/s and was cancelled
- three findings while running on the real file, all fixed before the final
  run and detailed in the issue document: XML parsing, not download or
  gunzip, dominated runtime, so a byte-level prefilter was added (~7x,
  identical matches on a 100k sample); `tarfile` streaming leaked memory
  linearly (4.7 GB at 6.4M entries, would have exhausted 16 GB), fixed by
  clearing `TarFile.members`; and per-file writes on `/mnt/e` were I/O-bound,
  so matches are written from an 8-thread pool (gunzip itself cannot be
  parallelized)
- result: 26,078,951 records scanned, 301,763 matched (1.157%) in 81.6 min,
  MD5 verified, 301,763 files on disk equal to the match count; output in
  `data/orcid_bulk/filtered/` as `<3-digit>/<iD>.xml`
- tests: `tests/test_orcid_bulk_pipeline_unit.py` (7 passed, no network) and
  `tests/test_orcid_bulk_pipeline_live_smoke.py` (skipped by default; passes
  with `ORCID_LIVE_TEST=1` against the real file's first 2,000 entries)
- new limitation recorded in `docs/pipeline/known_limitations.md`
  (point-in-time snapshot, "any ES affiliation" semantics, prefilter
  serialization assumption, checksum checked after writing)
- `docs/roadmap/tfm/tfm_roadmap.md`'s status row for `#95` updated to
  `Completed`
- next: issue `#96` (Synthetic CVN Generator), which can seed from
  `data/orcid_bulk/filtered/`; issue `#97` should consider packing the
  300k small files instead of landing them one by one

### Issue #94 Completed: ORCID API Client

- fifth TFM implementation issue completed; branch
  `issue-94-orcid-api-client`
- original plan assumed a free, individually-registrable ORCID Public API
  client (`client_id`/`client_secret`, OAuth2 client-credentials); the
  actual registration form asks for the app to be described as a tool for
  a registered ORCID member organization, which a personal TFM project does
  not fit, blocking that path (this contradicts ORCID's own documentation,
  which says individuals can hold Public API credentials independent of
  membership -- the discrepancy was not chased further)
- pivoted to the ORCID Public API's anonymous (unauthenticated) tier
  instead: `pub.orcid.org/v3.0/{orcid-id}/{record,works,employments,
  educations}` answers plain `GET` requests with no token and no
  `client_id`, capped at 25k reads/day / 12 req/s per IP rather than 100k
  reads/day per registered `client_id` -- acceptable given issues `#96`/
  `#97` only need low-volume, per-iD lookups, not registry crawling
- new package `src/tfm_lakehouse/orcid_client/` (`client.py`,
  `exceptions.py`): ORCID iD checksum validation (ISO 7064 MOD 11-2),
  `OrcidClient` with `get_record`/`get_works`/`get_employments`/
  `get_educations`, typed errors (`OrcidValidationError`,
  `OrcidNotFoundError`, `OrcidApiError`), bounded 429 retry with backoff;
  no typed response models added, since `#96`/`#97` haven't defined which
  fields they need yet
- `requests>=2.32` added to `pyproject.toml`
- verified against the real, unauthenticated ORCID API, not just mocks: a
  credential-less lookup of the public "Josiah Carberry" ORCID demo record
  (`0000-0002-1825-0097`) returned the expected identifier field; 12 mocked
  unit tests cover checksum/404/500/429-retry behavior; full detail in
  `docs/roadmap/tfm/issues/issue-94-orcid-api-client.md`
- `docs/roadmap/tfm/tfm_roadmap.md`'s status row for `#94` updated to
  `Completed`

### Issue #93 Completed: Spark Job Execution From Airflow

- fourth TFM implementation issue completed; branch
  `issue-93-spark-job-execution-from-airflow`
- built a custom Spark image (`tfm-lakehouse/spark-py:3.5.9-iceberg1.11.0`)
  from Spark's own `bin/docker-image-tool.sh` PySpark base plus a thin
  custom `Dockerfile` layer (`infra/spark-conf/Dockerfile`) adding the
  three jars issue `#92` pinned, and loaded it into k3s's containerd
  directly (`docker save | sudo k3s ctr images import -`, no registry in
  this cluster)
- added RBAC (`infra/spark-conf/spark-rbac.yaml`: `ServiceAccount spark`,
  namespaced `Role`, `RoleBinding`) so the Spark driver can create/clean up
  its own executor pods/services/configmaps/PVCs
- wrote a minimal Airflow DAG (`dags/issue93_spark_iceberg_smoke_test.py`,
  `KubernetesPodOperator`) that runs `spark-submit --master k8s://... --deploy-mode client`
  from inside the cluster, and a trivial PySpark job
  (`src/tfm_lakehouse/jobs/iceberg_smoke_test.py`) that writes and reads
  back an Iceberg table through issue `#92`'s catalog
- three of issue `#92`'s locked decisions turned out to need correction
  once actually run: the `fs.s3a.aws.credentials.provider` class name
  (`org.apache.hadoop.fs.s3a.EnvironmentVariableCredentialsProvider`) does
  not exist in `hadoop-aws:3.3.4` at all -- corrected to the real class,
  `com.amazonaws.auth.EnvironmentVariableCredentialsProvider`, from
  `aws-java-sdk-bundle`; `spark.kubernetes.driver.*` pod-spec properties
  (credentials, service account) are silent no-ops in `client` deploy
  mode and had to move to the `KubernetesPodOperator` pod spec directly;
  and the RBAC `Role` needed `deletecollection`, a verb distinct from
  `delete`, for Spark's own bulk cleanup on shutdown. Full detail,
  including two more debugging findings (entrypoint/passwd handling for
  arbitrary UIDs, and the bundled-Hadoop-version check that confirmed no
  jar-pin revision was needed), is in
  `docs/roadmap/tfm/issues/issue-93-spark-job-execution-from-airflow.md`
- verified end to end, not just via the job's own internal read-back: a
  separate throwaway pod, unrelated to the job run, independently queried
  the written table through the same catalog config and got back the
  exact two rows written (`INDEPENDENT_VERIFY_ROW_COUNT=2`)
- this is also issue `#92`'s own missing end-to-end proof, left pending
  when that issue closed; `docs/roadmap/tfm/issues/issue-92-iceberg-catalog-on-minio.md`'s
  `Verification`/`Status` are updated to `Completed` as a result, and the
  corresponding `docs/pipeline/known_limitations.md` entry is resolved
- `docs/roadmap/tfm/tfm_roadmap.md`'s status rows for `#93` **and** `#92`
  updated to `Completed`
- next: issue `#94` (ORCID API client), first issue of epic phase 2

### Issue #92 In Progress: Iceberg Catalog On MinIO

- third TFM implementation issue started; branch
  `issue-92-iceberg-catalog-on-minio`
- resolved a circular dependency the epic's own planning left unresolved:
  issue `#92`'s original plan deferred jar-version pinning to "the Spark
  version chosen in issue `#93`", while issue `#93`'s own plan expected to
  inherit "the Iceberg/S3A dependencies from issue `#92`" — neither issue
  actually picked a Spark version. Fixed by locking the full version set
  here instead: Spark `3.5.9`, `iceberg-spark-runtime-3.5_2.12:1.11.0`,
  `hadoop-aws:3.3.4`, `aws-java-sdk-bundle:1.12.262`, chosen for mutual
  classpath compatibility (matching the Hadoop client jars Spark 3.5.x
  bundles), not just recency
- locked a catalog/warehouse design not spelled out in the epic: one
  Iceberg Hadoop catalog (`spark.sql.catalog.lakehouse`) rooted at
  `s3a://lakehouse/warehouse` — deliberately a different prefix from the
  raw `lakehouse/bronze|silver|gold` file-landing prefixes issue `#91`
  created, so Iceberg's own namespace/table directories never mix with
  raw landed files — with `bronze`/`silver`/`gold` as Iceberg namespaces
  inside that one catalog rather than three separate catalogs
  (`lakehouse.bronze.<table>`, etc.)
- new `infra/spark-conf/` directory added: `iceberg-catalog.conf` (the
  Spark properties file issue `#93`'s `spark-submit` calls will consume)
  and `README.md` (pinned versions, verified download URLs, and the
  credentials-via-`EnvironmentVariableCredentialsProvider` wiring issue
  `#93` must do against the existing `minio-root-credentials` secret from
  issue `#91` — no new secret, nothing committed)
- verified this session, not just researched: the
  `s3a://lakehouse/warehouse` path is writable (`mc pipe`/`ls`/`rm`
  round-trip via a throwaway pod); all four pinned artifacts resolve
  (`curl -I`, HTTP 200 each) for the Spark tarball, Iceberg runtime jar,
  `hadoop-aws`, and `aws-java-sdk-bundle`; and the `hadoop-aws`/
  `aws-java-sdk-bundle` version pairing directly from
  `hadoop-project-3.3.4.pom`'s `aws-java-sdk.version` property, not a
  secondary source
- deliberately **not** marked `Completed`: this issue's own scope stops at
  a verified, ready-to-consume catalog configuration; the actual proof
  that Spark can create a namespace/table through it and read it back
  requires a Spark image and `spark-submit` wiring, which is issue `#93`'s
  deliverable. Full detail in
  `docs/roadmap/tfm/issues/issue-92-iceberg-catalog-on-minio.md`
- `docs/roadmap/tfm/tfm_roadmap.md`'s status row for `#92` updated to
  `In Progress`
- next: issue `#93` (Spark Job Execution From Airflow), which consumes
  `infra/spark-conf/iceberg-catalog.conf` directly and supplies this
  issue's missing end-to-end proof

### Issue #91 Completed: Core Services Deployment (MinIO, PostgreSQL, Airflow)

- second TFM implementation issue completed; branch
  `issue-91-core-services-deployment`
- MinIO, a dedicated PostgreSQL instance, and Airflow (`KubernetesExecutor`)
  Helm-installed into the `tfm-lakehouse` namespace from issue `#90`, using
  values files under `infra/helm-values/`
  (`minio-values.yaml`, `postgresql-values.yaml`, `airflow-values.yaml`,
  `README.md`)
- every open decision the epic left for this issue was locked in the issue
  document's "Task 0 - Decisions Locked" before implementation, choosing
  the safest/easiest-to-debug option at each fork: one MinIO bucket
  (`lakehouse`) with `bronze`/`silver`/`gold` prefixes; a PostgreSQL
  instance dedicated to the future `gold` database, kept separate from
  Airflow's own embedded metadata Postgres (avoids custom external-DB
  wiring); Airflow DAGs delivered via a persistence-backed volume rather
  than `gitSync` (no sidecar/credentials to debug)
- major finding: the Bitnami Helm/image free catalog changed materially in
  2025-2026 (Broadcom's "Bitnami Secure Images" transition, MinIO's own
  Docker Hub images pulled in October 2025, MinIO's GitHub repo archived
  February 2026). Every Bitnami-chart image reference for MinIO and
  PostgreSQL — including MinIO's separate console/object-browser image,
  easy to miss — is pinned explicitly to the frozen but still-public
  `docker.io/bitnamilegacy` registry, with each tag verified pullable
  against the live registry before use rather than assumed; recorded as a
  new limitation in `docs/pipeline/known_limitations.md`
  ("Infrastructure Limitations (TFM)")
- second finding relevant to later DAG work (`#97`/`#99`): Airflow 3's
  `scheduler` pod does not mount the DAGs persistence volume (only
  `dag-processor`/`api-server` do), and newly parsed DAGs default to
  `is_paused=True` even for a manually triggered run; both confirmed with
  a throwaway smoke-test DAG that was deleted after verifying
  `KubernetesExecutor` spawns, runs, and completes a real task pod
  end-to-end
- full detail, including every pinned chart/image version, the exact
  install/verify commands, and the complete adjustments/findings record,
  is in
  `docs/roadmap/tfm/issues/issue-91-core-services-deployment.md`
- `docs/roadmap/tfm/tfm_roadmap.md`'s status row for `#91` updated to
  `Completed`
- next: issue `#92` (Iceberg Catalog On MinIO), which depends on this
  issue's `lakehouse` bucket

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
