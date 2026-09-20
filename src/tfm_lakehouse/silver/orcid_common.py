"""What the ORCID bulk-XML and ORCID API extractors share (issue #98, D5)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from tfm_lakehouse.orcid_client.client import validate_orcid_id
from tfm_lakehouse.orcid_client.exceptions import OrcidValidationError

RULE_XML_PARSE = "orcid_xml_parse"
RULE_JSON_SHAPE = "orcid_json_shape"
RULE_ORCID_ID = "orcid_id_checksum"
RULE_REQUIRED = "orcid_required_field"
RULE_NO_ACTIVITY = "orcid_no_activity"


@dataclass
class OrcidResult:
    """Outcome of processing one ORCID record.

    Args:
        errors: ``(rule, message)`` pairs; any error rejects the record.
        person: The ``person_record`` fields, or None when rejected.
        affiliations: ``affiliation`` rows, empty when rejected.
        publications: ``publication`` rows, empty when rejected.
    """

    errors: list[tuple[str, str]] = field(default_factory=list)
    person: dict[str, Any] | None = None
    affiliations: list[dict[str, Any]] = field(default_factory=list)
    publications: list[dict[str, Any]] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.errors


def orcid_id_error(orcid_id: str | None) -> tuple[str, str] | None:
    """Return the ``(rule, message)`` of an absent or invalid ORCID iD, else None."""
    if orcid_id is None:
        return RULE_REQUIRED, "missing ORCID iD"
    try:
        validate_orcid_id(orcid_id)
    except OrcidValidationError as exc:
        return RULE_ORCID_ID, str(exc)
    return None


def check_required(
    result: OrcidResult,
    *,
    given_names: str | None,
    family_name: str | None,
    affiliation_count: int,
    publication_count: int,
) -> None:
    """Append the D5 required-field errors to ``result``.

    Given and family names are required (the name/affiliation fallback of the
    entity resolution needs them), and so is at least one affiliation or work.
    """
    if given_names is None:
        result.errors.append((RULE_REQUIRED, "missing given names"))
    if family_name is None:
        result.errors.append((RULE_REQUIRED, "missing family name"))
    if affiliation_count == 0 and publication_count == 0:
        result.errors.append((RULE_NO_ACTIVITY, "no employment, education or work entry"))
