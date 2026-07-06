from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError
from pydantic import ValidationError

from open_cvn.import_utils import (
    extract_json_trace_values,
    load_text_input,
    make_error,
    make_trace,
    make_warning,
    pydantic_errors_to_issues,
    serializable_details,
)
from open_cvn.open_cvn_models import OpenCvnDocument, is_newer_compatible_version
from open_cvn.parser_contract import (
    CvnErrorCode,
    CvnInput,
    CvnParseIssue,
    CvnParseResult,
    CvnSourceFormat,
    CvnValidationStatus,
)


def parse_open_cvn_json(source: CvnInput, *, source_identifier: str | None = None) -> CvnParseResult:
    if isinstance(source, Mapping):
        return validate_open_cvn_json(source, source_identifier=source_identifier)
    try:
        loaded = load_text_input(
            source,  # type: ignore[arg-type]
            source_identifier=source_identifier,
            missing_path_is_text=True,
        )
    except (OSError, UnicodeDecodeError) as exc:
        return _json_failed_result(
            source_identifier=source_identifier,
            source_path=str(source) if isinstance(source, Path | str) else None,
            error=make_error(
                code=CvnErrorCode.UNREADABLE_FILE,
                message="JSON input could not be read.",
                details={"error": str(exc)},
            ),
        )
    except TypeError as exc:
        return _json_failed_result(
            source_identifier=source_identifier,
            source_path=None,
            error=make_error(
                code=CvnErrorCode.UNSUPPORTED_INPUT_FORMAT,
                message="Open CVN JSON input must be a path, bytes, JSON string, or mapping.",
                details={"error": str(exc)},
            ),
        )

    try:
        document = json.loads(loaded.text)
    except json.JSONDecodeError as exc:
        source_location = f"line {exc.lineno} column {exc.colno}"
        return _json_failed_result(
            source_identifier=loaded.source_identifier,
            source_path=loaded.source_path,
            error=make_error(
                code=CvnErrorCode.INVALID_JSON,
                message="Input is not valid JSON.",
                source_location=source_location,
                details={"line": exc.lineno, "column": exc.colno, "error": exc.msg},
            ),
        )

    if not isinstance(document, Mapping):
        return _json_invalid_result(
            source_identifier=loaded.source_identifier,
            source_path=loaded.source_path,
            errors=(
                make_error(
                    code=CvnErrorCode.PYDANTIC_VALIDATION_FAILURE,
                    message="Open CVN JSON document must be an object.",
                    details={"input_type": type(document).__name__},
                ),
            ),
            document=None,
        )
    return validate_open_cvn_json(
        document,
        source_identifier=loaded.source_identifier,
        source_path=loaded.source_path,
    )


def validate_open_cvn_json(
    document: Mapping[str, Any],
    *,
    source_identifier: str | None = None,
    source_path: str | None = None,
) -> CvnParseResult:
    schema_version, policy_name, policy_version = extract_json_trace_values(document)
    trace = make_trace(
        source_format=CvnSourceFormat.OPEN_CVN_JSON,
        source_identifier=source_identifier,
        source_path=source_path,
        schema_version=schema_version,
        policy_name=policy_name,
        policy_version=policy_version,
    )

    schema_errors = _validate_json_schema(document)
    if schema_errors:
        return CvnParseResult(
            source_format=CvnSourceFormat.OPEN_CVN_JSON,
            source_identifier=source_identifier,
            validation_status=CvnValidationStatus.INVALID,
            errors=schema_errors,
            trace=trace,
        )

    try:
        open_cvn_document = OpenCvnDocument.model_validate(document)
    except ValidationError as exc:
        return CvnParseResult(
            source_format=CvnSourceFormat.OPEN_CVN_JSON,
            source_identifier=source_identifier,
            validation_status=CvnValidationStatus.INVALID,
            errors=pydantic_errors_to_issues(exc),
            trace=trace,
        )

    warnings = _version_warnings(open_cvn_document.schema_version)
    return CvnParseResult(
        source_format=CvnSourceFormat.OPEN_CVN_JSON,
        source_identifier=source_identifier,
        data=open_cvn_document.model_dump(mode="json", exclude_none=True),
        validation_status=(
            CvnValidationStatus.VALID_WITH_WARNINGS if warnings else CvnValidationStatus.VALID
        ),
        warnings=warnings,
        trace=trace,
    )


def _validate_json_schema(document: Mapping[str, Any]) -> tuple[CvnParseIssue, ...]:
    validator = _json_schema_validator()
    errors = sorted(
        validator.iter_errors(document),
        key=lambda error: (tuple(str(part) for part in error.absolute_path), error.message),
    )
    return tuple(_json_schema_error_to_issue(error) for error in errors)


@lru_cache(maxsize=1)
def _json_schema_validator() -> Draft202012Validator:
    schema = json.loads(_schema_path().read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def _schema_path() -> Path:
    return Path(__file__).resolve().parents[2] / "schemas" / "open_cvn.schema.json"


def _json_schema_error_to_issue(error: JsonSchemaValidationError) -> CvnParseIssue:
    return make_error(
        code=CvnErrorCode.JSON_SCHEMA_VALIDATION_FAILURE,
        message="Open CVN JSON does not match the generated schema.",
        path=tuple(str(part) for part in error.absolute_path),
        details=serializable_details(
            {
                "message": error.message,
                "validator": error.validator,
                "validator_value": error.validator_value,
            }
        ),
    )


def _version_warnings(schema_version: str) -> tuple[CvnParseIssue, ...]:
    if not is_newer_compatible_version(schema_version):
        return ()
    return (
        make_warning(
            code=CvnErrorCode.PYDANTIC_VALIDATION_FAILURE,
            message="Open CVN JSON schema_version is newer than the current runtime version.",
            path=("schema_version",),
            details={"schema_version": schema_version},
        ),
    )


def _json_failed_result(
    *, source_identifier: str | None, source_path: str | None, error: CvnParseIssue
) -> CvnParseResult:
    return CvnParseResult(
        source_format=CvnSourceFormat.OPEN_CVN_JSON,
        source_identifier=source_identifier or source_path,
        validation_status=CvnValidationStatus.FAILED,
        errors=(error,),
        trace=make_trace(
            source_format=CvnSourceFormat.OPEN_CVN_JSON,
            source_identifier=source_identifier or source_path,
            source_path=source_path,
        ),
    )


def _json_invalid_result(
    *,
    source_identifier: str | None,
    source_path: str | None,
    errors: tuple[CvnParseIssue, ...],
    document: Mapping[str, Any] | None,
) -> CvnParseResult:
    schema_version = policy_name = policy_version = None
    if document is not None:
        schema_version, policy_name, policy_version = extract_json_trace_values(document)
    return CvnParseResult(
        source_format=CvnSourceFormat.OPEN_CVN_JSON,
        source_identifier=source_identifier,
        validation_status=CvnValidationStatus.INVALID,
        errors=errors,
        trace=make_trace(
            source_format=CvnSourceFormat.OPEN_CVN_JSON,
            source_identifier=source_identifier,
            source_path=source_path,
            schema_version=schema_version,
            policy_name=policy_name,
            policy_version=policy_version,
        ),
    )
