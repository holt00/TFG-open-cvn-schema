from cvn_codegen.auxiliary_sources.bundle import AuxiliarySourceBundle
from cvn_codegen.auxiliary_sources.reference_tables_metadata import (
    ReferenceTableMetadata,
)
from cvn_codegen.normalization_types import (
    ReferenceResolution,
    ReferenceResolutionStatus,
    ReferenceResolutionTrace,
    ReferenceSourceFamily,
    SemanticReferenceKind,
    SerializationPattern
)
UNRESOLVED_MANUAL_REFERENCE_NAMES = frozenset({"CVN_AGENCY_C"})
def _normalize_reference_name(raw_reference: str | None) -> str | None:
    """Normalize a manual reference value for deterministic resolution.
    Args:
        raw_reference (str | None): Raw manual reference value extracted from
            ``SpecificationManual.xml``.
    Returns:
        str | None: Stripped reference value, or ``None`` when the input is
        missing or empty after normalization.
    """
    if raw_reference is None:
        return None
    normalized_reference = raw_reference.strip()
    if not normalized_reference:
        return None
    return normalized_reference
def _is_subtype_backed_table(
    table_metadata: ReferenceTableMetadata | None,
) -> bool:
    """Check whether resolved reference-table metadata is subtype-backed.
    Args:
        table_metadata (ReferenceTableMetadata | None): Resolved reference-table
            metadata when available.
    Returns:
        bool: ``True`` when the resolved table uses
        ``Subtype@Subtypes.xsd``, otherwise ``False``.
    """
    if table_metadata is None:
        return False
    return table_metadata.xml_data_type == "Subtype@Subtypes.xsd"
def _has_subtype_support(
    normalized_reference: str | None,
    auxiliary_bundle: AuxiliarySourceBundle,
) -> bool:
    """Check whether subtype metadata exists for a normalized reference name.
    Args:
        normalized_reference (str | None): Normalized manual reference name.
        auxiliary_bundle (AuxiliarySourceBundle): Aggregated auxiliary-source
            metadata bundle.
    Returns:
        bool: ``True`` when subtype metadata is available for the normalized
        reference name, otherwise ``False``.
    """
    if normalized_reference is None:
        return False
    return normalized_reference in auxiliary_bundle.subtypes_by_source_code
def _build_resolution_trace(
    manual_reference: str | None,
    resolved_from_artifact: str | None,
    resolution_rule: str,
    supporting_metadata: tuple[str, ...] = (),
    manual_code: str | None = None,
) -> ReferenceResolutionTrace:
    """Build traceability metadata for auxiliary-reference resolution.
    Args:
        manual_reference (str | None): Raw manual reference value before
            resolution.
        resolved_from_artifact (str | None): Canonical source artifact used to
            resolve the reference when available.
        resolution_rule (str): Short rule label describing how the resolution
            was obtained.
        supporting_metadata (tuple[str, ...]): Supporting technical metadata
            captured during resolution. Defaults to ``()``.
        manual_code (str | None): CVN manual code associated with the resolved
            reference when available.
    Returns:
        ReferenceResolutionTrace: Resolution-trace record attached to the final
        normalized auxiliary-reference result.
    """
    return ReferenceResolutionTrace(
        manual_reference=manual_reference,
        resolved_from_artifact=resolved_from_artifact,
        resolution_rule=resolution_rule,
        supporting_metadata=supporting_metadata,
        manual_code=manual_code,
    )

def classify_serialization_pattern(
    raw_reference: str | None,
    source_family: ReferenceSourceFamily | None,
    table_metadata: ReferenceTableMetadata | None,
) -> SerializationPattern | None:
    """Classify the serialization pattern for one resolved manual reference.
    Args:
        raw_reference (str | None): Raw manual reference value before
            normalization.
        source_family (ReferenceSourceFamily | None): Resolved source family for
            the manual reference when available.
        table_metadata (ReferenceTableMetadata | None): Resolved
            reference-table metadata when the reference points to
            ``ReferenceTables.xml``.
    Returns:
        SerializationPattern | None: Classified serialization pattern for the
        resolved reference, or ``None`` when the manual field has no reference.
    """
    normalized_reference = _normalize_reference_name(raw_reference)
    if normalized_reference is None:
        return None
    if source_family == ReferenceSourceFamily.SIDE_PACKAGE_REGISTRY:
        return SerializationPattern.SIDE_PACKAGE_REGISTRY
    if source_family == ReferenceSourceFamily.SIDE_PACKAGE_THESAURUS:
        return SerializationPattern.SIDE_PACKAGE_THESAURUS
    if source_family == ReferenceSourceFamily.UNRESOLVED_MANUAL_ONLY:
        return SerializationPattern.UNRESOLVED
    if table_metadata is None:
        return SerializationPattern.UNKNOWN_PRESENT_BUT_RESOLVED
    if _is_subtype_backed_table(table_metadata):
        return SerializationPattern.SUBTYPE
    if (
        table_metadata.xml_property == "Filter"
        and table_metadata.xml_indicator == "Value"
    ):
        return SerializationPattern.FILTER_VALUE
    if (
        table_metadata.xml_property == "Quality"
        and table_metadata.xml_indicator == "Measure"
    ):
        return SerializationPattern.QUALITY_MEASURE
    if (
        table_metadata.xml_property == "Scope"
        and table_metadata.xml_indicator == "Type"
    ):
        return SerializationPattern.SCOPE_TYPE
    if (
        table_metadata.xml_property == "ExternalPK"
        and table_metadata.xml_indicator == "Type"
    ):
        return SerializationPattern.EXTERNAL_PK_TYPE
    if (
        table_metadata.xml_property == "Entity"
        and table_metadata.xml_indicator == "Type"
    ):
        return SerializationPattern.ENTITY_TYPE
    if (
        table_metadata.xml_property == "Dedication"
        and table_metadata.xml_indicator is None
    ):
        return SerializationPattern.DEDICATION
    if (
        table_metadata.xml_property == "PhysicalDimension"
        and table_metadata.xml_indicator == "Type"
    ):
        return SerializationPattern.PHYSICAL_DIMENSION_TYPE
    if (
        table_metadata.xml_property == "Subject"
        and table_metadata.xml_indicator == "Description"
    ):
        return SerializationPattern.SUBJECT_DESCRIPTION
    return SerializationPattern.UNKNOWN_PRESENT_BUT_RESOLVED

def classify_semantic_reference_kind(
    raw_reference: str | None,
    source_family: ReferenceSourceFamily | None,
    serialization_pattern: SerializationPattern | None,
    table_metadata: ReferenceTableMetadata | None,
    under_traced_table_names: frozenset[str],
) -> SemanticReferenceKind | None:
    """Classify the semantic reference kind for one resolved manual reference.
    Args:
        raw_reference (str | None): Raw manual reference value before
            normalization.
        source_family (ReferenceSourceFamily | None): Resolved source family for
            the manual reference when available.
        serialization_pattern (SerializationPattern | None): Classified
            serialization pattern for the resolved reference.
        table_metadata (ReferenceTableMetadata | None): Resolved
            reference-table metadata when the reference points to
            ``ReferenceTables.xml``.
        under_traced_table_names (frozenset[str]): Table names that are
            technically present but currently under-traced in repository
            documentation.
    Returns:
        SemanticReferenceKind | None: Classified semantic kind for the resolved
        reference, or ``None`` when the manual field has no reference.
    """
    normalized_reference = _normalize_reference_name(raw_reference)
    if normalized_reference is None:
        return None
    if normalized_reference in under_traced_table_names:
        return SemanticReferenceKind.UNDER_TRACED_REFERENCE_TABLE
    if source_family == ReferenceSourceFamily.SIDE_PACKAGE_REGISTRY:
        return SemanticReferenceKind.SIDE_PACKAGE_REGISTRY
    if source_family == ReferenceSourceFamily.SIDE_PACKAGE_THESAURUS:
        return SemanticReferenceKind.SIDE_PACKAGE_THESAURUS_OR_VOCABULARY
    if source_family == ReferenceSourceFamily.UNRESOLVED_MANUAL_ONLY:
        return SemanticReferenceKind.UNRESOLVED_MANUAL_ONLY_REFERENCE
    if serialization_pattern == SerializationPattern.SUBTYPE:
        return SemanticReferenceKind.SUBTYPE_BACKED_CONTROLLED_FAMILY
    if serialization_pattern == SerializationPattern.QUALITY_MEASURE:
        return SemanticReferenceKind.COMPACT_SCALE_OR_MEASURE
    if serialization_pattern == SerializationPattern.EXTERNAL_PK_TYPE:
        return SemanticReferenceKind.IDENTIFIER_TYPE_TABLE
    if serialization_pattern == SerializationPattern.SCOPE_TYPE:
        return SemanticReferenceKind.SCOPE_TABLE
    if serialization_pattern == SerializationPattern.SUBJECT_DESCRIPTION:
        return SemanticReferenceKind.HIERARCHICAL_THEMATIC_CLASSIFICATION
    if normalized_reference == "UNESCO_CODES":
        return SemanticReferenceKind.HIERARCHICAL_THEMATIC_CLASSIFICATION
    if table_metadata is not None and table_metadata.has_hierarchy:
        return SemanticReferenceKind.HIERARCHICAL_THEMATIC_CLASSIFICATION
    return SemanticReferenceKind.COMPACT_ENUM_LIKE_TABLE


def resolve_manual_reference(
    raw_reference: str | None,
    auxiliary_bundle: AuxiliarySourceBundle,
    manual_code: str | None = None,
) -> ReferenceResolution:
    """Resolve one manual reference against canonical auxiliary source metadata.
    Args:
        raw_reference (str | None): Raw manual reference value extracted from
            ``SpecificationManual.xml``.
        auxiliary_bundle (AuxiliarySourceBundle): Aggregated auxiliary-source
            metadata bundle used during normalization.
        manual_code (str | None): CVN manual code associated with the reference
            when available.
    Returns:
        ReferenceResolution: Deterministic auxiliary-reference resolution result
        for the manual reference.
    """
    normalized_reference = _normalize_reference_name(raw_reference)
    if normalized_reference is None:
        return ReferenceResolution(
            raw_reference=raw_reference,
            status=ReferenceResolutionStatus.NO_REFERENCE,
            source_family=None,
            source_artifact=None,
            resolved_name=None,
            serialization_pattern=None,
            semantic_kind=None,
            is_subtype_backed=False,
            subtype_metadata_present=None,
            diagnostic_message=None,
            trace=_build_resolution_trace(
                manual_reference=raw_reference,
                resolved_from_artifact=None,
                resolution_rule="no_reference",
                manual_code=manual_code,
            ),
        )
    if normalized_reference == "ENTITY@Entity.xsd":
        serialization_pattern = classify_serialization_pattern(
            raw_reference=normalized_reference,
            source_family=ReferenceSourceFamily.SIDE_PACKAGE_REGISTRY,
            table_metadata=None,
        )
        semantic_kind = classify_semantic_reference_kind(
            raw_reference=normalized_reference,
            source_family=ReferenceSourceFamily.SIDE_PACKAGE_REGISTRY,
            serialization_pattern=serialization_pattern,
            table_metadata=None,
            under_traced_table_names=auxiliary_bundle.under_traced_table_names,
        )
        return ReferenceResolution(
            raw_reference=raw_reference,
            status=ReferenceResolutionStatus.RESOLVED,
            source_family=ReferenceSourceFamily.SIDE_PACKAGE_REGISTRY,
            source_artifact=(
                None
                if auxiliary_bundle.entity_catalog is None
                else auxiliary_bundle.entity_catalog.source_artifact
            ),
            resolved_name=normalized_reference,
            serialization_pattern=serialization_pattern,
            semantic_kind=semantic_kind,
            is_subtype_backed=False,
            subtype_metadata_present=None,
            diagnostic_message=None,
            trace=_build_resolution_trace(
                manual_reference=raw_reference,
                resolved_from_artifact=(
                    None
                    if auxiliary_bundle.entity_catalog is None
                    else auxiliary_bundle.entity_catalog.source_artifact
                ),
                resolution_rule="explicit_side_package_entity",
                manual_code=manual_code,
            ),
        )
    if normalized_reference == "THESAURUS@thesaurus.xsd":
        serialization_pattern = classify_serialization_pattern(
            raw_reference=normalized_reference,
            source_family=ReferenceSourceFamily.SIDE_PACKAGE_THESAURUS,
            table_metadata=None,
        )
        semantic_kind = classify_semantic_reference_kind(
            raw_reference=normalized_reference,
            source_family=ReferenceSourceFamily.SIDE_PACKAGE_THESAURUS,
            serialization_pattern=serialization_pattern,
            table_metadata=None,
            under_traced_table_names=auxiliary_bundle.under_traced_table_names,
        )
        return ReferenceResolution(
            raw_reference=raw_reference,
            status=ReferenceResolutionStatus.RESOLVED,
            source_family=ReferenceSourceFamily.SIDE_PACKAGE_THESAURUS,
            source_artifact=(
                None
                if auxiliary_bundle.thesaurus_catalog is None
                else auxiliary_bundle.thesaurus_catalog.source_artifact
            ),
            resolved_name=normalized_reference,
            serialization_pattern=serialization_pattern,
            semantic_kind=semantic_kind,
            is_subtype_backed=False,
            subtype_metadata_present=None,
            diagnostic_message=None,
            trace=_build_resolution_trace(
                manual_reference=raw_reference,
                resolved_from_artifact=(
                    None
                    if auxiliary_bundle.thesaurus_catalog is None
                    else auxiliary_bundle.thesaurus_catalog.source_artifact
                ),
                resolution_rule="explicit_side_package_thesaurus",
                manual_code=manual_code,
            ),
        )
    table_metadata = auxiliary_bundle.reference_tables_by_name.get(normalized_reference)
    if table_metadata is not None:
        is_subtype_backed = _is_subtype_backed_table(table_metadata)
        subtype_metadata_present = None
        if is_subtype_backed:
            subtype_metadata_present = _has_subtype_support(
                normalized_reference=normalized_reference,
                auxiliary_bundle=auxiliary_bundle,
            )
        source_family = ReferenceSourceFamily.REFERENCE_TABLE
        if is_subtype_backed:
            source_family = ReferenceSourceFamily.SUBTYPE_BACKED_TABLE
        serialization_pattern = classify_serialization_pattern(
            raw_reference=normalized_reference,
            source_family=source_family,
            table_metadata=table_metadata,
        )
        semantic_kind = classify_semantic_reference_kind(
            raw_reference=normalized_reference,
            source_family=source_family,
            serialization_pattern=serialization_pattern,
            table_metadata=table_metadata,
            under_traced_table_names=auxiliary_bundle.under_traced_table_names,
        )
        supporting_metadata = tuple(
            metadata_value
            for metadata_value in (
                table_metadata.xml_data_type,
                table_metadata.xml_property,
                table_metadata.xml_indicator,
            )
            if metadata_value is not None
        )
        diagnostic_message = None
        if (
            semantic_kind == SemanticReferenceKind.UNDER_TRACED_REFERENCE_TABLE
        ):
            diagnostic_message = (
                f"Reference table '{normalized_reference}' is technically present "
                "but currently under-traced in repository documentation."
            )
        elif is_subtype_backed and subtype_metadata_present is False:
            diagnostic_message = (
                f"Reference table '{normalized_reference}' is subtype-backed but "
                "no matching subtype metadata was found."
            )
        return ReferenceResolution(
            raw_reference=raw_reference,
            status=ReferenceResolutionStatus.RESOLVED,
            source_family=source_family,
            source_artifact="ReferenceTables.xml",
            resolved_name=normalized_reference,
            serialization_pattern=serialization_pattern,
            semantic_kind=semantic_kind,
            is_subtype_backed=is_subtype_backed,
            subtype_metadata_present=subtype_metadata_present,
            diagnostic_message=diagnostic_message,
            trace=_build_resolution_trace(
                manual_reference=raw_reference,
                resolved_from_artifact="ReferenceTables.xml",
                resolution_rule="reference_tables_exact_match",
                supporting_metadata=supporting_metadata,
                manual_code=manual_code,
            ),
        )
    diagnostic_message = None
    if normalized_reference in UNRESOLVED_MANUAL_REFERENCE_NAMES:
        diagnostic_message = (
            f"Manual reference '{normalized_reference}' does not resolve to "
            "ReferenceTables.xml or a supported side-package artifact."
        )
    serialization_pattern = classify_serialization_pattern(
        raw_reference=normalized_reference,
        source_family=ReferenceSourceFamily.UNRESOLVED_MANUAL_ONLY,
        table_metadata=None,
    )
    semantic_kind = classify_semantic_reference_kind(
        raw_reference=normalized_reference,
        source_family=ReferenceSourceFamily.UNRESOLVED_MANUAL_ONLY,
        serialization_pattern=serialization_pattern,
        table_metadata=None,
        under_traced_table_names=auxiliary_bundle.under_traced_table_names,
    )
    return ReferenceResolution(
        raw_reference=raw_reference,
        status=ReferenceResolutionStatus.UNRESOLVED,
        source_family=ReferenceSourceFamily.UNRESOLVED_MANUAL_ONLY,
        source_artifact=None,
        resolved_name=normalized_reference,
        serialization_pattern=serialization_pattern,
        semantic_kind=semantic_kind,
        is_subtype_backed=False,
        subtype_metadata_present=None,
        diagnostic_message=diagnostic_message,
        trace=_build_resolution_trace(
            manual_reference=raw_reference,
            resolved_from_artifact=None,
            resolution_rule="unresolved_manual_reference",
            manual_code=manual_code,
        ),
    )
