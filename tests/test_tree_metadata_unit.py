from pathlib import Path
import xml.etree.ElementTree as ET

import pytest as pt

from cvn_codegen.normalization_types import TreePathEntry
from cvn_codegen.tree_metadata import (
    build_tree_path_entry,
    build_xml_path,
    collect_indicator_entries,
    collect_property_entries,
    extract_tree_entries,
    get_attribute,
    index_tree_entries_by_code,
    index_tree_entries_by_xml_path,
    load_and_extract_tree_entries,
    load_tree_model,
    strip_namespace,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
TREE_MODEL_XML = (
    REPO_ROOT / "docs" / "CvnXML_v1.4.3_2.1_17012025" / "XML" / "CVNTreeModel.xml"
)


def test_load_tree_model_raises_for_missing_file(tmp_path):
    # Arrange
    missing_file_path = tmp_path / "missing_tree_model.xml"

    # Act / Assert
    with pt.raises(FileNotFoundError):
        load_tree_model(missing_file_path)


def test_load_tree_model_parses_canonical_file():
    # Arrange
    tree_model_path = TREE_MODEL_XML

    # Act
    root = load_tree_model(tree_model_path)

    # Assert
    assert isinstance(root, ET.Element), (
        f"Expected an XML Element root, but got {type(root)}."
    )
    assert strip_namespace(root.tag) == "CVNTreeModel", (
        f"Expected root tag 'CVNTreeModel', but got '{strip_namespace(root.tag)}'."
    )


def test_strip_namespace_returns_local_name_for_expanded_tag():
    # Arrange
    tag = "{http://cv.normalizado.org/CVNTreeModel}Indicator"

    # Act
    local_name = strip_namespace(tag)

    # Assert
    assert local_name == "Indicator", (
        f"Expected local tag name 'Indicator', but got '{local_name}'."
    )


def test_strip_namespace_returns_plain_tag_unchanged():
    # Arrange
    tag = "Indicator"

    # Act
    local_name = strip_namespace(tag)

    # Assert
    assert local_name == "Indicator", (
        f"Expected unchanged tag 'Indicator', but got '{local_name}'."
    )


def test_get_attribute_returns_namespaced_attribute_value():
    # Arrange
    element = ET.fromstring(
        """
        <Property xmlns="http://cv.normalizado.org/CVNTreeModel"
                  xmlns:mo="http://cv.normalizado.org/CVNTreeModel"
                  mo:name="Identification"
                  mo:code="000.010.000.130" />
        """
    )

    # Act
    attribute_value = get_attribute(element, "name")

    # Assert
    assert attribute_value == "Identification", (
        f"Expected attribute value 'Identification', but got '{attribute_value}'."
    )


def test_get_attribute_returns_none_for_missing_attribute():
    # Arrange
    element = ET.fromstring(
        """
        <Property xmlns="http://cv.normalizado.org/CVNTreeModel"
                  xmlns:mo="http://cv.normalizado.org/CVNTreeModel"
                  mo:name="Identification" />
        """
    )

    # Act
    attribute_value = get_attribute(element, "code")

    # Assert
    assert attribute_value is None, "Expected None for a missing attribute."


def test_build_xml_path_returns_root_for_empty_segments():
    # Arrange
    path_segments: list[str] = []

    # Act
    xml_path = build_xml_path(path_segments)

    # Assert
    assert xml_path == "/", f"Expected '/', but got '{xml_path}'."


def test_build_xml_path_joins_segments_into_absolute_path():
    # Arrange
    path_segments = [
        "Node",
        "Agent",
        "Property[@name='Identification']",
        "Indicator[@name='Gender']",
    ]

    # Act
    xml_path = build_xml_path(path_segments)

    # Assert
    assert xml_path == (
        "/Node/Agent/Property[@name='Identification']/Indicator[@name='Gender']"
    ), f"Unexpected XML path built: '{xml_path}'."


def test_build_tree_path_entry_normalizes_code_and_trace():
    # Arrange
    code = " 000.010.000.030 "

    # Act
    entry = build_tree_path_entry(
        code=code,
        tree_cvn_item_code=None,
        tree_property_name="Identification",
        tree_indicator_name="Gender",
        tree_value=None,
        xml_path="/Node/Agent/Property[@name='Identification']/Indicator[@name='Gender']",
    )

    # Assert
    assert isinstance(entry, TreePathEntry)
    assert entry.code == "000.010.000.030"
    assert entry.trace.source_file == "CVNTreeModel.xml"
    assert entry.trace.source_code == "000.010.000.030"


def test_build_tree_path_entry_raises_for_empty_code():
    # Arrange
    invalid_code = "   "

    # Act / Assert
    with pt.raises(ValueError) as exc_info:
        build_tree_path_entry(
            code=invalid_code,
            tree_cvn_item_code=None,
            tree_property_name="Identification",
            tree_indicator_name="Gender",
            tree_value=None,
            xml_path="/Node/Agent/Property[@name='Identification']/Indicator[@name='Gender']",
        )

    assert "empty" in str(exc_info.value).lower()


def test_collect_indicator_entries_collects_parent_and_nested_indicators():
    # Arrange
    indicator_element = ET.fromstring(
        """
        <Indicator xmlns="http://cv.normalizado.org/CVNTreeModel"
                   xmlns:mo="http://cv.normalizado.org/CVNTreeModel"
                   mo:name="Telephone"
                   mo:code="000.010.000.210">
            <Value>000</Value>
            <Child>
                <Indicator mo:name="Number" mo:code="000.010.000.210" />
            </Child>
        </Indicator>
        """
    )

    # Act
    entries = collect_indicator_entries(
        indicator_element=indicator_element,
        current_path_segments=["Node", "Agent", "Property[@name='Contact']"],
        tree_cvn_item_code=None,
        tree_property_name="Contact",
    )

    # Assert
    assert len(entries) == 2, f"Expected 2 entries, but got {len(entries)}."
    assert entries[0].tree_indicator_name == "Telephone"
    assert entries[0].tree_value == "000"
    assert entries[1].tree_indicator_name == "Number"
    assert entries[1].xml_path.endswith("/Indicator[@name='Number']"), (
        f"Expected nested indicator path, but got '{entries[1].xml_path}'."
    )


def test_collect_property_entries_collects_property_and_indicator_entries():
    # Arrange
    property_element = ET.fromstring(
        """
        <Property xmlns="http://cv.normalizado.org/CVNTreeModel"
                  xmlns:mo="http://cv.normalizado.org/CVNTreeModel"
                  mo:name="Identification"
                  mo:code="000.010.000.130">
            <Indicator mo:name="Gender" mo:code="000.010.000.030" />
        </Property>
        """
    )

    # Act
    entries = collect_property_entries(
        property_element=property_element,
        current_path_segments=["Node", "Agent"],
        tree_cvn_item_code=None,
    )

    # Assert
    assert len(entries) == 2, f"Expected 2 entries, but got {len(entries)}."
    assert entries[0].tree_property_name == "Identification"
    assert entries[0].tree_indicator_name is None
    assert entries[1].tree_indicator_name == "Gender"


def test_extract_tree_entries_raises_when_node_is_missing():
    # Arrange
    root = ET.fromstring("<CVNTreeModel />")

    # Act / Assert
    with pt.raises(ValueError) as exc_info:
        extract_tree_entries(root)

    assert "node" in str(exc_info.value).lower()


def test_extract_tree_entries_returns_known_canonical_entry():
    # Arrange
    root = load_tree_model(TREE_MODEL_XML)

    # Act
    entries = extract_tree_entries(root)
    matching_entries = [entry for entry in entries if entry.code == "000.010.000.030"]

    # Assert
    assert matching_entries, "Expected to find code '000.010.000.030' in tree entries."
    assert any(entry.tree_indicator_name == "Gender" for entry in matching_entries), (
        "Expected at least one tree entry for code '000.010.000.030' with indicator 'Gender'."
    )
    assert any(
        entry.tree_property_name == "Identification" for entry in matching_entries
    ), (
        "Expected at least one tree entry for code '000.010.000.030' under property 'Identification'."
    )


def test_load_and_extract_tree_entries_returns_non_empty_result():
    # Arrange
    tree_model_path = TREE_MODEL_XML

    # Act
    entries = load_and_extract_tree_entries(tree_model_path)

    # Assert
    assert entries, "Expected non-empty tree entries from canonical tree model XML."


def test_index_tree_entries_by_code_groups_multiple_entries():
    # Arrange
    tree_entries = [
        build_tree_path_entry(
            code="000.010.000.030",
            tree_cvn_item_code=None,
            tree_property_name="Identification",
            tree_indicator_name="Gender",
            tree_value=None,
            xml_path="/Node/Agent/Property[@name='Identification']/Indicator[@name='Gender']",
        ),
        build_tree_path_entry(
            code="000.010.000.030",
            tree_cvn_item_code=None,
            tree_property_name="AnotherProperty",
            tree_indicator_name="AnotherIndicator",
            tree_value=None,
            xml_path="/Node/Agent/Property[@name='AnotherProperty']/Indicator[@name='AnotherIndicator']",
        ),
    ]

    # Act
    grouped_entries = index_tree_entries_by_code(tree_entries)

    # Assert
    assert "000.010.000.030" in grouped_entries
    assert len(grouped_entries["000.010.000.030"]) == 2, (
        "Expected two grouped entries for code '000.010.000.030'."
    )


def test_index_tree_entries_by_xml_path_groups_entries_by_path():
    # Arrange
    xml_path = "/Node/Agent/Property[@name='Identification']/Indicator[@name='Gender']"
    tree_entries = [
        build_tree_path_entry(
            code="000.010.000.030",
            tree_cvn_item_code=None,
            tree_property_name="Identification",
            tree_indicator_name="Gender",
            tree_value=None,
            xml_path=xml_path,
        ),
        build_tree_path_entry(
            code="000.010.000.031",
            tree_cvn_item_code=None,
            tree_property_name="Identification",
            tree_indicator_name="GenderAlias",
            tree_value=None,
            xml_path=xml_path,
        ),
    ]

    # Act
    grouped_entries = index_tree_entries_by_xml_path(tree_entries)

    # Assert
    assert xml_path in grouped_entries
    assert len(grouped_entries[xml_path]) == 2, (
        f"Expected two grouped entries for xml path '{xml_path}'."
    )
