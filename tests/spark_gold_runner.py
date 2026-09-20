"""Runs the issue #99 gold jobs in local-mode Spark inside the Spark image.

Not a test module: ``tests/test_gold_jobs_spark.py`` mounts and executes it in a
container. Reads ``/work/input.json``::

    {"silver": {"entity": [rows...], ...},     # tables to create in lakehouse.silver
     "steps": [{"op": "gold", "options": {...}}, {"op": "publish", "jdbc_url": "..."}],
     "dump": ["dim_researcher", ...]}          # gold tables to write to the output

and writes ``/work/output.json`` with one result (or error) per step and the dumped
gold tables. A missing silver table is simply not listed in ``silver``.
"""

import json
import os

from pyspark.sql import SparkSession

from tfm_lakehouse.gold import schemas as gold_schemas
from tfm_lakehouse.silver import schemas as silver_schemas
from tfm_lakehouse.spark_jobs import publish_gold_to_postgres, silver_to_gold


def _session() -> SparkSession:
    return (
        SparkSession.builder.master("local[2]")
        .appName("issue99_gold_jobs")
        .config("spark.ui.enabled", "false")
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.sql.catalog.lakehouse", "org.apache.iceberg.spark.SparkCatalog")
        .config("spark.sql.catalog.lakehouse.type", "hadoop")
        .config("spark.sql.catalog.lakehouse.warehouse", "file:///work/warehouse")
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
        .getOrCreate()
    )


def _create_silver(spark: SparkSession, silver: dict) -> None:
    spark.sql("CREATE NAMESPACE IF NOT EXISTS lakehouse.silver")
    for table, rows in silver.items():
        columns = silver_schemas.TABLE_COLUMNS[table]
        data = [tuple(row.get(name) for name, _ in columns) for row in rows]
        frame = spark.createDataFrame(data, silver_schemas.columns_ddl(columns))
        frame.writeTo(f"lakehouse.silver.{table}").using("iceberg").createOrReplace()


def _step(spark: SparkSession, step: dict) -> dict:
    try:
        if step["op"] == "gold":
            return {"ok": silver_to_gold.run(spark, **step.get("options", {}))}
        if step["op"] == "publish":
            return {
                "ok": publish_gold_to_postgres.run(
                    spark, jdbc_url=step["jdbc_url"], user="gold", password=os.environ["PG_PASSWORD"], **step.get("options", {})
                )
            }
        raise ValueError(step["op"])
    except (silver_to_gold.SilverToGoldError, publish_gold_to_postgres.PublishError) as exc:
        return {"error": str(exc)}


def main() -> None:
    spark = _session()
    data = json.load(open("/work/input.json", encoding="utf-8"))
    _create_silver(spark, data.get("silver", {}))
    results = [_step(spark, step) for step in data["steps"]]
    tables = {}
    for name in data.get("dump", []):
        if spark.catalog.tableExists(f"lakehouse.gold.{name}"):
            tables[name] = [row.asDict() for row in spark.table(f"lakehouse.gold.{name}").collect()]
    existing = [row["tableName"] for row in spark.sql("SHOW TABLES IN lakehouse.gold").collect()] if spark.catalog.databaseExists("lakehouse.gold") else []
    output = {"results": results, "tables": tables, "gold_tables_present": sorted(existing), "known_tables": gold_schemas.TABLES}
    json.dump(output, open("/work/output.json", "w", encoding="utf-8"), ensure_ascii=False, default=str)
    spark.stop()


if __name__ == "__main__":
    main()
