from dataclasses import dataclass, field
from typing import List, Optional 
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
    source_file : str
    xml_path : Optional[str] = None 
    source_code : Optional[str] = None

@dataclass(frozen=True)
class ManualCodeEntry:
    code : str
    manual_name: Optional[ str]
    manual_short_name: Optional[str]
    manual_type: Optional[str]
    manual_obligatory: Optional[bool]
    manual_multiplicity: Optional[bool]
    manual_reference_table: Optional[str]
    manual_level: Optional[str] = None
    manual_order: Optional[int] = None
    manual_link: Optional[str] = None
    manual_length: Optional[int] = None
    trace: SourceTrace = field(
        default_factory=lambda: SourceTrace(source_file="SpecificationManual.xml")
    )

@dataclass(frozen=True)
class TreePathEntry:
    code: str
    tree_cvn_item_code: Optional[str] 
    tree_property_name: Optional[str] 
    tree_indicator_name: Optional[str] 
    tree_value: Optional[str]
    xml_path: str
    trace: SourceTrace


@dataclass(frozen=True)
class NormalizedCodeEntry:
    code: str
    manual: Optional[ManualCodeEntry]
    tree_paths: tuple[TreePathEntry, ...]
    source_files: tuple[str, ...]

@dataclass(frozen=True)
class NormalizationMismatch:
    kind: NormalizationMismatchKind
    code: Optional[str]
    message: str
    xml_path: Optional[str] = None

@dataclass(frozen=True)
class NormalizationResult:
    by_code: dict[str, NormalizedCodeEntry]
    by_xml_path: dict[str, tuple[TreePathEntry, ...]]
    manual_only_codes: tuple[str, ...]
    tree_only_codes: tuple[str, ...]
    mismatches: tuple[NormalizationMismatch, ...]