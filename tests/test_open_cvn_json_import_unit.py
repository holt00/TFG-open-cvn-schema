import json
from pathlib import Path

from open_cvn import (
    CvnErrorCode,
    CvnValidationStatus,
    parse_open_cvn_json,
    validate_open_cvn_json,
)


FIXTURES = Path("tests/fixtures/open_cvn")


def test_parse_open_cvn_json_accepts_path_input():
    result = parse_open_cvn_json(FIXTURES / "valid_minimal.json")

    assert result.validation_status == CvnValidationStatus.VALID
    assert result.trace is not None
    assert result.trace.source_path == str(FIXTURES / "valid_minimal.json")
    assert result.trace.schema_version == "0.1.0"
    assert result.trace.policy_name == "default_cvn_semantic_policy"
    assert result.trace.policy_version == "0.1.0"


def test_parse_open_cvn_json_accepts_inline_json_string():
    payload = (FIXTURES / "valid_minimal.json").read_text(encoding="utf-8")

    result = parse_open_cvn_json(payload, source_identifier="inline-json")

    assert result.validation_status == CvnValidationStatus.VALID
    assert result.source_identifier == "inline-json"


def test_parse_open_cvn_json_accepts_json_bytes():
    payload = (FIXTURES / "valid_minimal.json").read_bytes()

    result = parse_open_cvn_json(payload, source_identifier="bytes-json")

    assert result.validation_status == CvnValidationStatus.VALID
    assert result.source_identifier == "bytes-json"


def test_parse_open_cvn_json_accepts_mapping_input():
    payload = json.loads((FIXTURES / "valid_minimal.json").read_text(encoding="utf-8"))

    result = parse_open_cvn_json(payload, source_identifier="mapping-json")

    assert result.validation_status == CvnValidationStatus.VALID
    assert result.source_identifier == "mapping-json"


def test_parse_open_cvn_json_reports_malformed_json():
    result = parse_open_cvn_json(FIXTURES / "malformed.json")

    assert result.validation_status == CvnValidationStatus.FAILED
    assert result.errors[0].code == CvnErrorCode.INVALID_JSON
    assert result.errors[0].source_location == "line 2 column 1"


def test_parse_open_cvn_json_reports_runtime_validation_failure_for_non_object():
    result = parse_open_cvn_json("[]", source_identifier="json-list")

    assert result.validation_status == CvnValidationStatus.INVALID
    assert result.errors[0].code == CvnErrorCode.PYDANTIC_VALIDATION_FAILURE
    assert result.errors[0].details["input_type"] == "list"


def test_validate_open_cvn_json_reports_schema_failures():
    payload = json.loads((FIXTURES / "wrong_shape.json").read_text(encoding="utf-8"))

    result = validate_open_cvn_json(payload, source_identifier="wrong-shape")

    codes = {error.code for error in result.errors}

    assert result.validation_status == CvnValidationStatus.INVALID
    assert CvnErrorCode.JSON_SCHEMA_VALIDATION_FAILURE in codes
    assert result.trace is not None
    assert result.trace.schema_version == "0.1.0"


def test_validate_open_cvn_json_reports_schema_version_failures():
    payload = json.loads((FIXTURES / "unsupported_major.json").read_text(encoding="utf-8"))

    result = validate_open_cvn_json(payload, source_identifier="unsupported-major")

    assert result.validation_status == CvnValidationStatus.INVALID
    assert result.errors[0].code == CvnErrorCode.JSON_SCHEMA_VALIDATION_FAILURE
    assert ("schema_version",) in {error.path for error in result.errors}


def test_validate_open_cvn_json_returns_normalized_data():
    payload = json.loads((FIXTURES / "valid_minimal.json").read_text(encoding="utf-8"))

    result = validate_open_cvn_json(payload, source_identifier="valid")

    dumped = result.model_dump(mode="json")

    assert result.validation_status == CvnValidationStatus.VALID
    assert dumped["data"]["schema_version"] == "0.1.0"
    assert dumped["errors"] == []
