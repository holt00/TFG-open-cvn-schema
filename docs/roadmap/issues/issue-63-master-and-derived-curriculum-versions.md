# Issue 63 - Implement Master And Derived Curriculum Versions

## Summary

Issue `#63` implements the MVP versioning model for one master curriculum and
multiple derived curriculum versions.

This issue is part of epic `#60`.

## Goal

- keep a master curriculum with all known validated data
- create derived versions for specific targets
- allow derived versions to include less data than the master
- preserve traceability from derived entries back to master data

## MVP Versioning Model

The MVP should not implement a complex Git-like history. It should store:

- one master curriculum per local store or profile
- derived versions that reference the master curriculum
- version metadata such as name, purpose, created date, and updated date
- selection rules or derived JSON payloads sufficient for export

The preferred MVP approach is selection-based derivation: a derived version stores
which sections or entries from the master are included or excluded. If direct field
overrides are implemented, they must be explicit and auditable.

## Planned Scope

- mark one stored curriculum as master
- create derived version records
- list master and derived versions
- clone a derived version from the master
- include or exclude curriculum sections or entries
- generate an Open CVN JSON document for a derived version
- preserve trace metadata and source references where possible

## Planned Steps

1. define version records in the SQLite schema
2. define derived-version selection model
3. implement master creation or assignment
4. implement derived version creation from master
5. implement include/exclude behavior for sections and entries
6. implement derived Open CVN JSON materialization
7. add tests for master, derived, clone, include, exclude, and export behavior
8. document the MVP versioning model and known limits

## Expected Output

- versioning service or repository module
- CLI commands for listing and creating versions
- tests for master and derived behavior
- documentation of version semantics

## Verification

- derived version can be created from master
- derived version export contains selected data only
- master data remains unchanged after derived selection edits
- full repository verification passes or a reason is documented

## Impact On Later Issues

- issue `#65` adds editing or selection commands
- issue `#66` exports selected derived versions to LaTeX

## Status

- Status: planned
