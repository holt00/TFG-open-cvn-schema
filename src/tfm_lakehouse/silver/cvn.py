"""Validation and extraction of one synthetic/real Open CVN JSON document (issue #98, D4).

Three validation layers, then extraction:

1. ``validate_open_cvn_json`` (rule ``cvn_schema``): the project's JSON Schema
   plus Pydantic gate. Issue #97's landing check already ran it; it is repeated
   because bronze may come from another producer.
2. Entity-level schemas (rule ``cvn_entity_schema``): ``identity`` and every
   entry's ``data`` against their own ``$defs`` schema, which the free-form
   document schema does not enforce.
3. Business rules: declared ORCID iDs have a valid checksum
   (``cvn_orcid_checksum``), the name is present (``cvn_required_field``), and
   no date range ends before it starts (``cvn_date_order``).

Errors reject the record; the validator's warnings do not, they are returned
beside the extraction.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from open_cvn.parser_contract import CvnValidationStatus, validate_open_cvn_json
from tfm_lakehouse.cvn_validation import (
    ORCID_SOURCE_CODE,
    entity_schema_errors,
    orcid_identifier_errors,
)
from tfm_lakehouse.silver.normalize import parse_int
from tfm_lakehouse.silver.records import (
    KIND_EDUCATION,
    KIND_EMPLOYMENT,
    make_affiliation,
    make_person,
    make_publication,
)

RULE_PARSE = "cvn_json_parse"
RULE_SCHEMA = "cvn_schema"
RULE_ENTITY = "cvn_entity_schema"
RULE_ORCID = "cvn_orcid_checksum"
RULE_REQUIRED = "cvn_required_field"
RULE_DATE_ORDER = "cvn_date_order"

_DOI_TYPE_CODE = "040"
# CVN countries are numeric ISO 3166 codes, ORCID's are alpha-2. Only Spain is
# mapped (the one this project's data is filtered on); others stay unknown.
_COUNTRY_ALPHA2 = {"724": "ES"}


@dataclass
class CvnResult:
    """Outcome of processing one CVN document.

    Args:
        errors: ``(rule, message)`` pairs; any error rejects the record.
        warnings: Messages that do not reject it.
        person: The ``person_record`` fields, or None when rejected.
        affiliations: ``affiliation`` rows, empty when rejected.
        publications: ``publication`` rows, empty when rejected.
    """

    errors: list[tuple[str, str]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    person: dict[str, Any] | None = None
    affiliations: list[dict[str, Any]] = field(default_factory=list)
    publications: list[dict[str, Any]] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.errors


def process_cvn_document(source: str | Mapping[str, Any]) -> CvnResult:
    """Validate a CVN document and extract its silver rows.

    Args:
        source: The Open CVN document, as its JSON text or already parsed. The
            job passes the payload parsed from the bronze line, which is the
            document exactly as the producer wrote it.

    Returns:
        The result; extraction only runs when no layer reported an error.
    """
    document: Any = source
    if isinstance(source, str):
        try:
            document = json.loads(source)
        except ValueError as exc:
            return CvnResult(errors=[(RULE_PARSE, f"not valid JSON: {exc}")])
    if not isinstance(document, Mapping):
        return CvnResult(errors=[(RULE_PARSE, "the document is not a JSON object")])

    result = CvnResult()
    _layer_schema(document, result)
    _layer_entities(document, result)
    _layer_business_rules(document, result)
    if result.errors:
        return result

    curriculum = document["curriculum"]
    identity = curriculum["identity"]
    orcid_ids = _declared_orcid_ids(identity)
    if len(set(orcid_ids)) > 1:
        result.warnings.append(f"identity declares several ORCID iDs: {', '.join(sorted(set(orcid_ids)))}")
    result.person = make_person(
        given_names=_text(identity.get("nombre")),
        family_name=_text(identity.get("apellidos")),
        orcid_id=orcid_ids[0] if orcid_ids else None,
    )
    result.affiliations = _affiliations(curriculum)
    result.publications = _publications(curriculum)
    return result


def _layer_schema(document: Mapping[str, Any], result: CvnResult) -> None:
    parsed = validate_open_cvn_json(document)
    if parsed.validation_status in (CvnValidationStatus.INVALID, CvnValidationStatus.FAILED):
        for issue in parsed.errors:
            where = "/".join(issue.path) or "<root>"
            result.errors.append((RULE_SCHEMA, f"{issue.code.value} at {where}: {issue.details.get('message', issue.message)}"))
        if not parsed.errors:
            result.errors.append((RULE_SCHEMA, f"document status is {parsed.validation_status.value}"))
    for issue in parsed.warnings:
        result.warnings.append(f"{issue.code.value} at {'/'.join(issue.path) or '<root>'}: {issue.message}")


def _layer_entities(document: Mapping[str, Any], result: CvnResult) -> None:
    for message in entity_schema_errors(document):
        result.errors.append((RULE_ENTITY, message))


def _layer_business_rules(document: Mapping[str, Any], result: CvnResult) -> None:
    curriculum = document.get("curriculum")
    if not isinstance(curriculum, Mapping):
        return
    identity = curriculum.get("identity")
    if isinstance(identity, Mapping):
        for message in orcid_identifier_errors(identity):
            result.errors.append((RULE_ORCID, message))
        for field_name in ("nombre", "apellidos"):
            if _text(identity.get(field_name)) is None:
                result.errors.append((RULE_REQUIRED, f"identity/{field_name} is missing or empty"))
    for section in ("professional_experience", "education"):
        for index, data in _entries(curriculum, section):
            start = _year_month(data.get("fecha_de_inicio"))
            end = _year_month(data.get("fecha_de_finalizacion"))
            if start is not None and end is not None and (start[0], start[1] or 1) > (end[0], end[1] or 12):
                result.errors.append((RULE_DATE_ORDER, f"curriculum/{section}/{index}: ends {end} before it starts {start}"))


def _declared_orcid_ids(identity: Mapping[str, Any]) -> list[str]:
    identifiers = identity.get("identificador_digital_de_autor") or []
    types = identity.get("tipo_de_identificador_digital_de_autor") or []
    return [
        str(identifier)
        for identifier, identifier_type in zip(identifiers, types)
        if isinstance(identifier_type, Mapping) and identifier_type.get("code") == ORCID_SOURCE_CODE
    ]


def _affiliations(curriculum: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for _, data in _entries(curriculum, "professional_experience"):
        organization = _organization(data.get("entidad_empleadora"))
        if organization is None:
            continue
        start = _year_month(data.get("fecha_de_inicio"))
        end = _year_month(data.get("fecha_de_finalizacion"))
        rows.append(
            make_affiliation(
                kind=KIND_EMPLOYMENT,
                organization=organization,
                role=_text(data.get("categoria_profesional_puesto_o_cargo")),
                city=_text(data.get("ciudad_entidad_empleadora")),
                country=_country(data.get("pais_entidad_empleadora")),
                start_year=start[0] if start else None,
                start_month=start[1] if start else None,
                end_year=end[0] if end else None,
                end_month=end[1] if end else None,
            )
        )
    for _, data in _entries(curriculum, "education"):
        organization = _organization(data.get("entidad_de_titulacion"))
        if organization is None:
            continue
        # Degrees and doctorates name the same things differently.
        awarded = _year_month(data.get("fecha_de_titulacion"))
        rows.append(
            make_affiliation(
                kind=KIND_EDUCATION,
                organization=organization,
                role=_label(data.get("nombre_del_titulo")) or _label(data.get("programa_de_doctorado")),
                city=_text(data.get("ciudad_entidad_titulacion")) or _text(data.get("ciudad_entidad_de_la_titulacion")),
                country=_country(data.get("pais_entidad_titulacion")) or _country(data.get("pais_entidad_de_la_titulacion")),
                end_year=awarded[0] if awarded else None,
                end_month=awarded[1] if awarded else None,
            )
        )
    return rows


def _publications(curriculum: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for _, data in _entries(curriculum, "research"):
        title = _text(data.get("publicacion_titulo"))
        if title is None:
            continue
        published = _year_month(data.get("publicacion_fecha"))
        authors = data.get("autores_as_p_o_de_firma_nombre")
        rows.append(
            make_publication(
                title=title,
                year=published[0] if published else None,
                month=published[1] if published else None,
                doi=_doi(data),
                work_type=_label(data.get("tipo_de_produccion")),
                authors=[author for author in authors if isinstance(author, str)] if isinstance(authors, list) else [],
            )
        )
    return rows


def _doi(data: Mapping[str, Any]) -> str | None:
    identifiers = data.get("identificador_de_publicacion_digital") or []
    types = data.get("tipo_de_identificador_de_publicacion_digital") or []
    for identifier, identifier_type in zip(identifiers, types):
        if isinstance(identifier_type, Mapping) and identifier_type.get("code") == _DOI_TYPE_CODE:
            return str(identifier)
    return None


def _entries(curriculum: Mapping[str, Any], section: str) -> list[tuple[int, Mapping[str, Any]]]:
    entries = curriculum.get(section)
    if not isinstance(entries, list):
        return []
    found: list[tuple[int, Mapping[str, Any]]] = []
    for index, entry in enumerate(entries):
        data = entry.get("data") if isinstance(entry, Mapping) else None
        if isinstance(data, Mapping):
            found.append((index, data))
    return found


def _year_month(value: Any) -> tuple[int, int | None] | None:
    if not isinstance(value, Mapping):
        return None
    year = parse_int(value.get("year"))
    if year is None:
        return None
    return year, parse_int(value.get("month"))


def _organization(value: Any) -> str | None:
    if isinstance(value, Mapping):
        return _text(value.get("name"))
    return _text(value)


def _label(value: Any) -> str | None:
    if isinstance(value, Mapping):
        return _text(value.get("label")) or _text(value.get("raw_value"))
    return _text(value)


def _country(value: Any) -> str | None:
    if isinstance(value, Mapping):
        return _COUNTRY_ALPHA2.get(str(value.get("code")))
    return None


def _text(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = " ".join(value.split())
    return stripped or None
