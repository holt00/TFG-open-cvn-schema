import os
import pytest
from tfm_lakehouse.orcid_client import OrcidClient

JOSIAH_CARBERRY_ORCID_ID = "0000-0002-1825-0097"

pytestmark = pytest.mark.skipif(
    os.environ.get("ORCID_LIVE_TEST") != "1",
    reason="set ORCID_LIVE_TEST=1 to run this test against the real, unauthenticated ORCID API",
)


def test_get_record_returns_expected_fields_for_known_public_demo_id():
    client = OrcidClient()
    record = client.get_record(JOSIAH_CARBERRY_ORCID_ID)
    assert record["orcid-identifier"]["path"] == JOSIAH_CARBERRY_ORCID_ID
