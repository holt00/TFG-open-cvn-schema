import pytest as pt

from cvn_codegen.auxiliary_sources.bundle import AuxiliarySourceBundle
from cvn_codegen.normalization_report import (
    build_mismatch,
    collect_reference_resolution_mismatches,
    collect_manual_only_mismatches,
    collect_normalization_mismatches,
    collect_under_traced_table_mismatches,
    collect_tree_only_mismatches,
    collect_tree_structure_mismatches,
)
from cvn_codegen.normalization_types import (
    NormalizationMismatch,
    NormalizationMismatchKind,
    NormalizedCodeEntry,
    ReferenceResolution,
    ReferenceResolutionStatus,
    ReferenceResolutionTrace,
    ReferenceSourceFamily,
    SemanticReferenceKind,
    SerializationPattern,
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


def test_collect_reference_resolution_mismatches_reports_unresolved_case():
    # Arrange
    normalized_entries_by_code = {
        "060.010.000.030": NormalizedCodeEntry(
            code="060.010.000.030",
            manual=None,
            tree_paths=(),
            source_files=(),
            reference_resolution=ReferenceResolution(
                raw_reference="CVN_AGENCY_C",
                status=ReferenceResolutionStatus.UNRESOLVED,
                source_family=ReferenceSourceFamily.UNRESOLVED_MANUAL_ONLY,
                source_artifact=None,
                resolved_name="CVN_AGENCY_C",
                serialization_pattern=SerializationPattern.UNRESOLVED,
                semantic_kind=SemanticReferenceKind.UNRESOLVED_MANUAL_ONLY_REFERENCE,
                is_subtype_backed=False,
                subtype_metadata_present=None,
                diagnostic_message="Known unresolved manual reference.",
                trace=ReferenceResolutionTrace(
                    manual_reference="CVN_AGENCY_C",
                    resolved_from_artifact=None,
                    resolution_rule="unresolved_manual_reference",
                    manual_code="060.010.000.030",
                ),
            ),
        )
    }

    # Act
    mismatches = collect_reference_resolution_mismatches(
        normalized_entries_by_code
    )

    # Assert
    assert len(mismatches) == 1
    assert mismatches[0].kind == NormalizationMismatchKind.UNRESOLVED_MANUAL_REFERENCE
    assert mismatches[0].code == "060.010.000.030"


def test_collect_reference_resolution_mismatches_reports_missing_subtype_support():
    # Arrange
    normalized_entries_by_code = {
        "060.010.010.010": NormalizedCodeEntry(
            code="060.010.010.010",
            manual=None,
            tree_paths=(),
            source_files=(),
            reference_resolution=ReferenceResolution(
                raw_reference="CVN_KNOW_A",
                status=ReferenceResolutionStatus.RESOLVED,
                source_family=ReferenceSourceFamily.SUBTYPE_BACKED_TABLE,
                source_artifact="ReferenceTables.xml",
                resolved_name="CVN_KNOW_A",
                serialization_pattern=SerializationPattern.SUBTYPE,
                semantic_kind=SemanticReferenceKind.SUBTYPE_BACKED_CONTROLLED_FAMILY,
                is_subtype_backed=True,
                subtype_metadata_present=False,
                diagnostic_message="Subtype support missing.",
                trace=ReferenceResolutionTrace(
                    manual_reference="CVN_KNOW_A",
                    resolved_from_artifact="ReferenceTables.xml",
                    resolution_rule="reference_tables_exact_match",
                    manual_code="060.010.010.010",
                ),
            ),
        )
    }

    # Act
    mismatches = collect_reference_resolution_mismatches(
        normalized_entries_by_code
    )

    # Assert
    assert len(mismatches) == 1
    assert mismatches[0].kind == NormalizationMismatchKind.MISSING_SUBTYPE_SUPPORT
    assert mismatches[0].code == "060.010.010.010"


def test_collect_under_traced_table_mismatches_reports_documented_tables():
    # Arrange
    auxiliary_bundle = AuxiliarySourceBundle(
        reference_tables_by_name={},
        subtypes_by_source_code={},
        entity_catalog=None,
        thesaurus_catalog=None,
        under_traced_table_names=frozenset({"CVN_INTERVENTION_A", "CVN_PRUEBA"}),
    )

    # Act
    mismatches = collect_under_traced_table_mismatches(auxiliary_bundle)

    # Assert
    assert len(mismatches) == 2
    assert {mismatch.code for mismatch in mismatches} == {
        "CVN_INTERVENTION_A",
        "CVN_PRUEBA",
    }
    assert all(
        mismatch.kind == NormalizationMismatchKind.UNDER_TRACED_REFERENCE_TABLE
        for mismatch in mismatches
    )


def test_collect_normalization_mismatches_combines_auxiliary_findings():
    # Arrange
    normalized_entries_by_code = {
        "060.010.000.030": NormalizedCodeEntry(
            code="060.010.000.030",
            manual=None,
            tree_paths=(),
            source_files=(),
            reference_resolution=ReferenceResolution(
                raw_reference="CVN_AGENCY_C",
                status=ReferenceResolutionStatus.UNRESOLVED,
                source_family=ReferenceSourceFamily.UNRESOLVED_MANUAL_ONLY,
                source_artifact=None,
                resolved_name="CVN_AGENCY_C",
                serialization_pattern=SerializationPattern.UNRESOLVED,
                semantic_kind=SemanticReferenceKind.UNRESOLVED_MANUAL_ONLY_REFERENCE,
                is_subtype_backed=False,
                subtype_metadata_present=None,
                diagnostic_message="Known unresolved manual reference.",
                trace=ReferenceResolutionTrace(
                    manual_reference="CVN_AGENCY_C",
                    resolved_from_artifact=None,
                    resolution_rule="unresolved_manual_reference",
                    manual_code="060.010.000.030",
                ),
            ),
        )
    }
    auxiliary_bundle = AuxiliarySourceBundle(
        reference_tables_by_name={},
        subtypes_by_source_code={},
        entity_catalog=None,
        thesaurus_catalog=None,
        under_traced_table_names=frozenset({"CVN_INTERVENTION_A"}),
    )

    # Act
    mismatches = collect_normalization_mismatches(
        manual_only_codes=("000.010.000.030",),
        tree_only_codes=("030.010.000.250",),
        normalized_entries_by_code=normalized_entries_by_code,
        auxiliary_bundle=auxiliary_bundle,
    )

    # Assert
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
    assert any(
        mismatch.kind == NormalizationMismatchKind.UNRESOLVED_MANUAL_REFERENCE
        and mismatch.code == "060.010.000.030"
        for mismatch in mismatches
    )
    assert any(
        mismatch.kind == NormalizationMismatchKind.UNDER_TRACED_REFERENCE_TABLE
        and mismatch.code == "CVN_INTERVENTION_A"
        for mismatch in mismatches
    )
