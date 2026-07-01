from contextlib import contextmanager
from pathlib import Path
from typing import Iterator
import fcntl

from cvn_codegen.xsdata_runner import XSDTargetSpec, run_xsdata_generation_per_target


REPO_ROOT = Path(__file__).resolve().parent.parent
LOCK_PATH = REPO_ROOT / ".pytest_cache" / "xsdata_generation.lock"


@contextmanager
def locked_xsdata_generation() -> Iterator[None]:
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOCK_PATH.open("w", encoding="utf-8") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def run_xsdata_generation_per_target_locked(target: XSDTargetSpec) -> None:
    with locked_xsdata_generation():
        run_xsdata_generation_per_target(target)
