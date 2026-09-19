# infra

Infrastructure manifests and Helm values for the TFM lakehouse platform
(`docs/roadmap/tfm/issues/issue-89-epic-tfm-lakehouse-platform.md`).

- `k3s/`: local k3s cluster bring-up notes (issue `#90`)
- `helm-values/`: Helm values files for each service deployed onto the
  cluster, added as each issue that deploys a service is implemented
  (starting with issue `#91`, core services: MinIO, PostgreSQL, Airflow —
  see `helm-values/README.md` for the pinned versions and install/verify
  commands actually used)
- `spark-conf/`: Iceberg Hadoop-catalog and S3A properties for Spark jobs
  (issue `#92`), plus the custom Spark image `Dockerfile` and the driver's
  RBAC manifest (`spark-rbac.yaml`, issue `#93`) — see `spark-conf/README.md`
  for the catalog/warehouse layout, the pinned Spark/Iceberg/hadoop-aws/
  aws-java-sdk-bundle versions, and the image build/import commands

This directory targets a single local k3s cluster only, per the epic's
scope decision; there is no Terraform/multi-node/cloud tooling here.

Airflow DAG sources are tracked separately under `dags/` at the repo root
(delivered to the `dag-processor` pod's DAGs PVC — see issue `#93`), not
under `infra/`, since they are pipeline code rather than deployment
config.
