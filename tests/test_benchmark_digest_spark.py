"""The content digest of issue #101 (decision D9), run in local-mode Spark inside the Spark image.

Skipped when Docker or the image is not available.
"""

import json

import pytest
from spark_image import GOLD_IMAGE, image_available, run_in_image

pytestmark = pytest.mark.skipif(not image_available(GOLD_IMAGE), reason=f"needs docker and the {GOLD_IMAGE} image")


@pytest.fixture(scope="module")
def digests(tmp_path_factory):
    work = tmp_path_factory.mktemp("digest")
    command = (
        "export PYTHONPATH=/repo/src:/repo/tests PYSPARK_PYTHON=python3; exec /opt/spark/bin/spark-submit --master local[2] "
        "--conf spark.ui.enabled=false /repo/tests/spark_digest_runner.py"
    )
    completed = run_in_image(["bash", "-c", command], {work: "/work"}, image=GOLD_IMAGE)
    assert completed.returncode == 0, completed.stdout[-3000:] + completed.stderr[-3000:]
    return json.loads((work / "output.json").read_text(encoding="utf-8"))


def test_the_digest_does_not_depend_on_row_order_or_partitioning(digests):
    assert digests["reordered"] == digests["base"]
    assert digests["base"]["rows"] == 4


def test_the_digest_changes_when_a_value_changes_or_a_row_is_added(digests):
    assert digests["changed"]["rows"] == 4 and digests["changed"]["digest"] != digests["base"]["digest"]
    assert digests["extra"]["rows"] == 5 and digests["extra"]["digest"] != digests["base"]["digest"]


def test_an_empty_table_has_zero_rows_and_a_digest_of_zero(digests):
    assert digests["empty"] == {"rows": 0, "digest": "0"}


def test_the_cli_survives_a_table_that_does_not_exist_at_all(digests):
    """A run that OOM'd before writing anything leaves no table, not merely an empty one; the
    digest job (as the benchmark campaign runs it) must record that as data, not crash (D24)."""
    assert digests["cli_exit_code"] == 0
    assert digests["cli_digests"]["present"]["exists"] is True and digests["cli_digests"]["present"]["rows"] == 4
    assert digests["cli_digests"]["absent"] == {"rows": 0, "digest": "0", "exists": False}
