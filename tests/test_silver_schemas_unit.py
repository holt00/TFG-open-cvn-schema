import pytest

from tfm_lakehouse.silver import records, schemas
from tfm_lakehouse.silver.schemas import column_names, columns_ddl, row_values


def test_record_builders_and_schema_columns_agree():
    person = records.make_person(given_names="Ana", family_name="García", orcid_id=None)
    affiliation = records.make_affiliation(kind=records.KIND_EMPLOYMENT, organization="X")
    publication = records.make_publication(title="T")

    assert set(person) == set(column_names(schemas.PERSON_COLUMNS))
    assert set(affiliation) == set(column_names(schemas.AFFILIATION_COLUMNS))
    assert set(publication) == set(column_names(schemas.PUBLICATION_COLUMNS))


def test_table_columns_are_unique_and_start_with_the_record_id():
    for table, columns in schemas.TABLE_COLUMNS.items():
        names = column_names(columns)
        assert len(names) == len(set(names)), table
        assert names[0] == ("entity_id" if table == "entity" else "record_id"), table


def test_columns_ddl_and_row_values():
    columns = [("a", "STRING"), ("n", "INT"), ("xs", "ARRAY<STRING>")]

    assert columns_ddl(columns) == "a STRING, n INT, xs ARRAY<STRING>"
    assert row_values(columns, {"xs": ["x"], "a": "1", "n": 2}) == ("1", 2, ["x"])
    with pytest.raises(KeyError):
        row_values(columns, {"a": "1"})
