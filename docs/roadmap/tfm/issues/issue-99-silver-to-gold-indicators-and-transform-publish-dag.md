# Issue 99 - Silver -> Gold: Indicators & `transform_publish` DAG

## Summary

Compute the final research indicators and publish them to both Iceberg and
PostgreSQL, and wire the `transform_publish` DAG. Closing issue of TFM epic
phase 3.

## Original Goal

Have gold-layer indicator tables available for BI (issue `#100`) and the
memoria's evaluation chapter, materialized somewhere Superset can query with
no extra query-engine dependency.

## Original Plan

- finalize the exact 2-3 indicators from the epic's candidates (publications
  per researcher per year, co-authorship/collaboration pairs, career
  trajectory/affiliation timeline); per the epic's scope cut list, reduce to
  1 indicator first if the time budget is tight
- implement `src/tfm_lakehouse/spark_jobs/silver_to_gold.py` computing them
  from issue `#98`'s silver tables
- publish gold to Iceberg
- materialize gold to PostgreSQL as the final publish step (so Superset,
  issue `#100`, never needs to query Iceberg/Spark directly)
- build the `transform_publish` Airflow DAG wiring
  `bronze_to_silver` (issue `#98`) -> `silver_to_gold` -> `publish_gold_to_postgres`

### Detailed Plan (accepted 2026-09-20)

Planned in a dedicated session before any code, following issues `#91`-`#98`: every
decision the epic and the original plan left open is locked in Task 0 with its reason
and the rejected alternative. The three decisions marked *(user)* (D1, D8, D10) were put to the user, who
accepted the recommended option of each. Work then
proceeds task by task; every step states which task (and subtask) is active, opens with a
summary of what it covers, and closes by stating which files, if any, the user has to
modify and the next step. Nothing is done for which the information is missing: an unknown
is resolved by a spike (Task 1) or reported to the user, not assumed.

#### Facts established while planning (verified, not assumed)

- **Branch:** `issue-99-silver-to-gold-indicators-and-transform-publish-dag`, created from
  `origin/development` (which contains `#98`, merge commit `cfbbbcc`).
- **The cluster is up** (checked 2026-09-20): MinIO (`svc/minio:9000`), the dedicated gold
  PostgreSQL 17.6 (`svc/postgresql:5432`, database `gold`, user `gold`, Secret
  `postgresql-gold-credentials` with keys `password` and `postgres-password`), and the
  Airflow 3 pods are running. Nothing has ever been written to that PostgreSQL yet.
- **The Spark image has no JDBC driver.** The jars in `/opt/spark/jars` added by this
  project are the Iceberg runtime, `hadoop-aws` and `aws-java-sdk-bundle` (issue `#92`).
  Publishing gold to PostgreSQL from Spark needs `org.postgresql:postgresql`; the latest
  release on Maven Central is `42.7.13` (`postgresql-42.7.13.jar` answers HTTP 200). It
  has to be baked into a new image layer (a new tag imported into k3s by the user with
  `sudo`, like `#93` and `#98`): `--packages` would download from the internet on every
  run.
- **Silver's shape is the input contract** (`src/tfm_lakehouse/silver/schemas.py`): `entity`
  (person key, `has_cvn`, `has_orcid`, display name), `entity_link` (`record_id` ->
  `entity_id`, `evidence` JSON with `name_match` and `shared_organizations` for rule R2),
  `person_record`, `affiliation` (`kind`, `organization_norm`, `role`, `start_*`, `end_*`)
  and `publication` (`title_norm`, `year`, `doi`, `authors` only for CVN publications).
  `publication` and `affiliation` are keyed by `record_id`, **not** by entity, so every
  indicator has to join through `entity_link`.
- **One real person can report the same publication through several records** of one entity
  (a CVN and an ORCID record, or the bulk and the API record). Counting rows of
  `publication` per entity would inflate the indicator. Issue `#98` says to deduplicate
  on `(entity_id, doi)` or `(entity_id, title_norm, year)` before counting.
- **Silver has no co-author entity ids.** ORCID work summaries carry no author list, and
  a CVN's `authors` are name strings, not resolved entities. A co-authorship indicator can
  therefore only be built from what silver really has: two entities that report the
  same publication (same DOI). That is a lower bound of collaboration, not the full
  co-authorship graph, and it has a trap: a CVN that was **not** merged with its seed's ORCID
  record (a rule-R2 miss, recall 74.2%) reports the same DOIs as the seed entity and would
  show up as a collaboration between a person and themselves. Task 1 measures how big
  that contamination is before the indicator is committed to (D2).
- **Silver held 30,868 person records, 29,767 entities, 543,879 publications and 99,979
  affiliations after `#98`'s last rebuild** (`e2e98-5`), plus a daily `ingest_validate`
  partition not yet read. Gold is small by design (aggregates), so the Spark work here is
  cheap; the epic's reason for publishing to PostgreSQL is exactly that.
- Spark-side Python is the image's **3.10**: every module of this issue that the job
  imports must stay 3.10 compatible (`#98`'s syntax test is extended to them).
- Spark's JDBC writer in `overwrite` mode with `truncate=true` truncates and then inserts
  in **separate transactions**, so a dashboard reading during the publish could see an empty
  or half-filled table (Spark JDBC documentation; the `SaveMode.Overwrite` trap articles).
  This is why D5 publishes through staging tables and one atomic swap.

#### Task 0 - Decisions Locked

| # | Decision | Reason | Rejected alternative |
| --- | --- | --- | --- |
| D1 *(user)* | Indicators, in the epic's own terms: **I1 publications per researcher per year**, **I3 career trajectory / affiliation timeline**, and **I2 collaboration pairs** as the third, conditional on Task 1 (D2). Cut order if time is short, per the epic's cut list: I2 first, then I3; I1 is never cut. | The epic asks for 2-3 and allows reducing to 1 only under time pressure. I1 needs nothing beyond silver; I3 exercises the entity resolution (a trajectory only exists across the records an entity fuses); I2 is the one silver can least support. | Building all three unconditionally: risks a misleading I2. Only I1: the minimum, but wastes the HA01 fusion in the evaluation chapter. |
| D2 | **I2 is defined as pairs of distinct entities that report the same publication** (same DOI, deduplicated per entity), with `shared_publications`, first and last year. It is committed to only if Task 1 shows the self-collaboration contamination is small or removable; otherwise it is dropped (D1's cut order) and the reason recorded as a finding. Pairs are stored once (`entity_a < entity_b`). | Silver has no co-author entities (facts above); DOI overlap is the only honest signal. Measuring first keeps a data artifact out of the indicators. | Author-name matching from CVN `authors`: re-does entity resolution on strings inside the gold layer. Counting a CVN and its seed as a pair: false collaboration. |
| D3 | **Deduplicate publications per entity** with the key `coalesce(doi, sha1(title_norm) + '/' + year)`; the entity's year of a publication is the **minimum non-null year** among its copies. Publications with no usable year (null, before 1900 or after the current year + 1) are **excluded from the per-year counts and counted in the run summary**, not silently dropped. | Follows `#98`'s guidance and makes the per-year figure count each real work once. The summary keeps the exclusion measurable. | Counting `publication` rows: inflated by fused records. Dropping year-less works without reporting: hides a data-quality effect. |
| D4 | **Gold tables** (Iceberg namespace `lakehouse.gold`, mirrored 1:1 into PostgreSQL schema `gold`): `dim_researcher` (entity id, display name, ORCID iD, sources, `has_cvn`, `has_orcid`, distinct publications, first and last publication year, distinct organizations, career span in years), `publications_per_researcher_year` (I1), `affiliation_timeline` (I3: entity, kind, organization, normalized organization, role, start and end year, deduplicated across the entity's records), `collaboration_pairs` (I2, conditional) and `gold_run` (one row per run: run id, timestamp, the Iceberg snapshot id of every silver table read, row counts, excluded-publication count). | BI tables should be small, denormalized and directly chartable. `dim_researcher` lets Superset show names without a second query engine. `gold_run` extends the epic's "conservar procedencia" to gold: any figure can be traced to the exact silver snapshots. | No dimension: Superset would need joins over UUID-like ids. No run table: gold would have no provenance. |
| D5 | **Publish through staging tables and an atomic swap.** The Spark job writes each gold table into `gold._new_<table>` over JDBC, then one PostgreSQL transaction drops the old table and renames the staging one, for all tables together. The swap runs from the driver through the JVM's `DriverManager`. A failure before the swap leaves the published tables untouched. | Superset (`#100`) can be reading at any time; the epic wants a "zero-glue" native Postgres connector, so it must never see an empty table. Idempotent (same silver -> same rows). | Spark `overwrite` + `truncate`: separate transactions, visible empty window. A separate Python pod with `psycopg`: adds a dependency and a second image; PyIceberg does not support the Hadoop catalog used here. |
| D6 | **Two new Spark jobs, not one:** `spark_jobs/silver_to_gold.py` (reads `lakehouse.silver`, writes `lakehouse.gold` Iceberg with `createOrReplace`, D9 of `#98` again: full deterministic rebuild) and `spark_jobs/publish_gold_to_postgres.py` (reads `lakehouse.gold`, D5). Both are DataFrame/Spark SQL code with no Python UDFs, in modules `src/tfm_lakehouse/gold/` (Python 3.10 compatible; column definitions as data, like `silver/schemas.py`). | Matches the original plan's three DAG tasks and keeps "publish" retryable on its own without recomputing. Native Spark functions avoid the Python-worker cost that dominated `#98`. | One job doing both: a PostgreSQL outage would force recomputing gold. Python UDFs: slower and untestable on the host for no gain. |
| D7 | **New image tag `...-silver` -> `...-gold`** (`infra/spark-conf/Dockerfile.gold`, layered on the silver image) adding only `postgresql-42.7.13.jar`. The user imports it into k3s with `sudo`. Code and schema still come from the hostPath mounts; `iceberg-catalog.conf` stays unchanged (each launcher overrides the image, as in `#98`). PostgreSQL credentials reach the driver by `secretKeyRef` on the launcher pod and the executors by `spark.kubernetes.executor.secretKeyRef.PG_PASSWORD=postgresql-gold-credentials:password` *(refined in Task 5 and confirmed on the cluster in Task 8: the executors need no variable, the password travels in the JDBC write options)*. Nothing secret in git. | Same delivery pattern as `#93` and `#98`; no runtime internet dependency. | `spark-submit --packages`: needs internet every run and Ivy cache writes. Baking the password: never. |
| D8 *(user)* | **`transform_publish` DAG** (`dags/transform_publish.py`): three `KubernetesPodOperator` tasks in a chain, `bronze_to_silver >> silver_to_gold >> publish_gold_to_postgres`, each the Spark-driver-pod pattern of `#93`/`#98`, sharing one command builder. `schedule=None` at first (manual trigger, params for sizing and thresholds carried over from `#98`). If time allows, an Airflow 3 asset event from `ingest_validate` triggers it. The provisional `issue98_bronze_to_silver` DAG is **removed** (file deleted from the `dag-processor` PVC, DAG deleted in Airflow) once `transform_publish` reproduces its result. | The original plan and `#98` D11 name exactly this wiring. A manual trigger first proves the chain without a second moving part; an asset schedule is HA03 evidence but optional. | Scheduling straight away: hides failures behind cron. Keeping both DAGs: two launchers of the same job. |
| D9 | **Indicators are computed over all entity links**, including rule R2 merges; the R2 `evidence` (`name_match`, `shared_organizations`) is **not** used to filter by default. Task 8 reports, on the ground-truth run, how much each indicator changes if R2 merges with a single shared organization are excluded, so the effect of R2's 95.8% precision on the indicators is a measured figure in the memoria. | `#98` left the evidence so gold could be stricter; using it silently would change the meaning of the numbers, ignoring it silently would hide the risk. A sensitivity check does neither. | Filtering by default: throws away 74% recall for a precision figure that is a property of the synthetic ground truth. |
| D10 *(user)* | **Who writes the files:** the assistant writes code, infrastructure files and documentation (the `#97`/`#98` mode); the user acts only where the assistant cannot (the `sudo` image import) or where a decision is open. Accepted on 2026-09-20 with the user's instruction to do everything possible without their intervention, to notify them when it is needed, and to do nothing for which the information is missing. | `#98` D13 recorded that the user chose this. The repository's default protocol is that the user edits code and values files unless told otherwise per task, so the choice was stated again rather than assumed. | Assuming `#98`'s choice carries over silently. |
| D11 | **A DOI reported by more than `--max-entities-per-doi` entities (default 200) is left out of the collaboration pairs** and counted in `gold_run.dois_excluded_too_many_entities`. | Pairs grow quadratically with the entities per DOI (a consortium paper with 5,000 authors would give 12.5 million pairs). Task 1.3 measured a maximum of 14 on the current silver, so today the guard excludes nothing; it is a bound on the job's cost as the data grows, and the exclusion is reported, not silent. Added during Task 3, not in the accepted plan. | No guard: unbounded self-join. A silent cap: hides an effect on the indicator. |

Files touched by Task 0: this document; the `#99` row of `docs/roadmap/tfm/tfm_roadmap.md`
(`In Progress`, changed when Task 1 starts, not by this planning step).

#### Task Breakdown

Status in brackets, updated as work proceeds. Estimated effort about 20-24 h, inside the
epic's phase-3 budget (days 8-11); `#98` used the budget of phase 3's first half.

1. **Task 1 - Feasibility spikes and data inspection** [done; results in "Adjustments Made During Implementation"].
   - 1.1 roadmap row to `In Progress`; the issue document links its Task 0 [done].
   - 1.2 inspect the real `lakehouse.silver` (throwaway Spark pod, as `#98` Task 8.4):
     row counts, null rate of `publication.year`, `doi`, `title_norm`, year range and
     outliers, affiliations without `start_year`, publications per entity distribution,
     how many `(entity_id, doi)` duplicates fused records create [done].
   - 1.3 **the I2 gate:** entity pairs sharing a DOI, split into pairs that are the same
     person (a CVN singleton against its seed's entity, checkable on the ground-truth
     manifest of `e2e98-big`) and plausible collaborations between different people
     (real ORCID records); decide D2 with the numbers [done: gate passed].
   - 1.4 JDBC spike: `postgresql-42.7.13.jar` added to a container of the silver image, a
     `DataFrame.write.jdbc` into `gold._spike` on the cluster's PostgreSQL through a
     throwaway pod, and the swap transaction through `spark._jvm.java.sql.DriverManager`;
     confirm the `gold` user can `CREATE SCHEMA`/`CREATE TABLE`; list what `psql` shows [done].
   - 1.5 confirm PostgreSQL types for each Spark type (`ARRAY<STRING>` is not needed in
     gold; `INT`, `BIGINT`, `TEXT`, `BOOLEAN`, `TIMESTAMP`), and the identifier-quoting
     behaviour of the Spark JDBC dialect for column names such as `year` [done].
2. **Task 2 - Gold Spark image** [done; the k3s import with `sudo` was done by the user]: `infra/spark-conf/Dockerfile.gold` (D7), build
   `tfm-lakehouse/spark-py:3.5.9-iceberg1.11.0-gold`, check the jar and the silver
   validation still work as uid 185, update `infra/spark-conf/README.md`; **the user imports the
   image with `sudo`** (`docker save ... | sudo k3s ctr images import -`), then a
   pod with `imagePullPolicy: Never` confirms it.
3. **Task 3 - Gold library** [done] in `src/tfm_lakehouse/gold/` (Python 3.10).
   - 3.1 `schemas.py`: column definitions of the gold tables (Iceberg and PostgreSQL types
     as data, like `silver/schemas.py`), the PostgreSQL DDL and the staging/swap SQL as
     pure string builders (testable on the host).
   - 3.2 `publications.py`: the deduplicated publication set per entity (D3) and I1.
   - 3.3 `affiliations.py`: the deduplicated timeline per entity and the career figures (I3).
   - 3.4 `collaboration.py`: I2 (D2), only if the gate passes.
   - 3.5 `dim_researcher` and `gold_run` assembly.
4. **Task 4 - `silver_to_gold` job** [done] `spark_jobs/silver_to_gold.py`: read the six
   silver tables and record their snapshot ids, build the gold tables, write them with
   `createOrReplace` (D6), write `TASK_SUMMARY {...}` and a JSON summary (row counts,
   excluded publications, entities without publications). Fails (exit 1, nothing
   written) when silver is empty or lacks a table, so a broken upstream never replaces a
   good gold.
5. **Task 5 - `publish_gold_to_postgres` job** [done] (D5): read `lakehouse.gold`, JDBC
   write to staging tables, one-transaction swap, row-count reconciliation between Iceberg
   and PostgreSQL before the swap (a mismatch aborts), indexes on the columns Superset
   filters by (`entity_id`, `year`), a `GRANT SELECT` decision left to `#100`, summary.
6. **Task 6 - `transform_publish` DAG** [done; run in Task 8, `issue98_bronze_to_silver` retired] (D8): one command builder for the three
   tasks, the `#98` params plus gold sizing, PostgreSQL secret wiring (D7), retire
   `issue98_bronze_to_silver`, deliver to the `dag-processor` PVC (`kubectl cp`), check
   `airflow dags list-import-errors` and `airflow tasks render`. Optional: asset trigger
   from `ingest_validate`.
7. **Task 7 - Tests** [done] (no network on the host; Spark tests run in the image and
   skip without Docker and the image, like `#98`).
   - unit: PostgreSQL DDL/swap SQL builders, schema/column consistency, the Python 3.10
     syntax guard extended to `gold/` and the two jobs, DAG file structure (task ids,
     chain, no literal secrets);
   - Spark in the image, local mode: a **small hand-built silver dataset** whose gold
     values are computed by hand (fused records that must not double count a publication,
     a year-less publication, an entity with a career across two organizations, two
     entities sharing a DOI, a CVN singleton sharing DOIs with its seed if I2 is in), and
     the job's failure paths (empty silver, missing table writes nothing).
8. **Task 8 - End-to-end verification** [done; results in "Adjustments Made During Implementation"].
   - 8.1 run `transform_publish` through Airflow on the real data (with
     `ground_truth_run_id=e2e98-big`, which also rebuilds silver with the pending daily partition);
     three task pods, none left behind.
   - 8.2 gold Iceberg row counts against silver; **independent recomputation** of every
     indicator in plain Python over exported silver, compared to gold row by row.
   - 8.3 PostgreSQL read through `psql` in a throwaway pod: counts equal Iceberg's, types,
     indexes, no `_new_*` table left.
   - 8.4 idempotency: a second run gives identical gold (content digests per snapshot, as
     `#98` 8.3) and identical PostgreSQL rows.
   - 8.5 atomicity: kill the publish task between staging and swap; the published tables keep
     the previous content.
   - 8.6 sensitivity of the indicators to R2 (D9) on the ground-truth run; results into the issue
     document.
   - 8.7 a first look at runtimes of both new jobs (input for `#101`; first run discarded).
9. **Task 9 - Full test suite** [done: 798 passed, 2 skipped; Task 8 changed no code]: `uv run pytest -n auto tests` (the documented
   command), started in the background.
10. **Task 10 - Documentation close-out** [done]: this document (Adjustments,
    Implementation, Verification, Findings, Limitations, Impact, Status), `current_status.md`,
    `tfm_roadmap.md` (`Completed`), `known_limitations.md`, `infra/README.md`,
    `infra/spark-conf/README.md`, `infra/helm-values/README.md` (PostgreSQL client note),
    `PROJECT_GUIDE.md` (`src/tfm_lakehouse/gold/`, `dags/`), `AGENTS.md` only if its map
    changes.

#### Risks

- **I2 measures a data artifact** (facts above): mitigated by the gate in 1.3; the
  cut list allows dropping it.
- **JDBC swap from PySpark's JVM gateway** is less common than a `psycopg` call: 1.4 proves it
  before the design depends on it; the fallback is a small pod on the ingest image with
  `psycopg` that performs only the swap.
- **Gold PostgreSQL has never been written to** and its `gold` user's privileges are
  unverified: 1.4 finds out first.
- **Airflow api-server liveness probe** (issue `#97`): can fail a run at its start; a
  re-trigger fixes it (hardening is `#102`).
- **Image import needs the user's `sudo`** (Task 2): the one blocking hand-off; requested
  as early as possible.
- **Silver includes a daily partition it has not read** and `e2e98-big`'s 10,000 CVNs: the
  gold figures on the real cluster describe that bronze, not the default landing; recorded
  with every figure.
- **Time:** if the budget is at risk, cut in this order: `gold_run` and the asset trigger,
  then I2, then `affiliation_timeline`'s extras (keep only career span in `dim_researcher`).
  Never cut I1, the PostgreSQL publish or the DAG.

## Adjustments Made During Implementation

- Plan accepted on 2026-09-20 with the decisions above (Task 0). D1 (I1 and I3 firm, I2 conditional on
  the Task 1.3 gate), D8 (manual-trigger `transform_publish` first) and D10 (the assistant writes code,
  infrastructure and documentation) resolved as recommended. Working protocol for every step: state the
  active task and subtask, open with what it covers, close with whether the user must modify any file
  and the next step.
- **Task 1 spikes (2026-09-20). They confirm D2, D5 and D7 and refine D3 and D5:**
  - *1.2, the real silver* (throwaway Spark pod in local mode, silver image, `lakehouse.silver` read
    through the catalog; the script was delivered through a ConfigMap because uid 185 cannot read
    the scratchpad). Counts equal `#98`'s last rebuild: 30,868 `person_record`, 99,979
    `affiliation`, 543,879 `publication`, 0 `rejected`, 30,868 `entity_link`, 29,767 `entity`.
    Publications: 6,434 (1.2%) have no year, 16 have a year outside 1900-2027 (`0` twelve times,
    `1`, `20`, `198`, and `2028`; the six `2027` are plausible forthcoming works), 180,089 (33%)
    have no DOI, and none lacks `title_norm`, so the fallback key of D3 is always defined.
    Affiliations: 18,166 (18%) have no `start_year`, 32,688 (33%) no `end_year` (ongoing or
    unknown), `end_year` reaches 2036, none ends before it starts; 59,230 employment and 40,749
    education entries. **Fused records inflate a naive count by 27,483 rows (5.1%)**: 543,879
    publication rows through `entity_link` collapse to 516,396 distinct `(entity_id, key)`, so
    the deduplication of D3 changes the indicator and is not optional. (The spike first reported
    513,187 / 30,692 / 5.6%; that was wrong: its key was built with `concat`, which is null when
    the year is null, so the title-keyed works without a year collapsed into one per entity. The
    gold job's key treats a null year as empty, and the independent recomputation of Task 8.2
    reproduced 516,396 exactly.) Of the 29,767 entities,
    21,207 have publications (8,560 have none); publications per entity: median 10, 90th
    percentile 53, 99th 210, maximum 1,906. The current silver snapshot is the rebuild of
    2026-09-19 21:39 UTC.
  - *1.3, the I2 gate: passed.* Over the deduplicated `(entity, DOI)` pairs of the real silver, with the
    ground truth of both synthetic runs in silver (`e2e-default-1`, `e2e98-big`): 319,488 DOIs,
    23,454 shared by two or more entities, at most **14 entities per DOI** (so the pair self-join
    cannot explode); **9,540 entity pairs** share a DOI. By ground truth: 25 pairs (0.26%) are the
    same person (22 pairs of an entity with a CVN record against an ORCID-only entity, 3 between two
    CVN entities, sharing 229 DOIs) -- the self-collaboration artifact predicted in the facts, real
    but small; 4,423 pairs involve an entity with a CVN record and a *different* person; **5,092 pairs
    (25,557 shared DOIs) involve no CVN record at all**, that is, real ORCID data only, with a heavy
    tail (the top pairs share 800-1,000 DOIs, large consortia). Decision: **I2 is built**, over
    all entities as D2 says, and each pair carries `has_cvn_member` so BI (and the memoria) can
    restrict it to real data; the 25 same-person pairs are recorded as a limitation, since a
    production run has no ground truth to remove them (they are the price of the rule-R2 recall of
    74.2%).
  - *1.4, JDBC from Spark to the cluster's PostgreSQL* (silver image plus
    `postgresql-42.7.13.jar` on `--jars` and `--driver-class-path`, a throwaway pod, `PG_PASSWORD` from
    the `postgresql-gold-credentials` Secret): PostgreSQL 17.6 reports the `gold` user as owner with
    `CREATE` on the database, and it can create and drop schemas; `DataFrame.write.jdbc` wrote
    through the driver; and the whole swap of D5 works **from the driver through the JVM's
    `DriverManager`** (`Class.forName("org.postgresql.Driver")`, one connection, `setAutoCommit(false)`,
    `DROP TABLE` + `ALTER TABLE ... RENAME` in one transaction): a forced `SELECT 1/0` inside the
    transaction rolled everything back, the published table kept its 2 rows and the staging table its
    1, and the next attempt succeeded. The fallback of the risks section (a `psycopg` pod) is not
    needed. `mode="overwrite"` + `truncate=true` also works but has the visible-empty-window problem of
    D5, so it is not used. The jar must be on the JVM's **system** classpath for `DriverManager` to
    see the driver; in the image it will sit in `/opt/spark/jars`, as the other jars. Nothing was
    left behind in PostgreSQL (checked with `psql`), and the spike jar lives only in the git-ignored
    `data/spike99/`.
  - *1.5, types.* Left to itself Spark creates `TEXT`, `INTEGER`, `BIGINT`, `BOOLEAN`, `DOUBLE PRECISION`
    and **`timestamp without time zone`**, and no primary key or index. `year` needs no quoting
    handling: Spark's dialect quotes every column name. A table created first with explicit DDL
    (`TIMESTAMPTZ`, composite `PRIMARY KEY (entity_id, year)`) accepted a Spark `append` with correct
    round-trip values, and a duplicate row was rejected by the primary key (`duplicate key value
    violates unique constraint`).
  - *Refinement of D5:* the staging tables are **created with explicit DDL** (PostgreSQL types,
    `NOT NULL`, primary keys, `TIMESTAMPTZ` for run timestamps) through the same `DriverManager`
    connection, Spark then **appends** into them, and the swap renames them. The DDL is generated from
    the column definitions of `gold/schemas.py` (pure string builders, unit-testable on the host).
    Reason: control of types and constraints, and the primary key doubles as a check that gold has no
    duplicate rows. Indexes are created on the staging table before the swap, so the published table
    is never without them.
  - *Refinement of D3:* the year bounds are 1900 and **the year of the run plus 1** (2027 on
    2026-09-20), the upper bound being a job argument (`--max-year`), so a re-run in a later year
    does not need a code change; on the current silver they exclude 6,450 publications rows
    (6,434 without a year and 16 out of range) before deduplication.
- **Task 2 (gold image), 2026-09-20.** `infra/spark-conf/Dockerfile.gold` layers
  `postgresql-42.7.13.jar` on the silver image, in `/opt/spark/jars` (system classpath, needed by
  `DriverManager`, Task 1.4). Built locally as `tfm-lakehouse/spark-py:3.5.9-iceberg1.11.0-gold`
  (2.55 GB) and checked as uid 185: Python 3.10.12, pydantic/jsonschema/requests import, the
  Iceberg jar is intact, the driver jar is present. `infra/spark-conf/README.md` has the section
  (build, import, why the jar is not on `--jars` only, credentials). **The import into k3s needs
  the user's `sudo`**: a pod with `imagePullPolicy: Never` reported `ErrImageNeverPull` at the end
  of Task 6, so the cluster runs (Task 8) wait for it.
- **Task 3 (gold library), design choices not fixed by the plan:**
  - *Where each thing lives.* `gold/schemas.py` is pure (column definitions, primary keys, indexes,
    the Spark -> PostgreSQL type map, and the SQL of D5 as string builders) and is tested on the
    host; `gold/indicators.py` holds every DataFrame transformation (native Spark functions, no
    Python UDFs, so nothing runs in Python workers) and is imported only inside the image.
  - *Index and constraint names.* A table renamed by the swap keeps its staging index names
    (`_new_<table>_pkey`), which would collide with the next publish's staging table. The primary
    key and every index are therefore named explicitly on the staging table and renamed to their
    final names inside the swap transaction. This was found while writing the swap SQL, before any
    run; the publish tests check the final names in `pg_indexes`.
  - *I3 grouping (a refinement of D4).* `affiliation_timeline` groups the records of an entity by
    `(entity_id, kind, organization_norm, start_year)`: the end year is the latest known one (a
    record that lacks it does not erase another's), the organization and role the alphabetically
    first non-null ones (arbitrary but deterministic). It has **no primary key** because the key
    contains a nullable year; stays with no start year are kept, merged per organization.
  - *Career figures (a definition D4 left open).* `career_start_year`, `career_last_year` and
    `career_span_years` come from **employment** stays only and use **known years only**: a stay
    without an end year is not extended to today, so the span is a lower bound, and it is null when no
    employment has a start year. `organization_count` counts distinct normalized organizations
    across employment and education.
  - *`dim_researcher.sources`* is a comma-separated string (sorted), not an array, so PostgreSQL and
    Superset need no array handling; `has_cvn` and `has_orcid` stay booleans.
  - *`has_cvn_member`* on each collaboration pair (from Task 1.3): true when either entity has a
    CVN record, so real-data-only pairs are the `false` ones.
  - *The publication key* is `doi:<doi>` when a DOI exists, else `title:<sha1(title_norm)>/<year>`
    (the year of that copy, empty when null). Copies of one work with a DOI in one record and none
    in another are therefore counted as two works; the deduplication is exact only within each
    kind of key (recorded as a limitation).
- **Task 4 (`silver_to_gold`).** Same shape as `bronze_to_silver`: `run(spark, ...)` returns a
  summary, `main` logs `TASK_SUMMARY` and writes the JSON. It reads the four silver tables the
  indicators need, records their latest Iceberg snapshot ids, and raises `SilverToGoldError`
  (exit 1, nothing written) when a table is missing or `entity` is empty. The four indicator tables
  are written first and **`gold_run` last**, so its presence marks a complete write and the publish
  job can refuse to run without it. `--run-id` (the Airflow run id) and `--max-year` (default: the
  current year plus one) are arguments.
- **Task 5 (`publish_gold_to_postgres`).** Implements D5 with the Task 1.4/1.5 refinements: an
  empty staging table per gold table from explicit DDL, a Spark `append` into it, **a row-count
  reconciliation between Iceberg and PostgreSQL (a mismatch aborts)**, the indexes, then the swap
  in one transaction, and a final count of the published tables. Any failure before the swap drops
  the staging tables (the cleanup itself failing is only logged, because the original failure
  matters more) and leaves the published tables as they were. The password comes only from the
  `PG_PASSWORD` environment variable. **Refinement of D7:** the executors get no PostgreSQL
  environment variable at all, because the write's JDBC options (including the password) travel
  with the write task; Spark redacts a `password` option in its plans. This is confirmed on the
  cluster in Task 8 (the local tests run in `local` mode and cannot show it).
- **Task 6 (DAG).** `dags/transform_publish.py`: one `spark_submit_command` builder and one
  `_spark_driver_task` factory for the three tasks; the `#98` parameters are kept and gold ones added
  (`gold_executors`, `gold_executor_memory`, `gold_shuffle_partitions`, `max_year`,
  `max_entities_per_doi`); `schedule=None` (D8). **One image for all three tasks**, the gold one
  (silver plus the driver), instead of two images, so a single import serves the whole DAG.
  Delivered to the `dag-processor` PVC with `kubectl cp`; `airflow dags list-import-errors`
  reported no errors, `airflow tasks list` shows the three tasks, and `airflow tasks render`
  produced the expected `spark-submit` commands (image override, hostPath options on the
  executors, job arguments, and `PG_PASSWORD` wired from `postgresql-gold-credentials` on the
  publish driver only). At the end of this task (before the image import) the DAG was new and therefore
  **paused and not yet triggered**, and `issue98_bronze_to_silver` was **still there**, to be removed
  after `transform_publish` had reproduced its result (D8). Both were resolved in Task 8: the DAG was
  unpaused and ran twice, and the provisional DAG was retired.
- **Task 7 (tests).** New: `tests/test_gold_schemas_unit.py` (14, host: definitions, identifier
  lengths and uniqueness, DDL, swap and cleanup SQL, every staging index renamed by the swap),
  `tests/test_transform_publish_dag_unit.py` (11, host: static structure of the DAG, no secrets),
  `tests/test_gold_jobs_spark.py` (12, in the gold image with a real `postgres:17` container) with the
  runner `tests/spark_gold_runner.py`; `tests/spark_image.py` gained the gold image, a Docker
  network and environment variables, and `tests/test_silver_python310_unit.py` now also covers
  `gold/`. The Spark tests build a hand-made silver (four entities, thirteen publication rows,
  six affiliations) whose gold values were computed by hand before running: a work reported by two
  records of one entity with years 2020 and 2019 counts once, in 2019; a year before 1900 and one
  after the maximum leave the per-year indicator but not the work counts; two records of one stay
  merge; two pairs share DOIs; and the run row's counts. They also cover a rebuild giving the same
  gold, the DOI guard, nothing written on empty or incomplete silver, and, against PostgreSQL:
  tables, primary keys, final index names, `TIMESTAMPTZ`, no staging table left, a second publish
  replacing the first, a publish that fails at the start leaving the published tables unchanged,
  and a publish refused when gold was never built. All 12 passed on the first run, so the hand-computed
  values were right. They take about 8 minutes (each Spark start is about 40 s) and skip without
  Docker and both images, like `#98`'s.
- **Task 8 (verification in the cluster, 2026-09-20).** The user imported the gold image into k3s (a pod
  with `imagePullPolicy: Never` then found the JDBC jar), so Task 2 closed and the DAG could run. Every
  run below is the `transform_publish` DAG, triggered with the Airflow CLI and
  `ground_truth_run_id=e2e98-big`, two executors per job.
  - *Early check before the image import.* Because the locally built image could already run in Docker,
    `silver_to_gold` was run in `local[4]` mode against the cluster's MinIO through a `kubectl
    port-forward` (S3A endpoint overridden) and gold was exported with a small throwaway Spark script. It
    took 91 s and produced the same numbers as the later DAG runs. It is how the 5.6% error of Task 1.2
    was found: the independent recomputation gave 516,396 distinct publications against the spike's
    513,187, and the cause was the spike's `concat` nulling the key of title-keyed works with no year
    (corrected above). The local path is a convenient development loop and was not used as verification
    of record.
  - *8.1, the DAG through the pods (run `e2e99-1`, success, 10 min).* `bronze_to_silver` 5 min 57 s (the
    job itself 280.8 s), `silver_to_gold` 1 min 50 s (73.0 s), `publish_gold_to_postgres` 1 min 50 s
    (79.2 s). Silver equals `#98`'s rebuild exactly (30,868 person records, 543,879 publications, 99,979
    affiliations, 29,767 entities, 0 rejected; the daily `ingest_validate` partition that silver had not
    read was deduplicated on `record_id`: 1,000 CVN and 201 API records dropped as duplicates), and its
    evaluation against the ground truth reproduces `#98`'s figures: rule R1 7,098 of 7,098, rule R2 144
    merges, 138 correct, 6 false, precision 95.8%, recall 74.2%. Gold: `dim_researcher` 29,767 rows,
    `publications_per_researcher_year` 172,861, `affiliation_timeline` 94,431, `collaboration_pairs`
    9,540, `gold_run` 1. No task, driver or executor pod was left behind. **This meets D8's condition, so
    `issue98_bronze_to_silver` was retired**: the DAG deleted in Airflow (`airflow dags delete`), its file
    removed from the `dag-processor` PVC and from the repository.
  - *8.2, independent recomputation.* A plain-Python script, written differently on purpose
    (dictionaries and tuple keys instead of Spark and hashes), recomputed every gold table from an
    export of the silver tables and compared it with the exported gold: `dim_researcher` (all columns),
    per-year counts, affiliation timeline, collaboration pairs (shared publications, first and last year,
    `has_cvn_member`) and every count of `gold_run`, on the DAG's own output: **0 mismatches in 29,767 +
    172,861 + 94,431 + 9,540 rows, and all 9 counts of `gold_run` equal**. It also passed on the earlier
    local run.
  - *8.3, PostgreSQL.* Read through `psql` in throwaway pods: the five tables exist in schema `gold`
    with the Iceberg row counts, the four primary keys and four secondary indexes carry their **final**
    names (8 indexes, none named `_new_*`), no staging table remains, `computed_at` is `timestamp with
    time zone` and the counts are `bigint`. Every row of the four large tables was dumped with
    `row_to_json` and compared with the Iceberg export: **306,599 rows, 0 differences**. The two
    executors of the publish task wrote over JDBC **with no PostgreSQL environment variable of their
    own**, confirming the D7 refinement.
  - *8.4, idempotency (run `e2e99-2`, success, 10 min; warm: 219.8 s, 71.3 s and 69.3 s per job).* A
    second run over the same bronze gave PostgreSQL tables **identical row for row** to the first run's
    (0 differing rows in the four tables), while `gold_run` recorded the silver snapshot ids of its own
    rebuild: same content, new provenance.
  - *8.5, atomicity.* The publish job was launched by hand in a pod (same image and credentials) and
    killed with `--grace-period=0 --force` as soon as `_new_affiliation_timeline` held rows (47,201 of
    94,431, so mid-load): the five published tables were untouched (same `run_id`, same row counts, same
    MD5 of the per-year table) and the five staging tables were left half-loaded. **A retry recovered by
    itself**: it dropped the leftovers, loaded, reconciled the counts, swapped and finished in 59.5 s with
    no staging table and no `_new_*` index left, and the published content unchanged.
  - *8.6, sensitivity to rule R2 (D9).* Of the 164 R2 links, 75 rest on exactly one shared organization
    and 89 on two or more. Undoing the 75 (each becomes its own entity) changes: entities 29,767 ->
    29,842 (+0.25%), distinct publications 516,396 -> 516,742 (+0.07%), per-year rows 172,861 ->
    173,081 (+0.13%), collaboration pairs 9,540 -> 9,595 (+0.58%); of the 55 new pairs, 38 are the split
    record paired with the entity it was taken from (an artifact of undoing) and no built pair
    disappears. The indicators are therefore insensitive to the false merges of rule R2 at this scale;
    the default is unchanged.
  - *8.7, runtimes (input for `#101`).* Cold, first run: `bronze_to_silver` 280.8 s, `silver_to_gold`
    73.0 s, publish 79.2 s; warm second run: 219.8 s, 71.3 s, 69.3 s. The cold penalty is about 1.3
    times for the silver job, much smaller than `#98`'s 2.5 times, probably because the data was already
    in the node's page cache (not verified). `silver_to_gold` on 543,879 publications and 99,979
    affiliations is bounded by Spark start-up and shuffle, not by compute (91 s in a single Docker
    container with 4 cores); the JDBC load of 172,861 rows took about 23 s.
  - *As planned:* the Airflow api-server liveness failure of `#97`/`#98` did not appear in any of the
    three runs; no re-trigger was needed.
  - *State left in the cluster:* bronze as `#98` left it; `lakehouse.silver` holds the rebuild of run
    `e2e99-2` and `lakehouse.gold` its gold; the PostgreSQL `gold` schema holds the last publish
    (`gold_run.run_id = e2e99-2`, published by the manual recovery pod, whose content equals the DAG's);
    `transform_publish` is unpaused with no schedule; `issue98_bronze_to_silver` no longer exists; no
    extra pods, ConfigMaps or port-forwards remain. Git-ignored run folders `data/silver_runs/e2e99-*`
    and `data/gold_runs/e2e99-*` hold the summaries.

## Implementation Performed

- `src/tfm_lakehouse/gold/`: `schemas` (column definitions of the five gold tables, primary keys,
  indexes, the Spark -> PostgreSQL type map, and the DDL/swap/cleanup SQL as pure string builders) and
  `indicators` (deduplicated publications per entity, indicator I1, the affiliation timeline I3, the
  collaboration pairs I2 with its DOI guard, `dim_researcher`; native Spark functions only). Python 3.10
  compatible.
- `src/tfm_lakehouse/spark_jobs/silver_to_gold.py`: reads four silver tables, records their snapshot
  ids, writes `lakehouse.gold` (full rebuild, `gold_run` last), refuses to write on empty or incomplete
  silver.
- `src/tfm_lakehouse/spark_jobs/publish_gold_to_postgres.py`: staging tables from explicit DDL, JDBC
  append, row-count reconciliation, indexes, one-transaction swap, cleanup on failure.
- `infra/spark-conf/Dockerfile.gold`: the silver image plus `postgresql-42.7.13.jar` (built and
  imported into k3s); a section in `infra/spark-conf/README.md`.
- `dags/transform_publish.py`: `bronze_to_silver >> silver_to_gold >> publish_gold_to_postgres`, manual
  trigger, sizing and threshold parameters; it replaced `dags/issue98_bronze_to_silver.py`, which was
  removed.
- Gold tables (Iceberg `lakehouse.gold`, mirrored 1:1 in PostgreSQL schema `gold`): `dim_researcher`,
  `publications_per_researcher_year` (I1), `affiliation_timeline` (I3), `collaboration_pairs` (I2, with
  `has_cvn_member`) and `gold_run` (provenance and counts of the run).
- Tests: `test_gold_schemas_unit.py`, `test_transform_publish_dag_unit.py`, `test_gold_jobs_spark.py`
  with `spark_gold_runner.py`, an extended `spark_image.py`, and the Python 3.10 guard now covering
  `gold/`.

## Verification

Executed 2026-09-20 (details of every step in "Adjustments Made During Implementation", Tasks 7 and 8).

- **Unit and image tests:** `uv run pytest -n auto tests` -- 798 passed, 2 skipped (the two
  `*_live_smoke` tests that need `ORCID_LIVE_TEST=1`) in 9 min 53 s, against 753 passed at the end of
  issue `#98`; the 45 new tests include 12 that run the real jobs in the gold image against a real
  PostgreSQL 17 container and pass on a hand-built silver whose gold values were worked out by hand.
- **The DAG through the cluster's pods (Tasks 8.1, 8.4):** two full runs succeeded in about 10 minutes
  each; no pod left behind; the silver rebuild reproduced issue `#98`'s resolution evaluation exactly.
- **Independent recomputation (8.2):** every gold table and every `gold_run` count recomputed in plain
  Python from the exported silver: 0 mismatches.
- **PostgreSQL (8.3):** counts, types, primary keys, index names and no staging leftovers checked with
  `psql`; 306,599 rows compared one by one with Iceberg: 0 differences.
- **Idempotency (8.4):** the second run's PostgreSQL contents are identical to the first's.
- **Atomicity and recovery (8.5):** a publish killed mid-load left the published tables unchanged, and
  a retry cleaned up and completed.
- **Sensitivity to rule R2 (8.6):** undoing the 75 single-organization R2 merges moves the indicators
  by 0.07% to 0.58%.

## Findings

- **Publication counts must be deduplicated per entity, and the amount is measurable:** 543,879
  publication rows collapse to 516,396 distinct works (5.1% inflation from fused records). A first,
  naive measurement (5.6%) was wrong because of a null-propagating `concat`; an independent
  recomputation caught it, which is the reason to keep an independent check next to the Spark code.
- **The collaboration indicator survived its gate:** of 9,540 entity pairs sharing a DOI, 25 (0.26%)
  are the same person seen twice (the self-collaboration artifact of rule-R2 misses), 5,092 involve real
  ORCID data only, and the most entities behind one DOI is 14. Silver's lack of co-author entities makes
  it a lower bound.
- **The indicators are insensitive to rule R2's false merges at this scale:** undoing 75 weak merges
  moves every indicator by at most 0.58%, so the 95.8% precision of `#98` does not undermine the gold
  layer.
- **Staging tables and one transaction give real atomicity, verified by killing the job:** the swap
  works from the driver through the JVM's `DriverManager` with the driver in `/opt/spark/jars`; a
  renamed table keeps its staging index names, so the swap must rename them too (found while writing
  the SQL).
- **Spark's JDBC writer needs no environment variable on the executors:** the password travels in the
  write options, so only the driver pod needs the Secret.
- **Real-data quirks:** 6,119 distinct works (1.2%) have no usable year (and 16 publication rows have a
  year outside 1900-2027, including `0`, `1`, `20` and `198`), 33% of publication rows have no DOI, 18%
  of affiliations have no start year, and 29% of entities (8,560 of 29,767) have no publication at all.
- **A local development loop exists:** the gold image runs in Docker against the cluster through
  `kubectl port-forward`; it surfaced the error in a Task 1 figure before any pod ran.
- **Runtimes are small and dominated by Spark start-up and I/O:** the whole DAG takes about 10 minutes,
  of which `silver_to_gold` and the publish take under 2 minutes each.

## Known Limitations

Recorded in `docs/pipeline/known_limitations.md`: the collaboration indicator is a DOI-only lower bound
with a measured 0.26% same-person artifact; publications are deduplicated only within each kind of key
(DOI, or title and year); career figures are lower bounds from known years; gold is rebuilt in full and
PostgreSQL keeps only the latest publish; the gold indicators inherit entity-resolution errors (measured
insensitivity to rule R2); the PostgreSQL password is visible in the driver's write options. Per the
epic, ML-based resolution and author-name matching remain out of scope.

## Impact On Future Issues

Issue `#100` (Superset Dashboard) queries the PostgreSQL tables materialized here:

- database `gold` on `svc/postgresql:5432` (`postgresql.tfm-lakehouse.svc.cluster.local`), schema
  `gold`, user `gold`, password in the Secret `postgresql-gold-credentials` (key `password`); the tables
  are `dim_researcher` (join key `entity_id`), `publications_per_researcher_year` (I1),
  `affiliation_timeline` (I3), `collaboration_pairs` (I2; filter `has_cvn_member = false` for real ORCID
  data only) and `gold_run` (one row: which run and which silver snapshots the figures come from; worth
  showing on the dashboard as provenance);
- a read-only role for Superset is a `#100` decision: the publish never creates one, and it drops and
  renames tables on every run, so grants on the tables would be lost each time unless they are made
  through default privileges on the schema;
- the figures describe the bronze the cluster holds (19,469 bulk records, 11,000 CVNs of which 10,000
  come from the `seed=43` run, 399 API records), not the default landing;
- `dim_researcher` has 29,767 rows and `publications_per_researcher_year` 172,861: aggregate in Superset
  rather than plotting per researcher.

Issue `#101` (benchmark) measures these jobs and `#98`'s: warm-run job times are 219.8 s, 71.3 s and 69.3
s (`bronze_to_silver`, `silver_to_gold`, publish), the first run of a session was only about 1.3 times
slower for the silver job, the sizing is a set of DAG parameters (`executors`, `gold_executors`,
`shuffle_partitions`, `gold_shuffle_partitions`), and the number of rule-R2 matches, hence the gold
figures, depends on the landing sample. Issue `#102` (hardening) inherits the credential exposure in the
JDBC options, the manual schedule of `transform_publish` (an asset trigger from `ingest_validate` was not
built), and the single-node assumptions of the DAG (checkout paths mounted with hostPath, images imported
by hand).

## Status

`Completed`
