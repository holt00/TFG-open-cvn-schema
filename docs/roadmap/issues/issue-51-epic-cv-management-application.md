# Issue 51 - Epic: CV Management Application

## Summary

Epic `#51` is the placeholder for the application layer that will be built after
the agnostic schema, JSON Schema, and parser/validator work from epic `#41` is
defined.

This epic is intentionally not expanded yet. The next planning focus remains
epic `#41`.

## TFG Alignment

This epic addresses the application-oriented TFG phases:

1. local curriculum storage
2. JSON export
3. LaTeX export
4. PDF generation from LaTeX
5. user-facing management of master and derived curriculum versions

## Initial Scope

The future application should include:

- internal application logic built on the parser/validator from epic `#41`
- import and export of Open CVN JSON
- export to LaTeX using Jinja templates
- LaTeX compilation into PDF
- PDF preview inside the application
- SQLite persistence
- one master curriculum containing all known data
- multiple derived curriculum versions with more or fewer data depending on the
  target purpose
- ability to customize a derived version from the master curriculum by editing
  the original or cloning it
- ability to add or remove fields and CVN codes in derived versions

## Deferred Planning Notes

The epic should later decide:

- application type: desktop, web, CLI, or hybrid
- UI framework
- persistence schema and migration strategy
- versioning model for master and derived curricula
- LaTeX template structure
- PDF compiler dependency and sandboxing
- PDF preview mechanism
- editing workflow and validation UX

## Dependencies

- epic `#41` for the agnostic schema, JSON Schema, and parser/validator contract

## Out Of Scope For Now

- detailed task breakdown
- UI design
- database schema
- implementation plan
- dependency selection

## Status

- Status: planned placeholder
- Details pending after epic `#41` planning and implementation advances
