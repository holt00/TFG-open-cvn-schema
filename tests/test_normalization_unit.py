from pathlib import Path

import pytest as pt

from typing import cast
from cvn_codegen.normalization_types import ManualCodeEntry, TreePathEntry


from cvn_codegen.manual_metadata import (
    extract_manual_entries,
    load_specification_manual,
)
from cvn_codegen.normalization import (
    build_normalization_result,
    build_normalized_code,
    build_normalized_code_index,
    collect_all_code,
)
from cvn_codegen.normalization_types import (
    ManualCodeEntry,
    NormalizedCodeEntry,
    NormalizationResult,
)
from cvn_codegen.tree_metadata import (
    index_tree_entries_by_code,
    load_and_extract_tree_entries,
)
from cvn_codegen.auxiliary_sources.bundle import build_auxiliary_source_bundle
from cvn_codegen.normalization_types import (
    ReferenceSourceFamily,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
SPECIFICATION_MANUAL_XML = (
    REPO_ROOT
    / "docs"
    / "CvnXML_v1.4.3_2.1_17012025"
    / "XML"
    / "SpecificationManual.xml"
)
TREE_MODEL_XML = (
    REPO_ROOT / "docs" / "CvnXML_v1.4.3_2.1_17012025" / "XML" / "CVNTreeModel.xml"
)

REFERENCE_TABLES_XML = (
    REPO_ROOT / "docs" / "CvnXML_v1.4.3_2.1_17012025" / "XML" / "ReferenceTables.xml"
)
SUBTYPES_XML = (
    REPO_ROOT / "docs" / "CvnXML_v1.4.3_2.1_17012025" / "XML" / "Subtype_Spa.xml"
)
ENTITY_XML = (
    REPO_ROOT / "docs" / "CvnXML_v1.4.3_2.1_17012025" / "XML" / "Entity.xml"
)
THESAURUS_XML = (
    REPO_ROOT / "docs" / "CvnXML_v1.4.3_2.1_17012025" / "XML" / "Thesaurus.xml"
)

def test_collect_all_code_raises_for_invalid_manual_entries_type():
    # Arrange
    invalid_manual_entries = cast(dict[str, ManualCodeEntry], [])
    tree_entries_by_code: dict[str, tuple] = {}
    # Act / Assert
    with pt.raises(ValueError):
        collect_all_code(invalid_manual_entries, tree_entries_by_code)
def test_collect_all_code_raises_for_invalid_tree_entries_type():
    # Arrange
    manual_entries_by_code: dict[str, ManualCodeEntry] = {}
    invalid_tree_entries = cast(dict[str, tuple[TreePathEntry, ...]], [])
    # Act / Assert
    with pt.raises(ValueError):
        collect_all_code(manual_entries_by_code, invalid_tree_entries)


def test_collect_all_code_returns_sorted_union_of_codes():
    # Arrange
    manual_entries_by_code = {
        "000.010.000.030": ManualCodeEntry(
            code="000.010.000.030",
            manual_name="Sexo",
            manual_short_name="Sexo",
            manual_type="Alphanumeric",
            manual_obligatory=True,
            manual_multiplicity=False,
            manual_reference_table="CVN_SEX_A",
        ),
        "000.010.000.040": ManualCodeEntry(
            code="000.010.000.040",
            manual_name="Nacionalidad",
            manual_short_name="Nacionalidad",
            manual_type="Alphanumeric",
            manual_obligatory=None,
            manual_multiplicity=False,
            manual_reference_table="ISO_3166",
        ),
    }
    tree_entries_by_code = {
        "000.010.000.030": (),
        "000.010.000.050": (),
    }

    # Act
    all_codes = collect_all_code(manual_entries_by_code, tree_entries_by_code)

    # Assert
    assert all_codes == (
        "000.010.000.030",
        "000.010.000.040",
        "000.010.000.050",
    ), f"Unexpected all-codes result: {all_codes}."


def test_build_normalized_code_raises_for_empty_code():
    # Arrange
    manual_entries_by_code: dict[str, ManualCodeEntry] = {}
    tree_entries_by_code: dict[str, tuple] = {}

    # Act / Assert
    with pt.raises(ValueError) as exc_info:
        build_normalized_code("   ", manual_entries_by_code, tree_entries_by_code)

    assert "empty" in str(exc_info.value).lower()


def test_build_normalized_code_returns_manual_only_entry():
    # Arrange
    manual_entries_by_code = {
        "000.010.000.030": ManualCodeEntry(
            code="000.010.000.030",
            manual_name="Sexo",
            manual_short_name="Sexo",
            manual_type="Alphanumeric",
            manual_obligatory=True,
            manual_multiplicity=False,
            manual_reference_table="CVN_SEX_A",
        )
    }
    tree_entries_by_code: dict[str, tuple] = {}

    # Act
    normalized_entry = build_normalized_code(
        "000.010.000.030",
        manual_entries_by_code,
        tree_entries_by_code,
    )

    # Assert
    assert isinstance(normalized_entry, NormalizedCodeEntry)
    assert normalized_entry.code == "000.010.000.030"
    assert normalized_entry.manual is not None
    assert normalized_entry.tree_paths == ()
    assert normalized_entry.source_files == ("SpecificationManual.xml",)


def test_build_normalized_code_returns_combined_entry_for_known_code():
    # Arrange
    specification_manual = load_specification_manual(SPECIFICATION_MANUAL_XML)
    manual_entries_by_code = extract_manual_entries(specification_manual)
    tree_entries = load_and_extract_tree_entries(TREE_MODEL_XML)
    tree_entries_by_code = index_tree_entries_by_code(tree_entries)

    # Act
    normalized_entry = build_normalized_code(
        "000.010.000.030",
        manual_entries_by_code,
        tree_entries_by_code,
    )

    # Assert
    assert normalized_entry.code == "000.010.000.030"
    assert normalized_entry.manual is not None
    assert normalized_entry.manual.manual_name == "Sexo"
    assert normalized_entry.tree_paths
    assert set(normalized_entry.source_files) == {
        "SpecificationManual.xml",
        "CVNTreeModel.xml",
    }


def test_build_normalized_code_index_contains_known_combined_code():
    # Arrange
    specification_manual = load_specification_manual(SPECIFICATION_MANUAL_XML)
    manual_entries_by_code = extract_manual_entries(specification_manual)
    tree_entries = load_and_extract_tree_entries(TREE_MODEL_XML)
    tree_entries_by_code = index_tree_entries_by_code(tree_entries)

    # Act
    normalized_entries_by_code = build_normalized_code_index(
        manual_entries_by_code,
        tree_entries_by_code,
    )

    # Assert
    assert isinstance(normalized_entries_by_code, dict)
    assert "000.010.000.030" in normalized_entries_by_code
    assert isinstance(
        normalized_entries_by_code["000.010.000.030"],
        NormalizedCodeEntry,
    )


def test_build_normalization_result_returns_expected_shape():
    # Arrange
    specification_manual_path = SPECIFICATION_MANUAL_XML
    tree_model_path = TREE_MODEL_XML

    # Act
    normalization_result = build_normalization_result(
        specification_manual_path,
        tree_model_path,
    )

    # Assert
    assert isinstance(normalization_result, NormalizationResult)
    assert isinstance(normalization_result.by_code, dict)
    assert isinstance(normalization_result.by_xml_path, dict)
    assert isinstance(normalization_result.manual_only_codes, tuple)
    assert isinstance(normalization_result.tree_only_codes, tuple)
    assert isinstance(normalization_result.mismatches, tuple)
    assert len(normalization_result.mismatches) >= 2


def test_build_normalization_result_contains_known_code_and_expected_overlap_examples():
    # Arrange
    specification_manual_path = SPECIFICATION_MANUAL_XML
    tree_model_path = TREE_MODEL_XML

    # Act
    normalization_result = build_normalization_result(
        specification_manual_path,
        tree_model_path,
    )

    # Assert
    assert "000.010.000.030" in normalization_result.by_code
    assert "030.010.000.250" in normalization_result.tree_only_codes, (
        "Expected code '030.010.000.250' to be present among tree-only codes."
    )
    assert any(
        mismatch.code == "030.010.000.250"
        for mismatch in normalization_result.mismatches
    ), "Expected mismatch collection to include tree-only code '030.010.000.250'."
    assert any(
        mismatch.code == "060.030.070.220"
        for mismatch in normalization_result.mismatches
    ), "Expected mismatch collection to include known unexpected <Type> case '060.030.070.220'."


def test_build_normalization_result_matches_documented_baseline_counts():
    # Arrange
    specification_manual_path = SPECIFICATION_MANUAL_XML
    tree_model_path = TREE_MODEL_XML

    # Act
    normalization_result = build_normalization_result(
        specification_manual_path,
        tree_model_path,
    )

    # Assert
    assert len(normalization_result.by_code) == 1457, (
        f"Expected 1457 total normalized codes, but got {len(normalization_result.by_code)}."
    )
    assert len(normalization_result.manual_only_codes) == 27, (
        f"Expected 27 manual-only codes, but got {len(normalization_result.manual_only_codes)}."
    )
    assert len(normalization_result.tree_only_codes) == 1, (
        f"Expected 1 tree-only code, but got {len(normalization_result.tree_only_codes)}."
    )
    overlap_count = (
        len(normalization_result.by_code)
        - len(normalization_result.manual_only_codes)
        - len(normalization_result.tree_only_codes)
    )
    assert overlap_count == 1429, (
        f"Expected 1429 overlapping codes, but got {overlap_count}."
    )


def test_build_normalized_code_sets_reference_resolution_when_bundle_present():
    # Arrange
    specification_manual = load_specification_manual(SPECIFICATION_MANUAL_XML)
    manual_entries_by_code = extract_manual_entries(specification_manual)
    tree_entries = load_and_extract_tree_entries(TREE_MODEL_XML)
    tree_entries_by_code = index_tree_entries_by_code(tree_entries)
    auxiliary_bundle = build_auxiliary_source_bundle(
        reference_tables_path=REFERENCE_TABLES_XML,
        subtypes_path=SUBTYPES_XML,
        entity_path=ENTITY_XML,
        thesaurus_path=THESAURUS_XML,
    )
    # Act
    normalized_entry = build_normalized_code(
        "000.010.000.030",
        manual_entries_by_code,
        tree_entries_by_code,
        auxiliary_bundle=auxiliary_bundle,
    )
    # Assert
    assert normalized_entry.reference_resolution is not None
    assert (
        normalized_entry.reference_resolution.source_family
        == ReferenceSourceFamily.REFERENCE_TABLE
    )
def test_build_normalized_code_sets_tree_only_source_files_correctly():
    # Arrange
    specification_manual = load_specification_manual(SPECIFICATION_MANUAL_XML)
    manual_entries_by_code = extract_manual_entries(specification_manual)
    tree_entries = load_and_extract_tree_entries(TREE_MODEL_XML)
    tree_entries_by_code = index_tree_entries_by_code(tree_entries)
    # Act
    normalized_entry = build_normalized_code(
        "030.010.000.250",
        manual_entries_by_code,
        tree_entries_by_code,
    )
    # Assert
    assert normalized_entry.manual is None
    assert normalized_entry.tree_paths
    assert normalized_entry.source_files == ("CVNTreeModel.xml",)
def test_build_normalization_result_preserves_documented_baseline_with_auxiliary_paths():
    # Arrange / Act
    normalization_result = build_normalization_result(
        SPECIFICATION_MANUAL_XML,
        TREE_MODEL_XML,
        reference_tables_path=REFERENCE_TABLES_XML,
        subtypes_path=SUBTYPES_XML,
        entity_path=ENTITY_XML,
        thesaurus_path=THESAURUS_XML,
    )
    # Assert
    assert len(normalization_result.by_code) == 1457
    assert len(normalization_result.manual_only_codes) == 27
    assert len(normalization_result.tree_only_codes) == 1
    overlap_count = (
        len(normalization_result.by_code)
        - len(normalization_result.manual_only_codes)
        - len(normalization_result.tree_only_codes)
    )
    assert overlap_count == 1429
def test_build_normalization_result_includes_auxiliary_resolution_for_known_code():
    # Arrange / Act
    normalization_result = build_normalization_result(
        SPECIFICATION_MANUAL_XML,
        TREE_MODEL_XML,
        reference_tables_path=REFERENCE_TABLES_XML,
        subtypes_path=SUBTYPES_XML,
        entity_path=ENTITY_XML,
        thesaurus_path=THESAURUS_XML,
    )
    # Assert
    normalized_entry = normalization_result.by_code["000.010.000.030"]
    assert normalized_entry.reference_resolution is not None
    assert normalized_entry.reference_resolution.resolved_name == "CVN_SEX_A"
    assert (
        normalized_entry.reference_resolution.source_family
        == ReferenceSourceFamily.REFERENCE_TABLE
    )

def test_build_normalization_result_includes_entity_side_package_resolution_for_known_code():
    # Arrange / Act
    normalization_result = build_normalization_result(
        SPECIFICATION_MANUAL_XML,
        TREE_MODEL_XML,
        reference_tables_path=REFERENCE_TABLES_XML,
        subtypes_path=SUBTYPES_XML,
        entity_path=ENTITY_XML,
        thesaurus_path=THESAURUS_XML,
    )
    # Assert
    entity_entries = [
        entry
        for entry in normalization_result.by_code.values()
        if entry.manual is not None
        and entry.manual.manual_reference_table == "ENTITY@Entity.xsd"
    ]
    assert entity_entries, "Expected at least one ENTITY@Entity.xsd manual reference."
    resolved_entry = entity_entries[0]
    assert resolved_entry.reference_resolution is not None
    assert (
        resolved_entry.reference_resolution.source_family
        == ReferenceSourceFamily.SIDE_PACKAGE_REGISTRY
    )

def test_build_normalization_result_includes_thesaurus_side_package_resolution_for_known_code():
    # Arrange / Act
    normalization_result = build_normalization_result(
        SPECIFICATION_MANUAL_XML,
        TREE_MODEL_XML,
        reference_tables_path=REFERENCE_TABLES_XML,
        subtypes_path=SUBTYPES_XML,
        entity_path=ENTITY_XML,
        thesaurus_path=THESAURUS_XML,
    )
    # Assert
    thesaurus_entries = [
        entry
        for entry in normalization_result.by_code.values()
        if entry.manual is not None
        and entry.manual.manual_reference_table == "THESAURUS@thesaurus.xsd"
    ]
    assert thesaurus_entries, "Expected at least one THESAURUS@thesaurus.xsd manual reference."
    resolved_entry = thesaurus_entries[0]
    assert resolved_entry.reference_resolution is not None
    assert (
        resolved_entry.reference_resolution.source_family
        == ReferenceSourceFamily.SIDE_PACKAGE_THESAURUS
    )
