"""The issue #99 gold jobs end to end, in local-mode Spark inside the Spark image.

``silver_to_gold`` runs on a small hand-built silver whose gold values were worked out
by hand (the comments say how); ``publish_gold_to_postgres`` runs against a real
PostgreSQL 17 container. Skipped when Docker or the images are not available.
"""

import json
import subprocess
import uuid
from pathlib import Path

import pytest
from spark_image import GOLD_IMAGE, POSTGRES_IMAGE, image_available, run_in_image

pytestmark = pytest.mark.skipif(
    not (image_available(GOLD_IMAGE) and image_available(POSTGRES_IMAGE)),
    reason=f"needs docker and the {GOLD_IMAGE} and {POSTGRES_IMAGE} images",
)

MAX_YEAR = 2027
PASSWORD = "test-password"

ANA, BERTA, CARLA, DANI = "orcid:0000-0001-0000-0001", "orcid:0000-0001-0000-0002", "rec:carla", "orcid:0000-0001-0000-0004"


def _entity(entity_id, given, family, sources, has_cvn, has_orcid, records, orcid=None):
    return {
        "entity_id": entity_id, "orcid_id": orcid, "given_names": given, "family_name": family, "record_count": records,
        "sources": sources, "rules": [], "has_cvn": has_cvn, "has_orcid": has_orcid,
    }


def _pub(record_id, title, year, doi=None):
    return {"record_id": record_id, "title": title, "title_norm": title, "year": year, "doi": doi}


def _aff(record_id, kind, organization, norm, start, end, role=None):
    return {
        "record_id": record_id, "kind": kind, "organization": organization, "organization_norm": norm,
        "role": role, "start_year": start, "end_year": end,
    }


SILVER = {
    "entity": [
        _entity(ANA, "Ana", "García", ["synthetic_cvn", "orcid_bulk"], True, True, 2, "0000-0001-0000-0001"),
        _entity(BERTA, "Berta", "Ruiz", ["orcid_bulk"], False, True, 1, "0000-0001-0000-0002"),
        _entity(CARLA, "Carla", "Pérez", ["synthetic_cvn"], True, False, 1),
        _entity(DANI, "Dani", "Sanz", ["orcid_api"], False, True, 1, "0000-0001-0000-0004"),
    ],
    "entity_link": [
        {"record_id": record, "source": "x", "entity_id": entity, "match_rule": "orcid_id", "evidence": "{}", "ambiguous": False, "name_conflict": False}
        for record, entity in [("r1", ANA), ("r2", ANA), ("r3", BERTA), ("r4", CARLA), ("r5", DANI)]
    ],
    "publication": [
        # Ana, ORCID record: a, b, a work with no DOI, a work with a DOI and no year.
        _pub("r1", "p1", 2020, "10.1/a"), _pub("r1", "p2", 2021, "10.1/b"), _pub("r1", "t3", 2019), _pub("r1", "p4", None, "10.1/noyear"),
        # Ana, CVN record: the same `a` (earlier year: the minimum wins), the same no-DOI work, a year before 1900, a year after max.
        _pub("r2", "p1", 2019, "10.1/a"), _pub("r2", "t3", 2019), _pub("r2", "t5", 1850), _pub("r2", "p6", 2028, "10.1/future"),
        # Berta shares a and b with Ana and has z.
        _pub("r3", "p1", 2020, "10.1/a"), _pub("r3", "p2", 2021, "10.1/b"), _pub("r3", "p7", 2022, "10.1/z"),
        # Carla (a CVN singleton) shares z with Berta.
        _pub("r4", "p7", 2022, "10.1/z"), _pub("r4", "p8", 2023, "10.1/w"),
    ],
    "affiliation": [
        _aff("r1", "employment", "Universidad de Vigo", "universidad vigo", 2010, None),
        _aff("r1", "education", "Universidad de Vigo", "universidad vigo", 2004, 2009),
        _aff("r2", "employment", "Universidad de Vigo", "universidad vigo", 2010, 2015, "Profesora"),
        _aff("r2", "employment", "CSIC", "csic", 2016, None, "Investigadora"),
        _aff("r3", "employment", "CSIC", "csic", None, None),
        _aff("r5", "employment", "Universidad de Vigo", "universidad vigo", 2000, 2001),
    ],
}


def _run(tmp_path: Path, payload: dict, *, network: str | None = None, env: dict | None = None) -> dict:
    work = tmp_path / "work"
    work.mkdir(exist_ok=True)
    work.chmod(0o777)  # the container's user is not the host user
    (work / "input.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    command = (
        "export PYTHONPATH=/repo/src:/repo/tests PYSPARK_PYTHON=python3; exec /opt/spark/bin/spark-submit --master local[2] "
        "--conf spark.ui.enabled=false /repo/tests/spark_gold_runner.py"
    )
    completed = run_in_image(["bash", "-c", command], {work: "/work"}, image=GOLD_IMAGE, network=network, env=env)
    assert completed.returncode == 0, completed.stdout[-3000:] + completed.stderr[-3000:]
    return json.loads((work / "output.json").read_text(encoding="utf-8"))


def _rows(output: dict, table: str, key: str) -> dict:
    return {row[key] if isinstance(key, str) else tuple(row[k] for k in key): row for row in output["tables"][table]}


@pytest.fixture(scope="module")
def gold(tmp_path_factory):
    """One run of silver_to_gold over the hand-built silver, and a second identical one."""
    tmp_path = tmp_path_factory.mktemp("gold")
    steps = [
        {"op": "gold", "options": {"run_id": "test-run", "max_year": MAX_YEAR, "shuffle_partitions": 4}},
    ]
    output = _run(tmp_path, {"silver": SILVER, "steps": steps, "dump": _TABLES})
    second = _run(
        tmp_path,
        {"silver": SILVER, "steps": [{"op": "gold", "options": {"run_id": "test-run", "max_year": MAX_YEAR, "shuffle_partitions": 4}}], "dump": _TABLES},
    )
    return output, second


_TABLES = ["dim_researcher", "publications_per_researcher_year", "affiliation_timeline", "collaboration_pairs", "gold_run"]


def test_publications_are_counted_once_per_entity_and_the_earliest_year_wins(gold):
    output, _ = gold
    per_year = _rows(output, "publications_per_researcher_year", ("entity_id", "year"))

    # Ana: a (2020 and 2019 -> 2019) and the no-DOI work (2019 twice) are 2019; b is 2021.
    assert per_year[(ANA, 2019)]["publication_count"] == 2
    assert per_year[(ANA, 2021)]["publication_count"] == 1
    assert (ANA, 2020) not in per_year
    assert per_year[(BERTA, 2020)]["publication_count"] == 1
    assert {k for k in per_year if k[0] == BERTA} == {(BERTA, 2020), (BERTA, 2021), (BERTA, 2022)}
    assert {k for k in per_year if k[0] == CARLA} == {(CARLA, 2022), (CARLA, 2023)}
    assert len(per_year) == 7


def test_works_without_a_usable_year_are_excluded_from_the_per_year_indicator_only(gold):
    output, _ = gold
    per_year = _rows(output, "publications_per_researcher_year", ("entity_id", "year"))
    dim = _rows(output, "dim_researcher", "entity_id")

    years = {year for entity, year in per_year if entity == ANA}
    assert years == {2019, 2021}  # no 1850, no 2028, no null
    # Ana has six distinct works: a, b, the no-DOI one, no-year, 1850 and 2028.
    assert dim[ANA]["publication_count"] == 6


def test_dim_researcher(gold):
    dim = _rows(gold[0], "dim_researcher", "entity_id")

    ana = dim[ANA]
    assert (ana["display_name"], ana["sources"], ana["has_cvn"], ana["has_orcid"], ana["record_count"]) == (
        "Ana García", "orcid_bulk,synthetic_cvn", True, True, 2,
    )
    assert (ana["first_publication_year"], ana["last_publication_year"]) == (2019, 2021)
    assert ana["organization_count"] == 2
    # Employment only: Vigo 2010-2015 and CSIC from 2016 with no end -> last known year 2016.
    assert (ana["career_start_year"], ana["career_last_year"], ana["career_span_years"]) == (2010, 2016, 6)
    assert dim[BERTA]["publication_count"] == 3 and dim[BERTA]["career_span_years"] is None  # an undated employment
    assert dim[CARLA]["organization_count"] == 0 and dim[CARLA]["publication_count"] == 2
    dani = dim[DANI]
    assert (dani["publication_count"], dani["first_publication_year"], dani["career_span_years"]) == (0, None, 1)
    assert len(dim) == 4


def test_affiliation_timeline_merges_records_of_the_same_stay(gold):
    rows = [r for r in gold[0]["tables"]["affiliation_timeline"] if r["entity_id"] == ANA]
    by_key = {(r["kind"], r["organization_norm"], r["start_year"]): r for r in rows}

    assert len(rows) == 3
    merged = by_key[("employment", "universidad vigo", 2010)]
    assert merged["end_year"] == 2015 and merged["role"] == "Profesora"  # one record's missing end does not erase the other's
    assert by_key[("education", "universidad vigo", 2004)]["end_year"] == 2009
    assert by_key[("employment", "csic", 2016)]["end_year"] is None
    assert len(gold[0]["tables"]["affiliation_timeline"]) == 5  # Ana 3, Berta 1 (undated), Dani 1


def test_collaboration_pairs_share_dois_between_distinct_entities(gold):
    pairs = _rows(gold[0], "collaboration_pairs", ("entity_a", "entity_b"))

    assert set(pairs) == {(ANA, BERTA), (BERTA, CARLA)}  # stored once, entity_a < entity_b
    ana_berta = pairs[(ANA, BERTA)]
    # a (Ana 2019, Berta 2020 -> 2019) and b (2021, 2021).
    assert (ana_berta["shared_publications"], ana_berta["first_year"], ana_berta["last_year"]) == (2, 2019, 2021)
    assert ana_berta["has_cvn_member"] is True  # Ana's entity has a CVN record
    berta_carla = pairs[(BERTA, CARLA)]
    assert (berta_carla["shared_publications"], berta_carla["first_year"], berta_carla["last_year"]) == (1, 2022, 2022)
    assert berta_carla["has_cvn_member"] is True


def test_gold_run_records_provenance_and_counts(gold):
    output, _ = gold
    run = output["tables"]["gold_run"]
    summary = output["results"][0]["ok"]

    assert len(run) == 1
    row = run[0]
    assert row["run_id"] == "test-run" and row["max_year"] == MAX_YEAR
    assert set(json.loads(row["silver_snapshots"])) == {"entity", "entity_link", "publication", "affiliation"}
    assert all(isinstance(v, int) for v in json.loads(row["silver_snapshots"]).values())
    assert (row["entities"], row["entities_with_publications"]) == (4, 3)
    assert (row["publication_rows_read"], row["publications_distinct"], row["publications_without_year"]) == (13, 11, 3)
    assert (row["affiliation_rows_read"], row["timeline_rows"], row["per_year_rows"], row["collaboration_pairs"]) == (6, 5, 7, 2)
    assert row["dois_excluded_too_many_entities"] == 0
    assert summary["tables"] == {"dim_researcher": 4, "publications_per_researcher_year": 7, "affiliation_timeline": 5, "collaboration_pairs": 2, "gold_run": 1}


def test_a_rebuild_of_the_same_silver_gives_the_same_gold(gold):
    def content(output):
        return {name: sorted(json.dumps(r, sort_keys=True) for r in rows if "computed_at" not in r and "silver_snapshots" not in r) for name, rows in output["tables"].items() if name != "gold_run"}

    assert content(gold[0]) == content(gold[1])


def test_the_doi_guard_skips_pairs_of_dois_reported_by_too_many_entities(tmp_path):
    steps = [{"op": "gold", "options": {"run_id": "guard", "max_year": MAX_YEAR, "max_entities_per_doi": 1}}]
    output = _run(tmp_path, {"silver": SILVER, "steps": steps, "dump": ["collaboration_pairs", "gold_run"]})

    assert output["tables"]["collaboration_pairs"] == []
    assert output["tables"]["gold_run"][0]["dois_excluded_too_many_entities"] == 3  # a, b and z are each reported by two entities


def test_nothing_is_written_when_silver_is_empty_or_incomplete(tmp_path):
    empty = {name: [] for name in SILVER}
    (tmp_path / "empty").mkdir()
    output = _run(tmp_path / "empty", {"silver": empty, "steps": [{"op": "gold"}], "dump": _TABLES})
    assert "is empty" in output["results"][0]["error"]
    assert output["gold_tables_present"] == []

    missing = {name: rows for name, rows in SILVER.items() if name != "affiliation"}
    (tmp_path / "missing").mkdir()
    output = _run(tmp_path / "missing", {"silver": missing, "steps": [{"op": "gold"}], "dump": _TABLES})
    assert "lakehouse.silver.affiliation is missing" in output["results"][0]["error"]
    assert output["gold_tables_present"] == []


# ---------------------------------------------------------------- publish (real PostgreSQL)


@pytest.fixture()
def postgres():
    name = f"pg-gold-test-{uuid.uuid4().hex[:8]}"
    network = f"net-{name}"
    subprocess.run(["docker", "network", "create", network], check=True, capture_output=True)
    subprocess.run(
        ["docker", "run", "-d", "--rm", "--name", name, "--network", network, "-e", f"POSTGRES_PASSWORD={PASSWORD}",
         "-e", "POSTGRES_USER=gold", "-e", "POSTGRES_DB=gold", POSTGRES_IMAGE],
        check=True, capture_output=True,
    )
    try:
        for _ in range(60):
            if subprocess.run(["docker", "exec", name, "pg_isready", "-U", "gold", "-d", "gold"], capture_output=True).returncode == 0:
                # the entrypoint restarts the server once after initialisation
                if subprocess.run(["docker", "exec", name, "psql", "-U", "gold", "-d", "gold", "-c", "select 1"], capture_output=True).returncode == 0:
                    break
            subprocess.run(["sleep", "1"])
        else:
            pytest.fail("PostgreSQL did not start")

        def psql(sql: str) -> str:
            done = subprocess.run(["docker", "exec", name, "psql", "-U", "gold", "-d", "gold", "-At", "-c", sql], capture_output=True, text=True)
            assert done.returncode == 0, done.stderr
            return done.stdout.strip()

        yield name, network, psql
    finally:
        subprocess.run(["docker", "rm", "-f", name], capture_output=True)
        subprocess.run(["docker", "network", "rm", network], capture_output=True)


def _publish_steps(name: str, run_id: str) -> list[dict]:
    url = f"jdbc:postgresql://{name}:5432/gold"
    return [
        {"op": "gold", "options": {"run_id": run_id, "max_year": MAX_YEAR, "shuffle_partitions": 4}},
        {"op": "publish", "jdbc_url": url},
    ]


def test_publish_creates_the_tables_with_constraints_and_no_staging_left(tmp_path, postgres):
    name, network, psql = postgres
    output = _run(tmp_path, {"silver": SILVER, "steps": _publish_steps(name, "run-1"), "dump": []}, network=network, env={"PG_PASSWORD": PASSWORD})

    assert "ok" in output["results"][1], output["results"][1]
    assert output["results"][1]["ok"]["tables"] == {"dim_researcher": 4, "publications_per_researcher_year": 7, "affiliation_timeline": 5, "collaboration_pairs": 2, "gold_run": 1}
    assert psql("select count(*) from gold.dim_researcher") == "4"
    assert psql("select publication_count from gold.dim_researcher where entity_id = 'orcid:0000-0001-0000-0001'") == "6"
    assert psql("select run_id from gold.gold_run") == "run-1"
    assert psql("select data_type from information_schema.columns where table_schema='gold' and table_name='gold_run' and column_name='computed_at'") == "timestamp with time zone"
    assert psql("select count(*) from information_schema.tables where table_schema='gold' and table_name like '\\_new\\_%'") == "0"
    # the primary key and the secondary indexes carry their final names
    names = set(psql("select indexname from pg_indexes where schemaname='gold'").splitlines())
    assert {"dim_researcher_pkey", "publications_per_researcher_year_pkey", "collaboration_pairs_pkey", "gold_run_pkey",
            "publications_per_researcher_year_year_idx", "affiliation_timeline_entity_id_idx", "collaboration_pairs_entity_b_idx"} <= names
    assert not {n for n in names if n.startswith("_new_")}


def test_a_second_publish_replaces_the_first_and_a_failed_one_changes_nothing(tmp_path, postgres):
    name, network, psql = postgres
    env = {"PG_PASSWORD": PASSWORD}
    first_dir = tmp_path / "a"
    first_dir.mkdir()
    first = _run(first_dir, {"silver": SILVER, "steps": _publish_steps(name, "run-1"), "dump": []}, network=network, env=env)
    assert "ok" in first["results"][1]
    second_dir = tmp_path / "b"
    second_dir.mkdir()
    second = _run(second_dir, {"silver": SILVER, "steps": _publish_steps(name, "run-2"), "dump": []}, network=network, env=env)
    assert "ok" in second["results"][1]
    assert psql("select run_id from gold.gold_run") == "run-2"  # replaced, not appended
    assert psql("select count(*) from gold.dim_researcher") == "4"

    # A view squatting on a staging name makes the publish fail before anything is staged.
    psql("create view gold._new_gold_run as select 1 as x")
    third_dir = tmp_path / "c"
    third_dir.mkdir()
    third = _run(third_dir, {"silver": SILVER, "steps": _publish_steps(name, "run-3"), "dump": []}, network=network, env=env)

    assert "error" in third["results"][1]
    assert psql("select run_id from gold.gold_run") == "run-2"  # the published tables kept the previous content
    assert psql("select count(*) from gold.dim_researcher") == "4"
    psql("drop view gold._new_gold_run")


def test_publish_refuses_when_gold_has_not_been_built(tmp_path, postgres):
    name, network, psql = postgres
    steps = [{"op": "publish", "jdbc_url": f"jdbc:postgresql://{name}:5432/gold"}]
    output = _run(tmp_path, {"silver": {}, "steps": steps, "dump": []}, network=network, env={"PG_PASSWORD": PASSWORD})

    assert "missing" in output["results"][0]["error"]
    assert psql("select count(*) from information_schema.tables where table_schema='gold'") == "0"
