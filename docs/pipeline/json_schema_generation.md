# JSON Schema Generation

## Purpose

This document records the issue `#45` JSON Schema generation approach for Open
CVN.

The generated artifact is:

```text
schemas/open_cvn.schema.json
```

## Source Of Truth

The JSON Schema generator uses the issue `#43` `ConceptualModelInventory` as the
primary source of the schema root and definitions. This keeps the schema aligned
with the agnostic conceptual layer instead of exposing generated Python module
names or raw XML/XSD structures as the final Open CVN shape.

Pydantic v2 JSON Schema support remains relevant as technical evidence for the
domain-oriented model layer and shared components, but direct Pydantic schemas are
not treated as the canonical Open CVN root shape in issue `#45`.

## Generator

The generator lives at:

```text
src/cvn_codegen/json_schema_generator.py
```

Run canonical schema generation with:

```bash
uv run python -m cvn_codegen.json_schema_generator
```

To write to a temporary path during review:

```bash
uv run python -m cvn_codegen.json_schema_generator --output-path /tmp/open_cvn.schema.json
```

## Schema Contract

The artifact declares JSON Schema Draft 2020-12 explicitly:

```text
https://json-schema.org/draft/2020-12/schema
```

The schema metadata includes:

- `$id`: `https://open-cvn.local/schema/open-cvn.schema.json`
- `title`: `Open CVN JSON Schema`
- policy name and policy version from the semantic policy bundle
- issue and inventory trace through `x-open-cvn-*` extensions

The root object is provisional until issue `#46` defines the canonical Open CVN
JSON shape. The current root includes:

- `schema_version`
- `policy_name`
- `policy_version`
- `curriculum`

Definitions are emitted under `$defs` for conceptual entities, vocabularies, and
shared wrapper value shapes.

## Type Mapping

Conceptual attributes are mapped conservatively:

- text, date-like, and duration-like values map to JSON strings
- boolean values map to JSON booleans
- decimal-number values map to JSON numbers
- repeated values map to arrays
- optional values allow `null`
- wrapper values reference shared definitions such as `FlexibleDateValue` and
  `OfficialIdValue`
- unknown value kinds remain permissive and carry an explicit limitation
  extension

Controlled references are not closed unless semantic policy and reference-table
evidence classify them as eligible enumerations. For example:

- `CVN_SEX_A` is emitted as a closed enum-backed vocabulary definition
- `CVN_ENTITY_TYPE` remains open because it is enum-ineligible

## Trace Extensions

The generator preserves non-validating trace through `x-open-cvn-*` extensions
where evidence exists:

- `x-open-cvn-code`
- `x-open-cvn-xml-paths`
- `x-open-cvn-domain-shape-kind`
- `x-open-cvn-enum-eligibility`
- `x-open-cvn-source-reference`
- `x-open-cvn-confidence`
- `x-open-cvn-vocabulary-kind`

These extensions support auditability and later validation work without changing
JSON Schema validation semantics.

## Verification

Targeted verification for issue `#45` is:

```bash
uv run pytest -n auto tests/test_json_schema_generator_unit.py tests/test_generation_pipeline_json_schema.py -v
```

Default repository verification remains:

```bash
uv run pytest -n auto tests
```

## Limitations

- The issue `#45` root shape is provisional and intentionally defers final Open
  CVN JSON layout decisions to issue `#46`.
- JSON Schema cannot express every CVN semantic invariant, external registry
  requirement, or curated conceptual relationship.
- Conceptual relationships remain conservative because issue `#43` does not infer
  full domain associations from generated field annotations alone.
- Direct generated Pydantic schemas are useful for technical comparison, but they
  are not the canonical conceptual output of this issue.
