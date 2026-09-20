"""Column definitions of the silver tables (issue #98, D6).

Plain data, not ``pyspark`` types: PySpark cannot be imported on the host's
Python 3.14, and a test checks these columns against the dicts that
``records.py`` builds. The job turns them into Spark schemas with
``columns_ddl`` (``StructType.fromDDL`` / ``CREATE TABLE``).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

Column = tuple[str, str]

PROVENANCE_COLUMNS: list[Column] = [
    ("source_snapshot", "STRING"),
    ("retrieved_at", "STRING"),
    ("landed_at", "STRING"),
    ("ingestion_date", "STRING"),
    ("ingestion_run_id", "STRING"),
]

# The columns records.py builds, one list per extracted entity.
PERSON_COLUMNS: list[Column] = [
    ("given_names", "STRING"),
    ("family_name", "STRING"),
    ("given_norm", "STRING"),
    ("family_norm", "STRING"),
    ("family_key", "STRING"),
    ("given_initial", "STRING"),
    ("orcid_id", "STRING"),
    ("source_last_modified", "STRING"),
]
AFFILIATION_COLUMNS: list[Column] = [
    ("kind", "STRING"),
    ("organization", "STRING"),
    ("organization_norm", "STRING"),
    ("role", "STRING"),
    ("department", "STRING"),
    ("city", "STRING"),
    ("country", "STRING"),
    ("start_year", "INT"),
    ("start_month", "INT"),
    ("end_year", "INT"),
    ("end_month", "INT"),
]
PUBLICATION_COLUMNS: list[Column] = [
    ("title", "STRING"),
    ("title_norm", "STRING"),
    ("year", "INT"),
    ("month", "INT"),
    ("doi", "STRING"),
    ("work_type", "STRING"),
    ("authors", "ARRAY<STRING>"),
]

_RECORD_KEY: list[Column] = [("record_id", "STRING")]

TABLE_COLUMNS: dict[str, list[Column]] = {
    "person_record": [
        *_RECORD_KEY,
        ("source", "STRING"),
        ("source_ref", "STRING"),
        *PERSON_COLUMNS,
        *PROVENANCE_COLUMNS,
        ("validation_warnings", "ARRAY<STRING>"),
    ],
    "affiliation": [*_RECORD_KEY, *AFFILIATION_COLUMNS],
    "publication": [*_RECORD_KEY, *PUBLICATION_COLUMNS],
    "entity_link": [
        *_RECORD_KEY,
        ("source", "STRING"),
        ("entity_id", "STRING"),
        ("match_rule", "STRING"),
        ("evidence", "STRING"),
        ("ambiguous", "BOOLEAN"),
        ("name_conflict", "BOOLEAN"),
    ],
    "entity": [
        ("entity_id", "STRING"),
        ("orcid_id", "STRING"),
        ("given_names", "STRING"),
        ("family_name", "STRING"),
        ("record_count", "INT"),
        ("sources", "ARRAY<STRING>"),
        ("rules", "ARRAY<STRING>"),
        ("has_cvn", "BOOLEAN"),
        ("has_orcid", "BOOLEAN"),
    ],
    "rejected": [
        *_RECORD_KEY,
        ("source", "STRING"),
        ("source_ref", "STRING"),
        ("rules", "ARRAY<STRING>"),
        ("errors", "ARRAY<STRING>"),
        *PROVENANCE_COLUMNS,
    ],
}


def column_names(columns: Sequence[Column]) -> list[str]:
    """Return the column names, in order."""
    return [name for name, _ in columns]


def columns_ddl(columns: Sequence[Column]) -> str:
    """Return ``name TYPE, name TYPE`` for ``StructType.fromDDL`` or ``CREATE TABLE``."""
    return ", ".join(f"{name} {type_}" for name, type_ in columns)


def row_values(columns: Sequence[Column], values: Mapping[str, Any]) -> tuple[Any, ...]:
    """Order a dict's values as the columns, so it can be a Spark ``Row`` tuple.

    Raises:
        KeyError: If ``values`` lacks a column; a missing key is a bug, not a null.
    """
    return tuple(values[name] for name in column_names(columns))


def struct_ddl(columns: Sequence[Column]) -> str:
    """Return ``STRUCT<name: TYPE, ...>`` for a nested column of a UDF result."""
    return "STRUCT<" + ", ".join(f"{name}: {type_}" for name, type_ in columns) + ">"


ERROR_COLUMNS: list[Column] = [("rule", "STRING"), ("message", "STRING")]

# What the per-record parsing UDF returns (see pipeline.process_bronze_line).
RESULT_COLUMNS: list[Column] = [
    ("errors", f"ARRAY<{struct_ddl(ERROR_COLUMNS)}>"),
    ("warnings", "ARRAY<STRING>"),
    ("person", struct_ddl(PERSON_COLUMNS)),
    ("affiliations", f"ARRAY<{struct_ddl(AFFILIATION_COLUMNS)}>"),
    ("publications", f"ARRAY<{struct_ddl(PUBLICATION_COLUMNS)}>"),
]
