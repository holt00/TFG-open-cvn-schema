from __future__ import annotations

import json
from typing import Mapping

import pytest

from open_cvn.llm_import import (
    LlmImportConfig,
    LlmImportProviderError,
    LlmImportRequest,
    build_llm_import_prompts,
    load_open_cvn_schema,
)
from open_cvn.llm_providers import OpenAiResponsesProvider


def _request() -> LlmImportRequest:
    return LlmImportRequest(
        pdf_bytes=b"pdf bytes",
        filename="cv.pdf",
        schema=load_open_cvn_schema(),
        prompts=build_llm_import_prompts(),
        config=LlmImportConfig(
            provider="openai",
            model="gpt-test",
            base_url="https://api.test/v1",
            timeout_seconds=12.0,
            pdf_detail="low",
        ),
    )


def test_openai_provider_builds_responses_payload(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("OPENAI_API_KEY", "secret")
    calls: list[tuple[str, Mapping[str, str], bytes, float]] = []

    def post(url: str, headers: Mapping[str, str], body: bytes, timeout: float) -> bytes:
        calls.append((url, headers, body, timeout))
        return json.dumps(
            {
                "id": "resp_123",
                "output_text": json.dumps({"schema_version": "0.1.0"}),
                "usage": {"input_tokens": 10, "output_tokens": 5, "total_tokens": 15},
            }
        ).encode("utf-8")

    response = OpenAiResponsesProvider(http_post=post).extract_open_cvn_json(_request())

    url, headers, body, timeout = calls[0]
    payload = json.loads(body.decode("utf-8"))
    assert url == "https://api.test/v1/responses"
    assert headers["Authorization"] == "Bearer secret"
    assert timeout == 12.0
    assert payload["model"] == "gpt-test"
    assert payload["input"][1]["content"][0]["filename"] == "cv.pdf"
    assert payload["input"][1]["content"][0]["file_data"].startswith(
        "data:application/pdf;base64,"
    )
    assert payload["text"]["format"]["type"] == "json_schema"
    assert response.document == json.dumps({"schema_version": "0.1.0"})
    assert response.provider_metadata == {
        "response_id": "resp_123",
        "input_tokens": 10,
        "output_tokens": 5,
        "total_tokens": 15,
    }


def test_openai_provider_requires_api_key(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(LlmImportProviderError, match="Missing API key"):
        OpenAiResponsesProvider(http_post=lambda *_args: b"{}").extract_open_cvn_json(_request())


def test_openai_provider_reports_non_json_response(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("OPENAI_API_KEY", "secret")

    with pytest.raises(LlmImportProviderError, match="non-JSON"):
        OpenAiResponsesProvider(http_post=lambda *_args: b"not json").extract_open_cvn_json(
            _request()
        )


def test_openai_provider_reports_missing_output_text(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("OPENAI_API_KEY", "secret")

    with pytest.raises(LlmImportProviderError, match="output text"):
        OpenAiResponsesProvider(http_post=lambda *_args: b'{"id": "resp_123"}').extract_open_cvn_json(
            _request()
        )
