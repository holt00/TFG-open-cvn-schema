# Custom layer on top of the upstream Spark docker-image-tool.sh base image
# (issue #93, Task 0/4). Build context is the repo root:
#   docker build -f infra/spark-conf/Dockerfile \
#     -t tfm-lakehouse/spark-py:3.5.9-iceberg1.11.0 .
#
# Adds the three Iceberg/S3A jars pinned and verified in this directory's
# README.md, plus the Iceberg catalog properties file and the issue #93
# smoke-test job, baked in rather than mounted (see README.md's "Smoke-test
# script delivery" decision).

FROM tfm-lakehouse/spark-py:3.5.9-iceberg1.11.0-base

USER root

RUN curl -fSL -o /opt/spark/jars/iceberg-spark-runtime-3.5_2.12-1.11.0.jar \
      https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.5_2.12/1.11.0/iceberg-spark-runtime-3.5_2.12-1.11.0.jar \
 && curl -fSL -o /opt/spark/jars/hadoop-aws-3.3.4.jar \
      https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar \
 && curl -fSL -o /opt/spark/jars/aws-java-sdk-bundle-1.12.262.jar \
      https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar

COPY infra/spark-conf/iceberg-catalog.conf /opt/spark/conf/iceberg-catalog.conf
COPY src/tfm_lakehouse/jobs/iceberg_smoke_test.py /opt/spark/jobs/iceberg_smoke_test.py

USER 185
