"""Issue #93 end-to-end proof: write and read back a table through the
Iceberg Hadoop catalog on MinIO configured in infra/spark-conf/iceberg-catalog.conf.

Run via spark-submit --properties-file infra/spark-conf/iceberg-catalog.conf
(the catalog/S3A/credential config is applied at submit time, not here).
"""

from pyspark.sql import Row, SparkSession


def main() -> None:
    spark = SparkSession.builder.appName("iceberg_smoke_test").getOrCreate()

    spark.sql("CREATE NAMESPACE IF NOT EXISTS lakehouse.smoke_test")
    spark.sql(
        "CREATE TABLE IF NOT EXISTS lakehouse.smoke_test.ping "
        "(id BIGINT, message STRING) USING iceberg"
    )

    rows = [Row(id=1, message="issue-93-smoke-test"), Row(id=2, message="iceberg-on-minio")]
    spark.createDataFrame(rows).writeTo("lakehouse.smoke_test.ping").append()

    result = spark.sql("SELECT COUNT(*) AS row_count FROM lakehouse.smoke_test.ping")
    row_count = result.collect()[0]["row_count"]
    print(f"ICEBERG_SMOKE_TEST_ROW_COUNT={row_count}")

    spark.stop()


if __name__ == "__main__":
    main()
