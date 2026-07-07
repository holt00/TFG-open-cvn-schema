from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


DEFAULT_STORE_PATH = Path("~/.open-cvn/open_cvn.sqlite")


@dataclass(frozen=True)
class OpenCvnAppConfig:
    """Local application configuration shared by CLI commands."""

    store_path: Path

    @classmethod
    def default(cls) -> OpenCvnAppConfig:
        return cls.from_store_path(DEFAULT_STORE_PATH)

    @classmethod
    def from_store_path(cls, store_path: str | Path | None) -> OpenCvnAppConfig:
        if store_path is None:
            store_path = DEFAULT_STORE_PATH
        return cls(store_path=Path(store_path).expanduser())
