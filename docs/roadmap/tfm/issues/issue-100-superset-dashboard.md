# Issue 100 - Superset Dashboard

## Summary

Deploy Apache Superset and build a small dashboard on the gold indicators.
First issue of TFM epic phase 4.

## Original Goal

A live BI dashboard presenting the finalized indicators from issue `#99`.

## Original Plan

- Helm-deploy Superset onto the cluster (issue `#90`)
- connect Superset to PostgreSQL (native connector) and the gold tables
  materialized in issue `#99`; no Trino or Spark Thrift Server, per the
  epic's stack decision
- build 2-3 charts, one per finalized indicator

### Detailed Plan (accepted 2026-09-20)

Planned in a dedicated session before any code, following issues `#91`-`#99`: every decision
the epic and the original plan left open is locked in Task 0 with its reason and the rejected
alternative. The three decisions marked *(user)* (D1, D7, D8) were put to the user, who
accepted the recommended option of each. Work then proceeds task by task; every step states
which task (and subtask) is active, opens with a summary of what it covers, and closes by
stating which files, if any, the user has to modify and the next step. Nothing is done for
which the information is missing: an unknown is resolved by a spike (Task 1) or reported to
the user, not assumed.

#### Facts established while planning (verified, not assumed)

- **Branch:** `issue-100-superset-dashboard`, created from `origin/development` (which
  contains `#99`). `git fetch` could not run in the planning session (SSH key unavailable), so
  the local `origin/development` ref was used; its tree equals the `#99` branch's.
- **The Helm chart is deprecated.** `superset/superset` 0.22.8 (app version 6.1.0, the latest
  in the repo added by `#90`) has `deprecated: true` in its `Chart.yaml`, and the official
  Kubernetes installation page says the chart is not recommended for new deployments; the
  official path is the Apache Superset Kubernetes Operator (`v1alpha1`, v0.2.0 released
  2026-08-11 with breaking changes, no bundled PostgreSQL or Redis, requires CRDs).
- **The lean `apache/superset:6.1.0` image has no database drivers** (Superset 6.1.0 Docker
  builds documentation), so not even the metadata database over PostgreSQL works without
  `psycopg2`. `docker manifest inspect apache/superset:6.1.0` resolves.
- **The chart's bundled subcharts** (PostgreSQL 16.7.27 and Redis 17.9.4, OCI) already pin
  `bitnamilegacy/postgresql:14.17.0-debian-12-r3` and `bitnamilegacy/redis:7.0.10-debian-11-r4`,
  the same frozen registry issue `#91` settled on. Chart defaults to avoid: `admin/admin`, a
  known `SECRET_KEY`, image from `apachesuperset.docker.scarf.sh`.
- **The cluster** has 16 cores and about 10 GB of free RAM (checked 2026-09-20), StorageClass
  `local-path`, and the `#91` pods running; `svc/postgresql` holds the `#99` gold tables
  (`dim_researcher`, `publications_per_researcher_year`, `affiliation_timeline`,
  `collaboration_pairs`, `gold_run`; columns in `src/tfm_lakehouse/gold/schemas.py`).
- **Grants on gold tables do not survive a publish:** `#99`'s swap drops and renames tables, so
  Superset's read access has to come from default privileges on the schema, not from grants on
  tables.
- **Assets as code:** Superset exports and imports databases, datasets, charts and dashboards
  as a ZIP/YAML bundle (`import-directory` in the CLI, `/api/v1/dashboard/import` in the API);
  a database's password is masked in the export and must be supplied on import.

#### Task 0 - Decisions Locked

| # | Decision | Reason | Rejected alternative |
| --- | --- | --- | --- |
| D1 *(user)* | Deploy with the **Helm chart `superset/superset` 0.22.8**, pinned. Its deprecation is recorded as a limitation and the operator as future work. | It is what the original plan says, `#90` already added the repo, and the epic already rejected an alpha operator with CRDs for the same reason as the Spark Operator. It bundles PostgreSQL and Redis, so nothing else is needed. | Superset Kubernetes Operator v0.2.0: alpha, breaking changes between releases, needs CRDs and an external PostgreSQL and Valkey; more work and risk in phase 4. |
| D2 | **Own image** `tfm-lakehouse/superset:6.1.0-pg` (`infra/superset/Dockerfile`, the lean image plus `psycopg2-binary`), imported into k3s by the user with `sudo` like `#93`, `#98` and `#99`. | The lean image has no driver (facts above); a baked image needs no internet at runtime. | `pip install` in `bootstrapScript` on every pod start: internet dependency and slower starts (same reasoning as D7 of `#99`). |
| D3 | **Metadata database = the chart's own PostgreSQL subchart** with its own PVC; Redis from the subchart without persistence. Single replica per component. | Keeps Superset's state apart from the published gold data (as `#91` kept Airflow's metadata apart) and needs no external wiring. | Reusing the gold PostgreSQL: mixes application state with published data and needs the superuser password. |
| D4 | **Read-only role `superset_ro`** on database `gold`: `USAGE` on schema `gold`, `SELECT` on the current tables, and `ALTER DEFAULT PRIVILEGES FOR ROLE gold IN SCHEMA gold GRANT SELECT ON TABLES TO superset_ro`. Versioned SQL, password from a Secret. Checked to survive a `transform_publish` run. | Least privilege for BI; default privileges are the only mechanism that survives `#99`'s drop-and-rename swap. | Connecting as `gold`: gives write access to the BI tool. Grants on tables: lost at every publish. |
| D5 | **Secrets** (`SECRET_KEY`, admin password, `superset_ro` password) live in Kubernetes Secrets created with `kubectl`, never in git; the chart's defaults are overridden. Access by `kubectl port-forward svc/superset 8088:8088`, no Ingress. | Same handling as MinIO and PostgreSQL in `#91`; local-only cluster. | Chart defaults (`admin/admin`, known key): unacceptable even locally. |
| D6 | **Dashboard as code:** built once in the UI, exported to `infra/superset/assets/`, and the reimport into a clean Superset is checked to reproduce it. | A reviewer or a rebuilt cluster gets the same dashboard; the export is evidence for the memoria. | UI clicks only: not reproducible. |
| D7 *(user)* | **Three charts plus provenance:** I1 publications per year (aggregated in Superset), I3 affiliation timeline, I2 collaboration pairs filtered to `has_cvn_member = false`, and a tile with `gold_run.run_id`. No per-researcher chart (29,767 rows). Cut order if time is short: provenance tile and I2 first, then I3; I1 is never cut. | The original plan asks for 2-3 charts, one per finalized indicator; `#99`'s impact notes say to aggregate and to filter I2 for real data. | Per-researcher plots: unreadable. Only I1 and I3: the fallback, not the target. |
| D8 *(user)* | **Who writes the files:** the assistant writes code, infrastructure files and documentation (the `#98`/`#99` mode); the user acts only where the assistant cannot (the `sudo` image import) or where a decision is open. Accepted on 2026-09-20. | The repository default is that the user edits code and values files, so the choice was put again rather than assumed. | Assuming the earlier choice carries over silently. |
| D9 | **Time box:** if a working deployment is not reached after about 4 h of Tasks 2-4, apply the epic's fallback (a static table or chart from the PostgreSQL gold tables in the memoria) and record it. | Superset is the epic's first cut; the decision is made in advance. | Open-ended debugging of a deprecated chart. |
| D10 | **The admin user is created outside the chart:** `init.createAdmin: false`, and `infra/superset/create_admin.sh` creates it from the Secret `superset-secrets`, sending the password over stdin. Added during Task 4, not in the accepted plan. | The chart requires the admin password at render time and would write it into its config Secret and the Helm release, breaking D5's "no secret in values or release"; a script reading the Secret keeps a single source. | `init.createAdmin: true` with `--set init.adminUser.password=...`: password in the release and in the rendered init script. |
| D11 | **The database connection disables the data cache** (`cache_timeout = -1`, the value Superset reads as "do not cache"), inherited by every dataset and chart that sets no timeout of its own. Added during Task 5, not in the accepted plan. | The chart's own configuration caches query results for 24 h (`CACHE_DEFAULT_TIMEOUT: 86400`), so after a `transform_publish` run the dashboard would keep showing the previous figures, contradicting the issue's own check that charts update after a run. The gold tables are small aggregates and the queries fast, so serving them uncached costs nothing. | The default 24 h cache: stale figures. A short TTL: still stale for a while. Flushing Redis after every publish: needs a hook the DAG does not have. |
| D12 | **The dashboard shows aggregates only, never a person's name**, and the charts are built directly on the five gold tables (no virtual dataset joining `dim_researcher`). Added during Task 6, not in the accepted plan. | `dim_researcher.display_name` holds real names from public ORCID records, and the dashboard's screenshots go into a memoria that is defended and stored in a public repository; the epic's privacy reasoning for CVN data applies in spirit to what is displayed. Aggregates carry the indicators just as well. | A table of the top collaborating pairs with names: more striking, but puts identifiable people in the evidence. |
| D13 | **The bundle tests read the exported YAML with regular expressions, not a YAML parser.** Added during Task 8, not in the accepted plan. | PyYAML is not a dependency of the repository (`import yaml` fails in its environment) and the bundle is machine-generated in one stable shape; adding a dependency to `pyproject.toml`, `uv.lock` and CI for two file shapes is more change than the issue needs. A mutation check (a renamed column, a stray row) shows the tests do fail on the drift they guard. | Adding PyYAML as a development dependency: the cleaner parser, at the cost of touching the dependency set; it can replace the regular expressions later without changing what the tests assert. |
| D14 | **The number of Spark containers that run at once in the test suite is capped inside the tests** (`spark_slot` in `tests/spark_image.py`: four slots as lock files shared by all xdist workers, `SPARK_TEST_SLOTS` to change it), and a run that is aborted has its container removed. Added during Task 10, not in the accepted plan; it touches the test helper of `#98`/`#99`, with the user's go-ahead ("do whatever is necessary so that it works well"). | `pytest -n auto` gave 16 workers, hence up to 16 JVMs and Python processes at once, and the Spark tests failed on their own concurrency (timeouts and `CANNOT_OPEN_SOCKET`), so the documented command did not finish green even on an idle machine with the cluster stopped. With four slots the same suite passes in about 10 minutes, and no test's assertions or timeout limits change. Killing only the `docker` client on a timeout had left the container running and loading the machine, so the container is now removed too. | Documenting that the Spark test files must be run with `-n 4`: leaves the documented command broken for everyone, and CI (`pr-tests.yml`) runs it. Lowering `-n` for the whole suite: slows the ~800 fast tests to protect 17 slow ones. |

Files touched by Task 0: this document; the `#100` row of `docs/roadmap/tfm/tfm_roadmap.md`
(`In Progress`, changed when Task 1 starts, not by this planning step).

#### Task Breakdown

Status in brackets, updated as work proceeds. Estimated effort about 12-16 h, inside the
epic's phase-4 budget (days 12-14; epic target 2026-10-04).

1. **Task 1 - Spikes** [done; results in "Adjustments Made During Implementation"].
   - 1.1 roadmap row to `In Progress` [done].
   - 1.2 confirm `psycopg2` is absent from the lean 6.1.0 image [done].
   - 1.3 `helm pull` the chart: subcharts packaged or downloaded from OCI; `helm template` with
     draft values [done].
   - 1.4 whether the `gold` user can `CREATE ROLE`; otherwise use `postgres-password` [done:
     it cannot].
   - 1.5 how the database password is supplied on import (API `passwords` or the CLI) [done:
     the API].
   - 1.6 whether the chart's Celery worker can be disabled (synchronous queries are enough)
     [done: scale to 0].
2. **Task 2 - Superset image** [done; the k3s import with `sudo` was done by the user]: `infra/superset/Dockerfile`, build, check as a
   non-root user, README section; **the user imports it with `sudo`**.
3. **Task 3 - Read-only role** [done]: SQL script, Secret, apply, prove `superset_ro` reads
   and cannot write.
4. **Task 4 - Helm deployment** [done; the user imported the image with `sudo`]: `infra/helm-values/superset-values.yaml`, Secrets,
   `helm install`, pods, init job, login through the port-forward, resource use.
5. **Task 5 - Connection and datasets** [done]: database `superset_ro` -> `gold`, datasets
   over the five tables (a virtual dataset joining `dim_researcher` if needed).
6. **Task 6 - Charts and dashboard** [done]: the D7 charts and tile; figures checked
   against `psql`.
7. **Task 7 - Assets as code** [done]: export to `infra/superset/assets/`, an import
   script, reimport check on a clean Superset.
8. **Task 8 - Tests** [done] (host, no network): values files parse, pinned versions, no
   literal secrets; the role SQL; every table and column named in the assets exists in
   `gold/schemas.py` (drift guard).
9. **Task 9 - End-to-end verification** [done; results in "Adjustments Made During Implementation"]: run `transform_publish` (about 10 min) and
   confirm the dashboard shows the new `run_id` and updated charts; query during the publish
   (brief lock from the swap, never an empty table); grants survive; `superset_ro` cannot
   write; screenshots for the memoria.
10. **Task 10 - Full test suite** [done; the documented command is green, 828 passed, after capping the concurrent Spark containers (D14)]: `uv run pytest -n auto tests` (the documented
    command).
11. **Task 11 - Documentation close-out** [done]: this document, `current_status.md`,
    `tfm_roadmap.md` (`Completed`), `known_limitations.md`, `infra/README.md`,
    `infra/helm-values/README.md`, `PROJECT_GUIDE.md`; `AGENTS.md` only if its map changes.

#### Risks

- **Deprecated chart** (D1): mitigated by pinning and by D9.
- **Image import needs the user's `sudo`** (Task 2): requested as early as possible.
- **Bitnami subcharts** may fail to download or start; the images are already `bitnamilegacy`.
- **Datasets after the swap:** Superset must keep working after `#99`'s drop-and-rename; checked
  in Task 9.
- **Time:** cut in the D7 order; the fallback of D9 stays available.

## Adjustments Made During Implementation

- Plan accepted on 2026-09-20 with the decisions above (Task 0). D1 (Helm chart), D7 (three
  charts plus provenance) and D8 (the assistant writes code, infrastructure and documentation)
  resolved as recommended. Working protocol for every step: state the active task and subtask,
  open with what it covers, close with whether the user must modify any file and the next step.

- **Task 1 spikes (2026-09-20). They confirm D2, D3 and D4 and settle the open points of D5, D6 and
  the worker:**
  - *1.2, the lean image.* `apache/superset:6.1.0` (digest `sha256:16b50bbe...`) runs as uid 1000
    (`superset`) with Python 3.10 in `/app/.venv`, has `uv` and the `redis` client (5.3.1) but
    **no `psycopg2`** (`ModuleNotFoundError`). D2 stands: the image needs the driver, and it also
    serves the metadata database.
  - *1.3, the chart.* `helm pull superset/superset --version 0.22.8` gives a tarball that
    **already contains the PostgreSQL and Redis subcharts**, so `helm install` needs no OCI download of
    subcharts. `helm template` renders cleanly (only the warning "this chart is deprecated") into: the
    web Deployment, the worker Deployment, the `init-db` Job, the `env` and `config` Secrets, and the
    PostgreSQL and Redis StatefulSets with their images already on `docker.io/bitnamilegacy`. Three
    findings that shape Task 4: (a) **the chart does not create a `SECRET_KEY`**; Superset reads
    `SUPERSET_SECRET_KEY` from the environment and **refuses to start with the default one**
    (`Refusing to start due to insecure SECRET_KEY`), so the key enters through `extraEnvRaw` with a
    `secretKeyRef` (rendered into the web, worker and init pods; no value in the chart's Secret or in
    git); (b) **`init.adminUser.password` is mandatory at render time** (the chart fails when it is
    empty), so it cannot be a committed value and is supplied at install time from outside git; (c) the
    database password is rendered into the chart's own `env` Secret from Helm values (default
    `superset`), which would put it in the release; the chart's documented way to avoid that is to
    override `DB_PASS` with `extraEnvRaw` from a Secret, and to give the PostgreSQL subchart the same
    Secret through `auth.existingSecret`. This is verified in Task 4, not assumed here.
  - *1.4, the gold PostgreSQL.* The `gold` user is owner of the database, of schema `gold` and of the
    five tables, and has `CREATEDB`, but **not `CREATEROLE`** (`CREATE ROLE` fails with `permission
    denied`). Task 3 therefore creates `superset_ro` as the superuser `postgres`, with the
    `postgres-password` key of `postgresql-gold-credentials`; the default privileges are declared
    `FOR ROLE gold`, which the superuser can do. Nothing was left behind (throwaway pod, no role
    created).
  - *1.5, importing the dashboard with its database.* The CLI command `superset import-dashboards`
    takes only a path and a username and has **no way to pass the database password**; the REST
    endpoint `POST /api/v1/dashboard/import/` does (form field `passwords`, a JSON map from each
    `databases/*.yaml` to its password, plus `overwrite`). D6's import step therefore goes through the
    API with a login, not through the CLI; the exported YAML keeps the connection URI with a masked
    password, so nothing secret enters git. To be exercised in Task 7.
  - *1.6, the worker.* The chart has no switch for the Celery worker, but
    `supersetWorker.replicas.replicaCount: 0` renders `replicas: 0`. Synchronous queries are all the
    dashboard needs, so the worker is scaled to zero (async queries, alerts and cache warm-up are not
    used). Beat, Flower and websockets are already disabled by default.

- **Task 2 (Superset image), 2026-09-20.** `infra/superset/Dockerfile` layers
  `psycopg2-binary==2.9.13` (the latest release with a cp310 manylinux wheel; the image's venv runs
  Python 3.10) on `apache/superset:6.1.0` with `uv pip install` in `/app/.venv`, and returns to the
  `superset` user. Built as `tfm-lakehouse/superset:6.1.0-pg` (1.28 GB) and checked as uid 1000:
  `psycopg2` 2.9.13 and `redis` 5.3.1 import, the original entrypoint and `CMD`
  (`/app/docker/entrypoints/run-server.sh`) are intact. The build context is `infra/superset/` alone,
  so the root `.dockerignore` is not needed. `infra/superset/README.md` has the build and import
  commands. **The import into k3s needs the user's `sudo`**; Task 4 waits for it (Tasks 3 and 7's
  scripts do not).

- **Task 3 (read-only role), 2026-09-20.** `infra/superset/gold_readonly_role.sql`: creates
  `superset_ro` once (`\gset`/`\if`, otherwise only resets the password), `NOSUPERUSER NOCREATEDB
  NOCREATEROLE NOREPLICATION`, `CONNECT` on `gold`, `USAGE` on schema `gold`, `SELECT` on the existing
  tables and `ALTER DEFAULT PRIVILEGES FOR ROLE gold IN SCHEMA gold GRANT SELECT ON TABLES`. The
  password reaches the script as a psql variable from the Secret `superset-gold-ro-credentials`
  (created with `kubectl`), and the script runs as `postgres` (Task 1.4). Verified on the cluster with
  throwaway pods: as `superset_ro` the published tables read (`dim_researcher` 29,767 rows,
  `gold_run.run_id = e2e99-2`); `INSERT`, `CREATE TABLE`, `DROP TABLE` and `DELETE` are all refused;
  and a **simulated `#99` swap on a scratch table** (a staging table created by `gold`, then `DROP` of
  the old one and `RENAME` in one transaction) left the renamed table readable by `superset_ro`
  without a new grant, which is the property D4 exists for. The scratch tables were dropped and the
  five published tables were never touched; the real publish is checked again in Task 9. A first
  draft of the script also had a `REVOKE ... ON SCHEMA public` line; it was removed because
  PostgreSQL 17 gives no role `CREATE` on `public`, so it changed nothing and only suggested a
  protection that was not there.

- **Task 4 (Helm deployment), first part, 2026-09-20.** Written before the image import, which is the
  one blocking step: `infra/helm-values/superset-values.yaml`, the Secret `superset-secrets`
  (`secret-key`, `postgres-password`, `password`, `admin-password`, all random, created with `kubectl`)
  and the install/verify commands in `infra/helm-values/README.md`. `helm template` renders without
  errors and shows: the web, init-job and worker pods take `SUPERSET_SECRET_KEY` and `DB_PASS` from
  `superset-secrets` (an explicit container env entry wins over the chart's own env Secret, whose
  `DB_PASS` defaults to `superset`); the PostgreSQL subchart reads its two passwords from the same
  Secret through `auth.existingSecret`; every Superset container has `imagePullPolicy: Never` and runs as
  uid 1000; the worker has `replicas: 0`. Refinements not fixed by the plan: **(D10)** the chart's init
  job does not create the admin user (`init.createAdmin: false`), because the chart would render the
  password into its config Secret and the Helm release; the user is created afterwards from the
  Secret, keeping D5's "no secret in values or release". A pod with `imagePullPolicy: Never` reported
  `ErrImageNeverPull`, so at that point the image was **not yet imported** and the install had not run (the second
  part below records what followed).

- **Task 4 (Helm deployment), second part, 2026-09-20.** The user imported the image with `sudo`
  (a pod with `imagePullPolicy: Never` then went past `ErrImageNeverPull`). `helm install` (chart 0.22.8,
  the values file above) brought up `superset-postgresql-0`, `superset-redis-master-0`, the web pod and the
  `superset-init-db` Job (`superset db upgrade`, `superset init`; admin and examples skipped). Findings:
  - *Helm marked the first install `failed`, but nothing was broken.* The chart's PostgreSQL took about two
    minutes to boot for the first time (its data directory on `local-path` under WSL2), the `wait-for-postgres`
    init container of the first init Job pod hit its own 120 s limit (`Init:Error`), the Job's second pod
    completed at 17:24:17Z, and Helm's default 5-minute timeout had already expired at 17:23
    (`failed post-install: ... Job in progress: context deadline exceeded`). `helm upgrade` with the same
    values and `--timeout 15m` gave revision 2, `deployed`, with the init Job `Completed` in 43 s (the
    init is idempotent and PostgreSQL was up). The install command in `infra/helm-values/README.md` now
    carries `--timeout 15m`.
  - *The web pod restarted once.* Its first start failed in `configure_fab` (`SQLAlchemyError` with an empty
    message, `Worker failed to boot`) at 17:22:32, before the init Job had created the metadata tables (the
    cause is inferred from that timing; the message itself says nothing); the kubelet restarted it and the
    second start was healthy. No lasting effect; noted in the README.
  - *Admin user (D10).* `infra/superset/create_admin.sh` (idempotent; the password goes over stdin from
    `superset-secrets`, never as a `kubectl` argument) created `admin` with role `Admin`; a second run reports
    that it already exists.
  - *Login checked through a port-forward:* `/health` and `/login/` answer 200, the API login with the
    Secret's password returns an access token and a wrong password returns 401.
  - *Resource use at rest:* web 197 Mi and 2 m CPU, PostgreSQL 36 Mi, Redis 3 Mi (the worker is at zero
    replicas), far below the 2 Gi limit, so the D9 budget was not an issue. Deployment reached inside the
    D9 time box.
  - *State left in the cluster:* Helm release `superset` (revision 2, `deployed`), Secrets
    `superset-secrets` and `superset-gold-ro-credentials`, role `superset_ro`; no throwaway pod remains.

- **Task 5 (connection and datasets), 2026-09-20.** All through the REST API with
  `infra/superset/superset_client.py` (standard library only: login, CSRF token, JSON requests, and the
  multipart upload Task 7 will use), over a `kubectl port-forward` of my own on port 18088; passwords
  were read from the Secrets inside the process and never printed.
  - *Connection.* `test_connection` answered `OK`; database `TFM Gold` (id 1) was created with the URI
    `postgresql+psycopg2://superset_ro:...@postgresql.tfm-lakehouse.svc.cluster.local:5432/gold`,
    `allow_dml: false`, `allow_run_async: false`, `expose_in_sqllab: true` (the role cannot write anyway) and
    `cache_timeout: -1` (D11). Superset stores the password masked and encrypted with the `SECRET_KEY`;
    the schemas it sees are `information_schema`, `gold` and `public`.
  - *Datasets.* One physical dataset per table over schema `gold` (ids 1-5: `dim_researcher`,
    `publications_per_researcher_year`, `affiliation_timeline`, `collaboration_pairs`, `gold_run`). The
    column list Superset read from each table **equals `TABLE_COLUMNS` of `gold/schemas.py` exactly**
    (16, 3, 7, 6 and 15 columns), which is the property Task 8's drift guard relies on.
  - *Cache (D11).* Two identical `chart/data` queries on `gold_run` both came back from PostgreSQL
    (`cache_timeout: -1`, no `is_cached`), returning `run_id = e2e99-2` and `entities = 29767`. The
    24 h default would have hidden a new run; it is a fact of the chart's generated `superset_config.py`,
    not a Superset default.
  - *No virtual dataset was needed yet;* Task 6 decides whether the charts need a join with
    `dim_researcher`.

- **Task 6 (charts and dashboard), 2026-09-20.** Built through the API (the assistant has no browser; a
  scratch builder outside git, idempotent by name), each chart saved with its own `query_context` so it can be
  checked by `GET /api/v1/chart/{id}/data/` without opening the UI. The exported assets of Task 7 are the
  versioned artifact, not the builder. Design (D12: aggregates only, no names, no virtual dataset):
  - *I1 - Publications per year* (chart 1): bars, `SUM(publication_count)` by `year`, `year >= 1980` (the
    443 publications before 1980 are left out and the chart's description says so).
  - *I3 - Affiliation stays started per year* (chart 2): stacked bars, `COUNT(*)` by `start_year` and `kind`,
    1970-2026: the chart shows 78,200 of the 94,431 stays; 16,130 have no start year and 101 more fall outside
    1970-2026, and all of them are left out.
  - *I2 - New collaboration pairs per year, real ORCID data* (chart 3): bars, `COUNT(*)` of pairs by
    `first_year` with `has_cvn_member = false` (D7).
  - *Provenance - gold run* (chart 4): a table over `gold_run` (`run_id`, `computed_at`, `max_year`, entities,
    distinct publications, collaboration pairs).
  - *The dashboard* `tfm-gold-indicators` (id 1, published): a markdown note (real ORCID plus synthetic CVN,
    aggregates only, a lower bound for I2), I1 full width, I3 and I2 side by side, the provenance table.
  - *Verified against PostgreSQL:* for each chart the rows Superset returns were compared with hand-written SQL run
    directly with `superset_ro` in a throwaway pod: I1 48 rows, I3 114 rows, I2 41 rows, provenance 1 row,
    **all identical**. The totals reconcile with the data: I1 sums to 509,834, which is the per-year table's
    510,277 publications (years 1910-2027) minus the 443 before 1980, and I2 sums to 5,092, the number of
    real-data pairs `#99` recorded.
  - *Not verified at this point:* how the charts look in a browser (no browser on the host); done in Task 9.

- **Task 7 (assets as code), 2026-09-20.**
  - *Export.* `GET /api/v1/dashboard/export/?q=!(1)` gave a 28 KB bundle with the database, the datasets, the
    four charts and the dashboard; it was unzipped into `infra/superset/assets/` (without the timestamped
    folder name). The database's password is `XXXXXXXXXX` (masked by Superset), and nothing in the bundle
    holds an owner, an e-mail or a person's data. **Only four datasets are exported**, not five: the export
    carries the datasets the charts use, and `dim_researcher` is used by none (D12), so that dataset does not
    survive a rebuild from the bundle; nothing depends on it.
  - *Import (D6, spike 1.5).* `infra/superset/import_dashboard.py` zips `assets/` under one root folder and
    posts it to `/api/v1/dashboard/import/` with `overwrite=true` and the password of `superset_ro` in the
    `passwords` field, keyed `databases/TFM_Gold.yaml` (the key has no root folder, as the API's own
    documentation shows; the form field is `formData`).
  - *Reimport check on an emptied Superset.* Baseline of every chart's rows was saved; then the dashboard, the
    four charts, the five datasets and the database were deleted through the API (all created in this issue),
    leaving 0 of each, and the script imported the bundle: it answered `OK` and the instance had again the
    database (new id 2), four datasets, four charts and the dashboard `tfm-gold-indicators` with **the same
    uuid** and four charts attached. **Every chart returned the same rows as before** (I1 48, I3 114, I2 41,
    provenance 1). The imported connection kept `cache_timeout: -1` and `allow_dml: false`; two identical
    queries were both uncached. The database list endpoint does not show `cache_timeout`, only the single
    resource does (checked, since it looked like a loss at first).
  - *The check is on the same Superset, not a second one:* the metadata database was emptied of these assets,
    not rebuilt from nothing (no second Superset was installed; the cluster's own PostgreSQL and Redis were
    reused).

- **Correction found while writing the Task 8 tests (a bug of Task 6).** The layout I first saved had each
  chart's `chartId` but not its `uuid` in the component's `meta`; Superset, which recognises a placed chart by
  `uuid`, then treated all four charts as unplaced and **appended a second row (`ROW-N-...`) holding a copy of
  each**, which the first export showed and would have made the dashboard render every chart twice. The layout
  was rebuilt with each chart's `uuid` in its `meta`; the live dashboard then had exactly four rows and four
  chart components, and the export none of the extra row. The whole cycle was repeated on the corrected
  bundle: export, delete everything, import, compare. Every chart returned the same rows (48, 114, 41, 1), the
  layout after the import had the same four rows and four charts, and a further export matched the bundle
  once the instance's ids (`chartId`, `datasource` ids) and the timestamp were normalised away; the only other
  difference was a `native_filter_configuration: []` that Superset adds when it saves, so the bundle committed
  is that post-import export. The export's file names end in the instance's ids (`..._9.yaml`), so a re-export
  renames files: replace the whole `assets/` folder rather than copying over it (the README says so).
  A test now fails when a chart lacks its uuid on the dashboard or a `ROW-N-` row appears.

- **Task 10 (full test suite), 2026-09-20 and 2026-09-21. The documented command first failed in two runs on the
  Spark-in-Docker tests; after capping their concurrency (D14) it is green in a single run (828 passed, 2 skipped,
  10 min 15 s), see the last three items of this record.** `uv run pytest -n auto tests` was first run twice, exactly
  as documented:
  - *Run 1:* 2 failed, 813 passed, 2 skipped, 7 errors in 32 min 11 s (the failures were
    `test_silver_resolution_spark[0.5]` and `test_gold_jobs_spark` cases; the seven errors were other
    `test_gold_jobs_spark` cases).
  - *Run 2:* 4 failed, 818 passed, 2 skipped in 33 min 7 s (`test_silver_resolution_spark[1.0]`,
    `test_silver_job_spark`, and two `test_gold_jobs_spark` cases).
  - *Every failure and error is `subprocess.TimeoutExpired` on the `docker run` of a Spark job* (the tests allow
    900 s each), none an assertion; the set of tests that timed out **differed between the two runs**. Pass counts
    are consistent with the tests added here: 798 (end of `#99`) + 24 new = 822, minus the 9 and the 4 that timed
    out gives the 813 and the 818 seen.
  - *They pass alone:* the 14 tests of the two files that failed or errored in run 1 passed in one run with
    `-n 4` (14 passed in 32 min 28 s, the machine still slow), and the 7 cases that failed in run 2 passed in 4
    min 8 s with `-n 2` and nothing else running.
  - *Cause (first reading, later corrected):* the suite took 32-33 minutes against 9 min 53 s at the end of `#99`, the
    load average reached 30-73 on 16 cores, and Airflow's probes (`airflow db check`, `airflow jobs check`) start a
    Python interpreter every few seconds and had restarted the Airflow pods many times during this session
    (scheduler 18 to 33 restarts); that load was taken to be the cause.
  - *2026-09-21 check, on an idle machine with the cluster stopped (k3s inactive, load average 0.3).* The three Spark
    test files that had failed (`test_gold_jobs_spark.py`, `test_silver_resolution_spark.py`,
    `test_silver_job_spark.py`, 17 tests) were run by the user with `uv run pytest -n auto` on those three files: **5 failed and 2
    errored in 17 min 22 s**, again with no assertion failure: two 600 s `TimeoutExpired` and five
    `PySparkRuntimeError: [CANNOT_OPEN_SOCKET] ... Connection refused` (the JVM logged `Accept timed out`, the
    Python process reached its socket too late), with single Spark stages taking 20-80 s. Then the same 17 tests
    were run with `-n 4`: **17 passed in 5 min 20 s**. So the cause is the number of Spark containers running at
    once (`-n auto` gives 16 workers, hence up to 16 JVMs and Python processes together), and the cluster's load
    only made it worse. The lesson for the record: `-n auto` was the wrong choice for the Spark files, and it was
    the assistant that proposed it.
  - *The fix (D14), 2026-09-21.* `tests/spark_image.py` now limits the Spark containers that run at once to four
    (`spark_slot`, exclusive `flock` on lock files shared by every pytest worker of the user, released by the
    operating system if a worker dies; `SPARK_TEST_SLOTS` overrides the number) and removes the container of a run
    that is aborted (a timeout or Ctrl-C used to kill only the `docker` client and leave the container running).
    `tests/test_spark_image_slots_unit.py` has 6 tests of it without Docker or Spark (the cap is reached and never
    exceeded, a single slot serialises, a slot is released when the block raises, a clear error when none frees up,
    the environment variable and its safe defaults, and an aborted run's container is removed).
  - *Two mistakes of my own while doing it, both caught by running it.* The first version of those tests used the
    real, shared lock files, so in the full suite they competed with the Spark tests that other workers were running
    (4 of them failed: `no Spark test slot became free` and a peak of 1 instead of 2, although all 824 other tests
    passed, in 9 min 52 s); the lock directory is now a parameter and each test uses its own. The test of the aborted
    run also took a real slot, which made it wait for as long as a simulation of mine kept all four slots held; it
    now does not. The six tests pass in about 3 s even while another process holds the four real slots.
  - *Result: `uv run pytest -n auto tests`, exactly as documented, on an idle machine with the cluster stopped, in a
    single run: 828 passed, 2 skipped in 10 min 15 s* (798 at the end of `#99` + 24 tests of the infrastructure + 6 of
    the slots), against 32-33 minutes with failures before the fix and 9 min 53 s at the end of `#99`. The two
    skipped are the `*_live_smoke` tests that need `ORCID_LIVE_TEST=1`.

- **Task 9 (end-to-end verification, 2026-09-20).** Run `e2e100-1` of `transform_publish`, triggered with the
  Airflow CLI and `ground_truth_run_id=e2e98-big` (the parameters of `#99`'s check), while a scratch reader
  polled the four charts through Superset's API about every 4 seconds (four queries and a 1.5 s pause).
  - *The DAG.* All three tasks succeeded (`bronze_to_silver` 17:55:47-18:04:56, `silver_to_gold`
    18:06:13-18:08:44, `publish_gold_to_postgres` 18:09:02-18:12:24). Each task shows two pods while it runs (the
    Airflow worker of the `KubernetesExecutor` and the Spark driver of the `KubernetesPodOperator`), and none was
    left behind. Wall-clock times are 548 s, 151 s and 201 s, slower than `#99`'s warm runs (357 s, 110 s, 110 s)
    because this session installed a headless browser, took screenshots and ran the reader during the run:
    **they must not be used as benchmark figures for `#101`.**
  - *What a dashboard user would have seen (the reader's log).* 238 samples over 1,040 s: **0 errors and 0
    empty results**, the row count of every chart constant (48, 114, 41 and 1), and the provenance's `run_id`
    went from `e2e99-2` to `e2e100-1` in one step, with no intermediate state. Latency was about 0.5-0.8 s per
    chart (median), with spikes up to 13.9 s that happened well before the switch (during Spark's load on the
    node) and about 1.3 s around it. **Limit of this evidence:** the swap's lock is held for milliseconds and a
    sample is taken only every few seconds, so this shows there was no sustained window, not that no query ever
    waited; the atomicity itself was proved in `#99` by killing the publish.
  - *The dashboard reflects the new run without any refresh or cache flush:* the provenance table changed from
    `e2e99-2` (computed 12:31:01) to `e2e100-1` (computed 18:07:02) because the connection caches nothing (D11).
    The bars are identical, as they must be: the bronze was the same and gold is deterministic (`#99`), so
    **the run id and timestamp are what show that a new run arrived**, not a changed figure.
  - *PostgreSQL after the publish, read as `superset_ro`:* `gold_run.run_id = e2e100-1`, counts 29,767,
    172,861, 94,431 and 9,540 (the same as before), `SELECT` on all five tables (**the default privileges of D4
    survived a real publish**, the tables having been recreated), no `_new_*` table left, and `INSERT`, `DROP
    TABLE` and `CREATE TABLE` refused.
  - *The dashboard in a real browser (headless Chromium, installed with `uvx`, outside the repository's
    dependencies).* It renders with three charts and the provenance table, no error, no duplicated row (which
    also confirms the layout correction above). The screenshots before and after the run are in
    `infra/superset/screenshots/` and the script that takes them is `infra/superset/screenshot_dashboard.py`
    (run once more from the repository to check it: 3 charts, 0 errors). One cosmetic point left as it is: the
    note at the top has more empty space than its text needs.
  - *The reader is a scratch script outside git;* the figures above are its output.

- **Task 8 (tests), 2026-09-20.** `tests/test_superset_infra_unit.py`, 24 tests on the host, no network
  (D13: regular expressions, not a YAML parser): the image (base image and driver pinned, ends as `superset`);
  the Helm values (own image with `pullPolicy: Never`, both secrets by `secretKeyRef`, `existingSecret`, no
  literal credential outside comments, admin not created by the chart, worker at zero, chart version and
  `--timeout 15m` in the README); the role script (default privileges, read-only, no `GRANT` of a write
  right, password only as a psql variable); and the bundle (one database, four charts, a dashboard; the
  connection has `cache_timeout -1`, `allow_dml false` and only the masked password; no file anywhere carries
  a credential; **every dataset is a gold table whose columns equal `TABLE_COLUMNS` of `gold/schemas.py`**;
  every chart uses only columns of its dataset; every chart is placed by uuid on the dashboard with no stray
  row; no chart selects a name column). Two provisioning scripts are covered: the import script zips the
  bundle under one root folder with the database file the password map names, and the client sends the bundle
  as multipart with its token and CSRF headers and reports an API error's status and body (a fake opener, no
  network). Two of my first assertions were wrong and were fixed, not the files: Superset lists a dataset's
  columns in its own order, so they are compared as sets, and the values file's header comment names the
  `admin/admin` default it overrides, so only non-comment lines are checked. **Mutation check:** renaming a
  dataset column and adding a stray row made exactly the three tests that guard them fail; the files were
  restored and the 24 pass again.

## Implementation Performed

- `infra/superset/Dockerfile`: `tfm-lakehouse/superset:6.1.0-pg`, the official lean `apache/superset:6.1.0` plus
  `psycopg2-binary==2.9.13` (built, imported into k3s by the user).
- `infra/helm-values/superset-values.yaml` and the Helm release `superset` (chart `superset/superset` 0.22.8,
  revision 2): own image with `pullPolicy: Never`, secrets only by `secretKeyRef` from `superset-secrets`, the
  chart's PostgreSQL and Redis subcharts, the Celery worker at zero, the admin user not created by the chart.
- `infra/superset/gold_readonly_role.sql`: the read-only role `superset_ro` with default privileges that survive
  `#99`'s drop-and-rename publish (applied to the cluster's PostgreSQL).
- `infra/superset/create_admin.sh`: creates the admin user from the Secret, over stdin.
- `infra/superset/assets/`, `import_dashboard.py` and `superset_client.py`: the dashboard `tfm-gold-indicators`
  as a versioned export (database `TFM Gold` with no data cache, four datasets, four charts, the dashboard) and
  the script that imports it through the REST API with the database password supplied separately.
- The dashboard: I1 publications per year, I3 affiliation stays started per year (employment and education),
  I2 new collaboration pairs per year (real ORCID data only), and a provenance table from `gold_run`; aggregates
  only, no personal names.
- `infra/superset/screenshot_dashboard.py` and `infra/superset/screenshots/`: the dashboard before and after a
  `transform_publish` run, from a headless browser.
- `tests/test_superset_infra_unit.py`: 24 tests (image, values, role SQL, bundle drift guard against
  `gold/schemas.py`, scripts).
- `tests/spark_image.py` (changed) and `tests/test_spark_image_slots_unit.py` (6 tests): a cap of four Spark
  containers at once across pytest workers, and removal of the container of an aborted run (D14).
- Documentation: `infra/superset/README.md`, `infra/helm-values/README.md`, `infra/README.md`,
  `PROJECT_GUIDE.md`, `docs/context/project_context_index.md`, `docs/pipeline/known_limitations.md`,
  `docs/context/tfm/current_status.md`, `docs/roadmap/tfm/tfm_roadmap.md`.

## Verification

Executed 2026-09-20 (details in "Adjustments Made During Implementation", Tasks 1-9).

- **Deployment (Task 4):** all pods `Running`, init Job `Completed`, release `deployed`; login through a
  port-forward works with the Secret's password and fails with a wrong one.
- **Connection and datasets (Task 5):** the connection test answered `OK`; the columns Superset read for each
  dataset equal `TABLE_COLUMNS` of `gold/schemas.py`; identical queries are not cached.
- **Charts (Task 6):** the rows of each chart equal hand-written SQL run directly in PostgreSQL (I1 48 rows, I3
  114, I2 41, provenance 1), and the totals reconcile with `#99` (I1 509,834 = 510,277 - 443; I2 5,092 real-data
  pairs).
- **Dashboard as code (Task 7):** export, delete everything, import from the files: same uuid, same rows in
  every chart, same layout of four rows and four charts.
- **Read-only access (Tasks 3 and 9):** `superset_ro` reads all five tables and is refused `INSERT`, `DELETE`,
  `DROP` and `CREATE`, before and after a real publish.
- **End to end (Task 9):** a full `transform_publish` run (`e2e100-1`) while a reader polled the charts: 238
  samples, 0 errors, 0 empty results, the run id changing in one step; the dashboard shows the new run without
  a refresh; the privileges survived the recreation of the tables; no staging table or pod left.
- **In a browser (Task 9):** headless Chromium renders three charts and the provenance table with no error and
  no duplicated row.
- **Tests:** `uv run pytest -n auto tests`, exactly as documented, on an idle machine with the cluster stopped:
  **828 passed, 2 skipped in 10 min 15 s** in a single run (798 at the end of `#99` + 24 + 6 new). Before the cap on
  concurrent Spark containers (D14) the same command failed in two runs (813 and 818 passed, 9 and 4 failures or
  errors, 32-33 min), always in the Spark-in-Docker tests and never on an assertion.

## Findings

- **The chart is deprecated and needs its own image:** the official Helm chart is marked `deprecated: true` and the
  official image has no PostgreSQL driver, so the deployment is a pinned chart, a pinned image and a baked-in
  driver; the dashboard, not the deployment, is the durable artifact.
- **A helm release can be `failed` with every pod healthy:** the chart's PostgreSQL needs about two minutes for
  its first boot and Helm's default timeout is five; `--timeout 15m` is in the documented install.
- **Superset's default data cache (24 h) would have hidden every new run,** and it is a property of the chart's
  generated configuration, not of Superset; the connection sets `cache_timeout = -1`.
- **A dashboard layout must carry each chart's `uuid`:** without it Superset treats the charts as unplaced and
  adds a second row with a copy of each; caught by the first export and now guarded by a test.
- **Default privileges are what keep read access across `#99`'s publish,** and the `gold` application user cannot
  create roles, so the role is created as the superuser.
- **Exports carry the instance's ids:** file names and `chartId` change from one instance to another, so a
  re-export renames files; assets are replaced as a whole folder, and equality is checked after normalising ids.
- **Privacy shaped the dashboard:** `dim_researcher` holds real names, so no chart uses it and the dashboard shows
  aggregates only.
- **The reader saw no sustained window during a publish,** but its sampling (every few seconds) cannot prove that
  no single query waited for the swap's millisecond lock; `#99` proved the atomicity itself.
- **The cluster is fragile under CPU load:** Airflow's probes (`airflow db check`, `airflow jobs check`) each start
  a Python interpreter every few seconds, and the restart counters of the Airflow pods rose sharply during this
  session's heavy runs (scheduler 18 to 33 restarts); `#102` inherits it.
- **The Spark tests failed on their own concurrency, not on the machine's load alone:** `pytest -n auto` ran up to 16
  Spark containers at once, and they failed with `TimeoutExpired` or `CANNOT_OPEN_SOCKET` (the Python process reached the
  JVM's socket too late), also on an idle machine with the cluster stopped. The first diagnosis (the cluster's load) was
  incomplete and was corrected by that check. A cap of four concurrent containers inside the tests (D14) made the
  documented command green in 10 min 15 s; a timeout also used to leave the container running, which is fixed.
- **Running a mechanism's tests next to the thing it limits needs isolation:** the first tests of the cap shared its
  real lock files and failed in the full suite, and one of them waited on real slots; each now has its own directory.

## Known Limitations

Recorded in `docs/pipeline/known_limitations.md`: Superset is deployed from a Helm chart its maintainers have
deprecated (the operator is future work); the deployment is local, single-replica and unhardened (no TLS or SSO,
port-forward access, no backup of Superset's metadata, a first-install timeout); and the dashboard shows
aggregates over a lower-bound indicator with its data cache disabled. A fourth, the Spark-in-Docker tests failing
when too many run at once, was found and **resolved** in this issue (D14) and is recorded there as such. Per the epic's scope cut list this issue
was the first thing to drop; it was not dropped, and its fallback (a static table or chart in the memoria) was not
needed.

## Impact On Future Issues

Issue `#101` (Spark performance benchmark) does not depend on Superset. Its inputs from this issue: the
`transform_publish` run `e2e100-1` took 548 s, 151 s and 201 s per task, **but it ran while a headless browser was
being installed and a reader polled Superset, so those figures must not be used**; `#99`'s warm-run figures
(219.8 s, 71.3 s, 69.3 s of job time) remain the reference. Run the benchmark on a quiet machine with the cluster
otherwise idle: this session's Airflow pods restarted many times under load. The Spark tests are no longer a source of
load in the suite: they run at most four at a time (D14, `SPARK_TEST_SLOTS`), and `docs/development/setup.md` says so.

Issue `#102` (hardening) inherits: the Superset deployment's single replica, missing TLS and SSO, port-forward-only
access, the unbacked-up metadata volume, the manually imported images (Spark, silver, gold, ingest and now Superset), the deprecated
chart, and the fragility of Airflow's probes and the Airflow pods under CPU load. It can also decide whether
Superset's Celery worker and a caching layer should return.

Issue `#103` (memoria assembly) has its evidence for the evaluation chapter: the dashboard export, the two
screenshots in `infra/superset/screenshots/` (aggregates only), the reader's result during a publish (with its limit
stated), and the read-only access checks. Nothing downstream depends on this issue.

## Status

`Completed`. The documented full-suite command is green in a single run: 828 passed, 2 skipped in 10 min 15 s
(see "Adjustments Made During Implementation", Task 10, and D14 for the change that made it reliable).
