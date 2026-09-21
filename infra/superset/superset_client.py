"""Minimal Superset REST client for provisioning the TFM dashboard (issue #100).

Standard library only, so it runs on the host with no extra dependency. It logs in with the
admin user (JWT plus the CSRF token Superset 6 requires on writes) and offers JSON requests and
the multipart upload used to import a dashboard bundle.
"""

from __future__ import annotations

import http.cookiejar
import json
import logging
import urllib.error
import urllib.request
import uuid
from typing import Any

logger = logging.getLogger(__name__)


class SupersetApiError(RuntimeError):
    """An HTTP error answered by the Superset API."""


class SupersetClient:
    """Authenticated session against one Superset instance."""

    def __init__(self, base_url: str, username: str, password: str) -> None:
        """Log in and fetch the CSRF token.

        Args:
            base_url: Superset root URL, for example ``http://localhost:8088``.
            username: Superset user with the Admin role.
            password: Password of that user.

        Raises:
            SupersetApiError: If the login is refused.
        """
        self._base_url = base_url.rstrip("/")
        self._opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())
        )
        login = self._request(
            "POST",
            "/api/v1/security/login",
            {"username": username, "password": password, "provider": "db", "refresh": True},
            authenticated=False,
        )
        self._token: str = login["access_token"]
        self._csrf: str = self._request("GET", "/api/v1/security/csrf_token/")["result"]

    def _headers(self, authenticated: bool = True) -> dict[str, str]:
        headers = {"Accept": "application/json", "Referer": self._base_url}
        if authenticated:
            headers["Authorization"] = f"Bearer {self._token}"
            if getattr(self, "_csrf", None):
                headers["X-CSRFToken"] = self._csrf
        return headers

    def _send(self, request: urllib.request.Request) -> dict[str, Any]:
        try:
            with self._opener.open(request, timeout=120) as response:
                body = response.read().decode("utf-8")
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            raise SupersetApiError(
                f"{request.get_method()} {request.full_url} -> {error.code}: {detail[:600]}"
            ) from error
        return json.loads(body) if body else {}

    def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        authenticated: bool = True,
    ) -> dict[str, Any]:
        headers = self._headers(authenticated)
        data = None
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(
            self._base_url + path, data=data, headers=headers, method=method
        )
        return self._send(request)

    def get(self, path: str) -> dict[str, Any]:
        """GET a JSON resource."""
        return self._request("GET", path)

    def post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        """POST a JSON body and return the JSON answer."""
        return self._request("POST", path, payload)

    def put(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        """PUT a JSON body and return the JSON answer."""
        return self._request("PUT", path, payload)

    def upload(
        self,
        path: str,
        file_field: str,
        filename: str,
        content: bytes,
        fields: dict[str, str],
    ) -> dict[str, Any]:
        """POST a multipart form with one file, as the bundle import endpoints expect.

        Args:
            path: API path of the import endpoint.
            file_field: Name of the form field that carries the file.
            filename: File name reported to Superset.
            content: File bytes.
            fields: Extra text fields (``passwords``, ``overwrite``...).

        Returns:
            The JSON answer.
        """
        boundary = f"----tfm{uuid.uuid4().hex}"
        parts: list[bytes] = []
        for name, value in fields.items():
            parts.append(
                f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode()
            )
        parts.append(
            (
                f'--{boundary}\r\nContent-Disposition: form-data; name="{file_field}"; '
                f'filename="{filename}"\r\nContent-Type: application/zip\r\n\r\n'
            ).encode()
            + content
            + b"\r\n"
        )
        parts.append(f"--{boundary}--\r\n".encode())
        headers = self._headers()
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
        request = urllib.request.Request(
            self._base_url + path, data=b"".join(parts), headers=headers, method="POST"
        )
        return self._send(request)
