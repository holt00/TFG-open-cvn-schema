from __future__ import annotations

import pytest

from open_cvn_app import __version__
from open_cvn_app.cli import build_parser, run


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


def test_versions_list_routes_to_issue_63_placeholder(capsys: pytest.CaptureFixture[str]):
    exit_code = run(["versions", "list"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Version listing is planned for issue #63" in output


def test_versions_derive_routes_to_issue_63_placeholder(capsys: pytest.CaptureFixture[str]):
    exit_code = run(["versions", "derive", "public", "--from", "master"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Derived version creation is planned for issue #63" in output


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
