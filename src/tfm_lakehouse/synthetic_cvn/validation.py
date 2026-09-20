from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from open_cvn.parser_contract import CvnValidationStatus, validate_open_cvn_json
from tfm_lakehouse.cvn_validation import entity_schema_errors, orcid_identifier_errors


def validate_synthetic_document(document: Mapping[str, Any]) -> tuple[str, ...]:
    """Validate one generated Open CVN document, returning every problem found.

    Runs two layers. First `validate_open_cvn_json`, which is the project's
    schema and Pydantic gate; warnings from it count as errors here because a
    generated document has no excuse for them. Then a stricter layer
    (`tfm_lakehouse.cvn_validation`, shared with the bronze -> silver job): the
    JSON Schema only requires entry ``data`` and ``identity`` to be free-form
    objects, so each is also validated against the ``$defs`` schema of its own
    entity, which rejects invented fields and missing required ones.

    Returns:
        An empty tuple when the document is valid.
    """
    errors: list[str] = []

    result = validate_open_cvn_json(document)
    if result.validation_status != CvnValidationStatus.VALID:
        for issue in (*result.errors, *result.warnings):
            detail = issue.details.get("message", issue.message)
            errors.append(f"{issue.code.value} at {'/'.join(issue.path) or '<root>'}: {detail}")
        if not errors:
            errors.append(f"document status is {result.validation_status.value}")

    errors.extend(entity_schema_errors(document))

    curriculum = document.get("curriculum")
    identity = curriculum.get("identity") if isinstance(curriculum, Mapping) else None
    if isinstance(identity, Mapping):
        errors.extend(orcid_identifier_errors(identity))
    return tuple(errors)
