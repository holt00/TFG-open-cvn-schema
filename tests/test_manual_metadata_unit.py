import pytest as pt

from cvn_codegen.manual_metadata import (
    build_manual_code_entry,
    select_name_detail,
    load_specification_manual,
    extract_manual_entries
)
from cvn_codegen.normalization_types import ManualCodeEntry, SourceTrace
from generated.specification_manual.specification_manual import (
    SpecificationManual,
    NameType,
)
from generated.specification_manual.isoutilities import Iso639
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SPECIFICATION_MANUAL_XML = (
    REPO_ROOT
    / "docs"
    / "CvnXML_v1.4.3_2.1_17012025"
    / "XML"
    / "SpecificationManual.xml"
)

#---------------- TESTS FOR load_specification_manual --------------------

def test_load_specification_manual_raises_for_missing_file(tmp_path):

#arrange
    
    missing_path_file = tmp_path / "non_existent_file.xml"

    #act and assert
    with pt.raises(FileNotFoundError):
        load_specification_manual(missing_path_file)

def test_load_specification_manual_parses_canonical_file():
    #arrange
    specification_manual_path = SPECIFICATION_MANUAL_XML

    #act
    specification_manual = load_specification_manual(specification_manual_path)

    #assert
    assert isinstance(specification_manual, SpecificationManual), (
        f"Expected result to be an instance of SpecificationManual, but got {type(specification_manual)}."
    )
    assert len(specification_manual.manual.item) > 0, "Expected at least one item in the specification manual, but found none."


#---------------- TESTS FOR select_name_detail --------------------

def test_select_name_detail_return_none_for_empty_list():
    #arrange
    name_details= []

    #act

    selected_name_detail = select_name_detail(name_details)

    #assert
    assert selected_name_detail is None, f"Expected None for empty list, but got {selected_name_detail}."

def test_select_name_detail_prefers_requested_language():
    #arrange
    english_detail = NameType.NameDetail(
        name="Gender",
        short_name="Gender",
        lang = Iso639.ENG,
    )
    spanish_detail = NameType.NameDetail(
        name="Sexo",
        short_name="Sexo",
        lang = Iso639.SPA,
    )
    french_detail = NameType.NameDetail(
        name="Sexe",
        short_name="Sexe",
        lang = Iso639.FRA,
    )
    name_details = [english_detail, spanish_detail, french_detail]

    #act
    selected_detail = select_name_detail(name_details, preferred_language="spa")

    #assert
    assert selected_detail == spanish_detail, f"Expected Spanish detail to be selected, but got {selected_detail}."

def test_select_name_detail_falls_back_to_first_entry():
    # Arrange
    english_detail = NameType.NameDetail(
        name="Gender",
        short_name="Gender",
        lang = Iso639.ENG,
    )
    french_detail = NameType.NameDetail(
        name="Sexe",
        short_name="Sexe",
        lang = Iso639.FRA,
    )
    name_details = [english_detail, french_detail]
    # Act
    selected_name_detail = select_name_detail(
        name_details,
        preferred_language="spa",
    )
    # Assert
    assert selected_name_detail == english_detail, (
        "Expected first name detail to be returned when preferred language is missing."
    )

#---------------- TESTS FOR build_manual_code_entry --------------------

def get_manual_item_by_code(specification_manual: SpecificationManual, code: str,) -> SpecificationManual.Manual.Item:
    for item in specification_manual.manual.item:
        if str(item.code).strip() == code:
            return item
    raise AssertionError(f"Manual item with code '{code}' was not found.")


def test_build_manual_code_entry_maps_expected_fields_for_known_code():
    # Arrange
    specification_manual = load_specification_manual(SPECIFICATION_MANUAL_XML)
    item = get_manual_item_by_code(specification_manual, "000.010.000.030")
    # Act
    entry = build_manual_code_entry(item)
    # Assert
    assert entry.code == "000.010.000.030"
    assert entry.manual_name == "Sexo"
    assert entry.manual_short_name == "Sexo"
    assert entry.manual_type == "Alphanumeric"
    assert entry.manual_obligatory is True
    assert entry.manual_multiplicity is False
    assert entry.manual_reference_table == "CVN_SEX_A"
    assert entry.trace.source_file == "SpecificationManual.xml"
    assert entry.trace.source_code == "000.010.000.030"

def test_build_manual_code_entry_raises_for_empty_code():
    # Arrange
    specification_manual = load_specification_manual(SPECIFICATION_MANUAL_XML)
    item = get_manual_item_by_code(specification_manual, "000.010.000.030")
    invalid_item = item.model_copy(update={"code": "   "})

    # Act / Assert
    with pt.raises(ValueError) as exc_info:
        build_manual_code_entry(invalid_item)
    assert "empty" in str(exc_info.value).lower()

#---------------- TESTS FOR extract_manual_entries --------------------

def test_extract_manual_entries_returns_expected_canonical_count():
    # Arrange
    specification_manual = load_specification_manual(SPECIFICATION_MANUAL_XML)
    # Act
    entries_by_code = extract_manual_entries(specification_manual)
    # Assert
    assert isinstance(entries_by_code, dict), (
        f"Expected a dictionary, but got {type(entries_by_code)}."
    )
    assert len(entries_by_code) == 1456, (
        f"Expected 1456 manual entries, but got {len(entries_by_code)}."
    )
    assert "000.010.000.030" in entries_by_code, (
        "Expected code '000.010.000.030' to be present in manual entries."
    )


def test_extract_manual_entries_raises_for_duplicate_codes():
    # Arrange
    specification_manual = load_specification_manual(SPECIFICATION_MANUAL_XML)
    first_item = specification_manual.manual.item[0]
    second_item = specification_manual.manual.item[1].model_copy(
        update={"code": str(first_item.code).strip()}
    )
    duplicated_items = [first_item, second_item]
    duplicated_manual = specification_manual.manual.model_copy(
        update={"item": duplicated_items}
    )
    duplicated_specification_manual = specification_manual.model_copy(
        update={"manual": duplicated_manual}
    )
    # Act / Assert
    with pt.raises(ValueError) as exc_info:
        extract_manual_entries(duplicated_specification_manual)
    assert "duplicate" in str(exc_info.value).lower()
    

def test_extract_manual_entries_returns_expected_entry_for_known_code():
    # Arrange
    specification_manual = load_specification_manual(SPECIFICATION_MANUAL_XML)
    # Act
    entries_by_code = extract_manual_entries(specification_manual)
    entry = entries_by_code["000.010.000.030"]
    # Assert
    assert isinstance(entry, ManualCodeEntry)
    assert entry.manual_name == "Sexo"
    assert entry.manual_reference_table == "CVN_SEX_A"