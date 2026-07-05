from cvn_codegen.conceptual_model_types import (
    ConceptualAttribute,
    ConceptualCardinalityKind,
    ConceptualConfidence,
    ConceptualDomainArea,
    ConceptualEntity,
    ConceptualModelInventory,
    ConceptualPresenceKind,
    ConceptualTrace,
    ConceptualValueKind,
)
from cvn_codegen.json_schema_generator import (
    JSON_SCHEMA_DRAFT_2020_12,
    build_open_cvn_json_schema,
    build_schema_for_attribute,
)


def build_trace() -> ConceptualTrace:
    return ConceptualTrace(
        cvn_codes=("000.010.000.030",),
        xml_paths=("CVN/CvnItem/Value",),
        source_files=("SpecificationManual.xml",),
        manual_reference_table="CVN_SEX_A",
    )


def build_attribute(
    *,
    value_kind: ConceptualValueKind = ConceptualValueKind.TEXT,
    presence: ConceptualPresenceKind = ConceptualPresenceKind.OPTIONAL,
    cardinality: ConceptualCardinalityKind = ConceptualCardinalityKind.SINGLE,
) -> ConceptualAttribute:
    return ConceptualAttribute(
        attribute_id="identity.person.sex",
        name="sex",
        source_label="Sexo",
        value_kind=value_kind,
        presence=presence,
        cardinality=cardinality,
        python_type_hint="str",
        domain_shape_kind="strict_enum_candidate",
        enum_eligibility="eligible",
        confidence=ConceptualConfidence.HIGH,
        trace=build_trace(),
        vocabulary_id="vocabularies.cvn_sex_a",
    )


def build_inventory() -> ConceptualModelInventory:
    root_entity = ConceptualEntity(
        entity_id="core.curriculum",
        name="Curriculum",
        domain_area_id="core",
        source_group_key=None,
        attributes=(),
        trace=ConceptualTrace(cvn_codes=(), xml_paths=(), source_files=()),
        description="Root conceptual entity.",
    )
    person_entity = ConceptualEntity(
        entity_id="identity.person",
        name="Person",
        domain_area_id="identity",
        source_group_key="000.010.000.000",
        attributes=(build_attribute(presence=ConceptualPresenceKind.REQUIRED),),
        trace=build_trace(),
        description="Person identity.",
    )
    return ConceptualModelInventory(
        inventory_id="test_inventory",
        source_issue="#43",
        policy_name="test_policy",
        policy_version="1.0.0",
        domain_areas=(
            ConceptualDomainArea(
                area_id="core",
                name="Core",
                entities=(root_entity,),
            ),
            ConceptualDomainArea(
                area_id="identity",
                name="Identity",
                entities=(person_entity,),
            ),
        ),
        relationships=(),
        vocabularies=(),
        limitations=(),
    )


def test_schema_metadata_declares_draft_2020_12():
    schema = build_open_cvn_json_schema(build_inventory())

    assert schema["$schema"] == JSON_SCHEMA_DRAFT_2020_12
    assert schema["$id"] == "https://open-cvn.local/schema/open-cvn.schema.json"
    assert schema["title"] == "Open CVN JSON Schema"
    assert schema["x-open-cvn-policy-name"] == "test_policy"
    assert schema["x-open-cvn-source-issue"] == "#46"


def test_schema_root_uses_canonical_open_cvn_format():
    schema = build_open_cvn_json_schema(build_inventory())

    assert schema["required"] == ["schema_version", "metadata", "curriculum"]
    assert set(schema["properties"]) == {
        "schema_version",
        "metadata",
        "curriculum",
        "extensions",
    }
    assert schema["properties"]["schema_version"]["const"] == "0.1.0"
    assert schema["properties"]["metadata"]["properties"]["policy"]["properties"]["name"] == {
        "const": "test_policy",
        "type": "string",
    }
    assert schema["properties"]["curriculum"]["properties"]["education"]["type"] == "array"


def test_optional_string_attribute_allows_null():
    schema = build_schema_for_attribute(build_attribute())

    assert schema["type"] == ["null", "string"]


def test_repeated_attribute_becomes_array():
    schema = build_schema_for_attribute(
        build_attribute(cardinality=ConceptualCardinalityKind.REPEATED)
    )

    assert schema["type"] == "array"
    assert schema["items"]["type"] == ["null", "string"]


def test_unknown_attribute_preserves_limitation_extension():
    schema = build_schema_for_attribute(
        build_attribute(value_kind=ConceptualValueKind.UNKNOWN)
    )

    assert schema["anyOf"][0]["x-open-cvn-limitation"] == "unknown_conceptual_value_kind"


def test_trace_extensions_are_emitted_for_attribute():
    schema = build_schema_for_attribute(build_attribute(presence=ConceptualPresenceKind.REQUIRED))

    assert schema["x-open-cvn-code"] == "000.010.000.030"
    assert schema["x-open-cvn-xml-paths"] == ["CVN/CvnItem/Value"]
    assert schema["x-open-cvn-source-reference"] == "CVN_SEX_A"


def test_controlled_reference_attribute_accepts_canonical_reference_fields():
    schema = build_schema_for_attribute(
        build_attribute(
            value_kind=ConceptualValueKind.CONTROLLED_REFERENCE,
            presence=ConceptualPresenceKind.REQUIRED,
        )
    )

    assert set(schema["properties"]) == {
        "code",
        "label",
        "raw_value",
        "reference_status",
        "source",
        "uri",
    }


def test_schema_generation_is_deterministic_for_same_inventory():
    inventory = build_inventory()

    assert build_open_cvn_json_schema(inventory) == build_open_cvn_json_schema(inventory)
