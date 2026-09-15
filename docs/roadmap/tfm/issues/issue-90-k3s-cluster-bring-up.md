# Issue 90 - k3s Cluster Bring-Up

## Summary

Stand up the local k3s Kubernetes cluster that every other TFM component
runs on. First issue of the TFM epic (`docs/roadmap/tfm/issues/issue-89-epic-tfm-lakehouse-platform.md`,
phase 0).

## Original Goal

Have a working local k3s cluster, with a dedicated namespace and the Helm
repositories needed by later issues, ready for service deployment.

## Original Plan

- install k3s on the local machine
- create a dedicated namespace for the TFM lakehouse (e.g. `tfm-lakehouse`)
- add and configure the Helm repositories required by later issues: Bitnami
  (MinIO, PostgreSQL), the official Airflow chart, the official Superset
  chart
- verify `kubectl` access and basic pod scheduling in the namespace (a
  trivial test pod)
- decide and record the repository layout for infra manifests/Helm values
  (proposed in the epic as `infra/`)

## Adjustments Made During Implementation

Not applicable yet; no implementation has started.

## Implementation Performed

Not applicable yet; no implementation has started.

## Verification

Planned: `kubectl get nodes` shows the node `Ready`; a test pod runs
successfully to completion in the dedicated namespace. Not yet executed.

## Findings

Not applicable yet.

## Known Limitations

Not applicable yet. Per the epic, this is a local single-machine cluster
only; multi-node/cloud deployment is out of scope and documented as future
work.

## Impact On Future Issues

Issue `#91` (Core Services Deployment) deploys MinIO, PostgreSQL, and
Airflow onto the cluster and namespace created here.

## Status

`Planned`
