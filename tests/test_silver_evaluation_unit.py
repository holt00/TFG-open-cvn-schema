import json

from tfm_lakehouse.silver import evaluation as ev

A, B, C, D = "0000-0000-0000-0001", "0000-0000-0000-0002", "0000-0000-0000-0003", "0000-0000-0000-0004"


def _truth(*rows):
    return {f"synthetic_cvn:{d}": ev.GroundTruth(d, seed, linkage, variant) for d, seed, linkage, variant in rows}


def _link(document, entity_id, rule, ambiguous=False):
    return {"record_id": f"synthetic_cvn:{document}", "source": "synthetic_cvn", "entity_id": entity_id, "match_rule": rule, "ambiguous": ambiguous}


def test_load_manifest_keys_ground_truth_by_the_silver_record_id(tmp_path):
    path = tmp_path / "manifest.jsonl"
    path.write_text(
        json.dumps({"document_id": "SYN-1", "seed_orcid_id": A, "linkage": "orcid_id", "name_variant": "exact", "line_number": 0}) + "\n\n",
        encoding="utf-8",
    )

    truth = ev.load_manifest(path)

    assert list(truth) == ["synthetic_cvn:SYN-1"]
    assert truth["synthetic_cvn:SYN-1"].true_entity_id == f"orcid:{A}"


def test_evaluate_counts_correct_false_and_missed_merges_over_the_evaluable_subset():
    truth = _truth(
        ("d1", A, "orcid_id", "exact"),
        ("d2", B, "name_affiliation", "given_initial"),  # evaluable, merged correctly
        ("d3", C, "name_affiliation", "family_upper"),  # evaluable, merged with the wrong person
        ("d4", D, "name_affiliation", "exact"),  # evaluable, ambiguous: missed
        ("d5", "0000-0000-0000-0005", "name_affiliation", "exact"),  # no counterpart, merged anyway: false merge
        ("d6", "0000-0000-0000-0006", "name_affiliation", "exact"),  # no counterpart, left alone: fine
        ("d7", B, "name_affiliation", "accents_stripped"),  # evaluable, no candidate: missed
        ("gone", B, "orcid_id", "exact"),  # not in silver (rejected)
    )
    links = [
        _link("d1", f"orcid:{A}", "orcid_id"),
        _link("d2", f"orcid:{B}", "name_affiliation"),
        _link("d3", f"orcid:{A}", "name_affiliation"),
        _link("d4", "rec:x", "singleton", ambiguous=True),
        _link("d5", f"orcid:{A}", "name_affiliation"),
        _link("d6", "rec:y", "singleton"),
        _link("d7", "rec:z", "singleton"),
        {"record_id": "orcid_bulk:other", "source": "orcid_bulk", "entity_id": "orcid:x", "match_rule": "orcid_id", "ambiguous": False},
    ]

    report = ev.evaluate(links, truth, {A, B, C, D})

    assert report["documents"] == {"in_manifest": 8, "in_silver": 7, "not_in_silver": 1}
    assert report["declared_orcid_id"] == {"documents": 1, "correct": 1, "incorrect": 0, "with_an_orcid_record_in_silver": 1, "fused_with_that_record": 1}
    named = report["name_affiliation"]
    assert (named["documents"], named["evaluable"], named["not_evaluable"]) == (6, 4, 2)
    assert (named["merged"], named["correct_merges"], named["false_merges"]) == (3, 1, 2)
    assert (named["false_merges_of_documents_without_a_counterpart"], named["false_merges_of_documents_merged_with_the_wrong_person"]) == (1, 1)
    assert named["precision"] == 1 / 3 and named["recall"] == 1 / 4
    assert named["missed"] == {"total": 3, "ambiguous": 1, "no_candidate": 1, "merged_with_the_wrong_person": 1}
    assert named["recall_by_name_variant"] == {
        "accents_stripped": {"evaluable": 1, "found": 0},
        "exact": {"evaluable": 1, "found": 0},
        "family_upper": {"evaluable": 1, "found": 0},
        "given_initial": {"evaluable": 1, "found": 1},
    }


def test_a_declared_id_document_in_the_wrong_entity_is_reported_incorrect():
    truth = _truth(("d1", A, "orcid_id", "exact"))

    report = ev.evaluate([_link("d1", f"orcid:{B}", "orcid_id")], truth, {A})

    assert report["declared_orcid_id"]["incorrect"] == 1 and report["declared_orcid_id"]["fused_with_that_record"] == 0


def test_precision_and_recall_are_none_without_merges_or_evaluable_documents():
    report = ev.evaluate([_link("d1", "rec:x", "singleton")], _truth(("d1", "0000-0000-0000-0009", "name_affiliation", "exact")), set())

    named = report["name_affiliation"]
    assert named["precision"] is None and named["recall"] is None
    assert "precision n/a, recall n/a" in ev.format_report(report)


def test_format_report_summarizes_both_rules():
    truth = _truth(("d1", A, "orcid_id", "exact"), ("d2", B, "name_affiliation", "exact"))
    links = [_link("d1", f"orcid:{A}", "orcid_id"), _link("d2", f"orcid:{B}", "name_affiliation")]

    text = ev.format_report(ev.evaluate(links, truth, {A, B}))

    assert "rule orcid_id: 1/1" in text and "precision 100.0%, recall 100.0%" in text
