import os

import pytest

from tfm_lakehouse.orcid_bulk.pipeline import fetch_orcid_bulk_subset

LIVE_TEST_ENABLED = os.environ.get("ORCID_LIVE_TEST") == "1"


@pytest.mark.skipif(
    not LIVE_TEST_ENABLED,
    reason="set ORCID_LIVE_TEST=1 to run against the real ORCID Figshare file",
)
def test_fetch_orcid_bulk_subset_against_real_file(tmp_path):
    """Streams a small real slice of the real 2025 summaries.tar.gz to confirm
    the real endpoint, real gzip/tar framing, and the Task 1-confirmed
    country XML path all work end to end, without pulling the full 46.3 GB.
    """
    result = fetch_orcid_bulk_subset(
        output_dir=tmp_path,
        countries=frozenset({"ES", "US", "IT"}),
        max_scanned=2_000,
    )

    assert result.scanned == 2_000
    assert result.matched > 0
    matched_files = list(tmp_path.rglob("*.xml"))
    assert len(matched_files) == result.matched
