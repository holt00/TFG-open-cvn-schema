"""Validation and extraction of one ORCID Public API ``/record`` payload (issue #98, D5).

Same fields, same rules and the same output shape as ``orcid_xml``; the API
serializes them as JSON (``{"value": ...}`` wrappers, epoch-millisecond
timestamps, affiliation groups of ``summaries``). Emails, biography,
researcher URLs, other names and addresses are deliberately not read (issue
#96's privacy rule).
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any

from tfm_lakehouse.silver.normalize import parse_int
from tfm_lakehouse.silver.orcid_common import (
    RULE_JSON_SHAPE,
    RULE_ORCID_ID,
    OrcidResult,
    check_required,
    orcid_id_error,
)
from tfm_lakehouse.silver.records import (
    KIND_EDUCATION,
    KIND_EMPLOYMENT,
    make_affiliation,
    make_person,
    make_publication,
)


def process_orcid_api_record(record: Any, expected_orcid_id: str | None = None) -> OrcidResult:
    """Validate an ORCID API ``/record`` payload and extract its silver rows.

    Args:
        record: The parsed JSON payload, as bronze landed it.
        expected_orcid_id: The iD that was requested (the envelope's
            ``source_ref``). When given, a payload for a different iD is
            rejected.

    Returns:
        The result; extraction only counts when it has no errors.
    """
    if not isinstance(record, Mapping):
        return OrcidResult(errors=[(RULE_JSON_SHAPE, "the payload is not a JSON object")])

    result = OrcidResult()
    identifier = record.get("orcid-identifier")
    orcid_id = _str(identifier.get("path")) if isinstance(identifier, Mapping) else None
    id_error = orcid_id_error(orcid_id)
    if id_error is not None:
        result.errors.append(id_error)
    elif expected_orcid_id is not None and orcid_id != expected_orcid_id:
        result.errors.append((RULE_ORCID_ID, f"payload iD {orcid_id} does not match the requested {expected_orcid_id}"))

    person = record.get("person")
    name = person.get("name") if isinstance(person, Mapping) else None
    given_names = _value(name.get("given-names")) if isinstance(name, Mapping) else None
    family_name = _value(name.get("family-name")) if isinstance(name, Mapping) else None

    activities = record.get("activities-summary")
    activities = activities if isinstance(activities, Mapping) else {}
    affiliations = [
        *_affiliations(activities.get("employments"), "employment-summary", KIND_EMPLOYMENT),
        *_affiliations(activities.get("educations"), "education-summary", KIND_EDUCATION),
    ]
    publications = _publications(activities.get("works"))
    check_required(
        result,
        given_names=given_names,
        family_name=family_name,
        affiliation_count=len(affiliations),
        publication_count=len(publications),
    )
    if result.errors:
        return result

    history = record.get("history")
    result.person = make_person(
        given_names=given_names,
        family_name=family_name,
        orcid_id=orcid_id,
        source_last_modified=_epoch_ms_to_iso(_dig(history, "last-modified-date", "value")),
    )
    result.affiliations = affiliations
    result.publications = publications
    return result


def _affiliations(section: Any, summary_key: str, kind: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    groups = section.get("affiliation-group") if isinstance(section, Mapping) else None
    for group in groups if isinstance(groups, list) else []:
        summaries = group.get("summaries") if isinstance(group, Mapping) else None
        for wrapper in summaries if isinstance(summaries, list) else []:
            summary = wrapper.get(summary_key) if isinstance(wrapper, Mapping) else None
            if not isinstance(summary, Mapping):
                continue
            organization = summary.get("organization")
            name = _str(organization.get("name")) if isinstance(organization, Mapping) else None
            if name is None:
                continue
            address = organization.get("address") if isinstance(organization.get("address"), Mapping) else {}
            rows.append(
                make_affiliation(
                    kind=kind,
                    organization=name,
                    role=_str(summary.get("role-title")),
                    department=_str(summary.get("department-name")),
                    city=_str(address.get("city")),
                    country=_str(address.get("country")),
                    start_year=parse_int(_dig(summary, "start-date", "year", "value")),
                    start_month=parse_int(_dig(summary, "start-date", "month", "value")),
                    end_year=parse_int(_dig(summary, "end-date", "year", "value")),
                    end_month=parse_int(_dig(summary, "end-date", "month", "value")),
                )
            )
    return rows


def _publications(works: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    groups = works.get("group") if isinstance(works, Mapping) else None
    for group in groups if isinstance(groups, list) else []:
        summaries = group.get("work-summary") if isinstance(group, Mapping) else None
        summary = summaries[0] if isinstance(summaries, list) and summaries else None
        if not isinstance(summary, Mapping):
            continue
        title = _str(_dig(summary, "title", "title", "value"))
        if title is None:
            continue
        rows.append(
            make_publication(
                title=title,
                year=parse_int(_dig(summary, "publication-date", "year", "value")),
                month=parse_int(_dig(summary, "publication-date", "month", "value")),
                doi=_doi(summary.get("external-ids")) or _doi(group.get("external-ids")),
                work_type=_str(summary.get("type")),
            )
        )
    return rows


def _doi(external_ids: Any) -> str | None:
    entries = external_ids.get("external-id") if isinstance(external_ids, Mapping) else None
    for entry in entries if isinstance(entries, list) else []:
        if isinstance(entry, Mapping) and entry.get("external-id-type") == "doi":
            return _str(entry.get("external-id-value"))
    return None


def _dig(node: Any, *keys: str) -> Any:
    for key in keys:
        if not isinstance(node, Mapping):
            return None
        node = node.get(key)
    return node


def _value(node: Any) -> str | None:
    return _str(node.get("value")) if isinstance(node, Mapping) else None


def _str(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = " ".join(value.split())
    return stripped or None


def _epoch_ms_to_iso(value: Any) -> str | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return datetime.fromtimestamp(value / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
