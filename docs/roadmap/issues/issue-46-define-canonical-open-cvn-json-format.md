# Issue 46 - Define Canonical Open CVN JSON Format

## Summary

Issue `#46` defines the canonical Open CVN JSON format that will be validated by
the parser and consumed by later application work.

This issue is part of epic `#41`.

## Goal

- define the root JSON object and versioning strategy
- define how curriculum sections and entries are represented
- define how CVN source traceability survives in JSON
- define extension rules for future schema versions

## Background

The TFG requires a final JSON-based representation suitable for text files and
NoSQL-like storage. The format must be clearer than CVN XML while preserving
traceability to official CVN sources.

## Design Questions

1. What is the root object name and metadata shape?
2. How are curriculum sections grouped?
3. Are entries keyed by stable semantic names, CVN codes, or both?
4. How are repeated entries represented?
5. Where does source trace metadata live?
6. How are controlled references represented?
7. How are unresolved or under-traced CVN references represented?
8. How does the schema allow future extension without breaking old data?

## Planned Steps

1. review conceptual IR from issue `#43`
2. review JSON Schema generation findings from issue `#45`
3. define root metadata fields such as schema version, source, language, and
   generated timestamp policy
4. define section and entry structure
5. define trace metadata conventions
6. define controlled-reference JSON shapes
7. define extension and compatibility rules
8. document examples for representative personal, academic, and research data
9. update JSON Schema generation plan if needed

## Expected Output

- canonical Open CVN JSON format specification under `docs/`
- representative JSON examples
- mapping notes from CVN/domain Pydantic fields to JSON
- decisions for future versioning

## Verification

- examples validate against generated schema once issue `#45` is implemented
- format is not XML-centric
- traceability to CVN source identifiers remains preserved

## Impact On Later Issues

- issue `#49` imports and validates this JSON format
- epic `#51` stores, edits, and exports this format

## Status

- Status: planned
