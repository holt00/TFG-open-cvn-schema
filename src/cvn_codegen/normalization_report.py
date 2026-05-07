"""Mismatch reporting helpers for Issue #13 normalization.

This module converts known source inconsistencies and source-overlap findings
into normalized mismatch records that can be attached to the final
``NormalizationResult``.
"""

from cvn_codegen.auxiliary_sources.bundle import AuxiliarySourceBundle
from cvn_codegen.normalization_types import (
    NormalizationMismatch,
    NormalizationMismatchKind,
    NormalizedCodeEntry,
    ReferenceResolutionStatus,
    SemanticReferenceKind,
)




def build_mismatch(kind : NormalizationMismatchKind, message : str, code : str | None = None, xml_path : str | None = None) -> NormalizationMismatch:
    """Build one normalization mismatch record.

    Args:
        kind (NormalizationMismatchKind): Mismatch category.
        message (str): Human-readable mismatch description.
        code (str | None): CVN code associated with mismatch when available.
        xml_path (str | None): Technical XML path associated with mismatch when
            available.

    Returns:
        NormalizationMismatch: Constructed mismatch record.
    """
    return NormalizationMismatch(
        kind=kind,
        code=code,
        message=message,
        xml_path=xml_path
    )

def collect_manual_only_mismatches(manual_only_codes: tuple[str,...]) -> tuple[NormalizationMismatch,...]:
    """Build mismatches for codes present only in specification manual.

    Args:
        manual_only_codes (tuple[str, ...]): Codes found in
            ``SpecificationManual.xml`` but not in ``CVNTreeModel.xml``.

    Returns:
        tuple[NormalizationMismatch, ...]: Mismatch records for manual-only
        codes.
    """
    mismatches = []
    for code in manual_only_codes:
        mismatches.append(build_mismatch(
            kind=NormalizationMismatchKind.MANUAL_ONLY_CODE,
            message=f"Code {code}exists in SpecificationManual.xml but not in CVNTreeModel.xml.",
            code=code
        ))
    return tuple(mismatches)

def collect_tree_only_mismatches(tree_only_codes: tuple[str,...]) -> tuple[NormalizationMismatch,...]:
    """Build mismatches for codes present only in tree model.

    Args:
        tree_only_codes (tuple[str, ...]): Codes found in ``CVNTreeModel.xml``
            but not in ``SpecificationManual.xml``.

    Returns:
        tuple[NormalizationMismatch, ...]: Mismatch records for tree-only
        codes.
    """
    mismatches = []
    for code in tree_only_codes:
        mismatches.append(build_mismatch(
            kind=NormalizationMismatchKind.TREE_ONLY_CODE,
            message=f"Code {code} exists in CVNTreeModel.xml but not in SpecificationManual.xml.",
            code=code
        ))
    return tuple(mismatches)

def collect_tree_structure_mismatches() -> tuple[NormalizationMismatch,...]:
    """Build mismatches for known structural issues in canonical tree model.

    Returns:
        tuple[NormalizationMismatch, ...]: Known structural mismatch records for
        canonical ``CVNTreeModel.xml`` anomalies.
    """
    return (
        build_mismatch(
            kind=NormalizationMismatchKind.UNEXPECTED_TREE_ELEMENT,
            code="060.030.070.220",
            message=(
                "Unexpected child element <Type> found under Indicator in "
                "CVNTreeModel.xml. Value: "
                "'CVN_QualityTypeType@AuxTable.xsd'. "
                "TreeModel_v1.0 documentation defines Indicator children only "
                "as Value and Child."
            ),
            xml_path = None
        ),
        build_mismatch(
            kind=NormalizationMismatchKind.UNEXPECTED_TREE_ELEMENT,
            code="060.030.070.230",
            message=(
                "Unexpected child element <Type> found under Indicator in "
                "CVNTreeModel.xml. Value: "
                "'CVN_QualityTypeType@AuxTable.xsd'. "
                "TreeModel_v1.0 documentation defines Indicator children only "
                "as Value and Child."
            ),
            xml_path = None

        ),
    )

def collect_reference_resolution_mismatches(
    normalized_entries_by_code: dict[str, NormalizedCodeEntry],
) -> tuple[NormalizationMismatch, ...]:
    """Build mismatches from per-entry auxiliary-reference resolution results.
    Args:
        normalized_entries_by_code (dict[str, NormalizedCodeEntry]): Normalized
            entries indexed by CVN code.
    Returns:
        tuple[NormalizationMismatch, ...]: Mismatch records derived from
        auxiliary-reference resolution findings attached to normalized entries.
    """
    mismatches: list[NormalizationMismatch] = []
    for code, normalized_entry in normalized_entries_by_code.items():
        reference_resolution = normalized_entry.reference_resolution
        if reference_resolution is None:
            continue
        if reference_resolution.status == ReferenceResolutionStatus.UNRESOLVED:
            mismatches.append(
                build_mismatch(
                    kind=NormalizationMismatchKind.UNRESOLVED_MANUAL_REFERENCE,
                    code=code,
                    message=(
                        f"Manual reference '{reference_resolution.resolved_name}' "
                        f"for code '{code}' does not resolve to a supported auxiliary source."
                    ),
                )
            )
        if reference_resolution.status == ReferenceResolutionStatus.AMBIGUOUS:
            mismatches.append(
                build_mismatch(
                    kind=NormalizationMismatchKind.AMBIGUOUS_AUXILIARY_RESOLUTION,
                    code=code,
                    message=(
                        f"Manual reference '{reference_resolution.raw_reference}' "
                        f"for code '{code}' matched multiple auxiliary-source candidates "
                        "and could not be resolved deterministically."
                    ),
                )
            )
        if (
            reference_resolution.is_subtype_backed
            and reference_resolution.subtype_metadata_present is False
        ):
            mismatches.append(
                build_mismatch(
                    kind=NormalizationMismatchKind.MISSING_SUBTYPE_SUPPORT,
                    code=code,
                    message=(
                        f"Reference table '{reference_resolution.resolved_name}' "
                        f"for code '{code}' is subtype-backed but no matching subtype metadata was found."
                    ),
                )
            )
        if (
            reference_resolution.semantic_kind
            == SemanticReferenceKind.UNDER_TRACED_REFERENCE_TABLE
        ):
            mismatches.append(
                build_mismatch(
                    kind=NormalizationMismatchKind.UNDER_TRACED_REFERENCE_TABLE,
                    code=code,
                    message=(
                        f"Reference table '{reference_resolution.resolved_name}' "
                        f"for code '{code}' is technically present but currently under-traced "
                        "in repository documentation."
                    ),
                )
            )
    return tuple(mismatches)

def collect_under_traced_table_mismatches(
    auxiliary_bundle: AuxiliarySourceBundle | None,
) -> tuple[NormalizationMismatch, ...]:
    """Build global mismatches for technically present but under-traced tables.
    Args:
        auxiliary_bundle (AuxiliarySourceBundle | None): Aggregated
            auxiliary-source metadata bundle when auxiliary resolution is
            available.
    Returns:
        tuple[NormalizationMismatch, ...]: Global mismatch records for
        under-traced reference tables documented by the repository.
    """
    if auxiliary_bundle is None:
        return ()
    mismatches: list[NormalizationMismatch] = []
    for table_name in sorted(auxiliary_bundle.under_traced_table_names):
        mismatches.append(
            build_mismatch(
                kind=NormalizationMismatchKind.UNDER_TRACED_REFERENCE_TABLE,
                code=table_name,
                message=(
                    f"Reference table '{table_name}' is present in ReferenceTables.xml "
                    "but remains functionally under-traced in current normalization inputs."
                ),
            )
        )
    return tuple(mismatches)

def collect_auxiliary_resolution_mismatches(
    normalized_entries_by_code: dict[str, NormalizedCodeEntry],
    auxiliary_bundle: AuxiliarySourceBundle | None,
) -> tuple[NormalizationMismatch, ...]:
    """Collect all auxiliary-resolution mismatches reported by normalization.
    Args:
        normalized_entries_by_code (dict[str, NormalizedCodeEntry]): Normalized
            entries indexed by CVN code.
        auxiliary_bundle (AuxiliarySourceBundle | None): Aggregated
            auxiliary-source metadata bundle when auxiliary resolution is
            available.
    Returns:
        tuple[NormalizationMismatch, ...]: Combined mismatch collection for
        auxiliary-reference resolution findings.
    """
    reference_resolution_mismatches = collect_reference_resolution_mismatches(
        normalized_entries_by_code
    )
    under_traced_table_mismatches = collect_under_traced_table_mismatches(
        auxiliary_bundle
    )
    return reference_resolution_mismatches + under_traced_table_mismatches

def collect_normalization_mismatches(
    manual_only_codes: tuple[str, ...],
    tree_only_codes: tuple[str, ...],
    normalized_entries_by_code: dict[str, NormalizedCodeEntry] | None = None,
    auxiliary_bundle: AuxiliarySourceBundle | None = None,
) -> tuple[NormalizationMismatch, ...]:
    """Collect all mismatches currently reported by normalization layer.
    Args:
        manual_only_codes (tuple[str, ...]): Codes present only in
            ``SpecificationManual.xml``.
        tree_only_codes (tuple[str, ...]): Codes present only in
            ``CVNTreeModel.xml``.
        normalized_entries_by_code (dict[str, NormalizedCodeEntry] | None):
            Normalized entries indexed by CVN code when auxiliary-reference
            resolution has been attached.
        auxiliary_bundle (AuxiliarySourceBundle | None): Aggregated
            auxiliary-source metadata bundle when auxiliary resolution is
            available.
    Returns:
        tuple[NormalizationMismatch, ...]: Combined mismatch collection for the
        current normalization run.
    """
    manual_only_mismatches = collect_manual_only_mismatches(manual_only_codes)
    tree_only_mismatches = collect_tree_only_mismatches(tree_only_codes)
    tree_structure_mismatches = collect_tree_structure_mismatches()
    auxiliary_resolution_mismatches: tuple[NormalizationMismatch, ...] = ()
    if normalized_entries_by_code is not None:
        auxiliary_resolution_mismatches = (
            collect_auxiliary_resolution_mismatches(
                normalized_entries_by_code=normalized_entries_by_code,
                auxiliary_bundle=auxiliary_bundle,
            )
        )
    return (
        manual_only_mismatches
        + tree_only_mismatches
        + tree_structure_mismatches
        + auxiliary_resolution_mismatches
    )