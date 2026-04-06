# Issue 14 - Define Semantic Mapping Rules And Override Policy

## Summary

Issue `#14` will define the rules that transform normalized CVN metadata into
 domain-oriented Pydantic models.

## Original Goal

- create deterministic type, naming, enum, multiplicity, and override rules for
  the semantic generation layer

## Original Plan

1. define type-mapping rules
2. decide enum vs string treatment for controlled tables
3. define naming rules for classes, fields, and modules
4. define how to treat `choice`, wrappers, and recursion
5. create an explicit override mechanism
6. document all decisions in versioned repository files

## Minimum Decisions Required

1. which wrappers collapse to primitives in the domain layer
2. which controlled sets become enums and which remain strings
3. how multilingual names affect class and field naming
4. how multiplicity becomes optional fields versus `list[T]`
5. how external reference tables remain represented
6. how code-specific exceptions are registered outside the generic algorithm

## Constraints To Respect

- many structural XSD types are technical wrappers rather than domain concepts
- some reference tables are internal and some are external to the package
- `choice` appears rarely but in high-value structures
- XML interoperability metadata should not leak into the future domain API by
  default

## Relevant Known Inputs

- structural bindings preserve fidelity but expose known limitations for
  `choice`, multiplicity, and wrapper ergonomics
- external reference tables remain unresolved from the official package alone

## Status

- Status: pending
