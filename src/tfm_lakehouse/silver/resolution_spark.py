"""The entity resolution rules of ``resolution.py`` as Spark DataFrame operations (issue #98, D7).

Same rules, same comparison functions (``names_compatible``,
``best_org_similarity``), expressed as joins so they run distributed. The
in-memory resolver is this module's oracle: ``tests/test_silver_resolution_spark.py``
runs both on the same data and compares their output.

Runs only inside the Spark image (Python 3.10, PySpark 3.5); it is not imported
on the host.
"""

from __future__ import annotations

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F
from pyspark.sql import types as T

from tfm_lakehouse.silver.resolution import (
    DEFAULT_ORG_THRESHOLD,
    RULE_NAME_AFFILIATION,
    RULE_ORCID_ID,
    RULE_SINGLETON,
    SOURCE_CVN,
    best_org_similarity,
    name_match_kind,
    names_compatible,
)

_MAX_LISTED_CANDIDATES = 5
_PERSON_COLUMNS = (
    "record_id",
    "source",
    "orcid_id",
    "given_names",
    "family_name",
    "given_norm",
    "family_norm",
    "family_key",
    "given_initial",
    "source_last_modified",
)


def _names_compatible(given_a, family_a, given_b, family_b):
    if None in (given_a, family_a, given_b, family_b):
        return False
    return names_compatible(given_a, family_a, given_b, family_b)


def _name_match_kind(given_a, family_a, given_b, family_b):
    if None in (given_a, family_a, given_b, family_b):
        return None
    return name_match_kind(given_a, family_a, given_b, family_b)


def _best_org_similarity(organizations_a, organizations_b):
    return float(best_org_similarity(organizations_a or [], organizations_b or []))


_names_compatible_udf = F.udf(_names_compatible, T.BooleanType())
_name_match_kind_udf = F.udf(_name_match_kind, T.StringType())
_best_org_similarity_udf = F.udf(_best_org_similarity, T.DoubleType())


def resolve_entities(
    persons: DataFrame,
    affiliations: DataFrame,
    org_threshold: float = DEFAULT_ORG_THRESHOLD,
) -> tuple[DataFrame, DataFrame]:
    """Resolve every person record to an entity.

    Args:
        persons: ``person_record`` rows (the columns of ``schemas.TABLE_COLUMNS``).
        affiliations: ``affiliation`` rows.
        org_threshold: Minimum organization similarity for rule R2.

    Returns:
        ``(entity_link, entity)`` DataFrames with the columns of the matching
        silver tables.
    """
    persons = persons.select(*_PERSON_COLUMNS)
    organizations = (
        affiliations.where(F.col("organization_norm") != "")
        .groupBy("record_id")
        .agg(F.collect_set("organization_norm").alias("orgs"))
    )
    with_orgs = persons.join(organizations, "record_id", "left").withColumn(
        "orgs", F.coalesce(F.col("orgs"), F.array().cast("array<string>"))
    )

    anchored = with_orgs.where(F.col("orcid_id").isNotNull()).withColumn(
        "entity_id", F.concat(F.lit("orcid:"), F.col("orcid_id"))
    )
    unlinked = with_orgs.where(F.col("orcid_id").isNull())

    links = _links_by_orcid_id(anchored).unionByName(_links_without_id(unlinked, anchored, org_threshold))
    return links, _entities(persons, links)


def _links_by_orcid_id(anchored: DataFrame) -> DataFrame:
    orcid_members = anchored.where(F.col("source") != SOURCE_CVN).select(
        "entity_id", F.col("given_norm").alias("o_given"), F.col("family_norm").alias("o_family")
    )
    conflicts = (
        anchored.where(F.col("source") == SOURCE_CVN)
        .select("record_id", "entity_id", "given_norm", "family_norm")
        .join(orcid_members, "entity_id", "left")
        .groupBy("record_id")
        .agg(
            F.count("o_given").alias("orcid_members"),
            F.max(
                F.when(_names_compatible_udf("given_norm", "family_norm", "o_given", "o_family"), 1).otherwise(0)
            ).alias("any_compatible"),
        )
    )
    return (
        anchored.join(conflicts, "record_id", "left")
        .select(
            "record_id",
            "source",
            "entity_id",
            F.lit(RULE_ORCID_ID).alias("match_rule"),
            F.to_json(F.struct(F.col("orcid_id"))).alias("evidence"),
            F.lit(False).alias("ambiguous"),
            ((F.coalesce(F.col("orcid_members"), F.lit(0)) > 0) & (F.coalesce(F.col("any_compatible"), F.lit(0)) == 0)).alias(
                "name_conflict"
            ),
        )
    )


def _links_without_id(unlinked: DataFrame, anchored: DataFrame, org_threshold: float) -> DataFrame:
    entity_orgs = anchored.groupBy("entity_id").agg(
        F.array_distinct(F.flatten(F.collect_list("orgs"))).alias("entity_orgs")
    )
    members = anchored.select(
        "entity_id",
        F.col("record_id").alias("member_record_id"),
        F.col("given_norm").alias("m_given"),
        F.col("family_norm").alias("m_family"),
        F.col("family_key").alias("m_key"),
        F.col("given_initial").alias("m_initial"),
    )
    candidates = (
        unlinked.select(
            F.col("record_id").alias("u_record_id"),
            F.col("given_norm").alias("u_given"),
            F.col("family_norm").alias("u_family"),
            F.col("family_key").alias("u_key"),
            F.col("given_initial").alias("u_initial"),
            F.col("orgs").alias("u_orgs"),
        )
        .join(members, (F.col("u_key") == F.col("m_key")) & (F.col("u_initial") == F.col("m_initial")))
        .withColumn("name_match", _name_match_kind_udf("u_given", "u_family", "m_given", "m_family"))
        .where(F.col("name_match").isNotNull())
        .join(entity_orgs, "entity_id")
        .withColumn("similarity", _best_org_similarity_udf("u_orgs", "entity_orgs"))
        .withColumn("shared", F.size(F.array_intersect("u_orgs", "entity_orgs")))
        .where((F.col("similarity") > 0.0) & (F.col("similarity") >= F.lit(org_threshold)))
    )
    decisions = (
        candidates.groupBy("u_record_id", "entity_id")
        .agg(
            F.min(F.struct("member_record_id", "name_match")).alias("member"),
            F.max("similarity").alias("similarity"),
            F.max("shared").alias("shared"),
        )
        .groupBy("u_record_id")
        .agg(
            F.count("*").alias("n"),
            F.sort_array(F.collect_list("entity_id")).alias("entity_ids"),
            F.min("member").alias("member"),
            F.max("similarity").alias("similarity"),
            F.max("shared").alias("shared"),
        )
    )

    joined = unlinked.select("record_id", "source").join(
        decisions, F.col("record_id") == F.col("u_record_id"), "left"
    )
    matched = F.col("n") == 1
    ambiguous = F.coalesce(F.col("n"), F.lit(0)) > 1
    singleton_id = F.concat(F.lit("rec:"), F.sha1(F.col("record_id")))
    return joined.select(
        "record_id",
        "source",
        F.when(matched, F.col("entity_ids")[0]).otherwise(singleton_id).alias("entity_id"),
        F.when(matched, F.lit(RULE_NAME_AFFILIATION)).otherwise(F.lit(RULE_SINGLETON)).alias("match_rule"),
        F.when(
            matched,
            F.to_json(
                F.struct(
                    F.lit(1).alias("candidates"),
                    F.col("member.member_record_id").alias("matched_record_id"),
                    F.col("member.name_match").alias("name_match"),
                    F.round(F.col("similarity"), 4).alias("org_similarity"),
                    F.col("shared").alias("shared_organizations"),
                )
            ),
        )
        .when(ambiguous, F.to_json(F.struct(F.slice(F.col("entity_ids"), 1, _MAX_LISTED_CANDIDATES).alias("candidates"))))
        .otherwise(F.lit("{}"))
        .alias("evidence"),
        ambiguous.alias("ambiguous"),
        F.lit(False).alias("name_conflict"),
    )


def _entities(persons: DataFrame, links: DataFrame) -> DataFrame:
    priority = (
        F.when(F.col("source") == "orcid_api", 0)
        .when(F.col("source") == "orcid_bulk", 1)
        .when(F.col("source") == SOURCE_CVN, 2)
        .otherwise(3)
    )
    ranking = Window.partitionBy("entity_id").orderBy(
        priority.asc(), F.col("source_last_modified").desc_nulls_last(), F.col("record_id").asc()
    )
    display = (
        links.select("record_id", "entity_id")
        .join(persons.select("record_id", "source", "given_names", "family_name", "source_last_modified"), "record_id")
        .withColumn("rank", F.row_number().over(ranking))
        .where(F.col("rank") == 1)
        .select("entity_id", "given_names", "family_name")
    )
    aggregates = links.groupBy("entity_id").agg(
        F.count("*").cast("int").alias("record_count"),
        F.sort_array(F.collect_set("source")).alias("sources"),
        F.sort_array(F.collect_set("match_rule")).alias("rules"),
    )
    return aggregates.join(display, "entity_id").select(
        "entity_id",
        F.when(F.col("entity_id").startswith("orcid:"), F.expr("substring(entity_id, 7)")).alias("orcid_id"),
        "given_names",
        "family_name",
        "record_count",
        "sources",
        "rules",
        F.array_contains(F.col("sources"), SOURCE_CVN).alias("has_cvn"),
        F.exists(F.col("sources"), lambda source: source != F.lit(SOURCE_CVN)).alias("has_orcid"),
    )
