import argparse
import json

from pathlib import Path
from typing import Any

from cvn_codegen.conceptual_model_extractor import (
    build_canonical_conceptual_model_inventory,
)
from cvn_codegen.conceptual_model_types import (
    ConceptualAttribute,
    ConceptualCardinalityKind,
    ConceptualEntity,
    ConceptualModelInventory,
    ConceptualPresenceKind,
    ConceptualValueKind,
    ConceptualVocabulary,
    ConceptualVocabularyKind,
)


OPEN_CVN_SCHEMA_ID = "https://open-cvn.local/schema/open-cvn.schema.json"
OPEN_CVN_SCHEMA_VERSION = "0.1.0"
JSON_SCHEMA_DRAFT_2020_12 = "https://json-schema.org/draft/2020-12/schema"


WRAPPER_DEFINITIONS: dict[str, dict[str, Any]] = {
    "FlexibleDateValue": {
        "additionalProperties": False,
        "properties": {
            "day": {"type": ["string", "null"]},
            "month": {"type": ["string", "null"]},
            "raw_value": {"type": ["string", "null"]},
            "year": {"type": ["string", "null"]},
        },
        "title": "FlexibleDateValue",
        "type": "object",
    },
    "OfficialIdValue": {
        "additionalProperties": False,
        "properties": {
            "dni": {"type": ["string", "null"]},
            "nie": {"type": ["string", "null"]},
            "others": {"type": ["string", "null"]},
            "passport": {"type": ["string", "null"]},
        },
        "title": "OfficialIdValue",
        "type": "object",
    },
    "EntityTypeValue": {
        "additionalProperties": False,
        "properties": {
            "code": {"type": ["string", "null"]},
            "label": {"type": ["string", "null"]},
            "others": {"type": ["string", "null"]},
        },
        "title": "EntityTypeValue",
        "type": "object",
    },
    "EntityNameValue": {
        "additionalProperties": False,
        "properties": {
            "name": {"type": ["string", "null"]},
            "others": {"type": ["string", "null"]},
        },
        "title": "EntityNameValue",
        "type": "object",
    },
}

WRAPPER_COMPONENT_BY_STRUCTURAL_TYPE = {
    "FlexibleDatesType": "FlexibleDateValue",
    "OfficialIdType": "OfficialIdValue",
    "EntityTypeType": "EntityTypeValue",
    "EntityNameType": "EntityNameValue",
}


def build_json_schema_metadata(
    inventory: ConceptualModelInventory,
) -> dict[str, Any]:
    return {
        "$id": OPEN_CVN_SCHEMA_ID,
        "$schema": JSON_SCHEMA_DRAFT_2020_12,
        "description": (
            "Generated Open CVN JSON Schema from the conceptual model inventory "
            "and domain-oriented Pydantic evidence. Root shape is provisional "
            "until issue #46 defines the canonical Open CVN JSON representation."
        ),
        "title": "Open CVN JSON Schema",
        "type": "object",
        "x-open-cvn-inventory-id": inventory.inventory_id,
        "x-open-cvn-policy-name": inventory.policy_name,
        "x-open-cvn-policy-version": inventory.policy_version,
        "x-open-cvn-schema-version": OPEN_CVN_SCHEMA_VERSION,
        "x-open-cvn-source-issue": "#45",
    }


def add_nullable(schema: dict[str, Any]) -> dict[str, Any]:
    schema = dict(schema)
    if "$ref" in schema:
        return {"anyOf": [schema, {"type": "null"}]}
    schema_type = schema.get("type")
    if isinstance(schema_type, str):
        schema["type"] = sorted({schema_type, "null"})
    elif isinstance(schema_type, list):
        schema["type"] = sorted({*schema_type, "null"})
    else:
        schema = {"anyOf": [schema, {"type": "null"}]}
    return schema


def build_trace_extensions(attribute: ConceptualAttribute) -> dict[str, Any]:
    extensions: dict[str, Any] = {
        "x-open-cvn-confidence": attribute.confidence.value,
        "x-open-cvn-domain-shape-kind": attribute.domain_shape_kind,
        "x-open-cvn-enum-eligibility": attribute.enum_eligibility,
    }
    if attribute.trace.cvn_codes:
        extensions["x-open-cvn-code"] = attribute.trace.cvn_codes[0]
    if attribute.trace.xml_paths:
        extensions["x-open-cvn-xml-paths"] = sorted(attribute.trace.xml_paths)
    source_reference = attribute.trace.manual_reference_table
    if source_reference is not None:
        extensions["x-open-cvn-source-reference"] = source_reference
    if attribute.vocabulary_id is not None:
        extensions["x-open-cvn-vocabulary-id"] = attribute.vocabulary_id
    return extensions


def get_wrapper_ref(attribute: ConceptualAttribute) -> str | None:
    for wrapper_type_name in sorted(attribute.wrapper_type_names):
        component_name = WRAPPER_COMPONENT_BY_STRUCTURAL_TYPE.get(
            wrapper_type_name,
            wrapper_type_name,
        )
        if component_name in WRAPPER_DEFINITIONS:
            return f"#/$defs/{component_name}"
    return None


def build_controlled_reference_schema(attribute: ConceptualAttribute) -> dict[str, Any]:
    code_schema: dict[str, Any]
    if attribute.vocabulary_id is not None:
        code_schema = {"$ref": f"#/$defs/{attribute.vocabulary_id}"}
    else:
        code_schema = {"type": ["string", "null"]}

    return {
        "additionalProperties": False,
        "properties": {
            "code": code_schema,
            "label": {"type": ["string", "null"]},
        },
        "type": "object",
    }


def build_base_schema_for_attribute(attribute: ConceptualAttribute) -> dict[str, Any]:
    if attribute.value_kind == ConceptualValueKind.TEXT:
        return {"type": "string"}
    if attribute.value_kind == ConceptualValueKind.DATE_LIKE:
        return {"type": "string"}
    if attribute.value_kind == ConceptualValueKind.DURATION_LIKE:
        return {"type": "string"}
    if attribute.value_kind == ConceptualValueKind.BOOLEAN:
        return {"type": "boolean"}
    if attribute.value_kind == ConceptualValueKind.DECIMAL_NUMBER:
        return {"type": "number"}
    if attribute.value_kind == ConceptualValueKind.CONTROLLED_REFERENCE:
        return build_controlled_reference_schema(attribute)
    if attribute.value_kind == ConceptualValueKind.VALUE_OBJECT:
        wrapper_ref = get_wrapper_ref(attribute)
        if wrapper_ref is not None:
            return {"$ref": wrapper_ref}
    return {
        "x-open-cvn-limitation": "unknown_conceptual_value_kind",
    }


def build_schema_for_attribute(attribute: ConceptualAttribute) -> dict[str, Any]:
    base_schema = build_base_schema_for_attribute(attribute)
    base_schema.update(build_trace_extensions(attribute))
    if attribute.source_label is not None:
        base_schema["description"] = attribute.source_label

    if attribute.presence != ConceptualPresenceKind.REQUIRED:
        base_schema = add_nullable(base_schema)

    if attribute.cardinality == ConceptualCardinalityKind.REPEATED:
        return {
            "items": base_schema,
            "type": "array",
            **build_trace_extensions(attribute),
        }

    return base_schema


def build_schema_for_entity(entity: ConceptualEntity) -> dict[str, Any]:
    properties = {
        attribute.name: build_schema_for_attribute(attribute)
        for attribute in sorted(entity.attributes, key=lambda item: item.name)
    }
    required = [
        attribute.name
        for attribute in sorted(entity.attributes, key=lambda item: item.name)
        if attribute.presence == ConceptualPresenceKind.REQUIRED
        and attribute.cardinality != ConceptualCardinalityKind.REPEATED
    ]
    schema: dict[str, Any] = {
        "additionalProperties": False,
        "description": entity.description,
        "properties": properties,
        "title": entity.name,
        "type": "object",
        "x-open-cvn-domain-area-id": entity.domain_area_id,
        "x-open-cvn-entity-id": entity.entity_id,
    }
    if entity.source_group_key is not None:
        schema["x-open-cvn-source-group-key"] = entity.source_group_key
    if entity.trace.cvn_codes:
        schema["x-open-cvn-codes"] = sorted(entity.trace.cvn_codes)
    if required:
        schema["required"] = required
    return schema


def build_schema_for_vocabulary(vocabulary: ConceptualVocabulary) -> dict[str, Any]:
    schema: dict[str, Any]
    if vocabulary.kind == ConceptualVocabularyKind.ENUMERATION and vocabulary.values:
        schema = {
            "enum": [code for code, _label in sorted(vocabulary.values)],
            "type": "string",
        }
    else:
        schema = {"type": "string"}
    schema.update(
        {
            "title": vocabulary.name,
            "x-open-cvn-enum-eligibility": vocabulary.enum_eligibility,
            "x-open-cvn-source-reference": vocabulary.source_reference,
            "x-open-cvn-vocabulary-id": vocabulary.vocabulary_id,
            "x-open-cvn-vocabulary-kind": vocabulary.kind.value,
        }
    )
    if vocabulary.item_count is not None:
        schema["x-open-cvn-item-count"] = vocabulary.item_count
    if vocabulary.values:
        schema["x-open-cvn-labels"] = {
            code: label
            for code, label in sorted(vocabulary.values)
        }
    return schema


def build_schema_definitions(
    inventory: ConceptualModelInventory,
) -> dict[str, dict[str, Any]]:
    definitions = {
        name: dict(schema)
        for name, schema in sorted(WRAPPER_DEFINITIONS.items())
    }
    for vocabulary in sorted(inventory.vocabularies, key=lambda item: item.vocabulary_id):
        definitions[vocabulary.vocabulary_id] = build_schema_for_vocabulary(vocabulary)
    for area in sorted(inventory.domain_areas, key=lambda item: item.area_id):
        for entity in sorted(area.entities, key=lambda item: item.entity_id):
            definitions[entity.entity_id] = build_schema_for_entity(entity)
    return definitions


def build_open_cvn_json_schema(
    inventory: ConceptualModelInventory,
) -> dict[str, Any]:
    schema = build_json_schema_metadata(inventory)
    schema.update(
        {
            "$defs": build_schema_definitions(inventory),
            "additionalProperties": False,
            "properties": {
                "curriculum": {"$ref": "#/$defs/core.curriculum"},
                "policy_name": {"const": inventory.policy_name, "type": "string"},
                "policy_version": {"const": inventory.policy_version, "type": "string"},
                "schema_version": {"const": OPEN_CVN_SCHEMA_VERSION, "type": "string"},
            },
            "required": [
                "schema_version",
                "policy_name",
                "policy_version",
                "curriculum",
            ],
        }
    )
    return schema


def write_json_schema(output_path: Path, schema: dict[str, Any]) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(schema, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output_path


def generate_open_cvn_json_schema(
    output_path: Path = Path("schemas/open_cvn.schema.json"),
) -> Path:
    inventory = build_canonical_conceptual_model_inventory()
    schema = build_open_cvn_json_schema(inventory)
    return write_json_schema(output_path=output_path, schema=schema)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate the canonical Open CVN JSON Schema artifact.",
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        default=Path("schemas/open_cvn.schema.json"),
        help="Path where the generated JSON Schema artifact will be written.",
    )
    args = parser.parse_args()

    written_path = generate_open_cvn_json_schema(output_path=args.output_path)
    print(f"Generated JSON Schema: {written_path}")


if __name__ == "__main__":
    main()
