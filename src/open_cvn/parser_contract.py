from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any, Mapping, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, model_validator


CvnInput: TypeAlias = Path | str | bytes | Mapping[str, Any]
DEFERRED_IMPLEMENTATION_MESSAGE = "Parser implementation is deferred to issue #48/#49."


class CvnSourceFormat(str, Enum):
    PDF = "pdf"
    CVN_XML = "cvn_xml"
    OPEN_CVN_JSON = "open_cvn_json"


class CvnValidationStatus(str, Enum):
    NOT_RUN = "not_run"
    VALID = "valid"
    VALID_WITH_WARNINGS = "valid_with_warnings"
    INVALID = "invalid"
    FAILED = "failed"


class CvnIssueSeverity(str, Enum):
    WARNING = "warning"
    ERROR = "error"


class CvnErrorCode(str, Enum):
    UNSUPPORTED_INPUT_FORMAT = "unsupported_input_format"
    UNREADABLE_FILE = "unreadable_file"
    PDF_WITHOUT_EXTRACTABLE_XML = "pdf_without_extractable_xml"
    INVALID_XML = "invalid_xml"
    XML_SEMANTICALLY_UNMAPPABLE = "xml_semantically_unmappable"
    INVALID_JSON = "invalid_json"
    JSON_SCHEMA_VALIDATION_FAILURE = "json_schema_validation_failure"
    PYDANTIC_VALIDATION_FAILURE = "pydantic_validation_failure"


class CvnParseIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: CvnErrorCode
    severity: CvnIssueSeverity
    message: str
    source_location: str | None = None
    path: tuple[str, ...] = ()
    details: dict[str, str | int | float | bool | None] = Field(default_factory=dict)


class CvnParseTrace(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_format: CvnSourceFormat
    source_identifier: str | None = None
    source_path: str | None = None
    extracted_from: str | None = None
    cvn_codes: tuple[str, ...] = ()
    xml_paths: tuple[str, ...] = ()
    schema_version: str | None = None
    policy_name: str | None = None
    policy_version: str | None = None


class CvnParseResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_format: CvnSourceFormat
    source_identifier: str | None = None
    data: Mapping[str, Any] | None = None
    validation_status: CvnValidationStatus
    warnings: tuple[CvnParseIssue, ...] = ()
    errors: tuple[CvnParseIssue, ...] = ()
    trace: CvnParseTrace | None = None

    @model_validator(mode="after")
    def _validate_status_matches_issues(self) -> CvnParseResult:
        if self.errors and self.validation_status not in {
            CvnValidationStatus.INVALID,
            CvnValidationStatus.FAILED,
        }:
            raise ValueError("Results with errors must be invalid or failed")
        if self.validation_status == CvnValidationStatus.VALID_WITH_WARNINGS and not self.warnings:
            raise ValueError("valid_with_warnings results must include at least one warning")
        for issue in self.warnings:
            if issue.severity != CvnIssueSeverity.WARNING:
                raise ValueError("warnings must contain warning-severity issues")
        for issue in self.errors:
            if issue.severity != CvnIssueSeverity.ERROR:
                raise ValueError("errors must contain error-severity issues")
        return self


def parse_cvn_pdf(source: CvnInput, *, source_identifier: str | None = None) -> CvnParseResult:
    raise NotImplementedError(DEFERRED_IMPLEMENTATION_MESSAGE)


def parse_cvn_xml(source: CvnInput, *, source_identifier: str | None = None) -> CvnParseResult:
    raise NotImplementedError(DEFERRED_IMPLEMENTATION_MESSAGE)


def parse_open_cvn_json(source: CvnInput, *, source_identifier: str | None = None) -> CvnParseResult:
    raise NotImplementedError(DEFERRED_IMPLEMENTATION_MESSAGE)


def validate_open_cvn_json(
    document: Mapping[str, Any], *, source_identifier: str | None = None
) -> CvnParseResult:
    raise NotImplementedError(DEFERRED_IMPLEMENTATION_MESSAGE)
