# Issue 101 - Spark Performance Benchmark

## Summary

Measure the effect of Spark executor count on processing runtime at 2-3
synthetic data scales. Second issue of TFM epic phase 4, and the platform's
one bounded performance evaluation, feeding `CP04`.

## Original Goal

Produce a concrete, reproducible performance datapoint for the memoria's
evaluation chapter, without turning into an open-ended scalability study.

## Original Plan

- pick 2-3 synthetic data scales by replicating/augmenting the synthetic
  CVN + ORCID subset volume from issues `#95`/`#96`
- run the bronze-to-silver Spark job (issue `#98`) at each scale, varying
  the executor count
- capture timings from Spark job logs / the Spark History Server, not a
  dedicated observability stack (Prometheus/Grafana explicitly deferred per
  the epic)
- tabulate and chart the results for the memoria

### Detailed Plan (accepted 2026-09-21)

Planned in a dedicated session before any code, following issues `#91`-`#100`: every decision
the epic and the original plan left open is locked in Task 0 with its reason and the rejected
alternative. The three decisions marked *(user)* (D1, D2, D3) were put to the user, who chose
each of them. Work then proceeds task by task; every step states which task (and subtask) is
active, opens with a summary of what it covers, and closes by stating which files, if any, the
user has to modify and the next step. Nothing is done for which the information is missing: an
unknown is resolved by a spike (Task 1) or reported to the user, not assumed.

#### Facts established while planning (verified, not assumed)

- **Branch:** `issue-101-spark-performance-benchmark`, created from `origin/development`
  (`git fetch origin` worked; `origin/development` is `ec8f2ce`, which contains `#100`). The
  working tree carried a pre-existing, unrelated modification of `initial_prompt.md` onto the
  branch; it is not part of this issue.
- **What is measured already parametrizes:** `bronze_to_silver.py` takes `--bronze-root`,
  `--namespace` and `--shuffle-partitions`; `silver_to_gold.py` takes `--silver-namespace`,
  `--gold-namespace` and `--shuffle-partitions`; `publish_gold_to_postgres.py` takes
  `--gold-namespace` and `--pg-schema`. A benchmark can therefore read and write elsewhere
  than production without editing any job of `#98`/`#99`. The DAG `transform_publish` does
  **not** expose those namespaces as parameters (only executors, memory, shuffle partitions
  and thresholds).
- **Existing timings** (input from `#98`/`#99`, one warm run at two executors of 1 GiB heap
  plus 1 GiB overhead, one core each, over 30,868 person records): 219.8 s, 71.3 s and 69.3 s
  for `bronze_to_silver`, `silver_to_gold` and the publish. The first run of a session was 1.3
  to 2.5 times slower than the next ones (573 s against 197-227 s in `#98`).
- **Sizing constraints:** the machine has 16 CPUs; `.wslconfig` gives WSL2 16 GiB
  (`memory=17129537536`), of which about 10 GB were free for the cluster when `#98` and `#100`
  were planned. Each executor is 1 GiB heap plus 1 GiB overhead (the overhead holds the Python
  workers that parse the XML; a single ORCID line can be 17.4 MB) and the driver is a 2 GiB pod,
  so four executors already need about 10 GiB. Whether four fit is a Task 1 spike.
- **Spark on Kubernetes defaults that would distort a scaling curve** (Spark 3.5 documentation):
  `spark.scheduler.minRegisteredResourcesRatio` is `0.8` on Kubernetes with a 30 s maximum wait
  (`spark.scheduler.maxRegisteredResourcesWaitingTime`), so with four executors the job can
  start on three; executor pods are requested in batches of `spark.kubernetes.allocation.batch.size=5`
  every `spark.kubernetes.allocation.batch.delay=1s`; adaptive query execution is on by default
  since 3.2 (`spark.sql.adaptive.enabled`, `spark.sql.adaptive.coalescePartitions.enabled=true`)
  and can merge the partitions that `--shuffle-partitions` sets; dynamic allocation is off by
  default.
- **Metrics without an observability stack:** the event log (`spark.eventLog.enabled`,
  `spark.eventLog.dir`) records per-task `executorRunTime`, `jvmGCTime`, shuffle read/write,
  spill and `peakExecutionMemory`, and it is what the History Server reads. The Spark image
  already contains `sbin/start-history-server.sh` (checked with `docker run`), so the History
  Server needs no new image. S3A/MinIO as `spark.eventLog.dir` is a documented, common setup but
  is proven here only in Task 1.
- **Bronze landing:** `land_records` and `find_landed_runs` take a `bucket` argument, while the
  prefix `bronze/` is a module constant (`BRONZE_PREFIX`); whether `land_bronze` and the CLI
  expose a bucket, and whether the bulk records are taken in a deterministic order so that 2x
  contains 1x, is a Task 1 spike. The ORCID subset holds 301,763 records (`data/orcid_bulk/filtered/`,
  37 GB on disk), so 80,000 bulk records for 4x exist. The ORCID API has an anonymous cap of
  25,000 reads a day (`#94`).
- **Current bronze:** bulk cap 20,000 landed 19,469 records (531 rejected, 2.66%), plus 11,000
  synthetic CVNs and 399 API records, plus the partitions of the daily `ingest_validate` runs. It
  is therefore not a clean 1x; the benchmark builds its own.
- **k3s state:** stopped at the end of `#100` (`systemctl is-active k3s` reports `inactive`);
  it must be started with `sudo systemctl start k3s` before any cluster work.

#### Task 0 - Decisions Locked

| # | Decision | Reason | Rejected alternative |
| --- | --- | --- | --- |
| D1 *(user)* | **Who writes the files:** the assistant writes code, infrastructure files and documentation (the `#98`/`#99`/`#100` mode); the user acts only where the assistant cannot (`sudo`, starting the k3s service) or where a decision is open. Chosen on 2026-09-21. | The repository default is that the user edits code and values files, so the choice was put again rather than assumed. | Assuming the earlier choice carries over silently. |
| D2 *(user)* | **Measure all three jobs:** `bronze_to_silver`, `silver_to_gold` and `publish_gold_to_postgres`. Chosen on 2026-09-21. The recommendation was silver plus gold: the publish is a JDBC write into one PostgreSQL instance, so its curve is expected to be flat. It is measured anyway. | The user chose completeness. It costs about 70 s a run, and a flat curve is itself a finding for the evaluation chapter (which stage of the pipeline scales with executors and which is bound by a single sink). The original plan named only the silver job; this widens it by the user's decision. | Silver only (the plan's letter) or silver plus gold (the recommendation): fewer runs, one or two curves. |
| D3 *(user)* | **Three data scales times executors {1, 2, 4}.** Chosen on 2026-09-21. If Task 1 shows that four executors do not fit in memory, the grid becomes {1, 2, 3}. The epic's cut list applies if the time budget is at risk: one scale first. | 2-3 scales is what the original plan asks for; four executors is the practical ceiling of about 10 GiB (facts above). Three executor counts give a curve with a saturation point rather than one ratio. | Two scales (fewer runs, a two-point volume curve); one scale with 1-4 executors (the epic's minimum, kept as the fallback). |
| D4 | **Scale definition:** 1x = 20,000 ORCID bulk records requested + 11,000 synthetic CVNs; 2x = 40,000 + 22,000; 4x = 80,000 + 44,000. The ORCID API sample stays fixed (200 records, under 1% of the bytes; see Task 1.5). The number of records that survive the landing check per scale is measured and reported, not assumed equal to the request. | The bulk XML dominates both bytes (mean 138 KB per record against 8.3 KB per CVN) and the Python parsing cost, so scaling both real and synthetic sources keeps their proportion, and real records are used instead of replicas. Scales are nested if the bulk order is deterministic (Task 1.5). A fixed API sample keeps the benchmark independent of the live ORCID API and its daily cap. | Replicating landed records under new `record_id`s: duplicates ORCID iDs, so rule R1 would fuse the copies and the entity-resolution work would no longer be comparable. Scaling the API sample: makes the benchmark depend on the network and on a 25k-a-day cap for under 1% of the data. |
| D5 | **Isolation from production:** the benchmark bronze lives outside `s3a://lakehouse/bronze` (an alternative bucket or prefix, settled in Task 1.5); silver and gold write to `lakehouse.bench_silver_<scale>x` and `lakehouse.bench_gold_<scale>x`; the publish writes to PostgreSQL schema `bench_<scale>x`. The production `lakehouse.silver`, `lakehouse.gold`, PostgreSQL schema `gold` and the Superset dashboard of `#100` are never written. | `bronze_to_silver` rebuilds silver in full and the publish replaces the published tables, so benchmark runs against the real namespaces would destroy the state `#100` verified and the dashboard reads. All three jobs already take the arguments needed, so `#98`/`#99` stay untouched. | Benchmarking against the real bronze/silver/gold and rebuilding afterwards: the dashboard would show benchmark artifacts and the real bronze is not a clean 1x. |
| D6 | **A benchmark runner without Airflow:** a module `src/tfm_lakehouse/benchmark/` creates the Spark driver pod by `kubectl` (the pod is the driver in client mode and runs `spark-submit` through `/opt/entrypoint.sh`, exactly as the DAG does), waits for it, collects the run's outputs and removes it. Its `spark-submit` flags are built by the runner; a test compares the flags shared with `dags/transform_publish.py` so the two cannot drift. One cross-check run through the real DAG (Task 6) confirms the runner measures the same thing. | The DAG does not expose the namespaces (facts above) and Airflow adds scheduling latency, memory (competing with the executors on a single node) and noise; a direct runner keeps the measurement controlled. | Editing `transform_publish` to add parameters: touches `#99`'s delivered DAG (redelivery to the PVC, retest). Driving the benchmark through the Airflow API: same problems and more moving parts. |
| D7 | **Metrics from the Spark event log:** `spark.eventLog.enabled=true` and `spark.eventLog.dir=s3a://lakehouse/spark-events/` (or the benchmark bucket) added by the runner as `--conf`, no change to any job. A pure-Python parser reads each run's log and extracts application start/end, job and stage durations and the task metrics; two times are reported: `app_seconds` (submit to end) and `compute_seconds` (first job start to last job end, without executor start-up). A History Server pod from the existing image is optional, for a screenshot only. | It is the source the original plan names (job logs / History Server) and needs neither Prometheus/Grafana (deferred by the epic) nor a change to the jobs; parsing offline is reproducible and testable. Separating start-up from compute matters because executor pods are requested in batches. | Reading the History Server UI by hand: not reproducible and not testable. Adding timing code to `#98`/`#99` jobs: would change what is measured; their own `elapsed_seconds` also includes `count()` calls and the optional evaluation. |
| D8 | **Measurement protocol:** executors fixed at 1 core, 1 GiB heap and 1 GiB memory overhead, driver 1 GiB in a 2 GiB pod (the `#98` sizing), so only the executor count varies; `spark.scheduler.minRegisteredResourcesRatio=1.0` with a long `maxRegisteredResourcesWaitingTime` so the job never starts on fewer executors than the configuration says; shuffle partitions fixed and reported (AQE left at its default and its effect recorded); the first run of a session is a discarded warm-up; then 3 measured runs per point, in interleaved order with a fixed seed (not three of the same configuration in a row); the median and the range are reported; a point whose `(max - min) / median` exceeds 10% is repeated or flagged. The benchmark tables of the previous run are dropped before each run so that the Iceberg state is identical. | Strong scaling means fixed problem size and varying resources; the medians and the discarded warm-up follow the methodology found in the literature and `#98`'s own finding of a 1.3-2.5 times slower first run; interleaving stops a slow drift of the machine (thermal, page cache, WSL2 memory) from being read as an effect of the executor count. | One run per point: no estimate of noise. Three back-to-back runs of a configuration: confounds drift with configuration. Dynamic allocation: the number of executors would no longer be the independent variable. |
| D9 | **A run counts only if its output is correct:** a content digest per output table (the method of `#98`: SHA-1 over the sorted rows of an Iceberg snapshot) must be equal across 1, 2 and 4 executors at the same scale, and the row counts must be recorded. The silver job runs **without** `--manifest`: the evaluation against the synthetic ground truth is not part of the ETL and would add time that is not the job's. | A faster run that produced different silver or gold data measures nothing; `#98` showed rebuilds are deterministic, so equal digests are a fair expectation and any difference is a bug to report. | Comparing only row counts: misses wrong content. Running the evaluation on every run: adds a step that does not scale with the job and makes the runs longer. |
| D10 | **Derived metrics:** speedup `S(n) = T(1)/T(n)`, efficiency `S(n)/n`, the Karp-Flatt experimentally determined serial fraction `e = (1/S - 1/n) / (1 - 1/n)`, the size-up exponent (log-log fit of time against scale at a fixed executor count), and throughput in records/s and MB/s per scale. Reported per job and per stage where the event log allows. | Cheap to compute from the medians and enough to say, with numbers, where the curve saturates and whether time grows linearly with volume; it directly serves `CP04` and `HA02`. | Reporting raw times only: leaves the reader to infer scaling. A model fit beyond three executor counts: over-claims with three points. |
| D11 | **Charts with matplotlib** as a development dependency added with `uv`, if it installs on Python 3.14 (Task 1.7); the committed results are a small CSV/JSON plus PNGs. Raw run records and event logs stay in the git-ignored `data/benchmark/`. | The memoria needs figures; a plotting library is the least effort. Committing only the compact results keeps the repository small. | Hand-written SVG (no dependency, more code, worse for a reader to change); a Superset chart over a benchmark table (couples the benchmark to the BI stack, which is the epic's first cut). |
| D12 | **Control of interference on the single node:** Superset and Airflow are scaled to zero replicas for the campaign and restored at the end (recorded in Task 11); every run records `nproc`, memory (`free`) and the pods that are running; the runs happen on an otherwise idle machine. | The executors, MinIO, PostgreSQL, Airflow and Superset share the same 16 CPUs and RAM, and `#100` already had to discard its own timings because a browser was being installed during the run. | Leaving every service running: the noise is unbounded. |
| D13 | **Time box and cut order (from the epic):** the campaign is estimated at about 7 h of machine time with three repetitions. If the pilot (Task 6) shows it does not fit the remaining budget, reduce first to fewer repetitions on the largest scale, then to a single scale (the epic's stated cut), and record it as a deviation with the reason. | The epic decides in advance that the benchmark is cut to one data scale before anything else on the never-cut list. | Deciding under time pressure. |

| D14 | **A new Spark job computes the content digest** (`spark_jobs/table_digest.py`): per table the row count and the sum of `xxhash64(to_json(struct(*)))` over the rows, cast to `decimal(38,0)` so the sum cannot overflow; an empty table gives digest `0`; `gold_run` (which legitimately holds a run id and timestamps) is compared by row count only. It runs once per executor configuration, right after that configuration's first measured run. Added during Task 3, not in the accepted plan. | D9 needs a digest and `#98` computed its own ad hoc, outside the repository. `to_json` handles the maps and arrays of the silver tables (which `hash` alone does not), and a sum of row hashes is independent of row order and partitioning, so a run with another executor count can be compared. Tested in the Spark image on order, partitioning, a changed value, an added row, maps, arrays, nulls and an empty table. | Comparing only row counts (misses wrong content); sorting and hashing every row (a full sort of the largest tables for no gain); the SHA-1 of sorted rows `#98` used (needs a shuffle and a sort). |
| D15 | **A warm-up per scale and job, not one per session** (the refinement found in Task 1.8): each `(scale, job)` starts with a run at two executors that is executed and recorded but never counted. Added during Task 1, refining D8. | The first probe run was 1.22 times slower than the next two and its cause was not isolated; a new scale reads new data, so it may recur. The cost is small (about a run per scale and job, and the gold and publish runs are short). | One warm-up per session (D8 as accepted): would leave a possible cold-data effect inside the 2x and 4x measurements. |
| D16 | **Each job keeps the executor memory overhead it has in `transform_publish`**: 1 GiB for `bronze_to_silver`, 512 MiB for `silver_to_gold` and the publish (heap 1 GiB and one core for all). D8 said 1 GiB heap plus 1 GiB overhead for every job. Added during Task 3, refining D8. | The benchmark measures the jobs as `#98` and `#99` deployed them; giving the gold jobs a bigger overhead would benchmark a configuration nobody runs. The drift-guard test pins these values to the DAG. | A uniform 1 GiB overhead: simpler to state, but not what the pipeline runs. |
| D17 | **The event log goes to its own bucket** `tfm-bench-events`, under `logs/` with a `.keep` marker, not to `lakehouse`. Added during Task 1.6, refining D7. | The bucket root is not a valid event-log directory (Spark fails with `path must be absolute`) and the production bucket should hold nothing of the benchmark. | `s3a://lakehouse/spark-events/` (D7 as accepted): mixes benchmark artifacts into the production bucket. |

| D18 | **The shuffle partitions of the silver and gold jobs scale with the data: 16 times the scale factor (16, 32, 64).** D8 said they stay fixed at 16. Added during Task 6, changing D8. | The pilot showed a fixed 16 does not survive 4x: with 4 executors the run lost executors repeatedly (`FetchFailedException`, the shuffle stage resubmitted again and again, replacement executors created) and was aborted after 22 minutes; with 64 partitions (the same amount of data per partition as at 1x) the same run finished in 1,324.9 s with no executor lost. Issue `#98` had already advised "raise `--shuffle-partitions` for volume". Holding the data per partition constant is the standard way to run a scale-up test. The mechanism (memory of a larger partition against the executor's 2 GiB limit) is the likely cause and is consistent with the two runs, but no OOM-kill was observed directly (Spark deletes the lost pod before it can be inspected). | Fixed 16 at every scale (D8 as accepted): 4x does not complete. Larger executors at 4x: changes the resource axis that the benchmark keeps fixed and does not fit 4 executors in memory. |
| D19 | **A task that Spark retried successfully does not invalidate a run; a lost executor, a failed job or a different executor count does.** Retried tasks are counted and shown in the tables (`task retries`). D8 said a run counts only if no task failed. Added during Task 6, refining D8. | The first 4x run showed 3 retried tasks (`UncheckedIOException: Failed to close current writer`, Iceberg writing to MinIO) in a run that finished correctly: retries are Spark's normal fault tolerance, and excluding every such run would discard exactly the heavy-load runs the benchmark is about. What cannot be compared is a run that changed its own resources (an executor lost and replaced) or did not complete. | Excluding any run with a failed task (D8 as accepted): would exclude runs for a recovered, ordinary event and hide a possible sign of an overloaded object store. Ignoring retries silently: hides the sign. |
| D20 | **Every run also records the system CPU use and MinIO's CPU.** The system-wide CPU shares (busy, system, I/O wait, steal) come from two readings of `/proc/stat` around the run, and MinIO's pod CPU (peak and mean, millicores) from `kubectl top` every five seconds. Added during Task 6. | The pilot's numbers rule out a plain CPU limit (the system was 19% busy at 4 executors on 4x) while the stage times point at the object store; without these two measurements the report could only speculate about why the runs stop scaling. Both are cheap and need no new component (metrics-server is already in k3s). | Prometheus/Grafana (deferred by the epic); no measurement (leaves the saturation unexplained). |
| D21 | **Pilot runs are kept apart:** run ids from `r901`, role `pilot` (or `warmup`), moved to `data/benchmark/pilot_runs/` before the campaign, and never counted by the report (a test enforces it). Added during Task 6. | The pilot ran under conditions that differ from the campaign (a concurrent landing loaded the machine, the code changed between runs), so mixing it with the measured runs would contaminate them; it stays as evidence for the decisions above. | Deleting the pilot runs: loses the evidence for D18-D20. Counting them: contaminates the medians. |

| D22 | **The runner's per-run timeout is measured with `time.monotonic()`, not `time.time()`.** The wall clock (`clock`) is kept only for the human-readable timestamps and `wall_seconds`; a new `active_seconds` (the monotonic budget actually consumed) and `suspected_suspend_seconds` (a wall-clock jump much larger than one poll cycle) are added to every run's record. Added during Task 7, not in the accepted plan; a real-incident fix, not a design choice offered as an alternative. | The host machine slept mid-campaign (Windows/WSL2 suspend) during run `1x-silver-e1-r011`: its driver log shows one task frozen for 61,933.6 s and then continuing normally, so the Spark job itself was healthy throughout and about to finish (task 44 of 48 in a read stage, well before any table write). `time.time()` jumped forward by the same ~17 h on resume, so the very next poll saw `elapsed > 3600 s` and the runner declared a timeout and deleted a healthy driver pod. `time.monotonic()` (`CLOCK_MONOTONIC` on Linux) excludes suspended time by definition and confirms this: the guest's own `uptime` also excluded the suspended hours. A regression test reproduces the incident (a wall clock that jumps 62,000 s between two polls, a monotonic clock that does not) and checks the run is no longer falsely timed out. | Raising the per-run timeout instead: does not fix the underlying issue and a long enough sleep would still trigger it. Catching the specific jump and retrying transparently within the same run: more complex, and the outer `campaign.execute`/`_done` resumability already retries a timed-out run for free once its status is not `ok`. |

| D23 | **A run that fails with a diagnosed executor-memory ceiling does not stop the campaign.** `_diagnose_failure` recognizes the log signature of Spark exhausting `spark.kubernetes.executor.maxNumFailures` after repeated JVM OOMs (`exit code 52(JVM OOM)` plus `ExecutorPodsAllocator: Max number of executor failures (N) reached`) and records it as `failure_reason: "executor_oom"`; `campaign.execute` continues past that specific outcome (logging a warning) but still raises and stops for any other failure or a timeout, exactly as before. Added during Task 7, not in the accepted plan; a real-incident fix, not a design choice offered as an alternative. | Run `2x-silver-e1-r042` (1 executor, 2x) OOM'd four times in a row over 18 minutes (executors 1-4, each `exit code 52`) until Spark gave up and stopped the whole application; 2 and 4 executors completed the same `2x` silver job without incident (468.3 s, 401.1 s, 1171.2 s). This is the benchmark doing exactly its job: a single executor of the fixed 1 GiB heap plus 1 GiB overhead (decision D8's controlled variable) must hold the whole scale's working set alone, unlike 2 or 4 executors that share it, so it hits a real, data-dependent memory ceiling rather than a bug. Stopping the whole campaign for a diagnosed, reproducible ceiling at one specific `(scale, executors)` point would have thrown away the rest of the plan for a result that is itself informative (and the isolation of D5/D9 means one point's failure cannot corrupt any other point's tables). | Raising executor memory for this point: breaks D8's fixed-memory-per-executor control, the whole reason the scaling curve is comparable. Retrying indefinitely: the ceiling is deterministic, not transient (four independent executor pods OOM'd the same way). Treating every non-`"ok"` status as campaign-stopping (the previous behavior): correct for an unrecognized failure, wrong for a diagnosed, data-dependent one. |

| D24 | **`table_digest.py` treats a missing Iceberg table as data (`{"rows": 0, "digest": "0", "exists": False}`), not an error.** `spark.table(...)` is wrapped per table; an `AnalysisException` (the table or its whole namespace does not exist) is caught and recorded instead of raised. Added during Task 7, not in the accepted plan; a real-incident fix, not a design choice offered as an alternative. | The digest scheduled right after `2x-silver-e1-r042`'s D23 OOM (`2x-digest-silver-e2-of1-r043`) crashed with `[TABLE_OR_VIEW_NOT_FOUND]`, which stopped the campaign again: `reset_namespace` (D9) removes the whole warehouse directory of a namespace before each run, not just its rows, and the OOM'd measured run died before its own `CREATE NAMESPACE`/`createOrReplace`, so the table genuinely did not exist, not merely empty. A digest of "nothing was written" is itself correct, useful information for a configuration that could not complete, not a fault in the digest job. Tested in the Spark image against both a real table and a table that was never created, through the actual CLI. | Skipping the digest run in the campaign plan when its measured run OOM'd: needs the campaign to look ahead at an outcome the plan is built before knowing, and loses the confirmation that genuinely nothing was written. Catching every exception broadly: would also hide a real bug in the digest job itself; `AnalysisException` is specific to an unresolved relation. |

| D25 | **The OOM signature is broadened to the literal Spark message alone (`exit code 52(JVM OOM)`), and the campaign skips further repeats of a configuration only once *every* attempt on record has OOM'd (zero successes across at least 2 attempts); a configuration with any success keeps its normal 3 repetitions.** Attempts are counted by `(scale, job, executors)`, not by run id, so retries of the same slot across a resumed campaign and fresh repetition slots both count. Added during Task 7 at the user's explicit choice, not in the accepted plan. | A third incident (below) showed `_diagnose_failure`'s original, narrower signature (`"Max number of executor failures"`) missed a real OOM that Spark gave up on a different way, stopping the campaign again for a cause it should have recognized; and it showed `(2x, silver, 2 executors)` is *not* a deterministic ceiling (2 successes, then one OOM), unlike `(2x, silver, 1 executor)` (2 attempts, 2 OOMs, 0 successes) -- so the cut has to be evidence-based per exact configuration, not assumed from the executor count alone, or it would throw away real variance data for a config that mostly works. The user chose to cut repeats once a ceiling is confirmed rather than run the full 3 for a config already proven to never succeed. | Keeping the original narrower OOM signature: already shown to miss a real incident. Cutting repeats by executor count (e.g. "always 1 attempt at 1 executor"): would have wrongly cut `(2x, silver, 2 executors)` too on its first OOM, discarding the fact that it mostly succeeds. Cutting after a single OOM: could stop on a fluke rather than a confirmed ceiling; 2 attempts is the least evidence that rules out chance for a binary (OOM or not) outcome. |

| D26 | **Two fixes to the same underlying gap: (a) skipping a confirmed-deterministic-OOM run id never overwrites that run id's own existing record (only a never-attempted run id gets a fresh "skipped" record); (b) before any `gold`/`digest_gold` run, if the chronologically latest silver attempt for that scale did not leave valid output, a repair run at `MAX_EXECUTORS` (the most reliable configuration observed) rebuilds it first, and the same applies to `publish` reading gold.** Added during Task 7, not in the accepted plan; two real-incident fixes, not a design choice offered as an alternative. | (a) After a host reboot, resuming the campaign correctly skipped `2x-silver-e1-r042` (2 confirmed OOMs), but `_skip_confirmed_oom` overwrote `r042`'s own `record.json` -- one of the two attempts that made the confirmation true -- with a `"skipped"` record whose `failure_reason` no longer matched `"executor_oom"`, so the *next* repeat, `r046`, no longer saw a confirmed ceiling and ran for real (and OOM'd again, at real cost, though not wrong data). (b) The campaign's randomized order can legitimately end a scale's silver phase on a failed run (decision D9 resets each job's own namespace before every attempt, including a failed one); `2x-gold-e2-r050` then read an empty `lakehouse.bench_silver_2x` and failed with `silver table ... is missing; gold was not written` -- correct behavior of `silver_to_gold.py`'s own guard, but a gap in the campaign, which had assumed *some* earlier silver run left good data without checking. | (a) Not fixing it: further executor-1 repeats at larger scales would keep costing full run time for no new information, defeating the point of D25. (b) Reordering the plan so a scale's very last silver/gold entry is always a reliable configuration: fights the randomized-block design of D8, which deliberately does not group runs by executor count. Treating a missing-upstream-table failure as another `executor_oom`-like "continue silently" case: would hide a real gap instead of fixing it, and gold/publish would then run against data from an unrelated, stale rebuild. |

| D27 | **`_attempt_outcomes` (and therefore `_confirmed_deterministic_oom`) never counts a `"skipped"` record as evidence, even though it is a record for the exact configuration.** | Skipping `4x-silver-e2-r081` (confirmed after its warm-up and first repeat both OOM'd) wrote `r081`'s own fresh `"skipped"`/`failure_reason="executor_oom_confirmed"` record; the *next* repeat, `r083`, then computed `_attempt_outcomes` over `[warm-up: executor_oom, r076: executor_oom, r081: executor_oom_confirmed]`, and `all(reason == "executor_oom" ...)` failed on the third entry, so `r083` ran for real instead of being skipped (a real ~30 min cost, a third genuine OOM confirmation, not wrong data). The same class of bug as D26(a), one level further: a skip is a *decision* about a configuration, not a new *attempt* at it, and must never feed back into the decision for the next repeat. | Making `_skip_confirmed_oom` write `failure_reason: "executor_oom"` instead of a distinct value: loses the ability to tell a real OOM apart from a skip in the run records and in the report's "excluded" listing. Skipping every repeat once `_attempt_outcomes` sees *any* non-`"ok"` entry regardless of reason: would also skip a repeat that failed for an unrelated cause, hiding it instead of surfacing it as an unrecognized failure. |

| D28 | **`_last_write_ok` judges recency by ``submitted_at`` (a real timestamp), not by the plan's ``sequence`` number.** | `4x-silver-e4-r085` (sequence 85) completed successfully; the campaign was then resumed and retried the still-`"failed"` `4x-silver-e2-r073` warm-up (sequence 73) -- lower sequence number, but it ran *later* in real time, reset the namespace again (decision D9), and OOM'd, leaving it empty. `_last_write_ok` compared by `sequence`, saw `r085` (85 > 73) as "latest", reported the namespace valid, and `4x-gold-e2-r086` then read a missing table -- D26(b)'s own repair mechanism, sound in design, failed because the recency check it depends on used the wrong ordering key. | Bumping a retried run id's sequence number to the current position when it is retried: `run_id` (and therefore every file path, and the drift-guard test comparing it to the DAG) is derived from `sequence` and must stay stable for `_done()`'s resumability to keep recognizing it. Re-numbering the whole plan on every resume: defeats the point of a fixed, reproducible plan. |

| D29 | **PostgreSQL's Helm values (`infra/helm-values/postgresql-values.yaml`) now set `primary.resources` explicitly** (256Mi/1 core requests, 1536Mi/1 core limits), overriding the chart's default `resourcesPreset: "nano"` (a hard 192Mi memory limit). Applied with `helm upgrade`, verified: the pod restarted healthy, and every schema (`gold`, `bench_1x`, `bench_2x`, `bench_4x`) and their data survived (`gold.dim_researcher` still 29,767 rows). Added during Task 7, not in the accepted plan; a real, infrastructure-level incident fix. | `4x-publish-e2-r099` failed twice with `Connection to postgresql...svc.cluster.local:5432 refused`; `kubectl describe pod` showed `Last State: Terminated, Reason: OOMKilled, Exit Code: 137` for the PostgreSQL container itself -- it OOMKilled while staging `4x`'s roughly 4-times-larger gold tables, something `1x`/`2x` never hit at the same 192Mi limit (a Bitnami chart default sized for a small workload, not this benchmark's largest scale). The failure is outside the benchmark job's own control (the JDBC client has no way to raise the server's container memory limit), and the machine has double-digit GB free, so the fix raises the ceiling with a wide margin. | Retrying at the same limit: deterministic, would OOMKill again every time (confirmed: it failed identically twice in a row). Reducing `4x`'s publish batch size or staging in smaller chunks in the job itself: treats the symptom in application code for what is an infrastructure sizing gap, and would diverge the job's behavior from what `#99` ships for `transform_publish`. |

Files touched by Task 0: this document. The `#101` row of `docs/roadmap/tfm/tfm_roadmap.md`
changes to `In Progress` when Task 1 starts, not by this planning step.

#### Task Breakdown

Status in brackets, updated as work proceeds. Estimated effort about 14-18 h including about 7
h of unattended machine time, inside the epic's phase-4 budget (days 12-14; epic target
2026-10-04).

1. **Task 1 - Preparation and spikes** [done; results in "Adjustments Made During
   Implementation"].
   - 1.1 roadmap row to `In Progress`; **the user starts k3s** (`sudo systemctl start k3s`) and
     the `tfm-lakehouse` pods are checked [done].
   - 1.2 capacity: node allocatable and free memory with Superset and Airflow scaled to zero;
     whether four executors of 2 GiB plus the 2 GiB driver fit (decides the grid of D3) [done:
     they fit, grid {1, 2, 4} stands; confirmed under load in Task 6].
   - 1.3 MinIO's PVC size and free space against the roughly 11 GB of the 4x bulk shards plus
     what is already there [done: no quota, 916 GB free].
   - 1.4 whether the PostgreSQL user `gold` can create a schema `bench_<scale>x` (D5); otherwise
     use the superuser secret, or report [done: it can].
   - 1.5 whether `land_bronze` and the CLI can land into an alternative bucket or prefix, and
     whether the bulk records are taken in a deterministic, nested order (D4, D5) [done: a
     bucket per scale, called from Python; bulk and CVN sets are nested; the API sample of
     `e2e98-big` is reused].
   - 1.6 the event log is written to MinIO from a client-mode driver pod and can be read back
     (D7) [done: dedicated bucket, `logs` subdirectory with a marker; see the note].
   - 1.7 `matplotlib` installs and imports on Python 3.14 with `uv` (D11) [done: resolves with
     wheels; nothing added to the lock yet].
   - 1.8 the noise floor: one job twice at one scale and one executor count, to size the
     tolerance of D8 with data [done: three runs, warm spread 2.3%; the first run of each new
     scale is discarded too].
2. **Task 2 - Benchmark data** [done] (D4, D5): land 1x, 2x and 4x into the isolated bronze;
   verify the record and byte counts per scale and keep the manifests.
3. **Task 3 - Runner** [code and unit tests done; proven on the cluster in Task 6] (D6, D8): `src/tfm_lakehouse/benchmark/` (configuration,
   driver-pod manifest, `kubectl` execution, wait for executors, cleanup, one JSON record per
   run) and the drift-guard test against the DAG.
4. **Task 4 - Event log parser** [done] (D7): per-run and per-stage metrics; tested on a
   sample log.
5. **Task 5 - Statistics and report** [done; run on the real records in Task 8] (D10, D11): medians, ranges, speedup,
   efficiency, Karp-Flatt, size-up exponent, throughput; Markdown/CSV tables and charts.
6. **Task 6 - Pilot** [done; results in "Adjustments Made During Implementation"] (D13, D18-D21): one run at 1x and two executors; the cross-check through
   the real `transform_publish` DAG against the `#99` figures; the go/no-go on the campaign
   size from the measured time of the largest configuration.
7. **Task 7 - Campaign** [done: started 2026-09-21 22:49, finished 2026-09-24 18:16, 108/108 plan
   items plus 2 repair runs; nine incidents along the way, D22-D29] (D8, D9, D12): per scale,
   silver at every executor count, then gold reading that scale's silver, then the publish;
   interleaved order, discarded warm-up, correctness digests, machine state recorded.
8. **Task 8 - Analysis and findings** [done] (D10): what scales and what does not, where it
   saturates, the memory ceiling, the reproducibility of the repeats; see "Findings" below.
9. **Task 9 - Tests and full suite** [done]: 76 unit tests for the parser, the statistics and
   the runner, plus 3 in the Spark image; `uv run pytest -n auto tests` (the documented command):
   909 passed, 2 skipped in 11 min 40 s, one run, on the machine straight after the campaign.
10. **Task 10 - Documentation close-out** [done]: this document, `current_status.md`,
    `tfm_roadmap.md`, `known_limitations.md`, `PROJECT_GUIDE.md`, `project_context_index.md`;
    `docs/benchmark/README.md` already had the reproduction steps from before the campaign, kept
    current; `AGENTS.md` needed no change (its map already listed the benchmark). The results
    text for `#103` is `docs/benchmark/results.md` itself plus the "Findings" section below.
11. **Task 11 - Close-out of the cluster** [done]: dropped the `bench_*` MinIO buckets, Iceberg
    namespaces and PostgreSQL schemas; restored Superset and Airflow to their pre-campaign
    replica counts (verified healthy, one Airflow log-groomer sidecar container restart-looping
    on a `DetachedInstanceError` after the restart -- the pre-existing Airflow operational
    fragility issue `#102` already covers, not something this issue introduced or is responsible
    for); k3s left running (the user may still want to look at the dashboard or the results).
    Nothing committed; that is the user's call.

#### Risks

- **Memory ceiling** (facts above): four executors may not fit; Task 1.2 decides and the grid
  becomes {1, 2, 3} if so.
- **MinIO disk:** the 4x bulk shards add about 11 GB (Task 1.3).
- **WSL2 noise:** mitigated by D8 (interleaving, discarded warm-up, the 10% criterion) and D12.
- **Single node:** speedup measures CPU parallelism on one machine that also hosts MinIO and
  PostgreSQL; there is no network shuffle. It is a limitation to state in the memoria, not
  something to fix here.
- **Time:** about 7 h of machine time; D13 fixes the cut order.
- **Event log format:** the parser depends on Spark's event-log JSON; Spark documents its REST
  API as backward compatible but not the raw log, so the parser is tested on a real log from the
  pinned Spark 3.5.9.

## Adjustments Made During Implementation

- Plan accepted on 2026-09-21 with the decisions above (Task 0). D1 (the assistant writes
  code, infrastructure and documentation), D2 (all three jobs, not the recommended silver plus
  gold) and D3 (three scales times executors {1, 2, 4}) were put to the user, who chose them.
  Working protocol for every step: state the active task and subtask, open with what it
  covers, close with whether the user must modify any file and the next step.

- **Task 1 spikes (2026-09-21).**
  - *1.1, cluster.* The user started k3s (`sudo systemctl start k3s`); the node was `Ready` at once
    and MinIO and PostgreSQL were `Ready` about two minutes later (the pods restart on their own
    after the cluster was stopped). Airflow's and Superset's web pods stayed `Unknown`, and two
    orphan pods of an interrupted scheduled ingestion (`generate-synthetic-cvn-…`,
    `ingest-validate-generate-synthetic-cvn-…`) remain in `Unknown`; the benchmark does not use
    Airflow (D6), so they were left alone.
  - *1.2, capacity (D3, D12).* Node allocatable 16 CPU and 16,326,840 KiB (15.57 GiB) of memory,
    the whole of WSL2's 15,944 MiB. To free memory for the campaign Superset and Airflow were scaled
    to zero (D12): the Deployments `superset`, `airflow-api-server`, `airflow-dag-processor`,
    `airflow-scheduler`, `airflow-statsd` and the StatefulSets `superset-postgresql`,
    `superset-redis-master`, `airflow-postgresql`, `airflow-triggerer`, each with 1 replica before
    (`superset-worker` was already 0); the PVCs are kept and **Task 11 must restore those replicas**.
    With only MinIO, its console and the gold PostgreSQL running, the node's requests are 2,060 Mi
    (13.5 GiB free for the scheduler) and `free` reports about 12.8 GiB available. Four executors
    request 4 x 2 GiB (1 GiB heap plus 1 GiB overhead) and the driver pod 1 GiB (limit 2 GiB), about
    10 GiB at worst, so **the grid {1, 2, 4} of D3 stands** by the scheduler's numbers. Real memory
    use at four executors on the largest scale is confirmed in Task 6, not assumed here; a further
    risk noted for Task 6 is one executor holding all of the 4x data.
  - *1.3, MinIO space.* The PVC `minio` is declared as 8 Gi, but the `local-path` StorageClass
    backs it with a plain host directory and enforces no quota: `df` inside the MinIO pod sees the
    whole 1007 GB disk (916 GB free). The bucket `lakehouse` holds 3.1 GB today (`bronze/` 2.7 GB,
    `warehouse/` 395 MB). The benchmark needs about 19 GB of bronze for the three scales (roughly
    2.7 + 5.4 + 11 GB) plus silver, gold and event logs, so about 22 GB: no space problem.
  - *1.4, PostgreSQL.* As user `gold` (no superuser), `CREATE SCHEMA`, `CREATE TABLE`,
    `ALTER TABLE ... RENAME` and `DROP SCHEMA ... CASCADE` all work (the operations of `#99`'s
    swap), so the publish can target `bench_<scale>x` (D5) with the existing Secret. The probe
    schema was dropped.
  - *1.5, landing (D4, D5).* (a) `land_bronze` takes a `bucket` argument but the CLI
    (`python -m tfm_lakehouse.bronze.tasks land-bronze`) does not expose it, and the prefix
    `bronze/` is a module constant, so the isolation is **one bucket per scale**
    (`s3a://<bucket>/bronze`, read by `--bronze-root`); Task 2 calls `land_bronze` from its own
    script with `bucket=`, and neither the CLI nor `#97`'s code changes. (b) The bulk records are
    taken by `_iter_subset_paths` in sorted-folder then sorted-name order, first N, so the 20k, 40k
    and 80k sets are **nested** by construction. (c) The synthetic generator draws from a seeded
    random stream and stops at `count`: with `seed=43`, the first 30 documents of a 60-document
    run were byte-identical to the 30-document run (tested, 22 and 46 linked), so the 11k, 22k and
    44k CVN sets are nested too. (d) The API sample: `run_orcid_api_enrichment` calls the live ORCID
    API, which is not needed: the run `e2e98-big` (seed 43, 10,000 CVNs) already holds a 200-record
    sample of ORCID iDs declared by those CVNs, which are within the first 11,000 documents of every
    scale, so its `orcid_api/records.jsonl` and `orcid_api.summary.json` are copied into each
    benchmark run directory (fixed sample of **200** records, not the ~400 first estimated). (e)
    Composition caveat, to be reported with the results: the generator draws seeds from **the whole
    301,763-record subset**, while the landed bulk records are the **first N** in folder order, so
    the share of CVN iDs that also exist in the landed bulk data (which drives rule R1 across
    sources) grows with the scale; the per-scale entity counts are measured, not assumed.
  - *1.6, event log (D7).* Done with a throwaway driver pod (client mode, gold image, 4 executors of
    1 GiB heap plus 1 GiB overhead, `minRegisteredResourcesRatio=1.0`, a 6M-row job with a Python
    UDF; the script and pod were temporary and are not in the repository). Findings:
    (a) MinIO's pod carries its credentials as files (`MINIO_ROOT_USER_FILE`,
    `MINIO_ROOT_PASSWORD_FILE`), not as `MINIO_ROOT_*` variables, so `mc` inside it is configured
    with `mc alias set ... "$(cat $MINIO_ROOT_USER_FILE)" "$(cat $MINIO_ROOT_PASSWORD_FILE)"`; the
    first attempt with the variables failed with `Access Denied`. (b) The bucket root is not a
    usable event-log directory: `spark.eventLog.dir=s3a://tfm-bench-events/` fails with
    `IllegalArgumentException: path must be absolute`; **`s3a://tfm-bench-events/logs`** works once a
    marker object `logs/.keep` exists (Spark requires the directory to exist), so the runner
    creates the bucket and the marker; the event log lives in a dedicated bucket, not in
    `lakehouse`. (c) With the ratio at 1.0 the driver logged 4 executors registered before
    scheduling, the job ran 9.8 s and the memory available to WSL did not fall under 9.7 GB with
    the four executors up, so **four executors do start and coexist** (the heavy-load check is
    still Task 6). (d) The log is one file per application, `spark-<uuid>` (246 KiB here), readable
    back with `mc cat`, and holds `SparkListenerApplicationStart`/`End` (epoch-millisecond
    `Timestamp`), `ExecutorAdded`, `JobStart`/`JobEnd`, `StageSubmitted`/`StageCompleted`,
    `TaskEnd` with `Executor Run Time`, `Executor CPU Time`, `JVM GC Time`, `Peak Execution
    Memory`, `Memory`/`Disk Bytes Spilled`, `Shuffle Read/Write Metrics`, `Input/Output Metrics`,
    and the SQL execution events: everything D7 needs. A copy of this log is the seed of the
    parser's test fixture (Task 4). The test pod, executors and log object were removed; the
    bucket `tfm-bench-events` and its `logs/.keep` remain and are dropped in Task 11.
  - *1.7, plotting (D11).* `uv pip compile --python-version 3.14 --only-binary :all:` resolves
    `matplotlib` 3.11.2 with 10 dependencies (`numpy` 2.5.3, `pillow` 12.3.0, `fonttools`,
    `kiwisolver`, `contourpy`, ...), all with wheels for CPython 3.14, so D11 stands. Nothing was
    added to `pyproject.toml` or `uv.lock` yet (`uv add` has no `--dry-run`); that happens in
    Task 5. The ten transitive packages will enter the lock file, which CI installs. Only the
    resolution was tested, not an import; Task 5 imports it for real.
  - *1.8, noise floor (D8).* `bronze_to_silver` was run three times in a row with the `#98` sizing
    (2 executors, 1 GiB heap plus 1 GiB overhead, 16 shuffle partitions) over the production
    bronze **read-only**, writing to a probe namespace `lakehouse.bench_probe` (dropped afterwards;
    production `silver`, `gold` and `smoke_test` untouched), with a throwaway pod equivalent to
    what the Task 3 runner will build. Job time (`elapsed_seconds`) **253.8 s, 208.5 s, 213.4 s**;
    pod wall time 284 s, 229 s, 237 s (the 30 s or so on top is pod scheduling, executor start-up
    and teardown, which is why D7 separates `app_seconds` from `compute_seconds`). All three runs
    produced exactly the tables of `#98`/`#99` (30,868 person records, 29,767 entities, 543,879
    publications, 99,979 affiliations, 0 rejected). Reading of the numbers: (a) the two warm runs
    differ by 2.3% of their median, well inside D8's 10% criterion, so the criterion stays as a
    conservative bound rather than being tightened on two samples; (b) they agree with `#99`'s
    219.8 s warm figure within 5%, so the throwaway pod measures the same thing as the DAG; (c) the
    first run was **1.22 times** slower than the warm ones (against 1.3-2.5 in `#98`); the cause was
    not isolated (executor images, JIT and the storage cache are all candidates), so **D8 is refined:
    the first run of each new scale is discarded too, not only the first of the session**, because
    a new scale reads data for the first time; (d) the memory available to WSL fell from about 12.9
    GB idle to 8.3 GB at the lowest point with two executors, roughly 4.5 GB used, so four
    executors are expected to leave a few GB free; the check under load stays in Task 6. The
    25 MB event log of a real silver run (2,498 events, dominated by SQL plan descriptions) was
    kept outside the repository as the raw material of the parser's fixture, which will be a
    trimmed copy.

- **Task 2, benchmark data (2026-09-21).** `python -m tfm_lakehouse.benchmark.data 1x 2x 4x`
  (`src/tfm_lakehouse/benchmark/data.py`) landed the three scales, one bucket each, through a
  port-forward to MinIO (about 1 hour in total, the CVN generation at 35 documents/s and the
  bulk landing at about 9.5 MB/s dominating). Measured, not assumed:

  | scale | bulk records landed (rejected) | CVN documents (with ORCID iD) | API | person records | bucket size |
  | --- | --- | --- | --- | --- | --- |
  | 1x | 19,469 (2.66%) | 11,000 (7,800) | 200 | 30,669 | 2.82 GB |
  | 2x | 38,920 (2.70%) | 22,000 (15,500) | 200 | 61,120 | 5.49 GB |
  | 4x | 77,868 (2.67%) | 44,000 (31,003) | 200 | 122,068 | 10.94 GB |

  The rejection rate stays at the 2.7% of `#97` at every scale (records without a public name), so
  the composition is stable; the bulk records of 1x are byte-for-byte those of `#97`'s default
  landing (same 19,469 landed). The three buckets, the event-log bucket and the run directories
  under `data/bronze_runs/bench-*` are the state Task 11 removes.

- **Tasks 3-5, code (2026-09-21).** `src/tfm_lakehouse/benchmark/` (`data`, `runner`, `campaign`,
  `eventlog`, `report`) and `src/tfm_lakehouse/spark_jobs/table_digest.py`, with 51 new tests
  (`tests/test_benchmark_unit.py`, `tests/test_benchmark_digest_spark.py`) and a trimmed real
  event log as fixture (`tests/fixtures/spark_event_log_sample.jsonl`, 371 KB, 517 events of the
  25 MB log; its expected figures were counted from the file, not from the parser). Two corrections
  the tests forced: the digest job's `str(None)` for an empty table, and my own wrong expectation
  of 37 stages (37 were the stage ids the job events list; 12 stages complete). One design point
  found while writing the report: a digest run always uses two executors, so its record carries
  `executors_of`, the executor count of the run whose output it digests; without it every
  configuration's digest would have looked like the two-executor one. `matplotlib` 3.11.2 was
  added as a development dependency with `uv add --dev` (`pyproject.toml`, `uv.lock`).

- **Task 6, pilot (2026-09-21).** Run on the real cluster, over 1x and 4x, before the campaign. It
  changed the design three times (D18-D20), which is what a pilot is for.
  - *6.1, the runner end to end.* `runner --scale 1x --job silver --executors 2` finished `ok`
    (pod 394.7 s, job 343.4 s: inflated, the landing of 2x was running at the same time and none of
    the pilot's timings is used) with 30,669 person records, 29,805 entities, 538,472 publications,
    99,340 affiliations and no rejection (the production silver differs, 30,868 and 29,767, because
    its bronze holds the 399 API records and the seed-42 CVNs). The record, the driver log, the 25 MB
    event log and the summary were written, the event log parsed (application 354.8 s, start-up
    10.9 s, compute 337.9 s, driver gaps 31.9 s) and no pod was left behind.
  - *6.2, the mechanics at 1 and 2 executors (13 runs, 40 minutes).* Silver, gold and publish with
    their digests. The digests of the three outputs (silver tables, gold tables, PostgreSQL rows) are
    **identical across executor counts**; adding the runs with 4 executors below, across 1, 2 and 4.
  - *6.3, four executors do not go faster.* On the idle machine, silver at 1x took 295.4 s of
    application time with 4 executors against about 215 s at 2 (Task 1.8: job time 208.5 s and 213.4
    s; the two are close but not the same metric, the campaign measures every point the same way);
    gold took 101.4 s against 94.7 s and the publish 98.9 s against 85.4 s. Comparing the same 1x job
    stage by stage, the total task time nearly doubles (856 s at 4 executors against 442 s at 2) for
    the same work, and it is not spread evenly: the stages that write the Iceberg tables to MinIO
    (`createOrReplace`) take **3.7-4.0 times** the task time, the stage that reads and parses the
    bronze 2.2 times and the resolution stage 1.3 times. So more executors made each task slower,
    most of all where the job writes to the object store. The 4x run with 4 executors (below) had the
    system CPU **19% busy** (16 logical CPUs; 6.1% I/O wait, 6.1% system, no steal): the machine was
    not CPU bound. What the data support is that the shared object store is the likely limit (the
    stage pattern, and 3 writer-close failures in the 4x run); what they do not show is the
    mechanism inside MinIO, which is why D20 adds direct measurements. The CPU is an AMD Ryzen 7
    2700X: 8 physical cores and 16 logical processors, so WSL2's 16 CPUs are hyper-threads.
  - *6.4, the 4x scale needs proportional shuffle partitions (D18).* The first 4x run (4 executors,
    16 partitions) was aborted after 22 minutes: executor 3 was lost about 9.5 minutes in, the
    shuffle stage failed with `FetchFailedException`, was resubmitted repeatedly and replacement
    executors kept appearing (`exec-5`, `exec-7`); the executors' memory read 1.4-1.5 GiB of the
    2 GiB limit when looked at. With 64 partitions it finished `ok` in 1,324.9 s (application 1,202.4
    s: start-up 27.9 s, compute 1,158.8 s of which 99.5 s driver gaps), 4 executors registered, none
    lost, 3 retried tasks (Iceberg writer close), 122,066 person records, 110,789 entities,
    2,097,315 publications, 394,504 affiliations, 2 rejected records, minimum available memory 5.2 GB.
    The digests of the 4x output were not compared yet (they are, per configuration, in the
    campaign).
  - *Budget (D13, revised).* The measured 1x times give, per repetition of all executor counts, about
    14 minutes of silver at 1x, 28 at 2x and 62 at 4x (1 executor about twice 2 executors; 4 executors
    a third more than 2), plus gold and publish and the digests: about **8.5-9 hours of machine time
    for the 108 runs** with three repetitions, more than the 7 h first estimated because 4 executors
    are slower than 2. The plan runs scale by scale (1x, then 2x, then 4x), so the campaign can be
    stopped after any scale and still gives complete data for the scales before it; the cut order
    of D13 stays (fewer repetitions on 4x, then a single scale). The decision taken is to run the
    full plan.

- **Task 7, campaign, incident and fix (2026-09-22).** The campaign (`python -m
  tfm_lakehouse.benchmark.campaign`) started 2026-09-21 22:48:58; runs 1-10 (the `1x` silver
  warm-up and the first nine measured/digest runs, executors 2, 1, 2, 4, 1, 2 in the seeded
  order) completed normally in 37-42 minutes of elapsed campaign time. Run 11
  (`1x-silver-e1-r011`) was submitted 2026-09-21 23:30:44 and the runner reported it as `timeout`
  at 2026-09-22 16:48:04 (`wall_seconds` 62,202.9). The host machine had slept overnight
  (Windows/WSL2 suspend, not a reboot: the node's age and the pods' ages stayed continuous,
  `uptime` after resume read about 7 h, consistent with only the active hours counting); the
  driver log shows the job frozen mid-task (one task logged as taking 61,933,613 ms) and then
  resuming completely normally afterward, so the job itself was never unhealthy -- it was killed
  by the runner's own false timeout, root-caused and fixed as decision D22 above. No pod was left
  behind by the kill (`executor_leftovers` was empty and a live check found none), and the killed
  run was in an early read stage, before any `writeTo(...).createOrReplace()`, so no partial
  output exists in `lakehouse.bench_silver_1x` to clean up.
  - **the user must prevent the host from sleeping for the rest of the campaign** (Windows power
    settings, or keeping the machine awake by other means); this is outside what the assistant can
    control from inside the repository or the cluster, and a second sleep would still cost real
    time re-running whatever point it interrupts, even though it can no longer produce a false
    "timeout" record now that D22 is fixed.
  - the campaign is resumable by design (`campaign.execute`/`_done` skip only runs recorded `ok`),
    so it was restarted with the same command and the same default seed; it picked up at run 11
    without re-running 1-10.

- **Task 7, campaign, second incident and fix (2026-09-22).** After the D22 fix, the campaign was
  resumed (16:55:27) and ran cleanly through run 41 (2x, up to executor count 4). Run 42
  (`2x-silver-e1-r042`, 1 executor) ended `failed` after 1,396.8 s (`active_seconds` 1,377.1,
  `suspected_suspend_seconds` 0.0 -- not a repeat of D22): its driver log shows the sole executor
  exiting with `code 52(JVM OOM)` at minute 4, Spark requesting a replacement, that replacement
  OOMing too at minute 13, a third at minute 19, a fourth immediately after, then
  `ExecutorPodsAllocator: Max number of executor failures (3) reached` and the application
  stopping itself (`SparkContext is stopping with exitCode 0`, a clean shutdown, not a crash). The
  same `2x` silver job completed without incident at 2 executors (468.3 s, 401.1 s) and 4
  executors (1,171.2 s), confirming the ceiling is specific to holding the whole `2x` scale in one
  1 GiB-heap executor, not a general problem with the job or the scale. No pod was left behind
  (`executor_leftovers` empty, confirmed live) and, since the job failed in an early stage before
  any `writeTo(...).createOrReplace()`, no partial silver output exists to clean up. Fixed as
  decision D23 above (the campaign now records this outcome and moves on instead of stopping), and
  the campaign was resumed again with the same command; it picked up at run 42.
  - this is expected to recur for `(4x, silver, 1 executor)` (four times the volume of a
    configuration that already cannot hold `2x`) and is now handled the same way; it is a finding
    for the evaluation chapter (the number of executors is not just a speed lever at fixed memory,
    it decides whether a configuration can run at all at larger scale), reported in Task 8 rather
    than hidden.

- **Task 7, campaign, third incident and fix (2026-09-22).** The D23 fix worked as designed: run
  42 OOM'd again (1,298.5 s, the same `exit code 52(JVM OOM)` pattern) and the campaign correctly
  logged it and moved on to run 43. Run 43 (`2x-digest-silver-e2-of1-r043`, the digest of run 42's
  output) then crashed for a different, new reason and stopped the campaign again: its driver log
  shows `pyspark.errors.exceptions.captured.AnalysisException:
  [TABLE_OR_VIEW_NOT_FOUND] The table or view `lakehouse`.`bench_silver_2x`.`person_record`
  cannot be found`. Root cause and fix are decision D24 above. No pod was left behind. The
  campaign was resumed a third time with the same command; it picked up at run 42 again (its
  earlier attempt was recorded `failed`, not `ok`, so the resumability rule reran it rather than
  skipping it, giving `(2x, silver, 1 executor)` a second independent OOM data point).

- **Task 7, campaign, fourth incident and D25 (2026-09-22).** With D23/D24 in place, the campaign
  ran cleanly from run 42 through run 44 (`2x-silver-e1-r042` OOM'd a second time as expected and
  the campaign moved on, as designed; `2x-digest-silver-e2-of1-r043` correctly digested the
  missing table, `2x-silver-e4-r044` completed normally). At this point the user asked for a
  revised time estimate; recomputing it surfaced that `(2x, silver, 1 executor)` still had two
  more planned repetitions (`r046`, `r049`), each worth a full ~23-30 minutes before failing again
  for no new information, since the ceiling was already confirmed twice. Given that, the user
  chose to stop repeating a configuration once it is confirmed to never succeed, rather than run
  the full accepted 3 repetitions everywhere unconditionally.
  - implementing that surfaced a **new, distinct incident** before the campaign could even be
    resumed: while waiting for the in-flight `2x-silver-e2-r045` to finish before stopping the
    process cleanly, it ended `failed` (782.6 s) -- **also an executor OOM** (`exit code
    52(JVM OOM)` on executor id 5), but Spark gave up a different way this time (repeated
    `FetchFailedException`/`ExecutorDeadException` from the lost executor exceeded the *stage's*
    own retry limit -- `"has failed the maximum allowable number of times: 4"` -- rather than the
    executor allocator's own ceiling), which `_diagnose_failure`'s original, narrower signature
    did not recognize, so the campaign correctly stopped for an "unrecognized" failure that was in
    fact the same root cause. Two earlier `(2x, silver, 2 executors)` runs had already succeeded
    (401.1 s, 468.3 s), showing this configuration is *not* a deterministic ceiling like the
    1-executor one -- it is marginal, occasionally exceeding the fixed 1 GiB heap.
  - both findings are decision D25: the diagnosis signature is broadened to the literal, stable
    `"exit code 52(JVM OOM)"` message alone (present in both incidents), and the campaign now only
    skips further repeats of a `(scale, job, executors)` configuration once *every* recorded
    attempt of it OOM'd (zero successes across at least 2 attempts) -- so `(2x, silver, 1
    executor)`'s remaining repeats are skipped, while `(2x, silver, 2 executors)` keeps retrying
    normally like any other transient failure. No pod was left behind by `r045`. The campaign was
    resumed a fourth time with the same command.
  - **finding for the evaluation chapter, not hidden:** the fixed 1 GiB heap plus 1 GiB overhead
    sizing (decision D8) is not only a hard, deterministic ceiling at 1 executor for `2x`/`4x`
    volume; it is close enough to the edge at 2 executors that a single run can occasionally OOM
    even there, while 3 other runs at the same configuration succeeded. This bears directly on
    `HA02`/`CP04`: the number of executors is not just a speed lever under fixed per-executor
    memory, it is a reliability lever too.
  - **implementation gap found immediately after writing D25:** counting attempts by scanning
    `record.json` files undercounts a run id retried across several campaign resumes (the real
    `2x-silver-e1-r042`: three separate real attempts, but only the latest record.json survives
    on disk, since each retry overwrites the same file), which would have let `r042` itself run a
    third time for no reason before the skip could trigger. Fixed before resuming: `execute()`
    archives a run id's existing record to `record.attemptN.json` right before retrying it, and
    `_attempt_outcomes` reads both; the campaign was resumed a fifth time only after this held (63
    then 65 tests, including one that reproduces this exact gap).

- **Task 7, campaign, fifth and sixth incidents, D26 (2026-09-23).** After the D22-D25 fixes, the
  campaign ran unattended through the night; the host restarted for real at some point overnight
  (`uptime` showed about 4 minutes on the next check, and the scratchpad log under `/tmp` was
  gone -- `/tmp` does not survive a WSL2 restart, unlike the actual benchmark data under the
  repository checkout, which was untouched). Three orphaned pods from the interrupted run
  (`bench-2x-silver-e2-r045` and its two executors, stuck `Unknown`) were force-deleted; MinIO and
  PostgreSQL came back healthy on their own; Superset and Airflow were still at 0 replicas (that
  state lives in the cluster, not the host). The campaign was resumed a sixth time.
  - **fifth incident:** `2x-silver-e1-r042` was correctly skipped this time (D25 working), but its
    own record got overwritten in the process, so `2x-silver-e1-r046` ran for real instead of
    being skipped too (a real ~22 min cost, not a correctness problem: it produced a third genuine
    `executor_oom` confirmation), and the same then happened to `2x-silver-e1-r049`. Root-caused
    and fixed as decision D26(a).
  - **sixth incident:** with `2x-silver-e1-r049` (OOM'd, no output) the last silver attempt of the
    scale, `2x-gold-e2-r050` (a warm-up) failed cleanly with `silver_to_gold`'s own
    `silver table lakehouse.bench_silver_2x.entity is missing; gold was not written`, which
    `_diagnose_failure` correctly did not recognize as an OOM, so the campaign correctly stopped
    for a genuinely new cause. Root-caused and fixed as decision D26(b); resumed a seventh time.

- **Task 7, campaign, seventh incident, D27 (2026-09-23).** The campaign then ran unattended
  through most of `2x`'s gold/publish phase and into `4x`'s silver phase; along the way it
  survived a second, genuine host suspend mid-run (`2x-publish-e2-r063`, frozen for about 7h40m,
  `active_seconds` correctly under budget thanks to D22, so it simply finished once the host woke
  -- no intervention needed, confirming D22's fix generalizes beyond its original incident). At
  `4x`, `(silver, 2 executors)` also turned out to be a confirmed deterministic OOM (its warm-up
  and first repeat both OOM'd, exactly like `(silver, 1 executor)` at this scale), correctly
  triggering a D25 skip for its second repeat (`r081`) -- but the skip's own fresh record then
  broke the confirmation for the *third* repeat (`r083`), which ran for real instead of being
  skipped, the same class of gap as D26(a) one step removed. Root-caused and fixed as decision
  D27; caught before it could affect the upcoming gold phase (which has not shown any OOM so far,
  but the fix applies uniformly). The already-running process was stopped cleanly at the silver/
  gold boundary (its last silver run, `4x-silver-e4-r085`, had already finished successfully, and
  the just-started `4x-gold-e2-r086` was deleted a few seconds in, before writing any record) and
  resumed an eighth time with the fix loaded (70 tests).

- **Task 7, campaign, eighth incident, D28 (2026-09-23).** The resumed campaign correctly retried
  `4x-silver-e2-r073`'s warm-up (D27 working: `r076`, `r078`, `r081`, `r082`, `r083`, `r084` were
  all then instantly skipped, no wasted time), but that retry OOM'd, and `4x-gold-e2-r086`
  immediately failed with the same `silver table ... is missing` message as the sixth incident,
  even though D26(b)'s repair check had, by design, just run before it. Root cause and fix are
  decision D28: the repair check used `_last_write_ok`, which judged recency by `sequence`, and
  `r085` (a higher sequence number, from *before* this resume) still looked like the latest write
  even though the retried `r073` (lower sequence, but it started ~4 hours later in real time)
  had since reset and OOM'd. Fixed and resumed a ninth time (71 tests).

- **Task 7, campaign, ninth and tenth incidents (2026-09-23/24).** The campaign then ran through
  the rest of `4x` silver and all of gold unattended (D25/D27's skips firing correctly and fast
  for every already-confirmed OOM configuration along the way), reaching `4x-publish` at run 99
  before the host restarted for real again (uptime back to a few minutes; the usual orphaned
  pods force-deleted, MinIO/PostgreSQL/Superset/Airflow state all as expected). Resumed; on this
  attempt `4x-publish-e2-r099` failed with a PostgreSQL connection refused right at its own
  cleanup step -- PostgreSQL's own pod was still mid-WAL-recovery from the same host restart
  (`database system was interrupted`), a benign, one-off startup race resolved by simply waiting
  for it and retrying, no code change needed.
  - **tenth incident, decision D29:** resumed again, and `4x-publish-e2-r099` failed the *same way*
    a second time, but this time PostgreSQL was already confirmed healthy beforehand -- a genuine,
    reproducible cause, not a race. `kubectl describe pod` showed the PostgreSQL container itself
    had been `OOMKilled` (a hard 192Mi memory limit inherited from the Bitnami chart's default
    `resourcesPreset: "nano"`, never exercised by `1x`/`2x`'s smaller gold tables). Root-caused and
    fixed as D29 (raised via `helm upgrade`, verified healthy with all schemas and data intact);
    resumed a tenth time.

- **Task 8, analysis (2026-09-24).** `python -m tfm_lakehouse.benchmark.report` over the full
  108-run campaign plus its 2 repair runs (110 records) produced 27 usable
  `(scale, job, executors)` points and `docs/benchmark/results.md`/`.csv`/`.json` plus three
  charts. Two report bugs were found and fixed while reading the first version of the output
  (both before any figure was trusted for the findings below):
  - `correctness_ok` was `False` for `2x`/`4x` silver purely because 1 (and, at `4x`, also 2)
    executors never produced output at all (D25's confirmed ceiling) -- correct as a blunt
    whole-set comparison, misleading as a verdict. `report.correctness` now separately reports
    `empty_executors` (confirmed-OOM configurations that wrote nothing) and `consistent` (do the
    configurations that *did* produce output agree). Result: **every configuration that
    completed at every scale produced byte-identical Iceberg/PostgreSQL output** (`2x` silver at
    2 and 4 executors: identical row counts and content hashes down to the digest; same at `4x`
    gold and publish across all three executor counts).
  - all 9 of the `4x-publish` warm-up/measured runs -- the very last work the campaign did --
    showed `executor_leftovers: [bronze-to-silver-...-exec-6, bronze-to-silver-...-exec-7]` and
    were excluded from the figures. Both pods belonged to the unrelated, independently-failed
    `4x-silver-e2-r073` (an OOM at 15:33:47Z that left them uncleaned); `Cluster.executor_pods()`
    listed every executor pod in the namespace by the generic `spark-role=executor` label, not
    scoped to the run being checked, so a stale orphan from one interrupted run got blamed on nine
    later, unrelated, genuinely successful ones. Fixed for future runs (`Cluster.app_id` reads the
    driver's own `spark-app-selector` label; `executor_pods`/the final leftover check are scoped
    to it, 76 tests including two reproducing this exact scenario) and corrected by hand in the
    nine affected records, with the evidence for the correction recorded in each
    (`executor_leftovers_note`).

## Implementation Performed

`src/tfm_lakehouse/benchmark/` (`data`, `runner`, `campaign`, `eventlog`, `report`) and
`src/tfm_lakehouse/spark_jobs/table_digest.py`: an isolated three-scale data campaign (1x/2x/4x,
each nested in the smaller ones), a Spark-job runner that mirrors `transform_publish`'s own
`spark-submit` invocation, a resumable campaign that ran the full accepted plan (108 runs, three
repetitions per `(scale, job, executors)` point, warm-ups discarded) plus two automatic repair
runs, an event-log parser, and a report generator producing `docs/benchmark/results.{md,csv,json}`
and three charts. See `docs/benchmark/README.md` for the reproduction steps and D1-D29 above for
every design decision and its reason.

## Verification

The campaign ran to completion (108/108 plan items, 2026-09-21 22:49 to 2026-09-24 18:16 of wall
time, most of it unattended). Correctness (decision D9): every `(scale, job)` where more than one
executor count actually produced output agrees byte-for-byte (identical Iceberg/PostgreSQL content
digests) -- confirmed for `1x`/`2x`/`4x` gold and publish across 1, 2 and 4 executors, and for
`1x`/`2x` silver (`4x` silver only ever had one surviving executor count, so there is nothing to
compare it against). 76 unit tests (`tests/test_benchmark_unit.py`) plus 3 in the Spark image
(`tests/test_benchmark_digest_spark.py`) cover the modules built for this issue, several of them
reproducing real incidents found while running the campaign. The full documented suite
(`uv run pytest -n auto tests`) is run as part of Task 9, below.

## Findings

- **The number of executors is a reliability lever, not only a speed lever, once volume grows.**
  At the fixed per-executor sizing of decision D8 (1 GiB heap, 1 GiB overhead for silver, 512 MiB
  for gold/publish), silver at 1 executor is a **deterministic memory ceiling** from `2x` upward:
  every attempt at `2x`/`4x` with 1 executor OOM'd (`exit code 52(JVM OOM)`), while 2 and 4
  executors completed it every time they were tried. At `4x`, even **2 executors** turned out to
  be a deterministic ceiling for silver (both its attempts OOM'd); only 4 executors ever
  completed `4x` silver. Gold hit the same wall once, at `4x`/2 executors (a `SIGKILL`, container
  OOM), though not deterministically. This directly serves `HA02`/`CP04`: under a fixed resource
  budget, adding executors is what makes a larger job *possible*, before it is what makes it
  faster.
- **More executors do not reliably mean less time on this single-node cluster.** Silver's speedup
  at `1x` is 1.50x with 2 executors and only 1.63x with 4 (efficiency 0.75 and 0.41): far from
  linear. Gold's efficiency collapses even faster (1.00 to 0.53 to 0.23 from 1 to 2 to 4
  executors at every scale) because its workload -- a handful of already-aggregated tables -- is
  too small to benefit from more parallelism once fixed per-executor overhead (start-up,
  scheduling) is paid. The publish job's size-up exponent is **negative** (-0.09 to -0.16): its
  runtime barely grows with data volume at all (61-142 s across every scale and executor count),
  because it stages and swaps the same small number of gold tables regardless of how many rows
  they hold. Silver, in contrast, has a size-up exponent of 1.22 at 4 executors (`1x`->`4x`):
  close to linear growth with volume, as expected for a job whose work is dominated by parsing and
  writing the raw records themselves.
- **The task-level evidence points at the shared object store (MinIO), not CPU, as the limit on
  this single node.** The pilot (Task 6) already showed writing to MinIO scaling worse than
  reading; the campaign's own CPU sampling confirms the node was never CPU-bound (8.7-32.2% system
  CPU busy across every silver run, highest exactly at 4 executors where MinIO's own sampled CPU
  also peaked, 141-392 millicores). This is consistent with, not proof of, a single shared
  object-store bottleneck; the exact mechanism (network, MinIO's own I/O, or contention with
  PostgreSQL and k3s on the same disk) was not isolated further, which is why it is reported as an
  observation, not a proven root cause.
- **PostgreSQL's default resource sizing (a Bitnami chart preset meant for a small workload) was
  the true ceiling for publishing at the largest scale**, not anything about the benchmark's own
  design: `4x`'s gold tables OOMKilled the PostgreSQL container at its inherited 192Mi memory
  limit twice in a row; raising it (decision D29) let every `4x` publish configuration complete
  cleanly afterward, all three agreeing byte-for-byte.
- **The campaign spent a large share of its wall time recovering from infrastructure interruptions
  it did not cause**, not from the benchmark's own design: the host machine slept or restarted for
  real six separate times across the roughly 68 hours the campaign was open (decisions D22, and
  the incidents of Task 7 dated 2026-09-22 through 2026-09-24), each requiring the assistant to
  clean up orphaned pods and resume; none of them lost data or corrupted a result, but they are
  why the campaign's calendar time is not a meaningful "how long the benchmark takes" figure --
  the per-job timings in `docs/benchmark/results.md` are.

## Known Limitations

- **Single node, no real network shuffle.** The executors, MinIO, PostgreSQL and k3s all share one
  machine's 16 logical CPUs and RAM; the reported speedups measure local parallelism, not a
  distributed cluster's, and there is no network cost between executors to see.
- **`4x` silver has no executor-count comparison.** Only 4 executors ever completed it (1 and 2 are
  both confirmed deterministic OOM ceilings at that scale), so the correctness check and the
  speedup/efficiency figures for `4x` silver at 1 and 2 executors do not exist, not merely "did not
  finish in time" -- they cannot exist at this fixed sizing.
- **The object-store bottleneck hypothesis is not proven, only consistent with the evidence.** CPU
  and MinIO CPU sampling (decision D20) point at MinIO rather than CPU as the practical limit on
  write-heavy stages, but the exact mechanism inside MinIO was not isolated (a dedicated I/O
  profiling pass was out of scope, consistent with the epic's deferral of a full observability
  stack).
- **The event-log-derived `Executor CPU Time` excludes the Python worker processes** that parse the
  raw ORCID/CVN records, so it understates true CPU use of the pipeline; the system-wide `/proc/
  stat` sampling (decision D20) is the more complete figure and is what the findings above use.
- **The benchmark's own reliability-hardening (decisions D22-D29) reacted to real infrastructure
  interruptions during this specific campaign**; it was not designed against them in advance, and
  a future rerun on a machine that never sleeps would look different (faster, with fewer excluded
  runs) without being a more "correct" benchmark -- the current results already reflect a
  real-world single machine, sleep interruptions included, which is itself informative for a
  self-hosted, single-node deployment story.
- **Nine of the 110 run records required a documented hand-correction** after the fact (the
  `executor_leftovers` misattribution found in Task 8); the corrected records carry an
  `executor_leftovers_note` field stating exactly what was wrong and why, kept as part of the
  benchmark's own raw data rather than silently edited.

## Impact On Future Issues

Feeds the memoria (issue `#103`) as the evaluation chapter's performance evidence: the results
tables and charts in `docs/benchmark/`, the reliability-vs-scale finding (`HA02`/`CP04`), and the
infrastructure-sizing finding (PostgreSQL's default resource preset) are all concrete, reproducible
evidence points. Issue `#102` (hardening) inherits the fixed-sizing memory ceiling documented here
as a known, accepted limitation of the current deployment, and the raised PostgreSQL resource
limits (`infra/helm-values/postgresql-values.yaml`, decision D29) as a production-relevant change
made during this issue, not `#99`/`#100`.

## Status

`Completed`. All eleven tasks done: the campaign (108/108 plan items plus 2 repair runs), the
analysis and report (`docs/benchmark/`), the full documented test suite (909 passed, 2 skipped),
documentation close-out, and the cluster left in a clean, production-safe state.
