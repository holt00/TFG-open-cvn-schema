# Issue 93 - Spark Job Execution From Airflow

## Summary

Build a Spark image and prove `spark-submit` can be launched from Airflow
against the k3s cluster, reading and writing Iceberg tables through the
catalog from issue `#92`. Second issue of TFM epic phase 1.

## Original Goal

An end-to-end proof that Spark, Iceberg, and Airflow work together on this
cluster, before any real ingestion or transform logic is built on top of it.

## Original Plan

Planned in a dedicated planning session before implementation started
(2026-09-16), following the same execution convention issues `#91`/`#92`
used: every open decision the epic/issue text left unresolved is locked in
advance (Task 0 below) before any file is touched, then work proceeds task
by task in the order below; each task names exactly which files (if any)
need a human edit.

### Task 0 - Decisions Locked (research, no files changed)

Research performed (web search, 2026-09-16) to resolve every design choice
the original plan above left open, choosing the option that minimizes new
moving parts for a local single-node k3s cluster, consistent with issues
`#90`-`#92`'s own Task 0 approach.

| Decision | Locked choice | Why this over the alternative |
| --- | --- | --- |
| Spark deploy mode | `client` | The Airflow task pod itself becomes the Spark driver process; only one pod layer to reason about (driver pod = the pod Airflow already created), logs stream straight into the Airflow task log. `cluster` mode would have `spark-submit` ask the Kubernetes API to create a *second*, separate driver pod, adding a layer with no benefit here since Airflow already recycles the submitting pod either way. |
| Airflow trigger mechanism | `KubernetesPodOperator` running the custom Spark image, command = `spark-submit` | In-cluster Kubernetes auth is automatic (the pod's mounted ServiceAccount token), no kubeconfig to manage. Keeps the Spark/Iceberg/Hadoop dependency surface entirely inside a dedicated Spark image instead of bloating the Airflow image itself (a `BashOperator` on a generic Airflow worker would need Spark and every jar baked into the Airflow image, plus manual kubeconfig wiring, to reach the same cluster it is already running on). |
| Spark image build method | Spark's own `bin/docker-image-tool.sh -p kubernetes/dockerfiles/spark/bindings/python/Dockerfile` (from the unpacked `3.5.9` tarball) as the base image, extended by one small custom `Dockerfile` layer on top | The upstream tool already gets the k8s-specific entrypoint, UID/GID handling, and `SPARK_HOME` layout right; hand-writing a Dockerfile from scratch would re-implement that plumbing with real risk of a subtle submit-time bug. The custom layer on top only adds the three verified jars (Task 3) and the smoke-test script/conf (Task 6). |
| Image distribution (no registry deployed) | Build locally with `docker build`, then `docker save <image> \| sudo k3s ctr images import -` directly into k3s's containerd store; pod spec uses `imagePullPolicy: IfNotPresent` | Single-node k3s on the same WSL2 machine the image is built on (issue `#90`); no registry exists in this cluster and standing one up is out of scope. `ctr images import` is the documented way to hand a locally built image straight to k3s's own containerd without one. |
| Driver/executor Kubernetes RBAC | Dedicated `spark` `ServiceAccount` in `tfm-lakehouse`, bound via a namespaced `Role` (verbs `create`/`get`/`list`/`watch`/`delete` on `pods`, `services`, `configmaps`) and a `RoleBinding` — not a `ClusterRole` | The Spark driver only ever creates executor pods and a headless service in its own namespace; a namespaced `Role` is the documented minimum, and stays consistent with this cluster's single-namespace (`tfm-lakehouse`) scope. |
| Credential injection into driver + executor pods | Spark's native `spark.kubernetes.{driver,executor}.secretKeyRef.<ENV_NAME>=minio-root-credentials:<key>` config properties, added to `infra/spark-conf/iceberg-catalog.conf` | `spark-submit` itself instructs Kubernetes to mount the existing secret's keys as env vars on both driver and executor pod specs — no new secret (same convention as issues `#91`/`#92`), and no hand-written pod-template YAML needed just to set two env vars. |
| Smoke-test script delivery | Baked into the custom Spark image at a fixed path (`COPY`'d at build time), not mounted from the Airflow DAGs PVC | This issue is a one-off proof, not the real ingestion pipeline; rebuilding the image on script change is an acceptable cost here. Issues `#97`/`#99` (real DAGs) must decide their own job-code delivery mechanism independently — not solved by this choice. |

Files touched: none (decision record only, folded into this section).

### Task 1 - Branch (done)

Branch `issue-93-spark-job-execution-from-airflow` created off
`origin/development` (which already includes issue `#92`'s squash-merged
commit). Files touched: none (git operation only).

### Task 2 - RBAC for the Spark driver

- 2.1 write `infra/spark-conf/spark-rbac.yaml`: `ServiceAccount spark`,
  `Role` (verbs above on `pods`/`services`/`configmaps`), `RoleBinding`, all
  namespaced to `tfm-lakehouse`
- 2.2 `kubectl apply -f infra/spark-conf/spark-rbac.yaml`
- 2.3 verify with `kubectl auth can-i create pods --as=system:serviceaccount:tfm-lakehouse:spark -n tfm-lakehouse` (and `services`, `configmaps`)

Files to modify: `infra/spark-conf/spark-rbac.yaml` (new, this assistant
per this session's explicit autonomy instruction), `infra/spark-conf/README.md`
(extended).

### Task 3 - Bundled-Hadoop-version verification and jar re-verification

- 3.1 download and unpack `spark-3.5.9-bin-hadoop3.tgz`; inspect `jars/` for
  the actual bundled `hadoop-common-*`/`hadoop-client-*` version
- 3.2 compare against the `hadoop-aws:3.3.4` pin issue `#92` locked from the
  well-known Spark-3.5-line default (not from unpacking); if it does not
  match, pick a revised `hadoop-aws`/`aws-java-sdk-bundle` pair from that
  Hadoop release's own `hadoop-project` POM (never guessed independently),
  and record the deviation here, in `infra/spark-conf/README.md`, and in
  `docs/pipeline/known_limitations.md`
- 3.3 re-verify (`curl -I`, expect HTTP 200) all four pinned artifacts still
  resolve, since time has passed since issue `#92`'s own check

Files to modify: `infra/spark-conf/README.md` (only if Task 3.2 finds a
mismatch), this issue document's "Adjustments Made During Implementation"
(only if a deviation occurs).

### Task 4 - Build the Spark container image

- 4.1 `bin/docker-image-tool.sh -r <local-tag-prefix> -t 3.5.9-iceberg1.11.0 -p kubernetes/dockerfiles/spark/bindings/python/Dockerfile build`
  from the unpacked tarball, producing the upstream-correct PySpark-on-k8s
  base image
- 4.2 write a small custom `Dockerfile` `FROM` that base image: `COPY` the
  three verified jars (Task 3) into `$SPARK_HOME/jars/`, `COPY`
  `infra/spark-conf/iceberg-catalog.conf` and the Task 6 smoke-test script
  into fixed in-image paths; build this as the final tagged image
- 4.3 `docker save <image>:<tag> | sudo k3s ctr images import -`; confirm
  with `k3s ctr images ls | grep spark`

Files to modify: a new `Dockerfile` under `infra/spark-conf/` (this
assistant, per this session's autonomy instruction), `infra/spark-conf/README.md`
(build/import commands documented).

### Task 5 - Wire MinIO credentials into the properties file

- 5.1 add the `spark.kubernetes.driver.secretKeyRef.*` /
  `spark.kubernetes.executor.secretKeyRef.*` properties (Task 0) to
  `infra/spark-conf/iceberg-catalog.conf`, referencing
  `minio-root-credentials` by name/key only
- 5.2 confirm no literal key material is added anywhere in the repo

Files to modify: `infra/spark-conf/iceberg-catalog.conf` (extended).

### Task 6 - Trivial Iceberg smoke-test job

- 6.1 write `src/tfm_lakehouse/jobs/iceberg_smoke_test.py`: creates a
  namespace under the `lakehouse` catalog if absent, creates a small
  Iceberg table, inserts a few rows, reads them back, prints a row count
  for log-based verification
- 6.2 baked into the image per Task 0/4.2, not delivered via the DAGs PVC

Files to modify: `src/tfm_lakehouse/jobs/iceberg_smoke_test.py` (new).

### Task 7 - Airflow DAG

- 7.1 write a minimal DAG using `KubernetesPodOperator` against the image
  from Task 4, command runs `spark-submit --master k8s://kubernetes.default.svc:443
  --deploy-mode client --properties-file <in-image path to iceberg-catalog.conf>
  --conf spark.kubernetes.container.image=<image> --conf
  spark.kubernetes.authenticate.driver.serviceAccountName=spark
  local:///opt/spark/jobs/iceberg_smoke_test.py`
- 7.2 deliver the DAG file to the `dag-processor` pod's DAGs PVC (not
  `scheduler` — issue `#91`'s finding)
- 7.3 unpause the DAG (`airflow dags unpause`), since newly parsed DAGs
  default to `is_paused=True` (also issue `#91`'s finding)

Files to modify: a new DAG file (this assistant, per this session's
autonomy instruction; delivered into the cluster the same way issue `#91`'s
smoke-test DAG was).

### Task 8 - End-to-end verification

- 8.1 trigger the DAG, watch driver/executor pods come up
  (`kubectl get pods -n tfm-lakehouse -w`)
- 8.2 confirm task success (`airflow tasks state`)
- 8.3 independently re-query the written table via a throwaway
  `pyspark`/`spark-sql` pod using the same catalog config, proving the data
  persists and is queryable after the job pod is gone — this is also the
  end-to-end proof issue `#92` left pending (see that issue's
  "Verification" and `docs/pipeline/known_limitations.md`'s Iceberg
  Hadoop-catalog entry); once it passes, issue `#92`'s status should move
  from `In Progress` to `Completed`

Files to modify: none (verification-only task).

### Task 9 - Documentation protocol close-out (this assistant, same session)

- 9.1 this issue document: `Adjustments Made During Implementation`,
  `Implementation Performed`, `Verification`, `Findings`, `Known
  Limitations`, `Impact On Future Issues`, `Status` -> `Completed`
- 9.2 `docs/context/tfm/current_status.md`: new entry, same style as issues
  `#90`-`#92`'s
- 9.3 `docs/pipeline/known_limitations.md`: resolve/update the "Iceberg
  Hadoop-Catalog Configuration Is Pinned But Not Yet Proven End-To-End"
  entry, add new entries for any findings from Tasks 3/4/8
- 9.4 `docs/roadmap/tfm/tfm_roadmap.md`: issue `#93` status row ->
  `Completed`, **and** issue `#92`'s row -> `Completed` (per Task 8.3 above)
- 9.5 `docs/roadmap/tfm/issues/issue-92-iceberg-catalog-on-minio.md`: close
  out its own `Verification`/`Status` sections now that Task 8.3 supplies
  its missing end-to-end proof
- 9.6 `infra/README.md` / `infra/spark-conf/README.md`: document the new
  RBAC manifest, Dockerfile, and image build/import commands
- 9.7 `PROJECT_GUIDE.md`: only if the documentation map changed

Files to modify: this assistant, all of the above.

## Adjustments Made During Implementation

- Task 3 found the bundled Hadoop version matched exactly
  (`spark-3.5.9-bin-hadoop3`'s `jars/hadoop-client-api-3.3.4.jar` and
  `hadoop-client-runtime-3.3.4.jar`), so issue `#92`'s `hadoop-aws:3.3.4`/
  `aws-java-sdk-bundle:1.12.262` pins needed no revision.
- Task 0's `fs.s3a.aws.credentials.provider` class name, inherited verbatim
  from issue `#92`'s properties file
  (`org.apache.hadoop.fs.s3a.EnvironmentVariableCredentialsProvider`), does
  not exist anywhere in `hadoop-aws:3.3.4` (confirmed by listing the jar's
  contents) -- this is exactly the gap issue `#92` flagged as unverified
  pending an end-to-end proof, and this issue's Task 8 run is what actually
  surfaced it. Corrected to the real class,
  `com.amazonaws.auth.EnvironmentVariableCredentialsProvider`, which ships
  in `aws-java-sdk-bundle` (confirmed the same way) and is what Hadoop's
  S3A connector actually loads via that config key.
- Task 0's credential-injection decision
  (`spark.kubernetes.{driver,executor}.secretKeyRef.*` in
  `infra/spark-conf/iceberg-catalog.conf`) only works for the **executor**
  side. `spark.kubernetes.driver.*` pod-spec properties are no-ops in
  `client` deploy mode: Spark only ever builds a driver pod spec itself in
  `cluster` mode, and in `client` mode the driver is whatever pod ran
  `spark-submit` in the first place. The driver silently ran with no AWS
  credentials until this was found. Corrected by setting
  `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` directly on the
  `KubernetesPodOperator` pod spec in the DAG file (via `secretKeyRef`),
  removing the dead `spark.kubernetes.driver.secretKeyRef.*` lines from the
  properties file. The same no-op applies to
  `spark.kubernetes.authenticate.driver.serviceAccountName`; that property
  was left in place as an accurate statement of intent, but the launcher
  pod's actual ServiceAccount is set via `KubernetesPodOperator`'s own
  `service_account_name`.
- The DAG's first version fully replaced the Spark image's own
  `ENTRYPOINT` (`cmds=["/bin/bash", "-c"]`) to run `spark-submit` directly.
  This skipped `/opt/entrypoint.sh`'s own `/etc/passwd` patch for the
  arbitrary `spark_uid` (`185`, no matching OS user by default), which
  cascaded into two separate crashes: Ivy's local-repo init
  (`java.lang.IllegalArgumentException: basedir must be absolute:
  ?/.ivy2/local`, from `user.home` resolving empty) and Hadoop's
  `UserGroupInformation` login (`NullPointerException: invalid null input:
  name`, from no OS username to resolve). Setting `HOME`,
  `JAVA_TOOL_OPTIONS=-Duser.home=/tmp`, and `HADOOP_USER_NAME` as
  workarounds did not fully resolve the second failure. The actual fix was
  to stop bypassing the entrypoint: the command now execs
  `/opt/entrypoint.sh /opt/spark/bin/spark-submit ...` (its `$1` is neither
  `driver` nor `executor`, so it falls into that script's own pass-through
  branch), which patches `/etc/passwd` correctly first (confirmed
  `/etc/passwd` is group-writable, group `0`, matching the pod's GID) and
  made all three of the above workaround env vars unnecessary.
- Task 2's RBAC `Role` (verbs `create`/`get`/`list`/`watch`/`delete` on
  `pods`/`services`/`configmaps`) was missing `deletecollection`, a
  distinct RBAC verb from `delete`: the Spark driver's shutdown path
  bulk-deletes its own executor pods, services, configmaps, and PVCs by
  label selector, which requires `deletecollection` specifically. The first
  successful job run still ended in pod state `Error` because of this
  (job itself succeeded; only post-job cleanup failed). Fixed by adding
  `deletecollection` and `persistentvolumeclaims` to the `Role`.

## Implementation Performed

- Task 2: `infra/spark-conf/spark-rbac.yaml` (`ServiceAccount spark`,
  namespaced `Role`, `RoleBinding`) applied to `tfm-lakehouse`; verified
  with `kubectl auth can-i` for every verb/resource combination used.
- Task 3: downloaded and unpacked the real `spark-3.5.9-bin-hadoop3.tgz`;
  confirmed bundled Hadoop `3.3.4` client jars match the existing pin;
  re-verified all four pinned artifacts still resolve (`curl -I`, HTTP 200).
- Task 4: built the base image with Spark's own
  `bin/docker-image-tool.sh -p kubernetes/dockerfiles/spark/bindings/python/Dockerfile`;
  wrote `infra/spark-conf/Dockerfile` on top of it (downloads the three
  verified jars at build time via `curl`, rather than committing binaries,
  plus bakes in the properties file and the smoke-test script); loaded the
  final image into k3s's containerd with
  `docker save ... | sudo k3s ctr images import -` (required the user's
  own sudo session, twice, once per image rebuild -- see Known Limitations).
- Task 5: added `spark.kubernetes.executor.secretKeyRef.*` to
  `infra/spark-conf/iceberg-catalog.conf` (driver-side credentials moved to
  the DAG file, see Adjustments).
- Task 6: `src/tfm_lakehouse/jobs/iceberg_smoke_test.py` (creates
  `lakehouse.smoke_test`, creates table `ping`, inserts 2 rows, reads them
  back, prints a row count).
- Task 7: `dags/issue93_spark_iceberg_smoke_test.py`, a `KubernetesPodOperator`
  task delivered to the `dag-processor` pod's DAGs PVC (via `kubectl cp`,
  not `scheduler` -- issue `#91`'s finding) and unpaused (also issue
  `#91`'s finding: new DAGs default `is_paused=True`).
- Task 8: triggered the DAG multiple times while iterating through the
  Adjustments above; the final run succeeded end to end.

## Verification

All executed, this session, on the final (corrected) run:

- Airflow task `spark_submit_iceberg_smoke_test` (DAG
  `issue93_spark_iceberg_smoke_test`) reported `state=success`
  (`airflow tasks states-for-dag-run`).
- The launcher/driver pod (`issue93-spark-submit-launcher-ogh0m087`)
  reached `Completed`; its log contains
  `ICEBERG_SMOKE_TEST_ROW_COUNT=2`, and two executor pods
  (`iceberg-smoke-test-*-exec-1`/`exec-2`) also reached `Completed`.
- Independent re-query (Task 8.3, also this issue's promised fulfillment
  of issue `#92`'s missing end-to-end proof): a separate throwaway pod
  (`issue93-iceberg-verify`, same image, `local[1]` master, no connection
  to the job that wrote the data) ran `SELECT COUNT(*)` and
  `SELECT * ... ORDER BY id` against `lakehouse.smoke_test.ping` through
  the same `infra/spark-conf/iceberg-catalog.conf`. Result:
  `INDEPENDENT_VERIFY_ROW_COUNT=2`, with exactly the two rows the job
  wrote (`1, issue-93-smoke-test` and `2, iceberg-on-minio`). Pod deleted
  after the check.

## Findings

- `hadoop-aws:3.3.4` never shipped any class named
  `EnvironmentVariableCredentialsProvider` in the `org.apache.hadoop.fs.s3a`
  package (or any subpackage) -- confirmed by listing the jar's contents.
  The correct class for reading `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`
  from the environment is `com.amazonaws.auth.EnvironmentVariableCredentialsProvider`,
  shipped in `aws-java-sdk-bundle`, also confirmed by listing that jar.
  Any future Hadoop/S3A credential-provider config in this repo should be
  verified against the actual jar contents, not assumed from the class's
  simple name.
- `spark.kubernetes.driver.*` pod-spec properties
  (`secretKeyRef`, `authenticate.driver.serviceAccountName`, and likely
  others in that family) are silent no-ops in `client` deploy mode. This
  is easy to miss because `spark-submit` neither errors nor warns; the
  driver just runs without whatever the property was supposed to set.
  Anything pod-spec-related for the driver in `client` mode must be set on
  the submitting pod's own spec (i.e., in the `KubernetesPodOperator`
  arguments in Airflow's case), not via `spark.kubernetes.driver.*` conf.
- Spark's own k8s images (built via `docker-image-tool.sh`) are designed to
  be invoked through their bundled `/opt/entrypoint.sh`, which is what
  patches `/etc/passwd` for an arbitrary UID (works because `/etc/passwd`
  is shipped group-writable, group `0`, matching the image's default GID)
  -- fully replacing the image's `ENTRYPOINT`/`CMD` to run `spark-submit`
  directly skips that patch and produces confusing downstream JVM/Hadoop
  errors (Ivy, `UserGroupInformation`) that look unrelated to their real
  cause. The correct pattern is to pass the desired command as *arguments*
  to the existing entrypoint (which passes through untouched for any `$1`
  other than `driver`/`executor`), not to override it.
- RBAC's `delete` and `deletecollection` are separate verbs; a `Role` that
  grants one does not implicitly grant the other. Spark's own driver
  shutdown path always attempts a label-selector bulk delete of its
  executor pods/services/configmaps/PVCs, so `deletecollection` on all four
  resource types is required even for the simplest possible job.

## Known Limitations

- The image build/load step (Task 4) is entirely manual and requires the
  user's own `sudo` session (`docker save | sudo k3s ctr images import -`)
  each time the image changes -- not automated, not CI-able yet. Any
  future issue that changes the Spark image will hit this same friction;
  worth automating (e.g. a local registry, or a passwordless-sudo policy
  scoped to this one command) before issue `#101`'s benchmark work, which
  will likely iterate on this image more.
- `on_finish_action="keep_pod"` on the DAG's `KubernetesPodOperator` leaves
  every run's launcher pod around after completion (deliberate, for this
  issue's own debugging and Task 8's manual inspection). Issues `#97`/`#99`
  should default to `delete_pod` for their real, repeatedly-run DAGs.
- The smoke-test script and properties file are baked into the Spark image
  rather than delivered from a shared, versioned location (Task 0's
  deliberate choice for this one-off proof). Issues `#97`/`#99` need their
  own job-code delivery decision; not solved here.
- No TLS/ingress involved anywhere in this issue, consistent with the
  cluster's existing local-only scope (issues `#90`/`#91`).

## Impact On Future Issues

Issues `#97` and `#99` (the real ingestion/transform DAGs) build directly
on the Spark-from-Airflow pattern proven here, and should reuse -- not
rediscover -- three things found the hard way in this issue: (1) route the
Spark image's command through its own `/opt/entrypoint.sh` rather than
replacing it, (2) driver-side pod-spec config (credentials, service
account) must be set on the `KubernetesPodOperator` pod spec directly in
`client` deploy mode, not via `spark.kubernetes.driver.*` properties, and
(3) the RBAC `Role` needs `deletecollection`, not just `delete`. Issue
`#92`'s status moves from `In Progress` to `Completed` as a direct result
of this issue's Task 8.3 independent re-query, which supplies the
end-to-end proof that issue explicitly left pending.

## Status

`Completed`
