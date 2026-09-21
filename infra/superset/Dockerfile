# Superset image for the issue #100 dashboard: the official lean image plus the
# PostgreSQL driver. Build:
#   docker build -f infra/superset/Dockerfile -t tfm-lakehouse/superset:6.1.0-pg infra/superset
#
# apache/superset:6.1.0 is a "lean" build with no database drivers (Superset 6.1.0
# Docker builds documentation), and Superset needs psycopg2 twice: for its own
# metadata database and for the connection to the gold PostgreSQL (issue #99).
# The driver is baked in instead of installed in the chart's bootstrapScript on
# every pod start, so nothing needs the internet at runtime (issue #100, D2).
# psycopg2-binary 2.9.13 was the latest release with a cp310 manylinux wheel when
# the issue was planned; the image's venv runs Python 3.10.

FROM apache/superset:6.1.0

USER root

RUN . /app/.venv/bin/activate && uv pip install psycopg2-binary==2.9.13

USER superset
