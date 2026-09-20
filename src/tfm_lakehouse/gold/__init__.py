"""Silver -> gold logic of the TFM lakehouse (issue #99).

Everything in this package runs inside the Spark image's Python 3.10 (see
``infra/spark-conf/Dockerfile.gold``), so it must stay 3.10 compatible: no
``datetime.UTC``, ``StrEnum`` or ``tomllib``, and no import of
``tfm_lakehouse.bronze``. ``schemas`` is pure and testable on the host;
``indicators`` builds Spark DataFrames and needs PySpark, so it is only
imported inside the image.
"""
