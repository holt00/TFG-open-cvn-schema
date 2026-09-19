from __future__ import annotations

import logging
import random
import time
from collections import deque
from collections.abc import Iterator
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

from tfm_lakehouse.synthetic_cvn.builders import build_document
from tfm_lakehouse.synthetic_cvn.config import SyntheticCvnConfig
from tfm_lakehouse.synthetic_cvn.exceptions import SyntheticCvnGenerationError
from tfm_lakehouse.synthetic_cvn.seed import OrcidSeedPool, SeedDraw, parse_orcid_summary
from tfm_lakehouse.synthetic_cvn.validation import validate_synthetic_document
from tfm_lakehouse.synthetic_cvn.writer import ManifestEntry, ShardedJsonlWriter

logger = logging.getLogger(__name__)

_READ_WORKERS = 16
_PREFETCH_WINDOW = 128
_PROGRESS_INTERVAL = 1_000
_MAX_INVALID_SAMPLES = 5


@dataclass(frozen=True)
class SyntheticCvnResult:
    requested: int
    generated: int
    linked: int
    unlinked: int
    skipped_seeds: int
    invalid_discarded: int
    invalid_samples: tuple[tuple[str, ...], ...]
    max_seed_reuse_round: int
    shards_written: int
    output_dir: Path
    elapsed_seconds: float


def _read_seed_file(path: Path) -> bytes | None:
    try:
        return path.read_bytes()
    except OSError:
        return None


def _prefetch_seed_files(
    draws: Iterator[SeedDraw], executor: ThreadPoolExecutor
) -> Iterator[tuple[SeedDraw, bytes | None]]:
    """Read seed files ahead of use, in draw order.

    Reading ~300k small files from the Windows-mounted drive is I/O-bound
    (issue #95 hit the same wall), so reads overlap in a thread pool while
    documents are built and validated in the caller's thread.
    """
    pending: deque[tuple[SeedDraw, Future[bytes | None]]] = deque()
    while True:
        while len(pending) < _PREFETCH_WINDOW:
            draw = next(draws)
            pending.append((draw, executor.submit(_read_seed_file, draw.path)))
        draw, future = pending.popleft()
        yield draw, future.result()


def generate_synthetic_cvn(config: SyntheticCvnConfig) -> SyntheticCvnResult:
    """Generate synthetic, schema-valid Open CVN documents seeded from ORCID.

    Every document is validated before it is written; an invalid one is
    discarded and counted rather than written. Output is deterministic in
    ``config.seed`` and the contents of ``config.orcid_seed_dir``.

    Raises:
        SyntheticCvnSeedError: If the seed directory is missing or empty.
        SyntheticCvnGenerationError: If too many seeds or documents are
            rejected to reach ``config.count``, which points at a generator or
            seed-data problem rather than bad luck.
        FileExistsError: If ``config.output_dir`` already holds a run and
            ``config.overwrite`` is false.
    """
    started = time.monotonic()
    # Two independent streams: seed-file draws must not depend on how much
    # randomness building a document consumed, or prefetching them ahead of
    # the documents would change the output.
    draw_rng = random.Random(f"{config.seed}:draws")
    rng = random.Random(f"{config.seed}:documents")
    pool = OrcidSeedPool(config.orcid_seed_dir)
    max_attempts = config.count * 3 + 1_000

    generated = linked = skipped_seeds = invalid_discarded = max_reuse_round = attempts = 0
    invalid_samples: list[tuple[str, ...]] = []

    with (
        ShardedJsonlWriter(config.output_dir, config.shard_size, config.overwrite) as writer,
        ThreadPoolExecutor(max_workers=_READ_WORKERS) as executor,
    ):
        for draw, seed_bytes in _prefetch_seed_files(pool.iter_draws(draw_rng), executor):
            if generated >= config.count:
                break
            attempts += 1
            if attempts > max_attempts:
                raise SyntheticCvnGenerationError(
                    f"gave up after {attempts - 1} seeds: {generated} valid documents, "
                    f"{skipped_seeds} unusable seeds, {invalid_discarded} invalid documents"
                )
            seed = parse_orcid_summary(seed_bytes) if seed_bytes is not None else None
            if seed is None:
                skipped_seeds += 1
                continue

            include_orcid = rng.random() < config.orcid_link_ratio
            document_id = f"SYN-{config.seed}-{generated + 1:08d}"
            document, name_variant = build_document(
                seed,
                document_id=document_id,
                run_seed=config.seed,
                include_orcid=include_orcid,
                rng=rng,
            )
            errors = validate_synthetic_document(document)
            if errors:
                invalid_discarded += 1
                if len(invalid_samples) < _MAX_INVALID_SAMPLES:
                    invalid_samples.append(errors)
                    logger.warning(f"discarded invalid synthetic document {document_id}: {errors[:3]}")
                continue

            writer.write(
                document,
                ManifestEntry(
                    document_id=document_id,
                    seed_orcid_id=seed.orcid_id,
                    linkage="orcid_id" if include_orcid else "name_affiliation",
                    seed_reuse_round=draw.reuse_round,
                    name_variant=name_variant,
                ),
            )
            generated += 1
            linked += include_orcid
            max_reuse_round = max(max_reuse_round, draw.reuse_round)
            if generated % _PROGRESS_INTERVAL == 0:
                logger.info(f"generated {generated}/{config.count} synthetic CVN documents")

        shards_written = writer.shards_written

    return SyntheticCvnResult(
        requested=config.count,
        generated=generated,
        linked=linked,
        unlinked=generated - linked,
        skipped_seeds=skipped_seeds,
        invalid_discarded=invalid_discarded,
        invalid_samples=tuple(invalid_samples),
        max_seed_reuse_round=max_reuse_round,
        shards_written=shards_written,
        output_dir=config.output_dir,
        elapsed_seconds=time.monotonic() - started,
    )
