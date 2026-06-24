import re

from collections import defaultdict
from decimal import Decimal

from cvn_codegen.normalization_types import (
    NormalizationResult,
    NormalizedCodeEntry,
    ReferenceTableEnumEvidence,

)
from cvn_codegen.semantic_policy import (
    SemanticFieldPolicy,
    SemanticPolicyBundle,
    SemanticBaseKind,
    CardinalityKind,
    PresenceKind,
    DomainShapeKind,
    EnumEligibility,
    build_semantic_field_policy,
    normalize_ascii_text,
)
from cvn_codegen.domain_model_types import (
    DomainFieldSpec,
    DomainGenerationResult,
    DomainGenerationUnit,
    DomainEnumSpec,

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
        sorted(
            (
                entry
                for group_key in sorted(grouped_entries)
                for entry in grouped_entries[group_key]
            ),
            key=lambda entry: entry.code,
        )
    )
    enum_specs = build_enum_specs_for_entries(
        entries=normalized_entries,
        policy_index=policy_index,
    )
    return DomainGenerationResult(
        units=tuple(sorted(units, key=lambda unit: unit.module_name)),
        enums=enum_specs,
        normalized_entries=normalized_entries,
        semantic_policies=tuple(policy_index[code] for code in sorted_codes),
    )

def should_emit_enum_for_policy(policy: SemanticFieldPolicy) -> bool:
    return (
        policy.domain_shape_kind == DomainShapeKind.STRICT_ENUM_CANDIDATE
        and policy.enum_eligibility == EnumEligibility.ELIGIBLE
    )

def build_enum_class_name(policy: SemanticFieldPolicy) -> str:
    base_name = get_class_name_from_policy(policy)
    if not base_name:
        return "UnnamedEnum"
    if base_name.endswith("Enum"):
        return base_name
    return f"{base_name}Enum"

def build_enum_member_name(
    preferred_label: str,
    code_value: str,
) -> str:
    normalized_label = normalize_ascii_text(preferred_label).upper()
    normalized_label = re.sub(r"[^A-Z0-9]+", "_", normalized_label).strip("_")
    if normalized_label and not normalized_label[0].isdigit():
        return normalized_label
    normalized_code = re.sub(r"[^A-Z0-9]+", "_", code_value.upper()).strip("_")
    if not normalized_code:
        normalized_code = "UNKNOWN"
    return f"CODE_{normalized_code}"

def get_enum_evidence_from_entry(
    entry: NormalizedCodeEntry,
) -> tuple[ReferenceTableEnumEvidence | None, str | None]:
    reference_resolution = entry.reference_resolution
    if reference_resolution is None:
        return None, None
    source_reference = (
        reference_resolution.resolved_name
        or reference_resolution.raw_reference
        or entry.code
    )
    evidence = reference_resolution.reference_table_enum_evidence
    if evidence is None:
        return None, source_reference
    return evidence, source_reference

def build_domain_enum_spec(
    policy: SemanticFieldPolicy,
    evidence: ReferenceTableEnumEvidence,
    source_reference: str,
) -> DomainEnumSpec:
    members_with_labels = sorted(
        zip(evidence.normalized_codes, evidence.preferred_labels),
        key=lambda item: item[0],
    )
    members = tuple(
        (
            build_enum_member_name(
                preferred_label=preferred_label,
                code_value=code_value,
            ),
            code_value,
        )
        for code_value, preferred_label in members_with_labels
    )
    labels = {
        code_value: preferred_label
        for code_value, preferred_label in members_with_labels
    }
    return DomainEnumSpec(
        class_name=build_enum_class_name(policy),
        source_reference=source_reference,
        members=members,
        labels=labels,
        trace={
            "code": policy.code,
            "xml_paths": policy.xml_paths,
            "source_reference": source_reference,
            "domain_shape_kind": policy.domain_shape_kind.value,
            "enum_eligibility": policy.enum_eligibility.value,
        },
    )

def build_enum_specs_for_entries(
    entries: tuple[NormalizedCodeEntry, ...],
    policy_index: dict[str, SemanticFieldPolicy],
) -> tuple[DomainEnumSpec, ...]:
    enum_specs_by_source_reference: dict[str, DomainEnumSpec] = {}
    for entry in sorted(entries, key=lambda item: item.code):
        policy = policy_index[entry.code]
        if not should_emit_enum_for_policy(policy):
            continue
        evidence, source_reference = get_enum_evidence_from_entry(entry)
        if evidence is None or source_reference is None:
            continue
        if source_reference in enum_specs_by_source_reference:
            continue
        enum_specs_by_source_reference[source_reference] = build_domain_enum_spec(
            policy=policy,
            evidence=evidence,
            source_reference=source_reference,
        )
    return tuple(
        sorted(
            enum_specs_by_source_reference.values(),
            key=lambda enum_spec: enum_spec.class_name,
        )
    )


def render_field_annotation(field: DomainFieldSpec) -> str:
    if field.repeated:
        return field.python_type

    if field.required:
        return field.python_type

    return f"{field.python_type} | None"


def render_field_default(field: DomainFieldSpec) -> str:
    if field.repeated:
        return "Field(default_factory=list)"

    if field.required:
        return "Field(...)"

    return "Field(default=None)"


def render_field_line(field: DomainFieldSpec) -> str:
    annotation = render_field_annotation(field)
    default = render_field_default(field)
    return f"    {field.field_name}: {annotation} = {default}"


def extract_base_type_names(type_expression: str) -> tuple[str, ...]:
    normalized = (
        type_expression
        .replace("[", " ")
        .replace("]", " ")
        .replace("|", " ")
        .replace(",", " ")
    )
    parts = tuple(
        part
        for part in normalized.split()
        if part
    )
    ignored = {"list", "None"}
    return tuple(
        part
        for part in parts
        if part not in ignored
    )


def collect_unit_import_types(
    unit: DomainGenerationUnit,
) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    stdlib_types: set[str] = set()
    shared_component_types: set[str] = {"BaseCvnDomainModel"}
    enum_types: set[str] = set()

    shared_component_type_names = {
        "OpenCodedValue",
        "MeasureOrScaleValue",
        "IdentifierReference",
        "ScopeReference",
        "SubtypeBackedValue",
        "HierarchicalCodeReference",
        "RegistryReference",
        "VocabularyReference",
        "UnresolvedReference",
        "UnderTracedReference",
    }

    for field in unit.fields:
        for type_name in extract_base_type_names(field.python_type):
            if type_name == "Decimal":
                stdlib_types.add("Decimal")
            elif type_name.endswith("Enum"):
                enum_types.add(type_name)
            elif type_name in shared_component_type_names:
                shared_component_types.add(type_name)

    return (
        tuple(sorted(stdlib_types)),
        tuple(sorted(shared_component_types)),
        tuple(sorted(enum_types)),
    )


def render_unit_class(unit: DomainGenerationUnit) -> str:
    class_lines = [f"class {unit.class_name}(BaseCvnDomainModel):"]

    if not unit.fields:
        class_lines.append("    pass")
        return "\n".join(class_lines)

    class_lines.extend(
        render_field_line(field)
        for field in unit.fields
    )
    return "\n".join(class_lines)


def render_unit_module(unit: DomainGenerationUnit) -> str:
    stdlib_types, shared_component_types, enum_types = collect_unit_import_types(unit)

    lines = [
        "# Generated by cvn domain model generator. Do not edit manually.",
        "from __future__ import annotations",
        "",
    ]

    if stdlib_types:
        if stdlib_types == ("Decimal",):
            lines.append("from decimal import Decimal")
        else:
            lines.append(
                f"from decimal import {', '.join(stdlib_types)}"
            )
        lines.append("")

    lines.append("from pydantic import Field")
    lines.append("")

    lines.append(
        "from models.cvn.components import "
        + ", ".join(shared_component_types)
    )

    if enum_types:
        lines.append("")
        lines.append(f"from .enums import {', '.join(enum_types)}")

    lines.append("")
    lines.append("")
    lines.append(render_unit_class(unit))
    lines.append("")

    return "\n".join(lines)


def render_enums_module(
    enums: tuple[DomainEnumSpec, ...],
) -> str:
    lines = [
        "# Generated by cvn domain model generator. Do not edit manually.",
        "from __future__ import annotations",
        "",
        "from enum import Enum",
        "",
    ]

    for index, enum_spec in enumerate(sorted(enums, key=lambda item: item.class_name)):
        lines.append(f"class {enum_spec.class_name}(str, Enum):")

        if not enum_spec.members:
            lines.append("    pass")
        else:
            for member_name, code_value in enum_spec.members:
                lines.append(f'    {member_name} = "{code_value}"')

        if index != len(enums) - 1:
            lines.append("")

    lines.append("")
    lines.append("")
    return "\n".join(lines)


def render_generated_package_init(
    result: DomainGenerationResult,
) -> str:
    lines = [
        "# Generated by cvn domain model generator. Do not edit manually.",
        "from __future__ import annotations",
        "",
    ]

    exported_names: list[str] = []

    for unit in sorted(result.units, key=lambda item: (item.module_name, item.class_name)):
        lines.append(f"from .{unit.module_name} import {unit.class_name}")
        exported_names.append(unit.class_name)

    if result.enums:
        if result.units:
            lines.append("")
        enum_names = [
            enum_spec.class_name
            for enum_spec in sorted(result.enums, key=lambda item: item.class_name)
        ]
        lines.append(f"from .enums import {', '.join(enum_names)}")
        exported_names.extend(enum_names)

    lines.append("")
    lines.append("__all__ = [")
    for exported_name in exported_names:
        lines.append(f'    "{exported_name}",')
    lines.append("]")
    lines.append("")
    lines.append("")

    return "\n".join(lines)


def render_domain_generation_result(
    result: DomainGenerationResult,
) -> dict[str, str]:
    rendered_files: dict[str, str] = {}

    for unit in result.units:
        rendered_files[f"{unit.module_name}.py"] = render_unit_module(unit)

    rendered_files["enums.py"] = render_enums_module(result.enums)
    rendered_files["__init__.py"] = render_generated_package_init(result)

    return rendered_files
