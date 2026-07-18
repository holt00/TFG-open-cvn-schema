from __future__ import annotations

import json
from pathlib import Path

import pytest
import pymupdf

from open_cvn import (
    CvnErrorCode,
    CvnIssueSeverity,
    CvnParseIssue,
    CvnParseResult,
    CvnParseTrace,
    CvnSourceFormat,
    CvnValidationStatus,
    validate_open_cvn_json,
)
import open_cvn_app.cli as cli_module
from open_cvn_app import __version__
from open_cvn_app.cli import build_parser, run
from open_cvn_app.pdf import CompilerRunDiagnostic, PdfCompilationError, PdfGenerationResult, PdfGenerationUnavailable
from open_cvn_app.pdf import PdfEnvironmentDiagnostic
from open_cvn_app.storage import CurriculumCreate, CurriculumRepository, initialize_store


FIXTURES_DIR = Path(__file__).parent / "fixtures" / "open_cvn"
EXAMPLES_DIR = Path(__file__).parent.parent / "examples" / "open_cvn"
SEMANTIC_CVN_XML = """<?xml version="1.0" encoding="UTF-8"?>
<CVNRoot xmlns="https://example.test/cvn">
  <CVNItem code="020.010.010.000">
    <Field code="020.010.010.030">Synthetic Computer Science Degree</Field>
  </CVNItem>
</CVNRoot>
"""


def _create_store_with_curriculum(tmp_path):
    store_path = tmp_path / "open-cvn.sqlite"
    initialize_store(store_path)
    repository = CurriculumRepository(store_path)
    document = json.loads((FIXTURES_DIR / "valid_minimal.json").read_text(encoding="utf-8"))
    curriculum = repository.create_curriculum(CurriculumCreate(display_name="Master CV", document=document))
    return store_path, curriculum


def _save_pdf_with_embedded_xml(path: Path, xml_text: str = SEMANTIC_CVN_XML) -> None:
    document = pymupdf.open()
    document.new_page()
    document.embfile_add("cvn.xml", xml_text.encode("utf-8"), filename="cvn.xml")
    document.save(path)
    document.close()


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


def test_pdf_import_stores_valid_pdf_parse_result(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    store_path = tmp_path / "open-cvn.sqlite"
    initialize_store(store_path)
    input_path = tmp_path / "cv.pdf"
    input_path.write_bytes(b"%PDF synthetic")
    document = json.loads((FIXTURES_DIR / "valid_minimal.json").read_text(encoding="utf-8"))

    def parse_pdf(source, **kwargs):
        assert source == input_path
        assert kwargs["validate_extracted_xml"] is True
        assert kwargs["allow_llm"] is False
        return CvnParseResult(
            source_format=CvnSourceFormat.PDF,
            source_identifier=str(input_path),
            data=document,
            validation_status=CvnValidationStatus.VALID,
            trace=CvnParseTrace(
                source_format=CvnSourceFormat.PDF,
                source_identifier=str(input_path),
                source_path=str(input_path),
                extracted_from="embedded_file:cvn.xml",
            ),
        )

    monkeypatch.setattr(cli_module, "parse_cvn_pdf", parse_pdf)

    exit_code = run([
        "pdf",
        "import",
        str(input_path),
        "--store",
        str(store_path),
        "--name",
        "PDF CV",
        "--as-master",
    ])

    output = capsys.readouterr().out
    repository = CurriculumRepository(store_path)
    assert exit_code == 0
    assert "Imported PDF as curriculum 'PDF CV'." in output
    assert "Import path: embedded_file:cvn.xml" in output
    assert "Assigned master curriculum version 'master'" in output
    assert len(repository.list_curricula()) == 1
    assert len(repository.list_versions()) == 1


def test_pdf_import_stores_semantic_embedded_xml_without_llm(capsys: pytest.CaptureFixture[str], tmp_path: Path):
    store_path = tmp_path / "open-cvn.sqlite"
    initialize_store(store_path)
    input_path = tmp_path / "cv.pdf"
    _save_pdf_with_embedded_xml(input_path)

    exit_code = run([
        "pdf",
        "import",
        str(input_path),
        "--store",
        str(store_path),
        "--name",
        "Semantic PDF CV",
    ])

    output = capsys.readouterr().out
    repository = CurriculumRepository(store_path)
    curricula = repository.list_curricula()
    stored = repository.get_curriculum(curricula[0].id)
    assert exit_code == 0
    assert "Imported PDF as curriculum 'Semantic PDF CV'." in output
    assert "Import path: embedded_file:cvn.xml" in output
    assert len(curricula) == 1
    assert stored is not None
    assert stored.document["curriculum"]["education"][0]["data"]["nombre_del_titulo"]["raw_value"] == (
        "Synthetic Computer Science Degree"
    )


def test_pdf_import_requires_explicit_external_llm_opt_in(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    store_path = tmp_path / "open-cvn.sqlite"
    initialize_store(store_path)
    input_path = tmp_path / "cv.pdf"
    input_path.write_bytes(b"%PDF synthetic")
    called = False

    def parse_pdf(source, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("parse_cvn_pdf should not run before privacy opt-in")

    monkeypatch.setattr(cli_module, "parse_cvn_pdf", parse_pdf)

    exit_code = run([
        "pdf",
        "import",
        str(input_path),
        "--store",
        str(store_path),
        "--llm-provider",
        "openai",
    ])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert called is False
    assert "PDF may contain personal data" in captured.err
    assert CurriculumRepository(store_path).list_curricula() == ()


def test_pdf_import_passes_llm_options_after_privacy_opt_in(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    store_path = tmp_path / "open-cvn.sqlite"
    initialize_store(store_path)
    input_path = tmp_path / "cv.pdf"
    input_path.write_bytes(b"%PDF synthetic")
    document = json.loads((FIXTURES_DIR / "valid_minimal.json").read_text(encoding="utf-8"))

    def parse_pdf(source, **kwargs):
        assert kwargs["allow_llm"] is True
        assert kwargs["llm_config"].provider == "openai"
        assert kwargs["llm_config"].model == "gpt-test"
        assert kwargs["llm_config"].base_url == "https://api.test/v1"
        assert kwargs["llm_config"].api_key_env == "TEST_OPENAI_KEY"
        assert kwargs["llm_config"].timeout_seconds == 3.5
        assert kwargs["llm_config"].pdf_detail == "high"
        return CvnParseResult(
            source_format=CvnSourceFormat.PDF,
            source_identifier=str(input_path),
            data=document,
            validation_status=CvnValidationStatus.VALID,
            trace=CvnParseTrace(
                source_format=CvnSourceFormat.PDF,
                source_identifier=str(input_path),
                source_path=str(input_path),
                extracted_from="llm_fallback",
            ),
        )

    monkeypatch.setattr(cli_module, "parse_cvn_pdf", parse_pdf)

    exit_code = run([
        "pdf",
        "import",
        str(input_path),
        "--store",
        str(store_path),
        "--llm-provider",
        "openai",
        "--llm-model",
        "gpt-test",
        "--llm-base-url",
        "https://api.test/v1",
        "--llm-api-key-env",
        "TEST_OPENAI_KEY",
        "--llm-timeout",
        "3.5",
        "--pdf-detail",
        "high",
        "--allow-external-llm",
    ])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Import path: llm_fallback" in output
    assert len(CurriculumRepository(store_path).list_curricula()) == 1


def test_pdf_import_failure_leaves_store_empty(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    store_path = tmp_path / "open-cvn.sqlite"
    initialize_store(store_path)
    input_path = tmp_path / "cv.pdf"
    input_path.write_bytes(b"%PDF synthetic")

    def parse_pdf(source, **kwargs):
        return CvnParseResult(
            source_format=CvnSourceFormat.PDF,
            source_identifier=str(input_path),
            validation_status=CvnValidationStatus.INVALID,
            errors=(
                CvnParseIssue(
                    code=CvnErrorCode.LLM_OUTPUT_VALIDATION_FAILURE,
                    severity=CvnIssueSeverity.ERROR,
                    message="LLM-produced Open CVN JSON failed local validation.",
                ),
            ),
        )

    monkeypatch.setattr(cli_module, "parse_cvn_pdf", parse_pdf)

    exit_code = run(["pdf", "import", str(input_path), "--store", str(store_path)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "PDF import failed." in captured.err
    assert "llm_output_validation_failure" in captured.err
    assert CurriculumRepository(store_path).list_curricula() == ()


def test_pdf_import_reports_duplicate_master_without_storage_pollution(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    store_path, curriculum = _create_store_with_curriculum(tmp_path)
    repository = CurriculumRepository(store_path)
    repository.assign_master_curriculum(curriculum.id)
    input_path = tmp_path / "cv.pdf"
    input_path.write_bytes(b"%PDF synthetic")
    document = json.loads((FIXTURES_DIR / "valid_minimal.json").read_text(encoding="utf-8"))

    def parse_pdf(source, **kwargs):
        return CvnParseResult(
            source_format=CvnSourceFormat.PDF,
            source_identifier=str(input_path),
            data=document,
            validation_status=CvnValidationStatus.VALID,
        )

    monkeypatch.setattr(cli_module, "parse_cvn_pdf", parse_pdf)

    exit_code = run(["pdf", "import", str(input_path), "--store", str(store_path), "--as-master"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "A master curriculum version already exists." in captured.err
    assert len(repository.list_curricula()) == 1


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


def test_latex_export_writes_master_tex(capsys: pytest.CaptureFixture[str], tmp_path):
    store_path, curriculum = _create_store_with_curriculum(tmp_path)
    repository = CurriculumRepository(store_path)
    repository.assign_master_curriculum(curriculum.id)
    output_path = tmp_path / "exports" / "cv.tex"

    exit_code = run(["latex", "export", str(output_path), "--store", str(store_path), "--version", "master"])

    output = capsys.readouterr().out
    exported_text = output_path.read_text(encoding="utf-8")
    assert exit_code == 0
    assert "Exported LaTeX version 'master'" in output
    assert "Validation status: valid" in output
    assert "\\documentclass[11pt,a4paper]{article}" in exported_text
    assert "\\section*{Version Metadata}" in exported_text
    assert exported_text.endswith("\n")


def test_latex_export_writes_materialized_derived_tex(capsys: pytest.CaptureFixture[str], tmp_path):
    store_path = tmp_path / "open-cvn.sqlite"
    initialize_store(store_path)
    repository = CurriculumRepository(store_path)
    document = json.loads((EXAMPLES_DIR / "research_entry.json").read_text(encoding="utf-8"))
    curriculum = repository.create_curriculum(CurriculumCreate(display_name="Master CV", document=document))
    repository.assign_master_curriculum(curriculum.id)
    repository.create_derived_version("public")
    repository.exclude_from_version("public", "/curriculum/research")
    output_path = tmp_path / "public.tex"

    exit_code = run(["latex", "export", str(output_path), "--store", str(store_path), "--version", "public"])

    output = capsys.readouterr().out
    exported_text = output_path.read_text(encoding="utf-8")
    assert exit_code == 0
    assert "Exported LaTeX version 'public'" in output
    assert "\\item[Version] public" in exported_text
    assert "Open CVN data representation" not in exported_text


def test_latex_export_reports_missing_version(capsys: pytest.CaptureFixture[str], tmp_path):
    store_path = tmp_path / "open-cvn.sqlite"
    initialize_store(store_path)
    output_path = tmp_path / "missing.tex"

    exit_code = run(["latex", "export", str(output_path), "--store", str(store_path), "--version", "missing"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "LaTeX export failed." in captured.err
    assert "Curriculum version not found: missing" in captured.err


def test_pdf_generate_reports_missing_compiler(capsys: pytest.CaptureFixture[str], monkeypatch):
    def unavailable(*args, **kwargs):
        raise PdfGenerationUnavailable(("latexmk", "pdflatex"))

    monkeypatch.setattr(cli_module, "generate_pdf_document", unavailable)

    exit_code = run(["pdf", "generate", "cv.pdf"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "PDF generation unavailable." in captured.err
    assert "No supported TeX compiler found" in captured.err


def test_pdf_doctor_reports_available_engine(capsys: pytest.CaptureFixture[str], monkeypatch, tmp_path):
    diagnostic = PdfEnvironmentDiagnostic(
        managed_cache_path=tmp_path / "tectonic",
        managed_tectonic=str(tmp_path / "tectonic" / "tectonic"),
        system_tectonic=None,
        latexmk=None,
        pdflatex=None,
        selected_engine="managed tectonic",
        selected_executable=str(tmp_path / "tectonic" / "tectonic"),
        managed_download_supported=True,
    )

    monkeypatch.setattr(cli_module, "diagnose_pdf_environment", lambda: diagnostic)

    exit_code = run(["pdf", "doctor"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "PDF generation environment:" in output
    assert "Selected engine: managed tectonic" in output


def test_pdf_doctor_reports_missing_engine(capsys: pytest.CaptureFixture[str], monkeypatch, tmp_path):
    diagnostic = PdfEnvironmentDiagnostic(
        managed_cache_path=tmp_path / "tectonic",
        managed_tectonic=None,
        system_tectonic=None,
        latexmk=None,
        pdflatex=None,
        selected_engine=None,
        selected_executable=None,
        managed_download_supported=True,
    )

    monkeypatch.setattr(cli_module, "diagnose_pdf_environment", lambda: diagnostic)

    exit_code = run(["pdf", "doctor"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "PDF generation unavailable." in captured.err
    assert "run open-cvn pdf generate to download managed Tectonic" in captured.err


def test_pdf_generate_writes_master_pdf(capsys: pytest.CaptureFixture[str], monkeypatch, tmp_path):
    store_path, curriculum = _create_store_with_curriculum(tmp_path)
    repository = CurriculumRepository(store_path)
    repository.assign_master_curriculum(curriculum.id)
    output_path = tmp_path / "exports" / "cv.pdf"
    calls = []

    def fake_generate_pdf_document(repository, **kwargs):
        calls.append(kwargs)
        output = Path(kwargs["output_path"])
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(b"%PDF-1.4\n")
        return PdfGenerationResult(
            output_path=output,
            version_name="master",
            validation_status="valid",
            compiler_name="latexmk",
            preview_opened=False,
        )

    monkeypatch.setattr(cli_module, "generate_pdf_document", fake_generate_pdf_document)

    exit_code = run(["pdf", "generate", str(output_path), "--store", str(store_path), "--version", "master"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert output_path.exists()
    assert "Generated PDF version 'master'" in output
    assert "Validation status: valid" in output
    assert "Compiler: latexmk" in output
    assert calls == [
        {
            "version": "master",
            "output_path": str(output_path),
            "open_pdf": False,
            "allow_managed_tectonic_download": True,
        }
    ]


def test_pdf_generate_writes_materialized_derived_pdf(capsys: pytest.CaptureFixture[str], monkeypatch, tmp_path):
    store_path = tmp_path / "open-cvn.sqlite"
    initialize_store(store_path)
    repository = CurriculumRepository(store_path)
    document = json.loads((EXAMPLES_DIR / "research_entry.json").read_text(encoding="utf-8"))
    curriculum = repository.create_curriculum(CurriculumCreate(display_name="Master CV", document=document))
    repository.assign_master_curriculum(curriculum.id)
    repository.create_derived_version("public")
    repository.exclude_from_version("public", "/curriculum/research")
    output_path = tmp_path / "public.pdf"
    materialized_versions = []

    def fake_generate_pdf_document(repository, **kwargs):
        materialized_versions.append(repository.materialize_version(kwargs["version"]).document)
        output = Path(kwargs["output_path"])
        output.write_bytes(b"%PDF-1.4\n")
        return PdfGenerationResult(
            output_path=output,
            version_name="public",
            validation_status="valid",
            compiler_name="pdflatex",
            preview_opened=False,
        )

    monkeypatch.setattr(cli_module, "generate_pdf_document", fake_generate_pdf_document)

    exit_code = run(["pdf", "generate", str(output_path), "--store", str(store_path), "--version", "public"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Generated PDF version 'public'" in output
    assert "Compiler: pdflatex" in output
    assert materialized_versions[0]["curriculum"]["research"] == []


def test_pdf_generate_open_triggers_preview_flag(capsys: pytest.CaptureFixture[str], monkeypatch, tmp_path):
    store_path, curriculum = _create_store_with_curriculum(tmp_path)
    CurriculumRepository(store_path).assign_master_curriculum(curriculum.id)
    output_path = tmp_path / "cv.pdf"
    calls = []

    def fake_generate_pdf_document(repository, **kwargs):
        calls.append(kwargs)
        output = Path(kwargs["output_path"])
        output.write_bytes(b"%PDF-1.4\n")
        return PdfGenerationResult(
            output_path=output,
            version_name="master",
            validation_status="valid",
            compiler_name="latexmk",
            preview_opened=True,
        )

    monkeypatch.setattr(cli_module, "generate_pdf_document", fake_generate_pdf_document)

    exit_code = run(["pdf", "generate", str(output_path), "--store", str(store_path), "--open"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Preview handoff: opened" in output
    assert calls[0]["open_pdf"] is True


def test_pdf_generate_reports_missing_version(capsys: pytest.CaptureFixture[str], tmp_path):
    store_path = tmp_path / "open-cvn.sqlite"
    initialize_store(store_path)
    output_path = tmp_path / "missing.pdf"

    exit_code = run(["pdf", "generate", str(output_path), "--store", str(store_path), "--version", "missing"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "PDF generation failed." in captured.err
    assert "Curriculum version not found: missing" in captured.err


def test_pdf_generate_reports_compiler_failure(capsys: pytest.CaptureFixture[str], monkeypatch, tmp_path):
    store_path, curriculum = _create_store_with_curriculum(tmp_path)
    CurriculumRepository(store_path).assign_master_curriculum(curriculum.id)
    diagnostic = CompilerRunDiagnostic(
        command=("latexmk", "cv.tex"),
        return_code=1,
        stdout="compiler stdout",
        stderr="compiler stderr",
    )

    def fake_generate_pdf_document(repository, **kwargs):
        raise PdfCompilationError("PDF compilation failed.", (diagnostic,))

    monkeypatch.setattr(cli_module, "generate_pdf_document", fake_generate_pdf_document)

    exit_code = run(["pdf", "generate", str(tmp_path / "cv.pdf"), "--store", str(store_path)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "PDF generation failed." in captured.err
    assert "PDF compilation failed." in captured.err
    assert "compiler stdout" in captured.err
    assert "compiler stderr" in captured.err
