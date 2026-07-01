from cvn_codegen.normalization_types import (
    NormalizationResult,
    ReferenceResolutionStatus,
    ManualCodeEntry, 
    NormalizedCodeEntry,
)
from cvn_codegen.semantic_policy import (
    DomainShapeKind,
    EnumEligibility,
    PolicyConfidence,
    SemanticBaseKind,
    SemanticFieldPolicy,
    CardinalityKind,
    DomainShapeKind,
    EnumEligibility,
    OverrideRule,
    PolicyConfidence,
    PresenceKind,
    SemanticPolicyBundle,
    build_default_semantic_policy_bundle,
    build_semantic_field_policy,
    build_default_semantic_policy_bundle,
    select_applicable_override,
    build_naming_policy,

)

from cvn_codegen.domain_model_generator import (
    resolve_field_name_collisions,
)

def build_policy_for_code(
    normalization_result: NormalizationResult,
    code: str,
) -> SemanticFieldPolicy:
    bundle = build_default_semantic_policy_bundle()
    return build_semantic_field_policy(
        entry=normalization_result.by_code[code],
        bundle=bundle,
    )
def find_policy_by_reference(
    normalization_result: NormalizationResult,
    raw_reference: str,
) -> SemanticFieldPolicy:
    bundle = build_default_semantic_policy_bundle()
    for entry in normalization_result.by_code.values():
        if entry.manual is None:
            continue
        if entry.manual.manual_reference_table != raw_reference:
            continue
        return build_semantic_field_policy(entry=entry, bundle=bundle)
    raise AssertionError(f"Reference {raw_reference!r} not found in normalization result.")
def test_semantic_pipeline_builds_deterministic_policy_for_real_entry(
    canonical_normalization_result: NormalizationResult,
):
    policy_a = build_policy_for_code(canonical_normalization_result, "000.010.000.030")
    policy_b = build_policy_for_code(canonical_normalization_result, "000.010.000.030")
    assert policy_a == policy_b
    assert policy_a.code == "000.010.000.030"
    assert policy_a.decision_trace.code == "000.010.000.030"
def test_semantic_pipeline_maps_plain_name_to_text_and_enum_ineligible(
    canonical_normalization_result: NormalizationResult,
):
    policy = build_policy_for_code(canonical_normalization_result, "000.010.000.020")
    assert policy.base_kind == SemanticBaseKind.TEXT
    assert policy.domain_shape_kind == DomainShapeKind.PLAIN_VALUE
    assert policy.enum_eligibility == EnumEligibility.INELIGIBLE
    assert policy.naming_policy.normalized_field_name == "nombre"
def test_semantic_pipeline_maps_cvn_sex_a_to_eligible_strict_enum_candidate(
    canonical_normalization_result: NormalizationResult,
):
    policy = build_policy_for_code(canonical_normalization_result, "000.010.000.030")
    assert policy.base_kind == SemanticBaseKind.CONTROLLED_REFERENCE
    assert policy.domain_shape_kind == DomainShapeKind.STRICT_ENUM_CANDIDATE
    assert policy.fallback_shape_kind == DomainShapeKind.OPEN_CODED_VALUE
    assert policy.enum_eligibility == EnumEligibility.ELIGIBLE
    assert policy.policy_confidence == PolicyConfidence.HIGH
    assert "enum_evidence:strict_enum_eligible" in policy.decision_trace.applied_rules
def test_semantic_pipeline_maps_cvn_entity_type_to_ineligible_strict_enum_candidate(
    canonical_normalization_result: NormalizationResult,
):
    policy = find_policy_by_reference(
        canonical_normalization_result,
        "CVN_ENTITY_TYPE",
    )
    assert policy.base_kind == SemanticBaseKind.CONTROLLED_REFERENCE
    assert policy.domain_shape_kind == DomainShapeKind.STRICT_ENUM_CANDIDATE
    assert policy.fallback_shape_kind == DomainShapeKind.OPEN_CODED_VALUE
    assert policy.enum_eligibility == EnumEligibility.INELIGIBLE
    assert policy.policy_confidence == PolicyConfidence.HIGH
    assert "enum_evidence:delegate_present" in policy.decision_trace.applied_rules
def test_semantic_pipeline_maps_representative_reference_families(
    canonical_normalization_result: NormalizationResult,
):
    expected_shapes = {
        "CVN_KNOW_A": DomainShapeKind.SUBTYPE_BACKED_VALUE,
        "ENTITY@Entity.xsd": DomainShapeKind.REGISTRY_REFERENCE,
        "THESAURUS@thesaurus.xsd": DomainShapeKind.VOCABULARY_REFERENCE,
        "UNESCO_CODES": DomainShapeKind.HIERARCHICAL_CODE_REFERENCE,
        "CVN_AGENCY_C": DomainShapeKind.UNRESOLVED_REFERENCE,
    }
    for raw_reference, expected_shape in expected_shapes.items():
        policy = find_policy_by_reference(canonical_normalization_result, raw_reference)
        assert policy.base_kind == SemanticBaseKind.CONTROLLED_REFERENCE
        assert policy.domain_shape_kind == expected_shape
        assert policy.enum_eligibility == EnumEligibility.INELIGIBLE
def test_semantic_pipeline_preserves_reference_trace_for_real_entry(
    canonical_normalization_result: NormalizationResult,
):
    entry = canonical_normalization_result.by_code["000.010.000.030"]
    policy = build_policy_for_code(canonical_normalization_result, "000.010.000.030")
    assert entry.reference_resolution is not None
    assert entry.reference_resolution.status == ReferenceResolutionStatus.RESOLVED
    assert policy.xml_paths
    assert policy.decision_trace.xml_paths == policy.xml_paths
    assert policy.decision_trace.manual_reference_table == "CVN_SEX_A"
    assert policy.decision_trace.reference_source_artifact == "ReferenceTables.xml"
    assert (
        policy.decision_trace.semantic_reference_kind
        == entry.reference_resolution.semantic_kind
    )
    assert (
        policy.decision_trace.serialization_pattern
        == entry.reference_resolution.serialization_pattern
    )

def test_semantic_pipeline_override_prefers_code_and_xml_path(
    canonical_normalization_result: NormalizationResult,
):
    entry = canonical_normalization_result.by_code["000.010.000.030"]
    xml_path = entry.tree_paths[0].xml_path
    selection = select_applicable_override(
        entry,
        (
            OverrideRule(
                rule_id="code_only",
                target_code=entry.code,
                enum_eligibility=EnumEligibility.INELIGIBLE,
            ),
            OverrideRule(
                rule_id="code_and_xml_path",
                target_code=entry.code,
                target_xml_path=xml_path,
                enum_eligibility=EnumEligibility.REVIEW_REQUIRED,
            ),
        ),
    )
    assert selection.selected_override is not None
    assert selection.selected_override.rule_id == "code_and_xml_path"
    assert selection.conflict_detected is False
def test_semantic_pipeline_override_prefers_code_over_xml_path(
    canonical_normalization_result: NormalizationResult,
):
    entry = canonical_normalization_result.by_code["000.010.000.030"]
    xml_path = entry.tree_paths[0].xml_path
    selection = select_applicable_override(
        entry,
        (
            OverrideRule(
                rule_id="xml_path_only",
                target_xml_path=xml_path,
                enum_eligibility=EnumEligibility.REVIEW_REQUIRED,
            ),
            OverrideRule(
                rule_id="code_only",
                target_code=entry.code,
                enum_eligibility=EnumEligibility.INELIGIBLE,
            ),
        ),
    )
    assert selection.selected_override is not None
    assert selection.selected_override.rule_id == "code_only"
    assert selection.conflict_detected is False
def test_semantic_pipeline_override_matches_semantic_kind_and_serialization_pattern(
    canonical_normalization_result: NormalizationResult,
):
    entry = canonical_normalization_result.by_code["000.010.000.030"]
    assert entry.reference_resolution is not None
    selection = select_applicable_override(
        entry,
        (
            OverrideRule(
                rule_id="semantic_kind_match",
                target_semantic_reference_kind=entry.reference_resolution.semantic_kind,
                enum_eligibility=EnumEligibility.INELIGIBLE,
            ),
            OverrideRule(
                rule_id="serialization_pattern_match",
                target_serialization_pattern=entry.reference_resolution.serialization_pattern,
                enum_eligibility=EnumEligibility.REVIEW_REQUIRED,
            ),
        ),
    )
    assert selection.conflict_detected is True
    assert selection.matched_rule_ids == (
        "semantic_kind_match",
        "serialization_pattern_match",
    )
def test_semantic_pipeline_override_application_changes_only_policy_outputs(
    canonical_normalization_result: NormalizationResult,
):
    default_bundle = build_default_semantic_policy_bundle()
    bundle = SemanticPolicyBundle(
        metadata=default_bundle.metadata,
        base_type_policies_by_manual_type=default_bundle.base_type_policies_by_manual_type,
        reference_kind_policies=default_bundle.reference_kind_policies,
        serialization_pattern_refinements=default_bundle.serialization_pattern_refinements,
        wrapper_policies_by_name=default_bundle.wrapper_policies_by_name,
        overrides=(
            OverrideRule(
                rule_id="force_open_value",
                target_code="000.010.000.030",
                domain_shape_kind=DomainShapeKind.OPEN_CODED_VALUE,
                enum_eligibility=EnumEligibility.REVIEW_REQUIRED,
                presence_kind=PresenceKind.REQUIRED,
                cardinality_kind=CardinalityKind.REPEATED,
                normalized_name="sexo_forzado",
            ),
        ),
        validation_cases=default_bundle.validation_cases,
    )
    entry = canonical_normalization_result.by_code["000.010.000.030"]
    policy = build_semantic_field_policy(entry=entry, bundle=bundle)
    assert policy.code == entry.code
    assert policy.decision_trace.manual_reference_table == "CVN_SEX_A"
    assert policy.domain_shape_kind == DomainShapeKind.OPEN_CODED_VALUE
    assert policy.enum_eligibility == EnumEligibility.REVIEW_REQUIRED
    assert policy.presence_kind == PresenceKind.REQUIRED
    assert policy.cardinality_kind == CardinalityKind.REPEATED
    assert policy.naming_policy.normalized_field_name == "sexo_forzado"
    assert "Applied override rule 'force_open_value'." in policy.notes
def test_semantic_pipeline_same_rank_override_conflict_requires_review(
    canonical_normalization_result: NormalizationResult,
):
    default_bundle = build_default_semantic_policy_bundle()
    bundle = SemanticPolicyBundle(
        metadata=default_bundle.metadata,
        base_type_policies_by_manual_type=default_bundle.base_type_policies_by_manual_type,
        reference_kind_policies=default_bundle.reference_kind_policies,
        serialization_pattern_refinements=default_bundle.serialization_pattern_refinements,
        wrapper_policies_by_name=default_bundle.wrapper_policies_by_name,
        overrides=(
            OverrideRule(
                rule_id="code_conflict_a",
                target_code="000.010.000.030",
                enum_eligibility=EnumEligibility.INELIGIBLE,
            ),
            OverrideRule(
                rule_id="code_conflict_b",
                target_code="000.010.000.030",
                enum_eligibility=EnumEligibility.REVIEW_REQUIRED,
            ),
        ),
        validation_cases=default_bundle.validation_cases,
    )
    entry = canonical_normalization_result.by_code["000.010.000.030"]
    policy = build_semantic_field_policy(entry=entry, bundle=bundle)
    assert policy.policy_confidence == PolicyConfidence.REQUIRES_REVIEW
    assert any("Override conflict detected" in note for note in policy.notes)

def test_semantic_pipeline_naming_normalizes_ascii_and_snake_case(
    canonical_normalization_result: NormalizationResult,
):
    entry = canonical_normalization_result.by_code["000.010.000.020"]
    policy = build_policy_for_code(canonical_normalization_result, entry.code)
    assert policy.naming_policy.source_label == "Nombre"
    assert policy.naming_policy.normalized_field_name == "nombre"
    assert policy.naming_policy.normalized_class_name == "Nombre"
def test_semantic_pipeline_naming_preserves_source_code_in_trace(
    canonical_normalization_result: NormalizationResult,
):
    policy = build_policy_for_code(canonical_normalization_result, "000.010.000.020")
    assert policy.code == "000.010.000.020"
    assert policy.decision_trace.code == "000.010.000.020"

def test_semantic_pipeline_naming_preserves_unesco_acronym():
    entry = NormalizedCodeEntry(
        code="999.999.999.999",
        manual=ManualCodeEntry(
            code="999.999.999.999",
            manual_name="Código UNESCO",
            manual_short_name=None,
            manual_type="Alphanumeric",
            manual_obligatory=False,
            manual_multiplicity=False,
            manual_reference_table=None,
        ),
        tree_paths=(),
        source_files=("SpecificationManual.xml",),
    )
    policy = build_semantic_field_policy(
        entry=entry,
        bundle=build_default_semantic_policy_bundle(),
    )
    assert policy.naming_policy.normalized_class_name == "CodigoUNESCO"
    assert policy.naming_policy.normalized_field_name == "codigo_unesco"

def test_semantic_pipeline_naming_collision_fallback_is_deterministic():
    entry_a = NormalizedCodeEntry(
        code="001.001",
        manual=ManualCodeEntry(
            code="001.001",
            manual_name="Título",
            manual_short_name=None,
            manual_type="Alphanumeric",
            manual_obligatory=False,
            manual_multiplicity=False,
            manual_reference_table=None,
        ),
        tree_paths=(),
        source_files=("SpecificationManual.xml",),
    )
    entry_b = NormalizedCodeEntry(
        code="002.002",
        manual=ManualCodeEntry(
            code="002.002",
            manual_name="Título",
            manual_short_name=None,
            manual_type="Alphanumeric",
            manual_obligatory=False,
            manual_multiplicity=False,
            manual_reference_table=None,
        ),
        tree_paths=(),
        source_files=("SpecificationManual.xml",),
    )
    bundle = build_default_semantic_policy_bundle()
    policies = (
        build_semantic_field_policy(entry=entry_b, bundle=bundle),
        build_semantic_field_policy(entry=entry_a, bundle=bundle),
    )
    resolved = resolve_field_name_collisions(policies)
    assert resolved == {
        "001.001": "titulo_001_001",
        "002.002": "titulo_002_002",
    }
    assert resolved == resolve_field_name_collisions(policies)