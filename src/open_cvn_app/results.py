from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AppResult:
    """Result returned by application command handlers."""

    exit_code: int
    message: str
    error: str | None = None

    @classmethod
    def ok(cls, message: str) -> AppResult:
        return cls(exit_code=0, message=message)

    @classmethod
    def failed(cls, message: str, *, exit_code: int = 1, error: str | None = None) -> AppResult:
        return cls(exit_code=exit_code, message=message, error=error)
