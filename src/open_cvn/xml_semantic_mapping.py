from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True)
class XmlFieldMapping:
    code: str
    field_name: str
    entity_id: str
    domain_area_id: str
    source_group_key: str
    domain_shape_kind: str | None
    vocabulary_kind: str | None
    source_reference: str | None
    schema: Mapping[str, Any]


@dataclass(frozen=True)
class XmlEntityMapping:
    entity_id: str
    domain_area_id: str
    source_group_key: str
    fields: tuple[XmlFieldMapping, ...]


@dataclass(frozen=True)
class XmlSemanticMappingIndex:
    entities_by_group_code: Mapping[str, XmlEntityMapping]
    fields_by_code: Mapping[str, tuple[XmlFieldMapping, ...]]
    fields_by_group_code: Mapping[str, tuple[XmlFieldMapping, ...]]

    def entity_for_group(self, code: str) -> XmlEntityMapping | None:
        entity = self.entities_by_group_code.get(code)
        if entity is not None:
            return entity
        if code.startswith("000."):
            return self.entities_by_group_code.get("__no_cvn_item__")
        return None

    def fields_for_code(self, code: str, *, group_code: str | None = None) -> tuple[XmlFieldMapping, ...]:
        fields = self.fields_by_code.get(code, ())
        if group_code is None:
            return fields
        if group_code.startswith("000."):
            scoped = tuple(field for field in fields if field.source_group_key == "__no_cvn_item__")
            if scoped:
                return scoped
        scoped = tuple(field for field in fields if field.source_group_key == group_code)
        return scoped or fields


@lru_cache(maxsize=1)
def load_xml_semantic_mapping_index() -> XmlSemanticMappingIndex:
    schema = json.loads(_schema_path().read_text(encoding="utf-8"))
    defs = schema.get("$defs", {})
    if not isinstance(defs, Mapping):
        return XmlSemanticMappingIndex({}, {}, {})

    entities_by_group_code: dict[str, XmlEntityMapping] = {}
    fields_by_code: dict[str, list[XmlFieldMapping]] = {}
    fields_by_group_code: dict[str, list[XmlFieldMapping]] = {}

    for definition in defs.values():
        if not isinstance(definition, Mapping):
            continue
        entity_id = _string_or_none(definition.get("x-open-cvn-entity-id"))
        domain_area_id = _string_or_none(definition.get("x-open-cvn-domain-area-id"))
        source_group_key = _string_or_none(definition.get("x-open-cvn-source-group-key"))
        if entity_id is None or domain_area_id is None or source_group_key is None:
            continue

        properties = definition.get("properties", {})
        entity_fields: list[XmlFieldMapping] = []
        if isinstance(properties, Mapping):
            for field_name, field_schema in properties.items():
                if not isinstance(field_name, str) or not isinstance(field_schema, Mapping):
                    continue
                field_code = _string_or_none(field_schema.get("x-open-cvn-code"))
                if field_code is None:
                    continue
                field_mapping = XmlFieldMapping(
                    code=field_code,
                    field_name=field_name,
                    entity_id=entity_id,
                    domain_area_id=domain_area_id,
                    source_group_key=source_group_key,
                    domain_shape_kind=_string_or_none(field_schema.get("x-open-cvn-domain-shape-kind")),
                    vocabulary_kind=_string_or_none(field_schema.get("x-open-cvn-vocabulary-kind")),
                    source_reference=_string_or_none(field_schema.get("x-open-cvn-source-reference")),
                    schema=field_schema,
                )
                entity_fields.append(field_mapping)
                fields_by_code.setdefault(field_code, []).append(field_mapping)
                fields_by_group_code.setdefault(source_group_key, []).append(field_mapping)

        entities_by_group_code[source_group_key] = XmlEntityMapping(
            entity_id=entity_id,
            domain_area_id=domain_area_id,
            source_group_key=source_group_key,
            fields=tuple(entity_fields),
        )

    return XmlSemanticMappingIndex(
        entities_by_group_code=entities_by_group_code,
        fields_by_code={code: tuple(fields) for code, fields in fields_by_code.items()},
        fields_by_group_code={code: tuple(fields) for code, fields in fields_by_group_code.items()},
    )


def _schema_path() -> Path:
    return Path(__file__).resolve().parents[2] / "schemas" / "open_cvn.schema.json"


def _string_or_none(value: object) -> str | None:
    if isinstance(value, str):
        return value
    return None
