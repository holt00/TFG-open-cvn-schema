"""The gold table definitions and the PostgreSQL publish SQL (issue #99), on the host, no Spark."""

import pytest

from tfm_lakehouse.gold import schemas


def test_every_table_has_unique_columns_and_supported_types():
    assert set(schemas.TABLES) == set(schemas.TABLE_COLUMNS)
    for table, columns in schemas.TABLE_COLUMNS.items():
        names = schemas.column_names(columns)
        assert len(names) == len(set(names)), table
        for _, type_ in columns:
            assert type_ in schemas.PG_TYPES, f"{table}: no PostgreSQL type for {type_}"


def test_keys_and_indexes_refer_to_real_columns():
    for table, key in schemas.PRIMARY_KEYS.items():
        assert set(key) <= set(schemas.column_names(schemas.TABLE_COLUMNS[table])), table
    for table, indexes in schemas.INDEXES.items():
        for columns in indexes:
            assert set(columns) <= set(schemas.column_names(schemas.TABLE_COLUMNS[table])), table


def test_all_postgres_identifiers_fit_in_63_characters():
    too_long = [name for name in schemas.all_identifiers() if len(name) > schemas.MAX_IDENTIFIER_LENGTH]
    assert too_long == []


def test_all_postgres_identifiers_are_distinct():
    names = schemas.all_identifiers()
    assert len(names) == len(set(names))


def test_create_staging_sql_uses_explicit_types_and_a_named_primary_key():
    sql = schemas.create_staging_sql("gold", schemas.PUBLICATIONS_PER_RESEARCHER_YEAR)

    assert sql == (
        'CREATE TABLE "gold"."_new_publications_per_researcher_year" ('
        '"entity_id" TEXT NOT NULL, "year" INTEGER NOT NULL, "publication_count" INTEGER, '
        'CONSTRAINT "_new_publications_per_researcher_year_pkey" PRIMARY KEY ("entity_id", "year"))'
    )


def test_timestamp_columns_keep_their_time_zone():
    assert "TIMESTAMPTZ" in schemas.create_staging_sql("gold", schemas.GOLD_RUN)


def test_a_table_without_primary_key_has_no_constraint():
    assert "CONSTRAINT" not in schemas.create_staging_sql("gold", schemas.AFFILIATION_TIMELINE)


def test_prepare_statements_drop_leftovers_first_and_never_touch_published_tables():
    statements = schemas.prepare_statements("gold")

    assert statements[0] == 'CREATE SCHEMA IF NOT EXISTS "gold"'
    assert statements[1] == 'DROP TABLE IF EXISTS "gold"."_new_dim_researcher"'
    assert statements[2].startswith('CREATE TABLE "gold"."_new_dim_researcher"')
    for statement in statements:
        assert "_new_" in statement or statement.startswith("CREATE SCHEMA")


def test_swap_statements_replace_every_table_and_rename_its_indexes():
    statements = schemas.swap_statements("gold")

    for table in schemas.TABLES:
        drop = f'DROP TABLE IF EXISTS "gold"."{table}"'
        rename = f'ALTER TABLE "gold"."_new_{table}" RENAME TO "{table}"'
        assert drop in statements and rename in statements
        assert statements.index(drop) < statements.index(rename)
    assert 'ALTER INDEX "gold"."_new_collaboration_pairs_pkey" RENAME TO "collaboration_pairs_pkey"' in statements
    assert 'ALTER INDEX "gold"."_new_affiliation_timeline_entity_id_idx" RENAME TO "affiliation_timeline_entity_id_idx"' in statements
    # Nothing but drops, renames of tables and of indexes: no data statement can fail half way.
    assert all(s.startswith(("DROP TABLE", "ALTER TABLE", "ALTER INDEX")) for s in statements)


def test_every_index_created_on_staging_is_renamed_by_the_swap():
    created = {s.split()[2] for s in schemas.index_statements("gold")}
    renamed = {s.split()[2].split(".")[-1] for s in schemas.swap_statements("gold") if s.startswith("ALTER INDEX")}

    assert created <= renamed


def test_cleanup_statements_only_drop_staging_tables():
    statements = schemas.cleanup_statements("gold")

    assert len(statements) == len(schemas.TABLES)
    assert all("_new_" in s and s.startswith("DROP TABLE IF EXISTS") for s in statements)


def test_quote_ident_escapes_quotes():
    assert schemas.quote_ident('a"b') == '"a""b"'


def test_row_values_orders_by_column_and_rejects_a_missing_key():
    columns = [("a", "STRING"), ("n", "INT")]

    assert schemas.row_values(columns, {"n": 2, "a": "x"}) == ("x", 2)
    with pytest.raises(KeyError):
        schemas.row_values(columns, {"a": "x"})


def test_columns_ddl():
    assert schemas.columns_ddl([("a", "STRING"), ("n", "INT")]) == "a STRING, n INT"
