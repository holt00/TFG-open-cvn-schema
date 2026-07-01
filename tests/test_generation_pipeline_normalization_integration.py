from cvn_codegen.normalization_types import (
    NormalizationMismatchKind,
    NormalizationResult,
    ReferenceResolutionStatus,
    ReferenceSourceFamily,
)
def test_pipeline_normalization_preserves_documented_baseline_counts(
    canonical_normalization_result: NormalizationResult,
):
    result = canonical_normalization_result
    overlap_count = (
        len(result.by_code)
        - len(result.manual_only_codes)
        - len(result.tree_only_codes)
    )
    assert len(result.by_code) == 1457
    assert len(result.manual_only_codes) == 27
    assert len(result.tree_only_codes) == 1
    assert overlap_count == 1429
def test_pipeline_normalization_reports_documented_mismatch_categories(
    canonical_normalization_result: NormalizationResult,
):
    mismatches = canonical_normalization_result.mismatches
    mismatch_kinds = {mismatch.kind for mismatch in mismatches}
    mismatch_codes = {mismatch.code for mismatch in mismatches}
    assert NormalizationMismatchKind.MANUAL_ONLY_CODE in mismatch_kinds
    assert NormalizationMismatchKind.TREE_ONLY_CODE in mismatch_kinds
    assert NormalizationMismatchKind.UNEXPECTED_TREE_ELEMENT in mismatch_kinds
    assert NormalizationMismatchKind.UNRESOLVED_MANUAL_REFERENCE in mismatch_kinds
    assert NormalizationMismatchKind.UNDER_TRACED_REFERENCE_TABLE in mismatch_kinds
    assert "030.010.000.250" in canonical_normalization_result.tree_only_codes
    assert "060.030.070.220" in mismatch_codes
    assert "060.030.070.230" in mismatch_codes
    assert "CVN_INTERVENTION_A" in mismatch_codes
    assert "CVN_PRUEBA" in mismatch_codes
def test_pipeline_normalization_attaches_auxiliary_reference_resolution(
    canonical_normalization_result: NormalizationResult,
):
    sex_entry = canonical_normalization_result.by_code["000.010.000.030"]
    assert sex_entry.reference_resolution is not None
    assert sex_entry.reference_resolution.status == ReferenceResolutionStatus.RESOLVED
    assert sex_entry.reference_resolution.resolved_name == "CVN_SEX_A"
    assert sex_entry.reference_resolution.source_family == ReferenceSourceFamily.REFERENCE_TABLE
    assert sex_entry.reference_resolution.reference_table_enum_evidence is not None
def test_pipeline_normalization_attaches_side_package_reference_resolution(
    canonical_normalization_result: NormalizationResult,
):
    entity_entries = [
        entry
        for entry in canonical_normalization_result.by_code.values()
        if entry.manual is not None
        and entry.manual.manual_reference_table == "ENTITY@Entity.xsd"
    ]
    thesaurus_entries = [
        entry
        for entry in canonical_normalization_result.by_code.values()
        if entry.manual is not None
        and entry.manual.manual_reference_table == "THESAURUS@thesaurus.xsd"
    ]
    assert entity_entries
    assert thesaurus_entries
    entity_resolution = entity_entries[0].reference_resolution
    thesaurus_resolution = thesaurus_entries[0].reference_resolution
    assert entity_resolution is not None
    assert thesaurus_resolution is not None
    assert entity_resolution.source_family == ReferenceSourceFamily.SIDE_PACKAGE_REGISTRY
    assert thesaurus_resolution.source_family == ReferenceSourceFamily.SIDE_PACKAGE_THESAURUS
def test_pipeline_normalization_attaches_structural_type_evidence(
    canonical_normalization_result: NormalizationResult,
):
    entries_with_structural_evidence = [
        entry
        for entry in canonical_normalization_result.by_code.values()
        if entry.structural_type_evidence
    ]
    terminal_wrapper_names = {
        evidence.terminal_wrapper_type_name
        for entry in entries_with_structural_evidence
        for evidence in entry.structural_type_evidence
        if evidence.terminal_wrapper_type_name is not None
    }
    assert entries_with_structural_evidence
    assert "FlexibleDatesType" in terminal_wrapper_names
    assert "OfficialIdType" in terminal_wrapper_names
    assert "EntityTypeType" in terminal_wrapper_names
    assert "EntityNameType" in terminal_wrapper_names