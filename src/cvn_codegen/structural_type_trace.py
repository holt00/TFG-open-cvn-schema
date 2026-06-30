from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element

from cvn_codegen.normalization_types import (
    SourceTrace,
    StructuralTypeEvidence,
    TreePathEntry,
)


XSD_NAMESPACE = "http://www.w3.org/2001/XMLSchema"
XSD_ELEMENT = f"{{{XSD_NAMESPACE}}}element"
XSD_COMPLEX_TYPE = f"{{{XSD_NAMESPACE}}}complexType"
TARGET_WRAPPER_TYPE_NAMES = frozenset(
    {
        "FlexibleDatesType",
        "OfficialIdType",
        "EntityTypeType",
        "EntityNameType",
    }
)


@dataclass(frozen=True)
class StructuralElementType:
    element_name: str
    declaring_type_name: str | None
    structural_type_name: str | None
    source_xsd_file: str


@dataclass(frozen=True)
class StructuralTypeIndex:
    child_types_by_declaring_type: dict[str, dict[str, StructuralElementType]]
    root_types_by_element_name: dict[str, StructuralElementType]
    source_file_by_type_name: dict[str, str]
    wrapper_type_names: frozenset[str] = TARGET_WRAPPER_TYPE_NAMES


def load_xsd_root(xsd_path: Path) -> Element:
    if not isinstance(xsd_path, Path):
        raise ValueError(f"xsd_path must be a Path object, got {type(xsd_path)}.")
    if not xsd_path.is_file():
        raise FileNotFoundError(f"XSD file not found at path: {xsd_path}")
    return ET.parse(xsd_path).getroot()


def strip_namespace_prefix(type_name: str | None) -> str | None:
    if type_name is None:
        return None
    normalized_type_name = type_name.strip()
    if not normalized_type_name:
        return None
    if ":" in normalized_type_name:
        return normalized_type_name.split(":", 1)[1]
    return normalized_type_name


def iter_named_complex_types(xsd_root: Element) -> tuple[Element, ...]:
    return tuple(
        complex_type
        for complex_type in xsd_root.findall(XSD_COMPLEX_TYPE)
        if complex_type.get("name")
    )


def extract_type_source_files(
    xsd_roots_by_file_name: dict[str, Element],
) -> dict[str, str]:
    source_file_by_type_name: dict[str, str] = {}
    for source_file_name, xsd_root in xsd_roots_by_file_name.items():
        for complex_type in iter_named_complex_types(xsd_root):
            type_name = complex_type.get("name")
            if type_name is None:
                continue
            source_file_by_type_name[type_name] = source_file_name
    return source_file_by_type_name


def build_child_type_index(
    xsd_roots_by_file_name: dict[str, Element],
    source_file_by_type_name: dict[str, str],
) -> dict[str, dict[str, StructuralElementType]]:
    child_types_by_declaring_type: dict[str, dict[str, StructuralElementType]] = {}
    for source_file_name, xsd_root in xsd_roots_by_file_name.items():
        for complex_type in iter_named_complex_types(xsd_root):
            declaring_type_name = complex_type.get("name")
            if declaring_type_name is None:
                continue
            child_types: dict[str, StructuralElementType] = {}
            for child_element in complex_type.findall(f".//{XSD_ELEMENT}"):
                element_name = child_element.get("name")
                if element_name is None:
                    continue
                structural_type_name = strip_namespace_prefix(child_element.get("type"))
                child_source_file = source_file_by_type_name.get(
                    structural_type_name or "",
                    source_file_name,
                )
                child_types[element_name] = StructuralElementType(
                    element_name=element_name,
                    declaring_type_name=declaring_type_name,
                    structural_type_name=structural_type_name,
                    source_xsd_file=child_source_file,
                )
            child_types_by_declaring_type[declaring_type_name] = child_types
    return child_types_by_declaring_type


def find_global_element(xsd_root: Element, element_name: str) -> Element | None:
    for child in xsd_root.findall(XSD_ELEMENT):
        if child.get("name") == element_name:
            return child
    return None


def build_root_type_index(
    cvn_xsd_root: Element,
    source_file_by_type_name: dict[str, str],
) -> dict[str, StructuralElementType]:
    cvn_element = find_global_element(cvn_xsd_root, "CVN")
    if cvn_element is None:
        return {}
    root_types_by_element_name: dict[str, StructuralElementType] = {}
    for child_element in cvn_element.findall(f".//{XSD_ELEMENT}"):
        element_name = child_element.get("name")
        if element_name is None:
            continue
        structural_type_name = strip_namespace_prefix(child_element.get("type"))
        if structural_type_name is None:
            continue
        root_types_by_element_name[element_name] = StructuralElementType(
            element_name=element_name,
            declaring_type_name=None,
            structural_type_name=structural_type_name,
            source_xsd_file=source_file_by_type_name.get(
                structural_type_name,
                "CVN.xsd",
            ),
        )
    return root_types_by_element_name


def build_structural_type_index(
    cvn_xsd_path: Path,
    common_xsd_path: Path,
) -> StructuralTypeIndex:
    cvn_xsd_root = load_xsd_root(cvn_xsd_path)
    common_xsd_root = load_xsd_root(common_xsd_path)
    xsd_roots_by_file_name = {
        cvn_xsd_path.name: cvn_xsd_root,
        common_xsd_path.name: common_xsd_root,
    }
    source_file_by_type_name = extract_type_source_files(xsd_roots_by_file_name)
    return StructuralTypeIndex(
        child_types_by_declaring_type=build_child_type_index(
            xsd_roots_by_file_name=xsd_roots_by_file_name,
            source_file_by_type_name=source_file_by_type_name,
        ),
        root_types_by_element_name=build_root_type_index(
            cvn_xsd_root=cvn_xsd_root,
            source_file_by_type_name=source_file_by_type_name,
        ),
        source_file_by_type_name=source_file_by_type_name,
    )


def parse_path_segment(path_segment: str) -> tuple[str, str | None]:
    match = re.match(r"^(?P<tag>[^[]+)(?:\[@(?:name|code)='(?P<value>[^']+)'\])?$", path_segment)
    if match is None:
        return path_segment, None
    return match.group("tag"), match.group("value")


def get_structural_element_name(tag_name: str, segment_value: str | None) -> str | None:
    if tag_name in {"Property", "Indicator"}:
        return segment_value
    if tag_name in {"Version", "Agent"}:
        return tag_name
    if tag_name in {"CvnItem", "CVNItem"}:
        return "CvnItem"
    return None


def build_structural_type_evidence(
    element_type: StructuralElementType,
    xml_path: str,
    ancestor_wrapper_type_names: tuple[str, ...],
    structural_type_index: StructuralTypeIndex,
) -> StructuralTypeEvidence:
    terminal_wrapper_type_name = None
    if element_type.structural_type_name in structural_type_index.wrapper_type_names:
        terminal_wrapper_type_name = element_type.structural_type_name
    return StructuralTypeEvidence(
        element_name=element_type.element_name,
        declaring_type_name=element_type.declaring_type_name,
        structural_type_name=element_type.structural_type_name,
        xml_path=xml_path,
        source_xsd_file=element_type.source_xsd_file,
        terminal_wrapper_type_name=terminal_wrapper_type_name,
        ancestor_wrapper_type_names=ancestor_wrapper_type_names,
    )


def resolve_structural_type_evidence(
    xml_path: str,
    structural_type_index: StructuralTypeIndex,
) -> StructuralTypeEvidence | None:
    path_segments = tuple(
        segment for segment in xml_path.split("/") if segment
    )
    current_type_name: str | None = None
    active_wrapper_type_names: tuple[str, ...] = ()
    last_evidence: StructuralTypeEvidence | None = None

    for raw_segment in path_segments:
        tag_name, segment_value = parse_path_segment(raw_segment)
        if tag_name == "Node":
            continue

        element_name = get_structural_element_name(tag_name, segment_value)
        if element_name is None:
            continue

        if current_type_name is None:
            root_element_type = structural_type_index.root_types_by_element_name.get(
                element_name,
            )
            if root_element_type is None:
                continue
            last_evidence = build_structural_type_evidence(
                element_type=root_element_type,
                xml_path=xml_path,
                ancestor_wrapper_type_names=active_wrapper_type_names,
                structural_type_index=structural_type_index,
            )
            current_type_name = root_element_type.structural_type_name
            continue

        if tag_name in {"CvnItem", "CVNItem"} and current_type_name == "CvnItemType":
            continue

        child_types = structural_type_index.child_types_by_declaring_type.get(
            current_type_name,
            {},
        )
        child_type = child_types.get(element_name)
        if child_type is None:
            continue

        last_evidence = build_structural_type_evidence(
            element_type=child_type,
            xml_path=xml_path,
            ancestor_wrapper_type_names=active_wrapper_type_names,
            structural_type_index=structural_type_index,
        )
        current_type_name = child_type.structural_type_name
        if child_type.structural_type_name in structural_type_index.wrapper_type_names:
            active_wrapper_type_names = (
                *active_wrapper_type_names,
                child_type.structural_type_name,
            )

    return last_evidence


def enrich_tree_entry_with_structural_type_evidence(
    tree_entry: TreePathEntry,
    structural_type_index: StructuralTypeIndex,
) -> TreePathEntry:
    structural_type_evidence = resolve_structural_type_evidence(
        xml_path=tree_entry.xml_path,
        structural_type_index=structural_type_index,
    )
    if structural_type_evidence is None:
        return tree_entry
    return replace(
        tree_entry,
        structural_type_evidence=structural_type_evidence,
        trace=SourceTrace(
            source_file=tree_entry.trace.source_file,
            xml_path=tree_entry.trace.xml_path,
            source_code=tree_entry.trace.source_code,
        ),
    )


def enrich_tree_entries_with_structural_type_evidence(
    tree_entries: list[TreePathEntry],
    structural_type_index: StructuralTypeIndex,
) -> list[TreePathEntry]:
    return [
        enrich_tree_entry_with_structural_type_evidence(
            tree_entry=tree_entry,
            structural_type_index=structural_type_index,
        )
        for tree_entry in tree_entries
    ]
