from __future__ import annotations

import re
from pathlib import Path
from typing import Mapping
from xml.etree import ElementTree

from open_cvn.import_utils import load_text_input, make_error, make_trace
from open_cvn.parser_contract import (
    CvnErrorCode,
    CvnInput,
    CvnParseIssue,
    CvnParseResult,
    CvnSourceFormat,
    CvnValidationStatus,
)
from open_cvn.xml_semantic_import import import_cvn_xml_semantically


CVN_CODE_RE = re.compile(r"\b\d{3}\.\d{3}\.\d{3}\.\d{3}\b")


def parse_cvn_xml(source: CvnInput, *, source_identifier: str | None = None) -> CvnParseResult:
    if isinstance(source, Mapping):
        return _xml_failed_result(
            source_identifier=source_identifier,
            source_path=None,
            error=make_error(
                code=CvnErrorCode.UNSUPPORTED_INPUT_FORMAT,
                message="CVN XML input must be a path, bytes, or XML string.",
                details={"input_type": type(source).__name__},
            ),
        )
    try:
        loaded = load_text_input(
            source,  # type: ignore[arg-type]
            source_identifier=source_identifier,
            missing_path_is_text=True,
        )
    except (OSError, UnicodeDecodeError) as exc:
        return _xml_failed_result(
            source_identifier=source_identifier,
            source_path=str(source) if isinstance(source, Path | str) else None,
            error=make_error(
                code=CvnErrorCode.UNREADABLE_FILE,
                message="CVN XML input could not be read.",
                details={"error": str(exc)},
            ),
        )
    except TypeError as exc:
        return _xml_failed_result(
            source_identifier=source_identifier,
            source_path=None,
            error=make_error(
                code=CvnErrorCode.UNSUPPORTED_INPUT_FORMAT,
                message="CVN XML input must be a path, bytes, or XML string.",
                details={"error": str(exc)},
            ),
        )

    try:
        root = ElementTree.fromstring(loaded.text)
    except ElementTree.ParseError as exc:
        return _xml_failed_result(
            source_identifier=loaded.source_identifier,
            source_path=loaded.source_path,
            error=make_error(
                code=CvnErrorCode.INVALID_XML,
                message="Input is not well-formed XML.",
                source_location=_xml_error_location(exc),
                details={"error": str(exc)},
            ),
        )

    xml_paths = _xml_paths(root)
    cvn_codes = _cvn_codes(root)
    trace = make_trace(
        source_format=CvnSourceFormat.CVN_XML,
        source_identifier=loaded.source_identifier,
        source_path=loaded.source_path,
        cvn_codes=cvn_codes,
        xml_paths=xml_paths,
    )
    if not _has_cvn_evidence(root, loaded.text, cvn_codes):
        return CvnParseResult(
            source_format=CvnSourceFormat.CVN_XML,
            source_identifier=loaded.source_identifier,
            validation_status=CvnValidationStatus.INVALID,
            errors=(
                make_error(
                    code=CvnErrorCode.XML_SEMANTICALLY_UNMAPPABLE,
                    message="XML is readable but does not contain enough CVN evidence for import.",
                    path=(xml_paths[0],) if xml_paths else (),
                ),
            ),
            trace=trace,
        )

    try:
        document = import_cvn_xml_semantically(
            source_identifier=loaded.source_identifier,
            source_path=loaded.source_path,
            root=root,
        )
    except ValueError as exc:
        return CvnParseResult(
            source_format=CvnSourceFormat.CVN_XML,
            source_identifier=loaded.source_identifier,
            validation_status=CvnValidationStatus.INVALID,
            errors=(
                make_error(
                    code=CvnErrorCode.XML_SEMANTICALLY_UNMAPPABLE,
                    message="CVN XML is readable but cannot be mapped to valid Open CVN JSON.",
                    path=(xml_paths[0],) if xml_paths else (),
                    details={"error": str(exc)},
                ),
            ),
            trace=trace,
        )
    return CvnParseResult(
        source_format=CvnSourceFormat.CVN_XML,
        source_identifier=loaded.source_identifier,
        data=document,
        validation_status=CvnValidationStatus.VALID,
        trace=trace,
    )


def _xml_paths(root: ElementTree.Element) -> tuple[str, ...]:
    paths: list[str] = []

    def visit(element: ElementTree.Element, path: str) -> None:
        paths.append(path)
        counts: dict[str, int] = {}
        for child in list(element):
            child_name = _local_name(child.tag)
            counts[child_name] = counts.get(child_name, 0) + 1
            visit(child, f"{path}/{child_name}[{counts[child_name]}]")

    visit(root, _local_name(root.tag))
    return tuple(paths[:200])


def _cvn_codes(root: ElementTree.Element) -> tuple[str, ...]:
    codes: list[str] = []
    seen: set[str] = set()
    for element in root.iter():
        values = [str(element.tag), *(str(value) for value in element.attrib.values())]
        if element.text:
            values.append(element.text)
        for value in values:
            for match in CVN_CODE_RE.findall(value):
                if match not in seen:
                    seen.add(match)
                    codes.append(match)
    return tuple(codes)


def _has_cvn_evidence(root: ElementTree.Element, text: str, cvn_codes: tuple[str, ...]) -> bool:
    root_name = _local_name(root.tag).lower()
    text_sample = text[:4096].lower()
    return bool(cvn_codes) or any(
        marker in root_name or marker in text_sample
        for marker in (
            "cvn",
            "curriculumvitaenormalizado",
            "curriculum vitae normalizado",
        )
    )


def _xml_error_location(error: ElementTree.ParseError) -> str | None:
    position = getattr(error, "position", None)
    if not position:
        return None
    line, column = position
    return f"line {line} column {column}"


def _xml_failed_result(
    *, source_identifier: str | None, source_path: str | None, error: CvnParseIssue
) -> CvnParseResult:
    return CvnParseResult(
        source_format=CvnSourceFormat.CVN_XML,
        source_identifier=source_identifier or source_path,
        validation_status=CvnValidationStatus.FAILED,
        errors=(error,),
        trace=make_trace(
            source_format=CvnSourceFormat.CVN_XML,
            source_identifier=source_identifier or source_path,
            source_path=source_path,
        ),
    )


def _local_name(tag: object) -> str:
    text = str(tag)
    if "}" in text:
        return text.rsplit("}", maxsplit=1)[1]
    return text
