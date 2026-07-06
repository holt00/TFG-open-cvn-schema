from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from pydantic import ValidationError

from open_cvn.parser_contract import (
    CvnErrorCode,
    CvnIssueSeverity,
    CvnParseIssue,
    CvnParseTrace,
    CvnSourceFormat,
)


JsonScalar = str | int | float | bool | None


@dataclass(frozen=True)
class LoadedText:
    text: str
    source_path: str | None
    source_identifier: str | None


def load_text_input(
    source: Path | str | bytes,
    *,
    source_identifier: str | None,
    missing_path_is_text: bool,
) -> LoadedText:
    if isinstance(source, Path):
        return _load_path(source, source_identifier=source_identifier)
    if isinstance(source, bytes):
        return LoadedText(
            text=source.decode("utf-8"),
            source_path=None,
            source_identifier=source_identifier,
        )
    if isinstance(source, str):
        path = Path(source)
        if path.exists():
            return _load_path(path, source_identifier=source_identifier)
        if not missing_path_is_text and _looks_like_path(source):
            raise OSError(f"Input path does not exist: {source}")
        return LoadedText(text=source, source_path=None, source_identifier=source_identifier)
    raise TypeError(f"Unsupported input type: {type(source).__name__}")


def make_trace(
    *,
    source_format: CvnSourceFormat,
    source_identifier: str | None,
    source_path: str | None = None,
    extracted_from: str | None = None,
    cvn_codes: tuple[str, ...] = (),
    xml_paths: tuple[str, ...] = (),
    schema_version: str | None = None,
    policy_name: str | None = None,
    policy_version: str | None = None,
) -> CvnParseTrace:
    return CvnParseTrace(
        source_format=source_format,
        source_identifier=source_identifier,
        source_path=source_path,
        extracted_from=extracted_from,
        cvn_codes=cvn_codes,
        xml_paths=xml_paths,
        schema_version=schema_version,
        policy_name=policy_name,
        policy_version=policy_version,
    )


def make_error(
    *,
    code: CvnErrorCode,
    message: str,
    source_location: str | None = None,
    path: tuple[str, ...] = (),
    details: Mapping[str, Any] | None = None,
) -> CvnParseIssue:
    return CvnParseIssue(
        code=code,
        severity=CvnIssueSeverity.ERROR,
        message=message,
        source_location=source_location,
        path=path,
        details=serializable_details(details or {}),
    )


def make_warning(
    *,
    code: CvnErrorCode,
    message: str,
    source_location: str | None = None,
    path: tuple[str, ...] = (),
    details: Mapping[str, Any] | None = None,
) -> CvnParseIssue:
    return CvnParseIssue(
        code=code,
        severity=CvnIssueSeverity.WARNING,
        message=message,
        source_location=source_location,
        path=path,
        details=serializable_details(details or {}),
    )


def pydantic_errors_to_issues(error: ValidationError) -> tuple[CvnParseIssue, ...]:
    issues: list[CvnParseIssue] = []
    for item in error.errors():
        issues.append(
            make_error(
                code=CvnErrorCode.PYDANTIC_VALIDATION_FAILURE,
                message=str(item.get("msg", "Pydantic validation failed.")),
                path=tuple(str(part) for part in item.get("loc", ())),
                details={"type": item.get("type")},
            )
        )
    return tuple(issues)


def extract_json_trace_values(document: Mapping[str, Any]) -> tuple[str | None, str | None, str | None]:
    schema_version = _string_or_none(document.get("schema_version"))
    metadata = document.get("metadata")
    if not isinstance(metadata, Mapping):
        return schema_version, None, None
    policy = metadata.get("policy")
    if not isinstance(policy, Mapping):
        return schema_version, None, None
    return (
        schema_version,
        _string_or_none(policy.get("name")),
        _string_or_none(policy.get("version")),
    )


def serializable_details(details: Mapping[str, Any]) -> dict[str, JsonScalar]:
    result: dict[str, JsonScalar] = {}
    for key, value in details.items():
        if value is None or isinstance(value, str | int | float | bool):
            result[str(key)] = value
        else:
            result[str(key)] = json.dumps(value, sort_keys=True, default=str)
    return result


def _load_path(path: Path, *, source_identifier: str | None) -> LoadedText:
    text = path.read_text(encoding="utf-8")
    source_path = str(path)
    return LoadedText(
        text=text,
        source_path=source_path,
        source_identifier=source_identifier or source_path,
    )


def _looks_like_path(source: str) -> bool:
    return source.endswith((".json", ".xml")) or "/" in source or "\\" in source


def _string_or_none(value: Any) -> str | None:
    if isinstance(value, str):
        return value
    return None
