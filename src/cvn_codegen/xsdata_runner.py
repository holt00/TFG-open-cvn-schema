from argparse import ArgumentParser
import logging
from subprocess import run, CalledProcessError
from dataclasses import dataclass
from pathlib import Path
from typing import Final
from shutil import rmtree


logger = logging.getLogger(__name__)


# ---------------- Data type definitions ----------------


@dataclass
class XSDTargetSpec:
    """
    Represent the configuration for one XSD code-generation target.
    """

    name: str  # logical target name
    source_xsd: Path  # source XSD file path
    package: str  # destination package name for generated code
    output_dir: Path  # destination directory for generated files


# ---------------- Exception definitions ----------------


class RunnerError(Exception):
    """Base exception for xsdata runner execution errors."""

    pass


# ---------------- Constant definitions ----------------

REPO_ROOT: Final[Path] = Path(__file__).resolve().parent.parent.parent
# Repository root path

XSDATA_CONFIG_FILE_PATH: Final[Path] = REPO_ROOT / "config" / ".xsdata.xml"
# xsdata configuration file path

CANONICAL_XSD_DIR: Final[Path] = (
    REPO_ROOT / "docs" / "CvnXML_v1.4.3_2.1_17012025" / "XSD"
)
# Directory containing the canonical XSD files

GENERATED_ROOT_DIR: Final[Path] = REPO_ROOT / "src" / "generated"
# Root directory for generated output

TARGET_TABLE: Final[dict[str, XSDTargetSpec]] = {
    "cvn": XSDTargetSpec(
        name="cvn",
        source_xsd=CANONICAL_XSD_DIR / "CVN.xsd",
        package="generated.cvn",
        output_dir=GENERATED_ROOT_DIR / "cvn",
    ),
    "specification_manual": XSDTargetSpec(
        name="specification_manual",
        source_xsd=CANONICAL_XSD_DIR / "SpecificationManual.xsd",
        package="generated.specification_manual",
        output_dir=GENERATED_ROOT_DIR / "specification_manual",
    ),
    "tree_model": XSDTargetSpec(
        name="tree_model",
        source_xsd=CANONICAL_XSD_DIR / "CVNTreeModel_v1.0.xsd",
        package="generated.tree_model",
        output_dir=GENERATED_ROOT_DIR / "tree_model",
    ),
}
# Map from logical target name to full target specification

EXECUTION_ORDER_ALL: Final[list[str]] = ["cvn", "specification_manual", "tree_model"]
# Target keys in the order they must be executed

TARGET_OVERRIDES: Final[dict[str, list[str]]] = {
    "tree_model": ["--unnest-classes"],
}
# Map from logical target name to additional xsdata CLI arguments

# ---------------- Function definitions ----------------


def xsdata_target_resolver(target_name: str) -> list[XSDTargetSpec]:
    """
    Resolve a target name into one or more target specifications.

    Args:
        target_name (str): Target name to resolve.

    Returns:
        list[XSDTargetSpec]: Resolved target specifications.

    Raises:
        RunnerError: If the target name is not recognized.
    """

    if target_name == "all":
        return [TARGET_TABLE[name] for name in EXECUTION_ORDER_ALL]
    elif target_name in TARGET_TABLE:
        return [TARGET_TABLE[target_name]]
    else:
        raise RunnerError(
            f"Target '{target_name}' no reconocido. Opciones válidas: {EXECUTION_ORDER_ALL + ['all']}"
        )


def is_path_within(output_dir: Path, root_dir: Path) -> bool:
    """
    Check whether an output directory is inside the generated root directory.

    Args:
        output_dir (pathlib.Path): Output directory to validate.
        root_dir (pathlib.Path): Generated root directory.

    Returns:
        bool: True if the output directory is within the generated root.
    """
    output_dir_resolved = output_dir.resolve()
    root_dir_resolved = root_dir.resolve()
    return output_dir_resolved.is_relative_to(root_dir_resolved)


def validate_xsdata_and_xsdata_pydantic() -> None:
    """
    Validate that xsdata and xsdata-pydantic are available from the CLI.

    Raises:
        RunnerError: If xsdata or xsdata-pydantic is not installed or not accessible.
    """
    try:
        run(
            ["uv", "run", "xsdata", "--version"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (CalledProcessError, FileNotFoundError) as e:
        raise RunnerError(
            "xsdata no está instalado o no es accesible desde la línea de comandos."
        ) from e

    try:
        run(
            ["uv", "run", "python", "-c", "import xsdata_pydantic"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (CalledProcessError, FileNotFoundError) as e:
        raise RunnerError(
            "El plugin xsdata-pydantic no está instalado o no es accesible desde la línea de comandos."
        ) from e


def validate_xsdata_prerequistes(target: XSDTargetSpec) -> None:
    """
    Validate the prerequisites required to run xsdata for a target.

    Args:
        target (XSDTargetSpec): Target specification to validate.

    Raises:
        RunnerError: If any prerequisite is not satisfied.
    """
    # Validate configuration file existence.
    if not XSDATA_CONFIG_FILE_PATH.is_file():
        raise RunnerError(
            f"El archivo de configuración de xsdata '{XSDATA_CONFIG_FILE_PATH}' no existe o no es un archivo."
        )

    # Validate the source XSD file.
    if not isinstance(target, XSDTargetSpec):
        raise RunnerError(f"El objetivo {target} no es una instancia de XSDTargetSpec.")

    if not target.source_xsd.is_file():
        raise RunnerError(
            f"El archivo XSD '{target.source_xsd}' no existe o no es un archivo"
        )

    if not target.source_xsd.suffix.lower() == ".xsd":
        raise RunnerError(
            f'El archivo \'{target.source_xsd}\' debe ser un fichero ".xsd", sim embargo es de tipo "{target.source_xsd.suffix}"'
        )

    # Validate generated root directory existence.

    if not GENERATED_ROOT_DIR.is_dir():
        raise RunnerError(
            f"El directorio raíz de salida '{GENERATED_ROOT_DIR}' no existe o no es un directorio."
        )

    # Validate that the output directory stays inside the generated root.
    if not is_path_within(target.output_dir, GENERATED_ROOT_DIR):
        raise RunnerError(
            f"El directorio de salida '{target.output_dir}' no se encuentra dentro del directorio raíz de generación '{GENERATED_ROOT_DIR}'."
        )

    validate_xsdata_and_xsdata_pydantic()


def clean_generated_code(target: XSDTargetSpec) -> None:
    """
    Remove previously generated output for a target.

    Args:
        target (XSDTargetSpec): Target specification to clean.

    Raises:
        RunnerError: If an error occurs while cleaning generated code.
    """
    if not is_path_within(target.output_dir, GENERATED_ROOT_DIR):
        raise RunnerError(
            f"El directorio de salida '{target.output_dir}' no se encuentra dentro del directorio raíz de generación '{GENERATED_ROOT_DIR}'."
        )

    if target.output_dir.resolve() == GENERATED_ROOT_DIR.resolve():
        raise RunnerError(
            f"El directorio de salida '{target.output_dir}' no puede ser el mismo que el directorio raíz de generación '{GENERATED_ROOT_DIR}' para evitar borrados accidentales."
        )

    target.output_dir.mkdir(parents=True, exist_ok=True)

    for item in target.output_dir.iterdir():
        try:
            if item.is_dir() and not item.is_symlink():
                rmtree(item)
            else:
                item.unlink()
        except OSError as e:
            raise RunnerError(
                f"Error al limpiar el código generado en '{item}': {e}"
            ) from e


def build_xsdata_command(target: XSDTargetSpec) -> list[str]:
    """
    Build the xsdata command for one generation target.

    Args:
        target (XSDTargetSpec): Target specification for command generation.

    Returns:
        list[str]: xsdata command expressed as a list of CLI arguments.
    """

    command = [
        "uv",
        "run",
        "xsdata",
        "generate",
        "--config",
        str(XSDATA_CONFIG_FILE_PATH),
        "--package",
        target.package,
    ]
    command.extend(TARGET_OVERRIDES.get(target.name, []))
    command.append(str(target.source_xsd))

    return command


def execute_xsdata_command(target: XSDTargetSpec) -> None:
    """
    Execute the xsdata command for a target.

    Args:
        target (XSDTargetSpec): Target specification to execute.

    Raises:
        RunnerError: If command execution fails.
    """
    command = build_xsdata_command(target)
    try:
        run(command, check=True, cwd=REPO_ROOT / "src")
    except (CalledProcessError, FileNotFoundError) as e:
        raise RunnerError(
            f"Error al ejecutar el comando '{' '.join(command)}': {e}"
        ) from e


def validate_generated_output(target: XSDTargetSpec) -> None:
    """
    Validate that code generation produced Python output for a target.

    Args:
        target (XSDTargetSpec): Target specification to validate.

    Raises:
        RunnerError: If the output directory is missing, empty, or contains no Python files.
    """
    if not target.output_dir.is_dir():
        raise RunnerError(
            f"El directorio de salida '{target.output_dir}' no existe o no es un directorio después de ejecutar xsdata para el objetivo '{target.name}'."
        )

    if not any(target.output_dir.iterdir()):
        raise RunnerError(
            f"El directorio de salida '{target.output_dir}' está vacío después de ejecutar xsdata para el objetivo '{target.name}'."
        )

    if not any(target.output_dir.glob("**/*.py")):
        raise RunnerError(
            f"No se encontraron archivos .py generados en '{target.output_dir}' después de ejecutar xsdata para el objetivo '{target.name}'."
        )


def run_xsdata_generation_per_target(target: XSDTargetSpec) -> None:
    """
    Run the full xsdata generation workflow for one target.

    Args:
        target (XSDTargetSpec): Target specification to generate.

    Raises:
        RunnerError: If any step in the generation workflow fails.
    """

    validate_xsdata_prerequistes(target)

    clean_generated_code(target)

    execute_xsdata_command(target)

    validate_generated_output(target)


def run_targets_generation(targets: list[XSDTargetSpec]) -> None:
    """
    Run xsdata generation sequentially for a list of targets.

    Args:
        targets (list[XSDTargetSpec]): Target specifications to generate.

    Raises:
        RunnerError: If generation fails for any target.
    """
    generated_outputs: list[str] = []

    for target in targets:
        logger.info(
            f"Ejecutando generación de código para el objetivo '{target.name}'..."
        )
        run_xsdata_generation_per_target(target)
        logger.info(
            f"Generación de código para el objetivo '{target.name}' completada exitosamente."
        )
        generated_outputs.append(f"{target.name} -> {target.output_dir}")

    logger.info(
        "Proceso de generación de código para todos los objetivos completado exitosamente."
    )
    logger.info("Archivos generados:")
    for archivo in generated_outputs:
        logger.info(f" - {archivo}")


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(
        description="Runner de generación de código a partir de archivos XSD utilizando xsdata."
    )
    parser.add_argument(
        "target",
        choices=EXECUTION_ORDER_ALL + ["all"],
        type=str,
        help=f"El objetivo de generación de código a ejecutar. Opciones válidas: {EXECUTION_ORDER_ALL + ['all']}",
    )
    return parser


def main() -> int:
    """Run the xsdata generation CLI entry point.

    Returns:
        int: Process exit code. Returns ``0`` on success and ``1`` on failure.
    """

    logging.basicConfig(level=logging.INFO)

    try:
        parser = build_parser()

        arguments = parser.parse_args()

        execution_list = xsdata_target_resolver(arguments.target)

        run_targets_generation(execution_list)

    except RunnerError as e:
        logger.error(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# TODO: keep only the imports that remain necessary after implementation stabilizes.
