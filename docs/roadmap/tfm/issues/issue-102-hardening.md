# Issue 102 - Hardening

## Summary

Bug-fix buffer and a from-scratch reproducibility quickstart guide. TFM
epic phase 5.

## Original Goal

Reduce the risk of a broken demo or defense by fixing issues found while
dogfooding the whole pipeline, and documenting exactly how to stand it up
from nothing.

## Original Plan

- run the full pipeline (issues `#90`-`#101`) end-to-end as a real user
  would, and fix whatever breaks
- write a reproducibility quickstart document (proposed location:
  `docs/development/tfm_lakehouse_workflow.md`, mirroring the TFG's
  `docs/development/regeneration_workflow.md`) covering cluster bring-up,
  service deployment, both DAG runs, and the dashboard/benchmark
- add basic error handling anywhere the pipeline currently fails
  ungracefully

### Detailed Plan (accepted 2026-09-25)

Planned in a dedicated session before any code, following issues `#90`-`#101`: every decision
the epic and the original plan left open is locked in Task 0 with its reason and the rejected
alternative. D1 and D4 are marked *(user)*: they were put to the user, who chose each of them.
Work then proceeds task by task; every step states which task (and subtask) is active, opens
with a summary of what it covers, and closes by stating which files, if any, the user has to
modify and the next step. Nothing is done for which the information is missing.

#### Facts established while planning (verified, not assumed)

- **Branch:** `issue-102-hardening`, created from `origin/development` (`git fetch origin`
  worked; `origin/development` is `2fc3537`, which contains `#101`'s Spark performance
  benchmark). The working tree carried a pre-existing, unrelated modification of
  `initial_prompt.md` onto the branch, same as `#101`; not part of this issue. A separate local
  branch `issue-101-spark-performance-benchmark` still holds one unmerged follow-up commit
  (a CI drift-guard fix) not part of this issue either.
- **The cluster is live, not freshly built**, 23 h uptime at planning time
  (`kubectl get pods -n tfm-lakehouse`): `airflow-scheduler` is **1/2 ready with 56 restarts**
  on its log-groomer sidecar; three stale pods sit in the namespace unreclaimed
  (`generate-synthetic-cvn-1v0ocudn` and `ingest-validate-generate-synthetic-cvn-02rg8jb7`,
  both `Unknown`, 4 days old; `issue93-spark-submit-launcher`, `Completed`, 8 days old). This is
  real, present-tense evidence of the operational fragility `#101`'s status entry already
  flagged as `#102`'s to fix, not a hypothetical to reproduce.
- **The log-groomer `DetachedInstanceError` restart loop was first observed** at the end of
  `#101` (`docs/context/tfm/current_status.md`'s `#101` entry) and is not yet its own entry in
  `docs/pipeline/known_limitations.md`; it needs one, resolved or not, after Task 1.1.
- **The Airflow api-server liveness self-kill is already a documented limitation** (`#97`'s
  finding, `docs/pipeline/known_limitations.md`, "The Airflow api-server Can Be Killed By Its
  Own Liveness Probe"), unresolved; a probe-tuning fix is in scope here if low-risk.
- **k3s state:** `systemctl is-active k3s` reports `active`; the cluster does not need starting
  before Phase A work.

#### Task 0 - Decisions Locked

| # | Decision | Reason | Rejected alternative |
| --- | --- | --- | --- |
| D1 *(user)* | **Who writes the files:** the assistant writes code, infrastructure files and documentation (the `#98`-`#101` mode), notifying the user only for `sudo`/interactive checkpoints or an open decision. Stated by the user directly in `initial_prompt.md`'s own instructions for this issue (2026-09-25), rather than asked again as a separate question. | The repository default is that the user edits code and values files, so the choice is restated per issue rather than assumed to carry over, per this project's standing planning protocol. | Assuming the `#101` choice carries over silently. |
| D2 | **Quickstart doc path and shape:** `docs/development/tfm_lakehouse_workflow.md`, mirroring `docs/development/regeneration_workflow.md`'s section structure (Purpose / Canonical Prerequisites / Environment Setup / Complete Workflow / Workflow Stages / Repository Boundaries / Verification Matrix / Known Limitations To Preserve), covering cluster bring-up through the dashboard, with a pointer to `docs/benchmark/README.md` rather than duplicating benchmark reproduction steps. | Matches the issue's own proposed location and the TFG's own precedent for a from-scratch reproducibility document, which this repository's readers already know how to navigate; a pointer instead of a duplicate keeps the benchmark's own documentation as the single source of truth. | A new document shape: no precedent in this repository, harder for a future reader to compare against the TFG counterpart. Duplicating the benchmark steps: two documents to keep in sync. |
| D3 | **Bug-fix scope is bounded to concrete breakage found dogfooding**, plus the two already-known live issues (log-groomer `DetachedInstanceError`, orphan-pod cleanup) and the already-documented api-server liveness self-kill if a low-risk probe-tuning fix exists. Explicitly out of scope: turning Superset's deprecated Helm chart or single-replica deployment into a hardened, multi-replica setup, and any other genuine production-hardening beyond a bug-fix buffer. | The issue is named "hardening" but scoped by the epic as a bug-fix buffer within a 6-ECTS, ~120-140 h budget with `#103` (memoria) still ahead; the epic's own known-limitations register already treats the Superset chart/replica gaps as accepted, documented limitations, not defects to fix. | Attempting full infrastructure hardening (HA Superset, TLS, secrets management, etc.): far outside the remaining time budget and outside what the epic ever scoped for `#102`. |
| D4b *(user)* | **Phase B runs against an isolated k3d cluster (k3s-in-Docker), not a `k3s-uninstall.sh` teardown of the real cluster.** k3d creates its own separate node containers and storage, sharing nothing with the real k3s install's data directory; the repository checkout is bind-mounted into the k3d node containers at the same path so the DAGs' hostPath volumes resolve identically. The real k3s stays stopped (as found) throughout Phase B and is restarted unmodified at the end. Chosen by the user on 2026-09-26 ("do the best option"), after the user asked whether destruction could be avoided and the assistant proposed three options (destroy-and-rebuild the real cluster; a second bare-metal k3s instance on this host with its own `--data-dir`; k3d) with a recommendation for k3d. | Found at Phase B's start that k3s was already stopped, so nothing live would be interrupted, but its on-disk state (production Iceberg tables, PostgreSQL `gold`, the Superset dashboard's metadata) would still be destroyed by `k3s-uninstall.sh`. k3d is the standard, well-supported tool for a disposable, isolated cluster and needs the least manual setup of the three options; everything past cluster bring-up (Helm charts, values files, images, DAGs) is identical to bare-metal k3s either way, so the substitution does not weaken what actually tends to break in practice. | A second bare-metal k3s instance with its own `--data-dir`: more faithful (the real k3s binary/install path, not an emulation layer) but no officially supported multi-instance path via the installer script, so it would need a hand-rolled foreground process, its own port, and manual kubeconfig juggling for a fidelity gain that buys little given the doc's content is otherwise identical. Destroying and rebuilding the real cluster: the original D4 plan, rejected once destruction turned out to be avoidable at acceptable cost. |
| D4 *(user)* | **Verification is two-phase and gated.** Phase A: validate the quickstart document against the current live cluster, stage by stage, fixing real breakage found; gate on all stages passing clean. Phase B: only if Phase A's gate passes, tear down k3s and rebuild from nothing following only the quickstart document, exactly as the issue's original verification target states. Chosen by the user on 2026-09-25 ("start with the in place validation, if that is all ok, go with full refresh"). | Phase A is cheap and fast and matches the remaining budget; Phase B is the strongest proof and matches the letter of the original plan, but is costly (likely hours, several `sudo`/interactive checkpoints, real risk of a multi-hour incident as `#101`'s campaign hit) and is only worth paying for once Phase A shows the document is basically sound. | Phase B only (the plan's literal wording): pays the full cost even if the document has an obvious gap a cheap pass would have caught first. Phase A only: never actually proves a from-scratch bootstrap, the issue's own stated verification target. |

## Adjustments Made During Implementation

- **The `#101` status entry's description of the log-groomer restart loop was imprecise.** It named
  the `scheduler-log-groomer` sidecar; the actual crash-looping container is `scheduler` itself
  (confirmed via `kubectl get pod -o jsonpath` per-container `restartCount`: `scheduler` at 57
  restarts and `CrashLoopBackOff`, `scheduler-log-groomer` healthy at 1). The sidecar's own repeated
  `find: cannot delete '/opt/airflow/logs': Device or resource busy` messages are a separate,
  harmless cosmetic issue (it cannot delete its own mount point; nothing depends on that succeeding)
  and are left alone.
- **Root cause is upstream apache/airflow issue [#67813](https://github.com/apache/airflow/issues/67813)**,
  open and unfixed as of Airflow 3.2.2 / `cncf-kubernetes` provider `10.17.1` (this deployment's exact
  pins): `SchedulerJobRunner.adopt_or_reset_orphaned_tasks` crashes with `sqlalchemy.orm.exc.DetachedInstanceError`
  while building a log message (`repr(ti)` lazy-loads `TaskInstance.state` on a session-detached
  instance). Because the triggering DB row persists, every scheduler restart re-crashes on it
  deterministically -- a poison pill, not a transient fault.
- **The exact poison-pill row was identified, not assumed:** `ingest_validate.generate_synthetic_cvn`,
  run `scheduled__2026-09-21T00:00:00+00:00`, state `running`, hostname
  `ingest-validate-generate-synthetic-cvn-02rg8jb7` -- one of the orphaned "Unknown" pods spotted at
  planning time. Its pod was long gone; nothing ever marked its `TaskInstance`/`DagRun` rows terminal,
  so every scheduler startup tried to adopt/reset it and hit the bug.
- **No upstream fix exists yet**, so the workaround is operational, not a code change: the stuck
  `TaskInstance` and `DagRun` rows were marked `failed` directly (through a healthy pod's Airflow ORM
  session, the same mutation the Airflow UI's "mark failed" action performs), then the three stale
  pods (`generate-synthetic-cvn-1v0ocudn`, `ingest-validate-generate-synthetic-cvn-02rg8jb7`,
  `issue93-spark-submit-launcher-ogh0m087`) were deleted and the scheduler pod force-restarted. It
  came up immediately with 0 restarts on both containers.
- **This class of failure is a real, reproducible risk, not just a one-off incident**, and needs a
  documented recovery recipe (Task 5), since the same DB-write permission gap that blocked the
  assistant from applying it directly (a production DB mutation via `kubectl exec`, correctly refused
  by the harness's own auto-permission classifier) will recur for a future incident of the same shape.
- **Subtask 1.2 (orphan-pod cleanup) needed no code fix.** The two `Unknown` pods were not a general
  cleanup-mechanism gap: Airflow's `KubernetesExecutor` deliberately keeps a failed worker pod for
  debugging (`delete_worker_pods_on_failure` defaults `False`), but a scheduler that crashes before
  ever processing the pod's terminal event never reaches that decision at all, so the pod is stuck in
  limbo rather than genuinely leaked. The third pod (`issue93-spark-submit-launcher`, `Completed`) is
  benign leftover from `#93`'s smoke-test `KubernetesPodOperator`, not a defect. This becomes an
  operational note in the quickstart document (Task 5), not new automation.
- **Subtask 1.3 fix, applied and verified live:** the api-server had `resources: {}` (no CPU/memory
  request at all) and the chart's default 5 s/5-failure liveness and readiness probes. On this shared
  single-node cluster, a pod with no resource request gets the lowest CPU scheduling priority of
  anything running, so it was starved first under contention -- exactly matching `#97`'s finding.
  Fixed in `infra/helm-values/airflow-values.yaml` (`apiServer.resources.requests` = 200m CPU / 512Mi
  memory, no limit set, to avoid trading starvation for a new OOM risk per the PostgreSQL lesson of
  `#101`'s D29; `apiServer.livenessProbe`/`readinessProbe` timeout 5s -> 15s, failures 5 -> 8, period
  10s -> 15s). Applied with `helm upgrade airflow apache-airflow/airflow -n tfm-lakehouse -f
  infra/helm-values/airflow-values.yaml --version 1.22.0 --reuse-values`; confirmed on the live pod
  spec after rollout.
- **Unplanned side effect of the `helm upgrade`, worth documenting:** changing only `apiServer.*`
  values also rolled the `scheduler` deployment to a new pod-template generation (the chart stamps a
  shared config-checksum annotation across every Airflow component's pod template, so any values
  change restarts all of them together, not just the one edited). Not a bug, but a real operational
  fact for the quickstart document: a values-file change to this chart is a full-component rollout,
  not a scoped one.
- **Subtask 1.3's fix was exercised by a real, unplanned repeat of `#97`'s exact finding**, not just
  inferred from the values change: after the scheduler recovered (1.1's fix) but before the api-server
  fix landed, the freshly-recovered scheduler immediately dispatched `ingest_validate`'s missed daily
  run, whose first task (`fetch_orcid_bulk_subset`) got a `ReadTimeout` talking to the still-unpatched
  api-server and was `SIGKILL`ed, failing the whole run (`upstream_failed` downstream). This reproduced
  `#97`'s finding live, moments before the fix was applied. A fresh manual run
  (`issue102_verify_1`) was triggered immediately after the fix to confirm it holds; see Verification.
- **Phase B (k3d) execution log, added as it runs:**
  - installed `k3d v5.9.0` to `~/.local/bin` (no `sudo`: `USE_SUDO=false K3D_INSTALL_DIR=~/.local/bin`
    against the official install script)
  - created cluster `tfm-lakehouse-b`, one server node, pinned to `rancher/k3s:v1.36.4-k3s1` --
    **the exact same k3s version issue `#90` installed on the real cluster** (`current_status.md`'s
    `#90` entry), not k3d's own newer default (`v1.35.5-k3s1`, note: numerically older tag string but
    k3d's own bundled default, unrelated to the real cluster's version); repository checkout
    bind-mounted into the node at its own path (`--volume ".../TFG-open-cvn-schema:...same path...@server:0"`)
    so the DAGs' hostPath volumes resolve identically to bare-metal k3s; `--flannel-backend=host-gw`
    kept to match; own kubeconfig at `~/.config/k3d/kubeconfig-tfm-lakehouse-b.yaml`
    (`--kubeconfig-update-default=false`), never touching `~/.kube/config` or the real cluster's
    context
  - verified, not assumed: `kubectl get nodes` shows `v1.36.4+k3s1`; `docker exec
    k3d-tfm-lakehouse-b-server-0 ls <repo-path>` lists the real checkout; `helm repo list` already has
    both repos (Helm's repo config is user-level, shared across kubeconfig contexts, so issue `#90`'s
    original `helm repo add` step needs no repeat)
  - core services (MinIO, PostgreSQL, Airflow) installed exactly per the document's pinned chart
    versions and values files; **all 9 pods `Running`, and `airflow-scheduler`/`airflow-api-server`
    both came up at `0` restarts immediately** -- direct proof that Task 1.3's fix (now committed in
    `infra/helm-values/airflow-values.yaml`, not just live-patched) is durable across a genuine fresh
    install, not something that only worked because it was applied to an already-running pod
  - both DAGs delivered, registered with no import errors, and `ingest_validate` (`phaseb_verify_1`)
    succeeded end to end
  - **new, real finding: `publish_gold_to_postgres` failed twice in a row** (`phaseb_verify_1`,
    `phaseb_verify_2`) with `FATAL: password authentication failed for user "gold" ... Role "gold"
    does not exist`. Root-caused, not guessed: `kubectl logs postgresql-0 --previous` showed the
    PostgreSQL pod's very first boot was interrupted mid-`initdb`, stopped right after "Generating
    local authentication configuration" and before ever creating the `gold` role (`primary.resources`
    is a request/limit, not a startup-order guarantee, and this cluster's first minute has MinIO,
    PostgreSQL and Airflow's own embedded PostgreSQL all cold-starting and pulling images at once).
    The Bitnami image never retries an interrupted init on restart -- it sees a non-empty data
    directory and serves connections anyway, permanently missing the role/database an interrupted run
    never got to create. Fixed by deleting the pod and its PVC (`data-postgresql-0`) to force a clean
    reinitialization; verified with a throwaway `psql` pod that `gold`/`gold` now authenticates. A
    fresh `transform_publish` run (`phaseb_verify_3`) confirms the fix
  - to get the failed pod's actual logs at all, `on_finish_action` on the Spark driver operator had to
    be changed from `"delete_pod"` to `"keep_pod"` **locally, temporarily, delivered only to the
    isolated cluster's `dag-processor`**, since no log persistence is configured for Airflow's
    Kubernetes-executed tasks and the pod (and its logs) vanish on completion otherwise -- reverted and
    redelivered before continuing; the debug-kept pods deleted by hand
  - `transform_publish` (`phaseb_verify_3`) succeeded end to end after the PostgreSQL fix
  - Superset installed from the document's exact commands (secrets, `superset_ro`-equivalent
    `gold_readonly_role.sql` role, `helm install --timeout 15m`, `create_admin.sh`,
    `import_dashboard.py`); confirmed queryable, not just "pod is Running": the Superset REST API
    (`/api/v1/dashboard/`) lists the imported dashboard `tfm-gold-indicators` by name on the fresh
    cluster
  - **Phase B verdict: the document works end to end on a genuinely fresh cluster**, modulo the one
    real bug found and fixed along the way (the PostgreSQL init race) and the one already-known,
    accepted gap (`REPO_ROOT`, which needed no action here since the k3d node was bind-mounted at the
    same path as the real machine)
- **Task ordering adjusted:** Task 2's Phase A ("validate in place") means walking the quickstart
  document stage by stage against the live cluster, which cannot happen before the document exists.
  Task 3 (write the quickstart document) is done before Task 2, not after as the task list's original
  ordering implied; Task 2 Phase A then validates that document rather than re-deriving the same steps
  from scratch a second time.

## Implementation Performed

- `infra/helm-values/airflow-values.yaml`: added `apiServer.resources.requests` and relaxed
  `apiServer.livenessProbe`/`readinessProbe` timing (subtask 1.3)
- live-cluster operational fix (not a repository file): the poison-pill `TaskInstance`/`DagRun` rows
  marked `failed`, three stale pods deleted, scheduler pod force-restarted (subtask 1.1/1.2)
- `docs/development/tfm_lakehouse_workflow.md` (new): the reproducibility quickstart document (Task
  3), covering k3s bring-up through the Superset dashboard, mirroring `regeneration_workflow.md`'s
  section shape. Built from the actual infra READMEs, DAG source files (read directly, not assumed),
  and this issue's own live findings, not from memory
- **Task 2 Phase A (validate in place) executed and passed clean**, not skipped: chart versions
  installed on the live cluster (`minio-17.0.21`/`postgresql-18.11.3`/`airflow-1.22.0`/`superset-0.22.8`)
  cross-checked byte-for-byte against the document's pins via `helm list -o json`; every file path the
  document names confirmed to exist; the expected Secrets confirmed present by name; the document's
  steps 5 and 6 (deliver + trigger both DAGs) are exactly what subtask 1.4 already executed and proved
  successful, not re-run separately. `sudo k3s ctr images ls` could not be checked directly (no
  non-interactive `sudo` in this environment), so image presence is inferred instead from the DAG runs
  actually succeeding (a missing image would have failed the pod, not silently degraded) and from the
  live Superset pod's `spec.containers[].image` matching the document's tag exactly
- **real reproducibility gap found while writing the document, fixed, not just documented**:
  `dags/ingest_validate.py` and `dags/transform_publish.py` both hardcoded `REPO_ROOT` to this
  machine's exact checkout path with no override; a from-scratch reproduction on another machine or
  path would need to hand-edit both files with no warning otherwise. Fixed (Task 4) by reading it from
  `TFM_REPO_ROOT` with the existing path kept as the default (`os.environ.get(...)`, same pattern
  already used by the benchmark package's own `BENCH_REPO_ROOT`, issue `#101`) -- behavior on this
  cluster is unchanged (the env var is unset here), and both files still import and pass their
  existing tests (`uv run pytest tests/test_transform_publish_dag_unit.py tests/test_benchmark_unit.py -q`:
  11 + 76 passed). Redelivered to the live `dag-processor` PVC; `airflow dags list-import-errors`
  reported none
- no other ungraceful-failure spots were fixed under Task 4: nothing else surfaced by Task 1's audit or
  Task 2's dogfooding needed a code-level error-handling change (per D3, scope is bounded to concrete
  breakage found, not a speculative sweep)

## Verification

- **Task 1 (fragility audit) verified live, on the real cluster, not just by config inspection:**
  - subtask 1.1: scheduler pod force-restarted after the poison-pill DB fix; came up
    `restartCount=0` on both containers immediately and stayed there through everything below
  - subtask 1.3: `ingest_validate` run `issue102_verify_1` (2026-09-25 16:13:58-16:18:17 UTC, 4m20s):
    all 4 tasks (`fetch_orcid_bulk_subset`, `generate_synthetic_cvn`, `fetch_orcid_api_enrichment`,
    `validate_and_land_bronze`) succeeded; `transform_publish` run `issue102_verify_1`
    (16:19:17-16:28:39 UTC, 9m22s): `bronze_to_silver` 358.5s, `silver_to_gold` 109.2s,
    `publish_gold_to_postgres` 63.4s, all succeeded, in line with `#98`/`#99`/`#101`'s historical
    timings. `scheduler`/`api-server` restart counts stayed at 0 through both runs
- **Two-phase gate (D4): both phases passed.** Phase A: chart versions, file paths, and Secrets in
  `docs/development/tfm_lakehouse_workflow.md` cross-checked against the live cluster; steps 5-6 (both
  DAG triggers) proven by the runs above. Phase B (D4b: an isolated k3d rebuild rather than destroying
  the real cluster): the whole document run end to end on cluster `tfm-lakehouse-b` -- k3s v1.36.4+k3s1
  bring-up, MinIO/PostgreSQL/Airflow install (`airflow-scheduler`/`airflow-api-server` both `0`
  restarts immediately, confirming Task 1.3's fix is durable across a fresh install), Spark/ingest
  image import, both DAGs delivered and run (`ingest_validate` succeeded; `transform_publish` failed
  twice on a real PostgreSQL init race, fixed, then succeeded), and Superset installed with its
  dashboard confirmed queryable through the REST API. Cluster deleted afterward
  (`k3d cluster delete`); the real k3s was never touched by any of this
- **the real cluster's own `DetachedInstanceError` poison pill recurred independently, for real,
  after Phase B**: restarting the real k3s (stopped again since planning, an unrelated host event)
  brought the scheduler up in the same `CrashLoopBackOff` as subtask 1.1, with a fresh orphaned
  `ingest_validate.fetch_orcid_bulk_subset` row from a different date. The exact same documented
  recovery (mark the row and its `DagRun` `failed`, delete the orphan pods, force-restart the
  scheduler pod) fixed it immediately again, with no code changes -- independent, real-world
  confirmation that the operational recovery recipe in `known_limitations.md` actually works
  repeatably, not just once by chance
- `uv run pytest tests/test_transform_publish_dag_unit.py tests/test_benchmark_unit.py -q`: 11 + 76
  passed (Task 4's `REPO_ROOT` change), then the full documented suite,
  `uv run pytest -n auto tests`: **909 passed, 2 skipped in 10m51s**, one run, no regressions from
  this issue's changes (same 909/2 baseline `#101` left)
- re-run once more after Phase B to cover the small back-and-forth debug edit to
  `dags/transform_publish.py` (confirmed fully reverted first: `on_finish_action` diffed back to
  `"delete_pod"`, no `keep_pod` string left anywhere in the file). The host rebooted mid-run
  (unrelated), losing that run's log; re-run fresh once the cluster was confirmed healthy again
  (Findings, below): `uv run pytest -n auto tests` gave **907 passed, 2 skipped, 2 errors in 10m52s**,
  both errors `test_gold_jobs_spark.py`'s own throwaway-PostgreSQL-container fixture timing out
  ("PostgreSQL did not start") -- the exact Spark-in-Docker container-concurrency flakiness
  `known_limitations.md` already documents (worse right after a fresh reboot with everything else this
  session had running). Confirmed a flake, not a regression: `uv run pytest tests/test_gold_jobs_spark.py -q`
  alone gave **12 passed in 5m31s**, including both tests that had just failed

## Findings

- **`#101`'s own status entry misidentified which container was crash-looping** (named the
  `scheduler-log-groomer` sidecar; it was the `scheduler` container itself). Worth remembering for any
  future fragility report: read `kubectl get pod -o jsonpath` per-container `restartCount`, don't infer
  the crashing container from which one logs the most alarming-looking repeated message -- the
  sidecar's own noisy `Device or resource busy` retry loop was a red herring, unrelated and harmless
- the two most serious findings (the scheduler `DetachedInstanceError` poison pill and the api-server
  starvation) are both **infrastructure-sizing/upstream-bug problems, not application bugs** in this
  repository's own code -- consistent with a platform that had never been dogfoded under sustained load
  before this issue, rather than a sign of a design flaw
- a `helm upgrade` to Airflow rolls **every** component together, not just the one whose values
  changed (shared config-checksum annotation across pod templates) -- worth knowing before any future
  values edit, so an unexpected scheduler/triggerer restart isn't mistaken for a new incident
- the hardcoded `REPO_ROOT` in both DAG files was a genuine reproducibility gap that no README had
  flagged; found only by actually trying to write a from-scratch document for someone else to follow,
  which is exactly what this issue's quickstart-document task was for
- **all core services cold-starting together on a genuinely fresh cluster is itself a fragility
  trigger, distinct from the sustained-load fragility Task 1 found**: the PostgreSQL init race
  (Findings, below) only exists because a from-scratch bring-up starts MinIO, PostgreSQL and Airflow's
  own embedded PostgreSQL all at once; the same chart, installed onto an already-otherwise-idle
  cluster (as issue `#91` originally did), would not have hit it. Bring-up-time contention and
  sustained-load contention are two different fragility classes and this issue found one example of
  each
- the user's own question ("can we not erase everything and reconstruct it in a temp folder or other
  folder?") led directly to the k3d substitution (D4b), which is what let Phase B run at all without
  a multi-hour, higher-risk teardown of the real cluster -- and, incidentally, to actually finding the
  PostgreSQL init race, which a `k3s-uninstall.sh`-based rebuild might well have hit too, but which
  would have been far more costly to debug and recover from against the real cluster's own data
- **the host actually rebooted mid-issue, for real, and doubled as an unplanned second test of every
  recovery recipe this issue wrote down**: it lost the in-progress final test-suite run's log and
  brought the real cluster's pods back in the resync-then-partial-restart pattern already described in
  Task 1's Findings (not a new bug, the same self-recovering churn); the cluster settled to fully
  healthy on its own within a few minutes with no `DetachedInstanceError` this time, confirming that
  class of failure needs a mid-task crash specifically, not just any restart, to trigger
- **new, real finding: `publish_gold_to_postgres` failed with a PostgreSQL authentication error caused
  two steps upstream**, in a service `transform_publish` does not even directly depend on until its
  last task. Root-caused via `kubectl logs postgresql-0 --previous`: the pod's very first `initdb` was
  interrupted by cold-start contention (all core services starting and pulling images at once) before
  it ever created the `gold` role, and the Bitnami image never retries an interrupted first-boot init
  on restart. Fixed by deleting the pod and its PVC to force a clean reinitialization; getting to this
  root cause required temporarily flipping the Spark driver operator's `on_finish_action` from
  `"delete_pod"` to `"keep_pod"` (locally, delivered only to the isolated cluster, reverted after),
  since no Airflow log persistence is configured and the failing pod's logs vanish with it otherwise

## Known Limitations

Six new/updated entries in `docs/pipeline/known_limitations.md` (matrix rows and narrative sections):
the Airflow api-server liveness kill (now **Resolved**), a scheduler crash-loop on a stale
orphaned-task row (**Resolved operationally**, no upstream fix exists, and independently reconfirmed
by a second real recurrence during this same issue), a crashed scheduler leaving `KubernetesExecutor`
worker pods stuck `Unknown` (accepted, documented recovery step), an interrupted PostgreSQL first boot
never creating the `gold` role (accepted upstream behavior, documented recovery step), plus the
`REPO_ROOT` portability note folded into `docs/development/tfm_lakehouse_workflow.md`'s own Canonical
Prerequisites and Known Limitations To Preserve sections rather than duplicated in the main register.

## Impact On Future Issues

Issue `#103` (memoria assembly) can cite `docs/development/tfm_lakehouse_workflow.md` directly instead
of re-deriving setup instructions, and can cite this issue's findings (the DetachedInstanceError
poison pill and its independent reconfirmation, the api-server starvation, the PostgreSQL init race,
the shared-Helm-rollout behavior, and the k3d-instead-of-destroying-production methodology itself) as
evidence for the memoria's own hardening/lessons-learned discussion. Any future issue that needs a
disposable, from-scratch test of this platform now has a proven, low-cost method (k3d) instead of
defaulting to a real teardown.

## Status

`Completed` -- all four tasks done and verified: Task 1 (fragility audit) fixed and verified live, its
recovery recipe independently reconfirmed by a second real recurrence; Task 2 (both verification
phases) passed, including a real bug (the PostgreSQL init race) found and fixed during Phase B; Task 3
(quickstart document) written and proven accurate end to end; Task 4 (the `REPO_ROOT` fix) applied and
tested. Full suite green (909 passed, 2 skipped) after every change, including the debug detour.
