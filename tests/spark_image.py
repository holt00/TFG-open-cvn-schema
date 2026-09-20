"""Runs commands in the project's Spark image, for the tests that need PySpark (issue #98).

PySpark cannot be installed on the host's Python 3.14, so those tests execute
inside the image, in local mode. They skip themselves without Docker or the image.
"""

import os
import shutil
import subprocess
from pathlib import Path

IMAGE = "tfm-lakehouse/spark-py:3.5.9-iceberg1.11.0-silver"
REPO = Path(__file__).resolve().parents[1]


def image_available() -> bool:
    if shutil.which("docker") is None:
        return False
    return subprocess.run(["docker", "image", "inspect", IMAGE], capture_output=True).returncode == 0


def run_in_image(command: list[str], mounts: dict[Path, str], *, timeout: int = 900) -> subprocess.CompletedProcess:
    """Run ``command`` in the image as the host user, through its entrypoint.

    The entrypoint is what registers the arbitrary uid in /etc/passwd; going
    around it makes the JVM fail with ``basedir must be absolute: ?/.ivy2``
    (the same root cause issue #93 recorded). Running as the host uid (group 0,
    which owns /etc/passwd's write bit in the image) makes the files the container
    writes to a mounted directory deletable by pytest's tmp-dir cleanup; as the
    image's uid 185 they were not.

    Args:
        command: The command and its arguments.
        mounts: Host directory -> container path. ``src/`` and ``schemas/`` are
            always mounted read-only at ``/repo``.
        timeout: Seconds before the run is aborted.
    """
    volumes = [f"{REPO / 'src'}:/repo/src:ro", f"{REPO / 'schemas'}:/repo/schemas:ro"]
    volumes += [f"{host}:{container}" for host, container in mounts.items()]
    arguments = ["docker", "run", "--rm", "--user", f"{os.getuid()}:0", "--entrypoint", "/opt/entrypoint.sh", "-e", "HOME=/tmp"]
    for volume in volumes:
        arguments += ["-v", volume]
    return subprocess.run([*arguments, IMAGE, *command], capture_output=True, text=True, timeout=timeout)
