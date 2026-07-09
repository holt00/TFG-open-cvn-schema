from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from open_cvn_app.storage import CurriculumRepository, InvalidSelectionRule


@dataclass(frozen=True)
class CurriculumSectionView:
    name: str
    pointer: str
    value_kind: str
    entry_count: int | None


@dataclass(frozen=True)
class CurriculumEntryView:
    index: int
    pointer: str
    entry_id: str | None
    entry_type: str | None
    summary: str | None
    cvn_codes: tuple[str, ...]


def list_curriculum_sections(
    repository: CurriculumRepository,
    version: str,
) -> tuple[CurriculumSectionView, ...]:
    document = repository.materialize_version(version).document
    curriculum = _curriculum_mapping(document)
    sections: list[CurriculumSectionView] = []
    for name, value in curriculum.items():
        if isinstance(value, list):
            value_kind = "list"
            entry_count = len(value)
        elif isinstance(value, Mapping):
            value_kind = "object"
            entry_count = None
        else:
            value_kind = type(value).__name__
            entry_count = None
        sections.append(
            CurriculumSectionView(
                name=str(name),
                pointer=f"/curriculum/{_escape_json_pointer_token(str(name))}",
                value_kind=value_kind,
                entry_count=entry_count,
            )
        )
    return tuple(sections)


def list_curriculum_entries(
    repository: CurriculumRepository,
    version: str,
    section: str,
) -> tuple[CurriculumEntryView, ...]:
    section_name = _section_name_from_argument(section)
    document = repository.materialize_version(version).document
    curriculum = _curriculum_mapping(document)
    if section_name not in curriculum:
        raise InvalidSelectionRule(f"Curriculum section not found: {section_name}")
    entries = curriculum[section_name]
    if not isinstance(entries, list):
        raise InvalidSelectionRule(
            f"Curriculum section is not a repeated entry list: {section_name}"
        )
    escaped_section = _escape_json_pointer_token(section_name)
    return tuple(
        CurriculumEntryView(
            index=index,
            pointer=f"/curriculum/{escaped_section}/{index}",
            entry_id=_optional_string(entry, "id"),
            entry_type=_optional_string(entry, "type"),
            summary=_entry_summary(entry),
            cvn_codes=_cvn_codes(entry),
        )
        for index, entry in enumerate(entries)
    )


def _curriculum_mapping(document: Mapping[str, Any]) -> Mapping[str, Any]:
    curriculum = document.get("curriculum")
    if not isinstance(curriculum, Mapping):
        raise InvalidSelectionRule("Open CVN curriculum field must be an object.")
    return curriculum


def _section_name_from_argument(section: str) -> str:
    if section.startswith("/curriculum/"):
        parts = section.split("/")
        if len(parts) != 3:
            raise InvalidSelectionRule(
                f"Section selector must target one curriculum section: {section}"
            )
        return parts[2].replace("~1", "/").replace("~0", "~")
    if section.startswith("/"):
        raise InvalidSelectionRule(f"Section selector must target /curriculum: {section}")
    return section


def _optional_string(value: object, key: str) -> str | None:
    if not isinstance(value, Mapping):
        return None
    item = value.get(key)
    if item is None:
        return None
    return str(item)


def _entry_summary(value: object) -> str | None:
    if not isinstance(value, Mapping):
        return None
    data = value.get("data")
    if not isinstance(data, Mapping):
        return None
    parts: list[str] = []
    for key, item in _summary_items(data):
        if isinstance(item, str | int | float | bool):
            parts.append(f"{key}={item}")
        if len(parts) == 2:
            break
    return "; ".join(parts) if parts else None


def _summary_items(data: Mapping[str, Any]) -> tuple[tuple[str, Any], ...]:
    priority = ("title", "degree_name", "project_title", "name")
    items: list[tuple[str, Any]] = []
    seen: set[str] = set()
    for key in priority:
        if key in data:
            items.append((key, data[key]))
            seen.add(key)
    items.extend((str(key), value) for key, value in data.items() if key not in seen)
    return tuple(items)


def _cvn_codes(value: object) -> tuple[str, ...]:
    if not isinstance(value, Mapping):
        return ()
    trace = value.get("trace")
    if not isinstance(trace, Mapping):
        return ()
    codes = trace.get("cvn_codes")
    if not isinstance(codes, list):
        return ()
    return tuple(str(code) for code in codes)


def _escape_json_pointer_token(token: str) -> str:
    return token.replace("~", "~0").replace("/", "~1")
