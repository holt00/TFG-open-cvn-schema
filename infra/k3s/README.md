# k3s cluster bring-up

Local single-node k3s cluster for the TFM lakehouse platform, built under
issue `#90` (`docs/roadmap/tfm/issues/issue-90-k3s-cluster-bring-up.md`).
Environment: WSL2 (Linux), systemd enabled.

## WSL2 prerequisite

`/etc/wsl.conf` must have, then `wsl --shutdown` and reopen the shell:

```ini
[boot]
systemd=true
```

## Install

`--flannel-backend=host-gw` avoids a known VXLAN/UDP issue under WSL2's
virtualized networking; irrelevant for a single node beyond avoiding that
bug.

```bash
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="--flannel-backend=host-gw --write-kubeconfig-mode=644" sh -
```

## kubectl access

`/etc/rancher/k3s/k3s.yaml` is root-owned; `kubectl config` subcommands
that write to it (e.g. `set-context`) fail without sudo even when the file
is readable. Copy it to a user-writable location instead:

```bash
mkdir -p ~/.kube
cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
chmod 600 ~/.kube/config
export KUBECONFIG=~/.kube/config   # add to ~/.bashrc to persist
```

## Namespace

```bash
kubectl create namespace tfm-lakehouse
kubectl config set-context --current --namespace=tfm-lakehouse
```

## Helm

Installed to `~/.local/bin/helm` (no sudo required), repos added:

```bash
helm repo add apache-airflow https://airflow.apache.org
helm repo add superset https://apache.github.io/superset
helm repo update
```

MinIO and PostgreSQL (issue `#91`) are **not** added via a classic
`helm repo add bitnami ...` — `charts.bitnami.com` is OCI-only as of 2025.
Pull those charts by OCI reference instead, pinned to an exact version:

```bash
helm show chart oci://registry-1.docker.io/bitnamicharts/minio --version <pin>
helm show chart oci://registry-1.docker.io/bitnamicharts/postgresql --version <pin>
```

## Verification performed

- `kubectl get nodes` → node `Ready`
- test pod (`busybox`) scheduled, ran, completed, and was cleaned up in
  `tfm-lakehouse`
- `helm repo list` shows `apache-airflow` and `superset`
