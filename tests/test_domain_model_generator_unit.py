from cvn_codegen.domain_model_generator import (
    build_semantic_policy_index,
    group_entries_by_cvn_item_code,
    get_field_name_from_policy,
)

from cvn_codegen.normalization_types import (
    ManualCodeEntry,
    NormalizedCodeEntry,
    NormalizationResult,
    SourceTrace, 
    TreePathEntry,

)
from cvn_codegen.semantic_policy import (
    SemanticFieldPolicy,
    build_default_semantic_policy_bundle,
    build_semantic_field_policy,

)

from test_semantic_policy_unit import build_normalized_entry


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