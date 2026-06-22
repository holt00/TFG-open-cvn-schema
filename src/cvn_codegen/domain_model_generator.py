from collections import defaultdict
from decimal import Decimal

from cvn_codegen.normalization_types import (
    NormalizationResult,
    NormalizedCodeEntry
)
from cvn_codegen.semantic_policy import (
    SemanticFieldPolicy,
    SemanticPolicyBundle,
    SemanticBaseKind,
    CardinalityKind,
    PresenceKind,
    DomainShapeKind,
    build_semantic_field_policy,
)
from cvn_codegen.domain_model_types import (
    DomainFieldSpec,
    DomainGenerationResult,
    DomainGenerationUnit,
)


def build_semantic_policy_index(
    normalization_result: NormalizationResult,
    bundle: SemanticPolicyBundle,
) -> dict[str, SemanticFieldPolicy]:
    return {
        code: build_semantic_field_policy(
            entry=normalization_result.by_code[code],
            bundle=bundle,
        )
        for code in sorted(normalization_result.by_code)
    }

def group_entries_by_cvn_item_code(
    entries: dict[str, NormalizedCodeEntry],
) -> dict[str, tuple[NormalizedCodeEntry, ...]]:
    grouped: dict[str, list[NormalizedCodeEntry]] = {}

    for code in sorted(entries):
        entry = entries[code]

        if not entry.tree_paths:
            grouped.setdefault("__no_tree__", []).append(entry)
            continue

        seen_group_keys: set[str] = set()
        for tree_path in entry.tree_paths:
            group_key = tree_path.tree_cvn_item_code or "__no_cvn_item__"
            if group_key in seen_group_keys:
                continue
            grouped.setdefault(group_key, []).append(entry)
            seen_group_keys.add(group_key)

    return {
        group_key: tuple(grouped[group_key])
        for group_key in sorted(grouped)
    }

def get_field_name_from_policy(policy: SemanticFieldPolicy) -> str:
    return policy.naming_policy.normalized_field_name


def get_class_name_from_policy(policy: SemanticFieldPolicy) -> str:
    return policy.naming_policy.normalized_class_name or "Unnamed"

def resolve_field_name_collisions(
    policies: tuple[SemanticFieldPolicy, ...],
) -> dict[str, str]:
    grouped_by_name: dict[str, list[SemanticFieldPolicy]] = defaultdict(list)
    for policy in policies:
        base_name = policy.naming_policy.normalized_field_name
        grouped_by_name[base_name].append(policy)
    resolved_names: dict[str, str] = {}
    for base_name in sorted(grouped_by_name):
        grouped_policies = sorted(
            grouped_by_name[base_name],
            key=lambda policy: policy.code,
        )
        if len(grouped_policies) == 1:
            policy = grouped_policies[0]
            resolved_names[policy.code] = base_name
            continue
        for policy in grouped_policies:
            normalized_code_suffix = policy.code.replace(".", "_")
            resolved_names[policy.code] = f"{base_name}_{normalized_code_suffix}"
    return resolved_names

def build_resolved_field_names(
    policies: tuple[SemanticFieldPolicy, ...],
) -> dict[str, str]:
    return resolve_field_name_collisions(policies)

def get_python_type_for_base_kind(policy: SemanticFieldPolicy) -> str:
    if policy.base_kind == SemanticBaseKind.TEXT:
        return "str"
    if policy.base_kind == SemanticBaseKind.BOOLEAN:
        return "bool"
    if policy.base_kind == SemanticBaseKind.DECIMAL_NUMBER:
        return "Decimal"
    if policy.base_kind == SemanticBaseKind.DATE_LIKE:
        return "str"
    if policy.base_kind == SemanticBaseKind.DURATION_LIKE:
        return "str"
    return "object"

def is_repeated_field(policy: SemanticFieldPolicy) -> bool:
    return policy.cardinality_kind == CardinalityKind.REPEATED

def is_required_field(policy: SemanticFieldPolicy) -> bool:
    return policy.presence_kind == PresenceKind.REQUIRED

def build_python_type_for_policy(policy: SemanticFieldPolicy) -> str:
    base_type = get_python_type_for_base_kind(policy)
    if is_repeated_field(policy):
        return f"list[{base_type}]"
    return base_type

def is_controlled_reference_field(policy: SemanticFieldPolicy) -> bool:
    return policy.base_kind == SemanticBaseKind.CONTROLLED_REFERENCE



def get_python_type_for_controlled_reference(policy: SemanticFieldPolicy) -> str:
    if policy.domain_shape_kind == DomainShapeKind.STRICT_ENUM_CANDIDATE:
        return "str"
    if policy.domain_shape_kind == DomainShapeKind.OPEN_CODED_VALUE:
        return "OpenCodedValue"
    if policy.domain_shape_kind == DomainShapeKind.MEASURE_OR_SCALE_VALUE:
        return "MeasureOrScaleValue"
    if policy.domain_shape_kind == DomainShapeKind.IDENTIFIER_REFERENCE:
        return "IdentifierReference"
    if policy.domain_shape_kind == DomainShapeKind.SCOPE_REFERENCE:
        return "ScopeReference"
    if policy.domain_shape_kind == DomainShapeKind.SUBTYPE_BACKED_VALUE:
        return "SubtypeBackedValue"
    if policy.domain_shape_kind == DomainShapeKind.HIERARCHICAL_CODE_REFERENCE:
        return "HierarchicalCodeReference"
    if policy.domain_shape_kind == DomainShapeKind.REGISTRY_REFERENCE:
        return "RegistryReference"
    if policy.domain_shape_kind == DomainShapeKind.VOCABULARY_REFERENCE:
        return "VocabularyReference"
    if policy.domain_shape_kind == DomainShapeKind.UNRESOLVED_REFERENCE:
        return "UnresolvedReference"
    if policy.domain_shape_kind == DomainShapeKind.UNDER_TRACED_REFERENCE:
        return "UnderTracedReference"
    return "str"

def resolve_python_type_for_policy(policy: SemanticFieldPolicy) -> str:
    if is_controlled_reference_field(policy):
        base_type = get_python_type_for_controlled_reference(policy)
    else:
        base_type = get_python_type_for_base_kind(policy)
    if is_repeated_field(policy):
        return f"list[{base_type}]"
    return base_type

def build_domain_field_spec(
    policy: SemanticFieldPolicy,
    resolved_field_name: str,
) -> DomainFieldSpec:
    return DomainFieldSpec(
        field_name=resolved_field_name,
        python_type=resolve_python_type_for_policy(policy),
        code=policy.code,
        xml_paths=policy.xml_paths,
        required=is_required_field(policy),
        repeated=is_repeated_field(policy),
        domain_shape_kind=policy.domain_shape_kind.value,
        enum_eligibility=policy.enum_eligibility.value,
        trace={
            "code": policy.code,
            "xml_paths": policy.xml_paths,
            "base_kind": policy.base_kind.value,
            "domain_shape_kind": policy.domain_shape_kind.value,
            "enum_eligibility": policy.enum_eligibility.value,
        },
    )

def build_domain_generation_unit(
    group_key: str,
    policies: tuple[SemanticFieldPolicy, ...],
) -> DomainGenerationUnit:
    resolved_names = build_resolved_field_names(policies)
    sorted_policies = tuple(sorted(policies, key=lambda policy: policy.code))
    if group_key == "__no_tree__":
        module_name = "manual_only"
    elif group_key == "__no_cvn_item__":
        module_name = "tree_without_item"
    else:
        module_name = f"cvn_item_{group_key.replace('.', '_')}"
    class_name = "Unnamed"
    if sorted_policies:
        class_name = get_class_name_from_policy(sorted_policies[0])
    return DomainGenerationUnit(
        module_name=module_name,
        class_name=class_name,
        source_group_key=group_key,
        fields=tuple(
            build_domain_field_spec(
                policy=policy,
                resolved_field_name=resolved_names[policy.code],
            )
            for policy in sorted_policies
        ),
    )

def build_domain_generation_result(
    policy_index: dict[str, SemanticFieldPolicy],
    grouped_entries: dict[str, tuple[NormalizedCodeEntry, ...]],
) -> DomainGenerationResult:
    units = []
    for group_key in sorted(grouped_entries):
        entries = grouped_entries[group_key]
        sorted_entries = tuple(sorted(entries, key=lambda entry: entry.code))
        policies = tuple(policy_index[entry.code] for entry in sorted_entries)
        units.append(
            build_domain_generation_unit(
                group_key=group_key,
                policies=policies,
            )
        )
    sorted_codes = tuple(sorted(policy_index))
    normalized_entries = tuple(
        entry
        for group_key in sorted(grouped_entries)
        for entry in sorted(grouped_entries[group_key], key=lambda item: item.code)
    )
    return DomainGenerationResult(
        units=tuple(sorted(units, key=lambda unit: unit.module_name)),
        enums=(),
        normalized_entries=tuple(
            sorted(normalized_entries, key=lambda entry: entry.code)
        ),
        semantic_policies=tuple(policy_index[code] for code in sorted_codes),
    )