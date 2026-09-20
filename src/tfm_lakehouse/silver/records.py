"""The common shape silver gives every source's persons, affiliations and publications.

CVN documents, ORCID bulk XML and ORCID API JSON each have their own extractor;
all of them build their output through the functions below, so the shape (and
the normalized keys entity resolution compares) is defined in one place. The
keys of each dict are the columns of the matching table in ``schemas.py``.
"""

from __future__ import annotations

from typing import Any

from tfm_lakehouse.silver.normalize import (
    normalize_doi,
    normalize_organization,
    normalize_person_name,
    normalize_title,
)

KIND_EMPLOYMENT = "employment"
KIND_EDUCATION = "education"


def make_person(
    *,
    given_names: str | None,
    family_name: str | None,
    orcid_id: str | None,
    source_last_modified: str | None = None,
) -> dict[str, Any]:
    """Build one ``person_record`` row (without the envelope provenance)."""
    name = normalize_person_name(given_names, family_name)
    return {
        "given_names": given_names,
        "family_name": family_name,
        "given_norm": name.given,
        "family_norm": name.family,
        "family_key": name.family_key,
        "given_initial": name.given_initial,
        "orcid_id": orcid_id,
        "source_last_modified": source_last_modified,
    }


def make_affiliation(
    *,
    kind: str,
    organization: str,
    role: str | None = None,
    department: str | None = None,
    city: str | None = None,
    country: str | None = None,
    start_year: int | None = None,
    start_month: int | None = None,
    end_year: int | None = None,
    end_month: int | None = None,
) -> dict[str, Any]:
    """Build one ``affiliation`` row (without ``record_id``)."""
    return {
        "kind": kind,
        "organization": organization,
        "organization_norm": normalize_organization(organization),
        "role": role,
        "department": department,
        "city": city,
        "country": country,
        "start_year": start_year,
        "start_month": start_month,
        "end_year": end_year,
        "end_month": end_month,
    }


def make_publication(
    *,
    title: str,
    year: int | None = None,
    month: int | None = None,
    doi: str | None = None,
    work_type: str | None = None,
    authors: list[str] | None = None,
) -> dict[str, Any]:
    """Build one ``publication`` row (without ``record_id``).

    ``authors`` is only known for CVN publications; ORCID work summaries carry
    no author list, so it is empty there.
    """
    return {
        "title": title,
        "title_norm": normalize_title(title),
        "year": year,
        "month": month,
        "doi": normalize_doi(doi),
        "work_type": work_type,
        "authors": list(authors or []),
    }
