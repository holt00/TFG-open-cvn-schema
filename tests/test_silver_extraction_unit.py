import copy
import json

import pytest

from silver_fixtures import BIOGRAPHY, orcid_api_record, orcid_id, orcid_xml, synthetic_document
from tfm_lakehouse.silver import cvn, orcid_common
from tfm_lakehouse.silver.cvn import process_cvn_document
from tfm_lakehouse.silver.orcid_api import process_orcid_api_record
from tfm_lakehouse.silver.orcid_xml import process_orcid_xml

IDENT = orcid_id(1234)


def _rules(result):
    return [rule for rule, _ in result.errors]


# --- CVN -------------------------------------------------------------------


def test_valid_cvn_document_yields_person_affiliations_and_publications():
    result = process_cvn_document(synthetic_document(IDENT))

    assert result.is_valid and result.errors == []
    assert result.person["orcid_id"] == IDENT
    assert (result.person["given_norm"], result.person["family_key"]) == ("ana", "garcia")
    assert sorted(a["kind"] for a in result.affiliations) == ["education", "employment", "employment"]
    assert {a["organization_norm"] for a in result.affiliations} == {"ejemplo universidad", "centro pruebas"}
    education = next(a for a in result.affiliations if a["kind"] == "education")
    assert (education["end_year"], education["country"]) == (2012, "ES")
    assert 3 <= len(result.publications) <= 5
    assert any(p["doi"] and p["doi"].startswith("10.1000/t") for p in result.publications)
    assert all(p["authors"] == ["García López, Ana"] and p["year"] for p in result.publications)


def test_cvn_document_without_orcid_has_no_orcid_id():
    result = process_cvn_document(synthetic_document(IDENT, include_orcid=False))
    assert result.is_valid and result.person["orcid_id"] is None


def test_cvn_json_text_and_parsed_document_give_the_same_result():
    document = synthetic_document(IDENT)
    assert process_cvn_document(json.dumps(document)) == process_cvn_document(document)


def test_cvn_rejects_invented_fields_through_the_entity_layer():
    document = synthetic_document(IDENT)
    document["curriculum"]["identity"]["campo_inventado"] = 1

    result = process_cvn_document(document)

    assert not result.is_valid and cvn.RULE_ENTITY in _rules(result)
    assert result.person is None and result.affiliations == [] and result.publications == []


def test_cvn_rejects_a_declared_orcid_id_with_a_bad_checksum():
    document = synthetic_document(IDENT)
    document["curriculum"]["identity"]["identificador_digital_de_autor"] = ["0000-0000-0000-0000"]

    assert cvn.RULE_ORCID in _rules(process_cvn_document(document))


def test_cvn_rejects_a_date_range_that_ends_before_it_starts():
    document = synthetic_document(IDENT)
    entry = next(e for e in document["curriculum"]["professional_experience"] if "fecha_de_finalizacion" in e["data"])
    entry["data"]["fecha_de_inicio"] = {"raw_value": "2030-01", "year": "2030", "month": "01"}

    result = process_cvn_document(document)

    assert cvn.RULE_DATE_ORDER in _rules(result)


def test_cvn_reports_every_failing_layer_not_only_the_first():
    document = synthetic_document(IDENT)
    broken = copy.deepcopy(document)
    broken["curriculum"]["identity"]["campo_inventado"] = 1
    broken["curriculum"]["identity"]["identificador_digital_de_autor"] = ["0000-0000-0000-0000"]

    assert {cvn.RULE_ENTITY, cvn.RULE_ORCID} <= set(_rules(process_cvn_document(broken)))


@pytest.mark.parametrize(("source", "rule"), [("not json", cvn.RULE_PARSE), ("[1, 2]", cvn.RULE_PARSE), ("{}", cvn.RULE_SCHEMA)])
def test_cvn_rejects_unparseable_or_schema_invalid_input(source, rule):
    assert rule in _rules(process_cvn_document(source))


# --- ORCID bulk XML -----------------------------------------------------------


def test_valid_orcid_xml_yields_the_common_shape():
    result = process_orcid_xml(orcid_xml(IDENT))

    assert result.is_valid
    assert result.person["orcid_id"] == IDENT
    assert (result.person["given_norm"], result.person["family_norm"], result.person["family_key"]) == ("ana", "garcia lopez", "garcia")
    assert result.person["source_last_modified"] == "2025-04-21T14:47:21.296Z"
    assert sorted((a["kind"], a["organization_norm"]) for a in result.affiliations) == [
        ("education", "ejemplo universidad"),
        ("employment", "centro pruebas"),
        ("employment", "ejemplo universidad"),
    ]
    current = next(a for a in result.affiliations if a["role"] == "Profesora Titular")
    assert (current["start_year"], current["start_month"], current["end_year"], current["country"]) == (2018, 9, None, "ES")


def test_orcid_xml_takes_one_work_per_group_and_finds_the_doi_in_summary_or_group():
    publications = process_orcid_xml(orcid_xml(IDENT)).publications

    assert [p["title"] for p in publications] == ["Un artículo de ejemplo", "Un capítulo de ejemplo", "Una ponencia sin DOI"]
    assert [p["doi"] for p in publications] == ["10.1000/abc", "10.1000/group-level", None]
    assert publications[0]["year"] == 2020 and publications[0]["work_type"] == "journal-article"


def test_orcid_xml_rejections():
    assert _rules(process_orcid_xml(orcid_xml(IDENT, family=None))) == [orcid_common.RULE_REQUIRED]
    assert _rules(process_orcid_xml(orcid_xml(IDENT, given=None, family=None))) == [orcid_common.RULE_REQUIRED] * 2
    assert _rules(process_orcid_xml(orcid_xml("0000-0000-0000-0000"))) == [orcid_common.RULE_ORCID_ID]
    assert _rules(process_orcid_xml(orcid_xml(IDENT, activities=False))) == [orcid_common.RULE_NO_ACTIVITY]
    assert _rules(process_orcid_xml("<record>")) == [orcid_common.RULE_XML_PARSE]


def test_orcid_extractors_never_read_the_biography():
    for result in (process_orcid_xml(orcid_xml(IDENT)), process_orcid_api_record(orcid_api_record(IDENT))):
        assert BIOGRAPHY not in repr(result)


# --- ORCID API ------------------------------------------------------------------


def test_orcid_api_record_yields_the_same_shape_as_the_xml():
    from_api = process_orcid_api_record(orcid_api_record(IDENT), IDENT)
    from_xml = process_orcid_xml(orcid_xml(IDENT))

    assert from_api.is_valid
    assert from_api.person["source_last_modified"] == "2026-09-18T08:37:11Z"
    assert {k: v for k, v in from_api.person.items() if k != "source_last_modified"} == {
        k: v for k, v in from_xml.person.items() if k != "source_last_modified"
    }
    assert from_api.affiliations == from_xml.affiliations
    assert from_api.publications == from_xml.publications


@pytest.mark.parametrize(
    ("record", "expected"),
    [
        ({**orcid_api_record(IDENT), "orcid-identifier": {"path": orcid_id(99)}}, [orcid_common.RULE_ORCID_ID]),
        (orcid_api_record(IDENT, family=None), [orcid_common.RULE_REQUIRED]),
        ({"orcid-identifier": {"path": IDENT}}, [orcid_common.RULE_REQUIRED, orcid_common.RULE_REQUIRED, orcid_common.RULE_NO_ACTIVITY]),
        ([], [orcid_common.RULE_JSON_SHAPE]),
        (None, [orcid_common.RULE_JSON_SHAPE]),
    ],
)
def test_orcid_api_rejections(record, expected):
    assert _rules(process_orcid_api_record(record, IDENT)) == expected


def test_orcid_api_tolerates_private_names_and_missing_sections():
    record = orcid_api_record(IDENT)
    record["person"]["name"] = None
    del record["activities-summary"]["works"]

    result = process_orcid_api_record(record)

    assert _rules(result) == [orcid_common.RULE_REQUIRED] * 2
