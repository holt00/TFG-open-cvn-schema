"""The benchmark campaign of issue #101: the ordered list of runs and how to execute it.

For each scale and job (silver, then gold, then the publish, because each reads the previous
job's output of the same scale) the plan holds one discarded warm-up run, then ``repetitions``
measured runs for every executor count, ordered in randomized blocks (each repetition is a
permutation of the executor counts, drawn from a seed) so a slow drift of the machine is not read
as an effect of the executor count (decision D8). The first measured run of every executor count
is followed by a digest of the tables it wrote (silver, gold) or, for the publish, a digest of the
PostgreSQL tables, which is what decision D9 compares across executor counts.

The plan is deterministic, so an interrupted campaign resumes: runs whose record says ``ok`` are
skipped. It stops at the first failed run, because the runs that follow would not be comparable.
"""

from __future__ import annotations

import argparse
import json
import logging
import random
import shutil
import sys
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from tfm_lakehouse.benchmark.data import SCALE_FACTORS, scale_for
from tfm_lakehouse.benchmark.runner import (
    DIGEST_EXECUTORS,
    DIGEST_GOLD,
    DIGEST_SILVER,
    JOB_GOLD,
    JOB_PUBLISH,
    JOB_SILVER,
    MEASURED_JOBS,
    RUNS_SUBDIR,
    Cluster,
    RunSpec,
    pg_digest_sql,
    run_once,
)

logger = logging.getLogger(__name__)

DEFAULT_EXECUTORS = (1, 2, 4)
DEFAULT_REPETITIONS = 3
DEFAULT_SEED = 101
WARMUP_EXECUTORS = 2
SETTLE_SECONDS = 15.0
_DIGEST_JOB = {JOB_SILVER: DIGEST_SILVER, JOB_GOLD: DIGEST_GOLD}


class CampaignError(RuntimeError):
    """A run of the campaign failed; the ones after it would not be comparable."""


CONFIRMED_OOM_ATTEMPTS = 2


def _attempt_outcomes(data_dir: Path, spec: RunSpec) -> list[tuple[bool, str | None]]:
    """``(succeeded, failure_reason)`` of every recorded *real* attempt of ``spec``'s configuration.

    Matches by ``(scale, job, executors)``, not by run id: a resumed campaign retries a failed run
    under the *same* run id (several attempts, one record, overwritten each time), while a fresh
    repetition of the same configuration gets its *own* run id (several records), and the role
    (warm-up or measured) does not matter either -- both genuinely exercise the configuration.
    Either way, every attempt that has actually happened is counted.

    A ``"skipped"`` record is *not* counted, even though it is a record for this exact
    configuration: it never ran, so it carries no new evidence, only a bookkeeping decision based
    on the *other* attempts already counted -- real incident (issue #101, D26/D27): a repeat
    skipped by `_skip_confirmed_oom` got its own fresh "skipped" record (`failure_reason ==
    "executor_oom_confirmed"`, not `"executor_oom"`), and counting it broke the `all(...)` check
    for the *next* repeat of the same configuration, which then ran for real instead of being
    skipped too.
    """
    outcomes = []
    # both the current record.json of every run id and any earlier attempt of the *same* run id
    # that _archive_attempt preserved before a retry overwrote it (otherwise a run id retried
    # across campaign resumes -- the real 2x-silver-e1-r042 -- would count as only 1 attempt).
    for record_file in (data_dir / RUNS_SUBDIR).glob("*/record*.json"):
        record = json.loads(record_file.read_text(encoding="utf-8"))
        if record.get("status") == "skipped":
            continue
        if (record.get("scale"), record.get("job"), record.get("executors")) == (spec.scale.name, spec.job, spec.executors):
            outcomes.append((record.get("status") == "ok", record.get("failure_reason")))
    return outcomes


def _archive_attempt(record_file: Path) -> None:
    """Preserve a run id's previous attempt before it is overwritten, so a retry is not lost."""
    if not record_file.is_file():
        return
    existing = sorted(record_file.parent.glob("record.attempt*.json"))
    next_number = len(existing) + 1
    shutil.copyfile(record_file, record_file.parent / f"record.attempt{next_number}.json")


def _confirmed_deterministic_oom(data_dir: Path, spec: RunSpec) -> bool:
    """Whether every attempt of this exact configuration so far OOM'd, with none succeeding.

    A configuration on the edge of the fixed per-executor memory sizing (decision D8) can fail
    only sometimes (real incident: `2x-silver-e2` succeeded twice, 401.1 s and 468.3 s, then OOM'd
    once on a third attempt) -- that is data worth keeping every repetition for, not a ceiling to
    stop chasing. Only a configuration with *zero* successes across at least
    ``CONFIRMED_OOM_ATTEMPTS`` attempts, all of them diagnosed as ``executor_oom``, is a
    deterministic ceiling (real incident: `2x-silver-e1` OOM'd on both of its attempts).
    """
    outcomes = _attempt_outcomes(data_dir, spec)
    return len(outcomes) >= CONFIRMED_OOM_ATTEMPTS and all(reason == "executor_oom" for _, reason in outcomes) and not any(ok for ok, _ in outcomes)


def _skip_confirmed_oom(spec: RunSpec, data_dir: Path, attempts: int) -> dict:
    """Record a confirmed-deterministic point as skipped, without running it.

    A run id that was *itself* one of the attempts confirming the ceiling (a retried slot such as
    the real `2x-silver-e1-r042`, attempted three times across campaign resumes under the same run
    id) already holds its own real, counted outcome in ``record.json``; that file is left
    untouched, since overwriting it with a "skipped" record would erase one of the very attempts
    `_confirmed_deterministic_oom` needs to keep recognizing the ceiling for the *other* repeats of
    the same configuration -- a real bug found while resuming the campaign after a host reboot (a
    later repeat, `2x-silver-e1-r046`, ran for real instead of being skipped, because skipping
    `r042` had just overwritten its own confirming evidence). A run id that was never attempted
    (`r046`, `r049`) gets a fresh, lightweight ``"skipped"`` record instead.
    """
    folder = data_dir / RUNS_SUBDIR / spec.run_id
    record_file = folder / "record.json"
    if record_file.is_file():
        return json.loads(record_file.read_text(encoding="utf-8"))
    record = {
        "run_id": spec.run_id,
        "scale": spec.scale.name,
        "job": spec.job,
        "executors": spec.executors,
        "role": spec.role,
        "status": "skipped",
        "failure_reason": "executor_oom_confirmed",
        "note": f"{attempts} earlier attempts of this exact configuration all failed with executor_oom and none succeeded (decision D25); this repeat was not run.",
    }
    folder.mkdir(parents=True, exist_ok=True)
    record_file.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
    return record


MAX_EXECUTORS = 4
REPAIR_SEQUENCE_OFFSET = 8000


def _last_write_ok(data_dir: Path, scale_name: str, job: str) -> bool | None:
    """Whether the chronologically latest attempt of ``job`` for ``scale_name`` left valid output.

    Every attempt of a benchmark job resets its own namespace before it runs (decision D9), so the
    *current* state of that namespace is whatever the most recently *attempted* run of that job
    left behind -- not necessarily the most recent success. A ``"skipped"`` record never touches
    the namespace, so it is not a candidate for "most recent". Returns ``None`` if the job has
    never been attempted for this scale yet.

    Recency is judged by ``submitted_at`` (when a run actually started, and so reset the
    namespace), not by the plan's ``sequence`` number: real incident (issue #101, D28) -- a
    campaign resume retries a failed run id (`4x-silver-e2-r073`, a warm-up) *after* later-numbered
    runs (`r085`) already completed successfully, so it executes later in real time despite its
    lower sequence number. Using ``sequence`` said `r085` (the higher number) was still the latest,
    when in fact the retried `r073` ran afterward, reset the namespace again, and failed, leaving
    it empty -- so `4x-gold-e2-r086` then read a missing table.
    """
    latest: dict | None = None
    for record_file in (data_dir / RUNS_SUBDIR).glob("*/record.json"):
        record = json.loads(record_file.read_text(encoding="utf-8"))
        if record.get("scale") != scale_name or record.get("job") != job or record.get("status") == "skipped":
            continue
        if latest is None or record.get("submitted_at", "") > latest.get("submitted_at", ""):
            latest = record
    return None if latest is None else latest.get("status") == "ok"


def _repair(job: str, scale, sequence: int, cluster: Cluster, data_dir: Path, run: Callable[..., dict]) -> dict:
    """Rerun ``job`` at the machine's most reliable configuration so its output is valid again.

    Real incident (issue #101): the campaign's randomized order can legitimately end a scale's
    silver (or gold) phase on a run that OOM'd (decision D25's own confirmed ceiling, or a
    marginal one-off failure); the very next gold (or publish) run then finds an empty or missing
    upstream table and fails for a different, unrecognized reason, stopping the campaign. Rather
    than assume any particular attempt in the plan left good data, this explicitly guarantees it:
    ``MAX_EXECUTORS`` has the fewest observed OOM failures of any executor count. The repair run's
    own record is written with ``role="repair"``, so `report.points` (which only counts
    ``role == "measured"``) never mixes it into the benchmark's own figures.
    """
    spec = RunSpec(scale, job, MAX_EXECUTORS, REPAIR_SEQUENCE_OFFSET + sequence, role="repair")
    logger.warning(f"{spec.run_id}: the last {job} attempt for {scale.name} did not leave valid output; repairing before continuing (issue #101 finding)")
    record = run(spec, cluster, data_dir)
    if record["status"] != "ok":
        raise CampaignError(f"repair run {spec.run_id} ({job}, {MAX_EXECUTORS} executors) also failed with status {record['status']}; see data/{RUNS_SUBDIR}/{spec.run_id}/driver.log")
    return record


@dataclass(frozen=True)
class PlannedRun:
    """A run of the plan; ``pg_digest`` asks for the PostgreSQL digest once a publish run is done."""

    spec: RunSpec
    pg_digest: bool = False


def build_plan(
    scales: Sequence[str],
    executors: Sequence[int] = DEFAULT_EXECUTORS,
    repetitions: int = DEFAULT_REPETITIONS,
    seed: int = DEFAULT_SEED,
    jobs: Sequence[str] = MEASURED_JOBS,
    first_sequence: int = 1,
    measured_role: str = "measured",
) -> list[PlannedRun]:
    """The ordered runs of the campaign (see the module docstring).

    ``first_sequence`` and ``measured_role`` let a pilot reuse the same plan without colliding with
    the campaign's run ids (the pilot uses sequences from 901 and the role ``pilot``, which the
    report never counts).
    """
    plan: list[PlannedRun] = []
    sequence = first_sequence - 1

    def add(scale_name: str, job: str, count: int, role: str, of_executors: int | None = None, pg_digest: bool = False) -> None:
        nonlocal sequence
        sequence += 1
        plan.append(PlannedRun(RunSpec(scale_for(scale_name), job, count, sequence, role, of_executors=of_executors), pg_digest))

    for scale_name in scales:
        for job in jobs:
            add(scale_name, job, WARMUP_EXECUTORS, "warmup")
            rng = random.Random(f"{seed}:{scale_name}:{job}")
            digested: set[int] = set()
            for _ in range(repetitions):
                order = list(executors)
                rng.shuffle(order)
                for count in order:
                    first = count not in digested
                    digested.add(count)
                    add(scale_name, job, count, measured_role, pg_digest=first and job == JOB_PUBLISH)
                    if first and job in _DIGEST_JOB:
                        add(scale_name, _DIGEST_JOB[job], DIGEST_EXECUTORS, "digest", of_executors=count)
    return plan


def parse_pg_digest(output: str) -> dict[str, list[str]]:
    """``table|rows|hash`` lines of ``pg_digest_sql`` into ``{table: [rows, hash]}``."""
    digest = {}
    for line in output.splitlines():
        if line.count("|") == 2:
            table, rows, value = line.split("|")
            digest[table] = [rows, value]
    return digest


def _done(record_file: Path, item: PlannedRun) -> bool:
    if not record_file.is_file():
        return False
    record = json.loads(record_file.read_text(encoding="utf-8"))
    return record.get("status") == "ok" and (not item.pg_digest or "pg_digest" in record)


def execute(
    plan: Sequence[PlannedRun],
    cluster: Cluster,
    data_dir: Path,
    *,
    settle_seconds: float = SETTLE_SECONDS,
    sleep: Callable[[float], None] = time.sleep,
    run: Callable[..., dict] = run_once,
) -> list[dict]:
    """Execute the plan in order, skipping runs already recorded as ``ok``; stop at the first failure."""
    records = []
    started = time.time()
    for index, item in enumerate(plan, start=1):
        spec = item.spec
        record_file = data_dir / RUNS_SUBDIR / spec.run_id / "record.json"
        if _done(record_file, item):
            logger.info(f"[{index}/{len(plan)}] {spec.run_id}: already done, skipped")
            continue
        if spec.job in (JOB_GOLD, DIGEST_GOLD) and _last_write_ok(data_dir, spec.scale.name, JOB_SILVER) is False:
            sleep(settle_seconds)
            _repair(JOB_SILVER, spec.scale, spec.sequence, cluster, data_dir, run)
        elif spec.job == JOB_PUBLISH and _last_write_ok(data_dir, spec.scale.name, JOB_GOLD) is False:
            sleep(settle_seconds)
            _repair(JOB_GOLD, spec.scale, spec.sequence, cluster, data_dir, run)
        if item.spec.role == "measured" and _confirmed_deterministic_oom(data_dir, spec):
            attempts = len(_attempt_outcomes(data_dir, spec))
            logger.warning(f"[{index}/{len(plan)}] {spec.run_id}: skipped, {attempts} earlier attempts of this exact configuration all OOM'd (decision D25)")
            records.append(_skip_confirmed_oom(spec, data_dir, attempts))
            continue
        _archive_attempt(record_file)
        sleep(settle_seconds)
        logger.info(f"[{index}/{len(plan)}] {spec.run_id} ({spec.role}, {spec.executors} executors)")
        record = run(spec, cluster, data_dir)
        if record["status"] != "ok" and record.get("failure_reason") != "executor_oom":
            raise CampaignError(f"{spec.run_id} ended with status {record['status']}; see {record_file.parent}/driver.log")
        if record["status"] != "ok":
            logger.warning(f"{spec.run_id}: {record['failure_reason']} (a diagnosed, data-dependent memory ceiling); continuing")
        if item.pg_digest:
            record["pg_digest"] = parse_pg_digest(cluster.psql(pg_digest_sql(spec.scale.pg_schema)))
            record_file.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
        records.append(record)
        logger.info(f"elapsed {(time.time() - started) / 60:.0f} min, {len(plan) - index} runs left")
    return records


def main(argv: Sequence[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s", stream=sys.stdout)
    parser = argparse.ArgumentParser(prog="python -m tfm_lakehouse.benchmark.campaign", description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--scales", nargs="+", default=[f"{f}x" for f in SCALE_FACTORS])
    parser.add_argument("--executors", nargs="+", type=int, default=list(DEFAULT_EXECUTORS))
    parser.add_argument("--repetitions", type=int, default=DEFAULT_REPETITIONS)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--jobs", nargs="+", default=list(MEASURED_JOBS), choices=list(MEASURED_JOBS))
    parser.add_argument("--pilot", action="store_true", help="a pilot: run ids from r901 and role 'pilot' (never counted by the report)")
    parser.add_argument("--dry-run", action="store_true", help="print the plan and exit")
    args = parser.parse_args(argv)
    plan = build_plan(
        args.scales, args.executors, args.repetitions, args.seed, args.jobs,
        first_sequence=901 if args.pilot else 1, measured_role="pilot" if args.pilot else "measured",
    )
    if args.dry_run:
        for item in plan:
            print(f"{item.spec.sequence:3d} {item.spec.run_id:38s} {item.spec.role:8s}{' +pg_digest' if item.pg_digest else ''}")
        print(f"{len(plan)} runs")
        return 0
    execute(plan, Cluster(), args.data_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
