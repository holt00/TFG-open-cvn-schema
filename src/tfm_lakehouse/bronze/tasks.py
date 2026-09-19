"""Entry points of the ``ingest_validate`` DAG tasks (issue #97).

Each function does one DAG task and returns a small JSON-serializable summary;
``main`` exposes them as ``python -m tfm_lakehouse.bronze.tasks <command>``,
which is what the DAG's pods run. Tasks hand data to each other through the
shared ``data/`` directory (``data/bronze_runs/<run_id>/``), not through XCom.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import random
import sys
import time
from collections import deque
from collections.abc import Callable, Iterator
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests

from tfm_lakehouse.bronze.checks import check_cvn_document, check_orcid_api_record, check_orcid_summary_xml
from tfm_lakehouse.bronze.envelope import (
    PAYLOAD_FORMAT_JSON,
    PAYLOAD_FORMAT_XML,
    SOURCE_ORCID_API,
    SOURCE_ORCID_BULK,
    SOURCE_SYNTHETIC_CVN,
    RunContext,
    build_envelope,
    utc_timestamp,
)
from tfm_lakehouse.bronze.exceptions import BronzeLandingError, BronzeSourceNotReadyError
from tfm_lakehouse.bronze.landing import (
    DEFAULT_BUCKET,
    DEFAULT_REJECTION_THRESHOLD,
    S3Client,
    create_s3_client,
    find_landed_runs,
    land_records,
)
from tfm_lakehouse.orcid_bulk import fetch_orcid_bulk_subset_from_local_file
from tfm_lakehouse.orcid_bulk.pipeline import DEFAULT_SOURCE_MD5
from tfm_lakehouse.orcid_client import OrcidApiError, OrcidClient, OrcidNotFoundError
from tfm_lakehouse.synthetic_cvn import SyntheticCvnConfig, generate_synthetic_cvn

logger = logging.getLogger(__name__)

DEFAULT_DATA_DIR = Path(os.environ.get("TFM_DATA_DIR", "/repo/data"))
ORCID_ARCHIVE_NAME = "ORCID_2025_10_summaries.tar.gz"
ORCID_BULK_SNAPSHOT = "ORCID_2025_10_summaries|country=ES"
# Matches recorded by issue #95 on the real archive. A subset directory with a
# different file count is treated as partial and never adopted.
ISSUE_95_EXPECTED_MATCHES = 301_763
DEFAULT_BULK_MAX_RECORDS = 20_000
DEFAULT_ENRICHMENT_SAMPLE_SIZE = 200
# The anonymous ORCID API tier allows 12 requests/s; stay under it.
API_MIN_INTERVAL_SECONDS = 0.1
API_MAX_TOLERATED_FAILURE_SHARE = 0.5
_READ_WORKERS = 16
_PREFETCH_WINDOW = 128


def _now_iso() -> str:
    return utc_timestamp(datetime.now(UTC))


def _paths(data_dir: Path, run: RunContext | None = None) -> dict[str, Path]:
    bulk = data_dir / "orcid_bulk"
    paths = {
        "subset_dir": bulk / "filtered",
        "subset_marker": bulk / "_subset_complete.json",
        "archive": bulk / "raw" / ORCID_ARCHIVE_NAME,
    }
    if run is not None:
        run_dir = data_dir / "bronze_runs" / run.run_id
        paths |= {
            "run_dir": run_dir,
            "synthetic_dir": run_dir / "synthetic_cvn",
            "api_file": run_dir / "orcid_api" / "records.jsonl",
        }
    return paths


def _write_summary(run: RunContext, data_dir: Path, name: str, summary: dict[str, Any]) -> dict[str, Any]:
    run_dir = _paths(data_dir, run)["run_dir"]
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / f"{name}.summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    logger.info(f"TASK_SUMMARY {json.dumps({'task': name, **summary})}")
    return summary


def _read_summary(run: RunContext, data_dir: Path, name: str) -> dict[str, Any]:
    path = _paths(data_dir, run)["run_dir"] / f"{name}.summary.json"
    if not path.is_file():
        raise BronzeSourceNotReadyError(f"{path} is missing: the {name} task has not run for run {run.run_id}")
    return json.loads(path.read_text(encoding="utf-8"))


def _count_subset_files(subset_dir: Path) -> int:
    total = 0
    with os.scandir(subset_dir) as buckets:
        for bucket in buckets:
            if bucket.is_dir():
                with os.scandir(bucket.path) as entries:
                    total += sum(1 for entry in entries if entry.name.endswith(".xml"))
    return total


def _archive_metadata(archive: Path) -> dict[str, Any]:
    retrieved_at = utc_timestamp(datetime.fromtimestamp(archive.stat().st_mtime, UTC)) if archive.is_file() else _now_iso()
    return {"name": ORCID_ARCHIVE_NAME, "md5": DEFAULT_SOURCE_MD5, "retrieved_at": retrieved_at}


def ensure_orcid_subset(data_dir: Path = DEFAULT_DATA_DIR, *, force_refetch: bool = False) -> dict[str, Any]:
    """Make sure the issue #95 ORCID subset exists and is known to be complete.

    ``fetch_orcid_bulk_subset*`` writes no completion marker, and an interrupted
    run leaves a partial directory that looks finished, so this task keeps its
    own marker (``data/orcid_bulk/_subset_complete.json``, outside ``filtered/``
    because the seed pool lists that directory). With a marker, the 81-minute
    extraction is skipped. Without one, an existing directory is adopted only
    when its file count equals the matches issue #95 recorded; otherwise the
    extraction runs from the local archive. The archive is never downloaded.

    Args:
        data_dir: Repository ``data/`` directory.
        force_refetch: Ignore the marker and extract again.

    Returns:
        A summary with the action taken (``skipped``, ``adopted`` or
        ``extracted``) and the marker's contents.

    Raises:
        BronzeSourceNotReadyError: When there is no complete subset and no
            archive to extract one from.
    """
    paths = _paths(data_dir)
    marker_path, subset_dir, archive = paths["subset_marker"], paths["subset_dir"], paths["archive"]

    if marker_path.is_file() and not force_refetch:
        return {"action": "skipped", **json.loads(marker_path.read_text(encoding="utf-8"))}
    marker_path.unlink(missing_ok=True)

    if subset_dir.is_dir() and not force_refetch:
        matched = _count_subset_files(subset_dir)
        if matched == ISSUE_95_EXPECTED_MATCHES:
            action, scanned = "adopted", None
        elif matched > 0 and not archive.is_file():
            raise BronzeSourceNotReadyError(
                f"{subset_dir} holds {matched} files, not the {ISSUE_95_EXPECTED_MATCHES} issue #95 recorded, "
                f"and there is no archive at {archive} to rebuild it from"
            )
        else:
            action, scanned = None, None
        if action:
            return _write_marker(marker_path, action, matched, scanned, _archive_metadata(archive))

    if not archive.is_file():
        raise BronzeSourceNotReadyError(f"no ORCID subset marker and no archive at {archive}; download it first (issue #95)")
    logger.info(f"extracting the ORCID subset from {archive}; issue #95 measured about 81 minutes")
    result = fetch_orcid_bulk_subset_from_local_file(archive, subset_dir)
    return _write_marker(marker_path, "extracted", result.matched, result.scanned, _archive_metadata(archive))


def _write_marker(path: Path, action: str, matched: int, scanned: int | None, archive: dict[str, Any]) -> dict[str, Any]:
    marker = {
        "source_snapshot": ORCID_BULK_SNAPSHOT,
        "matched": matched,
        "scanned": scanned,
        "archive": {"name": archive["name"], "md5": archive["md5"]},
        "retrieved_at": archive["retrieved_at"],
        "marked_at": _now_iso(),
        "how": action,
    }
    path.write_text(json.dumps(marker, indent=2), encoding="utf-8")
    return {"action": action, **marker}


def run_synthetic_cvn(
    run: RunContext,
    data_dir: Path = DEFAULT_DATA_DIR,
    *,
    count: int,
    seed: int,
    orcid_link_ratio: float,
) -> dict[str, Any]:
    """Generate the run's synthetic CVN documents from the ORCID subset (issue #96)."""
    paths = _paths(data_dir, run)
    if not paths["subset_marker"].is_file():
        raise BronzeSourceNotReadyError("the ORCID subset is not marked complete; run the orcid-bulk-subset task first")
    result = generate_synthetic_cvn(
        SyntheticCvnConfig(
            count=count,
            seed=seed,
            orcid_seed_dir=paths["subset_dir"],
            output_dir=paths["synthetic_dir"],
            orcid_link_ratio=orcid_link_ratio,
            overwrite=True,
        )
    )
    summary = {
        "generated_at": _now_iso(),
        "seed": seed,
        "requested": result.requested,
        "generated": result.generated,
        "linked": result.linked,
        "unlinked": result.unlinked,
        "invalid_discarded": result.invalid_discarded,
        "shards_written": result.shards_written,
    }
    return _write_summary(run, data_dir, "synthetic_cvn", summary)


def _sample_linked_orcid_ids(manifest_path: Path, sample_size: int, seed: int) -> list[str]:
    linked: set[str] = set()
    with manifest_path.open(encoding="utf-8") as manifest:
        for line in manifest:
            entry = json.loads(line)
            if entry["linkage"] == "orcid_id":
                linked.add(entry["seed_orcid_id"])
    ordered = sorted(linked)
    return random.Random(seed).sample(ordered, min(sample_size, len(ordered)))


def run_orcid_api_enrichment(
    run: RunContext,
    data_dir: Path = DEFAULT_DATA_DIR,
    *,
    sample_size: int,
    seed: int,
    client: OrcidClient | None = None,
    sleep: Callable[[float], None] = time.sleep,
) -> dict[str, Any]:
    """Fetch the current ORCID record of a sample of the synthetic CVNs' ORCID iDs (issue #94).

    Looks up iDs that the run's synthetic CVNs declare, the cross-source case
    the epic describes: the API answers with the record as of today, which can
    differ from the 2025 bulk snapshot. Requests are paced under the anonymous
    tier's 12 requests/s. A 404 (deleted or deprecated iD), a persistent API
    error, or a network failure is recorded and skipped; the task fails only when more than half of
    the iDs could not be fetched.

    Args:
        run: The landing run.
        data_dir: Repository ``data/`` directory.
        sample_size: Maximum number of iDs to look up.
        seed: Seed of the deterministic sample.
        client: ORCID client; a default anonymous one when omitted.
        sleep: Sleep function, injectable for tests.

    Returns:
        A summary with counts per outcome.

    Raises:
        BronzeSourceNotReadyError: When the synthetic CVN task has not run.
        BronzeLandingError: When most lookups failed.
    """
    paths = _paths(data_dir, run)
    manifest_path = paths["synthetic_dir"] / "manifest.jsonl"
    if not manifest_path.is_file():
        raise BronzeSourceNotReadyError(f"{manifest_path} is missing: run the synthetic-cvn task first")
    orcid_ids = _sample_linked_orcid_ids(manifest_path, sample_size, seed)
    client = client or OrcidClient()

    paths["api_file"].parent.mkdir(parents=True, exist_ok=True)
    counts = {"ok": 0, "not_found": 0, "error": 0}
    with paths["api_file"].open("w", encoding="utf-8", newline="\n") as output:
        for index, orcid_id in enumerate(orcid_ids):
            if index:
                sleep(API_MIN_INTERVAL_SECONDS)
            line: dict[str, Any] = {"orcid_id": orcid_id, "retrieved_at": _now_iso(), "status": "ok", "record": None}
            try:
                line["record"] = client.get_record(orcid_id)
            except OrcidNotFoundError:
                line["status"] = "not_found"
            except (OrcidApiError, requests.RequestException) as exc:
                # The client wraps HTTP errors but not network ones (timeouts,
                # resets); a transient failure of one iD must not lose the rest.
                line["status"] = "error"
                line["error"] = str(exc)
            counts[line["status"]] += 1
            output.write(json.dumps(line, ensure_ascii=False, separators=(",", ":")) + "\n")

    summary = {"requested": len(orcid_ids), "seed": seed, **counts}
    _write_summary(run, data_dir, "orcid_api", summary)
    failed = counts["not_found"] + counts["error"]
    if orcid_ids and (counts["ok"] == 0 or failed / len(orcid_ids) > API_MAX_TOLERATED_FAILURE_SHARE):
        raise BronzeLandingError(f"only {counts['ok']} of {len(orcid_ids)} ORCID lookups succeeded: {counts}")
    return summary


def _iter_synthetic_envelopes(run: RunContext, synthetic_dir: Path, generated_at: str) -> Iterator[dict[str, Any]]:
    for shard in sorted(synthetic_dir.glob("cvn_shard_*.jsonl")):
        with shard.open(encoding="utf-8") as lines:
            for line in lines:
                document = json.loads(line)
                identity = document.get("curriculum", {}).get("identity", {})
                source_ref = str(identity.get("identificador_unico_de_cv", "unknown"))
                source = document.get("metadata", {}).get("source", {})
                yield build_envelope(
                    source=SOURCE_SYNTHETIC_CVN,
                    source_ref=source_ref,
                    payload=document,
                    payload_format=PAYLOAD_FORMAT_JSON,
                    run=run,
                    retrieved_at=generated_at,
                    source_snapshot=f"{source.get('orcid_snapshot', 'unknown')}|generator_seed={source.get('generator_seed')}",
                    check=check_cvn_document(document, source_identifier=source_ref),
                    source_files=(shard.name,),
                )


def _iter_api_envelopes(run: RunContext, api_file: Path) -> Iterator[dict[str, Any]]:
    with api_file.open(encoding="utf-8") as lines:
        for line in lines:
            entry = json.loads(line)
            if entry["status"] != "ok":
                continue
            yield build_envelope(
                source=SOURCE_ORCID_API,
                source_ref=entry["orcid_id"],
                payload=entry["record"],
                payload_format=PAYLOAD_FORMAT_JSON,
                run=run,
                retrieved_at=entry["retrieved_at"],
                source_snapshot="orcid_public_api_v3.0",
                check=check_orcid_api_record(entry["record"], entry["orcid_id"]),
                source_files=(f"pub.orcid.org/v3.0/{entry['orcid_id']}/record",),
            )


def _read_bytes(path: Path) -> bytes:
    return path.read_bytes()


def _iter_subset_paths(subset_dir: Path, max_records: int) -> Iterator[Path]:
    """First ``max_records`` subset files in bucket then name order (0 means all)."""
    emitted = 0
    for bucket in sorted(entry for entry in subset_dir.iterdir() if entry.is_dir()):
        for path in sorted(bucket.glob("*.xml")):
            if max_records and emitted >= max_records:
                return
            emitted += 1
            yield path


def _iter_bulk_envelopes(
    run: RunContext, subset_dir: Path, marker: dict[str, Any], snapshot: str, max_records: int
) -> Iterator[dict[str, Any]]:
    artifact = {"name": marker["archive"]["name"], "md5": marker["archive"]["md5"]}
    pending: deque[tuple[Path, Future[bytes]]] = deque()
    paths = _iter_subset_paths(subset_dir, max_records)
    with ThreadPoolExecutor(max_workers=_READ_WORKERS) as executor:
        exhausted = False
        while pending or not exhausted:
            while not exhausted and len(pending) < _PREFETCH_WINDOW:
                path = next(paths, None)
                if path is None:
                    exhausted = True
                else:
                    pending.append((path, executor.submit(_read_bytes, path)))
            if not pending:
                break
            path, future = pending.popleft()
            xml_bytes = future.result()
            check, _ = check_orcid_summary_xml(xml_bytes)
            yield build_envelope(
                source=SOURCE_ORCID_BULK,
                source_ref=path.stem,
                payload=xml_bytes.decode("utf-8"),
                payload_format=PAYLOAD_FORMAT_XML,
                run=run,
                retrieved_at=marker["retrieved_at"],
                source_snapshot=snapshot,
                check=check,
                source_files=(f"filtered/{path.parent.name}/{path.name}",),
                source_artifacts=(artifact,),
            )


def land_bronze(
    run: RunContext,
    data_dir: Path = DEFAULT_DATA_DIR,
    *,
    s3: S3Client | None = None,
    bucket: str = DEFAULT_BUCKET,
    bulk_max_records: int = DEFAULT_BULK_MAX_RECORDS,
    rejection_threshold: float = DEFAULT_REJECTION_THRESHOLD,
    force_bulk_landing: bool = False,
) -> dict[str, Any]:
    """Check every source's records and land them into MinIO bronze.

    Synthetic CVN and API records are landed on every run. The ORCID bulk
    subset is a static snapshot, so it is landed only once per snapshot and
    record cap (later runs report ``skipped``) unless ``force_bulk_landing`` is
    set. ``bulk_max_records`` caps how many subset records are landed, in a
    deterministic bucket order, because the whole subset is about 40 GB of XML;
    0 lands all of it.

    Args:
        run: The landing run.
        data_dir: Repository ``data/`` directory.
        s3: S3 client; a MinIO one from the environment when omitted.
        bucket: Target bucket.
        bulk_max_records: Cap on ORCID bulk records landed; 0 for no cap.
        rejection_threshold: Highest tolerated share of rejected records per source.
        force_bulk_landing: Land the bulk snapshot even if it was landed before.

    Returns:
        A summary per source.
    """
    s3 = s3 or create_s3_client()
    paths = _paths(data_dir, run)
    synthetic = _read_summary(run, data_dir, "synthetic_cvn")
    summaries: dict[str, Any] = {}

    summaries[SOURCE_SYNTHETIC_CVN] = land_records(
        s3,
        bucket=bucket,
        source=SOURCE_SYNTHETIC_CVN,
        run=run,
        source_snapshot=f"synthetic|generator_seed={synthetic['seed']}",
        envelopes=_iter_synthetic_envelopes(run, paths["synthetic_dir"], synthetic["generated_at"]),
        rejection_threshold=rejection_threshold,
        extra_manifest={"generated": synthetic["generated"], "linked": synthetic["linked"]},
    ).to_dict()

    summaries[SOURCE_ORCID_API] = land_records(
        s3,
        bucket=bucket,
        source=SOURCE_ORCID_API,
        run=run,
        source_snapshot="orcid_public_api_v3.0",
        envelopes=_iter_api_envelopes(run, paths["api_file"]),
        rejection_threshold=rejection_threshold,
        extra_manifest=_read_summary(run, data_dir, "orcid_api"),
    ).to_dict()

    marker = json.loads(paths["subset_marker"].read_text(encoding="utf-8"))
    snapshot = f"{marker['source_snapshot']}|records={'all' if bulk_max_records == 0 else bulk_max_records}"
    earlier = [run_id for run_id in find_landed_runs(s3, bucket=bucket, source=SOURCE_ORCID_BULK, source_snapshot=snapshot) if run_id != run.run_id]
    if earlier and not force_bulk_landing:
        summaries[SOURCE_ORCID_BULK] = {"skipped": True, "reason": "snapshot already landed", "landed_by_runs": earlier}
    else:
        summaries[SOURCE_ORCID_BULK] = land_records(
            s3,
            bucket=bucket,
            source=SOURCE_ORCID_BULK,
            run=run,
            source_snapshot=snapshot,
            envelopes=_iter_bulk_envelopes(run, paths["subset_dir"], marker, snapshot, bulk_max_records),
            rejection_threshold=rejection_threshold,
            extra_manifest={"bulk_max_records": bulk_max_records, "subset_matched": marker["matched"]},
        ).to_dict()
    return _write_summary(run, data_dir, "land_bronze", {"sources": summaries})


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m tfm_lakehouse.bronze.tasks", description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    commands = parser.add_subparsers(dest="command", required=True)

    bulk = commands.add_parser("orcid-bulk-subset", help="ensure the ORCID subset exists and is marked complete")
    bulk.add_argument("--force-refetch", action="store_true")

    for name in ("synthetic-cvn", "orcid-api-enrichment", "land-bronze"):
        command = commands.add_parser(name)
        command.add_argument("--run-id", required=True)
        if name == "synthetic-cvn":
            command.add_argument("--count", type=int, required=True)
            command.add_argument("--seed", type=int, default=42)
            command.add_argument("--orcid-link-ratio", type=float, default=0.7)
        elif name == "orcid-api-enrichment":
            command.add_argument("--sample-size", type=int, default=DEFAULT_ENRICHMENT_SAMPLE_SIZE)
            command.add_argument("--seed", type=int, default=42)
        else:
            command.add_argument("--bulk-max-records", type=int, default=DEFAULT_BULK_MAX_RECORDS)
            command.add_argument("--rejection-threshold", type=float, default=DEFAULT_REJECTION_THRESHOLD)
            command.add_argument("--force-bulk-landing", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s", stream=sys.stdout)
    args = _parser().parse_args(argv)
    if args.command == "orcid-bulk-subset":
        summary = ensure_orcid_subset(args.data_dir, force_refetch=args.force_refetch)
        logger.info(f"TASK_SUMMARY {json.dumps({'task': 'orcid_bulk_subset', **summary})}")
        return 0

    run = RunContext.create(args.run_id)
    if args.command == "synthetic-cvn":
        run_synthetic_cvn(run, args.data_dir, count=args.count, seed=args.seed, orcid_link_ratio=args.orcid_link_ratio)
    elif args.command == "orcid-api-enrichment":
        run_orcid_api_enrichment(run, args.data_dir, sample_size=args.sample_size, seed=args.seed)
    else:
        land_bronze(
            run,
            args.data_dir,
            bulk_max_records=args.bulk_max_records,
            rejection_threshold=args.rejection_threshold,
            force_bulk_landing=args.force_bulk_landing,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
