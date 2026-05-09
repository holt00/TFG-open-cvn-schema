import pytest as pt

from cvn_codegen.xsdata_runner import (
    XSDTargetSpec,
    RunnerError,
    xsdata_target_resolver,
    build_xsdata_command,
    validate_generated_output,
    TARGET_TABLE as target_table,
    XSDATA_CONFIG_FILE_PATH as config_path,
    TARGET_OVERRIDES as target_overrides,
    EXECUTION_ORDER_ALL as execution_order_all
)

@pt.mark.parametrize(
    ("target_name", "expected_xsd_name", "expected_package"),
    [
        ("cvn", "CVN.xsd", "generated.cvn"),
        ("specification_manual", "SpecificationManual.xsd", "generated.specification_manual"),
        ("tree_model", "CVNTreeModel_v1.0.xsd", "generated.tree_model"),
        ("reference_tables", "ReferenceTables.xsd", "generated.reference_tables"),
        ("subtypes", "Subtypes.xsd", "generated.subtypes"),
        ("entity", "Entity_v1.4.xsd", "generated.entity"),
        ("thesaurus", "Thesaurus.xsd", "generated.thesaurus"),
    ],
)

def test_resolve_single_target_returns_expected_spec(
    target_name: str, expected_xsd_name: str, expected_package: str
):
    resolved_target = xsdata_target_resolver(target_name)
    assert isinstance(resolved_target, list)
    assert len(resolved_target) == 1
    assert isinstance(resolved_target[0], XSDTargetSpec)
    spec = resolved_target[0]
    assert spec.name == target_name
    assert spec.package == expected_package
    assert spec.source_xsd.name == expected_xsd_name
    assert spec.output_dir.name == target_name


def test_resolve_all_returns_targets_in_stable_order():
    expected_targets: list[str] = [
        "cvn",
        "specification_manual",
        "tree_model",
        "reference_tables",
        "subtypes",
        "entity",
        "thesaurus",
    ]
    resolved_targets = xsdata_target_resolver("all")
    assert isinstance(resolved_targets, list)
    assert len(resolved_targets) == len(expected_targets)
    assert [target.name for target in resolved_targets] == expected_targets



def test_invalid_target_raises_runner_error():
    # Arrange
    invalid_target_name = "invalid_target"
    valid_target_names = execution_order_all + ["all"]

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

def test_build_xsdata_command_for_reference_tables_uses_expected_arguments():
    expected_target: XSDTargetSpec = target_table["reference_tables"]
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
    built_command = build_xsdata_command(expected_target)
    assert isinstance(built_command, list)
    assert built_command == expected_args_list


def test_build_xsdata_command_for_entity_uses_expected_arguments():
    expected_target: XSDTargetSpec = target_table["entity"]
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
    built_command = build_xsdata_command(expected_target)
    assert isinstance(built_command, list)
    assert built_command == expected_args_list


def test_build_xsdata_command_for_cvn_uses_expected_arguments():
    # Arrange
    expected_target: XSDTargetSpec = target_table["cvn"]
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


def test_build_xsdata_command_for_tree_model_keeps_override():
    target = target_table["tree_model"]
    built_command = build_xsdata_command(target)
    assert "--unnest-classes" in built_command

def test_target_overrides_has_only_tree_model():
    assert set(target_overrides.keys()) == {"tree_model"}