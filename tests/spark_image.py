"""Runs commands in the project's Spark image, for the tests that need PySpark (issue #98).

PySpark cannot be installed on the host's Python 3.14, so those tests execute
inside the image, in local mode. They skip themselves without Docker or the image.

Each run is a JVM plus a Python process, so ``pytest -n auto`` (one worker per core) used to start
up to 16 of them at once and starve them: runs ended in ``TimeoutExpired`` or in ``CANNOT_OPEN_SOCKET``
(the Python process reached the JVM's socket too late), with no assertion failing (issue #100). The
number of containers running at the same time is therefore capped, across all xdist workers, by a
set of lock files (``spark_slot``).
"""

import contextlib
import fcntl
import os
import random
import shutil
import subprocess
import tempfile
import time
import uuid
from collections.abc import Iterator
from pathlib import Path

IMAGE = "tfm-lakehouse/spark-py:3.5.9-iceberg1.11.0-silver"
# The silver image plus the PostgreSQL JDBC driver (issue #99).
GOLD_IMAGE = "tfm-lakehouse/spark-py:3.5.9-iceberg1.11.0-gold"
POSTGRES_IMAGE = "postgres:17"
REPO = Path(__file__).resolve().parents[1]

# Spark containers allowed to run at once. Four ran the 17 Spark tests in 5 min 20 s on a 16-core machine
# (issue #100); override with SPARK_TEST_SLOTS.
DEFAULT_SLOTS = 4
SLOT_WAIT_SECONDS = 7200.0


def configured_slots() -> int:
    """Number of Spark containers that may run at once (``SPARK_TEST_SLOTS``, default 4, at least 1)."""
    try:
        return max(1, int(os.environ.get("SPARK_TEST_SLOTS", DEFAULT_SLOTS)))
    except ValueError:
        return DEFAULT_SLOTS


@contextlib.contextmanager
def spark_slot(slots: int | None = None, wait: float = SLOT_WAIT_SECONDS, directory: Path | None = None) -> Iterator[int]:
    """Hold one of ``slots`` cross-process slots for the duration of the block.

    A slot is an exclusive ``flock`` on a lock file, so it is shared by every pytest worker of
    this user and released by the operating system if a worker dies.

    Args:
        slots: Number of slots; defaults to ``configured_slots()``.
        wait: Seconds to wait for a free slot before giving up.
        directory: Where the lock files live; defaults to a folder in the temp directory shared by all
            workers. Only the tests of this mechanism pass another one, so they do not compete with real runs.

    Yields:
        The index of the slot held.

    Raises:
        TimeoutError: If no slot became free within ``wait`` seconds.
    """
    count = max(1, slots if slots is not None else configured_slots())
    directory = directory or Path(tempfile.gettempdir()) / f"tfm-spark-test-slots-{os.getuid()}"
    directory.mkdir(exist_ok=True)
    deadline = time.monotonic() + wait
    while True:
        for index in range(count):
            handle = open(directory / f"slot-{index}.lock", "w")
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                handle.close()
                continue
            try:
                yield index
            finally:
                fcntl.flock(handle, fcntl.LOCK_UN)
                handle.close()
            return
        if time.monotonic() > deadline:
            raise TimeoutError(f"no Spark test slot became free within {wait:.0f} s")
        time.sleep(random.uniform(0.2, 0.6))


def image_available(image: str = IMAGE) -> bool:
    if shutil.which("docker") is None:
        return False
    return subprocess.run(["docker", "image", "inspect", image], capture_output=True).returncode == 0


def run_in_image(
    command: list[str],
    mounts: dict[Path, str],
    *,
    timeout: int = 900,
    image: str = IMAGE,
    network: str | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    """Run ``command`` in the image as the host user, through its entrypoint.

    The entrypoint is what registers the arbitrary uid in /etc/passwd; going
    around it makes the JVM fail with ``basedir must be absolute: ?/.ivy2``
    (the same root cause issue #93 recorded). Running as the host uid (group 0,
    which owns /etc/passwd's write bit in the image) makes the files the container
    writes to a mounted directory deletable by pytest's tmp-dir cleanup; as the
    image's uid 185 they were not.

    Args:
        command: The command and its arguments.
        mounts: Host directory -> container path. ``src/``, ``schemas/`` and
            ``tests/`` are always mounted read-only at ``/repo``.
        timeout: Seconds before the run is aborted (counted from the start of the run, not from the
            wait for a free slot). An aborted run's container is removed.
        image: The image to run (``IMAGE`` or ``GOLD_IMAGE``).
        network: A Docker network to join (the publish test reaches its PostgreSQL by name).
        env: Extra environment variables of the container.
    """
    volumes = [f"{REPO / 'src'}:/repo/src:ro", f"{REPO / 'schemas'}:/repo/schemas:ro", f"{REPO / 'tests'}:/repo/tests:ro"]
    volumes += [f"{host}:{container}" for host, container in mounts.items()]
    name = f"tfm-spark-test-{uuid.uuid4().hex[:12]}"
    arguments = ["docker", "run", "--rm", "--name", name, "--user", f"{os.getuid()}:0", "--entrypoint", "/opt/entrypoint.sh", "-e", "HOME=/tmp"]
    for volume in volumes:
        arguments += ["-v", volume]
    if network:
        arguments += ["--network", network]
    for name, value in (env or {}).items():
        arguments += ["-e", f"{name}={value}"]
    with spark_slot():
        try:
            return subprocess.run([*arguments, image, *command], capture_output=True, text=True, timeout=timeout)
        except BaseException:
            # killing the docker client (a timeout, Ctrl-C) leaves the container running and loading the machine
            subprocess.run(["docker", "rm", "-f", name], capture_output=True)
            raise
