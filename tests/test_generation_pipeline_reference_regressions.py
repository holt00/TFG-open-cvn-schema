import pytest
from cvn_codegen.auxiliary_sources.bundle import AuxiliarySourceBundle
from cvn_codegen.auxiliary_sources.reference_resolution import resolve_manual_reference
from cvn_codegen.normalization_types import (
    ReferenceResolutionStatus,
    ReferenceSourceFamily,
    SemanticReferenceKind,
    SerializationPattern,
)
def test_reference_regression_cvn_sex_a_is_direct_enum_like_table(
    canonical_auxiliary_bundle: AuxiliarySourceBundle,
):
    resolution = resolve_manual_reference("CVN_SEX_A", canonical_auxiliary_bundle)
    assert resolution.status == ReferenceResolutionStatus.RESOLVED
    assert resolution.source_family == ReferenceSourceFamily.REFERENCE_TABLE
    assert resolution.source_artifact == "ReferenceTables.xml"
    assert resolution.resolved_name == "CVN_SEX_A"
    assert resolution.serialization_pattern == SerializationPattern.UNKNOWN_PRESENT_BUT_RESOLVED
    assert resolution.semantic_kind == SemanticReferenceKind.COMPACT_ENUM_LIKE_TABLE
    assert resolution.reference_table_enum_evidence is not None
    assert resolution.reference_table_enum_evidence.table_name == "CVN_SEX_A"
    assert resolution.reference_table_enum_evidence.item_count == 2
    assert resolution.reference_table_enum_evidence.has_delegate is False
    assert resolution.reference_table_enum_evidence.has_hierarchy is False
def test_reference_regression_cvn_entity_type_has_delegate_open_world_signal(
    canonical_auxiliary_bundle: AuxiliarySourceBundle,
):
    resolution = resolve_manual_reference("CVN_ENTITY_TYPE", canonical_auxiliary_bundle)
    assert resolution.status == ReferenceResolutionStatus.RESOLVED
    assert resolution.source_family == ReferenceSourceFamily.REFERENCE_TABLE
    assert resolution.source_artifact == "ReferenceTables.xml"
    assert resolution.resolved_name == "CVN_ENTITY_TYPE"
    assert resolution.semantic_kind == SemanticReferenceKind.COMPACT_ENUM_LIKE_TABLE
    assert resolution.reference_table_enum_evidence is not None
    assert resolution.reference_table_enum_evidence.table_name == "CVN_ENTITY_TYPE"
    assert resolution.reference_table_enum_evidence.has_delegate is True
    assert "delegate_present" in resolution.reference_table_enum_evidence.open_world_signals
def test_reference_regression_cvn_know_a_is_subtype_backed(
    canonical_auxiliary_bundle: AuxiliarySourceBundle,
):
    resolution = resolve_manual_reference("CVN_KNOW_A", canonical_auxiliary_bundle)
    assert resolution.status == ReferenceResolutionStatus.RESOLVED
    assert resolution.source_family == ReferenceSourceFamily.SUBTYPE_BACKED_TABLE
    assert resolution.source_artifact == "ReferenceTables.xml"
    assert resolution.resolved_name == "CVN_KNOW_A"
    assert resolution.serialization_pattern == SerializationPattern.SUBTYPE
    assert resolution.semantic_kind == SemanticReferenceKind.SUBTYPE_BACKED_CONTROLLED_FAMILY
    assert resolution.is_subtype_backed is True
    assert resolution.subtype_metadata_present is True
    assert resolution.reference_table_enum_evidence is not None
    assert resolution.reference_table_enum_evidence.table_name == "CVN_KNOW_A"
def test_reference_regression_entity_reference_is_side_package_registry(
    canonical_auxiliary_bundle: AuxiliarySourceBundle,
):
    resolution = resolve_manual_reference("ENTITY@Entity.xsd", canonical_auxiliary_bundle)
    assert resolution.status == ReferenceResolutionStatus.RESOLVED
    assert resolution.source_family == ReferenceSourceFamily.SIDE_PACKAGE_REGISTRY
    assert resolution.source_artifact == "Entity.xml"
    assert resolution.resolved_name == "ENTITY@Entity.xsd"
    assert resolution.serialization_pattern == SerializationPattern.SIDE_PACKAGE_REGISTRY
    assert resolution.semantic_kind == SemanticReferenceKind.SIDE_PACKAGE_REGISTRY
    assert resolution.reference_table_enum_evidence is None
def test_reference_regression_thesaurus_reference_is_side_package_vocabulary(
    canonical_auxiliary_bundle: AuxiliarySourceBundle,
):
    resolution = resolve_manual_reference(
        "THESAURUS@thesaurus.xsd",
        canonical_auxiliary_bundle,
    )
    assert resolution.status == ReferenceResolutionStatus.RESOLVED
    assert resolution.source_family == ReferenceSourceFamily.SIDE_PACKAGE_THESAURUS
    assert resolution.source_artifact == "Thesaurus.xml"
    assert resolution.resolved_name == "THESAURUS@thesaurus.xsd"
    assert resolution.serialization_pattern == SerializationPattern.SIDE_PACKAGE_THESAURUS
    assert resolution.semantic_kind == SemanticReferenceKind.SIDE_PACKAGE_THESAURUS_OR_VOCABULARY
    assert resolution.reference_table_enum_evidence is None
def test_reference_regression_unesco_codes_is_hierarchical_thematic_reference(
    canonical_auxiliary_bundle: AuxiliarySourceBundle,
):
    resolution = resolve_manual_reference("UNESCO_CODES", canonical_auxiliary_bundle)
    assert resolution.status == ReferenceResolutionStatus.RESOLVED
    assert resolution.source_family == ReferenceSourceFamily.REFERENCE_TABLE
    assert resolution.source_artifact == "ReferenceTables.xml"
    assert resolution.resolved_name == "UNESCO_CODES"
    assert resolution.serialization_pattern == SerializationPattern.SUBJECT_DESCRIPTION
    assert resolution.semantic_kind == SemanticReferenceKind.HIERARCHICAL_THEMATIC_CLASSIFICATION
    assert resolution.reference_table_enum_evidence is not None
    assert resolution.reference_table_enum_evidence.table_name == "UNESCO_CODES"
    assert resolution.reference_table_enum_evidence.has_hierarchy is True
def test_reference_regression_cvn_agency_c_is_unresolved_manual_only(
    canonical_auxiliary_bundle: AuxiliarySourceBundle,
):
    resolution = resolve_manual_reference("CVN_AGENCY_C", canonical_auxiliary_bundle)
    assert resolution.status == ReferenceResolutionStatus.UNRESOLVED
    assert resolution.source_family == ReferenceSourceFamily.UNRESOLVED_MANUAL_ONLY
    assert resolution.source_artifact is None
    assert resolution.resolved_name == "CVN_AGENCY_C"
    assert resolution.serialization_pattern == SerializationPattern.UNRESOLVED
    assert resolution.semantic_kind == SemanticReferenceKind.UNRESOLVED_MANUAL_ONLY_REFERENCE
    assert resolution.diagnostic_message is not None
    assert resolution.reference_table_enum_evidence is None
@pytest.mark.parametrize("raw_reference", ["CVN_INTERVENTION_A", "CVN_PRUEBA"])
def test_reference_regression_under_traced_tables_are_explicit(
    canonical_auxiliary_bundle: AuxiliarySourceBundle,
    raw_reference: str,
):
    resolution = resolve_manual_reference(raw_reference, canonical_auxiliary_bundle)
    assert resolution.status == ReferenceResolutionStatus.RESOLVED
    assert resolution.source_family == ReferenceSourceFamily.REFERENCE_TABLE
    assert resolution.source_artifact == "ReferenceTables.xml"
    assert resolution.resolved_name == raw_reference
    assert resolution.semantic_kind == SemanticReferenceKind.UNDER_TRACED_REFERENCE_TABLE
    assert resolution.diagnostic_message is not None
    assert resolution.reference_table_enum_evidence is not None
    assert resolution.reference_table_enum_evidence.table_name == raw_reference