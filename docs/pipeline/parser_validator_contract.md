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

In issue `#47`, these functions intentionally raised `NotImplementedError` with
this message:

```text
Parser implementation is deferred to issue #48/#49.
```

Issue `#48` implements `parse_cvn_pdf(...)` for deterministic PDF XML
extraction. The XML and JSON entry points remain deferred to issue `#49`.

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

Issue `#48` implements PDF handling behind `parse_cvn_pdf(...)`.

Responsibilities:

- read PDF input
- extract embedded-file CVN XML when possible
- extract PDF XML metadata when it contains CVN XML evidence
- validate only that the extracted candidate is well-formed and plausibly
  CVN-related
- return `pdf_without_extractable_xml` when no XML can be extracted
- leave XML interpretation to the issue `#49` XML import path

PDF parsing is not the domain validator. It does not perform OCR, page text
reconstruction, LLM reconstruction, XML-to-domain mapping, Open CVN JSON
validation, or JSON Schema validation.

Successful PDF extraction returns `validation_status="not_run"` because issue
`#48` extracts XML but does not validate the XML against the future import path.
The result `data` contains:

- `xml_text`: extracted XML text
- `extraction`: metadata such as source kind, source name, byte size,
  embedded-file count, candidate count, metadata presence, and metadata xref when
  available

### XML

Issue `#49` implements CVN XML import behind `parse_cvn_xml(...)`.

Responsibilities:

- read CVN XML input
- classify unreadable input separately from invalid XML
- preserve CVN XML trace where possible
- report `xml_semantically_unmappable` when structurally readable XML cannot map
  to Open CVN/domain representation

Implemented behavior:

- accepts path, inline XML string, and XML bytes inputs
- rejects mapping inputs as `unsupported_input_format`
- validates XML well-formedness with `xml.etree.ElementTree`
- records simplified XML paths and detected CVN code-like values in trace metadata
- emits a conservative Open CVN JSON document with trace-only import diagnostics
  for plausible CVN XML
- does not yet perform full semantic XML-to-domain mapping from real CVN records

### JSON

Issue `#49` implements Open CVN JSON import behind `parse_open_cvn_json(...)` and
`validate_open_cvn_json(...)`.

Responsibilities:

- classify malformed JSON as `invalid_json`
- validate the canonical issue `#46` root shape
- use the generated `schemas/open_cvn.schema.json` artifact for JSON Schema
  validation when the validation dependency is introduced
- distinguish JSON Schema validation failures from Pydantic/runtime validation
  failures

Implemented behavior:

- accepts path, inline JSON string, JSON bytes, and already-loaded mapping inputs
- validates the generated Draft 2020-12 schema with `jsonschema`
- runs JSON Schema validation before Pydantic runtime validation
- maps malformed JSON to `invalid_json`
- maps JSON Schema failures to `json_schema_validation_failure`
- maps runtime model failures to `pydantic_validation_failure`
- preserves `schema_version`, `metadata.policy.name`, and
  `metadata.policy.version` in parser trace metadata

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

### Successful PDF XML Extraction

```json
{
  "source_format": "pdf",
  "source_identifier": "cvn.pdf",
  "data": {
    "xml_text": "<CVNRoot />",
    "extraction": {
      "source_kind": "embedded_file",
      "source_name": "cvn.xml",
      "source_index": 0,
      "xml_bytes_size": 11,
      "metadata_xref": null,
      "embedded_file_count": 1,
      "candidate_count": 1,
      "metadata_present": false
    }
  },
  "validation_status": "not_run",
  "warnings": [],
  "errors": [],
  "trace": {
    "source_format": "pdf",
    "source_identifier": "cvn.pdf",
    "source_path": "cvn.pdf",
    "extracted_from": "embedded_file:cvn.xml",
    "cvn_codes": [],
    "xml_paths": [],
    "schema_version": null,
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

### Successful Trace-Only CVN XML Import

```json
{
  "source_format": "cvn_xml",
  "source_identifier": "minimal_cvn.xml",
  "data": {
    "schema_version": "0.1.0",
    "metadata": {
      "source": {
        "format": "cvn_xml",
        "identifier": "minimal_cvn.xml",
        "path": "minimal_cvn.xml",
        "root": "CVNRoot"
      },
      "policy": {
        "name": "default_cvn_semantic_policy",
        "version": "0.1.0"
      }
    },
    "curriculum": {
      "identity": {},
      "education": [],
      "research": [],
      "professional_experience": [],
      "achievements": [],
      "other": []
    },
    "extensions": {
      "x-open-cvn.import": {
        "cvn_codes": ["000.010.000.000"],
        "xml_paths": ["CVNRoot", "CVNRoot/CVNItem[1]"],
        "mapping_status": "trace_only"
      }
    }
  },
  "validation_status": "valid",
  "warnings": [],
  "errors": [],
  "trace": {
    "source_format": "cvn_xml",
    "source_identifier": "minimal_cvn.xml",
    "source_path": "minimal_cvn.xml",
    "extracted_from": null,
    "cvn_codes": ["000.010.000.000"],
    "xml_paths": ["CVNRoot", "CVNRoot/CVNItem[1]"],
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
