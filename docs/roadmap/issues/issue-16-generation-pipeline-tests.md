# Issue 16 - Add Automated Tests For The Generation Pipeline

## Summary

Issue `#16` will expand the current smoke tests into a reproducible test suite
for the structural and semantic generation workflow.

## Original Goal

- validate the pipeline end-to-end and protect against regressions

## Original Plan

1. add fixtures from the canonical CVN package
2. test parsing of manual and tree-model inputs
3. test normalization
4. test semantic mapping and overrides
5. test generated module imports
6. add at least one end-to-end generation test
7. cover known mismatches and special cases

## Minimum Coverage Goals

1. structural parsing smoke tests for generated bindings
2. normalization tests using real XML inputs
3. regression tests for `choice` and recursion-related cases where relevant
4. tests for enum-vs-string mapping decisions
5. end-to-end generation tests for importable domain outputs

## Known Inputs From Earlier Issues

- issue `#12` already added runner smoke tests
- known XML/XSD mismatches must be asserted as documented behavior rather than
  treated as surprising failures

## Status

- Status: pending
