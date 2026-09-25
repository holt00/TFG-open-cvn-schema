"""Issue #101: an order-independent content digest of Iceberg tables.

The benchmark uses it to check that a run with a different executor count produced the same
tables (decision D9): for every table it prints the row count and the sum of a 64-bit hash of
each row's JSON form, which does not depend on row order or on how the rows were partitioned.
Run with ``spark-submit --properties-file iceberg-catalog.conf`` on the gold image.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pyspark.errors.exceptions.captured import AnalysisException
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F


def table_digest(frame: DataFrame) -> dict:
    """Return ``{"rows": n, "digest": "<decimal string>"}`` for a DataFrame."""
    row_hash = F.xxhash64(F.to_json(F.struct(*[F.col(f"`{name}`") for name in frame.columns])))
    result = frame.agg(F.count(F.lit(1)).alias("rows"), F.sum(row_hash.cast("decimal(38,0)")).alias("digest")).first()
    digest = result["digest"]
    return {"rows": int(result["rows"]), "digest": "0" if digest is None else str(digest)}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Print the content digest of Iceberg tables.")
    parser.add_argument("--namespace", required=True, help="for example lakehouse.bench_silver_1x")
    parser.add_argument("--tables", nargs="+", required=True)
    parser.add_argument(
        "--rows-only",
        nargs="*",
        default=[],
        help="tables whose content legitimately differs between runs (a run id, timestamps): only the row count is kept",
    )
    parser.add_argument("--summary-file")
    args = parser.parse_args(argv)

    spark = SparkSession.builder.appName("table_digest").getOrCreate()
    try:
        digests = {}
        for table in args.tables:
            try:
                frame = spark.table(f"{args.namespace}.{table}")
            except AnalysisException:
                # A run that failed before writing anything leaves no table at all (the namespace
                # reset before it removes the whole warehouse directory, not just its rows), which
                # is legitimate data for a benchmark run's digest, not an error (issue #101, D24).
                digests[table] = {"rows": 0, "digest": "0", "exists": False}
                continue
            digests[table] = {"rows": frame.count(), "exists": True} if table in args.rows_only else {**table_digest(frame), "exists": True}
    finally:
        spark.stop()

    print(f"TASK_SUMMARY {json.dumps({'namespace': args.namespace, 'digests': digests}, sort_keys=True)}", file=sys.stdout, flush=True)
    if args.summary_file:
        Path(args.summary_file).parent.mkdir(parents=True, exist_ok=True)
        Path(args.summary_file).write_text(json.dumps(digests, indent=2, sort_keys=True), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
