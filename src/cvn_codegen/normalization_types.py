from dataclasses import dataclass, field
from enum import Enum

class ReferenceResolutionStatus(str, Enum):
    """Enumerate the reference resolution statuses."""

    NO_REFERENCE = "no_reference"
    RESOLVED = "resolved"
    UNRESOLVED = "unresolved"
    AMBIGUOUS = "ambiguous"

class ReferenceSourceFamily(str, Enum):
    """Enumerate the reference source families."""

    REFERENCE_TABLE = "reference_table"
    SUBTYPE_BACKED_TABLE = "subtype_backed_table"
    SIDE_PACKAGE_REGISTRY = "side_package_registry"
    SIDE_PACKAGE_THESAURUS = "side_package_thesaurus"
    UNRESOLVED_MANUAL_ONLY = "unresolved_manual_only"

class SerializationPattern(str, Enum):
    """Enumerate the serialization patterns."""

    FILTER_VALUE = "filter_value"
    QUALITY_MEASURE = "quality_measure"
    SCOPE_TYPE = "scope_type"
    EXTERNAL_PK_TYPE = "external_pk_type"
    ENTITY_TYPE = "entity_type"
    DEDICATION = "dedication"
    PHYSICAL_DIMENSION_TYPE = "physical_dimension_type"
    SUBJECT_DESCRIPTION = "subject_description"
    SUBTYPE = "subtype"
    SIDE_PACKAGE_REGISTRY = "side_package_registry"
    SIDE_PACKAGE_THESAURUS = "side_package_thesaurus"
    UNRESOLVED = "unresolved"
    UNKNOWN_PRESENT_BUT_RESOLVED = "unknown_present_but_resolved"


class SemanticReferenceKind(str, Enum):
    """Enumerate the semantic reference kinds."""

    COMPACT_ENUM_LIKE_TABLE = "compact_enum_like_table"
    COMPACT_SCALE_OR_MEASURE = "compact_scale_or_measure"
    IDENTIFIER_TYPE_TABLE = "identifier_type_table"
    SCOPE_TABLE = "scope_table"
    SUBTYPE_BACKED_CONTROLLED_FAMILY = "subtype_backed_controlled_family"
    HIERARCHICAL_THEMATIC_CLASSIFICATION = "hierarchical_thematic_classification"
    SIDE_PACKAGE_REGISTRY = "side_package_registry"
    SIDE_PACKAGE_THESAURUS_OR_VOCABULARY = "side_package_thesaurus_or_vocabulary"
    UNRESOLVED_MANUAL_ONLY_REFERENCE = "unresolved_manual_only_reference"
    UNDER_TRACED_REFERENCE_TABLE = "under_traced_reference_table"

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
    UNRESOLVED_MANUAL_REFERENCE = "unresolved_manual_reference"
    AMBIGUOUS_AUXILIARY_RESOLUTION = "ambiguous_auxiliary_resolution"
    MISSING_SUBTYPE_SUPPORT = "missing_subtype_support"
    UNDER_TRACED_REFERENCE_TABLE = "under_traced_reference_table"


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
class ReferenceResolutionTrace:
    """Store traceability details for auxiliary-reference resolution."""

    manual_reference: str | None
    resolved_from_artifact: str | None
    resolution_rule: str
    supporting_metadata: tuple[str, ...] = ()
    manual_code: str | None = None
    
@dataclass(frozen=True)
class ReferenceTableEnumEvidence:
    """Store enum-eligibility evidence extracted from ReferenceTables.xml."""
    table_name: str
    item_count: int
    has_hierarchy: bool
    has_delegate: bool
    has_other_like_entry: bool
    has_duplicate_codes: bool
    has_duplicate_preferred_labels: bool
    has_blank_code: bool
    has_blank_preferred_label: bool
    normalized_codes: tuple[str, ...]
    preferred_labels: tuple[str, ...]
    normalized_preferred_labels: tuple[str, ...]
    open_world_signals: tuple[str, ...]


@dataclass(frozen=True)
class StructuralTypeEvidence:
    """Store structural XSD type evidence for one normalized tree path."""

    element_name: str
    declaring_type_name: str | None
    structural_type_name: str | None
    xml_path: str
    source_xsd_file: str
    terminal_wrapper_type_name: str | None = None
    ancestor_wrapper_type_names: tuple[str, ...] = ()


@dataclass(frozen=True)
class ReferenceResolution:
    """Represent resolved auxiliary-reference metadata for one manual reference."""
    raw_reference: str | None
    status: ReferenceResolutionStatus
    source_family: ReferenceSourceFamily | None
    source_artifact: str | None
    resolved_name: str | None
    serialization_pattern: SerializationPattern | None
    semantic_kind: SemanticReferenceKind | None
    is_subtype_backed: bool
    subtype_metadata_present: bool | None
    diagnostic_message: str | None
    trace: ReferenceResolutionTrace
    reference_table_enum_evidence: ReferenceTableEnumEvidence | None = None

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
        structural_type_evidence (StructuralTypeEvidence | None): Optional XSD
            type evidence resolved upstream for this tree path.
    """

    code: str
    tree_cvn_item_code: str | None
    tree_property_name: str | None
    tree_indicator_name: str | None
    tree_value: str | None
    xml_path: str
    trace: SourceTrace
    structural_type_evidence: StructuralTypeEvidence | None = None


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
        reference_resolution (ReferenceResolution | None): Resolved auxiliary
            reference metadata attached to the aggregate entry when available.
        structural_type_evidence (tuple[StructuralTypeEvidence, ...]): XSD type
            evidence aggregated from tree paths.
    """

    code: str
    manual: ManualCodeEntry | None
    tree_paths: tuple[TreePathEntry, ...]
    source_files: tuple[str, ...]
    reference_resolution: ReferenceResolution | None = None
    structural_type_evidence: tuple[StructuralTypeEvidence, ...] = ()


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
