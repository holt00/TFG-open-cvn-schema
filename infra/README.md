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
- `ingest/`: `Dockerfile` and README for the `tfm-lakehouse/ingest` image that
  runs the `ingest_validate` DAG's tasks (issue `#97`): Python 3.14 plus the
  project dependencies only; the code, schema and data are mounted from the
  checkout with hostPath — see `ingest/README.md`
- `spark-conf/Dockerfile.silver` and `spark-conf/requirements-silver.txt`: the
  Spark image extended with pydantic, jsonschema and requests, so the
  bronze -> silver job (issue `#98`) can run the repository's own code on the
  Spark image's Python 3.10 — see `spark-conf/README.md`, "Silver image"
- `spark-conf/Dockerfile.gold`: the silver image plus the PostgreSQL JDBC driver,
  so the job that publishes gold to the dedicated PostgreSQL (issue `#99`) can
  write over JDBC and swap tables in one transaction — see
  `spark-conf/README.md`, "Gold image"

This directory targets a single local k3s cluster only, per the epic's
scope decision; there is no Terraform/multi-node/cloud tooling here.

Airflow DAG sources are tracked separately under `dags/` at the repo root
(delivered to the `dag-processor` pod's DAGs PVC — see issues `#93`, `#97`, `#98` and `#99`), not
under `infra/`, since they are pipeline code rather than deployment
config.
