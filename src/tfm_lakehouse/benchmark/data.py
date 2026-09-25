"""Benchmark data of issue #101: one isolated bronze bucket per scale.

Scale ``Nx`` lands ``N * 20,000`` ORCID bulk records requested and ``N * 11,000``
synthetic CVN documents, plus a fixed sample of ORCID API records, into the bucket
``tfm-bench-<N>x`` (its ``bronze/`` prefix), so the production bronze, silver and gold are
never touched. The bulk records are the first ones in the subset's folder order and the CVN
documents the first ones of a seeded stream, so every scale contains the smaller ones.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import shutil
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tfm_lakehouse.bronze.envelope import RunContext
from tfm_lakehouse.bronze.landing import BRONZE_PREFIX, S3Client, create_s3_client
from tfm_lakehouse.bronze.tasks import DEFAULT_DATA_DIR, land_bronze, run_synthetic_cvn

logger = logging.getLogger(__name__)

BASE_BULK_RECORDS = 20_000
BASE_CVN_DOCUMENTS = 11_000
SCALE_FACTORS = (1, 2, 4)
SYNTHETIC_SEED = 43
ORCID_LINK_RATIO = 0.7
# Run whose 200-record ORCID API sample (iDs declared by the seed-43 CVNs) every scale reuses.
API_SAMPLE_RUN = "e2e98-big"
EVENTS_BUCKET = "tfm-bench-events"


@dataclass(frozen=True)
class Scale:
    """One data scale of the benchmark."""

    factor: int

    @property
    def bulk_records(self) -> int:
        return BASE_BULK_RECORDS * self.factor

    @property
    def cvn_documents(self) -> int:
        return BASE_CVN_DOCUMENTS * self.factor

    @property
    def name(self) -> str:
        return f"{self.factor}x"

    @property
    def run_id(self) -> str:
        return f"bench-{self.name}"

    @property
    def bucket(self) -> str:
        return f"tfm-bench-{self.name}"

    @property
    def bronze_root(self) -> str:
        return f"s3a://{self.bucket}/{BRONZE_PREFIX}"

    @property
    def silver_namespace(self) -> str:
        return f"lakehouse.bench_silver_{self.factor}x"

    @property
    def gold_namespace(self) -> str:
        return f"lakehouse.bench_gold_{self.factor}x"

    @property
    def pg_schema(self) -> str:
        return f"bench_{self.factor}x"


def scale_for(name: str | int) -> Scale:
    """Return the scale called ``"2x"`` (or ``2``); only the planned factors exist."""
    factor = int(str(name).lower().rstrip("x"))
    if factor not in SCALE_FACTORS:
        raise ValueError(f"unknown scale {name!r}; the benchmark scales are {[f'{f}x' for f in SCALE_FACTORS]}")
    return Scale(factor)


def ensure_bucket(s3: Any, bucket: str) -> bool:
    """Create ``bucket`` when it does not exist; return whether it was created."""
    from botocore.exceptions import ClientError

    try:
        s3.head_bucket(Bucket=bucket)
        return False
    except ClientError as exc:
        if exc.response.get("Error", {}).get("Code") not in {"404", "NoSuchBucket", "NotFound"}:
            raise
    s3.create_bucket(Bucket=bucket)
    logger.info(f"created bucket {bucket}")
    return True


def measure_bucket(s3: S3Client, bucket: str) -> dict[str, dict[str, int]]:
    """Objects and bytes under ``bronze/`` per source (rejected records under ``_rejected``)."""
    totals: dict[str, dict[str, int]] = {}
    token: str | None = None
    while True:
        kwargs: dict[str, Any] = {"Bucket": bucket, "Prefix": f"{BRONZE_PREFIX}/"}
        if token:
            kwargs["ContinuationToken"] = token
        page = s3.list_objects_v2(**kwargs)
        for item in page.get("Contents", []):
            parts = item["Key"].split("/")
            rejected = parts[1] == "_rejected"
            source = next((part.removeprefix("source=") for part in parts if part.startswith("source=")), "other")
            entry = totals.setdefault(f"{source}{' (rejected)' if rejected else ''}", {"objects": 0, "bytes": 0})
            entry["objects"] += 1
            entry["bytes"] += int(item["Size"])
        if not page.get("IsTruncated"):
            return totals
        token = page.get("NextContinuationToken")


def copy_api_sample(data_dir: Path, run: RunContext, *, source_run: str = API_SAMPLE_RUN) -> None:
    """Copy ``source_run``'s ORCID API records and summary into ``run``'s directory."""
    source = data_dir / "bronze_runs" / source_run
    target = data_dir / "bronze_runs" / run.run_id
    records = source / "orcid_api" / "records.jsonl"
    summary = source / "orcid_api.summary.json"
    if not records.is_file() or not summary.is_file():
        raise FileNotFoundError(f"run {source_run} has no ORCID API sample under {source}")
    (target / "orcid_api").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(records, target / "orcid_api" / "records.jsonl")
    shutil.copyfile(summary, target / "orcid_api.summary.json")


def prepare_scale(scale: Scale, data_dir: Path = DEFAULT_DATA_DIR, *, s3: Any | None = None) -> dict[str, Any]:
    """Generate the CVNs, copy the API sample and land one scale into its own bucket.

    Args:
        scale: The scale to prepare.
        data_dir: Repository ``data/`` directory (holds the ORCID subset and the run files).
        s3: S3 client; a MinIO one from the environment when omitted.

    Returns:
        The landing summary per source plus the measured objects and bytes of the bucket.
    """
    s3 = s3 or create_s3_client()
    run = RunContext.create(scale.run_id)
    ensure_bucket(s3, scale.bucket)
    run_synthetic_cvn(run, data_dir, count=scale.cvn_documents, seed=SYNTHETIC_SEED, orcid_link_ratio=ORCID_LINK_RATIO)
    copy_api_sample(data_dir, run)
    landing = land_bronze(run, data_dir, s3=s3, bucket=scale.bucket, bulk_max_records=scale.bulk_records)
    result = {"scale": scale.name, "bucket": scale.bucket, "landing": landing, "bucket_contents": measure_bucket(s3, scale.bucket)}
    output = data_dir / "benchmark" / "data"
    output.mkdir(parents=True, exist_ok=True)
    (output / f"{scale.name}.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return result


def main(argv: Sequence[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s", stream=sys.stdout)
    parser = argparse.ArgumentParser(prog="python -m tfm_lakehouse.benchmark.data", description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path(os.environ.get("TFM_DATA_DIR", DEFAULT_DATA_DIR)))
    parser.add_argument("scales", nargs="+", help="scales to prepare, e.g. 1x 2x 4x")
    args = parser.parse_args(argv)
    for name in args.scales:
        result = prepare_scale(scale_for(name), args.data_dir)
        logger.info(f"TASK_SUMMARY {json.dumps({'task': 'benchmark_data', 'scale': result['scale'], 'contents': result['bucket_contents']})}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
