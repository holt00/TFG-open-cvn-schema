import json
from pathlib import Path

import pytest

from tfm_lakehouse.synthetic_cvn import SyntheticCvnConfig, generate_synthetic_cvn
from tfm_lakehouse.synthetic_cvn.validation import validate_synthetic_document

ORCID_SUBSET_DIR = Path(__file__).resolve().parent.parent / "data" / "orcid_bulk" / "filtered"


@pytest.mark.skipif(
    not ORCID_SUBSET_DIR.is_dir(),
    reason="the issue #95 ORCID subset is not present locally (data/ is git-ignored)",
)
def test_generation_from_the_real_orcid_subset_is_valid_and_varied(tmp_path):
    """Generates from the real ~300k-record subset, which fabricated fixtures cannot cover.

    The real data has records with no works, hundreds of works, DOIs written as
    URLs, and unusual affiliation text; none of it may yield an invalid document.
    """
    result = generate_synthetic_cvn(
        SyntheticCvnConfig(count=150, seed=2026, orcid_seed_dir=ORCID_SUBSET_DIR, output_dir=tmp_path)
    )

    assert result.generated == 150
    assert result.invalid_discarded == 0
    documents = [
        json.loads(line)
        for shard in sorted(tmp_path.glob("cvn_shard_*.jsonl"))
        for line in shard.read_text(encoding="utf-8").splitlines()
    ]
    assert all(validate_synthetic_document(document) == () for document in documents)
    assert len({json.dumps(document, sort_keys=True) for document in documents}) == 150
    publications = [entry for document in documents for entry in document["curriculum"]["research"]]
    assert len({entry["data"]["publicacion_titulo"] for entry in publications}) > len(publications) * 0.8
