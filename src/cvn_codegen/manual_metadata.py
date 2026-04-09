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

def load_specification_manual(specification_manual_path: Path) -> SpecificationManual:
    return SpecificationManual() #TODO remove this 
    pass


def select_name_detail(name_details: list[NameType.NameDetail], preferred_language: str = "spa") -> Optional[NameType.NameDetail]:
    pass
def build_manual_code_entry(item: SpecificationManual.Manual.Item,) -> ManualCodeEntry:
    pass

def extract_manual_entries(specification_manual: SpecificationManual) -> dict[str, ManualCodeEntry]: