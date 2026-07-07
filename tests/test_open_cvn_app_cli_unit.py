from __future__ import annotations

import json
from pathlib import Path

import pytest

from open_cvn_app import __version__
from open_cvn_app.cli import build_parser, run
from open_cvn_app.storage import CurriculumCreate, CurriculumRepository, initialize_store


FIXTURES_DIR = Path(__file__).parent / "fixtures" / "open_cvn"


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


def test_json_import_routes_to_issue_64_placeholder(capsys: pytest.CaptureFixture[str]):
    exit_code = run(["json", "import", "input.json"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Open CVN JSON import is planned for issue #64" in output


def test_json_export_routes_to_issue_64_placeholder(capsys: pytest.CaptureFixture[str]):
    exit_code = run(["json", "export", "output.json", "--version", "public"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Open CVN JSON export is planned for issue #64" in output


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
