"""Runs ``table_digest`` in local-mode Spark inside the Spark image (issue #101).

Not a test module: ``tests/test_benchmark_digest_spark.py`` executes it in a container and reads
``/work/output.json``: the digest of a table, of the same rows in another order and partitioning,
of the same table with one value changed, of the table with an extra row, and of an empty table.
"""

import json

from pyspark.sql import SparkSession

from tfm_lakehouse.spark_jobs import table_digest as table_digest_module
from tfm_lakehouse.spark_jobs.table_digest import table_digest

SCHEMA = "id int, name string, tags array<int>, attrs map<string,int>, at timestamp"


def main() -> None:
    spark = (
        SparkSession.builder.master("local[2]")
        .appName("digest_test")
        .config("spark.ui.enabled", "false")
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.sql.catalog.lakehouse", "org.apache.iceberg.spark.SparkCatalog")
        .config("spark.sql.catalog.lakehouse.type", "hadoop")
        .config("spark.sql.catalog.lakehouse.warehouse", "file:///work/warehouse")
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
        .getOrCreate()
    )
    rows = [
        (1, "x", [1, 2], {"a": 1}, None),
        (2, "y", [3], {"b": 2}, None),
        (3, None, [], {}, None),
        (4, "w", [5], {"c": 3}, None),
    ]
    base = spark.createDataFrame(rows, SCHEMA)
    reordered = spark.createDataFrame(list(reversed(rows)), SCHEMA).repartition(3)
    changed = spark.createDataFrame([rows[0], (2, "z", [3], {"b": 2}, None), *rows[2:]], SCHEMA)
    extra = spark.createDataFrame([*rows, (5, "v", [], {}, None)], SCHEMA)
    empty = spark.createDataFrame([], SCHEMA)
    output = {name: table_digest(frame) for name, frame in [("base", base), ("reordered", reordered), ("changed", changed), ("extra", extra), ("empty", empty)]}

    # A run that OOM'd before writing anything leaves its Iceberg table (and namespace directory)
    # missing entirely, not merely empty (issue #101, D24): the CLI must treat that as data, not
    # crash. spark.stop() below shuts down this SparkSession too, so run the CLI first.
    spark.sql("CREATE NAMESPACE IF NOT EXISTS lakehouse.bench_probe")
    base.writeTo("lakehouse.bench_probe.present").using("iceberg").createOrReplace()
    exit_code = table_digest_module.main(
        [
            "--namespace",
            "lakehouse.bench_probe",
            "--tables",
            "present",
            "absent",
            "--rows-only",
            "absent",
            "--summary-file",
            "/work/cli_output.json",
        ]
    )
    output["cli_exit_code"] = exit_code
    with open("/work/cli_output.json", encoding="utf-8") as handle:
        output["cli_digests"] = json.load(handle)

    with open("/work/output.json", "w", encoding="utf-8") as handle:
        json.dump(output, handle)
    spark.stop()


main()
