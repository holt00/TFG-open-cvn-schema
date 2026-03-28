from argparse import ArgumentParser
from subprocess import run, CalledProcessError
from dataclasses import dataclass
from pathlib import Path
from typing import Final
from shutil import rmtree



#---------------- Zona de definicion de tipos de datos ----------------

@dataclass
class XSDTargetSpec:
    """
    Esta clase representa la configuracion del objetivo de generación de código a partir de un archivo XSD.
    """
    name : str #nombre logico del objetivo
    source_xsd : Path #ruta original del archivo xsd
    package : str #nombre del paquete destino en el que se generará el código
    output_dir : Path #ruta del directorio donde se guardará el archivo generado


#---------------- Zona de definicion de excepciones ----------------

class RunnerError(Exception):
    """Excepcion base para errores relacionados con la ejecución del runner de xsdata."""
    pass


#---------------- Zona de definicion de constantes ----------------

REPO_ROOT : Final[Path] = Path(__file__).resolve().parent.parent.parent
#Ruta raiz del repositorio

XSDATA_CONFIG_FILE_PATH : Final[Path] = REPO_ROOT/ "config" / ".xsdata.xml"
#Ruta del archivo de configuracion del xsdata

CANONICAL_XSD_DIR : Final[Path] = REPO_ROOT / "docs" / "CvnXML_v1.4.3_2.1_17012025" / "XSD"
#ruta donde se encuentran los archivos xsd

GENERATED_ROOT_DIR : Final[Path] = REPO_ROOT / "src" / "generated"
#ruta raiz donde se guardaran los archivos generados 

TARGET_TABLE : Final[dict[str, XSDTargetSpec]] = {
    "cvn": XSDTargetSpec(
        name="cvn",
        source_xsd = CANONICAL_XSD_DIR / "CVN.xsd",
        package = "generated.cvn",
        output_dir = GENERATED_ROOT_DIR / "cvn"
    ),
    "specification_manual": XSDTargetSpec(
        name="specification_manual",
        source_xsd = CANONICAL_XSD_DIR / "SpecificationManual.xsd",
        package = "generated.specification_manual",
        output_dir = GENERATED_ROOT_DIR / "specification_manual"
    ),
    "tree_model": XSDTargetSpec(
        name="tree_model",
        source_xsd = CANONICAL_XSD_DIR / "CVNTreeModel_v1.0.xsd",
        package = "generated.tree_model",
        output_dir = GENERATED_ROOT_DIR / "tree_model"
    )
}
#Tabla que mapea el nombre logico del xsd a su especificacion completa

EXECUTION_ORDER_ALL : Final[list[str]] = ["cvn", "specification_manual", "tree_model"]
#lista de las claves de TARGET_TABLE en el orden en el que deben ser ejecutados 


#---------------- Zona de definicion de funciones ----------------

def xsdata_target_resolver (target_name : str) -> list[XSDTargetSpec]:
    """
    Resuelve el nombre del objetivo a su especificacion completa.
    Args:
        target_name (str): El nombre del objetivo a resolver.
    Returns:
        list[XSDTargetSpec]: Una lista con la especificacion/es completa/s de los objetivos.

    Raises:
        RunnerError: Si el nombre del objetivo no es reconocido.
    """

    if target_name == "all":
        return [TARGET_TABLE[name] for name in EXECUTION_ORDER_ALL]
    elif target_name in TARGET_TABLE:
        return [TARGET_TABLE[target_name]]
    else:
        raise RunnerError(f"Target '{target_name}' no reconocido. Opciones válidas: {EXECUTION_ORDER_ALL + ['all']}")


def is_path_within(output_dir : Path, root_dir : Path) -> bool:
    """
    Valida que el directorio de salida dado se encuentre dentro del directorio raíz de generación.
    Args:
        output_dir (pathlib.Path): El directorio de salida a validar.
        root_dir (pathlib.Path): El directorio raíz de generación.
    Returns:
        bool: True si el directorio de salida se encuentra dentro del directorio raíz de generación
    """
    output_dir_resolved = output_dir.resolve()
    root_dir_resolved = root_dir.resolve()
    return output_dir_resolved.is_relative_to(root_dir_resolved)

def validate_xsdata_and_xsdata_pydantic()-> None:
    """
    Valida que xsdata y su plugin de pydantic estén instalados y accesibles desde la línea de comandos.
    Raises:
        RunnerError: Si xsdata o el plugin de pydantic no están instalados o no son accesibles.
    """
    try:
        run(["uv","run","xsdata", "--version"], check=True, capture_output=True, text=True)
    except (CalledProcessError, FileNotFoundError) as e:
        raise RunnerError("xsdata no está instalado o no es accesible desde la línea de comandos.") from e

    try:
        run(["uv","run","python","-c","import xsdata_pydantic"], check=True, capture_output=True, text=True)
    except (CalledProcessError, FileNotFoundError) as e:
        raise RunnerError("El plugin xsdata-pydantic no está instalado o no es accesible desde la línea de comandos.") from e


def validate_xsdata_prerequistes(target : XSDTargetSpec) -> None:
    """
    Valida que se cumplan los prerrequisitos para ejecutar xsdata en el objetivo dado.
    Args:
        target (XSDTargetSpec): La especificacion del objetivo a validar.
    Raises:
        RunnerError: Si no se cumple algun prerrequisito.
    """
    #comprobaciones del archivo de configuracion
    if not XSDATA_CONFIG_FILE_PATH.is_file():
        raise RunnerError(f"El archivo de configuración de xsdata '{XSDATA_CONFIG_FILE_PATH}' no existe o no es un archivo.")


    #comprobaciones del archivo source_xsd
    if not isinstance(target, XSDTargetSpec): 
        raise RunnerError(f"El objetivo {target} no es una instancia de XSDTargetSpec.")

    if not target.source_xsd.is_file():
        raise RunnerError(f"El archivo XSD '{target.source_xsd}' no existe o no es un archivo")
    
    if not target.source_xsd.suffix.lower() == ".xsd":
        raise RunnerError(f"El archivo '{target.source_xsd}' debe ser un fichero \".xsd\", sim embargo es de tipo \"{target.source_xsd.suffix}\"")


    #comprobacion de que el directorio raiz de salida existe

    if not GENERATED_ROOT_DIR.is_dir():
        raise RunnerError(f"El directorio raíz de salida '{GENERATED_ROOT_DIR}' no existe o no es un directorio.")

    #comprobacion de que el directorio de salida se encuentra dentro del directorio raiz de generacion
    if not is_path_within(target.output_dir, GENERATED_ROOT_DIR):
        raise RunnerError(f"El directorio de salida '{target.output_dir}' no se encuentra dentro del directorio raíz de generación '{GENERATED_ROOT_DIR}'.")
    
    validate_xsdata_and_xsdata_pydantic()    



def clean_generated_code(target : XSDTargetSpec) -> None:
    """
    Limpia la salida generada anteriormente para cada uno de los objetivos
    Args:
        target (XSDTargetSpec): La especificacion del objetivo a limpiar.
    
    Raises:
        RunnerError: Si ocurre un error al limpiar el código generado.
    """
    if not is_path_within(target.output_dir, GENERATED_ROOT_DIR):
        raise RunnerError(f"El directorio de salida '{target.output_dir}' no se encuentra dentro del directorio raíz de generación '{GENERATED_ROOT_DIR}'.")
    
    if target.output_dir.resolve() == GENERATED_ROOT_DIR.resolve():
        raise RunnerError(f"El directorio de salida '{target.output_dir}' no puede ser el mismo que el directorio raíz de generación '{GENERATED_ROOT_DIR}' para evitar borrados accidentales.")

    target.output_dir.mkdir(parents=True, exist_ok=True)
    
    for item in target.output_dir.iterdir():
        try:
            if item.is_dir() and not item.is_symlink():
                rmtree(item)
            else:
                item.unlink()
        except OSError as e:
            raise RunnerError(f"Error al limpiar el código generado en '{item}': {e}") from e

def build_xsdata_command(target : XSDTargetSpec) -> list[str]:
    """
    Construye el comando de xsdata para generar el código a partir del objetivo dado.
    Args:
        target (XSDTargetSpec): La especificacion del objetivo para el cual construir el comando.
    Returns:
        list[str]: El comando de xsdata construido como una lista de argumentos.
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
        str(target.source_xsd)
    ]
    return command

def execute_xsdata_command(target : XSDTargetSpec) -> None:
    """
    Ejecuta el comando de xsdata dado.
    Args:
        target (XSDTargetSpec): El objetivo para el cual ejecutar el comando.
    Raises:
        RunnerError: Si ocurre un error durante la ejecución del comando.
    """
    command = build_xsdata_command(target)
    try:
        run(command, check=True)
    except (CalledProcessError, FileNotFoundError) as e:
        raise RunnerError(f"Error al ejecutar el comando '{' '.join(command)}': {e}") from e


def validate_generated_output(target : XSDTargetSpec) -> None:
    """
    Valida que se ha generado el código correctamente para el objetivo dado.
    Args:
        target (XSDTargetSpec): El objetivo para el cual validar el código generado.
    Raises:
        RunnerError: Si no se encuentra ningún archivo .py en el directorio de salida después de la generación.
    """
    if not target.output_dir.is_dir():
        raise RunnerError(f"El directorio de salida '{target.output_dir}' no existe o no es un directorio después de ejecutar xsdata para el objetivo '{target.name}'.")
    
    if not any(target.output_dir.iterdir()):
        raise RunnerError(f"El directorio de salida '{target.output_dir}' está vacío después de ejecutar xsdata para el objetivo '{target.name}'.")

    if not any(target.output_dir.glob("**/*.py")):
        raise RunnerError(f"No se encontraron archivos .py generados en '{target.output_dir}' después de ejecutar xsdata para el objetivo '{target.name}'.")
    
    
def run_xsdata_generation_per_target(target: XSDTargetSpec) -> None:
    """
    Ejecuta el proceso completo de generación de código a partir de un archivo XSD para el objetivo dado, incluyendo validaciones, limpieza y ejecución del comando de xsdata.
    Args:
        target (XSDTargetSpec): El objetivo para el cual ejecutar el proceso de generación de código.
    Raises:
        RunnerError: Si ocurre algún error durante el proceso de generación de código.
    """

    validate_xsdata_prerequistes(target)

    clean_generated_code(target)

    execute_xsdata_command(target)

    validate_generated_output(target)



def run_targets_generation(targets: list[XSDTargetSpec]) -> None:
    """
    Lanza el proceso de generación de código a partir de archivos XSD para una lista de objetivos dada, ejecutando el proceso completo para cada objetivo en orden.
    Args:
        targets (list[XSDTargetSpec]): La lista de objetivos para los cuales ejecutar el proceso de generación de código.
    Raises:
        RunnerError: Si ocurre algún error durante el proceso de generación de código para alguno de los objetivos.
    """
    generated_outputs: list[str] = []

    for target in targets:
        print(f"Ejecutando generación de código para el objetivo '{target.name}'...")
        run_xsdata_generation_per_target(target)
        print(f"Generación de código para el objetivo '{target.name}' completada exitosamente.\n")
        generated_outputs.append(f"{target.name} -> {target.output_dir}")

    print("Proceso de generación de código para todos los objetivos completado exitosamente.")
    print("Archivos generados:")
    for archivo in generated_outputs:
        print(f" - {archivo}")

def build_parser() -> ArgumentParser:
    parser = ArgumentParser(description="Runner de generación de código a partir de archivos XSD utilizando xsdata.")
    parser.add_argument(
        "target",
        choices=EXECUTION_ORDER_ALL + ["all"],
        type=str,
        help=f"El objetivo de generación de código a ejecutar. Opciones válidas: {EXECUTION_ORDER_ALL + ['all']}"
    )
    return parser

def main() -> int :
    """Función principal del runner de generación de código a partir de archivos XSD utilizando xsdata. Esta función se encarga de parsear los argumentos de línea de comandos, resolver los objetivos a ejecutar y lanzar el proceso de generación de código para cada objetivo en orden.
    Returns:
        int: El código de salida del programa. 0 si la ejecución fue exitosa, 1 si ocurrió un error.
    """

    try:
        parser = build_parser()
        
        arguments = parser.parse_args()

        execution_list = xsdata_target_resolver(arguments.target)

        run_targets_generation(execution_list)

    except RunnerError as e:
        print(f"Error: {e}")
        return 1

    return 0

if __name__ == "__main__":
    raise SystemExit(main())

#TODO al final de la implementacion del archivo dejar los imports de typing y parthlib con los imports unicos necesarios
