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

- Last updated: 2026-09-26 (issue `#102`, hardening, completed: both verification phases passed,
  including a real bug found and fixed during the fresh-cluster rebuild; the epic's phase 5 is done)

## Entries

### Issue #102 Completed: Hardening

- thirteenth TFM implementation issue started; branch `issue-102-hardening`, created from
  `origin/development` (which contained `#101`). First (and only) issue of epic phase 5
- planned first and every decision recorded with its reason in the issue document (Task 0, D1-D4); D1
  (assistant does everything possible, notifies on `sudo`/an open decision) was stated directly by the
  user in this issue's own kickoff instructions rather than asked again; D4 (verification depth) was
  put to the user, who chose a two-phase gate: validate in place first, then a full fresh rebuild only
  if that passes clean
- **Task 1 (fragility audit) found real, live breakage on the cluster at planning time, not
  hypothetical risk**: `airflow-scheduler` was in `CrashLoopBackOff` at 57 restarts. Root cause,
  confirmed via logs and a direct DB query (not assumed): upstream apache/airflow issue `#67813`
  (open, unfixed on Airflow 3.2.2 / `cncf-kubernetes` 10.17.1), a `DetachedInstanceError` crash
  building a log message for a stale `TaskInstance` row a dead scheduler had left running. `#101`'s own
  status entry had misidentified the crashing container as the `scheduler-log-groomer` sidecar; it was
  the `scheduler` container itself. No upstream fix exists; fixed operationally by marking the row
  `failed` through Airflow's ORM and cleaning three stale pods. The scheduler's very first task
  dispatch after recovery then reproduced a second, separate known issue live (`#97`'s finding: the
  api-server killed by its own liveness probe under load, root-caused this time to having **no**
  resource request at all, so it was starved first under contention) -- fixed in
  `infra/helm-values/airflow-values.yaml` (a CPU/memory request, relaxed probe timing) and confirmed by
  two fresh DAG runs (`ingest_validate` 4m20s, `transform_publish` 9m22s) completing cleanly with 0
  component restarts throughout
- **Task 3**: `docs/development/tfm_lakehouse_workflow.md` (new), the from-scratch reproducibility
  quickstart, mirroring `regeneration_workflow.md`'s section shape, built from the actual infra READMEs
  and DAG source read directly
- **Task 2 Phase A (validate in place) passed clean**: the document's chart-version pins, file paths,
  and Secrets all cross-checked against the live cluster; its DAG-trigger steps are exactly what Task
  1's verification runs already proved. Phase B (tear down k3s, rebuild from nothing following only the
  document) is gated on Phase A and not yet run -- costly (hours, several `sudo`/interactive
  checkpoints), the user's call per D4
- **Task 4**: one real, concrete fix, not a speculative sweep -- writing the quickstart document
  surfaced that `dags/ingest_validate.py` and `dags/transform_publish.py` both hardcoded `REPO_ROOT` to
  this machine's exact checkout path with no override, undocumented anywhere. Fixed with a
  `TFM_REPO_ROOT` environment-variable override (same pattern as the benchmark package's own
  `BENCH_REPO_ROOT`, issue `#101`), default unchanged, redelivered to the live cluster, no import
  errors, existing tests still pass
- **Task 2 Phase B ran, not skipped -- against an isolated k3d cluster, not the real one.** The user
  asked whether destruction could be avoided ("can we not erase everything and reconstruct it in a
  temp folder or other folder?"); the assistant proposed three options (destroy-and-rebuild the real
  cluster; a second bare-metal k3s instance with its own `--data-dir`; k3d) recommending k3d, and the
  user chose it ("do the best option"). `k3d` installed with no `sudo` (`~/.local/bin`); a cluster
  pinned to the exact same k3s version as the real one (`v1.36.4+k3s1`) was created with the repository
  checkout bind-mounted at its own path, so the DAGs' hostPath volumes resolved identically; its own
  separate kubeconfig never touched `~/.kube/config` or the real cluster
- the whole quickstart document ran end to end on that isolated cluster: core services (both
  `scheduler`/`api-server` at `0` restarts immediately, confirming Task 1.3's fix is baked into the
  values file, not just live-patched), Spark/ingest images (`k3d image import`, no `sudo` needed
  either), `ingest_validate` (clean), and Superset (installed, dashboard confirmed queryable through
  its own REST API)
- **`transform_publish` found a second real bug**: `publish_gold_to_postgres` failed with
  `password authentication failed for user "gold" ... Role "gold" does not exist`, even though the two
  jobs before it had already succeeded. Root cause, confirmed via `kubectl logs postgresql-0
  --previous`: on a genuinely fresh cluster, all core services cold-start and pull images at once, and
  that contention killed PostgreSQL's very first `initdb` before it ever created the `gold` role; the
  Bitnami image never retries an interrupted first-boot init on restart. Fixed by deleting the pod and
  its PVC to force a clean reinitialization; getting the actual failing pod's logs (deleted by default
  on completion, no log persistence configured) required a temporary, reverted debug edit
  (`on_finish_action`: `"delete_pod"` -> `"keep_pod"`, delivered only to the isolated cluster)
- **independent, real-world reconfirmation of Task 1.1's fix**: after Phase B, restarting the real k3s
  (stopped again by an unrelated host event) brought the scheduler up in the exact same
  `DetachedInstanceError` `CrashLoopBackOff` as at planning time, with a fresh orphaned task row from a
  different date. The same documented recovery (mark the row and its `DagRun` failed, delete the
  orphan pods, force-restart the scheduler) fixed it again immediately, with zero code changes --
  strong evidence the recovery recipe is genuinely reusable, not a one-off
- six new/updated entries in `docs/pipeline/known_limitations.md`: the api-server liveness kill (now
  **Resolved**), the scheduler `DetachedInstanceError` poison pill (**Resolved operationally**, no
  upstream fix, independently reconfirmed), a crashed scheduler leaving `KubernetesExecutor` worker
  pods stuck `Unknown` (accepted, documented recovery step), and an interrupted PostgreSQL first boot
  never creating its application role (accepted upstream behavior, documented recovery step)
- tests: `uv run pytest -n auto tests`, as documented, run before Phase B (**909 passed, 2 skipped in
  10m51s**) and again after (the host rebooted mid-run first, unrelated, losing that log; a fresh run
  once the cluster was confirmed healthy again gave **907 passed, 2 skipped, 2 errors in 10m52s**, both
  errors the already-documented Spark-in-Docker container-concurrency flakiness, confirmed not a
  regression by `uv run pytest tests/test_gold_jobs_spark.py -q` alone: **12 passed in 5m31s**)
- state left in the cluster: the isolated k3d cluster was deleted after Phase B
  (`k3d cluster delete`); the real cluster is fully healthy (`airflow-scheduler`/`airflow-api-server`
  both `0` restarts on their current pods) after the independent recovery above; production
  `lakehouse.silver`/`.gold` and the PostgreSQL `gold` schema hold the rebuild from Task 1's
  verification runs (`issue102_verify_1`); Superset/Airflow replica counts untouched; k3s left running
- next: issue `#103` (memoria assembly), which can cite `docs/development/tfm_lakehouse_workflow.md`
  directly and this issue's findings (the poison pill and its reconfirmation, the api-server
  starvation, the PostgreSQL init race, the k3d methodology) for the memoria's hardening discussion

### Issue #101 Completed: Spark Performance Benchmark

- twelfth TFM implementation issue completed; branch `issue-101-spark-performance-benchmark`,
  created from `origin/development` (which contained `#100`). Second issue of epic phase 4
- planned first and every decision recorded with its reason in the issue document (Task 0, D1-D21
  accepted before execution); the three decisions put to the user (D1 the assistant writes files,
  D2 measure all three jobs not just silver, D3 three scales times executors `{1,2,4}`) were all
  chosen as offered or, for D2, more broadly than the recommendation
- **new package** `src/tfm_lakehouse/benchmark/` (`data`, `runner`, `campaign`, `eventlog`,
  `report`) and `src/tfm_lakehouse/spark_jobs/table_digest.py`; `matplotlib` added as a
  development dependency; results in `docs/benchmark/` (`results.md`/`.csv`/`.json`, three
  charts), reproduction steps in `docs/benchmark/README.md`
- **isolated three-scale campaign:** 1x/2x/4x (each nested in the smaller ones: 20k/40k/80k ORCID
  bulk records, 11k/22k/44k synthetic CVNs, a fixed 200-record ORCID API sample), landed into
  their own MinIO buckets and Iceberg namespaces/PostgreSQL schemas, never touching production
  (`lakehouse.silver`/`.gold`, PostgreSQL `gold`, the `#100` dashboard)
- **the campaign itself (108 runs: silver/gold/publish x 3 scales x 3 executor counts x 3
  repetitions, warm-ups and digests) ran from 2026-09-21 22:49 to 2026-09-24 18:16**, almost all
  of it unattended, and needed nine rounds of the assistant diagnosing and fixing a real incident
  before it could finish (decisions D22-D29, each with the exact incident, root cause and fix
  recorded in the issue document): a host suspend producing a false timeout (fixed with a
  monotonic clock, D22); a real, deterministic executor-memory ceiling at 1 executor for larger
  scales, which the campaign learned to stop repeating once confirmed (D23, D25, and two further
  bugs in that same bookkeeping found and fixed, D26/D27/D28); a missing-table crash when a digest
  or a downstream job read an upstream stage's failed output, fixed by treating a missing table as
  data (D24) and by an automatic repair run before gold/publish when the upstream output was not
  valid (D26b, with its own recency-tracking bug fixed as D28); and PostgreSQL's own default Helm
  chart memory limit (192Mi) OOMKilling the container while publishing the largest scale's gold
  tables, fixed by raising it (D29, `infra/helm-values/postgresql-values.yaml`)
- **the host slept or restarted for real six separate times** across the roughly 68 hours the
  campaign was open; each time the assistant found and cleaned orphaned pods, confirmed MinIO/
  PostgreSQL/Superset/Airflow state, and resumed the campaign from where it stopped (it is
  resumable by design: a run recorded `"ok"` is never repeated)
- **correctness (decision D9), verified:** every `(scale, job)` where more than one executor count
  actually produced output agrees byte-for-byte on its Iceberg/PostgreSQL content digest --
  confirmed for `1x`/`2x`/`4x` gold and publish across 1, 2 and 4 executors, and for `1x`/`2x`
  silver (`4x` silver only ever had one surviving executor count, 4, so nothing to compare it to)
- **headline finding:** at the fixed per-executor sizing, the number of executors is a
  *reliability* lever, not only a speed one, once volume grows -- 1 executor is a deterministic
  memory ceiling for silver from `2x` upward, and at `4x` even 2 executors is one; more executors
  also do not reliably reduce runtime on this single-node cluster (silver's speedup at `1x` is
  only 1.63x at 4 executors; gold's efficiency collapses from 1.00 to 0.23 between 1 and 4
  executors at every scale), with CPU sampling pointing at the shared MinIO object store, not CPU,
  as the practical limit (not proven, but consistent evidence); the publish job's runtime barely
  grows with data volume at all (a negative size-up exponent), since it always stages the same
  small number of already-aggregated gold tables
- **two report bugs found and fixed while reading the first analysis** (not campaign bugs, both
  before any figure was trusted): a misleading `correctness_ok=False` caused purely by confirmed-
  OOM configurations producing no output (fixed by reporting `empty_executors` and `consistent`
  separately); and all 9 final `4x-publish` runs falsely showing "executor pods left behind"
  because the leftover check listed every executor pod in the namespace instead of scoping to the
  run's own Spark application id -- a stale orphan from one unrelated, earlier, independently-
  failed run got blamed on nine later, unrelated, genuinely successful ones (fixed for future runs,
  `Cluster.app_id`/scoped `executor_pods`; the nine affected records corrected by hand with the
  evidence recorded in each)
- tests: 76 new in `tests/test_benchmark_unit.py` (several reproducing real incidents found while
  running the campaign) plus 3 in `tests/test_benchmark_digest_spark.py` (Spark image); full suite
  `uv run pytest -n auto tests`, as documented: 909 passed, 2 skipped in 11 min 40 s, one run
- new limitations recorded in `docs/pipeline/known_limitations.md` (the fixed-sizing deterministic
  ceiling, single-node non-CPU-bound scaling, and the PostgreSQL default resource preset, now
  resolved); `docs/roadmap/tfm/tfm_roadmap.md`'s row for `#101` is `Completed`; full detail,
  including every decision D1-D29 with its reason and rejected alternative, and the full incident-
  by-incident record of the campaign, is in
  `docs/roadmap/tfm/issues/issue-101-spark-performance-benchmark.md`
- state left in the cluster: the `bench_*` MinIO buckets, Iceberg namespaces and PostgreSQL
  schemas are dropped; Superset and Airflow are restored to their pre-campaign replica counts and
  verified healthy (one Airflow log-groomer sidecar container restart-looping on a
  `DetachedInstanceError`, the pre-existing operational fragility issue `#102` already covers, not
  introduced by this issue); production `lakehouse.silver`/`.gold`, PostgreSQL `gold` and the
  `#100` dashboard were never touched by the campaign; k3s left running
- next: issue `#102` (hardening), which inherits the fixed-sizing memory ceiling as an accepted,
  documented limitation and the raised PostgreSQL resource limit as a production-relevant change
  made during this issue

### Issue #100 Completed: Superset Dashboard

- eleventh TFM implementation issue completed; branch `issue-100-superset-dashboard`, created from
  `origin/development` (a `git fetch` was not possible, the local ref already contained `#99`). First issue of
  epic phase 4
- planned first and every decision recorded with its reason in the issue document (Task 0, D1-D14); the user
  accepted the three put to them (Helm chart, three charts plus provenance, the assistant writes the files). Added
  while working: D10 admin created outside the chart, D11 no data cache, D12 aggregates only and no names, D13
  regular expressions instead of PyYAML in the tests, D14 a cap of four concurrent Spark containers in the test suite
- key finding while planning: the `superset/superset` Helm chart is **deprecated** upstream (the official path is
  now a `v1alpha1` operator) and the official image has **no PostgreSQL driver**; the chart was kept (pinned, no
  CRDs) with an own image (`tfm-lakehouse/superset:6.1.0-pg`, imported into k3s by the user with `sudo`)
- **deployed:** Superset 6.1.0 in the `tfm-lakehouse` namespace (web, the chart's own PostgreSQL and Redis, worker
  at zero, admin created from a Secret), a read-only role `superset_ro` on the gold database whose **default
  privileges survive `#99`'s drop-and-rename publish**, and the dashboard `tfm-gold-indicators`: publications per
  year (I1), affiliation stays started per year (I3), new collaboration pairs per year on real ORCID data (I2) and a
  provenance table from `gold_run`. Aggregates only, no personal names
- **dashboard as code:** `infra/superset/assets/` is a versioned export; `import_dashboard.py` rebuilds it through
  the REST API (the CLI cannot pass a database password). Deleting everything and importing from the files gave
  the same uuid and the same rows in every chart
- **verified:** every chart equals hand-written SQL in PostgreSQL, row by row; a full `transform_publish` run
  (`e2e100-1`) while a reader polled the four charts gave 0 errors and 0 empty results in 238 samples, the run id
  changed in one step and the dashboard showed it without a refresh; privileges survived the recreation of the
  tables; the dashboard renders in a headless browser (screenshots in `infra/superset/screenshots/`)
- things that went differently from the plan: the first `helm install` was marked `failed` with every pod healthy
  (PostgreSQL's first boot outlasted Helm's 5-minute timeout, fixed with `--timeout 15m`); the chart's 24 h data
  cache would have hidden a new run (disabled on the connection); my first layout lacked the charts' `uuid`, so
  Superset added a duplicate row (found in the first export, fixed and guarded by a test)
- tests: 24 new in `tests/test_superset_infra_unit.py`, including a drift guard between the exported dashboard and
  `gold/schemas.py`, and 6 in `tests/test_spark_image_slots_unit.py`. **`uv run pytest -n auto tests`, as documented,
  is green in a single run: 828 passed, 2 skipped in 10 min 15 s** (idle machine, cluster stopped). It was not before:
  two runs on 2026-09-20 had 9 and 4 failures (32-33 min), all `TimeoutExpired` or `CANNOT_OPEN_SOCKET` in the
  Spark-in-Docker tests, because `-n auto` ran up to 16 Spark containers at once. Cause and fix: `tests/spark_image.py`
  now lets four run at once across the pytest workers (`SPARK_TEST_SLOTS` changes it) and removes the container of an
  aborted run (decision D14 in the issue document; this touches the test helper of `#98`/`#99`)
- three new sections in `docs/pipeline/known_limitations.md` (and rows in its matrix), plus one on the Spark test
  concurrency (resolved); `docs/roadmap/tfm/tfm_roadmap.md`'s row for `#100` is `Completed`; full detail
  in `docs/roadmap/tfm/issues/issue-100-superset-dashboard.md`
- the `transform_publish` run `e2e100-1` timings (548 s, 151 s, 201 s) are **not** usable for `#101`: a browser was
  being installed during the run
- state left in the cluster: Helm release `superset` (revision 2), Secrets `superset-secrets` and
  `superset-gold-ro-credentials`, role `superset_ro`, the dashboard imported in Superset; `lakehouse.silver`,
  `lakehouse.gold` and the PostgreSQL `gold` schema hold the rebuild of run `e2e100-1`; no throwaway pod remains
- next: issue `#101` (Spark performance benchmark), which measures `#98`'s and `#99`'s jobs; run it on a quiet machine
- the cluster was shut down at the end of the session (k3s stopped); start it again with `sudo systemctl start k3s`
  before any cluster work, and check `kubectl get pods -n tfm-lakehouse` (the Airflow pods restart on their own)

### Issue #99 Completed: Silver -> Gold, Indicators & `transform_publish` DAG

- tenth TFM implementation issue completed; branch
  `issue-99-silver-to-gold-indicators-and-transform-publish-dag`, created from
  `origin/development`. Closes epic phase 3 (transform)
- planned first and every decision recorded with its reason in the issue document (Task 0,
  D1-D11): three indicators (publications per researcher per year, affiliation timeline,
  collaboration pairs), five gold tables, publish to PostgreSQL through staging tables and one
  atomic swap, one image for the whole DAG. The user accepted the three decisions put to them
  (indicators, manual-trigger DAG, the assistant writes files)
- **new packages and jobs:** `src/tfm_lakehouse/gold/` (definitions and DDL/swap SQL as pure
  code; DataFrame indicators, native Spark functions only), `spark_jobs/silver_to_gold.py`,
  `spark_jobs/publish_gold_to_postgres.py`, `infra/spark-conf/Dockerfile.gold` (the silver image plus
  `postgresql-42.7.13.jar`, imported into k3s by the user with `sudo`) and
  `dags/transform_publish.py` (`bronze_to_silver >> silver_to_gold >> publish_gold_to_postgres`,
  manual trigger). The provisional `issue98_bronze_to_silver` DAG was retired
- **gold tables** (Iceberg `lakehouse.gold`, mirrored 1:1 in PostgreSQL schema `gold`):
  `dim_researcher` 29,767 rows, `publications_per_researcher_year` 172,861,
  `affiliation_timeline` 94,431, `collaboration_pairs` 9,540, `gold_run` (provenance: run id and the
  silver snapshot ids read, plus counts)
- **spikes settled the design:** the real silver showed fused records inflate a naive publication
  count by 5.1% (543,879 rows -> 516,396 works), so deduplication per entity is required; the
  collaboration indicator passed its gate (25 of 9,540 pairs, 0.26%, are one person seen twice; 5,092
  involve real ORCID data only); JDBC from Spark and a table swap in one transaction through the JVM's
  `DriverManager` work on the cluster's PostgreSQL. A first figure of the spike (5.6%) was wrong and was
  caught by an independent recomputation
- **verified on the real data through the DAG's pods:** two runs of about 10 minutes each; gold
  recomputed independently in plain Python with 0 mismatches; PostgreSQL rows identical to Iceberg (306,599
  rows compared); a second run gave identical PostgreSQL content; a publish killed mid-load left the
  published tables untouched and a retry recovered by itself; no pod left behind. The silver rebuild
  reproduced `#98`'s resolution evaluation exactly (R2 precision 95.8%, recall 74.2%)
- **the gold indicators are insensitive to rule R2's false merges:** undoing the 75 single-organization
  merges moves them by 0.07% to 0.58%
- **runtimes (input for `#101`):** warm run 219.8 s, 71.3 s and 69.3 s for the three jobs, cold run 280.8 s,
  73.0 s and 79.2 s
- two things that differed from the plan: the PostgreSQL password needs no environment variable on the
  executors (it travels in the JDBC write options), and staging tables are created with explicit DDL
  instead of letting Spark create them (types, primary keys, `TIMESTAMPTZ`)
- tests: 45 new (schemas, DAG structure, and 12 that run the real jobs in the gold image against a real
  PostgreSQL 17 container); full suite `uv run pytest -n auto tests`: 798 passed, 2 skipped (753 at the end
  of `#98`)
- five new sections in `docs/pipeline/known_limitations.md` (and rows in its matrix);
  `docs/roadmap/tfm/tfm_roadmap.md`'s status row for `#99` updated to `Completed`; full detail in
  `docs/roadmap/tfm/issues/issue-99-silver-to-gold-indicators-and-transform-publish-dag.md`
- state left in the cluster: `lakehouse.silver` and `lakehouse.gold` hold the rebuild of run `e2e99-2`;
  the PostgreSQL `gold` schema holds the same content (`gold_run.run_id = e2e99-2`);
  `transform_publish` is unpaused with no schedule; the `ingest_validate` DAG keeps its daily schedule
  (its next run adds a partition that the next `transform_publish` run deduplicates)
- next: issue `#100` (Superset dashboard), which connects to the PostgreSQL `gold` schema; the
  `Impact On Future Issues` section of the issue document lists the connection facts and the table
  meanings

### Issue #98 Completed: Bronze -> Silver, Validation & Entity Resolution

- ninth TFM implementation issue completed; branch
  `issue-98-bronze-to-silver-validation-and-entity-resolution`, created from
  `origin/development`. First issue of epic phase 3, the HA01 centerpiece
- planned first and every decision recorded with its reason in the issue document
  (Task 0, D1-D13): one Spark job on the Spark image extended with pydantic, jsonschema
  and requests; three-layer CVN validation reusing `parser_contract`; ORCID rule-based
  checks; a common shape; deterministic entity resolution (same ORCID iD, then
  name and affiliation); silver rebuilt in full on every run
- key finding while planning: the Spark image runs **Python 3.10** and PySpark 3.5 does
  not support 3.14, so the repository's own code has to run on 3.10; a spike showed
  `validate_open_cvn_json` does with the libraries added, and the Spark-side code was kept
  3.10 compatible (tests guard it). `uv.lock` cannot be pinned as it stands (its
  `rpds-py` needs Python >=3.11)
- new packages `src/tfm_lakehouse/silver/`, `src/tfm_lakehouse/spark_jobs/` and
  `src/tfm_lakehouse/cvn_validation.py` (promoted from `#96`'s validation, which still
  passes its tests); `infra/spark-conf/Dockerfile.silver`; `dags/issue98_bronze_to_silver.py`
  (manual trigger, provisional until `#99`); the user imported the image into k3s with `sudo`
- verified on the real data through the DAG's pods: counts equal `#97`'s manifests exactly
  (19,469 bulk, 1,000 CVN, 200 API); 15 of 15 independent integrity checks; injected invalid
  records rejected with the right rules; rebuilds identical (per-snapshot content digests);
  no pod left behind
- **entity resolution measured against the generator's ground truth**: with 10,000 CVNs
  (a run with `seed=43` that stays in bronze), rule R1 places 7,098 of 7,098 declaring
  documents in their entity; rule R2 reaches **precision 95.8% and recall 74.2%** on 186
  evaluable documents. The plan's 99% precision target was **not met**: the first run gave
  90.8%, the analysis found one weak-evidence combination (a relaxed given name and a
  shortened family name at once, wrong 8 of 8 times), which was forbidden at no cost in
  correct merges; the remaining 6 false merges are namesakes with one shared
  organization. Recall is at its data ceiling (47 of 186 have no affiliation). Each link's
  `evidence` carries `name_match` and `shared_organizations` so `#99` can be stricter
- other findings: an organization-similarity threshold cannot separate a campus suffix from
  a different institution (0.60 against 0.67), so equality is the default and the sweep shows
  no gain below it; Spark's 200 default shuffle partitions made the job 4 times slower
  (225 s against 55 s with 16); the first run of a session is 2.5 times slower
- the evaluation itself was corrected during the issue (a match through another CVN that
  declares the same iD is a counterpart); the Spark tests now run the container as the host
  uid so pytest can clean up its temporary files
- tests: new `tests/test_silver_*` files and three Spark tests that run in the Spark image
  (skipped without Docker and the image); full suite `uv run pytest -n auto tests`:
  753 passed, 2 skipped (577 at the end of `#97`). One earlier attempt hit an intermittent collection error in a TFG test (a race between xdist workers over the in-place regeneration of `src/generated/`, unrelated to this issue; the file passes alone and the repeat was clean)
- five new sections in `docs/pipeline/known_limitations.md`;
  `docs/roadmap/tfm/tfm_roadmap.md`'s status row for `#98` updated to `Completed`;
  full detail in
  `docs/roadmap/tfm/issues/issue-98-bronze-to-silver-validation-and-entity-resolution.md`
- state left in the cluster: bronze holds `#97`'s run plus the `e2e98-big` partition;
  `lakehouse.silver` holds the last rebuild (30,868 person records, 29,767 entities);
  the `issue98_bronze_to_silver` DAG is unpaused (no schedule); the `ingest_validate`
  DAG's scheduled run of 2026-09-20 00:00 UTC succeeded and added a partition that silver has
  not read yet (the next rebuild deduplicates it)
- next: issue `#99` (silver to gold: indicators and the `transform_publish` DAG), which
  absorbs this job's launcher, reads `lakehouse.silver`, and should deduplicate
  publications per entity before counting

### Issue #97 Completed: Bronze Landing & `ingest_validate` DAG

- eighth TFM implementation issue completed; branch
  `issue-97-bronze-landing-and-ingest-validate-dag`, created from
  `origin/development`. Closes epic phase 2 (ingestion)
- planned first and every decision recorded with its reason in the issue
  document (Task 0, D1-D13): one pod per task on a new image, code and data
  mounted from the checkout with hostPath, bronze as raw JSON Lines under the
  `bronze/` prefix with a per-record provenance envelope, a landing check that
  sends failures to `bronze/_rejected/` and fails the task above 5%
- key finding while planning: Airflow's Python is 3.13.13 and the repository
  requires `>=3.14`, so `tfm_lakehouse` cannot run in Airflow's workers; the tasks
  run in a `python:3.14-slim` image (`infra/ingest/`, 158 MB), imported into k3s
  by the user with `sudo`
- new package `src/tfm_lakehouse/bronze/` (`envelope`, `checks`, `landing`,
  `tasks`) and `dags/ingest_validate.py` (four `KubernetesPodOperator` tasks,
  `@daily`, eight params); `boto3` added to `pyproject.toml`; a root
  `.dockerignore` keeps the ~46 GB `data/` out of Docker builds
- verified twice on the real data: from the host, and through the DAG's own pods.
  The default run took about 9 minutes and left in MinIO 19,469 landed and 531
  rejected ORCID bulk records (2.66%, all for missing public names), 1,000
  synthetic CVN and 200 real ORCID API records, with the 12 provenance fields on
  every record, 0 duplicates and one manifest per source. A second run skipped the
  bulk source as designed. No task pod was left behind
- the independent Spark read (issue `#93`'s image) found a real defect: Spark reads
  every part file under `bronze/` regardless of the manifest, so a run that failed
  the threshold had left 1,949 valid records visible. A failed landing now removes
  its landed shards. It also showed that reading all of `bronze/` collapses
  `payload` to `string`, so issue `#98` must read each source separately
- the whole ORCID bulk subset is roughly 42 GB of XML (estimate), so the bulk source
  is landed once per snapshot and capped at 20,000 records by default
  (`bulk_max_records`, 0 lands all). The 20,000 default was proposed here and
  confirmed by the user
- two things that went differently from the plan: unpausing the DAG created the
  cron run for 00:00 that day immediately (Airflow 3 runs at the cron time; the
  plan had assumed midnight), and the Airflow api-server was killed by its own
  liveness probe at that moment, failing that run and the first manual one before
  any task started (a pre-existing fragility of issue `#91`'s deployment). A
  re-trigger passed
- tests: `tests/test_bronze_landing_unit.py` and
  `tests/test_bronze_tasks_unit.py` (46 tests, no network); full suite
  `uv run pytest -n auto tests`: 577 passed, 2 skipped
- new entries in `docs/pipeline/known_limitations.md`;
  `docs/roadmap/tfm/tfm_roadmap.md`'s status row for `#97` updated to `Completed`;
  full detail in
  `docs/roadmap/tfm/issues/issue-97-bronze-landing-and-ingest-validate-dag.md`
- the DAG is left unpaused; its next scheduled run is 2026-09-20 00:00 UTC
- next: issue `#98` (bronze to silver: validation and entity resolution), reading
  each bronze source separately and deduplicating on `record_id`

### Issue #96 Completed: Synthetic CVN Generator

- seventh TFM implementation issue completed; branch
  `issue-96-synthetic-cvn-generator`, created from `origin/development`
- new package `src/tfm_lakehouse/synthetic_cvn/`:
  `generate_synthetic_cvn(SyntheticCvnConfig(...))` builds Open CVN JSON
  curricula seeded with the real public name, affiliations, and works of the
  issue `#95` ORCID subset (four entity types: identity, degree/doctorate
  education, professional positions, scientific publications), validates
  each one, and writes sharded JSON Lines plus a ground-truth manifest to the
  git-ignored `data/synthetic_cvn/`. No new dependency (standard-library
  `random`, not Faker, whose Python 3.14 support could not be confirmed)
- key finding: the document JSON Schema leaves `identity` and every entry's
  `data` free-form, so `validate_open_cvn_json` alone accepts invented fields.
  Each entity's own `$defs` schema is strict, and the generator's validation
  layer applies it. That layer discarded 179 of the first 200 documents on
  the first real run and exposed two builder bugs, which were fixed. Also:
  `FlexibleDateValue` is string-typed in the schema but integer-typed in the
  XML importer (a pre-existing TFG inconsistency, recorded as a limitation,
  TFG code untouched)
- ORCID linkage for issue `#98`: a configurable share of documents carries the
  seed's ORCID iD (`identificador_digital_de_autor`, type code `140`); the
  rest keep a varied name and unchanged affiliations. `manifest.jsonl` is the
  ground truth
- performance was I/O-bound on seed files (~16 documents/s, disk wait), so
  seed files are prefetched by a thread pool with a separate random stream
  for draws: 10,000 real-seeded documents in 169 s (~59 documents/s), 0
  invalid, 8.3 KB each
- privacy handling: only public name/affiliation/work fields are read;
  identity filler is invented (`000` phones, `@example.invalid` emails, no
  DNI, no nationality); each document carries `metadata.source.synthetic =
  true`. Three new limitation sections in `docs/pipeline/known_limitations.md`
- tests: `tests/test_synthetic_cvn_generator_unit.py` (23 passed, no network)
  and `tests/test_synthetic_cvn_local_smoke.py` (runs against the local
  `#95` subset, skipped when absent)
- `docs/roadmap/tfm/tfm_roadmap.md`'s status row for `#96` updated to
  `Completed`; full detail in
  `docs/roadmap/tfm/issues/issue-96-synthetic-cvn-generator.md`
- next: issue `#97` (Bronze Landing & `ingest_validate` DAG), which calls
  `generate_synthetic_cvn` and should land the JSON Lines shards, not one
  object per document

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
