from pathlib import Path
from cvn_codegen.auxiliary_sources.bundle import build_auxiliary_source_bundle
from cvn_codegen.auxiliary_sources.reference_resolution import (
    resolve_manual_reference,
)
from cvn_codegen.normalization_types import (
    ReferenceResolutionStatus,
    ReferenceSourceFamily,
    SemanticReferenceKind,
    SerializationPattern,
)
REPO_ROOT = Path(__file__).resolve().parent.parent
CANONICAL_XML_DIR = (
    REPO_ROOT / "docs" / "CvnXML_v1.4.3_2.1_17012025" / "XML"
)
REFERENCE_TABLES_XML = CANONICAL_XML_DIR / "ReferenceTables.xml"
SUBTYPES_XML = CANONICAL_XML_DIR / "Subtype_Spa.xml"
ENTITY_XML = CANONICAL_XML_DIR / "Entity.xml"
THESAURUS_XML = CANONICAL_XML_DIR / "Thesaurus.xml"
def build_test_auxiliary_bundle():
    return build_auxiliary_source_bundle(
        reference_tables_path=REFERENCE_TABLES_XML,
        subtypes_path=SUBTYPES_XML,
        entity_path=ENTITY_XML,
        thesaurus_path=THESAURUS_XML,
    )
def test_resolve_manual_reference_returns_no_reference_for_none():
    # Arrange
    auxiliary_bundle = build_test_auxiliary_bundle()
    # Act
    resolution = resolve_manual_reference(
        raw_reference=None,
        auxiliary_bundle=auxiliary_bundle,
    )
    # Assert
    assert resolution.status == ReferenceResolutionStatus.NO_REFERENCE
    assert resolution.source_family is None
    assert resolution.serialization_pattern is None
    assert resolution.semantic_kind is None
def test_resolve_manual_reference_returns_no_reference_for_whitespace():
    # Arrange
    auxiliary_bundle = build_test_auxiliary_bundle()
    # Act
    resolution = resolve_manual_reference(
        raw_reference="   ",
        auxiliary_bundle=auxiliary_bundle,
    )
    # Assert
    assert resolution.status == ReferenceResolutionStatus.NO_REFERENCE
    assert resolution.source_family is None
    assert resolution.serialization_pattern is None
    assert resolution.semantic_kind is None
def test_resolve_manual_reference_resolves_reference_table_case():
    # Arrange
    auxiliary_bundle = build_test_auxiliary_bundle()
    # Act
    resolution = resolve_manual_reference(
        raw_reference="CVN_SEX_A",
        auxiliary_bundle=auxiliary_bundle,
    )
    # Assert
    assert resolution.status == ReferenceResolutionStatus.RESOLVED
    assert resolution.source_family == ReferenceSourceFamily.REFERENCE_TABLE
    assert resolution.source_artifact == "ReferenceTables.xml"
    assert resolution.resolved_name == "CVN_SEX_A"
    assert resolution.serialization_pattern is not None
    assert resolution.semantic_kind is not None
def test_resolve_manual_reference_resolves_entity_side_package_case():
    # Arrange
    auxiliary_bundle = build_test_auxiliary_bundle()
    # Act
    resolution = resolve_manual_reference(
        raw_reference="ENTITY@Entity.xsd",
        auxiliary_bundle=auxiliary_bundle,
    )
    # Assert
    assert resolution.status == ReferenceResolutionStatus.RESOLVED
    assert resolution.source_family == ReferenceSourceFamily.SIDE_PACKAGE_REGISTRY
    assert resolution.source_artifact == "Entity.xml"
    assert resolution.serialization_pattern == SerializationPattern.SIDE_PACKAGE_REGISTRY
    assert resolution.semantic_kind == SemanticReferenceKind.SIDE_PACKAGE_REGISTRY
def test_resolve_manual_reference_resolves_thesaurus_side_package_case():
    # Arrange
    auxiliary_bundle = build_test_auxiliary_bundle()
    # Act
    resolution = resolve_manual_reference(
        raw_reference="THESAURUS@thesaurus.xsd",
        auxiliary_bundle=auxiliary_bundle,
    )
    # Assert
    assert resolution.status == ReferenceResolutionStatus.RESOLVED
    assert resolution.source_family == ReferenceSourceFamily.SIDE_PACKAGE_THESAURUS
    assert resolution.source_artifact == "Thesaurus.xml"
    assert resolution.serialization_pattern == SerializationPattern.SIDE_PACKAGE_THESAURUS
    assert (
        resolution.semantic_kind
        == SemanticReferenceKind.SIDE_PACKAGE_THESAURUS_OR_VOCABULARY
    )
def test_resolve_manual_reference_classifies_unesco_codes_as_hierarchical():
    # Arrange
    auxiliary_bundle = build_test_auxiliary_bundle()
    # Act
    resolution = resolve_manual_reference(
        raw_reference="UNESCO_CODES",
        auxiliary_bundle=auxiliary_bundle,
    )
    # Assert
    assert resolution.status == ReferenceResolutionStatus.RESOLVED
    assert resolution.resolved_name == "UNESCO_CODES"
    assert (
        resolution.serialization_pattern
        == SerializationPattern.SUBJECT_DESCRIPTION
    )
    assert (
        resolution.semantic_kind
        == SemanticReferenceKind.HIERARCHICAL_THEMATIC_CLASSIFICATION
    )
def test_resolve_manual_reference_returns_unresolved_for_known_manual_only_case():
    # Arrange
    auxiliary_bundle = build_test_auxiliary_bundle()
    # Act
    resolution = resolve_manual_reference(
        raw_reference="CVN_AGENCY_C",
        auxiliary_bundle=auxiliary_bundle,
    )
    # Assert
    assert resolution.status == ReferenceResolutionStatus.UNRESOLVED
    assert resolution.source_family == ReferenceSourceFamily.UNRESOLVED_MANUAL_ONLY
    assert resolution.serialization_pattern == SerializationPattern.UNRESOLVED
    assert (
        resolution.semantic_kind
        == SemanticReferenceKind.UNRESOLVED_MANUAL_ONLY_REFERENCE
    )
    assert resolution.diagnostic_message is not None
def test_resolve_manual_reference_classifies_under_traced_known_table():
    # Arrange
    auxiliary_bundle = build_test_auxiliary_bundle()
    # Act
    resolution = resolve_manual_reference(
        raw_reference="CVN_INTERVENTION_A",
        auxiliary_bundle=auxiliary_bundle,
    )
    # Assert
    assert resolution.status == ReferenceResolutionStatus.RESOLVED
    assert (
        resolution.semantic_kind
        == SemanticReferenceKind.UNDER_TRACED_REFERENCE_TABLE
    )
    assert resolution.diagnostic_message is not None

def test_resolve_manual_reference_marks_subtype_catalog_available_for_subtype_backed_table():
    # Arrange
    auxiliary_bundle = build_test_auxiliary_bundle()
    # Act
    resolution = resolve_manual_reference(
        raw_reference="CVN_KNOW_A",
        auxiliary_bundle=auxiliary_bundle,
    )
    # Assert
    assert resolution.status == ReferenceResolutionStatus.RESOLVED
    assert resolution.source_family == ReferenceSourceFamily.SUBTYPE_BACKED_TABLE
    assert resolution.is_subtype_backed is True
    assert resolution.subtype_metadata_present is True
    assert resolution.serialization_pattern == SerializationPattern.SUBTYPE
    assert (
        resolution.semantic_kind
        == SemanticReferenceKind.SUBTYPE_BACKED_CONTROLLED_FAMILY
    )