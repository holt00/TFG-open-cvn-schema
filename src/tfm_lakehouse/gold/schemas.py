"""Column definitions of the gold tables and the PostgreSQL SQL that publishes them (issue #99).

Plain data and string builders, not ``pyspark`` types: PySpark cannot be imported on
the host's Python 3.14, and everything here is checked by host tests. The same column
list defines the Iceberg table (``lakehouse.gold.<table>``, Spark DDL types) and its
PostgreSQL mirror (``gold.<table>``, the types of ``PG_TYPES``).

Publishing (decision D5) never touches the published tables until every table has
been staged: each is created empty with explicit DDL as ``_new_<table>`` (types, primary
key, indexes), Spark appends the rows into it, and one transaction drops the published
tables and renames the staging ones (``swap_statements``).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

Column = tuple[str, str]

DIM_RESEARCHER = "dim_researcher"
PUBLICATIONS_PER_RESEARCHER_YEAR = "publications_per_researcher_year"
AFFILIATION_TIMELINE = "affiliation_timeline"
COLLABORATION_PAIRS = "collaboration_pairs"
GOLD_RUN = "gold_run"

# Order in which tables are written and published.
TABLES: list[str] = [
    DIM_RESEARCHER,
    PUBLICATIONS_PER_RESEARCHER_YEAR,
    AFFILIATION_TIMELINE,
    COLLABORATION_PAIRS,
    GOLD_RUN,
]

TABLE_COLUMNS: dict[str, list[Column]] = {
    DIM_RESEARCHER: [
        ("entity_id", "STRING"),
        ("given_names", "STRING"),
        ("family_name", "STRING"),
        ("display_name", "STRING"),
        ("orcid_id", "STRING"),
        ("sources", "STRING"),
        ("has_cvn", "BOOLEAN"),
        ("has_orcid", "BOOLEAN"),
        ("record_count", "INT"),
        ("publication_count", "INT"),
        ("first_publication_year", "INT"),
        ("last_publication_year", "INT"),
        ("organization_count", "INT"),
        ("career_start_year", "INT"),
        ("career_last_year", "INT"),
        ("career_span_years", "INT"),
    ],
    PUBLICATIONS_PER_RESEARCHER_YEAR: [
        ("entity_id", "STRING"),
        ("year", "INT"),
        ("publication_count", "INT"),
    ],
    AFFILIATION_TIMELINE: [
        ("entity_id", "STRING"),
        ("kind", "STRING"),
        ("organization", "STRING"),
        ("organization_norm", "STRING"),
        ("role", "STRING"),
        ("start_year", "INT"),
        ("end_year", "INT"),
    ],
    COLLABORATION_PAIRS: [
        ("entity_a", "STRING"),
        ("entity_b", "STRING"),
        ("shared_publications", "INT"),
        ("first_year", "INT"),
        ("last_year", "INT"),
        ("has_cvn_member", "BOOLEAN"),
    ],
    GOLD_RUN: [
        ("run_id", "STRING"),
        ("computed_at", "TIMESTAMP"),
        ("max_year", "INT"),
        ("max_entities_per_doi", "INT"),
        ("silver_snapshots", "STRING"),
        ("entities", "BIGINT"),
        ("entities_with_publications", "BIGINT"),
        ("publication_rows_read", "BIGINT"),
        ("publications_distinct", "BIGINT"),
        ("publications_without_year", "BIGINT"),
        ("affiliation_rows_read", "BIGINT"),
        ("timeline_rows", "BIGINT"),
        ("per_year_rows", "BIGINT"),
        ("collaboration_pairs", "BIGINT"),
        ("dois_excluded_too_many_entities", "BIGINT"),
    ],
}

# Primary keys double as a check that gold has no duplicate rows. The affiliation
# timeline has none: its grouping key contains nullable years.
PRIMARY_KEYS: dict[str, list[str]] = {
    DIM_RESEARCHER: ["entity_id"],
    PUBLICATIONS_PER_RESEARCHER_YEAR: ["entity_id", "year"],
    COLLABORATION_PAIRS: ["entity_a", "entity_b"],
    GOLD_RUN: ["run_id"],
}

# Secondary indexes, on the columns a dashboard filters or joins by.
INDEXES: dict[str, list[list[str]]] = {
    PUBLICATIONS_PER_RESEARCHER_YEAR: [["year"]],
    AFFILIATION_TIMELINE: [["entity_id"], ["organization_norm"]],
    COLLABORATION_PAIRS: [["entity_b"]],
}

# Spark DDL type -> PostgreSQL type. Spark would create ``timestamp without time zone``
# on its own; the explicit DDL keeps the zone (issue #99, Task 1.5).
PG_TYPES: dict[str, str] = {
    "STRING": "TEXT",
    "INT": "INTEGER",
    "BIGINT": "BIGINT",
    "BOOLEAN": "BOOLEAN",
    "TIMESTAMP": "TIMESTAMPTZ",
}

STAGING_PREFIX = "_new_"
# PostgreSQL truncates longer identifiers silently, which would break the renames.
MAX_IDENTIFIER_LENGTH = 63


def column_names(columns: Sequence[Column]) -> list[str]:
    """Return the column names, in order."""
    return [name for name, _ in columns]


def columns_ddl(columns: Sequence[Column]) -> str:
    """Return ``name TYPE, name TYPE`` for ``StructType.fromDDL`` or ``CREATE TABLE``."""
    return ", ".join(f"{name} {type_}" for name, type_ in columns)


def quote_ident(name: str) -> str:
    """Quote a PostgreSQL identifier."""
    return '"' + name.replace('"', '""') + '"'


def staging_name(table: str) -> str:
    """Name of the table a publish stages ``table`` into."""
    return f"{STAGING_PREFIX}{table}"


def pkey_name(table: str) -> str:
    """Final name of a table's primary-key constraint (and its index)."""
    return f"{table}_pkey"


def index_name(table: str, columns: Sequence[str]) -> str:
    """Final name of a secondary index."""
    return f"{table}_{'_'.join(columns)}_idx"


def _qualified(schema: str, name: str) -> str:
    return f"{quote_ident(schema)}.{quote_ident(name)}"


def create_staging_sql(schema: str, table: str) -> str:
    """Return the ``CREATE TABLE`` of a table's staging copy, with its primary key.

    Raises:
        KeyError: If ``table`` is not a gold table.
    """
    primary_key = PRIMARY_KEYS.get(table, [])
    definitions = [
        f"{quote_ident(name)} {PG_TYPES[type_]}{' NOT NULL' if name in primary_key else ''}"
        for name, type_ in TABLE_COLUMNS[table]
    ]
    if primary_key:
        columns = ", ".join(quote_ident(name) for name in primary_key)
        definitions.append(f"CONSTRAINT {quote_ident(staging_name(pkey_name(table)))} PRIMARY KEY ({columns})")
    return f"CREATE TABLE {_qualified(schema, staging_name(table))} ({', '.join(definitions)})"


def create_index_statements(schema: str, table: str) -> list[str]:
    """Return the ``CREATE INDEX`` statements of a table's staging copy."""
    statements = []
    for columns in INDEXES.get(table, []):
        listed = ", ".join(quote_ident(name) for name in columns)
        statements.append(
            f"CREATE INDEX {quote_ident(staging_name(index_name(table, columns)))} "
            f"ON {_qualified(schema, staging_name(table))} ({listed})"
        )
    return statements


def prepare_statements(schema: str, tables: Sequence[str] = TABLES) -> list[str]:
    """Return the statements that leave an empty staging table per gold table.

    Run before Spark appends the rows. A staging table left by a failed publish is
    dropped first, so a retry starts clean; the published tables are not touched.
    """
    statements = [f"CREATE SCHEMA IF NOT EXISTS {quote_ident(schema)}"]
    for table in tables:
        statements.append(f"DROP TABLE IF EXISTS {_qualified(schema, staging_name(table))}")
        statements.append(create_staging_sql(schema, table))
    return statements


def index_statements(schema: str, tables: Sequence[str] = TABLES) -> list[str]:
    """Return the secondary-index statements of every staging table (run after the load)."""
    return [statement for table in tables for statement in create_index_statements(schema, table)]


def swap_statements(schema: str, tables: Sequence[str] = TABLES) -> list[str]:
    """Return the statements that replace the published tables by the staged ones.

    They must run in ONE transaction: a reader sees either the old tables or the new
    ones, never a missing or half-loaded table. A renamed table keeps its staging
    index names, which would collide with the next publish's staging tables, so the
    primary-key and secondary indexes are renamed to their final names too.
    """
    statements: list[str] = []
    for table in tables:
        statements.append(f"DROP TABLE IF EXISTS {_qualified(schema, table)}")
        statements.append(f"ALTER TABLE {_qualified(schema, staging_name(table))} RENAME TO {quote_ident(table)}")
        if PRIMARY_KEYS.get(table):
            statements.append(
                f"ALTER INDEX {_qualified(schema, staging_name(pkey_name(table)))} RENAME TO {quote_ident(pkey_name(table))}"
            )
        for columns in INDEXES.get(table, []):
            statements.append(
                f"ALTER INDEX {_qualified(schema, staging_name(index_name(table, columns)))} "
                f"RENAME TO {quote_ident(index_name(table, columns))}"
            )
    return statements


def cleanup_statements(schema: str, tables: Sequence[str] = TABLES) -> list[str]:
    """Return the statements that drop any staging table (after a failed publish)."""
    return [f"DROP TABLE IF EXISTS {_qualified(schema, staging_name(table))}" for table in tables]


def all_identifiers(tables: Sequence[str] = TABLES) -> list[str]:
    """Every table, staging table, primary-key and index name the publish creates."""
    names: list[str] = []
    for table in tables:
        names += [table, staging_name(table)]
        if PRIMARY_KEYS.get(table):
            names += [pkey_name(table), staging_name(pkey_name(table))]
        for columns in INDEXES.get(table, []):
            names += [index_name(table, columns), staging_name(index_name(table, columns))]
    return names


def row_values(columns: Sequence[Column], values: Mapping[str, object]) -> tuple[object, ...]:
    """Order a dict's values as the columns, so it can be a Spark ``Row`` tuple.

    Raises:
        KeyError: If ``values`` lacks a column; a missing key is a bug, not a null.
    """
    return tuple(values[name] for name in column_names(columns))
