"""Mismatch reporting helpers for Issue #13 normalization.

This module converts known source inconsistencies and source-overlap findings
into normalized mismatch records that can be attached to the final
``NormalizationResult``.
"""

from cvn_codegen.normalization_types import NormalizationMismatch, NormalizationMismatchKind




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


def collect_normalization_mismatches(manual_only_codes: tuple[str, ...],tree_only_codes: tuple[str, ...],) -> tuple[NormalizationMismatch, ...]:
    """Collect all mismatches currently reported by normalization layer.

    Args:
        manual_only_codes (tuple[str, ...]): Codes present only in
            ``SpecificationManual.xml``.
        tree_only_codes (tuple[str, ...]): Codes present only in
            ``CVNTreeModel.xml``.

    Returns:
        tuple[NormalizationMismatch, ...]: Combined mismatch collection for the
        current normalization run.
    """
    manual_only_mismatches = collect_manual_only_mismatches(manual_only_codes)
    tree_only_mismatches = collect_tree_only_mismatches(tree_only_codes)
    tree_structure_mismatches = collect_tree_structure_mismatches()
    return (
        manual_only_mismatches
        + tree_only_mismatches
        + tree_structure_mismatches
    )
