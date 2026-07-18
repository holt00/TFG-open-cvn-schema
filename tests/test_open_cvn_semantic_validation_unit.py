import json
from pathlib import Path

from open_cvn import CvnErrorCode, CvnValidationStatus, validate_open_cvn_json
from open_cvn.semantic_validation import validate_open_cvn_semantics


FIXTURES = Path("tests/fixtures/open_cvn")


def _valid_document():
    return json.loads((FIXTURES / "valid_minimal.json").read_text(encoding="utf-8"))


def test_semantic_validation_warns_for_section_type_mismatch():
    document = _valid_document()
    document["curriculum"]["education"].append(
        {"id": "research-in-education", "type": "research.publication", "data": {}}
    )

    warnings = validate_open_cvn_semantics(document)

    assert len(warnings) == 1
    assert warnings[0].code == CvnErrorCode.SEMANTIC_VALIDATION_WARNING
    assert warnings[0].path == ("curriculum", "education", "0", "type")


def test_semantic_validation_warns_for_invalid_trace_code():
    document = _valid_document()
    document["curriculum"]["research"].append(
        {
            "id": "research-001",
            "type": "research.publication",
            "data": {},
            "trace": {"cvn_codes": ["not-a-cvn-code"]},
        }
    )

    warnings = validate_open_cvn_semantics(document)

    assert warnings[0].path == ("curriculum", "research", "0", "trace", "cvn_codes", "0")


def test_semantic_validation_warns_for_empty_controlled_reference():
    document = _valid_document()
    document["curriculum"]["achievements"].append(
        {
            "id": "achievement-001",
            "type": "achievements.award",
            "data": {"kind": {"source": "CVN_TEST"}},
        }
    )

    warnings = validate_open_cvn_semantics(document)

    assert warnings[0].path == ("curriculum", "achievements", "0", "data", "kind")


def test_json_validation_returns_semantic_warnings_after_schema_and_pydantic_validation():
    document = _valid_document()
    document["curriculum"]["education"].append(
        {"id": "research-in-education", "type": "research.publication", "data": {}}
    )

    result = validate_open_cvn_json(document, source_identifier="semantic-warning")

    assert result.validation_status == CvnValidationStatus.VALID_WITH_WARNINGS
    assert result.warnings[0].code == CvnErrorCode.SEMANTIC_VALIDATION_WARNING
