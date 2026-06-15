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

def test_reference_table_metadata_exposes_enum_evidence_for_cvn_sex_a():
    # Arrange / Act
    metadata_by_name = load_reference_tables_metadata(REFERENCE_TABLES_XML)
    metadata = metadata_by_name["CVN_SEX_A"]
    # Assert
    assert metadata.item_codes
    assert metadata.preferred_labels
    assert metadata.normalized_codes == ("000", "010")
    assert metadata.has_hierarchy is False
    assert metadata.has_delegate is False
    assert metadata.has_blank_code is False
    assert metadata.has_blank_preferred_label is False
    assert metadata.has_duplicate_codes is False
    assert metadata.has_duplicate_preferred_labels is False
def test_reference_table_metadata_detects_open_world_signals_for_cvn_entity_type():
    # Arrange / Act
    metadata_by_name = load_reference_tables_metadata(REFERENCE_TABLES_XML)
    metadata = metadata_by_name["CVN_ENTITY_TYPE"]
    # Assert
    assert metadata.has_delegate is True
    assert metadata.has_other_like_entry is True
    assert "delegate_present" in metadata.open_world_signals
    assert any(
        signal.startswith("label_token:")
        for signal in metadata.open_world_signals
    )