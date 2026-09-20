"""Bronze -> silver logic of the TFM lakehouse (issue #98).

Everything in this package runs inside the Spark image's Python 3.10 (see
``infra/spark-conf/Dockerfile.silver``), so it must stay 3.10 compatible: no
``datetime.UTC``, ``StrEnum`` or ``tomllib``, and no import of
``tfm_lakehouse.bronze`` (whose envelope module uses ``datetime.UTC``). The
functions here are pure and testable on the host without Spark.
"""
