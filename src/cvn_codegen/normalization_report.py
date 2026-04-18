from cvn_codegen.normalization_types import NormalizationMismatch, NormalizationMismatchKind




def build_mismatch(kind : NormalizationMismatchKind, message : str, code : str | None = None, xml_path : str | None = None) -> NormalizationMismatch:
    return NormalizationMismatch(
        kind=kind,
        code=code,
        message=message,
        xml_path=xml_path
    )

def collect_manual_only_mismatches(manual_only_codes: tuple[str,...]) -> tuple[NormalizationMismatch,...]:
    mismatches = []
    for code in manual_only_codes:
        mismatches.append(build_mismatch(
            kind=NormalizationMismatchKind.MANUAL_ONLY_CODE,
            message=f"Code {code}exists in SpecificationManual.xml but not in CVNTreeModel.xml.",
            code=code
        ))
    return tuple(mismatches)

def collect_tree_only_mismatches(tree_only_codes: tuple[str,...]) -> tuple[NormalizationMismatch,...]:
    mismatches = []
    for code in tree_only_codes:
        mismatches.append(build_mismatch(
            kind=NormalizationMismatchKind.TREE_ONLY_CODE,
            message=f"Code {code} exists in CVNTreeModel.xml but not in SpecificationManual.xml.",
            code=code
        ))
    return tuple(mismatches)

def collect_tree_structure_mismatches() -> tuple[NormalizationMismatch,...]:
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
    manual_only_mismatches = collect_manual_only_mismatches(manual_only_codes)
    tree_only_mismatches = collect_tree_only_mismatches(tree_only_codes)
    tree_structure_mismatches = collect_tree_structure_mismatches()
    return (
        manual_only_mismatches
        + tree_only_mismatches
        + tree_structure_mismatches
    )