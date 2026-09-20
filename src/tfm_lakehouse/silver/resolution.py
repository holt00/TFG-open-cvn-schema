"""Deterministic entity resolution rules (issue #98, D7, D8).

Pure functions and an in-memory reference resolver. The Spark job
(``resolution_spark.py``) runs the same rules as DataFrame joins; this module
is its oracle in the tests and the single definition of the comparisons both
use (``names_compatible``, ``best_org_similarity``).

Rules, in order:

* **R1 ``orcid_id``**: records carrying the same valid ORCID iD (a CVN that
  declares it, a bulk record, an API record) are one entity, ``orcid:<iD>``.
* **R2 ``name_affiliation``**: a record with no iD joins an R1 entity when a
  record of that entity has the same block key (family key and given initial),
  a compatible name (at most one of given and family name relaxed), and the entity
  shares an organization with it, and **exactly one** entity qualifies. The link's
  evidence records the kind of name match and the number of shared organizations,
  so a consumer can demand more than the rule does. With several the record stays alone and is flagged
  ``ambiguous``: a wrong merge corrupts every downstream indicator, a missed one
  only splits an entity.
* **R3 ``singleton``**: everything else is its own entity, ``rec:<sha1>``.

An R1 merge whose names disagree is kept (the iD is authoritative) and flagged
``name_conflict``.

No probabilistic scoring: the epic excludes it.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from tfm_lakehouse.silver.normalize import token_jaccard

RULE_ORCID_ID = "orcid_id"
RULE_NAME_AFFILIATION = "name_affiliation"
RULE_SINGLETON = "singleton"

SOURCE_CVN = "synthetic_cvn"
# Which record names an entity, best first: the API is the freshest ORCID source.
_DISPLAY_PRIORITY = {"orcid_api": 0, "orcid_bulk": 1, SOURCE_CVN: 2}
_MAX_LISTED_CANDIDATES = 5

# 1.0 means the normalized organization names must be equal. Measured on real
# names (issue #98, Task 4): a campus suffix of the same institution scores 0.60
# and 0.40, while two different institutions ("Universitat de València" and
# "Universitat Politècnica de València") score 0.67, so no lower threshold
# separates them; it stays a parameter for the Task 8 sensitivity run only.
DEFAULT_ORG_THRESHOLD = 1.0


def entity_id_for_orcid(orcid_id: str) -> str:
    """Return the id of the entity anchored at an ORCID iD."""
    return f"orcid:{orcid_id}"


def entity_id_for_record(record_id: str) -> str:
    """Return the id of the singleton entity of a record (deterministic)."""
    return f"rec:{hashlib.sha1(record_id.encode('utf-8')).hexdigest()}"


NAME_FULL = "full"
NAME_GIVEN_VARIANT = "given_variant"
NAME_SURNAME_PREFIX = "surname_prefix"


def name_match_kind(given_a: str, family_a: str, given_b: str, family_b: str) -> str | None:
    """Classify how two normalized names match, or return None when they cannot be one person's.

    Inputs come from ``normalize.normalize_person_name`` (folded, space-separated).
    Given names may be equal, equal except that some are initials of the other's
    (``ana m`` and ``ana maria``), or one side may be initials only (``j``, ``j a``)
    matching the other's initials. Family names may be equal or one may be a
    leading part of the other (people who drop their second surname).

    **At most one of the two may be relaxed.** A name that differs in both the
    given and the family name is rejected: measured on the synthetic ground truth
    (issue #98, Task 8.5), 8 of 8 such merges (``I. García`` and ``Irene García
    Meilán``, both at one shared organization) joined different people, and
    forbidding them costs no correct merge.

    Args:
        given_a: Folded given names of the first person.
        family_a: Folded family name of the first person.
        given_b: Folded given names of the second person.
        family_b: Folded family name of the second person.

    Returns:
        ``"full"`` (identical), ``"given_variant"`` (family equal, given relaxed),
        ``"surname_prefix"`` (given equal, family a leading part), or None.
    """
    family_tokens_a, family_tokens_b = family_a.split(), family_b.split()
    given_tokens_a, given_tokens_b = given_a.split(), given_b.split()
    if not family_tokens_a or not family_tokens_b or not given_tokens_a or not given_tokens_b:
        return None

    short, long = sorted((family_tokens_a, family_tokens_b), key=len)
    if long[: len(short)] != short:
        return None
    family_equal = family_tokens_a == family_tokens_b

    given_equal = given_tokens_a == given_tokens_b
    if not given_equal and not (
        _tokens_compatible(given_tokens_a, given_tokens_b)
        or _initials_match(given_tokens_a, given_tokens_b)
        or _initials_match(given_tokens_b, given_tokens_a)
    ):
        return None

    if family_equal and given_equal:
        return NAME_FULL
    if family_equal:
        return NAME_GIVEN_VARIANT
    if given_equal:
        return NAME_SURNAME_PREFIX
    return None


def names_compatible(given_a: str, family_a: str, given_b: str, family_b: str) -> bool:
    """Say whether two normalized names can be the same person's (see ``name_match_kind``)."""
    return name_match_kind(given_a, family_a, given_b, family_b) is not None


def _tokens_compatible(tokens_a: Sequence[str], tokens_b: Sequence[str]) -> bool:
    """Same number of given names, each pair equal or one the initial of the other.

    Covers "ana m" against "ana maria": a person who later spells out an initial
    (found in the real data, issue #98, Task 5). It does not cover a dropped
    given name ("ana" against "ana maria").
    """
    return len(tokens_a) == len(tokens_b) and all(
        a == b or (len(a) == 1 and b.startswith(a)) or (len(b) == 1 and a.startswith(b)) for a, b in zip(tokens_a, tokens_b)
    )


def _initials_match(initials: Sequence[str], full: Sequence[str]) -> bool:
    return (
        all(len(token) == 1 for token in initials)
        and len(full) >= len(initials)
        and [token[0] for token in full[: len(initials)]] == list(initials)
    )


def best_org_similarity(organizations_a: Iterable[str], organizations_b: Iterable[str]) -> float:
    """Return the best Jaccard similarity between any pair of organizations.

    Args:
        organizations_a: ``organization_norm`` values (sorted tokens joined by a space).
        organizations_b: The same, for the other side.

    Returns:
        1.0 for equal names, 0.0 when either side is empty.
    """
    tokens_b = [frozenset(name.split()) for name in organizations_b]
    best = 0.0
    for name in organizations_a:
        tokens_a = frozenset(name.split())
        for other in tokens_b:
            best = max(best, token_jaccard(tokens_a, other))
    return best


@dataclass
class Link:
    """One record's assignment to an entity (a row of ``silver.entity_link``)."""

    record_id: str
    source: str
    entity_id: str
    match_rule: str
    evidence: dict[str, Any] = field(default_factory=dict)
    ambiguous: bool = False
    name_conflict: bool = False

    def evidence_json(self) -> str:
        return json.dumps(self.evidence, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def resolve_in_memory(
    persons: Sequence[Mapping[str, Any]],
    affiliations: Sequence[Mapping[str, Any]],
    org_threshold: float = DEFAULT_ORG_THRESHOLD,
) -> list[Link]:
    """Resolve every person record to an entity, in memory.

    Args:
        persons: ``person_record`` rows (at least ``record_id``, ``source``,
            ``orcid_id``, ``given_norm``, ``family_norm``, ``family_key``,
            ``given_initial``).
        affiliations: ``affiliation`` rows (``record_id``, ``organization_norm``).
        org_threshold: Minimum organization similarity for R2.

    Returns:
        One link per person, in the order of ``persons``.
    """
    organizations: dict[str, set[str]] = {}
    for row in affiliations:
        if row["organization_norm"]:
            organizations.setdefault(row["record_id"], set()).add(row["organization_norm"])

    anchored: dict[str, list[Mapping[str, Any]]] = {}
    for person in persons:
        if person["orcid_id"]:
            anchored.setdefault(entity_id_for_orcid(person["orcid_id"]), []).append(person)
    entity_organizations = {
        entity_id: set().union(*(organizations.get(member["record_id"], set()) for member in members))
        for entity_id, members in anchored.items()
    }
    blocks: dict[tuple[str, str], list[Mapping[str, Any]]] = {}
    for entity_id, members in anchored.items():
        for member in members:
            blocks.setdefault((member["family_key"], member["given_initial"]), []).append(member)

    links: list[Link] = []
    for person in persons:
        if person["orcid_id"]:
            entity_id = entity_id_for_orcid(person["orcid_id"])
            links.append(
                Link(
                    record_id=person["record_id"],
                    source=person["source"],
                    entity_id=entity_id,
                    match_rule=RULE_ORCID_ID,
                    evidence={"orcid_id": person["orcid_id"]},
                    name_conflict=_has_name_conflict(person, anchored[entity_id]),
                )
            )
            continue
        links.append(_resolve_without_id(person, blocks, entity_organizations, organizations, org_threshold))
    return links


def _has_name_conflict(person: Mapping[str, Any], members: Sequence[Mapping[str, Any]]) -> bool:
    """A CVN whose name matches none of the ORCID records sharing its iD."""
    if person["source"] != SOURCE_CVN:
        return False
    orcid_members = [member for member in members if member["source"] != SOURCE_CVN]
    return bool(orcid_members) and not any(
        names_compatible(person["given_norm"], person["family_norm"], member["given_norm"], member["family_norm"])
        for member in orcid_members
    )


def _resolve_without_id(
    person: Mapping[str, Any],
    blocks: Mapping[tuple[str, str], Sequence[Mapping[str, Any]]],
    entity_organizations: Mapping[str, set[str]],
    organizations: Mapping[str, set[str]],
    org_threshold: float,
) -> Link:
    own_organizations = organizations.get(person["record_id"], set())
    matched_member: dict[str, tuple[Mapping[str, Any], str]] = {}
    for member in sorted(blocks.get((person["family_key"], person["given_initial"]), ()), key=lambda item: item["record_id"]):
        entity_id = entity_id_for_orcid(member["orcid_id"])
        if entity_id in matched_member:
            continue
        kind = name_match_kind(person["given_norm"], person["family_norm"], member["given_norm"], member["family_norm"])
        if kind is not None:
            matched_member[entity_id] = (member, kind)

    candidates: dict[str, tuple[Mapping[str, Any], str, float]] = {}
    for entity_id, (member, kind) in matched_member.items():
        similarity = best_org_similarity(own_organizations, entity_organizations[entity_id])
        if similarity > 0.0 and similarity >= org_threshold:
            candidates[entity_id] = (member, kind, similarity)

    singleton = entity_id_for_record(person["record_id"])
    if len(candidates) == 1:
        entity_id, (member, kind, similarity) = next(iter(candidates.items()))
        return Link(
            record_id=person["record_id"],
            source=person["source"],
            entity_id=entity_id,
            match_rule=RULE_NAME_AFFILIATION,
            evidence={
                "candidates": 1,
                "matched_record_id": member["record_id"],
                "name_match": kind,
                "org_similarity": round(similarity, 4),
                "shared_organizations": len(own_organizations & entity_organizations[entity_id]),
            },
        )
    return Link(
        record_id=person["record_id"],
        source=person["source"],
        entity_id=singleton,
        match_rule=RULE_SINGLETON,
        evidence={"candidates": sorted(candidates)[:_MAX_LISTED_CANDIDATES]} if candidates else {},
        ambiguous=len(candidates) > 1,
    )


def build_entities(persons: Sequence[Mapping[str, Any]], links: Sequence[Link]) -> list[dict[str, Any]]:
    """Aggregate links into ``silver.entity`` rows, ordered by ``entity_id``.

    The display name is the best record's: ORCID API first, then bulk, then CVN,
    then the most recently modified, then the smallest ``record_id``.
    """
    person_by_id = {person["record_id"]: person for person in persons}
    members: dict[str, list[Link]] = {}
    for link in links:
        members.setdefault(link.entity_id, []).append(link)

    rows: list[dict[str, Any]] = []
    for entity_id in sorted(members):
        entity_links = members[entity_id]
        best = min(
            (person_by_id[link.record_id] for link in entity_links),
            key=lambda person: (
                _DISPLAY_PRIORITY.get(person["source"], len(_DISPLAY_PRIORITY)),
                _descending(person.get("source_last_modified")),
                person["record_id"],
            ),
        )
        sources = sorted({link.source for link in entity_links})
        rows.append(
            {
                "entity_id": entity_id,
                "orcid_id": entity_id[len("orcid:") :] if entity_id.startswith("orcid:") else None,
                "given_names": best["given_names"],
                "family_name": best["family_name"],
                "record_count": len(entity_links),
                "sources": sources,
                "rules": sorted({link.match_rule for link in entity_links}),
                "has_cvn": SOURCE_CVN in sources,
                "has_orcid": any(source != SOURCE_CVN for source in sources),
            }
        )
    return rows


def _descending(timestamp: str | None) -> tuple[int, ...]:
    """Sort key placing later ISO timestamps first and missing ones last."""
    if not timestamp:
        return (1,)
    return (0, *(-ord(char) for char in timestamp))
