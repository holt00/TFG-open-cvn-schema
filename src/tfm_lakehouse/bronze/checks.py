from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any
from xml.etree import ElementTree as ET

from open_cvn.parser_contract import CvnValidationStatus, validate_open_cvn_json
from tfm_lakehouse.bronze.envelope import CHECK_INVALID, CHECK_VALID, LandingCheck
from tfm_lakehouse.orcid_client.client import validate_orcid_id
from tfm_lakehouse.orcid_client.exceptions import OrcidValidationError

_NS = {
    "common": "http://www.orcid.org/ns/common",
    "personal": "http://www.orcid.org/ns/personal-details",
    "employment": "http://www.orcid.org/ns/employment",
    "education": "http://www.orcid.org/ns/education",
}

_AFFILIATION_PATHS = (
    ".//employment:employment-summary/common:organization/common:name",
    ".//education:education-summary/common:organization/common:name",
)


def _result(errors: list[str]) -> LandingCheck:
    return LandingCheck(status=CHECK_INVALID if errors else CHECK_VALID, errors=tuple(errors))


def _text(element: ET.Element | None) -> str | None:
    if element is None or element.text is None:
        return None
    stripped = element.text.strip()
    return stripped or None


def _orcid_id_errors(orcid_id: str | None) -> list[str]:
    if orcid_id is None:
        return ["missing ORCID iD (common:orcid-identifier/common:path)"]
    try:
        validate_orcid_id(orcid_id)
    except OrcidValidationError as exc:
        return [str(exc)]
    return []


def check_cvn_document(document: Mapping[str, Any], source_identifier: str | None = None) -> LandingCheck:
    """Check that a CVN document is a schema-valid Open CVN JSON document.

    This is the light landing-time gate: it reuses `validate_open_cvn_json`
    (JSON Schema plus Pydantic) and nothing stricter. The entity-level check
    of each entry is issue #98's job.

    Args:
        document: The Open CVN JSON document.
        source_identifier: Optional identifier used in the validator's messages.

    Returns:
        A valid check, or an invalid one listing each validator error.
    """
    result = validate_open_cvn_json(document, source_identifier=source_identifier)
    if result.validation_status in (CvnValidationStatus.INVALID, CvnValidationStatus.FAILED):
        return LandingCheck(
            status=CHECK_INVALID,
            errors=tuple(f"{issue.code.value}: {issue.message}" for issue in result.errors) or ("invalid document",),
        )
    return LandingCheck(status=CHECK_VALID)


def check_orcid_summary_xml(xml_bytes: bytes) -> tuple[LandingCheck, str | None]:
    """Check the required fields of an ORCID record-summary XML.

    Required: well-formed XML, an ORCID iD with a valid checksum, given and
    family names, and at least one employment or education entry with an
    organization name. Names and affiliations are what issue #98's
    name/affiliation fallback needs; the affiliation is also what the
    issue #95 filter selected the record for.

    Args:
        xml_bytes: The raw record-summary XML.

    Returns:
        The check, and the ORCID iD when one could be read (so a rejected
        record can still be traced).
    """
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        return LandingCheck(status=CHECK_INVALID, errors=(f"malformed XML: {exc}",)), None

    orcid_id = _text(root.find("common:orcid-identifier/common:path", _NS))
    errors = _orcid_id_errors(orcid_id)
    if _text(root.find(".//personal:given-names", _NS)) is None:
        errors.append("missing given names (personal-details:given-names)")
    if _text(root.find(".//personal:family-name", _NS)) is None:
        errors.append("missing family name (personal-details:family-name)")
    if not any(_text(root.find(path, _NS)) is not None for path in _AFFILIATION_PATHS):
        errors.append("no employment or education entry with an organization name")
    return _result(errors), orcid_id


def check_orcid_api_record(record: Mapping[str, Any], expected_orcid_id: str) -> LandingCheck:
    """Check the required fields of an ORCID Public API ``/record`` response.

    Required: an ORCID iD with a valid checksum that matches the requested
    one, and a ``person`` section.
    """
    identifier = record.get("orcid-identifier")
    orcid_id = identifier.get("path") if isinstance(identifier, Mapping) else None
    errors = _orcid_id_errors(orcid_id if isinstance(orcid_id, str) else None)
    if not errors and orcid_id != expected_orcid_id:
        errors.append(f"record iD {orcid_id} does not match the requested {expected_orcid_id}")
    if not isinstance(record.get("person"), Mapping):
        errors.append("missing person section")
    return _result(errors)


def serialize_line(value: Mapping[str, Any]) -> bytes:
    """Serialize one JSON Lines record (compact, UTF-8, newline-terminated)."""
    return (json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
