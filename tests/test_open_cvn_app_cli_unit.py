from __future__ import annotations

import json
from pathlib import Path

import pytest

from open_cvn import CvnValidationStatus, validate_open_cvn_json
from open_cvn_app import __version__
from open_cvn_app.cli import build_parser, run
from open_cvn_app.storage import CurriculumCreate, CurriculumRepository, initialize_store


FIXTURES_DIR = Path(__file__).parent / "fixtures" / "open_cvn"
EXAMPLES_DIR = Path(__file__).parent.parent / "examples" / "open_cvn"


def _create_store_with_curriculum(tmp_path):
    store_path = tmp_path / "open-cvn.sqlite"
    initialize_store(store_path)
    repository = CurriculumRepository(store_path)
    document = json.loads((FIXTURES_DIR / "valid_minimal.json").read_text(encoding="utf-8"))
    curriculum = repository.create_curriculum(CurriculumCreate(display_name="Master CV", document=document))
    return store_path, curriculum


def test_cli_help_contains_program_and_command_groups(capsys: pytest.CaptureFixture[str]):
    parser = build_parser()

    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["--help"])

    assert exc_info.value.code == 0
    output = capsys.readouterr().out
    assert "open-cvn" in output
    for command_group in ("store", "json", "versions", "latex", "pdf"):
        assert command_group in output


def test_cli_version_command_outputs_project_version(capsys: pytest.CaptureFixture[str]):
    exit_code = run(["version"])

    assert exit_code == 0
    assert capsys.readouterr().out.strip() == f"open-cvn {__version__}"


def test_store_init_creates_local_store(capsys: pytest.CaptureFixture[str], tmp_path):
    store_path = tmp_path / "open-cvn.sqlite"

    exit_code = run(["store", "init", "--path", str(store_path)])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Initialized Open CVN store" in output
    assert str(store_path) in output
    assert store_path.exists()


def test_json_import_stores_valid_open_cvn_document(capsys: pytest.CaptureFixture[str], tmp_path):
    store_path = tmp_path / "open-cvn.sqlite"
    initialize_store(store_path)
    input_path = FIXTURES_DIR / "valid_minimal.json"

    exit_code = run([
        "json",
        "import",
        str(input_path),
        "--store",
        str(store_path),
        "--name",
        "Imported CV",
    ])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Imported Open CVN JSON as curriculum 'Imported CV'." in output
    assert "Curriculum ID:" in output
    assert "Validation status: valid" in output
    repository = CurriculumRepository(store_path)
    curricula = repository.list_curricula()
    assert len(curricula) == 1
    assert curricula[0].display_name == "Imported CV"
    assert curricula[0].source_identifier == str(input_path)


def test_json_import_can_assign_master_version(capsys: pytest.CaptureFixture[str], tmp_path):
    store_path = tmp_path / "open-cvn.sqlite"
    initialize_store(store_path)
    input_path = FIXTURES_DIR / "valid_minimal.json"

    exit_code = run(["json", "import", str(input_path), "--store", str(store_path), "--as-master"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Assigned master curriculum version 'master'" in output
    repository = CurriculumRepository(store_path)
    curricula = repository.list_curricula()
    versions = repository.list_versions()
    assert len(curricula) == 1
    assert len(versions) == 1
    assert versions[0].kind == "master"
    assert versions[0].master_curriculum_id == curricula[0].id


def test_json_import_reports_duplicate_master(capsys: pytest.CaptureFixture[str], tmp_path):
    store_path, curriculum = _create_store_with_curriculum(tmp_path)
    repository = CurriculumRepository(store_path)
    repository.assign_master_curriculum(curriculum.id)
    input_path = FIXTURES_DIR / "valid_minimal.json"

    exit_code = run(["json", "import", str(input_path), "--store", str(store_path), "--as-master"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Open CVN JSON import failed." in captured.err
    assert "A master curriculum version already exists." in captured.err


def test_json_import_reports_schema_validation_errors(capsys: pytest.CaptureFixture[str], tmp_path):
    store_path = tmp_path / "open-cvn.sqlite"
    initialize_store(store_path)
    input_path = FIXTURES_DIR / "wrong_shape.json"

    exit_code = run(["json", "import", str(input_path), "--store", str(store_path)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Open CVN JSON import failed." in captured.err
    assert "Validation status: invalid" in captured.err
    assert "json_schema_validation_failure" in captured.err
    assert CurriculumRepository(store_path).list_curricula() == ()


def test_json_import_reports_malformed_json(capsys: pytest.CaptureFixture[str], tmp_path):
    store_path = tmp_path / "open-cvn.sqlite"
    initialize_store(store_path)
    input_path = FIXTURES_DIR / "malformed.json"

    exit_code = run(["json", "import", str(input_path), "--store", str(store_path)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Open CVN JSON import failed." in captured.err
    assert "Validation status: failed" in captured.err
    assert "invalid_json" in captured.err
    assert CurriculumRepository(store_path).list_curricula() == ()


def test_json_export_writes_revalidatable_master_document(capsys: pytest.CaptureFixture[str], tmp_path):
    store_path, curriculum = _create_store_with_curriculum(tmp_path)
    repository = CurriculumRepository(store_path)
    repository.assign_master_curriculum(curriculum.id)
    output_path = tmp_path / "exports" / "master.json"

    exit_code = run(["json", "export", str(output_path), "--store", str(store_path), "--version", "master"])

    output = capsys.readouterr().out
    exported_text = output_path.read_text(encoding="utf-8")
    exported_document = json.loads(exported_text)
    validation_result = validate_open_cvn_json(exported_document, source_identifier="exported-master")
    assert exit_code == 0
    assert "Exported Open CVN JSON version 'master'" in output
    assert "Validation status: valid" in output
    assert validation_result.validation_status == CvnValidationStatus.VALID
    assert exported_text.endswith("\n")
    assert exported_text == f"{json.dumps(exported_document, ensure_ascii=False, sort_keys=True, indent=2)}\n"


def test_json_export_writes_materialized_derived_document(capsys: pytest.CaptureFixture[str], tmp_path):
    store_path = tmp_path / "open-cvn.sqlite"
    initialize_store(store_path)
    repository = CurriculumRepository(store_path)
    document = json.loads((EXAMPLES_DIR / "research_entry.json").read_text(encoding="utf-8"))
    curriculum = repository.create_curriculum(CurriculumCreate(display_name="Master CV", document=document))
    repository.assign_master_curriculum(curriculum.id)
    repository.create_derived_version("public")
    repository.exclude_from_version("public", "/curriculum/research")
    output_path = tmp_path / "public.json"

    exit_code = run(["json", "export", str(output_path), "--store", str(store_path), "--version", "public"])

    output = capsys.readouterr().out
    exported_document = json.loads(output_path.read_text(encoding="utf-8"))
    validation_result = validate_open_cvn_json(exported_document, source_identifier="exported-public")
    assert exit_code == 0
    assert "Exported Open CVN JSON version 'public'" in output
    assert exported_document["curriculum"]["research"] == []
    assert exported_document["extensions"]["x-open-cvn.versioning"]["version_name"] == "public"
    assert validation_result.validation_status == CvnValidationStatus.VALID


def test_json_export_reports_missing_version(capsys: pytest.CaptureFixture[str], tmp_path):
    store_path = tmp_path / "open-cvn.sqlite"
    initialize_store(store_path)
    output_path = tmp_path / "missing.json"

    exit_code = run(["json", "export", str(output_path), "--store", str(store_path), "--version", "missing"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Open CVN JSON export failed." in captured.err
    assert "Curriculum version not found: missing" in captured.err


def test_json_export_reports_uninitialized_store(capsys: pytest.CaptureFixture[str], tmp_path):
    store_path = tmp_path / "open-cvn.sqlite"
    output_path = tmp_path / "missing.json"

    exit_code = run(["json", "export", str(output_path), "--store", str(store_path)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Open CVN JSON export failed." in captured.err
    assert "SQLite file is not an initialized Open CVN store." in captured.err


def test_versions_list_reads_initialized_store(capsys: pytest.CaptureFixture[str], tmp_path):
    store_path = tmp_path / "open-cvn.sqlite"
    initialize_store(store_path)

    exit_code = run(["versions", "list", "--store", str(store_path)])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "No curriculum versions found." in output


def test_versions_master_and_derive_create_versions(capsys: pytest.CaptureFixture[str], tmp_path):
    store_path, curriculum = _create_store_with_curriculum(tmp_path)

    master_exit = run(["versions", "master", curriculum.id, "--store", str(store_path)])
    derive_exit = run(["versions", "derive", "public", "--from", "master", "--store", str(store_path)])
    list_exit = run(["versions", "list", "--store", str(store_path)])

    output = capsys.readouterr().out
    assert master_exit == 0
    assert derive_exit == 0
    assert list_exit == 0
    assert "Assigned master curriculum version 'master'" in output
    assert "Created derived curriculum version 'public'" in output
    assert "master (master)" in output
    assert "public (derived)" in output


def test_versions_include_and_exclude_update_derived_selection(capsys: pytest.CaptureFixture[str], tmp_path):
    store_path, curriculum = _create_store_with_curriculum(tmp_path)
    run(["versions", "master", curriculum.id, "--store", str(store_path)])
    run(["versions", "derive", "public", "--store", str(store_path)])

    exclude_exit = run(["versions", "exclude", "public", "/curriculum/research", "--store", str(store_path)])
    include_exit = run(["versions", "include", "public", "/curriculum/research", "--store", str(store_path)])

    output = capsys.readouterr().out
    assert exclude_exit == 0
    assert include_exit == 0
    assert "Excluded /curriculum/research" in output
    assert "Included /curriculum/research" in output


def test_versions_sections_lists_materialized_sections(capsys: pytest.CaptureFixture[str], tmp_path):
    store_path = tmp_path / "open-cvn.sqlite"
    initialize_store(store_path)
    repository = CurriculumRepository(store_path)
    document = json.loads((EXAMPLES_DIR / "research_entry.json").read_text(encoding="utf-8"))
    curriculum = repository.create_curriculum(CurriculumCreate(display_name="Master CV", document=document))
    repository.assign_master_curriculum(curriculum.id)
    repository.create_derived_version("public")

    exit_code = run(["versions", "sections", "public", "--store", str(store_path)])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Curriculum sections for version 'public':" in output
    assert "- research pointer=/curriculum/research entries=1" in output
    assert "- identity pointer=/curriculum/identity entries=object" in output


def test_versions_entries_lists_plain_and_pointer_sections(capsys: pytest.CaptureFixture[str], tmp_path):
    store_path = tmp_path / "open-cvn.sqlite"
    initialize_store(store_path)
    repository = CurriculumRepository(store_path)
    document = json.loads((EXAMPLES_DIR / "research_entry.json").read_text(encoding="utf-8"))
    curriculum = repository.create_curriculum(CurriculumCreate(display_name="Master CV", document=document))
    repository.assign_master_curriculum(curriculum.id)
    repository.create_derived_version("public")

    plain_exit = run(["versions", "entries", "public", "research", "--store", str(store_path)])
    pointer_exit = run([
        "versions",
        "entries",
        "public",
        "/curriculum/research",
        "--store",
        str(store_path),
    ])

    output = capsys.readouterr().out
    assert plain_exit == 0
    assert pointer_exit == 0
    assert "Entries for version 'public' section 'research':" in output
    assert "pointer=/curriculum/research/0" in output
    assert "id=research-001" in output
    assert "type=research.publication" in output


def test_versions_entries_reports_empty_and_non_list_sections(capsys: pytest.CaptureFixture[str], tmp_path):
    store_path = tmp_path / "open-cvn.sqlite"
    initialize_store(store_path)
    repository = CurriculumRepository(store_path)
    document = json.loads((EXAMPLES_DIR / "education_entry.json").read_text(encoding="utf-8"))
    curriculum = repository.create_curriculum(CurriculumCreate(display_name="Master CV", document=document))
    repository.assign_master_curriculum(curriculum.id)
    repository.create_derived_version("public")

    empty_exit = run(["versions", "entries", "public", "research", "--store", str(store_path)])
    non_list_exit = run(["versions", "entries", "public", "identity", "--store", str(store_path)])

    captured = capsys.readouterr()
    assert empty_exit == 0
    assert "No entries found in section 'research'." in captured.out
    assert non_list_exit == 1
    assert "Entry listing failed." in captured.err
    assert "Curriculum section is not a repeated entry list: identity" in captured.err


def test_versions_metadata_show_and_update(capsys: pytest.CaptureFixture[str], tmp_path):
    store_path, curriculum = _create_store_with_curriculum(tmp_path)
    repository = CurriculumRepository(store_path)
    repository.assign_master_curriculum(curriculum.id)
    repository.create_derived_version("public")

    update_exit = run([
        "versions",
        "metadata",
        "public",
        "--display-name",
        "Public CV",
        "--purpose",
        "grant application",
        "--store",
        str(store_path),
    ])
    show_exit = run(["versions", "metadata", "public", "--store", str(store_path)])

    output = capsys.readouterr().out
    assert update_exit == 0
    assert show_exit == 0
    assert "Updated metadata for derived curriculum version 'public'." in output
    assert "Display name: Public CV" in output
    assert "Purpose: grant application" in output


def test_versions_field_edit_reports_unsupported_without_mutating(capsys: pytest.CaptureFixture[str], tmp_path):
    store_path, curriculum = _create_store_with_curriculum(tmp_path)
    repository = CurriculumRepository(store_path)
    repository.assign_master_curriculum(curriculum.id)
    repository.create_derived_version("public")
    before = repository.materialize_version("public").document

    exit_code = run([
        "versions",
        "field-edit",
        "public",
        "/curriculum/research/0/data/title",
        "New title",
        "--store",
        str(store_path),
    ])

    captured = capsys.readouterr()
    after = repository.materialize_version("public").document
    assert exit_code == 1
    assert "Field-level edits are not supported in issue #65 MVP." in captured.err
    assert "Use include/exclude section or entry selection instead." in captured.err
    assert after == before


def test_versions_derive_reports_missing_master(capsys: pytest.CaptureFixture[str], tmp_path):
    store_path = tmp_path / "open-cvn.sqlite"
    initialize_store(store_path)

    exit_code = run(["versions", "derive", "public", "--store", str(store_path)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Derived version creation failed." in captured.err
    assert "Master curriculum version has not been assigned." in captured.err


def test_latex_export_routes_to_issue_66_placeholder(capsys: pytest.CaptureFixture[str]):
    exit_code = run(["latex", "export", "cv.tex"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "LaTeX export is planned for issue #66" in output


def test_pdf_generate_routes_to_issue_67_placeholder(capsys: pytest.CaptureFixture[str]):
    exit_code = run(["pdf", "generate", "cv.pdf"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "PDF generation is planned for issue #67" in output
