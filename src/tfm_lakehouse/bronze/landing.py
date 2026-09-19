from __future__ import annotations

import hashlib
import json
import logging
import os
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any, Protocol

from tfm_lakehouse.bronze.checks import serialize_line
from tfm_lakehouse.bronze.envelope import RunContext
from tfm_lakehouse.bronze.exceptions import BronzeLandingError, BronzeRejectionThresholdError

logger = logging.getLogger(__name__)

DEFAULT_ENDPOINT_URL = "http://minio.tfm-lakehouse.svc.cluster.local:9000"
DEFAULT_BUCKET = "lakehouse"
BRONZE_PREFIX = "bronze"
REJECTED_PREFIX = f"{BRONZE_PREFIX}/_rejected"
MANIFEST_NAME = "_manifest.json"
DEFAULT_SHARD_TARGET_BYTES = 64 * 1024 * 1024
DEFAULT_REJECTION_THRESHOLD = 0.05


class S3Client(Protocol):
    """The four boto3 S3 client calls landing uses; tests inject a fake."""

    def put_object(self, **kwargs: Any) -> Any: ...

    def get_object(self, **kwargs: Any) -> Any: ...

    def list_objects_v2(self, **kwargs: Any) -> Any: ...

    def delete_objects(self, **kwargs: Any) -> Any: ...


def create_s3_client(endpoint_url: str | None = None) -> S3Client:
    """Create a boto3 client for the in-cluster MinIO.

    Credentials come from the standard ``AWS_ACCESS_KEY_ID`` /
    ``AWS_SECRET_ACCESS_KEY`` environment variables, which the DAG injects
    from the ``minio-root-credentials`` Secret. Nothing secret is read from
    the repository.
    """
    import boto3
    from botocore.config import Config

    return boto3.client(
        "s3",
        endpoint_url=endpoint_url or os.environ.get("BRONZE_S3_ENDPOINT", DEFAULT_ENDPOINT_URL),
        region_name="us-east-1",
        config=Config(s3={"addressing_style": "path"}, signature_version="s3v4"),
    )


def partition_prefix(source: str, run: RunContext, *, rejected: bool = False) -> str:
    """Object-key prefix of one run's partition of one source.

    Hive-style ``key=value`` segments let Spark discover ``source``,
    ``ingestion_date`` and ``run_id`` as partition columns. Rejected records
    live under ``bronze/_rejected/``: readers that skip ``_``-prefixed paths
    (Spark and Hadoop input formats do) never see them when reading
    ``bronze/``.
    """
    root = REJECTED_PREFIX if rejected else BRONZE_PREFIX
    return f"{root}/source={source}/ingestion_date={run.ingestion_date.isoformat()}/run_id={run.run_id}/"


def _list_keys(s3: S3Client, bucket: str, prefix: str) -> list[str]:
    keys: list[str] = []
    token: str | None = None
    while True:
        kwargs: dict[str, Any] = {"Bucket": bucket, "Prefix": prefix}
        if token:
            kwargs["ContinuationToken"] = token
        page = s3.list_objects_v2(**kwargs)
        keys.extend(item["Key"] for item in page.get("Contents", []))
        if not page.get("IsTruncated"):
            return keys
        token = page["NextContinuationToken"]


def _delete_prefix(s3: S3Client, bucket: str, prefix: str) -> int:
    keys = _list_keys(s3, bucket, prefix)
    for start in range(0, len(keys), 1000):
        chunk = keys[start : start + 1000]
        s3.delete_objects(Bucket=bucket, Delete={"Objects": [{"Key": key} for key in chunk], "Quiet": True})
    return len(keys)


@dataclass(frozen=True)
class ShardInfo:
    key: str
    records: int
    bytes: int
    sha256: str


@dataclass(frozen=True)
class LandingSummary:
    """Result of landing one source in one run."""

    source: str
    run_id: str
    ingestion_date: str
    source_snapshot: str
    records_landed: int
    records_rejected: int
    shards: tuple[ShardInfo, ...] = field(default=())
    rejected_shards: tuple[ShardInfo, ...] = field(default=())
    manifest_key: str = ""

    @property
    def rejection_rate(self) -> float:
        total = self.records_landed + self.records_rejected
        return self.records_rejected / total if total else 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "run_id": self.run_id,
            "ingestion_date": self.ingestion_date,
            "source_snapshot": self.source_snapshot,
            "records_landed": self.records_landed,
            "records_rejected": self.records_rejected,
            "rejection_rate": round(self.rejection_rate, 6),
            "shards": [vars(shard) for shard in self.shards],
            "rejected_shards": [vars(shard) for shard in self.rejected_shards],
            "manifest_key": self.manifest_key,
        }


class _ShardWriter:
    """Accumulates JSON Lines and uploads one object each time it reaches its target size."""

    def __init__(self, s3: S3Client, bucket: str, prefix: str, target_bytes: int) -> None:
        self._s3 = s3
        self._bucket = bucket
        self._prefix = prefix
        self._target_bytes = target_bytes
        self._buffer = bytearray()
        self._buffered_records = 0
        self.shards: list[ShardInfo] = []

    @property
    def records(self) -> int:
        return sum(shard.records for shard in self.shards) + self._buffered_records

    def add(self, line: bytes) -> None:
        self._buffer += line
        self._buffered_records += 1
        if len(self._buffer) >= self._target_bytes:
            self._flush()

    def close(self) -> None:
        if self._buffered_records:
            self._flush()

    def _flush(self) -> None:
        key = f"{self._prefix}part-{len(self.shards):05d}.jsonl"
        body = bytes(self._buffer)
        self._s3.put_object(Bucket=self._bucket, Key=key, Body=body, ContentType="application/x-ndjson")
        self.shards.append(
            ShardInfo(key=key, records=self._buffered_records, bytes=len(body), sha256=hashlib.sha256(body).hexdigest())
        )
        logger.info(f"landed {key} ({self._buffered_records} records, {len(body)} bytes)")
        self._buffer = bytearray()
        self._buffered_records = 0


def land_records(
    s3: S3Client,
    *,
    bucket: str,
    source: str,
    run: RunContext,
    source_snapshot: str,
    envelopes: Iterable[Mapping[str, Any]],
    shard_target_bytes: int = DEFAULT_SHARD_TARGET_BYTES,
    rejection_threshold: float = DEFAULT_REJECTION_THRESHOLD,
    extra_manifest: Mapping[str, Any] | None = None,
) -> LandingSummary:
    """Land envelopes of one source as one partition of bronze.

    Records whose ``landing_check`` is invalid go to the ``_rejected`` prefix;
    the rest go to the source's partition. Any earlier objects of the *same*
    run for this source are deleted first, so re-running a task with the same
    run id replaces its partition instead of duplicating it. The manifest is
    written last, and a run that fails removes its landed shards, so bronze
    never exposes a partial partition to a reader that ignores manifests.

    Args:
        s3: An S3 client.
        bucket: Target bucket.
        source: One of ``envelope.SOURCES``.
        run: The landing run.
        source_snapshot: Identifier of the source version, kept in the manifest.
        envelopes: Records built with ``envelope.build_envelope``.
        shard_target_bytes: Size at which a shard is uploaded and a new one starts.
        rejection_threshold: Highest tolerated share of rejected records.
        extra_manifest: Extra keys for the manifest (run parameters).

    Returns:
        The landing summary.

    Raises:
        BronzeLandingError: When no record was received.
        BronzeRejectionThresholdError: When the rejection rate exceeds
            ``rejection_threshold``. The landed shards are removed and no
            manifest is written; the rejected records stay for inspection.
    """
    landed_prefix = partition_prefix(source, run)
    rejected_prefix = partition_prefix(source, run, rejected=True)
    replaced = _delete_prefix(s3, bucket, landed_prefix) + _delete_prefix(s3, bucket, rejected_prefix)
    if replaced:
        logger.info(f"replaced {replaced} objects of an earlier attempt of run {run.run_id} for {source}")

    landed = _ShardWriter(s3, bucket, landed_prefix, shard_target_bytes)
    rejected = _ShardWriter(s3, bucket, rejected_prefix, shard_target_bytes)
    try:
        for envelope in envelopes:
            target = landed if envelope["landing_check"]["status"] == "valid" else rejected
            target.add(serialize_line(envelope))
        landed.close()
        rejected.close()

        summary = LandingSummary(
            source=source,
            run_id=run.run_id,
            ingestion_date=run.ingestion_date.isoformat(),
            source_snapshot=source_snapshot,
            records_landed=landed.records,
            records_rejected=rejected.records,
            shards=tuple(landed.shards),
            rejected_shards=tuple(rejected.shards),
            manifest_key=f"{landed_prefix}{MANIFEST_NAME}",
        )
        if summary.records_landed + summary.records_rejected == 0:
            raise BronzeLandingError(f"no records received for {source} in run {run.run_id}")
        if summary.rejection_rate > rejection_threshold:
            raise BronzeRejectionThresholdError(
                f"{source}: {summary.records_rejected} of {summary.records_landed + summary.records_rejected} "
                f"records rejected ({summary.rejection_rate:.1%}), above the {rejection_threshold:.1%} threshold; "
                f"see s3://{bucket}/{rejected_prefix}"
            )
    except BaseException:
        # A partition without a manifest is incomplete by convention, but Spark
        # reads every part file under bronze/ regardless, so a failed run must
        # not leave landed shards behind. Rejected records stay for diagnosis.
        _delete_prefix(s3, bucket, landed_prefix)
        raise

    manifest = {**summary.to_dict(), "landed_at": run.landed_at, **dict(extra_manifest or {})}
    s3.put_object(
        Bucket=bucket,
        Key=summary.manifest_key,
        Body=json.dumps(manifest, indent=2, ensure_ascii=False).encode("utf-8"),
        ContentType="application/json",
    )
    return summary


def find_landed_runs(s3: S3Client, *, bucket: str, source: str, source_snapshot: str) -> list[str]:
    """Return the run ids that completely landed the given snapshot of a source.

    Only partitions with a manifest count. Used to land a static snapshot (the
    ORCID bulk subset) once rather than once per day.
    """
    run_ids: list[str] = []
    for key in _list_keys(s3, bucket, f"{BRONZE_PREFIX}/source={source}/"):
        if not key.endswith(f"/{MANIFEST_NAME}"):
            continue
        manifest = json.loads(s3.get_object(Bucket=bucket, Key=key)["Body"].read())
        if manifest.get("source_snapshot") == source_snapshot:
            run_ids.append(str(manifest["run_id"]))
    return run_ids
