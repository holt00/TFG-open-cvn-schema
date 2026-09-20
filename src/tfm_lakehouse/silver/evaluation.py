"""Measuring entity resolution against the synthetic generator's ground truth (issue #98, D12).

The generator (issue #96) records, per document, the ORCID iD of the record it
was seeded from (``seed_orcid_id``) and how the document was meant to be linked
(``linkage``): ``orcid_id`` when it declares the iD, ``name_affiliation`` when it
does not and has to be found by name and affiliation. The true entity of a
document is therefore ``orcid:<seed_orcid_id>``.

Only documents whose seed record is present in silver are *evaluable*: the
bronze bulk landing is a capped sample, so most seeds are not there. A merge of
a document whose seed is absent is still counted, as a false merge, because
nothing correct could have been merged with it.
"""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tfm_lakehouse.silver.resolution import (
    RULE_NAME_AFFILIATION,
    RULE_ORCID_ID,
    SOURCE_CVN,
    entity_id_for_orcid,
)

LINKAGE_ORCID_ID = "orcid_id"
LINKAGE_NAME_AFFILIATION = "name_affiliation"


@dataclass(frozen=True)
class GroundTruth:
    """The generator's record of one synthetic document."""

    document_id: str
    seed_orcid_id: str
    linkage: str
    name_variant: str

    @property
    def record_id(self) -> str:
        """The bronze/silver ``record_id`` of the document."""
        return f"{SOURCE_CVN}:{self.document_id}"

    @property
    def true_entity_id(self) -> str:
        return entity_id_for_orcid(self.seed_orcid_id)


def load_manifest(path: Path | str) -> dict[str, GroundTruth]:
    """Read a synthetic run's ``manifest.jsonl`` into ground truth keyed by ``record_id``."""
    truth: dict[str, GroundTruth] = {}
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            entry = GroundTruth(
                document_id=row["document_id"],
                seed_orcid_id=row["seed_orcid_id"],
                linkage=row["linkage"],
                name_variant=row["name_variant"],
            )
            truth[entry.record_id] = entry
    return truth


def evaluate(
    links: Iterable[Mapping[str, Any]],
    truth: Mapping[str, GroundTruth],
    orcid_ids_in_silver: set[str],
    anchored_orcid_ids: set[str] | None = None,
) -> dict[str, Any]:
    """Compare the resolution of the CVN documents with the ground truth.

    Args:
        links: ``entity_link`` rows (``record_id``, ``source``, ``entity_id``,
            ``match_rule``, ``ambiguous``); rows of other sources are ignored.
        truth: The generator's manifest, keyed by ``record_id``.
        orcid_ids_in_silver: ORCID iDs that have a bulk or API record in silver.
        anchored_orcid_ids: ORCID iDs carried by any record in silver, ORCID or CVN
            (a document meant to be found by name can also be found through another
            CVN that declares its iD). Defaults to ``orcid_ids_in_silver``.

    Returns:
        A report with the counts of both rules, precision and recall of the
        name/affiliation rule, and its recall per name variant.
    """
    cvn_links = {link["record_id"]: link for link in links if link["source"] == SOURCE_CVN}
    in_silver = {record_id: entry for record_id, entry in truth.items() if record_id in cvn_links}

    by_declared_id = _declared_id_report(in_silver, cvn_links, orcid_ids_in_silver)
    by_name = _name_affiliation_report(in_silver, cvn_links, anchored_orcid_ids if anchored_orcid_ids is not None else orcid_ids_in_silver)
    return {
        "documents": {
            "in_manifest": len(truth),
            "in_silver": len(in_silver),
            "not_in_silver": len(truth) - len(in_silver),
        },
        "declared_orcid_id": by_declared_id,
        "name_affiliation": by_name,
    }


def _declared_id_report(
    in_silver: Mapping[str, GroundTruth], links: Mapping[str, Mapping[str, Any]], orcid_ids: set[str]
) -> dict[str, Any]:
    documents = {rid: entry for rid, entry in in_silver.items() if entry.linkage == LINKAGE_ORCID_ID}
    correct = sum(
        1
        for rid, entry in documents.items()
        if links[rid]["match_rule"] == RULE_ORCID_ID and links[rid]["entity_id"] == entry.true_entity_id
    )
    evaluable = [rid for rid, entry in documents.items() if entry.seed_orcid_id in orcid_ids]
    return {
        "documents": len(documents),
        "correct": correct,
        "incorrect": len(documents) - correct,
        "with_an_orcid_record_in_silver": len(evaluable),
        "fused_with_that_record": sum(1 for rid in evaluable if links[rid]["entity_id"] == documents[rid].true_entity_id),
    }


def _name_affiliation_report(
    in_silver: Mapping[str, GroundTruth], links: Mapping[str, Mapping[str, Any]], orcid_ids: set[str]
) -> dict[str, Any]:
    documents = {rid: entry for rid, entry in in_silver.items() if entry.linkage == LINKAGE_NAME_AFFILIATION}
    evaluable = {rid for rid, entry in documents.items() if entry.seed_orcid_id in orcid_ids}
    merged = {rid for rid in documents if links[rid]["match_rule"] == RULE_NAME_AFFILIATION}
    correct = {rid for rid in merged if links[rid]["entity_id"] == documents[rid].true_entity_id}
    wrong = merged - correct

    missed = evaluable - correct
    variant_totals = Counter(documents[rid].name_variant for rid in evaluable)
    variant_found = Counter(documents[rid].name_variant for rid in correct)
    return {
        "documents": len(documents),
        "evaluable": len(evaluable),
        "not_evaluable": len(documents) - len(evaluable),
        "merged": len(merged),
        "correct_merges": len(correct),
        "false_merges": len(wrong),
        "false_merges_of_documents_without_a_counterpart": len(wrong - evaluable),
        "false_merges_of_documents_merged_with_the_wrong_person": len(wrong & evaluable),
        "precision": len(correct) / len(merged) if merged else None,
        "recall": len(correct) / len(evaluable) if evaluable else None,
        "missed": {
            "total": len(missed),
            "ambiguous": sum(1 for rid in missed if links[rid]["ambiguous"]),
            "no_candidate": sum(1 for rid in missed if not links[rid]["ambiguous"] and rid not in wrong),
            "merged_with_the_wrong_person": len(missed & wrong),
        },
        "recall_by_name_variant": {
            variant: {"evaluable": total, "found": variant_found[variant]} for variant, total in sorted(variant_totals.items())
        },
    }


def format_report(report: Mapping[str, Any]) -> str:
    """Render an ``evaluate`` report as text for the run log and the memoria."""
    documents, declared, named = report["documents"], report["declared_orcid_id"], report["name_affiliation"]

    def percent(value: float | None) -> str:
        return "n/a" if value is None else f"{value:.1%}"

    lines = [
        f"documents: {documents['in_silver']} in silver of {documents['in_manifest']} in the manifest",
        f"rule orcid_id: {declared['correct']}/{declared['documents']} documents in their seed's entity; "
        f"{declared['fused_with_that_record']}/{declared['with_an_orcid_record_in_silver']} fused with an ORCID record",
        f"rule name_affiliation: {named['documents']} documents meant to be found by name, "
        f"{named['evaluable']} with their seed's record in silver",
        f"  merged {named['merged']}: {named['correct_merges']} correct, {named['false_merges']} false "
        f"({named['false_merges_of_documents_without_a_counterpart']} of documents without a counterpart)",
        f"  precision {percent(named['precision'])}, recall {percent(named['recall'])}; missed {named['missed']['total']} "
        f"(ambiguous {named['missed']['ambiguous']}, no candidate {named['missed']['no_candidate']}, "
        f"wrong person {named['missed']['merged_with_the_wrong_person']})",
    ]
    for variant, counts in named["recall_by_name_variant"].items():
        lines.append(f"  variant {variant}: {counts['found']}/{counts['evaluable']}")
    return "\n".join(lines)
