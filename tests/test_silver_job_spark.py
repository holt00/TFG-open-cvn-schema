"""The bronze -> silver job end to end, in local-mode Spark inside the Spark image (issue #98).

Runs the real ``spark_jobs/bronze_to_silver.py`` against a small bronze tree in
the layout issue #97 lands (Hive-style partitions, JSON Lines envelopes) and a
local Iceberg Hadoop catalog. Skipped when Docker or the image is not available.
"""

import json
from pathlib import Path

import pytest
from silver_fixtures import envelope, orcid_api_record, orcid_id, orcid_xml, synthetic_document
from spark_image import IMAGE, image_available, run_in_image

pytestmark = pytest.mark.skipif(not image_available(), reason=f"needs docker and the {IMAGE} image")

A, B, C = orcid_id(1), orcid_id(2), orcid_id(3)


def _write(bronze: Path, source: str, run_id: str, date: str, envelopes: list, extra_lines: list[str] = ()) -> None:
    directory = bronze / f"source={source}" / f"ingestion_date={date}" / f"run_id={run_id}"
    directory.mkdir(parents=True)
    lines = [json.dumps(item, ensure_ascii=False) for item in envelopes] + list(extra_lines)
    (directory / "part-00000.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (directory / "_manifest.json").write_text("{}", encoding="utf-8")


def _bronze(tmp_path: Path) -> Path:
    bronze = tmp_path / "bronze"
    _write(
        bronze, "orcid_bulk", "run-1", "2026-09-19",
        [
            envelope("orcid_bulk", A, orcid_xml(A, "Ana", "García López")),
            envelope("orcid_bulk", B, orcid_xml(B, "Berta", "Ruiz")),
            envelope("orcid_bulk", C, orcid_xml(C, "Carla", "Pérez")),
            envelope("orcid_bulk", "BAD", orcid_xml("0000-0000-0000-0000")),
        ],
    )
    _write(bronze, "orcid_api", "run-1", "2026-09-19", [envelope("orcid_api", A, orcid_api_record(A, "Ana", "García López"))])
    invalid = synthetic_document(A)
    invalid["curriculum"]["identity"]["campo_inventado"] = 1
    _write(
        bronze, "synthetic_cvn", "run-1", "2026-09-19",
        [
            envelope("synthetic_cvn", "doc1", synthetic_document(A, given="Ana", family="García López")),
            envelope("synthetic_cvn", "doc2", synthetic_document(C, include_orcid=False, given="C.", family="Pérez")),
            envelope("synthetic_cvn", "doc3", synthetic_document(C, include_orcid=False, given="Zoe", family="Nadie")),
            envelope("synthetic_cvn", "invalid", invalid),
        ],
    )
    # The same document landed again by a later run: only this copy must survive.
    _write(
        bronze, "synthetic_cvn", "run-2", "2026-09-20",
        [envelope("synthetic_cvn", "doc1", synthetic_document(A, given="Ana", family="García López"), landed_at="2026-09-20T10:00:00Z", run_id="run-2")],
    )
    return bronze


def _submit(tmp_path: Path, bronze: Path, *job_args: str):
    work = tmp_path / "work"
    work.mkdir(exist_ok=True)
    work.chmod(0o777)  # the container's user (185) is not the host user
    command = (
        "export PYTHONPATH=/repo/src PYSPARK_PYTHON=python3; exec /opt/spark/bin/spark-submit --master local[2] "
        "--conf spark.ui.enabled=false --conf spark.sql.catalog.lakehouse=org.apache.iceberg.spark.SparkCatalog "
        "--conf spark.sql.catalog.lakehouse.type=hadoop --conf spark.sql.catalog.lakehouse.warehouse=file:///work/warehouse "
        "--conf spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions "
        "--conf spark.executorEnv.PYTHONPATH=/repo/src /repo/src/tfm_lakehouse/spark_jobs/bronze_to_silver.py "
        "--bronze-root file:///bronze --summary-file /work/summary.json --shuffle-partitions 4 " + " ".join(job_args)
    )
    completed = run_in_image(["bash", "-c", command], {bronze: "/bronze:ro", work: "/work"})
    return completed, work


def _manifest(work: Path) -> None:
    rows = [
        {"document_id": "doc1", "seed_orcid_id": A, "linkage": "orcid_id", "name_variant": "exact"},
        {"document_id": "doc2", "seed_orcid_id": C, "linkage": "name_affiliation", "name_variant": "given_initial"},
        {"document_id": "doc3", "seed_orcid_id": orcid_id(9), "linkage": "name_affiliation", "name_variant": "exact"},
    ]
    work.mkdir(exist_ok=True)
    (work / "manifest.jsonl").write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


def test_job_validates_deduplicates_resolves_and_writes_the_six_tables(tmp_path):
    _manifest(tmp_path / "work")

    completed, work = _submit(tmp_path, _bronze(tmp_path), "--rejection-threshold 0.5", "--manifest /work/manifest.jsonl")

    assert completed.returncode == 0, completed.stdout[-3000:] + completed.stderr[-3000:]
    summary = json.loads((work / "summary.json").read_text(encoding="utf-8"))

    sources = summary["sources"]
    assert (sources["synthetic_cvn"]["read"], sources["synthetic_cvn"]["deduplicated"], sources["synthetic_cvn"]["duplicates_dropped"]) == (5, 4, 1)
    assert (sources["synthetic_cvn"]["valid"], sources["synthetic_cvn"]["rejected"]) == (3, 1)
    assert (sources["orcid_bulk"]["read"], sources["orcid_bulk"]["valid"], sources["orcid_bulk"]["rejected"]) == (4, 3, 1)
    assert (sources["orcid_api"]["deduplicated"], sources["orcid_api"]["rejected"]) == (1, 0)
    assert summary["rejected_by_rule"] == {"orcid_bulk": {"orcid_id_checksum": 1}, "synthetic_cvn": {"cvn_entity_schema": 1}}

    # 7 valid persons (3 bulk + 1 API + 3 CVN) in 4 entities: A (bulk, API, doc1), B, C (bulk + doc2), and doc3 alone.
    tables = summary["tables"]
    assert (tables["person_record"], tables["rejected"], tables["entity_link"], tables["entity"]) == (7, 2, 7, 4)
    assert tables["affiliation"] > 0 and tables["publication"] > 0
    assert summary["resolution"]["links_by_rule"] == {"orcid_id": 5, "name_affiliation": 1, "singleton": 1}
    assert summary["resolution"]["entities_fusing_cvn_and_orcid"] == 2
    assert (summary["resolution"]["ambiguous"], summary["resolution"]["name_conflict"]) == (0, 0)

    evaluation = summary["evaluation"]
    assert evaluation["declared_orcid_id"]["correct"] == 1
    named = evaluation["name_affiliation"]
    # doc2 is found by name (its seed is in silver); doc3's seed is not, and it correctly stays alone.
    assert (named["evaluable"], named["merged"], named["correct_merges"], named["false_merges"]) == (1, 1, 1, 0)
    assert (named["precision"], named["recall"]) == (1.0, 1.0)


def test_job_writes_nothing_when_a_source_exceeds_the_rejection_threshold(tmp_path):
    completed, work = _submit(tmp_path, _bronze(tmp_path), "--rejection-threshold 0.1")

    assert completed.returncode == 1
    assert "above the 10.00% threshold" in completed.stdout + completed.stderr
    assert not (work / "summary.json").exists()
    assert not (work / "warehouse" / "silver").exists()


def test_job_fails_when_there_is_no_bronze_data(tmp_path):
    empty = tmp_path / "bronze"
    empty.mkdir()

    completed, _ = _submit(tmp_path, empty)

    assert completed.returncode == 1
    assert "no bronze data found" in completed.stdout + completed.stderr
