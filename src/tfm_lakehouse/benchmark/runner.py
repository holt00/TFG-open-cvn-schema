"""Run one measured Spark job of the benchmark on the cluster (issue #101).

The pod this module creates is the Spark driver (``--deploy-mode client``) and runs
``spark-submit`` through the image's ``/opt/entrypoint.sh``, exactly as the pods of the
``transform_publish`` DAG do (``dags/transform_publish.py``); a test compares the flags the two
share. Only what the benchmark needs differs: the outputs go to ``bench_*`` namespaces and a
PostgreSQL schema of their own, the executor count is the independent variable, the job waits for
all of its executors before scheduling, and the Spark event log is written to MinIO.
"""

from __future__ import annotations

import argparse
import base64
import json
import logging
import os
import subprocess
import sys
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from tfm_lakehouse.benchmark.data import EVENTS_BUCKET, Scale, scale_for
from tfm_lakehouse.gold import schemas as gold_schemas

logger = logging.getLogger(__name__)

NAMESPACE = "tfm-lakehouse"
SPARK_IMAGE = "tfm-lakehouse/spark-py:3.5.9-iceberg1.11.0-gold"
# Path of the repository checkout on the machine that runs k3s (hostPath), as in the DAGs.
REPO_ROOT = os.environ.get("BENCH_REPO_ROOT", str(Path(__file__).resolve().parents[3]))
JOBS = "/repo/src/tfm_lakehouse/spark_jobs"
EVENT_LOG_DIR = f"s3a://{EVENTS_BUCKET}/logs"
REGISTRATION_WAIT = "300s"

JOB_SILVER = "silver"
JOB_GOLD = "gold"
JOB_PUBLISH = "publish"
DIGEST_SILVER = "digest_silver"
DIGEST_GOLD = "digest_gold"
MEASURED_JOBS = (JOB_SILVER, JOB_GOLD, JOB_PUBLISH)

JOB_SCRIPTS = {
    JOB_SILVER: "bronze_to_silver.py",
    JOB_GOLD: "silver_to_gold.py",
    JOB_PUBLISH: "publish_gold_to_postgres.py",
    DIGEST_SILVER: "table_digest.py",
    DIGEST_GOLD: "table_digest.py",
}
# Executor memory overhead per job, as `transform_publish` sizes them (issues #98 and #99).
JOB_OVERHEAD = {JOB_SILVER: "1g", JOB_GOLD: "512m", JOB_PUBLISH: "512m", DIGEST_SILVER: "512m", DIGEST_GOLD: "512m"}
EXECUTOR_MEMORY = "1g"
DRIVER_MEMORY = "1g"
DIGEST_EXECUTORS = 2
# Shuffle partitions of the 1x scale; the other scales multiply it so each partition holds about the
# same amount of data (issue #98 advised raising it for volume, and a fixed 16 at 4x lost executors).
BASE_SHUFFLE_PARTITIONS = 16
SILVER_TABLES = ["person_record", "affiliation", "publication", "rejected", "entity_link", "entity"]

RUNS_SUBDIR = Path("benchmark") / "runs"


@dataclass(frozen=True)
class RunSpec:
    """One Spark job launch: which job, on which scale, with how many executors.

    Args:
        scale: Data scale (decides the bronze bucket and the output namespaces).
        job: One of ``silver``, ``gold``, ``publish``, ``digest_silver``, ``digest_gold``.
        executors: Executor pods requested (one core each).
        sequence: Position of the run in the campaign; makes the run id unique.
        role: ``measured``, ``warmup`` (first run of a scale and job, discarded), ``pilot`` or ``digest``.
        shuffle_partitions: ``spark.sql.shuffle.partitions`` of the job; by default 16 times the scale
            factor, so the data per partition does not grow with the scale.
        of_executors: For a digest run, the executor count of the measured run whose tables it digests.
    """

    scale: Scale
    job: str
    executors: int
    sequence: int = 0
    role: str = "measured"
    shuffle_partitions: int | None = None
    of_executors: int | None = None

    @property
    def effective_shuffle_partitions(self) -> int:
        return self.shuffle_partitions or BASE_SHUFFLE_PARTITIONS * self.scale.factor

    @property
    def run_id(self) -> str:
        of = f"-of{self.of_executors}" if self.of_executors else ""
        return f"{self.scale.name}-{self.job.replace('_', '-')}-e{self.executors}{of}-r{self.sequence:03d}"

    @property
    def pod_name(self) -> str:
        return f"bench-{self.run_id}"

    @property
    def summary_path(self) -> str:
        return f"/repo/data/{RUNS_SUBDIR.as_posix()}/{self.run_id}/summary.json"


def job_args(spec: RunSpec) -> list[str]:
    """Arguments of the job script (the ground-truth manifest is never passed: decision D9)."""
    scale = spec.scale
    if spec.job == JOB_SILVER:
        return [
            f"--bronze-root {scale.bronze_root}",
            f"--namespace {scale.silver_namespace}",
            f"--shuffle-partitions {spec.effective_shuffle_partitions}",
            f"--summary-file {spec.summary_path}",
        ]
    if spec.job == JOB_GOLD:
        return [
            f"--silver-namespace {scale.silver_namespace}",
            f"--gold-namespace {scale.gold_namespace}",
            f"--run-id {spec.run_id}",
            f"--shuffle-partitions {spec.effective_shuffle_partitions}",
            f"--summary-file {spec.summary_path}",
        ]
    if spec.job == JOB_PUBLISH:
        return [
            f"--gold-namespace {scale.gold_namespace}",
            f"--pg-schema {scale.pg_schema}",
            f"--summary-file {spec.summary_path}",
        ]
    if spec.job == DIGEST_SILVER:
        return [f"--namespace {scale.silver_namespace}", "--tables " + " ".join(SILVER_TABLES), f"--summary-file {spec.summary_path}"]
    if spec.job == DIGEST_GOLD:
        tables = " ".join(gold_schemas.TABLES)
        return [
            f"--namespace {scale.gold_namespace}",
            f"--tables {tables}",
            f"--rows-only {gold_schemas.GOLD_RUN}",
            f"--summary-file {spec.summary_path}",
        ]
    raise ValueError(f"unknown job {spec.job!r}")


def _executor_hostpath(name: str) -> str:
    return (
        f"--conf spark.kubernetes.executor.volumes.hostPath.{name}.mount.path=/repo/{name} "
        f"--conf spark.kubernetes.executor.volumes.hostPath.{name}.mount.readOnly=true "
        f"--conf spark.kubernetes.executor.volumes.hostPath.{name}.options.path={REPO_ROOT}/{name}"
    )


def spark_submit_command(spec: RunSpec) -> str:
    """The shell command the driver pod runs: ``spark-submit`` in client mode."""
    return " ".join(
        [
            "exec /opt/entrypoint.sh /opt/spark/bin/spark-submit",
            "--master k8s://https://kubernetes.default.svc:443",
            "--deploy-mode client",
            f"--name {spec.pod_name}",
            "--properties-file /opt/spark/conf/iceberg-catalog.conf",
            f"--conf spark.kubernetes.namespace={NAMESPACE}",
            f"--conf spark.kubernetes.container.image={SPARK_IMAGE}",
            "--conf spark.driver.bindAddress=0.0.0.0",
            "--conf spark.driver.host=$POD_IP",
            f"--driver-memory {DRIVER_MEMORY}",
            f"--conf spark.executor.instances={spec.executors}",
            "--conf spark.executor.cores=1",
            f"--conf spark.executor.memory={EXECUTOR_MEMORY}",
            f"--conf spark.executor.memoryOverhead={JOB_OVERHEAD[spec.job]}",
            "--conf spark.executorEnv.PYTHONPATH=/repo/src",
            _executor_hostpath("src"),
            _executor_hostpath("schemas"),
            # Benchmark only: never start on fewer executors than requested, and log the events.
            "--conf spark.scheduler.minRegisteredResourcesRatio=1.0",
            f"--conf spark.scheduler.maxRegisteredResourcesWaitingTime={REGISTRATION_WAIT}",
            "--conf spark.eventLog.enabled=true",
            f"--conf spark.eventLog.dir={EVENT_LOG_DIR}",
            f"{JOBS}/{JOB_SCRIPTS[spec.job]}",
            *job_args(spec),
        ]
    )


def _secret_env(name: str, secret: str, key: str) -> dict[str, Any]:
    return {"name": name, "valueFrom": {"secretKeyRef": {"name": secret, "key": key}}}


def pod_manifest(spec: RunSpec) -> dict[str, Any]:
    """The driver pod, the same shape as ``_spark_driver_task`` in ``dags/transform_publish.py``."""
    env: list[dict[str, Any]] = [
        {"name": "POD_IP", "valueFrom": {"fieldRef": {"fieldPath": "status.podIP"}}},
        {"name": "PYTHONPATH", "value": "/repo/src"},
        _secret_env("AWS_ACCESS_KEY_ID", "minio-root-credentials", "root-user"),
        _secret_env("AWS_SECRET_ACCESS_KEY", "minio-root-credentials", "root-password"),
    ]
    if spec.job == JOB_PUBLISH:
        env.append(_secret_env("PG_PASSWORD", "postgresql-gold-credentials", "password"))
    return {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {"name": spec.pod_name, "namespace": NAMESPACE, "labels": {"app": "tfm-benchmark", "benchmark-run": spec.run_id}},
        "spec": {
            "restartPolicy": "Never",
            "serviceAccountName": "spark",
            "containers": [
                {
                    "name": "driver",
                    "image": SPARK_IMAGE,
                    "imagePullPolicy": "IfNotPresent",
                    "command": ["/bin/bash", "-c"],
                    "args": [spark_submit_command(spec)],
                    "env": env,
                    "resources": {"requests": {"cpu": "500m", "memory": "1Gi"}, "limits": {"memory": "2Gi"}},
                    "volumeMounts": [
                        {"name": "src", "mountPath": "/repo/src", "readOnly": True},
                        {"name": "schemas", "mountPath": "/repo/schemas", "readOnly": True},
                        {"name": "data", "mountPath": "/repo/data"},
                    ],
                }
            ],
            "volumes": [
                {"name": "src", "hostPath": {"path": f"{REPO_ROOT}/src", "type": "Directory"}},
                {"name": "schemas", "hostPath": {"path": f"{REPO_ROOT}/schemas", "type": "Directory"}},
                {"name": "data", "hostPath": {"path": f"{REPO_ROOT}/data", "type": "DirectoryOrCreate"}},
            ],
        },
    }


def pg_digest_sql(schema: str) -> str:
    """One row per published table: its name, row count and an order-independent content hash."""
    selects = []
    for table in gold_schemas.TABLES:
        if table == gold_schemas.GOLD_RUN:
            selects.append(f"select '{table}', count(*), 0::numeric from {schema}.{table}")
        else:
            selects.append(f"select '{table}', count(*), coalesce(sum(hashtextextended(t::text, 0)::numeric), 0) from {schema}.{table} t")
    return " union all ".join(selects)


class Cluster:
    """Thin ``kubectl`` wrapper; ``run`` is injectable so the tests need no cluster."""

    def __init__(self, namespace: str = NAMESPACE, run: Callable[..., subprocess.CompletedProcess] = subprocess.run) -> None:
        self.namespace = namespace
        self._run = run

    def kubectl(self, *args: str, input: str | None = None, check: bool = True, stdout: Any = None) -> subprocess.CompletedProcess:
        command = ["kubectl", "-n", self.namespace, *args]
        result = self._run(command, input=input, text=True, stdout=stdout if stdout is not None else subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if check and result.returncode != 0:
            raise RuntimeError(f"{' '.join(command[:5])} failed ({result.returncode}): {(result.stderr or '').strip()[:500]}")
        return result

    def apply(self, manifest: dict[str, Any]) -> None:
        self.kubectl("apply", "-f", "-", input=json.dumps(manifest))

    def pod_phase(self, name: str) -> str:
        result = self.kubectl("get", "pod", name, "-o", "jsonpath={.status.phase}", check=False)
        return (result.stdout or "").strip() or "Unknown"

    def logs(self, name: str) -> str:
        return self.kubectl("logs", name, check=False).stdout or ""

    def delete_pod(self, name: str) -> None:
        self.kubectl("delete", "pod", name, "--ignore-not-found", "--wait=true", check=False)

    def app_id(self, driver_pod_name: str) -> str | None:
        """The Spark application id (label ``spark-app-selector``) of a driver pod, once it has one.

        Spark sets this label on the driver and on every executor it creates; it is the only
        reliable way to scope ``executor_pods`` to *this* run instead of the whole namespace.
        Empty/absent while the driver is still starting.
        """
        result = self.kubectl("get", "pod", driver_pod_name, "-o", "jsonpath={.metadata.labels.spark-app-selector}", check=False)
        return (result.stdout or "").strip() or None

    def executor_pods(self, app_id: str | None = None) -> list[str]:
        """Executor pods in the namespace, or only this run's own when ``app_id`` is given.

        Real incident (issue #101, Task 8): without ``app_id``, this lists *every* executor pod in
        the namespace by the generic `spark-role=executor` label, so a pod orphaned by an earlier,
        unrelated, interrupted run (the host suspending/rebooting mid-run, a repeated theme of this
        campaign) is misattributed as *this* run's own leftover -- it happened to 9 later,
        unrelated, genuinely successful `4x-publish` runs, all blamed for one `4x-silver` run's
        own leftover pods until the report was corrected by hand.
        """
        selector = f"spark-app-selector={app_id},spark-role=executor" if app_id else "spark-role=executor"
        result = self.kubectl("get", "pods", "-l", selector, "--no-headers", "-o", "custom-columns=NAME:.metadata.name", check=False)
        return [line.strip() for line in (result.stdout or "").splitlines() if line.strip()]

    def running_pods(self) -> list[str]:
        result = self.kubectl("get", "pods", "--field-selector=status.phase=Running", "--no-headers", "-o", "custom-columns=NAME:.metadata.name", check=False)
        return sorted(line.strip() for line in (result.stdout or "").splitlines() if line.strip())

    def minio_cpu_millicores(self) -> int | None:
        """Current CPU use of MinIO's pod in millicores (``kubectl top``), or ``None`` when unavailable."""
        result = self.kubectl("top", "pods", "-l", "app.kubernetes.io/name=minio", "--no-headers", check=False)
        for line in (result.stdout or "").splitlines():
            fields = line.split()
            if len(fields) >= 2 and fields[0].startswith("minio-") and "console" not in fields[0]:
                value = fields[1]
                return int(value[:-1]) if value.endswith("m") else int(float(value) * 1000)
        return None

    def minio(self, script: str, *, stdout: Any = None) -> subprocess.CompletedProcess:
        """Run ``script`` with the ``mc`` client of MinIO's pod, alias ``local`` (credentials are files there)."""
        prelude = 'mc alias set local http://localhost:9000 "$(cat $MINIO_ROOT_USER_FILE)" "$(cat $MINIO_ROOT_PASSWORD_FILE)" >/dev/null; '
        return self.kubectl("exec", "deploy/minio", "--", "sh", "-c", prelude + script, stdout=stdout)

    def clear_event_logs(self) -> None:
        self.minio(f"for f in $(mc ls local/{EVENTS_BUCKET}/logs/ | awk '{{print $NF}}' | grep '^spark-'); do mc rm local/{EVENTS_BUCKET}/logs/$f >/dev/null; done")

    def fetch_event_log(self, destination: Path) -> bool:
        """Copy the (single) event log to ``destination``; False when none was written."""
        script = f"f=$(mc ls local/{EVENTS_BUCKET}/logs/ | awk '{{print $NF}}' | grep '^spark-' | tail -1); [ -n \"$f\" ] && mc cat local/{EVENTS_BUCKET}/logs/$f"
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("wb") as handle:
            result = self._run(
                ["kubectl", "-n", self.namespace, "exec", "deploy/minio", "--", "sh", "-c",
                 'mc alias set local http://localhost:9000 "$(cat $MINIO_ROOT_USER_FILE)" "$(cat $MINIO_ROOT_PASSWORD_FILE)" >/dev/null; ' + script],
                stdout=handle, stderr=subprocess.PIPE, check=False,
            )
        return result.returncode == 0 and destination.stat().st_size > 0

    def reset_namespace(self, namespace: str) -> None:
        """Delete an Iceberg namespace's directory in the warehouse so every run starts from nothing."""
        name = namespace.removeprefix("lakehouse.")
        self.minio(f"mc rm --recursive --force local/lakehouse/warehouse/{name}/ >/dev/null 2>&1; true")

    def psql(self, sql: str) -> str:
        """Run ``sql`` as user ``gold``; the password goes over stdin, never onto a command line."""
        secret = self.kubectl("get", "secret", "postgresql-gold-credentials", "-o", "jsonpath={.data.password}").stdout
        password = base64.b64decode(secret).decode("utf-8")
        script = 'read -r PGPASSWORD; export PGPASSWORD; psql -h 127.0.0.1 -U gold -d gold -v ON_ERROR_STOP=1 -At -F "|" -c "$1"'
        return self.kubectl("exec", "-i", "postgresql-0", "--", "sh", "-c", script, "_", sql, input=password + "\n").stdout or ""


def read_available_memory_mb() -> int:
    """``MemAvailable`` of this machine (WSL2 hosts the whole cluster) in MiB."""
    with open("/proc/meminfo", encoding="utf-8") as meminfo:
        for line in meminfo:
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) // 1024
    return -1


_CPU_FIELDS = ("user", "nice", "system", "idle", "iowait", "irq", "softirq", "steal")


def read_cpu_times() -> dict[str, int]:
    """The system-wide CPU time counters of ``/proc/stat`` (jiffies since boot, all logical CPUs)."""
    with open("/proc/stat", encoding="utf-8") as stat:
        fields = stat.readline().split()[1:]
    return dict(zip(_CPU_FIELDS, (int(value) for value in fields[: len(_CPU_FIELDS)])))


def cpu_utilization(before: dict[str, int], after: dict[str, int]) -> dict[str, float]:
    """Share of the logical CPUs' time spent busy, waiting for I/O and stolen, between two readings."""
    delta = {name: after[name] - before[name] for name in _CPU_FIELDS}
    total = sum(delta.values())
    if total <= 0:
        return {}
    busy = total - delta["idle"] - delta["iowait"]
    return {
        "busy_pct": round(100 * busy / total, 1),
        "system_pct": round(100 * (delta["system"] + delta["irq"] + delta["softirq"]) / total, 1),
        "iowait_pct": round(100 * delta["iowait"] / total, 1),
        "steal_pct": round(100 * delta["steal"] / total, 1),
    }


def _iso(moment: float) -> str:
    return datetime.fromtimestamp(moment, UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


_EXECUTOR_OOM_SIGNATURE = "exit code 52(JVM OOM)"


def _diagnose_failure(log: str) -> str | None:
    """``"executor_oom"`` when the log shows an executor's JVM heap was exhausted.

    Seen for real in the campaign (issue #101) in two shapes that share the same root cause and
    the same literal Spark message (``exited with exit code 52(JVM OOM)``): (1) a single executor
    holding a whole data scale's partitions alone OOMs, Spark keeps replacing it, and gives up
    once ``spark.kubernetes.executor.maxNumFailures`` is reached (``ExecutorPodsAllocator: Max
    number of executor failures (N) reached``); (2) one executor among several OOMs, and the
    shuffle-fetch failures the survivors see while a replacement starts exceed the stage's own
    retry limit (``... has failed the maximum allowable number of times: N``). Both are a genuine,
    data-dependent memory ceiling of the fixed per-executor sizing (decision D8), not a bug, so
    the campaign records the outcome instead of aborting (decision D23) -- unlike an unrecognized
    failure, which still stops the campaign for investigation. Detecting the OOM itself, rather
    than either specific way Spark gives up afterward, is deliberately the narrower, more robust
    signature (decision D25).
    """
    return "executor_oom" if _EXECUTOR_OOM_SIGNATURE in log else None


def _task_summary(log: str) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for line in log.splitlines():
        if "TASK_SUMMARY " in line:
            try:
                summary = json.loads(line.split("TASK_SUMMARY ", 1)[1])
            except json.JSONDecodeError:
                continue
    return summary


def prepare_outputs(spec: RunSpec, cluster: Cluster) -> None:
    """Remove what the previous run of this job left, so each run starts from the same state."""
    cluster.clear_event_logs()
    if spec.job == JOB_SILVER:
        cluster.reset_namespace(spec.scale.silver_namespace)
    elif spec.job == JOB_GOLD:
        cluster.reset_namespace(spec.scale.gold_namespace)
    elif spec.job == JOB_PUBLISH:
        cluster.psql(f"DROP SCHEMA IF EXISTS {spec.scale.pg_schema} CASCADE")


def run_once(
    spec: RunSpec,
    cluster: Cluster,
    data_dir: Path,
    *,
    timeout: float = 3600.0,
    poll_seconds: float = 5.0,
    clock: Callable[[], float] = time.time,
    monotonic: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
    memory_probe: Callable[[], int] = read_available_memory_mb,
    cpu_probe: Callable[[], dict[str, int]] = read_cpu_times,
) -> dict[str, Any]:
    """Launch the job, wait for it, collect its log and event log, and write ``record.json``.

    A failed or timed-out job is reported in the record (``status``), not raised, so a campaign
    can decide what to do; the driver pod is always removed and executor leftovers are reported.

    The ``timeout`` budget is measured with ``monotonic`` (``time.monotonic``, ``CLOCK_MONOTONIC``
    on Linux), not with the wall clock: a host suspend/resume (the machine sleeping mid-campaign)
    freezes the guest and its monotonic clock along with it, so it does not count against the
    budget, while the wall clock jumps forward by the suspended duration and would otherwise
    trigger a false timeout on the very next poll -- exactly what happened to run
    ``1x-silver-e1-r011`` during the real campaign (issue #101, decision D22), which was killed
    mid-task although it was healthy and about to finish. A wall-clock jump much larger than
    ``poll_seconds`` between two polls is recorded as ``suspected_suspend_seconds``, informational
    only.
    """
    out_dir = data_dir / RUNS_SUBDIR / spec.run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    prepare_outputs(spec, cluster)
    machine = {
        "cpus": os.cpu_count(),
        "available_mb_before": memory_probe(),
        "loadavg_before": [round(value, 2) for value in os.getloadavg()],
        "running_pods": cluster.running_pods(),
    }

    submitted = clock()
    submitted_mono = monotonic()
    cpu_before = cpu_probe()
    cluster.apply(pod_manifest(spec))
    min_available = machine["available_mb_before"]
    max_executors = 0
    minio_cpu: list[int] = []
    phase = "Pending"
    last_wall = submitted
    suspected_suspend_seconds = 0.0
    app_id: str | None = None
    while monotonic() - submitted_mono < timeout:
        phase = cluster.pod_phase(spec.pod_name)
        now_wall = clock()
        if now_wall - last_wall > poll_seconds * 5:  # far more than one poll cycle: the host likely slept
            suspected_suspend_seconds += now_wall - last_wall
        last_wall = now_wall
        min_available = min(min_available, memory_probe())
        app_id = app_id or cluster.app_id(spec.pod_name)  # not set until the driver has registered
        max_executors = max(max_executors, len(cluster.executor_pods(app_id)))
        sample = cluster.minio_cpu_millicores()
        if sample is not None:
            minio_cpu.append(sample)
        if phase in {"Succeeded", "Failed"}:
            break
        sleep(poll_seconds)
    else:
        phase = "TimedOut"
    ended = clock()
    cpu = cpu_utilization(cpu_before, cpu_probe())

    log = cluster.logs(spec.pod_name)
    (out_dir / "driver.log").write_text(log, encoding="utf-8")
    app_id = app_id or cluster.app_id(spec.pod_name)
    cluster.delete_pod(spec.pod_name)
    has_event_log = cluster.fetch_event_log(out_dir / "eventlog")
    # Scoped to this run's own app id when known; falls back to every executor pod in the
    # namespace only if the driver never registered one (an early failure), same as before.
    leftovers = cluster.executor_pods(app_id)

    record = {
        "run_id": spec.run_id,
        "scale": spec.scale.name,
        "job": spec.job,
        "executors": spec.executors,
        "sequence": spec.sequence,
        "role": spec.role,
        "shuffle_partitions": spec.effective_shuffle_partitions,
        "executors_of": spec.of_executors,
        "status": {"Succeeded": "ok", "Failed": "failed", "TimedOut": "timeout"}.get(phase, phase.lower()),
        "failure_reason": _diagnose_failure(log) if phase == "Failed" else None,
        "submitted_at": _iso(submitted),
        "ended_at": _iso(ended),
        "wall_seconds": round(ended - submitted, 1),
        "active_seconds": round(monotonic() - submitted_mono, 1),
        "suspected_suspend_seconds": round(suspected_suspend_seconds, 1),
        "min_available_mb": min_available,
        "cpu": cpu,
        "minio_cpu_millicores": {"peak": max(minio_cpu), "mean": round(sum(minio_cpu) / len(minio_cpu))} if minio_cpu else None,
        "max_executors_seen": max_executors,
        "executor_leftovers": leftovers,
        "machine": machine,
        "summary": _task_summary(log),
        "has_event_log": has_event_log,
    }
    (out_dir / "record.json").write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
    logger.info(f"{spec.run_id}: {record['status']} in {record['wall_seconds']} s (min available {min_available} MB)")
    return record


def main(argv: Sequence[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s", stream=sys.stdout)
    parser = argparse.ArgumentParser(prog="python -m tfm_lakehouse.benchmark.runner", description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path(REPO_ROOT) / "data")
    parser.add_argument("--scale", required=True)
    parser.add_argument("--job", required=True, choices=sorted(JOB_SCRIPTS))
    parser.add_argument("--executors", type=int, required=True)
    parser.add_argument("--sequence", type=int, default=0)
    parser.add_argument("--role", default="measured", choices=["measured", "warmup", "pilot", "digest"])
    parser.add_argument("--shuffle-partitions", type=int, default=None, help="default: 16 times the scale factor")
    parser.add_argument("--timeout", type=float, default=3600.0)
    args = parser.parse_args(argv)
    spec = RunSpec(scale_for(args.scale), args.job, args.executors, args.sequence, args.role, args.shuffle_partitions)
    record = run_once(spec, Cluster(), args.data_dir, timeout=args.timeout)
    return 0 if record["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
