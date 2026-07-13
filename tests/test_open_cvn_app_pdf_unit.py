from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from open_cvn_app.pdf import (
    PdfCompilationError,
    PdfGenerationUnavailable,
    PdfPreviewError,
    discover_tex_compiler,
    format_compilation_diagnostics,
    generate_pdf_document,
)
from open_cvn_app.storage import CurriculumCreate, CurriculumRepository, initialize_store


FIXTURES_DIR = Path(__file__).parent / "fixtures" / "open_cvn"
EXAMPLES_DIR = Path(__file__).parent.parent / "examples" / "open_cvn"


def _repository_with_master(tmp_path: Path, document_path: Path | None = None) -> CurriculumRepository:
    store_path = tmp_path / "open-cvn.sqlite"
    initialize_store(store_path)
    repository = CurriculumRepository(store_path)
    source = document_path or FIXTURES_DIR / "valid_minimal.json"
    document = json.loads(source.read_text(encoding="utf-8"))
    curriculum = repository.create_curriculum(CurriculumCreate(display_name="Master CV", document=document))
    repository.assign_master_curriculum(curriculum.id)
    return repository


def test_discover_tex_compiler_prefers_latexmk():
    def lookup(name: str) -> str | None:
        return {"latexmk": "/usr/bin/latexmk", "pdflatex": "/usr/bin/pdflatex"}.get(name)

    compiler = discover_tex_compiler(lookup=lookup)

    assert compiler.name == "latexmk"
    assert compiler.executable == "/usr/bin/latexmk"


def test_discover_tex_compiler_uses_pdflatex_fallback():
    def lookup(name: str) -> str | None:
        return {"pdflatex": "/usr/bin/pdflatex"}.get(name)

    compiler = discover_tex_compiler(lookup=lookup)

    assert compiler.name == "pdflatex"
    assert compiler.executable == "/usr/bin/pdflatex"


def test_discover_tex_compiler_reports_missing_compiler():
    with pytest.raises(PdfGenerationUnavailable, match="No supported TeX compiler found") as exc_info:
        discover_tex_compiler(lookup=lambda name: None)

    assert exc_info.value.searched_compilers == ("latexmk", "pdflatex")


def test_generate_pdf_document_with_latexmk_copies_expected_pdf(tmp_path):
    repository = _repository_with_master(tmp_path)
    output_path = tmp_path / "exports" / "cv.pdf"
    calls: list[tuple[str, ...]] = []
    environments: list[dict[str, str]] = []

    def runner(command: tuple[str, ...], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        environments.append(kwargs["env"])
        tex_path = Path(command[-1])
        (Path(kwargs["cwd"]) / f"{tex_path.stem}.pdf").write_bytes(b"%PDF-1.4\n")
        return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

    result = generate_pdf_document(
        repository,
        version="master",
        output_path=output_path,
        compiler_lookup=lambda name: "/usr/bin/latexmk" if name == "latexmk" else None,
        runner=runner,
    )

    assert result.output_path == output_path
    assert result.version_name == "master"
    assert result.validation_status == "valid"
    assert result.compiler_name == "latexmk"
    assert result.preview_opened is False
    assert output_path.read_bytes() == b"%PDF-1.4\n"
    assert len(calls) == 1
    assert calls[0][1:5] == ("-pdf", "-interaction=nonstopmode", "-halt-on-error", "-outdir")
    assert environments[0]["SOURCE_DATE_EPOCH"] == "0"


def test_generate_pdf_document_with_pdflatex_runs_two_passes(tmp_path):
    repository = _repository_with_master(tmp_path)
    output_path = tmp_path / "cv.pdf"
    calls: list[tuple[str, ...]] = []

    def runner(command: tuple[str, ...], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        tex_path = Path(command[-1])
        (Path(kwargs["cwd"]) / f"{tex_path.stem}.pdf").write_bytes(b"%PDF-1.4\n")
        return subprocess.CompletedProcess(command, 0, stdout=f"pass {len(calls)}", stderr="")

    result = generate_pdf_document(
        repository,
        version="master",
        output_path=output_path,
        compiler_lookup=lambda name: "/usr/bin/pdflatex" if name == "pdflatex" else None,
        runner=runner,
    )

    assert result.compiler_name == "pdflatex"
    assert output_path.exists()
    assert len(calls) == 2
    assert all(call[1:4] == ("-interaction=nonstopmode", "-halt-on-error", "-output-directory") for call in calls)


def test_generate_pdf_document_preserves_compiler_failure_diagnostics(tmp_path):
    repository = _repository_with_master(tmp_path)
    command_result = subprocess.CompletedProcess(("latexmk",), 12, stdout="compiler stdout", stderr="compiler stderr")

    def runner(command: tuple[str, ...], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        return command_result

    with pytest.raises(PdfCompilationError, match="PDF compilation failed") as exc_info:
        generate_pdf_document(
            repository,
            version="master",
            output_path=tmp_path / "cv.pdf",
            compiler_lookup=lambda name: "/usr/bin/latexmk" if name == "latexmk" else None,
            runner=runner,
        )

    diagnostics = exc_info.value.diagnostics
    assert len(diagnostics) == 1
    assert diagnostics[0].return_code == 12
    assert diagnostics[0].stdout == "compiler stdout"
    assert diagnostics[0].stderr == "compiler stderr"
    assert "compiler stdout" in format_compilation_diagnostics(diagnostics)


def test_generate_pdf_document_preserves_timeout_diagnostics(tmp_path):
    repository = _repository_with_master(tmp_path)

    def runner(command: tuple[str, ...], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        raise subprocess.TimeoutExpired(command, timeout=1, output=b"partial stdout", stderr=b"partial stderr")

    with pytest.raises(PdfCompilationError, match="PDF compilation failed") as exc_info:
        generate_pdf_document(
            repository,
            version="master",
            output_path=tmp_path / "cv.pdf",
            compiler_lookup=lambda name: "/usr/bin/latexmk" if name == "latexmk" else None,
            runner=runner,
            timeout_seconds=1,
        )

    diagnostic = exc_info.value.diagnostics[0]
    assert diagnostic.return_code is None
    assert diagnostic.timed_out is True
    assert diagnostic.stdout == "partial stdout"
    assert diagnostic.stderr == "partial stderr"


def test_generate_pdf_document_reports_missing_pdf_after_success(tmp_path):
    repository = _repository_with_master(tmp_path)

    def runner(command: tuple[str, ...], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

    with pytest.raises(PdfCompilationError, match="did not create the expected PDF"):
        generate_pdf_document(
            repository,
            version="master",
            output_path=tmp_path / "cv.pdf",
            compiler_lookup=lambda name: "/usr/bin/latexmk" if name == "latexmk" else None,
            runner=runner,
        )


def test_generate_pdf_document_opens_preview_when_requested(tmp_path):
    repository = _repository_with_master(tmp_path, EXAMPLES_DIR / "research_entry.json")
    opened_urls: list[str] = []

    def runner(command: tuple[str, ...], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        tex_path = Path(command[-1])
        (Path(kwargs["cwd"]) / f"{tex_path.stem}.pdf").write_bytes(b"%PDF-1.4\n")
        return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

    result = generate_pdf_document(
        repository,
        version="master",
        output_path=tmp_path / "cv.pdf",
        open_pdf=True,
        compiler_lookup=lambda name: "/usr/bin/latexmk" if name == "latexmk" else None,
        runner=runner,
        preview_opener=lambda url: opened_urls.append(url) is None or True,
    )

    assert result.preview_opened is True
    assert opened_urls == [(tmp_path / "cv.pdf").resolve().as_uri()]


def test_generate_pdf_document_reports_preview_failure(tmp_path):
    repository = _repository_with_master(tmp_path)

    def runner(command: tuple[str, ...], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        tex_path = Path(command[-1])
        (Path(kwargs["cwd"]) / f"{tex_path.stem}.pdf").write_bytes(b"%PDF-1.4\n")
        return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

    with pytest.raises(PdfPreviewError, match="Could not open generated PDF"):
        generate_pdf_document(
            repository,
            version="master",
            output_path=tmp_path / "cv.pdf",
            open_pdf=True,
            compiler_lookup=lambda name: "/usr/bin/latexmk" if name == "latexmk" else None,
            runner=runner,
            preview_opener=lambda url: False,
        )
