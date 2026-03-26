import argparse
import subprocess
from dataclasses import dataclass
import pathlib
import typing



#---------------- Zona de definicion de tipos de datos ----------------

@dataclass
class XSDTargetSpec:
    """
    Esta clase representa la configuracion del objetivo de generación de código a partir de un archivo XSD.
    """
    name : str #nombre logico del objetivo
    source_xsd : pathlib.Path #ruta original del archivo xsd
    package : str #nombre del paquete destino en el que se generará el código
    output_dir : pathlib.Path #ruta del directorio donde se guardará el archivo generado


#---------------- Zona de definicion de excepciones ----------------

class RunnerError(Exception):
    """Excepcion base para errores relacionados con la ejecución del runner de xsdata."""
    pass


#---------------- Zona de definicion de constantes ----------------

REPO_ROOT : typing.Final[pathlib.Path] = pathlib.Path(__file__).resolve().parent.parent.parent
#Ruta raiz del repositorio

XSDATA_CONFIG_FILE_PATH : typing.Final[pathlib.Path] = REPO_ROOT/ "config" / ".xsdata.xml"
#Ruta del archivo de configuracion del xsdata

CANONICAL_XSD_DIR : typing.Final[pathlib.Path] = REPO_ROOT / "docs" / "CvnXML_v1.4.3_2.1_17012025" / "XSD"
#ruta donde se encuentran los archivos xsd

GENERATED_ROOT_DIR : typing.Final[pathlib.Path] = REPO_ROOT / "src" / "generated"
#ruta raiz donde se guardaran los archivos generados 

TARGET_TABLE : typing.Final[dict[str, XSDTargetSpec]] = {
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

EXECUTION_ORDER_ALL : typing.Final[list[str]] = ["cvn", "specification_manual", "tree_model"]
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





#TODO al final de la implementacion del archivo dejar los imports de typing y parthlib con los imports unicos necesarios
