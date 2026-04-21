import pytest as pt

from cvn_codegen.normalization_report import (
    build_mismatch,
    collect_manual_only_mismatches,
    collect_normalization_mismatches,
    collect_tree_only_mismatches,
    collect_tree_structure_mismatches,
)
from cvn_codegen.normalization_types import (
    NormalizationMismatch,
    NormalizationMismatchKind,
)


def test_build_mismatch_returns_expected_object():
    # Arrange
    kind = NormalizationMismatchKind.MANUAL_ONLY_CODE
    message = "Code exists only in SpecificationManual.xml."
    code = "000.010.000.030"
    xml_path = "/CVNTreeModel/Node/Agent/Property[@name='Identification']"

    # Act
    mismatch = build_mismatch(
        kind=kind,
        message=message,
        code=code,
        xml_path=xml_path,
    )

    # Assert
    assert isinstance(mismatch, NormalizationMismatch)
    assert mismatch.kind == kind
    assert mismatch.message == message
    assert mismatch.code == code
    assert mismatch.xml_path == xml_path


def test_collect_manual_only_mismatches_returns_expected_kind_and_codes():
    # Arrange
    manual_only_codes = ("000.010.000.030", "000.010.000.040")

    # Act
    mismatches = collect_manual_only_mismatches(manual_only_codes)

    # Assert
    assert len(mismatches) == 2
    assert all(
        mismatch.kind == NormalizationMismatchKind.MANUAL_ONLY_CODE
        for mismatch in mismatches
    )
    assert tuple(mismatch.code for mismatch in mismatches) == manual_only_codes


def test_collect_tree_only_mismatches_returns_expected_kind_and_codes():
    # Arrange
    tree_only_codes = ("030.010.000.250",)

    # Act
    mismatches = collect_tree_only_mismatches(tree_only_codes)

    # Assert
    assert len(mismatches) == 1
    assert mismatches[0].kind == NormalizationMismatchKind.TREE_ONLY_CODE
    assert mismatches[0].code == "030.010.000.250"


def test_collect_tree_structure_mismatches_returns_two_known_type_mismatches():
    # Act
    mismatches = collect_tree_structure_mismatches()

    # Assert
    assert len(mismatches) == 2
    assert all(
        mismatch.kind == NormalizationMismatchKind.UNEXPECTED_TREE_ELEMENT
        for mismatch in mismatches
    )
    assert {mismatch.code for mismatch in mismatches} == {
        "060.030.070.220",
        "060.030.070.230",
    }
    assert all("<Type>" in mismatch.message for mismatch in mismatches)
    assert all(
        "CVN_QualityTypeType@AuxTable.xsd" in mismatch.message
        for mismatch in mismatches
    )


def test_collect_normalization_mismatches_combines_all_sources():
    # Arrange
    manual_only_codes = ("000.010.000.030",)
    tree_only_codes = ("030.010.000.250",)

    # Act
    mismatches = collect_normalization_mismatches(
        manual_only_codes=manual_only_codes,
        tree_only_codes=tree_only_codes,
    )

    # Assert
    assert len(mismatches) == 4
    assert any(
        mismatch.kind == NormalizationMismatchKind.MANUAL_ONLY_CODE
        and mismatch.code == "000.010.000.030"
        for mismatch in mismatches
    )
    assert any(
        mismatch.kind == NormalizationMismatchKind.TREE_ONLY_CODE
        and mismatch.code == "030.010.000.250"
        for mismatch in mismatches
    )
    assert sum(
        1
        for mismatch in mismatches
        if mismatch.kind == NormalizationMismatchKind.UNEXPECTED_TREE_ELEMENT
    ) == 2
