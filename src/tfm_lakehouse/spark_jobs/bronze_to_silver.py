"""Issue #98: the bronze -> silver Spark job.

Reads each bronze source separately as JSON Lines text, deduplicates on
``record_id``, validates and normalizes every record into the common shape,
resolves entities across sources, and writes six Iceberg tables to the
``lakehouse.silver`` namespace (full rebuild, decision D9):
``person_record``, ``affiliation``, ``publication``, ``rejected``,
``entity_link`` and ``entity``.

Run with ``spark-submit --properties-file iceberg-catalog.conf`` on the silver
image (Python 3.10 with pydantic, jsonschema and requests); ``src/`` and
``schemas/`` are mounted from the checkout (infra/spark-conf/README.md).
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from pyspark import StorageLevel
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql import types as T
from pyspark.sql.types import _parse_datatype_string

from tfm_lakehouse.silver import schemas
from tfm_lakehouse.silver.evaluation import evaluate, format_report, load_manifest
from tfm_lakehouse.silver.pipeline import SOURCES, process_bronze_line
from tfm_lakehouse.silver.resolution import DEFAULT_ORG_THRESHOLD, SOURCE_CVN
from tfm_lakehouse.silver.resolution_spark import resolve_entities

logger = logging.getLogger("tfm_lakehouse.spark_jobs.bronze_to_silver")

DEFAULT_BRONZE_ROOT = "s3a://lakehouse/bronze"
DEFAULT_NAMESPACE = "lakehouse.silver"
DEFAULT_REJECTION_THRESHOLD = 0.05
# Spark's default of 200 shuffle partitions turns each join of this job into
# hundreds of tiny tasks that each start a Python worker (measured in issue #98,
# Task 5: 600 tasks for a 217 MB sample). Raise it for volume runs.
DEFAULT_SHUFFLE_PARTITIONS = 16

_ENVELOPE_FIELDS = (
    "source_ref",
    "source_snapshot",
    "retrieved_at",
    "landed_at",
    "ingestion_date",
    "ingestion_run_id",
)


class BronzeToSilverError(RuntimeError):
    """The job cannot produce a trustworthy silver layer."""


def main(argv: Sequence[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s", stream=sys.stdout)
    args = _parse_args(argv)
    spark = SparkSession.builder.appName("bronze_to_silver").getOrCreate()
    try:
        summary = run(
            spark,
            bronze_root=args.bronze_root,
            namespace=args.namespace,
            sources=args.sources,
            org_threshold=args.org_threshold,
            rejection_threshold=args.rejection_threshold,
            shuffle_partitions=args.shuffle_partitions,
            manifest_path=args.manifest,
        )
    except BronzeToSilverError as exc:
        logger.error(f"bronze -> silver failed: {exc}")
        return 1
    finally:
        spark.stop()

    logger.info(f"TASK_SUMMARY {json.dumps(summary, sort_keys=True)}")
    if args.summary_file:
        Path(args.summary_file).parent.mkdir(parents=True, exist_ok=True)
        with open(args.summary_file, "w", encoding="utf-8") as handle:
            json.dump(summary, handle, indent=2, sort_keys=True)
    return 0


def run(
    spark: SparkSession,
    *,
    bronze_root: str = DEFAULT_BRONZE_ROOT,
    namespace: str = DEFAULT_NAMESPACE,
    sources: Sequence[str] = SOURCES,
    org_threshold: float = DEFAULT_ORG_THRESHOLD,
    rejection_threshold: float = DEFAULT_REJECTION_THRESHOLD,
    shuffle_partitions: int = DEFAULT_SHUFFLE_PARTITIONS,
    manifest_path: str | None = None,
) -> dict[str, Any]:
    """Rebuild the silver tables from the current bronze data.

    Args:
        spark: A session configured with the Iceberg ``lakehouse`` catalog.
        bronze_root: Root of the landed bronze objects.
        namespace: Catalog namespace receiving the silver tables.
        sources: Bronze sources to read.
        org_threshold: Organization similarity threshold of the R2 rule.
        rejection_threshold: Highest tolerated share of rejected records of any
            source; above it nothing is written.
        shuffle_partitions: Value of ``spark.sql.shuffle.partitions`` for the run.
        manifest_path: Local path of a synthetic run's ``manifest.jsonl``. When given,
            the resolution is evaluated against it and the report is added to the
            summary (``silver/evaluation.py``).

    Returns:
        The run summary (counts per source, per rule, per table).

    Raises:
        BronzeToSilverError: If no bronze data is found, or a source exceeds the
            rejection threshold.
    """
    started = time.time()
    spark.conf.set("spark.sql.shuffle.partitions", str(shuffle_partitions))
    parsed = _read_and_parse(spark, bronze_root, sources)
    if parsed is None:
        raise BronzeToSilverError(f"no bronze data found under {bronze_root} for sources {list(sources)}")
    parsed.persist(StorageLevel.MEMORY_AND_DISK)

    source_stats = _source_stats(parsed)
    for source, stats in source_stats.items():
        if stats["rejection_rate"] > rejection_threshold:
            raise BronzeToSilverError(
                f"{source}: {stats['rejected']} of {stats['deduplicated']} records rejected "
                f"({stats['rejection_rate']:.2%}), above the {rejection_threshold:.2%} threshold; silver was not written"
            )

    valid = parsed.where(F.size("result.errors") == 0)
    person_record = _conform(_person_record(valid), "person_record")
    affiliation = _conform(_exploded(valid, "affiliations", schemas.AFFILIATION_COLUMNS), "affiliation")
    publication = _conform(_exploded(valid, "publications", schemas.PUBLICATION_COLUMNS), "publication")
    rejected = _conform(_rejected(parsed.where(F.size("result.errors") > 0)), "rejected")
    entity_link_raw, entity_raw = resolve_entities(person_record, affiliation, org_threshold)
    # Cached before projecting so the entity table reuses the same computation.
    entity_link_raw.persist(StorageLevel.MEMORY_AND_DISK)
    entity_link = _conform(entity_link_raw, "entity_link")
    entity = _conform(entity_raw, "entity")

    spark.sql(f"CREATE NAMESPACE IF NOT EXISTS {namespace}")
    tables = {
        "person_record": person_record,
        "affiliation": affiliation,
        "publication": publication,
        "rejected": rejected,
        "entity_link": entity_link,
        "entity": entity,
    }
    for name, frame in tables.items():
        frame.writeTo(f"{namespace}.{name}").using("iceberg").createOrReplace()
        logger.info(f"wrote {namespace}.{name}")

    summary = {
        "bronze_root": bronze_root,
        "namespace": namespace,
        "org_threshold": org_threshold,
        "rejection_threshold": rejection_threshold,
        "shuffle_partitions": shuffle_partitions,
        "sources": source_stats,
        "rejected_by_rule": _rejected_by_rule(rejected),
        "tables": {name: spark.table(f"{namespace}.{name}").count() for name in tables},
        "resolution": _resolution_stats(spark, namespace),
    }
    if manifest_path:
        summary["evaluation"] = _evaluate(spark, namespace, manifest_path)
        logger.info("resolution evaluation against the ground truth\n" + format_report(summary["evaluation"]))
    summary["elapsed_seconds"] = round(time.time() - started, 1)
    parsed.unpersist()
    entity_link_raw.unpersist()
    return summary


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rebuild the silver tables from bronze (issue #98).")
    parser.add_argument("--bronze-root", default=DEFAULT_BRONZE_ROOT)
    parser.add_argument("--namespace", default=DEFAULT_NAMESPACE)
    parser.add_argument("--sources", nargs="+", default=list(SOURCES), choices=SOURCES)
    parser.add_argument("--org-threshold", type=float, default=DEFAULT_ORG_THRESHOLD)
    parser.add_argument("--rejection-threshold", type=float, default=DEFAULT_REJECTION_THRESHOLD)
    parser.add_argument("--shuffle-partitions", type=int, default=DEFAULT_SHUFFLE_PARTITIONS)
    parser.add_argument("--manifest", help="manifest.jsonl of a synthetic run; evaluates the resolution against it")
    parser.add_argument("--summary-file", help="Also write the summary JSON to this local path")
    return parser.parse_args(argv)


def _read_and_parse(spark: SparkSession, bronze_root: str, sources: Sequence[str]) -> DataFrame | None:
    result_type = _parse_datatype_string(schemas.columns_ddl(schemas.RESULT_COLUMNS))
    frames = []
    for source in sources:
        path = f"{bronze_root.rstrip('/')}/source={source}"
        if not _exists(spark, path):
            logger.warning(f"no bronze data for source {source} at {path}")
            continue
        frames.append(_parse_source(spark.read.text(path), source, result_type))
    if not frames:
        return None
    combined = frames[0]
    for frame in frames[1:]:
        combined = combined.unionByName(frame)
    return combined


def _parse_source(lines: DataFrame, source: str, result_type: T.DataType) -> DataFrame:
    """Deduplicate a source's lines on ``record_id`` and parse the winners.

    The envelope fields come from ``get_json_object`` (in the JVM), so the
    Python workers only parse records that survive deduplication; a line can be
    several megabytes (ORCID XML). The latest ``landed_at``, then the greatest
    ``ingestion_run_id``, wins.
    """
    envelopes = lines.select(
        "value",
        F.coalesce(F.get_json_object("value", "$.record_id"), F.concat(F.lit("unidentified:"), F.sha1("value"))).alias("record_id"),
        *[F.get_json_object("value", f"$.{name}").alias(name) for name in _ENVELOPE_FIELDS],
    )
    ranked = (
        envelopes.groupBy("record_id")
        .agg(
            F.count("*").alias("copies"),
            F.max(F.struct("landed_at", "ingestion_run_id", "value", "source_ref", "source_snapshot", "retrieved_at", "ingestion_date")).alias("winner"),
        )
    )
    parse = F.udf(lambda line: process_bronze_line(source, line), result_type)
    return ranked.select(
        "record_id",
        F.lit(source).alias("source"),
        "copies",
        *[F.col(f"winner.{name}").alias(name) for name in _ENVELOPE_FIELDS],
        parse(F.col("winner.value")).alias("result"),
    )


def _exists(spark: SparkSession, path: str) -> bool:
    hadoop_path = spark._jvm.org.apache.hadoop.fs.Path(path)
    return bool(hadoop_path.getFileSystem(spark._jsc.hadoopConfiguration()).exists(hadoop_path))


def _source_stats(parsed: DataFrame) -> dict[str, dict[str, Any]]:
    rows = (
        parsed.groupBy("source")
        .agg(
            F.sum("copies").alias("read"),
            F.count("*").alias("deduplicated"),
            F.sum(F.when(F.size("result.errors") > 0, 1).otherwise(0)).alias("rejected"),
            F.sum(F.when(F.size("result.warnings") > 0, 1).otherwise(0)).alias("with_warnings"),
        )
        .collect()
    )
    stats: dict[str, dict[str, Any]] = {}
    for row in rows:
        deduplicated, rejected = int(row["deduplicated"]), int(row["rejected"])
        stats[row["source"]] = {
            "read": int(row["read"]),
            "deduplicated": deduplicated,
            "duplicates_dropped": int(row["read"]) - deduplicated,
            "valid": deduplicated - rejected,
            "rejected": rejected,
            "rejection_rate": rejected / deduplicated if deduplicated else 0.0,
            "with_warnings": int(row["with_warnings"]),
        }
    return stats


def _provenance() -> list:
    return [F.col(name) for name in schemas.column_names(schemas.PROVENANCE_COLUMNS)]


def _person_record(valid: DataFrame) -> DataFrame:
    return valid.select(
        "record_id",
        "source",
        "source_ref",
        *[F.col(f"result.person.{name}").alias(name) for name in schemas.column_names(schemas.PERSON_COLUMNS)],
        *_provenance(),
        F.col("result.warnings").alias("validation_warnings"),
    )


def _exploded(valid: DataFrame, column: str, columns: Sequence[schemas.Column]) -> DataFrame:
    return valid.select("record_id", F.explode(f"result.{column}").alias("item")).select(
        "record_id", *[F.col(f"item.{name}").alias(name) for name in schemas.column_names(columns)]
    )


def _rejected(rejected: DataFrame) -> DataFrame:
    return rejected.select(
        "record_id",
        "source",
        "source_ref",
        F.sort_array(F.array_distinct(F.transform("result.errors", lambda error: error["rule"]))).alias("rules"),
        F.transform("result.errors", lambda error: F.concat(error["rule"], F.lit(": "), error["message"])).alias("errors"),
        *_provenance(),
    )


def _conform(frame: DataFrame, table: str) -> DataFrame:
    """Select and cast the frame to exactly the columns of a silver table."""
    return frame.select(*[F.col(name).cast(type_).alias(name) for name, type_ in schemas.TABLE_COLUMNS[table]])


def _rejected_by_rule(rejected: DataFrame) -> dict[str, dict[str, int]]:
    rows = rejected.select("source", F.explode("rules").alias("rule")).groupBy("source", "rule").count().collect()
    by_rule: dict[str, dict[str, int]] = {}
    for row in rows:
        by_rule.setdefault(row["source"], {})[row["rule"]] = int(row["count"])
    return by_rule


def _evaluate(spark: SparkSession, namespace: str, manifest_path: str) -> dict[str, Any]:
    links = [
        row.asDict()
        for row in spark.table(f"{namespace}.entity_link")
        .where(F.col("source") == SOURCE_CVN)
        .select("record_id", "source", "entity_id", "match_rule", "ambiguous")
        .collect()
    ]
    persons = spark.table(f"{namespace}.person_record").where(F.col("orcid_id").isNotNull())
    orcid_ids = {
        row["orcid_id"] for row in persons.where(F.col("source") != SOURCE_CVN).select("orcid_id").distinct().collect()
    }
    anchored_ids = {row["orcid_id"] for row in persons.select("orcid_id").distinct().collect()}
    return evaluate(links, load_manifest(manifest_path), orcid_ids, anchored_ids)


def _resolution_stats(spark: SparkSession, namespace: str) -> dict[str, Any]:
    links = spark.table(f"{namespace}.entity_link")
    entities = spark.table(f"{namespace}.entity")
    by_rule = {row["match_rule"]: int(row["count"]) for row in links.groupBy("match_rule").count().collect()}
    flags = links.agg(
        F.sum(F.col("ambiguous").cast("int")).alias("ambiguous"), F.sum(F.col("name_conflict").cast("int")).alias("name_conflict")
    ).collect()[0]
    entity_counts = entities.agg(
        F.count("*").alias("entities"),
        F.sum(F.when(F.col("has_cvn") & F.col("has_orcid"), 1).otherwise(0)).alias("fused_cvn_and_orcid"),
        F.sum(F.when(F.col("record_count") > 1, 1).otherwise(0)).alias("multi_record"),
    ).collect()[0]
    return {
        "links_by_rule": by_rule,
        "ambiguous": int(flags["ambiguous"] or 0),
        "name_conflict": int(flags["name_conflict"] or 0),
        "entities": int(entity_counts["entities"]),
        "entities_fusing_cvn_and_orcid": int(entity_counts["fused_cvn_and_orcid"] or 0),
        "entities_with_several_records": int(entity_counts["multi_record"] or 0),
    }


if __name__ == "__main__":
    sys.exit(main())
