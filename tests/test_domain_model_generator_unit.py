from pathlib import Path

import pytest
import importlib
import sys

from cvn_codegen.domain_model_generator import (
    build_domain_enum_spec,
    build_domain_field_spec,
    build_domain_generation_result,
    build_domain_generation_unit,
    collect_unit_import_types,
    build_enum_class_name,
    build_enum_member_name,
    build_enum_specs_for_entries,
    build_resolved_field_names,
    build_semantic_policy_index,
    generate_domain_models,
    get_class_name_from_policy,
    get_canonical_generation_paths,
    get_enum_evidence_from_entry,
    get_field_name_from_policy,
    get_python_type_for_base_kind,
    get_python_type_for_controlled_reference,
    group_entries_by_cvn_item_code,
    is_controlled_reference_field,
    is_repeated_field,
    is_required_field,
    main,
    render_domain_generation_result,
    render_enums_module,
    render_field_annotation,
    render_field_default,
    render_field_line,
    render_generated_package_init,
    render_unit_class,
    render_unit_module,
    resolve_field_name_collisions,
    resolve_python_type_for_policy,
    should_emit_enum_for_policy,
    write_rendered_domain_files,
)

from cvn_codegen.normalization_types import (
    ManualCodeEntry,
    NormalizedCodeEntry,
    NormalizationResult,
    ReferenceResolution,
    ReferenceResolutionStatus,
    ReferenceResolutionTrace,
    ReferenceSourceFamily,
    ReferenceTableEnumEvidence,
    SemanticReferenceKind,
    SerializationPattern,
    SourceTrace,
    TreePathEntry,
)
from cvn_codegen.domain_model_types import (
    DomainEnumSpec,
    DomainFieldSpec,
    DomainGenerationResult,
    DomainGenerationUnit,
)

from cvn_codegen.semantic_policy import (
    SemanticFieldPolicy,
    build_default_semantic_policy_bundle,
    build_semantic_field_policy,
)
from models.cvn.components import (
    BaseCvnDomainModel,
    BaseControlledReferenceValue,
    CvnTrace,
    HierarchicalCodeReference,
    IdentifierReference,
    MeasureOrScaleValue,
    OpenCodedValue,
    RegistryReference,
    ScopeReference,
    SubtypeBackedValue,
    UnderTracedReference,
    UnresolvedReference,
    VocabularyReference,
)


def build_normalized_entry(
    *,
    code: str = "000.000.000.000",
    manual_type: str | None = "Alphanumeric",
    reference_resolution: ReferenceResolution | None = None,
    manual_obligatory: bool | None = False,
    manual_multiplicity: bool | None = False,
    manual_name: str | None = "Nombre de prueba",
    manual_short_name: str | None = "Prueba",
    xml_path: str | None = None,
) -> NormalizedCodeEntry:
    manual_entry = None
    if manual_type is not None:
        manual_entry = ManualCodeEntry(
            code=code,
            manual_name=manual_name,
            manual_short_name=manual_short_name,
            manual_type=manual_type,
            manual_obligatory=manual_obligatory,
            manual_multiplicity=manual_multiplicity,
            manual_reference_table=None,
        )

    tree_paths: tuple[TreePathEntry, ...] = ()
    source_files: tuple[str, ...] = ("SpecificationManual.xml",)
    if xml_path is not None:
        tree_paths = (
            TreePathEntry(
                code=code,
                tree_cvn_item_code=None,
                tree_property_name="TestProperty",
                tree_indicator_name="TestIndicator",
                tree_value=None,
                xml_path=xml_path,
                trace=SourceTrace(
                    source_file="CVNTreeModel.xml",
                    xml_path=xml_path,
                    source_code=code,
                ),
            ),
        )
        source_files = ("CVNTreeModel.xml", "SpecificationManual.xml")

    return NormalizedCodeEntry(
        code=code,
        manual=manual_entry,
        tree_paths=tree_paths,
        source_files=source_files,
        reference_resolution=reference_resolution,
    )


def build_reference_table_enum_evidence(
    *,
    table_name: str = "CVN_TEST",
    item_count: int = 2,
    has_hierarchy: bool = False,
    has_delegate: bool = False,
    has_other_like_entry: bool = False,
    has_duplicate_codes: bool = False,
    has_duplicate_preferred_labels: bool = False,
    has_blank_code: bool = False,
    has_blank_preferred_label: bool = False,
) -> ReferenceTableEnumEvidence:
    return ReferenceTableEnumEvidence(
        table_name=table_name,
        item_count=item_count,
        has_hierarchy=has_hierarchy,
        has_delegate=has_delegate,
        has_other_like_entry=has_other_like_entry,
        has_duplicate_codes=has_duplicate_codes,
        has_duplicate_preferred_labels=has_duplicate_preferred_labels,
        has_blank_code=has_blank_code,
        has_blank_preferred_label=has_blank_preferred_label,
        normalized_codes=("000", "010"),
        preferred_labels=("Uno", "Dos"),
        normalized_preferred_labels=("UNO", "DOS"),
        open_world_signals=(),
    )


def clear_generated_imports() -> dict[str, object]:
    saved_modules = {
        module_name: module
        for module_name, module in sys.modules.items()
        if module_name == "generated" or module_name.startswith("generated.")
    }
    for module_name in tuple(saved_modules):
        sys.modules.pop(module_name, None)
    importlib.invalidate_caches()
    return saved_modules


def restore_generated_imports(saved_modules: dict[str, object]) -> None:
    for module_name in tuple(sys.modules):
        if module_name == "generated" or module_name.startswith("generated."):
            sys.modules.pop(module_name, None)
    sys.modules.update(saved_modules)
    importlib.invalidate_caches()

def build_test_entry_with_tree_path(
    code: str,
    tree_cvn_item_code: str | None,
    xml_path: str,
) -> NormalizedCodeEntry:
    return NormalizedCodeEntry(
        code=code,
        manual=ManualCodeEntry(
            code=code,
            manual_name=f"Campo {code}",
            manual_short_name=None,
            manual_type="Alphanumeric",
            manual_obligatory=False,
            manual_multiplicity=False,
            manual_reference_table=None,
        ),
        tree_paths=(
            TreePathEntry(
                code=code,
                tree_cvn_item_code=tree_cvn_item_code,
                tree_property_name="TestProperty",
                tree_indicator_name="TestIndicator",
                tree_value=None,
                xml_path=xml_path,
                trace=SourceTrace(
                    source_file="CVNTreeModel.xml",
                    xml_path=xml_path,
                    source_code=code,
                ),
            ),
        ),
        source_files=("SpecificationManual.xml", "CVNTreeModel.xml"),
    )



def build_test_entry(code: str) -> NormalizedCodeEntry:
    return NormalizedCodeEntry(
        code=code,
        manual=ManualCodeEntry(
            code=code,
            manual_name=f"Campo {code}",
            manual_short_name=None,
            manual_type="Alphanumeric",
            manual_obligatory=False,
            manual_multiplicity=False,
            manual_reference_table=None,
        ),
        tree_paths=(),
        source_files=("SpecificationManual.xml",),
    )

def build_reference_resolution(
    *,
    raw_reference: str = "CVN_TEST",
    semantic_kind: SemanticReferenceKind = SemanticReferenceKind.COMPACT_ENUM_LIKE_TABLE,
    serialization_pattern: SerializationPattern = SerializationPattern.FILTER_VALUE,
    source_family: ReferenceSourceFamily = ReferenceSourceFamily.REFERENCE_TABLE,
    reference_table_enum_evidence: ReferenceTableEnumEvidence | None = None,
) -> ReferenceResolution:
    return ReferenceResolution(
        raw_reference=raw_reference,
        status=ReferenceResolutionStatus.RESOLVED,
        source_family=source_family,
        source_artifact="ReferenceTables.xml",
        resolved_name=raw_reference,
        serialization_pattern=serialization_pattern,
        semantic_kind=semantic_kind,
        is_subtype_backed=False,
        subtype_metadata_present=None,
        diagnostic_message=None,
        trace=ReferenceResolutionTrace(
            manual_reference=raw_reference,
            resolved_from_artifact="ReferenceTables.xml",
            resolution_rule="test_reference_resolution",
        ),
        reference_table_enum_evidence=reference_table_enum_evidence,
    )

def test_build_semantic_policy_index_is_sorted_by_code():
    normalization_result = NormalizationResult(
        by_code={
            "002": build_test_entry("002"),
            "001": build_test_entry("001"),
        },
        by_xml_path={},
        manual_only_codes=(),
        tree_only_codes=(),
        mismatches=(),
    )
    bundle = build_default_semantic_policy_bundle()

    policy_index = build_semantic_policy_index(normalization_result, bundle)

    assert tuple(policy_index) == ("001", "002")

def test_build_semantic_policy_index_preserves_policy_trace():
    normalization_result = NormalizationResult(
        by_code={
            "001": build_test_entry("001"),
        },
        by_xml_path={},
        manual_only_codes=(),
        tree_only_codes=(),
        mismatches=(),
    )
    bundle = build_default_semantic_policy_bundle()

    policy_index = build_semantic_policy_index(normalization_result, bundle)

    policy = policy_index["001"]
    assert isinstance(policy, SemanticFieldPolicy)
    assert policy.code == "001"
    assert policy.decision_trace.code == "001"

def test_build_semantic_policy_index_covers_all_normalized_entries():
    normalization_result = NormalizationResult(
        by_code={
            "003": build_test_entry("003"),
            "001": build_test_entry("001"),
            "002": build_test_entry("002"),
        },
        by_xml_path={},
        manual_only_codes=(),
        tree_only_codes=(),
        mismatches=(),
    )
    bundle = build_default_semantic_policy_bundle()

    policy_index = build_semantic_policy_index(normalization_result, bundle)

    assert len(policy_index) == 3
    assert set(policy_index) == {"001", "002", "003"}


def test_group_entries_by_cvn_item_code_groups_entries_by_tree_item():
    entries = {
        "002": build_test_entry_with_tree_path(
            code="002",
            tree_cvn_item_code="060.010.000.000",
            xml_path="/Node/CVNItem[@code='060.010.000.000']/Property[@name='B']",
        ),
        "001": build_test_entry_with_tree_path(
            code="001",
            tree_cvn_item_code="060.010.000.000",
            xml_path="/Node/CVNItem[@code='060.010.000.000']/Property[@name='A']",
        ),
    }

    grouped = group_entries_by_cvn_item_code(entries)

    assert tuple(grouped) == ("060.010.000.000",)
    assert tuple(entry.code for entry in grouped["060.010.000.000"]) == ("001", "002")

def test_group_entries_by_cvn_item_code_puts_entries_without_tree_paths_in_no_tree():
    entries = {
        "001": build_test_entry("001"),
    }

    grouped = group_entries_by_cvn_item_code(entries)

    assert tuple(grouped) == ("__no_tree__",)
    assert tuple(entry.code for entry in grouped["__no_tree__"]) == ("001",)

def test_group_entries_by_cvn_item_code_puts_entries_without_item_code_in_no_cvn_item():
    entries = {
        "001": build_test_entry_with_tree_path(
            code="001",
            tree_cvn_item_code=None,
            xml_path="/Node/Agent/Property[@name='Test']",
        ),
    }

    grouped = group_entries_by_cvn_item_code(entries)

    assert tuple(grouped) == ("__no_cvn_item__",)
    assert tuple(entry.code for entry in grouped["__no_cvn_item__"]) == ("001",)

def test_group_entries_by_cvn_item_code_does_not_duplicate_entry_with_same_group_key():
    entry = NormalizedCodeEntry(
        code="001",
        manual=ManualCodeEntry(
            code="001",
            manual_name="Campo 001",
            manual_short_name=None,
            manual_type="Alphanumeric",
            manual_obligatory=False,
            manual_multiplicity=False,
            manual_reference_table=None,
        ),
        tree_paths=(
            TreePathEntry(
                code="001",
                tree_cvn_item_code="060.010.000.000",
                tree_property_name="A",
                tree_indicator_name=None,
                tree_value=None,
                xml_path="/Node/CVNItem[@code='060.010.000.000']/Property[@name='A']",
                trace=SourceTrace(
                    source_file="CVNTreeModel.xml",
                    xml_path="/Node/CVNItem[@code='060.010.000.000']/Property[@name='A']",
                    source_code="001",
                ),
            ),
            TreePathEntry(
                code="001",
                tree_cvn_item_code="060.010.000.000",
                tree_property_name="B",
                tree_indicator_name=None,
                tree_value=None,
                xml_path="/Node/CVNItem[@code='060.010.000.000']/Property[@name='B']",
                trace=SourceTrace(
                    source_file="CVNTreeModel.xml",
                    xml_path="/Node/CVNItem[@code='060.010.000.000']/Property[@name='B']",
                    source_code="001",
                ),
            ),
        ),
        source_files=("SpecificationManual.xml", "CVNTreeModel.xml"),
    )

    grouped = group_entries_by_cvn_item_code({"001": entry})

    assert tuple(grouped) == ("060.010.000.000",)
    assert tuple(item.code for item in grouped["060.010.000.000"]) == ("001",)
    assert len(grouped["060.010.000.000"]) == 1

def test_get_field_name_from_policy_returns_semantic_policy_name():
    entry = build_normalized_entry(
        code="001",
        manual_name="Título del proyecto",
    )
    bundle = build_default_semantic_policy_bundle()

    policy = build_semantic_field_policy(entry, bundle)

    assert get_field_name_from_policy(policy) == "titulo_del_proyecto"


def test_get_class_name_from_policy_returns_semantic_policy_class_name():
    entry = build_normalized_entry(
        code="001",
        manual_name="Título del proyecto",
    )
    bundle = build_default_semantic_policy_bundle()
    policy = build_semantic_field_policy(entry, bundle)
    assert get_class_name_from_policy(policy) == "TituloDelProyecto"

def test_resolve_field_name_collisions_uses_clean_name_and_code_suffix_on_collision():
    bundle = build_default_semantic_policy_bundle()
    entry_a = build_normalized_entry(
        code="001.002",
        manual_name="Título",
    )
    entry_b = build_normalized_entry(
        code="003.004",
        manual_name="Título",
    )
    entry_c = build_normalized_entry(
        code="005.006",
        manual_name="Resumen",
    )
    policy_a = build_semantic_field_policy(entry_a, bundle)
    policy_b = build_semantic_field_policy(entry_b, bundle)
    policy_c = build_semantic_field_policy(entry_c, bundle)
    resolved = resolve_field_name_collisions((policy_b, policy_c, policy_a))
    assert resolved["001.002"] == "titulo_001_002"
    assert resolved["003.004"] == "titulo_003_004"
    assert resolved["005.006"] == "resumen"

def test_build_resolved_field_names_returns_final_names_for_block():
    bundle = build_default_semantic_policy_bundle()
    entry_a = build_normalized_entry(
        code="001.002",
        manual_name="Título",
    )
    entry_b = build_normalized_entry(
        code="003.004",
        manual_name="Título",
    )
    entry_c = build_normalized_entry(
        code="005.006",
        manual_name="Resumen",
    )
    policy_a = build_semantic_field_policy(entry_a, bundle)
    policy_b = build_semantic_field_policy(entry_b, bundle)
    policy_c = build_semantic_field_policy(entry_c, bundle)
    resolved = build_resolved_field_names((policy_a, policy_b, policy_c))
    assert resolved == {
        "001.002": "titulo_001_002",
        "003.004": "titulo_003_004",
        "005.006": "resumen",
    }

from cvn_codegen.domain_model_generator import get_python_type_for_base_kind
def test_get_python_type_for_base_kind_maps_supported_base_kinds():
    bundle = build_default_semantic_policy_bundle()
    text_policy = build_semantic_field_policy(
        build_normalized_entry(code="001", manual_type="Alphanumeric"),
        bundle,
    )
    boolean_policy = build_semantic_field_policy(
        build_normalized_entry(code="002", manual_type="Boolean"),
        bundle,
    )
    decimal_policy = build_semantic_field_policy(
        build_normalized_entry(code="003", manual_type="Double"),
        bundle,
    )
    date_policy = build_semantic_field_policy(
        build_normalized_entry(code="004", manual_type="Date"),
        bundle,
    )
    duration_policy = build_semantic_field_policy(
        build_normalized_entry(code="005", manual_type="Duration"),
        bundle,
    )
    unknown_policy = build_semantic_field_policy(
        build_normalized_entry(code="006", manual_type="UnexpectedType"),
        bundle,
    )
    assert get_python_type_for_base_kind(text_policy) == "str"
    assert get_python_type_for_base_kind(boolean_policy) == "bool"
    assert get_python_type_for_base_kind(decimal_policy) == "Decimal"
    assert get_python_type_for_base_kind(date_policy) == "str"
    assert get_python_type_for_base_kind(duration_policy) == "str"
    assert get_python_type_for_base_kind(unknown_policy) == "object"

def test_is_repeated_field_returns_true_only_for_repeated_cardinality():
    bundle = build_default_semantic_policy_bundle()
    repeated_policy = build_semantic_field_policy(
        build_normalized_entry(code="001", manual_multiplicity=True),
        bundle,
    )
    single_policy = build_semantic_field_policy(
        build_normalized_entry(code="002", manual_multiplicity=False),
        bundle,
    )
    assert is_repeated_field(repeated_policy) is True
    assert is_repeated_field(single_policy) is False
def test_is_required_field_returns_true_only_for_required_presence():
    bundle = build_default_semantic_policy_bundle()
    required_policy = build_semantic_field_policy(
        build_normalized_entry(code="001", manual_obligatory=True),
        bundle,
    )
    optional_policy = build_semantic_field_policy(
        build_normalized_entry(code="002", manual_obligatory=False),
        bundle,
    )
    assert is_required_field(required_policy) is True
    assert is_required_field(optional_policy) is False
def test_is_controlled_reference_field_detects_controlled_reference_base_kind():
    bundle = build_default_semantic_policy_bundle()
    controlled_policy = build_semantic_field_policy(
        build_normalized_entry(
            code="001",
            manual_type="Alphanumeric",
            reference_resolution=build_reference_resolution(),
        ),
        bundle,
    )
    text_policy = build_semantic_field_policy(
        build_normalized_entry(code="002", manual_type="Alphanumeric"),
        bundle,
    )
    assert is_controlled_reference_field(controlled_policy) is True
    assert is_controlled_reference_field(text_policy) is False
def test_get_python_type_for_controlled_reference_maps_supported_domain_shapes():
    bundle = build_default_semantic_policy_bundle()
    open_coded_policy = build_semantic_field_policy(
        build_normalized_entry(
            code="001",
            reference_resolution=build_reference_resolution(
                semantic_kind=SemanticReferenceKind.COMPACT_SCALE_OR_MEASURE,
                serialization_pattern=SerializationPattern.QUALITY_MEASURE,
            ),
        ),
        bundle,
    )
    registry_policy = build_semantic_field_policy(
        build_normalized_entry(
            code="002",
            reference_resolution=build_reference_resolution(
                raw_reference="ENTITY@Entity.xsd",
                semantic_kind=SemanticReferenceKind.SIDE_PACKAGE_REGISTRY,
                serialization_pattern=SerializationPattern.SIDE_PACKAGE_REGISTRY,
                source_family=ReferenceSourceFamily.SIDE_PACKAGE_REGISTRY,
            ),
        ),
        bundle,
    )
    unresolved_policy = build_semantic_field_policy(
        build_normalized_entry(
            code="003",
            reference_resolution=build_reference_resolution(
                raw_reference="CVN_AGENCY_C",
                semantic_kind=SemanticReferenceKind.UNRESOLVED_MANUAL_ONLY_REFERENCE,
                serialization_pattern=SerializationPattern.UNRESOLVED,
                source_family=ReferenceSourceFamily.UNRESOLVED_MANUAL_ONLY,
            ),
        ),
        bundle,
    )
    assert get_python_type_for_controlled_reference(open_coded_policy) == "MeasureOrScaleValue"
    assert get_python_type_for_controlled_reference(registry_policy) == "RegistryReference"
    assert get_python_type_for_controlled_reference(unresolved_policy) == "UnresolvedReference"
def test_resolve_python_type_for_policy_maps_scalar_and_repeated_shapes():
    bundle = build_default_semantic_policy_bundle()
    scalar_policy = build_semantic_field_policy(
        build_normalized_entry(code="001", manual_type="Boolean"),
        bundle,
    )
    repeated_scalar_policy = build_semantic_field_policy(
        build_normalized_entry(
            code="002",
            manual_type="Double",
            manual_multiplicity=True,
        ),
        bundle,
    )
    repeated_controlled_policy = build_semantic_field_policy(
        build_normalized_entry(
            code="003",
            manual_type="Alphanumeric",
            manual_multiplicity=True,
            reference_resolution=build_reference_resolution(
                raw_reference="ENTITY@Entity.xsd",
                semantic_kind=SemanticReferenceKind.SIDE_PACKAGE_REGISTRY,
                serialization_pattern=SerializationPattern.SIDE_PACKAGE_REGISTRY,
                source_family=ReferenceSourceFamily.SIDE_PACKAGE_REGISTRY,
            ),
        ),
        bundle,
    )
    assert resolve_python_type_for_policy(scalar_policy) == "bool"
    assert resolve_python_type_for_policy(repeated_scalar_policy) == "list[Decimal]"
    assert resolve_python_type_for_policy(repeated_controlled_policy) == "list[RegistryReference]"
def test_build_domain_field_spec_builds_expected_spec():
    bundle = build_default_semantic_policy_bundle()
    policy = build_semantic_field_policy(
        build_normalized_entry(
            code="001.002",
            manual_name="Título",
            manual_type="Alphanumeric",
            manual_obligatory=True,
            manual_multiplicity=False,
        ),
        bundle,
    )
    spec = build_domain_field_spec(
        policy=policy,
        resolved_field_name="titulo",
    )
    assert spec.field_name == "titulo"
    assert spec.python_type == "str"
    assert spec.code == "001.002"
    assert spec.xml_paths == ()
    assert spec.required is True
    assert spec.repeated is False
    assert spec.domain_shape_kind == policy.domain_shape_kind.value
    assert spec.enum_eligibility == policy.enum_eligibility.value
    assert spec.trace["code"] == "001.002"
    assert spec.trace["base_kind"] == policy.base_kind.value
    assert spec.trace["domain_shape_kind"] == policy.domain_shape_kind.value
    assert spec.trace["enum_eligibility"] == policy.enum_eligibility.value
def test_build_domain_generation_unit_builds_sorted_field_specs():
    bundle = build_default_semantic_policy_bundle()
    policy_a = build_semantic_field_policy(
        build_normalized_entry(
            code="003.004",
            manual_name="Título",
            manual_type="Alphanumeric",
        ),
        bundle,
    )
    policy_b = build_semantic_field_policy(
        build_normalized_entry(
            code="001.002",
            manual_name="Título",
            manual_type="Alphanumeric",
        ),
        bundle,
    )
    policy_c = build_semantic_field_policy(
        build_normalized_entry(
            code="005.006",
            manual_name="Resumen",
            manual_type="Alphanumeric",
        ),
        bundle,
    )
    unit = build_domain_generation_unit(
        group_key="060.010.000.000",
        policies=(policy_a, policy_c, policy_b),
    )
    assert unit.module_name == "cvn_item_060_010_000_000"
    assert unit.class_name == "Titulo"
    assert unit.source_group_key == "060.010.000.000"
    assert tuple(field.code for field in unit.fields) == (
        "001.002",
        "003.004",
        "005.006",
    )
    assert tuple(field.field_name for field in unit.fields) == (
        "titulo_001_002",
        "titulo_003_004",
        "resumen",
    )
def test_build_domain_generation_unit_uses_manual_only_module_name_for_no_tree_group():
    bundle = build_default_semantic_policy_bundle()
    policy = build_semantic_field_policy(
        build_normalized_entry(
            code="001.002",
            manual_name="Resumen",
            manual_type="Alphanumeric",
        ),
        bundle,
    )
    unit = build_domain_generation_unit(
        group_key="__no_tree__",
        policies=(policy,),
    )
    assert unit.module_name == "manual_only"
    assert unit.class_name == "Resumen"
def test_build_domain_generation_unit_uses_tree_without_item_module_name_for_no_cvn_item_group():
    bundle = build_default_semantic_policy_bundle()
    policy = build_semantic_field_policy(
        build_normalized_entry(
            code="001.002",
            manual_name="Resumen",
            manual_type="Alphanumeric",
        ),
        bundle,
    )
    unit = build_domain_generation_unit(
        group_key="__no_cvn_item__",
        policies=(policy,),
    )
    assert unit.module_name == "tree_without_item"
    assert unit.class_name == "Resumen"
def test_build_domain_generation_result_builds_units_and_preserves_sorted_entries_and_policies():
    bundle = build_default_semantic_policy_bundle()
    entry_a = build_test_entry_with_tree_path(
        code="002",
        tree_cvn_item_code="060.010.000.000",
        xml_path="/Node/CVNItem[@code='060.010.000.000']/Property[@name='B']",
    )
    entry_b = build_test_entry_with_tree_path(
        code="001",
        tree_cvn_item_code="060.010.000.000",
        xml_path="/Node/CVNItem[@code='060.010.000.000']/Property[@name='A']",
    )
    entry_c = build_test_entry("003")
    policy_index = {
        "002": build_semantic_field_policy(entry_a, bundle),
        "001": build_semantic_field_policy(entry_b, bundle),
        "003": build_semantic_field_policy(entry_c, bundle),
    }
    grouped_entries = {
        "060.010.000.000": (entry_a, entry_b),
        "__no_tree__": (entry_c,),
    }
    result = build_domain_generation_result(
        policy_index=policy_index,
        grouped_entries=grouped_entries,
    )
    assert tuple(unit.module_name for unit in result.units) == (
        "cvn_item_060_010_000_000",
        "manual_only",
    )
    assert result.enums == ()
    assert tuple(entry.code for entry in result.normalized_entries) == (
        "001",
        "002",
        "003",
    )
    assert tuple(policy.code for policy in result.semantic_policies) == (
        "001",
        "002",
        "003",
    )

def test_should_emit_enum_for_policy_returns_true_only_for_eligible_strict_enum_candidates():
    bundle = build_default_semantic_policy_bundle()
    eligible_policy = build_semantic_field_policy(
        build_normalized_entry(
            code="001",
            manual_type="Alphanumeric",
            reference_resolution=build_reference_resolution(
                raw_reference="CVN_SEX_A",
                semantic_kind=SemanticReferenceKind.COMPACT_ENUM_LIKE_TABLE,
                serialization_pattern=SerializationPattern.FILTER_VALUE,
                reference_table_enum_evidence=build_reference_table_enum_evidence(
                    table_name="CVN_SEX_A",
                    item_count=2,
                ),
            ),
        ),
        bundle,
    )
    review_policy = build_semantic_field_policy(
        build_normalized_entry(
            code="002",
            manual_type="Alphanumeric",
            reference_resolution=build_reference_resolution(
                raw_reference="CVN_OTHER",
                semantic_kind=SemanticReferenceKind.COMPACT_ENUM_LIKE_TABLE,
                serialization_pattern=SerializationPattern.FILTER_VALUE,
                reference_table_enum_evidence=build_reference_table_enum_evidence(
                    table_name="CVN_OTHER",
                    item_count=2,
                    has_other_like_entry=True,
                ),
            ),
        ),
        bundle,
    )
    non_enum_policy = build_semantic_field_policy(
        build_normalized_entry(
            code="003",
            manual_type="Alphanumeric",
            reference_resolution=build_reference_resolution(
                raw_reference="ENTITY@Entity.xsd",
                semantic_kind=SemanticReferenceKind.SIDE_PACKAGE_REGISTRY,
                serialization_pattern=SerializationPattern.SIDE_PACKAGE_REGISTRY,
                source_family=ReferenceSourceFamily.SIDE_PACKAGE_REGISTRY,
            ),
        ),
        bundle,
    )
    assert should_emit_enum_for_policy(eligible_policy) is True
    assert should_emit_enum_for_policy(review_policy) is False
    assert should_emit_enum_for_policy(non_enum_policy) is False
def test_build_enum_class_name_adds_enum_suffix():
    bundle = build_default_semantic_policy_bundle()
    policy = build_semantic_field_policy(
        build_normalized_entry(
            code="001",
            manual_name="Sexo",
            manual_type="Alphanumeric",
            reference_resolution=build_reference_resolution(
                raw_reference="CVN_SEX_A",
                semantic_kind=SemanticReferenceKind.COMPACT_ENUM_LIKE_TABLE,
                serialization_pattern=SerializationPattern.FILTER_VALUE,
                reference_table_enum_evidence=build_reference_table_enum_evidence(
                    table_name="CVN_SEX_A",
                    item_count=2,
                ),
            ),
        ),
        bundle,
    )
    assert build_enum_class_name(policy) == "SexoEnum"
def test_build_enum_member_name_uses_label_or_code_fallback():
    assert build_enum_member_name("Mujer", "000") == "MUJER"
    assert build_enum_member_name("Hombre", "010") == "HOMBRE"
    assert build_enum_member_name("", "010") == "CODE_010"
    assert build_enum_member_name("3 años", "003") == "CODE_003"
def test_get_enum_evidence_from_entry_returns_evidence_and_source_reference():
    entry = build_normalized_entry(
        code="001",
        manual_type="Alphanumeric",
        reference_resolution=build_reference_resolution(
            raw_reference="CVN_SEX_A",
            semantic_kind=SemanticReferenceKind.COMPACT_ENUM_LIKE_TABLE,
            serialization_pattern=SerializationPattern.FILTER_VALUE,
            reference_table_enum_evidence=build_reference_table_enum_evidence(
                table_name="CVN_SEX_A",
                item_count=2,
            ),
        ),
    )
    evidence, source_reference = get_enum_evidence_from_entry(entry)
    assert evidence is not None
    assert evidence.table_name == "CVN_SEX_A"
    assert source_reference == "CVN_SEX_A"
def test_get_enum_evidence_from_entry_returns_none_when_resolution_missing():
    entry = build_normalized_entry(
        code="001",
        manual_type="Alphanumeric",
        reference_resolution=None,
    )
    evidence, source_reference = get_enum_evidence_from_entry(entry)
    assert evidence is None
    assert source_reference is None
def test_build_domain_enum_spec_builds_expected_enum_spec():
    bundle = build_default_semantic_policy_bundle()
    policy = build_semantic_field_policy(
        build_normalized_entry(
            code="001",
            manual_name="Sexo",
            manual_type="Alphanumeric",
            reference_resolution=build_reference_resolution(
                raw_reference="CVN_SEX_A",
                semantic_kind=SemanticReferenceKind.COMPACT_ENUM_LIKE_TABLE,
                serialization_pattern=SerializationPattern.FILTER_VALUE,
                reference_table_enum_evidence=ReferenceTableEnumEvidence(
                    table_name="CVN_SEX_A",
                    item_count=2,
                    has_hierarchy=False,
                    has_delegate=False,
                    has_other_like_entry=False,
                    has_duplicate_codes=False,
                    has_duplicate_preferred_labels=False,
                    has_blank_code=False,
                    has_blank_preferred_label=False,
                    normalized_codes=("000", "010"),
                    preferred_labels=("Mujer", "Hombre"),
                    normalized_preferred_labels=("MUJER", "HOMBRE"),
                    open_world_signals=(),
                ),
            ),
        ),
        bundle,
    )
    evidence, source_reference = get_enum_evidence_from_entry(
        build_normalized_entry(
            code="001",
            manual_type="Alphanumeric",
            reference_resolution=build_reference_resolution(
                raw_reference="CVN_SEX_A",
                semantic_kind=SemanticReferenceKind.COMPACT_ENUM_LIKE_TABLE,
                serialization_pattern=SerializationPattern.FILTER_VALUE,
                reference_table_enum_evidence=ReferenceTableEnumEvidence(
                    table_name="CVN_SEX_A",
                    item_count=2,
                    has_hierarchy=False,
                    has_delegate=False,
                    has_other_like_entry=False,
                    has_duplicate_codes=False,
                    has_duplicate_preferred_labels=False,
                    has_blank_code=False,
                    has_blank_preferred_label=False,
                    normalized_codes=("000", "010"),
                    preferred_labels=("Mujer", "Hombre"),
                    normalized_preferred_labels=("MUJER", "HOMBRE"),
                    open_world_signals=(),
                ),
            ),
        )
    )
    assert evidence is not None
    assert source_reference is not None
    enum_spec = build_domain_enum_spec(
        policy=policy,
        evidence=evidence,
        source_reference=source_reference,
    )
    assert enum_spec.class_name == "SexoEnum"
    assert enum_spec.source_reference == "CVN_SEX_A"
    assert enum_spec.members == (
        ("MUJER", "000"),
        ("HOMBRE", "010"),
    )
    assert enum_spec.labels == {
        "000": "Mujer",
        "010": "Hombre",
    }
    assert enum_spec.trace["code"] == "001"
    assert enum_spec.trace["source_reference"] == "CVN_SEX_A"
def test_build_enum_specs_for_entries_builds_only_eligible_and_deduplicated_enums():
    bundle = build_default_semantic_policy_bundle()
    entry_a = build_normalized_entry(
        code="001",
        manual_name="Sexo",
        manual_type="Alphanumeric",
        reference_resolution=build_reference_resolution(
            raw_reference="CVN_SEX_A",
            semantic_kind=SemanticReferenceKind.COMPACT_ENUM_LIKE_TABLE,
            serialization_pattern=SerializationPattern.FILTER_VALUE,
            reference_table_enum_evidence=build_reference_table_enum_evidence(
                table_name="CVN_SEX_A",
                item_count=2,
            ),
        ),
    )
    entry_b = build_normalized_entry(
        code="002",
        manual_name="Sexo alternativo",
        manual_type="Alphanumeric",
        reference_resolution=build_reference_resolution(
            raw_reference="CVN_SEX_A",
            semantic_kind=SemanticReferenceKind.COMPACT_ENUM_LIKE_TABLE,
            serialization_pattern=SerializationPattern.FILTER_VALUE,
            reference_table_enum_evidence=build_reference_table_enum_evidence(
                table_name="CVN_SEX_A",
                item_count=2,
            ),
        ),
    )
    entry_c = build_normalized_entry(
        code="003",
        manual_name="Tipo entidad",
        manual_type="Alphanumeric",
        reference_resolution=build_reference_resolution(
            raw_reference="CVN_ENTITY_TYPE",
            semantic_kind=SemanticReferenceKind.COMPACT_ENUM_LIKE_TABLE,
            serialization_pattern=SerializationPattern.FILTER_VALUE,
            reference_table_enum_evidence=build_reference_table_enum_evidence(
                table_name="CVN_ENTITY_TYPE",
                item_count=17,
                has_other_like_entry=True,
            ),
        ),
    )
    policy_index = {
        "001": build_semantic_field_policy(entry_a, bundle),
        "002": build_semantic_field_policy(entry_b, bundle),
        "003": build_semantic_field_policy(entry_c, bundle),
    }
    enum_specs = build_enum_specs_for_entries(
        entries=(entry_c, entry_b, entry_a),
        policy_index=policy_index,
    )
    assert len(enum_specs) == 1
    assert enum_specs[0].source_reference == "CVN_SEX_A"
    assert enum_specs[0].class_name.endswith("Enum")
def test_build_domain_generation_result_populates_enums_for_eligible_enum_entries():
    bundle = build_default_semantic_policy_bundle()
    entry_a = build_test_entry_with_tree_path(
        code="001",
        tree_cvn_item_code="060.010.000.000",
        xml_path="/Node/CVNItem[@code='060.010.000.000']/Property[@name='Sexo']",
    )
    entry_a = NormalizedCodeEntry(
        code=entry_a.code,
        manual=ManualCodeEntry(
            code=entry_a.code,
            manual_name="Sexo",
            manual_short_name=None,
            manual_type="Alphanumeric",
            manual_obligatory=False,
            manual_multiplicity=False,
            manual_reference_table=None,
        ),
        tree_paths=entry_a.tree_paths,
        source_files=entry_a.source_files,
        reference_resolution=build_reference_resolution(
            raw_reference="CVN_SEX_A",
            semantic_kind=SemanticReferenceKind.COMPACT_ENUM_LIKE_TABLE,
            serialization_pattern=SerializationPattern.FILTER_VALUE,
            reference_table_enum_evidence=build_reference_table_enum_evidence(
                table_name="CVN_SEX_A",
                item_count=2,
            ),
        ),
    )
    entry_b = build_test_entry("002")
    policy_index = {
        "001": build_semantic_field_policy(entry_a, bundle),
        "002": build_semantic_field_policy(entry_b, bundle),
    }
    grouped_entries = {
        "060.010.000.000": (entry_a,),
        "__no_tree__": (entry_b,),
    }
    result = build_domain_generation_result(
        policy_index=policy_index,
        grouped_entries=grouped_entries,
    )
    assert len(result.enums) == 1
    assert result.enums[0].source_reference == "CVN_SEX_A"
    assert result.enums[0].class_name.endswith("Enum")


def test_controlled_reference_components_are_importable():
    assert BaseCvnDomainModel is not None
    assert BaseControlledReferenceValue is not None
    assert CvnTrace is not None
    assert OpenCodedValue is not None
    assert MeasureOrScaleValue is not None
    assert IdentifierReference is not None
    assert ScopeReference is not None
    assert SubtypeBackedValue is not None
    assert HierarchicalCodeReference is not None
    assert RegistryReference is not None
    assert VocabularyReference is not None
    assert UnresolvedReference is not None
    assert UnderTracedReference is not None
def test_controlled_reference_components_inherit_from_base_component():
    component_types = (
        OpenCodedValue,
        MeasureOrScaleValue,
        IdentifierReference,
        ScopeReference,
        SubtypeBackedValue,
        HierarchicalCodeReference,
        RegistryReference,
        VocabularyReference,
        UnresolvedReference,
        UnderTracedReference,
    )
    for component_type in component_types:
        assert issubclass(component_type, BaseControlledReferenceValue)


def test_controlled_reference_components_do_not_inherit_from_base_cvn_domain_model():
    component_types = (
        OpenCodedValue,
        MeasureOrScaleValue,
        IdentifierReference,
        ScopeReference,
        SubtypeBackedValue,
        HierarchicalCodeReference,
        RegistryReference,
        VocabularyReference,
        UnresolvedReference,
        UnderTracedReference,
    )

    for component_type in component_types:
        assert not issubclass(component_type, BaseCvnDomainModel)


def test_cvn_trace_model_exposes_accepted_trace_contract():
    trace = CvnTrace(
        code="001.002",
        xml_paths=("/Node/CVNItem[@code='001']/Property[@name='Test']",),
        base_kind="text",
        domain_shape_kind="plain_value",
        enum_eligibility="ineligible",
        source_reference="CVN_TEST",
        notes=("note-a", "note-b"),
    )

    assert trace.code == "001.002"
    assert trace.xml_paths == ("/Node/CVNItem[@code='001']/Property[@name='Test']",)
    assert trace.base_kind == "text"
    assert trace.domain_shape_kind == "plain_value"
    assert trace.enum_eligibility == "ineligible"
    assert trace.source_reference == "CVN_TEST"
    assert trace.notes == ("note-a", "note-b")


def test_base_cvn_domain_model_exposes_optional_cvn_trace():
    trace = CvnTrace(
        code="001.002",
        xml_paths=("/Node/CVNItem[@code='001']/Property[@name='Test']",),
        base_kind="text",
        domain_shape_kind="plain_value",
        enum_eligibility="ineligible",
    )
    model = BaseCvnDomainModel(cvn_trace=trace)

    assert model.cvn_trace is trace
def test_specialized_controlled_reference_components_expose_expected_extra_fields():
    hierarchical = HierarchicalCodeReference(
        code="001",
        label="Tema",
        parent_code="000",
    )
    registry = RegistryReference(
        code="001",
        label="Entidad",
        registry_id="RID-1",
    )
    vocabulary = VocabularyReference(
        code="001",
        label="Tesauro",
        vocabulary_source="THESAURUS",
    )
    unresolved = UnresolvedReference(
        code="001",
        label="Agencia",
        raw_reference="CVN_AGENCY_C",
    )
    under_traced = UnderTracedReference(
        code="001",
        label="Prueba",
        raw_reference="CVN_PRUEBA",
    )
    assert hierarchical.parent_code == "000"
    assert registry.registry_id == "RID-1"
    assert vocabulary.vocabulary_source == "THESAURUS"
    assert unresolved.raw_reference == "CVN_AGENCY_C"
    assert under_traced.raw_reference == "CVN_PRUEBA"
def test_resolve_python_type_for_policy_returns_component_names_backed_by_real_components():
    bundle = build_default_semantic_policy_bundle()
    policies_and_expected_types = (
        (
            build_semantic_field_policy(
                build_normalized_entry(
                    code="001",
                    manual_type="Alphanumeric",
                    reference_resolution=build_reference_resolution(
                        raw_reference="CVN_MEASURE",
                        semantic_kind=SemanticReferenceKind.COMPACT_SCALE_OR_MEASURE,
                        serialization_pattern=SerializationPattern.QUALITY_MEASURE,
                    ),
                ),
                bundle,
            ),
            "MeasureOrScaleValue",
        ),
        (
            build_semantic_field_policy(
                build_normalized_entry(
                    code="002",
                    manual_type="Alphanumeric",
                    reference_resolution=build_reference_resolution(
                        raw_reference="CVN_IDTYPE",
                        semantic_kind=SemanticReferenceKind.IDENTIFIER_TYPE_TABLE,
                        serialization_pattern=SerializationPattern.EXTERNAL_PK_TYPE,
                    ),
                ),
                bundle,
            ),
            "IdentifierReference",
        ),
        (
            build_semantic_field_policy(
                build_normalized_entry(
                    code="003",
                    manual_type="Alphanumeric",
                    reference_resolution=build_reference_resolution(
                        raw_reference="CVN_SCOPE",
                        semantic_kind=SemanticReferenceKind.SCOPE_TABLE,
                        serialization_pattern=SerializationPattern.SCOPE_TYPE,
                    ),
                ),
                bundle,
            ),
            "ScopeReference",
        ),
        (
            build_semantic_field_policy(
                build_normalized_entry(
                    code="004",
                    manual_type="Alphanumeric",
                    reference_resolution=build_reference_resolution(
                        raw_reference="CVN_KNOW_A",
                        semantic_kind=SemanticReferenceKind.SUBTYPE_BACKED_CONTROLLED_FAMILY,
                        serialization_pattern=SerializationPattern.SUBTYPE,
                        source_family=ReferenceSourceFamily.SUBTYPE_BACKED_TABLE,
                    ),
                ),
                bundle,
            ),
            "SubtypeBackedValue",
        ),
        (
            build_semantic_field_policy(
                build_normalized_entry(
                    code="005",
                    manual_type="Alphanumeric",
                    reference_resolution=build_reference_resolution(
                        raw_reference="UNESCO_CODES",
                        semantic_kind=SemanticReferenceKind.HIERARCHICAL_THEMATIC_CLASSIFICATION,
                        serialization_pattern=SerializationPattern.SUBJECT_DESCRIPTION,
                    ),
                ),
                bundle,
            ),
            "HierarchicalCodeReference",
        ),
        (
            build_semantic_field_policy(
                build_normalized_entry(
                    code="006",
                    manual_type="Alphanumeric",
                    reference_resolution=build_reference_resolution(
                        raw_reference="ENTITY@Entity.xsd",
                        semantic_kind=SemanticReferenceKind.SIDE_PACKAGE_REGISTRY,
                        serialization_pattern=SerializationPattern.SIDE_PACKAGE_REGISTRY,
                        source_family=ReferenceSourceFamily.SIDE_PACKAGE_REGISTRY,
                    ),
                ),
                bundle,
            ),
            "RegistryReference",
        ),
        (
            build_semantic_field_policy(
                build_normalized_entry(
                    code="007",
                    manual_type="Alphanumeric",
                    reference_resolution=build_reference_resolution(
                        raw_reference="THESAURUS@thesaurus.xsd",
                        semantic_kind=SemanticReferenceKind.SIDE_PACKAGE_THESAURUS_OR_VOCABULARY,
                        serialization_pattern=SerializationPattern.SIDE_PACKAGE_THESAURUS,
                        source_family=ReferenceSourceFamily.SIDE_PACKAGE_THESAURUS,
                    ),
                ),
                bundle,
            ),
            "VocabularyReference",
        ),
        (
            build_semantic_field_policy(
                build_normalized_entry(
                    code="008",
                    manual_type="Alphanumeric",
                    reference_resolution=build_reference_resolution(
                        raw_reference="CVN_AGENCY_C",
                        semantic_kind=SemanticReferenceKind.UNRESOLVED_MANUAL_ONLY_REFERENCE,
                        serialization_pattern=SerializationPattern.UNRESOLVED,
                        source_family=ReferenceSourceFamily.UNRESOLVED_MANUAL_ONLY,
                    ),
                ),
                bundle,
            ),
            "UnresolvedReference",
        ),
        (
            build_semantic_field_policy(
                build_normalized_entry(
                    code="009",
                    manual_type="Alphanumeric",
                    reference_resolution=build_reference_resolution(
                        raw_reference="CVN_PRUEBA",
                        semantic_kind=SemanticReferenceKind.UNDER_TRACED_REFERENCE_TABLE,
                        serialization_pattern=SerializationPattern.FILTER_VALUE,
                    ),
                ),
                bundle,
            ),
            "UnderTracedReference",
        ),
    )
    for policy, expected_type in policies_and_expected_types:
        assert resolve_python_type_for_policy(policy) == expected_type


def test_render_field_annotation_renders_required_optional_and_repeated_cases():
    required_field = DomainFieldSpec(
        field_name="titulo",
        python_type="str",
        code="001",
        xml_paths=(),
        required=True,
        repeated=False,
        domain_shape_kind="plain_value",
        enum_eligibility="ineligible",
        trace={},
    )
    optional_field = DomainFieldSpec(
        field_name="sexo",
        python_type="SexoEnum",
        code="002",
        xml_paths=(),
        required=False,
        repeated=False,
        domain_shape_kind="strict_enum_candidate",
        enum_eligibility="eligible",
        trace={},
    )
    repeated_field = DomainFieldSpec(
        field_name="entidades",
        python_type="list[RegistryReference]",
        code="003",
        xml_paths=(),
        required=False,
        repeated=True,
        domain_shape_kind="registry_reference",
        enum_eligibility="ineligible",
        trace={},
    )

    assert render_field_annotation(required_field) == "str"
    assert render_field_annotation(optional_field) == "SexoEnum | None"
    assert render_field_annotation(repeated_field) == "list[RegistryReference]"


def test_render_field_default_renders_required_optional_and_repeated_cases():
    required_field = DomainFieldSpec(
        field_name="titulo",
        python_type="str",
        code="001",
        xml_paths=(),
        required=True,
        repeated=False,
        domain_shape_kind="plain_value",
        enum_eligibility="ineligible",
        trace={},
    )
    optional_field = DomainFieldSpec(
        field_name="sexo",
        python_type="SexoEnum",
        code="002",
        xml_paths=(),
        required=False,
        repeated=False,
        domain_shape_kind="strict_enum_candidate",
        enum_eligibility="eligible",
        trace={},
    )
    repeated_field = DomainFieldSpec(
        field_name="entidades",
        python_type="list[RegistryReference]",
        code="003",
        xml_paths=(),
        required=False,
        repeated=True,
        domain_shape_kind="registry_reference",
        enum_eligibility="ineligible",
        trace={},
    )

    assert render_field_default(required_field) == "Field(...)"
    assert render_field_default(optional_field) == "Field(default=None)"
    assert render_field_default(repeated_field) == "Field(default_factory=list)"


def test_render_field_line_renders_complete_field_line():
    field = DomainFieldSpec(
        field_name="sexo",
        python_type="SexoEnum",
        code="001",
        xml_paths=(),
        required=False,
        repeated=False,
        domain_shape_kind="strict_enum_candidate",
        enum_eligibility="eligible",
        trace={},
    )

    assert (
        render_field_line(field)
        == "    sexo: SexoEnum | None = Field(default=None)"
    )


def test_collect_unit_import_types_collects_stdlib_shared_and_enum_types():
    field_a = DomainFieldSpec(
        field_name="titulo",
        python_type="str",
        code="001",
        xml_paths=(),
        required=True,
        repeated=False,
        domain_shape_kind="plain_value",
        enum_eligibility="ineligible",
        trace={},
    )
    field_b = DomainFieldSpec(
        field_name="importe",
        python_type="Decimal",
        code="002",
        xml_paths=(),
        required=True,
        repeated=False,
        domain_shape_kind="plain_value",
        enum_eligibility="ineligible",
        trace={},
    )
    field_c = DomainFieldSpec(
        field_name="sexo",
        python_type="SexoEnum",
        code="003",
        xml_paths=(),
        required=False,
        repeated=False,
        domain_shape_kind="strict_enum_candidate",
        enum_eligibility="eligible",
        trace={},
    )
    field_d = DomainFieldSpec(
        field_name="entidades",
        python_type="list[RegistryReference]",
        code="004",
        xml_paths=(),
        required=False,
        repeated=True,
        domain_shape_kind="registry_reference",
        enum_eligibility="ineligible",
        trace={},
    )

    unit = DomainGenerationUnit(
        module_name="cvn_item_060_010_000_000",
        class_name="DatosPersonales",
        source_group_key="060.010.000.000",
        fields=(field_a, field_b, field_c, field_d),
    )

    stdlib_types, shared_types, enum_types = collect_unit_import_types(unit)

    assert stdlib_types == ("Decimal",)
    assert shared_types == ("BaseCvnDomainModel", "RegistryReference")
    assert enum_types == ("SexoEnum",)


def test_render_unit_class_renders_class_with_fields():
    field_a = DomainFieldSpec(
        field_name="titulo",
        python_type="str",
        code="001",
        xml_paths=(),
        required=True,
        repeated=False,
        domain_shape_kind="plain_value",
        enum_eligibility="ineligible",
        trace={},
    )
    field_b = DomainFieldSpec(
        field_name="sexo",
        python_type="SexoEnum",
        code="002",
        xml_paths=(),
        required=False,
        repeated=False,
        domain_shape_kind="strict_enum_candidate",
        enum_eligibility="eligible",
        trace={},
    )

    unit = DomainGenerationUnit(
        module_name="cvn_item_060_010_000_000",
        class_name="DatosPersonales",
        source_group_key="060.010.000.000",
        fields=(field_a, field_b),
    )

    rendered = render_unit_class(unit)

    assert rendered == (
        "class DatosPersonales(BaseCvnDomainModel):\n"
        "    titulo: str = Field(...)\n"
        "    sexo: SexoEnum | None = Field(default=None)"
    )
    assert "cvn_trace:" not in rendered


def test_render_unit_class_renders_pass_for_empty_unit():
    unit = DomainGenerationUnit(
        module_name="manual_only",
        class_name="ManualOnly",
        source_group_key="__no_tree__",
        fields=(),
    )

    rendered = render_unit_class(unit)

    assert rendered == (
        "class ManualOnly(BaseCvnDomainModel):\n"
        "    pass"
    )


def test_render_unit_module_renders_header_imports_and_class():
    field_a = DomainFieldSpec(
        field_name="importe",
        python_type="Decimal",
        code="001",
        xml_paths=(),
        required=True,
        repeated=False,
        domain_shape_kind="plain_value",
        enum_eligibility="ineligible",
        trace={},
    )
    field_b = DomainFieldSpec(
        field_name="sexo",
        python_type="SexoEnum",
        code="002",
        xml_paths=(),
        required=False,
        repeated=False,
        domain_shape_kind="strict_enum_candidate",
        enum_eligibility="eligible",
        trace={},
    )
    field_c = DomainFieldSpec(
        field_name="entidades",
        python_type="list[RegistryReference]",
        code="003",
        xml_paths=(),
        required=False,
        repeated=True,
        domain_shape_kind="registry_reference",
        enum_eligibility="ineligible",
        trace={},
    )

    unit = DomainGenerationUnit(
        module_name="cvn_item_060_010_000_000",
        class_name="DatosPersonales",
        source_group_key="060.010.000.000",
        fields=(field_a, field_b, field_c),
    )

    rendered = render_unit_module(unit)

    assert rendered == (
        "# Generated by cvn domain model generator. Do not edit manually.\n"
        "from __future__ import annotations\n"
        "\n"
        "from decimal import Decimal\n"
        "\n"
        "from pydantic import Field\n"
        "\n"
        "from models.cvn.components import BaseCvnDomainModel, RegistryReference\n"
        "\n"
        "from .enums import SexoEnum\n"
        "\n"
        "\n"
        "class DatosPersonales(BaseCvnDomainModel):\n"
        "    importe: Decimal = Field(...)\n"
        "    sexo: SexoEnum | None = Field(default=None)\n"
        "    entidades: list[RegistryReference] = Field(default_factory=list)\n"
    )


def test_render_enums_module_renders_string_enums():
    enums = (
        DomainEnumSpec(
            class_name="SexoEnum",
            source_reference="CVN_SEX_A",
            members=(
                ("MUJER", "000"),
                ("HOMBRE", "010"),
            ),
            labels={
                "000": "Mujer",
                "010": "Hombre",
            },
            trace={},
        ),
        DomainEnumSpec(
            class_name="TipoEntidadEnum",
            source_reference="CVN_ENTITY_TYPE",
            members=(("UNIVERSIDAD", "001"),),
            labels={
                "001": "Universidad",
            },
            trace={},
        ),
    )

    rendered = render_enums_module(enums)

    assert rendered == (
        "# Generated by cvn domain model generator. Do not edit manually.\n"
        "from __future__ import annotations\n"
        "\n"
        "from enum import Enum\n"
        "\n"
        "class SexoEnum(str, Enum):\n"
        "    MUJER = \"000\"\n"
        "    HOMBRE = \"010\"\n"
        "\n"
        "class TipoEntidadEnum(str, Enum):\n"
        "    UNIVERSIDAD = \"001\"\n"
        "\n"
    )


def test_render_generated_package_init_renders_units_and_enums_exports():
    unit_a = DomainGenerationUnit(
        module_name="cvn_item_060_010_000_000",
        class_name="DatosPersonales",
        source_group_key="060.010.000.000",
        fields=(),
    )
    unit_b = DomainGenerationUnit(
        module_name="manual_only",
        class_name="ManualOnly",
        source_group_key="__no_tree__",
        fields=(),
    )
    enum_a = DomainEnumSpec(
        class_name="SexoEnum",
        source_reference="CVN_SEX_A",
        members=(),
        labels={},
        trace={},
    )

    result = DomainGenerationResult(
        units=(unit_a, unit_b),
        enums=(enum_a,),
        normalized_entries=(),
        semantic_policies=(),
    )

    rendered = render_generated_package_init(result)

    assert rendered == (
        "# Generated by cvn domain model generator. Do not edit manually.\n"
        "from __future__ import annotations\n"
        "\n"
        "from .cvn_item_060_010_000_000 import DatosPersonales\n"
        "from .manual_only import ManualOnly\n"
        "\n"
        "from .enums import SexoEnum\n"
        "\n"
        "__all__ = [\n"
        "    \"DatosPersonales\",\n"
        "    \"ManualOnly\",\n"
        "    \"SexoEnum\",\n"
        "]\n"
        "\n"
    )


def test_render_domain_generation_result_renders_complete_file_map():
    bundle = build_default_semantic_policy_bundle()

    entry_a = build_normalized_entry(
        code="001",
        manual_name="Sexo",
        manual_type="Alphanumeric",
        reference_resolution=build_reference_resolution(
            raw_reference="CVN_SEX_A",
            semantic_kind=SemanticReferenceKind.COMPACT_ENUM_LIKE_TABLE,
            serialization_pattern=SerializationPattern.FILTER_VALUE,
            reference_table_enum_evidence=build_reference_table_enum_evidence(
                table_name="CVN_SEX_A",
                item_count=2,
            ),
        ),
    )
    entry_b = build_normalized_entry(
        code="002",
        manual_name="Entidad",
        manual_type="Alphanumeric",
        reference_resolution=build_reference_resolution(
            raw_reference="ENTITY@Entity.xsd",
            semantic_kind=SemanticReferenceKind.SIDE_PACKAGE_REGISTRY,
            serialization_pattern=SerializationPattern.SIDE_PACKAGE_REGISTRY,
            source_family=ReferenceSourceFamily.SIDE_PACKAGE_REGISTRY,
        ),
    )

    policy_index = {
        "001": build_semantic_field_policy(entry_a, bundle),
        "002": build_semantic_field_policy(entry_b, bundle),
    }   
    grouped_entries = {
        "__no_tree__": (entry_a, entry_b),
    }

    result = build_domain_generation_result(
        policy_index=policy_index,
        grouped_entries=grouped_entries,
    )
    rendered_files = render_domain_generation_result(result)

    assert set(rendered_files) == {"__init__.py", "enums.py", "manual_only.py"}
    assert rendered_files["enums.py"].startswith(
        "# Generated by cvn domain model generator. Do not edit manually."
    )
    assert "class Sexo(BaseCvnDomainModel):" in rendered_files["manual_only.py"]
    assert "from .manual_only import Sexo" in rendered_files["__init__.py"]


def test_write_rendered_domain_files_creates_output_dir_and_writes_files(tmp_path, monkeypatch):
    repo_root = tmp_path
    target_dir = repo_root / "src" / "models" / "cvn" / "generated"
    monkeypatch.chdir(repo_root)

    written_paths = write_rendered_domain_files(
        output_dir=target_dir,
        rendered_files={
            "__init__.py": "# init\n",
            "manual_only.py": "# module\n",
        },
    )

    assert target_dir.is_dir()
    assert (target_dir / "__init__.py").read_text(encoding="utf-8") == "# init\n"
    assert (target_dir / "manual_only.py").read_text(encoding="utf-8") == "# module\n"
    assert written_paths == (
        target_dir.resolve() / "__init__.py",
        target_dir.resolve() / "manual_only.py",
    )


def test_write_rendered_domain_files_rejects_wrong_output_dir(tmp_path, monkeypatch):
    repo_root = tmp_path
    allowed_dir = repo_root / "src" / "models" / "cvn" / "generated"
    wrong_dir = repo_root / "src" / "models" / "cvn" / "other"
    allowed_dir.mkdir(parents=True)
    wrong_dir.mkdir(parents=True)
    monkeypatch.chdir(repo_root)

    with pytest.raises(ValueError, match="output_dir must resolve exactly"):
        write_rendered_domain_files(
            output_dir=wrong_dir,
            rendered_files={"__init__.py": "# init\n"},
        )


def test_write_rendered_domain_files_deletes_only_python_files(tmp_path, monkeypatch):
    repo_root = tmp_path
    target_dir = repo_root / "src" / "models" / "cvn" / "generated"
    target_dir.mkdir(parents=True)
    (target_dir / "old.py").write_text("old\n", encoding="utf-8")
    (target_dir / "keep.txt").write_text("keep\n", encoding="utf-8")
    monkeypatch.chdir(repo_root)

    write_rendered_domain_files(
        output_dir=target_dir,
        rendered_files={"__init__.py": "# init\n"},
    )

    assert not (target_dir / "old.py").exists()
    assert (target_dir / "keep.txt").read_text(encoding="utf-8") == "keep\n"
    assert (target_dir / "__init__.py").read_text(encoding="utf-8") == "# init\n"


def test_write_rendered_domain_files_rejects_unexpected_subdirectories(tmp_path, monkeypatch):
    repo_root = tmp_path
    target_dir = repo_root / "src" / "models" / "cvn" / "generated"
    nested_dir = target_dir / "nested"
    nested_dir.mkdir(parents=True)
    monkeypatch.chdir(repo_root)

    with pytest.raises(ValueError, match="Unexpected subdirectory"):
        write_rendered_domain_files(
            output_dir=target_dir,
            rendered_files={"__init__.py": "# init\n"},
        )


def test_write_rendered_domain_files_rejects_parent_traversal_paths(tmp_path, monkeypatch):
    repo_root = tmp_path
    target_dir = repo_root / "src" / "models" / "cvn" / "generated"
    monkeypatch.chdir(repo_root)

    with pytest.raises(ValueError, match="must stay within"):
        write_rendered_domain_files(
            output_dir=target_dir,
            rendered_files={"../escape.py": "bad\n"},
        )


def test_write_rendered_domain_files_rejects_nested_paths_outside_direct_output(tmp_path, monkeypatch):
    repo_root = tmp_path
    target_dir = repo_root / "src" / "models" / "cvn" / "generated"
    monkeypatch.chdir(repo_root)

    with pytest.raises(ValueError, match="must stay within"):
        write_rendered_domain_files(
            output_dir=target_dir,
            rendered_files={"nested/module.py": "bad\n"},
        )


def test_write_rendered_domain_files_returns_paths_in_sorted_order(tmp_path, monkeypatch):
    repo_root = tmp_path
    target_dir = repo_root / "src" / "models" / "cvn" / "generated"
    monkeypatch.chdir(repo_root)

    written_paths = write_rendered_domain_files(
        output_dir=target_dir,
        rendered_files={
            "zeta.py": "# zeta\n",
            "__init__.py": "# init\n",
            "alpha.py": "# alpha\n",
        },
    )

    assert written_paths == (
        target_dir.resolve() / "__init__.py",
        target_dir.resolve() / "alpha.py",
        target_dir.resolve() / "zeta.py",
    )


def test_write_rendered_domain_files_overwrites_previous_python_output(tmp_path, monkeypatch):
    repo_root = tmp_path
    target_dir = repo_root / "src" / "models" / "cvn" / "generated"
    target_dir.mkdir(parents=True)
    (target_dir / "__init__.py").write_text("old init\n", encoding="utf-8")
    (target_dir / "manual_only.py").write_text("old module\n", encoding="utf-8")
    monkeypatch.chdir(repo_root)

    write_rendered_domain_files(
        output_dir=target_dir,
        rendered_files={
            "__init__.py": "new init\n",
            "manual_only.py": "new module\n",
        },
    )

    assert (target_dir / "__init__.py").read_text(encoding="utf-8") == "new init\n"
    assert (target_dir / "manual_only.py").read_text(encoding="utf-8") == "new module\n"


def test_write_rendered_domain_files_rejects_output_path_when_target_is_file(tmp_path, monkeypatch):
    repo_root = tmp_path
    target_dir = repo_root / "src" / "models" / "cvn" / "generated"
    target_dir.parent.mkdir(parents=True)
    target_dir.write_text("not a dir\n", encoding="utf-8")
    monkeypatch.chdir(repo_root)

    with pytest.raises(ValueError, match="is not a directory"):
        write_rendered_domain_files(
            output_dir=target_dir,
            rendered_files={"__init__.py": "# init\n"},
        )


def test_get_canonical_generation_paths_returns_expected_keys_and_paths():
    paths = get_canonical_generation_paths()

    assert set(paths) == {
        "specification_manual",
        "tree_model",
        "reference_tables",
        "subtypes",
        "entity",
        "thesaurus",
    }
    assert paths["specification_manual"] == Path(
        "docs/CvnXML_v1.4.3_2.1_17012025/XML/SpecificationManual.xml"
    )
    assert paths["tree_model"] == Path(
        "docs/CvnXML_v1.4.3_2.1_17012025/XML/CVNTreeModel.xml"
    )
    assert paths["reference_tables"] == Path(
        "docs/CvnXML_v1.4.3_2.1_17012025/XML/ReferenceTables.xml"
    )
    assert paths["subtypes"] == Path(
        "docs/CvnXML_v1.4.3_2.1_17012025/XML/Subtype_Spa.xml"
    )
    assert paths["entity"] == Path(
        "docs/CvnXML_v1.4.3_2.1_17012025/XML/Entity.xml"
    )
    assert paths["thesaurus"] == Path(
        "docs/CvnXML_v1.4.3_2.1_17012025/XML/Thesaurus.xml"
    )


def test_generate_domain_models_orchestrates_pipeline_with_defaults(monkeypatch):
    recorded: dict[str, object] = {}

    fake_bundle = object()
    fake_written_paths = (Path("src/models/cvn/generated/__init__.py"),)

    class FakeNormalizationResult:
        by_code = {"001": "entry-001"}

    fake_normalization_result = FakeNormalizationResult()
    fake_policy_index = {"001": "policy-001"}
    fake_grouped_entries = {"__no_tree__": ("entry-001",)}
    fake_generation_result = "generation-result"
    fake_rendered_files = {"__init__.py": "# init\n"}

    def fake_build_default_semantic_policy_bundle():
        return fake_bundle

    def fake_build_normalization_result(**kwargs):
        recorded["normalization_kwargs"] = kwargs
        return fake_normalization_result

    def fake_build_semantic_policy_index(normalization_result, bundle):
        recorded["policy_index_args"] = (normalization_result, bundle)
        return fake_policy_index

    def fake_group_entries_by_cvn_item_code(by_code):
        recorded["grouped_by_code"] = by_code
        return fake_grouped_entries

    def fake_build_domain_generation_result(policy_index, grouped_entries):
        recorded["generation_result_args"] = (policy_index, grouped_entries)
        return fake_generation_result

    def fake_render_domain_generation_result(result):
        recorded["render_result_arg"] = result
        return fake_rendered_files

    def fake_write_rendered_domain_files(output_dir, rendered_files):
        recorded["write_args"] = (output_dir, rendered_files)
        return fake_written_paths

    monkeypatch.setattr(
        "cvn_codegen.domain_model_generator.build_default_semantic_policy_bundle",
        fake_build_default_semantic_policy_bundle,
    )
    monkeypatch.setattr(
        "cvn_codegen.domain_model_generator.build_normalization_result",
        fake_build_normalization_result,
    )
    monkeypatch.setattr(
        "cvn_codegen.domain_model_generator.build_semantic_policy_index",
        fake_build_semantic_policy_index,
    )
    monkeypatch.setattr(
        "cvn_codegen.domain_model_generator.group_entries_by_cvn_item_code",
        fake_group_entries_by_cvn_item_code,
    )
    monkeypatch.setattr(
        "cvn_codegen.domain_model_generator.build_domain_generation_result",
        fake_build_domain_generation_result,
    )
    monkeypatch.setattr(
        "cvn_codegen.domain_model_generator.render_domain_generation_result",
        fake_render_domain_generation_result,
    )
    monkeypatch.setattr(
        "cvn_codegen.domain_model_generator.write_rendered_domain_files",
        fake_write_rendered_domain_files,
    )

    written_paths = generate_domain_models()

    assert written_paths == fake_written_paths
    assert recorded["policy_index_args"] == (fake_normalization_result, fake_bundle)
    assert recorded["grouped_by_code"] == {"001": "entry-001"}
    assert recorded["generation_result_args"] == (
        fake_policy_index,
        fake_grouped_entries,
    )
    assert recorded["render_result_arg"] == fake_generation_result
    assert recorded["write_args"] == (
        Path("src/models/cvn/generated"),
        fake_rendered_files,
    )


def test_generate_domain_models_uses_explicit_output_dir_and_bundle(monkeypatch, tmp_path):
    recorded: dict[str, object] = {}

    explicit_output_dir = tmp_path / "generated"
    explicit_bundle = object()
    fake_written_paths = (explicit_output_dir / "__init__.py",)

    class FakeNormalizationResult:
        by_code = {"001": "entry-001"}

    monkeypatch.setattr(
        "cvn_codegen.domain_model_generator.build_default_semantic_policy_bundle",
        lambda: pytest.fail("default bundle should not be used"),
    )
    monkeypatch.setattr(
        "cvn_codegen.domain_model_generator.build_normalization_result",
        lambda **kwargs: FakeNormalizationResult(),
    )
    monkeypatch.setattr(
        "cvn_codegen.domain_model_generator.build_semantic_policy_index",
        lambda normalization_result, bundle: {"001": bundle},
    )
    monkeypatch.setattr(
        "cvn_codegen.domain_model_generator.group_entries_by_cvn_item_code",
        lambda by_code: {"__no_tree__": ("entry-001",)},
    )
    monkeypatch.setattr(
        "cvn_codegen.domain_model_generator.build_domain_generation_result",
        lambda policy_index, grouped_entries: "generation-result",
    )
    monkeypatch.setattr(
        "cvn_codegen.domain_model_generator.render_domain_generation_result",
        lambda result: {"__init__.py": "# init\n"},
    )

    def fake_write_rendered_domain_files(output_dir, rendered_files):
        recorded["write_args"] = (output_dir, rendered_files)
        return fake_written_paths

    monkeypatch.setattr(
        "cvn_codegen.domain_model_generator.write_rendered_domain_files",
        fake_write_rendered_domain_files,
    )

    written_paths = generate_domain_models(
        output_dir=explicit_output_dir,
        bundle=explicit_bundle,
    )

    assert written_paths == fake_written_paths
    assert recorded["write_args"][0] == explicit_output_dir


def test_generate_domain_models_passes_canonical_paths_to_normalization(monkeypatch):
    recorded: dict[str, object] = {}

    class FakeNormalizationResult:
        by_code = {}

    monkeypatch.setattr(
        "cvn_codegen.domain_model_generator.build_default_semantic_policy_bundle",
        lambda: object(),
    )
    monkeypatch.setattr(
        "cvn_codegen.domain_model_generator.build_semantic_policy_index",
        lambda normalization_result, bundle: {},
    )
    monkeypatch.setattr(
        "cvn_codegen.domain_model_generator.group_entries_by_cvn_item_code",
        lambda by_code: {},
    )
    monkeypatch.setattr(
        "cvn_codegen.domain_model_generator.build_domain_generation_result",
        lambda policy_index, grouped_entries: "generation-result",
    )
    monkeypatch.setattr(
        "cvn_codegen.domain_model_generator.render_domain_generation_result",
        lambda result: {"__init__.py": "# init\n"},
    )
    monkeypatch.setattr(
        "cvn_codegen.domain_model_generator.write_rendered_domain_files",
        lambda output_dir, rendered_files: (),
    )

    def fake_build_normalization_result(**kwargs):
        recorded["normalization_kwargs"] = kwargs
        return FakeNormalizationResult()

    monkeypatch.setattr(
        "cvn_codegen.domain_model_generator.build_normalization_result",
        fake_build_normalization_result,
    )

    generate_domain_models()

    assert recorded["normalization_kwargs"] == {
        "specification_manual_path": Path(
            "docs/CvnXML_v1.4.3_2.1_17012025/XML/SpecificationManual.xml"
        ),
        "tree_model_path": Path(
            "docs/CvnXML_v1.4.3_2.1_17012025/XML/CVNTreeModel.xml"
        ),
        "reference_tables_path": Path(
            "docs/CvnXML_v1.4.3_2.1_17012025/XML/ReferenceTables.xml"
        ),
        "subtypes_path": Path(
            "docs/CvnXML_v1.4.3_2.1_17012025/XML/Subtype_Spa.xml"
        ),
        "entity_path": Path(
            "docs/CvnXML_v1.4.3_2.1_17012025/XML/Entity.xml"
        ),
        "thesaurus_path": Path(
            "docs/CvnXML_v1.4.3_2.1_17012025/XML/Thesaurus.xml"
        ),
    }


def test_main_prints_generated_paths(monkeypatch, capsys):
    fake_paths = (
        Path("src/models/cvn/generated/__init__.py"),
        Path("src/models/cvn/generated/enums.py"),
    )

    monkeypatch.setattr(
        "cvn_codegen.domain_model_generator.generate_domain_models",
        lambda: fake_paths,
    )

    main()

    captured = capsys.readouterr()

    assert captured.out == (
        "Generated 2 files:\n"
        "src/models/cvn/generated/__init__.py\n"
        "src/models/cvn/generated/enums.py\n"
    )


def test_main_calls_generate_domain_models_once(monkeypatch):
    calls = {"count": 0}

    def fake_generate_domain_models():
        calls["count"] += 1
        return ()

    monkeypatch.setattr(
        "cvn_codegen.domain_model_generator.generate_domain_models",
        fake_generate_domain_models,
    )

    main()

    assert calls["count"] == 1


def test_render_domain_generation_result_is_deterministic_for_same_input():
    bundle = build_default_semantic_policy_bundle()

    entry_a = build_normalized_entry(
        code="001",
        manual_name="Sexo",
        manual_type="Alphanumeric",
        reference_resolution=build_reference_resolution(
            raw_reference="CVN_SEX_A",
            semantic_kind=SemanticReferenceKind.COMPACT_ENUM_LIKE_TABLE,
            serialization_pattern=SerializationPattern.FILTER_VALUE,
            reference_table_enum_evidence=build_reference_table_enum_evidence(
                table_name="CVN_SEX_A",
                item_count=2,
            ),
        ),
    )
    entry_b = build_normalized_entry(
        code="002",
        manual_name="Entidad",
        manual_type="Alphanumeric",
        reference_resolution=build_reference_resolution(
            raw_reference="ENTITY@Entity.xsd",
            semantic_kind=SemanticReferenceKind.SIDE_PACKAGE_REGISTRY,
            serialization_pattern=SerializationPattern.SIDE_PACKAGE_REGISTRY,
            source_family=ReferenceSourceFamily.SIDE_PACKAGE_REGISTRY,
        ),
    )

    policy_index = {
        "001": build_semantic_field_policy(entry_a, bundle),
        "002": build_semantic_field_policy(entry_b, bundle),
    }
    grouped_entries = {
        "__no_tree__": (entry_a, entry_b),
    }

    result = build_domain_generation_result(
        policy_index=policy_index,
        grouped_entries=grouped_entries,
    )

    first = render_domain_generation_result(result)
    second = render_domain_generation_result(result)

    assert first == second


def test_write_rendered_domain_files_is_deterministic_for_sorted_paths(tmp_path, monkeypatch):
    repo_root = tmp_path
    target_dir = repo_root / "src" / "models" / "cvn" / "generated"
    monkeypatch.chdir(repo_root)

    rendered_files = {
        "zeta.py": "# zeta\n",
        "__init__.py": "# init\n",
        "alpha.py": "# alpha\n",
    }

    first_written_paths = write_rendered_domain_files(
        output_dir=target_dir,
        rendered_files=rendered_files,
    )
    first_contents = {
        path.name: path.read_text(encoding="utf-8")
        for path in first_written_paths
    }

    second_written_paths = write_rendered_domain_files(
        output_dir=target_dir,
        rendered_files=rendered_files,
    )
    second_contents = {
        path.name: path.read_text(encoding="utf-8")
        for path in second_written_paths
    }

    assert first_written_paths == second_written_paths
    assert first_contents == second_contents


def test_generated_modules_are_importable_from_written_temp_package(tmp_path, monkeypatch):
    bundle = build_default_semantic_policy_bundle()

    entry_a = build_normalized_entry(
        code="001",
        manual_name="Sexo",
        manual_type="Alphanumeric",
        reference_resolution=build_reference_resolution(
            raw_reference="CVN_SEX_A",
            semantic_kind=SemanticReferenceKind.COMPACT_ENUM_LIKE_TABLE,
            serialization_pattern=SerializationPattern.FILTER_VALUE,
            reference_table_enum_evidence=build_reference_table_enum_evidence(
                table_name="CVN_SEX_A",
                item_count=2,
            ),
        ),
    )
    entry_b = build_normalized_entry(
        code="002",
        manual_name="Entidad",
        manual_type="Alphanumeric",
        reference_resolution=build_reference_resolution(
            raw_reference="ENTITY@Entity.xsd",
            semantic_kind=SemanticReferenceKind.SIDE_PACKAGE_REGISTRY,
            serialization_pattern=SerializationPattern.SIDE_PACKAGE_REGISTRY,
            source_family=ReferenceSourceFamily.SIDE_PACKAGE_REGISTRY,
        ),
    )

    policy_index = {
        "001": build_semantic_field_policy(entry_a, bundle),
        "002": build_semantic_field_policy(entry_b, bundle),
    }
    grouped_entries = {
        "__no_tree__": (entry_a, entry_b),
    }

    result = build_domain_generation_result(
        policy_index=policy_index,
        grouped_entries=grouped_entries,
    )
    rendered_files = render_domain_generation_result(result)

    generated_dir = tmp_path / "generated"
    generated_dir.mkdir(parents=True)

    for relative_path, content in rendered_files.items():
        (generated_dir / relative_path).write_text(content, encoding="utf-8")

    monkeypatch.syspath_prepend(str(tmp_path))
    saved_modules = clear_generated_imports()

    try:
        generated_package = importlib.import_module("generated")
        generated_enums = importlib.import_module("generated.enums")
        generated_manual_only = importlib.import_module("generated.manual_only")

        assert generated_package is not None
        assert generated_enums is not None
        assert generated_manual_only is not None
    finally:
        restore_generated_imports(saved_modules)


def test_generated_package_reexports_generated_classes_and_enums(tmp_path, monkeypatch):
    bundle = build_default_semantic_policy_bundle()

    entry_a = build_normalized_entry(
        code="001",
        manual_name="Sexo",
        manual_type="Alphanumeric",
        reference_resolution=build_reference_resolution(
            raw_reference="CVN_SEX_A",
            semantic_kind=SemanticReferenceKind.COMPACT_ENUM_LIKE_TABLE,
            serialization_pattern=SerializationPattern.FILTER_VALUE,
            reference_table_enum_evidence=build_reference_table_enum_evidence(
                table_name="CVN_SEX_A",
                item_count=2,
            ),
        ),
    )
    entry_b = build_normalized_entry(
        code="002",
        manual_name="Entidad",
        manual_type="Alphanumeric",
        reference_resolution=build_reference_resolution(
            raw_reference="ENTITY@Entity.xsd",
            semantic_kind=SemanticReferenceKind.SIDE_PACKAGE_REGISTRY,
            serialization_pattern=SerializationPattern.SIDE_PACKAGE_REGISTRY,
            source_family=ReferenceSourceFamily.SIDE_PACKAGE_REGISTRY,
        ),
    )

    policy_index = {
        "001": build_semantic_field_policy(entry_a, bundle),
        "002": build_semantic_field_policy(entry_b, bundle),
    }
    grouped_entries = {
        "__no_tree__": (entry_a, entry_b),
    }

    result = build_domain_generation_result(
        policy_index=policy_index,
        grouped_entries=grouped_entries,
    )
    rendered_files = render_domain_generation_result(result)

    generated_dir = tmp_path / "generated"
    generated_dir.mkdir(parents=True)

    for relative_path, content in rendered_files.items():
        (generated_dir / relative_path).write_text(content, encoding="utf-8")

    monkeypatch.syspath_prepend(str(tmp_path))
    saved_modules = clear_generated_imports()

    try:
        generated_package = importlib.import_module("generated")

        assert hasattr(generated_package, "Sexo")
        assert hasattr(generated_package, "SexoEnum")
    finally:
        restore_generated_imports(saved_modules)


def test_generated_enum_is_importable_and_exposes_expected_values(tmp_path, monkeypatch):
    bundle = build_default_semantic_policy_bundle()

    entry = build_normalized_entry(
        code="001",
        manual_name="Sexo",
        manual_type="Alphanumeric",
        reference_resolution=build_reference_resolution(
            raw_reference="CVN_SEX_A",
            semantic_kind=SemanticReferenceKind.COMPACT_ENUM_LIKE_TABLE,
            serialization_pattern=SerializationPattern.FILTER_VALUE,
            reference_table_enum_evidence=build_reference_table_enum_evidence(
                table_name="CVN_SEX_A",
                item_count=2,
            ),
        ),
    )

    policy_index = {
        "001": build_semantic_field_policy(entry, bundle),
    }
    grouped_entries = {
        "__no_tree__": (entry,),
    }

    result = build_domain_generation_result(
        policy_index=policy_index,
        grouped_entries=grouped_entries,
    )
    rendered_files = render_domain_generation_result(result)

    generated_dir = tmp_path / "generated"
    generated_dir.mkdir(parents=True)

    for relative_path, content in rendered_files.items():
        (generated_dir / relative_path).write_text(content, encoding="utf-8")

    monkeypatch.syspath_prepend(str(tmp_path))
    saved_modules = clear_generated_imports()

    try:
        generated_enums = importlib.import_module("generated.enums")
        sexo_enum = generated_enums.SexoEnum

        assert tuple(member.value for member in sexo_enum) == ("000", "010")
        assert all(isinstance(member.value, str) for member in sexo_enum)
        assert issubclass(sexo_enum, str)
    finally:
        restore_generated_imports(saved_modules)


def test_generated_model_exposes_expected_field_annotations(tmp_path, monkeypatch):
    bundle = build_default_semantic_policy_bundle()

    entry_a = build_normalized_entry(
        code="001",
        manual_name="Sexo",
        manual_type="Alphanumeric",
        reference_resolution=build_reference_resolution(
            raw_reference="CVN_SEX_A",
            semantic_kind=SemanticReferenceKind.COMPACT_ENUM_LIKE_TABLE,
            serialization_pattern=SerializationPattern.FILTER_VALUE,
            reference_table_enum_evidence=build_reference_table_enum_evidence(
                table_name="CVN_SEX_A",
                item_count=2,
            ),
        ),
    )
    entry_b = build_normalized_entry(
        code="002",
        manual_name="Entidad",
        manual_type="Alphanumeric",
        reference_resolution=build_reference_resolution(
            raw_reference="ENTITY@Entity.xsd",
            semantic_kind=SemanticReferenceKind.SIDE_PACKAGE_REGISTRY,
            serialization_pattern=SerializationPattern.SIDE_PACKAGE_REGISTRY,
            source_family=ReferenceSourceFamily.SIDE_PACKAGE_REGISTRY,
        ),
    )

    policy_index = {
        "001": build_semantic_field_policy(entry_a, bundle),
        "002": build_semantic_field_policy(entry_b, bundle),
    }
    grouped_entries = {
        "__no_tree__": (entry_a, entry_b),
    }

    result = build_domain_generation_result(
        policy_index=policy_index,
        grouped_entries=grouped_entries,
    )
    rendered_files = render_domain_generation_result(result)

    generated_dir = tmp_path / "generated"
    generated_dir.mkdir(parents=True)

    for relative_path, content in rendered_files.items():
        (generated_dir / relative_path).write_text(content, encoding="utf-8")

    monkeypatch.syspath_prepend(str(tmp_path))
    saved_modules = clear_generated_imports()

    try:
        generated_manual_only = importlib.import_module("generated.manual_only")
        model_class = generated_manual_only.Sexo

        annotations = model_class.__annotations__

        assert "sexo" in annotations
        assert "entidad" in annotations
    finally:
        restore_generated_imports(saved_modules)


def test_generated_model_inherits_cvn_trace_from_base_model(tmp_path, monkeypatch):
    bundle = build_default_semantic_policy_bundle()

    entry = build_normalized_entry(
        code="001",
        manual_name="Nombre",
        manual_type="Alphanumeric",
    )

    policy_index = {
        "001": build_semantic_field_policy(entry, bundle),
    }
    grouped_entries = {
        "__no_tree__": (entry,),
    }

    result = build_domain_generation_result(
        policy_index=policy_index,
        grouped_entries=grouped_entries,
    )
    rendered_files = render_domain_generation_result(result)

    generated_dir = tmp_path / "generated"
    generated_dir.mkdir(parents=True)

    for relative_path, content in rendered_files.items():
        (generated_dir / relative_path).write_text(content, encoding="utf-8")

    monkeypatch.syspath_prepend(str(tmp_path))
    saved_modules = clear_generated_imports()

    try:
        generated_manual_only = importlib.import_module("generated.manual_only")
        model_class = generated_manual_only.Nombre

        assert hasattr(model_class, "model_fields")
        assert "cvn_trace" in model_class.model_fields
    finally:
        restore_generated_imports(saved_modules)
