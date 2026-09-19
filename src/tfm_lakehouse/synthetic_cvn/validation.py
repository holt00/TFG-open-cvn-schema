from __future__ import annotations

import json
from collections.abc import Mapping
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from open_cvn.parser_contract import CvnValidationStatus, validate_open_cvn_json
from tfm_lakehouse.orcid_client.client import validate_orcid_id
from tfm_lakehouse.orcid_client.exceptions import OrcidValidationError

_SECTIONS = ("education", "research", "professional_experience", "achievements", "other")
_IDENTITY_DEF = "identity.person"
_ORCID_SOURCE_CODE = "140"


def validate_synthetic_document(document: Mapping[str, Any]) -> tuple[str, ...]:
    """Validate one generated Open CVN document, returning every problem found.

    Runs two layers. First `validate_open_cvn_json`, which is the project's
    schema and Pydantic gate; warnings from it count as errors here because a
    generated document has no excuse for them. Then a stricter layer: the
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

    curriculum = document.get("curriculum")
    if not isinstance(curriculum, Mapping):
        return (*errors, "curriculum is missing or not an object")

    identity = curriculum.get("identity")
    if isinstance(identity, Mapping):
        errors.extend(_entity_errors(_IDENTITY_DEF, identity, "curriculum/identity"))
        errors.extend(_orcid_errors(identity))
    else:
        errors.append("curriculum/identity is missing or not an object")

    for section in _SECTIONS:
        entries = curriculum.get(section, [])
        for index, entry in enumerate(entries if isinstance(entries, list) else []):
            location = f"curriculum/{section}/{index}"
            entry_type = entry.get("type") if isinstance(entry, Mapping) else None
            data = entry.get("data") if isinstance(entry, Mapping) else None
            if not isinstance(entry_type, str) or not isinstance(data, Mapping):
                errors.append(f"{location}: entry needs a string type and an object data")
                continue
            errors.extend(_entity_errors(entry_type, data, location))
    return tuple(errors)


def _entity_errors(entity_def: str, data: Mapping[str, Any], location: str) -> list[str]:
    validator = _entity_validator(entity_def)
    if validator is None:
        return [f"{location}: '{entity_def}' is not an entity type defined by the schema"]
    return [
        f"{location}/{'/'.join(str(part) for part in error.absolute_path)}: {error.message}"
        if error.absolute_path
        else f"{location}: {error.message}"
        for error in sorted(validator.iter_errors(data), key=lambda item: item.message)
    ]


def _orcid_errors(identity: Mapping[str, Any]) -> list[str]:
    identifiers = identity.get("identificador_digital_de_autor") or []
    types = identity.get("tipo_de_identificador_digital_de_autor") or []
    if len(identifiers) != len(types):
        return ["identity: identificador_digital_de_autor and its type list differ in length"]
    errors: list[str] = []
    for identifier, identifier_type in zip(identifiers, types, strict=True):
        if not isinstance(identifier_type, Mapping) or identifier_type.get("code") != _ORCID_SOURCE_CODE:
            continue
        try:
            validate_orcid_id(str(identifier))
        except OrcidValidationError as exc:
            errors.append(f"identity: {exc}")
    return errors


@lru_cache(maxsize=1)
def _schema() -> dict[str, Any]:
    schema_path = Path(__file__).resolve().parents[3] / "schemas" / "open_cvn.schema.json"
    return json.loads(schema_path.read_text(encoding="utf-8"))


@lru_cache(maxsize=None)
def _entity_validator(entity_def: str) -> Draft202012Validator | None:
    schema = _schema()
    definitions = schema["$defs"]
    if entity_def not in definitions:
        return None
    return Draft202012Validator(
        {"$schema": schema["$schema"], "$ref": f"#/$defs/{entity_def}", "$defs": definitions}
    )
