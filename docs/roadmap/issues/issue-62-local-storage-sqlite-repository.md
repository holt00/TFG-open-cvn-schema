# Issue 62 - Implement Local Storage With SQLite

## Summary

Issue `#62` implements the local persistence layer for the MVP CV management
application.

This issue is part of epic `#60`.

## Goal

- store Open CVN curriculum documents locally
- keep the MVP usable without external services
- preserve parser validation status and trace metadata
- support later master and derived version management

## Storage Direction

The MVP should use SQLite because it is local, available from Python standard
library support, easy to test, and sufficient for a single-user prototype.

The storage layer should keep Open CVN JSON documents as canonical JSON payloads
inside SQLite while storing enough metadata for listing, selection, and versioning.

## Planned Scope

- create a local SQLite database file
- create schema initialization and schema-version metadata
- store curriculum records with:
  - internal ID
  - display name
  - Open CVN JSON payload
  - schema version
  - policy name and policy version
  - source format or source identifier
  - created and updated timestamps
- store parser issues or import diagnostics where useful
- expose repository functions for create, read, update, list, and delete where
  needed by MVP commands

## Planned Steps

1. define SQLite schema for MVP storage
2. implement database initialization
3. implement repository functions for curriculum documents
4. preserve Open CVN JSON payload exactly enough for export
5. validate or revalidate documents before storage using epic `#41` validators
6. add unit tests with temporary SQLite files
7. document the local storage file and backup expectations

## Expected Output

- storage module under `src/open_cvn_app/`
- SQLite schema initialization
- repository tests
- documented local database behavior

## Verification

- temporary database tests pass
- stored Open CVN JSON can be read back without data loss
- invalid JSON cannot be stored as a valid curriculum record
- full repository verification passes or a reason is documented

## Impact On Later Issues

- issue `#63` builds master and derived versions on top of stored documents
- issue `#64` imports and exports through the storage repository

## Status

- Status: planned
