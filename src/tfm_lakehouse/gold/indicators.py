"""The gold indicators, as DataFrame transformations over the silver tables (issue #99).

Every function takes and returns Spark DataFrames and uses only native Spark
functions (no Python UDFs), so the work stays in the JVM. The module needs PySpark and
is only imported inside the Spark image; ``build_gold`` is what the job calls and what
the image tests exercise on small hand-built silver tables.

Silver keys publications and affiliations by ``record_id``, not by entity, so every
indicator joins through ``entity_link``. One real person can report the same work
through several records (a CVN and an ORCID record), so publications are first
deduplicated per entity (decision D3).
"""

from __future__ import annotations

from dataclasses import dataclass

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from tfm_lakehouse.gold import schemas

MIN_YEAR = 1900
DEFAULT_MAX_ENTITIES_PER_DOI = 200

KIND_EMPLOYMENT = "employment"


@dataclass
class GoldBuild:
    """The gold tables built from silver, plus what the run summary needs.

    Args:
        tables: DataFrames keyed by the names of ``schemas.TABLES`` except ``gold_run``
            (the job builds that one, because it needs the silver snapshot ids).
        distinct_publications: The per-entity deduplicated publications.
        dois_excluded: How many DOIs were left out of the collaboration pairs because
            more entities reported them than the guard allows.
    """

    tables: dict[str, DataFrame]
    distinct_publications: DataFrame
    dois_excluded: int


def publication_key() -> F.Column:
    """The identity of a work within one entity: its DOI, else a hash of title and year."""
    year_text = F.coalesce(F.col("year").cast("string"), F.lit(""))
    return F.coalesce(
        F.concat(F.lit("doi:"), F.col("doi")),
        F.concat(F.lit("title:"), F.sha1(F.col("title_norm")), F.lit("/"), year_text),
    )


def distinct_publications(publication: DataFrame, entity_link: DataFrame, max_year: int) -> DataFrame:
    """Return one row per ``(entity_id, pub_key)``: the works an entity reported, once each.

    The year is the minimum usable year among the copies (usable: between ``MIN_YEAR``
    and ``max_year``); it is null when no copy has one, and such works are still real
    works, so they count everywhere except in the per-year indicator.

    Args:
        publication: ``silver.publication``.
        entity_link: ``silver.entity_link`` (``record_id`` -> ``entity_id``).
        max_year: Highest year accepted as a publication year.

    Returns:
        A frame with ``entity_id``, ``pub_key``, ``doi`` and ``year``.
    """
    usable_year = F.when(F.col("year").between(MIN_YEAR, max_year), F.col("year"))
    return (
        publication.join(entity_link.select("record_id", "entity_id"), "record_id")
        .withColumn("pub_key", publication_key())
        .where(F.col("pub_key").isNotNull())
        .groupBy("entity_id", "pub_key")
        .agg(F.max("doi").alias("doi"), F.min(usable_year).alias("year"))
    )


def publications_per_researcher_year(distinct: DataFrame) -> DataFrame:
    """Indicator I1: distinct publications per entity and year (works without a usable year excluded)."""
    return (
        distinct.where(F.col("year").isNotNull())
        .groupBy("entity_id", "year")
        .agg(F.count("*").cast("int").alias("publication_count"))
    )


def affiliation_timeline(affiliation: DataFrame, entity_link: DataFrame) -> DataFrame:
    """Indicator I3: one row per entity, kind, organization and start year.

    Records of the same entity that report the same stay are merged: the end year is the
    latest known one (a record that lacks it does not erase another's), the organization
    and role are the alphabetically first non-null ones, which is arbitrary but
    deterministic. Stays without a start year are kept, merged per organization.
    """
    return (
        affiliation.join(entity_link.select("record_id", "entity_id"), "record_id")
        .groupBy("entity_id", "kind", "organization_norm", "start_year")
        .agg(
            F.min("organization").alias("organization"),
            F.min("role").alias("role"),
            F.max("end_year").alias("end_year"),
        )
        .select(*schemas.column_names(schemas.TABLE_COLUMNS[schemas.AFFILIATION_TIMELINE]))
    )


def collaboration_pairs(
    distinct: DataFrame, entity: DataFrame, max_entities_per_doi: int = DEFAULT_MAX_ENTITIES_PER_DOI
) -> tuple[DataFrame, DataFrame]:
    """Indicator I2: pairs of distinct entities that report the same DOI.

    Silver has no co-author entities (ORCID work summaries carry no author list), so a
    shared DOI is the only honest signal; it is a lower bound of collaboration. Pairs
    are stored once, ``entity_a < entity_b``.

    Args:
        distinct: The output of ``distinct_publications``.
        entity: ``silver.entity`` (for ``has_cvn``).
        max_entities_per_doi: DOIs reported by more entities than this are left out,
            because their pairs grow quadratically (a consortium paper); they are
            returned so the run can report them.

    Returns:
        The pairs, and the DOIs left out.
    """
    with_doi = distinct.where(F.col("doi").isNotNull()).select("entity_id", "doi", "year")
    reporters = with_doi.groupBy("doi").agg(F.count("*").alias("entities"))
    excluded = reporters.where(F.col("entities") > max_entities_per_doi).select("doi")
    shared = reporters.where((F.col("entities") > 1) & (F.col("entities") <= max_entities_per_doi)).select("doi")
    candidates = with_doi.join(shared, "doi")
    left, right = candidates.alias("a"), candidates.alias("b")
    pairs = (
        left.join(right, (F.col("a.doi") == F.col("b.doi")) & (F.col("a.entity_id") < F.col("b.entity_id")))
        .select(
            F.col("a.entity_id").alias("entity_a"),
            F.col("b.entity_id").alias("entity_b"),
            F.col("a.doi").alias("doi"),
            F.least(F.col("a.year"), F.col("b.year")).alias("year"),
        )
        .groupBy("entity_a", "entity_b")
        .agg(
            F.countDistinct("doi").cast("int").alias("shared_publications"),
            F.min("year").alias("first_year"),
            F.max("year").alias("last_year"),
        )
    )
    cvn = entity.select("entity_id", "has_cvn")
    flagged = (
        pairs.join(cvn.select(F.col("entity_id").alias("entity_a"), F.col("has_cvn").alias("a_cvn")), "entity_a")
        .join(cvn.select(F.col("entity_id").alias("entity_b"), F.col("has_cvn").alias("b_cvn")), "entity_b")
        .withColumn("has_cvn_member", F.coalesce(F.col("a_cvn"), F.lit(False)) | F.coalesce(F.col("b_cvn"), F.lit(False)))
    )
    columns = schemas.column_names(schemas.TABLE_COLUMNS[schemas.COLLABORATION_PAIRS])
    return flagged.select(*columns), excluded


def dim_researcher(entity: DataFrame, distinct: DataFrame, timeline: DataFrame) -> DataFrame:
    """The researcher dimension: who each entity is, and its headline figures.

    ``career_*`` come from employment stays only and use known years only (a stay
    without an end year is not extended to today), so ``career_span_years`` is null when
    no employment has a start year, and a lower bound otherwise.
    """
    publications = distinct.groupBy("entity_id").agg(
        F.count("*").cast("int").alias("publication_count"),
        F.min("year").alias("first_publication_year"),
        F.max("year").alias("last_publication_year"),
    )
    organizations = timeline.groupBy("entity_id").agg(F.countDistinct("organization_norm").cast("int").alias("organization_count"))
    career = (
        timeline.where(F.col("kind") == KIND_EMPLOYMENT)
        .groupBy("entity_id")
        .agg(
            F.min("start_year").alias("career_start_year"),
            F.max(F.greatest(F.col("start_year"), F.col("end_year"))).alias("career_last_year"),
        )
    )
    joined = (
        entity.join(publications, "entity_id", "left")
        .join(organizations, "entity_id", "left")
        .join(career, "entity_id", "left")
    )
    result = joined.select(
        "entity_id",
        "given_names",
        "family_name",
        F.concat_ws(" ", F.col("given_names"), F.col("family_name")).alias("display_name"),
        "orcid_id",
        F.array_join(F.sort_array(F.col("sources")), ",").alias("sources"),
        "has_cvn",
        "has_orcid",
        "record_count",
        F.coalesce(F.col("publication_count"), F.lit(0)).alias("publication_count"),
        "first_publication_year",
        "last_publication_year",
        F.coalesce(F.col("organization_count"), F.lit(0)).alias("organization_count"),
        "career_start_year",
        "career_last_year",
        F.when(
            F.col("career_start_year").isNotNull() & F.col("career_last_year").isNotNull(),
            F.col("career_last_year") - F.col("career_start_year"),
        ).alias("career_span_years"),
    )
    return _conform(result, schemas.DIM_RESEARCHER)


def build_gold(
    *,
    entity: DataFrame,
    entity_link: DataFrame,
    publication: DataFrame,
    affiliation: DataFrame,
    max_year: int,
    max_entities_per_doi: int = DEFAULT_MAX_ENTITIES_PER_DOI,
) -> GoldBuild:
    """Build every gold table except ``gold_run`` from the silver tables.

    Args:
        entity: ``silver.entity``.
        entity_link: ``silver.entity_link``.
        publication: ``silver.publication``.
        affiliation: ``silver.affiliation``.
        max_year: Highest year accepted as a publication year (the run's year plus one).
        max_entities_per_doi: Guard of ``collaboration_pairs``.
    """
    distinct = distinct_publications(publication, entity_link, max_year)
    timeline = affiliation_timeline(affiliation, entity_link)
    pairs, excluded = collaboration_pairs(distinct, entity, max_entities_per_doi)
    tables = {
        schemas.DIM_RESEARCHER: dim_researcher(entity, distinct, timeline),
        schemas.PUBLICATIONS_PER_RESEARCHER_YEAR: _conform(
            publications_per_researcher_year(distinct), schemas.PUBLICATIONS_PER_RESEARCHER_YEAR
        ),
        schemas.AFFILIATION_TIMELINE: _conform(timeline, schemas.AFFILIATION_TIMELINE),
        schemas.COLLABORATION_PAIRS: _conform(pairs, schemas.COLLABORATION_PAIRS),
    }
    return GoldBuild(tables=tables, distinct_publications=distinct, dois_excluded=int(excluded.count()))


def _conform(frame: DataFrame, table: str) -> DataFrame:
    """Select and cast the frame to exactly the columns of a gold table."""
    return frame.select(*[F.col(name).cast(type_.lower()).alias(name) for name, type_ in schemas.TABLE_COLUMNS[table]])
