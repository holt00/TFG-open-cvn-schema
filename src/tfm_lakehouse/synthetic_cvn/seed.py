from __future__ import annotations

import logging
import os
import random
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET

from tfm_lakehouse.orcid_client.client import validate_orcid_id
from tfm_lakehouse.orcid_client.exceptions import OrcidValidationError
from tfm_lakehouse.synthetic_cvn.exceptions import SyntheticCvnSeedError

logger = logging.getLogger(__name__)

_NS = {
    "common": "http://www.orcid.org/ns/common",
    "personal": "http://www.orcid.org/ns/personal-details",
    "person": "http://www.orcid.org/ns/person",
    "employment": "http://www.orcid.org/ns/employment",
    "education": "http://www.orcid.org/ns/education",
    "work": "http://www.orcid.org/ns/work",
    "keyword": "http://www.orcid.org/ns/keyword",
}

# Consecutive already-used draws after which the pool is treated as exhausted
# and drawing restarts with a higher reuse round.
_EXHAUSTION_MISSES = 2_000


@dataclass(frozen=True)
class OrcidWork:
    title: str
    work_type: str | None
    year: str | None
    month: str | None
    doi: str | None


@dataclass(frozen=True)
class OrcidAffiliation:
    kind: str
    organization: str
    city: str | None
    country: str | None
    role_title: str | None
    department: str | None
    start_year: str | None
    start_month: str | None
    end_year: str | None
    end_month: str | None


@dataclass(frozen=True)
class OrcidSeed:
    """The public ORCID fields one synthetic curriculum is seeded with.

    Biography, emails and researcher URLs are deliberately not read (see
    issue #96, Decision 9).
    """

    orcid_id: str
    given_names: str
    family_name: str
    affiliations: tuple[OrcidAffiliation, ...]
    works: tuple[OrcidWork, ...]
    keywords: tuple[str, ...]


@dataclass(frozen=True)
class SeedDraw:
    path: Path
    reuse_round: int


def parse_orcid_summary(source: Path | bytes) -> OrcidSeed | None:
    """Parse one ORCID record-summary XML into an `OrcidSeed`.

    Args:
        source: A path to, or the raw bytes of, a record-summary XML entry.

    Returns:
        The seed, or None when the record is unusable: malformed XML, missing
        or invalid ORCID iD, or a missing given or family name (both are
        required fields of a CVN identity).
    """
    try:
        root = ET.fromstring(source.read_bytes() if isinstance(source, Path) else source)
    except (ET.ParseError, OSError):
        return None

    orcid_id = _text(root.find("common:orcid-identifier/common:path", _NS))
    given_names = _text(root.find(".//personal:given-names", _NS))
    family_name = _text(root.find(".//personal:family-name", _NS))
    if orcid_id is None or given_names is None or family_name is None:
        return None
    try:
        validate_orcid_id(orcid_id)
    except OrcidValidationError:
        return None

    affiliations = (
        *_parse_affiliations(root, "employment", "employment:employment-summary"),
        *_parse_affiliations(root, "education", "education:education-summary"),
    )
    return OrcidSeed(
        orcid_id=orcid_id,
        given_names=given_names,
        family_name=family_name,
        affiliations=affiliations,
        works=_parse_works(root),
        keywords=tuple(
            text
            for element in root.findall(".//keyword:keyword/keyword:content", _NS)
            if (text := _text(element)) is not None
        ),
    )


def _parse_affiliations(root: ET.Element, kind: str, path: str) -> Iterator[OrcidAffiliation]:
    for summary in root.iterfind(f".//{path}", _NS):
        organization = _text(summary.find("common:organization/common:name", _NS))
        if organization is None:
            continue
        yield OrcidAffiliation(
            kind=kind,
            organization=organization,
            city=_text(summary.find("common:organization/common:address/common:city", _NS)),
            country=_text(summary.find("common:organization/common:address/common:country", _NS)),
            role_title=_text(summary.find("common:role-title", _NS)),
            department=_text(summary.find("common:department-name", _NS)),
            start_year=_text(summary.find("common:start-date/common:year", _NS)),
            start_month=_text(summary.find("common:start-date/common:month", _NS)),
            end_year=_text(summary.find("common:end-date/common:year", _NS)),
            end_month=_text(summary.find("common:end-date/common:month", _NS)),
        )


def _parse_works(root: ET.Element) -> tuple[OrcidWork, ...]:
    works: list[OrcidWork] = []
    for summary in root.iterfind(".//work:work-summary", _NS):
        title = _text(summary.find("work:title/common:title", _NS))
        if title is None:
            continue
        doi = None
        for external_id in summary.iterfind("common:external-ids/common:external-id", _NS):
            if _text(external_id.find("common:external-id-type", _NS)) == "doi":
                doi = _text(external_id.find("common:external-id-value", _NS))
                break
        works.append(
            OrcidWork(
                title=title,
                work_type=_text(summary.find("work:type", _NS)),
                year=_text(summary.find("common:publication-date/common:year", _NS)),
                month=_text(summary.find("common:publication-date/common:month", _NS)),
                doi=doi,
            )
        )
    return tuple(works)


def _text(element: ET.Element | None) -> str | None:
    if element is None or element.text is None:
        return None
    stripped = " ".join(element.text.split())
    return stripped or None


class OrcidSeedPool:
    """Deterministic random access to the issue #95 ORCID subset on disk.

    The subset holds ~300k files, so listing all of them up front would be
    slow on the Windows-mounted drive. Buckets (``<3-digit>`` directories) are
    listed lazily, and a draw is a random bucket followed by a random file in
    it. Buckets are filled by the last digits of the ORCID iD, so they are
    close to equal in size and the draw is close to uniform.
    """

    def __init__(self, root: Path) -> None:
        if not root.is_dir():
            raise SyntheticCvnSeedError(f"ORCID seed directory does not exist: {root}")
        self._root = root
        self._buckets = sorted(entry.name for entry in os.scandir(root) if entry.is_dir())
        if not self._buckets:
            raise SyntheticCvnSeedError(f"ORCID seed directory has no bucket subdirectories: {root}")
        self._files_by_bucket: dict[str, list[str]] = {}

    def iter_draws(self, rng: random.Random) -> Iterator[SeedDraw]:
        """Yield seed file paths forever: distinct ones until the pool runs out.

        Once nearly every file has been drawn, drawing restarts and
        ``reuse_round`` is incremented, so callers know a seed is being reused
        and must vary it.
        """
        used: set[Path] = set()
        reuse_round = 0
        misses = 0
        while True:
            bucket = rng.choice(self._buckets)
            files = self._files(bucket)
            if not files:
                misses += 1
                if misses > _EXHAUSTION_MISSES:
                    raise SyntheticCvnSeedError(f"ORCID seed directory has no XML files: {self._root}")
                continue
            path = self._root / bucket / rng.choice(files)
            if path in used:
                misses += 1
                if misses > _EXHAUSTION_MISSES:
                    used.clear()
                    reuse_round += 1
                    misses = 0
                continue
            misses = 0
            used.add(path)
            yield SeedDraw(path=path, reuse_round=reuse_round)

    def _files(self, bucket: str) -> list[str]:
        files = self._files_by_bucket.get(bucket)
        if files is None:
            files = sorted(name for name in os.listdir(self._root / bucket) if name.endswith(".xml"))
            self._files_by_bucket[bucket] = files
        return files
