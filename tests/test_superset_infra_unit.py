"""The Superset deployment and dashboard files of issue #100, checked on the host with no network.

Covers the image, the Helm values (pinned versions, no literal secrets), the read-only role's SQL, the
exported dashboard bundle (a drift guard against ``tfm_lakehouse.gold.schemas``, so a renamed gold
column fails here and not in front of a dashboard), and the two provisioning scripts.

The exported YAML is read with regular expressions rather than a YAML parser: PyYAML is not a
dependency of the repository, and the bundle is machine-generated in one stable shape. Running the
deployment itself is done in the cluster (issue #100, Tasks 4, 7 and 9).
"""

import importlib.util
import io
import json
import re
import zipfile
from pathlib import Path

import pytest

from tfm_lakehouse.gold import schemas

ROOT = Path(__file__).resolve().parents[1]
SUPERSET = ROOT / "infra" / "superset"
ASSETS = SUPERSET / "assets"
VALUES = ROOT / "infra" / "helm-values" / "superset-values.yaml"
HELM_README = ROOT / "infra" / "helm-values" / "README.md"

CHART_VERSION = "0.22.8"
MASKED_PASSWORD = "XXXXXXXXXX"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _scalar(text: str, key: str) -> str:
    match = re.search(rf"(?m)^{re.escape(key)}:[ \t]*(.*?)[ \t]*$", text)
    assert match, f"no top-level '{key}' in the file"
    return match.group(1)


def _block_list(text: str, key: str) -> list[str]:
    """Items of a block list (``key:`` then ``- item`` lines), or [] for ``key: []``."""
    match = re.search(rf"(?m)^([ \t]*){re.escape(key)}:[ \t]*(\[\])?[ \t]*\n((?:\1- .*\n)*)", text)
    if not match:
        return []
    return [line.strip()[2:] for line in match.group(3).splitlines() if line.strip().startswith("- ")]


def _dataset_files() -> list[Path]:
    return sorted((ASSETS / "datasets").rglob("*.yaml"))


def _chart_files() -> list[Path]:
    return sorted((ASSETS / "charts").glob("*.yaml"))


def _dataset_columns(text: str) -> list[str]:
    columns = text.split("\ncolumns:\n", 1)[1]
    return re.findall(r"(?m)^- column_name: (\S+)$", columns)


# --- image ------------------------------------------------------------------------------------------


def test_dockerfile_pins_the_base_image_and_the_driver_and_runs_unprivileged():
    dockerfile = _text(SUPERSET / "Dockerfile")

    assert re.search(r"(?m)^FROM apache/superset:6\.1\.0$", dockerfile)
    assert re.search(r"psycopg2-binary==\d+\.\d+\.\d+", dockerfile)
    assert dockerfile.rstrip().splitlines()[-1] == "USER superset"


# --- Helm values ------------------------------------------------------------------------------------


def test_values_use_the_own_image_that_is_never_pulled():
    values = _text(VALUES)

    assert re.search(r"(?m)^  repository: tfm-lakehouse/superset$", values)
    assert re.search(r"(?m)^  tag: 6\.1\.0-pg$", values)
    assert re.search(r"(?m)^  pullPolicy: Never$", values)


def test_values_take_every_secret_from_the_secret_and_write_none_in_the_file():
    values = _text(VALUES)

    for env_name in ("SUPERSET_SECRET_KEY", "DB_PASS"):
        assert re.search(rf"name: {env_name}\n\s+valueFrom:\n\s+secretKeyRef:\n\s+name: superset-secrets", values)
    assert re.search(r"(?m)^    existingSecret: superset-secrets$", values)
    # no credential written as a value: only key *names* (adminPasswordKey...) may mention passwords
    literal = re.findall(r"(?mi)^\s*(?:password|secretKey|secret_key|adminPassword)\s*:\s*\S+", values)
    assert literal == []
    code = "\n".join(line for line in values.splitlines() if not line.lstrip().startswith("#"))
    assert "admin/admin" not in code  # the header comment may name the default it overrides
    assert re.search(r"(?m)^  createAdmin: false$", values)


def test_values_keep_the_worker_off_and_the_metadata_database_separate():
    values = _text(VALUES)

    assert re.search(r"(?m)^    replicaCount: 0$", values)
    assert re.search(r"(?m)^  enabled: true$", values)  # the chart's own PostgreSQL subchart (D3)


def test_the_chart_version_is_pinned_where_it_is_installed_and_documented():
    assert CHART_VERSION in _text(VALUES)
    readme = _text(HELM_README)
    assert f"--version {CHART_VERSION}" in readme
    assert "--timeout 15m" in readme  # the first PostgreSQL boot outlasts Helm's default 5 minutes


# --- read-only role ---------------------------------------------------------------------------------


def test_the_role_script_grants_only_read_access_that_survives_a_publish():
    sql = _text(SUPERSET / "gold_readonly_role.sql")

    assert "ALTER DEFAULT PRIVILEGES FOR ROLE gold IN SCHEMA gold GRANT SELECT ON TABLES TO superset_ro;" in sql
    assert "GRANT USAGE ON SCHEMA gold TO superset_ro;" in sql
    assert "NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION" in sql
    assert not re.search(r"(?i)GRANT\s+(INSERT|UPDATE|DELETE|TRUNCATE|ALL|CREATE)\b", sql)


def test_the_role_script_takes_its_password_from_a_psql_variable():
    sql = _text(SUPERSET / "gold_readonly_role.sql")

    assert ":'ro_password'" in sql
    assert not re.search(r"(?i)PASSWORD\s+'", sql)  # never a literal


# --- exported bundle --------------------------------------------------------------------------------


def test_the_bundle_has_one_database_four_charts_and_a_dashboard():
    assert len(list((ASSETS / "databases").glob("*.yaml"))) == 1
    assert len(_chart_files()) == 4
    assert len(list((ASSETS / "dashboards").glob("*.yaml"))) == 1
    assert (ASSETS / "metadata.yaml").is_file()


def test_the_database_connection_is_read_only_uncached_and_holds_no_password():
    database = _text(ASSETS / "databases" / "TFM_Gold.yaml")

    assert _scalar(database, "cache_timeout") == "-1"  # D11: a new publish must show up
    assert _scalar(database, "allow_dml") == "false"
    uri = _scalar(database, "sqlalchemy_uri")
    assert uri.startswith("postgresql+psycopg2://superset_ro:")
    assert re.fullmatch(r"postgresql\+psycopg2://superset_ro:XXXXXXXXXX@[^/\s]+/gold", uri)


def test_no_file_in_the_bundle_carries_a_credential():
    for path in ASSETS.rglob("*"):
        if path.is_file():
            for password in re.findall(r"://[^:@/\s]+:([^@\s]+)@", _text(path)):
                assert password == MASKED_PASSWORD, path


@pytest.mark.parametrize("path", _dataset_files(), ids=lambda p: p.name)
def test_each_dataset_is_a_gold_table_with_exactly_its_columns(path: Path):
    text = _text(path)
    table = _scalar(text, "table_name")

    assert _scalar(text, "schema") == "gold"
    assert table in schemas.TABLES
    exported = _dataset_columns(text)  # Superset orders the columns its own way
    assert len(exported) == len(set(exported))
    assert sorted(exported) == sorted(schemas.column_names(schemas.TABLE_COLUMNS[table]))


def test_every_dataset_belongs_to_the_bundles_database():
    database_uuid = _scalar(_text(ASSETS / "databases" / "TFM_Gold.yaml"), "uuid")

    for path in _dataset_files():
        assert _scalar(_text(path), "database_uuid") == database_uuid, path.name


@pytest.mark.parametrize("path", _chart_files(), ids=lambda p: p.name)
def test_each_chart_uses_only_columns_that_exist_in_its_dataset(path: Path):
    datasets = {_scalar(_text(p), "uuid"): _text(p) for p in _dataset_files()}
    chart = _text(path)
    dataset = datasets[_scalar(chart, "dataset_uuid")]
    available = set(_dataset_columns(dataset))
    params = chart.split("\nparams:\n", 1)[1].split("\nquery_context:", 1)[0]

    used = set(_block_list(params, "groupby")) | set(_block_list(params, "all_columns"))
    used |= set(re.findall(r"(?m)^\s+subject: (\S+)$", params))
    used |= set(re.findall(r"(?m)^\s+column_name: (\S+)$", params))
    used |= set(re.findall(r"(?m)^\s+x_axis: (\S+)$", params))

    assert used, "the chart references no column at all"
    assert used <= available, f"{path.name}: {sorted(used - available)} not in {sorted(available)}"


def test_every_chart_sits_on_the_dashboard_and_the_layout_has_no_stray_row():
    dashboard = _text(next((ASSETS / "dashboards").glob("*.yaml")))
    chart_uuids = {_scalar(_text(p), "uuid") for p in _chart_files()}

    assert _scalar(dashboard, "slug") == "tfm-gold-indicators"
    assert _scalar(dashboard, "published") == "true"
    placed = set(re.findall(r"(?m)^\s+uuid: ([0-9a-f-]{36})$", dashboard))
    assert chart_uuids <= placed  # a chart missing its uuid is not recognised as placed
    assert "ROW-N-" not in dashboard  # Superset adds such a row for charts it thinks are unplaced
    assert len(re.findall(r"(?m)^  CHART-\S+:$", dashboard)) == len(chart_uuids)


def test_the_dashboard_names_no_person():
    # D12: aggregates only. dim_researcher (names) is not part of the bundle and no chart selects a name column
    assert not any("dim_researcher" in p.name for p in _dataset_files())
    for path in _chart_files():
        assert not re.search(r"display_name|given_names|family_name", _text(path)), path.name


# --- provisioning scripts ---------------------------------------------------------------------------


def test_the_import_script_zips_the_bundle_under_one_root_folder():
    module = _load_module("import_dashboard", SUPERSET / "import_dashboard.py")

    names = zipfile.ZipFile(io.BytesIO(module.build_bundle())).namelist()

    assert all(name.startswith(f"{module.BUNDLE_ROOT}/") for name in names)
    assert f"{module.BUNDLE_ROOT}/metadata.yaml" in names
    assert f"{module.BUNDLE_ROOT}/{module.DATABASE_FILE}" in names
    assert (ASSETS / module.DATABASE_FILE).is_file()


class _FakeResponse:
    def __init__(self, body: bytes) -> None:
        self._body = body

    def read(self) -> bytes:
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *exc) -> None:
        return None


class _FakeOpener:
    def __init__(self) -> None:
        self.requests = []

    def open(self, request, timeout=None):
        self.requests.append(request)
        return _FakeResponse(b'{"message": "OK"}')


def test_the_client_sends_the_bundle_as_multipart_with_its_token_and_csrf_headers():
    module = _load_module("superset_client", SUPERSET / "superset_client.py")
    client = module.SupersetClient.__new__(module.SupersetClient)
    client._base_url = "http://superset.test"
    client._token = "jwt-token"
    client._csrf = "csrf-token"
    client._opener = _FakeOpener()

    answer = client.upload(
        "/api/v1/dashboard/import/", "formData", "bundle.zip", b"ZIPBYTES", {"passwords": json.dumps({"a": "b"})}
    )

    request = client._opener.requests[0]
    body = request.data.decode("latin-1")
    assert answer == {"message": "OK"}
    assert request.full_url == "http://superset.test/api/v1/dashboard/import/"
    assert request.get_header("Authorization") == "Bearer jwt-token"
    assert request.get_header("X-csrftoken") == "csrf-token"
    assert request.get_header("Content-type").startswith("multipart/form-data; boundary=")
    assert 'name="passwords"' in body and 'name="formData"; filename="bundle.zip"' in body and "ZIPBYTES" in body


def test_the_client_reports_the_status_and_body_of_an_api_error():
    module = _load_module("superset_client", SUPERSET / "superset_client.py")
    import urllib.error

    class _Failing:
        def open(self, request, timeout=None):
            raise urllib.error.HTTPError(request.full_url, 422, "Unprocessable", {}, io.BytesIO(b'{"errors": "bad"}'))

    client = module.SupersetClient.__new__(module.SupersetClient)
    client._base_url, client._token, client._csrf, client._opener = "http://s", "t", "c", _Failing()

    with pytest.raises(module.SupersetApiError, match="422.*bad"):
        client.get("/api/v1/dashboard/")
