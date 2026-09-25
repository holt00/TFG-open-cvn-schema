"""Spark performance benchmark of the TFM lakehouse (issue #101).

``data`` prepares the isolated bronze data of each scale, ``runner`` launches one measured
Spark job on the cluster, ``eventlog`` reads a run's Spark event log, and ``report`` turns the
run records into the tables and charts of the memoria.
"""
