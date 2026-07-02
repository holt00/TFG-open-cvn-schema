# Issue 43 - Define Agnostic Conceptual Model Extraction Layer

## Summary

Issue `#43` defines an intermediate representation for agnostic curriculum
concepts derived from the generated/domain Pydantic layer and CVN trace metadata.

This issue is part of epic `#41`.

## Goal

- define a conceptual model inventory that is not tied to XML serialization,
  Python implementation details, or generated module structure
- preserve traceability to CVN codes, XML paths, reference resolution, and
  semantic policy decisions
- create the source layer from which UML and JSON schema work can proceed

## Background

The current domain generator emits traceable Pydantic artifacts, but the TFG
requires a representation that describes curriculum concepts rather than CVN XML
mechanics. A conceptual IR should sit between generated Pydantic models and
diagram/schema outputs.

## Proposed Conceptual IR Contents

The IR should represent:

- conceptual entities
- attributes
- relationships
- controlled vocabularies and reference families
- required/optional status
- cardinality
- value type
- source CVN code trace
- source XML path trace when relevant
- semantic policy decision trace
- known limitations or unresolved cases

## Planned Steps

1. inspect available domain generation metadata and `cvn_trace` values
2. define dataclasses or typed records for conceptual entities, fields,
   relationships, vocabularies, and trace data
3. decide grouping rules by curriculum domain areas instead of raw XML packages
4. map representative generated Pydantic fields into the conceptual IR
5. define deterministic ordering and stable identifiers
6. document which XML/Python details must be excluded from conceptual output
7. add tests if implementation is authorized

## Expected Output

- conceptual IR contract under `src/cvn_codegen/` if implementation is approved
- documentation of mapping rules from generated/domain metadata into the IR
- representative inventory for at least personal data and one academic/research
  section

## Verification

- tests for deterministic extraction if code is implemented
- manual review that generated concepts are domain-oriented, not XML-oriented
- trace fields preserved for representative entries

## Impact On Later Issues

- issue `#44` renders UML from this IR
- issue `#45` and issue `#46` can use this IR to guide JSON shape decisions

## Status

- Status: planned
