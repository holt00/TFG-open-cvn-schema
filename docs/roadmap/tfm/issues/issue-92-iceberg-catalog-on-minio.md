# Issue 92 - Iceberg Catalog On MinIO

## Summary

Configure a Hadoop path-based Iceberg catalog rooted on the MinIO bucket
from issue `#91`. First issue of TFM epic phase 1
(`docs/roadmap/tfm/issues/issue-89-epic-tfm-lakehouse-platform.md`).

## Original Goal

Have a working Iceberg catalog, reachable from Spark, with no separate
catalog service (Hive Metastore/REST/Nessie) to deploy or debug, per the
epic's technology stack decision record.

## Original Plan

Planned in a dedicated planning session before implementation started
(2026-09-15), following the same execution convention issue `#91` used:
work proceeds task by task in the order below; each task names exactly
which files (if any) need a human edit — the user edits values/config
files themselves per session convention, this assistant edits
documentation.

The issue's own original plan deferred jar-version pinning to "the Spark
version chosen in issue `#93`", but issue `#93`'s own plan says it builds
its Spark image with "the Iceberg/S3A dependencies from issue `#92`" —
i.e. each issue expected the other to decide the Spark version first. That
circularity is resolved here: this issue locks the Spark version too (Task
0 below), the same way issue `#91`'s Task 0 locked chart/image versions
ahead of the issues that would consume them, so issue `#93` has a fixed
target to build against instead of re-deciding it.

### Task 0 - Decisions Locked (research, no files changed)

Research performed (web search, 2026-09-15) to pick a mutually-compatible,
currently-maintained version set, and a catalog/warehouse layout that does
not collide with the raw bronze/silver/gold prefixes issue `#91` already
created in the `lakehouse` bucket for pre-Iceberg file landing.

**Version pins** (chosen for mutual compatibility, not just recency):

| Component | Pinned version | Why |
| --- | --- | --- |
| Apache Spark | `3.5.9` | Latest patch on the `3.5` line (released 2026-07-16); `3.5` is the branch with a stable, widely-supported `iceberg-spark-runtime-3.5_2.12` artifact; avoids adopting a newer major (`4.x`) untested against the rest of this stack under the epic's time budget |
| Iceberg Spark runtime | `iceberg-spark-runtime-3.5_2.12:1.11.0` | Latest Iceberg release (2026-05-19) that still publishes a `3.5`-suffixed runtime jar; bundles Iceberg core, Parquet/Avro/ORC support, and the Hadoop-catalog implementation in one artifact — no other Iceberg jars should be added to the classpath (avoids the version-conflict risk the Iceberg docs call out for mixing runtime and non-runtime modules) |
| `hadoop-aws` | `3.3.4` | Must match the Hadoop client version bundled inside the `spark-3.5.9-bin-hadoop3` distribution issue `#93` will build its image from, since S3A classes are loaded from Spark's own `hadoop-client-*` jars; using a mismatched `hadoop-aws` is a well-documented source of `NoSuchMethodError`/classpath skew |
| `aws-java-sdk-bundle` | `1.12.262` | The exact SDK version `hadoop-aws:3.3.4` itself declares as a compile dependency (`HADOOP-18344`, bumped for the Jackson CVE-2018-7489 fix); pinning anything else risks the same class-conflict problem as above |

Issue `#93` must verify at implementation time that `spark-3.5.9-bin-hadoop3`
still ships Hadoop `3.3.4` client jars before building its image (Spark's
bundled Hadoop version has changed across minor lines before); if it does
not, the `hadoop-aws`/`aws-java-sdk-bundle` pins above must be revised
together, not independently.

**Catalog and warehouse layout**:

| Decision | Locked choice | Why this over the alternative |
| --- | --- | --- |
| Number of catalogs | **One** Spark catalog, `spark.sql.catalog.lakehouse`, `type=hadoop` | A separate catalog per medallion layer (`bronze`/`silver`/`gold` each its own Hadoop catalog) was considered and rejected: three catalog roots to configure/debug for no functional gain, when Iceberg namespaces already give layer separation under one catalog |
| Warehouse root | `s3a://lakehouse/warehouse` | Deliberately a **different** prefix from `lakehouse/bronze`, `lakehouse/silver`, `lakehouse/gold` (created in issue `#91`) to avoid confusing two different things that happen to share layer names: those three prefixes are the raw, pre-Iceberg file landing zone future ingestion issues (`#97`+) write into; `warehouse/` is where Iceberg itself lays out `<namespace>/<table>/{data,metadata}` — mixing raw files and Iceberg-managed table directories under the same prefix risks Iceberg's own listing/commit logic tripping over unrelated objects |
| Namespaces inside the warehouse | `bronze`, `silver`, `gold` (Iceberg databases under the one catalog, e.g. `lakehouse.bronze.<table>`, `lakehouse.silver.<table>`, `lakehouse.gold.<table>`) | Mirrors the medallion architecture at the table level without needing three catalogs; matches how issues `#98`/`#99` already talk about "bronze -> silver -> gold" as a single pipeline over one warehouse |
| Credentials in Spark/Hadoop conf | `fs.s3a.aws.credentials.provider = org.apache.hadoop.fs.s3a.EnvironmentVariableCredentialsProvider`, reading `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` from pod env, not literal keys in a committed conf file | Same "nothing committed to git" convention issue `#91` used for the `minio-root-credentials`/`postgresql-gold-credentials` secrets; issue `#93` wires those env vars into the Spark driver/executor pod specs from the existing `minio-root-credentials` secret, no new secret needed |
| Config file location | `infra/spark-conf/iceberg-catalog.conf` (a Spark `--properties-file`-style properties file), documented by `infra/spark-conf/README.md` | Mirrors the `infra/helm-values/` pattern issue `#91` established: one directory per config concern, with its own README explaining what's pinned and why; keeps Spark/Iceberg config out of `src/` (it is deployment config, not application logic) |

Required `fs.s3a.*` / Iceberg keys to be written into that properties file
(values, not literal secrets):

- `spark.sql.catalog.lakehouse=org.apache.iceberg.spark.SparkCatalog`
- `spark.sql.catalog.lakehouse.type=hadoop`
- `spark.sql.catalog.lakehouse.warehouse=s3a://lakehouse/warehouse`
- `spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions`
- `spark.hadoop.fs.s3a.endpoint=http://minio.tfm-lakehouse.svc.cluster.local:9000`
  (in-cluster Kubernetes DNS for the `minio` Service issue `#91` created;
  confirm the exact Service name/port with `kubectl get svc -n
  tfm-lakehouse` at implementation time rather than assuming)
- `spark.hadoop.fs.s3a.path.style.access=true` (required for MinIO; virtual-
  host-style addressing resolves to nothing for a self-hosted endpoint)
- `spark.hadoop.fs.s3a.connection.ssl.enabled=false` (no TLS configured for
  MinIO per issue `#91`'s scope; local cluster only)
- `spark.hadoop.fs.s3a.aws.credentials.provider=org.apache.hadoop.fs.s3a.EnvironmentVariableCredentialsProvider`

Files touched: none (decision record only, folded into this section).

### Task 1 - Branch (done)

Branch `issue-92-iceberg-catalog-on-minio` created off `development`.
Files touched: none (git operation only).

### Task 2 - Warehouse path creation

- 2.1 confirm (or create, if the chart's `defaultBuckets` prefix-creation
  does not extend to arbitrary sub-paths) the `s3a://lakehouse/warehouse`
  root exists and is writable, using the same `mc`/`kubectl run` pattern
  issue `#91` used for its bucket round-trip check
- 2.2 do **not** pre-create `bronze/`, `silver/`, `gold/` folders under
  `warehouse/` by hand — Iceberg's Hadoop catalog creates namespace/table
  directories itself on first `CREATE NAMESPACE`/`CREATE TABLE`; a smoke
  test of that creation happens together with issue `#93`, per this
  issue's "Verification" section below

Files to modify (user): none expected (verification-only task, unless the
bucket check requires a one-off `mc` command captured in documentation).

### Task 3 - Iceberg/S3A catalog configuration file

- 3.1 write `infra/spark-conf/iceberg-catalog.conf` with the exact
  properties listed in Task 0 above
- 3.2 write `infra/spark-conf/README.md`: what the file is, how issue `#93`
  should consume it (`spark-submit --properties-file
  infra/spark-conf/iceberg-catalog.conf ...` or baked into the Spark image),
  and the credentials-via-env-var convention (pointing at the existing
  `minio-root-credentials` secret from issue `#91`, not a new one)

Files to modify (user): `infra/spark-conf/iceberg-catalog.conf` (new),
`infra/spark-conf/README.md` (new).

### Task 4 - Jar/version resolvability verification

- 4.1 verify each pinned artifact from Task 0 actually resolves before
  committing to the pins, the same "verified pullable against the live
  registry" discipline issue `#91` used for its container images:
  `spark-3.5.9-bin-hadoop3.tgz` from the Apache Spark archive/mirror,
  `iceberg-spark-runtime-3.5_2.12:1.11.0`, `hadoop-aws:3.3.4`, and
  `aws-java-sdk-bundle:1.12.262` from Maven Central
- 4.2 record the exact download URLs/coordinates used in
  `infra/spark-conf/README.md` so issue `#93` does not need to re-derive
  them

Files to modify: `infra/spark-conf/README.md` (extends Task 3's file).

### Task 5 - Documentation protocol close-out (this assistant, same session as implementation)

- 5.1 this issue document: `Adjustments Made During Implementation`,
  `Implementation Performed`, `Verification` (cross-referencing the
  end-to-end proof that actually happens in issue `#93`), `Findings`,
  `Known Limitations`, `Impact On Future Issues`, `Status` -> `Completed`
- 5.2 `docs/context/tfm/current_status.md`: new entry, same style as issues
  `#90`/`#91`'s
- 5.3 `docs/pipeline/known_limitations.md`: add an entry if warranted (e.g.
  if the Spark/Hadoop bundled-version check in Task 0 turns up a mismatch
  that forces a deviation)
- 5.4 `docs/roadmap/tfm/tfm_roadmap.md`: issue `#92` status row ->
  `Completed`
- 5.5 `infra/README.md`: add the `spark-conf/` entry (new subdirectory,
  same pattern as the existing `k3s/`/`helm-values/` entries)
- 5.6 `PROJECT_GUIDE.md`: only if the documentation map changed (the new
  `infra/spark-conf/README.md` entry)

Files to modify: this assistant, all of the above. Not yet executed — this
task runs during implementation, not during this planning session.

## Adjustments Made During Implementation

- The original plan deferred jar-version pinning to "the Spark version
  chosen in issue `#93`", while issue `#93`'s own plan expected to inherit
  "the Iceberg/S3A dependencies from issue `#92`" -- a circular dependency
  neither issue actually resolved. Fixed by locking the Spark version here
  too (Task 0), so issue `#93` has a fixed, already-verified target instead
  of re-deciding it. See the "Original Plan" section above for the full
  decision record and rationale.
- The MinIO in-cluster endpoint assumed in Task 0
  (`minio.tfm-lakehouse.svc.cluster.local:9000`) was confirmed live via
  `kubectl get svc -n tfm-lakehouse` (Service `minio`, port `9000`) rather
  than left as an assumption.

## Implementation Performed

- Task 2: confirmed `s3a://lakehouse/warehouse` is writable with an
  `mc pipe` / `mc ls` / `mc rm` round-trip via a throwaway
  `minio-warehouse-check` pod (deleted after the check); no folders were
  pre-created under it, per the plan (Iceberg creates its own namespace/
  table directories on first `CREATE NAMESPACE`/`CREATE TABLE`).
- Task 3: wrote `infra/spark-conf/iceberg-catalog.conf` (the Iceberg
  Hadoop-catalog + S3A properties for Spark) and
  `infra/spark-conf/README.md` (purpose, consumption via
  `spark-submit --properties-file`, and the credentials-via-env-var wiring
  issue `#93` must do against the existing `minio-root-credentials`
  secret).
- Task 4: verified all four pinned artifacts resolve (`curl -I`, all
  HTTP 200): the `spark-3.5.9-bin-hadoop3.tgz` archive, `iceberg-spark-
  runtime-3.5_2.12:1.11.0`, `hadoop-aws:3.3.4`, and `aws-java-sdk-
  bundle:1.12.262` from Maven Central. Additionally confirmed directly
  from `hadoop-project-3.3.4.pom` (not just secondary sources) that
  Hadoop `3.3.4` itself pins `aws-java-sdk.version=1.12.262`, matching the
  bundle version chosen here exactly.

## Verification

Done this session: the warehouse path round-trip (Task 2) and the jar/
tarball resolvability checks (Task 4), both above.

Supplied by issue `#93` (Spark Job Execution From Airflow): an actual
Spark session, running from Airflow via `spark-submit --master k8s://...`,
created namespace `lakehouse.smoke_test`, created and wrote to table
`ping` through this exact catalog configuration
(`infra/spark-conf/iceberg-catalog.conf`), and a separate, independent
throwaway pod re-queried that table afterward and got back the same two
rows (`INDEPENDENT_VERIFY_ROW_COUNT=2`). This catalog configuration is now
proven end-to-end, not just pinned and resolvable. Full detail in
`docs/roadmap/tfm/issues/issue-93-spark-job-execution-from-airflow.md`'s
Verification section.

## Findings

- Confirmed the circular jar-version dependency between this issue and
  issue `#93` described above; resolved by locking the full version set
  (Spark, Iceberg runtime, hadoop-aws, aws-java-sdk-bundle) here instead of
  splitting the decision across both issues.
- `hadoop-aws`'s AWS SDK dependency version is not declared in its own POM
  but inherited from `hadoop-project`'s `aws-java-sdk.version` property;
  worth knowing for future dependency updates -- bumping `hadoop-aws`
  alone without checking the matching `hadoop-project` pin can silently
  change the SDK version.

## Known Limitations

- Resolved by issue `#93`: `spark-3.5.9-bin-hadoop3` was confirmed to
  bundle Hadoop `3.3.4` client jars exactly
  (`hadoop-client-api-3.3.4.jar`/`hadoop-client-runtime-3.3.4.jar`), so no
  jar-pin revision was needed.
- Resolved by issue `#93`: a Spark session created a namespace/table
  through this catalog configuration and it was independently read back;
  the catalog is proven to work, not just pinned and resolvable. One
  correction did surface along the way: the
  `fs.s3a.aws.credentials.provider` class this issue locked
  (`org.apache.hadoop.fs.s3a.EnvironmentVariableCredentialsProvider`) does
  not exist in `hadoop-aws:3.3.4`; corrected in
  `infra/spark-conf/iceberg-catalog.conf` to the real class,
  `com.amazonaws.auth.EnvironmentVariableCredentialsProvider`, from
  `aws-java-sdk-bundle`.
- Per the epic, a Hive Metastore, REST catalog, or Nessie versioned
  catalog are explicitly deferred to future work; this issue only
  configures the Hadoop path-based catalog.

The two resolved items above are also updated in
`docs/pipeline/known_limitations.md` ("Infrastructure Limitations (TFM)"
-> "Iceberg Hadoop-Catalog Configuration Is Pinned And Now Proven
End-To-End (Resolved)").

## Impact On Future Issues

Issue `#93` (Spark Job Execution From Airflow) consumes
`infra/spark-conf/iceberg-catalog.conf` directly, must wire
`AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` into the Spark pod env from the
`minio-root-credentials` secret as documented in
`infra/spark-conf/README.md`, and must re-verify the Spark/Hadoop bundled-
version pairing before finalizing its image. It also provides this issue's
own missing end-to-end proof (a table written and read back through this
catalog). Every later Spark job (issues `#98`, `#99`, `#101`) depends on
this catalog configuration being correct.

## Status

`Completed` -- catalog/warehouse design locked, config file authored, all
jar/tarball pins verified resolvable, and the end-to-end proof supplied by
issue `#93`.
