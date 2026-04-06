import pytest as pt

from cvn_codegen.xsdata_runner import (
    XSDTargetSpec,
    RunnerError,
    xsdata_target_resolver,
    build_xsdata_command,
    validate_generated_output,
    TARGET_TABLE as TT,
    XSDATA_CONFIG_FILE_PATH as config_path,
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
        f"{target_name.upper()}.xsd"
    ), (
        f"Expected source XSD path to contain '{target_name.upper()}.xsd', but got '{resolved_target[0].source_xsd}'."
    )
    assert str(resolved_target[0].output_dir).endswith(
        "src/generated/" + target_name
    ), (
        f"Expected output directory path to end with '{target_name}', but got '{resolved_target[0].output_dir}'."
    )


def test_resolve_all_returns_targets_in_stable_order():
    # Arrange
    expected_targets: list[str] = ["cvn", "specification_manual", "tree_model"]

    # Act
    resolved_targets = xsdata_target_resolver("all")

    # Assert
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


def test_invalid_target_raises_runner_error():
    # Arrange
    invalid_target_name = "invalid_target"
    valid_target_names = ["cvn", "specification_manual", "tree_model", "all"]

    # Act & Assert
    with pt.raises(RunnerError) as exc_info:
        xsdata_target_resolver(invalid_target_name)

    assert isinstance(exc_info.value, RunnerError), (
        f"Expected exception to be of type RunnerError, but got {type(exc_info.value)}."
    )

    assert (
        str(exc_info.value)
        == f"Target '{invalid_target_name}' no reconocido. Opciones válidas: {valid_target_names}"
    ), (
        f"Expected error message to be 'Target '{invalid_target_name}' no reconocido. Opciones válidas: {valid_target_names}', but got '{str(exc_info.value)}'."
    )


def test_build_xsdata_command_for_cvn_uses_expected_arguments():
    # Arrange
    expected_target: XSDTargetSpec = TT["cvn"]
    expected_args_list: list[str] = [
        "uv",
        "run",
        "xsdata",
        "generate",
        "--config",
        str(config_path),
        "--package",
        str(expected_target.package),
        str(expected_target.source_xsd),
    ]

    # Act
    built_command = build_xsdata_command(expected_target)

    # Assert
    assert isinstance(built_command, list), (
        f"Expected command to be a list, but got {type(built_command)}."
    )
    assert built_command == expected_args_list, (
        f"Expected command to be {expected_args_list}, but got {built_command}."
    )


def test_validate_generated_output_fails_for_empty_directory(tmp_path):
    # Arrange
    target = XSDTargetSpec(
        name="dummy",
        source_xsd=tmp_path / "dummy.xsd",
        package="generated.dummy",
        output_dir=tmp_path / "generated_output",
    )
    target.output_dir.mkdir()

    # Act / Assert
    with pt.raises(RunnerError) as exc_info:
        validate_generated_output(target)

    assert "está vacío" in str(exc_info.value), (
        f"Expected error message to mention empty directory, but got '{str(exc_info.value)}'."
    )
