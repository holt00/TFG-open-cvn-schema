# Issue 49 - Implement XML And JSON Import Validation

## Summary

Issue `#49` implements direct CVN XML import and Open CVN JSON import validation
using the parser contract from issue `#47`.

This issue is part of epic `#41`.

## Goal

- import CVN XML into validated domain/Open CVN data
- import Open CVN JSON and validate it against Pydantic and JSON Schema rules
- preserve source traceability and structured validation errors

## Background

The repository already has structural CVN bindings and domain-generation logic,
but the final parser must consume user inputs, not only source package metadata.
This issue starts the parser/validator implementation for direct XML and JSON
inputs.

## XML Import Direction

The XML path should:

1. parse CVN XML using structural bindings where useful
2. map structural CVN values into the domain/Open CVN shape
3. validate mapped data with Pydantic domain models
4. preserve CVN codes and source paths where available
5. report structural or semantic validation failures clearly

## JSON Import Direction

The JSON path should:

1. load JSON safely
2. validate against Open CVN Pydantic models
3. validate against generated JSON Schema when available
4. report schema and Pydantic errors through the common parser contract
5. preserve version and trace metadata

## Planned Steps

1. consume parser result and error contract from issue `#47`
2. implement XML input loading and structural parse path if approved
3. implement XML-to-domain/Open CVN mapping prototype
4. implement JSON loading and validation path
5. integrate JSON Schema artifact from issue `#45`
6. add valid and invalid fixtures
7. add tests for structured errors and trace preservation
8. document parser examples

## Expected Output

- XML import implementation if approved
- JSON import validation implementation if approved
- fixtures and tests for valid and invalid inputs
- documentation for parser usage

## Verification

- valid XML imports into expected domain/Open CVN shape
- invalid XML produces structured errors
- valid JSON validates against Pydantic and JSON Schema
- invalid JSON produces structured errors
- trace metadata survives import when available

## Known Risks

- XML-to-domain mapping may require more semantic decisions than current domain
  generator exposes
- JSON Schema and Pydantic validation errors may need normalization for usability
- sample CVN XML files may include personal data and require synthetic fixtures

## Impact On Later Issues

- completes parser input support with issue `#48`
- epic `#51` consumes XML and JSON import/export behavior

## Status

- Status: planned
