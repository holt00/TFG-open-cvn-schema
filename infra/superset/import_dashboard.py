"""Import the versioned TFM dashboard bundle into a running Superset (issue #100, Task 7).

The bundle in ``infra/superset/assets/`` is the export of the dashboard (database, datasets, charts and
dashboard as YAML). A database's password is masked in an export, and the ``superset
import-dashboards`` command cannot receive one, so the bundle is zipped here and sent to the REST
endpoint ``/api/v1/dashboard/import/``, which takes the password in its ``passwords`` field.

Environment:
    SUPERSET_URL: Superset root URL (default ``http://localhost:8088``, a ``kubectl port-forward``).
    SUPERSET_ADMIN_USER: admin user (default ``admin``).
    SUPERSET_ADMIN_PASSWORD: its password (key ``admin-password`` of the Secret ``superset-secrets``).
    SUPERSET_GOLD_RO_PASSWORD: password of ``superset_ro`` (Secret ``superset-gold-ro-credentials``).
"""

from __future__ import annotations

import io
import json
import logging
import os
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from superset_client import SupersetClient  # noqa: E402

logger = logging.getLogger(__name__)

ASSETS_DIR = Path(__file__).resolve().parent / "assets"
BUNDLE_ROOT = "tfm_gold_dashboard"
DATABASE_FILE = "databases/TFM_Gold.yaml"


def build_bundle(assets_dir: Path = ASSETS_DIR) -> bytes:
    """Zip the exported assets under one root folder, the layout Superset's importer expects.

    Args:
        assets_dir: Folder holding ``metadata.yaml`` and the exported subfolders.

    Returns:
        The ZIP file's bytes.
    """
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as bundle:
        for path in sorted(assets_dir.rglob("*")):
            if path.is_file():
                bundle.write(path, f"{BUNDLE_ROOT}/{path.relative_to(assets_dir).as_posix()}")
    return buffer.getvalue()


def main() -> int:
    """Import the bundle, overwriting assets that already exist.

    Returns:
        Process exit code.
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    client = SupersetClient(
        os.environ.get("SUPERSET_URL", "http://localhost:8088"),
        os.environ.get("SUPERSET_ADMIN_USER", "admin"),
        os.environ["SUPERSET_ADMIN_PASSWORD"],
    )
    passwords = {DATABASE_FILE: os.environ["SUPERSET_GOLD_RO_PASSWORD"]}
    result = client.upload(
        "/api/v1/dashboard/import/",
        "formData",
        "tfm_gold_dashboard.zip",
        build_bundle(),
        {"passwords": json.dumps(passwords), "overwrite": "true"},
    )
    logger.info(f"import answered: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
