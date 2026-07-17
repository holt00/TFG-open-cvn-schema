from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Protocol

from open_cvn.import_utils import extract_json_trace_values, make_error, make_trace
from open_cvn.parser_contract import (
    CvnErrorCode,
    CvnParseIssue,
    CvnParseResult,
    CvnSourceFormat,
    CvnValidationStatus,
    validate_open_cvn_json,
)


@dataclass(frozen=True)
class LlmImportConfig:
    provider: str
    model: str
    base_url: str | None = None
    api_key_env: str = "OPENAI_API_KEY"
    timeout_seconds: float = 60.0
    pdf_detail: str = "low"


@dataclass(frozen=True)
class LlmImportPrompts:
    system_prompt: str
    user_instruction: str


@dataclass(frozen=True)
class LlmImportRequest:
    pdf_bytes: bytes
    filename: str
    schema: Mapping[str, Any]
    prompts: LlmImportPrompts
    config: LlmImportConfig


@dataclass(frozen=True)
class LlmProviderResponse:
    document: Mapping[str, Any] | str
    provider_metadata: Mapping[str, str | int | float | bool | None] | None = None


class LlmImportProvider(Protocol):
    def extract_open_cvn_json(self, request: LlmImportRequest) -> LlmProviderResponse:
        """Return an Open CVN JSON candidate extracted from the PDF."""


class LlmImportProviderError(RuntimeError):
    pass


def import_pdf_with_llm(
    pdf_source: Path | str | bytes,
    *,
    source_identifier: str | None,
    config: LlmImportConfig,
    provider: LlmImportProvider,
    fallback_reason: str,
) -> CvnParseResult:
    try:
        pdf_bytes, filename, source_path = _load_pdf_bytes(pdf_source, source_identifier=source_identifier)
    except OSError as exc:
        return _failed_result(
            source_identifier=source_identifier,
            source_path=str(pdf_source) if isinstance(pdf_source, Path | str) else None,
            code=CvnErrorCode.UNREADABLE_FILE,
            message="PDF input could not be read for LLM import.",
            details={"error": str(exc)},
        )
    except TypeError as exc:
        return _failed_result(
            source_identifier=source_identifier,
            source_path=None,
            code=CvnErrorCode.UNSUPPORTED_INPUT_FORMAT,
            message="PDF input must be a path or bytes.",
            details={"error": str(exc)},
        )

    schema = load_open_cvn_schema()
    request = LlmImportRequest(
        pdf_bytes=pdf_bytes,
        filename=filename,
        schema=schema,
        prompts=build_llm_import_prompts(),
        config=config,
    )
    try:
        provider_response = provider.extract_open_cvn_json(request)
    except LlmImportProviderError as exc:
        return _failed_result(
            source_identifier=source_identifier or source_path,
            source_path=source_path,
            code=CvnErrorCode.LLM_PROVIDER_ERROR,
            message="LLM provider failed during PDF import.",
            details={"error": str(exc), "provider": config.provider, "model": config.model},
        )

    candidate = _coerce_provider_document(provider_response.document)
    if candidate is None:
        return _failed_result(
            source_identifier=source_identifier or source_path,
            source_path=source_path,
            code=CvnErrorCode.LLM_INVALID_RESPONSE,
            message="LLM response did not contain a JSON object.",
            details={"provider": config.provider, "model": config.model},
        )

    document = _attach_llm_provenance(
        candidate,
        config=config,
        fallback_reason=fallback_reason,
        provider_metadata=provider_response.provider_metadata or {},
    )
    validation_result = validate_open_cvn_json(document, source_identifier=source_identifier or source_path)
    if validation_result.validation_status in {CvnValidationStatus.INVALID, CvnValidationStatus.FAILED}:
        return CvnParseResult(
            source_format=CvnSourceFormat.PDF,
            source_identifier=source_identifier or source_path,
            validation_status=CvnValidationStatus.INVALID,
            errors=(
                make_error(
                    code=CvnErrorCode.LLM_OUTPUT_VALIDATION_FAILURE,
                    message="LLM-produced Open CVN JSON failed local validation.",
                    details={"provider": config.provider, "model": config.model},
                ),
                *validation_result.errors,
            ),
            trace=make_trace(
                source_format=CvnSourceFormat.PDF,
                source_identifier=source_identifier or source_path,
                source_path=source_path,
                extracted_from="llm_fallback",
                schema_version=validation_result.trace.schema_version if validation_result.trace else None,
                policy_name=validation_result.trace.policy_name if validation_result.trace else None,
                policy_version=validation_result.trace.policy_version if validation_result.trace else None,
            ),
        )

    schema_version, policy_name, policy_version = extract_json_trace_values(validation_result.data or document)
    return CvnParseResult(
        source_format=CvnSourceFormat.PDF,
        source_identifier=source_identifier or source_path,
        data=validation_result.data,
        validation_status=validation_result.validation_status,
        warnings=validation_result.warnings,
        trace=make_trace(
            source_format=CvnSourceFormat.PDF,
            source_identifier=source_identifier or source_path,
            source_path=source_path,
            extracted_from="llm_fallback",
            schema_version=schema_version,
            policy_name=policy_name,
            policy_version=policy_version,
        ),
    )


def load_open_cvn_schema() -> Mapping[str, Any]:
    return json.loads(_schema_path().read_text(encoding="utf-8"))


def build_llm_import_prompts() -> LlmImportPrompts:
    return LlmImportPrompts(
        system_prompt=(
            "You extract academic CV data from PDF files into Open CVN JSON. "
            "Return only JSON matching the provided schema. Do not invent data. "
            "If a value is not visible in the PDF, omit it or use an empty array/object "
            "where the schema requires that container."
        ),
        user_instruction=(
            "Read the attached PDF and produce one Open CVN JSON document. "
            "Use schema_version 0.1.0 and policy default_cvn_semantic_policy version 0.1.0. "
            "Keep provenance in extensions when useful. Return JSON only."
        ),
    )


def _load_pdf_bytes(
    source: Path | str | bytes, *, source_identifier: str | None
) -> tuple[bytes, str, str | None]:
    if isinstance(source, bytes):
        return source, source_identifier or "input.pdf", None
    if isinstance(source, Path):
        return source.read_bytes(), source.name, str(source)
    if isinstance(source, str):
        path = Path(source)
        if path.exists():
            return path.read_bytes(), path.name, str(path)
        raise OSError(f"PDF path does not exist: {source}")
    raise TypeError(f"Unsupported PDF input type: {type(source).__name__}")


def _coerce_provider_document(document: Mapping[str, Any] | str) -> Mapping[str, Any] | None:
    if isinstance(document, Mapping):
        return document
    try:
        parsed = json.loads(document)
    except json.JSONDecodeError:
        return None
    if isinstance(parsed, Mapping):
        return parsed
    return None


def _attach_llm_provenance(
    document: Mapping[str, Any],
    *,
    config: LlmImportConfig,
    fallback_reason: str,
    provider_metadata: Mapping[str, str | int | float | bool | None],
) -> dict[str, Any]:
    result = dict(document)
    extensions = dict(result.get("extensions") or {})
    extensions["x-open-cvn.llm_import"] = {
        "provider": config.provider,
        "model": config.model,
        "fallback_reason": fallback_reason,
        "provider_metadata": dict(provider_metadata),
        "validation": "local_open_cvn_json",
    }
    result["extensions"] = extensions
    return result


def _failed_result(
    *,
    source_identifier: str | None,
    source_path: str | None,
    code: CvnErrorCode,
    message: str,
    details: Mapping[str, Any],
) -> CvnParseResult:
    return CvnParseResult(
        source_format=CvnSourceFormat.PDF,
        source_identifier=source_identifier or source_path,
        validation_status=CvnValidationStatus.FAILED,
        errors=(
            make_error(
                code=code,
                message=message,
                details=details,
            ),
        ),
        trace=make_trace(
            source_format=CvnSourceFormat.PDF,
            source_identifier=source_identifier or source_path,
            source_path=source_path,
        ),
    )


def _schema_path() -> Path:
    return Path(__file__).resolve().parents[2] / "schemas" / "open_cvn.schema.json"
