import importlib

import pytest

from cvn_codegen.xsdata_runner import (
    TARGET_TABLE,
    XSDTargetSpec,
)
from xsdata_generation_lock import run_xsdata_generation_per_target_locked


CORE_TARGETS = (
    ("cvn", "generated.cvn"),
    ("specification_manual", "generated.specification_manual"),
    ("tree_model", "generated.tree_model"),
)
AUXILIARY_TARGETS = (
    ("reference_tables", "generated.reference_tables"),
    ("subtypes", "generated.subtypes"),
    ("entity", "generated.entity"),
    ("thesaurus", "generated.thesaurus"),
)


def assert_generated_target_is_importable(target: XSDTargetSpec, package_name: str) -> None:
    run_xsdata_generation_per_target_locked(target)
    assert target.output_dir.exists()
    assert any(target.output_dir.glob("**/*.py"))
    imported_module = importlib.import_module(package_name)
    assert imported_module is not None


@pytest.mark.parametrize(("target_name", "package_name"), CORE_TARGETS)
def test_structural_generation_core_targets_are_importable(
    target_name: str,
    package_name: str,
):
    target = TARGET_TABLE[target_name]
    assert_generated_target_is_importable(target, package_name)


@pytest.mark.parametrize(("target_name", "package_name"), AUXILIARY_TARGETS)
def test_structural_generation_auxiliary_targets_are_importable(
    target_name: str,
    package_name: str,
):
    target = TARGET_TABLE[target_name]
    assert_generated_target_is_importable(target, package_name)


def test_structural_generation_all_targets_are_covered_by_pipeline_tests():
    tested_targets = {
        target_name
        for target_name, _package_name in CORE_TARGETS + AUXILIARY_TARGETS
    }
    assert tested_targets == set(TARGET_TABLE)
