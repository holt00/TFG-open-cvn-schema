import copy
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from bronze_fakes import FakeS3
from tfm_lakehouse.bronze.checks import (
    check_cvn_document,
    check_orcid_api_record,
    check_orcid_summary_xml,
    serialize_line,
)
from tfm_lakehouse.bronze.envelope import (
    PAYLOAD_FORMAT_XML,
    SOURCE_ORCID_BULK,
    SOURCE_SYNTHETIC_CVN,
    LandingCheck,
    RunContext,
    build_envelope,
    make_record_id,
)
from tfm_lakehouse.bronze.exceptions import BronzeLandingError, BronzeRejectionThresholdError
from tfm_lakehouse.bronze.landing import (
    find_landed_runs,
    land_records,
    partition_prefix,
)

EXAMPLES = Path(__file__).resolve().parent.parent / "examples" / "open_cvn"
VALID_ORCID_ID = "0000-0002-1825-0097"
BAD_CHECKSUM_ORCID_ID = "0000-0002-1825-0098"
BUCKET = "lakehouse"

_NAMESPACES = (
    'xmlns:common="http://www.orcid.org/ns/common" '
    'xmlns:person="http://www.orcid.org/ns/person" '
    'xmlns:personal="http://www.orcid.org/ns/personal-details" '
    'xmlns:activities="http://www.orcid.org/ns/activities" '
    'xmlns:employment="http://www.orcid.org/ns/employment" '
    'xmlns:record="http://www.orcid.org/ns/record"'
)


def _orcid_xml(
    orcid_id: str = VALID_ORCID_ID,
    *,
    given: str | None = "Ana",
    family: str | None = "García",
    organization: str | None = "Universidad de Ejemplo",
) -> bytes:
    given_xml = f"<personal:given-names>{given}</personal:given-names>" if given else ""
    family_xml = f"<personal:family-name>{family}</personal:family-name>" if family else ""
    activities = ""
    if organization:
        activities = (
            "<activities:activities-summary><employment:employment-summary>"
            f"<common:organization><common:name>{organization}</common:name></common:organization>"
            "</employment:employment-summary></activities:activities-summary>"
        )
    return (
        f'<?xml version="1.0" encoding="UTF-8"?><record:record {_NAMESPACES}>'
        f"<common:orcid-identifier><common:path>{orcid_id}</common:path></common:orcid-identifier>"
        f"<person:person><person:name>{given_xml}{family_xml}</person:name></person:person>"
        f"{activities}</record:record>"
    ).encode()


def _run(run_id: str = "manual__2026-09-19") -> RunContext:
    return RunContext.create(run_id, now=datetime(2026, 9, 19, 12, 30, tzinfo=UTC))


def _envelope(index: int, *, valid: bool = True, run: RunContext | None = None) -> dict:
    check = LandingCheck(status="valid") if valid else LandingCheck(status="invalid", errors=("broken",))
    return build_envelope(
        source=SOURCE_ORCID_BULK,
        source_ref=f"ref-{index}",
        payload=f"<x>{index}</x>",
        payload_format=PAYLOAD_FORMAT_XML,
        run=run or _run(),
        retrieved_at="2026-09-18T00:00:00Z",
        source_snapshot="snap-1",
        check=check,
    )


# --- envelope ---------------------------------------------------------------


def test_run_context_sanitizes_airflow_run_ids_deterministically():
    first = RunContext.create("scheduled__2026-09-19T00:00:00+00:00")
    second = RunContext.create("scheduled__2026-09-19T00:00:00+00:00")

    assert first.run_id == second.run_id == "scheduled__2026-09-19T00_00_00_00_00"
    assert all(character.isalnum() or character in "._-" for character in first.run_id)


def test_run_context_rejects_an_empty_run_id():
    with pytest.raises(ValueError):
        RunContext.create(":::")


def test_run_context_uses_the_utc_date_of_the_run():
    run = RunContext.create("r", now=datetime(2026, 9, 19, 23, 59, tzinfo=UTC))

    assert run.ingestion_date.isoformat() == "2026-09-19"
    assert run.landed_at == "2026-09-19T23:59:00Z"


def test_envelope_carries_provenance_and_the_untouched_payload():
    envelope = build_envelope(
        source=SOURCE_ORCID_BULK,
        source_ref=VALID_ORCID_ID,
        payload="<record/>",
        payload_format=PAYLOAD_FORMAT_XML,
        run=_run(),
        retrieved_at="2026-09-18T00:00:00Z",
        source_snapshot="ORCID_2025_10",
        check=LandingCheck(status="valid"),
        source_files=("000/x.xml",),
        source_artifacts=({"name": "a.tar.gz", "md5": "abc"},),
    )

    assert envelope["record_id"] == make_record_id(SOURCE_ORCID_BULK, VALID_ORCID_ID)
    assert envelope["payload"] == "<record/>"
    assert envelope["ingestion_run_id"] == "manual__2026-09-19"
    assert envelope["ingestion_date"] == "2026-09-19"
    assert envelope["retrieved_at"] == "2026-09-18T00:00:00Z"
    assert envelope["landed_at"] == "2026-09-19T12:30:00Z"
    assert envelope["source_files"] == ["000/x.xml"]
    assert envelope["source_artifacts"] == [{"name": "a.tar.gz", "md5": "abc"}]
    assert envelope["landing_check"] == {"status": "valid", "errors": []}
    json.dumps(envelope)


def test_serialize_line_is_compact_utf8_and_newline_terminated():
    line = serialize_line({"nombre": "García", "n": 1})

    assert line == '{"nombre":"García","n":1}\n'.encode()


# --- checks -----------------------------------------------------------------


def test_cvn_check_accepts_a_schema_valid_document():
    document = json.loads((EXAMPLES / "minimal.json").read_text(encoding="utf-8"))

    assert check_cvn_document(document).is_valid


def test_cvn_check_rejects_a_document_without_a_curriculum():
    document = json.loads((EXAMPLES / "minimal.json").read_text(encoding="utf-8"))
    broken = copy.deepcopy(document)
    del broken["curriculum"]

    check = check_cvn_document(broken)

    assert not check.is_valid
    assert check.errors


def test_orcid_xml_check_accepts_a_complete_record_and_returns_its_id():
    check, orcid_id = check_orcid_summary_xml(_orcid_xml())

    assert check.is_valid
    assert orcid_id == VALID_ORCID_ID


@pytest.mark.parametrize(
    ("xml", "expected_error"),
    [
        (_orcid_xml(BAD_CHECKSUM_ORCID_ID), "checksum"),
        (_orcid_xml(family=None), "family name"),
        (_orcid_xml(given=None), "given names"),
        (_orcid_xml(organization=None), "organization name"),
    ],
)
def test_orcid_xml_check_rejects_a_record_missing_a_required_field(xml, expected_error):
    check, _ = check_orcid_summary_xml(xml)

    assert not check.is_valid
    assert any(expected_error in error for error in check.errors)


def test_orcid_xml_check_rejects_malformed_xml_without_raising():
    check, orcid_id = check_orcid_summary_xml(b"<record:record")

    assert not check.is_valid
    assert orcid_id is None
    assert "malformed XML" in check.errors[0]


def test_orcid_api_check_accepts_a_matching_record_with_a_person():
    record = {"orcid-identifier": {"path": VALID_ORCID_ID}, "person": {"name": None}}

    assert check_orcid_api_record(record, VALID_ORCID_ID).is_valid


def test_orcid_api_check_rejects_a_different_id_and_a_missing_person():
    record = {"orcid-identifier": {"path": "0000-0001-5109-3700"}}

    check = check_orcid_api_record(record, VALID_ORCID_ID)

    assert not check.is_valid
    assert any("does not match" in error for error in check.errors)
    assert any("person" in error for error in check.errors)


# --- landing ----------------------------------------------------------------


def _lines(s3: FakeS3, key: str) -> list[dict]:
    return [json.loads(line) for line in s3.objects[key].decode().splitlines()]


def test_partition_layout_is_hive_style_and_rejected_is_underscore_prefixed():
    run = _run()

    assert partition_prefix(SOURCE_ORCID_BULK, run) == (
        "bronze/source=orcid_bulk/ingestion_date=2026-09-19/run_id=manual__2026-09-19/"
    )
    assert partition_prefix(SOURCE_ORCID_BULK, run, rejected=True).startswith("bronze/_rejected/source=orcid_bulk/")


def test_land_records_splits_valid_and_rejected_and_writes_the_manifest_last():
    s3 = FakeS3()
    envelopes = [_envelope(1), _envelope(2), _envelope(3), _envelope(4, valid=False)]

    summary = land_records(
        s3,
        bucket=BUCKET,
        source=SOURCE_ORCID_BULK,
        run=_run(),
        source_snapshot="snap-1",
        envelopes=envelopes,
        rejection_threshold=0.5,
        extra_manifest={"bulk_max_records": 4},
    )

    assert (summary.records_landed, summary.records_rejected) == (3, 1)
    assert [envelope["source_ref"] for envelope in _lines(s3, summary.shards[0].key)] == ["ref-1", "ref-2", "ref-3"]
    rejected_key = summary.rejected_shards[0].key
    assert rejected_key.startswith("bronze/_rejected/")
    assert _lines(s3, rejected_key)[0]["landing_check"]["errors"] == ["broken"]
    assert s3.put_order[-1] == summary.manifest_key
    manifest = json.loads(s3.objects[summary.manifest_key])
    assert manifest["records_landed"] == 3
    assert manifest["records_rejected"] == 1
    assert manifest["source_snapshot"] == "snap-1"
    assert manifest["bulk_max_records"] == 4
    assert manifest["shards"][0]["sha256"]


def test_land_records_starts_a_new_shard_at_the_target_size():
    s3 = FakeS3()

    summary = land_records(
        s3,
        bucket=BUCKET,
        source=SOURCE_ORCID_BULK,
        run=_run(),
        source_snapshot="snap-1",
        envelopes=[_envelope(index) for index in range(10)],
        shard_target_bytes=1,
    )

    assert len(summary.shards) == 10
    assert [shard.records for shard in summary.shards] == [1] * 10
    assert summary.shards[3].key.endswith("part-00003.jsonl")


def test_rerunning_the_same_run_replaces_its_partition_instead_of_duplicating_it():
    s3 = FakeS3(page_size=2)
    kwargs = {"bucket": BUCKET, "source": SOURCE_ORCID_BULK, "run": _run(), "source_snapshot": "snap-1"}

    land_records(s3, envelopes=[_envelope(index) for index in range(6)], shard_target_bytes=1, **kwargs)
    summary = land_records(s3, envelopes=[_envelope(1), _envelope(2)], **kwargs)

    partition_keys = [key for key in s3.objects if key.startswith(partition_prefix(SOURCE_ORCID_BULK, _run()))]
    assert sorted(partition_keys) == sorted([summary.shards[0].key, summary.manifest_key])
    assert summary.records_landed == 2


def test_a_different_run_lands_next_to_the_first_one():
    s3 = FakeS3()
    common = {"bucket": BUCKET, "source": SOURCE_ORCID_BULK, "source_snapshot": "snap-1"}

    first = land_records(s3, run=_run("run-a"), envelopes=[_envelope(1)], **common)
    second = land_records(s3, run=_run("run-b"), envelopes=[_envelope(1)], **common)

    assert first.manifest_key != second.manifest_key
    assert first.manifest_key in s3.objects
    assert second.manifest_key in s3.objects


def test_land_records_fails_above_the_rejection_threshold_leaving_only_the_rejected_records():
    s3 = FakeS3()
    envelopes = [_envelope(1), _envelope(2, valid=False), _envelope(3, valid=False)]

    with pytest.raises(BronzeRejectionThresholdError, match="66.7%"):
        land_records(
            s3,
            bucket=BUCKET,
            source=SOURCE_ORCID_BULK,
            run=_run(),
            source_snapshot="snap-1",
            envelopes=envelopes,
            rejection_threshold=0.05,
        )

    assert not any(key.endswith("_manifest.json") for key in s3.objects)
    assert s3.objects
    assert all(key.startswith("bronze/_rejected/") for key in s3.objects)


def test_a_failure_while_landing_removes_the_partition_written_so_far():
    s3 = FakeS3()

    def envelopes():
        yield _envelope(1)
        yield _envelope(2)
        raise ConnectionError("source went away")

    with pytest.raises(ConnectionError):
        land_records(
            s3,
            bucket=BUCKET,
            source=SOURCE_ORCID_BULK,
            run=_run(),
            source_snapshot="snap-1",
            envelopes=envelopes(),
            shard_target_bytes=1,
        )

    assert not [key for key in s3.objects if not key.startswith("bronze/_rejected/")]


def test_land_records_fails_when_the_source_delivered_nothing():
    with pytest.raises(BronzeLandingError, match="no records"):
        land_records(
            FakeS3(),
            bucket=BUCKET,
            source=SOURCE_SYNTHETIC_CVN,
            run=_run(),
            source_snapshot="snap-1",
            envelopes=[],
        )


def test_find_landed_runs_only_counts_complete_partitions_of_the_snapshot():
    s3 = FakeS3()
    common = {"bucket": BUCKET, "source": SOURCE_ORCID_BULK}
    land_records(s3, run=_run("run-a"), source_snapshot="snap-1", envelopes=[_envelope(1)], **common)
    land_records(s3, run=_run("run-b"), source_snapshot="snap-2", envelopes=[_envelope(1)], **common)
    with pytest.raises(BronzeRejectionThresholdError):
        land_records(
            s3,
            run=_run("run-c"),
            source_snapshot="snap-1",
            envelopes=[_envelope(1, valid=False)],
            **common,
        )

    assert find_landed_runs(s3, bucket=BUCKET, source=SOURCE_ORCID_BULK, source_snapshot="snap-1") == ["run-a"]
    assert find_landed_runs(s3, bucket=BUCKET, source=SOURCE_ORCID_BULK, source_snapshot="snap-3") == []
