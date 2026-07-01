import importlib
import sys
from pathlib import Path
from types import ModuleType
from cvn_codegen.domain_model_generator import (
    build_domain_generation_result,
    build_semantic_policy_index,
    group_entries_by_cvn_item_code,
    render_domain_generation_result,
)
from cvn_codegen.normalization import build_normalization_result
from cvn_codegen.semantic_policy import build_default_semantic_policy_bundle
def clear_generated_domain_imports(package_name: str) -> dict[str, ModuleType]:
    saved_modules = {
        module_name: module
        for module_name, module in sys.modules.items()
        if module_name == package_name or module_name.startswith(f"{package_name}.")
    }
    for module_name in tuple(saved_modules):
        sys.modules.pop(module_name, None)
    importlib.invalidate_caches()
    return saved_modules
def restore_generated_domain_imports(
    package_name: str,
    saved_modules: dict[str, ModuleType],
) -> None:
    for module_name in tuple(sys.modules):
        if module_name == package_name or module_name.startswith(f"{package_name}."):
            sys.modules.pop(module_name, None)
    sys.modules.update(saved_modules)
    importlib.invalidate_caches()
def write_temp_generated_package(rendered_files: dict[str, str], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for relative_path, content in rendered_files.items():
        (output_dir / relative_path).write_text(content, encoding="utf-8")
def test_generation_pipeline_e2e_from_canonical_sources_to_importable_domain_package(
    canonical_paths: dict[str, Path],
    tmp_path: Path,
):
    normalization_result = build_normalization_result(
        specification_manual_path=canonical_paths["specification_manual"],
        tree_model_path=canonical_paths["tree_model"],
        reference_tables_path=canonical_paths["reference_tables"],
        subtypes_path=canonical_paths["subtypes"],
        entity_path=canonical_paths["entity"],
        thesaurus_path=canonical_paths["thesaurus"],
        cvn_xsd_path=canonical_paths["cvn_xsd"],
        common_xsd_path=canonical_paths["common_xsd"],
    )
    bundle = build_default_semantic_policy_bundle()
    policy_index = build_semantic_policy_index(normalization_result, bundle)
    grouped_entries = group_entries_by_cvn_item_code(normalization_result.by_code)
    generation_result = build_domain_generation_result(
        policy_index=policy_index,
        grouped_entries=grouped_entries,
    )
    rendered_files = render_domain_generation_result(generation_result)
    output_dir = tmp_path / "generated_domain"
    write_temp_generated_package(rendered_files, output_dir)
    saved_modules = clear_generated_domain_imports("generated_domain")
    sys.path.insert(0, str(tmp_path))
    try:
        generated_package = importlib.import_module("generated_domain")
        enums_module = importlib.import_module("generated_domain.enums")
        manual_only_module = importlib.import_module("generated_domain.manual_only")
        representative_module_name = next(
            path.stem for path in sorted(output_dir.glob("cvn_item_*.py"))
        )
        representative_module = importlib.import_module(
            f"generated_domain.{representative_module_name}"
        )
        assert generated_package is not None
        assert enums_module is not None
        assert manual_only_module is not None
        assert representative_module is not None
        assert len(normalization_result.by_code) == 1457
        assert len(policy_index) == 1457
        assert len(generation_result.semantic_policies) == 1457
        assert len(rendered_files) == 105
    finally:
        sys.path.remove(str(tmp_path))
        restore_generated_domain_imports("generated_domain", saved_modules)