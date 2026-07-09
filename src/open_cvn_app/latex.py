from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jinja2 import Environment, PackageLoader, StrictUndefined

from open_cvn_app.storage import CurriculumRepository


SECTION_TITLES = {
    "education": "Education",
    "research": "Research",
    "professional_experience": "Professional Experience",
    "achievements": "Achievements",
    "other": "Other",
}

SUMMARY_KEYS = ("title", "degree_name", "project_title", "name")


@dataclass(frozen=True)
class LatexField:
    label: str
    value: str


@dataclass(frozen=True)
class LatexEntry:
    entry_id: str | None
    entry_type: str | None
    summary: str | None
    fields: tuple[LatexField, ...]


@dataclass(frozen=True)
class LatexSection:
    name: str
    title: str
    entries: tuple[LatexEntry, ...]


@dataclass(frozen=True)
class LatexExportResult:
    output_path: Path
    version_name: str
    validation_status: str


def escape_latex(value: object) -> str:
    if value is None:
        return ""
    replacements = {
        "\\": r"\textbackslash{}",
        "{": r"\{",
        "}": r"\}",
        "$": r"\$",
        "&": r"\&",
        "#": r"\#",
        "%": r"\%",
        "_": r"\_",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in str(value))


def render_latex_document(document: Mapping[str, Any], *, version_name: str) -> str:
    template = _environment().get_template("basic_cv.tex.jinja")
    rendered = template.render(_template_context(document, version_name=version_name))
    return _normalize_final_newline(rendered)


def export_latex_document(
    repository: CurriculumRepository,
    *,
    version: str,
    output_path: str | Path,
) -> LatexExportResult:
    materialized = repository.materialize_version(version)
    path = Path(output_path)
    rendered = render_latex_document(
        materialized.document,
        version_name=materialized.version.name,
    )
    _write_text(path, rendered)
    return LatexExportResult(
        output_path=path,
        version_name=materialized.version.name,
        validation_status=materialized.validation_status,
    )


def _environment() -> Environment:
    environment = Environment(
        loader=PackageLoader("open_cvn_app", "templates/latex"),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
        undefined=StrictUndefined,
    )
    environment.filters["latex"] = escape_latex
    return environment


def _template_context(document: Mapping[str, Any], *, version_name: str) -> dict[str, Any]:
    metadata = _mapping(document.get("metadata"))
    curriculum = _mapping(document.get("curriculum"))
    versioning = _versioning_metadata(document)
    identity = _mapping(curriculum.get("identity"))
    display_name = _display_name(identity)
    return {
        "title": display_name or "Open CVN Curriculum",
        "schema_version": str(document.get("schema_version", "")),
        "language": str(metadata.get("language", "")),
        "version_name": str(versioning.get("version_name", version_name)),
        "version_kind": str(versioning.get("version_kind", "unknown")),
        "identity_fields": _identity_fields(identity),
        "sections": _sections(curriculum),
    }


def _versioning_metadata(document: Mapping[str, Any]) -> Mapping[str, Any]:
    extensions = _mapping(document.get("extensions"))
    return _mapping(extensions.get("x-open-cvn.versioning"))


def _display_name(identity: Mapping[str, Any]) -> str | None:
    given_name = identity.get("given_name")
    family_name = identity.get("family_name")
    parts = [str(part) for part in (given_name, family_name) if part]
    if parts:
        return " ".join(parts)
    name = identity.get("name")
    return str(name) if name else None


def _identity_fields(identity: Mapping[str, Any]) -> tuple[LatexField, ...]:
    return tuple(
        LatexField(label=_label(key), value=_format_value(value))
        for key, value in identity.items()
        if key != "trace" and _format_value(value)
    )


def _sections(curriculum: Mapping[str, Any]) -> tuple[LatexSection, ...]:
    sections: list[LatexSection] = []
    for name in ("education", "research", "professional_experience", "achievements", "other"):
        value = curriculum.get(name)
        if not isinstance(value, list) or not value:
            continue
        entries = tuple(_entry(entry) for entry in value)
        sections.append(
            LatexSection(
                name=name,
                title=SECTION_TITLES[name],
                entries=entries,
            )
        )
    return tuple(sections)


def _entry(value: object) -> LatexEntry:
    if not isinstance(value, Mapping):
        return LatexEntry(entry_id=None, entry_type=None, summary=_format_value(value), fields=())
    data = _mapping(value.get("data"))
    return LatexEntry(
        entry_id=_optional_string(value.get("id")),
        entry_type=_optional_string(value.get("type")),
        summary=_entry_summary(data),
        fields=tuple(
            LatexField(label=_label(key), value=_format_value(item))
            for key, item in data.items()
            if _format_value(item)
        ),
    )


def _entry_summary(data: Mapping[str, Any]) -> str | None:
    for key in SUMMARY_KEYS:
        value = data.get(key)
        if isinstance(value, str | int | float | bool):
            return str(value)
    for value in data.values():
        if isinstance(value, str | int | float | bool):
            return str(value)
    return None


def _format_value(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, str | int | float | bool):
        return str(value)
    if isinstance(value, Mapping | Sequence) and not isinstance(value, str | bytes | bytearray):
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(", ", ": "))
    return str(value)


def _label(value: object) -> str:
    return str(value).replace("_", " ").title()


def _mapping(value: object) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}


def _optional_string(value: object) -> str | None:
    return str(value) if value is not None else None


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_normalize_final_newline(content), encoding="utf-8")


def _normalize_final_newline(content: str) -> str:
    return f"{content.rstrip(chr(10))}\n"
