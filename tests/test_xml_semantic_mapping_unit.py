from open_cvn.xml_semantic_mapping import load_xml_semantic_mapping_index


def test_mapping_index_contains_representative_entities_and_fields():
    index = load_xml_semantic_mapping_index()

    identity = index.entity_for_group("000.010.000.000")
    education = index.entity_for_group("020.010.010.000")
    research = index.entity_for_group("060.010.040.000")

    assert identity is not None
    assert identity.entity_id == "identity.person"
    assert identity.source_group_key == "__no_cvn_item__"
    assert education is not None
    assert education.domain_area_id == "education"
    assert research is not None
    assert research.domain_area_id == "research"
    assert index.fields_for_code("000.010.000.020", group_code="000.010.000.000")[0].field_name == "nombre"
    assert index.fields_for_code("020.010.010.030", group_code="020.010.010.000")[0].field_name == (
        "nombre_del_titulo"
    )


def test_mapping_index_scopes_duplicate_codes_by_group():
    index = load_xml_semantic_mapping_index()

    fields = index.fields_for_code("020.010.010.000", group_code="020.010.010.000")

    assert fields
    assert all(field.source_group_key == "020.010.010.000" for field in fields)
