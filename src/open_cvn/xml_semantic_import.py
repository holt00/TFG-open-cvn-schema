from __future__ import annotations

from collections import Counter
from typing import Any
from xml.etree import ElementTree

from open_cvn.json_import import validate_open_cvn_json
from open_cvn.open_cvn_models import OPEN_CVN_SCHEMA_VERSION
from open_cvn.parser_contract import CvnSourceFormat, CvnValidationStatus
from open_cvn.xml_semantic_extraction import ExtractedXmlItem, extract_xml_semantic_items
from open_cvn.xml_semantic_mapping import XmlEntityMapping, load_xml_semantic_mapping_index
from open_cvn.xml_value_conversion import convert_xml_value


DEFAULT_POLICY_NAME = "default_cvn_semantic_policy"
DEFAULT_POLICY_VERSION = "0.1.0"


def import_cvn_xml_semantically(
    *,
    root: ElementTree.Element,
    source_identifier: str | None,
    source_path: str | None,
) -> dict[str, Any]:
    extraction = extract_xml_semantic_items(root)
    index = load_xml_semantic_mapping_index()
    counters: Counter[str] = Counter()
    curriculum: dict[str, Any] = {
        "identity": {},
        "education": [],
        "research": [],
        "professional_experience": [],
        "achievements": [],
        "other": [],
    }
    section_counts: Counter[str] = Counter()
    unmapped_codes: list[str] = []

    for item in extraction.items:
        counters["items_seen"] += 1
        entity = index.entity_for_group(item.code)
        if entity is None:
            counters["items_unmapped"] += 1
            unmapped_codes.append(item.code)
            _append_unmapped_item(curriculum, item)
            counters["fields_seen"] += len(item.fields)
            counters["fields_unmapped"] += len(item.fields)
            continue

        counters["items_mapped"] += 1
        data: dict[str, Any] = {}
        xml_paths = [item.xml_path]
        for field in item.fields:
            counters["fields_seen"] += 1
            field_mappings = index.fields_for_code(field.code, group_code=item.code)
            if not field_mappings:
                counters["fields_unmapped"] += 1
                if field.code not in unmapped_codes:
                    unmapped_codes.append(field.code)
                continue
            field_mapping = field_mappings[0]
            data[field_mapping.field_name] = convert_xml_value(field.raw_value, field_mapping)
            xml_paths.append(field.xml_path)
            counters["fields_mapped"] += 1

        if entity.domain_area_id == "identity":
            curriculum["identity"].update(data)
        else:
            section = _section_name(entity)
            section_counts[section] += 1
            curriculum[section].append(
                {
                    "id": _entry_id(section, item.code, section_counts[section]),
                    "type": entity.entity_id,
                    "data": data,
                    "trace": {
                        "cvn_codes": [item.code],
                        "xml_paths": xml_paths,
                        "confidence": "medium" if data else "low",
                    },
                }
            )

    mapping_status = "semantic_partial" if counters["items_mapped"] else "trace_only"
    document = {
        "schema_version": OPEN_CVN_SCHEMA_VERSION,
        "metadata": {
            "language": "es",
            "source": {
                "format": CvnSourceFormat.CVN_XML.value,
                "identifier": source_identifier,
                "path": source_path,
                "root": _local_name(root.tag),
            },
            "policy": {"name": DEFAULT_POLICY_NAME, "version": DEFAULT_POLICY_VERSION},
        },
        "curriculum": curriculum,
        "extensions": {
            "x-open-cvn.import": {
                "cvn_codes": list(extraction.cvn_codes),
                "xml_paths": list(extraction.xml_paths),
                "mapping_status": mapping_status,
            },
            "x-open-cvn.xml_import": {
                "mapping_status": mapping_status,
                "items_seen": counters["items_seen"],
                "items_mapped": counters["items_mapped"],
                "items_unmapped": counters["items_unmapped"],
                "fields_seen": counters["fields_seen"],
                "fields_mapped": counters["fields_mapped"],
                "fields_unmapped": counters["fields_unmapped"],
                "unmapped_codes": unmapped_codes,
            },
        },
    }
    validation = validate_open_cvn_json(document, source_identifier=source_identifier, source_path=source_path)
    if validation.validation_status in {CvnValidationStatus.INVALID, CvnValidationStatus.FAILED}:
        raise ValueError(
            "Semantic CVN XML import produced invalid Open CVN JSON: "
            f"{[issue.model_dump(mode='json') for issue in validation.errors]}"
        )
    return dict(validation.data or document)


def _append_unmapped_item(curriculum: dict[str, Any], item: ExtractedXmlItem) -> None:
    curriculum["other"].append(
        {
            "id": _entry_id("other", item.code, len(curriculum["other"]) + 1),
            "type": "other.unmapped_cvn_item",
            "data": {},
            "trace": {
                "cvn_codes": [item.code],
                "xml_paths": [item.xml_path, *(field.xml_path for field in item.fields)],
                "confidence": "low",
            },
            "extensions": {
                "x-open-cvn.xml_import": {
                    "raw_fields": [
                        {"code": field.code, "raw_value": field.raw_value, "xml_path": field.xml_path}
                        for field in item.fields
                    ]
                }
            },
        }
    )


def _section_name(entity: XmlEntityMapping) -> str:
    if entity.domain_area_id in {
        "education",
        "research",
        "professional_experience",
        "achievements",
        "other",
    }:
        return entity.domain_area_id
    return "other"


def _entry_id(section: str, code: str, number: int) -> str:
    return f"{section}-{code.replace('.', '-')}-{number:03d}"


def _local_name(tag: object) -> str:
    text = str(tag)
    if "}" in text:
        return text.rsplit("}", maxsplit=1)[1]
    return text
