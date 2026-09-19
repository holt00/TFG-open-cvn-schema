import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
import requests

from bronze_fakes import FakeS3
from tfm_lakehouse.bronze import tasks
from tfm_lakehouse.bronze.envelope import SOURCE_ORCID_API, SOURCE_ORCID_BULK, SOURCE_SYNTHETIC_CVN, RunContext
from tfm_lakehouse.bronze.exceptions import (
    BronzeLandingError,
    BronzeRejectionThresholdError,
    BronzeSourceNotReadyError,
)
from tfm_lakehouse.orcid_bulk.pipeline import OrcidBulkSubsetResult
from tfm_lakehouse.orcid_client import OrcidApiError, OrcidNotFoundError

BUCKET = "lakehouse"
SUBSET_SIZE = 12
_NAMESPACES = " ".join(
    f'xmlns:{prefix}="http://www.orcid.org/ns/{name}"'
    for prefix, name in (
        ("record", "record"),
        ("common", "common"),
        ("personal", "personal-details"),
        ("person", "person"),
        ("employment", "employment"),
        ("activities", "activities"),
    )
)


def _orcid_id(number: int) -> str:
    digits = f"{number:015d}"
    total = 0
    for digit in digits:
        total = (total + int(digit)) * 2
    check_value = (12 - total % 11) % 11
    full = digits + ("X" if check_value == 10 else str(check_value))
    return "-".join(full[i : i + 4] for i in range(0, 16, 4))


def _xml(orcid_id: str, *, family: str | None = "García") -> bytes:
    family_xml = f"<personal:family-name>{family}</personal:family-name>" if family else ""
    return (
        f'<?xml version="1.0" encoding="UTF-8"?><record:record {_NAMESPACES}>'
        f"<common:orcid-identifier><common:path>{orcid_id}</common:path></common:orcid-identifier>"
        f"<person:person><person:name><personal:given-names>Ana</personal:given-names>{family_xml}"
        "</person:name></person:person><activities:activities-summary><employment:employment-summary>"
        "<common:role-title>Profesora</common:role-title>"
        "<common:start-date><common:year>2015</common:year><common:month>09</common:month></common:start-date>"
        "<common:organization><common:name>Universidad de Ejemplo</common:name><common:address>"
        "<common:city>Madrid</common:city><common:country>ES</common:country></common:address></common:organization>"
        "</employment:employment-summary></activities:activities-summary></record:record>"
    ).encode()


def _build_subset(data_dir: Path, *, bad_family_for: tuple[int, ...] = ()) -> list[str]:
    subset = data_dir / "orcid_bulk" / "filtered"
    ids = []
    for number in range(1, SUBSET_SIZE + 1):
        orcid_id = _orcid_id(number)
        ids.append(orcid_id)
        bucket = subset / f"{number % 3:03d}"
        bucket.mkdir(parents=True, exist_ok=True)
        family = None if number in bad_family_for else "García"
        (bucket / f"{orcid_id}.xml").write_bytes(_xml(orcid_id, family=family))
    return ids


@pytest.fixture
def data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(tasks, "ISSUE_95_EXPECTED_MATCHES", SUBSET_SIZE)
    return tmp_path / "data"


@pytest.fixture(autouse=True)
def _no_real_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(tasks, "API_MIN_INTERVAL_SECONDS", 0.0)


class FakeOrcidClient:
    def __init__(
        self,
        missing: frozenset[str] = frozenset(),
        broken: frozenset[str] = frozenset(),
        timing_out: frozenset[str] = frozenset(),
    ) -> None:
        self.requested: list[str] = []
        self._missing = missing
        self._broken = broken
        self._timing_out = timing_out

    def get_record(self, orcid_id: str) -> dict:
        self.requested.append(orcid_id)
        if orcid_id in self._missing:
            raise OrcidNotFoundError("not found", status_code=404, body="")
        if orcid_id in self._broken:
            raise OrcidApiError("boom", status_code=500, body="")
        if orcid_id in self._timing_out:
            raise requests.ConnectionError("timed out")
        return {"orcid-identifier": {"path": orcid_id}, "person": {"name": {"given-names": {"value": "Ana"}}}}


def _run(run_id: str = "manual__1") -> RunContext:
    return RunContext.create(run_id, now=datetime(2026, 9, 19, 12, 0, tzinfo=UTC))


def _prepare_run(data_dir: Path, run: RunContext, *, count: int = 10, bad_family_for: tuple[int, ...] = ()) -> list[str]:
    ids = _build_subset(data_dir, bad_family_for=bad_family_for)
    tasks.ensure_orcid_subset(data_dir)
    tasks.run_synthetic_cvn(run, data_dir, count=count, seed=7, orcid_link_ratio=1.0)
    return ids


def _all_lines(s3: FakeS3, prefix: str) -> list[dict]:
    return [
        json.loads(line)
        for key in sorted(s3.objects)
        if key.startswith(prefix) and key.endswith(".jsonl")
        for line in s3.objects[key].decode().splitlines()
    ]


# --- 4.1 ORCID bulk subset --------------------------------------------------


def test_a_complete_subset_without_a_marker_is_adopted_and_then_skipped(data_dir):
    _build_subset(data_dir)

    first = tasks.ensure_orcid_subset(data_dir)
    second = tasks.ensure_orcid_subset(data_dir)

    assert first["action"] == "adopted"
    assert first["matched"] == SUBSET_SIZE
    assert second["action"] == "skipped"
    assert (data_dir / "orcid_bulk" / "_subset_complete.json").is_file()


def test_the_marker_is_not_inside_the_directory_the_seed_pool_lists(data_dir):
    _build_subset(data_dir)
    tasks.ensure_orcid_subset(data_dir)

    assert all(child.is_dir() for child in (data_dir / "orcid_bulk" / "filtered").iterdir())


def test_a_partial_subset_is_never_adopted(data_dir):
    _build_subset(data_dir)
    next((data_dir / "orcid_bulk" / "filtered").glob("*/*.xml")).unlink()

    with pytest.raises(BronzeSourceNotReadyError, match="no archive"):
        tasks.ensure_orcid_subset(data_dir)
    assert not (data_dir / "orcid_bulk" / "_subset_complete.json").exists()


def test_without_a_subset_or_an_archive_the_task_fails_instead_of_downloading(data_dir):
    with pytest.raises(BronzeSourceNotReadyError, match="download it first"):
        tasks.ensure_orcid_subset(data_dir)


def test_a_partial_subset_with_an_archive_is_rebuilt_from_the_archive(data_dir, monkeypatch):
    _build_subset(data_dir)
    next((data_dir / "orcid_bulk" / "filtered").glob("*/*.xml")).unlink()
    archive = data_dir / "orcid_bulk" / "raw" / tasks.ORCID_ARCHIVE_NAME
    archive.parent.mkdir(parents=True)
    archive.write_bytes(b"archive")
    calls = []

    def fake_extract(archive_path, output_dir):
        calls.append((archive_path, output_dir))
        return OrcidBulkSubsetResult(scanned=100, matched=SUBSET_SIZE, output_dir=output_dir)

    monkeypatch.setattr(tasks, "fetch_orcid_bulk_subset_from_local_file", fake_extract)

    summary = tasks.ensure_orcid_subset(data_dir)

    assert summary["action"] == "extracted"
    assert (summary["scanned"], summary["matched"]) == (100, SUBSET_SIZE)
    assert calls == [(archive, data_dir / "orcid_bulk" / "filtered")]


def test_force_refetch_ignores_the_marker(data_dir, monkeypatch):
    _build_subset(data_dir)
    tasks.ensure_orcid_subset(data_dir)
    archive = data_dir / "orcid_bulk" / "raw" / tasks.ORCID_ARCHIVE_NAME
    archive.parent.mkdir(parents=True)
    archive.write_bytes(b"archive")
    monkeypatch.setattr(
        tasks,
        "fetch_orcid_bulk_subset_from_local_file",
        lambda archive_path, output_dir: OrcidBulkSubsetResult(scanned=5, matched=SUBSET_SIZE, output_dir=output_dir),
    )

    assert tasks.ensure_orcid_subset(data_dir, force_refetch=True)["action"] == "extracted"


# --- 4.2 / 4.3 synthetic CVN and API enrichment -----------------------------


def test_synthetic_cvn_requires_the_subset_to_be_marked_complete(data_dir):
    _build_subset(data_dir)

    with pytest.raises(BronzeSourceNotReadyError, match="orcid-bulk-subset"):
        tasks.run_synthetic_cvn(_run(), data_dir, count=3, seed=1, orcid_link_ratio=1.0)


def test_enrichment_looks_up_only_linked_ids_deterministically_and_stores_raw_records(data_dir):
    run = _run()
    ids = _prepare_run(data_dir, run)
    first_client, second_client = FakeOrcidClient(), FakeOrcidClient()

    summary = tasks.run_orcid_api_enrichment(run, data_dir, sample_size=4, seed=3, client=first_client)
    tasks.run_orcid_api_enrichment(run, data_dir, sample_size=4, seed=3, client=second_client)

    assert summary == {"requested": 4, "seed": 3, "ok": 4, "not_found": 0, "error": 0}
    assert first_client.requested == second_client.requested
    assert set(first_client.requested) <= set(ids)
    lines = [json.loads(line) for line in (data_dir / "bronze_runs" / run.run_id / "orcid_api" / "records.jsonl").read_text().splitlines()]
    assert [line["orcid_id"] for line in lines] == first_client.requested
    assert all(line["status"] == "ok" and line["record"]["person"] for line in lines)


def test_enrichment_tolerates_a_missing_record_an_api_error_and_a_network_failure(data_dir):
    run = _run()
    _prepare_run(data_dir, run)
    everything = tasks._sample_linked_orcid_ids(data_dir / "bronze_runs" / run.run_id / "synthetic_cvn" / "manifest.jsonl", 100, 3)
    client = FakeOrcidClient(
        missing=frozenset(everything[:1]),
        broken=frozenset(everything[1:2]),
        timing_out=frozenset(everything[2:3]),
    )

    summary = tasks.run_orcid_api_enrichment(run, data_dir, sample_size=100, seed=3, client=client)

    assert (summary["not_found"], summary["error"]) == (1, 2)
    assert summary["ok"] == len(everything) - 3


def test_enrichment_fails_when_most_lookups_fail(data_dir):
    run = _run()
    _prepare_run(data_dir, run)
    everything = tasks._sample_linked_orcid_ids(data_dir / "bronze_runs" / run.run_id / "synthetic_cvn" / "manifest.jsonl", 100, 3)

    with pytest.raises(BronzeLandingError, match="lookups succeeded"):
        tasks.run_orcid_api_enrichment(run, data_dir, sample_size=100, seed=3, client=FakeOrcidClient(broken=frozenset(everything)))


def test_enrichment_requires_the_synthetic_cvn_task_to_have_run(data_dir):
    with pytest.raises(BronzeSourceNotReadyError, match="synthetic-cvn"):
        tasks.run_orcid_api_enrichment(_run(), data_dir, sample_size=1, seed=1, client=FakeOrcidClient())


# --- 4.4 landing ------------------------------------------------------------


def _land(data_dir: Path, s3: FakeS3, run: RunContext, **kwargs) -> dict:
    return tasks.land_bronze(run, data_dir, s3=s3, bucket=BUCKET, **kwargs)


def test_landing_puts_all_three_sources_in_bronze_with_provenance_on_every_record(data_dir):
    run = _run()
    _prepare_run(data_dir, run)
    tasks.run_orcid_api_enrichment(run, data_dir, sample_size=5, seed=1, client=FakeOrcidClient())
    s3 = FakeS3()

    summary = _land(data_dir, s3, run, bulk_max_records=5)["sources"]

    assert summary[SOURCE_SYNTHETIC_CVN]["records_landed"] == 10
    assert summary[SOURCE_ORCID_API]["records_landed"] == 5
    assert summary[SOURCE_ORCID_BULK]["records_landed"] == 5
    for source in (SOURCE_SYNTHETIC_CVN, SOURCE_ORCID_API, SOURCE_ORCID_BULK):
        records = _all_lines(s3, f"bronze/source={source}/ingestion_date=2026-09-19/run_id={run.run_id}/")
        assert records
        for record in records:
            assert record["source"] == source
            assert record["ingestion_run_id"] == run.run_id
            assert record["retrieved_at"] and record["landed_at"] and record["source_snapshot"]
            assert record["landing_check"] == {"status": "valid", "errors": []}
            assert record["payload"]
        manifest = json.loads(s3.objects[f"bronze/source={source}/ingestion_date=2026-09-19/run_id={run.run_id}/_manifest.json"])
        assert manifest["records_landed"] == len(records)


def test_bulk_records_keep_the_raw_xml_and_name_their_archive(data_dir):
    run = _run()
    _prepare_run(data_dir, run)
    tasks.run_orcid_api_enrichment(run, data_dir, sample_size=2, seed=1, client=FakeOrcidClient())
    s3 = FakeS3()

    _land(data_dir, s3, run, bulk_max_records=3)

    record = _all_lines(s3, "bronze/source=orcid_bulk/")[0]
    assert record["payload_format"] == "xml"
    assert record["payload"].startswith("<?xml")
    assert record["source_artifacts"][0]["name"] == tasks.ORCID_ARCHIVE_NAME
    assert record["source_files"][0].startswith("filtered/")
    assert record["source_ref"] in record["payload"]


def test_the_bulk_cap_takes_the_first_records_in_a_deterministic_order(data_dir):
    run = _run()
    _prepare_run(data_dir, run)
    tasks.run_orcid_api_enrichment(run, data_dir, sample_size=2, seed=1, client=FakeOrcidClient())
    first, second = FakeS3(), FakeS3()

    _land(data_dir, first, run, bulk_max_records=4)
    _land(data_dir, second, run, bulk_max_records=4)

    refs = lambda s3: [record["source_ref"] for record in _all_lines(s3, "bronze/source=orcid_bulk/")]  # noqa: E731
    assert refs(first) == refs(second)
    assert len(refs(first)) == 4


def test_zero_lands_the_whole_bulk_subset(data_dir):
    run = _run()
    _prepare_run(data_dir, run)
    tasks.run_orcid_api_enrichment(run, data_dir, sample_size=2, seed=1, client=FakeOrcidClient())
    s3 = FakeS3()

    summary = _land(data_dir, s3, run, bulk_max_records=0)["sources"]

    assert summary[SOURCE_ORCID_BULK]["records_landed"] == SUBSET_SIZE


def test_a_later_run_does_not_land_the_static_bulk_snapshot_again_unless_forced(data_dir):
    first_run, second_run = _run("run-a"), _run("run-b")
    _prepare_run(data_dir, first_run)
    tasks.run_orcid_api_enrichment(first_run, data_dir, sample_size=2, seed=1, client=FakeOrcidClient())
    tasks.run_synthetic_cvn(second_run, data_dir, count=4, seed=8, orcid_link_ratio=1.0)
    tasks.run_orcid_api_enrichment(second_run, data_dir, sample_size=2, seed=1, client=FakeOrcidClient())
    s3 = FakeS3()

    _land(data_dir, s3, first_run, bulk_max_records=5)
    skipped = _land(data_dir, s3, second_run, bulk_max_records=5)["sources"][SOURCE_ORCID_BULK]
    forced = _land(data_dir, s3, second_run, bulk_max_records=5, force_bulk_landing=True)["sources"][SOURCE_ORCID_BULK]

    assert skipped == {"skipped": True, "reason": "snapshot already landed", "landed_by_runs": ["run-a"]}
    assert forced["records_landed"] == 5


def test_rerunning_the_same_run_replaces_its_own_bulk_partition_instead_of_skipping_it(data_dir):
    run = _run()
    _prepare_run(data_dir, run)
    tasks.run_orcid_api_enrichment(run, data_dir, sample_size=2, seed=1, client=FakeOrcidClient())
    s3 = FakeS3()

    _land(data_dir, s3, run, bulk_max_records=5)
    again = _land(data_dir, s3, run, bulk_max_records=5)["sources"][SOURCE_ORCID_BULK]

    assert again["records_landed"] == 5
    assert len(_all_lines(s3, "bronze/source=orcid_bulk/")) == 5


def test_a_different_bulk_cap_is_a_different_snapshot_and_lands_again(data_dir):
    first_run, second_run = _run("run-a"), _run("run-b")
    _prepare_run(data_dir, first_run)
    tasks.run_orcid_api_enrichment(first_run, data_dir, sample_size=2, seed=1, client=FakeOrcidClient())
    tasks.run_synthetic_cvn(second_run, data_dir, count=4, seed=8, orcid_link_ratio=1.0)
    tasks.run_orcid_api_enrichment(second_run, data_dir, sample_size=2, seed=1, client=FakeOrcidClient())
    s3 = FakeS3()

    _land(data_dir, s3, first_run, bulk_max_records=5)
    bigger = _land(data_dir, s3, second_run, bulk_max_records=8)["sources"][SOURCE_ORCID_BULK]

    assert bigger["records_landed"] == 8


def test_invalid_bulk_records_are_rejected_and_kept_out_of_bronze(data_dir):
    run = _run()
    _prepare_run(data_dir, run, bad_family_for=(1,))
    tasks.run_orcid_api_enrichment(run, data_dir, sample_size=2, seed=1, client=FakeOrcidClient())
    s3 = FakeS3()

    summary = _land(data_dir, s3, run, bulk_max_records=0, rejection_threshold=0.5)["sources"][SOURCE_ORCID_BULK]

    assert (summary["records_landed"], summary["records_rejected"]) == (SUBSET_SIZE - 1, 1)
    rejected = _all_lines(s3, "bronze/_rejected/source=orcid_bulk/")
    assert len(rejected) == 1
    assert "family name" in rejected[0]["landing_check"]["errors"][0]
    assert all(record["landing_check"]["status"] == "valid" for record in _all_lines(s3, "bronze/source=orcid_bulk/"))


def test_landing_fails_when_rejections_exceed_the_default_threshold(data_dir):
    run = _run()
    _prepare_run(data_dir, run, bad_family_for=(1, 2, 3))
    tasks.run_orcid_api_enrichment(run, data_dir, sample_size=2, seed=1, client=FakeOrcidClient())

    with pytest.raises(BronzeRejectionThresholdError):
        _land(data_dir, FakeS3(), run, bulk_max_records=0)


def test_landing_requires_the_generation_task_to_have_run(data_dir):
    _build_subset(data_dir)
    tasks.ensure_orcid_subset(data_dir)

    with pytest.raises(BronzeSourceNotReadyError, match="synthetic_cvn"):
        _land(data_dir, FakeS3(), _run())


def test_the_cli_parser_exposes_the_dag_defaults():
    args = tasks._parser().parse_args(["land-bronze", "--run-id", "x"])

    assert args.bulk_max_records == tasks.DEFAULT_BULK_MAX_RECORDS == 20_000
    assert args.rejection_threshold == 0.05
    assert tasks._parser().parse_args(["orcid-api-enrichment", "--run-id", "x"]).sample_size == 200
