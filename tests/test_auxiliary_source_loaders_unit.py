from pathlib import Path
from cvn_codegen.auxiliary_sources.bundle import build_auxiliary_source_bundle
from cvn_codegen.auxiliary_sources.entity_metadata import (
    load_entity_catalog_metadata,
)
from cvn_codegen.auxiliary_sources.reference_tables_metadata import (
    load_reference_tables_metadata,
)
from cvn_codegen.auxiliary_sources.subtypes_metadata import (
    load_subtypes_metadata,
)
from cvn_codegen.auxiliary_sources.thesaurus_metadata import (
    load_thesaurus_catalog_metadata,
)

from cvn_codegen.auxiliary_sources.bundle import AuxiliarySourceBundle
from cvn_codegen.normalization_types import (
    NormalizedCodeEntry,
    ReferenceResolution,
    ReferenceResolutionStatus,
    ReferenceResolutionTrace,
    ReferenceSourceFamily,
    SemanticReferenceKind,
    SerializationPattern,
    NormalizationMismatchKind
)

from cvn_codegen.normalization_report import (
    collect_reference_resolution_mismatches,
    collect_normalization_mismatches,
    collect_under_traced_table_mismatches
)

REPO_ROOT = Path(__file__).resolve().parent.parent
CANONICAL_XML_DIR = (
    REPO_ROOT / "docs" / "CvnXML_v1.4.3_2.1_17012025" / "XML"
)
REFERENCE_TABLES_XML = CANONICAL_XML_DIR / "ReferenceTables.xml"
SUBTYPES_XML = CANONICAL_XML_DIR / "Subtype_Spa.xml"
ENTITY_XML = CANONICAL_XML_DIR / "Entity.xml"
THESAURUS_XML = CANONICAL_XML_DIR / "Thesaurus.xml"
def test_load_reference_tables_metadata_returns_known_table():
    # Arrange / Act
    metadata_by_name = load_reference_tables_metadata(REFERENCE_TABLES_XML)
    # Assert
    assert isinstance(metadata_by_name, dict)
    assert "CVN_SEX_A" in metadata_by_name
    assert metadata_by_name["CVN_SEX_A"].table_name == "CVN_SEX_A"
def test_load_subtypes_metadata_returns_expected_numeric_source_code_shape():
    # Arrange / Act
    metadata_by_source_code = load_subtypes_metadata(SUBTYPES_XML)
    # Assert
    assert isinstance(metadata_by_source_code, dict)
    assert "001" in metadata_by_source_code
    assert metadata_by_source_code["001"].source_code == "001"
    assert metadata_by_source_code["001"].code_subtype1
def test_load_entity_catalog_metadata_returns_registry_shape():
    # Arrange / Act
    metadata = load_entity_catalog_metadata(ENTITY_XML)
    # Assert
    assert metadata.source_artifact == "Entity.xml"
    assert metadata.item_count > 0
    assert metadata.is_registry is True
    assert len(metadata.item_ids) > 0
def test_load_thesaurus_catalog_metadata_returns_hierarchical_vocabulary():
    # Arrange / Act
    metadata = load_thesaurus_catalog_metadata(THESAURUS_XML)
    # Assert
    assert metadata.source_artifact == "Thesaurus.xml"
    assert metadata.item_count > 0
    assert metadata.has_hierarchy is True
    assert metadata.is_vocabulary is True
def test_build_auxiliary_source_bundle_loads_all_requested_sources():
    # Arrange / Act
    auxiliary_bundle = build_auxiliary_source_bundle(
        reference_tables_path=REFERENCE_TABLES_XML,
        subtypes_path=SUBTYPES_XML,
        entity_path=ENTITY_XML,
        thesaurus_path=THESAURUS_XML,
    )
    # Assert
    assert "CVN_SEX_A" in auxiliary_bundle.reference_tables_by_name
    assert "001" in auxiliary_bundle.subtypes_by_source_code    
    assert auxiliary_bundle.entity_catalog is not None
    assert auxiliary_bundle.thesaurus_catalog is not None




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