"""Issue #99: the silver -> gold Spark job.

Reads the silver Iceberg tables of issue #98, computes the research indicators
(publications per researcher per year, affiliation timeline, collaboration pairs) and
the researcher dimension, and writes the ``lakehouse.gold`` Iceberg tables as a full
deterministic rebuild (``createOrReplace``, the same choice as silver). ``gold_run`` is
written last: one row with the silver snapshot ids that were read and the row counts,
which makes any gold figure traceable to the exact silver state and marks a complete
write. Nothing is written when silver is empty or lacks a table, so a broken upstream
never replaces a good gold.

Run with ``spark-submit --properties-file iceberg-catalog.conf`` on the silver or gold
image; ``src/`` is mounted from the checkout (infra/spark-conf/README.md).
"""

from __future__ import annotations

import argparse
import datetime
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
from pyspark.sql.utils import AnalysisException

from tfm_lakehouse.gold import indicators, schemas

logger = logging.getLogger("tfm_lakehouse.spark_jobs.silver_to_gold")

DEFAULT_SILVER_NAMESPACE = "lakehouse.silver"
DEFAULT_GOLD_NAMESPACE = "lakehouse.gold"
DEFAULT_SHUFFLE_PARTITIONS = 16
# The silver tables the indicators read.
SILVER_INPUTS = ("entity", "entity_link", "publication", "affiliation")


class SilverToGoldError(RuntimeError):
    """The job cannot produce a trustworthy gold layer."""


def main(argv: Sequence[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s", stream=sys.stdout)
    args = _parse_args(argv)
    spark = SparkSession.builder.appName("silver_to_gold").getOrCreate()
    try:
        summary = run(
            spark,
            silver_namespace=args.silver_namespace,
            gold_namespace=args.gold_namespace,
            run_id=args.run_id,
            max_year=args.max_year,
            max_entities_per_doi=args.max_entities_per_doi,
            shuffle_partitions=args.shuffle_partitions,
        )
    except SilverToGoldError as exc:
        logger.error(f"silver -> gold failed: {exc}")
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
    silver_namespace: str = DEFAULT_SILVER_NAMESPACE,
    gold_namespace: str = DEFAULT_GOLD_NAMESPACE,
    run_id: str | None = None,
    max_year: int | None = None,
    max_entities_per_doi: int = indicators.DEFAULT_MAX_ENTITIES_PER_DOI,
    shuffle_partitions: int = DEFAULT_SHUFFLE_PARTITIONS,
) -> dict[str, Any]:
    """Rebuild the gold tables from the current silver tables.

    Args:
        spark: A session configured with the Iceberg ``lakehouse`` catalog.
        silver_namespace: Catalog namespace holding the silver tables.
        gold_namespace: Catalog namespace receiving the gold tables.
        run_id: Identifier stored in ``gold_run`` (the Airflow run id); generated from
            the clock when omitted.
        max_year: Highest year accepted as a publication year; the current year plus
            one when omitted.
        max_entities_per_doi: Guard of the collaboration pairs (``indicators``).
        shuffle_partitions: Value of ``spark.sql.shuffle.partitions`` for the run.

    Returns:
        The run summary (the ``gold_run`` row, and the row count of every table).

    Raises:
        SilverToGoldError: If a silver table is missing or silver holds no entities.
    """
    started = time.time()
    now = datetime.datetime.now(datetime.timezone.utc)
    run_id = run_id or now.strftime("manual__%Y-%m-%dT%H:%M:%SZ")
    max_year = max_year if max_year is not None else now.year + 1
    spark.conf.set("spark.sql.shuffle.partitions", str(shuffle_partitions))

    silver = {name: _read_silver(spark, silver_namespace, name) for name in SILVER_INPUTS}
    snapshots = {name: _current_snapshot(spark, silver_namespace, name) for name in SILVER_INPUTS}
    entities = silver["entity"].count()
    if entities == 0:
        raise SilverToGoldError(f"{silver_namespace}.entity is empty; gold was not written")

    built = indicators.build_gold(
        entity=silver["entity"],
        entity_link=silver["entity_link"],
        publication=silver["publication"],
        affiliation=silver["affiliation"],
        max_year=max_year,
        max_entities_per_doi=max_entities_per_doi,
    )
    for frame in built.tables.values():
        frame.persist(StorageLevel.MEMORY_AND_DISK)
    built.distinct_publications.persist(StorageLevel.MEMORY_AND_DISK)

    counts = {name: frame.count() for name, frame in built.tables.items()}
    run_row = {
        "run_id": run_id,
        "computed_at": now,
        "max_year": max_year,
        "max_entities_per_doi": max_entities_per_doi,
        "silver_snapshots": json.dumps(snapshots, sort_keys=True),
        "entities": entities,
        "entities_with_publications": built.tables[schemas.DIM_RESEARCHER].where(F.col("publication_count") > 0).count(),
        "publication_rows_read": silver["publication"].count(),
        "publications_distinct": built.distinct_publications.count(),
        "publications_without_year": built.distinct_publications.where(F.col("year").isNull()).count(),
        "affiliation_rows_read": silver["affiliation"].count(),
        "timeline_rows": counts[schemas.AFFILIATION_TIMELINE],
        "per_year_rows": counts[schemas.PUBLICATIONS_PER_RESEARCHER_YEAR],
        "collaboration_pairs": counts[schemas.COLLABORATION_PAIRS],
        "dois_excluded_too_many_entities": built.dois_excluded,
    }
    gold_run = spark.createDataFrame(
        [schemas.row_values(schemas.TABLE_COLUMNS[schemas.GOLD_RUN], run_row)],
        schemas.columns_ddl(schemas.TABLE_COLUMNS[schemas.GOLD_RUN]),
    )

    spark.sql(f"CREATE NAMESPACE IF NOT EXISTS {gold_namespace}")
    for name in schemas.TABLES:
        frame = gold_run if name == schemas.GOLD_RUN else built.tables[name]
        frame.writeTo(f"{gold_namespace}.{name}").using("iceberg").createOrReplace()
        logger.info(f"wrote {gold_namespace}.{name}")

    for frame in built.tables.values():
        frame.unpersist()
    built.distinct_publications.unpersist()
    return {
        "silver_namespace": silver_namespace,
        "gold_namespace": gold_namespace,
        "shuffle_partitions": shuffle_partitions,
        "run": {**run_row, "computed_at": now.isoformat(), "silver_snapshots": snapshots},
        "tables": {name: int(spark.table(f"{gold_namespace}.{name}").count()) for name in schemas.TABLES},
        "elapsed_seconds": round(time.time() - started, 1),
    }


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rebuild the gold tables from silver (issue #99).")
    parser.add_argument("--silver-namespace", default=DEFAULT_SILVER_NAMESPACE)
    parser.add_argument("--gold-namespace", default=DEFAULT_GOLD_NAMESPACE)
    parser.add_argument("--run-id", help="Identifier stored in gold_run (the Airflow run id)")
    parser.add_argument("--max-year", type=int, help="Highest accepted publication year (default: current year + 1)")
    parser.add_argument("--max-entities-per-doi", type=int, default=indicators.DEFAULT_MAX_ENTITIES_PER_DOI)
    parser.add_argument("--shuffle-partitions", type=int, default=DEFAULT_SHUFFLE_PARTITIONS)
    parser.add_argument("--summary-file", help="Also write the summary JSON to this local path")
    return parser.parse_args(argv)


def _read_silver(spark: SparkSession, namespace: str, name: str) -> DataFrame:
    try:
        return spark.table(f"{namespace}.{name}")
    except AnalysisException as exc:
        raise SilverToGoldError(f"silver table {namespace}.{name} is missing; gold was not written") from exc


def _current_snapshot(spark: SparkSession, namespace: str, name: str) -> int | None:
    rows = spark.sql(f"SELECT snapshot_id FROM {namespace}.{name}.snapshots ORDER BY committed_at DESC LIMIT 1").collect()
    return int(rows[0]["snapshot_id"]) if rows else None


if __name__ == "__main__":
    sys.exit(main())
