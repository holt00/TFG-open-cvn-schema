from dataclasses import dataclass, field
from typing import List
from enum import Enum


class NormalizationMismatchKind(str, Enum):
    MANUAL_ONLY_CODE = "manual_only_code"
    TREE_ONLY_CODE = "tree_only_code"
    DUPLICATE_MANUAL_CODE = "duplicate_manual_code"
    DUPLICATE_TREE_CODE = "duplicate_tree_code"
    EMPTY_CODE = "empty_code"
    INVALID_XML_PATH = "invalid_xml_path"
    AMBIGUOUS_XML_PATH = "ambiguous_xml_path"


@dataclass(frozen=True)
class SourceTrace:
    source_file: str
    xml_path: str | None = None
    source_code: str | None = None


@dataclass(frozen=True)
class ManualCodeEntry:
    code: str
    manual_name: str | None
    manual_short_name: str | None
    manual_type: str | None
    manual_obligatory: bool | None
    manual_multiplicity: bool | None
    manual_reference_table: str | None
    manual_level: str | None = None
    manual_order: int | None = None
    manual_link: str | None = None
    manual_length: int | None = None
    trace: SourceTrace = field(
        default_factory=lambda: SourceTrace(source_file="SpecificationManual.xml")
    )


@dataclass(frozen=True)
class TreePathEntry:
    code: str
    tree_cvn_item_code: str | None
    tree_property_name: str | None
    tree_indicator_name: str | None
    tree_value: str | None
    xml_path: str
    trace: SourceTrace


@dataclass(frozen=True)
class NormalizedCodeEntry:
    code: str
    manual: ManualCodeEntry | None
    tree_paths: tuple[TreePathEntry, ...]
    source_files: tuple[str, ...]


@dataclass(frozen=True)
class NormalizationMismatch:
    kind: NormalizationMismatchKind
    code: str | None
    message: str
    xml_path: str | None = None


@dataclass(frozen=True)
class NormalizationResult:
    by_code: dict[str, NormalizedCodeEntry]
    by_xml_path: dict[str, tuple[TreePathEntry, ...]]
    manual_only_codes: tuple[str, ...]
    tree_only_codes: tuple[str, ...]
    mismatches: tuple[NormalizationMismatch, ...]
