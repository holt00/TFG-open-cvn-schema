from pathlib import Path
from typing import Any, Mapping

import pymupdf

from open_cvn import CvnErrorCode, CvnSourceFormat, CvnValidationStatus, parse_cvn_pdf
from open_cvn.llm_import import LlmImportConfig, LlmImportRequest, LlmProviderResponse
from open_cvn.pdf_xml_extraction import extract_cvn_xml_from_pdf


CVN_XML = """<?xml version="1.0" encoding="UTF-8"?>
<CVNRoot xmlns="https://example.test/cvn">
  <CVNItem code="020.010.010.000">
    <Field code="020.010.010.030">Synthetic Computer Science Degree</Field>
  </CVNItem>
</CVNRoot>
"""

VALID_OPEN_CVN_JSON: Mapping[str, Any] = {
    "schema_version": "0.1.0",
    "metadata": {
        "language": "es",
        "policy": {
            "name": "default_cvn_semantic_policy",
            "version": "0.1.0",
        },
    },
    "curriculum": {
        "identity": {},
        "education": [],
        "research": [],
        "professional_experience": [],
        "achievements": [],
        "other": [],
    },
}


class RecordingProvider:
    def __init__(self) -> None:
        self.requests: list[LlmImportRequest] = []

    def extract_open_cvn_json(self, request: LlmImportRequest) -> LlmProviderResponse:
        self.requests.append(request)
        return LlmProviderResponse(document=VALID_OPEN_CVN_JSON)


def _save_empty_pdf(path: Path) -> None:
    document = pymupdf.open()
    document.new_page()
    document.save(path)
    document.close()


def _save_pdf_with_embedded_xml(path: Path) -> None:
    document = pymupdf.open()
    document.new_page()
    document.embfile_add("cvn.xml", CVN_XML.encode("utf-8"), filename="cvn.xml")
    document.save(path)
    document.close()


def _save_pdf_with_xml_metadata(path: Path) -> None:
    document = pymupdf.open()
    document.new_page()
    document.set_xml_metadata(CVN_XML)
    document.save(path)
    document.close()


def test_extracts_cvn_xml_from_embedded_file(tmp_path):
    pdf_path = tmp_path / "cvn-embedded.pdf"
    _save_pdf_with_embedded_xml(pdf_path)

    result = extract_cvn_xml_from_pdf(pdf_path)

    assert result.extracted_xml is not None
    assert result.extracted_xml.source_kind == "embedded_file"
    assert result.extracted_xml.source_name == "cvn.xml"
    assert "CVNRoot" in result.extracted_xml.xml_text
    assert result.diagnostics.embedded_file_count == 1


def test_extracts_cvn_xml_from_pdf_xml_metadata(tmp_path):
    pdf_path = tmp_path / "cvn-metadata.pdf"
    _save_pdf_with_xml_metadata(pdf_path)

    result = extract_cvn_xml_from_pdf(pdf_path)

    assert result.extracted_xml is not None
    assert result.extracted_xml.source_kind == "xml_metadata"
    assert result.extracted_xml.metadata_xref is not None
    assert "CVNRoot" in result.extracted_xml.xml_text
    assert result.diagnostics.metadata_present is True


def test_parse_cvn_pdf_returns_extracted_xml_result(tmp_path):
    pdf_path = tmp_path / "cvn.pdf"
    _save_pdf_with_embedded_xml(pdf_path)

    result = parse_cvn_pdf(pdf_path)

    assert result.source_format == CvnSourceFormat.PDF
    assert result.validation_status == CvnValidationStatus.NOT_RUN
    assert result.errors == ()
    assert result.data is not None
    assert "CVNRoot" in result.data["xml_text"]
    assert result.data["extraction"]["source_kind"] == "embedded_file"
    assert result.trace is not None
    assert result.trace.extracted_from == "embedded_file:cvn.xml"


def test_parse_cvn_pdf_can_validate_extracted_xml_to_open_cvn_json(tmp_path):
    pdf_path = tmp_path / "cvn.pdf"
    _save_pdf_with_embedded_xml(pdf_path)

    result = parse_cvn_pdf(pdf_path, validate_extracted_xml=True)

    assert result.source_format == CvnSourceFormat.PDF
    assert result.validation_status == CvnValidationStatus.VALID
    assert result.data is not None
    assert result.data["extensions"]["x-open-cvn.xml_import"]["mapping_status"] == "semantic_partial"
    assert result.data["curriculum"]["education"][0]["data"]["nombre_del_titulo"]["raw_value"] == (
        "Synthetic Computer Science Degree"
    )
    assert result.trace is not None
    assert result.trace.extracted_from == "embedded_file:cvn.xml"
    assert result.trace.cvn_codes == ("020.010.010.000", "020.010.010.030")


def test_parse_cvn_pdf_does_not_call_llm_when_extracted_xml_validates(tmp_path):
    pdf_path = tmp_path / "cvn.pdf"
    _save_pdf_with_embedded_xml(pdf_path)
    provider = RecordingProvider()

    result = parse_cvn_pdf(
        pdf_path,
        validate_extracted_xml=True,
        allow_llm=True,
        llm_config=LlmImportConfig(provider="mock", model="mock-model"),
        llm_provider=provider,
    )

    assert result.validation_status == CvnValidationStatus.VALID
    assert provider.requests == []


def test_parse_cvn_pdf_without_xml_returns_structured_failure(tmp_path):
    pdf_path = tmp_path / "no-xml.pdf"
    _save_empty_pdf(pdf_path)

    result = parse_cvn_pdf(pdf_path)

    assert result.validation_status == CvnValidationStatus.FAILED
    assert result.errors[0].code == CvnErrorCode.PDF_WITHOUT_EXTRACTABLE_XML
    assert result.errors[0].details["embedded_file_count"] == 0
    assert result.errors[0].details["candidate_count"] == 0


def test_parse_cvn_pdf_llm_enabled_without_config_returns_structured_failure(tmp_path):
    pdf_path = tmp_path / "no-xml.pdf"
    _save_empty_pdf(pdf_path)

    result = parse_cvn_pdf(pdf_path, allow_llm=True)

    assert result.validation_status == CvnValidationStatus.FAILED
    assert result.errors[0].code == CvnErrorCode.LLM_IMPORT_DISABLED


def test_parse_cvn_pdf_uses_llm_fallback_when_no_xml_is_available(tmp_path):
    pdf_path = tmp_path / "no-xml.pdf"
    _save_empty_pdf(pdf_path)
    provider = RecordingProvider()

    result = parse_cvn_pdf(
        pdf_path,
        allow_llm=True,
        llm_config=LlmImportConfig(provider="mock", model="mock-model"),
        llm_provider=provider,
    )

    assert result.validation_status == CvnValidationStatus.VALID
    assert result.trace is not None
    assert result.trace.extracted_from == "llm_fallback"
    assert result.data is not None
    assert result.data["extensions"]["x-open-cvn.llm_import"]["fallback_reason"] == (
        "pdf_without_extractable_xml"
    )
    assert len(provider.requests) == 1


def test_parse_cvn_pdf_unreadable_input_returns_structured_failure():
    result = parse_cvn_pdf(b"not a pdf", source_identifier="broken.pdf")

    assert result.validation_status == CvnValidationStatus.FAILED
    assert result.errors[0].code == CvnErrorCode.UNREADABLE_FILE
    assert result.source_identifier == "broken.pdf"


def test_parse_cvn_pdf_mapping_input_is_unsupported():
    result = parse_cvn_pdf({"not": "pdf"}, source_identifier="mapping")

    assert result.validation_status == CvnValidationStatus.FAILED
    assert result.errors[0].code == CvnErrorCode.UNSUPPORTED_INPUT_FORMAT


def test_page_text_is_not_used_as_cvn_xml_fallback(tmp_path):
    pdf_path = tmp_path / "visible-cvn-text.pdf"
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), CVN_XML)
    document.save(pdf_path)
    document.close()

    result = parse_cvn_pdf(pdf_path)

    assert result.validation_status == CvnValidationStatus.FAILED
    assert result.errors[0].code == CvnErrorCode.PDF_WITHOUT_EXTRACTABLE_XML
