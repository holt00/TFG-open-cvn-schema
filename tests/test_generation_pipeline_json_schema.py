import json
import subprocess
import sys

from pathlib import Path

from cvn_codegen.conceptual_model_extractor import build_conceptual_model_inventory
from cvn_codegen.domain_model_generator import (
    build_domain_generation_result,
    build_semantic_policy_index,
    group_entries_by_cvn_item_code,
)
from cvn_codegen.json_schema_generator import (
    build_open_cvn_json_schema,
    write_json_schema,
)
from cvn_codegen.normalization_types import NormalizationResult
from cvn_codegen.semantic_policy import build_default_semantic_policy_bundle


def build_canonical_schema(normalization_result: NormalizationResult):
    bundle = build_default_semantic_policy_bundle()
    policy_index = build_semantic_policy_index(normalization_result, bundle)
    grouped_entries = group_entries_by_cvn_item_code(normalization_result.by_code)
    generation_result = build_domain_generation_result(
        policy_index=policy_index,
        grouped_entries=grouped_entries,
    )
    inventory = build_conceptual_model_inventory(generation_result)
    return build_open_cvn_json_schema(inventory)


def find_definition_by_source_reference(schema: dict, source_reference: str) -> dict:
    for definition in schema["$defs"].values():
        if definition.get("x-open-cvn-source-reference") == source_reference:
            return definition
    raise AssertionError(f"Definition not found for {source_reference}")


def test_json_schema_pipeline_generates_json_serializable_schema(
    canonical_normalization_result: NormalizationResult,
):
    schema = build_canonical_schema(canonical_normalization_result)

    encoded = json.dumps(schema, sort_keys=True)
    assert encoded


def test_json_schema_pipeline_declares_metadata(
    canonical_normalization_result: NormalizationResult,
):
    schema = build_canonical_schema(canonical_normalization_result)

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["$id"] == "https://open-cvn.local/schema/open-cvn.schema.json"
    assert schema["title"] == "Open CVN JSON Schema"
    assert schema["x-open-cvn-policy-name"]
    assert schema["x-open-cvn-policy-version"]
    assert schema["x-open-cvn-source-issue"] == "#46"


def test_json_schema_pipeline_contains_core_definitions(
    canonical_normalization_result: NormalizationResult,
):
    schema = build_canonical_schema(canonical_normalization_result)

    assert schema["$defs"]
    assert "core.curriculum" in schema["$defs"]
    assert "identity.person" in schema["$defs"]
    assert schema["properties"]["curriculum"]["properties"]["identity"]["type"] == "object"
    assert schema["properties"]["curriculum"]["properties"]["research"]["type"] == "array"


def test_json_schema_pipeline_uses_canonical_root_shape(
    canonical_normalization_result: NormalizationResult,
):
    schema = build_canonical_schema(canonical_normalization_result)

    assert schema["required"] == ["schema_version", "metadata", "curriculum"]
    assert "policy_name" not in schema["properties"]
    assert "policy_version" not in schema["properties"]
    assert schema["properties"]["metadata"]["required"] == ["language", "policy"]


def test_json_schema_pipeline_closes_eligible_enum_reference(
    canonical_normalization_result: NormalizationResult,
):
    schema = build_canonical_schema(canonical_normalization_result)
    sex_definition = find_definition_by_source_reference(schema, "CVN_SEX_A")

    assert sex_definition["x-open-cvn-vocabulary-kind"] == "enumeration"
    assert sex_definition["enum"]


def test_json_schema_pipeline_keeps_open_reference_without_enum(
    canonical_normalization_result: NormalizationResult,
):
    schema = build_canonical_schema(canonical_normalization_result)
    entity_type_definition = find_definition_by_source_reference(schema, "CVN_ENTITY_TYPE")

    assert entity_type_definition["x-open-cvn-enum-eligibility"] == "ineligible"
    assert "enum" not in entity_type_definition


def test_json_schema_pipeline_written_output_is_deterministic(
    canonical_normalization_result: NormalizationResult,
    tmp_path: Path,
):
    schema = build_canonical_schema(canonical_normalization_result)
    output_a = tmp_path / "open_cvn_a.schema.json"
    output_b = tmp_path / "open_cvn_b.schema.json"

    write_json_schema(output_a, schema)
    write_json_schema(output_b, schema)

    assert output_a.read_bytes() == output_b.read_bytes()


def test_json_schema_generator_cli_writes_output(tmp_path: Path):
    output_path = tmp_path / "open_cvn.schema.json"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "cvn_codegen.json_schema_generator",
            "--output-path",
            str(output_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Generated JSON Schema" in result.stdout
    assert output_path.exists()
    assert json.loads(output_path.read_text(encoding="utf-8"))["$schema"]
