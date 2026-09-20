"""Validation and extraction of one ORCID bulk-file record-summary XML (issue #98, D5).

Reads only public name, affiliation and work fields; emails, biography and
researcher URLs are deliberately not read (issue #96's privacy rule). Every
employment/education summary becomes an affiliation; one work summary per work
group becomes a publication (the summaries of a group are the same work as
reported by different sources).
"""

from __future__ import annotations

from xml.etree import ElementTree as ET

from tfm_lakehouse.silver.normalize import parse_int
from tfm_lakehouse.silver.orcid_common import (
    RULE_XML_PARSE,
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

_NS = {
    "common": "http://www.orcid.org/ns/common",
    "personal": "http://www.orcid.org/ns/personal-details",
    "person": "http://www.orcid.org/ns/person",
    "history": "http://www.orcid.org/ns/history",
    "activities": "http://www.orcid.org/ns/activities",
    "employment": "http://www.orcid.org/ns/employment",
    "education": "http://www.orcid.org/ns/education",
    "work": "http://www.orcid.org/ns/work",
}


def process_orcid_xml(xml_text: str) -> OrcidResult:
    """Validate an ORCID record-summary XML and extract its silver rows.

    Args:
        xml_text: The raw XML, exactly as bronze landed it.

    Returns:
        The result; extraction only counts when it has no errors.
    """
    try:
        root = ET.fromstring(xml_text.encode("utf-8"))
    except ET.ParseError as exc:
        return OrcidResult(errors=[(RULE_XML_PARSE, f"malformed XML: {exc}")])

    result = OrcidResult()
    orcid_id = _text(root.find("common:orcid-identifier/common:path", _NS))
    id_error = orcid_id_error(orcid_id)
    if id_error is not None:
        result.errors.append(id_error)

    given_names = _text(root.find("person:person/person:name/personal:given-names", _NS))
    family_name = _text(root.find("person:person/person:name/personal:family-name", _NS))
    affiliations = [
        *_affiliations(root, KIND_EMPLOYMENT, "activities:employments//employment:employment-summary"),
        *_affiliations(root, KIND_EDUCATION, "activities:educations//education:education-summary"),
    ]
    publications = _publications(root)
    check_required(
        result,
        given_names=given_names,
        family_name=family_name,
        affiliation_count=len(affiliations),
        publication_count=len(publications),
    )
    if result.errors:
        return result

    result.person = make_person(
        given_names=given_names,
        family_name=family_name,
        orcid_id=orcid_id,
        source_last_modified=_text(root.find("history:history/common:last-modified-date", _NS)),
    )
    result.affiliations = affiliations
    result.publications = publications
    return result


def _affiliations(root: ET.Element, kind: str, path: str) -> list[dict]:
    rows: list[dict] = []
    for summary in root.iterfind(f".//activities:activities-summary/{path}", _NS):
        organization = _text(summary.find("common:organization/common:name", _NS))
        if organization is None:
            continue
        rows.append(
            make_affiliation(
                kind=kind,
                organization=organization,
                role=_text(summary.find("common:role-title", _NS)),
                department=_text(summary.find("common:department-name", _NS)),
                city=_text(summary.find("common:organization/common:address/common:city", _NS)),
                country=_text(summary.find("common:organization/common:address/common:country", _NS)),
                start_year=parse_int(_text(summary.find("common:start-date/common:year", _NS))),
                start_month=parse_int(_text(summary.find("common:start-date/common:month", _NS))),
                end_year=parse_int(_text(summary.find("common:end-date/common:year", _NS))),
                end_month=parse_int(_text(summary.find("common:end-date/common:month", _NS))),
            )
        )
    return rows


def _publications(root: ET.Element) -> list[dict]:
    rows: list[dict] = []
    for group in root.iterfind(".//activities:works/activities:group", _NS):
        summary = group.find("work:work-summary", _NS)
        if summary is None:
            continue
        title = _text(summary.find("work:title/common:title", _NS))
        if title is None:
            continue
        rows.append(
            make_publication(
                title=title,
                year=parse_int(_text(summary.find("common:publication-date/common:year", _NS))),
                month=parse_int(_text(summary.find("common:publication-date/common:month", _NS))),
                doi=_doi(summary.find("common:external-ids", _NS)) or _doi(group.find("common:external-ids", _NS)),
                work_type=_text(summary.find("work:type", _NS)),
            )
        )
    return rows


def _doi(external_ids: ET.Element | None) -> str | None:
    if external_ids is None:
        return None
    for external_id in external_ids.iterfind("common:external-id", _NS):
        if _text(external_id.find("common:external-id-type", _NS)) == "doi":
            return _text(external_id.find("common:external-id-value", _NS))
    return None


def _text(element: ET.Element | None) -> str | None:
    if element is None or element.text is None:
        return None
    stripped = " ".join(element.text.split())
    return stripped or None

