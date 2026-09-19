from __future__ import annotations

import hashlib
import logging
import tarfile
from collections import deque
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET

import requests

from tfm_lakehouse.orcid_bulk.exceptions import OrcidBulkChecksumError

logger = logging.getLogger(__name__)

# ORCID 2025 Public Data File, record-summaries tar.gz
# (DOI 10.6084/m9.figshare.30375589, file id 58834837, verified via the
# Figshare API). See docs/roadmap/tfm/issues/issue-95-orcid-bulk-data-file-pipeline.md
# for why this file (not the larger activities files) and this country
# filter were chosen.
DEFAULT_SOURCE_URL = "https://ndownloader.figshare.com/files/58834837"
DEFAULT_SOURCE_MD5 = "210edf71f4a2bb44dd33aaa3037b3f17"

# Matched entries are written from a thread pool so slow per-file writes on the
# Windows-mounted drive do not stall the single-threaded gunzip/tar read loop.
_WRITE_WORKERS = 8
_MAX_PENDING_WRITES = 1000

_COMMON_PREFIX = "common"
NS_COMMON = "http://www.orcid.org/ns/common"
NS_EMPLOYMENT = "http://www.orcid.org/ns/employment"
NS_EDUCATION = "http://www.orcid.org/ns/education"

# Path confirmed against a real downloaded entry (issue #95, Task 1):
# <employment:employment-summary>/<education:education-summary> ->
# common:organization -> common:address -> common:country.
_COUNTRY_PATH = f"{{{NS_COMMON}}}organization/{{{NS_COMMON}}}address/{{{NS_COMMON}}}country"
_SUMMARY_TAGS = (
    f"{{{NS_EMPLOYMENT}}}employment-summary",
    f"{{{NS_EDUCATION}}}education-summary",
)


@dataclass
class OrcidBulkSubsetResult:
    scanned: int
    matched: int
    output_dir: Path


class _HashingReader:
    """Wraps a file-like object, updating an md5 hash as bytes are read through it."""

    def __init__(self, fileobj, hasher) -> None:
        self._fileobj = fileobj
        self._hasher = hasher

    def read(self, size: int = -1) -> bytes:
        chunk = self._fileobj.read(size)
        if chunk:
            self._hasher.update(chunk)
        return chunk


def _has_matching_country(xml_bytes: bytes, countries: frozenset[str]) -> bool:
    # Cheap byte-level prefilter: XML parsing dominates runtime (~7x slower
    # than gunzip+tar alone, measured on the real file), and any record that
    # matches the affiliation path below must contain this exact country
    # element text somewhere. It over-matches (e.g. a person-level address)
    # but never under-matches; the parse below confirms the real path.
    if not any(f">{country}</{_COMMON_PREFIX}:country>".encode() in xml_bytes for country in countries):
        return False

    root = ET.fromstring(xml_bytes)
    for tag in _SUMMARY_TAGS:
        for summary in root.iter(tag):
            country = summary.find(_COUNTRY_PATH)
            if country is not None and country.text in countries:
                return True
    return False


def _write_entry(destination: Path, data: bytes) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)


def _walk_tar_and_filter(
    fileobj,
    output_dir: Path,
    countries: frozenset[str],
    progress_every: int,
    max_scanned: int | None,
) -> tuple[int, int]:
    scanned = 0
    matched = 0
    pending: deque[Future] = deque()
    with (
        ThreadPoolExecutor(max_workers=_WRITE_WORKERS) as writers,
        tarfile.open(fileobj=fileobj, mode="r|gz") as tf,
    ):
        for member in tf:
            # TarFile keeps every TarInfo it has seen in .members, which grows
            # to several GB over the ~25M entries of the real file (measured:
            # 4.7 GB RSS at 6.4M entries) and would exhaust memory.
            tf.members.clear()

            if not member.isfile():
                continue
            extracted = tf.extractfile(member)
            if extracted is None:
                continue
            data = extracted.read()
            scanned += 1

            if _has_matching_country(data, countries):
                matched += 1
                relative = Path(*Path(member.name).parts[1:])
                pending.append(writers.submit(_write_entry, output_dir / relative, data))
                if len(pending) > _MAX_PENDING_WRITES:
                    pending.popleft().result()

            if scanned % progress_every == 0:
                logger.info("scanned=%d matched=%d", scanned, matched)

            if max_scanned is not None and scanned >= max_scanned:
                break

        for future in pending:
            future.result()

    return scanned, matched


def _check_checksum(hasher, expected_md5: str | None, source: str) -> None:
    if expected_md5 is not None and hasher.hexdigest() != expected_md5:
        raise OrcidBulkChecksumError(
            f"expected md5 {expected_md5}, got {hasher.hexdigest()} for {source}"
        )


def fetch_orcid_bulk_subset(
    output_dir: Path,
    countries: frozenset[str] = frozenset({"ES"}),
    source_url: str = DEFAULT_SOURCE_URL,
    expected_md5: str | None = DEFAULT_SOURCE_MD5,
    progress_every: int = 50_000,
    max_scanned: int | None = None,
) -> OrcidBulkSubsetResult:
    """Stream, filter, and store a country-affiliated subset of the ORCID
    Public Data File record-summaries.

    Reads the remote tar.gz in one sequential pass -- there is no random
    access into a remote gzip stream -- and writes matching entries under
    output_dir, preserving the source's own <checksum-bucket>/<iD>.xml
    layout so issue #97's bronze landing can consume it directly.

    max_scanned stops the pass early after that many entries; it exists for
    smoke-testing against the real file without pulling all 46.3 GB, not for
    the real subset run. See issue #95, Task 5's decision for why the real
    run must not use an early-stop cap (it would bias the sample toward
    whatever part of the iD keyspace is scanned first). Checksum
    verification is skipped whenever max_scanned is set, since a partial
    read can never match the full file's MD5.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    verify_checksum = expected_md5 is not None and max_scanned is None

    response = requests.get(source_url, stream=True, timeout=30)
    response.raise_for_status()

    hasher = hashlib.md5()
    stream = _HashingReader(response.raw, hasher)

    try:
        scanned, matched = _walk_tar_and_filter(
            stream, output_dir, countries, progress_every, max_scanned
        )
    finally:
        response.close()

    if verify_checksum:
        _check_checksum(hasher, expected_md5, source_url)

    return OrcidBulkSubsetResult(scanned=scanned, matched=matched, output_dir=output_dir)


def fetch_orcid_bulk_subset_from_local_file(
    archive_path: Path,
    output_dir: Path,
    countries: frozenset[str] = frozenset({"ES"}),
    expected_md5: str | None = DEFAULT_SOURCE_MD5,
    progress_every: int = 50_000,
    max_scanned: int | None = None,
) -> OrcidBulkSubsetResult:
    """Same filter/store behavior as fetch_orcid_bulk_subset, but reading the
    ORCID Public Data File summaries tar.gz from a local path instead of
    downloading it. For a manual/faster-connection download placed at
    archive_path ahead of time; see issue #95's Task 5 notes for why.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    verify_checksum = expected_md5 is not None and max_scanned is None

    hasher = hashlib.md5()
    with archive_path.open("rb") as raw_file:
        stream = _HashingReader(raw_file, hasher)
        scanned, matched = _walk_tar_and_filter(
            stream, output_dir, countries, progress_every, max_scanned
        )

    if verify_checksum:
        _check_checksum(hasher, expected_md5, str(archive_path))

    return OrcidBulkSubsetResult(scanned=scanned, matched=matched, output_dir=output_dir)
