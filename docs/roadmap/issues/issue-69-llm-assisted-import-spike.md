# Issue 69 - LLM-Assisted PDF Import For The Application MVP

## Summary

Issue `#69` implements a basic LLM-assisted import workflow for CVN PDF inputs in
the local CLI-first MVP.

The import path must remain validation-first:

```text
PDF input
-> deterministic embedded XML detection and extraction
-> XML import/validation when possible
-> LLM fallback only when XML is absent, incompatible, or not validatable
-> Open CVN JSON validation
-> local SQLite storage
```

## Scope Change From Original Spike

The original issue described a post-MVP exploratory spike. The accepted MVP plan
changes that scope to a basic implemented feature because PDF import should be
usable from the MVP application when deterministic embedded XML cannot produce a
valid Open CVN JSON document.

The implementation remains intentionally small:

- no GUI
- no background jobs
- no committed personal PDF fixtures
- no silent external LLM calls
- no database insert before Open CVN JSON validation succeeds

## Goal

- expose a CLI PDF import command for the local application MVP
- always try deterministic PDF XML extraction first
- detect whether a PDF has embedded XML or XML metadata
- use the existing XML/Open CVN validation path when deterministic import works
- call an LLM provider only when XML is missing, incompatible, or cannot validate
- send the PDF, the generated Open CVN JSON Schema, and strict system/user
  instructions to the model
- accept only JSON that validates through `validate_open_cvn_json(...)`
- store the validated JSON in the existing SQLite repository
- preserve provenance metadata for deterministic and LLM-assisted imports

## Non-Goals

- do not replace deterministic PDF/XML import with LLM import
- do not trust LLM output without local validation
- do not implement full semantic CVN XML-to-domain mapping beyond current parser
  behavior
- do not commit real personal CV PDFs
- do not require a real API call in automated tests
- do not add a GUI or multi-user server workflow

## Privacy And Safety Rules

- LLM fallback must require explicit user opt-in from the CLI before any external
  provider receives PDF content.
- API keys must come from environment variables or existing provider
  configuration; they must not be printed, persisted, or committed.
- Test coverage must use mocks or synthetic fixtures only.
- LLM output must preserve provenance metadata under an Open CVN extension, but
  raw prompts, raw PDF contents, raw API keys, and full model responses must not
  be stored by default.
- Hallucinated or schema-invalid curriculum data must fail import and leave the
  store unchanged.

## Provider Direction

- Primary MVP provider: OpenAI Responses API because it supports PDF file inputs
  and structured JSON outputs with JSON Schema.
- Secondary provider direction: OpenAI-compatible JSON-mode endpoints for future
  providers such as DeepSeek, only when the application can provide text input or
  another provider-specific file mechanism.
- Automated tests must use a mock provider and must not depend on internet access.

## Planned Files

- Create `src/open_cvn/llm_import.py` for LLM import types, prompt construction,
  schema loading, validation, and provenance wrapping.
- Create `src/open_cvn/llm_providers.py` for provider interfaces and the minimal
  OpenAI-compatible provider implementation.
- Modify `src/open_cvn/parser_contract.py` to add LLM-related error codes and
  deterministic-first PDF import orchestration.
- Modify `src/open_cvn/pdf_xml_extraction.py` only if more fallback diagnostics
  are needed.
- Modify `src/open_cvn_app/cli.py` to add `open-cvn pdf import`.
- Modify `src/open_cvn_app/storage.py` only if current diagnostics/provenance are
  insufficient.
- Modify `pyproject.toml` only if a small HTTP runtime dependency is required.
- Add or modify tests under `tests/` for parser, LLM import, PDF import, CLI, and
  MVP workflow coverage.
- Add `docs/development/llm_import_workflow.md`.
- Update persistent context and roadmap documentation after implementation.

## Execution Plan

### Task 1 - Baseline And Issue Plan

Summary: capture the accepted plan, inspect current parser/application import
behavior, and verify the starting point.

- [x] Subtask 1.1: Replace this issue document with the accepted MVP execution
  plan and scope change.
- [x] Subtask 1.2: Read parser, PDF extraction, JSON import, XML import, CLI,
  storage, and current tests before editing implementation code.
- [x] Subtask 1.3: Run targeted baseline tests for PDF extraction and CLI import.

### Task 2 - Parser Error Taxonomy

Summary: extend the public parser contract with explicit LLM-assisted import
failure modes.

- [x] Subtask 2.1: Add LLM-related `CvnErrorCode` values.
- [x] Subtask 2.2: Add parser-contract tests for new error values and result
  invariants.
- [x] Subtask 2.3: Run parser contract tests.

### Task 3 - LLM Import Core

Summary: implement validation-first LLM import logic without tying tests to a
real provider.

- [x] Subtask 3.1: Define `LlmImportConfig`, prompt structures, result helpers,
  and provider protocol.
- [x] Subtask 3.2: Load `schemas/open_cvn.schema.json` and build strict
  extraction instructions.
- [x] Subtask 3.3: Validate provider JSON through `validate_open_cvn_json(...)`.
- [x] Subtask 3.4: Add provenance metadata under
  `extensions["x-open-cvn.llm_import"]`.
- [x] Subtask 3.5: Add unit tests for valid, invalid, malformed, and provider
  failure outputs using mocks.

### Task 4 - Provider Implementation

Summary: add a minimal external provider adapter while keeping CI fully mocked.

- [x] Subtask 4.1: Add an OpenAI Responses API provider using base64 PDF input,
  schema-constrained JSON output, and environment-based API keys.
- [x] Subtask 4.2: Add safe error handling for timeout, HTTP failure, empty
  response, malformed response, and missing API key.
- [x] Subtask 4.3: Add tests using mocked HTTP/provider boundaries only.

### Task 5 - Deterministic-First PDF Import Orchestration

Summary: make PDF import prefer embedded XML and use LLM only as fallback.

- [x] Subtask 5.1: Preserve existing `parse_cvn_pdf(...)` behavior by default.
- [x] Subtask 5.2: Add opt-in LLM fallback parameters without breaking existing
  callers.
- [x] Subtask 5.3: When XML exists, call the existing XML import/validation path.
- [x] Subtask 5.4: When XML is absent, incompatible, or not validatable, call LLM
  only if explicitly enabled.
- [x] Subtask 5.5: Add tests proving deterministic XML path does not call LLM.

### Task 6 - CLI PDF Import

Summary: expose the MVP workflow through the application CLI and existing SQLite
repository.

- [x] Subtask 6.1: Add `open-cvn pdf import INPUT --store PATH [--name NAME]
  [--as-master]`.
- [x] Subtask 6.2: Add LLM options: provider, model, base URL, timeout, and
  explicit `--allow-external-llm` opt-in.
- [x] Subtask 6.3: Reuse JSON import storage behavior and master-assignment
  safeguards.
- [x] Subtask 6.4: Report deterministic vs LLM fallback source in CLI output.
- [x] Subtask 6.5: Add CLI tests for success, failure, privacy gate, duplicate
  master, and no store pollution after invalid output.

### Task 7 - End-To-End Workflow Tests

Summary: prove the MVP PDF import path works with synthetic fixtures and mocks.

- [x] Subtask 7.1: Add synthetic PDF fixtures generated in tests or built from
  non-personal test content.
- [x] Subtask 7.2: Add workflow test for PDF import through mocked LLM fallback,
  master assignment, JSON export, and revalidation.
- [x] Subtask 7.3: Add workflow test for invalid LLM output leaving storage empty.

### Task 8 - Documentation

Summary: document the user workflow, provider configuration, privacy behavior,
  and limitations.

- [x] Subtask 8.1: Add `docs/development/llm_import_workflow.md`.
- [x] Subtask 8.2: Update `docs/development/application_mvp_workflow.md` with the
  PDF import path.
- [x] Subtask 8.3: Update `docs/context/current_status.md`.
- [x] Subtask 8.4: Update `docs/pipeline/known_limitations.md` if new limitations
  remain.
- [x] Subtask 8.5: Update roadmap and entry-point maps if the new workflow doc is
  added.

### Task 9 - Verification And Closure

Summary: run targeted and full verification, then record final issue status.

- [x] Subtask 9.1: Run targeted LLM/PDF/parser/CLI tests.
- [x] Subtask 9.2: Run application MVP workflow tests.
- [x] Subtask 9.3: Run full repository test suite.
- [x] Subtask 9.4: Record verification results and final status in this issue.

## Implemented Artifacts

- `src/open_cvn/llm_import.py`: LLM import config, prompts, provider protocol,
  schema loading, validation, and provenance injection.
- `src/open_cvn/llm_providers.py`: minimal OpenAI Responses provider using
  base64 PDF input and schema-constrained JSON response instructions.
- `src/open_cvn/parser_contract.py`: LLM-related error codes and opt-in
  deterministic-first PDF import fallback orchestration.
- `src/open_cvn_app/cli.py`: `open-cvn pdf import` command with storage,
  master-assignment safeguards, LLM options, and explicit external-provider
  privacy gate.
- `tests/test_llm_import_unit.py`: mocked LLM import core tests.
- `tests/test_llm_providers_unit.py`: mocked OpenAI provider boundary tests.
- `tests/test_pdf_xml_extraction_unit.py`: deterministic-first PDF orchestration
  and fallback tests.
- `tests/test_open_cvn_app_cli_unit.py`: PDF import CLI tests.
- `tests/test_open_cvn_app_mvp_workflow.py`: MVP workflow tests for mocked LLM
  fallback success and invalid-output storage safety.
- `docs/development/llm_import_workflow.md`: user workflow and privacy guide.

## Acceptance Criteria

- PDF XML path is attempted before LLM fallback.
- LLM fallback runs only after XML is missing, incompatible, or cannot produce a
  valid Open CVN JSON document.
- External LLM calls require explicit user opt-in.
- LLM output must validate through `validate_open_cvn_json(...)` before storage.
- Invalid or malformed LLM output is reported through structured parser errors.
- Failed import does not create curricula or master versions.
- Automated tests perform no real provider calls.
- No personal PDF fixture is committed.
- CLI can import a synthetic PDF through mocked LLM fallback and export valid Open
  CVN JSON afterward.

## Verification Plan

Targeted verification:

```bash
uv run pytest -n auto tests/test_llm_import_unit.py tests/test_pdf_xml_extraction_unit.py tests/test_parser_validator_contract_unit.py tests/test_open_cvn_app_cli_unit.py -v
```

MVP workflow verification:

```bash
uv run pytest -n auto tests/test_open_cvn_app_mvp_workflow.py -v
```

Full repository verification:

```bash
uv run pytest -n auto tests
```

## Verification Performed

- Targeted LLM/PDF/parser/CLI verification:
  `uv run pytest -n auto tests/test_llm_import_unit.py tests/test_llm_providers_unit.py tests/test_pdf_xml_extraction_unit.py tests/test_parser_validator_contract_unit.py tests/test_open_cvn_app_cli_unit.py -v`
- Targeted result: `70 passed in 7.69s`
- MVP workflow verification:
  `uv run pytest -n auto tests/test_open_cvn_app_mvp_workflow.py -v`
- MVP workflow result: `5 passed in 5.26s`
- Full-suite verification:
  `uv run pytest -n auto tests`
- Full-suite result: `464 passed in 816.22s (0:13:36)`

## Status

- Status: completed
