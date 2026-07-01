import importlib
import sys
from pathlib import Path
from types import ModuleType


from cvn_codegen.domain_model_generator import (
    build_domain_generation_result,
    build_semantic_policy_index,
    get_python_type_for_controlled_reference,
    group_entries_by_cvn_item_code,
    render_domain_generation_result,
)
from cvn_codegen.normalization_types import NormalizationResult
from cvn_codegen.semantic_policy import (
    DomainShapeKind,
    EnumEligibility,
    build_default_semantic_policy_bundle,
)
def build_canonical_generation_result(normalization_result: NormalizationResult):
    bundle = build_default_semantic_policy_bundle()
    policy_index = build_semantic_policy_index(normalization_result, bundle)
    grouped_entries = group_entries_by_cvn_item_code(normalization_result.by_code)
    return build_domain_generation_result(
        policy_index=policy_index,
        grouped_entries=grouped_entries,
    )

def clear_models_generated_imports() -> dict[str, ModuleType]:
    saved_modules = {
        module_name: module
        for module_name, module in sys.modules.items()
        if module_name == "models.cvn.generated"
        or module_name.startswith("models.cvn.generated.")
    }
    for module_name in tuple(saved_modules):
        sys.modules.pop(module_name, None)
    importlib.invalidate_caches()
    return saved_modules
def restore_models_generated_imports(saved_modules: dict[str, ModuleType]) -> None:
    for module_name in tuple(sys.modules):
        if module_name == "models.cvn.generated" or module_name.startswith(
            "models.cvn.generated."
        ):
            sys.modules.pop(module_name, None)
    sys.modules.update(saved_modules)
    importlib.invalidate_caches()

def write_rendered_files_to_temp_package(
    rendered_files: dict[str, str],
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for relative_path, content in rendered_files.items():
        (output_dir / relative_path).write_text(content, encoding="utf-8")

def collect_file_bytes(output_dir: Path) -> dict[str, bytes]:
    return {
        path.relative_to(output_dir).as_posix(): path.read_bytes()
        for path in sorted(output_dir.glob("*.py"))
    }

def test_generator_pipeline_builds_policy_index_for_all_normalized_entries(
    canonical_normalization_result: NormalizationResult,
):
    bundle = build_default_semantic_policy_bundle()
    policy_index = build_semantic_policy_index(canonical_normalization_result, bundle)
    assert tuple(policy_index) == tuple(sorted(canonical_normalization_result.by_code))
    assert len(policy_index) == 1457
def test_generator_pipeline_builds_domain_generation_units(
    canonical_normalization_result: NormalizationResult,
):
    result = build_canonical_generation_result(canonical_normalization_result)
    assert result.units
    assert result.normalized_entries
    assert result.semantic_policies
    assert len({entry.code for entry in result.normalized_entries}) == 1457
    assert len(result.semantic_policies) == 1457
    assert any(unit.module_name == "manual_only" for unit in result.units)
    assert any(unit.module_name.startswith("cvn_item_") for unit in result.units)
    assert set(policy.code for policy in result.semantic_policies) == set(
    canonical_normalization_result.by_code
    )

def test_generator_pipeline_emits_enum_spec_only_for_eligible_strict_enum(
    canonical_normalization_result: NormalizationResult,
):
    result = build_canonical_generation_result(canonical_normalization_result)
    enum_sources = {enum.source_reference for enum in result.enums}
    assert "CVN_SEX_A" in enum_sources
    assert "CVN_ENTITY_TYPE" not in enum_sources
    assert "CVN_KNOW_A" not in enum_sources
    assert "UNESCO_CODES" not in enum_sources
def test_generator_pipeline_maps_non_enum_controlled_reference_components(
    canonical_normalization_result: NormalizationResult,
):
    bundle = build_default_semantic_policy_bundle()
    policy_index = build_semantic_policy_index(canonical_normalization_result, bundle)
    expected_types_by_reference = {
        "CVN_KNOW_A": "SubtypeBackedValue",
        "ENTITY@Entity.xsd": "RegistryReference",
        "THESAURUS@thesaurus.xsd": "VocabularyReference",
        "UNESCO_CODES": "HierarchicalCodeReference",
        "CVN_AGENCY_C": "UnresolvedReference",
    }
    for raw_reference, expected_type in expected_types_by_reference.items():
        matching_policies = []
        for code, policy in policy_index.items():
            entry = canonical_normalization_result.by_code[code]
            if entry.manual is None:
                continue
            if entry.manual.manual_reference_table != raw_reference:
                continue
            matching_policies.append(policy)
        assert matching_policies
        assert get_python_type_for_controlled_reference(matching_policies[0]) == expected_type
def test_generator_pipeline_preserves_cvn_trace_in_field_specs(
    canonical_normalization_result: NormalizationResult,
):
    result = build_canonical_generation_result(canonical_normalization_result)
    field_specs = [
        field
        for unit in result.units
        for field in unit.fields
    ]
    assert field_specs
    assert all(field.trace["code"] == field.code for field in field_specs)
    assert all("domain_shape_kind" in field.trace for field in field_specs)
    assert all("enum_eligibility" in field.trace for field in field_specs)
def test_generator_pipeline_domain_shapes_match_semantic_policy(
    canonical_normalization_result: NormalizationResult,
):
    bundle = build_default_semantic_policy_bundle()
    policy_index = build_semantic_policy_index(canonical_normalization_result, bundle)
    sex_policy = policy_index["000.010.000.030"]
    assert sex_policy.domain_shape_kind == DomainShapeKind.STRICT_ENUM_CANDIDATE
    assert sex_policy.enum_eligibility == EnumEligibility.ELIGIBLE


def test_generator_pipeline_writes_importable_generated_package(
    canonical_normalization_result: NormalizationResult,
    domain_generation_output_dir: Path,
):
    result = build_canonical_generation_result(canonical_normalization_result)
    rendered_files = render_domain_generation_result(result)
    write_rendered_files_to_temp_package(rendered_files, domain_generation_output_dir)
    generated_root = domain_generation_output_dir.parent
    saved_modules = clear_models_generated_imports()
    sys.path.insert(0, str(generated_root))
    try:
        generated_package = importlib.import_module("generated_domain")
        enums_module = importlib.import_module("generated_domain.enums")
        manual_only_module = importlib.import_module("generated_domain.manual_only")
        assert generated_package is not None
        assert enums_module is not None
        assert manual_only_module is not None
    finally:
        sys.path.remove(str(generated_root))
        restore_models_generated_imports(saved_modules)
def test_generator_pipeline_imports_representative_cvn_item_module(
    canonical_normalization_result: NormalizationResult,
    domain_generation_output_dir: Path,
):
    result = build_canonical_generation_result(canonical_normalization_result)
    rendered_files = render_domain_generation_result(result)
    write_rendered_files_to_temp_package(rendered_files, domain_generation_output_dir)
    generated_root = domain_generation_output_dir.parent
    representative_module = next(
        path.stem
        for path in sorted(domain_generation_output_dir.glob("cvn_item_*.py"))
    )
    saved_modules = clear_models_generated_imports()
    sys.path.insert(0, str(generated_root))
    try:
        imported_module = importlib.import_module(
            f"generated_domain.{representative_module}"
        )
        assert imported_module is not None
    finally:
        sys.path.remove(str(generated_root))
        restore_models_generated_imports(saved_modules)
def test_generator_pipeline_field_trace_metadata_contains_required_keys(
    canonical_normalization_result: NormalizationResult,
):
    result = build_canonical_generation_result(canonical_normalization_result)
    field = next(
        field
        for unit in result.units
        for field in unit.fields
        if field.code == "000.010.000.030"
    )
    assert field.trace["code"] == "000.010.000.030"
    assert "xml_paths" in field.trace
    assert "domain_shape_kind" in field.trace
    assert "enum_eligibility" in field.trace

def test_generator_pipeline_rendered_output_is_deterministic(
    canonical_normalization_result: NormalizationResult,
):
    result_a = build_canonical_generation_result(canonical_normalization_result)
    result_b = build_canonical_generation_result(canonical_normalization_result)
    rendered_a = render_domain_generation_result(result_a)
    rendered_b = render_domain_generation_result(result_b)
    assert rendered_a.keys() == rendered_b.keys()
    assert rendered_a == rendered_b

def test_generator_pipeline_written_output_is_deterministic(
    canonical_normalization_result: NormalizationResult,
    tmp_path: Path,
):
    result = build_canonical_generation_result(canonical_normalization_result)
    rendered_files = render_domain_generation_result(result)
    output_a = tmp_path / "generated_a"
    output_b = tmp_path / "generated_b"
    write_rendered_files_to_temp_package(rendered_files, output_a)
    write_rendered_files_to_temp_package(rendered_files, output_b)
    assert collect_file_bytes(output_a) == collect_file_bytes(output_b)


def test_generator_pipeline_rendered_output_is_ascii_only(
    canonical_normalization_result: NormalizationResult,
):
    result = build_canonical_generation_result(canonical_normalization_result)
    rendered_files = render_domain_generation_result(result)
    non_ascii_files = [
        relative_path
        for relative_path, content in rendered_files.items()
        if not content.isascii()
    ]
    assert non_ascii_files == []