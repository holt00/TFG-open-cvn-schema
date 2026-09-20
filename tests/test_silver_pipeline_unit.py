import json

import pytest

from silver_fixtures import orcid_api_record, orcid_id, orcid_xml, synthetic_document
from tfm_lakehouse.silver import pipeline, schemas
from tfm_lakehouse.silver.orcid_common import RULE_ORCID_ID

IDENT = orcid_id(77)


def _line(payload, source_ref=IDENT):
    return json.dumps({"record_id": f"x:{source_ref}", "source_ref": source_ref, "payload": payload})


def _fields(names, values):
    return dict(zip(schemas.column_names(names), values))


@pytest.mark.parametrize(
    ("source", "payload"),
    [
        (pipeline.SOURCE_SYNTHETIC_CVN, synthetic_document(IDENT)),
        (pipeline.SOURCE_ORCID_BULK, orcid_xml(IDENT)),
        (pipeline.SOURCE_ORCID_API, orcid_api_record(IDENT)),
    ],
)
def test_every_source_yields_a_result_shaped_as_the_udf_schema(source, payload):
    errors, warnings, person, affiliations, publications = pipeline.process_bronze_line(source, _line(payload))

    assert errors == [] and warnings == []
    assert len(person) == len(schemas.PERSON_COLUMNS)
    assert _fields(schemas.PERSON_COLUMNS, person)["orcid_id"] == IDENT
    assert affiliations and all(len(row) == len(schemas.AFFILIATION_COLUMNS) for row in affiliations)
    assert publications and all(len(row) == len(schemas.PUBLICATION_COLUMNS) for row in publications)
    assert len(schemas.RESULT_COLUMNS) == 5


def test_rejected_records_carry_errors_and_no_rows():
    bad_id = orcid_xml("0000-0000-0000-0000")

    errors, _, person, affiliations, publications = pipeline.process_bronze_line(pipeline.SOURCE_ORCID_BULK, _line(bad_id))

    assert [rule for rule, _ in errors] == [RULE_ORCID_ID]
    assert person is None and affiliations == [] and publications == []


@pytest.mark.parametrize("line", ["not json", "[1]", json.dumps({"no": "payload"}), json.dumps({"payload": {}}), json.dumps({"record_id": "", "payload": {}})])
def test_a_line_that_is_not_an_envelope_is_rejected_by_the_envelope_rule(line):
    errors = pipeline.process_bronze_line(pipeline.SOURCE_SYNTHETIC_CVN, line)[0]

    assert [rule for rule, _ in errors] == [pipeline.RULE_ENVELOPE]


def test_an_orcid_bulk_payload_must_be_an_xml_string():
    errors = pipeline.process_bronze_line(pipeline.SOURCE_ORCID_BULK, _line({"not": "xml"}))[0]

    assert [rule for rule, _ in errors] == [pipeline.RULE_ENVELOPE]


def test_an_api_record_for_another_id_than_the_requested_one_is_rejected():
    errors = pipeline.process_bronze_line(pipeline.SOURCE_ORCID_API, _line(orcid_api_record(IDENT), source_ref=orcid_id(78)))[0]

    assert [rule for rule, _ in errors] == [RULE_ORCID_ID]


def test_errors_and_messages_are_capped_so_a_record_cannot_become_a_huge_row(monkeypatch):
    document = synthetic_document(IDENT)
    for index in range(40):
        document["curriculum"]["identity"][f"campo_inventado_{index}"] = "x" * 5000

    errors = pipeline.process_bronze_line(pipeline.SOURCE_SYNTHETIC_CVN, _line(document))[0]

    assert 0 < len(errors) <= 20
    assert all(len(message) <= 1000 for _, message in errors)


def test_an_unknown_source_is_a_programming_error():
    with pytest.raises(ValueError):
        pipeline.process_bronze_line("nope", _line({}))
