from pathlib import Path

from open_cvn import CvnErrorCode, CvnValidationStatus, parse_cvn_xml


FIXTURES = Path("tests/fixtures/cvn_xml")


def test_parse_cvn_xml_accepts_path_input():
    result = parse_cvn_xml(FIXTURES / "minimal_cvn.xml")

    assert result.validation_status == CvnValidationStatus.VALID
    assert result.data is not None
    assert result.data["schema_version"] == "0.1.0"
    assert result.trace is not None
    assert result.trace.source_path == str(FIXTURES / "minimal_cvn.xml")
    assert "000.010.000.000" in result.trace.cvn_codes


def test_parse_cvn_xml_accepts_inline_xml_string():
    payload = (FIXTURES / "minimal_cvn.xml").read_text(encoding="utf-8")

    result = parse_cvn_xml(payload, source_identifier="inline-xml")

    assert result.validation_status == CvnValidationStatus.VALID
    assert result.source_identifier == "inline-xml"


def test_parse_cvn_xml_accepts_xml_bytes():
    payload = (FIXTURES / "minimal_cvn.xml").read_bytes()

    result = parse_cvn_xml(payload, source_identifier="bytes-xml")

    assert result.validation_status == CvnValidationStatus.VALID
    assert result.source_identifier == "bytes-xml"


def test_parse_cvn_xml_reports_unreadable_path():
    result = parse_cvn_xml(Path("tests/fixtures/cvn_xml/missing.xml"))

    assert result.validation_status == CvnValidationStatus.FAILED
    assert result.errors[0].code == CvnErrorCode.UNREADABLE_FILE


def test_parse_cvn_xml_reports_malformed_xml():
    result = parse_cvn_xml(FIXTURES / "malformed.xml")

    assert result.validation_status == CvnValidationStatus.FAILED
    assert result.errors[0].code == CvnErrorCode.INVALID_XML
    assert result.errors[0].source_location == "line 1 column 20"


def test_parse_cvn_xml_reports_well_formed_non_cvn_xml_as_unmappable():
    result = parse_cvn_xml(FIXTURES / "non_cvn.xml")

    assert result.validation_status == CvnValidationStatus.INVALID
    assert result.errors[0].code == CvnErrorCode.XML_SEMANTICALLY_UNMAPPABLE
    assert result.trace is not None
    assert result.trace.xml_paths[0] == "Document"


def test_parse_cvn_xml_preserves_xml_paths():
    result = parse_cvn_xml(FIXTURES / "minimal_cvn.xml")

    assert result.trace is not None
    assert result.trace.xml_paths[:3] == (
        "CVNRoot",
        "CVNRoot/CVNItem[1]",
        "CVNRoot/CVNItem[1]/Value[1]",
    )
