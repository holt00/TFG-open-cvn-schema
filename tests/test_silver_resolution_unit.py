import pytest

from tfm_lakehouse.silver import resolution as res
from tfm_lakehouse.silver.records import make_affiliation, make_person
from tfm_lakehouse.synthetic_cvn.builders import vary_name

ID_A = "0000-0002-1825-0097"
ID_B = "0000-0001-5109-3700"


def person(record_id, source, given, family, orcid_id=None, modified=None):
    row = make_person(given_names=given, family_name=family, orcid_id=orcid_id, source_last_modified=modified)
    return {"record_id": record_id, "source": source, **row}


def affiliations(record_id, *organizations):
    return [{"record_id": record_id, **make_affiliation(kind="employment", organization=name)} for name in organizations]


def by_record(links):
    return {link.record_id: link for link in links}


# --- names and organizations ---------------------------------------------------------


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (("ana luiza", "martins gomes"), ("ana luiza", "martins gomes"), True),
        (("ana luiza", "martins"), ("ana luiza", "martins gomes"), True),  # first_surname_only
        (("a", "martins gomes"), ("ana luiza", "martins gomes"), True),  # given_initial
        (("j a", "ruiz"), ("jose antonio", "ruiz"), True),  # several initials
        (("ana m", "luna morales"), ("ana maria", "luna morales"), True),  # an initial spelled out later (real case)
        (("j luis", "ruiz"), ("jose l", "ruiz"), True),
        (("ana m", "luna"), ("ana pedro", "luna"), False),  # the initial does not match
        (("ana", "luna"), ("ana maria", "luna"), False),  # a dropped given name is not evidence enough
        (("a", "martins"), ("ana luiza", "martins gomes"), False),  # two relaxations at once: initial AND surname prefix
        (("i", "garcia"), ("irene", "garcia melian"), False),
        (("ana", "martins gomes"), ("ana", "martins lopez"), False),  # different second surname
        (("ana", "gomes"), ("ana", "martins gomes"), False),  # a suffix is not a leading part
        (("ana", "ruiz"), ("berta", "ruiz"), False),
        (("b", "ruiz"), ("ana", "ruiz"), False),
        (("", "ruiz"), ("ana", "ruiz"), False),
        (("ana", ""), ("ana", "ruiz"), False),
    ],
)
def test_names_compatible(a, b, expected):
    assert res.names_compatible(*a, *b) is expected
    assert res.names_compatible(*b, *a) is expected


def test_the_name_variants_the_generator_produces_are_compatible_with_the_original():
    import random

    seed = type("Seed", (), {"given_names": "José Luis", "family_name": "Villacañas de Castro"})()
    original = person("o", "orcid_bulk", seed.given_names, seed.family_name)
    seen = set()
    for number in range(200):
        given, family, variant = vary_name(seed, random.Random(number))
        seen.add(variant)
        varied = person("v", "synthetic_cvn", given, family)
        assert res.names_compatible(varied["given_norm"], varied["family_norm"], original["given_norm"], original["family_norm"]), variant
        assert (varied["family_key"], varied["given_initial"]) == (original["family_key"], original["given_initial"]), variant
    assert {"accents_stripped", "given_initial", "family_upper", "first_surname_only"} <= seen


@pytest.mark.parametrize(
    ("a", "b", "kind"),
    [
        (("ana", "ruiz"), ("ana", "ruiz"), "full"),
        (("a", "ruiz"), ("ana", "ruiz"), "given_variant"),
        (("ana m", "ruiz"), ("ana maria", "ruiz"), "given_variant"),
        (("ana", "ruiz"), ("ana", "ruiz gomez"), "surname_prefix"),
        (("a", "ruiz"), ("ana", "ruiz gomez"), None),
        (("ana", "ruiz"), ("berta", "ruiz"), None),
    ],
)
def test_name_match_kind(a, b, kind):
    assert res.name_match_kind(*a, *b) == kind
    assert res.name_match_kind(*b, *a) == kind


def test_best_org_similarity():
    assert res.best_org_similarity(["ejemplo universidad"], ["ejemplo universidad", "x"]) == 1.0
    assert res.best_org_similarity(["a b c"], ["a b d"]) == pytest.approx(0.5)
    assert res.best_org_similarity([], ["a"]) == 0.0
    assert res.best_org_similarity(["a"], []) == 0.0


# --- R1: ORCID iD -----------------------------------------------------------------------


def test_records_sharing_an_orcid_id_form_one_entity_across_all_three_sources():
    persons = [
        person("synthetic_cvn:1", "synthetic_cvn", "Ana", "García", ID_A),
        person("orcid_bulk:A", "orcid_bulk", "Ana", "García", ID_A),
        person("orcid_api:A", "orcid_api", "Ana", "García", ID_A),
        person("orcid_bulk:B", "orcid_bulk", "Berta", "Ruiz", ID_B),
    ]

    links = by_record(res.resolve_in_memory(persons, []))

    assert {links[r].entity_id for r in ("synthetic_cvn:1", "orcid_bulk:A", "orcid_api:A")} == {f"orcid:{ID_A}"}
    assert links["orcid_bulk:B"].entity_id == f"orcid:{ID_B}"
    assert all(link.match_rule == res.RULE_ORCID_ID and not link.ambiguous for link in links.values())
    assert links["orcid_bulk:A"].evidence == {"orcid_id": ID_A}


def test_an_orcid_id_match_with_a_different_name_is_kept_but_flagged():
    persons = [
        person("synthetic_cvn:1", "synthetic_cvn", "Carlos", "Pérez", ID_A),
        person("orcid_bulk:A", "orcid_bulk", "Ana", "García", ID_A),
    ]

    links = by_record(res.resolve_in_memory(persons, []))

    assert links["synthetic_cvn:1"].entity_id == links["orcid_bulk:A"].entity_id
    assert links["synthetic_cvn:1"].name_conflict and not links["orcid_bulk:A"].name_conflict


def test_a_cvn_declaring_an_id_absent_from_orcid_is_its_own_anchored_entity_without_conflict():
    links = res.resolve_in_memory([person("synthetic_cvn:1", "synthetic_cvn", "Ana", "García", ID_A)], [])

    assert links[0].entity_id == f"orcid:{ID_A}" and not links[0].name_conflict


# --- R2: name and affiliation ------------------------------------------------------------


def _pair(cvn_given="Ana", cvn_family="García López", cvn_orgs=("Universidad de Ejemplo",), orcid_orgs=("Universidad de Ejemplo",)):
    persons = [
        person("orcid_bulk:A", "orcid_bulk", "Ana", "García López", ID_A),
        person("synthetic_cvn:1", "synthetic_cvn", cvn_given, cvn_family),
    ]
    rows = [*affiliations("orcid_bulk:A", *orcid_orgs), *affiliations("synthetic_cvn:1", *cvn_orgs)]
    return by_record(res.resolve_in_memory(persons, rows))


@pytest.mark.parametrize(
    ("given", "family"),
    [("Ana", "García López"), ("Ana", "GARCÍA LÓPEZ"), ("Ana", "Garcia Lopez"), ("A.", "García López"), ("Ana", "García")],
)
def test_an_id_less_cvn_with_a_name_variant_and_a_shared_organization_joins_the_orcid_entity(given, family):
    link = _pair(cvn_given=given, cvn_family=family)["synthetic_cvn:1"]

    assert link.match_rule == res.RULE_NAME_AFFILIATION and link.entity_id == f"orcid:{ID_A}"
    kind = {"García López": "full", "GARCÍA LÓPEZ": "full", "Garcia Lopez": "full"}.get(family, "surname_prefix" if family == "García" else "full")
    if given == "A.":
        kind = "given_variant"
    assert link.evidence == {"matched_record_id": "orcid_bulk:A", "org_similarity": 1.0, "candidates": 1, "name_match": kind, "shared_organizations": 1}


def test_the_same_name_at_a_different_organization_does_not_merge():
    link = _pair(cvn_orgs=("Otra Universidad",))["synthetic_cvn:1"]

    assert link.match_rule == res.RULE_SINGLETON and link.entity_id == res.entity_id_for_record("synthetic_cvn:1")
    assert not link.ambiguous


def test_a_different_person_at_the_same_organization_does_not_merge():
    assert _pair(cvn_given="Berta", cvn_family="Ruiz")["synthetic_cvn:1"].match_rule == res.RULE_SINGLETON


def test_partial_organization_similarity_is_off_by_default_and_a_threshold_enables_it():
    persons = [person("o", "orcid_bulk", "Ana", "García", ID_A), person("c", "synthetic_cvn", "Ana", "García")]
    rows = [*affiliations("o", "Universidad Autonoma Madrid"), *affiliations("c", "Universidad Autonoma Madrid Facultad Ciencias")]

    assert by_record(res.resolve_in_memory(persons, rows))["c"].match_rule == res.RULE_SINGLETON
    assert by_record(res.resolve_in_memory(persons, rows, org_threshold=0.5))["c"].match_rule == res.RULE_NAME_AFFILIATION


def test_two_candidate_entities_leave_the_record_alone_and_ambiguous():
    persons = [
        person("orcid_bulk:A", "orcid_bulk", "Ana", "García", ID_A),
        person("orcid_bulk:B", "orcid_bulk", "Ana", "García", ID_B),
        person("synthetic_cvn:1", "synthetic_cvn", "Ana", "García"),
    ]
    rows = [*affiliations("orcid_bulk:A", "Universidad de Ejemplo"), *affiliations("orcid_bulk:B", "Universidad de Ejemplo"), *affiliations("synthetic_cvn:1", "Universidad de Ejemplo")]

    link = by_record(res.resolve_in_memory(persons, rows))["synthetic_cvn:1"]

    assert link.match_rule == res.RULE_SINGLETON and link.ambiguous
    assert link.evidence == {"candidates": sorted([f"orcid:{ID_A}", f"orcid:{ID_B}"])}


def test_the_organizations_of_all_records_of_an_entity_count_for_the_match():
    persons = [
        person("orcid_bulk:A", "orcid_bulk", "Ana", "García", ID_A),
        person("orcid_api:A", "orcid_api", "Ana", "García", ID_A),
        person("synthetic_cvn:1", "synthetic_cvn", "Ana", "García"),
    ]
    rows = [*affiliations("orcid_bulk:A", "Vieja Universidad"), *affiliations("orcid_api:A", "Nueva Universidad"), *affiliations("synthetic_cvn:1", "Nueva Universidad")]

    assert by_record(res.resolve_in_memory(persons, rows))["synthetic_cvn:1"].entity_id == f"orcid:{ID_A}"


def test_a_record_without_affiliations_cannot_be_matched_by_name_alone():
    persons = [person("orcid_bulk:A", "orcid_bulk", "Ana", "García", ID_A), person("synthetic_cvn:1", "synthetic_cvn", "Ana", "García")]

    assert by_record(res.resolve_in_memory(persons, affiliations("orcid_bulk:A", "X")))["synthetic_cvn:1"].match_rule == res.RULE_SINGLETON


def test_id_less_records_never_merge_with_each_other():
    persons = [person("synthetic_cvn:1", "synthetic_cvn", "Ana", "García"), person("synthetic_cvn:2", "synthetic_cvn", "Ana", "García")]
    rows = [*affiliations("synthetic_cvn:1", "X"), *affiliations("synthetic_cvn:2", "X")]

    links = res.resolve_in_memory(persons, rows)

    assert len({link.entity_id for link in links}) == 2


def test_resolution_is_deterministic_and_independent_of_input_order():
    persons = [
        person("orcid_bulk:A", "orcid_bulk", "Ana", "García", ID_A),
        person("synthetic_cvn:1", "synthetic_cvn", "Ana", "García"),
        person("synthetic_cvn:2", "synthetic_cvn", "Zoe", "Nadie"),
    ]
    rows = [*affiliations("orcid_bulk:A", "X"), *affiliations("synthetic_cvn:1", "X"), *affiliations("synthetic_cvn:2", "Y")]

    forward = by_record(res.resolve_in_memory(persons, rows))
    backward = by_record(res.resolve_in_memory(list(reversed(persons)), list(reversed(rows))))

    assert forward == backward


# --- entities ------------------------------------------------------------------------------


def test_entities_aggregate_their_links_and_take_the_display_name_from_the_best_record():
    persons = [
        person("synthetic_cvn:1", "synthetic_cvn", "A.", "García", ID_A),
        person("orcid_bulk:A", "orcid_bulk", "Ana", "García López", ID_A, "2025-01-01T00:00:00Z"),
        person("orcid_api:A", "orcid_api", "Ana María", "García López", ID_A, "2026-01-01T00:00:00Z"),
        person("synthetic_cvn:2", "synthetic_cvn", "Zoe", "Nadie"),
    ]
    links = res.resolve_in_memory(persons, [])

    entities = {entity["entity_id"]: entity for entity in res.build_entities(persons, links)}

    anchored = entities[f"orcid:{ID_A}"]
    assert (anchored["orcid_id"], anchored["record_count"]) == (ID_A, 3)
    assert (anchored["given_names"], anchored["family_name"]) == ("Ana María", "García López")
    assert anchored["sources"] == ["orcid_api", "orcid_bulk", "synthetic_cvn"]
    assert (anchored["has_cvn"], anchored["has_orcid"], anchored["rules"]) == (True, True, [res.RULE_ORCID_ID])
    lone = entities[res.entity_id_for_record("synthetic_cvn:2")]
    assert (lone["orcid_id"], lone["record_count"], lone["has_orcid"], lone["rules"]) == (None, 1, False, [res.RULE_SINGLETON])
    assert len(entities) == 2


def test_the_more_recently_modified_record_names_the_entity_when_the_source_ties():
    persons = [
        person("orcid_bulk:1", "orcid_bulk", "Vieja", "Ruiz", ID_A, "2024-01-01T00:00:00Z"),
        person("orcid_bulk:2", "orcid_bulk", "Nueva", "Ruiz", ID_A, "2025-06-01T00:00:00Z"),
        person("orcid_bulk:3", "orcid_bulk", "SinFecha", "Ruiz", ID_A),
    ]

    entity = res.build_entities(persons, res.resolve_in_memory(persons, []))[0]

    assert entity["given_names"] == "Nueva"


def test_singleton_ids_are_stable_sha1_of_the_record_id():
    assert res.entity_id_for_record("synthetic_cvn:1") == res.entity_id_for_record("synthetic_cvn:1")
    assert res.entity_id_for_record("a") != res.entity_id_for_record("b")
    assert len(res.entity_id_for_record("a")) == len("rec:") + 40
