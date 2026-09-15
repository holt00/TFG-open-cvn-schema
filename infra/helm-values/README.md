# Helm values (issue #91)

Values files for the three core services deployed onto the `tfm-lakehouse`
k3s namespace (issue `#90`). Each file documents its own decisions and
pinned versions in a header comment; this file covers the parts common to
all three: credential handling and the install/verify commands actually
used.

See `docs/roadmap/tfm/issues/issue-91-core-services-deployment.md` for the
full decision record ("Task 0 - Decisions Locked") behind the image
sourcing and topology choices below.

## Why images are pinned to `bitnamilegacy`

Bitnami's free Helm/image catalog shrank sharply at the end of August/
September 2025 (Broadcom's "Bitnami Secure Images" transition). The two
Bitnami-chart services here (MinIO, PostgreSQL) explicitly pin every image
reference the chart uses (including secondary ones like MinIO's console/
object-browser sidecar) to `docker.io/bitnamilegacy/<image>:<exact tag>`:
frozen, unpatched, but public and pin-stable, verified pullable
anonymously at the time each chart was installed. Do not switch these back
to the chart defaults (`docker.io/bitnami/...`) without re-verifying they
still resolve; that registry's non-latest tags are being removed over
time. The Airflow chart is unaffected (official, actively maintained
chart); its bundled metadata-Postgres subchart already pins
`bitnamilegacy/postgresql` upstream, so no override was needed there.

## Credentials

Every service's credentials live in a Kubernetes Secret created ahead of
`helm install`, referenced from the values file via `auth.existingSecret`
(MinIO, PostgreSQL). Nothing is committed to git.

```bash
export KUBECONFIG=~/.kube/config

# MinIO root credentials
kubectl create secret generic minio-root-credentials \
  -n tfm-lakehouse \
  --from-literal=root-user="<choose a username>" \
  --from-literal=root-password="$(openssl rand -base64 24 | tr -d '/+=' | cut -c1-32)"

# PostgreSQL (dedicated gold-layer instance) credentials
kubectl create secret generic postgresql-gold-credentials \
  -n tfm-lakehouse \
  --from-literal=postgres-password="$(openssl rand -base64 24 | tr -d '/+=' | cut -c1-32)" \
  --from-literal=password="$(openssl rand -base64 24 | tr -d '/+=' | cut -c1-32)"
```

Airflow's own embedded metadata Postgres uses the chart's default
(unauthenticated-from-outside, plaintext `postgres` password inside the
cluster) — acceptable per the Task 0 "zero custom wiring" decision for a
local, non-internet-exposed cluster; not a pattern to reuse for anything
exposed beyond this machine.

## Install commands

```bash
export KUBECONFIG=~/.kube/config

helm install minio oci://registry-1.docker.io/bitnamicharts/minio \
  --version 17.0.21 \
  -f infra/helm-values/minio-values.yaml \
  -n tfm-lakehouse

helm install postgresql oci://registry-1.docker.io/bitnamicharts/postgresql \
  --version 18.11.3 \
  -f infra/helm-values/postgresql-values.yaml \
  -n tfm-lakehouse

helm install airflow apache-airflow/airflow \
  --version 1.22.0 \
  -f infra/helm-values/airflow-values.yaml \
  -n tfm-lakehouse
```

## Verify commands

```bash
export KUBECONFIG=~/.kube/config

# MinIO: bucket exists, object round-trip
export ROOT_USER=$(kubectl get secret -n tfm-lakehouse minio-root-credentials -o jsonpath="{.data.root-user}" | base64 -d)
export ROOT_PASSWORD=$(kubectl get secret -n tfm-lakehouse minio-root-credentials -o jsonpath="{.data.root-password}" | base64 -d)
kubectl run --namespace tfm-lakehouse minio-client-test --rm -i --restart='Never' \
  --env MINIO_SERVER_ROOT_USER="$ROOT_USER" --env MINIO_SERVER_ROOT_PASSWORD="$ROOT_PASSWORD" \
  --env MINIO_SERVER_HOST=minio \
  --image docker.io/bitnamilegacy/minio-client:2025.7.21-debian-12-r3 -- \
  bash -c 'mc alias set local http://minio:9000 $MINIO_SERVER_ROOT_USER $MINIO_SERVER_ROOT_PASSWORD && mc ls local'

# MinIO console (browser UI)
kubectl port-forward -n tfm-lakehouse svc/minio-console 9090:9090

# PostgreSQL: connect as the gold app user
export POSTGRES_PASSWORD=$(kubectl get secret -n tfm-lakehouse postgresql-gold-credentials -o jsonpath="{.data.password}" | base64 -d)
kubectl run postgresql-client-test --rm -i --restart='Never' -n tfm-lakehouse \
  --image docker.io/bitnamilegacy/postgresql:17.6.0-debian-12-r4 \
  --env PGPASSWORD="$POSTGRES_PASSWORD" \
  --command -- psql --host postgresql -U gold -d gold -p 5432 -c '\l'

# Airflow: scheduler DB health + API server UI
kubectl -n tfm-lakehouse exec deploy/airflow-scheduler -c scheduler -- airflow db check
kubectl port-forward -n tfm-lakehouse svc/airflow-api-server 8080:8080
```

Full KubernetesExecutor smoke-test procedure (spawn a real task pod, prove
scheduling end to end) is recorded in the issue document's Verification
section rather than repeated here, since it used a throwaway DAG file that
was deleted afterward — no DAGs are expected to exist in this deployment
until issue `#97`.
