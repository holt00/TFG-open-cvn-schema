"""Unit tests of the issue #101 benchmark package: data scales, event log parser, runner, campaign, report.

No cluster, no network and no Spark: the cluster is a fake, the event log is a trimmed real log of
a ``bronze_to_silver`` run (``tests/fixtures/spark_event_log_sample.jsonl``), and the expected
figures of that log were computed independently of the parser when the fixture was cut.
"""

import base64
import json
import re
import shutil
from pathlib import Path

import pytest
from botocore.exceptions import ClientError

from tfm_lakehouse.benchmark import campaign, data, eventlog, report, runner

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "spark_event_log_sample.jsonl"
DAG_SOURCE = (ROOT / "dags" / "transform_publish.py").read_text(encoding="utf-8")


# --------------------------------------------------------------------------- data


def test_scales_grow_linearly_from_the_base_and_name_their_outputs():
    for factor in (1, 2, 4):
        scale = data.scale_for(f"{factor}x")
        assert scale.bulk_records == 20_000 * factor
        assert scale.cvn_documents == 11_000 * factor
        assert scale.bucket == f"tfm-bench-{factor}x"
        assert scale.bronze_root == f"s3a://tfm-bench-{factor}x/bronze"
        assert scale.silver_namespace == f"lakehouse.bench_silver_{factor}x"
        assert scale.gold_namespace == f"lakehouse.bench_gold_{factor}x"
        assert scale.pg_schema == f"bench_{factor}x"
        assert scale.run_id == f"bench-{factor}x"


def test_no_benchmark_output_can_be_a_production_location():
    for factor in data.SCALE_FACTORS:
        scale = data.Scale(factor)
        assert scale.bucket != "lakehouse"
        assert scale.silver_namespace not in {"lakehouse.silver", "lakehouse.gold"}
        assert scale.gold_namespace not in {"lakehouse.silver", "lakehouse.gold"}
        assert scale.pg_schema != "gold"


def test_scale_for_accepts_names_and_numbers_and_rejects_unplanned_scales():
    assert data.scale_for(2).factor == 2 and data.scale_for("4X").factor == 4
    with pytest.raises(ValueError, match="unknown scale"):
        data.scale_for("3x")


class _FakeS3:
    def __init__(self, pages=None, existing=True):
        self.pages = pages or []
        self.existing = existing
        self.created: list[str] = []

    def head_bucket(self, Bucket):
        if not self.existing:
            raise ClientError({"Error": {"Code": "404"}}, "HeadBucket")

    def create_bucket(self, Bucket):
        self.created.append(Bucket)

    def list_objects_v2(self, **kwargs):
        index = 1 if kwargs.get("ContinuationToken") else 0
        return self.pages[index]


def test_ensure_bucket_creates_only_a_missing_bucket():
    missing, present = _FakeS3(existing=False), _FakeS3(existing=True)
    assert data.ensure_bucket(missing, "b") is True and missing.created == ["b"]
    assert data.ensure_bucket(present, "b") is False and present.created == []


def test_ensure_bucket_does_not_hide_other_errors():
    class Denied(_FakeS3):
        def head_bucket(self, Bucket):
            raise ClientError({"Error": {"Code": "403"}}, "HeadBucket")

    with pytest.raises(ClientError):
        data.ensure_bucket(Denied(), "b")


def test_measure_bucket_sums_objects_and_bytes_per_source_across_pages():
    pages = [
        {
            "Contents": [
                {"Key": "bronze/source=orcid_bulk/run_id=x/part-0.jsonl", "Size": 100},
                {"Key": "bronze/source=orcid_bulk/run_id=x/part-1.jsonl", "Size": 50},
            ],
            "IsTruncated": True,
            "NextContinuationToken": "t",
        },
        {
            "Contents": [
                {"Key": "bronze/source=synthetic_cvn/run_id=x/part-0.jsonl", "Size": 7},
                {"Key": "bronze/_rejected/source=orcid_bulk/run_id=x/part-0.jsonl", "Size": 3},
            ],
            "IsTruncated": False,
        },
    ]
    assert data.measure_bucket(_FakeS3(pages), "b") == {
        "orcid_bulk": {"objects": 2, "bytes": 150},
        "synthetic_cvn": {"objects": 1, "bytes": 7},
        "orcid_bulk (rejected)": {"objects": 1, "bytes": 3},
    }


def test_copy_api_sample_copies_the_records_and_the_summary(tmp_path):
    source = tmp_path / "bronze_runs" / data.API_SAMPLE_RUN
    (source / "orcid_api").mkdir(parents=True)
    (source / "orcid_api" / "records.jsonl").write_text('{"orcid_id": "x"}\n', encoding="utf-8")
    (source / "orcid_api.summary.json").write_text('{"requested": 1}', encoding="utf-8")
    run = data.RunContext.create("bench-1x")

    data.copy_api_sample(tmp_path, run)

    target = tmp_path / "bronze_runs" / "bench-1x"
    assert (target / "orcid_api" / "records.jsonl").read_text(encoding="utf-8") == '{"orcid_id": "x"}\n'
    assert json.loads((target / "orcid_api.summary.json").read_text(encoding="utf-8")) == {"requested": 1}


def test_copy_api_sample_fails_clearly_when_the_source_run_is_missing(tmp_path):
    with pytest.raises(FileNotFoundError, match=data.API_SAMPLE_RUN):
        data.copy_api_sample(tmp_path, data.RunContext.create("bench-1x"))


def test_prepare_scale_generates_copies_lands_into_the_scale_bucket_and_records_the_result(tmp_path, monkeypatch):
    calls = {}
    monkeypatch.setattr(data, "run_synthetic_cvn", lambda run, data_dir, **kw: calls.update(synthetic=(run.run_id, kw)))
    monkeypatch.setattr(data, "copy_api_sample", lambda data_dir, run: calls.update(api=run.run_id))
    monkeypatch.setattr(data, "land_bronze", lambda run, data_dir, **kw: calls.update(land=kw) or {"sources": {}})
    s3 = _FakeS3(pages=[{"Contents": [{"Key": "bronze/source=orcid_bulk/x", "Size": 5}], "IsTruncated": False}])

    result = data.prepare_scale(data.scale_for("2x"), tmp_path, s3=s3)

    assert calls["synthetic"] == ("bench-2x", {"count": 22_000, "seed": 43, "orcid_link_ratio": 0.7})
    assert calls["api"] == "bench-2x"
    assert calls["land"]["bucket"] == "tfm-bench-2x" and calls["land"]["bulk_max_records"] == 40_000
    assert result["bucket_contents"] == {"orcid_bulk": {"objects": 1, "bytes": 5}}
    assert json.loads((tmp_path / "benchmark" / "data" / "2x.json").read_text(encoding="utf-8"))["scale"] == "2x"


# --------------------------------------------------------------------------- event log


def test_the_real_event_log_sample_gives_the_figures_computed_independently():
    metrics = eventlog.parse_event_log_file(FIXTURE)

    assert metrics.app_name == "bronze_to_silver" and metrics.app_id.startswith("spark-")
    assert metrics.app_seconds == 261.558
    assert metrics.executors_added == 2 and metrics.startup_seconds == 7.505
    assert metrics.compute_seconds == 225.291
    assert metrics.jobs == 12 and metrics.jobs_failed == 0 and len(metrics.stages) == 12  # stages that completed; the 37 ids of the job events include skipped ones
    totals = metrics.totals
    assert totals["tasks"] == 429 and totals["failed_tasks"] == 0
    assert totals["executor_run_seconds"] == 413.265 and totals["jvm_gc_seconds"] == 1.959
    assert totals["input_bytes"] == 3_473_685_601 and totals["output_bytes"] == 48_407_887
    assert totals["shuffle_write_bytes"] == 438_403_205
    assert 0 < metrics.busy_seconds <= metrics.compute_seconds
    assert metrics.gap_seconds == pytest.approx(metrics.compute_seconds - metrics.busy_seconds, abs=0.002)
    assert metrics.sql_executions and all(item["seconds"] >= 0 for item in metrics.sql_executions)
    assert all(stage.wall_seconds is not None and stage.wall_seconds >= 0 for stage in metrics.stages)


def test_to_dict_is_json_serializable_and_carries_the_totals_and_stage_walls():
    payload = eventlog.parse_event_log_file(FIXTURE).to_dict()

    json.dumps(payload)
    assert payload["totals"]["tasks"] == 429
    assert all("wall_seconds" in stage for stage in payload["stages"])


def _lines(*events):
    return [json.dumps(event, separators=(",", ":")) for event in events]


def _app(start, end, executors, jobs, extra=()):
    events = [{"Event": "SparkListenerApplicationStart", "App Name": "t", "App ID": "spark-x", "Timestamp": start}]
    events += [{"Event": "SparkListenerExecutorAdded", "Timestamp": ts, "Executor ID": str(i)} for i, ts in enumerate(executors)]
    for number, (job_start, job_end, result) in enumerate(jobs):
        events.append({"Event": "SparkListenerJobStart", "Job ID": number, "Submission Time": job_start, "Stage IDs": []})
        events.append({"Event": "SparkListenerJobEnd", "Job ID": number, "Completion Time": job_end, "Job Result": {"Result": result}})
    events += list(extra)
    events.append({"Event": "SparkListenerApplicationEnd", "Timestamp": end})
    return _lines(*events)


def test_a_pause_between_jobs_is_driver_time_not_busy_time():
    lines = _app(0, 12_000, [500, 1_000], [(2_000, 5_000, "JobSucceeded"), (8_000, 10_000, "JobSucceeded")])

    metrics = eventlog.parse_event_log(lines)

    assert (metrics.app_seconds, metrics.startup_seconds, metrics.compute_seconds) == (12.0, 1.0, 8.0)
    assert (metrics.busy_seconds, metrics.gap_seconds) == (5.0, 3.0)


def test_overlapping_jobs_are_counted_once_in_the_busy_time():
    assert eventlog._union_seconds([(0, 4_000), (2_000, 6_000), (10_000, 11_000)]) == 7.0
    assert eventlog._union_seconds([]) == 0.0


def test_failed_tasks_and_failed_jobs_are_counted_not_summed_into_the_metrics():
    stage = {"Event": "SparkListenerStageCompleted", "Stage Info": {"Stage ID": 0, "Stage Attempt ID": 0, "Stage Name": "s", "Number of Tasks": 2, "Submission Time": 2_000, "Completion Time": 4_000}}
    ok = {"Event": "SparkListenerTaskEnd", "Stage ID": 0, "Stage Attempt ID": 0, "Task End Reason": {"Reason": "Success"}, "Task Metrics": {"Executor Run Time": 700, "JVM GC Time": 5}}
    bad = {"Event": "SparkListenerTaskEnd", "Stage ID": 0, "Stage Attempt ID": 0, "Task End Reason": {"Reason": "ExecutorLostFailure"}}
    lines = _app(0, 6_000, [500], [(2_000, 4_000, "JobFailed")], extra=[ok, bad, stage])

    metrics = eventlog.parse_event_log(lines)

    assert metrics.jobs_failed == 1
    assert metrics.totals["tasks"] == 1 and metrics.totals["failed_tasks"] == 1
    assert metrics.totals["executor_run_seconds"] == 0.7


def test_sql_plan_events_are_skipped_without_being_decoded():
    huge = '{"Event":"org.apache.spark.sql.execution.ui.SparkListenerSQLAdaptiveExecutionUpdate","plan": not even json'
    metrics = eventlog.parse_event_log([huge, *_app(0, 3_000, [100], [(1_000, 2_000, "JobSucceeded")])])

    assert metrics.jobs == 1


def test_a_lost_executor_is_counted_with_its_reason():
    lost = {"Event": "SparkListenerExecutorRemoved", "Timestamp": 3_000, "Executor ID": "2", "Removed Reason": "Pod exec-2 exited with 137 (OOMKilled)"}

    metrics = eventlog.parse_event_log(_app(0, 6_000, [500, 600, 3_500], [(2_000, 5_000, "JobSucceeded")], extra=[lost]))

    assert metrics.executors_added == 3 and metrics.executors_removed == 1
    assert metrics.executor_removal_reasons == ["Pod exec-2 exited with 137 (OOMKilled)"]
    assert eventlog.parse_event_log(FIXTURE.read_text(encoding="utf-8").splitlines()).executors_removed == 0


def test_a_log_without_an_application_end_or_without_jobs_is_rejected():
    with pytest.raises(eventlog.EventLogError, match="application start or end"):
        eventlog.parse_event_log(_lines({"Event": "SparkListenerApplicationStart", "App Name": "t", "Timestamp": 0}))
    with pytest.raises(eventlog.EventLogError, match="no completed job"):
        eventlog.parse_event_log(_app(0, 1_000, [10], []))


# --------------------------------------------------------------------------- runner


def _spec(job="silver", factor=2, executors=2, sequence=7, **kwargs):
    return runner.RunSpec(data.Scale(factor), job, executors, sequence, **kwargs)


def test_job_arguments_point_each_job_at_its_scale_and_never_pass_the_ground_truth_manifest():
    silver = " ".join(runner.job_args(_spec("silver")))
    gold = " ".join(runner.job_args(_spec("gold")))
    publish = " ".join(runner.job_args(_spec("publish")))

    assert "--bronze-root s3a://tfm-bench-2x/bronze" in silver and "--namespace lakehouse.bench_silver_2x" in silver
    assert "--silver-namespace lakehouse.bench_silver_2x" in gold and "--gold-namespace lakehouse.bench_gold_2x" in gold
    assert "--run-id 2x-gold-e2-r007" in gold
    assert "--gold-namespace lakehouse.bench_gold_2x" in publish and "--pg-schema bench_2x" in publish
    for text in (silver, gold, publish, " ".join(runner.job_args(_spec("digest_silver"))), " ".join(runner.job_args(_spec("digest_gold")))):
        assert "--manifest" not in text
        assert "lakehouse.silver" not in text.replace("bench_silver", "") and "--pg-schema gold" not in text


def test_shuffle_partitions_grow_with_the_scale_so_the_data_per_partition_does_not():
    for factor, expected in ((1, 16), (2, 32), (4, 64)):
        for job in ("silver", "gold"):
            assert f"--shuffle-partitions {expected}" in " ".join(runner.job_args(_spec(job, factor=factor)))
    assert "--shuffle-partitions 100" in " ".join(runner.job_args(_spec("silver", factor=4, shuffle_partitions=100)))


def test_the_digest_of_gold_keeps_only_the_row_count_of_the_run_table():
    text = " ".join(runner.job_args(_spec("digest_gold")))

    assert "--rows-only gold_run" in text and "--tables dim_researcher" in text
    with pytest.raises(ValueError):
        runner.job_args(_spec("nonsense"))


def test_the_command_fixes_everything_but_the_executor_count():
    silver = runner.spark_submit_command(_spec("silver", executors=4))
    gold = runner.spark_submit_command(_spec("gold", executors=1))

    assert "--conf spark.executor.instances=4" in silver and "--conf spark.executor.instances=1" in gold
    for command in (silver, gold):
        assert "--conf spark.scheduler.minRegisteredResourcesRatio=1.0" in command
        assert "--conf spark.eventLog.enabled=true" in command and "--conf spark.eventLog.dir=s3a://tfm-bench-events/logs" in command
        assert "--conf spark.executor.cores=1" in command and "--conf spark.executor.memory=1g" in command and "--driver-memory 1g" in command
        assert "volumes.hostPath.src.mount.path=/repo/src" in command and "volumes.hostPath.schemas.mount.path=/repo/schemas" in command
    assert "spark.executor.memoryOverhead=1g" in silver and "spark.executor.memoryOverhead=512m" in gold
    assert silver.endswith("--summary-file /repo/data/benchmark/runs/2x-silver-e4-r007/summary.json")


def _dag_constant(name):
    return re.search(rf'^{name} = "([^"]+)"', DAG_SOURCE, re.MULTILINE).group(1)


def test_the_runner_and_the_transform_publish_dag_launch_spark_the_same_way():
    """The drift guard of decision D6: what both build must not diverge."""
    command = runner.spark_submit_command(_spec("silver"))
    shared_flags = [
        "exec /opt/entrypoint.sh /opt/spark/bin/spark-submit",
        "--master k8s://https://kubernetes.default.svc:443",
        "--deploy-mode client",
        "--properties-file /opt/spark/conf/iceberg-catalog.conf",
        "--conf spark.driver.bindAddress=0.0.0.0",
        "--conf spark.driver.host=$POD_IP",
        "--driver-memory 1g",
        "--conf spark.executor.cores=1",
        "--conf spark.executorEnv.PYTHONPATH=/repo/src",
        "--conf spark.kubernetes.executor.volumes.hostPath.{name}.mount.readOnly=true",
    ]
    for flag in shared_flags:
        assert flag in DAG_SOURCE, f"the DAG no longer uses {flag!r}"
        assert flag.replace("{name}", "src") in command, f"the runner does not use {flag!r}"
    assert runner.SPARK_IMAGE == _dag_constant("SPARK_IMAGE")
    assert runner.NAMESPACE == _dag_constant("NAMESPACE")
    assert runner.JOBS == _dag_constant("JOBS")
    # REPO_ROOT is deliberately not compared: the DAG's is a fixed fact about the one machine
    # that runs k3s (issue #97, D2), while the runner's own default is computed from `__file__`
    # so it works wherever the benchmark actually runs (CI included, where the checkout is not
    # at that path at all); `BENCH_REPO_ROOT` overrides it for a real cluster run elsewhere.
    assert 'overhead="512m"' in DAG_SOURCE and runner.JOB_OVERHEAD["gold"] == runner.JOB_OVERHEAD["publish"] == "512m"
    assert '"executor_memory_overhead": Param("1g"' in DAG_SOURCE and runner.JOB_OVERHEAD["silver"] == "1g"


def test_the_driver_pod_has_no_literal_secret_and_the_postgres_password_only_for_the_publish():
    silver = runner.pod_manifest(_spec("silver"))
    publish = runner.pod_manifest(_spec("publish"))

    def env(manifest):
        return {item["name"]: item for item in manifest["spec"]["containers"][0]["env"]}

    assert "PG_PASSWORD" not in env(silver) and "PG_PASSWORD" in env(publish)
    for item in list(env(silver).values()) + list(env(publish).values()):
        if item["name"].endswith(("KEY_ID", "ACCESS_KEY", "PASSWORD")):
            assert "value" not in item and "secretKeyRef" in item["valueFrom"]
    assert silver["spec"]["restartPolicy"] == "Never" and silver["spec"]["serviceAccountName"] == "spark"
    assert {volume["name"] for volume in silver["spec"]["volumes"]} == {"src", "schemas", "data"}


def test_pod_names_are_valid_and_unique_per_run():
    names = {runner.RunSpec(data.Scale(f), job, n, s).pod_name for f in (1, 2, 4) for job in runner.JOB_SCRIPTS for n in (1, 2, 4) for s in (1, 2)}

    assert len(names) == 3 * len(runner.JOB_SCRIPTS) * 3 * 2
    assert all(re.fullmatch(r"[a-z0-9]([-a-z0-9]*[a-z0-9])?", name) and len(name) <= 63 for name in names)
    assert _spec("digest_silver", executors=2, sequence=3, of_executors=4).run_id == "2x-digest-silver-e2-of4-r003"


def test_the_publish_digest_hashes_the_four_data_tables_and_only_counts_the_run_table():
    sql = runner.pg_digest_sql("bench_1x")

    assert sql.count("union all") == 4
    assert "select 'gold_run', count(*), 0::numeric from bench_1x.gold_run" in sql
    assert "from bench_1x.dim_researcher t" in sql and "hashtextextended" in sql


class _FakeCluster:
    def __init__(self, phases, leftovers=(), event_log=True):
        self.phases = list(phases)
        self.leftovers = list(leftovers)
        self.event_log = event_log
        self.calls: list[str] = []
        self.applied = None
        self.deleted = False
        self.minio_samples = iter([120, 900, 400])

    def clear_event_logs(self):
        self.calls.append("clear")

    def reset_namespace(self, namespace):
        self.calls.append(f"reset:{namespace}")

    def psql(self, sql):
        self.calls.append(f"psql:{sql}")
        return ""

    def running_pods(self):
        return ["minio-1", "postgresql-0"]

    def minio_cpu_millicores(self):
        return next(self.minio_samples, None)

    def apply(self, manifest):
        self.applied = manifest

    def pod_phase(self, name):
        return self.phases.pop(0) if len(self.phases) > 1 else self.phases[0]

    def app_id(self, driver_pod_name):
        return "app-123"

    def executor_pods(self, app_id=None):
        self.executor_pods_calls = getattr(self, "executor_pods_calls", []) + [app_id]
        return self.leftovers if self.deleted else ["exec-1", "exec-2"]

    def logs(self, name):
        return 'INFO noise\nINFO TASK_SUMMARY {"elapsed_seconds": 12.5, "tables": {"entity": 3}}\n'

    def delete_pod(self, name):
        self.deleted = True

    def fetch_event_log(self, destination):
        if self.event_log:
            destination.write_text("log", encoding="utf-8")
        return self.event_log


class _Clock:
    """A fake wall clock; ``sleep`` advances it. A ``_MonotonicClock`` can track it separately
    so a test can make the wall clock jump (a host suspend) without moving the monotonic one."""

    def __init__(self):
        self.now = 1_000.0

    def __call__(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


class _MonotonicClock:
    """A fake monotonic clock, advanced only by ``sleep`` calls, never by a wall-clock jump."""

    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


def _cpu_probe():
    readings = iter(
        [
            {"user": 100, "nice": 0, "system": 20, "idle": 800, "iowait": 50, "irq": 0, "softirq": 10, "steal": 20},
            {"user": 400, "nice": 0, "system": 60, "idle": 1_000, "iowait": 100, "irq": 0, "softirq": 20, "steal": 20},
        ]
    )
    return lambda: next(readings)


def _run(spec, cluster, tmp_path, **kwargs):
    clock = _Clock()
    memory = iter([9_000, 7_500, 6_000, 8_000])
    return runner.run_once(spec, cluster, tmp_path, clock=clock, sleep=clock.sleep, memory_probe=lambda: next(memory, 9_999), cpu_probe=_cpu_probe(), **kwargs)


class _SuspendingClock:
    """A wall clock that jumps forward by ``jump`` seconds on its second reading (a host suspend)."""

    def __init__(self, jump):
        self.now = 1_000.0
        self.jump = jump
        self.reads = 0

    def __call__(self):
        self.reads += 1
        if self.reads == 3:
            self.now += self.jump
        return self.now


def test_a_successful_run_leaves_a_complete_record_and_its_files(tmp_path):
    cluster = _FakeCluster(["Pending", "Running", "Succeeded"])

    record = _run(_spec("silver"), cluster, tmp_path)

    assert record["shuffle_partitions"] == 32  # 2x scale
    assert record["status"] == "ok" and record["wall_seconds"] == 10.0
    assert record["min_available_mb"] == 6_000 and record["max_executors_seen"] == 2
    assert record["summary"] == {"elapsed_seconds": 12.5, "tables": {"entity": 3}}
    assert record["has_event_log"] is True and record["executor_leftovers"] == []
    assert record["machine"]["running_pods"] == ["minio-1", "postgresql-0"]
    folder = tmp_path / "benchmark" / "runs" / "2x-silver-e2-r007"
    assert json.loads((folder / "record.json").read_text(encoding="utf-8")) == record
    assert (folder / "driver.log").is_file() and (folder / "eventlog").read_text(encoding="utf-8") == "log"
    assert cluster.deleted and cluster.applied["metadata"]["name"] == "bench-2x-silver-e2-r007"


def test_run_once_queries_executor_pods_scoped_to_this_runs_own_app_id(tmp_path):
    cluster = _FakeCluster(["Pending", "Running", "Succeeded"])

    _run(_spec("silver"), cluster, tmp_path)

    assert cluster.executor_pods_calls and all(app_id == "app-123" for app_id in cluster.executor_pods_calls)


def test_the_system_cpu_use_of_a_run_is_taken_from_two_proc_stat_readings():
    before = {"user": 100, "nice": 0, "system": 20, "idle": 800, "iowait": 50, "irq": 0, "softirq": 10, "steal": 20}
    after = {"user": 400, "nice": 0, "system": 60, "idle": 1_000, "iowait": 100, "irq": 0, "softirq": 20, "steal": 20}

    # 300 user + 40 system + 200 idle + 50 iowait + 10 softirq = 600 jiffies; busy = 600 - 200 - 50 = 350
    assert runner.cpu_utilization(before, after) == {"busy_pct": 58.3, "system_pct": 8.3, "iowait_pct": 8.3, "steal_pct": 0.0}
    assert runner.cpu_utilization(before, before) == {}
    assert set(runner.read_cpu_times()) == set(runner._CPU_FIELDS)


def test_a_record_carries_the_cpu_use_of_its_run_and_of_minio(tmp_path):
    record = _run(_spec(), _FakeCluster(["Pending", "Running", "Succeeded"]), tmp_path)

    assert record["cpu"]["busy_pct"] == 58.3
    assert record["minio_cpu_millicores"] == {"peak": 900, "mean": 473}


def test_minio_cpu_is_read_from_kubectl_top_in_millicores_or_cores():
    top = "minio-788465fc4c-s88fv   130m   300Mi\nminio-console-6dfb57b494-7rtkq   1m   12Mi\n"
    assert runner.Cluster(run=_Recorder([(0, top)])).minio_cpu_millicores() == 130
    assert runner.Cluster(run=_Recorder([(0, "minio-abc   2   1Gi\n")])).minio_cpu_millicores() == 2000
    assert runner.Cluster(run=_Recorder([(1, "")])).minio_cpu_millicores() is None


def test_each_job_starts_from_clean_outputs_and_never_touches_the_others(tmp_path):
    silver, gold, publish, digest = (_FakeCluster(["Succeeded"]) for _ in range(4))

    _run(_spec("silver"), silver, tmp_path)
    _run(_spec("gold"), gold, tmp_path)
    _run(_spec("publish"), publish, tmp_path)
    _run(_spec("digest_silver", role="digest"), digest, tmp_path)

    assert silver.calls == ["clear", "reset:lakehouse.bench_silver_2x"]
    assert gold.calls == ["clear", "reset:lakehouse.bench_gold_2x"]
    assert publish.calls == ["clear", "psql:DROP SCHEMA IF EXISTS bench_2x CASCADE"]
    assert digest.calls == ["clear"]


def test_a_failed_run_is_reported_not_raised(tmp_path):
    record = _run(_spec(), _FakeCluster(["Running", "Failed"]), tmp_path)

    assert record["status"] == "failed" and record["failure_reason"] is None


_REAL_OOM_LOG_EXCERPT_ALLOCATOR_GAVE_UP = (
    "26/09/22 17:00:28 ERROR TaskSchedulerImpl: Lost executor 1 on 10.42.0.254: \n"
    "The executor with id 1 exited with exit code 52(JVM OOM).\n\n\n"
    "26/09/22 17:18:55 ERROR ExecutorPodsAllocator: Max number of executor failures (3) reached\n"
    "26/09/22 17:18:55 INFO SparkContext: Invoking stop() from shutdown hook\n"
)
_REAL_OOM_LOG_EXCERPT_STAGE_GAVE_UP = (
    "26/09/22 18:44:41 ERROR TaskSchedulerImpl: Lost executor 5 on 10.42.0.9: \n"
    "The executor with id 5 exited with exit code 52(JVM OOM).\n\n\n"
    "org.apache.spark.shuffle.FetchFailedException\n"
    "Caused by: org.apache.spark.ExecutorDeadException: [INTERNAL_ERROR_NETWORK] "
    "The relative remote executor(Id: 4), which maintains the block data to fetch is dead.\n"
    ": org.apache.spark.SparkException: Job aborted due to stage failure: ShuffleMapStage 10 "
    "has failed the maximum allowable number of times: 4. Most recent failure reason:\n"
)


def test_an_executor_oom_is_diagnosed_from_either_real_log_signature():
    """Reproduces both real incidents: D23's `2x-silver-e1-r042` (the sole executor OOM'd four
    times until Spark's own executor allocator gave up) and D25's `2x-silver-e2-r045` (one of two
    executors OOM'd once, and the shuffle-fetch failures that followed exceeded the *stage's* own
    retry limit instead) -- the same root cause, two different ways Spark gives up afterward."""
    assert runner._diagnose_failure(_REAL_OOM_LOG_EXCERPT_ALLOCATOR_GAVE_UP) == "executor_oom"
    assert runner._diagnose_failure(_REAL_OOM_LOG_EXCERPT_STAGE_GAVE_UP) == "executor_oom"
    assert runner._diagnose_failure("some other stack trace, no OOM here") is None


_REAL_OOM_LOG_EXCERPT = _REAL_OOM_LOG_EXCERPT_ALLOCATOR_GAVE_UP


def test_a_failure_diagnosed_as_an_executor_oom_is_recorded_as_such(tmp_path):
    cluster = _FakeCluster(["Running", "Failed"])
    cluster.logs = lambda name: _REAL_OOM_LOG_EXCERPT

    record = _run(_spec(), cluster, tmp_path)

    assert record["status"] == "failed" and record["failure_reason"] == "executor_oom"


def test_a_host_suspend_does_not_falsely_time_out_a_healthy_run(tmp_path):
    """Reproduces the real incident of decision D22: run 1x-silver-e1-r011 was killed by a false
    timeout when the host slept mid-campaign and time.time() jumped forward on resume."""
    wall = _SuspendingClock(jump=62_000.0)  # the real incident: a ~17 h jump
    mono = _MonotonicClock()
    memory = iter([9_000, 7_500, 6_000, 8_000, 8_000])
    cluster = _FakeCluster(["Pending", "Running", "Running", "Succeeded"])

    record = runner.run_once(
        _spec(), cluster, tmp_path, clock=wall, monotonic=mono, sleep=mono.sleep,
        memory_probe=lambda: next(memory, 9_999), cpu_probe=_cpu_probe(),
    )

    assert record["status"] == "ok"  # not "timeout", despite the huge wall-clock jump
    assert record["active_seconds"] < 60  # the monotonic budget only saw the real poll time
    assert record["suspected_suspend_seconds"] == pytest.approx(62_000.0)
    assert record["wall_seconds"] == pytest.approx(62_000.0, abs=20)  # still reported, for humans


def test_a_run_that_never_ends_times_out_and_leftover_executors_are_reported(tmp_path):
    cluster = _FakeCluster(["Running"], leftovers=["exec-9"])

    record = _run(_spec(), cluster, tmp_path, timeout=20.0)

    assert record["status"] == "timeout" and record["wall_seconds"] >= 20.0
    assert record["executor_leftovers"] == ["exec-9"]


def test_a_missing_event_log_is_recorded(tmp_path):
    assert _run(_spec(), _FakeCluster(["Succeeded"], event_log=False), tmp_path)["has_event_log"] is False


class _Recorder:
    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []

    def __call__(self, command, **kwargs):
        self.calls.append((command, kwargs))
        returncode, stdout = self.replies.pop(0)
        return type("Completed", (), {"returncode": returncode, "stdout": stdout, "stderr": "boom"})()


def test_a_kubectl_failure_raises_with_the_error_text():
    with pytest.raises(RuntimeError, match="boom"):
        runner.Cluster(run=_Recorder([(1, "")])).kubectl("get", "pods")


def test_the_postgres_password_goes_over_stdin_and_never_onto_a_command_line():
    secret = base64.b64encode(b"s3cret-pw").decode()
    recorder = _Recorder([(0, secret), (0, "1|2|3\n")])

    output = runner.Cluster(run=recorder).psql("select 1")

    assert output == "1|2|3\n"
    exec_command, exec_kwargs = recorder.calls[1]
    assert exec_kwargs["input"] == "s3cret-pw\n"
    assert not any("s3cret-pw" in part for part in exec_command) and exec_command[-1] == "select 1"


def test_app_id_reads_the_driver_pods_spark_app_selector_label():
    recorder = _Recorder([(0, "spark-a1b2c3\n")])
    assert runner.Cluster(run=recorder).app_id("bench-2x-silver-e2-r001") == "spark-a1b2c3"
    assert "spark-app-selector" in recorder.calls[0][0][-1]

    assert runner.Cluster(run=_Recorder([(0, "")])).app_id("bench-2x-silver-e2-r001") is None  # driver not registered yet


def test_executor_pods_is_scoped_to_the_given_app_id_and_falls_back_to_every_executor_without_one():
    """Reproduces the real incident (issue #101, Task 8): without scoping by app id, a pod
    orphaned by an earlier, unrelated run (`4x-silver-e2-r073`'s own OOM) was picked up as the
    "leftover" of 9 later, unrelated, genuinely successful `4x-publish` runs."""
    recorder = _Recorder([(0, "exec-1\nexec-2\n"), (0, "exec-1\nexec-2\nexec-3\n")])

    scoped = runner.Cluster(run=recorder).executor_pods("spark-a1b2c3")
    unscoped = runner.Cluster(run=recorder).executor_pods()

    assert scoped == ["exec-1", "exec-2"] and "spark-app-selector=spark-a1b2c3,spark-role=executor" in recorder.calls[0][0]
    assert unscoped == ["exec-1", "exec-2", "exec-3"] and "spark-role=executor" in recorder.calls[1][0] and "spark-app-selector" not in recorder.calls[1][0][-1]


# --------------------------------------------------------------------------- campaign


def _measured(plan, scale, job):
    return [p for p in plan if p.spec.scale.name == scale and p.spec.job == job and p.spec.role == "measured"]


def test_the_default_plan_has_36_runs_per_scale_and_108_in_total():
    plan = campaign.build_plan(["1x", "2x", "4x"])

    assert len(plan) == 108
    assert [p.spec.sequence for p in plan] == list(range(1, 109))
    for scale in ("1x", "2x", "4x"):
        assert sum(1 for p in plan if p.spec.scale.name == scale) == 36


def test_each_scale_and_job_starts_with_a_discarded_warm_up_and_jobs_follow_their_dependencies():
    plan = campaign.build_plan(["1x", "2x"])
    order = []
    for item in plan:
        key = (item.spec.scale.name, item.spec.job.replace("digest_", ""))
        if not order or order[-1] != key:
            order.append(key)
    assert order == [("1x", "silver"), ("1x", "gold"), ("1x", "publish"), ("2x", "silver"), ("2x", "gold"), ("2x", "publish")]
    first_of_each = {}
    for item in plan:
        first_of_each.setdefault((item.spec.scale.name, item.spec.job), item)
    for (scale, job), item in first_of_each.items():
        if job in {"silver", "gold", "publish"}:
            assert item.spec.role == "warmup" and item.spec.executors == campaign.WARMUP_EXECUTORS


def test_every_executor_count_is_measured_three_times_in_randomized_blocks():
    plan = campaign.build_plan(["1x"])

    for job in ("silver", "gold", "publish"):
        counts = [p.spec.executors for p in _measured(plan, "1x", job)]
        assert sorted(counts) == [1, 1, 1, 2, 2, 2, 4, 4, 4]
        blocks = [counts[i : i + 3] for i in range(0, 9, 3)]
        assert all(sorted(block) == [1, 2, 4] for block in blocks)


def test_the_first_measured_run_of_each_configuration_is_followed_by_a_digest_of_its_own_output():
    plan = campaign.build_plan(["1x"])

    for job, digest_job in (("silver", "digest_silver"), ("gold", "digest_gold")):
        digests = [(i, p.spec) for i, p in enumerate(plan) if p.spec.job == digest_job]
        assert sorted(spec.of_executors for _, spec in digests) == [1, 2, 4]
        for index, spec in digests:
            previous = plan[index - 1].spec
            assert previous.job == job and previous.role == "measured" and previous.executors == spec.of_executors
            assert spec.role == "digest" and spec.executors == runner.DIGEST_EXECUTORS
    assert sum(1 for p in _measured(plan, "1x", "publish") if p.pg_digest) == 3
    assert not any(p.pg_digest for p in plan if p.spec.job != "publish")


def test_the_plan_is_deterministic_and_the_seed_changes_the_order():
    same = [p.spec.run_id for p in campaign.build_plan(["1x", "2x", "4x"], seed=5)]

    assert same == [p.spec.run_id for p in campaign.build_plan(["1x", "2x", "4x"], seed=5)]
    assert same != [p.spec.run_id for p in campaign.build_plan(["1x", "2x", "4x"], seed=6)]


def test_a_reduced_campaign_keeps_the_same_rules():
    plan = campaign.build_plan(["1x"], executors=[1, 2, 3, 4], repetitions=2, jobs=["silver"])

    assert [p.spec.role for p in plan].count("measured") == 8 and plan[0].spec.role == "warmup"


def test_a_pilot_plan_never_shares_run_ids_with_the_campaign_and_is_never_counted_as_measured():
    campaign_ids = {p.spec.run_id for p in campaign.build_plan(["1x", "2x", "4x"])}
    pilot = campaign.build_plan(["1x"], executors=[1, 4], repetitions=1, first_sequence=901, measured_role="pilot")

    assert not campaign_ids & {p.spec.run_id for p in pilot}
    assert pilot[0].spec.sequence == 901 and pilot[0].spec.role == "warmup"
    assert {p.spec.role for p in pilot} == {"warmup", "pilot", "digest"}
    records = [{"run_id": p.spec.run_id, "scale": "1x", "job": p.spec.job, "executors": p.spec.executors, "role": p.spec.role, "status": "ok"} for p in pilot]
    assert report.points(records) == {}


def test_parse_pg_digest_reads_table_count_hash_lines():
    assert campaign.parse_pg_digest("a|3|123\nb|0|0\nnoise\n") == {"a": ["3", "123"], "b": ["0", "0"]}


class _CampaignCluster:
    def psql(self, sql):
        return "dim_researcher|5|99\ngold_run|1|0\n"


def _ok_record(spec, tmp_path):
    record = {"run_id": spec.run_id, "status": "ok", "job": spec.job}
    folder = tmp_path / "benchmark" / "runs" / spec.run_id
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "record.json").write_text(json.dumps(record), encoding="utf-8")
    return record


def test_execute_runs_the_plan_in_order_skips_finished_runs_and_records_the_pg_digest(tmp_path):
    plan = campaign.build_plan(["1x"], repetitions=1, jobs=["publish"])
    _ok_record(plan[0].spec, tmp_path)  # the warm-up is already done
    executed = []

    def fake_run(spec, cluster, data_dir):
        executed.append(spec.run_id)
        return _ok_record(spec, data_dir)

    records = campaign.execute(plan, _CampaignCluster(), tmp_path, settle_seconds=0, sleep=lambda s: None, run=fake_run)

    assert executed == [p.spec.run_id for p in plan[1:]] and len(records) == len(plan) - 1
    digested = [json.loads((tmp_path / "benchmark" / "runs" / p.spec.run_id / "record.json").read_text(encoding="utf-8")) for p in plan if p.pg_digest]
    assert len(digested) == 3 and all(d["pg_digest"]["dim_researcher"] == ["5", "99"] for d in digested)


def _write_record(tmp_path, spec, **overrides):
    record = {"run_id": spec.run_id, "scale": spec.scale.name, "job": spec.job, "executors": spec.executors, "role": spec.role, "status": "failed", "failure_reason": None}
    record.update(overrides)
    folder = tmp_path / "benchmark" / "runs" / spec.run_id
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "record.json").write_text(json.dumps(record), encoding="utf-8")
    return record


def test_a_skipped_record_is_not_counted_as_evidence_for_the_next_repeat(tmp_path):
    """Reproduces the real incident: skipping `4x-silver-e2-r081` wrote it a fresh "skipped"
    record (a different failure_reason string than "executor_oom"), which then broke the
    all-executor_oom check for the very next repeat, `r083`, and it ran for real instead of
    being skipped too."""
    scale = data.scale_for("4x")
    warmup = campaign.RunSpec(scale, "silver", 2, 73, "warmup")
    first = campaign.RunSpec(scale, "silver", 2, 76)
    second = campaign.RunSpec(scale, "silver", 2, 81)
    third = campaign.RunSpec(scale, "silver", 2, 83)
    _write_record(tmp_path, warmup, status="failed", failure_reason="executor_oom")
    _write_record(tmp_path, first, status="failed", failure_reason="executor_oom")
    assert campaign._confirmed_deterministic_oom(tmp_path, second) is True

    campaign._skip_confirmed_oom(second, tmp_path, 2)  # writes second's own fresh "skipped" record

    assert campaign._confirmed_deterministic_oom(tmp_path, third) is True  # must still see 2 real OOMs, not the skip


def test_last_write_ok_reads_the_chronologically_latest_non_skipped_attempt(tmp_path):
    scale = data.scale_for("2x")
    assert campaign._last_write_ok(tmp_path, "2x", "silver") is None  # never attempted

    _write_record(tmp_path, campaign.RunSpec(scale, "silver", 2, 1), status="ok", submitted_at="2026-09-23T10:00:00Z")
    _write_record(tmp_path, campaign.RunSpec(scale, "silver", 1, 2), status="failed", failure_reason="executor_oom", submitted_at="2026-09-23T10:05:00Z")
    assert campaign._last_write_ok(tmp_path, "2x", "silver") is False  # r2 started later, and it failed

    _write_record(tmp_path, campaign.RunSpec(scale, "silver", 1, 3), status="skipped", failure_reason="executor_oom_confirmed", submitted_at="2026-09-23T10:10:00Z")
    assert campaign._last_write_ok(tmp_path, "2x", "silver") is False  # a skip never touches the namespace; r2 is still the latest real attempt

    _write_record(tmp_path, campaign.RunSpec(scale, "silver", 4, 4), status="ok", submitted_at="2026-09-23T10:15:00Z")
    assert campaign._last_write_ok(tmp_path, "2x", "silver") is True  # r4 started latest, and it succeeded


def test_last_write_ok_uses_real_start_time_not_the_plan_sequence_number(tmp_path):
    """Reproduces the real incident (D28): a resumed campaign retries a low-sequence run id
    (`4x-silver-e2-r073`, a warm-up) *after* a higher-sequence one (`r085`) already succeeded --
    the retry starts later in real time and resets the namespace again, so it is what matters,
    not which one has the larger sequence number."""
    scale = data.scale_for("4x")
    _write_record(tmp_path, campaign.RunSpec(scale, "silver", 4, 85), status="ok", submitted_at="2026-09-23T18:00:00Z")
    assert campaign._last_write_ok(tmp_path, "4x", "silver") is True

    _write_record(tmp_path, campaign.RunSpec(scale, "silver", 2, 73, "warmup"), status="failed", failure_reason="executor_oom", submitted_at="2026-09-23T21:51:00Z")
    assert campaign._last_write_ok(tmp_path, "4x", "silver") is False  # the retry of r073 ran later and left it empty


def test_repair_reruns_at_the_safest_configuration_and_raises_if_it_also_fails(tmp_path):
    scale = data.scale_for("2x")
    calls = []

    def fake_run_ok(spec, cluster, data_dir):
        calls.append(spec)
        return {"status": "ok", "run_id": spec.run_id}

    record = campaign._repair("silver", scale, 50, _CampaignCluster(), tmp_path, fake_run_ok)

    assert record["status"] == "ok"
    assert calls[0].job == "silver" and calls[0].executors == campaign.MAX_EXECUTORS and calls[0].role == "repair"
    assert calls[0].sequence == campaign.REPAIR_SEQUENCE_OFFSET + 50

    def fake_run_fails(spec, cluster, data_dir):
        return {"status": "failed", "run_id": spec.run_id, "failure_reason": None}

    with pytest.raises(campaign.CampaignError, match="repair run"):
        campaign._repair("silver", scale, 50, _CampaignCluster(), tmp_path, fake_run_fails)


def test_execute_repairs_silver_before_gold_when_the_last_silver_attempt_failed(tmp_path):
    """Reproduces the real incident: 2x-silver-e1-r049 OOM'd last, leaving no silver output, so
    2x-gold-e2-r050 failed reading an empty table -- `silver_to_gold` was not written to notice."""
    plan = campaign.build_plan(["2x"], executors=[1], repetitions=1, jobs=["gold"])
    _write_record(tmp_path, campaign.RunSpec(plan[0].spec.scale, "silver", 1, 49), status="failed", failure_reason="executor_oom")
    ran = []

    def fake_run(spec, cluster, data_dir):
        ran.append((spec.job, spec.executors, spec.role))
        return _write_record(data_dir, spec, status="ok")

    campaign.execute(plan, _CampaignCluster(), tmp_path, settle_seconds=0, sleep=lambda s: None, run=fake_run)

    assert ran[0] == ("silver", campaign.MAX_EXECUTORS, "repair")  # repaired first
    assert ran[1][0] == "gold"  # then the plan's own warm-up runs, reading a now-valid silver


def test_execute_does_not_repair_when_the_last_silver_attempt_already_succeeded(tmp_path):
    plan = campaign.build_plan(["2x"], executors=[1], repetitions=1, jobs=["gold"])
    _write_record(tmp_path, campaign.RunSpec(plan[0].spec.scale, "silver", 2, 40), status="ok")
    ran = []

    def fake_run(spec, cluster, data_dir):
        ran.append(spec.role)
        return _write_record(data_dir, spec, status="ok")

    campaign.execute(plan, _CampaignCluster(), tmp_path, settle_seconds=0, sleep=lambda s: None, run=fake_run)

    assert "repair" not in ran


def test_a_configuration_is_a_confirmed_deterministic_oom_only_with_zero_successes(tmp_path):
    two_oom = _spec("silver", factor=2, executors=1, sequence=1)
    _write_record(tmp_path, two_oom, status="failed", failure_reason="executor_oom")
    assert campaign._confirmed_deterministic_oom(tmp_path, campaign.RunSpec(two_oom.scale, "silver", 1, 2)) is False  # only 1 attempt so far
    _write_record(tmp_path, campaign.RunSpec(two_oom.scale, "silver", 1, 2), status="failed", failure_reason="executor_oom")
    assert campaign._confirmed_deterministic_oom(tmp_path, campaign.RunSpec(two_oom.scale, "silver", 1, 3)) is True  # 2/2 failed, real incident (2x-silver-e1)

    mixed = campaign.RunSpec(two_oom.scale, "silver", 2, 10)
    _write_record(tmp_path, campaign.RunSpec(two_oom.scale, "silver", 2, 8), status="ok")
    _write_record(tmp_path, campaign.RunSpec(two_oom.scale, "silver", 2, 9), status="failed", failure_reason="executor_oom")
    assert campaign._confirmed_deterministic_oom(tmp_path, mixed) is False  # 1 success survives: real incident (2x-silver-e2), keep retrying

    unrelated_failure = campaign.RunSpec(two_oom.scale, "gold", 1, 20)
    _write_record(tmp_path, campaign.RunSpec(two_oom.scale, "gold", 1, 18), status="failed", failure_reason=None)
    _write_record(tmp_path, campaign.RunSpec(two_oom.scale, "gold", 1, 19), status="failed", failure_reason=None)
    assert campaign._confirmed_deterministic_oom(tmp_path, unrelated_failure) is False  # failed for an unrelated reason, not OOM


def test_a_retry_of_the_same_run_id_is_archived_before_being_overwritten_so_no_attempt_is_lost(tmp_path):
    """Reproduces the real gap found while fixing D25: `2x-silver-e1-r042` was retried across
    three separate campaign resumes under the *same* run id, each overwriting the last one's
    record.json, so a naive count of `record.json` files alone saw only 1 attempt, not 3."""
    spec = _spec("silver", factor=2, executors=1, sequence=42)
    record_file = tmp_path / "benchmark" / "runs" / spec.run_id / "record.json"
    _write_record(tmp_path, spec, status="failed", failure_reason="executor_oom")  # attempt 1

    campaign._archive_attempt(record_file)  # about to retry the same run id: archive it first
    _write_record(tmp_path, spec, status="failed", failure_reason="executor_oom")  # attempt 2 overwrites record.json

    outcomes = campaign._attempt_outcomes(tmp_path, spec)
    assert outcomes == [(False, "executor_oom"), (False, "executor_oom")]
    assert campaign._confirmed_deterministic_oom(tmp_path, spec) is True
    assert (record_file.parent / "record.attempt1.json").is_file()


def test_archiving_a_run_id_with_no_prior_record_does_nothing(tmp_path):
    never_run = tmp_path / "benchmark" / "runs" / "2x-silver-e1-r999" / "record.json"
    campaign._archive_attempt(never_run)  # must not raise
    assert not never_run.parent.exists()


def test_execute_skips_further_repeats_of_a_confirmed_deterministic_oom_without_running_them(tmp_path):
    # 5 items: warm-up (e2), measured #1 (e1), digest (e2, of e1), measured #2 (e1), measured #3 (e1)
    plan = campaign.build_plan(["2x"], executors=[1], repetitions=3, jobs=["silver"])
    ran = []

    def fake_run(spec, cluster, data_dir):
        ran.append(spec.run_id)
        oom = spec.job == "silver" and spec.executors == 1  # only the e1 measured/warm-up config OOMs
        return _write_record(data_dir, spec, status="failed" if oom else "ok", failure_reason="executor_oom" if oom else None)

    records = campaign.execute(plan, _CampaignCluster(), tmp_path, settle_seconds=0, sleep=lambda s: None, run=fake_run)

    # measured #1 and #2 both run for real (2/2 confirms the ceiling); #3 is skipped without running
    assert ran == [p.spec.run_id for p in (plan[0], plan[1], plan[2], plan[3])]
    skipped = [r for r in records if r["status"] == "skipped"]
    assert len(skipped) == 1 and skipped[0]["failure_reason"] == "executor_oom_confirmed"
    assert skipped[0]["run_id"] == plan[4].spec.run_id  # the 3rd measured attempt


def test_execute_never_skips_a_configuration_with_any_success(tmp_path):
    plan = campaign.build_plan(["2x"], executors=[2], repetitions=3, jobs=["silver"])
    _write_record(tmp_path, plan[1].spec, status="ok")
    _write_record(tmp_path, plan[2].spec, status="failed", failure_reason="executor_oom")
    ran = []

    def fake_run(spec, cluster, data_dir):
        ran.append(spec.run_id)
        return _write_record(data_dir, spec, status="ok")

    records = campaign.execute(plan, _CampaignCluster(), tmp_path, settle_seconds=0, sleep=lambda s: None, run=fake_run)

    assert not any(r["status"] == "skipped" for r in records)
    assert plan[3].spec.run_id in ran  # the 3rd measured attempt still runs: 2x-silver-e2 has a success on record


def test_execute_continues_past_a_diagnosed_executor_oom_but_still_stops_at_other_failures(tmp_path):
    plan = campaign.build_plan(["1x"], executors=[1, 2], repetitions=1, jobs=["silver"])
    executed = []

    def fake_run(spec, cluster, data_dir):
        executed.append(spec.run_id)
        if spec.executors == 1 and spec.role == "measured":
            return _ok_record(spec, data_dir) | {"status": "failed", "failure_reason": "executor_oom"}
        return _ok_record(spec, data_dir)

    records = campaign.execute(plan, _CampaignCluster(), tmp_path, settle_seconds=0, sleep=lambda s: None, run=fake_run)

    assert executed == [p.spec.run_id for p in plan]  # the whole plan ran, nothing was skipped by the OOM
    assert any(r["status"] == "failed" and r["failure_reason"] == "executor_oom" for r in records)


def test_execute_stops_at_the_first_failed_run(tmp_path):
    plan = campaign.build_plan(["1x"], repetitions=1, jobs=["gold"])
    executed = []

    def fake_run(spec, cluster, data_dir):
        executed.append(spec.run_id)
        return {"run_id": spec.run_id, "status": "failed" if len(executed) == 2 else "ok"}

    with pytest.raises(campaign.CampaignError, match="failed"):
        campaign.execute(plan, _CampaignCluster(), tmp_path, settle_seconds=0, sleep=lambda s: None, run=fake_run)
    assert len(executed) == 2


# --------------------------------------------------------------------------- report


def test_karp_flatt_and_the_size_up_slope_match_hand_computed_values():
    assert report.karp_flatt(2.0, 4) == pytest.approx(1 / 3)
    assert report.karp_flatt(4.0, 4) == pytest.approx(0.0)
    assert report.karp_flatt(1.0, 1) is None and report.karp_flatt(0.0, 2) is None
    assert report.loglog_slope([1, 2, 4], [10, 20, 40]) == pytest.approx(1.0)
    assert report.loglog_slope([1, 2, 4], [10, 10, 10]) == pytest.approx(0.0)
    assert report.loglog_slope([1], [10]) is None and report.loglog_slope([2, 2], [1, 3]) is None


def _record(scale, job, executors, seconds, *, role="measured", status="ok", registered=None, leftovers=(), run=0):
    return {
        "run_id": f"{scale}-{job}-e{executors}-r{run}",
        "scale": scale,
        "job": job,
        "executors": executors,
        "role": role,
        "status": status,
        "executor_leftovers": list(leftovers),
        "min_available_mb": 5_000,
        "cpu": {"busy_pct": 40.0, "iowait_pct": 2.0},
        "minio_cpu_millicores": {"peak": 500, "mean": 300},
        "metrics": {
            "app_seconds": seconds,
            "compute_seconds": seconds - 8,
            "startup_seconds": 6.0,
            "gap_seconds": 10.0,
            "executors_added": executors if registered is None else registered,
            "jobs_failed": 0,
            "totals": {"failed_tasks": 0, "jvm_gc_seconds": 1.0, "executor_run_seconds": seconds * executors, "input_bytes": 4e9, "shuffle_write_bytes": 1e8, "disk_spilled_bytes": 0, "memory_spilled_bytes": 0},
        },
    }


def _synthetic_records():
    times = {("1x", 1): (100, 102, 98), ("1x", 2): (52, 54, 50), ("1x", 4): (30, 31, 29)}
    records = [
        _record(scale, "silver", n, t, run=i)
        for (scale, n), values in times.items()
        for i, t in enumerate(values)
    ]
    records += [_record("2x", "silver", 1, t, run=i) for i, t in enumerate((200, 204, 196))]
    return records


def test_points_and_derived_metrics_are_computed_from_the_medians():
    derived = report.derive(report.points(_synthetic_records()))
    rows = {(r["scale"], r["executors"]): r for r in derived["points"] if r["job"] == "silver"}

    assert rows[("1x", 1)]["median"] == 100 and rows[("1x", 1)]["spread"] == pytest.approx(0.04)
    assert rows[("1x", 2)]["speedup"] == pytest.approx(100 / 52) and rows[("1x", 2)]["efficiency"] == pytest.approx(100 / 52 / 2)
    assert rows[("1x", 2)]["karp_flatt"] == pytest.approx((52 / 100 - 1 / 2) / (1 - 1 / 2))
    assert rows[("1x", 4)]["speedup"] == pytest.approx(100 / 30)
    assert rows[("1x", 1)]["karp_flatt"] is None and not rows[("1x", 1)]["flagged"]
    sizeup = [s for s in derived["sizeup"] if s["job"] == "silver" and s["executors"] == 1]
    assert sizeup and sizeup[0]["exponent"] == pytest.approx(1.0) and sizeup[0]["scales"] == [1, 2]


def test_a_point_with_more_than_ten_percent_spread_is_flagged():
    records = [_record("1x", "gold", 1, t, run=i) for i, t in enumerate((100, 120, 100))]

    rows = report.derive(report.points(records))["points"]

    assert rows[0]["flagged"] is True and rows[0]["spread"] == pytest.approx(0.20)


def test_runs_that_cannot_be_trusted_are_excluded_with_the_reason():
    records = [
        _record("1x", "silver", 4, 30, run=1),
        _record("1x", "silver", 4, 31, run=2, registered=3),
        _record("1x", "silver", 4, 32, run=3, status="failed"),
        _record("1x", "silver", 4, 33, run=4, leftovers=["exec-1"]),
        _record("1x", "silver", 4, 500, run=5, role="warmup"),
    ]

    point = report.points(records)[("1x", "silver", 4)]

    assert point["runs"] == 1 and point["median"] == 30
    reasons = " ".join(point["excluded"])
    assert "3 executors registered, 4 requested" in reasons and "status failed" in reasons and "left behind" in reasons
    assert "500" not in json.dumps(point["app_seconds"])  # the warm-up never counts


def test_a_task_retried_by_spark_is_counted_but_does_not_invalidate_the_run():
    record = _record("4x", "silver", 4, 500)
    record["metrics"]["totals"]["failed_tasks"] = 3

    assert report.invalid_reason(record) is None
    assert report.points([record])[("4x", "silver", 4)]["task_retries"] == 3
    record["metrics"]["jobs_failed"] = 1
    assert report.invalid_reason(record) == "a job failed"


def test_a_run_that_lost_an_executor_is_excluded_with_the_reason_even_if_it_finished():
    record = _record("4x", "silver", 4, 500)
    record["metrics"].update(executors_removed=1, executor_removal_reasons=["Pod exec-3 exited with 137 (OOMKilled)"])

    assert "1 executor(s) lost during the run: Pod exec-3 exited with 137" in report.invalid_reason(record)


def test_a_run_without_a_readable_event_log_is_invalid():
    record = _record("1x", "silver", 1, 10)
    record["metrics"] = None

    assert report.invalid_reason(record) == "no readable event log"


def _digest_record(scale, kind, of_executors, digests, status="ok"):
    return {"scale": scale, "job": f"digest_{kind}", "executors": 2, "executors_of": of_executors, "status": status, "summary": {"digests": digests}}


def test_correctness_requires_identical_digests_across_executor_counts():
    same = {"entity": {"rows": 3, "digest": "9", "exists": True}}
    records = [_digest_record("1x", "silver", n, same) for n in (1, 2, 4)]
    records += [_digest_record("1x", "gold", 1, same), _digest_record("1x", "gold", 2, {"entity": {"rows": 3, "digest": "8", "exists": True}})]
    records += [{"scale": "1x", "job": "publish", "executors": n, "status": "ok", "pg_digest": {"t": ["3", "7"]}} for n in (1, 2)]

    checks = report.correctness(records)

    assert checks[("1x", "silver")]["equal"] and checks[("1x", "silver")]["configurations"] == [1, 2, 4]
    assert checks[("1x", "silver")]["consistent"] is True and checks[("1x", "silver")]["empty_executors"] == []
    assert not checks[("1x", "gold")]["equal"] and checks[("1x", "gold")]["consistent"] is False
    assert checks[("1x", "publish")]["equal"] and checks[("1x", "publish")]["consistent"] is True
    assert report.correctness([_digest_record("1x", "silver", 1, same, status="failed")]) == {}


def test_correctness_treats_a_confirmed_oom_empty_digest_as_expected_not_a_mismatch():
    """Reproduces the real end-of-campaign result: 1 executor never wrote anything at 2x/4x silver
    (decision D25's confirmed deterministic OOM), while 2 and 4 executors agree byte-for-byte."""
    empty = {"entity": {"rows": 0, "digest": "0", "exists": False}, "affiliation": {"rows": 0, "digest": "0", "exists": False}}
    same = {"entity": {"rows": 58232, "digest": "1191198177217604302353", "exists": True}, "affiliation": {"rows": 198156, "digest": "-4602243799335964254422", "exists": True}}
    records = [_digest_record("2x", "silver", 1, empty), _digest_record("2x", "silver", 2, same), _digest_record("2x", "silver", 4, same)]

    result = report.correctness(records)[("2x", "silver")]

    assert result["equal"] is False  # the blunt whole-set comparison still flags it
    assert result["consistent"] is True  # but the runs that actually produced output agree
    assert result["empty_executors"] == [1]


def test_correctness_consistent_is_undefined_with_fewer_than_two_real_outputs():
    empty = {"entity": {"rows": 0, "digest": "0", "exists": False}}
    records = [_digest_record("4x", "silver", 1, empty), _digest_record("4x", "silver", 2, empty), _digest_record("4x", "silver", 4, {"entity": {"rows": 9, "digest": "7", "exists": True}})]

    result = report.correctness(records)[("4x", "silver")]

    assert result["empty_executors"] == [1, 2] and result["consistent"] is None


def test_the_markdown_tables_show_the_points_the_flags_and_the_correctness_verdicts():
    records = _synthetic_records() + [_record("1x", "gold", 1, t, run=i) for i, t in enumerate((100, 130, 100))]
    checks = report.correctness(
        [
            _digest_record("1x", "silver", 1, {"a": {"rows": 1, "digest": "x", "exists": True}}),
            _digest_record("1x", "silver", 2, {"a": {"rows": 2, "digest": "y", "exists": True}}),
        ]
    )

    text = report.render_markdown(report.derive(report.points(records)), checks)

    assert "## bronze_to_silver" in text and "## silver_to_gold" in text and "## publish_gold_to_postgres" not in text
    assert "| 1x | 2 | 3 | 52.0 | 50.0-54.0 |" in text and "1.92" in text
    assert "(!)" in text  # the gold point with a 30% spread
    assert "Size-up exponent" in text and "| 1x | silver | 1, 2 | - | **NO** |" in text


def test_write_outputs_reads_the_records_and_event_logs_and_writes_the_three_files(tmp_path):
    runs = tmp_path / "runs"
    for sequence in range(1, 4):
        folder = runs / f"1x-silver-e2-r00{sequence}"
        folder.mkdir(parents=True)
        shutil.copyfile(FIXTURE, folder / "eventlog")
        record = _record("1x", "silver", 2, 0, run=sequence)
        record.pop("metrics")
        record.update(run_id=folder.name, has_event_log=True)
        (folder / "record.json").write_text(json.dumps(record), encoding="utf-8")

    summary = report.write_outputs(runs, tmp_path / "out")

    assert summary == {"records": 3, "points": 1, "correctness_ok": True}
    results = json.loads((tmp_path / "out" / "results.json").read_text(encoding="utf-8"))
    assert results["points"][0]["median"] == 261.558 and results["points"][0]["runs"] == 3
    assert (tmp_path / "out" / "results.csv").read_text(encoding="utf-8").splitlines()[0].startswith("scale,job,executors,runs,median")
    assert "bronze_to_silver" in (tmp_path / "out" / "results.md").read_text(encoding="utf-8")


def test_charts_are_written_one_per_job(tmp_path):
    pytest.importorskip("matplotlib")
    derived = report.derive(report.points(_synthetic_records()))

    written = report.draw_charts(derived, tmp_path)

    assert [path.name for path in written] == ["benchmark_silver.png"] and written[0].stat().st_size > 1_000
