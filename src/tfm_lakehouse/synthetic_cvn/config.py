from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SyntheticCvnConfig:
    """Parameters of one synthetic CVN generation run.

    Args:
        count: Number of valid documents to produce.
        seed: Seed of the run's random generator; the same value and the same
            seed directory produce byte-identical output.
        orcid_seed_dir: Directory holding the issue #95 ORCID subset, laid out
            as ``<3-digit>/<iD>.xml``.
        output_dir: Directory receiving the JSON Lines shards and the manifest.
        orcid_link_ratio: Fraction of documents that carry their seed's ORCID
            iD. The rest keep the seed's name and affiliation, with realistic
            variation, but no iD.
        shard_size: Maximum number of documents per JSON Lines shard.
        overwrite: Replace an existing run in ``output_dir`` instead of failing.
    """

    count: int
    seed: int
    orcid_seed_dir: Path
    output_dir: Path
    orcid_link_ratio: float = 0.7
    shard_size: int = 10_000
    overwrite: bool = False

    def __post_init__(self) -> None:
        if self.count < 1:
            raise ValueError(f"count must be >= 1, got {self.count}")
        if not 0.0 <= self.orcid_link_ratio <= 1.0:
            raise ValueError(f"orcid_link_ratio must be within [0, 1], got {self.orcid_link_ratio}")
        if self.shard_size < 1:
            raise ValueError(f"shard_size must be >= 1, got {self.shard_size}")
