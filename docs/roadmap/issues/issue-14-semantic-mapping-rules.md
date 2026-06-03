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

## Corrected Prerequisite Chain

Issue `#14` no longer begins from only raw normalized manual and tree metadata.
It must start from the validated enriched normalization output implemented in
issue `#13` after hotfix `#5`, with auxiliary structural visibility already in
place from hotfix `#4`.

The corrected semantic-policy input now includes at minimum:

- `manual_type`
- `manual_multiplicity`
- `manual_obligatory`
- `xml_path`
- `reference_resolution.status`
- `reference_resolution.source_family`
- `reference_resolution.artifact_name`
- `reference_resolution.serialization_pattern`
- `reference_resolution.semantic_reference_kind`
- `reference_resolution.trace`

Issue `#14` must consume that typed metadata. It must not rebuild source-family,
side-package, subtype-backed, or hierarchical-reference detection from prose
documents or ad hoc table-name inspection.

## Planned Execution Steps

The implementation of issue `#14` should begin from the enriched normalization
layer produced in issue `#13` and should leave issue `#15` with an explicit,
deterministic semantic policy to consume without reopening source-discovery
questions.

## Agreed Execution Plan

The following plan was agreed before starting implementation work on issue
`#14`. It is the operative execution sequence for the issue and should guide the
step-by-step development session.

### Step `1 / 9` - Define Exact Scope Boundary

- Step summary:
  - define the exact execution boundary of issue `#14` so semantic policy,
    normalization responsibilities, and generator responsibilities stay clearly
    separated
- Step type:
  - standards, contracts, and documentation
- Files to modify or add if needed:
  - `docs/roadmap/issues/issue-14-semantic-mapping-rules.md`
  - `docs/adr/` if a stronger architecture decision must be recorded
- Root task `1 / 9`:
  - fix what belongs to issue `#14` and what remains deferred to issue `#15`
- Subtask `1.1 / 9`:
  - list the exact semantic-policy inputs consumed from `NormalizationResult`
- Subtask `1.2 / 9`:
  - list the exact outputs expected from the semantic policy layer
- Subtask `1.3 / 9`:
  - make explicit which upstream source-resolution logic must not be
    reimplemented in issue `#14`

### Step `2 / 9` - Design Semantic Output Contract

- Step summary:
  - define the machine-readable contract that issue `#15` will consume so later
    generation does not depend on prose interpretation
- Step type:
  - contract definition and technical design
- Files to modify or add if needed:
  - one or more new hand-maintained semantic-policy modules under
    `src/cvn_codegen/`
  - `docs/roadmap/issues/issue-14-semantic-mapping-rules.md`
- Root task `2 / 9`:
  - define the output shape of the semantic policy layer
- Subtask `2.1 / 9`:
  - decide the minimum record families needed, such as field-level semantic
    rules, naming rules, and override records
- Subtask `2.2 / 9`:
  - decide the indexing keys used by the policy, such as CVN `code`,
    `xml_path`, `semantic_reference_kind`, or serialization pattern
- Subtask `2.3 / 9`:
  - decide whether the contract should use dataclasses, enums, typed
    dictionaries, or another explicit typed structure

### Step `3 / 9` - Build Representative Case Inventory

- Step summary:
  - collect real normalized cases covering the main semantic categories so the
    policy is grounded in validated repository inputs
- Step type:
  - analysis and traceability
- Files to modify or add if needed:
  - `docs/roadmap/issues/issue-14-semantic-mapping-rules.md`
  - optional auxiliary analysis notes if a persistent inventory becomes useful
- Root task `3 / 9`:
  - select a representative set of enriched normalized entries
- Subtask `3.1 / 9`:
  - include a compact enum-like direct table case such as `CVN_SEX_A`
- Subtask `3.2 / 9`:
  - include a subtype-backed case such as `CVN_KNOW_A`
- Subtask `3.3 / 9`:
  - include a side-package registry case such as `ENTITY@Entity.xsd`
- Subtask `3.4 / 9`:
  - include a side-package thesaurus case such as `THESAURUS@thesaurus.xsd`
- Subtask `3.5 / 9`:
  - include a hierarchical thematic case such as `UNESCO_CODES`
- Subtask `3.6 / 9`:
  - include an unresolved case such as `CVN_AGENCY_C`
- Subtask `3.7 / 9`:
  - include an under-traced case such as `CVN_INTERVENTION_A` or `CVN_PRUEBA`

### Step `4 / 9` - Define Base Type, Wrapper, And Multiplicity Rules

- Step summary:
  - define the common semantic rules for scalar types, XML helper wrappers, and
    multiplicity behavior before handling controlled-reference policy
- Step type:
  - semantic design and contract definition
- Files to modify or add if needed:
  - one or more new hand-maintained semantic-policy modules under
    `src/cvn_codegen/`
  - `docs/roadmap/issues/issue-14-semantic-mapping-rules.md`
  - `docs/pipeline/known_limitations.md` if new limitations are found
- Root task `4 / 9`:
  - map manual types and structural wrappers to intended domain-facing types
- Subtask `4.1 / 9`:
  - decide the semantic treatment of `Alphanumeric`, `Date`, `Double`,
    `Boolean`, and `Duration`
- Subtask `4.2 / 9`:
  - decide which XML helper wrappers collapse to primitives and which should
    stay as dedicated value objects
- Subtask `4.3 / 9`:
  - decide how `manual_obligatory` and `manual_multiplicity` become required,
    optional, or repeated domain fields
- Subtask `4.4 / 9`:
  - document impacts from known structural limitations such as `xs:choice`,
    weak `minOccurs` enforcement, and attributes typed as `object`

### Step `5 / 9` - Define Policy Per Semantic Reference Kind

- Step summary:
  - define the core semantic treatment for each normalized
    `SemanticReferenceKind`
- Step type:
  - semantic design
- Files to modify or add if needed:
  - one or more new hand-maintained semantic-policy modules under
    `src/cvn_codegen/`
  - `docs/roadmap/issues/issue-14-semantic-mapping-rules.md`
- Root task `5 / 9`:
  - define open-versus-closed treatment and semantic shape by normalized
    reference kind
- Subtask `5.1 / 9`:
  - compact enum-like table
- Subtask `5.2 / 9`:
  - compact scale or measure table
- Subtask `5.3 / 9`:
  - identifier-type table
- Subtask `5.4 / 9`:
  - scope table
- Subtask `5.5 / 9`:
  - subtype-backed controlled family
- Subtask `5.6 / 9`:
  - hierarchical thematic classification
- Subtask `5.7 / 9`:
  - side-package registry
- Subtask `5.8 / 9`:
  - side-package thesaurus or vocabulary
- Subtask `5.9 / 9`:
  - unresolved manual-only reference
- Subtask `5.10 / 9`:
  - technically present but under-traced table

### Step `6 / 9` - Define Naming And Traceability Rules

- Step summary:
  - define how domain-facing names are derived while preserving CVN code and
    XML traceability
- Step type:
  - standards and technical design
- Files to modify or add if needed:
  - one or more new hand-maintained semantic-policy modules under
    `src/cvn_codegen/`
  - `docs/roadmap/issues/issue-14-semantic-mapping-rules.md`
- Root task `6 / 9`:
  - define naming rules for future domain classes, fields, and modules
- Subtask `6.1 / 9`:
  - decide the naming-language policy, including the role of Spanish academic
    terminology
- Subtask `6.2 / 9`:
  - decide how multilingual manual labels are normalized into stable
    identifiers
- Subtask `6.3 / 9`:
  - define collision-resolution rules for repeated or technically noisy names
- Subtask `6.4 / 9`:
  - define how semantic outputs preserve traceability back to CVN `code` and
    `xml_path`

### Step `7 / 9` - Design Override Mechanism

- Step summary:
  - design explicit override support for cases that generic semantic rules
    cannot resolve safely
- Step type:
  - contract definition and technical design
- Files to modify or add if needed:
  - one or more new hand-maintained override modules under `src/cvn_codegen/`
  - `docs/roadmap/issues/issue-14-semantic-mapping-rules.md`
- Root task `7 / 9`:
  - define override granularity, structure, and precedence
- Subtask `7.1 / 9`:
  - decide whether overrides can target CVN `code`
- Subtask `7.2 / 9`:
  - decide whether overrides can target `xml_path`
- Subtask `7.3 / 9`:
  - decide whether overrides can target `semantic_reference_kind`
- Subtask `7.4 / 9`:
  - decide whether overrides can target serialization pattern
- Subtask `7.5 / 9`:
  - define precedence rules when multiple generic or specific rules collide

### Step `8 / 9` - Validate Policy Against Real Cases

- Step summary:
  - verify that the semantic policy can classify and explain representative real
    cases without reopening unresolved semantic design work in issue `#15`
- Step type:
  - validation, documentation, and possible contract-level test preparation
- Files to modify or add if needed:
  - `docs/roadmap/issues/issue-14-semantic-mapping-rules.md`
  - `docs/pipeline/known_limitations.md` if a new limitation is discovered
  - optional semantic-policy tests if validation is captured in executable form
- Root task `8 / 9`:
  - validate the policy against representative normalized examples
- Subtask `8.1 / 9`:
  - validate a simple scalar field
- Subtask `8.2 / 9`:
  - validate a compact closed controlled table
- Subtask `8.3 / 9`:
  - validate a compact open controlled table
- Subtask `8.4 / 9`:
  - validate registry, thesaurus, and hierarchical references
- Subtask `8.5 / 9`:
  - validate a subtype-backed controlled family
- Subtask `8.6 / 9`:
  - validate unresolved and under-traced references
- Subtask `8.7 / 9`:
  - validate wrapper, `choice`, recursion, and override cases

### Step `9 / 9` - Document Final Policy And Prepare Handoff

- Step summary:
  - record final semantic-policy decisions, unresolved limits, and the handoff
    contract that issue `#15` will consume
- Step type:
  - documentation and issue closure preparation
- Files to modify or add if needed:
  - `docs/roadmap/issues/issue-14-semantic-mapping-rules.md`
  - `docs/context/current_status.md`
  - `docs/roadmap/cvn_generation_roadmap.md`
  - `docs/pipeline/known_limitations.md` if new limitations are found
- Root task `9 / 9`:
  - document the final policy and prepare the downstream handoff to issue `#15`
- Subtask `9.1 / 9`:
  - record any deviations from the original issue plan
- Subtask `9.2 / 9`:
  - leave a clear downstream checklist for issue `#15`
- Subtask `9.3 / 9`:
  - update roadmap and context documents when issue state changes

### Main Objective

- define a stable semantic mapping policy that translates normalized CVN
   metadata into domain-oriented generation rules for types, naming,
   multiplicity, controlled vocabularies, and explicit exceptions
- keep semantic cleanup outside `src/generated/` and preserve CVN code
  traceability for every domain-facing decision
- preserve semantic distinctions already surfaced by
  `reference_resolution.semantic_reference_kind` and
  `reference_resolution.serialization_pattern` instead of collapsing all
  controlled references into one policy bucket

### Execution Steps

1. define the semantic output contract
2. inventory representative enriched normalized cases
3. define base type-mapping rules
4. define controlled-reference policy over existing normalized classifications
5. define naming rules for domain artifacts
6. define multiplicity and optionality rules
7. define treatment for `choice`, wrappers, and recursion
8. design the override mechanism
9. validate rules against representative examples from each reference kind
10. document the final policy and unresolved limits

### Step `1` - Define The Semantic Output Contract

- decide which hand-maintained structure will represent semantic mapping rules
  for later consumption
- the contract should be explicit enough for issue `#15` to consume without
  reinterpreting prose documentation
- the contract should support both generic rules and targeted per-code or
  per-pattern exceptions

### Step `2` - Inventory Representative Normalized Cases

- review enriched normalized entries from issue `#13` and select
  representative samples across manual types, multiplicity combinations,
  serialization patterns, semantic reference kinds, wrappers, and known
  `choice` structures
- use this inventory to ensure semantic policy is grounded in real repository
  inputs rather than hypothetical cases
- preserve traceability from each representative case back to CVN `code`,
  `xml_path`, and source metadata
- ensure the sample set includes at minimum:
  - compact enum-like direct table case such as `CVN_SEX_A`
  - subtype-backed case such as `CVN_KNOW_A`
  - side-package registry case such as `ENTITY@Entity.xsd`
  - side-package thesaurus case such as `THESAURUS@thesaurus.xsd`
  - hierarchical thematic case such as `UNESCO_CODES`
  - unresolved case such as `CVN_AGENCY_C`
  - under-traced case such as `CVN_INTERVENTION_A` or `CVN_PRUEBA`

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

### Step `4` - Define Controlled-Reference Policy

- use `reference_resolution.semantic_reference_kind` as the main policy input
  rather than rediscovering categories from raw table names alone
- semantic policy must handle at minimum these normalized kinds:
  - compact enum-like table
  - compact scale or measure table
  - identifier-type table
  - scope table
  - subtype-backed controlled family
  - hierarchical thematic classification
  - side-package registry
  - side-package thesaurus or vocabulary
  - unresolved manual-only reference
  - technically present but under-traced table
- define open versus closed treatment for each kind
- define enum eligibility rules for compact internal tables
- define explicit treatment for:
  - `Entity`-backed registry references
  - `Thesaurus`-backed vocabulary references
  - `UNESCO_CODES` hierarchical thematic references
  - subtype-backed `Subtype@Subtypes.xsd` families
  - unresolved references such as `CVN_AGENCY_C`
  - under-traced tables such as `CVN_INTERVENTION_A` and `CVN_PRUEBA`
- document reasoning so issue `#15` can apply policy mechanically

### Step `5` - Define Naming Rules For Domain Artifacts

- define naming rules for classes, fields, and modules in the future semantic
  generation layer
- decide how multilingual manual labels are normalized into stable identifiers
- define how to resolve naming collisions, repeated labels, technical suffixes,
  and XML-oriented names that should not leak into the future domain API by
  default
- preserve code-level traceability even when domain names differ from technical
  XML names
- keep room for naming distinctions where semantic policy chooses different
  domain shapes for registry, thesaurus, subtype-backed, or unresolved
  references

### Step `6` - Define Multiplicity And Optionality Rules

- define how `manual_obligatory` and `manual_multiplicity` map to required
  fields, optional fields, and `list[T]`
- define how later generation should behave when structural defaults from the
  generated bindings are weaker than the intended domain semantics
- keep the policy clear enough to restore semantic meaning lost in the
  structural layer
- keep multiplicity rules orthogonal to controlled-reference kind so issue
  `#15` can combine both deterministically

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
  semantic reference kind, serialization pattern, reference table, or technical
  path
- keep overrides versioned, reviewable, and separate from generated output

### Step `9` - Validate Rules Against Representative Examples

- check the proposed policy against a representative set of normalized cases
- validation should include at least:
  - a simple scalar field
  - a controlled table expected to become an enum
  - a compact controlled table expected to remain open
  - a side-package registry reference
  - a side-package thesaurus or hierarchical thematic reference
  - a subtype-backed controlled family
  - an unresolved or under-traced reference
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
2. which categories of controlled references should become strict enums and
   which should remain open representations
3. how resolved external or hierarchical references such as
   `ENTITY@Entity.xsd`, `THESAURUS@thesaurus.xsd`, and `UNESCO_CODES` should be
   represented in the semantic layer
4. whether wrappers like flexible dates and durations should become primitives,
   unions, or dedicated value objects in the future domain API
5. what exact shape the override registry should take so later generation stays
   deterministic and reviewable

## Minimum Decisions Required

1. which wrappers collapse to primitives in the domain layer
2. which controlled-reference kinds become enums and which remain open
   representations
3. how multilingual names affect class and field naming
4. how multiplicity becomes optional fields versus `list[T]`
5. how registry, thesaurus, hierarchical, subtype-backed, unresolved, and
   under-traced references remain represented
6. how code-specific exceptions are registered outside the generic algorithm

## Constraints To Respect

- many structural XSD types are technical wrappers rather than domain concepts
- some reference tables are internal and some are external to the package
- `choice` appears rarely but in high-value structures
- XML interoperability metadata should not leak into the future domain API by
  default
- issue `#13` already performs source-resolution and reference-kind
  classification, so issue `#14` must build policy on top of that layer rather
  than duplicating it

## Relevant Known Inputs

- structural bindings preserve fidelity but expose known limitations for
  `choice`, multiplicity, and wrapper ergonomics
- auxiliary structural bindings now exist for:
  - `ReferenceTables.xsd`
  - `Subtypes.xsd`
  - `Entity_v1.4.xsd`
  - `Thesaurus.xsd`
- normalized aggregate entries already include additive
  `reference_resolution` metadata with typed status, source family,
  serialization pattern, semantic reference kind, and traceability
- the official source package version recently delivered by FECYT includes
  side-package material for several references that must now be treated as
  recently added auxiliary modules rather than opaque placeholders:
  - `ENTITY@Entity.xsd` is represented by the `Entity` family
  - `THESAURUS@thesaurus.xsd` is represented by the `Thesaurus` family
  - many Annex-I tables are materialized in `ReferenceTables.xml`
- not all manual references are fully resolved from the package alone; a known
  example is `CVN_AGENCY_C`
- some technically present tables remain documented as under-traced and require
  explicit fallback policy rather than silent collapse

## Status

- Status: pending
