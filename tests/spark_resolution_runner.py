"""Runs ``resolve_entities`` in local-mode Spark inside the Spark image (issue #98 parity test).

Not a test module: ``tests/test_silver_resolution_spark.py`` mounts and executes
it in a container. Reads ``/work/input.json`` (persons and affiliations), writes
``/work/output.json`` (links and entities).
"""

import json

from pyspark.sql import SparkSession

from tfm_lakehouse.silver.resolution_spark import resolve_entities

PERSON_DDL = (
    "record_id STRING, source STRING, orcid_id STRING, given_names STRING, family_name STRING, "
    "given_norm STRING, family_norm STRING, family_key STRING, given_initial STRING, source_last_modified STRING"
)
AFFILIATION_DDL = "record_id STRING, organization_norm STRING"


def main() -> None:
    spark = (
        SparkSession.builder.master("local[2]")
        .appName("issue98_resolution_parity")
        .config("spark.ui.enabled", "false")
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.driver.host", "127.0.0.1")
        .getOrCreate()
    )
    data = json.load(open("/work/input.json", encoding="utf-8"))
    persons = spark.createDataFrame(
        [tuple(row[name.split()[0]] for name in PERSON_DDL.split(", ")) for row in data["persons"]], PERSON_DDL
    )
    affiliations = spark.createDataFrame(
        [(row["record_id"], row["organization_norm"]) for row in data["affiliations"]], AFFILIATION_DDL
    )
    links, entities = resolve_entities(persons, affiliations, data["org_threshold"])
    output = {
        "links": [row.asDict() for row in links.collect()],
        "entities": [row.asDict() for row in entities.collect()],
    }
    json.dump(output, open("/work/output.json", "w", encoding="utf-8"), ensure_ascii=False)
    spark.stop()


if __name__ == "__main__":
    main()
