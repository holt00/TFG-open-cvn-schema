from pathlib import Path
from cvn_codegen.normalization_types import (
    TreePathEntry,
    SourceTrace,
)
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element


def load_tree_model(tree_model_path: Path) -> Element:
    if not isinstance(tree_model_path, Path):
        raise ValueError(
            f"tree_model_path must be a Path object, got {type(tree_model_path)} instead."
        )
    if not tree_model_path.is_file():
        raise FileNotFoundError(f"Tree model file not found at path: {tree_model_path}")

    tree = ET.parse(tree_model_path)
    root = tree.getroot()

    return root


def strip_namespace(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def get_attribute(element: Element, attribute_name: str) -> str | None:
    for attr_name, attr_value in element.attrib.items():
        local_name = strip_namespace(attr_name)
        if local_name == attribute_name:
            return attr_value
    return None


def build_xml_path(path_segments: list[str]) -> str:
    if not path_segments:
        return "/"
    return "/" + "/".join(path_segments)


def build_tree_path_entry(
    code: str,
    tree_cvn_item_code: str | None,
    tree_property_name: str | None,
    tree_indicator_name: str | None,
    tree_value: str | None,
    xml_path: str,
) -> TreePathEntry:
    normalized_code = str(code).strip()

    if not normalized_code:
        raise ValueError(
            f"Code cannot be empty or whitespace only. Received code: '{code}'"
        )

    return TreePathEntry(
        code=normalized_code,
        tree_cvn_item_code=tree_cvn_item_code,
        tree_property_name=tree_property_name,
        tree_indicator_name=tree_indicator_name,
        tree_value=tree_value,
        xml_path=xml_path,
        trace=SourceTrace(
            source_file="CVNTreeModel.xml",
            xml_path=xml_path,
            source_code=normalized_code,
        ),
    )


def collect_indicator_entries(
    indicator_element: Element,
    current_path_segments: list[str],
    tree_cvn_item_code: str | None,
    tree_property_name: str | None,
) -> list[TreePathEntry]:
    entries: list[TreePathEntry] = []

    indicator_name = get_attribute(indicator_element, "name")
    indicator_code = get_attribute(indicator_element, "code")

    if indicator_name is not None:
        indicator_segment = f"Indicator[@name='{indicator_name}']"
    else:
        indicator_segment = "Indicator"

    indicator_path_segments = current_path_segments + [indicator_segment]
    tree_value: str | None = None

    for child in indicator_element:
        if strip_namespace(child.tag) != "Value":
            continue

        if child.text is not None:
            normalized_value = child.text.strip()
            tree_value = normalized_value if normalized_value else None

        break
    if indicator_code is not None and indicator_code.strip():
        xml_path = build_xml_path(indicator_path_segments)
        entries.append(
            build_tree_path_entry(
                code=indicator_code,
                tree_cvn_item_code=tree_cvn_item_code,
                tree_property_name=tree_property_name,
                tree_indicator_name=indicator_name,
                tree_value=tree_value,
                xml_path=xml_path,
            )
        )
    for child in indicator_element:
        if strip_namespace(child.tag) != "Child":
            continue
        for nested_element in child:
            if strip_namespace(nested_element.tag) != "Indicator":
                continue
            entries.extend(
                collect_indicator_entries(
                    indicator_element=nested_element,
                    current_path_segments=indicator_path_segments,
                    tree_cvn_item_code=tree_cvn_item_code,
                    tree_property_name=tree_property_name,
                )
            )
    return entries


def collect_property_entries(
    property_element: Element,
    current_path_segments: list[str],
    tree_cvn_item_code: str | None,
) -> list[TreePathEntry]:
    entries: list[TreePathEntry] = []
    property_name = get_attribute(property_element, "name")
    property_code = get_attribute(property_element, "code")
    if property_name is not None:
        property_segment = f"Property[@name='{property_name}']"
    else:
        property_segment = "Property"
    property_path_segments = current_path_segments + [property_segment]
    if property_code is not None and property_code.strip():
        xml_path = build_xml_path(property_path_segments)
        entries.append(
            build_tree_path_entry(
                code=property_code,
                tree_cvn_item_code=tree_cvn_item_code,
                tree_property_name=property_name,
                tree_indicator_name=None,
                tree_value=None,
                xml_path=xml_path,
            )
        )
    for child in property_element:
        if strip_namespace(child.tag) != "Indicator":
            continue
        entries.extend(
            collect_indicator_entries(
                indicator_element=child,
                current_path_segments=property_path_segments,
                tree_cvn_item_code=tree_cvn_item_code,
                tree_property_name=property_name,
            )
        )
    return entries


def extract_tree_entries(root: Element) -> list[TreePathEntry]:
    entries: list[TreePathEntry] = []
    node_element: Element | None = None
    for child in root:
        if strip_namespace(child.tag) == "Node":
            node_element = child
            break

    if node_element is None:
        raise ValueError("CVNTreeModel XML does not contain a Node element.")

    for container in node_element:
        container_tag = strip_namespace(container.tag)

        if container_tag == "Version":
            current_path_segments = ["Node", "Version"]
            tree_cvn_item_code = None

        elif container_tag == "Agent":
            current_path_segments = ["Node", "Agent"]
            tree_cvn_item_code = None

        elif container_tag == "CVNItem":
            tree_cvn_item_code = get_attribute(container, "code")

            if tree_cvn_item_code is not None and tree_cvn_item_code.strip():
                current_path_segments = [
                    "Node",
                    f"CVNItem[@code='{tree_cvn_item_code.strip()}']",
                ]
            else:
                current_path_segments = ["Node", "CVNItem"]

        else:
            continue

        for child in container:
            if strip_namespace(child.tag) != "Property":
                continue

            entries.extend(
                collect_property_entries(
                    property_element=child,
                    current_path_segments=current_path_segments,
                    tree_cvn_item_code=tree_cvn_item_code,
                )
            )
    return entries


def load_and_extract_tree_entries(tree_model_path: Path) -> list[TreePathEntry]:
    root = load_tree_model(tree_model_path)
    return extract_tree_entries(root)


def index_tree_entries_by_code(
    tree_entries: list[TreePathEntry],
) -> dict[str, tuple[TreePathEntry, ...]]:
    grouped_entries: dict[str, list[TreePathEntry]] = {}
    for entry in tree_entries:
        grouped_entries.setdefault(entry.code, []).append(entry)
    return {code: tuple(entries) for code, entries in grouped_entries.items()}


def index_tree_entries_by_xml_path(
    tree_entries: list[TreePathEntry],
) -> dict[str, tuple[TreePathEntry, ...]]:
    grouped_entries: dict[str, list[TreePathEntry]] = {}
    for entry in tree_entries:
        grouped_entries.setdefault(entry.xml_path, []).append(entry)
    return {xml_path: tuple(entries) for xml_path, entries in grouped_entries.items()}
