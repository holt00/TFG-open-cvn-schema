# Issue 68 - Add Application MVP Tests And Documentation

## Summary

Issue `#68` closes the epic `#60` MVP by adding end-to-end tests and user-facing
documentation for the local CV management prototype.

This issue is part of epic `#60`.

## Goal

- prove the MVP workflow works from import to export
- document commands for a user or evaluator
- record known limitations and non-MVP behavior
- update persistent project context after epic `#60`

## Planned Test Coverage

- initialize local store
- import valid Open CVN JSON
- reject invalid Open CVN JSON
- create master curriculum
- create derived version
- include or exclude content in a derived version
- export derived version as Open CVN JSON
- render LaTeX for master or derived version
- handle PDF compiler unavailable case
- run CLI smoke workflow over temporary directories

## Documentation Targets

- application MVP user guide under `docs/development/` or `docs/application/`
- issue `#60` epic record
- issues `#61` through `#68`
- `docs/context/current_status.md`
- `docs/roadmap/cvn_generation_roadmap.md`
- `docs/pipeline/known_limitations.md` if new limitations are found
- `PROJECT_GUIDE.md` if document maps change

## Planned Steps

1. audit implemented application features from issues `#61` through `#67`
2. add focused unit tests for storage, versioning, import/export, and rendering
3. add CLI integration tests over temporary stores
4. add optional PDF behavior tests with mocked compiler paths
5. write user-facing MVP workflow documentation
6. run targeted application tests
7. run full repository verification
8. update epic `#60`, current status, roadmap, and limitation docs

## Expected Output

- application MVP test suite
- user guide for local CV management prototype
- verification record for epic `#60`
- documented limitations and follow-up work

## Verification

- targeted application MVP tests pass
- full repository verification passes with `uv run pytest -n auto tests`
- documentation records exact commands and results

## Impact On Later Issues

- later UI, richer XML mapping, template design, and LLM work can build on a
  documented local application foundation

## Status

- Status: planned
