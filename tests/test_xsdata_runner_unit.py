import pytest as pt

from cvn_codegen.xsdata_runner import (
    XSDTargetSpec,
    RunnerError,
    xsdata_target_resolver,
)


def test_resolve_single_target_returns_expected_spec():
    # Arrange
    target_name: str = "cvn"

    # Act
    resolved_target = xsdata_target_resolver(target_name)

    # Assert

    assert isinstance(resolved_target, list), (
        f"Expected result to be a list, but got {type(resolved_target)}."
    )
    assert len(resolved_target) == 1, (
        f"Expected exactly one target spec for '{target_name}', but got {len(resolved_target)}."
    )
    assert isinstance(resolved_target[0], XSDTargetSpec), (
        f"Expected result to be an instance of XSDTargetSpec, but got {type(resolved_target[0])}."
    )
    assert resolved_target[0].name == target_name, (
        f"Expected target name to be '{target_name}', but got '{resolved_target[0].name}'."
    )
    assert resolved_target[0].package == "generated." + target_name, (
        f"Expected package name to be 'generated.{target_name}', but got '{resolved_target[0].package}'."
    )
    assert str(resolved_target[0].source_xsd).endswith(
        f"{target_name.capitalize()}.xsd"
    ), (
        f"Expected source XSD path to contain '{target_name.capitalize()}.xsd', but got '{resolved_target[0].source_xsd}'."
    )
    assert str(resolved_target[0].output_dir).endswith(
        "src/generated/" + target_name
    ), (
        f"Expected output directory path to end with '{target_name}', but got '{resolved_target[0].output_dir}'."
    )


def test_resolve_all_returns_targets_in_stable_order():
    
    #Arrange
    expected_targets : list[str] = ["cvn", "specification_manual", "tree_model"]

    #Act
    resolved_targets = xsdata_target_resolver("all")

    #Assert
    assert isinstance(resolved_targets, list), (
        f"Expected result to be a list, but got {type(resolved_targets)}."
    )
    assert len(resolved_targets) == len(expected_targets), (
        f"Expected {len(expected_targets)} target specs, but got {len(resolved_targets)}."
    )
    for i, expected_name in enumerate(expected_targets):
        assert isinstance(resolved_targets[i], XSDTargetSpec), (
            f"Expected result to be an instance of XSDTargetSpec, but got {type(resolved_targets[i])}."
        )
        assert resolved_targets[i].name == expected_name, (
            f"Expected target name to be '{expected_name}', but got '{resolved_targets[i].name}'."
        )


def test_build_xsdata_command_for_cnv_uses_expected_arguments():
    pass


def test_invalid_target_raises_runner_error():
    pass


def test_smoke_test_model_creates_python_files():
    pass
