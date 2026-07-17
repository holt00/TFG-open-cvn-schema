from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any, Mapping, Protocol, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, model_validator


CvnInput: TypeAlias = Path | str | bytes | Mapping[str, Any]
DEFERRED_IMPLEMENTATION_MESSAGE = "Parser implementation is deferred to issue #48/#49."


class LlmPdfImportProvider(Protocol):
    def extract_open_cvn_json(self, request: Any) -> Any:
        """Protocol mirror for optional LLM providers without import-time coupling."""


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
    LLM_IMPORT_DISABLED = "llm_import_disabled"
    LLM_PROVIDER_ERROR = "llm_provider_error"
    LLM_INVALID_RESPONSE = "llm_invalid_response"
    LLM_OUTPUT_VALIDATION_FAILURE = "llm_output_validation_failure"
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


def parse_cvn_pdf(
    source: CvnInput,
    *,
    source_identifier: str | None = None,
    validate_extracted_xml: bool = False,
    allow_llm: bool = False,
    llm_config: Any | None = None,
    llm_provider: LlmPdfImportProvider | None = None,
) -> CvnParseResult:
    from open_cvn.pdf_xml_extraction import (
        UnsupportedPdfInputError,
        UnreadablePdfError,
        extract_cvn_xml_from_pdf,
    )

    if isinstance(source, Mapping):
        return _failed_pdf_result(
            source_identifier=source_identifier,
            source_path=None,
            error_code=CvnErrorCode.UNSUPPORTED_INPUT_FORMAT,
            message="PDF input must be a path or bytes.",
            details={"input_type": type(source).__name__},
        )

    try:
        extraction_result = extract_cvn_xml_from_pdf(source)  # type: ignore[arg-type]
    except UnsupportedPdfInputError as exc:
        return _failed_pdf_result(
            source_identifier=source_identifier,
            source_path=None,
            error_code=CvnErrorCode.UNSUPPORTED_INPUT_FORMAT,
            message="PDF input must be a path or bytes.",
            details={"error": str(exc)},
        )
    except UnreadablePdfError as exc:
        return _failed_pdf_result(
            source_identifier=source_identifier,
            source_path=exc.source_path,
            error_code=CvnErrorCode.UNREADABLE_FILE,
            message="PDF input could not be read.",
            details={"error": str(exc)},
        )

    diagnostics = extraction_result.diagnostics
    extracted_xml = extraction_result.extracted_xml
    result_identifier = source_identifier or diagnostics.source_path
    if extracted_xml is None:
        if allow_llm:
            return _parse_pdf_with_llm_fallback(
                source,
                source_identifier=result_identifier,
                source_path=diagnostics.source_path,
                llm_config=llm_config,
                llm_provider=llm_provider,
                fallback_reason=CvnErrorCode.PDF_WITHOUT_EXTRACTABLE_XML.value,
            )
        return _failed_pdf_result(
            source_identifier=result_identifier,
            source_path=diagnostics.source_path,
            error_code=CvnErrorCode.PDF_WITHOUT_EXTRACTABLE_XML,
            message="PDF does not contain extractable CVN XML.",
            details=diagnostics.as_details(),
        )

    extracted_from = extracted_xml.source_kind
    if extracted_xml.source_name is not None:
        extracted_from = f"{extracted_from}:{extracted_xml.source_name}"

    if validate_extracted_xml:
        xml_result = parse_cvn_xml(
            extracted_xml.xml_text,
            source_identifier=f"{result_identifier}:{extracted_from}" if result_identifier else extracted_from,
        )
        if xml_result.validation_status not in {CvnValidationStatus.INVALID, CvnValidationStatus.FAILED}:
            schema_version = xml_result.trace.schema_version if xml_result.trace else None
            policy_name = xml_result.trace.policy_name if xml_result.trace else None
            policy_version = xml_result.trace.policy_version if xml_result.trace else None
            return CvnParseResult(
                source_format=CvnSourceFormat.PDF,
                source_identifier=result_identifier,
                data=xml_result.data,
                validation_status=xml_result.validation_status,
                warnings=xml_result.warnings,
                trace=CvnParseTrace(
                    source_format=CvnSourceFormat.PDF,
                    source_identifier=result_identifier,
                    source_path=diagnostics.source_path,
                    extracted_from=extracted_from,
                    cvn_codes=xml_result.trace.cvn_codes if xml_result.trace else (),
                    xml_paths=xml_result.trace.xml_paths if xml_result.trace else (),
                    schema_version=schema_version,
                    policy_name=policy_name,
                    policy_version=policy_version,
                ),
            )
        if allow_llm:
            return _parse_pdf_with_llm_fallback(
                source,
                source_identifier=result_identifier,
                source_path=diagnostics.source_path,
                llm_config=llm_config,
                llm_provider=llm_provider,
                fallback_reason=xml_result.errors[0].code.value if xml_result.errors else "xml_validation_failed",
            )

    return CvnParseResult(
        source_format=CvnSourceFormat.PDF,
        source_identifier=result_identifier,
        data={
            "xml_text": extracted_xml.xml_text,
            "extraction": {
                "source_kind": extracted_xml.source_kind,
                "source_name": extracted_xml.source_name,
                "source_index": extracted_xml.source_index,
                "xml_bytes_size": extracted_xml.xml_bytes_size,
                "metadata_xref": extracted_xml.metadata_xref,
                **diagnostics.as_details(),
            },
        },
        validation_status=CvnValidationStatus.NOT_RUN,
        trace=CvnParseTrace(
            source_format=CvnSourceFormat.PDF,
            source_identifier=result_identifier,
            source_path=diagnostics.source_path,
            extracted_from=extracted_from,
        ),
    )


def _parse_pdf_with_llm_fallback(
    source: CvnInput,
    *,
    source_identifier: str | None,
    source_path: str | None,
    llm_config: Any | None,
    llm_provider: LlmPdfImportProvider | None,
    fallback_reason: str,
) -> CvnParseResult:
    if isinstance(source, Mapping):
        return _failed_pdf_result(
            source_identifier=source_identifier,
            source_path=source_path,
            error_code=CvnErrorCode.UNSUPPORTED_INPUT_FORMAT,
            message="PDF input must be a path or bytes.",
            details={"input_type": type(source).__name__},
        )
    if llm_config is None:
        return _failed_pdf_result(
            source_identifier=source_identifier,
            source_path=source_path,
            error_code=CvnErrorCode.LLM_IMPORT_DISABLED,
            message="LLM PDF import is not configured.",
            details={"fallback_reason": fallback_reason},
        )
    provider = llm_provider or _default_llm_provider(llm_config)
    if provider is None:
        return _failed_pdf_result(
            source_identifier=source_identifier,
            source_path=source_path,
            error_code=CvnErrorCode.LLM_IMPORT_DISABLED,
            message="No supported LLM provider is configured for PDF import.",
            details={"provider": str(getattr(llm_config, "provider", None))},
        )

    from open_cvn.llm_import import import_pdf_with_llm

    return import_pdf_with_llm(
        source,  # type: ignore[arg-type]
        source_identifier=source_identifier,
        config=llm_config,
        provider=provider,
        fallback_reason=fallback_reason,
    )


def _default_llm_provider(llm_config: Any) -> LlmPdfImportProvider | None:
    if getattr(llm_config, "provider", None) != "openai":
        return None
    from open_cvn.llm_providers import OpenAiResponsesProvider

    return OpenAiResponsesProvider()


def _failed_pdf_result(
    *,
    source_identifier: str | None,
    source_path: str | None,
    error_code: CvnErrorCode,
    message: str,
    details: dict[str, str | int | float | bool | None],
) -> CvnParseResult:
    return CvnParseResult(
        source_format=CvnSourceFormat.PDF,
        source_identifier=source_identifier or source_path,
        validation_status=CvnValidationStatus.FAILED,
        errors=(
            CvnParseIssue(
                code=error_code,
                severity=CvnIssueSeverity.ERROR,
                message=message,
                details=details,
            ),
        ),
        trace=CvnParseTrace(
            source_format=CvnSourceFormat.PDF,
            source_identifier=source_identifier or source_path,
            source_path=source_path,
        ),
    )


def parse_cvn_xml(source: CvnInput, *, source_identifier: str | None = None) -> CvnParseResult:
    from open_cvn.xml_import import parse_cvn_xml as _parse_cvn_xml

    return _parse_cvn_xml(source, source_identifier=source_identifier)


def parse_open_cvn_json(source: CvnInput, *, source_identifier: str | None = None) -> CvnParseResult:
    from open_cvn.json_import import parse_open_cvn_json as _parse_open_cvn_json

    return _parse_open_cvn_json(source, source_identifier=source_identifier)


def validate_open_cvn_json(
    document: Mapping[str, Any], *, source_identifier: str | None = None
) -> CvnParseResult:
    from open_cvn.json_import import validate_open_cvn_json as _validate_open_cvn_json

    return _validate_open_cvn_json(document, source_identifier=source_identifier)
