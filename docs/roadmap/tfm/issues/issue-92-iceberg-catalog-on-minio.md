# Issue 92 - Iceberg Catalog On MinIO

## Summary

Configure a Hadoop path-based Iceberg catalog rooted on the MinIO bucket
from issue `#91`. First issue of TFM epic phase 1
(`docs/roadmap/tfm/issues/issue-89-epic-tfm-lakehouse-platform.md`).

## Original Goal

Have a working Iceberg catalog, reachable from Spark, with no separate
catalog service (Hive Metastore/REST/Nessie) to deploy or debug, per the
epic's technology stack decision record.

## Original Plan

- decide and create the warehouse path/bucket layout (bronze/silver/gold
  prefixes)
- configure the Iceberg catalog as `type=hadoop`, `warehouse=s3a://...`,
  pointed at the MinIO bucket from issue `#91`
- configure the S3A filesystem settings needed to reach MinIO
  (`fs.s3a.endpoint`, path-style access, credentials)
- gather and pin the required jars: `iceberg-spark-runtime`, `hadoop-aws`,
  `aws-java-sdk-bundle` (exact versions matched to the Spark version chosen
  in issue `#93`)

## Adjustments Made During Implementation

Not applicable yet; no implementation has started.

## Implementation Performed

Not applicable yet; no implementation has started.

## Verification

Planned: verified together with issue `#93`'s end-to-end test (a table
written and read back through this catalog configuration). Not yet
executed.

## Findings

Not applicable yet.

## Known Limitations

Not applicable yet. Per the epic, a Hive Metastore, REST catalog, or Nessie
versioned catalog are explicitly deferred to future work.

## Impact On Future Issues

Issue `#93` (Spark Job Execution From Airflow) proves this catalog
configuration works end-to-end. Every later Spark job (issues `#98`, `#99`,
`#101`) depends on this catalog being correctly configured.

## Status

`Planned`
