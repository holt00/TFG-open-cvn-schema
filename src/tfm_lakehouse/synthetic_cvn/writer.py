from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from types import TracebackType
from typing import Any, IO

SHARD_FILE_TEMPLATE = "cvn_shard_{index:05d}.jsonl"
MANIFEST_FILE_NAME = "manifest.jsonl"


@dataclass(frozen=True)
class ManifestEntry:
    """Ground truth of one generated document, for verifying issue #98.

    Attributes:
        document_id: The document's ``identificador_unico_de_cv``.
        seed_orcid_id: ORCID iD of the real record the document was seeded from.
        linkage: ``"orcid_id"`` when the document carries that iD, or
            ``"name_affiliation"`` when it only keeps a varied name and
            affiliation.
        seed_reuse_round: 0 for a first use of the seed record; higher when
            the pool was exhausted and the seed is being reused.
        name_variant: How the document's name differs from the seed's
            (``"exact"`` when it does not).
    """

    document_id: str
    seed_orcid_id: str
    linkage: str
    seed_reuse_round: int
    name_variant: str


class ShardedJsonlWriter:
    """Writes documents as JSON Lines shards plus one manifest file.

    Few large shards instead of one file per document: issue #95 showed that
    hundreds of thousands of small files are I/O-bound on the Windows-mounted
    drive, and issue #97 lands the output into MinIO, which favors fewer,
    larger objects.
    """

    def __init__(self, output_dir: Path, shard_size: int, overwrite: bool = False) -> None:
        self._output_dir = output_dir
        self._shard_size = shard_size
        self._overwrite = overwrite
        self._shard_handle: IO[str] | None = None
        self._manifest_handle: IO[str] | None = None
        self._shard_index = -1
        self._lines_in_shard = 0
        self.documents_written = 0

    @property
    def shards_written(self) -> int:
        return self._shard_index + 1

    def __enter__(self) -> ShardedJsonlWriter:
        self._output_dir.mkdir(parents=True, exist_ok=True)
        existing = [
            *self._output_dir.glob("cvn_shard_*.jsonl"),
            *self._output_dir.glob(MANIFEST_FILE_NAME),
        ]
        if existing:
            if not self._overwrite:
                raise FileExistsError(
                    f"{self._output_dir} already holds a synthetic CVN run; set overwrite=True to replace it"
                )
            for path in existing:
                path.unlink()
        self._manifest_handle = (self._output_dir / MANIFEST_FILE_NAME).open("w", encoding="utf-8", newline="\n")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._shard_handle is not None:
            self._shard_handle.close()
        if self._manifest_handle is not None:
            self._manifest_handle.close()

    def write(self, document: Mapping[str, Any], manifest_entry: ManifestEntry) -> None:
        if self._manifest_handle is None:
            raise RuntimeError("ShardedJsonlWriter must be used as a context manager")
        if self._shard_handle is None or self._lines_in_shard >= self._shard_size:
            self._open_next_shard()
        assert self._shard_handle is not None
        line_number = self._lines_in_shard
        self._shard_handle.write(json.dumps(document, ensure_ascii=False, separators=(",", ":")) + "\n")
        self._lines_in_shard += 1
        self._manifest_handle.write(
            json.dumps(
                {
                    **asdict(manifest_entry),
                    "shard_file": SHARD_FILE_TEMPLATE.format(index=self._shard_index),
                    "line_number": line_number,
                },
                ensure_ascii=False,
                separators=(",", ":"),
            )
            + "\n"
        )
        self.documents_written += 1

    def _open_next_shard(self) -> None:
        if self._shard_handle is not None:
            self._shard_handle.close()
        self._shard_index += 1
        self._lines_in_shard = 0
        shard_path = self._output_dir / SHARD_FILE_TEMPLATE.format(index=self._shard_index)
        self._shard_handle = shard_path.open("w", encoding="utf-8", newline="\n")
