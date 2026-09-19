from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from typing import Any

SOURCE_ORCID_BULK = "orcid_bulk"
SOURCE_ORCID_API = "orcid_api"
SOURCE_SYNTHETIC_CVN = "synthetic_cvn"
SOURCES = (SOURCE_ORCID_BULK, SOURCE_ORCID_API, SOURCE_SYNTHETIC_CVN)

PAYLOAD_FORMAT_XML = "xml"
PAYLOAD_FORMAT_JSON = "json"

CHECK_VALID = "valid"
CHECK_INVALID = "invalid"

_RUN_ID_UNSAFE = re.compile(r"[^A-Za-z0-9._-]+")


def utc_timestamp(moment: datetime) -> str:
    return moment.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass(frozen=True)
class RunContext:
    """Identity and clock of one bronze landing run.

    Args:
        run_id: Run identifier, already safe for use in an object key.
        ingestion_date: Date the run landed its data; the partition value.
        landed_at: UTC timestamp of the run, as ``YYYY-MM-DDTHH:MM:SSZ``.
    """

    run_id: str
    ingestion_date: date
    landed_at: str

    @classmethod
    def create(cls, run_id: str, now: datetime | None = None) -> RunContext:
        """Build a context from an Airflow-style run id.

        Airflow run ids contain characters such as ``:`` and ``+``
        (``scheduled__2026-09-19T00:00:00+00:00``); they are replaced with
        ``_`` so the id can be used as an object-key segment and a directory
        name. The mapping is deterministic, so a cleared task re-run keeps its
        run id and replaces its own partition.
        """
        safe = _RUN_ID_UNSAFE.sub("_", run_id).strip("_")
        if not safe:
            raise ValueError(f"run_id {run_id!r} has no usable characters")
        moment = now or datetime.now(UTC)
        return cls(run_id=safe, ingestion_date=moment.astimezone(UTC).date(), landed_at=utc_timestamp(moment))


@dataclass(frozen=True)
class LandingCheck:
    """Outcome of the landing-time structural check of one record."""

    status: str
    errors: tuple[str, ...] = field(default=())

    @property
    def is_valid(self) -> bool:
        return self.status == CHECK_VALID

    def to_dict(self) -> dict[str, Any]:
        return {"status": self.status, "errors": list(self.errors)}


def make_record_id(source: str, source_ref: str) -> str:
    """Stable record identifier: the same source record keeps it across runs."""
    return f"{source}:{source_ref}"


def build_envelope(
    *,
    source: str,
    source_ref: str,
    payload: Any,
    payload_format: str,
    run: RunContext,
    retrieved_at: str,
    source_snapshot: str,
    check: LandingCheck,
    source_files: tuple[str, ...] = (),
    source_artifacts: tuple[dict[str, str], ...] = (),
) -> dict[str, Any]:
    """Wrap one source record with its provenance for landing in bronze.

    ``source_files`` and ``source_artifacts`` reuse the names of the TFG's
    ``trace`` block (docs/pipeline/open_cvn_json_format.md). ``retrieved_at``
    is when the source data was obtained (the subset extraction for the bulk
    file, the request for the API, the generation for synthetic CVN);
    ``landed_at`` is when this run wrote it to bronze.

    Args:
        source: One of ``SOURCES``.
        source_ref: The record's key in its source: an ORCID iD, or a CVN
            document id.
        payload: The record itself, untouched: an XML string or a JSON object.
        payload_format: ``"xml"`` or ``"json"``.
        run: The landing run.
        retrieved_at: UTC timestamp of when the source data was obtained.
        source_snapshot: Identifier of the source version (dataset release,
            API version, or generator run).
        check: Result of the landing-time structural check.
        source_files: Where the record came from, relative to the source.
        source_artifacts: Named artifacts the record derives from (name and
            checksum).

    Returns:
        The envelope as a JSON-serializable dict.
    """
    return {
        "record_id": make_record_id(source, source_ref),
        "source": source,
        "source_ref": source_ref,
        "source_snapshot": source_snapshot,
        "source_files": list(source_files),
        "source_artifacts": [dict(artifact) for artifact in source_artifacts],
        "retrieved_at": retrieved_at,
        "landed_at": run.landed_at,
        "ingestion_date": run.ingestion_date.isoformat(),
        "ingestion_run_id": run.run_id,
        "landing_check": check.to_dict(),
        "payload_format": payload_format,
        "payload": payload,
    }
