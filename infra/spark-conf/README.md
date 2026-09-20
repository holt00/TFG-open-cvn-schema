# Spark/Iceberg config (issue #92)

Iceberg Hadoop-catalog and S3A properties for Spark jobs running against the
`tfm-lakehouse` k3s cluster. This directory holds Spark deployment config,
not application logic (that stays under `src/tfm_lakehouse/` once issue
`#93`+ create it).

See `docs/roadmap/tfm/issues/issue-92-iceberg-catalog-on-minio.md` for the
full decision record (Task 0) behind every choice below.

## `iceberg-catalog.conf`

A Spark properties file (`spark-submit --properties-file
infra/spark-conf/iceberg-catalog.conf ...`) configuring:

- one Iceberg Hadoop catalog, `lakehouse`, rooted at
  `s3a://lakehouse/warehouse` -- deliberately separate from the
  `lakehouse/bronze|silver|gold` raw file-landing prefixes created in issue
  `#91`, so Iceberg's own namespace/table directory layout never mixes with
  raw landed files. Iceberg tables are addressed as
  `lakehouse.bronze.<table>`, `lakehouse.silver.<table>`,
  `lakehouse.gold.<table>` (namespaces created on first `CREATE NAMESPACE`,
  not pre-created by hand).
- the S3A settings MinIO requires: path-style addressing, no TLS (matches
  issue `#91`'s scope, local cluster only), and the in-cluster endpoint for
  the `minio` Service (`minio.tfm-lakehouse.svc.cluster.local:9000`,
  confirmed live via `kubectl get svc -n tfm-lakehouse` during issue `#92`).

## RBAC (issue #93, Task 2)

`spark-rbac.yaml` creates a dedicated `spark` `ServiceAccount` in
`tfm-lakehouse`, bound via a namespaced `Role` (verbs `create`/`get`/
`list`/`watch`/`delete`/`deletecollection` on `pods`/`services`/
`configmaps`/`persistentvolumeclaims`) and a `RoleBinding`. This is what
lets a Spark driver running in `client` deploy mode (see "Deploy mode"
below) create its own executor pods and headless service, and clean them
up again on shutdown -- `deletecollection` is required in addition to
`delete` because the driver's shutdown path bulk-deletes those resources
by label selector, a distinct RBAC verb (found the hard way in issue
`#93`'s Task 8: without it, the job itself succeeds but the driver pod
still ends in `Error` from the failed cleanup). Applied with:

```bash
kubectl apply -f infra/spark-conf/spark-rbac.yaml
```

Verified with `kubectl auth can-i <create|deletecollection>
<pods|services|configmaps|persistentvolumeclaims>
--as=system:serviceaccount:tfm-lakehouse:spark -n tfm-lakehouse` (all
`yes`).

## Deploy mode (issue #93)

`client`, not `cluster`: the Airflow `KubernetesPodOperator` pod that runs
`spark-submit` becomes the Spark driver process itself, rather than
`spark-submit` asking the Kubernetes API to create a second, separate
driver pod. One pod layer instead of two; logs stream directly into the
Airflow task log.

This has a consequence easy to miss: Spark only ever builds a driver *pod
spec* itself in `cluster` mode. In `client` mode, any
`spark.kubernetes.driver.*` property that configures a pod spec --
`secretKeyRef`, `authenticate.driver.serviceAccountName`, etc. -- is a
silent no-op for the driver (confirmed the hard way in issue `#93`'s Task
8). `iceberg-catalog.conf` still sets
`spark.kubernetes.authenticate.driver.serviceAccountName=spark` as an
accurate statement of intent, but the launcher pod's actual ServiceAccount
and credentials are set directly on the `KubernetesPodOperator` pod spec
in `dags/issue93_spark_iceberg_smoke_test.py`, not via that property.
`spark.kubernetes.executor.*` properties are unaffected by this and work
normally, since Spark always creates executor pods itself regardless of
driver deploy mode.

## Credentials wiring (issue #93)

The properties file sets
`fs.s3a.aws.credentials.provider=com.amazonaws.auth.EnvironmentVariableCredentialsProvider`
(from `aws-java-sdk-bundle` -- the class of the same name under
`org.apache.hadoop.fs.s3a` that issue `#92` originally referenced does not
actually exist in `hadoop-aws:3.3.4`, found the hard way in issue `#93`'s
Task 8) and intentionally contains no key material.
`spark.kubernetes.executor.secretKeyRef.*` in that file mounts
`AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` from the existing
`minio-root-credentials` Kubernetes Secret (created in issue `#91`)
directly onto executor pods. The driver's copy of those same env vars is
set on the `KubernetesPodOperator` pod spec instead, per the deploy-mode
no-op note above. Do not create a new secret or commit literal keys
anywhere in this repository.

## Pinned versions and where to get them (issue #92, Task 0/4)

Chosen for mutual compatibility (matching Hadoop client jars bundled inside
the Spark distribution), not just recency. Every coordinate below was
verified to actually resolve on 2026-09-15 (see commands below); issue
`#93` should re-verify before building its image in case an artifact is
later removed/moved.

| Artifact | Version | Source |
| --- | --- | --- |
| Apache Spark | `3.5.9` | `https://archive.apache.org/dist/spark/spark-3.5.9/spark-3.5.9-bin-hadoop3.tgz` |
| Iceberg Spark runtime | `iceberg-spark-runtime-3.5_2.12:1.11.0` | `https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.5_2.12/1.11.0/iceberg-spark-runtime-3.5_2.12-1.11.0.jar` |
| `hadoop-aws` | `3.3.4` | `https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar` |
| `aws-java-sdk-bundle` | `1.12.262` | `https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar` |

`hadoop-aws:3.3.4` and `aws-java-sdk-bundle:1.12.262` must match the Hadoop
client version actually bundled inside whichever `spark-3.5.9-bin-hadoop3`
build issue `#93` uses -- verify that pairing at implementation time (see
the issue document's Task 0 note) rather than assuming it still holds.

Only the Iceberg **runtime** jar should be added to the Spark classpath
(never `iceberg-core`/`iceberg-parquet` etc. alongside it) to avoid the
dependency-version conflicts the Iceberg project's own packaging guidance
warns about.

**Confirmed (issue `#93`, Task 3, 2026-09-16)**: unpacking the real
`spark-3.5.9-bin-hadoop3.tgz` shows `jars/hadoop-client-api-3.3.4.jar` and
`jars/hadoop-client-runtime-3.3.4.jar` -- Hadoop `3.3.4` exactly, matching
the pin above. No revision needed; all four artifacts re-verified
resolvable (`curl -I`, HTTP 200) the same day.

## Building and loading the Spark image (issue #93, Task 4)

Base image via Spark's own image-build tooling (correct k8s entrypoint/UID
handling out of the box), then a thin custom layer adding the three jars
above plus this directory's `iceberg-catalog.conf` and the smoke-test job,
baked in rather than mounted (see "Smoke-test script delivery" in the issue
document's Task 0):

```bash
# from the unpacked spark-3.5.9-bin-hadoop3/ directory
./bin/docker-image-tool.sh -r tfm-lakehouse -t 3.5.9-iceberg1.11.0-base \
  -p kubernetes/dockerfiles/spark/bindings/python/Dockerfile build

# from the repo root
docker build -f infra/spark-conf/Dockerfile \
  -t tfm-lakehouse/spark-py:3.5.9-iceberg1.11.0 .

# no registry in this cluster: load the built image straight into k3s's
# own containerd store
docker save tfm-lakehouse/spark-py:3.5.9-iceberg1.11.0 | sudo k3s ctr images import -
sudo k3s ctr images ls | grep tfm-lakehouse/spark-py
```

Referenced from `iceberg-catalog.conf` via
`spark.kubernetes.container.image` with `pullPolicy=IfNotPresent`, so
`spark-submit` never tries to pull it from a registry.

## Silver image: repository code on the Spark Python (issue #98)

The bronze -> silver job reuses the repository's own code
(`src/open_cvn/parser_contract.py`, `src/tfm_lakehouse/`), which needs
`pydantic`, `jsonschema` and `requests`. The image above has none of them, and
it runs Python **3.10.12** while the repository requires `>=3.14`. PySpark 3.5
requires driver and executors to run the same Python minor version and does
not support 3.14, so the job runs on the image's 3.10 with those three
libraries added, and the code it imports stays compatible with 3.10 (no
`datetime.UTC`, `StrEnum`, `tomllib`; a test parses the Spark-side modules
with `ast.parse(feature_version=(3, 10))`).

`Dockerfile.silver` layers `requirements-silver.txt` on the issue `#93` image
and does nothing else:

```bash
# from the repo root
docker build -f infra/spark-conf/Dockerfile.silver \
  -t tfm-lakehouse/spark-py:3.5.9-iceberg1.11.0-silver .

# no registry in this cluster: load it into k3s's containerd (needs sudo)
docker save tfm-lakehouse/spark-py:3.5.9-iceberg1.11.0-silver | sudo k3s ctr images import -
sudo k3s ctr images ls | grep spark-py
```

- The three direct dependencies equal `uv.lock`. The transitive ones are the
  versions pip resolves for Python 3.10, because `uv.lock`'s `rpds-py 2026.6.3`
  requires Python >=3.11.
- The code (`src/`) and the JSON Schema (`schemas/`) are **not** in the image.
  The job mounts them from the repository checkout with hostPath on the driver
  pod and, through `spark.kubernetes.executor.volumes.hostPath.*`, on every
  executor, with `PYTHONPATH=/repo/src` (driver: pod `env`; executors:
  `spark.executorEnv.PYTHONPATH`). Code changes need no rebuild. Like issue
  `#97`'s ingest pods, this is only valid because k3s is a single node on the
  machine that holds the checkout.
- `iceberg-catalog.conf` still names the issue `#93` image in
  `spark.kubernetes.container.image`. The silver job's launcher overrides it
  with `--conf spark.kubernetes.container.image=...-silver`; without the
  override the executors would start without the three libraries. The `#93`
  DAG is untouched.
- Rebuild and re-import only when `requirements-silver.txt` changes.

## Gold image: PostgreSQL JDBC driver (issue #99)

The silver -> gold job needs nothing new, but the job that publishes gold to the
dedicated PostgreSQL (`svc/postgresql`, database `gold`) needs the JDBC driver, which
no earlier image has. `Dockerfile.gold` layers `postgresql-42.7.13.jar` (the latest
release on Maven Central when the issue was planned) on the silver image and does
nothing else:

```bash
# from the repo root
docker build -f infra/spark-conf/Dockerfile.gold \
  -t tfm-lakehouse/spark-py:3.5.9-iceberg1.11.0-gold .

# no registry in this cluster: load it into k3s's containerd (needs sudo)
docker save tfm-lakehouse/spark-py:3.5.9-iceberg1.11.0-gold | sudo k3s ctr images import -
sudo k3s ctr images ls | grep spark-py
```

- The jar sits in `/opt/spark/jars`, on the JVM's system classpath, not only on
  `--jars`: the publish job opens a plain `java.sql.DriverManager` connection to run
  its table swap in one transaction, and `DriverManager` does not see a driver that
  was only added with `--jars` (verified in the issue's Task 1.4 spike).
- `--packages` was rejected: it downloads from the internet on every run.
- Credentials: only the launcher pod (the Spark driver) of the publish task gets
  `PG_PASSWORD`, by `secretKeyRef` on `postgresql-gold-credentials` (key `password`).
  The executors need no PostgreSQL variable: the password travels inside the JDBC write's
  options (confirmed on the cluster in issue `#99`'s Task 8). Nothing secret is in git.
- `iceberg-catalog.conf` is unchanged: each launcher overrides
  `spark.kubernetes.container.image`, as the silver one does.
- Rebuild and re-import only when the driver version changes.
