from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from open_cvn.parser_contract import CvnErrorCode, CvnIssueSeverity, CvnParseIssue
from open_cvn_app.storage import (
    SCHEMA_VERSION,
    CurriculumCreate,
    CurriculumNotFound,
    CurriculumRepository,
    CurriculumUpdate,
    InvalidCurriculumDocument,
    initialize_store,
)


FIXTURES_DIR = Path(__file__).parent / "fixtures" / "open_cvn"


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURES_DIR / name).read_text(encoding="utf-8"))


def test_initialize_store_creates_schema_and_metadata(tmp_path: Path):
    store_path = tmp_path / "nested" / "open-cvn.sqlite"

    store_info = initialize_store(store_path)

    assert store_info.path == store_path
    assert store_info.schema_version == SCHEMA_VERSION
    assert store_path.exists()

    with sqlite3.connect(store_path) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }
        schema_version = connection.execute(
            "SELECT value FROM app_metadata WHERE key = 'schema_version'"
        ).fetchone()[0]

    assert {"app_metadata", "curricula", "curriculum_diagnostics"} <= tables
    assert schema_version == SCHEMA_VERSION


def test_initialize_store_is_idempotent(tmp_path: Path):
    store_path = tmp_path / "open-cvn.sqlite"

    first = initialize_store(store_path)
    second = initialize_store(store_path)

    assert first == second


def test_repository_creates_reads_lists_updates_and_deletes_curriculum(tmp_path: Path):
    store_path = tmp_path / "open-cvn.sqlite"
    initialize_store(store_path)
    repository = CurriculumRepository(store_path)
    document = _load_fixture("valid_minimal.json")

    created = repository.create_curriculum(
        CurriculumCreate(
            display_name="Master CV",
            document=document,
            source_identifier="valid_minimal.json",
        )
    )

    fetched = repository.get_curriculum(created.id)
    listed = repository.list_curricula()
    updated = repository.update_curriculum(created.id, CurriculumUpdate(display_name="Updated CV"))

    assert fetched == created
    assert listed == (created,)
    assert updated.display_name == "Updated CV"
    assert updated.updated_at >= created.updated_at
    assert updated.schema_version == "0.1.0"
    assert updated.policy_name == "default_cvn_semantic_policy"
    assert updated.policy_version == "0.1.0"
    assert updated.source_format == "open_cvn_json"
    assert updated.source_identifier == "valid_minimal.json"
    assert updated.validation_status == "valid"

    repository.delete_curriculum(created.id)

    assert repository.list_curricula() == ()
    with pytest.raises(CurriculumNotFound):
        repository.get_curriculum(created.id)


def test_repository_round_trips_open_cvn_document_semantics(tmp_path: Path):
    store_path = tmp_path / "open-cvn.sqlite"
    initialize_store(store_path)
    repository = CurriculumRepository(store_path)
    document = _load_fixture("valid_minimal.json")

    created = repository.create_curriculum(CurriculumCreate(display_name="Master CV", document=document))

    assert created.document == document


def test_repository_rejects_invalid_open_cvn_document(tmp_path: Path):
    store_path = tmp_path / "open-cvn.sqlite"
    initialize_store(store_path)
    repository = CurriculumRepository(store_path)
    document = _load_fixture("wrong_shape.json")

    with pytest.raises(InvalidCurriculumDocument):
        repository.create_curriculum(CurriculumCreate(display_name="Broken CV", document=document))

    assert repository.list_curricula() == ()


def test_repository_replaces_payload_and_diagnostics(tmp_path: Path):
    store_path = tmp_path / "open-cvn.sqlite"
    initialize_store(store_path)
    repository = CurriculumRepository(store_path)
    document = _load_fixture("valid_minimal.json")
    first_issue = CvnParseIssue(
        code=CvnErrorCode.PYDANTIC_VALIDATION_FAILURE,
        severity=CvnIssueSeverity.WARNING,
        message="First diagnostic.",
        source_location="line 1 column 1",
        path=("metadata", "policy"),
        details={"field": "policy"},
    )
    second_issue = CvnParseIssue(
        code=CvnErrorCode.JSON_SCHEMA_VALIDATION_FAILURE,
        severity=CvnIssueSeverity.WARNING,
        message="Second diagnostic.",
        path=("schema_version",),
        details={"field": "schema_version"},
    )

    created = repository.create_curriculum(
        CurriculumCreate(display_name="Master CV", document=document, diagnostics=(first_issue,))
    )
    initial_diagnostics = repository.list_diagnostics(created.id)
    replaced = repository.replace_curriculum_payload(
        created.id,
        document,
        source_identifier="replacement.json",
        diagnostics=(second_issue,),
    )
    replaced_diagnostics = repository.list_diagnostics(created.id)

    assert replaced.source_identifier == "replacement.json"
    assert len(initial_diagnostics) == 1
    assert initial_diagnostics[0].message == "First diagnostic."
    assert initial_diagnostics[0].path == ("metadata", "policy")
    assert initial_diagnostics[0].details == {"field": "policy"}
    assert len(replaced_diagnostics) == 1
    assert replaced_diagnostics[0].message == "Second diagnostic."
    assert replaced_diagnostics[0].path == ("schema_version",)


def test_repository_raises_for_missing_curriculum_operations(tmp_path: Path):
    store_path = tmp_path / "open-cvn.sqlite"
    initialize_store(store_path)
    repository = CurriculumRepository(store_path)
    document = _load_fixture("valid_minimal.json")

    with pytest.raises(CurriculumNotFound):
        repository.update_curriculum("missing", CurriculumUpdate(display_name="Missing"))
    with pytest.raises(CurriculumNotFound):
        repository.replace_curriculum_payload("missing", document)
    with pytest.raises(CurriculumNotFound):
        repository.delete_curriculum("missing")
    with pytest.raises(CurriculumNotFound):
        repository.list_diagnostics("missing")
