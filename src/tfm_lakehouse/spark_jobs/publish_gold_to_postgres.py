"""Issue #99: publish the gold Iceberg tables to the dedicated PostgreSQL.

Superset (issue #100) reads these tables with its native PostgreSQL connector, so it
must never see a missing or half-loaded table while a publish runs (decision D5). The
job therefore stages first and swaps last:

1. create an empty ``_new_<table>`` per gold table with explicit DDL (types, primary
   key), dropping any left by a failed earlier attempt;
2. append the rows of ``lakehouse.gold.<table>`` into it over JDBC;
3. check that every staging table holds as many rows as its Iceberg table;
4. create the secondary indexes on the staging tables;
5. in ONE transaction, drop the published tables and rename the staging ones.

A failure before step 5 drops the staging tables and leaves the published tables as
they were. The SQL is built in ``tfm_lakehouse.gold.schemas`` (pure, tested on the
host); statements run over a plain ``java.sql.DriverManager`` connection opened through
the JVM of the Spark session, which needs the driver on the system classpath
(``infra/spark-conf/Dockerfile.gold``). The password comes from the ``PG_PASSWORD``
environment variable (a ``secretKeyRef`` on the launcher pod), never from an argument.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from pyspark.sql import SparkSession
from pyspark.sql.utils import AnalysisException

from tfm_lakehouse.gold import schemas

logger = logging.getLogger("tfm_lakehouse.spark_jobs.publish_gold_to_postgres")

DEFAULT_GOLD_NAMESPACE = "lakehouse.gold"
DEFAULT_JDBC_URL = "jdbc:postgresql://postgresql.tfm-lakehouse.svc.cluster.local:5432/gold"
DEFAULT_PG_USER = "gold"
DEFAULT_PG_SCHEMA = "gold"
DRIVER_CLASS = "org.postgresql.Driver"
PASSWORD_ENV = "PG_PASSWORD"
WRITE_PARTITIONS = 4
WRITE_BATCH_SIZE = 5000


class PublishError(RuntimeError):
    """The gold tables could not be published; the published tables are unchanged."""


def main(argv: Sequence[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s", stream=sys.stdout)
    args = _parse_args(argv)
    password = os.environ.get(PASSWORD_ENV)
    if not password:
        logger.error(f"publish failed: the {PASSWORD_ENV} environment variable is not set")
        return 1
    spark = SparkSession.builder.appName("publish_gold_to_postgres").getOrCreate()
    try:
        summary = run(
            spark,
            gold_namespace=args.gold_namespace,
            jdbc_url=args.jdbc_url,
            user=args.pg_user,
            password=password,
            pg_schema=args.pg_schema,
        )
    except PublishError as exc:
        logger.error(f"publish failed: {exc}")
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
    jdbc_url: str,
    user: str,
    password: str,
    gold_namespace: str = DEFAULT_GOLD_NAMESPACE,
    pg_schema: str = DEFAULT_PG_SCHEMA,
) -> dict[str, Any]:
    """Stage every gold table into PostgreSQL, then swap them in atomically.

    Args:
        spark: A session configured with the Iceberg ``lakehouse`` catalog and the
            PostgreSQL JDBC driver on its classpath.
        jdbc_url: JDBC URL of the target database.
        user: PostgreSQL user (owner of the database).
        password: Its password.
        gold_namespace: Catalog namespace holding the gold tables.
        pg_schema: PostgreSQL schema receiving the tables.

    Returns:
        The run summary (rows per table, the ``gold_run`` row that was published).

    Raises:
        PublishError: If a gold table is missing, ``gold_run`` does not hold exactly one
            row, a staging table's row count differs from Iceberg's, or PostgreSQL
            rejects a statement. The published tables are unchanged in every case.
    """
    started = time.time()
    frames = {name: _read_gold(spark, gold_namespace, name) for name in schemas.TABLES}
    expected = {name: int(frame.count()) for name, frame in frames.items()}
    if expected[schemas.GOLD_RUN] != 1:
        raise PublishError(f"{gold_namespace}.{schemas.GOLD_RUN} holds {expected[schemas.GOLD_RUN]} rows, expected exactly 1")

    properties = {"user": user, "password": password, "driver": DRIVER_CLASS}
    try:
        _execute(spark, jdbc_url, user, password, schemas.prepare_statements(pg_schema))
        logger.info(f"staged empty tables in schema {pg_schema}")
        for name, frame in frames.items():
            frame.select(*schemas.column_names(schemas.TABLE_COLUMNS[name])).write.jdbc(
                jdbc_url,
                f"{pg_schema}.{schemas.staging_name(name)}",
                mode="append",
                properties={**properties, "batchsize": str(WRITE_BATCH_SIZE), "numPartitions": str(WRITE_PARTITIONS)},
            )
            logger.info(f"loaded {schemas.staging_name(name)} ({expected[name]} rows expected)")

        staged = {name: _count(spark, jdbc_url, properties, pg_schema, schemas.staging_name(name)) for name in schemas.TABLES}
        mismatched = {name: (expected[name], staged[name]) for name in schemas.TABLES if expected[name] != staged[name]}
        if mismatched:
            raise PublishError(f"row counts differ between Iceberg and the staging tables (iceberg, postgres): {mismatched}")

        _execute(spark, jdbc_url, user, password, schemas.index_statements(pg_schema))
        _execute(spark, jdbc_url, user, password, schemas.swap_statements(pg_schema))
    except Exception as exc:
        _drop_staging(spark, jdbc_url, user, password, pg_schema)
        if isinstance(exc, PublishError):
            raise
        raise PublishError(f"{type(exc).__name__}: {exc}") from exc

    published = {name: _count(spark, jdbc_url, properties, pg_schema, name) for name in schemas.TABLES}
    if published != expected:
        raise PublishError(f"published row counts {published} differ from Iceberg's {expected} after the swap")
    run_row = frames[schemas.GOLD_RUN].collect()[0].asDict()
    return {
        "gold_namespace": gold_namespace,
        "pg_schema": pg_schema,
        "tables": published,
        "published_run": {key: (value.isoformat() if hasattr(value, "isoformat") else value) for key, value in run_row.items()},
        "elapsed_seconds": round(time.time() - started, 1),
    }


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Publish the gold tables to PostgreSQL (issue #99).")
    parser.add_argument("--gold-namespace", default=DEFAULT_GOLD_NAMESPACE)
    parser.add_argument("--jdbc-url", default=DEFAULT_JDBC_URL)
    parser.add_argument("--pg-user", default=DEFAULT_PG_USER)
    parser.add_argument("--pg-schema", default=DEFAULT_PG_SCHEMA)
    parser.add_argument("--summary-file", help="Also write the summary JSON to this local path")
    return parser.parse_args(argv)


def _read_gold(spark: SparkSession, namespace: str, name: str) -> Any:
    try:
        return spark.table(f"{namespace}.{name}")
    except AnalysisException as exc:
        raise PublishError(f"gold table {namespace}.{name} is missing; run silver_to_gold first") from exc


def _execute(spark: SparkSession, jdbc_url: str, user: str, password: str, statements: Sequence[str]) -> None:
    """Run statements in one transaction; all take effect or none does."""
    jvm = spark._jvm
    jvm.java.lang.Class.forName(DRIVER_CLASS)
    connection = jvm.java.sql.DriverManager.getConnection(jdbc_url, user, password)
    try:
        connection.setAutoCommit(False)
        statement = connection.createStatement()
        for sql in statements:
            statement.execute(sql)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def _drop_staging(spark: SparkSession, jdbc_url: str, user: str, password: str, pg_schema: str) -> None:
    try:
        _execute(spark, jdbc_url, user, password, schemas.cleanup_statements(pg_schema))
    except Exception as exc:  # the original failure matters more than a failed cleanup
        logger.warning(f"could not drop the staging tables: {exc}")


def _count(spark: SparkSession, jdbc_url: str, properties: dict[str, str], pg_schema: str, table: str) -> int:
    query = f'(SELECT count(*) AS n FROM "{pg_schema}"."{table}") AS counted'
    return int(spark.read.jdbc(jdbc_url, query, properties=properties).collect()[0]["n"])


if __name__ == "__main__":
    sys.exit(main())
