from unittest.mock import MagicMock, patch
import pytest
from tfm_lakehouse.orcid_client import OrcidApiError, OrcidClient, OrcidNotFoundError, OrcidValidationError
from tfm_lakehouse.orcid_client.client import validate_orcid_id

VALID_ORCID_ID = "0000-0002-1825-0097"


def test_validate_orcid_id_accepts_known_valid_id():
    validate_orcid_id(VALID_ORCID_ID)


@pytest.mark.parametrize(
    "orcid_id",
    [
        "0000-0002-1825-0098",
        "not-an-orcid-id",
        "0000-0002-1825-009",
    ],
)
def test_validate_orcid_id_rejects_malformed_or_bad_checksum(orcid_id):
    with pytest.raises(OrcidValidationError):
        validate_orcid_id(orcid_id)


def _mock_response(status_code: int, json_body: dict | None = None, headers: dict | None = None):
    response = MagicMock()
    response.status_code = status_code
    response.ok = 200 <= status_code < 300
    response.json.return_value = json_body or {}
    response.text = str(json_body or {})
    response.headers = headers or {}
    return response


def test_get_record_returns_parsed_json_on_success():
    client = OrcidClient()
    with patch.object(client._session, "get", return_value=_mock_response(200, {"orcid-identifier": {}})):
        result = client.get_record(VALID_ORCID_ID)
    assert result == {"orcid-identifier": {}}


def test_get_record_raises_not_found_on_404():
    client = OrcidClient()
    with patch.object(client._session, "get", return_value=_mock_response(404)):
        with pytest.raises(OrcidNotFoundError):
            client.get_record(VALID_ORCID_ID)


def test_get_record_raises_api_error_on_unexpected_status():
    client = OrcidClient()
    with patch.object(client._session, "get", return_value=_mock_response(500)):
        with pytest.raises(OrcidApiError):
            client.get_record(VALID_ORCID_ID)


def test_get_record_retries_on_429_then_succeeds():
    client = OrcidClient(backoff_seconds=0.0)
    responses = [
        _mock_response(429, headers={"Retry-After": "0"}),
        _mock_response(200, {"orcid-identifier": {}}),
    ]
    with patch.object(client._session, "get", side_effect=responses):
        result = client.get_record(VALID_ORCID_ID)
    assert result == {"orcid-identifier": {}}


def test_get_record_gives_up_after_max_retries():
    client = OrcidClient(max_retries=1, backoff_seconds=0.0)
    responses = [
        _mock_response(429, headers={"Retry-After": "0"}),
        _mock_response(429, headers={"Retry-After": "0"}),
    ]
    with patch.object(client._session, "get", side_effect=responses):
        with pytest.raises(OrcidApiError):
            client.get_record(VALID_ORCID_ID)


@pytest.mark.parametrize(
    ("method_name", "endpoint"),
    [
        ("get_works", "works"),
        ("get_employments", "employments"),
        ("get_educations", "educations"),
    ],
)
def test_endpoint_methods_hit_the_expected_path(method_name, endpoint):
    client = OrcidClient()
    with patch.object(client._session, "get", return_value=_mock_response(200, {})) as mock_get:
        getattr(client, method_name)(VALID_ORCID_ID)
    called_url = mock_get.call_args.args[0]
    assert called_url.endswith(f"/{VALID_ORCID_ID}/{endpoint}")
