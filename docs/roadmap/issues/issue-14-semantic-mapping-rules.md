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

## Planned Execution Steps

The implementation of issue `#14` should begin from the normalized metadata
layer produced in issue `#13` and should leave issue `#15` with an explicit,
deterministic semantic policy to consume.

### Main Objective

- define a stable semantic mapping policy that translates normalized CVN
  metadata into domain-oriented generation rules for types, naming,
  multiplicity, controlled vocabularies, and explicit exceptions
- keep semantic cleanup outside `src/generated/` and preserve CVN code
  traceability for every domain-facing decision

### Execution Steps

1. define the semantic output contract
2. inventory representative normalized cases
3. define base type-mapping rules
4. define controlled-table policy
5. define naming rules for domain artifacts
6. define multiplicity and optionality rules
7. define treatment for `choice`, wrappers, and recursion
8. design the override mechanism
9. validate rules against representative examples
10. document the final policy and unresolved limits

### Step `1` - Define The Semantic Output Contract

- decide which hand-maintained structure will represent semantic mapping rules
  for later consumption
- the contract should be explicit enough for issue `#15` to consume without
  reinterpreting prose documentation
- the contract should support both generic rules and targeted per-code or
  per-pattern exceptions

### Step `2` - Inventory Representative Normalized Cases

- review normalized entries from issue `#13` and select representative samples
  across manual types, multiplicity combinations, reference tables, wrappers,
  and known `choice` structures
- use this inventory to ensure semantic policy is grounded in real repository
  inputs rather than hypothetical cases
- preserve traceability from each representative case back to CVN `code`,
  `xml_path`, and source metadata

### Step `3` - Define Base Type-Mapping Rules

- map the current manual type families to intended domain-facing types
- current normalized manual types observed in the canonical manual are:
  - `Alphanumeric`
  - `Date`
  - `Double`
  - `Boolean`
  - `Duration`
- decide which structural XML helper types collapse to primitives and which, if
  any, should remain distinct domain value objects
- keep the result deterministic and independent from direct structural class
  names where those names are only XML-oriented wrappers

### Step `4` - Define Controlled-Table Policy

- classify reference tables into semantic categories such as:
  - internal CVN controlled tables that may become enums
  - ISO or other large standardized tables that may require a different policy
  - external or unresolved tables that cannot safely become closed enums from
    the canonical package alone
- decide which controlled sets become strict enums and which remain strings,
  aliases, or external-reference representations
- document the reasoning so issue `#15` can apply the same policy

### Step `5` - Define Naming Rules For Domain Artifacts

- define naming rules for classes, fields, and modules in the future semantic
  generation layer
- decide how multilingual manual labels are normalized into stable identifiers
- define how to resolve naming collisions, repeated labels, technical suffixes,
  and XML-oriented names that should not leak into the future domain API by
  default
- preserve code-level traceability even when domain names differ from technical
  XML names

### Step `6` - Define Multiplicity And Optionality Rules

- define how `manual_obligatory` and `manual_multiplicity` map to required
  fields, optional fields, and `list[T]`
- define how later generation should behave when structural defaults from the
  generated bindings are weaker than the intended domain semantics
- keep the policy clear enough to restore semantic meaning lost in the
  structural layer

### Step `7` - Define Treatment For `choice`, Wrappers, And Recursion

- define a semantic policy for the known high-value `xs:choice` cases already
  documented in the repository, including:
  - `FlexibleDatesType`
  - `OfficialIdType`
  - `EntityTypeType`
  - `EntityNameType`
- decide when wrappers are collapsed, when mutually exclusive alternatives
  become unions or dedicated domain objects, and how recursive structures are
  represented without reproducing raw XML complexity
- keep this policy aligned with the architectural rule that structural fidelity
  belongs to `src/generated/`, while semantic cleanup belongs to later layers

### Step `8` - Design The Override Mechanism

- create an explicit override strategy for cases that cannot be handled by the
  generic mapping algorithm alone
- decide the granularity of overrides, for example by CVN `code`, manual type,
  reference table, or technical path
- keep overrides versioned, reviewable, and separate from generated output

### Step `9` - Validate Rules Against Representative Examples

- check the proposed policy against a representative set of normalized cases
- validation should include at least:
  - a simple scalar field
  - a controlled table expected to become an enum
  - a controlled table expected to remain open
  - a `choice` structure
  - a wrapper-based field such as date or duration
  - a case that requires an explicit override
- goal: ensure issue `#15` can consume the policy without reopening semantic
  design questions already settled here

### Step `10` - Document The Final Policy And Unresolved Limits

- record final decisions in versioned repository documentation
- document any semantic ambiguities that remain unresolved after issue `#14`
- if a new limitation is discovered, record it in
  `docs/pipeline/known_limitations.md`
- if issue state changes, update the roadmap and current status documents in the
  same session

## Questions Still To Decide

Before issue `#14` can be considered fully specified, some semantic decisions
still need to be made explicitly:

1. whether future domain-facing names should prefer Spanish academic
   terminology, English conceptual terminology, or a documented hybrid rule
2. which categories of controlled tables should become strict enums and which
   should remain open representations
3. how external reference tables such as `ENTITY@Entity.xsd`,
   `THESAURUS@thesaurus.xsd`, and `UNESCO_CODES` should be represented in the
   semantic layer
4. whether wrappers like flexible dates and durations should become primitives,
   unions, or dedicated value objects in the future domain API
5. what exact shape the override registry should take so later generation stays
   deterministic and reviewable

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
- the official source package does include side-package material for several
  references previously treated as opaque placeholders:
  - `ENTITY@Entity.xsd` is represented by the `Entity` family
  - `THESAURUS@thesaurus.xsd` is represented by the `Thesaurus` family
  - many Annex-I tables are materialized in `ReferenceTables.xml`
- not all manual references are fully resolved from the package alone; a known
  example is `CVN_AGENCY_C`

## Status

- Status: pending
