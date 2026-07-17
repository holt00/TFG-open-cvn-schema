from xml.etree import ElementTree

from open_cvn.xml_semantic_extraction import extract_xml_semantic_items


def test_extracts_simplified_namespaced_cvn_item_fields():
    root = ElementTree.fromstring(
        """
        <CVNRoot xmlns="https://example.test/cvn">
          <CVNItem code="020.010.010.000">
            <Field code="020.010.010.030">Synthetic Degree</Field>
          </CVNItem>
        </CVNRoot>
        """
    )

    result = extract_xml_semantic_items(root)

    assert result.items[0].code == "020.010.010.000"
    assert result.items[0].fields[0].code == "020.010.010.030"
    assert result.items[0].fields[0].raw_value == "Synthetic Degree"
    assert result.items[0].xml_path == "CVNRoot/CVNItem[1]"


def test_extracts_official_like_cvn_item_code():
    root = ElementTree.fromstring(
        """
        <CVN>
          <CvnItem>
            <CvnItemID><CodeCVNItem><Item>020.010.010.000</Item></CodeCVNItem></CvnItemID>
            <Title code="020.010.010.030"><Name>Synthetic Degree</Name></Title>
          </CvnItem>
        </CVN>
        """
    )

    result = extract_xml_semantic_items(root)

    assert result.items[0].code == "020.010.010.000"
    assert result.items[0].fields[0].code == "020.010.010.030"
    assert result.items[0].fields[0].raw_value == "Synthetic Degree"
