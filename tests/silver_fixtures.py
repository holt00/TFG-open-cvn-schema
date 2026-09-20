"""Builders of ORCID and CVN records shaped like the real bronze payloads (issue #98 tests)."""

from __future__ import annotations

import random
from typing import Any

from tfm_lakehouse.synthetic_cvn.builders import build_document
from tfm_lakehouse.synthetic_cvn.seed import OrcidAffiliation, OrcidSeed, OrcidWork

BIOGRAPHY = "PRIVATE-BIOGRAPHY-TEXT"

_NAMESPACES = " ".join(
    f'xmlns:{prefix}="http://www.orcid.org/ns/{name}"'
    for prefix, name in (
        ("record", "record"),
        ("common", "common"),
        ("personal", "personal-details"),
        ("person", "person"),
        ("history", "history"),
        ("activities", "activities"),
        ("employment", "employment"),
        ("education", "education"),
        ("work", "work"),
    )
)


def orcid_id(number: int) -> str:
    """Return a well-formed ORCID iD with a valid ISO 7064 MOD 11-2 checksum."""
    digits = f"{number:015d}"
    total = 0
    for digit in digits:
        total = (total + int(digit)) * 2
    check_value = (12 - total % 11) % 11
    full = digits + ("X" if check_value == 10 else str(check_value))
    return "-".join(full[i : i + 4] for i in range(0, 16, 4))


def _xml_affiliation(tag: str, org: str, role: str | None, start: str, end: str | None) -> str:
    end_xml = f"<common:end-date><common:year>{end}</common:year><common:month>06</common:month></common:end-date>" if end else ""
    role_xml = f"<common:role-title>{role}</common:role-title>" if role else ""
    return (
        "<activities:affiliation-group>"
        f"<{tag}:{tag}-summary>{role_xml}<common:department-name>Dept</common:department-name>"
        f"<common:start-date><common:year>{start}</common:year><common:month>09</common:month></common:start-date>"
        f"{end_xml}<common:organization><common:name>{org}</common:name>"
        "<common:address><common:city>Madrid</common:city><common:country>ES</common:country></common:address>"
        f"</common:organization></{tag}:{tag}-summary></activities:affiliation-group>"
    )


def _xml_work_group(title: str, year: str, doi_in_group: str | None, doi_in_summary: str | None) -> str:
    def external_ids(doi: str | None) -> str:
        if doi is None:
            return ""
        return (
            "<common:external-ids><common:external-id><common:external-id-type>doi</common:external-id-type>"
            f"<common:external-id-value>{doi}</common:external-id-value></common:external-id></common:external-ids>"
        )

    summary = (
        f"<work:work-summary><work:title><common:title>{title}</common:title></work:title>{external_ids(doi_in_summary)}"
        "<work:type>journal-article</work:type>"
        f"<common:publication-date><common:year>{year}</common:year><common:month>03</common:month></common:publication-date>"
        "</work:work-summary>"
    )
    duplicate = summary.replace(title, f"{title} (duplicate from another source)")
    return f"<activities:group>{external_ids(doi_in_group)}{summary}{duplicate}</activities:group>"


def orcid_xml(
    ident: str,
    given: str | None = "Ana",
    family: str | None = "García López",
    *,
    activities: bool = True,
) -> str:
    """Build a record-summary XML with the real ORCID container structure."""
    given_xml = f"<personal:given-names>{given}</personal:given-names>" if given else ""
    family_xml = f"<personal:family-name>{family}</personal:family-name>" if family else ""
    body = ""
    if activities:
        body = (
            "<activities:activities-summary>"
            "<activities:employments>"
            + _xml_affiliation("employment", "Universidad de Ejemplo", "Profesora Titular", "2018", None)
            + _xml_affiliation("employment", "Centro de Pruebas", "Investigadora", "2012", "2018")
            + "</activities:employments><activities:educations>"
            + _xml_affiliation("education", "Universidad de Ejemplo", "Doctora en Informática", "2008", "2012")
            + "</activities:educations><activities:works>"
            + _xml_work_group("Un artículo de ejemplo", "2020", None, "https://doi.org/10.1000/ABC")
            + _xml_work_group("Un capítulo de ejemplo", "2019", "10.1000/group-level", None)
            + _xml_work_group("Una ponencia sin DOI", "2018", None, None)
            + "</activities:works></activities:activities-summary>"
        )
    return (
        f'<?xml version="1.0" encoding="UTF-8"?><record:record {_NAMESPACES}>'
        f"<common:orcid-identifier><common:path>{ident}</common:path></common:orcid-identifier>"
        "<history:history><common:last-modified-date>2025-04-21T14:47:21.296Z</common:last-modified-date></history:history>"
        f"<person:person><person:name>{given_xml}{family_xml}</person:name>"
        f"<person:biography><personal:content>{BIOGRAPHY}</personal:content></person:biography>"
        f"</person:person>{body}</record:record>"
    )


def _api_affiliation(kind: str, org: str, role: str, start: str, end: str | None) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "role-title": role,
        "department-name": "Dept",
        "start-date": {"year": {"value": start}, "month": {"value": "09"}, "day": None},
        "end-date": {"year": {"value": end}, "month": {"value": "06"}, "day": None} if end else None,
        "organization": {"name": org, "address": {"city": "Madrid", "region": None, "country": "ES"}},
    }
    return {"summaries": [{f"{kind}-summary": summary}]}


def _api_work_group(title: str, year: str, doi_in_group: str | None, doi_in_summary: str | None) -> dict[str, Any]:
    def external_ids(doi: str | None) -> dict[str, Any]:
        return {"external-id": [{"external-id-type": "doi", "external-id-value": doi}]} if doi else {"external-id": []}

    def summary(work_title: str) -> dict[str, Any]:
        return {
            "title": {"title": {"value": work_title}},
            "type": "journal-article",
            "publication-date": {"year": {"value": year}, "month": {"value": "03"}},
            "external-ids": external_ids(doi_in_summary),
        }

    return {"external-ids": external_ids(doi_in_group), "work-summary": [summary(title), summary(f"{title} (duplicate)")]}


def orcid_api_record(ident: str, given: str | None = "Ana", family: str | None = "García López") -> dict[str, Any]:
    """Build an ORCID Public API ``/record`` payload shaped like the real one."""
    return {
        "orcid-identifier": {"uri": f"https://orcid.org/{ident}", "path": ident, "host": "orcid.org"},
        "history": {"last-modified-date": {"value": 1789720631521}},
        "person": {
            "name": {"given-names": {"value": given} if given else None, "family-name": {"value": family} if family else None},
            "biography": {"content": BIOGRAPHY},
            "emails": {"email": []},
        },
        "activities-summary": {
            "employments": {
                "affiliation-group": [
                    _api_affiliation("employment", "Universidad de Ejemplo", "Profesora Titular", "2018", None),
                    _api_affiliation("employment", "Centro de Pruebas", "Investigadora", "2012", "2018"),
                ]
            },
            "educations": {"affiliation-group": [_api_affiliation("education", "Universidad de Ejemplo", "Doctora en Informática", "2008", "2012")]},
            "works": {
                "group": [
                    _api_work_group("Un artículo de ejemplo", "2020", None, "https://doi.org/10.1000/ABC"),
                    _api_work_group("Un capítulo de ejemplo", "2019", "10.1000/group-level", None),
                    _api_work_group("Una ponencia sin DOI", "2018", None, None),
                ]
            },
        },
    }


def synthetic_seed(ident: str, given: str = "Ana", family: str = "García López") -> OrcidSeed:
    """A seed with two employments, a doctorate, and five works (four with a DOI)."""
    affiliations = (
        OrcidAffiliation("employment", "Universidad de Ejemplo", "Madrid", "ES", "Profesora Titular", None, "2018", "09", None, None),
        OrcidAffiliation("employment", "Centro de Pruebas", "Madrid", "ES", "Investigadora", None, "2012", "09", "2018", "06"),
        OrcidAffiliation("education", "Universidad de Ejemplo", "Madrid", "ES", "Doctor en Informática", "Informática", "2008", "09", "2012", "06"),
    )
    works = tuple(
        OrcidWork(f"Trabajo número {index}", "journal-article", str(2015 + index), "03", f"10.1000/t{index}" if index else None)
        for index in range(5)
    )
    return OrcidSeed(orcid_id=ident, given_names=given, family_name=family, affiliations=affiliations, works=works, keywords=())


def synthetic_document(ident: str, *, include_orcid: bool = True, given: str = "Ana", family: str = "García López") -> dict[str, Any]:
    """A schema-valid synthetic Open CVN document built by the issue #96 generator."""
    document, _ = build_document(
        synthetic_seed(ident, given, family),
        document_id="SYN-TEST-00000001",
        run_seed=1,
        include_orcid=include_orcid,
        rng=random.Random(7),
    )
    return document


def envelope(
    source: str,
    source_ref: str,
    payload: Any,
    *,
    landed_at: str = "2026-09-19T10:00:00Z",
    run_id: str = "run-1",
) -> dict[str, Any]:
    """Wrap a payload in the bronze envelope issue #97 lands (same fields)."""
    return {
        "record_id": f"{source}:{source_ref}",
        "source": source,
        "source_ref": source_ref,
        "source_snapshot": "test-snapshot",
        "source_files": [],
        "source_artifacts": [],
        "retrieved_at": landed_at,
        "landed_at": landed_at,
        "ingestion_date": landed_at[:10],
        "ingestion_run_id": run_id,
        "landing_check": {"status": "valid", "errors": []},
        "payload_format": "xml" if isinstance(payload, str) else "json",
        "payload": payload,
    }
