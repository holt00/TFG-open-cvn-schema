# Issue 47 - Define Unified Parser And Validator Contract

## Summary

Issue `#47` defines the public parser and validator contract for importing CVN
data from PDF, XML, and JSON inputs.

This issue is part of epic `#41`.

## Goal

- define common input APIs for PDF, XML, and JSON
- define common result and error structures
- keep source-specific extraction separate from domain validation
- prepare implementation work for issues `#48` and `#49`

## Proposed API Direction

The parser should eventually expose functions similar to:

- `parse_cvn_pdf(...)`
- `parse_cvn_xml(...)`
- `parse_open_cvn_json(...)`
- `validate_open_cvn_json(...)`

Names are provisional and should follow repository conventions during
implementation.

## Result Contract

Parser results should include:

- source format
- source path or source identifier when available
- parsed domain object or validated JSON object
- validation status
- warnings
- structured errors
- trace metadata

## Error Contract

Errors should distinguish:

- unsupported input format
- unreadable file
- PDF without extractable XML
- invalid XML
- XML structurally valid but semantically unmappable
- invalid JSON
- JSON schema validation failure
- Pydantic validation failure

## Planned Steps

1. define parser result dataclasses or Pydantic models
2. define structured error codes and messages
3. define public parser function signatures
4. define source-specific responsibilities for PDF, XML, and JSON import
5. define trace preservation rules
6. document examples of success and failure cases
7. add unit tests if implementation is approved

## Expected Output

- parser/validator contract documentation
- typed result and error structures if implementation is approved
- tests for contract behavior if implementation is approved

## Verification

- result and error types cover all planned input paths
- API separates extraction from validation
- issue `#48` and issue `#49` can implement against the contract without
  redesigning it

## Impact On Later Issues

- issue `#48` implements PDF XML extraction behind this contract
- issue `#49` implements XML and JSON import validation behind this contract
- epic `#51` consumes this contract in the application layer

## Status

- Status: planned
