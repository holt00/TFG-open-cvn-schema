from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import webbrowser
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from open_cvn_app.latex import render_latex_document
from open_cvn_app.storage import CurriculumRepository


DEFAULT_COMPILERS = ("latexmk", "pdflatex")
DEFAULT_TIMEOUT_SECONDS = 60


@dataclass(frozen=True)
class TexCompiler:
    name: str
    executable: str


@dataclass(frozen=True)
class CompilerRunDiagnostic:
    command: tuple[str, ...]
    return_code: int | None
    stdout: str
    stderr: str
    timed_out: bool = False


@dataclass(frozen=True)
class PdfGenerationResult:
    output_path: Path
    version_name: str
    validation_status: str
    compiler_name: str
    preview_opened: bool


class PdfGenerationUnavailable(RuntimeError):
    def __init__(self, searched_compilers: Sequence[str]) -> None:
        self.searched_compilers = tuple(searched_compilers)
        super().__init__(
            "No supported TeX compiler found. "
            f"Install one of: {', '.join(self.searched_compilers)}."
        )


class PdfCompilationError(RuntimeError):
    def __init__(self, message: str, diagnostics: Sequence[CompilerRunDiagnostic]) -> None:
        self.diagnostics = tuple(diagnostics)
        super().__init__(message)


class PdfPreviewError(RuntimeError):
    pass


CompilerLookup = Callable[[str], str | None]
Runner = Callable[..., subprocess.CompletedProcess[str]]
PreviewOpener = Callable[[str], bool]


def discover_tex_compiler(
    *,
    lookup: CompilerLookup = shutil.which,
    compiler_order: Sequence[str] = DEFAULT_COMPILERS,
) -> TexCompiler:
    for compiler_name in compiler_order:
        executable = lookup(compiler_name)
        if executable:
            return TexCompiler(name=compiler_name, executable=executable)
    raise PdfGenerationUnavailable(compiler_order)


def generate_pdf_document(
    repository: CurriculumRepository,
    *,
    version: str,
    output_path: str | Path,
    open_pdf: bool = False,
    compiler_lookup: CompilerLookup = shutil.which,
    runner: Runner = subprocess.run,
    preview_opener: PreviewOpener = webbrowser.open,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> PdfGenerationResult:
    materialized = repository.materialize_version(version)
    compiler = discover_tex_compiler(lookup=compiler_lookup)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="open-cvn-pdf-") as build_dir_name:
        build_dir = Path(build_dir_name)
        tex_path = build_dir / f"{path.stem}.tex"
        tex_path.write_text(
            render_latex_document(materialized.document, version_name=materialized.version.name),
            encoding="utf-8",
        )
        built_pdf = _compile_tex(
            compiler,
            tex_path,
            build_dir=build_dir,
            runner=runner,
            timeout_seconds=timeout_seconds,
        )
        shutil.copyfile(built_pdf, path)

    preview_opened = False
    if open_pdf:
        preview_opened = _open_pdf(path, opener=preview_opener)

    return PdfGenerationResult(
        output_path=path,
        version_name=materialized.version.name,
        validation_status=materialized.validation_status,
        compiler_name=compiler.name,
        preview_opened=preview_opened,
    )


def format_compilation_diagnostics(diagnostics: Sequence[CompilerRunDiagnostic]) -> str:
    if not diagnostics:
        return "-"
    lines: list[str] = []
    for index, diagnostic in enumerate(diagnostics, start=1):
        lines.extend(
            (
                f"Run {index}:",
                f"Command: {' '.join(diagnostic.command)}",
                f"Return code: {diagnostic.return_code if diagnostic.return_code is not None else '-'}",
                f"Timed out: {diagnostic.timed_out}",
                f"Stdout: {_compact_output(diagnostic.stdout)}",
                f"Stderr: {_compact_output(diagnostic.stderr)}",
            )
        )
    return "\n".join(lines)


def _compile_tex(
    compiler: TexCompiler,
    tex_path: Path,
    *,
    build_dir: Path,
    runner: Runner,
    timeout_seconds: int,
) -> Path:
    expected_pdf = build_dir / f"{tex_path.stem}.pdf"
    diagnostics = (
        _run_latexmk(compiler, tex_path, build_dir=build_dir, runner=runner, timeout_seconds=timeout_seconds)
        if compiler.name == "latexmk"
        else _run_pdflatex(compiler, tex_path, build_dir=build_dir, runner=runner, timeout_seconds=timeout_seconds)
    )
    failing = next((diagnostic for diagnostic in diagnostics if diagnostic.return_code != 0), None)
    if failing is not None:
        raise PdfCompilationError("PDF compilation failed.", diagnostics)
    if not expected_pdf.exists():
        raise PdfCompilationError("PDF compiler finished but did not create the expected PDF.", diagnostics)
    return expected_pdf


def _run_latexmk(
    compiler: TexCompiler,
    tex_path: Path,
    *,
    build_dir: Path,
    runner: Runner,
    timeout_seconds: int,
) -> tuple[CompilerRunDiagnostic, ...]:
    command = (
        compiler.executable,
        "-pdf",
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-outdir",
        str(build_dir),
        str(tex_path),
    )
    return (_run_compiler(command, build_dir=build_dir, runner=runner, timeout_seconds=timeout_seconds),)


def _run_pdflatex(
    compiler: TexCompiler,
    tex_path: Path,
    *,
    build_dir: Path,
    runner: Runner,
    timeout_seconds: int,
) -> tuple[CompilerRunDiagnostic, ...]:
    command = (
        compiler.executable,
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-output-directory",
        str(build_dir),
        str(tex_path),
    )
    diagnostics: list[CompilerRunDiagnostic] = []
    for _ in range(2):
        diagnostic = _run_compiler(command, build_dir=build_dir, runner=runner, timeout_seconds=timeout_seconds)
        diagnostics.append(diagnostic)
        if diagnostic.return_code != 0:
            break
    return tuple(diagnostics)


def _run_compiler(
    command: Sequence[str],
    *,
    build_dir: Path,
    runner: Runner,
    timeout_seconds: int,
) -> CompilerRunDiagnostic:
    try:
        completed = runner(
            tuple(command),
            cwd=build_dir,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
            env=_compiler_environment(os.environ),
        )
    except subprocess.TimeoutExpired as exc:
        return CompilerRunDiagnostic(
            command=tuple(command),
            return_code=None,
            stdout=_timeout_output(exc.stdout),
            stderr=_timeout_output(exc.stderr),
            timed_out=True,
        )
    return CompilerRunDiagnostic(
        command=tuple(command),
        return_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def _compiler_environment(base_environment: Mapping[str, str]) -> dict[str, str]:
    environment = dict(base_environment)
    environment.setdefault("SOURCE_DATE_EPOCH", "0")
    return environment


def _open_pdf(path: Path, *, opener: PreviewOpener) -> bool:
    opened = opener(path.resolve().as_uri())
    if not opened:
        raise PdfPreviewError(f"Could not open generated PDF for preview: {path}")
    return opened


def _timeout_output(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode(errors="replace")
    return str(value)


def _compact_output(value: str, *, limit: int = 1200) -> str:
    if not value:
        return "-"
    normalized = value.strip()
    if len(normalized) <= limit:
        return normalized
    return f"{normalized[:limit]}... <truncated>"
