from __future__ import annotations

import random
import re
import unicodedata
from typing import Any

from tfm_lakehouse.synthetic_cvn.seed import OrcidAffiliation, OrcidSeed, OrcidWork

GENERATOR_NAME = "tfm_lakehouse.synthetic_cvn"
GENERATOR_VERSION = "0.1.0"
ORCID_SNAPSHOT = "ORCID 2025 Public Data File (October 2025 snapshot)"

EDUCATION_DEGREE_TYPE = (
    "education.estudiosde1oy2ocicloyantiguoscicloslicenciadosdiplomadosingenierossuperioresingenierostecnicosarquitectos"
    "_020_010_010_000"
)
EDUCATION_DOCTORATE_TYPE = "education.doctorados_020_010_020_000"
PROFESSIONAL_PAST_TYPE = "professional_experience.cargosyactividadesdesempenadosconanterioridad_010_020_000_000"
PROFESSIONAL_CURRENT_TYPE = "professional_experience.professionalsituation_010_010_000_000"
RESEARCH_PUBLICATION_TYPE = "research.publicacionesdocumentoscientificosytecnicos_060_010_010_000"

_SPAIN = {"code": "724", "label": "España", "source": "ISO_3166"}
_ORCID_TYPE = {"code": "140", "label": "ORCID", "source": "CVN_SOURCE_C"}
_DOI_TYPE = {"code": "040", "label": "DOI", "source": "CVN_SOURCE_B"}
_SEXES = (
    {"code": "000", "label": "Hombre", "source": "CVN_SEX_A"},
    {"code": "010", "label": "Mujer", "source": "CVN_SEX_A"},
)
_CONTRACTS = (
    {"code": "160", "label": "Contrato laboral indefinido", "source": "CVN_SITUATION_A"},
    {"code": "170", "label": "Contrato laboral temporal", "source": "CVN_SITUATION_A"},
    {"code": "350", "label": "Funcionario/a", "source": "CVN_SITUATION_A"},
    {"code": "040", "label": "Becario/a (pre o posdoctoral, otros)", "source": "CVN_SITUATION_A"},
)
_DEDICATIONS = (
    {"code": "020", "label": "Tiempo completo", "source": "CVN_DEDICATION_A"},
    {"code": "030", "label": "Tiempo parcial", "source": "CVN_DEDICATION_A"},
)
_MANAGEMENT_UNIVERSITY = {"code": "000", "label": "Universitaria", "source": "CVN_MANAGEMENT_TYPE_A"}
_MANAGEMENT_OPI = {"code": "010", "label": "OPIs", "source": "CVN_MANAGEMENT_TYPE_A"}
_MANAGEMENT_OTHER = {"code": "OTHERS", "label": "Otros", "source": "CVN_MANAGEMENT_TYPE_A"}

# ORCID work type -> CVN_PUBLICATION_A (code, label). Types with no faithful
# equivalent (conference papers have their own CVN item, preprints, etc.) map
# to OTHERS and keep the ORCID type in ``tipo_de_produccion_otros``.
_PUBLICATION_TYPES = {
    "journal-article": ("020", "Artículo científico"),
    "book-chapter": ("004", "Capítulo de libro"),
    "book": ("032", "Libro o monografía científica"),
    "edited-book": ("208", "Edición científica"),
    "report": ("018", "Informe científico-técnico"),
    "data-set": ("211", "Set de datos"),
    "software": ("210", "Software de investigación"),
    "research-tool": ("210", "Software de investigación"),
    "magazine-article": ("203", "Artículo de divulgación"),
}

_FALLBACK_ROLES = ("Investigador/a", "Personal docente e investigador", "Técnico/a de investigación")
_FALLBACK_FUNCTIONS = (
    "Docencia e investigación",
    "Investigación",
    "Docencia y gestión académica",
    "Apoyo técnico a la investigación",
)

_DOCTORATE_MARKERS = ("phd", "ph.d", "dphil", "doctor")
_MASTER_MARKERS = ("master", "máster", "msc", "m.sc", "mba", "postgrad", "posgrado", "magíster", "magister")
_DEGREE_MARKERS = (
    "licenciad",
    "licenciatura",
    "grado",
    "graduad",
    "bachelor",
    "bsc",
    "b.sc",
    "ingenier",
    "diplomad",
    "arquitect",
    "degree",
)

_MAX_EMPLOYMENTS = 8
_MAX_EDUCATIONS = 5


def build_document(
    seed: OrcidSeed,
    *,
    document_id: str,
    run_seed: int,
    include_orcid: bool,
    rng: random.Random,
    max_publications: int = 40,
) -> tuple[dict[str, Any], str]:
    """Build one synthetic Open CVN document from an ORCID seed.

    Args:
        seed: Public ORCID fields the document is seeded with.
        document_id: Value of the CV's unique identifier field.
        run_seed: Seed of the generation run, recorded in the metadata.
        include_orcid: Whether the document carries the seed's ORCID iD.
            Documents without it keep a varied name and the affiliations.
        rng: The run's random generator.
        max_publications: Upper bound on publications per document.

    Returns:
        The document and the name variant applied (``"exact"`` when none).
    """
    given, family, name_variant = (
        (seed.given_names, seed.family_name, "exact") if include_orcid else vary_name(seed, rng)
    )
    identity = _build_identity(
        seed, given=given, family=family, document_id=document_id, include_orcid=include_orcid, rng=rng
    )
    document_date = identity["fecha_del_documento"]
    document = {
        "schema_version": "0.1.0",
        "metadata": {
            "language": "es",
            "policy": {"name": "default_cvn_semantic_policy", "version": "0.1.0"},
            "source": {
                "format": "synthetic_open_cvn_json",
                "synthetic": True,
                "generator_seed": run_seed,
                "orcid_snapshot": ORCID_SNAPSHOT,
            },
            "generator": {"name": GENERATOR_NAME, "version": GENERATOR_VERSION},
            "created_at": f"{document_date}T00:00:00Z",
        },
        "curriculum": {
            "identity": identity,
            "education": _build_education(seed),
            "research": _build_research(seed, given=given, family=family, rng=rng, max_publications=max_publications),
            "professional_experience": _build_professional(seed, rng),
            "achievements": [],
            "other": [],
        },
    }
    return document, name_variant


def vary_name(seed: OrcidSeed, rng: random.Random) -> tuple[str, str, str]:
    """Return a realistic variant of the seed's name and its label.

    The variants mirror how the same person is written differently across
    systems, which is what issue #98's name/affiliation fallback must match.
    """
    given, family = seed.given_names, seed.family_name
    variant = rng.choice(("accents_stripped", "given_initial", "family_upper", "first_surname_only"))
    if variant == "accents_stripped":
        varied = (_strip_accents(given), _strip_accents(family))
    elif variant == "given_initial":
        varied = (f"{given[0]}.", family)
    elif variant == "family_upper":
        varied = (given, family.upper())
    else:
        varied = (given, family.split()[0])
    if varied == (given, family):
        return given, family, "exact"
    return (*varied, variant)


def _build_identity(
    seed: OrcidSeed,
    *,
    given: str,
    family: str,
    document_id: str,
    include_orcid: bool,
    rng: random.Random,
) -> dict[str, Any]:
    birth = f"{rng.randint(1955, 1999)}-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}"
    document_date = f"{rng.randint(2024, 2026)}-{rng.randint(1, 8):02d}-{rng.randint(1, 28):02d}"
    email_slug = re.sub(r"[^a-z0-9]", "", _strip_accents(f"{given}{family}").lower()) or "cv"
    identity: dict[str, Any] = {
        "nombre": given,
        "apellidos": family,
        "sexo": dict(rng.choice(_SEXES)),
        "fecha_de_nacimiento": birth,
        "fecha_del_documento": document_date,
        # The 000 prefix is not a valid Spanish number range, so these can
        # never belong to a real person.
        "telefono_fijo": f"000{rng.randint(0, 999_999):06d}",
        "telefono_movil": f"000{rng.randint(0, 999_999):06d}",
        # RFC 2606 reserves .invalid for addresses that can never resolve.
        "correo_electronico": f"{email_slug}{rng.randint(1, 999)}@example.invalid",
        "identificador_unico_de_cv": document_id,
    }
    if include_orcid:
        identity["identificador_digital_de_autor"] = [seed.orcid_id]
        identity["tipo_de_identificador_digital_de_autor"] = [dict(_ORCID_TYPE)]
    return identity


def _build_education(seed: OrcidSeed) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    seen: set[tuple[str, str | None, str | None]] = set()
    for affiliation in seed.affiliations:
        if affiliation.kind != "education" or affiliation.role_title is None:
            continue
        role = affiliation.role_title
        lowered = role.lower()
        date = _flexible_date(affiliation.end_year or affiliation.start_year, affiliation.end_month)
        if date is None or any(marker in lowered for marker in _MASTER_MARKERS):
            continue
        key = (affiliation.organization, role, date["raw_value"])
        if key in seen:
            continue
        common: dict[str, Any] = {"entidad_de_titulacion": {"name": affiliation.organization}}
        if any(marker in lowered for marker in _DOCTORATE_MARKERS):
            if affiliation.city:
                common["ciudad_entidad_de_la_titulacion"] = affiliation.city
            if affiliation.country == "ES":
                common["pais_entidad_de_la_titulacion"] = dict(_SPAIN)
            programme = affiliation.department or role
            data = {
                **common,
                "programa_de_doctorado": {"source": "CVN_TITLE_C", "raw_value": programme, "label": programme},
                "fecha_de_titulacion": date,
                "fecha_de_obtencion": date,
                "doctorado_europeo_internacional": False,
                "mencion_de_calidad": False,
                "premio_extraordinario_del_doctorado": False,
                "titulo_homologado": False,
                # Required by the schema and not nullable, yet meaningless for a
                # non-homologated title: an empty date object is the honest value.
                "titulo_homologado_fecha_de_homologacion": {},
            }
            entry_type, code = EDUCATION_DOCTORATE_TYPE, "020.010.020.000"
        elif any(marker in lowered for marker in _DEGREE_MARKERS):
            # The degree entity names these fields differently from the doctorate one.
            if affiliation.city:
                common["ciudad_entidad_titulacion"] = affiliation.city
            if affiliation.country == "ES":
                common["pais_entidad_titulacion"] = dict(_SPAIN)
            data = {
                **common,
                "nombre_del_titulo": {"source": "CVN_TITLE_B", "raw_value": role, "label": role},
                "fecha_de_titulacion": date,
            }
            entry_type, code = EDUCATION_DEGREE_TYPE, "020.010.010.000"
        else:
            continue
        seen.add(key)
        entries.append(_entry("education", entry_type, code, len(entries) + 1, data))
        if len(entries) >= _MAX_EDUCATIONS:
            break
    return entries


def _build_professional(seed: OrcidSeed, rng: random.Random) -> list[dict[str, Any]]:
    employments = sorted(
        (a for a in seed.affiliations if a.kind == "employment" and a.start_year is not None),
        key=lambda a: (a.start_year or "", a.start_month or ""),
        reverse=True,
    )
    entries: list[dict[str, Any]] = []
    current_used = False
    for affiliation in employments:
        start = _flexible_date(affiliation.start_year, affiliation.start_month)
        if start is None:
            continue
        common = _employment_common(affiliation, rng)
        if affiliation.end_year is None:
            if current_used:
                continue
            current_used = True
            data = {
                **common,
                "fecha_de_inicio": start,
                "funciones_desempenadas": rng.choice(_FALLBACK_FUNCTIONS),
                "modalidad_de_contrato": dict(rng.choice(_CONTRACTS)),
                "regimen_de_dedicacion": dict(rng.choices(_DEDICATIONS, weights=(8, 2))[0]),
            }
            entries.append(_entry("professional_experience", PROFESSIONAL_CURRENT_TYPE, "010.010.000.000", 1, data))
        else:
            end = _flexible_date(affiliation.end_year, affiliation.end_month)
            if end is None:
                continue
            data = {
                **common,
                "fecha_de_inicio": start,
                "fecha_de_finalizacion": end,
                "duracion": _duration(affiliation),
            }
            entries.append(
                _entry("professional_experience", PROFESSIONAL_PAST_TYPE, "010.020.000.000", len(entries) + 1, data)
            )
        if len(entries) >= _MAX_EMPLOYMENTS:
            break
    return _renumber(entries)


def _employment_common(affiliation: OrcidAffiliation, rng: random.Random) -> dict[str, Any]:
    lowered = affiliation.organization.lower()
    if "univ" in lowered:
        management = _MANAGEMENT_UNIVERSITY
    elif "csic" in lowered or "consejo superior de investigaciones" in lowered:
        management = _MANAGEMENT_OPI
    else:
        management = _MANAGEMENT_OTHER
    common: dict[str, Any] = {
        "entidad_empleadora": {"name": affiliation.organization},
        "categoria_profesional_puesto_o_cargo": affiliation.role_title or rng.choice(_FALLBACK_ROLES),
        "ambito_actividad_de_direccion_y_o_gestion": dict(management),
    }
    if affiliation.city:
        common["ciudad_entidad_empleadora"] = affiliation.city
    if affiliation.country == "ES":
        common["pais_entidad_empleadora"] = dict(_SPAIN)
    return common


def _build_research(
    seed: OrcidSeed, *, given: str, family: str, rng: random.Random, max_publications: int
) -> list[dict[str, Any]]:
    if not seed.works:
        return []
    count = min(len(seed.works), rng.randint(3, max_publications))
    chosen_indexes = sorted(rng.sample(range(len(seed.works)), count))
    entries: list[dict[str, Any]] = []
    for index in chosen_indexes:
        work = seed.works[index]
        entries.append(
            _entry(
                "research",
                RESEARCH_PUBLICATION_TYPE,
                "060.010.010.000",
                len(entries) + 1,
                _publication_data(work, author=f"{family}, {given}"),
            )
        )
    return entries


def _publication_data(work: OrcidWork, *, author: str) -> dict[str, Any]:
    code_label = _PUBLICATION_TYPES.get(work.work_type or "")
    data: dict[str, Any] = {
        "tipo_de_produccion": (
            {"code": code_label[0], "label": code_label[1], "source": "CVN_PUBLICATION_A"}
            if code_label
            else {"code": "OTHERS", "label": "Otros", "source": "CVN_PUBLICATION_A"}
        ),
        "publicacion_titulo": work.title,
        "autores_as_p_o_de_firma_nombre": [author],
    }
    if code_label is None and work.work_type:
        data["tipo_de_produccion_otros"] = work.work_type
    date = _flexible_date(work.year, work.month)
    if date is not None:
        data["publicacion_fecha"] = date
    doi = _normalize_doi(work.doi)
    if doi is not None:
        data["identificador_de_publicacion_digital"] = [doi]
        data["tipo_de_identificador_de_publicacion_digital"] = [dict(_DOI_TYPE)]
    return data


def _entry(section: str, entry_type: str, code: str, number: int, data: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": f"{section}-{code.replace('.', '-')}-{number:03d}",
        "type": entry_type,
        "data": data,
        "trace": {"cvn_codes": [code]},
    }


def _renumber(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Give professional entries unique, ordered ids across both entity types."""
    for number, entry in enumerate(entries, start=1):
        code = entry["trace"]["cvn_codes"][0]
        entry["id"] = f"professional_experience-{code.replace('.', '-')}-{number:03d}"
    return entries


def _flexible_date(year: str | None, month: str | None = None) -> dict[str, str] | None:
    if year is None or not re.fullmatch(r"\d{4}", year):
        return None
    if month is not None and re.fullmatch(r"\d{1,2}", month) and 1 <= int(month) <= 12:
        month_text = f"{int(month):02d}"
        return {"raw_value": f"{year}-{month_text}", "year": year, "month": month_text}
    return {"raw_value": year, "year": year}


def _duration(affiliation: OrcidAffiliation) -> str:
    """Format the employment length as the CVN manual's ``YY.MM.DD``."""
    start_months = int(affiliation.start_year or 0) * 12 + int(affiliation.start_month or 1)
    end_months = int(affiliation.end_year or 0) * 12 + int(affiliation.end_month or 1)
    years, months = divmod(max(end_months - start_months, 0), 12)
    return f"{years:02d}.{months:02d}.00"


def _normalize_doi(doi: str | None) -> str | None:
    if doi is None:
        return None
    normalized = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:)", "", doi.strip(), flags=re.IGNORECASE)
    return normalized if normalized.startswith("10.") else None


def _strip_accents(text: str) -> str:
    return "".join(
        char for char in unicodedata.normalize("NFKD", text) if not unicodedata.combining(char)
    )
