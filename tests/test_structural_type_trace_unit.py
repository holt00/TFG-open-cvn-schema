from pathlib import Path

from cvn_codegen.normalization_types import SourceTrace, TreePathEntry
from cvn_codegen.structural_type_trace import (
    build_structural_type_index,
    enrich_tree_entries_with_structural_type_evidence,
    resolve_structural_type_evidence,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
CANONICAL_PACKAGE_DIR = REPO_ROOT / "docs" / "CvnXML_v1.4.3_2.1_17012025"
CVN_XSD = CANONICAL_PACKAGE_DIR / "XSD" / "CVN.xsd"
COMMON_XSD = CANONICAL_PACKAGE_DIR / "XSD" / "Common.xsd"


def build_test_index():
    return build_structural_type_index(
        cvn_xsd_path=CVN_XSD,
        common_xsd_path=COMMON_XSD,
    )


def test_build_structural_type_index_extracts_root_and_child_mappings():
    structural_type_index = build_test_index()

    assert structural_type_index.root_types_by_element_name["Agent"].structural_type_name == "AgentType"
    assert (
        structural_type_index.child_types_by_declaring_type["PersonalIdentificationType"]["OfficialId"].structural_type_name
        == "OfficialIdType"
    )
    assert (
        structural_type_index.child_types_by_declaring_type["EntityType"]["EntityName"].structural_type_name
        == "EntityNameType"
    )


def test_resolve_structural_type_evidence_detects_official_id_wrapper():
    structural_type_index = build_test_index()
    xml_path = "/Node/Agent/Property[@name='Identification']/Indicator[@name='PersonalIdentification']/Indicator[@name='OfficialId']"

    evidence = resolve_structural_type_evidence(xml_path, structural_type_index)

    assert evidence is not None
    assert evidence.element_name == "OfficialId"
    assert evidence.structural_type_name == "OfficialIdType"
    assert evidence.terminal_wrapper_type_name == "OfficialIdType"
    assert evidence.ancestor_wrapper_type_names == ()


def test_resolve_structural_type_evidence_detects_entity_type_wrapper():
    structural_type_index = build_test_index()
    xml_path = "/Node/CVNItem[@code='010.010.000.000']/Property[@name='Entity']/Indicator[@name='Type']"

    evidence = resolve_structural_type_evidence(xml_path, structural_type_index)

    assert evidence is not None
    assert evidence.element_name == "Type"
    assert evidence.structural_type_name == "EntityTypeType"
    assert evidence.terminal_wrapper_type_name == "EntityTypeType"


def test_resolve_structural_type_evidence_detects_entity_name_wrapper():
    structural_type_index = build_test_index()
    xml_path = "/Node/CVNItem[@code='010.010.000.000']/Property[@name='Entity']/Indicator[@name='EntityName']"

    evidence = resolve_structural_type_evidence(xml_path, structural_type_index)

    assert evidence is not None
    assert evidence.element_name == "EntityName"
    assert evidence.structural_type_name == "EntityNameType"
    assert evidence.terminal_wrapper_type_name == "EntityNameType"


def test_resolve_structural_type_evidence_detects_flexible_dates_wrapper():
    structural_type_index = build_test_index()
    xml_path = "/Node/CVNItem[@code='010.010.000.000']/Property[@name='Date']/Indicator[@name='StartDate']"

    evidence = resolve_structural_type_evidence(xml_path, structural_type_index)

    assert evidence is not None
    assert evidence.element_name == "StartDate"
    assert evidence.structural_type_name == "FlexibleDatesType"
    assert evidence.terminal_wrapper_type_name == "FlexibleDatesType"


def test_resolve_structural_type_evidence_preserves_ancestor_wrapper_only_for_child_choice():
    structural_type_index = build_test_index()
    xml_path = "/Node/Agent/Property[@name='Identification']/Indicator[@name='PersonalIdentification']/Indicator[@name='OfficialId']/Indicator[@name='DNI']"

    evidence = resolve_structural_type_evidence(xml_path, structural_type_index)

    assert evidence is not None
    assert evidence.element_name == "DNI"
    assert evidence.structural_type_name == "CVN_string"
    assert evidence.terminal_wrapper_type_name is None
    assert evidence.ancestor_wrapper_type_names == ("OfficialIdType",)


def test_enrich_tree_entries_with_structural_type_evidence_attaches_evidence():
    structural_type_index = build_test_index()
    xml_path = "/Node/Agent/Property[@name='Identification']/Indicator[@name='PersonalIdentification']/Indicator[@name='OfficialId']"
    entry = TreePathEntry(
        code="000.010.000.100",
        tree_cvn_item_code=None,
        tree_property_name="Identification",
        tree_indicator_name="OfficialId",
        tree_value=None,
        xml_path=xml_path,
        trace=SourceTrace(
            source_file="CVNTreeModel.xml",
            xml_path=xml_path,
            source_code="000.010.000.100",
        ),
    )

    enriched_entries = enrich_tree_entries_with_structural_type_evidence(
        tree_entries=[entry],
        structural_type_index=structural_type_index,
    )

    assert len(enriched_entries) == 1
    assert enriched_entries[0].structural_type_evidence is not None
    assert enriched_entries[0].structural_type_evidence.terminal_wrapper_type_name == "OfficialIdType"
