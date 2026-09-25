"""Turn the benchmark's run records into the tables and charts of the memoria (issue #101).

Input: the ``record.json`` and ``eventlog`` files that ``runner.run_once`` leaves under
``data/benchmark/runs/<run_id>/``. Output: ``results.json``, ``results.csv``, ``results.md`` and PNG
charts. Everything that is a number is computed here from the records, never typed by hand.

Definitions (decision D10):

* runtime of a run: ``app_seconds`` of the event log (application start to end); the median over
  the measured runs of a point ``(scale, job, executors)``.
* speedup ``S(n) = T(1) / T(n)``, efficiency ``S(n) / n``.
* Karp-Flatt experimentally determined serial fraction ``e(n) = (1/S - 1/n) / (1 - 1/n)`` for n > 1.
* size-up exponent: slope of ``log T`` against ``log scale`` at a fixed executor count (1.0 means
  time grows linearly with data).
"""

from __future__ import annotations

import csv
import json
import math
import statistics
from collections import defaultdict
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any

from tfm_lakehouse.benchmark.eventlog import EventLogError, parse_event_log_file

SPREAD_LIMIT = 0.10
MEASURED_JOBS = ("silver", "gold", "publish")
DIGEST_JOBS = {"digest_silver": "silver", "digest_gold": "gold"}
Key = tuple[str, str, int]


def load_records(runs_dir: Path) -> list[dict[str, Any]]:
    """Every run record under ``runs_dir``, each with its parsed ``metrics`` when it has an event log."""
    records = []
    for record_file in sorted(runs_dir.glob("*/record.json")):
        record = json.loads(record_file.read_text(encoding="utf-8"))
        record["metrics"] = None
        event_log = record_file.parent / "eventlog"
        if record.get("has_event_log") and event_log.is_file():
            try:
                record["metrics"] = parse_event_log_file(event_log).to_dict()
            except EventLogError as exc:
                record["metrics_error"] = str(exc)
        records.append(record)
    return records


def invalid_reason(record: dict[str, Any]) -> str | None:
    """Why a measured run must not count, or ``None`` when it is usable."""
    if record["status"] != "ok":
        reason = record.get("failure_reason")
        return f"status {record['status']} ({reason})" if reason else f"status {record['status']}"
    metrics = record.get("metrics")
    if not metrics:
        return "no readable event log"
    if metrics.get("executors_removed"):
        return f"{metrics['executors_removed']} executor(s) lost during the run: {metrics['executor_removal_reasons'][0][:120]}"
    if metrics["executors_added"] != record["executors"]:
        return f"{metrics['executors_added']} executors registered, {record['executors']} requested"
    if metrics["jobs_failed"]:
        return "a job failed"
    if record.get("executor_leftovers"):
        return "executor pods left behind"
    return None


def _digest_is_empty(digest: Any) -> bool:
    """Whether a digest shows no output at all (a confirmed-OOM configuration never wrote anything).

    Two shapes: silver/gold digests are ``table -> {"rows": n, ...}``; the publish digest (D9's
    PostgreSQL row-hash check) is ``table -> [rows_str, hash_str]``.
    """
    rows = (v.get("rows") if isinstance(v, dict) else int(v[0]) for v in digest.values())
    return all(r == 0 for r in rows)


def correctness(records: Iterable[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    """Compare the content digests of the outputs across executor counts (decision D9).

    Returns, per ``(scale, kind)`` with kind ``silver``, ``gold`` or ``publish``:

    * ``configurations``: every executor count a digest was collected for.
    * ``empty_executors``: the executor counts whose digest is empty -- decision D25's confirmed
      deterministic OOM never wrote anything, so an empty digest there is expected, not a defect.
    * ``consistent``: whether the executor counts that *did* produce output all agree with each
      other (the actual correctness claim of D9); undefined (``None``) if fewer than two did.
    * ``equal``: the blunter, whole-set comparison kept for backward compatibility -- ``False``
      whenever any executor count is empty, even if every real output is byte-identical.
    """
    seen: dict[tuple[str, str], dict[int, Any]] = defaultdict(dict)
    for record in records:
        if record["status"] != "ok":
            continue
        if record["job"] in DIGEST_JOBS:
            digests = record.get("summary", {}).get("digests")
            if digests is not None:
                seen[(record["scale"], DIGEST_JOBS[record["job"]])][record.get("executors_of") or record["executors"]] = digests
        elif record["job"] == "publish" and record.get("pg_digest") is not None:
            seen[(record["scale"], "publish")][record["executors"]] = record["pg_digest"]
    result = {}
    for key, by_executors in seen.items():
        values = [json.dumps(value, sort_keys=True) for value in by_executors.values()]
        empty = sorted(executors for executors, digest in by_executors.items() if _digest_is_empty(digest))
        non_empty = {executors: digest for executors, digest in by_executors.items() if executors not in empty}
        non_empty_values = {json.dumps(digest, sort_keys=True) for digest in non_empty.values()}
        result[key] = {
            "equal": len(set(values)) == 1,
            "consistent": (len(non_empty_values) == 1) if len(non_empty) >= 2 else None,
            "empty_executors": empty,
            "configurations": sorted(by_executors),
            "digests": by_executors,
        }
    return result


def points(records: Iterable[dict[str, Any]]) -> dict[Key, dict[str, Any]]:
    """Aggregate the usable measured runs per ``(scale, job, executors)``."""
    grouped: dict[Key, list[dict[str, Any]]] = defaultdict(list)
    excluded: dict[Key, list[str]] = defaultdict(list)
    for record in records:
        if record["job"] not in MEASURED_JOBS or record["role"] != "measured":
            continue
        key = (record["scale"], record["job"], record["executors"])
        reason = invalid_reason(record)
        if reason:
            excluded[key].append(f"{record['run_id']}: {reason}")
        else:
            grouped[key].append(record)
    result: dict[Key, dict[str, Any]] = {}
    for key in sorted(set(grouped) | set(excluded), key=lambda k: (int(k[0].rstrip("x")), MEASURED_JOBS.index(k[1]), k[2])):
        runs = grouped.get(key, [])
        app = [r["metrics"]["app_seconds"] for r in runs]
        result[key] = {
            "runs": len(runs),
            "excluded": excluded.get(key, []),
            "app_seconds": app,
            "median": statistics.median(app) if app else None,
            "min": min(app) if app else None,
            "max": max(app) if app else None,
            "spread": (max(app) - min(app)) / statistics.median(app) if app else None,
            "compute_median": _median(r["metrics"]["compute_seconds"] for r in runs),
            "startup_median": _median(r["metrics"]["startup_seconds"] for r in runs),
            "gap_median": _median(r["metrics"]["gap_seconds"] for r in runs),
            "gc_median": _median(r["metrics"]["totals"]["jvm_gc_seconds"] for r in runs),
            "executor_run_median": _median(r["metrics"]["totals"]["executor_run_seconds"] for r in runs),
            "input_bytes": _median(r["metrics"]["totals"]["input_bytes"] for r in runs),
            "shuffle_bytes": _median(r["metrics"]["totals"]["shuffle_write_bytes"] for r in runs),
            "spilled_bytes": _median(r["metrics"]["totals"]["disk_spilled_bytes"] + r["metrics"]["totals"]["memory_spilled_bytes"] for r in runs),
            "peak_min_available_mb": min((r["min_available_mb"] for r in runs), default=None),
            "cpu_busy_median": _median(r["cpu"]["busy_pct"] for r in runs if r.get("cpu")),
            "task_retries": sum(r["metrics"]["totals"]["failed_tasks"] for r in runs),
            "minio_cpu_peak_median": _median(r["minio_cpu_millicores"]["peak"] for r in runs if r.get("minio_cpu_millicores")),
            "cpu_iowait_median": _median(r["cpu"]["iowait_pct"] for r in runs if r.get("cpu")),
        }
    return result


def _median(values: Iterable[float]) -> float | None:
    values = list(values)
    return statistics.median(values) if values else None


def karp_flatt(speedup: float, executors: int) -> float | None:
    """Experimentally determined serial fraction; undefined for one executor."""
    if executors < 2 or speedup <= 0:
        return None
    return (1 / speedup - 1 / executors) / (1 - 1 / executors)


def loglog_slope(xs: Sequence[float], ys: Sequence[float]) -> float | None:
    """Least-squares slope of ``log y`` against ``log x``; ``None`` with fewer than two points."""
    if len(xs) < 2 or len(set(xs)) < 2:
        return None
    lx = [math.log(x) for x in xs]
    ly = [math.log(y) for y in ys]
    mean_x, mean_y = statistics.fmean(lx), statistics.fmean(ly)
    return sum((a - mean_x) * (b - mean_y) for a, b in zip(lx, ly)) / sum((a - mean_x) ** 2 for a in lx)


def derive(aggregated: dict[Key, dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Speedup, efficiency, Karp-Flatt (per point) and the size-up exponents (per job and executors)."""
    rows = []
    for (scale, job, executors), point in aggregated.items():
        base = aggregated.get((scale, job, 1), {}).get("median")
        speedup = base / point["median"] if base and point["median"] else None
        rows.append(
            {
                "scale": scale,
                "job": job,
                "executors": executors,
                **point,
                "speedup": speedup,
                "efficiency": speedup / executors if speedup else None,
                "karp_flatt": karp_flatt(speedup, executors) if speedup else None,
                "flagged": bool(point["spread"] is not None and point["spread"] > SPREAD_LIMIT),
            }
        )
    sizeup = []
    for job in MEASURED_JOBS:
        for executors in sorted({k[2] for k in aggregated}):
            pairs = [(int(k[0].rstrip("x")), v["median"]) for k, v in aggregated.items() if k[1] == job and k[2] == executors and v["median"]]
            slope = loglog_slope([p[0] for p in pairs], [p[1] for p in pairs])
            if slope is not None:
                sizeup.append({"job": job, "executors": executors, "scales": [p[0] for p in pairs], "exponent": slope})
    return {"points": rows, "sizeup": sizeup}


def _fmt(value: float | None, digits: int = 1, suffix: str = "") -> str:
    return "-" if value is None else f"{value:.{digits}f}{suffix}"


def render_markdown(derived: dict[str, list[dict[str, Any]]], checks: dict[tuple[str, str], dict[str, Any]]) -> str:
    """The results as Markdown tables (one per job, plus size-up and correctness)."""
    out = ["# Spark benchmark results (issue #101)", "", "Generated by `tfm_lakehouse.benchmark.report`; every figure is computed from the run records.", ""]
    titles = {"silver": "bronze_to_silver", "gold": "silver_to_gold", "publish": "publish_gold_to_postgres"}
    for job in MEASURED_JOBS:
        rows = [r for r in derived["points"] if r["job"] == job]
        if not rows:
            continue
        out += [
            f"## {titles[job]}",
            "",
            "| scale | executors | runs | median s | min-max s | spread | speedup | efficiency | Karp-Flatt | startup s | compute s | driver gaps s | input MB | CPU busy % | iowait % | MinIO CPU peak m | task retries |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
        for r in rows:
            flag = " (!)" if r["flagged"] else ""
            out.append(
                f"| {r['scale']} | {r['executors']} | {r['runs']} | {_fmt(r['median'])} | {_fmt(r['min'])}-{_fmt(r['max'])} | "
                f"{_fmt(None if r['spread'] is None else r['spread'] * 100, 1, '%')}{flag} | {_fmt(r['speedup'], 2)} | {_fmt(r['efficiency'], 2)} | "
                f"{_fmt(r['karp_flatt'], 3)} | {_fmt(r['startup_median'])} | {_fmt(r['compute_median'])} | {_fmt(r['gap_median'])} | "
                f"{_fmt(None if r['input_bytes'] is None else r['input_bytes'] / 1e6, 0)} | {_fmt(r['cpu_busy_median'])} | {_fmt(r['cpu_iowait_median'])} | {_fmt(r['minio_cpu_peak_median'], 0)} | {r['task_retries']} |"
            )
        out.append("")
    if derived["sizeup"]:
        out += ["## Size-up exponent (log-log slope of time against scale; 1.0 = linear)", "", "| job | executors | scales | exponent |", "| --- | --- | --- | --- |"]
        for s in derived["sizeup"]:
            out.append(f"| {s['job']} | {s['executors']} | {', '.join(f'{x}x' for x in s['scales'])} | {s['exponent']:.2f} |")
        out.append("")
    if checks:
        out += [
            "## Output correctness (content digests across executor counts, decision D9)",
            "",
            "An executor count in \"empty (confirmed OOM)\" produced no output at all (decision D25's",
            "deterministic memory ceiling) and is excluded from the identical-content comparison, which",
            "only asks whether every executor count that *did* produce output agrees on it.",
            "",
            "| scale | output | executor counts compared | empty (confirmed OOM) | identical among the rest |",
            "| --- | --- | --- | --- | --- |",
        ]
        for (scale, kind), result in sorted(checks.items()):
            empty = ", ".join(map(str, result["empty_executors"])) or "-"
            consistent = {True: "yes", False: "**NO**", None: "n/a (fewer than 2 produced output)"}[result["consistent"]]
            out.append(f"| {scale} | {kind} | {', '.join(map(str, result['configurations']))} | {empty} | {consistent} |")
        out.append("")
    excluded = [(r["scale"], r["job"], r["executors"], why) for r in derived["points"] for why in r["excluded"]]
    if excluded:
        out += ["## Runs excluded", ""] + [f"- {scale} {job} n={executors}: {why}" for scale, job, executors, why in excluded] + [""]
    return "\n".join(out)


def write_outputs(runs_dir: Path, output_dir: Path) -> dict[str, Any]:
    """Compute everything and write ``results.json``, ``results.csv`` and ``results.md`` to ``output_dir``."""
    records = load_records(runs_dir)
    derived = derive(points(records))
    checks = correctness(records)
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "points": derived["points"],
        "sizeup": derived["sizeup"],
        "correctness": {
            f"{scale}/{kind}": {"equal": r["equal"], "consistent": r["consistent"], "empty_executors": r["empty_executors"], "configurations": r["configurations"]}
            for (scale, kind), r in checks.items()
        },
    }
    (output_dir / "results.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    columns = ["scale", "job", "executors", "runs", "median", "min", "max", "spread", "speedup", "efficiency", "karp_flatt", "startup_median", "compute_median", "gap_median", "gc_median", "input_bytes", "cpu_busy_median", "cpu_iowait_median", "minio_cpu_peak_median", "task_retries"]
    with (output_dir / "results.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(derived["points"])
    (output_dir / "results.md").write_text(render_markdown(derived, checks), encoding="utf-8")
    return {"records": len(records), "points": len(derived["points"]), "correctness_ok": all(r["consistent"] is not False for r in checks.values())}


def draw_charts(derived: dict[str, list[dict[str, Any]]], output_dir: Path) -> list[Path]:
    """Speedup and runtime charts, one figure per job (matplotlib is imported here only)."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    written = []
    for job in MEASURED_JOBS:
        rows = [r for r in derived["points"] if r["job"] == job and r["median"]]
        if not rows:
            continue
        figure, (time_axis, speed_axis) = plt.subplots(1, 2, figsize=(10, 4))
        for scale in sorted({r["scale"] for r in rows}, key=lambda s: int(s.rstrip("x"))):
            series = sorted((r for r in rows if r["scale"] == scale), key=lambda r: r["executors"])
            xs = [r["executors"] for r in series]
            time_axis.errorbar(xs, [r["median"] for r in series], yerr=[[r["median"] - r["min"] for r in series], [r["max"] - r["median"] for r in series]], marker="o", capsize=3, label=scale)
            speed_axis.plot(xs, [r["speedup"] for r in series], marker="o", label=scale)
        executors = sorted({r["executors"] for r in rows})
        speed_axis.plot(executors, [e / executors[0] for e in executors], linestyle="--", color="grey", label="ideal")
        time_axis.set(xlabel="executors", ylabel="application time (s)", title=f"{job}: runtime (median, min-max)", xticks=executors)
        speed_axis.set(xlabel="executors", ylabel="speedup vs 1 executor", title=f"{job}: speedup", xticks=executors)
        time_axis.legend(title="scale")
        speed_axis.legend()
        figure.tight_layout()
        path = output_dir / f"benchmark_{job}.png"
        figure.savefig(path, dpi=150)
        plt.close(figure)
        written.append(path)
    return written


def main(argv: Sequence[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(prog="python -m tfm_lakehouse.benchmark.report", description=__doc__)
    parser.add_argument("--runs-dir", type=Path, default=Path("data/benchmark/runs"))
    parser.add_argument("--output-dir", type=Path, default=Path("docs/benchmark"))
    parser.add_argument("--no-charts", action="store_true")
    args = parser.parse_args(argv)
    summary = write_outputs(args.runs_dir, args.output_dir)
    if not args.no_charts:
        draw_charts(json.loads((args.output_dir / "results.json").read_text(encoding="utf-8")), args.output_dir)
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
