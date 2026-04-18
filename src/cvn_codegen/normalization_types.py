from dataclasses import dataclass, field
from typing import List
from enum import Enum


class NormalizationMismatchKind(str, Enum):
    """Enumerate the mismatch categories recognized during normalization."""

    MANUAL_ONLY_CODE = "manual_only_code"
    TREE_ONLY_CODE = "tree_only_code"
    DUPLICATE_MANUAL_CODE = "duplicate_manual_code"
    DUPLICATE_TREE_CODE = "duplicate_tree_code"
    EMPTY_CODE = "empty_code"
    INVALID_XML_PATH = "invalid_xml_path"
    AMBIGUOUS_XML_PATH = "ambiguous_xml_path"
    UNEXPECTED_TREE_ELEMENT = "unexpected_tree_element"


@dataclass(frozen=True)
class SourceTrace:
    """Store source-document traceability for normalized metadata.

    Attributes:
        source_file (str): Source XML file name.
        xml_path (str | None): Technical XML path associated with the data.
        source_code (str | None): CVN code associated with the source element.
    """

    source_file: str
    xml_path: str | None = None
    source_code: str | None = None


@dataclass(frozen=True)
class ManualCodeEntry:
    """Represent normalized metadata extracted from ``SpecificationManual.xml``.

    Attributes:
        code (str): CVN code of the manual item.
        manual_name (str | None): Preferred localized item name.
        manual_short_name (str | None): Preferred localized short item name.
        manual_type (str | None): Manual-declared technical type.
        manual_obligatory (bool | None): Whether the field is marked as
            obligatory in the manual.
        manual_multiplicity (bool | None): Whether the field is marked as
            multiple in the manual.
        manual_reference_table (str | None): Reference table assigned by the
            manual.
        manual_level (str | None): Hierarchical manual level when present.
        manual_order (int | None): Manual display or processing order.
        manual_link (str | None): Link value declared by the manual.
        manual_length (int | None): Length constraint declared by the manual.
        trace (SourceTrace): Traceability back to the source XML element.
    """

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
    """Represent normalized metadata extracted from ``CVNTreeModel.xml``.

    Attributes:
        code (str): CVN code associated with the current tree node.
        tree_cvn_item_code (str | None): Enclosing ``CVNItem`` code when
            available.
        tree_property_name (str | None): Technical property name.
        tree_indicator_name (str | None): Technical indicator name.
        tree_value (str | None): Optional ``Value`` content found in the tree.
        xml_path (str): Stable XML-like path of the current tree node.
        trace (SourceTrace): Traceability back to the source XML element.
    """

    code: str
    tree_cvn_item_code: str | None
    tree_property_name: str | None
    tree_indicator_name: str | None
    tree_value: str | None
    xml_path: str
    trace: SourceTrace


@dataclass(frozen=True)
class NormalizedCodeEntry:
    """Aggregate normalized manual and tree metadata for one CVN code.

    Attributes:
        code (str): CVN code represented by this aggregate entry.
        manual (ManualCodeEntry | None): Manual metadata for the code when
            available.
        tree_paths (tuple[TreePathEntry, ...]): Technical tree occurrences for
            the code.
        source_files (tuple[str, ...]): Source files contributing to the
            aggregate entry.
    """

    code: str
    manual: ManualCodeEntry | None
    tree_paths: tuple[TreePathEntry, ...]
    source_files: tuple[str, ...]


@dataclass(frozen=True)
class NormalizationMismatch:
    """Describe a detected mismatch during metadata normalization.

    Attributes:
        kind (NormalizationMismatchKind): Category of mismatch detected.
        code (str | None): CVN code associated with the mismatch when present.
        message (str): Human-readable explanation of the mismatch.
        xml_path (str | None): Technical XML path associated with the mismatch
            when available.
    """

    kind: NormalizationMismatchKind
    code: str | None
    message: str
    xml_path: str | None = None


@dataclass(frozen=True)
class NormalizationResult:
    """Store the global output of the normalization stage.

    Attributes:
        by_code (dict[str, NormalizedCodeEntry]): Aggregate normalized view
            keyed by CVN code.
        by_xml_path (dict[str, tuple[TreePathEntry, ...]]): Tree entries keyed
            by technical XML path.
        manual_only_codes (tuple[str, ...]): Codes found only in the
            specification manual.
        tree_only_codes (tuple[str, ...]): Codes found only in the tree model.
        mismatches (tuple[NormalizationMismatch, ...]): Recorded normalization
            mismatches.
    """

    by_code: dict[str, NormalizedCodeEntry]
    by_xml_path: dict[str, tuple[TreePathEntry, ...]]
    manual_only_codes: tuple[str, ...]
    tree_only_codes: tuple[str, ...]
    mismatches: tuple[NormalizationMismatch, ...]
