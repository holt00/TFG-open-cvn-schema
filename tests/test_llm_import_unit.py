from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from open_cvn import CvnErrorCode, CvnValidationStatus
from open_cvn.llm_import import (
    LlmImportConfig,
    LlmImportProviderError,
    LlmImportRequest,
    LlmProviderResponse,
    build_llm_import_prompts,
    import_pdf_with_llm,
    load_open_cvn_schema,
)


FIXTURES_DIR = Path(__file__).parent / "fixtures" / "open_cvn"


class StaticProvider:
    def __init__(self, response: Mapping[str, Any] | str) -> None:
        self.response = response
        self.requests: list[LlmImportRequest] = []

    def extract_open_cvn_json(self, request: LlmImportRequest) -> LlmProviderResponse:
        self.requests.append(request)
        return LlmProviderResponse(
            document=self.response,
            provider_metadata={"mock": True, "tokens": 12},
        )


class FailingProvider:
    def extract_open_cvn_json(self, request: LlmImportRequest) -> LlmProviderResponse:
        raise LlmImportProviderError("timeout")


def _config() -> LlmImportConfig:
    return LlmImportConfig(provider="mock", model="mock-model")


def _valid_document() -> Mapping[str, Any]:
    return json.loads((FIXTURES_DIR / "valid_minimal.json").read_text(encoding="utf-8"))


def test_load_open_cvn_schema_returns_root_schema():
    schema = load_open_cvn_schema()

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["title"] == "Open CVN JSON Schema"


def test_build_llm_import_prompts_instructs_json_without_invention():
    prompts = build_llm_import_prompts()

    assert "Return only JSON" in prompts.system_prompt
    assert "Do not invent data" in prompts.system_prompt
    assert "schema_version 0.1.0" in prompts.user_instruction


def test_import_pdf_with_llm_validates_and_attaches_provenance(tmp_path: Path):
    pdf_path = tmp_path / "cv.pdf"
    pdf_path.write_bytes(b"%PDF synthetic bytes")
    provider = StaticProvider(_valid_document())

    result = import_pdf_with_llm(
        pdf_path,
        source_identifier="cv.pdf",
        config=_config(),
        provider=provider,
        fallback_reason="pdf_without_extractable_xml",
    )

    assert result.validation_status == CvnValidationStatus.VALID
    assert result.data is not None
    assert result.data["extensions"]["x-open-cvn.llm_import"] == {
        "provider": "mock",
        "model": "mock-model",
        "fallback_reason": "pdf_without_extractable_xml",
        "provider_metadata": {"mock": True, "tokens": 12},
        "validation": "local_open_cvn_json",
        "review_required": True,
        "authoritative": False,
    }
    assert result.trace is not None
    assert result.trace.extracted_from == "llm_fallback"
    assert provider.requests[0].filename == "cv.pdf"
    assert provider.requests[0].pdf_bytes == b"%PDF synthetic bytes"


def test_import_pdf_with_llm_accepts_json_string_response(tmp_path: Path):
    pdf_path = tmp_path / "cv.pdf"
    pdf_path.write_bytes(b"%PDF synthetic bytes")
    provider = StaticProvider(json.dumps(_valid_document()))

    result = import_pdf_with_llm(
        pdf_path,
        source_identifier="cv.pdf",
        config=_config(),
        provider=provider,
        fallback_reason="invalid_xml",
    )

    assert result.validation_status == CvnValidationStatus.VALID
    assert result.data is not None
    assert result.data["extensions"]["x-open-cvn.llm_import"]["fallback_reason"] == "invalid_xml"


def test_import_pdf_with_llm_reports_malformed_json_response(tmp_path: Path):
    pdf_path = tmp_path / "cv.pdf"
    pdf_path.write_bytes(b"%PDF synthetic bytes")
    provider = StaticProvider("not json")

    result = import_pdf_with_llm(
        pdf_path,
        source_identifier="cv.pdf",
        config=_config(),
        provider=provider,
        fallback_reason="pdf_without_extractable_xml",
    )

    assert result.validation_status == CvnValidationStatus.FAILED
    assert result.errors[0].code == CvnErrorCode.LLM_INVALID_RESPONSE


def test_import_pdf_with_llm_reports_schema_invalid_response(tmp_path: Path):
    pdf_path = tmp_path / "cv.pdf"
    pdf_path.write_bytes(b"%PDF synthetic bytes")
    provider = StaticProvider({"schema_version": "0.1.0"})

    result = import_pdf_with_llm(
        pdf_path,
        source_identifier="cv.pdf",
        config=_config(),
        provider=provider,
        fallback_reason="pdf_without_extractable_xml",
    )

    assert result.validation_status == CvnValidationStatus.INVALID
    assert result.errors[0].code == CvnErrorCode.LLM_OUTPUT_VALIDATION_FAILURE
    assert any(error.code == CvnErrorCode.JSON_SCHEMA_VALIDATION_FAILURE for error in result.errors)


def test_import_pdf_with_llm_reports_provider_failure(tmp_path: Path):
    pdf_path = tmp_path / "cv.pdf"
    pdf_path.write_bytes(b"%PDF synthetic bytes")

    result = import_pdf_with_llm(
        pdf_path,
        source_identifier="cv.pdf",
        config=_config(),
        provider=FailingProvider(),
        fallback_reason="pdf_without_extractable_xml",
    )

    assert result.validation_status == CvnValidationStatus.FAILED
    assert result.errors[0].code == CvnErrorCode.LLM_PROVIDER_ERROR
    assert result.errors[0].details["provider"] == "mock"
