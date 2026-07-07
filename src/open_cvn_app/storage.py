from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping

from open_cvn.parser_contract import (
    CvnParseIssue,
    CvnValidationStatus,
    validate_open_cvn_json,
)


SCHEMA_VERSION = "1"


class StorageError(RuntimeError):
    """Base error for local Open CVN storage failures."""


class StoreNotInitialized(StorageError):
    """Raised when a SQLite file is not an initialized Open CVN store."""


class IncompatibleStoreSchema(StorageError):
    """Raised when the store schema is newer than this application supports."""


class CurriculumNotFound(StorageError):
    """Raised when a curriculum ID does not exist in the local store."""


class InvalidCurriculumDocument(StorageError):
    """Raised when an Open CVN document fails validation before storage."""


@dataclass(frozen=True)
class StoreInfo:
    path: Path
    schema_version: str


@dataclass(frozen=True)
class CurriculumCreate:
    display_name: str
    document: Mapping[str, Any]
    source_identifier: str | None = None
    diagnostics: tuple[CvnParseIssue, ...] = ()


@dataclass(frozen=True)
class CurriculumUpdate:
    display_name: str | None = None


@dataclass(frozen=True)
class CurriculumDiagnostic:
    id: str
    curriculum_id: str
    severity: str
    code: str
    message: str
    source_location: str | None
    path: tuple[str, ...]
    details: dict[str, str | int | float | bool | None]
    created_at: str


@dataclass(frozen=True)
class CurriculumRecord:
    id: str
    display_name: str
    document: Mapping[str, Any]
    schema_version: str
    policy_name: str
    policy_version: str
    source_format: str
    source_identifier: str | None
    validation_status: str
    created_at: str
    updated_at: str


def initialize_store(path: str | Path) -> StoreInfo:
    store_path = _normalize_store_path(path)
    _ensure_parent_dir(store_path)
    with _connect(store_path) as connection:
        _configure_connection(connection)
        connection.executescript(_SCHEMA_SQL)
        current_version = _read_schema_version(connection)
        if current_version is None:
            connection.execute(
                "INSERT INTO app_metadata(key, value) VALUES (?, ?)",
                ("schema_version", SCHEMA_VERSION),
            )
        elif _schema_version_number(current_version) > _schema_version_number(SCHEMA_VERSION):
            raise IncompatibleStoreSchema(
                f"Store schema version {current_version} is newer than supported {SCHEMA_VERSION}."
            )
        connection.commit()
    return StoreInfo(path=store_path, schema_version=SCHEMA_VERSION)


class CurriculumRepository:
    def __init__(self, path: str | Path) -> None:
        self.path = _normalize_store_path(path)

    def create_curriculum(self, create: CurriculumCreate) -> CurriculumRecord:
        prepared = _prepare_document(
            create.document,
            source_identifier=create.source_identifier,
            diagnostics=create.diagnostics,
        )
        curriculum_id = str(uuid.uuid4())
        now = _utc_now()
        with self._connection() as connection:
            connection.execute(
                """
                INSERT INTO curricula(
                    id,
                    display_name,
                    payload_json,
                    schema_version,
                    policy_name,
                    policy_version,
                    source_format,
                    source_identifier,
                    validation_status,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    curriculum_id,
                    create.display_name,
                    prepared.payload_json,
                    prepared.schema_version,
                    prepared.policy_name,
                    prepared.policy_version,
                    prepared.source_format,
                    prepared.source_identifier,
                    prepared.validation_status,
                    now,
                    now,
                ),
            )
            _replace_diagnostics(
                connection,
                curriculum_id=curriculum_id,
                issues=prepared.issues,
                created_at=now,
            )
            connection.commit()
        return self.get_curriculum(curriculum_id)

    def get_curriculum(self, curriculum_id: str) -> CurriculumRecord:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT * FROM curricula WHERE id = ?",
                (curriculum_id,),
            ).fetchone()
        if row is None:
            raise CurriculumNotFound(f"Curriculum not found: {curriculum_id}")
        return _row_to_record(row)

    def list_curricula(self) -> tuple[CurriculumRecord, ...]:
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT * FROM curricula ORDER BY updated_at DESC, display_name ASC, id ASC"
            ).fetchall()
        return tuple(_row_to_record(row) for row in rows)

    def update_curriculum(self, curriculum_id: str, update: CurriculumUpdate) -> CurriculumRecord:
        existing = self.get_curriculum(curriculum_id)
        display_name = update.display_name if update.display_name is not None else existing.display_name
        now = _utc_now()
        with self._connection() as connection:
            cursor = connection.execute(
                "UPDATE curricula SET display_name = ?, updated_at = ? WHERE id = ?",
                (display_name, now, curriculum_id),
            )
            if cursor.rowcount == 0:
                raise CurriculumNotFound(f"Curriculum not found: {curriculum_id}")
            connection.commit()
        return self.get_curriculum(curriculum_id)

    def replace_curriculum_payload(
        self,
        curriculum_id: str,
        document: Mapping[str, Any],
        *,
        source_identifier: str | None = None,
        diagnostics: tuple[CvnParseIssue, ...] = (),
    ) -> CurriculumRecord:
        prepared = _prepare_document(
            document,
            source_identifier=source_identifier,
            diagnostics=diagnostics,
        )
        now = _utc_now()
        with self._connection() as connection:
            cursor = connection.execute(
                """
                UPDATE curricula
                SET payload_json = ?,
                    schema_version = ?,
                    policy_name = ?,
                    policy_version = ?,
                    source_format = ?,
                    source_identifier = ?,
                    validation_status = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    prepared.payload_json,
                    prepared.schema_version,
                    prepared.policy_name,
                    prepared.policy_version,
                    prepared.source_format,
                    prepared.source_identifier,
                    prepared.validation_status,
                    now,
                    curriculum_id,
                ),
            )
            if cursor.rowcount == 0:
                raise CurriculumNotFound(f"Curriculum not found: {curriculum_id}")
            _replace_diagnostics(
                connection,
                curriculum_id=curriculum_id,
                issues=prepared.issues,
                created_at=now,
            )
            connection.commit()
        return self.get_curriculum(curriculum_id)

    def delete_curriculum(self, curriculum_id: str) -> None:
        with self._connection() as connection:
            cursor = connection.execute("DELETE FROM curricula WHERE id = ?", (curriculum_id,))
            if cursor.rowcount == 0:
                raise CurriculumNotFound(f"Curriculum not found: {curriculum_id}")
            connection.commit()

    def list_diagnostics(self, curriculum_id: str) -> tuple[CurriculumDiagnostic, ...]:
        self.get_curriculum(curriculum_id)
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT * FROM curriculum_diagnostics
                WHERE curriculum_id = ?
                ORDER BY created_at ASC, id ASC
                """,
                (curriculum_id,),
            ).fetchall()
        return tuple(_row_to_diagnostic(row) for row in rows)

    def _connection(self) -> sqlite3.Connection:
        connection = _connect(self.path)
        try:
            _configure_connection(connection)
            _verify_initialized(connection)
        except Exception:
            connection.close()
            raise
        return connection


@dataclass(frozen=True)
class _PreparedDocument:
    payload_json: str
    schema_version: str
    policy_name: str
    policy_version: str
    source_format: str
    source_identifier: str | None
    validation_status: str
    issues: tuple[CvnParseIssue, ...]


def _prepare_document(
    document: Mapping[str, Any], *, source_identifier: str | None, diagnostics: tuple[CvnParseIssue, ...]
) -> _PreparedDocument:
    validation_result = validate_open_cvn_json(document, source_identifier=source_identifier)
    if validation_result.validation_status in {CvnValidationStatus.INVALID, CvnValidationStatus.FAILED}:
        messages = "; ".join(issue.message for issue in validation_result.errors)
        raise InvalidCurriculumDocument(messages or "Open CVN document is invalid.")
    if validation_result.data is None:
        raise InvalidCurriculumDocument("Open CVN validation did not return document data.")

    metadata = validation_result.data["metadata"]
    policy = metadata["policy"]
    payload_json = json.dumps(
        validation_result.data,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return _PreparedDocument(
        payload_json=payload_json,
        schema_version=str(validation_result.data["schema_version"]),
        policy_name=str(policy["name"]),
        policy_version=str(policy["version"]),
        source_format=validation_result.source_format.value,
        source_identifier=validation_result.source_identifier,
        validation_status=validation_result.validation_status.value,
        issues=validation_result.warnings + diagnostics,
    )


def _replace_diagnostics(
    connection: sqlite3.Connection,
    *,
    curriculum_id: str,
    issues: tuple[CvnParseIssue, ...],
    created_at: str,
) -> None:
    connection.execute("DELETE FROM curriculum_diagnostics WHERE curriculum_id = ?", (curriculum_id,))
    connection.executemany(
        """
        INSERT INTO curriculum_diagnostics(
            id,
            curriculum_id,
            severity,
            code,
            message,
            source_location,
            path_json,
            details_json,
            created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            (
                str(uuid.uuid4()),
                curriculum_id,
                issue.severity.value,
                issue.code.value,
                issue.message,
                issue.source_location,
                json.dumps(list(issue.path), ensure_ascii=False, separators=(",", ":")),
                json.dumps(issue.details, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
                created_at,
            )
            for issue in issues
        ),
    )


def _row_to_record(row: sqlite3.Row) -> CurriculumRecord:
    return CurriculumRecord(
        id=row["id"],
        display_name=row["display_name"],
        document=json.loads(row["payload_json"]),
        schema_version=row["schema_version"],
        policy_name=row["policy_name"],
        policy_version=row["policy_version"],
        source_format=row["source_format"],
        source_identifier=row["source_identifier"],
        validation_status=row["validation_status"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _row_to_diagnostic(row: sqlite3.Row) -> CurriculumDiagnostic:
    return CurriculumDiagnostic(
        id=row["id"],
        curriculum_id=row["curriculum_id"],
        severity=row["severity"],
        code=row["code"],
        message=row["message"],
        source_location=row["source_location"],
        path=tuple(json.loads(row["path_json"])),
        details=json.loads(row["details_json"]),
        created_at=row["created_at"],
    )


def _verify_initialized(connection: sqlite3.Connection) -> None:
    schema_version = _read_schema_version(connection)
    if schema_version is None:
        raise StoreNotInitialized("SQLite file is not an initialized Open CVN store.")
    if _schema_version_number(schema_version) > _schema_version_number(SCHEMA_VERSION):
        raise IncompatibleStoreSchema(
            f"Store schema version {schema_version} is newer than supported {SCHEMA_VERSION}."
        )


def _read_schema_version(connection: sqlite3.Connection) -> str | None:
    table_exists = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'app_metadata'"
    ).fetchone()
    if table_exists is None:
        return None
    row = connection.execute(
        "SELECT value FROM app_metadata WHERE key = ?",
        ("schema_version",),
    ).fetchone()
    return None if row is None else str(row["value"])


def _schema_version_number(value: str) -> int:
    try:
        return int(value)
    except ValueError as exc:
        raise IncompatibleStoreSchema(f"Invalid store schema version: {value}") from exc


def _connect(path: Path) -> sqlite3.Connection:
    return sqlite3.connect(path)


def _configure_connection(connection: sqlite3.Connection) -> None:
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")


def _normalize_store_path(path: str | Path) -> Path:
    return Path(path).expanduser()


def _ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS app_metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS curricula (
    id TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    schema_version TEXT NOT NULL,
    policy_name TEXT NOT NULL,
    policy_version TEXT NOT NULL,
    source_format TEXT NOT NULL,
    source_identifier TEXT,
    validation_status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS curriculum_diagnostics (
    id TEXT PRIMARY KEY,
    curriculum_id TEXT NOT NULL,
    severity TEXT NOT NULL,
    code TEXT NOT NULL,
    message TEXT NOT NULL,
    source_location TEXT,
    path_json TEXT NOT NULL,
    details_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (curriculum_id) REFERENCES curricula(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_curricula_display_name ON curricula(display_name);
CREATE INDEX IF NOT EXISTS idx_curricula_updated_at ON curricula(updated_at);
CREATE INDEX IF NOT EXISTS idx_curriculum_diagnostics_curriculum_id
    ON curriculum_diagnostics(curriculum_id);
"""
