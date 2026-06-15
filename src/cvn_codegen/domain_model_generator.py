from cvn_codegen.normalization_types import (
    NormalizationResult,
    NormalizedCodeEntry
)
from cvn_codegen.semantic_policy import (
    SemanticFieldPolicy,
    SemanticPolicyBundle,

    build_semantic_field_policy,
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