from cvn_codegen.xsdata_runner import (
    TARGET_TABLE as TT,
    run_xsdata_generation_per_target,
    XSDTargetSpec
)
import pytest as pt



def test_smoke_generate_specification_manual_creates_python_files():
    # Arrange
    target : XSDTargetSpec = TT["specification_manual"]

    # Act
    run_xsdata_generation_per_target(target)
    
    # Assert
    assert target.output_dir.exists(), f"Expected output directory '{target.output_dir}' to exist after generation."

    assert any(target.output_dir.glob("**/*.py")), f"Expected at least one Python file to be generated in '{target.output_dir}', but found none."