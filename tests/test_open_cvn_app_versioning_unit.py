from __future__ import annotations

import json
import sqlite3
from copy import deepcopy
from pathlib import Path

import pytest

from open_cvn_app.storage import (
    SCHEMA_VERSION,
    CurriculumCreate,
    CurriculumRepository,
    DuplicateCurriculumVersionName,
    InvalidSelectionRule,
    MasterCurriculumNotFound,
    initialize_store,
)


FIXTURES_DIR = Path(__file__).parent / "fixtures" / "open_cvn"
EXAMPLES_DIR = Path(__file__).parent.parent / "examples" / "open_cvn"


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURES_DIR / name).read_text(encoding="utf-8"))


def _load_example(name: str) -> dict:
    return json.loads((EXAMPLES_DIR / name).read_text(encoding="utf-8"))


def _create_repository_with_curriculum(tmp_path: Path, document: dict | None = None):
    store_path = tmp_path / "open-cvn.sqlite"
    initialize_store(store_path)
    repository = CurriculumRepository(store_path)
    curriculum = repository.create_curriculum(
        CurriculumCreate(display_name="Master CV", document=document or _load_fixture("valid_minimal.json"))
    )
    return repository, curriculum


def _multi_entry_document() -> dict:
    document = _load_example("research_entry.json")
    document = deepcopy(document)
    document["curriculum"]["research"].append(
        {
            "id": "research-002",
            "type": "research.project",
            "data": {"project_title": "Open CVN storage prototype"},
            "trace": {"cvn_codes": ["050.020.010.000"], "confidence": "high"},
        }
    )
    return document


def test_assigns_master_curriculum_and_lists_versions(tmp_path: Path):
    repository, curriculum = _create_repository_with_curriculum(tmp_path)

    master = repository.assign_master_curriculum(curriculum.id)
    versions = repository.list_versions()

    assert master.name == "master"
    assert master.kind == "master"
    assert master.master_curriculum_id == curriculum.id
    assert master.source_version_id is None
    assert master.selection.mode == "include_all"
    assert versions == (master,)


def test_rejects_second_master_version(tmp_path: Path):
    repository, curriculum = _create_repository_with_curriculum(tmp_path)
    repository.assign_master_curriculum(curriculum.id)

    with pytest.raises(DuplicateCurriculumVersionName):
        repository.assign_master_curriculum(curriculum.id, name="another-master")


def test_creates_derived_version_from_master(tmp_path: Path):
    repository, curriculum = _create_repository_with_curriculum(tmp_path)
    master = repository.assign_master_curriculum(curriculum.id)

    derived = repository.create_derived_version("public")

    assert derived.name == "public"
    assert derived.kind == "derived"
    assert derived.master_curriculum_id == curriculum.id
    assert derived.source_version_id == master.id
    assert derived.selection.mode == "include_all"


def test_clones_derived_version_selection(tmp_path: Path):
    repository, curriculum = _create_repository_with_curriculum(tmp_path, _multi_entry_document())
    repository.assign_master_curriculum(curriculum.id)
    public = repository.create_derived_version("public")
    repository.exclude_from_version(public.name, "/curriculum/research/0")

    cloned = repository.create_derived_version("short", source="public")


    assert cloned.source_version_id == repository.get_version("public").id
    assert cloned.selection.excluded_pointers == ("/curriculum/research/0",)


def test_rejects_duplicate_version_name(tmp_path: Path):
    repository, curriculum = _create_repository_with_curriculum(tmp_path)
    repository.assign_master_curriculum(curriculum.id)
    repository.create_derived_version("public")

    with pytest.raises(DuplicateCurriculumVersionName):
        repository.create_derived_version("public")


def test_rejects_derived_creation_without_master(tmp_path: Path):
    repository, _curriculum = _create_repository_with_curriculum(tmp_path)

    with pytest.raises(MasterCurriculumNotFound):
        repository.create_derived_version("public")


def test_excluding_section_materializes_selected_data_only(tmp_path: Path):
    repository, curriculum = _create_repository_with_curriculum(tmp_path, _multi_entry_document())
    repository.assign_master_curriculum(curriculum.id)
    repository.create_derived_version("public")
    repository.exclude_from_version("public", "/curriculum/research")

    materialized = repository.materialize_version("public")

    assert materialized.document["curriculum"]["research"] == []
    assert materialized.validation_status == "valid"
    assert repository.get_curriculum(curriculum.id).document["curriculum"]["research"]


def test_excluding_entry_materializes_without_mutating_master(tmp_path: Path):
    repository, curriculum = _create_repository_with_curriculum(tmp_path, _multi_entry_document())
    repository.assign_master_curriculum(curriculum.id)
    repository.create_derived_version("public")
    repository.exclude_from_version("public", "/curriculum/research/0")

    materialized = repository.materialize_version("public")
    master_after_edit = repository.get_curriculum(curriculum.id)

    assert [entry["id"] for entry in materialized.document["curriculum"]["research"]] == ["research-002"]
    assert [entry["id"] for entry in master_after_edit.document["curriculum"]["research"]] == [
        "research-001",
        "research-002",
    ]


def test_materialization_preserves_trace_metadata(tmp_path: Path):
    repository, curriculum = _create_repository_with_curriculum(tmp_path, _multi_entry_document())
    repository.assign_master_curriculum(curriculum.id)
    repository.create_derived_version("public")
    repository.exclude_from_version("public", "/curriculum/research/1")

    materialized = repository.materialize_version("public")

    assert materialized.document["curriculum"]["research"][0]["trace"]["cvn_codes"] == ["060.010.010.000"]
    assert materialized.document["extensions"]["x-open-cvn.versioning"]["version_name"] == "public"


def test_rejects_invalid_selection_edits(tmp_path: Path):
    repository, curriculum = _create_repository_with_curriculum(tmp_path, _multi_entry_document())
    repository.assign_master_curriculum(curriculum.id)
    repository.create_derived_version("public")

    with pytest.raises(InvalidSelectionRule):
        repository.exclude_from_version("master", "/curriculum/research/0")
    with pytest.raises(InvalidSelectionRule):
        repository.exclude_from_version("public", "/metadata/policy")
    with pytest.raises(InvalidSelectionRule):
        repository.exclude_from_version("public", "/curriculum/research/99")


def test_initialize_store_migrates_schema_version_1_store(tmp_path: Path):
    store_path = tmp_path / "open-cvn.sqlite"
    with sqlite3.connect(store_path) as connection:
        connection.executescript(
            """
            CREATE TABLE app_metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            INSERT INTO app_metadata(key, value) VALUES ('schema_version', '1');
            CREATE TABLE curricula (
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
            CREATE TABLE curriculum_diagnostics (
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
            """
        )

    store_info = initialize_store(store_path)

    assert store_info.schema_version == SCHEMA_VERSION
    with sqlite3.connect(store_path) as connection:
        schema_version = connection.execute(
            "SELECT value FROM app_metadata WHERE key = 'schema_version'"
        ).fetchone()[0]
        version_table = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'curriculum_versions'"
        ).fetchone()[0]
    assert schema_version == SCHEMA_VERSION
    assert version_table == "curriculum_versions"
