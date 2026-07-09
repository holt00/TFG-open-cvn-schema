from __future__ import annotations

import json
import sqlite3
import uuid
from collections.abc import MutableMapping
from copy import deepcopy
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping

from open_cvn.parser_contract import (
    CvnParseIssue,
    CvnValidationStatus,
    validate_open_cvn_json,
)


SCHEMA_VERSION = "2"


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


class CurriculumVersionNotFound(StorageError):
    """Raised when a curriculum version ID or name does not exist."""


class MasterCurriculumNotFound(StorageError):
    """Raised when a derived operation needs a master version that does not exist."""


class DuplicateCurriculumVersionName(StorageError):
    """Raised when a version name already exists in the local store."""


class InvalidSelectionRule(StorageError):
    """Raised when a derived-version selection rule is invalid."""


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


@dataclass(frozen=True)
class DerivedSelection:
    mode: str = "include_all"
    included_pointers: tuple[str, ...] = ()
    excluded_pointers: tuple[str, ...] = ()
    metadata: Mapping[str, str] | None = None


@dataclass(frozen=True)
class CurriculumVersionRecord:
    id: str
    name: str
    kind: str
    master_curriculum_id: str
    source_version_id: str | None
    selection: DerivedSelection
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class MaterializedVersion:
    version: CurriculumVersionRecord
    document: Mapping[str, Any]
    validation_status: str


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
        elif _schema_version_number(current_version) < _schema_version_number(SCHEMA_VERSION):
            _migrate_schema(connection, current_version)
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

    def assign_master_curriculum(self, curriculum_id: str, *, name: str = "master") -> CurriculumVersionRecord:
        self.get_curriculum(curriculum_id)
        selection = DerivedSelection()
        version_id = str(uuid.uuid4())
        now = _utc_now()
        with self._connection() as connection:
            existing_master = connection.execute(
                "SELECT id FROM curriculum_versions WHERE kind = ?",
                ("master",),
            ).fetchone()
            if existing_master is not None:
                raise DuplicateCurriculumVersionName("A master curriculum version already exists.")
            try:
                connection.execute(
                    """
                    INSERT INTO curriculum_versions(
                        id,
                        name,
                        kind,
                        master_curriculum_id,
                        source_version_id,
                        selection_json,
                        created_at,
                        updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        version_id,
                        name,
                        "master",
                        curriculum_id,
                        None,
                        _selection_to_json(selection),
                        now,
                        now,
                    ),
                )
            except sqlite3.IntegrityError as exc:
                raise DuplicateCurriculumVersionName(f"Curriculum version already exists: {name}") from exc
            connection.commit()
        return self.get_version(version_id)

    def get_master_version(self) -> CurriculumVersionRecord:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT * FROM curriculum_versions WHERE kind = ?",
                ("master",),
            ).fetchone()
        if row is None:
            raise MasterCurriculumNotFound("Master curriculum version has not been assigned.")
        return _row_to_version(row)

    def get_version(self, version: str) -> CurriculumVersionRecord:
        with self._connection() as connection:
            row = _fetch_version_row(connection, version)
        if row is None:
            raise CurriculumVersionNotFound(f"Curriculum version not found: {version}")
        return _row_to_version(row)

    def list_versions(self) -> tuple[CurriculumVersionRecord, ...]:
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT * FROM curriculum_versions
                ORDER BY CASE kind WHEN 'master' THEN 0 ELSE 1 END,
                         updated_at DESC,
                         name ASC,
                         id ASC
                """
            ).fetchall()
        return tuple(_row_to_version(row) for row in rows)

    def create_derived_version(self, name: str, *, source: str = "master") -> CurriculumVersionRecord:
        with self._connection() as connection:
            source_row = _fetch_version_row(connection, source)
            if source_row is None:
                if source == "master":
                    raise MasterCurriculumNotFound("Master curriculum version has not been assigned.")
                raise CurriculumVersionNotFound(f"Curriculum version not found: {source}")
            source_version = _row_to_version(source_row)
            version_id = str(uuid.uuid4())
            now = _utc_now()
            try:
                connection.execute(
                    """
                    INSERT INTO curriculum_versions(
                        id,
                        name,
                        kind,
                        master_curriculum_id,
                        source_version_id,
                        selection_json,
                        created_at,
                        updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        version_id,
                        name,
                        "derived",
                        source_version.master_curriculum_id,
                        source_version.id,
                        _selection_to_json(source_version.selection),
                        now,
                        now,
                    ),
                )
            except sqlite3.IntegrityError as exc:
                raise DuplicateCurriculumVersionName(f"Curriculum version already exists: {name}") from exc
            connection.commit()
        return self.get_version(version_id)

    def include_in_version(self, version: str, pointer: str) -> CurriculumVersionRecord:
        return self._update_selection(version, pointer, include=True)

    def exclude_from_version(self, version: str, pointer: str) -> CurriculumVersionRecord:
        return self._update_selection(version, pointer, include=False)

    def update_version_metadata(
        self,
        version: str,
        *,
        display_name: str | None = None,
        purpose: str | None = None,
    ) -> CurriculumVersionRecord:
        with self._connection() as connection:
            row = _fetch_version_row(connection, version)
            if row is None:
                raise CurriculumVersionNotFound(f"Curriculum version not found: {version}")
            version_record = _row_to_version(row)
            if version_record.kind == "master":
                raise InvalidSelectionRule("Master curriculum version metadata cannot be edited.")
            metadata = dict(version_record.selection.metadata or {})
            if display_name is not None:
                _set_or_remove_metadata(metadata, "display_name", display_name)
            if purpose is not None:
                _set_or_remove_metadata(metadata, "purpose", purpose)
            selection = DerivedSelection(
                mode=version_record.selection.mode,
                included_pointers=version_record.selection.included_pointers,
                excluded_pointers=version_record.selection.excluded_pointers,
                metadata=metadata,
            )
            now = _utc_now()
            connection.execute(
                "UPDATE curriculum_versions SET selection_json = ?, updated_at = ? WHERE id = ?",
                (_selection_to_json(selection), now, version_record.id),
            )
            connection.commit()
        updated = self.get_version(version_record.id)
        self.materialize_version(updated.id)
        return updated

    def materialize_version(self, version: str) -> MaterializedVersion:
        version_record = self.get_version(version)
        master = self.get_curriculum(version_record.master_curriculum_id)
        document = deepcopy(master.document)

        if version_record.kind == "derived":
            _apply_selection(document, version_record.selection, master.document)

        extensions = document.setdefault("extensions", {})
        if not isinstance(extensions, MutableMapping):
            raise InvalidSelectionRule("Open CVN extensions field must be an object for versioning metadata.")
        extensions["x-open-cvn.versioning"] = {
            "version_id": version_record.id,
            "version_name": version_record.name,
            "version_kind": version_record.kind,
            "master_curriculum_id": version_record.master_curriculum_id,
            "source_version_id": version_record.source_version_id,
            "selection": _selection_to_data(version_record.selection),
        }
        if version_record.selection.metadata:
            extensions["x-open-cvn.versioning"]["metadata"] = dict(version_record.selection.metadata)

        validation_result = validate_open_cvn_json(document, source_identifier=f"version:{version_record.name}")
        if validation_result.validation_status in {CvnValidationStatus.INVALID, CvnValidationStatus.FAILED}:
            messages = "; ".join(issue.message for issue in validation_result.errors)
            raise InvalidSelectionRule(messages or "Materialized Open CVN document is invalid.")
        if validation_result.data is None:
            raise InvalidSelectionRule("Materialized Open CVN validation did not return document data.")
        return MaterializedVersion(
            version=version_record,
            document=validation_result.data,
            validation_status=validation_result.validation_status.value,
        )

    def _update_selection(self, version: str, pointer: str, *, include: bool) -> CurriculumVersionRecord:
        _validate_selection_pointer(pointer)
        with self._connection() as connection:
            row = _fetch_version_row(connection, version)
            if row is None:
                raise CurriculumVersionNotFound(f"Curriculum version not found: {version}")
            version_record = _row_to_version(row)
            if version_record.kind == "master":
                raise InvalidSelectionRule("Master curriculum version selection cannot be edited.")
            master_row = connection.execute(
                "SELECT * FROM curricula WHERE id = ?",
                (version_record.master_curriculum_id,),
            ).fetchone()
            if master_row is None:
                raise CurriculumNotFound(f"Curriculum not found: {version_record.master_curriculum_id}")
            master_document = _row_to_record(master_row).document
            _resolve_json_pointer(master_document, pointer)
            selection = _change_selection(version_record.selection, pointer, include=include)
            now = _utc_now()
            connection.execute(
                "UPDATE curriculum_versions SET selection_json = ?, updated_at = ? WHERE id = ?",
                (_selection_to_json(selection), now, version_record.id),
            )
            connection.commit()
        return self.get_version(version_record.id)

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


def _row_to_version(row: sqlite3.Row) -> CurriculumVersionRecord:
    return CurriculumVersionRecord(
        id=row["id"],
        name=row["name"],
        kind=row["kind"],
        master_curriculum_id=row["master_curriculum_id"],
        source_version_id=row["source_version_id"],
        selection=_selection_from_json(row["selection_json"]),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _fetch_version_row(connection: sqlite3.Connection, version: str) -> sqlite3.Row | None:
    return connection.execute(
        "SELECT * FROM curriculum_versions WHERE id = ? OR name = ?",
        (version, version),
    ).fetchone()


def _selection_from_json(value: str) -> DerivedSelection:
    data = json.loads(value)
    raw_metadata = data.get("metadata") or {}
    if not isinstance(raw_metadata, Mapping):
        raise InvalidSelectionRule("Selection metadata must be an object.")
    selection = DerivedSelection(
        mode=str(data.get("mode", "include_all")),
        included_pointers=tuple(str(pointer) for pointer in data.get("included_pointers", ())),
        excluded_pointers=tuple(str(pointer) for pointer in data.get("excluded_pointers", ())),
        metadata={str(key): str(value) for key, value in raw_metadata.items()},
    )
    _validate_selection(selection)
    return selection


def _selection_to_json(selection: DerivedSelection) -> str:
    _validate_selection(selection)
    return json.dumps(_selection_to_data(selection), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _selection_to_data(selection: DerivedSelection) -> dict[str, Any]:
    data = {
        "mode": selection.mode,
        "included_pointers": list(selection.included_pointers),
        "excluded_pointers": list(selection.excluded_pointers),
    }
    if selection.metadata:
        data["metadata"] = dict(sorted(selection.metadata.items()))
    return data


def _validate_selection(selection: DerivedSelection) -> None:
    if selection.mode not in {"include_all", "include_only"}:
        raise InvalidSelectionRule(f"Unsupported selection mode: {selection.mode}")
    for pointer in selection.included_pointers + selection.excluded_pointers:
        _validate_selection_pointer(pointer)
    if selection.metadata is not None:
        for key, value in selection.metadata.items():
            if key not in {"display_name", "purpose"}:
                raise InvalidSelectionRule(f"Unsupported version metadata key: {key}")
            if not isinstance(value, str):
                raise InvalidSelectionRule(f"Version metadata value must be a string: {key}")


def _set_or_remove_metadata(metadata: dict[str, str], key: str, value: str) -> None:
    clean_value = value.strip()
    if clean_value:
        metadata[key] = clean_value
    else:
        metadata.pop(key, None)


def _validate_selection_pointer(pointer: str) -> None:
    if pointer == "/curriculum":
        raise InvalidSelectionRule("Selection pointer must target a curriculum section or entry, not /curriculum.")
    if not pointer.startswith("/curriculum/"):
        raise InvalidSelectionRule(f"Selection pointer must target /curriculum: {pointer}")
    for token in pointer.split("/")[1:]:
        if "~" in token.replace("~0", "").replace("~1", ""):
            raise InvalidSelectionRule(f"Invalid JSON Pointer escape sequence: {pointer}")


def _change_selection(selection: DerivedSelection, pointer: str, *, include: bool) -> DerivedSelection:
    included = list(selection.included_pointers)
    excluded = list(selection.excluded_pointers)
    if selection.mode == "include_all":
        if include:
            excluded = [item for item in excluded if item != pointer]
        elif pointer not in excluded:
            excluded.append(pointer)
    else:
        if include and pointer not in included:
            included.append(pointer)
        elif not include:
            included = [item for item in included if item != pointer]
    return DerivedSelection(
        mode=selection.mode,
        included_pointers=tuple(sorted(included)),
        excluded_pointers=tuple(sorted(excluded)),
        metadata=selection.metadata,
    )


def _apply_selection(document: MutableMapping[str, Any], selection: DerivedSelection, master_document: Mapping[str, Any]) -> None:
    if selection.mode == "include_all":
        for pointer in selection.excluded_pointers:
            _remove_json_pointer(document, pointer)
        return

    empty_document = {
        "schema_version": document["schema_version"],
        "metadata": deepcopy(document["metadata"]),
        "curriculum": {},
    }
    if "extensions" in document:
        empty_document["extensions"] = deepcopy(document["extensions"])
    for pointer in selection.included_pointers:
        value = deepcopy(_resolve_json_pointer(master_document, pointer))
        _set_json_pointer(empty_document, pointer, value)
    document.clear()
    document.update(empty_document)


def _resolve_json_pointer(document: Mapping[str, Any] | list[Any], pointer: str) -> Any:
    current: Any = document
    for token in _json_pointer_tokens(pointer):
        if isinstance(current, Mapping):
            if token not in current:
                raise InvalidSelectionRule(f"Selection pointer does not resolve: {pointer}")
            current = current[token]
        elif isinstance(current, list):
            if not token.isdigit():
                raise InvalidSelectionRule(f"Selection pointer list token is not an index: {pointer}")
            index = int(token)
            if index >= len(current):
                raise InvalidSelectionRule(f"Selection pointer index is out of range: {pointer}")
            current = current[index]
        else:
            raise InvalidSelectionRule(f"Selection pointer does not resolve: {pointer}")
    return current


def _remove_json_pointer(document: MutableMapping[str, Any] | list[Any], pointer: str) -> None:
    tokens = _json_pointer_tokens(pointer)
    if not tokens:
        raise InvalidSelectionRule("Cannot remove the root document.")
    parent = _resolve_json_pointer_tokens(document, tokens[:-1], pointer)
    token = tokens[-1]
    if isinstance(parent, MutableMapping):
        if token not in parent:
            raise InvalidSelectionRule(f"Selection pointer does not resolve: {pointer}")
        del parent[token]
        return
    if isinstance(parent, list):
        if not token.isdigit():
            raise InvalidSelectionRule(f"Selection pointer list token is not an index: {pointer}")
        index = int(token)
        if index >= len(parent):
            raise InvalidSelectionRule(f"Selection pointer index is out of range: {pointer}")
        del parent[index]
        return
    raise InvalidSelectionRule(f"Selection pointer does not resolve: {pointer}")


def _resolve_json_pointer_tokens(document: Mapping[str, Any] | list[Any], tokens: tuple[str, ...], pointer: str) -> Any:
    current: Any = document
    for token in tokens:
        if isinstance(current, Mapping):
            if token not in current:
                raise InvalidSelectionRule(f"Selection pointer does not resolve: {pointer}")
            current = current[token]
        elif isinstance(current, list):
            if not token.isdigit():
                raise InvalidSelectionRule(f"Selection pointer list token is not an index: {pointer}")
            index = int(token)
            if index >= len(current):
                raise InvalidSelectionRule(f"Selection pointer index is out of range: {pointer}")
            current = current[index]
        else:
            raise InvalidSelectionRule(f"Selection pointer does not resolve: {pointer}")
    return current


def _set_json_pointer(document: MutableMapping[str, Any], pointer: str, value: Any) -> None:
    tokens = _json_pointer_tokens(pointer)
    if not tokens:
        raise InvalidSelectionRule("Cannot replace the root document through selection.")
    current: Any = document
    for index, token in enumerate(tokens[:-1]):
        next_token = tokens[index + 1]
        if isinstance(current, MutableMapping):
            if token not in current:
                current[token] = [] if next_token.isdigit() else {}
            current = current[token]
        elif isinstance(current, list):
            if not token.isdigit():
                raise InvalidSelectionRule(f"Selection pointer list token is not an index: {pointer}")
            item_index = int(token)
            while len(current) <= item_index:
                current.append([] if next_token.isdigit() else {})
            current = current[item_index]
        else:
            raise InvalidSelectionRule(f"Selection pointer cannot be created: {pointer}")
    final_token = tokens[-1]
    if isinstance(current, MutableMapping):
        current[final_token] = value
        return
    if isinstance(current, list):
        if not final_token.isdigit():
            raise InvalidSelectionRule(f"Selection pointer list token is not an index: {pointer}")
        item_index = int(final_token)
        while len(current) <= item_index:
            current.append(None)
        current[item_index] = value
        return
    raise InvalidSelectionRule(f"Selection pointer cannot be created: {pointer}")


def _json_pointer_tokens(pointer: str) -> tuple[str, ...]:
    _validate_selection_pointer(pointer)
    return tuple(token.replace("~1", "/").replace("~0", "~") for token in pointer.split("/")[1:])


def _escape_json_pointer_token(token: str) -> str:
    return token.replace("~", "~0").replace("/", "~1")


def _verify_initialized(connection: sqlite3.Connection) -> None:
    schema_version = _read_schema_version(connection)
    if schema_version is None:
        raise StoreNotInitialized("SQLite file is not an initialized Open CVN store.")
    if _schema_version_number(schema_version) > _schema_version_number(SCHEMA_VERSION):
        raise IncompatibleStoreSchema(
            f"Store schema version {schema_version} is newer than supported {SCHEMA_VERSION}."
        )
    if _schema_version_number(schema_version) < _schema_version_number(SCHEMA_VERSION):
        _migrate_schema(connection, schema_version)
        connection.commit()


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


def _migrate_schema(connection: sqlite3.Connection, current_version: str) -> None:
    current_number = _schema_version_number(current_version)
    if current_number == 1:
        connection.executescript(_VERSIONING_SCHEMA_SQL)
        connection.execute(
            "UPDATE app_metadata SET value = ? WHERE key = ?",
            (SCHEMA_VERSION, "schema_version"),
        )
        return
    raise IncompatibleStoreSchema(f"Unsupported store schema migration from version {current_version}.")


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


_VERSIONING_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS curriculum_versions (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    kind TEXT NOT NULL CHECK (kind IN ('master', 'derived')),
    master_curriculum_id TEXT NOT NULL,
    source_version_id TEXT,
    selection_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (master_curriculum_id) REFERENCES curricula(id) ON DELETE CASCADE,
    FOREIGN KEY (source_version_id) REFERENCES curriculum_versions(id) ON DELETE SET NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_curriculum_versions_single_master
    ON curriculum_versions(kind)
    WHERE kind = 'master';
CREATE INDEX IF NOT EXISTS idx_curriculum_versions_name ON curriculum_versions(name);
CREATE INDEX IF NOT EXISTS idx_curriculum_versions_kind ON curriculum_versions(kind);
CREATE INDEX IF NOT EXISTS idx_curriculum_versions_updated_at ON curriculum_versions(updated_at);
CREATE INDEX IF NOT EXISTS idx_curriculum_versions_master_curriculum_id
    ON curriculum_versions(master_curriculum_id);
"""


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
""" + _VERSIONING_SCHEMA_SQL
