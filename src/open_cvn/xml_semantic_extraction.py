from __future__ import annotations

import re
from dataclasses import dataclass
from xml.etree import ElementTree


CVN_CODE_RE = re.compile(r"\b\d{3}\.\d{3}\.\d{3}\.\d{3}\b")


@dataclass(frozen=True)
class ExtractedXmlField:
    code: str
    raw_value: str
    xml_path: str


@dataclass(frozen=True)
class ExtractedXmlItem:
    code: str
    xml_path: str
    fields: tuple[ExtractedXmlField, ...]


@dataclass(frozen=True)
class XmlSemanticExtractionResult:
    items: tuple[ExtractedXmlItem, ...]
    cvn_codes: tuple[str, ...]
    xml_paths: tuple[str, ...]


def extract_xml_semantic_items(root: ElementTree.Element) -> XmlSemanticExtractionResult:
    paths = _element_paths(root)
    codes = _cvn_codes(root)
    items: list[ExtractedXmlItem] = []

    for element in root.iter():
        if _local_name(element.tag).lower() not in {"cvnitem", "cvn_item"}:
            continue
        item_code = _item_code(element)
        if item_code is None:
            continue
        item_path = paths.get(id(element), _local_name(element.tag))
        fields = _item_fields(element, item_code=item_code, paths=paths)
        items.append(ExtractedXmlItem(code=item_code, xml_path=item_path, fields=tuple(fields)))

    return XmlSemanticExtractionResult(items=tuple(items), cvn_codes=codes, xml_paths=tuple(paths.values())[:200])


def _item_fields(
    element: ElementTree.Element,
    *,
    item_code: str,
    paths: dict[int, str],
) -> list[ExtractedXmlField]:
    fields: list[ExtractedXmlField] = []
    seen: set[tuple[str, str, str]] = set()
    for descendant in element.iter():
        if descendant is element:
            continue
        field_code = _element_code(descendant)
        if field_code is None:
            continue
        raw_value = _raw_value(descendant)
        if not raw_value:
            continue
        if field_code == item_code and _is_item_identifier_path(descendant):
            continue
        xml_path = paths.get(id(descendant), _local_name(descendant.tag))
        key = (field_code, raw_value, xml_path)
        if key in seen:
            continue
        seen.add(key)
        fields.append(ExtractedXmlField(code=field_code, raw_value=raw_value, xml_path=xml_path))

    if not fields:
        raw_value = _raw_value(element)
        if raw_value and raw_value != item_code:
            fields.append(
                ExtractedXmlField(
                    code=item_code,
                    raw_value=raw_value,
                    xml_path=paths.get(id(element), _local_name(element.tag)),
                )
            )
    return fields


def _item_code(element: ElementTree.Element) -> str | None:
    code = _element_code(element)
    if code is not None:
        return code
    for descendant in element.iter():
        name = _local_name(descendant.tag).lower()
        if name in {"codecvnitem", "cvncode", "code"}:
            code = _element_code(descendant)
            if code is not None:
                return code
    return None


def _element_code(element: ElementTree.Element) -> str | None:
    for value in element.attrib.values():
        match = CVN_CODE_RE.search(str(value))
        if match:
            return match.group(0)
    if element.text:
        match = CVN_CODE_RE.search(element.text)
        if match:
            return match.group(0)
    for child in list(element):
        if _local_name(child.tag).lower() == "item" and child.text:
            match = CVN_CODE_RE.search(child.text)
            if match:
                return match.group(0)
    return None


def _raw_value(element: ElementTree.Element) -> str:
    values: list[str] = []
    for value in element.attrib.values():
        text = str(value).strip()
        if text and not CVN_CODE_RE.fullmatch(text):
            values.append(text)
    for descendant in element.iter():
        if descendant.text:
            text = descendant.text.strip()
            if text and not CVN_CODE_RE.fullmatch(text):
                values.append(text)
    return " ".join(dict.fromkeys(values)).strip()


def _is_item_identifier_path(element: ElementTree.Element) -> bool:
    names = {_local_name(descendant.tag).lower() for descendant in element.iter()}
    return bool({"codecvnitem", "cvnitemid"} & names)


def _element_paths(root: ElementTree.Element) -> dict[int, str]:
    paths: dict[int, str] = {}

    def visit(element: ElementTree.Element, path: str) -> None:
        paths[id(element)] = path
        counts: dict[str, int] = {}
        for child in list(element):
            child_name = _local_name(child.tag)
            counts[child_name] = counts.get(child_name, 0) + 1
            visit(child, f"{path}/{child_name}[{counts[child_name]}]")

    visit(root, _local_name(root.tag))
    return paths


def _cvn_codes(root: ElementTree.Element) -> tuple[str, ...]:
    codes: list[str] = []
    seen: set[str] = set()
    for element in root.iter():
        values = [str(element.tag), *(str(value) for value in element.attrib.values())]
        if element.text:
            values.append(element.text)
        for value in values:
            for match in CVN_CODE_RE.findall(value):
                if match not in seen:
                    seen.add(match)
                    codes.append(match)
    return tuple(codes)


def _local_name(tag: object) -> str:
    text = str(tag)
    if "}" in text:
        return text.rsplit("}", maxsplit=1)[1]
    return text
