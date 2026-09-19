import re
import time

import requests

from tfm_lakehouse.orcid_client.exceptions import (
    OrcidApiError,
    OrcidNotFoundError,
    OrcidValidationError,
)

ORCID_ID_PATTERN = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$")
PUB_API_BASE_URL = "https://pub.orcid.org/v3.0"


def validate_orcid_id(orcid_id: str) -> None:
    """Validate an ORCID iD's format and ISO 7064 MOD 11-2 checksum.

    Raises OrcidValidationError if the iD is malformed, so callers can fail
    fast without making a network call.
    """
    if not ORCID_ID_PATTERN.match(orcid_id):
        raise OrcidValidationError(
            f"'{orcid_id}' is not a well-formed ORCID iD (expected NNNN-NNNN-NNNN-NNNC)"
        )

    digits = orcid_id.replace("-", "")
    total = 0
    for digit in digits[:-1]:
        total = (total + int(digit)) * 2
    remainder = total % 11
    check_value = (12 - remainder) % 11
    expected_check_char = "X" if check_value == 10 else str(check_value)

    if digits[-1] != expected_check_char:
        raise OrcidValidationError(f"'{orcid_id}' failed ORCID checksum validation")


class OrcidClient:
    """Client for the ORCID Public API's anonymous (unauthenticated) tier.

    No client_id/client_secret or OAuth token is required: pub.orcid.org
    serves public record data to any caller with an `Accept: application/json`
    header. See docs/roadmap/tfm/issues/issue-94-orcid-api-client.md for why
    this client deliberately does not use the registered/OAuth tier.
    """

    def __init__(
        self,
        base_url: str = PUB_API_BASE_URL,
        timeout_seconds: float = 10.0,
        max_retries: int = 3,
        backoff_seconds: float = 1.0,
    ) -> None:
        self._base_url = base_url
        self._timeout_seconds = timeout_seconds
        self._max_retries = max_retries
        self._backoff_seconds = backoff_seconds
        self._session = requests.Session()
        self._session.headers["Accept"] = "application/json"

    def get_record(self, orcid_id: str) -> dict:
        return self._get(orcid_id, "record")

    def get_works(self, orcid_id: str) -> dict:
        return self._get(orcid_id, "works")

    def get_employments(self, orcid_id: str) -> dict:
        return self._get(orcid_id, "employments")

    def get_educations(self, orcid_id: str) -> dict:
        return self._get(orcid_id, "educations")

    def _get(self, orcid_id: str, endpoint: str) -> dict:
        validate_orcid_id(orcid_id)
        url = f"{self._base_url}/{orcid_id}/{endpoint}"

        attempt = 0
        while True:
            response = self._session.get(url, timeout=self._timeout_seconds)

            if response.status_code == 429 and attempt < self._max_retries:
                retry_after = float(
                    response.headers.get("Retry-After", self._backoff_seconds * (2**attempt))
                )
                time.sleep(retry_after)
                attempt += 1
                continue

            if response.status_code == 404:
                raise OrcidNotFoundError(
                    f"No ORCID record found for '{orcid_id}'",
                    status_code=404,
                    body=response.text,
                )

            if not response.ok:
                raise OrcidApiError(
                    f"ORCID API returned {response.status_code} for '{orcid_id}' {endpoint}",
                    status_code=response.status_code,
                    body=response.text,
                )

            return response.json()
