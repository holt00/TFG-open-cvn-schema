from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from open_cvn_app.editing import list_curriculum_entries, list_curriculum_sections
from open_cvn_app.storage import (
    CurriculumCreate,
    CurriculumRepository,
    InvalidSelectionRule,
    initialize_store,
)


EXAMPLES_DIR = Path(__file__).parent.parent / "examples" / "open_cvn"


def _load_example(name: str) -> dict:
    return json.loads((EXAMPLES_DIR / name).read_text(encoding="utf-8"))


def _repository_with_document(tmp_path: Path, document: dict):
    store_path = tmp_path / "open-cvn.sqlite"
    initialize_store(store_path)
    repository = CurriculumRepository(store_path)
    curriculum = repository.create_curriculum(CurriculumCreate(display_name="Master CV", document=document))
    repository.assign_master_curriculum(curriculum.id)
    repository.create_derived_version("public")
    return repository


def test_lists_curriculum_sections_for_materialized_version(tmp_path: Path):
    repository = _repository_with_document(tmp_path, _load_example("research_entry.json"))

    sections = list_curriculum_sections(repository, "public")

    research = next(section for section in sections if section.name == "research")
    identity = next(section for section in sections if section.name == "identity")
    assert research.pointer == "/curriculum/research"
    assert research.entry_count == 1
    assert identity.value_kind == "object"
    assert identity.entry_count is None


def test_lists_entries_with_stable_display_identifiers(tmp_path: Path):
    repository = _repository_with_document(tmp_path, _load_example("research_entry.json"))

    entries = list_curriculum_entries(repository, "public", "research")

    assert len(entries) == 1
    assert entries[0].index == 0
    assert entries[0].pointer == "/curriculum/research/0"
    assert entries[0].entry_id == "research-001"
    assert entries[0].entry_type == "research.publication"
    assert entries[0].summary == "title=Open CVN data representation; publication_year=2026"
    assert entries[0].cvn_codes == ("060.010.010.000",)


def test_lists_entries_with_missing_id_fallback(tmp_path: Path):
    document = _load_example("research_entry.json")
    document = deepcopy(document)
    del document["curriculum"]["research"][0]["id"]
    repository = _repository_with_document(tmp_path, document)

    entries = list_curriculum_entries(repository, "public", "/curriculum/research")

    assert entries[0].entry_id is None
    assert entries[0].pointer == "/curriculum/research/0"


def test_entry_listing_reports_empty_and_non_list_sections(tmp_path: Path):
    repository = _repository_with_document(tmp_path, _load_example("education_entry.json"))

    assert list_curriculum_entries(repository, "public", "research") == ()
    with pytest.raises(InvalidSelectionRule, match="not a repeated entry list"):
        list_curriculum_entries(repository, "public", "identity")


def test_updates_derived_metadata_and_materializes_extension(tmp_path: Path):
    repository = _repository_with_document(tmp_path, _load_example("research_entry.json"))

    version = repository.update_version_metadata(
        "public",
        display_name="Public CV",
        purpose="grant application",
    )
    materialized = repository.materialize_version("public")

    assert version.selection.metadata == {
        "display_name": "Public CV",
        "purpose": "grant application",
    }
    assert materialized.document["extensions"]["x-open-cvn.versioning"]["metadata"] == {
        "display_name": "Public CV",
        "purpose": "grant application",
    }
    assert materialized.validation_status == "valid"


def test_selection_edits_preserve_derived_metadata(tmp_path: Path):
    repository = _repository_with_document(tmp_path, _load_example("research_entry.json"))
    repository.update_version_metadata("public", display_name="Public CV", purpose="grant application")

    repository.exclude_from_version("public", "/curriculum/research/0")
    materialized = repository.materialize_version("public")

    assert repository.get_version("public").selection.metadata == {
        "display_name": "Public CV",
        "purpose": "grant application",
    }
    assert materialized.document["extensions"]["x-open-cvn.versioning"]["metadata"] == {
        "display_name": "Public CV",
        "purpose": "grant application",
    }


def test_rejects_master_metadata_updates_and_invalid_sections(tmp_path: Path):
    repository = _repository_with_document(tmp_path, _load_example("research_entry.json"))

    with pytest.raises(InvalidSelectionRule, match="Master curriculum version metadata cannot be edited"):
        repository.update_version_metadata("master", purpose="base")
    with pytest.raises(InvalidSelectionRule, match="Curriculum section not found"):
        list_curriculum_entries(repository, "public", "missing")
