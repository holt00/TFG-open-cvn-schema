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

### Research Findings (2026-09-15, informing the detailed plan below)

- **WSL2 execution environment**: this machine runs the repository inside
  WSL2 (Linux 6.6, WSL2). k3s needs systemd; WSL2 does not enable it by
  default. Fix: `systemd=true` under `[boot]` in `/etc/wsl.conf`, then
  `wsl --shutdown` from the Windows host and a shell restart, before
  installing k3s.
- **CNI on WSL2**: flannel's default VXLAN backend has known UDP handling
  problems under WSL2's virtualized networking (upstream WSL issue
  `#4150`). Since this is a single-node local cluster, install k3s with
  `--flannel-backend=host-gw` instead of the default VXLAN backend to avoid
  the issue entirely.
- **Bitnami Helm repository is deprecated as a classic repo**: as of 2025,
  `charts.bitnami.com` is OCI-only (the legacy index now 302-redirects to
  Broadcom's hosting). `helm repo add bitnami https://charts.bitnami.com/bitnami`
  is stale guidance. MinIO and PostgreSQL charts must instead be pulled by
  OCI reference (e.g. `oci://registry-1.docker.io/bitnamicharts/minio`,
  `oci://registry-1.docker.io/bitnamicharts/postgresql`), pinned to an exact
  chart version at install time. This issue documents the pattern; the
  actual pull/pin happens in issue `#91`, which consumes it.
- **Official Airflow chart repo**: `helm repo add apache-airflow https://airflow.apache.org`.
- **Official Superset chart repo**: `helm repo add superset https://apache.github.io/superset`.

### Task Tracking Convention

Work on this issue proceeds task by task (T1-T9 below), some with
subtasks. For each task/subtask in progress, this session reports, in
order: (1) a short summary of what that task/subtask is about to do, (2)
the work itself, (3) whether any file needs to be modified by the user
(per the user's standing instruction, the user applies file edits
themselves, especially code/config, unless told otherwise), and (4) the
next task/subtask to move to. Progress against this list is what gets
folded into "Adjustments Made During Implementation" and "Implementation
Performed" as work actually happens.

### Detailed Execution Plan

- **T1. WSL2 prep**
  - check/set `systemd=true` in `/etc/wsl.conf`; restart WSL
    (`wsl --shutdown`, user-side action since it targets the Windows host,
    not a file inside the repo)
  - verify with `systemctl is-system-running`
- **T2. Install k3s**
  - `curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="--flannel-backend=host-gw --write-kubeconfig-mode=644" sh -`
  - verify with `sudo k3s kubectl get nodes` -> `Ready`
- **T3. kubectl access**
  - export kubeconfig to `~/.kube/config`, install standalone `kubectl` if
    missing
  - verify plain `kubectl get nodes` works without `sudo`/`k3s` prefix
- **T4. Namespace**
  - `kubectl create namespace tfm-lakehouse`
  - set it as the current context's default namespace
- **T5. Helm install + repos**
  - install `helm` binary if missing
  - `helm repo add apache-airflow https://airflow.apache.org`
  - `helm repo add superset https://apache.github.io/superset`
  - no classic repo add for Bitnami (see Research Findings); record the OCI
    pull pattern for issue `#91` to consume
  - `helm repo update`
- **T6. Smoke test**
  - run a trivial test pod in `tfm-lakehouse`, confirm it schedules and
    completes/runs, then clean it up
- **T7. Repo layout for infra**
  - create `infra/` with `infra/k3s/` (install notes/scripts) and
    `infra/helm-values/` (later issues' Helm values land here), plus a
    short `infra/README.md` orientation stub
  - no Terraform, per the epic's local-only decision
- **T8. Documentation update** (per `AGENTS.md` / documentation
  conventions' mandatory update protocol)
  - this issue file: fill Adjustments/Implementation Performed/
    Verification/Findings/Status
  - `docs/context/tfm/current_status.md`: new dated entry
  - `docs/roadmap/tfm/tfm_roadmap.md`: status row for `#90`
  - `docs/pipeline/known_limitations.md`: only if a new limitation
    surfaces during execution
- **T9. Final verification pass**
  - `kubectl get nodes` -> `Ready`
  - test pod completed successfully in `tfm-lakehouse`
  - `helm repo list` shows `apache-airflow` and `superset`
  - OCI pull path for the Bitnami charts documented for issue `#91`

Tasks run T1 through T9 in order; each gates the next.

## Adjustments Made During Implementation

- **kubeconfig write access**: `/etc/rancher/k3s/k3s.yaml` is root-owned;
  even with `--write-kubeconfig-mode=644` (readable), `kubectl config
  set-context` still fails writing to it without sudo (it needs a
  `.lock` file next to it). Fix: copy the file to `~/.kube/config`
  (`chmod 600`) and use that as `KUBECONFIG` going forward, instead of
  editing the root-owned original in place. Documented in
  `infra/k3s/README.md`.
- **`sudo` requires a password interactively** in this environment and no
  password was available to the session; the user ran the k3s install
  command (`T2`) directly rather than the session running it via `sudo`.
  Every other task (`T1`, `T3`-`T9`) was run by the session without sudo.
- **Helm installed without sudo**: the official `get-helm-3` install
  script installs to `/usr/local/bin` via `sudo` internally. Installed the
  binary manually instead, to `~/.local/bin/helm` (no root needed),
  `PATH` updated in `~/.bashrc`. Resolved to Helm **v4.3.0** (latest
  stable at execution time, newer than the v3.x assumed during planning);
  `helm repo add`/`helm repo update` syntax used is unchanged between the
  two major versions.
- Env vars (`KUBECONFIG`, `PATH`) do not persist across separate shell
  tool invocations in this session's execution environment; every command
  after `T3` explicitly set `KUBECONFIG=~/.kube/config` inline rather than
  relying on an exported variable surviving between commands.

## Implementation Performed

All of `T1`-`T9` from the Detailed Execution Plan above, in order:

- `T1`: `systemd=true` set in `/etc/wsl.conf` by the user; WSL restarted;
  `systemctl is-system-running` returned `running`.
- `T2`: k3s `v1.36.4+k3s1` installed by the user via the documented
  `INSTALL_K3S_EXEC="--flannel-backend=host-gw --write-kubeconfig-mode=644"`
  command; installed as a systemd service, enabled and started.
- `T3`: kubeconfig copied to `~/.kube/config` (see Adjustments); plain
  `kubectl` (symlinked to the `k3s` binary by the installer) confirmed
  working.
- `T4`: `tfm-lakehouse` namespace created; set as the current context's
  default namespace.
- `T5`: `helm` v4.3.0 installed to `~/.local/bin`; `apache-airflow`
  (`https://airflow.apache.org`) and `superset`
  (`https://apache.github.io/superset`) repos added and updated; no
  classic Bitnami repo added (OCI pull pattern documented instead, for
  issue `#91`).
- `T6`: a `busybox` smoke-test pod was run in `tfm-lakehouse`, reached
  `Completed`, printed its expected log line, and was deleted.
- `T7`: `infra/` created with `infra/README.md`, `infra/k3s/README.md`
  (full install/access/verification notes for this issue), and
  `infra/helm-values/` (empty, placeholder for issue `#91` onward).
- `T8`: this section plus Verification/Findings/Status below, and the
  companion updates to `docs/context/tfm/current_status.md` and
  `docs/roadmap/tfm/tfm_roadmap.md`. No new entry needed in
  `docs/pipeline/known_limitations.md` (see Known Limitations below).
- `T9`: final verification pass, see Verification below.

## Verification

All executed and passing:

- `kubectl get nodes` -> one node, `STATUS Ready` (`desktop-cqjr96e`,
  `v1.36.4+k3s1`)
- smoke-test `busybox` pod in `tfm-lakehouse`: scheduled, ran to
  `Completed`, log output matched expected string, pod cleaned up
  afterward
- `helm repo list` shows `apache-airflow` and `superset` with their
  correct URLs
- `kubectl get ns tfm-lakehouse` -> `Active`
- current context's default namespace confirmed as `tfm-lakehouse`
  (`kubectl config view --minify`)

## Findings

- k3s's default kubeconfig write mode is read-only-safe but not
  write-safe for non-root users; any workflow that needs `kubectl config`
  mutations (not just reads) needs the user-owned copy from the start,
  not just a permissive file mode on the root-owned original.
- The Bitnami classic Helm repository being OCI-only now is a real
  planning trap: the epic's own wording ("add the Bitnami repo") no
  longer maps to a working command. Anyone resuming this work from the
  epic text alone, without this issue's research findings, would hit a
  dead repository URL.
- Helm's current stable major version is v4, not v3; no behavioral impact
  found for the commands used here, but worth flagging for issue `#91`
  in case any v3-specific chart values or CLI flags are assumed there.

## Known Limitations

Per the epic, this is a local single-machine cluster only;
multi-node/cloud deployment is out of scope and documented as future
work. No new limitation beyond what the epic already scopes was found
during this issue; the kubeconfig/Bitnami-OCI points above are
implementation adjustments, not standing limitations, so they are not
duplicated into `docs/pipeline/known_limitations.md`.

## Impact On Future Issues

Issue `#91` (Core Services Deployment) deploys MinIO, PostgreSQL, and
Airflow onto the cluster and namespace created here, and must use the
OCI-based pull pattern for the Bitnami MinIO/PostgreSQL charts documented
in `infra/k3s/README.md` and this issue's Research Findings, rather than
a classic `helm repo add bitnami ...` step.

## Status

`Completed`
