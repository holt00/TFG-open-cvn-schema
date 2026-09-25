"""Read a Spark event log into the metrics of one benchmark run (issue #101, decision D7).

The event log is what the Spark History Server reads: one JSON object per line. Only the events
that carry timings and task metrics are decoded; the large SQL plan events are skipped without
being parsed. The format written by the pinned Spark 3.5.9 was checked on real logs of the
benchmark's jobs; Spark documents its REST API, not this raw log, as the stable interface, so the
parser is tested on a sample taken from a real run.

Times reported:

* ``app_seconds``: application start to application end.
* ``startup_seconds``: application start to the last executor registered (the jobs wait for all
  of them, so this is the cost of having N executors, not part of the computation).
* ``compute_seconds``: first job start to last job end.
* ``busy_seconds``: time during which at least one job runs; ``gap_seconds`` is the rest of
  ``compute_seconds``, that is driver-side work between jobs, which does not scale with executors.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

_HANDLED = {
    "SparkListenerApplicationStart",
    "SparkListenerApplicationEnd",
    "SparkListenerExecutorAdded",
    "SparkListenerExecutorRemoved",
    "SparkListenerJobStart",
    "SparkListenerJobEnd",
    "SparkListenerStageCompleted",
    "SparkListenerTaskEnd",
    "org.apache.spark.sql.execution.ui.SparkListenerSQLExecutionStart",
    "org.apache.spark.sql.execution.ui.SparkListenerSQLExecutionEnd",
}
_EVENT_PREFIX = '{"Event":"'


class EventLogError(ValueError):
    """The event log is missing what a run needs (no application start or end)."""


@dataclass
class StageMetrics:
    """Timings and summed task metrics of one stage attempt."""

    stage_id: int
    attempt: int
    name: str
    tasks: int
    submitted_ms: int | None = None
    completed_ms: int | None = None
    succeeded_tasks: int = 0
    failed_tasks: int = 0
    executor_run_ms: int = 0
    executor_cpu_ns: int = 0
    jvm_gc_ms: int = 0
    shuffle_read_bytes: int = 0
    shuffle_write_bytes: int = 0
    input_bytes: int = 0
    output_bytes: int = 0
    memory_spilled_bytes: int = 0
    disk_spilled_bytes: int = 0
    peak_execution_memory_max: int = 0

    @property
    def wall_seconds(self) -> float | None:
        if self.submitted_ms is None or self.completed_ms is None:
            return None
        return round((self.completed_ms - self.submitted_ms) / 1000, 3)


@dataclass
class RunMetrics:
    """Everything a benchmark run keeps from its event log."""

    app_name: str
    app_id: str | None
    app_seconds: float
    executors_added: int
    startup_seconds: float
    compute_seconds: float
    busy_seconds: float
    gap_seconds: float
    jobs: int
    jobs_failed: int
    executors_removed: int = 0
    executor_removal_reasons: list[str] = field(default_factory=list)
    stages: list[StageMetrics] = field(default_factory=list)
    sql_executions: list[dict[str, Any]] = field(default_factory=list)

    @property
    def totals(self) -> dict[str, float]:
        """Sums over all stages, in seconds and bytes."""
        return {
            "tasks": sum(s.succeeded_tasks for s in self.stages),
            "failed_tasks": sum(s.failed_tasks for s in self.stages),
            "executor_run_seconds": round(sum(s.executor_run_ms for s in self.stages) / 1000, 3),
            "executor_cpu_seconds": round(sum(s.executor_cpu_ns for s in self.stages) / 1e9, 3),
            "jvm_gc_seconds": round(sum(s.jvm_gc_ms for s in self.stages) / 1000, 3),
            "shuffle_read_bytes": sum(s.shuffle_read_bytes for s in self.stages),
            "shuffle_write_bytes": sum(s.shuffle_write_bytes for s in self.stages),
            "input_bytes": sum(s.input_bytes for s in self.stages),
            "output_bytes": sum(s.output_bytes for s in self.stages),
            "memory_spilled_bytes": sum(s.memory_spilled_bytes for s in self.stages),
            "disk_spilled_bytes": sum(s.disk_spilled_bytes for s in self.stages),
            "peak_execution_memory_max": max((s.peak_execution_memory_max for s in self.stages), default=0),
        }

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["totals"] = self.totals
        for stage, raw in zip(self.stages, data["stages"]):
            raw["wall_seconds"] = stage.wall_seconds
        return data


def _event_name(line: str) -> str | None:
    """The event name of a line, without decoding it (the format starts with ``{"Event":"``)."""
    if line.startswith(_EVENT_PREFIX):
        end = line.find('"', len(_EVENT_PREFIX))
        return line[len(_EVENT_PREFIX) : end] if end > 0 else None
    return None


def _union_seconds(intervals: list[tuple[int, int]]) -> float:
    """Total length of the union of ``(start_ms, end_ms)`` intervals, in seconds."""
    total = 0
    current_start: int | None = None
    current_end = 0
    for start, end in sorted(intervals):
        if current_start is None or start > current_end:
            if current_start is not None:
                total += current_end - current_start
            current_start, current_end = start, end
        else:
            current_end = max(current_end, end)
    if current_start is not None:
        total += current_end - current_start
    return total / 1000


def parse_event_log(lines: Iterable[str]) -> RunMetrics:
    """Summarize one application's event log.

    Args:
        lines: The lines of the log (any other application's events must not be mixed in).

    Returns:
        The run's metrics.

    Raises:
        EventLogError: If the log has no application start or end event, or no job.
    """
    app_start: dict[str, Any] | None = None
    app_end_ms: int | None = None
    executor_ms: list[int] = []
    removal_reasons: list[str] = []
    job_start: dict[int, int] = {}
    job_intervals: list[tuple[int, int]] = []
    jobs_failed = 0
    stages: dict[tuple[int, int], StageMetrics] = {}
    pending: dict[tuple[int, int], StageMetrics] = {}
    sql_start: dict[int, dict[str, Any]] = {}
    sql_executions: list[dict[str, Any]] = []

    for line in lines:
        name = _event_name(line)
        if name is None:
            try:
                name = json.loads(line).get("Event")
            except (json.JSONDecodeError, AttributeError):
                continue
        if name not in _HANDLED:
            continue
        event = json.loads(line)

        if name == "SparkListenerApplicationStart":
            app_start = event
        elif name == "SparkListenerApplicationEnd":
            app_end_ms = int(event["Timestamp"])
        elif name == "SparkListenerExecutorAdded":
            executor_ms.append(int(event["Timestamp"]))
        elif name == "SparkListenerExecutorRemoved":
            removal_reasons.append(str(event.get("Removed Reason", ""))[:300])
        elif name == "SparkListenerJobStart":
            job_start[int(event["Job ID"])] = int(event["Submission Time"])
        elif name == "SparkListenerJobEnd":
            start = job_start.get(int(event["Job ID"]))
            if start is not None:
                job_intervals.append((start, int(event["Completion Time"])))
            if event.get("Job Result", {}).get("Result") != "JobSucceeded":
                jobs_failed += 1
        elif name == "SparkListenerStageCompleted":
            info = event["Stage Info"]
            key = (int(info["Stage ID"]), int(info["Stage Attempt ID"]))
            stage = pending.pop(key, None) or StageMetrics(key[0], key[1], info.get("Stage Name", ""), int(info.get("Number of Tasks", 0)))
            stage.name = info.get("Stage Name", stage.name)
            stage.tasks = int(info.get("Number of Tasks", stage.tasks))
            stage.submitted_ms = info.get("Submission Time")
            stage.completed_ms = info.get("Completion Time")
            stages[key] = stage
        elif name == "SparkListenerTaskEnd":
            key = (int(event["Stage ID"]), int(event["Stage Attempt ID"]))
            stage = stages.get(key) or pending.setdefault(key, StageMetrics(key[0], key[1], "", 0))
            metrics = event.get("Task Metrics")
            if event.get("Task End Reason", {}).get("Reason") != "Success" or not metrics:
                stage.failed_tasks += 1
                continue
            stage.succeeded_tasks += 1
            stage.executor_run_ms += int(metrics.get("Executor Run Time", 0))
            stage.executor_cpu_ns += int(metrics.get("Executor CPU Time", 0))
            stage.jvm_gc_ms += int(metrics.get("JVM GC Time", 0))
            shuffle_read = metrics.get("Shuffle Read Metrics", {})
            stage.shuffle_read_bytes += int(shuffle_read.get("Remote Bytes Read", 0)) + int(shuffle_read.get("Local Bytes Read", 0))
            stage.shuffle_write_bytes += int(metrics.get("Shuffle Write Metrics", {}).get("Shuffle Bytes Written", 0))
            stage.input_bytes += int(metrics.get("Input Metrics", {}).get("Bytes Read", 0))
            stage.output_bytes += int(metrics.get("Output Metrics", {}).get("Bytes Written", 0))
            stage.memory_spilled_bytes += int(metrics.get("Memory Bytes Spilled", 0))
            stage.disk_spilled_bytes += int(metrics.get("Disk Bytes Spilled", 0))
            stage.peak_execution_memory_max = max(stage.peak_execution_memory_max, int(metrics.get("Peak Execution Memory", 0)))
        elif name.endswith("SparkListenerSQLExecutionStart"):
            sql_start[int(event["executionId"])] = event
        elif name.endswith("SparkListenerSQLExecutionEnd"):
            start = sql_start.pop(int(event["executionId"]), None)
            if start is not None:
                sql_executions.append(
                    {
                        "execution_id": int(event["executionId"]),
                        "description": str(start.get("description", ""))[:160],
                        "seconds": round((int(event["time"]) - int(start["time"])) / 1000, 3),
                    }
                )

    if app_start is None or app_end_ms is None:
        raise EventLogError("the event log has no application start or end event (was the application stopped cleanly?)")
    if not job_intervals:
        raise EventLogError("the event log has no completed job")

    start_ms = int(app_start["Timestamp"])
    first_job = min(start for start, _ in job_intervals)
    last_job = max(end for _, end in job_intervals)
    compute = (last_job - first_job) / 1000
    busy = _union_seconds(job_intervals)
    return RunMetrics(
        app_name=str(app_start.get("App Name", "")),
        app_id=app_start.get("App ID"),
        app_seconds=round((app_end_ms - start_ms) / 1000, 3),
        executors_added=len(executor_ms),
        startup_seconds=round((max(executor_ms) - start_ms) / 1000, 3) if executor_ms else 0.0,
        compute_seconds=round(compute, 3),
        busy_seconds=round(busy, 3),
        gap_seconds=round(compute - busy, 3),
        jobs=len(job_intervals),
        jobs_failed=jobs_failed,
        executors_removed=len(removal_reasons),
        executor_removal_reasons=removal_reasons,
        stages=sorted(stages.values(), key=lambda s: (s.stage_id, s.attempt)),
        sql_executions=sql_executions,
    )


def parse_event_log_file(path: Path) -> RunMetrics:
    """``parse_event_log`` over a file."""
    with path.open(encoding="utf-8") as handle:
        return parse_event_log(handle)
