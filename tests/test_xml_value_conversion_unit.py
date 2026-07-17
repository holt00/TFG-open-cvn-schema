from open_cvn.xml_semantic_mapping import load_xml_semantic_mapping_index
from open_cvn.xml_value_conversion import convert_xml_value


def test_converts_controlled_reference_with_raw_value():
    mapping = load_xml_semantic_mapping_index().fields_for_code(
        "020.010.010.030",
        group_code="020.010.010.000",
    )[0]

    value = convert_xml_value("Synthetic Degree", mapping)

    assert value == {
        "label": "Synthetic Degree",
        "source": "CVN_TITLE_B",
        "raw_value": "Synthetic Degree",
    }


def test_converts_flexible_date_value():
    mapping = load_xml_semantic_mapping_index().fields_for_code(
        "020.010.010.130",
        group_code="020.010.010.000",
    )[0]

    value = convert_xml_value("2024-06-30", mapping)

    assert value == {"raw_value": "2024-06-30", "year": 2024, "month": 6, "day": 30}


def test_converts_plain_array_value():
    mapping = load_xml_semantic_mapping_index().fields_for_code(
        "060.010.040.350",
        group_code="060.010.040.000",
    )[0]

    assert convert_xml_value("Synthetic Author", mapping) == ["Synthetic Author"]
