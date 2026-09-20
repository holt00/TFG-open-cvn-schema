# Issue 98 - Bronze -> Silver: Validation & Entity Resolution

## Summary

Full validation, normalization, and cross-source entity resolution from
bronze to silver. First issue of TFM epic phase 3, and the HA01
("adquisición, fusión y análisis de múltiples fuentes") centerpiece of the
whole platform.

## Original Goal

Produce a clean, validated, deduplicated silver layer from the raw bronze
data landed in issue `#97`.

## Original Plan

- implement `src/tfm_lakehouse/spark_jobs/bronze_to_silver.py`
- CVN-side: full validation reusing `src/open_cvn/parser_contract.py`
  rather than reimplementing it
- ORCID-side: rule-based checks (required fields present, ORCID iD checksum
  valid)
- normalize both sources into a common shape
- implement entity resolution: ORCID-iD-first matching between a CVN record
  and an ORCID record when both declare/carry the same iD; fallback
  normalized name/affiliation matching when no iD match is available
  (deterministic only, no ML-based resolution, per the epic)
- write the resulting silver Iceberg tables through the catalog from issue
  `#92`

### Detailed Plan (accepted 2026-09-19)

Planned in a dedicated session before any code, following issues `#91`-`#97`:
every decision the epic and the original plan left open is locked in Task 0
with its reason and the rejected alternative. The three decisions marked
*(user)* (D1, D11, D13) were put to the user, who accepted the recommended
option of each. Work then proceeds task by task; every step states which task
(and subtask) is active, opens with a summary of what it covers, and closes by
stating which files, if any, the user has to modify and the next step. Per D13,
the assistant writes the code, infrastructure files and documentation of this
issue, at the user's explicit instruction to do everything it can without their
intervention and to notify them when something needs them (a `sudo` image import,
for example). Nothing is done for which the information is missing: an unknown is
resolved by a spike or reported to the user, not assumed.

#### Facts established while planning (verified, not assumed)

- **The Spark image cannot run the repository's code as it is.** It runs Python
  **3.10.12** and has neither `pydantic` nor `jsonschema`; the repository
  requires `>=3.14`. PySpark requires the driver and the executors to run the
  same Python minor version, and PySpark 3.5 supports neither 3.13 nor 3.14
  (search of the Spark supportability matrices; not confirmed on the official
  site, so Task 1 re-checks it by running). Running the job in the ingest image
  (3.14) is therefore not an option either.
- **Spike (2026-09-19): `validate_open_cvn_json` runs on the Spark image's
  Python 3.10** once `pydantic` and `jsonschema` are installed
  (`pip install --target`, latest versions), with `src/` and `schemas/` mounted:
  200 synthetic documents validated, 0 invalid, 4.5 s including imports.
  The reuse required by the original plan is feasible without touching the
  parser contract.
- `tfm_lakehouse.bronze.envelope` imports `datetime.UTC` (Python 3.11+), so the
  Spark-side code cannot import the `bronze` package. It needs its own
  Python-3.10-compatible package.
- Issue `#97`'s landing check already calls `validate_open_cvn_json`, the same
  function. Repeating it alone would add nothing; "full validation" must be
  stricter (see D4).
- The document JSON Schema leaves `identity` and every entry's `data`
  free-form (issue `#96`); the generator's `validation.py` shows how to validate
  each entity against its own `$defs` schema.
- Reading JSON Lines with schema inference collapses or widens the payload
  (`payload` becomes a `string` when sources are mixed, issue `#97`) and, for CVN
  documents with heterogeneous entry `data`, would produce a merged struct full of
  nulls. Re-serializing that with `to_json` no longer equals the original document,
  so validation must run on the original JSON text.
- **Overlap between the sources is small at the default landing.** The generator
  draws its seeds uniformly from the 301,763-record subset, while bronze holds
  only the first 20,000 bulk records (issue `#97`, D13), so about 6.6% of the
  synthetic documents have their seed's record in bronze. Plus the 200 API iDs,
  which are sampled from the *linked* documents. With the default 1,000 documents
  the fallback rule has almost no ground-truth positives (about 19 of the 288
  unlinked); a verification run with `count` 10,000 is needed (Task 8).
- Ground truth for resolution is `data/bronze_runs/<run_id>/synthetic_cvn/manifest.jsonl`
  (`seed_orcid_id`, `linkage`, `name_variant` per document); it is not in MinIO.
- The ORCID bulk XML averages 137 KB per record (heavy tail); the bulk source is
  19,469 landed records in 40 shards of about 64 MB by default.
- Iceberg writes through `DataFrameWriterV2` (`writeTo(...).createOrReplace()`,
  `overwritePartitions()`) and `MERGE INTO` are supported on Spark 3.5 (Iceberg
  documentation); the Hadoop catalog on MinIO is proven by issue `#93`.
- Not yet verified when planning, both resolved in Task 1: the exact JSON shape of an
  ORCID API `/record` payload as landed, and the bronze contents in MinIO.

#### Task 0 - Decisions Locked

| # | Decision | Reason | Rejected alternative |
| --- | --- | --- | --- |
| D1 *(user)* | Run everything in **one Spark job on the existing Spark image extended with `pydantic`, `jsonschema` and `requests`** (a new layer and tag, imported into k3s by the user with `sudo`, like `#93`). The code (`src/`) and the schema (`schemas/`) reach the driver and the executors by **hostPath**, as in `#97`'s D2 (executors through `spark.kubernetes.executor.volumes.hostPath.*`). | Keeps the reuse of `open_cvn.parser_contract` the plan asks for, keeps validation and resolution in one distributed job (HA02), and needs no image rebuild for code changes. The spike shows it works. | Two stages, a Python 3.14 pod that validates and parses into a staging area, then Spark for resolution: leaves Spark doing little of the "validation" the issue names and adds a hand-off. Reimplementing validation in pure Python: violates "reuse, do not reimplement". Building Python 3.14 into the Spark image: PySpark 3.5 does not support it. |
| D2 | Spark-side code lives in a new package `src/tfm_lakehouse/silver/` (pure functions: normalization, extraction, resolution rules) and the job entry point in `src/tfm_lakehouse/spark_jobs/bronze_to_silver.py`. It must stay **Python 3.10 compatible** (no `datetime.UTC`, `StrEnum`, `tomllib`); a unit test parses every module with `ast.parse(feature_version=(3, 10))`. `pyspark` is not added to `pyproject.toml`. | The issue and the epic name `spark_jobs/` (issue `#93` put its smoke job in `jobs/`; the epic and issue `#99` say `spark_jobs/`, so that wins). Pure functions are testable on the host's 3.14 with no Spark; the syntax test guards against the one failure the host cannot show. PySpark cannot run on the host's Python 3.14, so DataFrame code stays thin and is verified in the image (Task 8). | Importing `tfm_lakehouse.bronze`: breaks on 3.10. Adding `pyspark` to the project: cannot be installed on 3.14. |
| D3 | Read each bronze source **separately** (`bronze/source=<name>/`) **as text lines** and parse each line's envelope and payload with Python (`json.loads`). Deduplicate on `record_id` keeping the latest `landed_at`, then `ingestion_run_id`. Skip `_rejected/` and manifests (Spark ignores `_` paths). | Preserves the exact document for validation and avoids schema inference (facts above). One code path for the three sources. Partition columns are not needed: the envelope carries `source`, `ingestion_date` and `ingestion_run_id`. | `spark.read.json` with an inferred or explicit struct for `payload`: widens or nulls the heterogeneous `data`. Reading the whole `bronze/`: `payload` collapses to `string` (issue `#97`). |
| D4 | **CVN validation** in three layers: (1) `validate_open_cvn_json` re-run (defence in depth; bronze may come from another producer); (2) entity-level validation of `identity` and every entry's `data` against its own `$defs` schema, promoted from `synthetic_cvn/validation.py` to a neutral module both use; (3) business rules: every declared ORCID iD (type code `140`) has a valid checksum, and every date range has start <= end. Errors send the record to `silver.rejected` with the rule and message; validator warnings do **not** reject, they are kept in `validation_warnings`. | Layer 1 alone equals `#97`'s landing check. Layers 2 and 3 are what the free-form schema lets through (issue `#96`), and they are the bronze -> silver gate the epic describes. `#96` counted warnings as errors because a generator has no excuse for them; a real CV can. | Only layer 1: redundant with landing. Failing on warnings: would reject real CVs for style. Copying `validate_synthetic_document`: duplicates code that already has tests. |
| D5 | **ORCID validation** in silver: iD checksum (`validate_orcid_id`), given and family name present, at least one affiliation or work, well-formed XML/JSON. Same rejection path as CVN. | The epic asks for rule-based checks (required fields, checksum). Names are what the fallback rule needs. Landing already required names and an affiliation for the bulk XML; silver re-checks because it cannot trust the producer. | - |
| D6 | **Common shape** (Iceberg, namespace `lakehouse.silver`): `person_record` (one row per valid record of any source: `record_id`, `source`, `source_ref`, `orcid_id`, `given_names`, `family_name`, normalized name keys, provenance copied from the envelope, `source_last_modified`), `affiliation` (`record_id`, `kind` employment/education, organization, normalized organization, role, department, city, country, start/end year and month), `publication` (`record_id`, title, normalized title, year, DOI, type), `rejected`, `entity_link`, `entity`. | HA01 needs the fusion; `#99`'s candidate indicators (publications per researcher per year, collaboration, career trajectory) need affiliations and publications per resolved entity, and building them here avoids re-parsing in `#99`. Only the four entity types issue `#96` generates are extracted. | Only identity plus affiliations: `#99` would have to re-parse the payloads. Extracting every CVN section: far beyond the four the generator produces and unverifiable here. |
| D7 | **Entity resolution, deterministic, three rules in order.** R1 `orcid_id`: records that carry the same valid ORCID iD (a CVN declaring it, a bulk record, an API record) form one entity, keyed `orcid:<iD>`. R2 `name_affiliation`: a record with **no** iD (an unlinked CVN) is attached to an R1 entity only when block key (normalized family first token + given initial) matches, the name is compatible (family equal or first-surname prefix, given equal or initial; **refined in Task 8.5: at most one of the two may be relaxed**), at least one normalized organization matches (equality or token-set Jaccard >= a threshold fixed in Task 4), and **exactly one** entity qualifies. R3 `singleton`: everything else is its own entity. A record that is ambiguous under R2 stays a singleton and is flagged `ambiguous`. An R1 merge whose names disagree is kept (the iD is authoritative) and flagged `name_conflict`. | Follows the epic (ORCID-iD-first, name/affiliation fallback, no ML). Requiring a unique candidate favours precision over recall: a wrong merge corrupts every indicator downstream, a missed one only splits an entity. The flags make the residual risk measurable. | Probabilistic scoring and thresholds tuned on the data: excluded by the epic. Merging iD-less CVNs with each other: no ORCID anchor to validate against, recorded as a limitation instead. Best-candidate wins on ties: silent wrong merges. |
| D8 | `entity_link` (one row per record: `record_id`, `entity_id`, `match_rule`, `evidence` as a JSON string, flags) and `entity` (`entity_id`, `orcid_id`, display name, record count, sources, rules used). Ids are deterministic: `orcid:<iD>` for anchored entities, `rec:<sha1 of record_id>` for the rest. | An audit trail per link is the "conservar procedencia" requirement applied to fusion; deterministic ids make reruns comparable and `#99` joins stable. | Random UUIDs: break idempotency checks. Hash of the member set: changes whenever a member is added. |
| D9 | Silver is a **full deterministic rebuild** from the current bronze on each run (`writeTo(...).createOrReplace()`); no incremental `MERGE`. | Bronze is small, the transformation is a pure function of it, and a rebuild is trivially idempotent. Incremental processing is a scale concern for later. | `MERGE INTO` per table: more failure modes for no benefit at this volume. |
| D10 | The job takes the bronze root, the catalog namespace and the resolution thresholds as arguments, writes a `TASK_SUMMARY {...}` log line and a JSON summary (counts per source: read, deduplicated, valid, rejected by rule; entities; links per rule; ambiguous; name conflicts). The job fails when the rejection rate of a source exceeds a parameter (default 5%, like `#97`). | Same convention as `#97`; the summary is the input of the memoria's evaluation chapter and of `#101`. | Silent success on a bad source. |
| D11 *(user)* | A provisional manual-trigger DAG `dags/issue98_bronze_to_silver.py` (`schedule=None`, `KubernetesPodOperator` running `spark-submit` in client mode, the `#93` pattern with `on_finish_action="delete_pod"`) runs the job. Issue `#99` absorbs it into `transform_publish`. | Runs the job the way production will, proves HA03 evidence for this stage, and gives `#99` a working launcher to extend. | Only `kubectl` pods: works, but proves nothing about orchestration. Building `transform_publish` here: that is `#99`'s scope. |
| D12 | Evaluation: `src/tfm_lakehouse/silver/evaluation.py` compares `entity_link` with `manifest.jsonl` and reports precision, recall and the confusion per rule over the **evaluable subset** (documents whose seed record is present in silver). | The ground truth exists; without measuring, "resolves correctly" would be an assertion. Restricting to the evaluable subset avoids counting seeds that were never landed as misses. | Judging by a few hand-picked pairs. |
| D13 *(user)* | **Who writes the files: the assistant writes code, infrastructure files and documentation** (the `#97` mode); the user acts only where the assistant cannot (importing an image into k3s with `sudo`, decisions the plan does not settle). | The user's explicit instruction: do everything possible without their intervention, notify them when it is needed, and do nothing for which the information is missing. The repository's default protocol (user writes code and values files) was offered and not chosen. | The default protocol: slower, and the user asked not to be involved. |

Files touched by Task 0: this document; the `#98` row of
`docs/roadmap/tfm/tfm_roadmap.md` (`In Progress`).

#### Task Breakdown

Status in brackets; updated as work proceeds. Estimated effort about 22-26 h,
inside the epic's phase-3 budget (days 8-11).

1. **Task 1 - Branch and feasibility spikes** [done; results in "Adjustments
   Made During Implementation"].
   - 1.1 branch `issue-98-bronze-to-silver-validation-and-entity-resolution`
     from `origin/development` (which already contains `#97`) [done].
   - 1.2 what bronze holds in MinIO now (port-forward, list `bronze/`, read the
     manifests); daily runs may have added partitions.
   - 1.3 inventory the real ORCID XML and API `/record` payloads for silver:
     names, affiliation dates, organization, works, DOIs, `last-modified-date`;
     keep the XML/JSON path table in this document. No emails, biography or
     URLs (issue `#96`'s privacy rule).
   - 1.4 import check on Python 3.10 in the Spark image of every module the job
     will use (`open_cvn.*`, the ORCID checksum, the promoted validation module),
     and the `pip` versions taken from `uv.lock`. `validate_open_cvn_json` itself
     is confirmed [done].
   - 1.5 Spark spikes in a throwaway pod: `spark.read.text` on the 64 MB bulk
     shards (longest line), a Python UDF returning a nested struct, executor
     hostPath volumes, `writeTo(...).createOrReplace()` into `lakehouse.silver`.
   - 1.6 measure the per-record cost of ORCID XML parsing and CVN validation to
     size executors.
2. **Task 2 - Spark image with dependencies** [done; 2.4, the k3s import with `sudo`,
   was done by the user]: layer on
   `infra/spark-conf/Dockerfile` (or a second Dockerfile) adding pinned
   `pydantic`, `jsonschema`, `requests`; new tag; `iceberg-catalog.conf` and
   `infra/spark-conf/README.md` updated; the user imports the image (`sudo`).
3. **Task 3 - Silver library (pure Python 3.10)** [done] in `src/tfm_lakehouse/silver/`.
   - 3.1 `normalize.py`: accent folding (`unicodedata`), case, whitespace, name
     keys, organization normalization, DOI and title normalization.
   - 3.2 `cvn.py`: the three validation layers (D4) and extraction of person,
     affiliations and publications from an Open CVN document. The entity-level
     validation is promoted out of `synthetic_cvn/validation.py`, whose tests
     must keep passing.
   - 3.3 `orcid_xml.py` and 3.4 `orcid_api.py`: validation (D5) and extraction.
   - 3.5 `schemas.py`: the Spark schemas of the six tables, as data.
   - 3.6 unit tests, no Spark and no network (`tests/test_silver_*_unit.py`),
     including the Python 3.10 syntax test.
4. **Task 4 - Entity resolution** [done].
   - 4.1 `resolution.py`: pure functions (name compatibility, organization
     similarity, R2 decision over a candidate list, evidence) and the Jaccard
     threshold, fixed with the data of Task 1.
   - 4.2 R1 in DataFrames; 4.3 R2 (block join, score UDF, unique-candidate
     filter); 4.4 `entity` and `entity_link` with the deterministic ids.
   - 4.5 unit tests: shared iD merges; name variants of the generator
     (`accents_stripped`, `given_initial`, `family_upper`, `first_surname_only`)
     match; same name at a different organization does not; two candidates give
     `ambiguous`; unrelated records stay separate.
5. **Task 5 - Spark job** [done] `spark_jobs/bronze_to_silver.py`: read (D3), deduplicate,
   validate and extract, resolve, write the six tables (D9), summary (D10).
   Also copied into the image or read from the hostPath, decided in Task 2.
6. **Task 6 - Launch** [done; the runs are in Task 8] (D11): `dags/issue98_bronze_to_silver.py`, executor count,
   memory and hostPath configuration, delivery to the `dag-processor` PVC.
7. **Task 7 - Evaluation** [done] (D12): `evaluation.py` and a command that prints the
   report from a run's manifest.
8. **Task 8 - End-to-end verification** [done; 8.5 changed a rule, see "Adjustments"].
   - 8.1 job on the default bronze; counts reconcile: read = landed, valid +
     rejected = deduplicated, entities = person records minus merges.
   - 8.2 an injected invalid CVN and an ORCID record with a bad checksum land in
     `silver.rejected` with the right rule; the rest is unaffected.
   - 8.3 idempotency: a second run gives the same counts and the same entity ids.
   - 8.4 independent read of the six tables from a throwaway pod.
   - 8.5 evaluation on a larger run (`ingest_validate` with `count` 10,000) so the
     evaluable subset contains enough R2 cases; targets: R1 precision and recall
     100%, R2 precision >= 99% (recall reported, not gated). Unrelated records stay
     unmerged.
   - 8.6 the same run through the DAG's pods; no pod left behind.
9. **Task 9 - Full test suite** [done: 753 passed, 2 skipped]: `uv run pytest -n auto tests`, started in the
   background (the documented command).
10. **Task 10 - Documentation close-out** [done]: this document, `current_status.md`,
    `tfm_roadmap.md` (`Completed`), `known_limitations.md`, `infra/README.md`,
    `infra/spark-conf/README.md`, `PROJECT_GUIDE.md`, and `AGENTS.md` if its map
    changes.

#### Risks

- **Airflow api-server liveness probe** (issue `#97`): can fail a run at start; a
  re-trigger fixes it. Hardening is `#102`.
- **Python worker memory** with multi-megabyte XML strings: measured in 1.5/1.6
  before fixing executor memory.
- **Few R2 positives** at the default volume (facts above): addressed in 8.5.
- **Hidden 3.10 incompatibility** in a module the syntax test cannot see (a
  standard-library name): caught by 1.4 and by the real run.
- **Time**: if the budget is at risk, cut in this order: the `publication` table
  and its extraction, then the provisional DAG (run the job with a plain pod),
  then the evaluation on the 10,000 run. Never cut R1, R2, `rejected`, or the
  ground-truth evaluation of R1.

## Adjustments Made During Implementation

- Plan accepted on 2026-09-19 with the decisions above (Task 0). D13 resolved as
  "the assistant writes code, infrastructure and documentation".
- **Task 1 spikes (2026-09-19). They confirm D1-D3 and refine D1 and Task 6:**
  - *1.2, bronze in MinIO.* Only the `#97` run `e2e-default-1` is present: 19,469
    bulk records landed in 41 objects (2,688.7 MB) plus 531 rejected, 1,000
    synthetic CVN, 200 API records, one manifest per source. No daily partition
    exists yet (the first scheduled run is 2026-09-20 00:00 UTC). Under
    `warehouse/` only the `#93` `smoke_test` namespace exists, so no silver table
    exists yet.
  - *1.3, payload inventory.* The landed API payload is the `/record` JSON
    (`orcid-identifier`, `history`, `person`, `activities-summary`, `path`). The
    fields silver reads, and the ones it deliberately does not (biography, emails,
    researcher URLs, other names, addresses: issue `#96`'s privacy rule):

    | Silver field | ORCID bulk XML (record-summary) | ORCID API JSON (`/record`) |
    | --- | --- | --- |
    | ORCID iD | `common:orcid-identifier/common:path` | `orcid-identifier.path` |
    | given / family name | `person:name/personal-details:given-names`, `.../family-name` | `person.name.given-names.value`, `person.name.family-name.value` |
    | last modified | `history:history/common:last-modified-date` | `history.last-modified-date.value` (epoch ms) |
    | employment / education | `employment:employment-summary`, `education:education-summary` | `activities-summary.employments`/`.educations` `.affiliation-group[].summaries[].<kind>-summary` |
    | organization, city, country | `common:organization/common:name`, `.../common:address/common:city`, `.../common:country` | `organization.name`, `organization.address.city`, `organization.address.country` |
    | organization id | `common:organization/common:disambiguated-organization` | `organization.disambiguated-organization` (ROR in the sample) |
    | role, department | `common:role-title`, `common:department-name` | `role-title`, `department-name` |
    | start / end date | `common:start-date/common:year` (`month`, `day`) | `start-date.year.value` (`month`, `day`; strings) |
    | works | `work:work-summary` (`work:title/common:title`, `work:type`, `common:publication-date`) | `activities-summary.works.group[].work-summary[]` (`title.title.value`, `type`, `publication-date`) |
    | DOI | `common:external-ids/common:external-id` with type `doi` | `external-ids.external-id[]` with `external-id-type == "doi"` |

    An API work group can hold several summaries of the same work from different
    sources; silver takes the first one. The API and XML dates are strings, the
    ORCID timestamps of the API are epoch milliseconds.
  - *1.4, Python 3.10 imports (D1 refined).* `open_cvn.parser_contract`,
    `open_cvn.json_import`, `tfm_lakehouse.orcid_client.client`,
    `tfm_lakehouse.synthetic_cvn` and its `validation` module import and run on
    the Spark image's Python 3.10.12, and the strict validation gives 0 errors on
    100 landed documents. **`uv.lock` cannot be pinned as it stands:** its
    `rpds-py 2026.6.3` requires Python >=3.11, so the image pins the three direct
    dependencies (`pydantic==2.12.5`, `jsonschema==4.26.0`, `requests==2.34.2`,
    equal to `uv.lock`) and pins the versions pip resolves for 3.10 for the rest
    (`rpds-py 0.30.0`, `pydantic_core 2.41.5`, `annotated-types 0.8.0`,
    `typing_extensions 4.16.0`, `typing-inspection 0.4.4`, `attrs 26.1.0`,
    `referencing 0.37.0`, `jsonschema-specifications 2025.9.1`, `urllib3 2.8.0`,
    `certifi 2026.7.22`, `charset-normalizer 3.5.1`, `idna 3.20`). The validation
    behaviour is the one the tests cover only if these pins behave as `uv.lock`'s;
    the check is the strict-validation run above, repeated in Task 8.
  - *1.5, Spark mechanics (D1, D3 confirmed).* In a throwaway `client`-mode pod
    with two executors: `spark.read.text` read all 19,469 bulk lines in 39
    partitions (longest line **17.4 MB**, mean 138 KB, so executors need headroom
    for one such line); a Python UDF parsing each line's JSON ran on both
    executors; the executors ran Python **3.10.12** and imported
    `tfm_lakehouse` from `/repo/src` through the executor hostPath volume
    (`spark.kubernetes.executor.volumes.hostPath.*`) and
    `spark.executorEnv.PYTHONPATH`; `writeTo(...).using("iceberg").createOrReplace()`
    into `lakehouse.silver` wrote 1,000 rows and a second `createOrReplace`
    replaced them with 500 (D9 confirmed). The `version-hint.text` warnings of
    `HadoopTableOperations` appear on the first creation and are harmless. The
    spike table was dropped and the pods deleted; only the `warehouse/silver/`
    namespace directory remains, which the job needs anyway.
  - *1.6, cost per record on Python 3.10.* Parsing one ORCID record-summary XML
    (names, affiliations, works, DOIs, via `parse_orcid_summary`) takes 6.7 ms
    (23.6 MB/s; 356 of 360 real records usable); strict validation of one CVN
    (layers 1 and 2 of D4) takes 6.4 ms. Landing-scale silver (19,469 bulk records,
    10,000 CVNs) is therefore about two minutes of CPU in total, and the spike's
    six minutes were dominated by reading the 2.7 GB of shards from MinIO. The
    executor sizing of Task 6 is driven by memory (the 17.4 MB line), not CPU.
- **Resolves the "not yet verified" items of the facts:** the API payload shape and
  the bronze contents are the ones above. Still to be re-checked by running:
  that the Python-3.10 pins reproduce `uv.lock`'s validation behaviour (Task 8).
- **Task 2 (Spark image with dependencies).** `infra/spark-conf/Dockerfile.silver`
  and `requirements-silver.txt` layer the pinned libraries on the `#93` image;
  built locally as `tfm-lakehouse/spark-py:3.5.9-iceberg1.11.0-silver` (2.54 GB,
  +20 MB) and checked as uid 185: Python 3.10.12, 200 documents pass the strict
  validation, the Iceberg jars are intact. **`iceberg-catalog.conf` is not
  changed:** it names the `#93` image for the executors, so the silver launcher
  overrides `spark.kubernetes.container.image`; changing the shared file would
  have altered the `#93` DAG for no benefit. Documented in
  `infra/spark-conf/README.md`. Importing the image into k3s needs the user's
  `sudo` (subtask 2.4).
- **Task 3 (silver library), design choices not fixed by the plan:**
  - *Where the shared entity validation lives.* D4 said "a neutral module".
    It is `src/tfm_lakehouse/cvn_validation.py`, and it exposes two functions,
    `entity_schema_errors` and `orcid_identifier_errors`, instead of one, so the
    silver rejection can name the rule (`cvn_entity_schema` versus
    `cvn_orcid_checksum`). `synthetic_cvn/validation.py` now composes them; its 23
    tests pass unchanged. One visible difference: the ORCID error is listed after
    the section errors instead of before them; no test depends on the order.
  - *One place for the common shape.* `silver/records.py` builds every
    `person_record`, `affiliation` and `publication` row for the three sources, so
    the shape and the normalized keys cannot drift between extractors;
    `silver/orcid_common.py` holds what the two ORCID extractors share (rule
    names, the result type, the D5 required-field rule). Both extractors
    accept the payload as landed: `process_cvn_document` takes the JSON text or the
    parsed object (the job passes the parsed payload, avoiding a re-serialization).
  - *Table schemas are data, not PySpark types* (`silver/schemas.py`, column
    lists and DDL strings), because PySpark cannot be imported on the host's
    Python 3.14; a test checks the columns against the dicts `records.py` builds.
    Only the four tables Task 3 needs exist there (`person_record`, `affiliation`,
    `publication`, `rejected`); `entity_link` and `entity` are added in Task 4.
  - *Normalization* (`silver/normalize.py`): accents and case folded through
    `unicodedata`, punctuation removed; family-name **particles** (`de`, `del`,
    `la`, `van`, ...) are skipped when choosing the blocking key, so that
    "de la Torre" is keyed `torre` and not `de`; organizations reduce to their
    **sorted, stop-word-free tokens** with URLs removed (the real data has names
    such as `Instituto de Salud Carlos III; https://ror.org/00ca2c886`), so word
    order does not matter and a Jaccard similarity can be computed; DOIs lose the
    `https://doi.org/` and `doi:` prefixes and are lower-cased.
  - *Extraction conventions*, the same on the XML and the API: every employment
    and education summary is an affiliation; **one work summary per work group** is
    a publication (the summaries of a group are the same work from different
    sources), with the DOI of the summary or, if absent, of the group; CVN
    publications keep their author list (`authors`), which ORCID work summaries do
    not have; CVN countries are numeric ISO 3166 codes and only Spain (`724`) is
    mapped to `ES`, the others stay null (recorded as a limitation, and not used
    for matching); a CVN that declares several ORCID iDs keeps the first and gets a
    warning.
  - *Rejection rules* (the `rules` column of `silver.rejected`):
    `cvn_json_parse`, `cvn_schema`, `cvn_entity_schema`, `cvn_orcid_checksum`,
    `cvn_required_field`, `cvn_date_order`, `orcid_xml_parse`, `orcid_json_shape`,
    `orcid_id_checksum`, `orcid_required_field`, `orcid_no_activity`. A CVN is checked
    by all its layers and reports every failing one, not only the first.
  - *Checked on the real bronze data* (host, Python 3.14): 1,000 of 1,000
    synthetic CVNs valid (712 carry an ORCID iD, exactly the linked ones of `#97`;
    2,283 affiliations, 8,873 publications; 10.7 s); 200 of 200 API records valid
    (710 affiliations, 4,789 publications); 317 of 320 sampled bulk XML records
    valid, the 3 rejected for a missing name (`#97`'s known 2.7%), and the XML
    extractor agrees with `#96`'s `parse_orcid_summary` on which records are
    usable and on the affiliation count of all 317.
  - *Tests:* `tests/test_silver_normalize_unit.py`, `..._extraction_unit.py`,
    `..._schemas_unit.py`, `..._python310_unit.py` and the fixtures module
    `tests/silver_fixtures.py` (ORCID XML/API records with the real container
    structure, CVN documents built by the `#96` generator). The Python 3.10 test
    parses `open_cvn/`, the silver, `orcid_client/` and `synthetic_cvn/` modules
    with `ast.parse(feature_version=(3, 10))` and forbids `tomllib`,
    `datetime.UTC`, `StrEnum` and any import of `tfm_lakehouse.bronze` in silver
    code. 101 new tests; with `#96`'s, 124 passed.
  - `src/tfm_lakehouse/spark_jobs/__init__.py` was created (empty) for Task 5.
- **Task 4 (entity resolution), decisions and findings:**
  - *The organization threshold is 1.0 (equal normalized names), decided with
    measured data, not by preference.* D7 left "a threshold fixed in Task 4".
    Jaccard on the identity-carrying tokens of real organization names: the same
    institution with a campus or faculty suffix scores 0.60 (`Universidad Autónoma
    de Madrid` against `... Facultad de Ciencias`) and 0.40 (`Universitat Jaume I`
    against `... - Campus de Riu Sec`), while two different institutions score
    higher, 0.67 (`Universitat de València` against `Universitat Politècnica de
    València`). No threshold therefore separates the two cases, and any value
    below 0.7 would merge different institutions. Equality is the only safe default;
    `org_threshold` stays a parameter so Task 8 can report the effect of lowering
    it. Spanish/English translations of the same institution score 0.00 and are not
    matched (a limitation, not solvable by token overlap).
  - *Rules as implemented at this point* (`silver/resolution.py`; Task 8.5 later added the
    rule that at most one of the given and family name may be relaxed, see there):
    a record without iD joins an iD-anchored entity only if a member of that entity
    has the same block key (family key and given initial), a compatible name, and
    the **entity's organizations** (the union over all its records, so an entity
    with a bulk record at an old employer and an API record at a new one matches
    either) contain one equal to the record's; exactly one entity may qualify.
    Name compatibility: family names equal or one a leading part of the other
    (people drop their second surname); given names equal, or one side only
    initials (`a`, `j a`) matching the other's initials. Records without iD are
    never merged with each other (no ORCID anchor to check against), and a record
    with no affiliation cannot be matched by name alone; both are recorded
    limitations.
  - *`name_conflict`* is set on an iD-merged CVN whose name is compatible with none
    of the ORCID records sharing its iD; the merge is kept because the iD is the
    authoritative key.
  - *Determinism.* Entity ids are `orcid:<iD>` or `rec:<sha1(record_id)>` (Spark's
    `sha1` equals Python's); candidates are listed sorted; the matched record is the
    smallest `record_id`; the entity's display name comes from the ORCID API record,
    else the bulk record, else the CVN, then the most recently modified, then the
    smallest `record_id`. Evidence is compact JSON with sorted keys.
  - *Two implementations of the same rules, on purpose.* `resolve_in_memory` is
    plain Python and the oracle; `resolution_spark.py` is the DataFrame version the
    job runs (block join on family key and given initial, then the shared
    `names_compatible` and `best_org_similarity` as UDFs, so the comparison logic
    exists once). PySpark cannot run on the host, so
    `tests/test_silver_resolution_spark.py` runs the DataFrame version in local mode
    inside the Spark image and compares links, evidence, flags and entities with the
    oracle on a 40-ORCID-record scenario with colliding names, at thresholds 1.0 and
    0.5: identical, and the scenario exercises every rule, `ambiguous` and
    `name_conflict`. It skips itself without Docker or the image (CI has neither).
  - *Finding, again:* running the image as uid 185 needs its `/opt/entrypoint.sh`
    (it patches `/etc/passwd`); going around it fails with
    `basedir must be absolute: ?/.ivy2/local`, the same root cause issue `#93`
    recorded.
  - *Tests:* `tests/test_silver_resolution_unit.py` (31, pure) and the parity test
    (2). The name-variant test feeds `vary_name`, the generator's own function, so
    the four variants issue `#96` produces are matched against by construction.
- **Task 5 (Spark job), decisions and findings:**
  - *Structure* (`spark_jobs/bronze_to_silver.py`, `silver/pipeline.py`).
    `pipeline.process_bronze_line(source, line)` is the pure per-record function
    (envelope check, then the CVN, ORCID XML or ORCID API processing of
    Task 3) and returns a tuple shaped as `schemas.RESULT_COLUMNS`; the job wraps it in one
    Python UDF per source. A line that is not an envelope with a `payload` and a
    `record_id` is rejected by the rule `bronze_envelope` (a record without an id
    could be neither deduplicated nor linked; the job gives it a
    `unidentified:<sha1>` id so it still lands in `silver.rejected`).
  - *Deduplication before parsing.* The envelope fields are extracted with
    `get_json_object` in the JVM and the winner per `record_id` (latest
    `landed_at`, then greatest `ingestion_run_id`) is chosen with `max(struct(...))`,
    so the Python workers only parse records that survive, and never parse a
    duplicate of a multi-megabyte XML. The number of copies read is kept, so the
    summary reports `read`, `deduplicated` and `duplicates_dropped`.
  - *The rejection threshold is checked before anything is written* (default 5%,
    per source, like `#97`): a source above it makes the job exit 1 and leaves the
    existing silver tables untouched, so a bad bronze run cannot replace a good
    silver. Tested.
  - *Tables* are written with `writeTo(...).using("iceberg").createOrReplace()` after
    `_conform` selects and casts every column to the definition in `schemas.py`.
    The link DataFrame is cached before it is projected so `entity` reuses it.
  - *`--shuffle-partitions` (default 16) is a parameter.* First local run over a
    217 MB sample (3 bulk shards, the CVNs, the API records) took 224.9 s and the
    log showed `Submitting 600 missing tasks` per join stage: Spark's default of 200
    shuffle partitions turns each join of this job into hundreds of tiny tasks that
    each start a Python worker. With 16 it took 54.7 s with identical results.
    Volume runs (`#101`) should raise it.
  - *Real-data finding that changed a rule.* The first run reported one
    `name_conflict` that was not the injected one: a CVN seeded from the 2025 ORCID
    snapshot says `Ana M` while the 2026 API record for the same iD says
    `Ana María`. The name rule accepted only pure initials, so the rule
    `names_compatible` now also accepts the same number of given names where each
    pair is equal or one is the initial of the other (a spelled-out initial), and
    still rejects a dropped given name. Tests added; the parity test still passes.
  - *Verified locally in the Spark image (local mode) on real bronze data downloaded
    from MinIO, with injected cases:* `orcid_api` 200 valid; `orcid_bulk` 1,531 read
    (3 real shards plus 1 injected record with a bad checksum), 1 rejected
    (`orcid_id_checksum`); `synthetic_cvn` 1,003 lines read, 1,002 after dropping
    the newer copy of a document (the surviving row carries the newer run, checked in
    the table), 2 rejected (`bronze_envelope` for an injected non-JSON line,
    `cvn_entity_schema` for an injected invented field); 2,730 person records, 2,526
    entities, links `orcid_id` 2,442, `name_affiliation` 1, `singleton` 287; 203
    entities fuse a CVN with an ORCID record. A second run on the existing tables
    gave identical counts. The tables were read back from a separate session (schemas,
    rejected rows, no duplicate entity ids, no link without a person record).
  - *The R2 rule finds few pairs in this sample* (1) because the sample holds 3 of
    40 bulk shards: it is the small-overlap fact of the plan, not a defect. The
    evaluation of Task 8.5 uses the full landing and a larger CVN run.
  - *Tests:* `tests/test_silver_pipeline_unit.py` (13, pure) and
    `tests/test_silver_job_spark.py` (3, run the real job in the image against a
    small bronze tree: validation, deduplication, all three rules, the six tables,
    the threshold failure that writes nothing, and the no-data failure). Helper
    `tests/spark_image.py` starts containers through the image entrypoint. All
    Spark tests skip without Docker and the image.
- **Task 6 (launch through Airflow), decisions:**
  - *Sizing from the real node.* The node has 16 CPUs and about 10 GB of memory
    available, and issue `#97`'s spike showed a single ORCID line can be 17.4 MB. The
    DAG defaults to two executors of 1 GB heap plus **1 GB memory overhead** (the
    Python workers that parse the XML live in the overhead, not the heap), one
    core each, and a 1 GB driver in a pod limited to 2 GiB: about 6 GiB in
    total. All of it is a DAG parameter (`executors`, `executor_memory`,
    `executor_memory_overhead`, `shuffle_partitions`, `rejection_threshold`,
    `org_threshold`), so issue `#101` can scale it without editing code.
  - *`dags/issue98_bronze_to_silver.py`* follows issue `#93`: the
    `KubernetesPodOperator` pod is the Spark driver in `client` mode and runs
    `spark-submit` through `/opt/entrypoint.sh`. It overrides
    `spark.kubernetes.container.image` with the silver image (see Task 2), mounts
    `src/` and `schemas/` read-only and `data/` read-write with hostPath on the
    driver, and mounts `src/` and `schemas/` on the executors through
    `spark.kubernetes.executor.volumes.hostPath.*` (they run the validation UDFs, and
    `schemas/` is where `open_cvn.schema.json` is resolved from). `data/` is writable
    by the image's uid 185 (checked), which is where the summary JSON goes. The
    pod is deleted when it finishes (`on_finish_action="delete_pod"`, what `#93`
    deferred to the real DAGs). `schedule=None`: it is manual, and `#99` absorbs it into
    `transform_publish`.
  - *Delivered and checked without running it:* copied to the `dag-processor` PVC
    with `kubectl cp`, `airflow dags list-import-errors` reported no errors, the task is
    listed, and `airflow tasks render` produced the expected command (parameters,
    hostPath options and the summary path with `:` and `+` replaced). The DAG is
    **paused and has not been triggered**, because the silver image is not in k3s yet
    (a pod check with `imagePullPolicy: Never` reported `ErrImageNeverPull`); the
    import needs the user's `sudo` (subtask 2.4).
- **Task 7 (evaluation), decisions:**
  - *What is measured* (`silver/evaluation.py`). The generator's manifest gives, per
    document, the ORCID iD it was seeded from and how it was meant to be linked, so
    the true entity of a document is `orcid:<seed>`. For documents that declare the
    iD (rule R1) the report counts those in their seed's entity and those fused with
    an ORCID record present in silver. For documents meant to be found by name
    (rule R2) it reports the *evaluable* ones (whose seed record is in silver), the
    merges, the correct and false merges, **precision** (correct/merged), **recall**
    (correct/evaluable), why the missed ones were missed (ambiguous, no candidate,
    merged with the wrong person), and recall per name variant.
  - *A merge of a document whose seed is absent counts as a false merge*, not as
    "unevaluable": nothing correct could have been merged with it, so it is the direct
    measure of the plan's "unrelated records remain unmerged".
  - *Where it runs.* Inside the job (`--manifest`, and the DAG parameter
    `ground_truth_run_id`, empty by default = no evaluation): the entity links and the
    ORCID iDs are small (thousands of rows), so the driver collects them and the
    pure function computes the report, which is logged and added to the summary. No
    second Spark application is needed.
  - *First real report* (the 217 MB local sample, real manifest): 712 of 712 documents
    declaring their iD sit in their seed's entity, 202 of 202 fuse with an ORCID
    record (200 API records plus 2 bulk records); of the 288 documents meant to be found
    by name only 1 has its seed record in this sample (3 of 40 bulk shards), and it was
    found. This confirms that a meaningful R2 measurement needs the full landing and a
    larger CVN run (Task 8.5).
  - *Tests:* `tests/test_silver_evaluation_unit.py` (5) and the job test, which now
    checks the evaluation section of the summary.
- **Task 8 (verification in the cluster), 8.1-8.4 (2026-09-19).** The user imported the
  silver image into k3s (subtask 2.4); a `imagePullPolicy: Never` pod then confirmed
  it. Every run below is the `issue98_bronze_to_silver` DAG, triggered with the
  Airflow CLI and `ground_truth_run_id=e2e-default-1`, two executors.
  - *8.1, the bronze `#97` left in MinIO (run `e2e98-1`, success, 573 s).* The counts
    equal the `#97` manifests exactly: 19,469 bulk, 1,000 CVN and 200 API records read,
    0 duplicates, 0 rejected (the 531 bulk records `#97` rejected never entered
    bronze). Tables: `person_record` 20,669 (= 19,469 + 1,000 + 200), `affiliation`
    76,169, `publication` 451,774, `rejected` 0, `entity_link` 20,669, `entity` 20,393.
    Links: 20,381 `orcid_id`, 16 `name_affiliation`, 272 `singleton`; 0 ambiguous, 0
    `name_conflict`; 256 entities fuse a CVN with an ORCID record. The evaluation
    against the real manifest: 712 of 712 documents that declare their iD are in their
    seed's entity, 240 of them fused with their ORCID record (the 240 with an ORCID
    record in silver); of the 288 documents meant to be found by name, 16 have their
    seed record in silver and **all 16 were merged correctly, 0 false merges** (the
    other 272 have no counterpart and none was merged with anybody). Executor and
    driver pods were deleted afterwards (`delete_pod`), and the driver wrote
    `data/silver_runs/<run>/summary.json` through its hostPath.
  - *8.4, independent read (a separate throwaway pod, its own Spark session, local
    mode).* Counts equal the job's; 15 integrity checks pass: no duplicate
    `record_id` or `entity_id`; every link has a person record and every person record
    a link; every link's entity exists and every entity has links;
    `sum(record_count)` equals the person records; no orphan affiliation or
    publication; no record both valid and rejected; every stored ORCID iD matches the
    pattern and every ORCID-source record has one; every `orcid_id` link points to
    `orcid:<own iD>` and every singleton to `rec:<sha1(record_id)>`.
  - *8.2, invalid cases injected into the real bronze (run `e2e98-2`, success, 227 s).*
    One partition `run_id=inject-98` was added with: a CVN with an invented field, a
    non-JSON line, a bulk XML with a bad checksum, an API record without a family name,
    and a newer copy of CVN `SYN-42-00000001` with another given name. Result: reads
    +1 API, +1 bulk, +3 CVN; `duplicates_dropped` 1; valid counts unchanged;
    `rejected` had exactly 4 rows with the rules `orcid_required_field`,
    `orcid_id_checksum`, `cvn_entity_schema` and `bronze_envelope`, read back
    independently with their messages; the surviving row of the duplicated CVN carried
    the newer name and run (`inject-98`); the other tables kept their counts.
  - *8.3, idempotency (run `e2e98-3`, after deleting the injected objects, success,
    197 s).* A content digest (SHA-1 of the sorted rows) per Iceberg snapshot, read from
    the table history: the digests of snapshot 3 equal those of snapshot 1 for all six
    tables, and snapshot 2 differs exactly where the injection changed data
    (`rejected`, `person_record`, `entity`). Full rebuilds with identical input are
    therefore identical, including every entity id. The three snapshots of each table
    remain in the Iceberg history.
  - *The first run was 2.5 times slower than the next two (573 s against 227 s and
    197 s)* with identical parameters and data; the first run started executor pods
    and read the 2.7 GB of shards with a cold cache. Issue `#101` should therefore
    discard a first run when measuring.
- **Task 8.5 (evaluation at scale) and what it changed.** The ingest DAG was triggered
  with `count=10000` and `seed=43` (run `e2e98-big`, 10 minutes: 10,000 CVNs of which 7,098
  declare their iD and 2,902 do not, 200 new API records, the bulk source skipped as
  already landed). A different seed gives new `record_id`s, so bronze now holds
  those 10,000 CVNs beside the earlier 1,000. Silver was rebuilt from it with
  `ground_truth_run_id=e2e98-big`: 30,868 person records (19,469 bulk, 399 API,
  11,000 CVN), 0 rejected.
  - *First result (run `e2e98-4`), and why it is not the one to quote.* Rule R1:
    **7,098 of 7,098** declaring documents in their seed's entity, 658 fused with their
    ORCID record. Rule R2: precision **90.8%** (138 correct of 152 merged), recall
    76.7%. This **missed the plan's own target** (R2 precision >= 99%), so the cases
    were analysed before deciding anything.
  - *The evaluation itself was too strict, and was fixed.* It counted as "evaluable"
    only documents whose seed has an ORCID-source record, so a correct merge into an
    entity anchored by *another CVN that declares the same iD* (documents of the
    earlier seed-42 run) was reported as a merge without a counterpart. A document
    now has a counterpart when any silver record carries its seed's iD
    (`anchored_orcid_ids`); evaluable documents go from 180 to 186. The oracle was also
    indexed by block key: it went from unusable at 30,000 records to 0.3 s and its links
    were verified identical to the cluster's on all 30,868 records.
  - *Recall is at its ceiling.* 47 of the 186 evaluable documents have **no
    affiliation at all** (the generator only emits an entry when the ORCID affiliation
    has dates), and without an organization the rule has no evidence by design
    (D7). Ceiling 74.7%; the rule found 138, 74.2%, that is 99.3% of what is
    reachable. The 48 missed documents are 47 of those plus 1 other.
  - *The false merges have one cause.* All 14 shared exactly **one** organization
    (the 78 merges with two or more shared organizations were 78 of 78 correct), and
    by the kind of name match: identical folded names 79 correct and 2 false;
    given name relaxed with an equal family name 47 and 0; family name shortened to
    its first surname with an equal given name 12 and 4; **both relaxed at once 0 correct
    and 8 false** (`I. García` against `Irene García Meilán`). Of the 3 "false"
    merges into CVN-anchored entities that looked suspicious, 3 were correct once the
    counterpart definition was fixed, and one of the remaining `full` cases
    (`Maria Angeles Fernandez-Zamudio` in two ORCID iDs, same university) is very likely
    the same person with two ORCID profiles, which the seed-iD ground truth cannot
    express.
  - *Decision: forbid relaxing both names at once (a refinement of D7).*
    `resolution.name_match_kind` now classifies a match as `full`, `given_variant`
    (family equal, given name relaxed) or `surname_prefix` (given equal, family
    shortened) and rejects a name that differs in both; `names_compatible` is defined
    from it, so the Spark job and the oracle share it. It removes 8 false merges and
    **no correct one**. The link's `evidence` now also carries `name_match` and
    `shared_organizations`, so a consumer such as `#99` can demand more than the rule
    does (for example two shared organizations) without a re-run.
  - *Result of the rule change, run through the DAG (`e2e98-5`, success, 320 s):* R2 merged
    144, **138 correct, 6 false, precision 95.8%, recall 74.2%**, 0 ambiguous, R1 still
    7,098 of 7,098; precision by name variant unchanged in recall (given initial 47 of 60,
    first surname only 12 of 19, family upper-cased 26 of 31, exact 43 of 59, accents
    stripped 10 of 17). This is exactly what the offline simulation on the exported tables
    predicted.
  - *The 99% target is not met and is not going to be met by tuning.* The 6 remaining false
    merges are people with the same name and one shared organization, indistinguishable
    from a real match with this evidence. The measured options: additionally requiring two
    shared organizations for a shortened family name gives 133 merged, 131 correct, 2 false
    (precision 98.5%) but recall 70.4% (7 correct merges lost to avoid 4 false), and still
    not 99%; requiring two shared organizations for every non-identical name gives 98.3% and
    62.9%; for any merge, 100% and 41.9%. **Not adopted by default** (recall cost against
    a precision gain that still misses the target); available through the evidence
    fields. The figure to quote is 95.8% precision and 74.2% recall on 186 evaluable
    documents, against a synthetic ground truth (see the limitation).
  - *Organization threshold sensitivity (the sweep planned for this task, with the
    oracle on the exported tables):* thresholds 1.0, 0.8, 0.67 and 0.6 give identical
    results (144 merged, 138 correct, 6 false); 0.5 gives 147 merged, 136 correct, 11
    false and 2 ambiguous; 0.34 gives 149, 136, 13 and 2. Lowering the threshold never
    helped on this data, which confirms 1.0.
  - *Independent read of the final state (run `e2e98-5`):* 15 of 15 integrity checks pass on
    30,868 person records, 99,979 affiliations, 543,879 publications, 29,767 entities.
  - *8.6, through the DAG's pods:* every run above (`e2e98-1` to `e2e98-5`) was the
    `issue98_bronze_to_silver` DAG; after each, the Airflow worker pod, the Spark
    driver pod and the executors were gone.
  - *State left in the cluster:* MinIO bronze holds `#97`'s run `e2e-default-1` plus
    the `e2e98-big` partition (10,000 synthetic CVNs and 200 API records, seed 43);
    `lakehouse.silver` holds the rebuild of run `e2e98-5` (five snapshots per table in the
    Iceberg history). The DAG `issue98_bronze_to_silver` is unpaused (it has no schedule).
    The scheduled `ingest_validate` run of 2026-09-20 00:00 UTC succeeded and added one
    more partition of the same 1,000 synthetic documents and 200 API records, which silver has
    not read yet: the next rebuild deduplicates it on `record_id`.
  - *Test infrastructure fix.* The Spark tests wrote files as the image's uid 185 into
    pytest's temporary directories, which pytest then could not delete (a
    `PermissionError` warning and leftover directories in `/tmp`). `tests/spark_image.py` now
    runs the container as the host uid with group 0, which the image's entrypoint
    registers; the old leftovers were removed with a throwaway root container.

## Implementation Performed

- `src/tfm_lakehouse/silver/`: `normalize` (accent folding, name keys, organization
  tokens, DOI), `records` (the common shape), `cvn` (three validation layers and
  extraction), `orcid_xml` / `orcid_api` / `orcid_common` (D5 validation and extraction),
  `pipeline` (one bronze line to silver rows), `schemas` (table definitions as data),
  `resolution` (deterministic rules, in-memory oracle), `resolution_spark` (the same
  rules as DataFrame joins), `evaluation` (precision and recall against the
  generator's manifest). All Python 3.10 compatible.
- `src/tfm_lakehouse/cvn_validation.py`: entity-level validation promoted out of
  `synthetic_cvn/validation.py` (which now composes it; its tests are unchanged).
- `src/tfm_lakehouse/spark_jobs/bronze_to_silver.py`: reads each bronze source as text,
  deduplicates on `record_id`, validates and normalizes, checks the rejection threshold
  before writing, resolves entities, writes the six `lakehouse.silver` Iceberg tables,
  and logs and writes a summary (with the evaluation when given a manifest).
- `infra/spark-conf/Dockerfile.silver` and `requirements-silver.txt`: the Spark image
  with pydantic, jsonschema and requests (built and imported into k3s); section in
  `infra/spark-conf/README.md`.
- `dags/issue98_bronze_to_silver.py`: manual-trigger DAG (Spark driver in a
  `KubernetesPodOperator` pod, hostPath for `src/` and `schemas/` on driver and
  executors), delivered to the Airflow PVC.
- Tables: `person_record`, `affiliation`, `publication`, `rejected`, `entity_link`,
  `entity` (column definitions in `silver/schemas.py`).
- Tests (all new files prefixed `test_silver_`, plus `silver_fixtures.py`,
  `spark_image.py`, `spark_resolution_runner.py`): normalization, extraction of the
  three sources, schemas, Python 3.10 guards, pipeline, resolution rules, evaluation,
  and three Spark tests that run in the Spark image in local mode (parity of the
  DataFrame resolution with the oracle, and the whole job).

## Verification

Executed 2026-09-19 (details of every step in "Adjustments Made During Implementation").

- **Unit and local Spark tests:** `uv run pytest -n auto tests` -- 753 passed, 2 skipped (the two `*_live_smoke` tests that need `ORCID_LIVE_TEST=1`) in 8 min 20 s, against 577 passed at the end of issue `#97`; the 176 new tests include three that run Spark in the Spark image and skip without Docker and the image. One earlier attempt of the same command ended with 747 passed and one *collection* error in a TFG test (`test_generation_pipeline_parse_smoke.py`: `SyntaxError: source code string cannot contain null bytes` importing `generated.tree_model`). The file passes on its own, `src/generated/` had no null bytes or git changes afterwards, and the repeat was clean: it is an intermittent race between xdist workers, one importing the generated package at collection time while another regenerates it in place (`tests/xsdata_generation_lock.py` serializes the regenerating tests but not that import). It predates this issue and was not changed here.
- **Real bronze in MinIO, through the DAG's pods (Tasks 8.1-8.6):** counts equal the
  `#97` manifests exactly; 15 of 15 independent integrity checks pass; injected invalid
  records are rejected with the right rules and a duplicate keeps its newest copy; a
  rebuild of the same input is identical (per-snapshot content digests of all six tables
  equal, entity ids included); no pod is left behind.
- **Resolution against the ground truth, 1,000 documents (default landing):** 712 of 712
  documents declaring their iD in their entity; the 16 documents meant to be found by name
  that had a counterpart were all merged correctly, with 0 false merges.
- **Resolution against the ground truth, 10,000 documents (186 evaluable):** rule R1 7,098
  of 7,098; rule R2 precision 95.8%, recall 74.2% (138 correct, 6 false of 144 merged; the
  recall is at its ceiling of 74.7%). The plan's 99% precision target for R2 was not met;
  see "Findings".

## Findings

- Measuring against a ground truth found what unit tests could not: the first large run
  gave R2 precision 90.8%, and analysing the cases showed one weak-evidence combination
  (a relaxed given name **and** a shortened family name) that was wrong 8 of 8 times and
  cost nothing to forbid, and an evaluation that under-counted correct merges.
- Precision is governed by the number of shared organizations: every merge with two or more
  was correct (78 of 78), all 14 initial false merges shared one. Recall is governed by
  the data: without an affiliation there is no evidence, and 25% of the evaluable
  documents have none.
- A real data quirk changed a rule during Task 5: a CVN seeded from the 2025 ORCID
  snapshot says `Ana M` while the 2026 API record says `Ana María`.
- The overlap between the CVN and ORCID sources is a property of how the landing was
  sampled (about 6.5% of the bulk subset against seeds drawn from all of it): 16 evaluable
  documents at the default volume, 186 at 10,000. Any volume experiment (`#101`) changes
  the number of matches, not only the runtime.
- Silver is a pure function of bronze: rebuilds are byte-for-byte identical in content,
  so the Iceberg snapshot history is a free audit trail of what each rebuild changed.
- The first Spark run of a session is 2.5 times slower than the following ones (573 s
  against 197 s to 227 s for the same input).
- Spark's default 200 shuffle partitions made this job 4 times slower on small data
  (225 s against 55 s with 16).
- The bundled Spark Python (3.10) is what decides the language level of everything the job
  imports; that constraint reached into shared code (`cvn_validation`) but not into the
  parser contract, which needed no change.

## Known Limitations

Recorded in `docs/pipeline/known_limitations.md`: the job runs on Python 3.10 with a
dependency set that is not exactly `uv.lock`'s; entity resolution is deterministic and
conservative (rule R2 precision 95.8% and recall 74.2% at 10,000 documents, below the
plan's 99% precision target); silver extracts only the four CVN entity types the generator
produces; silver is rebuilt in full on every run; resolution quality is measured only
against the synthetic generator's ground truth. Per the epic, ML-based or probabilistic
entity resolution is out of scope.

## Impact On Future Issues

Issue `#99` (Silver -> Gold) consumes this silver output:

- read the six tables of `lakehouse.silver`; `entity_id` is the person key and is stable
  across rebuilds (`orcid:<iD>` or `rec:<sha1>`); `entity_link.evidence` carries
  `name_match` and `shared_organizations` for rule R2 merges, so an indicator that needs
  fewer false merges can filter on them without a new run;
- `publication` has one row per work (`authors` only for CVN publications), `affiliation`
  one per employment or education entry with `start_*`/`end_*` and normalized organization;
  the same real person appears once per `entity_id` but a publication can be reported by
  several records of the entity (a CVN and an ORCID record), so deduplicate on
  `(entity_id, doi)` or `(entity_id, title_norm, year)` before counting;
- `issue98_bronze_to_silver` is the launcher to absorb into `transform_publish`; it takes
  its sizing as DAG parameters;
- bronze now also holds the `e2e98-big` partition (10,000 synthetic CVNs), so silver has
  30,868 person records, not the 20,669 of the default landing.

Issue `#101` (benchmark) measures this job: discard the first run of a session, raise
`--shuffle-partitions` for volume, and note that the number of R2 matches depends on the
landing sample.

## Status

`Completed`
