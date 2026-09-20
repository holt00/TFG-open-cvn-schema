"""Guards for the Spark-side code, which runs on the Spark image's Python 3.10 (issue #98, D2).

The host runs Python 3.14 and PySpark cannot be installed on it, so the one
failure the host tests cannot show is a 3.11+ construct in code the Spark job
imports. These checks catch the syntax and the well-known names statically;
the real run in the Spark image (issue #98, Task 8) catches the rest.
"""

import ast
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
# Everything the bronze -> silver and silver -> gold jobs import, directly or transitively.
SPARK_SIDE = [
    *sorted((SRC / "open_cvn").glob("*.py")),
    *sorted((SRC / "tfm_lakehouse" / "silver").glob("*.py")),
    *sorted((SRC / "tfm_lakehouse" / "gold").glob("*.py")),
    *sorted((SRC / "tfm_lakehouse" / "orcid_client").glob("*.py")),
    *sorted((SRC / "tfm_lakehouse" / "spark_jobs").glob("*.py")),
    SRC / "tfm_lakehouse" / "__init__.py",
    SRC / "tfm_lakehouse" / "cvn_validation.py",
    *sorted((SRC / "tfm_lakehouse" / "synthetic_cvn").glob("*.py")),
]
# Silver code must not depend on these: they need a newer Python than the Spark image's.
FORBIDDEN_IMPORTS = {"tomllib", "tfm_lakehouse.bronze"}
FORBIDDEN_FROM_IMPORTS = {("datetime", "UTC"), ("enum", "StrEnum"), ("typing", "override")}


def _id(path: Path) -> str:
    return str(path.relative_to(SRC))


@pytest.mark.parametrize("path", SPARK_SIDE, ids=_id)
def test_spark_side_modules_parse_as_python_3_10(path):
    ast.parse(path.read_text(encoding="utf-8"), filename=str(path), feature_version=(3, 10))


@pytest.mark.parametrize("path", [p for p in SPARK_SIDE if "silver" in p.parts or "gold" in p.parts or p.name == "cvn_validation.py"], ids=_id)
def test_silver_and_gold_modules_avoid_names_newer_than_python_3_10(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert not {alias.name for alias in node.names} & FORBIDDEN_IMPORTS, f"{_id(path)} imports {node.names}"
        if isinstance(node, ast.ImportFrom):
            assert node.module not in FORBIDDEN_IMPORTS and not (node.module or "").startswith("tfm_lakehouse.bronze")
            for alias in node.names:
                assert (node.module, alias.name) not in FORBIDDEN_FROM_IMPORTS, f"{_id(path)}: {node.module}.{alias.name}"
        if isinstance(node, ast.Attribute) and node.attr == "UTC" and isinstance(node.value, ast.Name) and node.value.id == "datetime":
            pytest.fail(f"{_id(path)} uses datetime.UTC")
