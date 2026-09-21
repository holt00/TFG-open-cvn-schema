# Superset (issue #100)

Everything the TFM dashboard needs besides the Helm values
(`infra/helm-values/superset-values.yaml`, added by Task 4 of the issue). The decisions
behind these files are in
`docs/roadmap/tfm/issues/issue-100-superset-dashboard.md` ("Task 0 - Decisions Locked").

## Image

`Dockerfile` builds `tfm-lakehouse/superset:6.1.0-pg`: the official `apache/superset:6.1.0`
image plus `psycopg2-binary==2.9.13`. The official image is a "lean" build with no database
drivers, and Superset needs the PostgreSQL driver for its own metadata database as well as for
the connection to the gold tables, so it is baked in rather than installed at every pod start
(no internet needed at runtime). The image runs as uid 1000 (`superset`) with Python 3.10.

```bash
# build (from the repository root)
docker build -f infra/superset/Dockerfile -t tfm-lakehouse/superset:6.1.0-pg infra/superset

# import into k3s's containerd (there is no registry in this cluster); needs sudo
docker save tfm-lakehouse/superset:6.1.0-pg | sudo k3s ctr images import -

# confirm the node has it
sudo k3s ctr images ls | grep tfm-lakehouse/superset
```

The Helm values reference it with `pullPolicy: Never`, like the Spark and ingest images, so a
missing import shows up as `ErrImageNeverPull` instead of a silent pull of another image.

## Read-only role on the gold database

`gold_readonly_role.sql` creates the role `superset_ro` that Superset connects with: `CONNECT`
on database `gold`, `USAGE` on schema `gold`, `SELECT` on the tables that exist, and default
privileges `FOR ROLE gold IN SCHEMA gold GRANT SELECT ON TABLES`. Default privileges are what keep
read access across publishes: the `#99` publish job drops the published tables and renames new
staging tables into their place, and a table's own grants would go with it. The `gold` application
user cannot `CREATE ROLE`, so the script runs as the superuser `postgres`; the role's password comes
from the Secret `superset-gold-ro-credentials` (key `password`, created with `kubectl`, never in git)
and reaches the script as a psql variable. The script is idempotent.

```bash
export KUBECONFIG=~/.kube/config

# once: the role's password
kubectl create secret generic superset-gold-ro-credentials -n tfm-lakehouse \
  --from-literal=password="$(openssl rand -base64 24 | tr -d '/+=' | cut -c1-32)"

# apply (as postgres, from a throwaway pod; the script goes in through stdin)
kubectl run pg-role --rm -i --restart=Never -n tfm-lakehouse \
  --image docker.io/bitnamilegacy/postgresql:17.6.0-debian-12-r4 \
  --env PGPASSWORD="$(kubectl get secret -n tfm-lakehouse postgresql-gold-credentials -o jsonpath='{.data.postgres-password}' | base64 -d)" \
  --env RO_PW="$(kubectl get secret -n tfm-lakehouse superset-gold-ro-credentials -o jsonpath='{.data.password}' | base64 -d)" \
  --command -- sh -c 'psql -h postgresql -U postgres -d gold -v ON_ERROR_STOP=1 -v ro_password="$RO_PW" -f -' \
  < infra/superset/gold_readonly_role.sql
```

## Admin user

`create_admin.sh` creates the `admin` user (idempotent) with the password of the `admin-password` key
of `superset-secrets`, sent over stdin rather than as a `kubectl` argument. The Helm chart is told not
to create it (`init.createAdmin: false`) so the password stays out of the rendered config and the Helm
release. Run it once after the web pod is Ready.

## Dashboard as code

`assets/` is the export of the dashboard `tfm-gold-indicators` (Superset's ZIP layout, unzipped into
YAML): the database `TFM Gold`, the four datasets its charts use, the four charts and the dashboard. The
database's password is masked in an export (`XXXXXXXXXX`), so nothing secret is in git.
`import_dashboard.py` zips the folder and sends it to `POST /api/v1/dashboard/import/` (the
`superset import-dashboards` command cannot receive a database password), overwriting what exists;
`superset_client.py` is the small standard-library client it uses.

```bash
kubectl port-forward -n tfm-lakehouse svc/superset 8088:8088 &

SUPERSET_URL=http://localhost:8088 \
SUPERSET_ADMIN_PASSWORD="$(kubectl get secret -n tfm-lakehouse superset-secrets -o jsonpath='{.data.admin-password}' | base64 -d)" \
SUPERSET_GOLD_RO_PASSWORD="$(kubectl get secret -n tfm-lakehouse superset-gold-ro-credentials -o jsonpath='{.data.password}' | base64 -d)" \
python infra/superset/import_dashboard.py
```

To change the dashboard, edit it in the UI, export it (`Dashboards` -> `Export`, or
`GET /api/v1/dashboard/export/?q=!(<id>)`), replace the whole `assets/` folder with the unzipped export (its file names end in the instance's ids,
so a re-export renames files) and commit; check that no password appears in the diff. A chart must
carry its `uuid` in the dashboard layout, or Superset adds a duplicate row (the tests check it). The database connection sets `cache_timeout: -1` (no data cache), which the import
keeps.

## Screenshots

`screenshot_dashboard.py` takes a full-page screenshot with a headless Chromium (Playwright is not a
dependency of the repository; use `uvx --from playwright`, see the script's docstring).
`screenshots/dashboard_run_e2e99-2.png` and `dashboard_run_e2e100-1.png` are the dashboard before and after a
`transform_publish` run (issue #100, Task 9): the charts are the same, the provenance table shows the new run.
They contain aggregates only, no personal names.
