import hashlib
import io
import tarfile
from unittest.mock import Mock, patch

import pytest

from tfm_lakehouse.orcid_bulk.exceptions import OrcidBulkChecksumError
from tfm_lakehouse.orcid_bulk.pipeline import (
    fetch_orcid_bulk_subset,
    fetch_orcid_bulk_subset_from_local_file,
)

RECORD_TEMPLATE = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<record:record xmlns:common="http://www.orcid.org/ns/common"
                xmlns:employment="http://www.orcid.org/ns/employment"
                xmlns:record="http://www.orcid.org/ns/record">
    <common:orcid-identifier>
        <common:path>{orcid_id}</common:path>
    </common:orcid-identifier>
    <employment:employment-summary put-code="1">
        <common:organization>
            <common:name>{org_name}</common:name>
            <common:address>
                <common:city>{city}</common:city>
                <common:country>{country}</common:country>
            </common:address>
        </common:organization>
    </employment:employment-summary>
</record:record>
"""

NO_AFFILIATION_RECORD = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<record:record xmlns:common="http://www.orcid.org/ns/common"
                xmlns:record="http://www.orcid.org/ns/record">
    <common:orcid-identifier>
        <common:path>0000-0000-0000-0002</common:path>
    </common:orcid-identifier>
</record:record>
"""


PERSON_ADDRESS_ONLY_RECORD = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<record:record xmlns:common="http://www.orcid.org/ns/common"
                xmlns:address="http://www.orcid.org/ns/address"
                xmlns:employment="http://www.orcid.org/ns/employment"
                xmlns:record="http://www.orcid.org/ns/record">
    <address:address>
        <address:country>ES</address:country>
    </address:address>
    <employment:employment-summary put-code="1">
        <common:organization>
            <common:name>MIT</common:name>
            <common:address>
                <common:country>US</common:country>
            </common:address>
        </common:organization>
    </employment:employment-summary>
    <common:country>ES</common:country>
</record:record>
"""


def test_country_outside_affiliation_path_is_not_matched():
    from tfm_lakehouse.orcid_bulk.pipeline import _has_matching_country

    assert not _has_matching_country(
        PERSON_ADDRESS_ONLY_RECORD.encode(), frozenset({"ES"})
    )


def _build_tar_gz(entries: dict[str, str]) -> bytes:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as tf:
        for name, content in entries.items():
            data = content.encode("utf-8")
            info = tarfile.TarInfo(name=f"ORCID_2025_10_summaries/{name}")
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))
    return buffer.getvalue()


def _fixture_bytes() -> bytes:
    return _build_tar_gz(
        {
            "000/0000-0000-0000-0001.xml": RECORD_TEMPLATE.format(
                orcid_id="0000-0000-0000-0001",
                org_name="Universidad de Sevilla",
                city="Sevilla",
                country="ES",
            ),
            "000/0000-0000-0000-0002.xml": NO_AFFILIATION_RECORD,
            "000/0000-0000-0000-0003.xml": RECORD_TEMPLATE.format(
                orcid_id="0000-0000-0000-0003",
                org_name="MIT",
                city="Cambridge",
                country="US",
            ),
        }
    )


def _mock_response(payload: bytes) -> Mock:
    response = Mock()
    response.raw = io.BytesIO(payload)
    response.raise_for_status = Mock()
    response.close = Mock()
    return response


def test_fetch_orcid_bulk_subset_filters_by_country(tmp_path):
    payload = _fixture_bytes()
    expected_md5 = hashlib.md5(payload).hexdigest()

    with patch(
        "tfm_lakehouse.orcid_bulk.pipeline.requests.get",
        return_value=_mock_response(payload),
    ):
        result = fetch_orcid_bulk_subset(
            output_dir=tmp_path,
            countries=frozenset({"ES"}),
            expected_md5=expected_md5,
        )

    assert result.scanned == 3
    assert result.matched == 1
    matched_file = tmp_path / "000" / "0000-0000-0000-0001.xml"
    assert matched_file.exists()
    assert not (tmp_path / "000" / "0000-0000-0000-0002.xml").exists()
    assert not (tmp_path / "000" / "0000-0000-0000-0003.xml").exists()


def test_fetch_orcid_bulk_subset_accepts_multiple_countries(tmp_path):
    payload = _fixture_bytes()

    with patch(
        "tfm_lakehouse.orcid_bulk.pipeline.requests.get",
        return_value=_mock_response(payload),
    ):
        result = fetch_orcid_bulk_subset(
            output_dir=tmp_path,
            countries=frozenset({"ES", "US"}),
            expected_md5=None,
        )

    assert result.matched == 2


def test_fetch_orcid_bulk_subset_raises_on_checksum_mismatch(tmp_path):
    payload = _fixture_bytes()

    with patch(
        "tfm_lakehouse.orcid_bulk.pipeline.requests.get",
        return_value=_mock_response(payload),
    ):
        with pytest.raises(OrcidBulkChecksumError):
            fetch_orcid_bulk_subset(
                output_dir=tmp_path,
                expected_md5="0" * 32,
            )


def test_fetch_orcid_bulk_subset_skips_checksum_when_none_expected(tmp_path):
    payload = _fixture_bytes()

    with patch(
        "tfm_lakehouse.orcid_bulk.pipeline.requests.get",
        return_value=_mock_response(payload),
    ):
        result = fetch_orcid_bulk_subset(
            output_dir=tmp_path,
            expected_md5=None,
        )

    assert result.scanned == 3


def test_fetch_orcid_bulk_subset_from_local_file(tmp_path):
    payload = _fixture_bytes()
    archive_path = tmp_path / "ORCID_2025_10_summaries.tar.gz"
    archive_path.write_bytes(payload)
    expected_md5 = hashlib.md5(payload).hexdigest()
    output_dir = tmp_path / "filtered"

    result = fetch_orcid_bulk_subset_from_local_file(
        archive_path=archive_path,
        output_dir=output_dir,
        countries=frozenset({"ES"}),
        expected_md5=expected_md5,
    )

    assert result.scanned == 3
    assert result.matched == 1
    assert (output_dir / "000" / "0000-0000-0000-0001.xml").exists()


def test_fetch_orcid_bulk_subset_from_local_file_raises_on_checksum_mismatch(tmp_path):
    payload = _fixture_bytes()
    archive_path = tmp_path / "ORCID_2025_10_summaries.tar.gz"
    archive_path.write_bytes(payload)

    with pytest.raises(OrcidBulkChecksumError):
        fetch_orcid_bulk_subset_from_local_file(
            archive_path=archive_path,
            output_dir=tmp_path / "filtered",
            expected_md5="0" * 32,
        )
