from pathlib import Path
from xsdata_pydantic.bindings import XmlParser
from generated.specification_manual.specification_manual import(
    NameType,
    SpecificationManual,
)
from cvn_codegen.normalization_types import (
    ManualCodeEntry,
    SourceTrace,
)
from typing import Optional
import logging

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

def load_specification_manual(specification_manual_path: Path) -> SpecificationManual:
    
    if not isinstance(specification_manual_path, Path):
        raise ValueError(f"specification_manual_path must be a Path object, got {type(specification_manual_path)} instead.")
    
    if not specification_manual_path.is_file():
        raise FileNotFoundError(f"Specification manual file not found at path: {specification_manual_path}")
    
    xml_parser = XmlParser()
    specification_manual = xml_parser.from_path(specification_manual_path, SpecificationManual)
    return specification_manual
    
def select_name_detail(name_details: list[NameType.NameDetail], preferred_language: str = "spa") -> Optional[NameType.NameDetail]:
    
    if not name_details:
        return None
    for detail in name_details:
        if str(detail.lang) == preferred_language:
            return detail
    return name_details[0]

def build_manual_code_entry(item: SpecificationManual.Manual.Item,) -> ManualCodeEntry:
    pass

def extract_manual_entries(specification_manual: SpecificationManual) -> dict[str, ManualCodeEntry]: