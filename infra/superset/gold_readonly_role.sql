-- Read-only role for Superset on the gold database (issue #100, D4).
--
-- Run as the PostgreSQL superuser (the `gold` application user cannot CREATE ROLE, issue #100
-- Task 1.4), with the new role's password passed as a psql variable so it never appears in git:
--
--   psql -h postgresql -U postgres -d gold -v ON_ERROR_STOP=1 \
--        -v ro_password="$SUPERSET_RO_PASSWORD" -f gold_readonly_role.sql
--
-- Idempotent: safe to run again (creates the role once, otherwise only resets its password).
--
-- Why default privileges: the publish job of issue #99 drops the published tables and renames
-- freshly created staging tables into their place on every run, and a table's own grants go with
-- it. Default privileges declared FOR ROLE gold apply to every table that `gold` creates in
-- schema gold from now on, staging tables included, so read access survives each publish.

SELECT NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'superset_ro') AS create_role \gset
\if :create_role
  CREATE ROLE superset_ro LOGIN;
\endif

ALTER ROLE superset_ro WITH LOGIN PASSWORD :'ro_password'
  NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION;

GRANT CONNECT ON DATABASE gold TO superset_ro;
GRANT USAGE ON SCHEMA gold TO superset_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA gold TO superset_ro;
ALTER DEFAULT PRIVILEGES FOR ROLE gold IN SCHEMA gold GRANT SELECT ON TABLES TO superset_ro;
