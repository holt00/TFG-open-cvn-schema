#!/usr/bin/env bash
# Create (or leave in place) the Superset admin user from the Secret `superset-secrets`
# (issue #100, D10). The chart's init job is told not to create it (`init.createAdmin: false`)
# so the password never enters the rendered config or the Helm release; the password travels
# over stdin, not as an argument of kubectl.
#
#   infra/superset/create_admin.sh            # namespace tfm-lakehouse, user `admin`
set -euo pipefail

NAMESPACE="${NAMESPACE:-tfm-lakehouse}"
ADMIN_USER="${ADMIN_USER:-admin}"

if kubectl exec -n "$NAMESPACE" deploy/superset -- superset fab list-users 2>/dev/null \
    | grep -q "username:${ADMIN_USER}"; then
  echo "admin user '${ADMIN_USER}' already exists"
  exit 0
fi

kubectl get secret -n "$NAMESPACE" superset-secrets -o jsonpath='{.data.admin-password}' \
  | base64 -d \
  | kubectl exec -i -n "$NAMESPACE" deploy/superset -- sh -c \
      "read -r ADMIN_PW; superset fab create-admin --username '${ADMIN_USER}' \
         --firstname Superset --lastname Admin --email admin@example.invalid \
         --password \"\$ADMIN_PW\""
