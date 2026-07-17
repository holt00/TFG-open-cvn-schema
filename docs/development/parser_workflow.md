# Parser Workflow

## Purpose

This guide shows contributors how to use and verify the public Open CVN parser
and validator workflow implemented by issues `#47`, `#48`, and `#49`.

Use this guide when you need to:

- validate an Open CVN JSON document
- import direct CVN XML into the current semantic partial Open CVN shape
- extract embedded CVN XML from a PDF
- inspect structured parser errors and trace metadata
- run parser-focused regression tests

This guide does not define new parser behavior. The public contract remains
documented in `docs/pipeline/parser_validator_contract.md`.

## Public API

Import parser entry points from `open_cvn`:

```python
from open_cvn import (
    CvnErrorCode,
    CvnValidationStatus,
    parse_cvn_pdf,
    parse_cvn_xml,
    parse_open_cvn_json,
    validate_open_cvn_json,
)
```

Each parser returns `CvnParseResult` with:

- `source_format`
- `source_identifier`
- `data`
- `validation_status`
- `warnings`
- `errors`
- `trace`

Treat `validation_status` as the workflow decision point:

- `valid`: input was accepted
- `valid_with_warnings`: input was accepted, but warning issues exist
- `invalid`: input was read and classified as invalid
- `failed`: processing could not complete
- `not_run`: extraction succeeded, but validation was intentionally not executed

## Open CVN JSON

Parse JSON from a path:

```python
from pathlib import Path

from open_cvn import CvnValidationStatus, parse_open_cvn_json

result = parse_open_cvn_json(Path("examples/open_cvn/minimal.json"))

if result.validation_status == CvnValidationStatus.VALID:
    document = result.data
```

Parse inline JSON text or bytes:

```python
from open_cvn import parse_open_cvn_json

result_from_text = parse_open_cvn_json(
    '{"schema_version":"0.1.0","metadata":{"language":"es","policy":{"name":"default_cvn_semantic_policy","version":"0.1.0"}},"curriculum":{"identity":{},"education":[],"research":[],"professional_experience":[],"achievements":[],"other":[]}}',
    source_identifier="inline-json",
)

result_from_bytes = parse_open_cvn_json(
    b'{"schema_version":"0.1.0","metadata":{"language":"es","policy":{"name":"default_cvn_semantic_policy","version":"0.1.0"}},"curriculum":{"identity":{},"education":[],"research":[],"professional_experience":[],"achievements":[],"other":[]}}',
    source_identifier="bytes-json",
)
```

Validate an already-loaded mapping:

```python
from open_cvn import validate_open_cvn_json

document = {
    "schema_version": "0.1.0",
    "metadata": {
        "language": "es",
        "policy": {
            "name": "default_cvn_semantic_policy",
            "version": "0.1.0",
        },
    },
    "curriculum": {
        "identity": {},
        "education": [],
        "research": [],
        "professional_experience": [],
        "achievements": [],
        "other": [],
    },
}

result = validate_open_cvn_json(document, source_identifier="loaded-document")
```

Validation order is:

1. JSON decoding for string, bytes, or path inputs
2. generated JSON Schema validation against `schemas/open_cvn.schema.json`
3. Pydantic runtime validation through `src/open_cvn/open_cvn_models.py`

JSON errors use these codes:

- `invalid_json`: malformed JSON text
- `json_schema_validation_failure`: document does not match the generated schema
- `pydantic_validation_failure`: document reaches runtime model validation but
  violates runtime rules, or the loaded JSON value is not an object
- `unreadable_file`: path-like input cannot be read
- `unsupported_input_format`: unsupported source shape

## Direct CVN XML

Parse direct XML from a path:

```python
from pathlib import Path

from open_cvn import CvnValidationStatus, parse_cvn_xml

result = parse_cvn_xml(Path("tests/fixtures/cvn_xml/minimal_cvn.xml"))

if result.validation_status == CvnValidationStatus.VALID:
    open_cvn_document = result.data
    cvn_codes = result.trace.cvn_codes if result.trace else ()
```

Parse inline XML text or bytes:

```python
from open_cvn import parse_cvn_xml

result_from_text = parse_cvn_xml(
    "<CVNRoot><CVNItem><Value>000.010.000.000</Value></CVNItem></CVNRoot>",
    source_identifier="inline-xml",
)

result_from_bytes = parse_cvn_xml(
    b"<CVNRoot><CVNItem><Value>000.010.000.000</Value></CVNItem></CVNRoot>",
    source_identifier="bytes-xml",
)
```

Current XML import behavior is conservative semantic partial import:

- validates XML well-formedness
- checks for plausible CVN evidence
- preserves simplified XML paths
- preserves CVN code-like values when detected
- maps recognized `CvnItem` group and field codes into canonical Open CVN
  curriculum sections using `schemas/open_cvn.schema.json` annotations
- validates generated Open CVN JSON through `validate_open_cvn_json(...)`
- preserves unmapped source items in trace/extensions or `curriculum.other[]`
- does not perform complete semantic XML-to-domain mapping for every CVN edge case

For plausible CVN XML, `data["extensions"]["x-open-cvn.xml_import"]` records
`mapping_status = "semantic_partial"` when at least one item maps. Inputs with
CVN evidence but no recognized semantic items may still report
`mapping_status = "trace_only"`. Treat either status as an import diagnostic,
not proof that all curriculum content was converted.

XML errors use these codes:

- `invalid_xml`: XML is malformed
- `xml_semantically_unmappable`: XML is well-formed but lacks enough CVN evidence
  for the current importer
- `unreadable_file`: path-like input cannot be read
- `unsupported_input_format`: unsupported source shape

## CVN PDF

Parse a PDF path or PDF bytes:

```python
from pathlib import Path

from open_cvn import CvnValidationStatus, parse_cvn_pdf, parse_cvn_xml

pdf_result = parse_cvn_pdf(Path("cvn.pdf"))

if pdf_result.validation_status == CvnValidationStatus.NOT_RUN:
    xml_text = pdf_result.data["xml_text"]
    xml_result = parse_cvn_xml(xml_text, source_identifier="cvn.pdf:extracted-xml")
```

PDF handling is extraction-only:

- scans embedded PDF files first
- scans PDF XML metadata second
- accepts only well-formed XML with plausible CVN evidence
- returns `validation_status = not_run` for successful extraction
- stores extracted XML in `data["xml_text"]`
- stores extraction metadata in `data["extraction"]`
- leaves XML interpretation to `parse_cvn_xml(...)`

PDF handling does not attempt OCR or page text reconstruction. When
`validate_extracted_xml=True`, extracted XML is handed to `parse_cvn_xml(...)`,
which can now produce semantic partial Open CVN JSON before any configured LLM
fallback is considered.

PDF errors use these codes:

- `pdf_without_extractable_xml`: readable PDF has no acceptable CVN XML candidate
- `unreadable_file`: PDF input cannot be opened or read
- `unsupported_input_format`: unsupported source shape, such as a mapping

## Structured Errors

Inspect `errors` for machine-readable handling:

```python
from open_cvn import CvnErrorCode, CvnValidationStatus, parse_open_cvn_json

result = parse_open_cvn_json("{", source_identifier="broken-json")

if result.validation_status in {CvnValidationStatus.INVALID, CvnValidationStatus.FAILED}:
    for issue in result.errors:
        if issue.code == CvnErrorCode.INVALID_JSON:
            print(issue.source_location)
```

Each issue includes:

- `code`
- `severity`
- `message`
- `source_location`
- `path`
- `details`

Do not parse exception strings as control flow. Use `code` and `path` first.

## Trace Metadata

Parser trace is audit metadata. It does not change curriculum values.

Common trace fields include:

- `source_format`
- `source_identifier`
- `source_path`
- `extracted_from`
- `cvn_codes`
- `xml_paths`
- `schema_version`
- `policy_name`
- `policy_version`

Expected trace behavior:

- JSON import preserves `schema_version` and `metadata.policy` values when present
- XML import preserves simplified XML paths and detected CVN code-like values
- PDF import preserves PDF identity and extracted XML source identity
- error results should keep source trace where available without copying full
  personal payloads into diagnostics

## Verification Commands

Run parser-focused tests:

```bash
uv run pytest -n auto tests/test_parser_validator_contract_unit.py tests/test_pdf_xml_extraction_unit.py tests/test_open_cvn_json_import_unit.py tests/test_cvn_xml_import_unit.py -v
```

Run JSON Schema and Open CVN example tests:

```bash
uv run pytest -n auto tests/test_json_schema_generator_unit.py tests/test_generation_pipeline_json_schema.py tests/test_open_cvn_json_format_examples.py -v
```

Run conceptual model and diagram tests:

```bash
uv run pytest -n auto tests/test_conceptual_model_extractor_unit.py tests/test_generation_pipeline_conceptual_model.py tests/test_conceptual_model_diagrams_unit.py tests/test_generation_pipeline_conceptual_diagrams.py -v
```

Run full repository verification:

```bash
uv run pytest -n auto tests
```

## Related Documentation

- parser contract: `docs/pipeline/parser_validator_contract.md`
- Open CVN JSON format: `docs/pipeline/open_cvn_json_format.md`
- JSON Schema generation: `docs/pipeline/json_schema_generation.md`
- conceptual extraction: `docs/pipeline/conceptual_model_extraction.md`
- regeneration workflow: `docs/development/regeneration_workflow.md`
- known limitations: `docs/pipeline/known_limitations.md`
