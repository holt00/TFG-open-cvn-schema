# Issue 97 - Bronze Landing & `ingest_validate` DAG

## Summary

Wire issues `#94`, `#95`, and `#96` together into one Airflow DAG that lands
both data sources into MinIO bronze with provenance metadata and a
landing-time structural check. Closing issue of TFM epic phase 2.

## Original Goal

One working, scheduled ingestion pipeline covering both CVN and ORCID
sources, ready for the transform stage.

## Original Plan

- build the `ingest_validate` Airflow DAG with tasks
  `fetch_orcid_bulk_subset` (issue `#95`), `fetch_orcid_api_enrichment`
  (issue `#94`), `generate_synthetic_cvn` (issue `#96`), and
  `validate_and_land_bronze`
- land outputs into MinIO bronze, partitioned by source and ingestion date
- attach provenance metadata to every landed record (source, retrieval
  time), extending the same idea as the TFG's `cvn_trace` /
  `x-open-cvn-*` conventions rather than inventing a new provenance model
- implement the landing-time structural check: well-formed/schema-valid for
  CVN (lighter than issue `#98`'s full semantic validation), required-field
  presence for ORCID

### Detailed Plan (accepted 2026-09-19)

Planned in a dedicated session before any code was written, following the
convention of issues `#91`-`#96`: every open decision the epic and the
original plan left unresolved is locked below (Task 0) with its reason and
the alternatives rejected, so a later session does not re-litigate it. Work
then proceeds task by task; each task is announced with a summary of what it
and its subtasks cover and closed by stating which files the user has to
modify (if any) and the next step. Unless a task says otherwise, the
assistant writes the code, infrastructure files, and documentation for this
issue, at the user's explicit instruction to do everything it can without
their intervention and to notify them when something needs them.

#### Facts established while planning (verified, not assumed)

- The Airflow pods run **Python 3.13.13** (checked in the `dag-processor`
  pod) while this repository requires Python `>=3.14`. `tfm_lakehouse` cannot
  be imported by Airflow's own workers.
- Airflow is `3.2.2` with `apache-airflow-providers-amazon 9.29.0`,
  `boto3 1.43.0`, and `kubernetes 35.0.0` in the image. Only `dag-processor`
  mounts the DAGs PVC, and a new DAG is paused at creation (issue `#91`).
- `python:3.14-slim` exists on Docker Hub.
- `data/orcid_bulk/filtered/` holds the 301,763 XML records of issue `#95`;
  `data/synthetic_cvn/` does not exist yet.
- The document JSON Schema leaves entry `data` free-form, and the ORCID
  anonymous API tier allows 25,000 reads/day and 12 requests/s per IP
  (issues `#96` and `#94`).
- No literal `cvn_trace` identifier exists in `src/`; only the
  `x-open-cvn-*` schema annotations do. Where the TFG's trace convention
  lives is checked in Task 1 rather than assumed.
- A web search for Airflow 3.2 / boto3 support on Python 3.14 returned
  nothing conclusive, so both are verified by running them in Task 1.

#### Task 0 - Decisions Locked

Each decision lists the choice, the reason, and what was rejected. The four
decisions marked *(user)* were put to the user with their options
explained; the user accepted the recommended option in each case.

| # | Decision | Reason | Rejected alternative |
| --- | --- | --- | --- |
| D1 | Every DAG task is a `KubernetesPodOperator` running a new image, `tfm-lakehouse/ingest` (`python:3.14-slim` plus the project dependencies). The DAG file imports nothing from `tfm_lakehouse` at parse time. | Airflow's own Python is 3.13 and the project needs 3.14, so the business logic cannot run in Airflow's workers. Same pod-per-task pattern issue `#93` proved. | Running the logic in Airflow workers (`PythonOperator`/`@task`): impossible on 3.13. Rebuilding the Airflow image on 3.14: far larger scope than this issue. |
| D2 *(user)* | Code and data reach the pods by **hostPath**: `src/` read-only and `data/` read-write, mounted from the repository checkout. The image carries only Python and dependencies. | Editing code needs no image rebuild and no `sudo k3s ctr images import`, the friction issue `#93` recorded as a limitation. Data cannot be baked in anyway (301,763 files, several GB). k3s is a single node on the same machine, so hostPath resolves to the same disk. | Baking the code into the image: reproducible and portable, but a rebuild plus a `sudo` import on every change, and `data/` would still need hostPath or an extra step packing the subset into MinIO first. Kept as the fallback if Task 1 finds hostPath on `/mnt/e` unusable. |
| D3 | Tasks hand data to each other through the shared `data/` directory, one subdirectory per `run_id`. XCom carries only small summaries (paths, counts). | Each task is a separate pod and the payloads are gigabytes; XCom is for metadata. | Passing data through XCom, or through MinIO between tasks (extra I/O for data that is already local). |
| D4 | Bronze is **raw JSON Lines objects** under the `bronze/` prefix of issue `#91`: `s3a://lakehouse/bronze/source=<orcid_bulk\|orcid_api\|synthetic_cvn>/ingestion_date=YYYY-MM-DD/run_id=<id>/part-NNNNN.jsonl`, plus a `_manifest.json` per partition. They are not Iceberg tables. | Issue `#92` deliberately separated the raw landing prefixes from the Iceberg `warehouse/`; the Iceberg bronze namespace, if any, is issue `#98`'s to create from these files. Hive-style `key=value` directories let Spark discover the partitions with no extra code. | Writing Iceberg tables directly: needs Spark for landing, which this issue does not otherwise need, and pre-empts `#98`'s design. One object per record: I/O-bound on 300k records, the wall issues `#95` and `#96` both hit. |
| D5 | Every landed line is an envelope: `record_id`, `source`, `source_ref` (ORCID iD or CVN document id), `retrieved_at`, `ingestion_run_id`, `source_snapshot`, `landing_check` (`status`, `errors`), `payload`. The payload is the raw XML string (bulk), the JSON object (API), or the Open CVN document (synthetic). | Puts provenance on every record, as the issue requires. Keeping the ORCID XML as a string preserves the source byte for byte and lets the 301,763 small files be packed into a few shards, as issue `#95`'s closing note advised. | Provenance only in the per-partition manifest: not attached to each record, and lost as soon as records are read individually. Parsing ORCID XML into JSON at landing: lossy, and belongs to `#98`. |
| D6 *(user)* | Landing check: CVN with `validate_open_cvn_json` only (not `validate_synthetic_document`); ORCID with well-formed XML, a valid ORCID iD checksum (reusing `validate_orcid_id`), and required fields present. Records that fail go to a `rejected/` prefix with their errors and a counter, not into bronze proper, and the task **fails if the rejection rate exceeds 5%**. | The issue asks for a check lighter than `#98`'s, and the entity-level check is `#98`'s job. Keeping rejects, not dropping them, preserves the raw evidence. `#98` then reads clean partitions only. The threshold turns a systemic bug into a failed task; issue `#96` showed how a builder bug silently discarded 179 of 200 documents. For orientation, issue `#96` found 2.7% of ORCID records unusable as seeds (mostly no family name), so an ORCID name requirement would reject roughly that share, under 5% but without much margin (an estimate to be measured in Task 7, not a fact). | Landing everything with a `landing_check.status` flag in the same place: keeps bronze purely raw, but every consumer must remember to filter and there is no automatic alarm. |
| D7 | Task order: `fetch_orcid_bulk_subset` -> `generate_synthetic_cvn` -> `fetch_orcid_api_enrichment` -> `validate_and_land_bronze`. | The generator seeds from the bulk subset, and the enrichment needs the ORCID iDs of the linked synthetic CVNs (`manifest.jsonl`), which is the cross-source fusion case the epic describes. | The order in which the original plan listed the tasks: it put enrichment before the CVNs exist. |
| D8 | `fetch_orcid_bulk_subset` is idempotent: it does nothing when the subset already exists with a completion marker, and a DAG parameter `force_refetch` overrides that. It runs from the manually downloaded archive, never re-downloading 46 GB. | Rebuilding the subset took 81.6 min in issue `#95`; a scheduled DAG cannot repeat that daily. | Re-running the extraction on every DAG run. |
| D9 *(user)* | The API enrichment fetches **200** ORCID iDs per run (a DAG parameter), sampled deterministically from the linked synthetic CVNs; it tolerates 404 and 429. | Enough to demonstrate cross-source fusion (the API is fresher than the 2025 snapshot), well inside the anonymous quota (25,000 reads/day, 12 req/s), and safe for a daily schedule. No later issue needs a larger API sample: the benchmark of `#101` scales on the bulk and synthetic data. | 1,000-2,000 iDs (better statistics, but repeated runs the same day accumulate against the quota); 5,000 or more (a real risk of exhausting the quota). |
| D10 | Landing uses `boto3` (`TransferConfig` multipart), with the MinIO Service endpoint and the existing `minio-root-credentials` Secret injected as `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` by `secretKeyRef` on the pod spec, as issue `#93` found necessary. No new secret. | Standard S3 client, already part of Airflow's environment, and no credential ever enters the repository. | The `minio` SDK is the fallback if `boto3` does not install or run on Python 3.14 (verified in Task 1). |
| D11 | Code goes in `src/tfm_lakehouse/bronze/` (`envelope.py`, `checks.py`, `pack.py`, `landing.py`, `tasks.py` with a `python -m` entry point); the DAG in `dags/ingest_validate.py`; tests in `tests/test_bronze_*.py` using an injected S3 client and an in-memory fake, no `moto`. | Same one-package-per-concern pattern as `#94` (`orcid_client/`), `#95` (`orcid_bulk/`) and `#96` (`synthetic_cvn/`). `dags/` is where `#93` put DAGs, not the `airflow/dags/` the epic proposed. The fake avoids a new test dependency. | `src/tfm_lakehouse/ingestion/` and `airflow/dags/` as the epic proposed, same reasoning as issue `#96`'s Decision 6. |
| D12 *(user)* | The DAG is `schedule="@daily"`, `catchup=False`, `max_active_runs=1`, with parameters `count`, `seed` (**fixed, default 42**), and `orcid_link_ratio`; pods use `on_finish_action="delete_pod"`; the DAG is unpaused as a deploy step. | The fixed seed keeps runs reproducible and gives `#98` a stable ground truth; the scheduled run is mainly a demonstration that the pipeline runs unattended, and volume experiments (`#101`) are manual triggers with other `count`/`seed`. `delete_pod` is what issue `#93` deferred to this issue for repeatedly-run DAGs. Unpausing as a deploy step avoids changing the Airflow Helm release. | A seed derived from the run date (a fresh batch every day, more realistic incremental ingestion, but the same ORCID iD then appears across days with different filler, more cases for `#98`). Changing `dags_are_paused_at_creation` in `airflow-values.yaml`: a Helm upgrade for a one-DAG convenience. |

Known cost of D12: with a fixed seed, every daily run lands identical
documents in a new `ingestion_date` partition, so bronze accumulates copies
and issue `#98` must deduplicate or read only the latest partition. This is
accepted and passed on in "Impact On Future Issues".

Files touched by Task 0: this document, and the `#97` row of
`docs/roadmap/tfm/tfm_roadmap.md` (`In Progress`).

#### Task Breakdown

Status in brackets; updated as work proceeds.

1. **Task 1 - Branch and feasibility spikes** [done; results in
   "Adjustments Made During Implementation"].
   - 1.1 branch `issue-97-bronze-landing-and-ingest-validate-dag` from
     `origin/development` [done].
   - 1.2 throwaway pod: is a hostPath under `/mnt/e` visible, writable, and
     fast enough (confirms or overturns D2).
   - 1.3 `python:3.14-slim` can install this project and `boto3` (confirms or
     overturns D10).
   - 1.4 a pod can reach MinIO at the Service endpoint and write a test object
     under `bronze/`.
   - 1.5 find where the TFG's trace convention lives (D5) and whether
     `fetch_orcid_bulk_subset*` leaves a completion marker (D8).
2. **Task 2 - Ingest image** [done; the user imported it into k3s with
   `sudo`]: `infra/ingest/Dockerfile` and README.
3. **Task 3 - Bronze core library** [done]: envelope and provenance (3.1), landing
   checks (3.2), ORCID packing (3.3), S3 landing writer with layout,
   multipart, manifest, and idempotency (3.4), unit tests (3.5).
4. **Task 4 - Task entry points** [done] (`tasks.py`): the four DAG tasks,
   each writing a small JSON summary to the run directory.
5. **Task 5 - DAG** [done] `dags/ingest_validate.py`.
6. **Task 6 - Deploy** [done, DAG unpaused]: copy to
   the `dag-processor` PVC, confirm no import errors, unpause.
7. **Task 7 - End-to-end verification** [done, from the host and through the
   DAG's pods]: small run, then full-volume run;
   object and record counts against the manifest; provenance fields on every
   record; a deliberately invalid record is rejected; re-running a date does
   not duplicate; an independent Spark read of the landed JSON Lines with the
   issue `#93` image (proves `#98` can consume it); pods are cleaned up.
8. **Task 8 - Full test suite** [done, 577 passed]: `uv run pytest -n auto
   tests`, in the background.
9. **Task 9 - Documentation close-out**: this document, `current_status.md`,
   `tfm_roadmap.md`, `known_limitations.md`, `infra/README.md` and
   `infra/ingest/README.md`, `PROJECT_GUIDE.md`.

## Adjustments Made During Implementation

- Plan accepted on 2026-09-19 with the decisions above (Task 0).
- The original plan listed the four DAG tasks in the order bulk, API
  enrichment, synthetic, land. Decision D7 reorders them because the
  enrichment depends on the ORCID iDs the synthetic generator produces.
- **Task 1 spikes (2026-09-19), run in a throwaway `python:3.14-slim` pod in
  `tfm-lakehouse`, deleted afterwards. They confirm D2 and D10 and refine
  D2, D5 and D8:**
  - *1.2, hostPath (D2 confirmed).* A pod mounting `src/` read-only and
    `data/` read-write from `/mnt/e/...` sees all 1,100 checksum-bucket
    directories of the ORCID subset and can create and delete files there.
    Cold single-thread reads measured 25 ms per file (536 files, 63.3 MB),
    better than the ~50 ms issue `#96` measured on the host. The fallback of
    baking the code into the image is therefore not needed.
  - *1.3, dependencies on Python 3.14 (D10 confirmed).* `boto3` 1.43.98,
    `jsonschema` 4.26.0, `pydantic` 2.13.5, `requests` 2.34.2, and
    `pymupdf` 1.28.2 install on Python 3.14.7, and `tfm_lakehouse` and
    `open_cvn.parser_contract` import from the mounted `src/`. The `minio` SDK
    fallback is not needed.
  - *1.4, MinIO (D10 confirmed).* From the pod, `boto3` with the Service
    endpoint `http://minio.tfm-lakehouse.svc.cluster.local:9000`, path-style
    addressing, `s3v4`, and the credentials injected by `secretKeyRef` listed
    the `lakehouse` bucket and wrote, read back, and deleted an object under
    `bronze/`. The test object was removed.
  - *Refines D2: the pod must also mount `schemas/`.* `validate_open_cvn_json`
    and the issue `#96` validation layer resolve
    `schemas/open_cvn.schema.json` relative to the repository root
    (`Path(__file__).resolve().parents[2]` / `[3]`), which the first pod
    layout (only `src/` and `data/`) did not provide. With `schemas/` mounted
    read-only at `/repo/schemas`, `generate_synthetic_cvn` ran end to end in
    the pod on Python 3.14: 50 requested, 50 generated, 0 invalid, 37 linked,
    13 unlinked, 18 s (mostly seed-pool start-up). The test output was
    removed from `data/`.
  - *Refines D5: provenance vocabulary.* The TFG convention is the `trace`
    block of the Open CVN JSON format (`docs/pipeline/open_cvn_json_format.md`,
    "Trace Metadata": `source_files`, `source_artifacts`, `xml_paths`, ...)
    and the `CvnTrace` model (`src/models/cvn/components.py`); the literal
    name `cvn_trace` exists only as a field of the generated domain models. The
    envelope therefore reuses the `source_files`/`source_artifacts` naming for
    its source-of-origin fields instead of inventing new terms (for the bulk
    source: the archive name and its verified MD5, from issue `#95`), and
    keeps the record-level fields (`source`, `source_ref`, `retrieved_at`,
    `ingestion_run_id`) that the trace block has no place for, since it
    describes CVN evidence, not ingestion events. Final envelope fields:
    `record_id`, `source`, `source_ref`, `source_snapshot`, `source_files`,
    `source_artifacts`, `retrieved_at`, `landed_at`, `ingestion_date`,
    `ingestion_run_id`, `landing_check`, `payload_format`, `payload`.
    `retrieved_at` is when the source data was obtained (the archive's
    download time for the bulk file, the request time for the API, the
    generation time for synthetic CVN); `landed_at` is when the run wrote it.
  - *Refines D8: there is no completion marker to check.*
    `fetch_orcid_bulk_subset*` only creates the output directory and returns
    `OrcidBulkSubsetResult(scanned, matched, output_dir)`; it writes nothing
    recording completion, and an interrupted run leaves a partial directory
    that looks like a finished one. The task therefore writes the marker
    itself, `data/orcid_bulk/_subset_complete.json`, **outside `filtered/`**
    because the issue `#96` seed pool lists that directory and a stray file
    would sit among the bucket directories. The subset that already exists
    from issue `#95` has no marker, so the task adopts it once: it counts the
    files and writes the marker only if the count equals the 301,763 matches
    issue `#95` recorded, so a partial directory is never adopted; otherwise it
    extracts from the local archive, and it never downloads one.
- **Refines D3: no XCom at all.** Each task writes a JSON summary to
  `data/bronze_runs/<run_id>/<task>.summary.json` and prints a
  `TASK_SUMMARY {...}` line in its log. Using XCom from a `KubernetesPodOperator`
  needs the `do_xcom_push` sidecar container and `/airflow/xcom/return.json`,
  extra machinery for information the shared directory already carries.
- **Refines D6: the ORCID check and the measured rejection rate.** The ORCID XML
  check requires well-formed XML, a valid iD checksum, given and family names,
  and at least one employment or education entry with an organization name; the
  API check requires a matching, valid iD and a `person` section. Measured on
  the first 20,000 real records: 531 rejected (2.66%), all for missing names
  (531 without a family name, 48 without a given name, some both), which agrees
  with the 2.7% issue `#96` measured as unusable seeds and is inside the 5%
  threshold.
- **New D13 - the bulk subset is landed once per snapshot and capped at 20,000
  records by default *(user, option A)*.** Measured on a
  500-file sample, the ORCID XML averages 137 KB (median 44 KB, heavy tail), so
  the whole 301,763-record subset is roughly 42 GB (an estimate from the
  sample). MinIO's PVC is 8 Gi (the `local-path` provisioner does not enforce
  it, and the disk has ~925 GB free, but it is the declared size), and a daily
  schedule would re-land the same static file every day. So the bulk source is
  landed once per snapshot (later runs report `skipped`, unless
  `force_bulk_landing`), and `bulk_max_records` caps how many records are landed
  (in a deterministic bucket-then-name order; 0 lands all). The cap is part of
  the snapshot id, so raising it lands the larger set again. **The 20,000
  default was proposed here and confirmed by the user** (the alternatives put to
  them were landing everything, about 42 GB and roughly 1 h 40 min extrapolated,
  or another number): it keeps the daily demo bounded (2.7 GB, 4.5 minutes
  measured) and is not derived from any requirement. Landing everything is one
  parameter away, so issue `#101` can raise it if the benchmark needs the volume.
- **Refines D12: parameter defaults and the unpause.** The DAG's default
  `count` is 1,000 (17-24 s), not the 10,000 issue `#96` measured; a scheduled
  run is a demonstration, and bigger volumes are manual triggers. The plan
  was to keep the DAG paused until the pod run passed, on the assumption that
  the first `@daily` run would only fire at 00:00 UTC. That assumption was wrong;
  see "Unpausing fired a run at once" below.
- **New: a failed landing removes its landed shards.** Reading bronze from Spark
  showed that Spark reads every part file under `bronze/`, whether or not the
  partition has a manifest. A run that failed the rejection threshold had left
  its 1,949 valid records in place, and `spark.read.json("bronze/")` counted
  them (3,719 rows instead of the 1,770 that were complete). The rule "a
  partition without `_manifest.json` is incomplete" was therefore only a
  convention. `land_records` now deletes the run's landed prefix on any failure;
  the rejected records stay under `_rejected/` for diagnosis. Verified again on
  the real MinIO (no landed objects after a failed run) and covered by two unit
  tests.
- **New: network errors in the API enrichment.** `OrcidClient` wraps HTTP
  errors but not `requests` timeouts or connection resets, which would have
  aborted the task on the first transient failure. They are now recorded as a
  failed lookup like a 5xx, and the task still fails only when more than half of
  the lookups fail.
- **New: `boto3>=1.35` added to `pyproject.toml` and `uv.lock`, and a root
  `.dockerignore`.** Without the latter, `docker build` with the repository root
  as context would send the ~46 GB `data/` directory to the daemon (issue `#93`'s
  build predates `data/`).
- **Unpausing fired a run at once (D12's assumption was wrong).** Airflow 3's
  cron schedule runs *at* the cron time (the logical date is the trigger time,
  not the start of an interval), and with `catchup=False` the scheduler creates
  the latest missed run. Unpausing at 15:52 UTC therefore created
  `scheduled__2026-09-19T00:00:00+00:00` immediately, and it failed together with
  the first manual run because of the api-server restart described next. Neither
  failure reached the ingestion code. From now on the DAG runs at 00:00 UTC each
  day.
- **The Airflow api-server was killed by its own liveness probe at that moment.**
  Its container ended with exit code 137 at 15:54:49 UTC (liveness
  `timeout=5s`, five failures) and restarted, so the executor's worker pods got
  `Connection refused` from `http://airflow-api-server:8080/execution/` and both
  runs failed before starting a task. The pod already had 4 restarts when this
  session began, so it is a pre-existing fragility of the issue `#91` deployment
  on this WSL2 machine, not something the DAG causes. The failed executor worker
  pods stay in `Error` (Airflow does not delete them on failure) and were removed
  by hand. A re-trigger with a new run id passed.
- **Verification ran from the host first.** The image import into k3s needs the
  user's `sudo`, so the four tasks were first run from the host against the real
  data and the real MinIO (through `kubectl port-forward`), with the credentials
  read from the cluster Secret into the process environment only. The run
  through the DAG's pods is the remaining step.

## Implementation Performed

- `.dockerignore`, `infra/ingest/Dockerfile`, `infra/ingest/README.md`; image
  `tfm-lakehouse/ingest:py3.14` (158 MB, Python 3.14.7, dependencies from
  `uv.lock`), built and smoke-tested locally with `src/` and `schemas/` mounted.
- `src/tfm_lakehouse/bronze/`: `envelope.py` (`RunContext`, `LandingCheck`,
  `build_envelope`), `checks.py` (CVN, ORCID XML and ORCID API checks),
  `landing.py` (`land_records`: Hive-style layout, ~64 MB shards, rejected
  records under `bronze/_rejected/`, idempotent per run, threshold, manifest
  written last, cleanup on failure; `find_landed_runs`), `tasks.py` (the four
  task functions and the `python -m tfm_lakehouse.bronze.tasks` CLI),
  `exceptions.py`, `__init__.py`.
- Object layout: `bronze/source=<orcid_bulk|orcid_api|synthetic_cvn>/ingestion_date=YYYY-MM-DD/run_id=<id>/part-NNNNN.jsonl`
  plus `_manifest.json` in the same directory; rejected records in
  `bronze/_rejected/` with the same layout. `_`-prefixed paths are skipped by
  Spark and Hadoop readers, which is why the manifest and the rejects do not
  appear in a read of `bronze/`.
- `dags/ingest_validate.py`: four `KubernetesPodOperator` tasks in the order
  of D7, hostPath mounts of `src/`, `schemas/` and `data/`, credentials by
  `secretKeyRef`, `security_context` 1000:1000, memory limit 3 Gi,
  `delete_pod`, per-task timeouts (bulk subset 180 min with no retry), `@daily`,
  `catchup=False`, `max_active_runs=1`, eight params.
- Tests: `tests/test_bronze_landing_unit.py` and
  `tests/test_bronze_tasks_unit.py` with the in-memory `tests/bronze_fakes.py`
  S3 (no network, no `moto`).
- `pyproject.toml`/`uv.lock`: `boto3`.
- The DAG was copied to the `dag-processor` pod's DAGs PVC, parsed with no import
  errors, and unpaused; the image `tfm-lakehouse/ingest:py3.14` was imported into
  k3s by the user (`sudo`).

## Verification

Executed 2026-09-19.

- **Unit tests:** `uv run pytest tests/test_bronze_landing_unit.py
  tests/test_bronze_tasks_unit.py` -- 46 passed. A deliberate mutation of the
  idempotent replace made its test fail, so the test is not vacuous.
- **Real data, host-side, against the real MinIO:**
  - subset adoption: counted exactly 301,763 files in 40 s and wrote the marker;
  - synthetic CVN: 1,000 generated (712 linked, 288 unlinked, 0 invalid) in 24 s;
  - API enrichment: 200 of 200 lookups succeeded against the real ORCID API in
    65 s (14.5 MB, ~72 KB per record);
  - landing with the defaults: 270 s total. Read back from MinIO independently of
    the task's own summary: 19,469 bulk records landed in 40 shards (2,688.7 MB)
    plus 531 rejected (22.2 MB); 1,000 synthetic (8.8 MB); 200 API (14.6 MB).
    All 20,669 landed records carry all 12 required envelope fields and the
    right `source`; 0 duplicate `record_id`s;
  - a second run id with the same cap did not land the bulk snapshot again and
    reported the run that had (`landed_by_runs`);
  - re-running the same run id with a cap of 500 replaced its partition: 40
    shards became 2, with no leftovers, and 492 landed / 8 rejected;
  - a run with a 1% threshold failed with exit code 1 on the real 2.5% rate, wrote
    no manifest, and (after the fix above) left no landed objects.
- **Independent read with Spark** (the issue `#93` image, `local[2]`, a throwaway
  pod, deleted afterwards): a read of one source with `basePath` returned the
  expected 1,070 synthetic rows with no duplicate-column error, although the
  envelope's `source` and `ingestion_date` share names with partition
  directories; a read of the whole `bronze/` returned 1,770 rows (208 API, 492
  bulk, 1,070 synthetic), matching the manifests, after the cleanup fix; a read
  of one run directory returned 1,000 rows with `payload` as a `struct`.
- **DAG registration:** copied to `dag-processor`, `airflow dags list-import-errors`
  reported no errors, the four tasks and the `0 0 * * *` schedule appeared, and the
  DAG is paused.
- All verification data was removed afterwards (0 objects under `bronze/`, the
  local run directories deleted, throwaway pods deleted); only the subset marker
  stays, as it is valid state.
- **Full suite, the documented command:** `uv run pytest -n auto tests` -- 577
  passed, 2 skipped (the two `*_live_smoke` tests that need `ORCID_LIVE_TEST=1`)
  in 11 min 36 s. The previous suite (issue `#96`) had 531 passed, so the 46
  new tests account for the difference.
- **Through the DAG's own pods** (2026-09-19, image imported by the user; the
  DAG was unpaused and triggered with the Airflow CLI):
  - a small run (`count=200`, 10 API iDs, `bulk_max_records=200`, run
    `e2e-small-2`): all four tasks `success`; MinIO held 200 synthetic, 10 API and
    198 landed + 2 rejected bulk records, one manifest per source, every record
    carrying the 12 envelope fields, 0 duplicates. The parameters arrived correctly
    rendered (the bulk snapshot id read `records=200`);
  - a run with the default parameters (`e2e-default-1`), 16:04:08 to 16:13:00 UTC,
    about 9 minutes: subset task 20 s (marker present, skipped), synthetic 1,000
    documents 101 s (the host run took 24 s; the pod adds start-up and reads the
    seed files through hostPath), API 77 s, landing 5 min 5 s. MinIO then held
    exactly what the host run had produced: 19,469 bulk records landed in 40
    shards (2,688.6 MB) plus 531 rejected (22.2 MB), 1,000 synthetic (8.8 MB), 200
    API (14.6 MB); 0 records missing a field, 0 duplicate ids, one manifest per
    source;
  - a second default run (`e2e-default-2`), as a later daily run would be: the bulk
    source was skipped (no bulk manifest for that run) and only synthetic and API
    were landed. All 1,000 synthetic `record_id`s were present in both runs, which
    is the fixed-seed limitation, confirmed. That run's partitions were removed
    afterwards so bronze holds the first run only;
  - no task pod was left after any successful run (`on_finish_action="delete_pod"`).
- The DAG was left **unpaused**; the next scheduled run is 2026-09-20 00:00 UTC.
  It will skip the bulk source and land 1,000 synthetic and 200 API records in a
  new partition.

## Findings

- The Open CVN document schema check alone would not have caught what the
  independent Spark read caught: a partial partition is visible to any reader that
  ignores the manifest. The manifest is now a completeness signal backed by
  cleanup on failure, not only a convention.
- Reading the whole of `bronze/` in one `spark.read.json` collapses `payload` to
  `string`, because ORCID bulk payloads are XML strings and the other two sources
  are JSON objects. Issue `#98` should read each source separately (a
  `source=<name>` path), where `payload` keeps its natural type (`struct` for CVN
  and API records).
- The ORCID XML subset is far larger in bytes than in record count: ~42 GB
  (estimate) for 301,763 records. Landing it in full is a deliberate choice, not
  a default.
- The real rejection rate of the bulk records (2.66%) is dominated by profiles
  without a public family name; it is a property of the source, not a bug.
- A cron-scheduled DAG in Airflow 3 runs at the cron time and, with
  `catchup=False`, unpausing it creates the latest missed run immediately, so a
  DAG that must not run on unpause has to be unpaused just before its scheduled
  time or given a `start_date` in the future.
- The API answered 200 of 200 lookups for iDs taken from real ORCID records in a
  2025 snapshot, so no iD had been deleted in that time in this sample.

## Known Limitations

- The Airflow api-server's liveness probe (`timeout=5s`) can kill it under load,
  which fails every task that starts during the restart; it happened once, at the
  first run, and the pod had restarted 4 times before this issue. A re-trigger
  fixes it. Hardening belongs to issue `#102`.
- The bulk-subset task showed `up_for_reschedule` once, in `e2e-small-2` (its first
  executor pod was replaced by a second one about two minutes later, and the task
  then succeeded). The scheduler log shows the state change but I did not find its
  cause; it did not recur in the two later runs.
- hostPath ties the DAG to a single node that shares a disk with the repository
  checkout, and `REPO_ROOT` in the DAG file is an absolute path of this machine.
- The image must be imported into k3s by hand with `sudo` when `pyproject.toml` or
  `uv.lock` change (code changes need no rebuild).
- A fixed seed makes every daily run land identical synthetic documents in a new
  `ingestion_date` partition.
- The ORCID data is a point-in-time 2025 snapshot, and only the first 20,000
  records (in bucket order) are landed by default; that sample is deterministic,
  not random.
- `landed_at` is the start time of the run, not the moment each shard was written.
- The rejected-record threshold (5%) is a judgment, not derived from the source.

## Impact On Future Issues

Issue `#98` (Bronze -> Silver) consumes this DAG's bronze output:

- read each source from its own path (`bronze/source=<name>/`), not the whole of
  `bronze/`: `payload` changes type between sources;
- `_rejected/` and `_manifest.json` are skipped automatically by Spark readers;
  a partition is complete when it has a manifest, and failed runs leave no landed
  shards behind;
- expect the same `record_id` in several `ingestion_date` partitions (the fixed
  seed and the daily schedule): deduplicate on `record_id`, or read the latest
  partition;
- ORCID bulk payloads are raw XML strings, kept byte for byte; parsing them is
  `#98`'s job. ORCID API payloads are the `/record` JSON;
- CVN documents keep the date parts as strings (issue `#96`), whereas the XML
  importer emits integers;
- the ground truth for entity resolution is the synthetic run's `manifest.jsonl`
  under `data/bronze_runs/<run_id>/synthetic_cvn/`, which is not landed into MinIO.

Issue `#101` (benchmark) can scale the volume with the DAG's `count`, `seed` and
`bulk_max_records` parameters.

## Status

`Completed`
