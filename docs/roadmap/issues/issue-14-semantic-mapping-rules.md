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

<<<<<<< Updated upstream
=======
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
- `reference_resolution.source_artifact`
- `reference_resolution.serialization_pattern`
- `reference_resolution.semantic_kind`
- `reference_resolution.trace`

Issue `#14` must consume that typed metadata. It must not rebuild source-family,
side-package, subtype-backed, or hierarchical-reference detection from prose
documents or ad hoc table-name inspection.

>>>>>>> Stashed changes
## Planned Execution Steps

The implementation of issue `#14` should begin from the normalized metadata
layer produced in issue `#13` and should leave issue `#15` with an explicit,
<<<<<<< Updated upstream
deterministic semantic policy to consume.
=======
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
    `xml_path`, `reference_resolution.semantic_kind`, or serialization pattern
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
  - decide whether overrides can target `reference_resolution.semantic_kind`
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
>>>>>>> Stashed changes

## Established Semantic Policy Plan

The issue `#14` planning session established the decisions below. These
decisions are the operative specification for implementation work.

### Scope Boundary

Issue `#14` consumes only typed normalized metadata from issue `#13` as policy
inputs. Raw XML, raw XSD, and generated structural classes may be inspected for
human validation or override evidence, but they must not become base semantic
inputs.

Required normalized inputs are:

- `code`
- `xml_path`
- `manual_type`
- `manual_multiplicity`
- `manual_obligatory`
- `reference_resolution.status`
- `reference_resolution.source_family`
- `reference_resolution.source_artifact`
- `reference_resolution.resolved_name`
- `reference_resolution.serialization_pattern`
- `reference_resolution.semantic_kind`
- `reference_resolution.trace`

Issue `#14` must not reimplement source-family detection, serialization-pattern
classification, semantic-kind classification, side-package detection,
subtype-backed detection, unresolved-reference detection, under-traced-table
detection, manual/tree overlap computation, or `xml_path` construction.

If a repeated semantic decision needs raw source inspection, the missing data
belongs in issue `#13`. If the need is isolated and not generalizable, issue
`#14` may express it as an explicit override with trace evidence.

### Contract Families

The semantic policy contract should be implemented as explicit typed Python
structures, using `dataclass` records and `Enum` values. The root contract should
be an indexed `SemanticPolicyBundle`.

Minimum contract families are:

- `SemanticPolicyBundle`
- `SemanticFieldPolicy`
- `ReferenceKindPolicy`
- `BaseTypePolicy`
- `NamingPolicy`
- `MultiplicityPolicy`
- `ChoiceWrapperPolicy`
- `OverrideRule`
- `ValidationCaseDefinition`
- `PolicyMetadata`
- `SemanticDecisionTrace`

The bundle should expose deterministic lookups by CVN `code`, `xml_path`,
`reference_resolution.semantic_kind`, `reference_resolution.serialization_pattern`,
`manual_type`, and wrapper family.

### Policy Enums

The semantic contract should define these policy categories:

| Category | Values |
| --- | --- |
| `SemanticBaseKind` | `TEXT`, `CONTROLLED_REFERENCE`, `DATE_LIKE`, `DECIMAL_NUMBER`, `BOOLEAN`, `DURATION_LIKE`, `UNKNOWN` |
| `WrapperPolicyKind` | `COLLAPSE`, `VALUE_OBJECT_CANDIDATE`, `CHOICE_OBJECT_CANDIDATE`, `PRESERVE_STRUCTURAL_TRACE` |
| `PresenceKind` | `REQUIRED`, `OPTIONAL`, `UNKNOWN` |
| `CardinalityKind` | `SINGLE`, `REPEATED`, `UNKNOWN` |
| `StructuralLimitationFlag` | `CHOICE_NOT_ENFORCED`, `LIST_MIN_OCCURS_WEAK`, `OBJECT_TYPED_ATTRIBUTE`, `WRAPPER_ERGONOMICS` |
| `DomainShapeKind` | `PLAIN_VALUE`, `STRICT_ENUM_CANDIDATE`, `OPEN_CODED_VALUE`, `MEASURE_OR_SCALE_VALUE`, `IDENTIFIER_REFERENCE`, `SCOPE_REFERENCE`, `SUBTYPE_BACKED_VALUE`, `HIERARCHICAL_CODE_REFERENCE`, `REGISTRY_REFERENCE`, `VOCABULARY_REFERENCE`, `UNRESOLVED_REFERENCE`, `UNDER_TRACED_REFERENCE` |
| `PolicyConfidence` | `HIGH`, `MEDIUM`, `LOW`, `REQUIRES_REVIEW` |
| `EnumEligibility` | `ELIGIBLE`, `INELIGIBLE`, `REVIEW_REQUIRED` |

### Lookup And Override Precedence

Semantic policy resolution must use this precedence order:

1. `code + xml_path` override
2. `code` override
3. `xml_path` override
4. `reference_resolution.semantic_kind` policy or override
5. `reference_resolution.serialization_pattern` refinement
6. `manual_type` base policy
7. wrapper policy
8. presence/cardinality policy
9. global defaults

Overrides may change only semantic-policy outputs such as `domain_shape_kind`,
`fallback_shape_kind`, `enum_eligibility`, `policy_confidence`,
`wrapper_policy`, `presence_kind`, `cardinality_kind`, `normalized_name`,
`naming_confidence`, `structural_limitation_flags`, notes, and diagnostics.

Overrides must not mutate normalized input facts such as `code`, `xml_path`,
`manual_type`, `manual_reference_table`, `reference_resolution.status`,
`reference_resolution.source_family`, `reference_resolution.semantic_kind`,
`reference_resolution.serialization_pattern`, or upstream trace facts.

Same-priority conflicts should produce `PolicyConfidence.REQUIRES_REVIEW` rather
than silently choosing one rule.

### Base Type Policy

Issue `#14` defines semantic base kinds, not final Python/domain output types.
Issue `#15` will map these semantic kinds to concrete generated Python artifacts.

| `manual_type` condition | Semantic base kind |
| --- | --- |
| `Alphanumeric` without resolved controlled reference | `TEXT` |
| `Alphanumeric` with `reference_resolution.semantic_kind` | `CONTROLLED_REFERENCE` |
| `Date` | `DATE_LIKE` |
| `Double` | `DECIMAL_NUMBER` |
| `Boolean` | `BOOLEAN` |
| `Duration` | `DURATION_LIKE` |
| missing or unknown manual type | `UNKNOWN` |

Wrappers should collapse only when they add no domain information and do not
represent meaningful `xs:choice`, variable granularity, or structural
traceability concerns. `FlexibleDatesType`, `OfficialIdType`, `EntityTypeType`,
and `EntityNameType` must be marked as `CHOICE_OBJECT_CANDIDATE`.

### Presence And Cardinality Policy

| Normalized field | Value | Policy output |
| --- | --- | --- |
| `manual_obligatory` | `True` | `PresenceKind.REQUIRED` |
| `manual_obligatory` | `False` | `PresenceKind.OPTIONAL` |
| `manual_obligatory` | `None` | `PresenceKind.UNKNOWN` |
| `manual_multiplicity` | `True` | `CardinalityKind.REPEATED` |
| `manual_multiplicity` | `False` | `CardinalityKind.SINGLE` |
| `manual_multiplicity` | `None` | `CardinalityKind.UNKNOWN` |

Issue `#14` records semantic cardinality. Issue `#15` decides concrete Pydantic
field shape and validation behavior.

### Reference Kind Policy Matrix

| `reference_resolution.semantic_kind` | Domain shape | Fallback shape | Enum eligibility default | Confidence default |
| --- | --- | --- | --- | --- |
| `COMPACT_ENUM_LIKE_TABLE` | `STRICT_ENUM_CANDIDATE` | `OPEN_CODED_VALUE` | eligibility criteria required | `HIGH` or `REVIEW_REQUIRED` |
| `COMPACT_SCALE_OR_MEASURE` | `MEASURE_OR_SCALE_VALUE` | `OPEN_CODED_VALUE` | `REVIEW_REQUIRED` | `MEDIUM` |
| `IDENTIFIER_TYPE_TABLE` | `IDENTIFIER_REFERENCE` | `OPEN_CODED_VALUE` | `INELIGIBLE` for full identifier | `MEDIUM` |
| `SCOPE_TABLE` | `SCOPE_REFERENCE` | `OPEN_CODED_VALUE` | eligibility criteria required | `MEDIUM` |
| `SUBTYPE_BACKED_CONTROLLED_FAMILY` | `SUBTYPE_BACKED_VALUE` | `SUBTYPE_BACKED_VALUE` | `INELIGIBLE` until strict bridge exists | `MEDIUM` |
| `HIERARCHICAL_THEMATIC_CLASSIFICATION` | `HIERARCHICAL_CODE_REFERENCE` | `HIERARCHICAL_CODE_REFERENCE` | `INELIGIBLE` | `HIGH` |
| `SIDE_PACKAGE_REGISTRY` | `REGISTRY_REFERENCE` | `REGISTRY_REFERENCE` | `INELIGIBLE` | `HIGH` |
| `SIDE_PACKAGE_THESAURUS_OR_VOCABULARY` | `VOCABULARY_REFERENCE` | `VOCABULARY_REFERENCE` | `INELIGIBLE` | `HIGH` |
| `UNRESOLVED_MANUAL_ONLY_REFERENCE` | `UNRESOLVED_REFERENCE` | `UNRESOLVED_REFERENCE` | `INELIGIBLE` | `REQUIRES_REVIEW` |
| `UNDER_TRACED_REFERENCE_TABLE` | `UNDER_TRACED_REFERENCE` | `UNDER_TRACED_REFERENCE` | `INELIGIBLE` | `REQUIRES_REVIEW` |

Strict enum eligibility requires a resolved `REFERENCE_TABLE` source, no
hierarchy, no delegate, not subtype-backed, not side-package, not unresolved,
not under-traced, reasonable item count, stable codes, usable labels, and no
`OTHERS` or delegate-open behavior unless explicitly accepted by override.

### Naming Policy

The domain-facing naming policy is Spanish-first because the tool is aimed at a
Spanish research and university audience.

Accepted naming rules:

- use Spanish `manual_name` as the default label source
- use `manual_short_name` only when clearer and non-ambiguous
- normalize domain-facing identifiers to ASCII
- remove accents and punctuation deterministically
- use `snake_case` for fields and modules
- use `PascalCase` for classes
- preserve important acronyms such as `CVN`, `UNESCO`, `ORCID`, `DOI`, `ISBN`,
  `ISSN`, and `H`
- preserve CVN source identifiers literally in trace metadata
- use English technical names for internal codegen and policy-contract classes

Collision resolution should prefer readable Spanish names first, then semantic
context, then CVN-code suffix as the last deterministic fallback. Ambiguous
names should carry `naming_confidence=REQUIRES_REVIEW`.

### Representative Inventory And Validation Results

| Case | Role | Expected policy result | Validation |
| --- | --- | --- | --- |
| `000.010.000.020` / `Nombre` | simple scalar | `PLAIN_VALUE`, `TEXT`, enum ineligible | pass |
| `CVN_SEX_A` / `000.010.000.030` | compact closed enum-like table | `STRICT_ENUM_CANDIDATE`, enum eligible | pass |
| `CVN_ENTITY_TYPE` / `010.010.000.040` | compact open/review controlled table | `OPEN_CODED_VALUE`, enum review required | pass |
| `CVN_KNOW_A` / `050.030.010.030` | subtype-backed family | `SUBTYPE_BACKED_VALUE`, enum ineligible | pass |
| `ENTITY@Entity.xsd` / `010.010.000.020` | side-package registry | `REGISTRY_REFERENCE`, enum ineligible | pass |
| `THESAURUS@thesaurus.xsd` / `010.010.000.260` | side-package vocabulary | `VOCABULARY_REFERENCE`, enum ineligible | pass |
| `UNESCO_CODES` / `010.010.000.220` | hierarchical thematic classification | `HIERARCHICAL_CODE_REFERENCE`, enum ineligible | pass |
| `CVN_AGENCY_C` / `060.010.000.030` | unresolved manual-only reference | `UNRESOLVED_REFERENCE`, review required | pass |
| `CVN_INTERVENTION_A` | under-traced table, primary case | `UNDER_TRACED_REFERENCE`, review required | pass |
| `CVN_PRUEBA` | under-traced table, secondary case | `UNDER_TRACED_REFERENCE`, review required | pass |
| `FlexibleDatesType` | `xs:choice` date wrapper | `CHOICE_OBJECT_CANDIDATE` with limitation flags | pass |
| `OfficialIdType` | `xs:choice` identifier wrapper | `CHOICE_OBJECT_CANDIDATE` with limitation flags | pass |
| `EntityTypeType` | `xs:choice` entity type wrapper | `CHOICE_OBJECT_CANDIDATE` with limitation flags | pass |
| `EntityNameType` | `xs:choice` entity name wrapper | `CHOICE_OBJECT_CANDIDATE` with limitation flags | pass |

Under-traced tables may not produce generated domain fields in issue `#15` unless
future normalized entries reference them.

### Handoff Checklist For Issue `#15`

Issue `#15` should:

1. consume `SemanticPolicyBundle`
2. avoid re-deriving auxiliary-source resolution
3. generate by `domain_shape_kind`
4. preserve `SemanticDecisionTrace`
5. honor `enum_eligibility`
6. honor `fallback_shape_kind`
7. honor wrapper policies
8. keep domain-facing names Spanish-first and normalized
9. avoid strict enums for registry, thesaurus, hierarchical, subtype-backed,
   unresolved, or under-traced references
10. avoid under-traced field output unless normalized metadata later references
    those tables

### Established Open Limits

The following limitations remain visible for issue `#15`:

- `Subtype_Spa.xml` lacks a strict per-table bridge such as `CVN_KNOW_A` to
  subtype records
- `CVN_AGENCY_C` remains unresolved from the package alone
- `CVN_INTERVENTION_A` and `CVN_PRUEBA` remain technically present but
  under-traced
- generated bindings do not enforce `xs:choice` mutual exclusivity
- generated list defaults do not reliably enforce `minOccurs`
- final domain emission remains deferred to issue `#15`

### Main Objective

- define a stable semantic mapping policy that translates normalized CVN
  metadata into domain-oriented generation rules for types, naming,
  multiplicity, controlled vocabularies, and explicit exceptions
- keep semantic cleanup outside `src/generated/` and preserve CVN code
  traceability for every domain-facing decision
<<<<<<< Updated upstream
=======
- preserve semantic distinctions already surfaced by
  `reference_resolution.semantic_kind` and
  `reference_resolution.serialization_pattern` instead of collapsing all
  controlled references into one policy bucket
>>>>>>> Stashed changes

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

<<<<<<< Updated upstream
- classify reference tables into semantic categories such as:
  - internal CVN controlled tables that may become enums
  - ISO or other large standardized tables that may require a different policy
  - external or unresolved tables that cannot safely become closed enums from
    the canonical package alone
- decide which controlled sets become strict enums and which remain strings,
  aliases, or external-reference representations
- document the reasoning so issue `#15` can apply the same policy
=======
- use `reference_resolution.semantic_kind` as the main policy input
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
>>>>>>> Stashed changes

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
<<<<<<< Updated upstream
  reference table, or technical path
=======
  `reference_resolution.semantic_kind`, serialization pattern, reference table,
  or technical path
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
=======
- auxiliary structural bindings now exist for:
  - `ReferenceTables.xsd`
  - `Subtypes.xsd`
  - `Entity_v1.4.xsd`
  - `Thesaurus.xsd`
- normalized aggregate entries already include additive
  `reference_resolution` metadata with typed status, source family,
  serialization pattern, semantic kind, and traceability
>>>>>>> Stashed changes
- the official source package version recently delivered by FECYT includes
  side-package material for several references that must now be treated as
  recently added auxiliary modules rather than opaque placeholders:
  - `ENTITY@Entity.xsd` is represented by the `Entity` family
  - `THESAURUS@thesaurus.xsd` is represented by the `Thesaurus` family
  - many Annex-I tables are materialized in `ReferenceTables.xml`
- not all manual references are fully resolved from the package alone; a known
  example is `CVN_AGENCY_C`

## Adjustments Made During Implementation

- No code implementation has been performed yet.
- Pre-implementation planning corrected the issue scope so semantic policy
  consumes enriched normalized metadata from issue `#13` instead of inspecting
  raw auxiliary sources as primary inputs.
- The policy input names were aligned with the implemented normalization
  contract: `reference_resolution.source_artifact` and
  `reference_resolution.semantic_kind`.
- Future issue documents for `#15`, `#16`, and `#17` were aligned with the
  agreed semantic-policy handoff before starting code.

## Implementation Performed

- None yet. Issue `#14` is planned with an agreed execution policy, but semantic
  policy modules, tests, and validation code are not implemented.

## Verification

- Documentation consistency was checked through issue-doc review and
  `git diff --check`.
- No code tests have been run for issue `#14` because no implementation exists
  yet.
- Future verification must cover semantic-policy construction, lookup
  precedence, override conflict handling, base type mapping, reference-kind
  mapping, enum eligibility, wrapper policy, naming policy, and representative
  validation cases.

## Findings

- Issue `#14` needs a typed semantic policy contract rather than ad hoc mapping
  logic inside the future generator.
- Raw XML, raw XSD, and generated structural classes may support validation and
  trace evidence, but normalized metadata is the operative semantic input.
- Override policy must change only semantic outputs, not upstream normalized
  facts.
- `CVN_ENTITY_TYPE` is not safe for blind strict-enum generation because its
  compact controlled table has open/review behavior.

## Known Limitations

- `Subtype_Spa.xml` lacks a strict per-table bridge such as `CVN_KNOW_A` to
  subtype records.
- `CVN_AGENCY_C` remains unresolved from the source package alone.
- `CVN_INTERVENTION_A` and `CVN_PRUEBA` remain technically present but
  under-traced.
- Generated structural bindings do not enforce `xs:choice` mutual exclusivity.
- Generated list defaults do not reliably enforce every `minOccurs` constraint.
- Final domain model emission remains deferred to issue `#15`.

## Impact On Future Issues

- Issue `#15` must consume `SemanticPolicyBundle` and generate concrete domain
  artifacts from semantic-policy outputs rather than redefining semantic
  classification.
- Issue `#16` must test semantic-policy behavior separately from generator
  output behavior.
- Issue `#17` must document `SemanticPolicyBundle` as the source-of-truth
  handoff between normalized metadata and domain generation.

## Status

- Status: planned with agreed execution policy
