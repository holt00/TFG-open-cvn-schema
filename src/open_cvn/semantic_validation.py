from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from open_cvn.import_utils import make_warning
from open_cvn.parser_contract import CvnErrorCode, CvnParseIssue


REPEATED_SECTIONS = (
    "education",
    "research",
    "professional_experience",
    "achievements",
    "other",
)
CVN_CODE_PATTERN = re.compile(r"^\d{3}(?:\.\d{3}){3}$")
CONTROLLED_REFERENCE_MARKERS = {"source", "reference_status", "semantic_reference_kind"}
CONTROLLED_REFERENCE_VALUE_KEYS = {"code", "label", "raw_value", "uri"}


def validate_open_cvn_semantics(document: Mapping[str, Any]) -> tuple[CvnParseIssue, ...]:
    """Return conservative Open CVN semantic warnings for schema-valid documents."""

    warnings: list[CvnParseIssue] = []
    curriculum = document.get("curriculum")
    if not isinstance(curriculum, Mapping):
        return ()
    for section in REPEATED_SECTIONS:
        entries = curriculum.get(section)
        if not isinstance(entries, list):
            continue
        for index, entry in enumerate(entries):
            if not isinstance(entry, Mapping):
                continue
            path = ("curriculum", section, str(index))
            warnings.extend(_entry_type_warnings(entry, section=section, path=path))
            warnings.extend(_trace_code_warnings(entry, path=path))
            data = entry.get("data")
            if isinstance(data, Mapping):
                warnings.extend(_controlled_reference_warnings(data, path=(*path, "data")))
    return tuple(warnings)


def _entry_type_warnings(
    entry: Mapping[str, Any], *, section: str, path: tuple[str, ...]
) -> tuple[CvnParseIssue, ...]:
    entry_type = entry.get("type")
    if not isinstance(entry_type, str):
        return ()
    expected_prefix = f"{section}."
    if entry_type.startswith(expected_prefix):
        return ()
    return (
        make_warning(
            code=CvnErrorCode.SEMANTIC_VALIDATION_WARNING,
            message="Open CVN entry type does not match its curriculum section prefix.",
            path=(*path, "type"),
            details={"section": section, "entry_type": entry_type, "expected_prefix": expected_prefix},
        ),
    )


def _trace_code_warnings(entry: Mapping[str, Any], *, path: tuple[str, ...]) -> tuple[CvnParseIssue, ...]:
    trace = entry.get("trace")
    if not isinstance(trace, Mapping):
        return ()
    codes = trace.get("cvn_codes")
    if not isinstance(codes, list):
        return ()
    warnings: list[CvnParseIssue] = []
    for index, code in enumerate(codes):
        if isinstance(code, str) and CVN_CODE_PATTERN.match(code):
            continue
        warnings.append(
            make_warning(
                code=CvnErrorCode.SEMANTIC_VALIDATION_WARNING,
                message="Open CVN trace contains a value that does not look like a CVN code.",
                path=(*path, "trace", "cvn_codes", str(index)),
                details={"cvn_code": str(code)},
            )
        )
    return tuple(warnings)


def _controlled_reference_warnings(
    value: Any, *, path: tuple[str, ...]
) -> tuple[CvnParseIssue, ...]:
    warnings: list[CvnParseIssue] = []
    if isinstance(value, Mapping):
        keys = set(str(key) for key in value.keys())
        if keys & CONTROLLED_REFERENCE_MARKERS and not _has_reference_value(value):
            warnings.append(
                make_warning(
                    code=CvnErrorCode.SEMANTIC_VALIDATION_WARNING,
                    message="Controlled reference has provenance but no code, label, raw_value, or uri.",
                    path=path,
                    details={"keys": sorted(keys)},
                )
            )
        for key, child in value.items():
            warnings.extend(_controlled_reference_warnings(child, path=(*path, str(key))))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            warnings.extend(_controlled_reference_warnings(child, path=(*path, str(index))))
    return tuple(warnings)


def _has_reference_value(value: Mapping[str, Any]) -> bool:
    for key in CONTROLLED_REFERENCE_VALUE_KEYS:
        item = value.get(key)
        if item not in (None, ""):
            return True
    return False
