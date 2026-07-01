from cvn_codegen.domain_model_generator import resolve_python_type_for_policy
from cvn_codegen.normalization_types import NormalizationResult
from cvn_codegen.semantic_policy import (
    StructuralLimitationFlag,
    WrapperPolicyKind,
    build_default_semantic_policy_bundle,
    build_semantic_field_policy,
)
def find_policy_with_terminal_wrapper(
    normalization_result: NormalizationResult,
    wrapper_name: str,
):
    bundle = build_default_semantic_policy_bundle()
    for entry in normalization_result.by_code.values():
        terminal_wrapper_names = {
            evidence.terminal_wrapper_type_name
            for evidence in entry.structural_type_evidence
            if evidence.terminal_wrapper_type_name is not None
        }
        if wrapper_name not in terminal_wrapper_names:
            continue
        return build_semantic_field_policy(entry=entry, bundle=bundle)
    raise AssertionError(f"Terminal wrapper {wrapper_name!r} not found.")
def find_entry_with_ancestor_wrapper(
    normalization_result: NormalizationResult,
    wrapper_name: str,
):
    for entry in normalization_result.by_code.values():
        ancestor_wrapper_names = {
            ancestor_name
            for evidence in entry.structural_type_evidence
            for ancestor_name in evidence.ancestor_wrapper_type_names
        }
        if wrapper_name in ancestor_wrapper_names:
            return entry
    raise AssertionError(f"Ancestor wrapper {wrapper_name!r} not found.")

def find_entry_with_ancestor_only_wrapper(
    normalization_result: NormalizationResult,
    wrapper_name: str,
):
    for entry in normalization_result.by_code.values():
        terminal_wrapper_names = {
            evidence.terminal_wrapper_type_name
            for evidence in entry.structural_type_evidence
            if evidence.terminal_wrapper_type_name is not None
        }
        ancestor_wrapper_names = {
            ancestor_name
            for evidence in entry.structural_type_evidence
            for ancestor_name in evidence.ancestor_wrapper_type_names
        }
        if wrapper_name in ancestor_wrapper_names and wrapper_name not in terminal_wrapper_names:
            return entry
    raise AssertionError(f"Ancestor-only wrapper {wrapper_name!r} not found.")


def test_wrapper_handoff_flexible_dates_maps_to_value_component(
    canonical_normalization_result: NormalizationResult,
):
    policy = find_policy_with_terminal_wrapper(
        canonical_normalization_result,
        "FlexibleDatesType",
    )
    assert policy.wrapper_type_names == ("FlexibleDatesType",)
    assert policy.wrapper_policy_kinds == (WrapperPolicyKind.CHOICE_OBJECT_CANDIDATE,)
    assert StructuralLimitationFlag.CHOICE_NOT_ENFORCED in policy.structural_limitation_flags
    assert resolve_python_type_for_policy(policy) == "FlexibleDateValue"
def test_wrapper_handoff_official_id_maps_to_value_component(
    canonical_normalization_result: NormalizationResult,
):
    policy = find_policy_with_terminal_wrapper(
        canonical_normalization_result,
        "OfficialIdType",
    )
    assert policy.wrapper_type_names == ("OfficialIdType",)
    assert policy.wrapper_policy_kinds == (WrapperPolicyKind.CHOICE_OBJECT_CANDIDATE,)
    assert StructuralLimitationFlag.CHOICE_NOT_ENFORCED in policy.structural_limitation_flags
    assert resolve_python_type_for_policy(policy) == "OfficialIdValue"
def test_wrapper_handoff_entity_type_maps_to_value_component(
    canonical_normalization_result: NormalizationResult,
):
    policy = find_policy_with_terminal_wrapper(
        canonical_normalization_result,
        "EntityTypeType",
    )
    assert policy.wrapper_type_names == ("EntityTypeType",)
    assert policy.wrapper_policy_kinds == (WrapperPolicyKind.CHOICE_OBJECT_CANDIDATE,)
    assert StructuralLimitationFlag.CHOICE_NOT_ENFORCED in policy.structural_limitation_flags
    assert resolve_python_type_for_policy(policy) == "EntityTypeValue"
def test_wrapper_handoff_entity_name_maps_to_value_component(
    canonical_normalization_result: NormalizationResult,
):
    policy = find_policy_with_terminal_wrapper(
        canonical_normalization_result,
        "EntityNameType",
    )
    assert policy.wrapper_type_names == ("EntityNameType",)
    assert policy.wrapper_policy_kinds == (WrapperPolicyKind.CHOICE_OBJECT_CANDIDATE,)
    assert StructuralLimitationFlag.CHOICE_NOT_ENFORCED in policy.structural_limitation_flags
    assert resolve_python_type_for_policy(policy) == "EntityNameValue"
def test_wrapper_handoff_ancestor_wrapper_does_not_attach_terminal_policy(
    canonical_normalization_result: NormalizationResult,
):
    entry = find_entry_with_ancestor_only_wrapper(
    canonical_normalization_result,
    "OfficialIdType",
)
    policy = build_semantic_field_policy(
        entry=entry,
        bundle=build_default_semantic_policy_bundle(),
    )
    assert policy.wrapper_type_names == ()
    assert policy.wrapper_policy_kinds == ()
    assert policy.decision_trace.terminal_wrapper_type_names == ()
    assert "OfficialIdType" in policy.decision_trace.ancestor_wrapper_type_names
    assert resolve_python_type_for_policy(policy) != "OfficialIdValue"