# infra

Infrastructure manifests and Helm values for the TFM lakehouse platform
(`docs/roadmap/tfm/issues/issue-89-epic-tfm-lakehouse-platform.md`).

- `k3s/`: local k3s cluster bring-up notes (issue `#90`)
- `helm-values/`: Helm values files for each service deployed onto the
  cluster, added as each issue that deploys a service is implemented
  (starting with issue `#91`, core services: MinIO, PostgreSQL, Airflow —
  see `helm-values/README.md` for the pinned versions and install/verify
  commands actually used)

This directory targets a single local k3s cluster only, per the epic's
scope decision; there is no Terraform/multi-node/cloud tooling here.
