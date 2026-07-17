# LLM-Assisted PDF Import Workflow

## Purpose

This guide describes the issue `#69` MVP workflow for importing CVN PDF files
when deterministic embedded XML extraction cannot produce importable Open CVN
JSON.

The workflow is validation-first:

```text
PDF input
-> deterministic embedded XML/XML metadata extraction
-> CVN XML import when possible
-> LLM fallback only when configured and explicitly allowed
-> Open CVN JSON validation
-> SQLite storage
```

## Privacy Rule

PDF files may contain personal data. The CLI never sends PDF content to an
external LLM provider unless both conditions are true:

- `--llm-provider` is set
- `--allow-external-llm` is passed

Do not use personal PDF fixtures in tests or commits unless explicitly approved.

## Deterministic PDF Import

Initialize a store:

```bash
uv run open-cvn store init --path /tmp/open-cvn-demo.sqlite
```

Import a PDF using only deterministic embedded XML extraction:

```bash
uv run open-cvn pdf import /path/to/cvn.pdf \
  --store /tmp/open-cvn-demo.sqlite \
  --as-master
```

If embedded XML or XML metadata is found and can be imported, the resulting Open
CVN JSON is stored. Current CVN XML import is trace-only, so embedded XML imports
may preserve trace metadata without populating all curriculum sections.

## LLM Fallback Import

Configure an OpenAI-compatible provider key through an environment variable:

```bash
export OPENAI_API_KEY=...
```

Run PDF import with explicit external-provider consent:

```bash
uv run open-cvn pdf import /path/to/cvn.pdf \
  --store /tmp/open-cvn-demo.sqlite \
  --as-master \
  --llm-provider openai \
  --llm-model gpt-4.1 \
  --allow-external-llm
```

Optional provider settings:

```bash
uv run open-cvn pdf import /path/to/cvn.pdf \
  --store /tmp/open-cvn-demo.sqlite \
  --llm-provider openai \
  --llm-model gpt-4.1 \
  --llm-base-url https://api.openai.com/v1 \
  --llm-api-key-env OPENAI_API_KEY \
  --llm-timeout 60 \
  --pdf-detail low \
  --allow-external-llm
```

The provider receives the PDF, the generated `schemas/open_cvn.schema.json`, and
strict extraction instructions. The returned JSON must validate through
`validate_open_cvn_json(...)` before it can be stored.

## Provenance

LLM-assisted imports add provenance under:

```text
extensions["x-open-cvn.llm_import"]
```

Recorded fields include provider, model, fallback reason, provider metadata, and
the validation marker. Raw prompts, raw PDF contents, API keys, and full provider
responses are not stored by default.

## Failure Behavior

Failed imports leave the local store unchanged.

Typical structured failures:

- `pdf_without_extractable_xml`: no deterministic XML and no LLM fallback
- `llm_import_disabled`: fallback requested without usable configuration
- `llm_provider_error`: provider call failed or API key is missing
- `llm_invalid_response`: provider did not return a JSON object
- `llm_output_validation_failure`: provider JSON failed local Open CVN validation

## Verification

Run LLM/PDF/parser/CLI tests:

```bash
uv run pytest -n auto \
  tests/test_llm_import_unit.py \
  tests/test_llm_providers_unit.py \
  tests/test_pdf_xml_extraction_unit.py \
  tests/test_parser_validator_contract_unit.py \
  tests/test_open_cvn_app_cli_unit.py \
  -v
```

Run MVP workflow tests:

```bash
uv run pytest -n auto tests/test_open_cvn_app_mvp_workflow.py -v
```

Run full suite:

```bash
uv run pytest -n auto tests
```
