from enum import Enum
from pathlib import Path

from cvn_codegen.auxiliary_sources.entity_metadata import load_entity_xml
from cvn_codegen.auxiliary_sources.reference_tables_metadata import (
    load_reference_tables_xml,
)
from cvn_codegen.auxiliary_sources.subtypes_metadata import load_subtypes_xml
from cvn_codegen.auxiliary_sources.thesaurus_metadata import load_thesaurus_xml
from cvn_codegen.domain_model_generator import (
    build_domain_generation_result,
    build_semantic_policy_index,
    group_entries_by_cvn_item_code,
)
from cvn_codegen.manual_metadata import extract_manual_entries, load_specification_manual
from cvn_codegen.normalization_types import NormalizationResult
from cvn_codegen.semantic_policy import build_default_semantic_policy_bundle
from cvn_codegen.tree_metadata import load_and_extract_tree_entries
from generated.cvn import aux_table


def test_all_manual_items_are_represented_in_normalization_policy_and_domain(
    canonical_paths: dict[str, Path],
    canonical_normalization_result: NormalizationResult,
):
    specification_manual = load_specification_manual(
        canonical_paths["specification_manual"]
    )
    manual_entries = extract_manual_entries(specification_manual)
    bundle = build_default_semantic_policy_bundle()
    policy_index = build_semantic_policy_index(canonical_normalization_result, bundle)
    generation_result = build_domain_generation_result(
        policy_index=policy_index,
        grouped_entries=group_entries_by_cvn_item_code(
            canonical_normalization_result.by_code
        ),
    )
    generated_codes = {entry.code for entry in generation_result.normalized_entries}

    assert len(specification_manual.manual.item) == 1456
    assert len(manual_entries) == 1456
    assert set(manual_entries) <= set(canonical_normalization_result.by_code)
    assert set(manual_entries) <= set(policy_index)
    assert set(manual_entries) <= generated_codes

    for code, manual_entry in manual_entries.items():
        normalized_entry = canonical_normalization_result.by_code[code]
        assert normalized_entry.manual == manual_entry


def test_all_tree_codes_are_represented_in_normalization_and_domain(
    canonical_paths: dict[str, Path],
    canonical_normalization_result: NormalizationResult,
):
    tree_entries = load_and_extract_tree_entries(canonical_paths["tree_model"])
    tree_codes = {entry.code for entry in tree_entries}
    bundle = build_default_semantic_policy_bundle()
    policy_index = build_semantic_policy_index(canonical_normalization_result, bundle)
    generation_result = build_domain_generation_result(
        policy_index=policy_index,
        grouped_entries=group_entries_by_cvn_item_code(
            canonical_normalization_result.by_code
        ),
    )
    generated_codes = {entry.code for entry in generation_result.normalized_entries}

    assert len(tree_entries) == 5051
    assert len(tree_codes) == 1430
    assert tree_codes <= set(canonical_normalization_result.by_code)
    assert tree_codes <= generated_codes


def test_auxiliary_xml_sources_are_loaded_without_losing_catalog_items(
    canonical_paths: dict[str, Path],
    canonical_auxiliary_bundle,
):
    reference_tables = load_reference_tables_xml(canonical_paths["reference_tables"])
    subtypes = load_subtypes_xml(canonical_paths["subtypes"])
    entity = load_entity_xml(canonical_paths["entity"])
    thesaurus = load_thesaurus_xml(canonical_paths["thesaurus"])

    assert len(canonical_auxiliary_bundle.reference_tables_by_name) == len(
        reference_tables.table
    )
    assert sum(
        metadata.item_count
        for metadata in canonical_auxiliary_bundle.reference_tables_by_name.values()
    ) == sum(len(table.item) for table in reference_tables.table)
    assert len(canonical_auxiliary_bundle.subtypes_by_source_code) == len(
        subtypes.subtype.item
    )
    assert canonical_auxiliary_bundle.entity_catalog is not None
    assert canonical_auxiliary_bundle.entity_catalog.item_count == len(entity.item)
    assert canonical_auxiliary_bundle.thesaurus_catalog is not None
    assert canonical_auxiliary_bundle.thesaurus_catalog.item_count == len(
        thesaurus.item
    )


def test_normalized_codes_have_semantic_policy_and_domain_generation_coverage(
    canonical_normalization_result: NormalizationResult,
):
    bundle = build_default_semantic_policy_bundle()
    policy_index = build_semantic_policy_index(canonical_normalization_result, bundle)
    generation_result = build_domain_generation_result(
        policy_index=policy_index,
        grouped_entries=group_entries_by_cvn_item_code(
            canonical_normalization_result.by_code
        ),
    )
    generated_codes = {entry.code for entry in generation_result.normalized_entries}

    assert len(canonical_normalization_result.by_code) == 1457
    assert set(canonical_normalization_result.by_code) == set(policy_index)
    assert set(canonical_normalization_result.by_code) == generated_codes


def test_core_aux_table_structural_enums_are_generated_and_importable():
    enum_classes = tuple(
        value
        for value in vars(aux_table).values()
        if isinstance(value, type) and issubclass(value, Enum) and value is not Enum
    )

    assert len(enum_classes) >= 30
    assert aux_table.CvnGenderType.VALUE_000.value == "000"
    assert aux_table.CvnGenderType.VALUE_010.value == "010"
