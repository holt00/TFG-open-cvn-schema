from __future__ import annotations

import os
import hashlib
import platform
import shutil
import subprocess
import tarfile
import tempfile
import urllib.request
import webbrowser
import zipfile
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from open_cvn_app.latex import render_latex_document
from open_cvn_app.storage import CurriculumRepository


MANAGED_TECTONIC_VERSION = "0.16.9"
MANAGED_TECTONIC_CACHE_ENV = "OPEN_CVN_TECTONIC_CACHE"
DEFAULT_COMPILERS = ("tectonic", "latexmk", "pdflatex")
DEFAULT_TIMEOUT_SECONDS = 60


@dataclass(frozen=True)
class TexCompiler:
    name: str
    executable: str
    managed: bool = False


@dataclass(frozen=True)
class ManagedTectonicAsset:
    platform_key: str
    archive_name: str
    url: str
    sha256: str


@dataclass(frozen=True)
class PdfEnvironmentDiagnostic:
    managed_cache_path: Path
    managed_tectonic: str | None
    system_tectonic: str | None
    latexmk: str | None
    pdflatex: str | None
    selected_engine: str | None
    selected_executable: str | None
    managed_download_supported: bool


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
ManagedDownloader = Callable[[Path], Path]


def discover_tex_compiler(
    *,
    lookup: CompilerLookup = shutil.which,
    compiler_order: Sequence[str] = DEFAULT_COMPILERS,
    managed_cache_dir: Path | None = None,
    allow_managed_download: bool = False,
    managed_downloader: ManagedDownloader | None = None,
) -> TexCompiler:
    cache_dir = managed_cache_dir or managed_tectonic_cache_dir()
    cached_tectonic = cached_managed_tectonic_path(cache_dir)
    if cached_tectonic is not None:
        return TexCompiler(name="tectonic", executable=str(cached_tectonic), managed=True)
    if allow_managed_download:
        downloader = managed_downloader or download_managed_tectonic
        try:
            cache_dir.mkdir(parents=True, exist_ok=True)
            downloaded = downloader(cache_dir)
        except (OSError, RuntimeError, ValueError):
            downloaded = None
        if downloaded is not None:
            return TexCompiler(name="tectonic", executable=str(downloaded), managed=True)
    for compiler_name in compiler_order:
        executable = lookup(compiler_name)
        if executable:
            return TexCompiler(name=compiler_name, executable=executable)
    raise PdfGenerationUnavailable(compiler_order)


def diagnose_pdf_environment(
    *,
    lookup: CompilerLookup = shutil.which,
    managed_cache_dir: Path | None = None,
) -> PdfEnvironmentDiagnostic:
    cache_dir = managed_cache_dir or managed_tectonic_cache_dir()
    managed_tectonic = cached_managed_tectonic_path(cache_dir)
    system_tectonic = lookup("tectonic")
    latexmk = lookup("latexmk")
    pdflatex = lookup("pdflatex")
    selected_engine = selected_executable = None
    if managed_tectonic is not None:
        selected_engine = "managed tectonic"
        selected_executable = str(managed_tectonic)
    elif system_tectonic:
        selected_engine = "tectonic"
        selected_executable = system_tectonic
    elif latexmk:
        selected_engine = "latexmk"
        selected_executable = latexmk
    elif pdflatex:
        selected_engine = "pdflatex"
        selected_executable = pdflatex
    return PdfEnvironmentDiagnostic(
        managed_cache_path=cache_dir,
        managed_tectonic=str(managed_tectonic) if managed_tectonic is not None else None,
        system_tectonic=system_tectonic,
        latexmk=latexmk,
        pdflatex=pdflatex,
        selected_engine=selected_engine,
        selected_executable=selected_executable,
        managed_download_supported=tectonic_asset_for_current_platform() is not None,
    )


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
    allow_managed_tectonic_download: bool = False,
    managed_cache_dir: Path | None = None,
    managed_downloader: ManagedDownloader | None = None,
) -> PdfGenerationResult:
    materialized = repository.materialize_version(version)
    compiler = discover_tex_compiler(
        lookup=compiler_lookup,
        allow_managed_download=allow_managed_tectonic_download,
        managed_cache_dir=managed_cache_dir,
        managed_downloader=managed_downloader,
    )
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
    if compiler.name == "tectonic":
        diagnostics = _run_tectonic(
            compiler,
            tex_path,
            build_dir=build_dir,
            runner=runner,
            timeout_seconds=timeout_seconds,
        )
    elif compiler.name == "latexmk":
        diagnostics = _run_latexmk(
            compiler,
            tex_path,
            build_dir=build_dir,
            runner=runner,
            timeout_seconds=timeout_seconds,
        )
    else:
        diagnostics = _run_pdflatex(
            compiler,
            tex_path,
            build_dir=build_dir,
            runner=runner,
            timeout_seconds=timeout_seconds,
        )
    failing = next((diagnostic for diagnostic in diagnostics if diagnostic.return_code != 0), None)
    if failing is not None:
        raise PdfCompilationError("PDF compilation failed.", diagnostics)
    if not expected_pdf.exists():
        raise PdfCompilationError("PDF compiler finished but did not create the expected PDF.", diagnostics)
    return expected_pdf


def _run_tectonic(
    compiler: TexCompiler,
    tex_path: Path,
    *,
    build_dir: Path,
    runner: Runner,
    timeout_seconds: int,
) -> tuple[CompilerRunDiagnostic, ...]:
    command = (
        compiler.executable,
        str(tex_path),
        "--outdir",
        str(build_dir),
    )
    return (_run_compiler(command, build_dir=build_dir, runner=runner, timeout_seconds=timeout_seconds),)


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


def managed_tectonic_cache_dir() -> Path:
    configured = os.environ.get(MANAGED_TECTONIC_CACHE_ENV)
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".cache" / "open-cvn" / "tectonic" / MANAGED_TECTONIC_VERSION


def cached_managed_tectonic_path(cache_dir: Path) -> Path | None:
    executable = "tectonic.exe" if os.name == "nt" else "tectonic"
    candidate = cache_dir / executable
    if candidate.exists() and os.access(candidate, os.X_OK):
        return candidate
    return None


def download_managed_tectonic(cache_dir: Path) -> Path:
    asset = tectonic_asset_for_current_platform()
    if asset is None:
        raise RuntimeError("Managed Tectonic download is not available for this platform.")
    cache_dir.mkdir(parents=True, exist_ok=True)
    archive_path = cache_dir / asset.archive_name
    with urllib.request.urlopen(asset.url, timeout=60) as response:  # noqa: S310 - pinned GitHub release URL.
        archive_bytes = response.read()
    digest = hashlib.sha256(archive_bytes).hexdigest()
    if digest != asset.sha256:
        raise ValueError("Downloaded Tectonic archive checksum does not match the pinned release digest.")
    archive_path.write_bytes(archive_bytes)
    _extract_tectonic_archive(archive_path, cache_dir)
    cached = cached_managed_tectonic_path(cache_dir)
    if cached is None:
        raise RuntimeError("Managed Tectonic archive did not provide an executable.")
    return cached


def tectonic_asset_for_current_platform() -> ManagedTectonicAsset | None:
    system = platform.system().lower()
    machine = platform.machine().lower()
    if system == "linux" and machine in {"x86_64", "amd64"}:
        return _asset(
            "x86_64-unknown-linux-gnu",
            "f3c825128095dc3399ea11c08c18035b33050a216930c295c79e8eb11bd21de4",
            extension="tar.gz",
        )
    if system == "linux" and machine in {"aarch64", "arm64"}:
        return _asset(
            "aarch64-unknown-linux-musl",
            "f9aa39017dbd51f111fdb93dda222178cbe51c8193508fc567b523cc74fff9c1",
            extension="tar.gz",
        )
    if system == "darwin" and machine in {"x86_64", "amd64"}:
        return _asset(
            "x86_64-apple-darwin",
            "79d8839fa3594bfea9b2bf2ac0a0455bcc4d0de956a5e5c403107e9a72f79e86",
            extension="tar.gz",
        )
    if system == "darwin" and machine in {"aarch64", "arm64"}:
        return _asset(
            "aarch64-apple-darwin",
            "edb67c61aba768289f6da441c9e6f523cfaff4f8b2a5708523ef29c543f8e88e",
            extension="tar.gz",
        )
    if system == "windows" and machine in {"x86_64", "amd64"}:
        return _asset(
            "x86_64-pc-windows-msvc",
            "131a24604785a9600989a3d91225f597df52ac06f00aeffe86fd529f99ee5cdd",
            extension="zip",
        )
    return None


def _asset(platform_key: str, sha256: str, *, extension: str) -> ManagedTectonicAsset:
    archive_name = f"tectonic-{MANAGED_TECTONIC_VERSION}-{platform_key}.{extension}"
    return ManagedTectonicAsset(
        platform_key=platform_key,
        archive_name=archive_name,
        url=(
            "https://github.com/tectonic-typesetting/tectonic/releases/download/"
            f"tectonic%40{MANAGED_TECTONIC_VERSION}/{archive_name}"
        ),
        sha256=sha256,
    )


def _extract_tectonic_archive(archive_path: Path, cache_dir: Path) -> None:
    executable = "tectonic.exe" if os.name == "nt" else "tectonic"
    if archive_path.suffix == ".zip":
        with zipfile.ZipFile(archive_path) as archive:
            member_name = _single_executable_member(archive.namelist(), executable)
            (cache_dir / executable).write_bytes(archive.read(member_name))
    else:
        with tarfile.open(archive_path, "r:gz") as archive:
            names = archive.getnames()
            member_name = _single_executable_member(names, executable)
            member = archive.extractfile(member_name)
            if member is None:
                raise RuntimeError("Tectonic archive executable could not be read.")
            (cache_dir / executable).write_bytes(member.read())
    if os.name != "nt":
        (cache_dir / executable).chmod(0o755)


def _single_executable_member(names: Sequence[str], executable: str) -> str:
    matches = [name for name in names if Path(name).name == executable]
    if len(matches) != 1:
        raise RuntimeError("Tectonic archive does not contain exactly one executable.")
    return matches[0]
