"""Parity of the Spark entity resolution with the in-memory oracle (issue #98).

PySpark cannot be installed on the host's Python 3.14, so the DataFrame version
runs in local mode inside the project's Spark image and its output is compared
with ``resolve_in_memory`` on the same data. Skipped when Docker or the image is
not available (CI has neither).
"""

import json
import random
from pathlib import Path

import pytest
from silver_fixtures import orcid_id
from spark_image import IMAGE, image_available, run_in_image

from tfm_lakehouse.silver import resolution as res
from tfm_lakehouse.silver.records import make_affiliation, make_person
from tfm_lakehouse.synthetic_cvn.builders import vary_name

pytestmark = pytest.mark.skipif(not image_available(), reason=f"needs docker and the {IMAGE} image")

_GIVEN = ["Ana", "José Luis", "María", "Carmen", "Pablo"]
_FAMILY = ["García López", "Martins Gomes", "de la Torre", "Ruiz", "Villacañas de Castro"]
_ORGS = ["Universidad de Vigo", "Universitat de València", "CSIC", "Universidad de Ejemplo"]


def _person(record_id, source, given, family, ident=None, modified=None):
    return {"record_id": record_id, "source": source, **make_person(given_names=given, family_name=family, orcid_id=ident, source_last_modified=modified)}


def _scenario(seed: int = 5):
    """ORCID records with colliding names (to force ambiguity), linked and unlinked CVNs."""
    rng = random.Random(seed)
    persons, affiliations = [], []

    def add(person, organizations):
        persons.append(person)
        affiliations.extend({"record_id": person["record_id"], **make_affiliation(kind="employment", organization=org)} for org in organizations)

    seeds = []
    for number in range(40):
        ident = orcid_id(number + 1)
        given, family = rng.choice(_GIVEN), rng.choice(_FAMILY)
        organizations = rng.sample(_ORGS, rng.randint(1, 2))
        seeds.append((ident, given, family, organizations))
        add(_person(f"orcid_bulk:{ident}", "orcid_bulk", given, family, ident, f"2025-0{rng.randint(1, 9)}-01T00:00:00Z"), organizations)
        if number % 5 == 0:
            add(_person(f"orcid_api:{ident}", "orcid_api", given, family, ident, "2026-01-01T00:00:00Z"), organizations[:1])
    for index, (ident, given, family, organizations) in enumerate(seeds):
        kind = index % 4
        if kind == 0:  # declares its iD
            add(_person(f"synthetic_cvn:{index}", "synthetic_cvn", given, family, ident), organizations)
        elif kind == 1:  # declares its iD, under a name that does not match the ORCID record
            add(_person(f"synthetic_cvn:{index}", "synthetic_cvn", "Zoe", "Nadie", ident), organizations)
        else:  # no iD, name variant
            varied_given, varied_family, _ = vary_name(type("Seed", (), {"given_names": given, "family_name": family})(), rng)
            add(_person(f"synthetic_cvn:{index}", "synthetic_cvn", varied_given, varied_family), organizations if kind == 2 else ["Otra Organización"])
    add(_person("synthetic_cvn:orphan", "synthetic_cvn", "Nadie", "Conocido"), ["Universidad de Vigo"])
    add(_person("synthetic_cvn:no-orgs", "synthetic_cvn", "Ana", "Ruiz"), [])
    return persons, affiliations


def _run_in_spark(tmp_path: Path, persons, affiliations, org_threshold):
    work = tmp_path / "work"
    work.mkdir()
    work.chmod(0o777)  # the container's user (185) is not the host user
    (work / "input.json").write_text(json.dumps({"persons": persons, "affiliations": affiliations, "org_threshold": org_threshold}), encoding="utf-8")
    command = (
        "export PYTHONPATH=/repo/src:/opt/spark/python:$(ls /opt/spark/python/lib/py4j-*-src.zip); "
        "export PYSPARK_PYTHON=python3; python3 /runner/spark_resolution_runner.py"
    )
    completed = run_in_image(
        ["bash", "-c", command], {Path(__file__).resolve().parent: "/runner:ro", work: "/work"}, timeout=600
    )
    assert completed.returncode == 0, completed.stderr[-3000:]
    return json.loads((work / "output.json").read_text(encoding="utf-8"))


def _link_key(link: dict) -> tuple:
    return (link["record_id"], link["source"], link["entity_id"], link["match_rule"], bool(link["ambiguous"]), bool(link["name_conflict"]), json.loads(link["evidence"]))


def _oracle_link_key(link: res.Link) -> tuple:
    return (link.record_id, link.source, link.entity_id, link.match_rule, link.ambiguous, link.name_conflict, json.loads(link.evidence_json()))


@pytest.mark.parametrize("org_threshold", [1.0, 0.5])
def test_spark_resolution_matches_the_in_memory_oracle(tmp_path, org_threshold):
    persons, affiliations = _scenario()
    oracle_links = res.resolve_in_memory(persons, affiliations, org_threshold)
    oracle_entities = res.build_entities(persons, oracle_links)

    output = _run_in_spark(tmp_path, persons, affiliations, org_threshold)

    assert sorted(map(_link_key, output["links"]), key=repr) == sorted(map(_oracle_link_key, oracle_links), key=repr)
    spark_entities = {row["entity_id"]: row for row in output["entities"]}
    assert set(spark_entities) == {row["entity_id"] for row in oracle_entities}
    for expected in oracle_entities:
        assert spark_entities[expected["entity_id"]] == expected

    rules = {link.match_rule for link in oracle_links}
    assert rules == {res.RULE_ORCID_ID, res.RULE_NAME_AFFILIATION, res.RULE_SINGLETON}, "the scenario must exercise every rule"
    assert any(link.ambiguous for link in oracle_links) and any(link.name_conflict for link in oracle_links)
