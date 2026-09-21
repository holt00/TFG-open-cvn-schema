"""The cap on Spark containers that run at once (issue #100), checked without Docker or Spark.

``pytest -n auto`` starts one worker per core, and the Spark tests each run a JVM and a Python process in
Docker; sixteen at once starved each other and ended in timeouts. ``spark_slot`` lets only a few run together.
"""

import contextlib
import threading
import time
from pathlib import Path

import pytest

import spark_image
from spark_image import DEFAULT_SLOTS, configured_slots, spark_slot


def _hold_slots(directory: Path, threads: int, slots: int, hold: float = 0.15) -> tuple[int, int]:
    """Run ``threads`` workers that each hold a slot for ``hold`` seconds; return (peak concurrency, finished).

    Every test here uses its own lock directory: sharing the real one would make it compete with the Spark
    tests that other pytest workers are running at the same time.
    """
    lock = threading.Lock()
    state = {"active": 0, "peak": 0, "done": 0}

    def worker() -> None:
        with spark_slot(slots=slots, wait=30, directory=directory):
            with lock:
                state["active"] += 1
                state["peak"] = max(state["peak"], state["active"])
            time.sleep(hold)
            with lock:
                state["active"] -= 1
        with lock:
            state["done"] += 1

    pool = [threading.Thread(target=worker) for _ in range(threads)]
    for thread in pool:
        thread.start()
    for thread in pool:
        thread.join()
    return state["peak"], state["done"]


def test_no_more_workers_than_slots_run_at_once_and_all_of_them_finish(tmp_path):
    peak, done = _hold_slots(tmp_path, threads=8, slots=2)

    assert peak == 2  # the cap is reached, never exceeded
    assert done == 8


def test_a_single_slot_serialises_the_runs(tmp_path):
    peak, done = _hold_slots(tmp_path, threads=4, slots=1, hold=0.05)

    assert (peak, done) == (1, 4)


def test_a_slot_is_released_when_the_block_raises(tmp_path):
    with pytest.raises(RuntimeError):
        with spark_slot(slots=1, wait=5, directory=tmp_path):
            raise RuntimeError("the run failed")

    with spark_slot(slots=1, wait=5, directory=tmp_path) as index:  # would wait until the timeout if it had leaked
        assert index == 0


def test_it_gives_up_with_a_clear_error_when_no_slot_frees_up(tmp_path):
    with spark_slot(slots=1, wait=5, directory=tmp_path):
        with pytest.raises(TimeoutError, match="no Spark test slot"):
            with spark_slot(slots=1, wait=0.6, directory=tmp_path):
                pass


def test_the_number_of_slots_comes_from_the_environment_with_a_safe_default(monkeypatch):
    monkeypatch.delenv("SPARK_TEST_SLOTS", raising=False)
    assert configured_slots() == DEFAULT_SLOTS == 4

    monkeypatch.setenv("SPARK_TEST_SLOTS", "2")
    assert configured_slots() == 2

    for bad in ("0", "-3"):
        monkeypatch.setenv("SPARK_TEST_SLOTS", bad)
        assert configured_slots() == 1  # never zero: nothing would run

    monkeypatch.setenv("SPARK_TEST_SLOTS", "many")
    assert configured_slots() == DEFAULT_SLOTS


def test_an_aborted_run_has_its_container_removed(monkeypatch):
    calls = []

    def fake_run(arguments, **kwargs):
        calls.append(arguments)
        if arguments[:2] == ["docker", "run"]:
            raise spark_image.subprocess.TimeoutExpired(arguments, 1)
        return spark_image.subprocess.CompletedProcess(arguments, 0, "", "")

    monkeypatch.setattr(spark_image.subprocess, "run", fake_run)
    monkeypatch.setattr(spark_image, "spark_slot", lambda: contextlib.nullcontext(0))  # not the real, shared slots

    with pytest.raises(spark_image.subprocess.TimeoutExpired):
        spark_image.run_in_image(["true"], {}, timeout=1)

    run_call, remove_call = calls
    name = run_call[run_call.index("--name") + 1]
    assert name.startswith("tfm-spark-test-")
    assert remove_call == ["docker", "rm", "-f", name]  # killing the client alone would leave it running
