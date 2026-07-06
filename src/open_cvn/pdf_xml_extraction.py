from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from xml.etree import ElementTree

import pymupdf


PdfInput = Path | str | bytes
PdfXmlSourceKind = Literal["embedded_file", "xml_metadata"]


@dataclass(frozen=True)
class ExtractedCvnXml:
    xml_text: str
    xml_bytes_size: int
    source_kind: PdfXmlSourceKind
    source_name: str | None = None
    source_index: int | None = None
    metadata_xref: int | None = None


@dataclass(frozen=True)
class PdfXmlExtractionDiagnostics:
    source_path: str | None
    embedded_file_count: int
    candidate_count: int
    metadata_present: bool

    def as_details(self) -> dict[str, str | int | float | bool | None]:
        return {
            "embedded_file_count": self.embedded_file_count,
            "candidate_count": self.candidate_count,
            "metadata_present": self.metadata_present,
        }


@dataclass(frozen=True)
class PdfXmlExtractionResult:
    extracted_xml: ExtractedCvnXml | None
    diagnostics: PdfXmlExtractionDiagnostics


class UnsupportedPdfInputError(TypeError):
    pass


class UnreadablePdfError(RuntimeError):
    def __init__(self, message: str, *, source_path: str | None = None) -> None:
        super().__init__(message)
        self.source_path = source_path


def extract_cvn_xml_from_pdf(source: PdfInput) -> PdfXmlExtractionResult:
    source_path = _source_path(source)
    try:
        with _open_pdf(source) as document:
            candidate_count = 0
            embedded_file_count = _embedded_file_count(document)

            for candidate in _iter_embedded_file_candidates(document):
                candidate_count += 1
                extracted = _validated_cvn_xml(candidate)
                if extracted is not None:
                    diagnostics = PdfXmlExtractionDiagnostics(
                        source_path=source_path,
                        embedded_file_count=embedded_file_count,
                        candidate_count=candidate_count,
                        metadata_present=bool(_get_xml_metadata(document)),
                    )
                    return PdfXmlExtractionResult(extracted, diagnostics)

            metadata = _get_xml_metadata(document)
            if metadata:
                candidate_count += 1
                metadata_candidate = ExtractedCvnXml(
                    xml_text=metadata,
                    xml_bytes_size=len(metadata.encode("utf-8")),
                    source_kind="xml_metadata",
                    source_name="xml_metadata",
                    metadata_xref=_xml_metadata_xref(document),
                )
                extracted = _validated_cvn_xml(metadata_candidate)
                if extracted is not None:
                    diagnostics = PdfXmlExtractionDiagnostics(
                        source_path=source_path,
                        embedded_file_count=embedded_file_count,
                        candidate_count=candidate_count,
                        metadata_present=True,
                    )
                    return PdfXmlExtractionResult(extracted, diagnostics)

            diagnostics = PdfXmlExtractionDiagnostics(
                source_path=source_path,
                embedded_file_count=embedded_file_count,
                candidate_count=candidate_count,
                metadata_present=bool(metadata),
            )
            return PdfXmlExtractionResult(None, diagnostics)
    except UnsupportedPdfInputError:
        raise
    except UnreadablePdfError:
        raise
    except Exception as exc:
        raise UnreadablePdfError(str(exc), source_path=source_path) from exc


def _open_pdf(source: PdfInput) -> pymupdf.Document:
    if isinstance(source, bytes):
        return pymupdf.open(stream=source, filetype="pdf")
    if isinstance(source, Path):
        return pymupdf.open(source)
    if isinstance(source, str):
        source_path = Path(source)
        if source_path.exists():
            return pymupdf.open(source_path)
        raise UnreadablePdfError(f"PDF path does not exist: {source}", source_path=source)
    raise UnsupportedPdfInputError(f"Unsupported PDF input type: {type(source).__name__}")


def _source_path(source: PdfInput) -> str | None:
    if isinstance(source, Path):
        return str(source)
    if isinstance(source, str) and Path(source).exists():
        return source
    return None


def _embedded_file_count(document: pymupdf.Document) -> int:
    try:
        return int(document.embfile_count())
    except Exception:
        return 0


def _iter_embedded_file_candidates(document: pymupdf.Document) -> tuple[ExtractedCvnXml, ...]:
    names = tuple(document.embfile_names())
    prioritized_names = sorted(
        names,
        key=lambda name: (
            not name.lower().endswith(".xml"),
            "cvn" not in name.lower(),
            name.lower(),
        ),
    )
    candidates: list[ExtractedCvnXml] = []
    for index, name in enumerate(prioritized_names):
        payload = document.embfile_get(name)
        text = _decode_xml_candidate(payload)
        if text is None:
            continue
        if not _name_or_payload_looks_xml(name, text):
            continue
        candidates.append(
            ExtractedCvnXml(
                xml_text=text,
                xml_bytes_size=len(payload),
                source_kind="embedded_file",
                source_name=name,
                source_index=index,
            )
        )
    return tuple(candidates)


def _get_xml_metadata(document: pymupdf.Document) -> str:
    try:
        return document.get_xml_metadata() or ""
    except Exception:
        return ""


def _xml_metadata_xref(document: pymupdf.Document) -> int | None:
    xref_getter = getattr(document, "xref_xml_metadata", None)
    if xref_getter is None:
        return None
    try:
        xref = int(xref_getter())
    except Exception:
        return None
    return xref or None


def _decode_xml_candidate(payload: bytes) -> str | None:
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return payload.decode(encoding)
        except UnicodeDecodeError:
            continue
    return None


def _name_or_payload_looks_xml(name: str, text: str) -> bool:
    stripped = text.lstrip()
    return name.lower().endswith(".xml") or stripped.startswith("<?xml") or stripped.startswith("<")


def _validated_cvn_xml(candidate: ExtractedCvnXml) -> ExtractedCvnXml | None:
    try:
        root = ElementTree.fromstring(candidate.xml_text)
    except ElementTree.ParseError:
        return None
    if not _has_cvn_evidence(root, candidate.xml_text):
        return None
    return candidate


def _has_cvn_evidence(root: ElementTree.Element, text: str) -> bool:
    root_name = root.tag.lower()
    text_sample = text[:4096].lower()
    return any(
        marker in root_name or marker in text_sample
        for marker in (
            "cvn",
            "curriculumvitaenormalizado",
            "curriculum vitae normalizado",
        )
    )
