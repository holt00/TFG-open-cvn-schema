# Issue 64 - Implement Open CVN JSON Import And Export Workflow

## Summary

Issue `#64` connects the epic `#41` parser/validator to the MVP application
storage and versioning workflow.

This issue is part of epic `#60`.

## Goal

- import Open CVN JSON into local storage
- export master or derived versions as Open CVN JSON
- preserve validation status, structured parser issues, and trace metadata
- provide CLI commands that prove the storage and exchange workflow

## Dependency On Epic `#41`

Import must call `parse_open_cvn_json(...)` or `validate_open_cvn_json(...)` from
`open_cvn`. It must not validate against a new app-specific JSON shape.

## Planned Scope

- `open-cvn import-json <path>` or equivalent
- `open-cvn export-json <version> <path>` or equivalent
- import from existing examples under `examples/open_cvn/`
- reject invalid input with structured error output
- store accepted documents through issue `#62` repository functions
- export canonical Open CVN JSON with deterministic formatting

## Planned Steps

1. review parser workflow docs and Open CVN JSON examples
2. implement JSON import command
3. route validation errors to user-readable CLI output
4. persist valid imported documents as master or named records
5. implement JSON export command for stored master versions
6. extend export to derived versions after issue `#63`
7. add CLI and repository integration tests
8. document import/export commands

## Expected Output

- working JSON import command
- working JSON export command
- tests using safe Open CVN JSON fixtures
- documentation for import/export examples

## Verification

- valid Open CVN JSON imports into local storage
- invalid Open CVN JSON fails with structured error output
- exported JSON revalidates with `validate_open_cvn_json(...)`
- full repository verification passes or a reason is documented

## Impact On Later Issues

- issue `#66` can use exported or stored Open CVN JSON for LaTeX rendering
- issue `#68` documents the complete MVP workflow

## Status

- Status: planned
