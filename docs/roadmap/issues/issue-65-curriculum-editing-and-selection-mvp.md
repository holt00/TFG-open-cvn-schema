# Issue 65 - Implement Curriculum Editing And Selection MVP

## Summary

Issue `#65` adds minimal editing and selection operations needed to customize a
derived curriculum version from a master curriculum.

This issue is part of epic `#60`.

## Goal

- provide basic user-facing customization of derived CV versions
- avoid a full GUI editor in the MVP
- keep edits auditable and easy to export
- preserve Open CVN JSON validity after edits

## MVP Editing Direction

The MVP should prioritize coarse operations over a full nested JSON editor:

- list curriculum sections and entries
- include or exclude sections
- include or exclude individual entries when entries have stable IDs or indexes
- optionally apply simple metadata edits such as derived version name or purpose
- optionally apply explicit field overrides only when they can be validated

## Planned Scope

- CLI commands for listing curriculum sections and entries
- CLI commands for include/exclude selection in derived versions
- optional command for setting derived version metadata
- validation of materialized derived Open CVN JSON after edits
- clear unsupported messages for field-level edits not implemented in MVP

## Planned Steps

1. define selection command grammar
2. implement section listing
3. implement entry listing with stable display identifiers
4. implement include/exclude section behavior
5. implement include/exclude entry behavior where feasible
6. validate derived document after selection changes
7. add tests for selection behavior and invalid selectors
8. document editing limitations

## Detailed Execution Plan

This plan is the accepted execution plan for implementing issue `#65`.
During execution, each work update must identify the active task and, when
applicable, the active subtask. Each task or subtask update should include:

- initial summary of the task or subtask goal
- current task and subtask identifier
- whether the user must modify any file manually
- next step to follow

Unless explicitly requested otherwise, code edits are expected to be performed by
the user. Documentation edits may be applied when the user asks to establish or
update the issue plan.

### Task 1 - Confirm Scope And Constraints

- Subtask 1.1: confirm issue `#65` builds user-facing editing and selection UX on
  top of the issue `#63` versioning repository behavior instead of rewriting the
  storage or materialization core.
- Subtask 1.2: confirm existing `versions include NAME POINTER` and
  `versions exclude NAME POINTER` commands remain the canonical include/exclude
  mutation commands.
- Subtask 1.3: confirm selectors continue to use JSON Pointer syntax and remain
  restricted to `/curriculum` section or entry paths.
- Subtask 1.4: confirm field-level edits are unsupported in the MVP and must fail
  with a clear message.
- Subtask 1.5: confirm materialized Open CVN JSON is validated through
  `validate_open_cvn_json(...)` after selection or metadata changes where
  applicable.
- Subtask 1.6: confirm `src/generated/` remains untouched.

Expected output: final implementation boundary for issue `#65` before code work.

### Task 2 - Define Selection Command Grammar

- Subtask 2.1: keep JSON Pointer as the canonical selector representation.
- Subtask 2.2: document section selectors such as `/curriculum/research`.
- Subtask 2.3: document entry selectors such as `/curriculum/research/0`.
- Subtask 2.4: follow RFC 6901 pointer rules for `/`, `~0`, `~1`, object tokens,
  and zero-based array indexes.
- Subtask 2.5: reject root, metadata, extensions, and bare `/curriculum` selectors
  for issue `#65` selection edits.
- Subtask 2.6: display entry `id` values where present but keep the JSON Pointer
  as the selector that commands consume.
- Subtask 2.7: use entry indexes as the stable MVP fallback when an entry lacks an
  explicit `id`.

Expected output: deterministic command grammar and selector rules for CLI help,
tests, and documentation.

### Task 3 - Implement Curriculum Inspection Support

- Subtask 3.1: add a small inspection layer in `src/open_cvn_app/storage.py` or a
  focused helper module under `src/open_cvn_app/`.
- Subtask 3.2: expose an operation to list curriculum sections for a materialized
  version.
- Subtask 3.3: expose an operation to list entries inside a repeated curriculum
  section for a materialized version.
- Subtask 3.4: derive inspection results from `CurriculumRepository.materialize_version(...)`
  so derived selections are reflected in user-facing output.
- Subtask 3.5: preserve deterministic ordering from the Open CVN JSON
  `curriculum` object.
- Subtask 3.6: return section metadata including name, pointer, value kind, and
  entry count when applicable.
- Subtask 3.7: return entry metadata including index, pointer, optional `id`,
  optional `type`, compact summary, and trace CVN codes when present.

Expected output: reusable inspection behavior for CLI listing commands without a
GUI editor.

### Task 4 - Define Entry Summary Rules

- Subtask 4.1: show `entry["id"]` when present and `-` when absent.
- Subtask 4.2: show `entry["type"]` when present and `-` when absent.
- Subtask 4.3: build a compact summary from the first simple scalar fields under
  `entry["data"]`.
- Subtask 4.4: use `-` when no simple scalar summary is available.
- Subtask 4.5: show CVN codes from `entry["trace"]["cvn_codes"]` when present.
- Subtask 4.6: avoid adding heavy heuristics or new runtime dependencies for
  summary generation.

Expected output: stable, human-readable entry listing suitable for choosing
include/exclude pointers.

### Task 5 - Implement Section Listing CLI

- Subtask 5.1: add `open-cvn versions sections NAME [--store PATH]` to
  `src/open_cvn_app/cli.py`.
- Subtask 5.2: resolve the local store path through `OpenCvnAppConfig`.
- Subtask 5.3: load the requested version through the inspection behavior.
- Subtask 5.4: print a deterministic section listing with names, pointers, and
  entry counts or value kinds.
- Subtask 5.5: return `No curriculum sections found.` for empty curriculum
  objects.
- Subtask 5.6: convert storage and selection failures into
  `AppResult.failed("Section listing failed.", error=str(exc))`.

Expected output: users can discover section-level selectors before applying
include/exclude commands.

### Task 6 - Implement Entry Listing CLI

- Subtask 6.1: add `open-cvn versions entries NAME SECTION [--store PATH]` to
  `src/open_cvn_app/cli.py`.
- Subtask 6.2: accept both `research` and `/curriculum/research` as the `SECTION`
  argument.
- Subtask 6.3: normalize section arguments to a canonical `/curriculum/<section>`
  pointer.
- Subtask 6.4: reject missing sections with a clear error.
- Subtask 6.5: reject non-list curriculum sections such as `identity` with a clear
  unsupported message.
- Subtask 6.6: print deterministic entry lines with index, pointer, id, type,
  summary, and CVN codes.
- Subtask 6.7: return `No entries found in section '<section>'.` for empty
  repeated sections.

Expected output: users can discover entry-level selectors without manually
opening Open CVN JSON files.

### Task 7 - Implement Derived Version Metadata Editing

- Subtask 7.1: store optional derived-version metadata without adding a new table
  when possible by extending deterministic selection JSON.
- Subtask 7.2: preserve compatibility with existing selection JSON that lacks
  metadata.
- Subtask 7.3: support metadata keys for MVP display name and purpose.
- Subtask 7.4: add repository behavior to update derived-version metadata.
- Subtask 7.5: reject metadata updates against the master version unless a later
  decision deliberately expands the scope.
- Subtask 7.6: include derived metadata in
  `extensions["x-open-cvn.versioning"]` during materialization.
- Subtask 7.7: validate materialized Open CVN JSON after metadata changes.

Expected output: derived versions can carry auditable human-facing purpose or name
metadata without implementing a full editor.

### Task 8 - Implement Metadata CLI

- Subtask 8.1: add `open-cvn versions metadata NAME [--store PATH]
  [--display-name TEXT] [--purpose TEXT]` to `src/open_cvn_app/cli.py`.
- Subtask 8.2: when no metadata options are passed, show current derived metadata.
- Subtask 8.3: when metadata options are passed, update the derived metadata.
- Subtask 8.4: print deterministic output with version name, display name, and
  purpose.
- Subtask 8.5: convert storage and validation failures into
  `AppResult.failed("Version metadata update failed.", error=str(exc))` or a
  similarly specific message.

Expected output: users can set and inspect simple derived-version metadata from
the CLI.

### Task 9 - Implement Unsupported Field-Edit Command

- Subtask 9.1: add an explicit CLI command such as
  `open-cvn versions field-edit NAME POINTER VALUE [--store PATH]`.
- Subtask 9.2: return exit code `1` for this command in issue `#65`.
- Subtask 9.3: print a clear message that field-level edits are not supported in
  the MVP and users should use section or entry include/exclude selection instead.
- Subtask 9.4: ensure the command does not mutate storage.

Expected output: unsupported fine-grained editing fails clearly instead of being
absent or ambiguous.

### Task 10 - Validate Selection Changes Immediately

- Subtask 10.1: after `versions include`, materialize the edited version to verify
  the selected document remains valid.
- Subtask 10.2: after `versions exclude`, materialize the edited version to verify
  the selected document remains valid.
- Subtask 10.3: preserve existing successful command messages where possible.
- Subtask 10.4: fail clearly if materialization validation fails after a selection
  change.
- Subtask 10.5: keep master curriculum payload immutable after derived selection
  edits.

Expected output: users get immediate validation feedback after selection edits,
not only during later export.

### Task 11 - Add Editing And Inspection Unit Tests

- Subtask 11.1: add a focused test module such as
  `tests/test_open_cvn_app_editing_unit.py`.
- Subtask 11.2: test section listing against representative Open CVN examples.
- Subtask 11.3: test entry listing for entries with `id`, `type`, summary, pointer,
  and CVN codes.
- Subtask 11.4: test entry listing fallback when an entry lacks `id`.
- Subtask 11.5: test empty repeated-section listing.
- Subtask 11.6: test non-list sections are rejected for entry listing.
- Subtask 11.7: test derived metadata update and materialized extension output.
- Subtask 11.8: test unsupported field-edit behavior does not mutate data if the
  implementation exposes a repository-level guard.
- Subtask 11.9: test invalid selectors fail clearly.

Expected output: unit tests cover inspection, metadata, unsupported edits, and
invalid selector behavior.

### Task 12 - Update CLI Tests

- Subtask 12.1: extend `tests/test_open_cvn_app_cli_unit.py` for
  `versions sections`.
- Subtask 12.2: extend CLI tests for `versions entries` with a plain section name.
- Subtask 12.3: extend CLI tests for `versions entries` with a full section
  pointer.
- Subtask 12.4: test empty entry listing after excluding a section or when a
  section has no entries.
- Subtask 12.5: test metadata show and update behavior.
- Subtask 12.6: test unsupported `versions field-edit` returns exit code `1` and a
  clear message.
- Subtask 12.7: test missing version, missing section, and non-list section error
  paths.
- Subtask 12.8: keep existing JSON import/export, versioning, LaTeX placeholder,
  and PDF placeholder tests passing.

Expected output: CLI tests prove user-facing issue `#65` behavior.

### Task 13 - Prepare Or Extend Fixtures

- Subtask 13.1: reuse `examples/open_cvn/research_entry.json` where possible.
- Subtask 13.2: reuse `examples/open_cvn/education_entry.json` where possible.
- Subtask 13.3: add a small deterministic fixture only if multi-entry or missing
  `id` behavior cannot be tested clearly with existing examples.
- Subtask 13.4: place any new Open CVN JSON test fixture under
  `tests/fixtures/open_cvn/`.
- Subtask 13.5: keep any new fixture valid against the Open CVN JSON validator.

Expected output: representative test data for section and entry listing without
overbuilding fixtures.

### Task 14 - Run Targeted Verification

- Subtask 14.1: run editing tests:
  `uv run pytest -n auto tests/test_open_cvn_app_editing_unit.py -v`.
- Subtask 14.2: run CLI tests:
  `uv run pytest -n auto tests/test_open_cvn_app_cli_unit.py -v`.
- Subtask 14.3: run storage and versioning regressions:
  `uv run pytest -n auto tests/test_open_cvn_app_storage_unit.py tests/test_open_cvn_app_versioning_unit.py -v`.
- Subtask 14.4: run parser contract regressions:
  `uv run pytest -n auto tests/test_open_cvn_json_import_unit.py tests/test_parser_validator_contract_unit.py -v`.
- Subtask 14.5: record exact results in this issue document.

Expected output: targeted issue behavior and dependencies pass.

### Task 15 - Run Console Script Smoke Verification

- Subtask 15.1: initialize a temporary smoke store under `/tmp/opencode`.
- Subtask 15.2: import `examples/open_cvn/research_entry.json` as master.
- Subtask 15.3: create a derived version named `public`.
- Subtask 15.4: list sections for the derived version.
- Subtask 15.5: list entries for the `research` section.
- Subtask 15.6: exclude `/curriculum/research/0` from the derived version.
- Subtask 15.7: export the derived version as Open CVN JSON.
- Subtask 15.8: confirm the exported derived JSON validates and omits the excluded
  entry.

Expected output: installed CLI proves the editing and selection workflow outside
direct unit tests.

### Task 16 - Run Full Repository Verification

- Subtask 16.1: run `uv run pytest -n auto tests`.
- Subtask 16.2: record the exact pass/fail result in this issue document.
- Subtask 16.3: if full verification cannot be completed, record the skipped
  command and reason.

Expected output: full repository verification passes or a documented reason is
available.

### Task 17 - Update Persistent Documentation

- Subtask 17.1: update this issue document with actual implementation artifacts,
  deviations, verification, and status.
- Subtask 17.2: update `docs/context/current_status.md` so issue `#65` is recorded
  accurately and issue `#66` becomes the next implementation issue if `#65` is
  completed.
- Subtask 17.3: update `docs/roadmap/cvn_generation_roadmap.md` if it tracks issue
  `#65` status.
- Subtask 17.4: update `docs/pipeline/known_limitations.md` only if a new durable
  limitation is found.
- Subtask 17.5: update `PROJECT_GUIDE.md` only if repository orientation,
  contributor reading order, or the documentation map changes.

Expected output: repository context remains resumable after issue completion.

## Planned Issue 65 CLI Shape

```text
open-cvn versions sections NAME [--store PATH]
open-cvn versions entries NAME SECTION [--store PATH]
open-cvn versions metadata NAME [--store PATH] [--display-name TEXT] [--purpose TEXT]
open-cvn versions field-edit NAME POINTER VALUE [--store PATH]
```

Existing selection mutation commands from issue `#63` remain part of the editing
workflow:

```text
open-cvn versions include NAME POINTER [--store PATH]
open-cvn versions exclude NAME POINTER [--store PATH]
```

## Planned Selector Rules

- Selectors use JSON Pointer syntax from RFC 6901.
- Section selectors target `/curriculum/<section>`.
- Entry selectors target `/curriculum/<section>/<index>`.
- Entry indexes are zero-based JSON array indexes.
- Entry `id` values are displayed when present, but pointers remain the canonical
  command selectors for the MVP.
- Field-level selectors below an entry may be displayed in future work but are not
  editable in issue `#65`.

## Planned Unsupported Field Edit Message

Fine-grained field editing should fail clearly in issue `#65`, with wording close
to:

```text
Field-level edits are not supported in issue #65 MVP.
Use include/exclude section or entry selection instead.
```

## Definition Of Done

- Users can list curriculum sections for a master or derived version.
- Users can list repeated entries in a curriculum section and see stable selection
  pointers.
- Users can include or exclude discovered section and entry pointers using the
  existing selection commands.
- Selection changes are validated through materialized Open CVN JSON.
- Users can inspect and update simple derived-version metadata such as display name
  or purpose.
- Unsupported field-level edits fail with a clear message.
- Tests cover section listing, entry listing, include/exclude validation, metadata,
  unsupported field edits, and invalid selectors.
- Console-script smoke verification covers the user-facing selection workflow.
- Full repository verification passes or a documented reason is recorded.
- Persistent documentation is updated in the same session as the implementation.

## Expected Output

- selection/editing CLI commands
- tests for derived version customization
- documented MVP editing behavior

## Verification

- users can remove a section from a derived CV
- users can remove an entry from a derived CV when entries are addressable
- exported derived JSON remains valid
- unsupported fine-grained edits fail clearly

## Impact On Later Issues

- issue `#66` exports customized derived versions to LaTeX
- later GUI work can reuse the same selection service

## Implementation Notes

- User-facing curriculum editing and selection support is implemented in:
  - `src/open_cvn_app/editing.py`
  - `src/open_cvn_app/cli.py`
  - `src/open_cvn_app/storage.py`
- The implementation builds on the issue `#63` selection repository behavior
  instead of replacing the storage or materialization core.
- The new inspection layer lists materialized curriculum sections and repeated
  entries for a requested master or derived version.
- Section listing exposes section names, JSON Pointer selectors, value kinds, and
  entry counts when a section is list-backed.
- Entry listing exposes zero-based index, JSON Pointer selector, optional entry
  `id`, optional entry `type`, compact summary, and trace CVN codes when present.
- Entry summaries prioritize title/name-like fields and then fall back to the next
  simple scalar data fields.
- Derived-version metadata is stored additively in deterministic selection JSON
  through optional `display_name` and `purpose` metadata keys.
- Materialized versions expose derived metadata under
  `extensions["x-open-cvn.versioning"]["metadata"]` when metadata is present.
- Existing include/exclude selection edits now materialize the edited version after
  mutation so users get immediate validation feedback.
- Fine-grained field edits are intentionally unsupported and fail through an
  explicit `versions field-edit` command without mutating stored data.
- `src/generated/` was not modified.

## Implemented CLI Behavior

Issue `#65` adds these user-facing editing and selection discovery commands:

```text
open-cvn versions sections NAME [--store PATH]
open-cvn versions entries NAME SECTION [--store PATH]
open-cvn versions metadata NAME [--store PATH] [--display-name TEXT] [--purpose TEXT]
open-cvn versions field-edit NAME POINTER VALUE [--store PATH]
```

The existing issue `#63` selection mutation commands remain functional and now
validate the materialized derived document immediately after mutation:

```text
open-cvn versions include NAME POINTER [--store PATH]
open-cvn versions exclude NAME POINTER [--store PATH]
```

## Tests Added Or Updated

- Added `tests/test_open_cvn_app_editing_unit.py`.
- Updated `tests/test_open_cvn_app_cli_unit.py`.

The new and updated tests cover:

- materialized section listing
- repeated-entry listing by section name and section pointer
- entry display identifiers, summaries, and trace CVN code output
- missing-entry-ID fallback to pointer/index display
- empty repeated sections and non-list section errors
- derived metadata update and materialized extension output
- metadata preservation across later selection edits
- unsupported field-edit behavior without storage mutation
- invalid selector and master-metadata error paths
- existing import/export, storage, versioning, LaTeX placeholder, and PDF
  placeholder regressions

## Verification Performed

- `uv run pytest -n auto tests/test_open_cvn_app_editing_unit.py -v`
  - result: `7 passed in 24.78s`
- `uv run pytest -n auto tests/test_open_cvn_app_cli_unit.py -v`
  - result: `23 passed in 26.12s`
- `uv run pytest -n auto tests/test_open_cvn_app_storage_unit.py tests/test_open_cvn_app_versioning_unit.py -v`
  - result: `18 passed in 26.31s`
- `uv run pytest -n auto tests/test_open_cvn_json_import_unit.py tests/test_parser_validator_contract_unit.py -v`
  - result: `22 passed in 25.91s`
- Console-script smoke workflow:
  - `uv run open-cvn store init --path /tmp/opencode/open-cvn-issue-65-smoke.sqlite`
  - `uv run open-cvn json import examples/open_cvn/research_entry.json --store /tmp/opencode/open-cvn-issue-65-smoke.sqlite --as-master`
  - `uv run open-cvn versions derive public --store /tmp/opencode/open-cvn-issue-65-smoke.sqlite`
  - `uv run open-cvn versions sections public --store /tmp/opencode/open-cvn-issue-65-smoke.sqlite`
  - `uv run open-cvn versions entries public research --store /tmp/opencode/open-cvn-issue-65-smoke.sqlite`
  - `uv run open-cvn versions exclude public /curriculum/research/0 --store /tmp/opencode/open-cvn-issue-65-smoke.sqlite`
  - `uv run open-cvn json export /tmp/opencode/open-cvn-issue-65-public.json --store /tmp/opencode/open-cvn-issue-65-smoke.sqlite --version public`
  - result: workflow initialized schema version `2`, imported a master document,
    created a derived version, listed sections, listed entries, excluded an entry,
    exported a valid derived JSON document, and confirmed the exported `research`
    entries were empty
- `uv run pytest -n auto tests`
  - result: `418 passed in 801.95s (0:13:21)`

## Deviations From Planned Scope

- No functional deviations.
- Derived metadata is stored in the existing `selection_json` document instead of
  adding a new SQLite table or schema version. This keeps the metadata auditable
  and avoids unnecessary migration for MVP-only fields.
- Entry summaries use a tiny title/name priority list before falling back to the
  next scalar data fields so canonical JSON key sorting does not make summaries
  less useful.

## New Limitations Found

- No new durable limitations were found.

## Impact On Later Issues After Implementation

- issue `#66` can export selected and metadata-tagged derived versions to LaTeX
- later GUI work can reuse the section/entry inspection service and repository
  selection behavior

## Status

- Status: completed
