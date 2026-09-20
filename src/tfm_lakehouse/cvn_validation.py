"""Entity-level validation of Open CVN JSON documents, shared by issues #96 and #98.

The document JSON Schema only requires ``identity`` and each entry's ``data`` to
be free-form objects, so ``validate_open_cvn_json`` accepts invented fields and
misses required ones (issue #96). The checks here validate each of them against
the ``$defs`` schema of its own entity, and check the ORCID iDs a document
declares. The synthetic generator (#96) and the bronze -> silver job (#98) both
use them.

Runs inside the Spark image's Python 3.10 as well as on the host, so it must
stay 3.10 compatible.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from tfm_lakehouse.orcid_client.client import validate_orcid_id
from tfm_lakehouse.orcid_client.exceptions import OrcidValidationError

SECTIONS = ("education", "research", "professional_experience", "achievements", "other")
IDENTITY_DEF = "identity.person"
ORCID_SOURCE_CODE = "140"


def entity_schema_errors(document: Mapping[str, Any]) -> list[str]:
    """Validate ``identity`` and every entry's ``data`` against their own entity schema.

    Args:
        document: An Open CVN JSON document.

    Returns:
        One message per problem, each starting with its location; empty when the
        document conforms.
    """
    curriculum = document.get("curriculum")
    if not isinstance(curriculum, Mapping):
        return ["curriculum is missing or not an object"]

    errors: list[str] = []
    identity = curriculum.get("identity")
    if isinstance(identity, Mapping):
        errors.extend(_entity_errors(IDENTITY_DEF, identity, "curriculum/identity"))
    else:
        errors.append("curriculum/identity is missing or not an object")

    for section in SECTIONS:
        entries = curriculum.get(section, [])
        for index, entry in enumerate(entries if isinstance(entries, list) else []):
            location = f"curriculum/{section}/{index}"
            entry_type = entry.get("type") if isinstance(entry, Mapping) else None
            data = entry.get("data") if isinstance(entry, Mapping) else None
            if not isinstance(entry_type, str) or not isinstance(data, Mapping):
                errors.append(f"{location}: entry needs a string type and an object data")
                continue
            errors.extend(_entity_errors(entry_type, data, location))
    return errors


def orcid_identifier_errors(identity: Mapping[str, Any]) -> list[str]:
    """Check the ORCID iDs an identity declares (type code ``140``).

    Returns:
        A message when the identifier and type lists differ in length or an
        iD fails its format or checksum; empty otherwise.
    """
    identifiers = identity.get("identificador_digital_de_autor") or []
    types = identity.get("tipo_de_identificador_digital_de_autor") or []
    if len(identifiers) != len(types):
        return ["identity: identificador_digital_de_autor and its type list differ in length"]
    errors: list[str] = []
    for identifier, identifier_type in zip(identifiers, types):
        if not isinstance(identifier_type, Mapping) or identifier_type.get("code") != ORCID_SOURCE_CODE:
            continue
        try:
            validate_orcid_id(str(identifier))
        except OrcidValidationError as exc:
            errors.append(f"identity: {exc}")
    return errors


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


@lru_cache(maxsize=1)
def _schema() -> dict[str, Any]:
    schema_path = Path(__file__).resolve().parents[2] / "schemas" / "open_cvn.schema.json"
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
