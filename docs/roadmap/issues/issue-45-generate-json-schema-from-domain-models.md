# Issue 45 - Generate JSON Schema From Domain Models

## Summary

Issue `#45` researches and implements JSON Schema generation from the
domain-oriented Pydantic layer.

This issue is part of epic `#41`.

## Goal

- generate JSON Schema for the Open CVN data representation
- use Pydantic v2 JSON Schema support where suitable
- preserve semantic trace and version metadata where useful
- document limitations of generated JSON Schema

## Background

Pydantic v2 supports JSON Schema generation through `model_json_schema()`,
`TypeAdapter.json_schema()`, and `models_json_schema(...)`. The expected standard
baseline is JSON Schema Draft 2020-12.

The project must decide whether the JSON Schema is generated directly from the
current domain Pydantic models or from a refined Open CVN root model defined in
issue `#46`.

## Planned Steps

1. inspect current generated domain model hierarchy
2. research Pydantic JSON Schema modes: `validation` and `serialization`
3. evaluate `models_json_schema(...)` for multi-model schema generation
4. define schema metadata: title, version, description, `$id`, and `$schema`
5. decide how to handle `$defs`, references, enums, unions, optional fields, and
   lists
6. decide how much CVN trace metadata belongs in JSON Schema
7. implement schema generation if approved
8. write generated schema output to a documented location
9. add tests for determinism and JSON validity

## Expected Output

- documented JSON Schema generation approach
- generated Open CVN JSON Schema artifact or prototype
- command to regenerate schema
- tests for schema generation if implementation is approved

## Verification

- schema is valid JSON
- schema declares expected draft metadata
- generation is deterministic
- representative model definitions appear under `$defs`
- schema supports validation needs for issue `#49`

## Impact On Later Issues

- issue `#46` uses findings to define canonical JSON shape
- issue `#49` uses schema for JSON import validation

## Status

- Status: planned
