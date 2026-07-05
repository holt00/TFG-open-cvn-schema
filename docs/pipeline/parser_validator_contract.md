# Parser And Validator Contract

## Purpose

This document records the issue `#47` public parser and validator contract for
future PDF, XML, and Open CVN JSON imports.

Issue `#47` defines the public API, result structures, error taxonomy, and trace
rules. It does not implement real PDF extraction, XML parsing, JSON Schema
validation, or domain mapping. Those responsibilities are deferred to issues
`#48` and `#49`.

## Public Package

The public runtime package is:

```text
src/open_cvn/
```

The contract implementation lives in:

```text
src/open_cvn/parser_contract.py
```

The package exports the contract through:

```python
from open_cvn import (
    CvnErrorCode,
    CvnIssueSeverity,
    CvnParseIssue,
    CvnParseResult,
    CvnParseTrace,
    CvnSourceFormat,
    CvnValidationStatus,
    parse_cvn_pdf,
    parse_cvn_xml,
    parse_open_cvn_json,
    validate_open_cvn_json,
)
```

## Public Functions

The public parser and validator entry points are:

```python
parse_cvn_pdf(source, *, source_identifier=None) -> CvnParseResult
parse_cvn_xml(source, *, source_identifier=None) -> CvnParseResult
parse_open_cvn_json(source, *, source_identifier=None) -> CvnParseResult
validate_open_cvn_json(document, *, source_identifier=None) -> CvnParseResult
```

In issue `#47`, these functions intentionally raise `NotImplementedError` with
this message:

```text
Parser implementation is deferred to issue #48/#49.
```

This makes the public contract importable without pretending that parsing already
exists.

## Source Formats

`CvnSourceFormat` values are stable JSON-serializable strings:

- `pdf`
- `cvn_xml`
- `open_cvn_json`

## Validation Status

`CvnValidationStatus` values are:

- `not_run`: validation was not attempted
- `valid`: input was accepted without warnings
- `valid_with_warnings`: input was accepted with warnings
- `invalid`: processing completed far enough to classify the input as invalid
- `failed`: processing could not complete

## Error Codes

`CvnErrorCode` values are:

- `unsupported_input_format`
- `unreadable_file`
- `pdf_without_extractable_xml`
- `invalid_xml`
- `xml_semantically_unmappable`
- `invalid_json`
- `json_schema_validation_failure`
- `pydantic_validation_failure`

Errors and warnings share `CvnParseIssue`, but their severity differs.

## Result Structure

Parser and validator functions return `CvnParseResult` once concrete
implementation exists.

Canonical fields:

- `source_format`
- `source_identifier`
- `data`
- `validation_status`
- `warnings`
- `errors`
- `trace`

Contract invariants:

- results with errors must use `invalid` or `failed`
- `valid_with_warnings` results must include at least one warning
- `warnings` must contain warning-severity issues
- `errors` must contain error-severity issues
- `data` remains broad in issue `#47`; concrete validated object shapes are
  finalized by later implementation work

## Trace Rules

`CvnParseTrace` preserves source and Open CVN evidence.

Canonical fields:

- `source_format`
- `source_identifier`
- `source_path`
- `extracted_from`
- `cvn_codes`
- `xml_paths`
- `schema_version`
- `policy_name`
- `policy_version`

Trace is metadata. It must not change curriculum values.

PDF extraction should preserve both the PDF identity and the extracted XML
identity when available. Open CVN JSON validation should preserve
`schema_version` and `metadata.policy` values when present.

## Source-Specific Responsibilities

### PDF

Issue `#48` should implement PDF handling behind `parse_cvn_pdf(...)`.

Responsibilities:

- read PDF input
- extract embedded or recoverable CVN XML when possible
- return `pdf_without_extractable_xml` when no XML can be extracted
- delegate XML interpretation to the XML import path

PDF parsing must not become the domain validator.

### XML

Issue `#49` should implement CVN XML import behind `parse_cvn_xml(...)`.

Responsibilities:

- read CVN XML input
- classify unreadable input separately from invalid XML
- preserve CVN XML trace where possible
- report `xml_semantically_unmappable` when structurally readable XML cannot map
  to Open CVN/domain representation

### JSON

Issue `#49` should implement Open CVN JSON import behind
`parse_open_cvn_json(...)` and `validate_open_cvn_json(...)`.

Responsibilities:

- classify malformed JSON as `invalid_json`
- validate the canonical issue `#46` root shape
- use the generated `schemas/open_cvn.schema.json` artifact for JSON Schema
  validation when the validation dependency is introduced
- distinguish JSON Schema validation failures from Pydantic/runtime validation
  failures

## Examples

### Successful Open CVN JSON Validation

```json
{
  "source_format": "open_cvn_json",
  "source_identifier": "examples/open_cvn/minimal.json",
  "data": {
    "schema_version": "0.1.0"
  },
  "validation_status": "valid",
  "warnings": [],
  "errors": [],
  "trace": {
    "source_format": "open_cvn_json",
    "source_identifier": "examples/open_cvn/minimal.json",
    "source_path": "examples/open_cvn/minimal.json",
    "extracted_from": null,
    "cvn_codes": [],
    "xml_paths": [],
    "schema_version": "0.1.0",
    "policy_name": "default_cvn_semantic_policy",
    "policy_version": "0.1.0"
  }
}
```

### Invalid JSON

```json
{
  "source_format": "open_cvn_json",
  "source_identifier": "broken.json",
  "data": null,
  "validation_status": "failed",
  "warnings": [],
  "errors": [
    {
      "code": "invalid_json",
      "severity": "error",
      "message": "Input is not valid JSON.",
      "source_location": "line 1 column 2",
      "path": [],
      "details": {}
    }
  ],
  "trace": {
    "source_format": "open_cvn_json",
    "source_identifier": "broken.json",
    "source_path": "broken.json",
    "extracted_from": null,
    "cvn_codes": [],
    "xml_paths": [],
    "schema_version": null,
    "policy_name": null,
    "policy_version": null
  }
}
```

### JSON Schema Validation Failure

```json
{
  "source_format": "open_cvn_json",
  "source_identifier": "wrong-shape.json",
  "data": null,
  "validation_status": "invalid",
  "warnings": [],
  "errors": [
    {
      "code": "json_schema_validation_failure",
      "severity": "error",
      "message": "Open CVN JSON does not match the generated schema.",
      "source_location": null,
      "path": ["curriculum"],
      "details": {}
    }
  ],
  "trace": {
    "source_format": "open_cvn_json",
    "source_identifier": "wrong-shape.json",
    "source_path": "wrong-shape.json",
    "extracted_from": null,
    "cvn_codes": [],
    "xml_paths": [],
    "schema_version": "0.1.0",
    "policy_name": null,
    "policy_version": null
  }
}
```

### PDF Without Extractable XML

```json
{
  "source_format": "pdf",
  "source_identifier": "cvn.pdf",
  "data": null,
  "validation_status": "failed",
  "warnings": [],
  "errors": [
    {
      "code": "pdf_without_extractable_xml",
      "severity": "error",
      "message": "PDF does not contain extractable CVN XML.",
      "source_location": null,
      "path": [],
      "details": {}
    }
  ],
  "trace": {
    "source_format": "pdf",
    "source_identifier": "cvn.pdf",
    "source_path": "cvn.pdf",
    "extracted_from": null,
    "cvn_codes": [],
    "xml_paths": [],
    "schema_version": null,
    "policy_name": null,
    "policy_version": null
  }
}
```

### XML Semantically Unmappable

```json
{
  "source_format": "cvn_xml",
  "source_identifier": "cvn.xml",
  "data": null,
  "validation_status": "invalid",
  "warnings": [],
  "errors": [
    {
      "code": "xml_semantically_unmappable",
      "severity": "error",
      "message": "CVN XML is readable but cannot be mapped to Open CVN JSON.",
      "source_location": null,
      "path": ["CVNRoot"],
      "details": {}
    }
  ],
  "trace": {
    "source_format": "cvn_xml",
    "source_identifier": "cvn.xml",
    "source_path": "cvn.xml",
    "extracted_from": null,
    "cvn_codes": [],
    "xml_paths": ["CVNRoot"],
    "schema_version": null,
    "policy_name": null,
    "policy_version": null
  }
}
```

## Verification

Issue `#47` verification should use contract-only tests:

```bash
uv run pytest -n auto tests/test_parser_validator_contract_unit.py -v
```

Default repository verification remains:

```bash
uv run pytest -n auto tests
```
