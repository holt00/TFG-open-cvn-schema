from pathlib import Path
from xml.etree import ElementTree

from open_cvn import CvnValidationStatus, validate_open_cvn_json
from open_cvn.xml_semantic_import import import_cvn_xml_semantically


FIXTURES = Path("tests/fixtures/cvn_xml")


def _import_fixture(name: str):
    root = ElementTree.fromstring((FIXTURES / name).read_text(encoding="utf-8"))
    return import_cvn_xml_semantically(root=root, source_identifier=name, source_path=str(FIXTURES / name))


def test_semantic_import_populates_identity():
    document = _import_fixture("semantic_identity.xml")

    assert document["curriculum"]["identity"]["nombre"] == "Ada"
    assert document["curriculum"]["identity"]["apellidos"] == "Lovelace Synthetic"
    assert document["extensions"]["x-open-cvn.xml_import"]["mapping_status"] == "semantic_partial"


def test_semantic_import_populates_education_entry_and_validates():
    document = _import_fixture("semantic_education.xml")
    validation = validate_open_cvn_json(document, source_identifier="semantic_education.xml")

    assert validation.validation_status == CvnValidationStatus.VALID
    entry = document["curriculum"]["education"][0]
    assert entry["id"] == "education-020-010-010-000-001"
    assert entry["type"].startswith("education.")
    assert entry["data"]["nombre_del_titulo"]["raw_value"] == "Synthetic Computer Science Degree"


def test_semantic_import_populates_research_entry():
    document = _import_fixture("semantic_research.xml")

    entry = document["curriculum"]["research"][0]
    assert entry["type"].startswith("research.")
    assert entry["data"]["autores_as_p_o_de_firma"] == ["Synthetic Author"]
    assert entry["data"]["ciudad_de_la_entidad_organizadora"] == "Synthetic outreach activity"


def test_semantic_import_preserves_unmapped_item():
    document = _import_fixture("semantic_unmapped.xml")

    diagnostic = document["extensions"]["x-open-cvn.xml_import"]

    assert diagnostic["mapping_status"] == "trace_only"
    assert diagnostic["items_unmapped"] == 1
    assert document["curriculum"]["other"][0]["type"] == "other.unmapped_cvn_item"
