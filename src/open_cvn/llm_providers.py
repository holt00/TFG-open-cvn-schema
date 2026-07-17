from __future__ import annotations

import base64
import json
import os
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from open_cvn.llm_import import (
    LlmImportProviderError,
    LlmImportRequest,
    LlmProviderResponse,
)


HttpPost = Callable[[str, Mapping[str, str], bytes, float], bytes]


@dataclass(frozen=True)
class OpenAiResponsesProvider:
    http_post: HttpPost | None = None

    def extract_open_cvn_json(self, request: LlmImportRequest) -> LlmProviderResponse:
        api_key = os.environ.get(request.config.api_key_env)
        if not api_key:
            raise LlmImportProviderError(
                f"Missing API key environment variable: {request.config.api_key_env}"
            )

        endpoint = (request.config.base_url or "https://api.openai.com/v1").rstrip("/")
        url = f"{endpoint}/responses"
        body = _responses_body(request)
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        post = self.http_post or _default_http_post
        try:
            raw_response = post(
                url,
                headers,
                json.dumps(body).encode("utf-8"),
                request.config.timeout_seconds,
            )
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            raise LlmImportProviderError(str(exc)) from exc

        try:
            payload = json.loads(raw_response.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise LlmImportProviderError("Provider returned a non-JSON response.") from exc

        text = _extract_output_text(payload)
        if text is None:
            raise LlmImportProviderError("Provider response did not contain output text.")
        return LlmProviderResponse(
            document=text,
            provider_metadata=_provider_metadata(payload),
        )


def _responses_body(request: LlmImportRequest) -> dict[str, Any]:
    encoded_pdf = base64.b64encode(request.pdf_bytes).decode("ascii")
    return {
        "model": request.config.model,
        "input": [
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": request.prompts.system_prompt,
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_file",
                        "filename": request.filename,
                        "file_data": f"data:application/pdf;base64,{encoded_pdf}",
                        "detail": request.config.pdf_detail,
                    },
                    {
                        "type": "input_text",
                        "text": request.prompts.user_instruction,
                    },
                ],
            },
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "open_cvn_document",
                "schema": request.schema,
                "strict": False,
            }
        },
    }


def _default_http_post(url: str, headers: Mapping[str, str], body: bytes, timeout: float) -> bytes:
    request = Request(url, data=body, headers=dict(headers), method="POST")
    with urlopen(request, timeout=timeout) as response:  # nosec: user-configured API endpoint
        return response.read()


def _extract_output_text(payload: Mapping[str, Any]) -> str | None:
    direct = payload.get("output_text")
    if isinstance(direct, str):
        return direct
    output = payload.get("output")
    if not isinstance(output, list):
        return None
    parts: list[str] = []
    for item in output:
        if not isinstance(item, Mapping):
            continue
        content = item.get("content")
        if not isinstance(content, list):
            continue
        for content_item in content:
            if not isinstance(content_item, Mapping):
                continue
            text = content_item.get("text")
            if isinstance(text, str):
                parts.append(text)
    return "".join(parts) if parts else None


def _provider_metadata(payload: Mapping[str, Any]) -> dict[str, str | int | float | bool | None]:
    usage = payload.get("usage")
    metadata: dict[str, str | int | float | bool | None] = {}
    if isinstance(payload.get("id"), str):
        metadata["response_id"] = payload["id"]
    if isinstance(usage, Mapping):
        for key in ("input_tokens", "output_tokens", "total_tokens"):
            value = usage.get(key)
            if isinstance(value, int | float):
                metadata[key] = value
    return metadata
