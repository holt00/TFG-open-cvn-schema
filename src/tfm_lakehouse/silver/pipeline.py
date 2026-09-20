"""Turning one bronze line into silver rows (issue #98, D3-D5). Pure Python, no Spark.

The Spark job hands each deduplicated bronze line to ``process_bronze_line``
through a UDF. Keeping it here lets the host test every source end to end
without Spark.
"""

from __future__ import annotations

import json
from typing import Any

from tfm_lakehouse.silver.cvn import process_cvn_document
from tfm_lakehouse.silver.orcid_api import process_orcid_api_record
from tfm_lakehouse.silver.orcid_xml import process_orcid_xml
from tfm_lakehouse.silver.schemas import (
    AFFILIATION_COLUMNS,
    PERSON_COLUMNS,
    PUBLICATION_COLUMNS,
    row_values,
)

SOURCE_ORCID_BULK = "orcid_bulk"
SOURCE_ORCID_API = "orcid_api"
SOURCE_SYNTHETIC_CVN = "synthetic_cvn"
SOURCES = (SOURCE_ORCID_BULK, SOURCE_ORCID_API, SOURCE_SYNTHETIC_CVN)

RULE_ENVELOPE = "bronze_envelope"

# A record that fails in many places must not become a huge row.
_MAX_ERRORS = 20
_MAX_MESSAGE_LENGTH = 1000


def process_bronze_line(source: str, line: str) -> tuple[Any, ...]:
    """Validate and extract one bronze JSON Lines record.

    Args:
        source: The bronze source the line was read from (one of ``SOURCES``).
        line: The line exactly as landed: an envelope with a ``payload``.

    Returns:
        A tuple shaped as ``schemas.RESULT_COLUMNS``: errors (rule, message),
        warnings, person, affiliations, publications. Rejected records have
        errors and no person.
    """
    errors, warnings, person, affiliations, publications = _process(source, line)
    return (
        [(rule, message[:_MAX_MESSAGE_LENGTH]) for rule, message in errors[:_MAX_ERRORS]],
        [warning[:_MAX_MESSAGE_LENGTH] for warning in warnings[:_MAX_ERRORS]],
        row_values(PERSON_COLUMNS, person) if person is not None else None,
        [row_values(AFFILIATION_COLUMNS, row) for row in affiliations],
        [row_values(PUBLICATION_COLUMNS, row) for row in publications],
    )


def _process(source: str, line: str) -> tuple[list[tuple[str, str]], list[str], Any, list, list]:
    try:
        envelope = json.loads(line)
    except ValueError as exc:
        return [(RULE_ENVELOPE, f"the line is not valid JSON: {exc}")], [], None, [], []
    if not isinstance(envelope, dict) or "payload" not in envelope:
        return [(RULE_ENVELOPE, "the line is not an envelope with a payload")], [], None, [], []
    if not isinstance(envelope.get("record_id"), str) or not envelope["record_id"]:
        return [(RULE_ENVELOPE, "the envelope has no record_id")], [], None, [], []
    payload = envelope["payload"]

    if source == SOURCE_SYNTHETIC_CVN:
        result = process_cvn_document(payload)
        return result.errors, result.warnings, result.person, result.affiliations, result.publications
    if source == SOURCE_ORCID_BULK:
        if not isinstance(payload, str):
            return [(RULE_ENVELOPE, "an orcid_bulk payload must be an XML string")], [], None, [], []
        orcid = process_orcid_xml(payload)
    elif source == SOURCE_ORCID_API:
        expected = envelope.get("source_ref")
        orcid = process_orcid_api_record(payload, expected if isinstance(expected, str) else None)
    else:
        raise ValueError(f"unknown bronze source {source!r}")
    return orcid.errors, [], orcid.person, orcid.affiliations, orcid.publications
