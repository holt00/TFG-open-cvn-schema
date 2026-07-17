import pytest
from pydantic import ValidationError
from pathlib import Path

from open_cvn import (
    CvnErrorCode,
    CvnIssueSeverity,
    CvnParseIssue,
    CvnParseResult,
    CvnParseTrace,
    CvnSourceFormat,
    CvnValidationStatus,
    parse_cvn_xml,
    parse_open_cvn_json,
    validate_open_cvn_json,
)


def test_contract_enums_have_stable_serialized_values():
    assert CvnSourceFormat.PDF.value == "pdf"
    assert CvnSourceFormat.CVN_XML.value == "cvn_xml"
    assert CvnSourceFormat.OPEN_CVN_JSON.value == "open_cvn_json"
    assert CvnValidationStatus.NOT_RUN.value == "not_run"
    assert CvnValidationStatus.VALID.value == "valid"
    assert CvnValidationStatus.VALID_WITH_WARNINGS.value == "valid_with_warnings"
    assert CvnValidationStatus.INVALID.value == "invalid"
    assert CvnValidationStatus.FAILED.value == "failed"
    assert CvnIssueSeverity.WARNING.value == "warning"
    assert CvnIssueSeverity.ERROR.value == "error"


def test_contract_error_codes_cover_issue_47_cases():
    assert {error_code.value for error_code in CvnErrorCode} == {
        "unsupported_input_format",
        "unreadable_file",
        "pdf_without_extractable_xml",
        "llm_import_disabled",
        "llm_provider_error",
        "llm_invalid_response",
        "llm_output_validation_failure",
        "invalid_xml",
        "xml_semantically_unmappable",
        "invalid_json",
        "json_schema_validation_failure",
        "pydantic_validation_failure",
    }


def test_parse_issue_serializes_structured_error_data():
    issue = CvnParseIssue(
        code=CvnErrorCode.INVALID_JSON,
        severity=CvnIssueSeverity.ERROR,
        message="Input is not valid JSON.",
        source_location="line 1 column 2",
        path=("metadata", "policy"),
        details={"line": 1, "column": 2},
    )

    assert issue.model_dump(mode="json") == {
        "code": "invalid_json",
        "severity": "error",
        "message": "Input is not valid JSON.",
        "source_location": "line 1 column 2",
        "path": ["metadata", "policy"],
        "details": {"line": 1, "column": 2},
    }


def test_parse_trace_serializes_source_and_policy_metadata():
    trace = CvnParseTrace(
        source_format=CvnSourceFormat.OPEN_CVN_JSON,
        source_identifier="examples/open_cvn/minimal.json",
        source_path="examples/open_cvn/minimal.json",
        cvn_codes=("000.010.000.000",),
        xml_paths=("CVNRoot/PersonalData",),
        schema_version="0.1.0",
        policy_name="default_cvn_semantic_policy",
        policy_version="0.1.0",
    )

    assert trace.model_dump(mode="json") == {
        "source_format": "open_cvn_json",
        "source_identifier": "examples/open_cvn/minimal.json",
        "source_path": "examples/open_cvn/minimal.json",
        "extracted_from": None,
        "cvn_codes": ["000.010.000.000"],
        "xml_paths": ["CVNRoot/PersonalData"],
        "schema_version": "0.1.0",
        "policy_name": "default_cvn_semantic_policy",
        "policy_version": "0.1.0",
    }


def test_parse_result_supports_valid_result_shape():
    result = CvnParseResult(
        source_format=CvnSourceFormat.OPEN_CVN_JSON,
        source_identifier="minimal.json",
        data={"schema_version": "0.1.0"},
        validation_status=CvnValidationStatus.VALID,
        trace=CvnParseTrace(
            source_format=CvnSourceFormat.OPEN_CVN_JSON,
            source_identifier="minimal.json",
            schema_version="0.1.0",
        ),
    )

    assert result.model_dump(mode="json")["validation_status"] == "valid"
    assert result.model_dump(mode="json")["errors"] == []


def test_parse_result_supports_valid_with_warnings_result_shape():
    warning = CvnParseIssue(
        code=CvnErrorCode.UNSUPPORTED_INPUT_FORMAT,
        severity=CvnIssueSeverity.WARNING,
        message="Best-effort parser warning.",
    )

    result = CvnParseResult(
        source_format=CvnSourceFormat.CVN_XML,
        validation_status=CvnValidationStatus.VALID_WITH_WARNINGS,
        warnings=(warning,),
    )

    assert result.model_dump(mode="json")["validation_status"] == "valid_with_warnings"
    assert result.model_dump(mode="json")["warnings"][0]["severity"] == "warning"


def test_parse_result_supports_invalid_result_shape():
    error = CvnParseIssue(
        code=CvnErrorCode.JSON_SCHEMA_VALIDATION_FAILURE,
        severity=CvnIssueSeverity.ERROR,
        message="Open CVN JSON does not match the generated schema.",
        path=("curriculum",),
    )

    result = CvnParseResult(
        source_format=CvnSourceFormat.OPEN_CVN_JSON,
        validation_status=CvnValidationStatus.INVALID,
        errors=(error,),
    )

    assert result.model_dump(mode="json")["validation_status"] == "invalid"
    assert result.model_dump(mode="json")["errors"][0]["code"] == (
        "json_schema_validation_failure"
    )


def test_parse_result_supports_failed_result_shape():
    error = CvnParseIssue(
        code=CvnErrorCode.PDF_WITHOUT_EXTRACTABLE_XML,
        severity=CvnIssueSeverity.ERROR,
        message="PDF does not contain extractable CVN XML.",
    )

    result = CvnParseResult(
        source_format=CvnSourceFormat.PDF,
        source_identifier="cvn.pdf",
        validation_status=CvnValidationStatus.FAILED,
        errors=(error,),
    )

    assert result.model_dump(mode="json")["validation_status"] == "failed"
    assert result.model_dump(mode="json")["errors"][0]["code"] == (
        "pdf_without_extractable_xml"
    )


def test_parse_result_rejects_errors_with_valid_status():
    error = CvnParseIssue(
        code=CvnErrorCode.INVALID_JSON,
        severity=CvnIssueSeverity.ERROR,
        message="Input is not valid JSON.",
    )

    with pytest.raises(ValidationError, match="Results with errors must be invalid or failed"):
        CvnParseResult(
            source_format=CvnSourceFormat.OPEN_CVN_JSON,
            validation_status=CvnValidationStatus.VALID,
            errors=(error,),
        )


def test_parse_result_rejects_warning_status_without_warning():
    with pytest.raises(
        ValidationError,
        match="valid_with_warnings results must include at least one warning",
    ):
        CvnParseResult(
            source_format=CvnSourceFormat.OPEN_CVN_JSON,
            validation_status=CvnValidationStatus.VALID_WITH_WARNINGS,
        )


def test_parse_cvn_xml_returns_contract_result():
    result = parse_cvn_xml("<CVNRoot />", source_identifier="input")

    assert result.source_format == CvnSourceFormat.CVN_XML
    assert result.source_identifier == "input"
    assert result.validation_status == CvnValidationStatus.VALID


def test_parse_open_cvn_json_returns_contract_result():
    payload = Path("tests/fixtures/open_cvn/valid_minimal.json").read_text(encoding="utf-8")

    result = parse_open_cvn_json(
        payload,
        source_identifier="input",
    )

    assert result.source_format == CvnSourceFormat.OPEN_CVN_JSON
    assert result.source_identifier == "input"
    assert result.validation_status == CvnValidationStatus.VALID


def test_validate_open_cvn_json_returns_contract_result():
    payload = {
        "schema_version": "0.1.0",
        "metadata": {
            "language": "es",
            "policy": {
                "name": "default_cvn_semantic_policy",
                "version": "0.1.0",
            },
        },
        "curriculum": {
            "identity": {},
            "education": [],
            "research": [],
            "professional_experience": [],
            "achievements": [],
            "other": [],
        },
    }

    result = validate_open_cvn_json(
        payload,
        source_identifier="input",
    )

    assert result.source_format == CvnSourceFormat.OPEN_CVN_JSON
    assert result.source_identifier == "input"
    assert result.validation_status == CvnValidationStatus.VALID
