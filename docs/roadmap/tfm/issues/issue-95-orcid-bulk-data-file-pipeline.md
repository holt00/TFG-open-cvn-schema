# Issue 95 - ORCID Bulk Data File Pipeline

## Summary

Download and filter the ORCID public data file to a manageable working
volume subset. Second data-source issue of TFM epic phase 2.

## Original Goal

Obtain a real, sizeable ORCID dataset as the platform's genuine "big data"
volume source, instead of relying on synthetic data for scale.

## Original Plan

- verify the current official download location and format for the ORCID
  Public Data File before writing any code against it (it has moved hosting
  providers over the years, per the epic's own caution)
- download the file (or the relevant portion of it)
- implement a filter to produce the working subset (candidate filters: a
  Spain-affiliated employment/education entry, or a field/keyword filter),
  bounding the volume used day-to-day
- store the filtered subset ready for bronze landing (issue `#97`)

## Adjustments Made During Implementation

**Download location and format confirmed (2026-09-18):** verified against the
live ORCID Figshare API rather than documentation prose alone. Current
hosting is Figshare (`orcid.figshare.com`), not AWS S3/BigQuery (those exist
but are secondary/paid-tier mirrors run by Digital Science, not the primary
free source). The 2025 dataset (`ORCID_2025_10_*`, DOI
`10.6084/m9.figshare.30375589`) exposes 12 files via
`https://api.figshare.com/v2/articles/30375589`: one `..._summaries.tar.gz`
(46.3 GB, real record-summary XML, one `[3-digit-checksum]/[iD].xml` entry
per registrant) and 11 `..._activities_N.tar.gz` files (~16-19 GB each,
~191 GB total, full works/fundings/peer-review detail). Each file entry
includes a `supplied_md5` for integrity verification and a direct
`download_url` (`ndownloader.figshare.com`), no authentication needed.

**Decision: use the summaries file only, not the activities files.** The
summaries file's `employment-summary`/`education-summary` elements carry
`organization`/`address`/country data, which is exactly what the candidate
"Spain-affiliated" filter needs; the activities files add works/funding/peer-
review detail that neither this issue's filter nor `#97`'s bronze-landing
scope currently requires. This cuts the source volume from ~238 GB to
46.3 GB before any filtering, directly serving the issue's own "manageable
working volume subset" goal without inventing scope. If a later issue needs
full activity detail per record, it can be fetched narrowly through `#94`'s
already-built `OrcidClient` (per-iD, on demand) instead of bulk-downloading
the activities files.

**Decision: Spain-affiliated employment/education filter (`country == "ES"`),
not the field/keyword alternative.** Both were named as candidates in the
original plan. Country filter chosen because it is a single, unambiguous,
machine-checkable field already present in every employment/education
summary entry, with no keyword-list-maintenance burden and no risk of
under/over-matching on free-text subject/field descriptions. Exact XML
element path (expected: `employment-summary`/`education-summary` ->
`organization` -> `address` -> `common:country`, ORCID XML schema v3.0
namespaces) is not yet confirmed against a real extracted entry -- Task 1
below verifies this before the filter is implemented, per this issue's own
"verify before coding" convention (matching how the original plan already
insisted on verifying the download location first).

**Decision: local filesystem output, not direct-to-MinIO-bronze.** This
issue's own scope, per the Summary, is "store the filtered subset ready for
bronze landing (issue `#97`)" -- landing into MinIO bronze with provenance
metadata is explicitly `#97`'s deliverable (`validate_and_land_bronze` task),
not this one's. Output goes to a new local, git-ignored working directory
(`data/orcid_bulk/filtered/`), one XML file per matched record, mirroring the
source tar's own `[3-digit]/[iD].xml` layout so `#97` can consume it without
a translation step.

**Decision: module path `src/tfm_lakehouse/orcid_bulk/`, not the epic's
originally-suggested `src/tfm_lakehouse/ingestion/orcid_bulk.py`.** This
follows the precedent `#94` already set: the epic's repository-standards
section names `src/tfm_lakehouse/ingestion/orcid_api.py`, but `#94` actually
shipped `src/tfm_lakehouse/orcid_client/` instead (see that issue's own
Implementation Performed section) without the epic's suggested layout being
revised at the time. `#95` follows that already-established real convention
(one dedicated package per ORCID data-access concern) rather than the
epic's unrevised original suggestion, for consistency with what `#94`
actually built.

**Decision: single full streaming pass over the 46.3 GB file, no early-stop
cap.** `tarfile` in streaming mode (`r|gz`) reads the gzip stream
sequentially -- there is no random access into a remote gzip stream, so every
byte must be read once regardless of filter outcome. Stopping early once N
matches are found would bias the sample: entries are bucketed by the last
three digits of the ORCID iD checksum, not by country, but registration
chronology is not guaranteed uniform across that keyspace either, so an
early stop cannot be assumed representative. A full pass collects every
Spain-affiliated match; an optional post-hoc downsample (plain random
sampling over the complete match set) is available afterward if the full
matched set turns out larger than convenient, without needing to re-download
anything.

**Decision: MD5 checksum verification against Figshare's `supplied_md5`
before extraction.** Cheap, already provided by the API response, and
guards against a corrupted/partial 46.3 GB download silently producing a
truncated or garbled filtered subset.

**Clarification on dataset size (2026-09-18):** the full 2025 dataset
(all 12 files) is 237.73 GB decimal = 221.41 GiB binary, which is the
"221 GB" figure shown by tools that report GiB as "GB". The summaries file
alone is 46,328,319,190 bytes (46.33 GB / 43.14 GiB). Only that one file is
used, per the decision above.

**Adjustment: read the archive from a local file, not only via streaming
HTTP.** The first Task 5 attempt streamed the file from Figshare and, after
33 minutes, had read 3.57 GB of 46.33 GB (7.7%, ~1.8 MB/s), projecting ~7 h
total. It was cancelled and the archive was downloaded manually with a
faster connection into `data/orcid_bulk/raw/` (git-ignored). To support
this, `fetch_orcid_bulk_subset_from_local_file` was added next to
`fetch_orcid_bulk_subset`; both share one tar-walk/filter core
(`_walk_tar_and_filter`) so the filter logic exists once. The streaming
function stays for a fully automated, no-manual-step path (and is what the
live smoke test exercises).

**Adjustment (found while measuring): the run is CPU-bound, not
network-bound, so a byte-level prefilter was added.** Processing the local
file was still only ~1,253 records/s (100k-entry sample), i.e. ~5.5 h for
~25M records, so a faster download alone would not have helped. Splitting
the cost on the same 100k sample: gunzip + tar + a bytes-substring check ran
at 9,746 records/s, i.e. XML parsing (`ElementTree`) was ~87% of the
runtime. `_has_matching_country` now first checks that the record's bytes
contain `>{country}</common:country>` and only then parses. This is a
superset test (the same element also appears in person-level addresses), so
it can over-match but never under-match the real affiliation path, which the
parse still confirms. Measured on the same 100k sample: 8,966 records/s and
1,229 confirmed matches, identical to the full-parse run (1,229), i.e.
lossless there. Assumption to keep in mind: it relies on ORCID serializing
the element as `<common:country>XX</common:country>` (true across every
entry inspected in Task 1 and the samples above). A unit test covers the
"ES only outside the affiliation path" case.

**Adjustment (found on the first full local run): unbounded memory growth
and I/O-bound writes.** The first full local run showed `top` at ~42% of a
single core (16 available, ~94% idle, process in `D` state), i.e. waiting on
disk, not on CPU, and its RSS had reached 4.7 GB at 6.4M entries and was
still growing. Cause: `tarfile` keeps every `TarInfo` it has read in
`TarFile.members`, ~730 bytes per entry, which projected to ~18 GB over the
~26M entries and would have exhausted the 16 GB machine's memory. Two fixes
in `_walk_tar_and_filter`: `tf.members.clear()` on every iteration (RSS
stays ~90-105 MB for the whole run), and matched entries are written from a
`ThreadPoolExecutor` (8 workers, at most 1,000 pending writes so memory
stays bounded, exceptions surfaced via `Future.result()`) so per-file writes
on the Windows-mounted `/mnt/e` drive no longer stall the read loop.
Benchmarked on the first 300k real entries writing to `/mnt/e`: ~5,471
records/s versus ~3,000 before. Decompression itself stays single-threaded
because one gzip stream cannot be split, so "use all cores" is only
partially achievable here (writes yes, gunzip no). The interrupted run was
discarded and restarted from an empty output directory.

**Adjustment: MD5 is verified while streaming, after the pass, not before
extraction.** The original decision text said "before extraction", but a
single sequential pass cannot know the digest until the last byte is read,
so the hash is computed incrementally as bytes pass through and compared at
the end. Consequence: on a mismatch, `OrcidBulkChecksumError` is raised
*after* the filtered files were written, so the output directory must be
treated as invalid in that case. Skipped whenever `max_scanned` is set.

**Adjustment: `max_scanned` parameter.** Added for the live smoke test only
(stop after N entries). The real run must not use it, per the sampling-bias
decision above.

Revised task breakdown:

1. **Task 1 - verify real summary XML shape.** Pull one real record-summary
   XML entry (via a short-ranged/partial stream read of the real tar.gz, not
   a full download) and confirm the exact element path and namespace for the
   country code used by the filter. Investigation only, no code written yet.
2. **Task 2 - implement `src/tfm_lakehouse/orcid_bulk/` package**:
   streaming downloader (`requests`, `stream=True`, chunked, MD5-verified
   against `supplied_md5`) piped into a streaming `tarfile` (`r|gz`) reader
   that parses each entry's XML, checks the country path confirmed in
   Task 1, and writes matches to `data/orcid_bulk/filtered/` in the source's
   own `[3-digit]/[iD].xml` layout. Exposes one importable function callable
   later by `#97`'s planned `fetch_orcid_bulk_subset` Airflow task, not just
   a throwaway script.
3. **Task 3 - unit tests** against a small fabricated fixture tar.gz (mixed
   countries, malformed entries) covering the filter logic, MD5-mismatch
   handling, and streaming behavior, without touching the network.
4. **Task 4 - live smoke test**, gated behind an env var
   (`ORCID_LIVE_TEST=1`, matching `#94`'s existing pattern), that streams a
   small real slice of the real Figshare file to confirm the real endpoint,
   real compression, and real XML shape all work end to end, without
   requiring the full 46.3 GB in CI.
5. **Task 5 - full real run** against the complete real summaries file,
   confirming it parses correctly end to end and that the Spain-affiliated
   subset lands at the expected order of magnitude (not the full
   multi-million-record file), per this issue's own Verification section.
   Resource-heavy (bandwidth/time for a 46.3 GB single-pass download);
   requires explicit go-ahead before starting, not folded silently into
   Task 2-4.
6. **Task 6 - documentation update**, per `AGENTS.md`'s Documentation Update
   Protocol: this issue document's own Implementation/Verification/Findings/
   Status sections, `docs/context/tfm/current_status.md`,
   `docs/roadmap/tfm/tfm_roadmap.md` status flip, `known_limitations.md` if
   a new limitation surfaces, `PROJECT_GUIDE.md` for the new
   `src/tfm_lakehouse/orcid_bulk/` path, and `.gitignore` for the new
   `data/` working directory.

## Implementation Performed

- **Task 1 (done):** streamed the first entries of the real 2025 summaries
  file (connection closed after the first few entries, no full download) and
  confirmed the country path against real records: `employment:employment-
  summary` -> `common:organization` -> `common:address` -> `common:country`
  (ISO 3166 alpha-2, e.g. `IT`, `US`), namespaces
  `http://www.orcid.org/ns/{common,employment,education,record}`. Entries
  are laid out as `ORCID_2025_10_summaries/<3-digit>/<iD>.xml`.
- **Task 2 (done):** new package `src/tfm_lakehouse/orcid_bulk/`
  (`pipeline.py`, `exceptions.py`, `__init__.py`): `fetch_orcid_bulk_subset`
  (streaming), `fetch_orcid_bulk_subset_from_local_file`, shared
  `_walk_tar_and_filter`, `OrcidBulkSubsetResult`, `OrcidBulkChecksumError`,
  byte-level prefilter. Output layout drops the archive's outer folder and
  keeps `<3-digit>/<iD>.xml`. No new dependency (`requests` was already
  present; `tarfile`/`xml.etree` are stdlib).
- **Task 3 (done):** `tests/test_orcid_bulk_pipeline_unit.py`, 7 tests on a
  fabricated in-memory tar.gz (country filter, multi-country, checksum
  mismatch and skip, local-file path and its mismatch, country outside the
  affiliation path not matched); no network.
- **Task 4 (done):** `tests/test_orcid_bulk_pipeline_live_smoke.py`, gated
  behind `ORCID_LIVE_TEST=1` (same pattern as issue `#94`), streams the first
  2,000 real entries. Skipped by default; passed live in 3.8 s.
- **Task 5 (done):** full single pass over the real
  `ORCID_2025_10_summaries.tar.gz` placed at
  `data/orcid_bulk/raw/` (46,328,319,190 bytes, size matches the Figshare
  API), filter `ES`, output `data/orcid_bulk/filtered/`. Result:
  26,078,951 records scanned, 301,763 matched (1.157%), 4,898 s (81.6 min),
  MD5 verified against Figshare's `210edf71f4a2bb44dd33aaa3037b3f17`
  (no `OrcidBulkChecksumError`, exit code 0). 301,763 `.xml` files counted
  on disk, equal to the reported match count.
- **Task 6 (done):** `.gitignore` (`data/`), `PROJECT_GUIDE.md`, this
  document, `docs/context/tfm/current_status.md`,
  `docs/roadmap/tfm/tfm_roadmap.md` and `docs/pipeline/known_limitations.md`.

## Verification

- `uv run pytest tests/test_orcid_bulk_pipeline_unit.py -q` -- 7 passed
- `uv run pytest tests/test_orcid_bulk_pipeline_live_smoke.py -q` -- 1
  skipped by default (no network in the default/CI path);
  `ORCID_LIVE_TEST=1` -- 1 passed against the real Figshare file (first
  2,000 entries)
- full run against the complete real file: every one of the 26,078,951
  entries parsed without error; the archive's MD5 matched Figshare's
  `supplied_md5`; the subset is 301,763 records (1.157% of the file), the
  expected order of magnitude (hundreds of thousands, not the ~26M of the
  full file); the on-disk file count equals the reported match count
- the byte-level prefilter was checked for losslessness on a 100k-entry
  sample (1,229 matches with and without it), not against the full file

## Findings

- the ORCID 2025 Public Data File is hosted on Figshare
  (`orcid.figshare.com`, DOI `10.6084/m9.figshare.30375589`), not S3; the
  full dataset is 12 files, 221.41 GiB (237.73 GB); the summaries file
  alone is 46.33 GB and holds ~26.08M records
- Spain-affiliated records (`ES` on any employment or education entry) are
  ~1.16% of the registry: 301,763 records
- processing cost is dominated by XML parsing, not decompression: gunzip +
  tar + a bytes-substring check ran ~7.8x faster than parsing every entry,
  and a substring prefilter recovers almost all of it
- `tarfile` streaming mode leaks memory linearly in the number of entries
  unless `TarFile.members` is cleared (4.7 GB at 6.4M entries); this would
  have crashed a full run on a 16 GB machine
- the first full-file attempt over HTTP projected ~7 h at ~1.8 MB/s; a
  manual download to `data/orcid_bulk/raw/` plus the optimizations above
  brought the whole pass to 81.6 min

## Known Limitations

Per the epic, processing the full public data file at web scale is
explicitly deferred to future work; only a filtered subset is in scope here.
Additional limitations, recorded in `docs/pipeline/known_limitations.md`:
the subset is a frozen October 2025 snapshot; "Spain-affiliated" means any
employment/education entry with country `ES` (any date), not current
affiliation; the prefilter assumes ORCID's exact `<common:country>`
serialization; and a checksum mismatch is detected only after the filtered
files were written.

## Impact On Future Issues

Feeds issue `#97` (bronze landing) as the ORCID bulk source, and indirectly
issue `#101` (benchmark), which needs a real base volume to scale from.

Practical notes for `#97`: the subset lives in the git-ignored
`data/orcid_bulk/filtered/` as 301,763 individual XML files laid out as
`<3-digit>/<iD>.xml` (source: ORCID 2025 summaries, October 2025 snapshot).
Landing 300k small files into MinIO one object at a time is likely slow, so
`#97` should consider batching/packing them (for example converting to a
columnar file) rather than mirroring the per-file layout. The entry points
are `fetch_orcid_bulk_subset` (streams from Figshare) and
`fetch_orcid_bulk_subset_from_local_file`, both in
`tfm_lakehouse.orcid_bulk`. Issue `#96` can read seed fields from the same
directory.

## Status

`Completed`
