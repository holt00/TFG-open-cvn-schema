# Issue 65 - Implement Curriculum Editing And Selection MVP

## Summary

Issue `#65` adds minimal editing and selection operations needed to customize a
derived curriculum version from a master curriculum.

This issue is part of epic `#60`.

## Goal

- provide basic user-facing customization of derived CV versions
- avoid a full GUI editor in the MVP
- keep edits auditable and easy to export
- preserve Open CVN JSON validity after edits

## MVP Editing Direction

The MVP should prioritize coarse operations over a full nested JSON editor:

- list curriculum sections and entries
- include or exclude sections
- include or exclude individual entries when entries have stable IDs or indexes
- optionally apply simple metadata edits such as derived version name or purpose
- optionally apply explicit field overrides only when they can be validated

## Planned Scope

- CLI commands for listing curriculum sections and entries
- CLI commands for include/exclude selection in derived versions
- optional command for setting derived version metadata
- validation of materialized derived Open CVN JSON after edits
- clear unsupported messages for field-level edits not implemented in MVP

## Planned Steps

1. define selection command grammar
2. implement section listing
3. implement entry listing with stable display identifiers
4. implement include/exclude section behavior
5. implement include/exclude entry behavior where feasible
6. validate derived document after selection changes
7. add tests for selection behavior and invalid selectors
8. document editing limitations

## Expected Output

- selection/editing CLI commands
- tests for derived version customization
- documented MVP editing behavior

## Verification

- users can remove a section from a derived CV
- users can remove an entry from a derived CV when entries are addressable
- exported derived JSON remains valid
- unsupported fine-grained edits fail clearly

## Impact On Later Issues

- issue `#66` exports customized derived versions to LaTeX
- later GUI work can reuse the same selection service

## Status

- Status: planned
