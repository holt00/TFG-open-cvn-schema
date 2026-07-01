import importlib

from cvn_codegen.xsdata_runner import (
    TARGET_TABLE as target_table,
    XSDTargetSpec,
)
import pytest as pt

from xsdata_generation_lock import run_xsdata_generation_per_target_locked


def test_smoke_generate_specification_manual_creates_python_files():
    # Arrange
    target : XSDTargetSpec = target_table["specification_manual"]

    # Act
    run_xsdata_generation_per_target_locked(target)
    
    # Assert
    assert target.output_dir.exists(), f"Expected output directory '{target.output_dir}' to exist after generation."

    assert any(target.output_dir.glob("**/*.py")), f"Expected at least one Python file to be generated in '{target.output_dir}', but found none."

@pt.mark.parametrize(
    "target_name",
    ["reference_tables", "subtypes", "thesaurus", "entity"],
)

def test_smoke_generate_auxiliary_target_creates_python_files(target_name: str):
    target: XSDTargetSpec = target_table[target_name]
    run_xsdata_generation_per_target_locked(target)
    assert target.output_dir.exists(), (
        f"Expected output directory '{target.output_dir}' to exist after generation."
    )
    assert any(target.output_dir.glob("**/*.py")), (
        f"Expected at least one Python file to be generated in '{target.output_dir}', but found none."
    )

@pt.mark.parametrize(
    ("target_name", "package_name"),
    [
        ("reference_tables", "generated.reference_tables"),
        ("subtypes", "generated.subtypes"),
        ("thesaurus", "generated.thesaurus"),
        ("entity", "generated.entity"),
    ],
)
def test_smoke_import_generated_auxiliary_package_after_generation(
    target_name: str, package_name: str
):
    target: XSDTargetSpec = target_table[target_name]
    run_xsdata_generation_per_target_locked(target)
    imported_module = importlib.import_module(package_name)
    assert imported_module is not None
