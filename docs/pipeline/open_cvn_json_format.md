# Open CVN JSON Format

## Purpose

This document defines the canonical Open CVN JSON document shape for issue `#46`.
It is the runtime JSON format that later parser and validation work should accept
for Open CVN files.

The format is designed for text files, local persistence, and NoSQL-like storage.
It must be easier to consume than CVN XML while preserving traceability to the
official CVN source package.

## Source Of Truth

The canonical JSON shape is based on the issue `#43` conceptual inventory and the
issue `#45` JSON Schema prototype.

The conceptual inventory remains the semantic source of truth for:

- curriculum domain areas
- conceptual entities
- conceptual attributes
- controlled vocabularies
- CVN code and XML path trace
- semantic-policy evidence

The generated JSON Schema remains the validation artifact. It must reflect this
format before issue `#49` relies on it for Open CVN JSON import.

## Root Object

Every Open CVN JSON document is an object with these canonical root fields:

```json
{
  "schema_version": "0.1.0",
  "metadata": {},
  "curriculum": {},
  "extensions": {}
}
```

Required root fields:

- `schema_version`
- `metadata`
- `curriculum`

Optional root fields:

- `extensions`

`schema_version` is the Open CVN format version. It is not the JSON Schema draft
version.

## Metadata

`metadata` describes the Open CVN document, not the curriculum content itself.

Canonical metadata fields:

- `language`: BCP 47 language tag for the primary human-language content, such as
  `es`
- `source`: optional object describing the input family used to create the file
- `created_at`: optional ISO 8601 timestamp for document creation
- `updated_at`: optional ISO 8601 timestamp for document update
- `generator`: optional object describing the tool that produced the file
- `policy`: object describing semantic policy evidence used to produce or validate
  the file

Canonical `metadata.policy` fields:

- `name`
- `version`

Generated timestamps are optional. Generators must not create nondeterministic
timestamps in reproducible artifacts unless the timestamp is part of user data or
explicit runtime output.

## Curriculum

`curriculum` groups content by conceptual domain area rather than by CVN XML
structure or generated Python modules.

Canonical section names are:

- `identity`
- `education`
- `research`
- `professional_experience`
- `achievements`
- `other`

`identity` is a single object because it describes the curriculum owner.

Other sections are arrays of entries because they commonly contain repeated
curriculum records.

Minimal empty curriculum shape:

```json
{
  "identity": {},
  "education": [],
  "research": [],
  "professional_experience": [],
  "achievements": [],
  "other": []
}
```

Sections may be omitted when empty, except when a validation profile requires
explicit empty sections.

## Entries

Repeated sections contain entry objects.

Canonical entry fields:

- `id`: optional stable local identifier for the entry
- `type`: stable conceptual entry type
- `data`: object containing the entry fields
- `trace`: optional CVN trace metadata
- `extensions`: optional extension object

Example:

```json
{
  "id": "education-001",
  "type": "education.degree",
  "data": {
    "degree_name": "Doctorado"
  },
  "trace": {
    "cvn_codes": ["020.010.010.000"]
  }
}
```

Array order preserves source document order unless a producer explicitly documents
a different ordering policy. Consumers must not treat array position as identity.

## Fields

Field names must be stable semantic names in `snake_case`.

Field names must not be generated Python module names, generated class names, raw
CVN XML element names, or one-off `cvn_item_*` identifiers.

Primitive values use JSON primitives:

- text values use strings
- date-like values use strings unless represented by `FlexibleDateValue`
- duration-like values use strings
- decimal values use numbers
- boolean values use booleans

Wrapper values use objects that match the shared wrapper definitions from the
domain layer:

- `FlexibleDateValue`
- `OfficialIdValue`
- `EntityTypeValue`
- `EntityNameValue`

Omitted fields mean no value is present. Explicit `null` means the value slot is
known but empty, unavailable, or intentionally blank. Producers should prefer
omission for unknown data unless a source distinction must be preserved.

## Controlled References

Controlled references use a common object shape.

Canonical fields:

- `code`: source code when known
- `label`: human-readable label when known
- `source`: source vocabulary, table, registry, or thesaurus reference
- `raw_value`: original value when normalization could not fully resolve it
- `uri`: optional external identifier
- `reference_status`: optional status for unresolved or under-traced cases

Closed enum behavior is allowed only when semantic policy marks the vocabulary as
enum-eligible. For example, `CVN_SEX_A` may be validated as a closed enum.

Open references must remain open even when the source package contains many known
values. This applies to enum-ineligible reference tables, registries, thesauri,
hierarchical code lists, subtype-backed tables without a strict bridge, unresolved
references, and under-traced references.

`CVN_ENTITY_TYPE` remains open because canonical evidence marks it enum-ineligible.
`CVN_AGENCY_C` remains unresolved unless stronger source evidence is introduced.

## Trace Metadata

`trace` preserves source CVN evidence for auditing, import diagnostics, and future
round-trip work.

Canonical trace fields:

- `cvn_codes`
- `xml_paths`
- `source_files`
- `source_artifacts`
- `manual_reference_table`
- `semantic_reference_kind`
- `serialization_pattern`
- `domain_shape_kind`
- `confidence`

Trace may appear at entry level, field level, or both.

Entry-level trace describes the conceptual record or CVN group. Field-level trace
describes a specific attribute when more precise evidence is useful.

Trace is metadata. It must not change the semantic value of the curriculum data.

## Extensions

`extensions` is the canonical location for tool-specific or project-specific
metadata.

Extension keys should use either:

- reverse-DNS names, such as `org.example.importer`
- `x-*` names for local experiments

Consumers should ignore unknown extensions unless configured for strict mode.

Extensions must not override canonical fields. If a value belongs to the canonical
format, it should be promoted to a documented canonical field in a future minor or
major version instead of being hidden in `extensions`.

## Versioning

The initial canonical format version is `0.1.0`.

Compatibility rules:

- patch version changes clarify documentation, examples, or non-breaking schema
  details
- minor version changes may add optional fields or new optional sections
- major version changes may remove fields, rename fields, or change validation
  semantics incompatibly

Parser expectations:

- parsers should accept compatible versions with the same major version
- parsers may warn for newer minor versions
- parsers should reject unknown major versions unless explicitly configured to try
  best-effort parsing

## Relationship To JSON Schema

The JSON Schema artifact at `schemas/open_cvn.schema.json` validates the canonical
shape. It also preserves source evidence through non-validating `x-open-cvn-*`
schema annotations.

Runtime Open CVN JSON uses ordinary data fields such as `metadata`, `trace`, and
`extensions`. Schema annotations such as `x-open-cvn-code` are not required to
appear in every JSON data file, but they inform validators and generators.

## Limitations

- JSON Schema cannot enforce every semantic rule, registry lookup, or source
  package consistency check.
- Conceptual relationships remain conservative until curated domain rules are
  added.
- Some CVN references remain unresolved or under-traced from the current source
  package alone.
- The format preserves trace to CVN sources but does not require XML-centric
  document structure.
