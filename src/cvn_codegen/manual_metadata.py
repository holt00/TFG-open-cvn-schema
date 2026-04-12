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
    
def select_name_detail(name_details: list[NameType.NameDetail], preferred_language: str = "spa") -> NameType.NameDetail | None:
    
    if not name_details:
        return None
    for detail in name_details:
        if str(detail.lang) == preferred_language:
            return detail
    return name_details[0]

def build_manual_code_entry(item: SpecificationManual.Manual.Item,) -> ManualCodeEntry:
    code = str(item.code).strip()
    
    if not code:
        raise ValueError(f"Item code is empty for item {item.name}")
    
    selected_name_detail = select_name_detail(item.name.name_detail, preferred_language="spa")

    manual_name = None
    manual_short_name = None

    if selected_name_detail:
        manual_name = selected_name_detail.name
        manual_short_name = selected_name_detail.short_name
        
    return ManualCodeEntry(
        code=code,
        manual_name=manual_name,
        manual_short_name=manual_short_name,
        manual_type=item.type_value,
        manual_obligatory=item.obligatory,
        manual_multiplicity=item.multiplicity,
        manual_reference_table=item.reference_table,
        manual_level=item.level,
        manual_order=item.order,
        manual_link=item.link,
        manual_length=item.length,
        trace=SourceTrace(
            source_file="SpecificationManual.xml",
            xml_path=f"/SpecificationManual/Manual/Item[@code='{code}']",
            source_code=code
        )
    )

def extract_manual_entries(specification_manual: SpecificationManual) -> dict[str, ManualCodeEntry]:
    entry_ny_code : dict[str, ManualCodeEntry] = {}

    for item in specification_manual.manual.item:
        entry: ManualCodeEntry = build_manual_code_entry(item)
        if entry.code in entry_ny_code:
            logging.warning(f"Duplicate code '{entry.code}' found in specification manual.")
            raise ValueError(f"Duplicate code '{entry.code}' found in specification manual.")
        entry_ny_code[entry.code] = entry
    
    return entry_ny_code
