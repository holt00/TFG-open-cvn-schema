from pathlib import Path
from typing import Any
import pytest
from xsdata_pydantic.bindings import XmlParser
from generated.entity import Entity
from generated.reference_tables import ReferenceTables
from generated.specification_manual import SpecificationManual
from generated.subtypes import Cvnsubtype
from generated.thesaurus import Thesaurus
from generated.tree_model import CvntreeModel
def parse_xml(path: Path, model_type: type[Any]) -> Any:
    parser = XmlParser()
    return parser.from_path(path, model_type)
def test_parse_specification_manual_canonical_xml(canonical_paths: dict[str, Path]):
    result = parse_xml(
        canonical_paths["specification_manual"],
        SpecificationManual,
    )
    assert isinstance(result, SpecificationManual)
@pytest.mark.parametrize(
    ("path_key", "model_type"),
    [
        ("reference_tables", ReferenceTables),
        ("subtypes", Cvnsubtype),
        ("entity", Entity),
        ("thesaurus", Thesaurus),
    ],
)
def test_parse_auxiliary_canonical_xml(
    canonical_paths: dict[str, Path],
    path_key: str,
    model_type: type[Any],
):
    result = parse_xml(canonical_paths[path_key], model_type)
    assert isinstance(result, model_type)
def test_parse_tree_model_canonical_xml_reports_documented_xsd_mismatch(
    canonical_paths: dict[str, Path],
):
    with pytest.raises(Exception) as exc_info:
        parse_xml(canonical_paths["tree_model"], CvntreeModel)
    message = str(exc_info.value)
    assert "Type" in message