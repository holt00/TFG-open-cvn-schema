from __future__ import annotations

import json
from pathlib import Path

import pytest

from open_cvn import CvnValidationStatus, validate_open_cvn_json
import open_cvn_app.cli as cli_module
from open_cvn_app.cli import run
from open_cvn_app.pdf import PdfGenerationUnavailable
from open_cvn_app.storage import CurriculumRepository


EXAMPLES_DIR = Path(__file__).parent.parent / "examples" / "open_cvn"
FIXTURES_DIR = Path(__file__).parent / "fixtures" / "open_cvn"


def test_mvp_cli_workflow_imports_derives_exports_latex_and_reports_pdf_unavailable(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    store_path = tmp_path / "open-cvn.sqlite"
    exported_json_path = tmp_path / "exports" / "public.json"
    exported_tex_path = tmp_path / "exports" / "public.tex"
    pdf_path = tmp_path / "exports" / "public.pdf"
    input_path = EXAMPLES_DIR / "research_entry.json"

    def unavailable_after_materialization(repository, **kwargs):
        repository.materialize_version(kwargs["version"])
        raise PdfGenerationUnavailable(("latexmk", "pdflatex"))

    monkeypatch.setattr(cli_module, "generate_pdf_document", unavailable_after_materialization)

    assert run(["store", "init", "--path", str(store_path)]) == 0
    assert run(["json", "import", str(input_path), "--store", str(store_path), "--as-master"]) == 0
    assert run(["versions", "derive", "public", "--store", str(store_path)]) == 0
    assert run(["versions", "sections", "public", "--store", str(store_path)]) == 0
    assert run(["versions", "entries", "public", "research", "--store", str(store_path)]) == 0
    assert run(["versions", "exclude", "public", "/curriculum/research/0", "--store", str(store_path)]) == 0
    assert run(["json", "export", str(exported_json_path), "--store", str(store_path), "--version", "public"]) == 0
    assert run(["latex", "export", str(exported_tex_path), "--store", str(store_path), "--version", "public"]) == 0
    assert run(["pdf", "generate", str(pdf_path), "--store", str(store_path), "--version", "public"]) == 1

    captured = capsys.readouterr()
    exported_document = json.loads(exported_json_path.read_text(encoding="utf-8"))
    exported_latex = exported_tex_path.read_text(encoding="utf-8")
    validation_result = validate_open_cvn_json(exported_document, source_identifier="issue-68-public")

    assert "Curriculum sections for version 'public':" in captured.out
    assert "Entries for version 'public' section 'research':" in captured.out
    assert "Excluded /curriculum/research/0" in captured.out
    assert "PDF generation unavailable." in captured.err
    assert "No supported TeX compiler found" in captured.err
    assert validation_result.validation_status == CvnValidationStatus.VALID
    assert exported_document["curriculum"]["research"] == []
    assert exported_document["extensions"]["x-open-cvn.versioning"]["version_name"] == "public"
    assert "\\item[Version] public" in exported_latex
    assert "Open CVN data representation" not in exported_latex
    assert exported_latex.endswith("\n")
    assert not pdf_path.exists()


def test_mvp_invalid_import_workflow_leaves_store_empty(capsys: pytest.CaptureFixture[str], tmp_path: Path):
    store_path = tmp_path / "open-cvn.sqlite"
    input_path = FIXTURES_DIR / "wrong_shape.json"

    assert run(["store", "init", "--path", str(store_path)]) == 0
    exit_code = run(["json", "import", str(input_path), "--store", str(store_path)])

    captured = capsys.readouterr()
    repository = CurriculumRepository(store_path)
    assert exit_code == 1
    assert "Open CVN JSON import failed." in captured.err
    assert "json_schema_validation_failure" in captured.err
    assert repository.list_curricula() == ()
    assert repository.list_versions() == ()


def test_mvp_temporary_stores_are_isolated_and_nested_exports_work(
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
):
    first_store = tmp_path / "first.sqlite"
    second_store = tmp_path / "second.sqlite"
    input_path = EXAMPLES_DIR / "minimal.json"
    nested_export = tmp_path / "nested" / "outputs" / "master.json"

    assert run(["store", "init", "--path", str(first_store)]) == 0
    assert run(["store", "init", "--path", str(second_store)]) == 0
    assert run(["json", "import", str(input_path), "--store", str(first_store), "--as-master"]) == 0
    assert run(["versions", "list", "--store", str(second_store)]) == 0
    assert run(["json", "export", str(nested_export), "--store", str(first_store), "--version", "master"]) == 0

    output = capsys.readouterr().out
    first_repository = CurriculumRepository(first_store)
    second_repository = CurriculumRepository(second_store)
    exported_document = json.loads(nested_export.read_text(encoding="utf-8"))

    assert len(first_repository.list_curricula()) == 1
    assert len(first_repository.list_versions()) == 1
    assert second_repository.list_curricula() == ()
    assert second_repository.list_versions() == ()
    assert "No curriculum versions found." in output
    assert nested_export.exists()
    assert validate_open_cvn_json(exported_document).validation_status == CvnValidationStatus.VALID
