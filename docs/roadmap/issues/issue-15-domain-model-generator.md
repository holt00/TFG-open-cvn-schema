# Issue 15 - Implement The Domain Pydantic Model Generator

## Summary

Issue `#15` will generate cleaner domain models from normalized metadata and
semantic mapping rules.

## Corrected Prerequisite Chain

Issue `#15` must consume two already prepared upstream layers:

1. auxiliary structural visibility from hotfix `#4`
2. enriched normalized metadata with `reference_resolution` from issue `#13`
   after hotfix `#5`

This issue must not redo source discovery or auxiliary-reference resolution.
Those responsibilities are already implemented upstream and should only be
consumed through the semantic policy finalized in issue `#14`.

## Original Goal

- emit readable, traceable, reproducible domain Pydantic models from the
  normalized metadata layer

## Original Plan

1. traverse `CVNItem`, `Property`, and `Indicator`
2. generate domain models for representative CVN blocks
3. factor reusable domain components where appropriate
4. preserve CVN code traceability in emitted code
5. keep output separate from structural bindings
6. make regeneration deterministic

## Corrected Generator Responsibilities

The generator design for issue `#15` must support distinct domain
representations for the controlled-reference classes already surfaced by
normalization and semantic policy.

At minimum, the generator must support:

1. strict enums or near-enums for closed compact tables
2. open coded-value representations for open controlled tables
3. structured external registry references for `Entity`-backed values
4. hierarchical subject or vocabulary references for `Thesaurus` and
   `UNESCO_CODES`
5. subtype-backed values with traceability to subtype codification support
6. explicit unresolved or under-traced reference representations when the
   package cannot support a stronger domain guarantee

The generator should prefer domain shapes that preserve semantic class
distinctions instead of flattening all controlled references to `str` plus
comments.

## Semantic Policy Handoff From Issue `#14`

Issue `#15` must treat the semantic policy contract from issue `#14` as its
generator input contract. The expected upstream policy artifact is
`SemanticPolicyBundle`.

The generator should consume these semantic-policy decisions directly:

- `domain_shape_kind`
- `fallback_shape_kind`
- `enum_eligibility`
- `policy_confidence`
- `wrapper_policy`
- `presence_kind`
- `cardinality_kind`
- `normalized_name`
- `naming_confidence`
- `structural_limitation_flags`
- `SemanticDecisionTrace`

Issue `#15` may decide concrete Python emission details, such as `Enum`,
`Literal`, Pydantic model classes, wrapper classes, or open coded-value records.
It must not change the semantic meaning established by issue `#14`.

The generator must not emit strict enums for policy outputs representing:

- registry references
- thesaurus or vocabulary references
- hierarchical code references
- subtype-backed values
- unresolved references
- under-traced references

Under-traced references should remain explicit in policy-aware generator logic,
but issue `#15` should not emit fields for under-traced tables unless normalized
metadata entries later reference those tables.

## Recommended First Scope

- identification
- contact information
- basic personal data
- a representative subset of `CVNItem` blocks
- at least one representative block for each major controlled-reference family
  already classified upstream

## Expected Outputs

- executable generator code
- first generated domain Pydantic models
- reusable shared domain components
- explicit traceability from generated domain artifacts back to CVN code and
  semantic-policy decisions where needed

## Generation Principle

- consume normalized metadata rather than generating from raw XSDs directly
- consume semantic policy from issue `#14` and enriched normalized metadata from
  issue `#13` rather than re-deriving source-of-truth rules in the generator
- keep `src/generated/` as structural layer and emit domain output separately

## Minimum Corrected Scope

Issue `#15` should document and implement at minimum:

1. traversal from normalized CVN item/group structure into generation units
2. deterministic mapping from semantic policy outputs to domain model shapes
3. different emitted shapes for enum-like, open coded, registry, thesaurus,
   hierarchical, subtype-backed, unresolved, and under-traced references
4. reusable domain components only where they preserve semantic meaning instead
   of erasing distinctions
5. regeneration determinism and traceability back to normalized input and CVN
   code

## Questions Still To Decide

1. whether strict enums should become Python `Enum`, `Literal`, or another
   constrained representation
2. what shape should represent `Entity`-backed references in generated domain
   models
3. what shape should represent hierarchical thesaurus and `UNESCO_CODES`
   references
4. how subtype-backed families should preserve subtype traceability in generated
   output
5. how unresolved or under-traced references should remain explicit without
   pretending stronger validation than repository can currently support

## Constraints To Respect

- issue `#13` already resolves auxiliary-reference source families and semantic
  kinds; generator must not duplicate that logic
- issue `#14` is responsible for semantic policy decisions; generator must
  implement those decisions, not redefine them
- generated domain artifacts must stay separate from structural bindings under
  `src/generated/`
- code-level traceability should remain preserved even when generated names and
  domain shapes differ from XML-oriented structures

## Wrapper Traceability Limitation And Hotfix `#8` Handoff

During issue `#15` implementation planning, the then-current normalized tree
metadata was checked for wrapper type evidence needed to apply semantic wrapper
policies automatically.

The relevant wrapper policy names are:

1. `FlexibleDatesType`
2. `OfficialIdType`
3. `EntityTypeType`
4. `EntityNameType`

Those names existed in `CVN.xsd`, generated structural bindings, and issue `#14`
semantic wrapper-policy validation cases, but they were not exposed by the
normalized handoff available during the original issue `#15` implementation. In
particular, `TreePathEntry.tree_value` did not carry these wrapper type names for
real canonical entries.

Issue `#15` therefore correctly avoided attaching wrapper-aware field shapes by
scanning raw XSD files or generated structural bindings inside the domain
generator. That would have violated the corrected generator boundary: issue
`#15` consumes normalized metadata and `SemanticPolicyBundle`; it does not
rediscover structural meaning.

The corrective follow-up is tracked in:

- `docs/roadmap/hotfixes/hotfix-8-wrapper-type-traceability-in-normalized-handoff.md`

Before hotfix `#8` was implemented, issue `#15` had to:

- keep wrapper policy decisions visible where already provided by issue `#14`
- avoid pretending wrapper auto-attachment is implemented
- generate scalar, controlled-reference, enum, trace, and deterministic output
  behavior independently from wrapper auto-attachment
- leave future wrapper-aware field emission ready to consume typed wrapper
  evidence once hotfix `#8` extends the handoff

Hotfix `#8` has now implemented that typed handoff. Canonical domain generation
passes `CVN.xsd` and `Common.xsd` into normalization, receives
`StructuralTypeEvidence`, attaches wrapper policies through semantic policy, and
maps wrapper-aware fields to shared wrapper value components without raw XSD
inspection inside the generator.

## Decisions Recorded During Issue `#15` Execution

This section records implementation decisions taken during the interactive issue
`#15` execution so future sessions can resume from repository documentation
rather than reconstructing the chat history.

### Execution And Verification Cadence

- The default verification command for this issue is the fast full-suite command:
  `uv run pytest -n auto tests`.
- Single-file pytest commands should be used only for debugging a specific
  failure, not as the normal documented verification path.
- Tests are added at the end of each task-level implementation slice rather than
  after every tiny helper, unless a failure requires tighter isolation.
- Code changes are made manually by the user unless explicit edit authorization
  is given; documentation changes may be applied when explicitly requested.

### Output Architecture

- Hand-maintained generator logic belongs in `src/cvn_codegen/`.
- The domain generator implementation is centered on
  `src/cvn_codegen/domain_model_generator.py`.
- Generator intermediate representation records belong in
  `src/cvn_codegen/domain_model_types.py`.
- Shared hand-maintained domain components belong in `src/models/cvn/`.
- Generated domain models will be emitted under `src/models/cvn/generated/`.
- Structural bindings under `src/generated/` remain a separate generated
  interoperability layer and must not be edited manually.
- Shared components are hand-maintained for now, while final block/domain models
  are generated. This avoids duplicating common component classes in generated
  output and keeps generated model files cleaner.

### Runtime Dependency Decision

- `pydantic` is an explicit project runtime dependency because generated domain
  models and shared domain components import Pydantic directly.
- The dependency should be added through the package manager command
  `uv add pydantic`, not by manually editing `pyproject.toml`.
- `xsdata-pydantic` remains part of the `codegen` dependency group because it is
  tied to structural generation rather than the final domain model runtime.

### Intermediate Representation Decision

The generator IR uses small frozen dataclasses and stores final type names as
strings to keep rendering deterministic and separate from semantic-policy
resolution.

The accepted IR records are:

1. `DomainFieldSpec`
2. `DomainEnumSpec`
3. `DomainTypeSpec`
4. `DomainGenerationUnit`
5. `DomainGenerationResult`

`DomainFieldSpec` records at minimum:

- `field_name`
- `python_type`
- `code`
- `xml_paths`
- `required`
- `repeated`
- `domain_shape_kind`
- `enum_eligibility`
- `trace`

`DomainGenerationResult` carries generated units, enum specs, normalized entries,
and semantic policies so tests and later emitters can validate traceability and
deterministic ordering.

### Policy Index And Grouping Decisions

- `build_semantic_policy_index(...)` builds one `SemanticFieldPolicy` per
  normalized code by calling `build_semantic_field_policy(...)` from issue `#14`.
- The policy index is ordered deterministically by CVN code.
- Grouping is based on `TreePathEntry.tree_cvn_item_code` where available.
- Entries without tree paths go to the `__no_tree__` group.
- Entries with tree paths but without a CVN item code go to the
  `__no_cvn_item__` group.
- The same normalized entry must not appear twice in the same group even when it
  has multiple tree paths in that group.

### Naming And Collision Decisions

- The generator reuses `SemanticFieldPolicy.naming_policy.normalized_field_name`
  and `normalized_class_name` instead of redefining naming rules.
- CVN code suffixes are added to field names only when a real field-name
  collision occurs inside the same generation unit.
- When a collision occurs, all fields in that collision group receive a CVN code
  suffix to avoid a confusing mix of one clean name and one suffixed name.
- The suffix format replaces `.` with `_`, for example
  `titulo_060_010_000_020`.
- CVN codes are always preserved in trace metadata even when they are not present
  in the Python field name.

### Base Type Mapping Decisions

- `SemanticBaseKind.TEXT` maps to `str`.
- `SemanticBaseKind.BOOLEAN` maps to `bool`.
- `SemanticBaseKind.DECIMAL_NUMBER` maps to `Decimal`.
- `SemanticBaseKind.DATE_LIKE` maps to `str` for now.
- `SemanticBaseKind.DURATION_LIKE` maps to `str` for now.
- unknown base kinds map to `object` rather than pretending stronger validation.
- Repeated fields wrap the resolved type as `list[...]`.
- Controlled references are detected through
  `SemanticBaseKind.CONTROLLED_REFERENCE` before applying domain-shape mapping.

### Strict Enum Decisions

- Strict enum emission is allowed only when
  `domain_shape_kind == STRICT_ENUM_CANDIDATE` and
  `enum_eligibility == ELIGIBLE`.
- `REVIEW_REQUIRED` and `INELIGIBLE` never emit strict enums in issue `#15`.
- Reviewed or ineligible strict-enum candidates fall back to safe non-enum
  representation, currently `str` until later emission logic refines the field
  type.
- Enum class names are derived from the semantic class name and receive an
  `Enum` suffix when needed.
- Enum member names are derived from preferred labels when they form valid
  identifiers; otherwise they fall back to `CODE_<normalized_code>`.
- `DomainEnumSpec` is built from explicit `ReferenceTableEnumEvidence`, not from
  table-name-specific generator logic.
- Enum specs are deduplicated by `source_reference` because multiple fields may
  reuse the same controlled table.

### Non-Enum Controlled Reference Decisions

The generator maps non-enum controlled-reference shapes to shared component type
names instead of flattening every case to `str`.

Accepted mappings:

| `DomainShapeKind` | Python component type |
| --- | --- |
| `OPEN_CODED_VALUE` | `OpenCodedValue` |
| `MEASURE_OR_SCALE_VALUE` | `MeasureOrScaleValue` |
| `IDENTIFIER_REFERENCE` | `IdentifierReference` |
| `SCOPE_REFERENCE` | `ScopeReference` |
| `SUBTYPE_BACKED_VALUE` | `SubtypeBackedValue` |
| `HIERARCHICAL_CODE_REFERENCE` | `HierarchicalCodeReference` |
| `REGISTRY_REFERENCE` | `RegistryReference` |
| `VOCABULARY_REFERENCE` | `VocabularyReference` |
| `UNRESOLVED_REFERENCE` | `UnresolvedReference` |
| `UNDER_TRACED_REFERENCE` | `UnderTracedReference` |

### Shared Component Decisions

- `src/models/cvn/components.py` contains shared hand-maintained component
  classes for non-enum controlled references.
- The shared controlled-reference base is `BaseControlledReferenceValue` with
  `code` and `label` fields.
- `HierarchicalCodeReference` adds `parent_code`.
- `RegistryReference` adds `registry_id`.
- `VocabularyReference` adds `vocabulary_source`.
- `UnresolvedReference` and `UnderTracedReference` add `raw_reference`.
- These components do not inherit from `BaseCvnDomainModel`; they are reusable
  value objects, while generated final models may later inherit from
  `BaseCvnDomainModel`.

### Trace Component Decisions

The accepted future trace contract is richer than the initial minimal proposal.
When implemented, `CvnTrace` should contain:

- `code: str`
- `xml_paths: tuple[str, ...]`
- `base_kind: str`
- `domain_shape_kind: str`
- `enum_eligibility: str`
- `source_reference: str | None = None`
- `notes: tuple[str, ...] = ()`

`BaseCvnDomainModel` should expose:

- `cvn_trace: CvnTrace | None = None`

The trace contract intentionally does not yet include full internal
`SemanticDecisionTrace.applied_rules`, diagnostics, `policy_confidence`, or
wrapper-policy fields. Those internal policy details can remain in generator
trace metadata until there is a concrete domain-facing need.

### Wrapper Decision

- Wrapper auto-attachment is implemented after issue `#15` through hotfix `#8`.
- The generator consumes `SemanticFieldPolicy.wrapper_type_names` and shared
  wrapper value components instead of reading raw XSD or generated structural
  bindings.
- Canonical generation supplies `CVN.xsd` and `Common.xsd` to the upstream
  normalization stage so wrapper evidence enters before semantic and domain
  generation.
- Normalization runs that omit those XSD paths preserve backward-compatible empty
  wrapper evidence and therefore cannot attach wrapper-aware fields.

## Accepted Execution Protocol

The user accepted this execution plan before implementation starts.

At every execution step, the implementer must report:

1. current task number and task name
2. current subtask number and subtask name, when a subtask is being executed
3. short initial summary of what the task or subtask will do
4. short final result for the task or subtask
5. whether the user must modify any file manually
6. next step to follow

File-modification rule:

- documentation changes may be performed when explicitly requested
- code changes should be left for the user unless the user explicitly authorizes
  the agent to edit code
- generated code under `src/generated/` must not be edited manually

## Accepted Execution Plan

### Task `1 / 23` - Register Plan In Issue Documentation

- Task summary:
  - record the accepted issue `#15` execution plan and remove stale conflict
    markers from the issue document
- Files involved:
  - `docs/roadmap/issues/issue-15-domain-model-generator.md`
- Subtask `1.1 / 23`:
  - remove `<<<<<<<`, `=======`, and `>>>>>>>` markers and duplicated generator
    responsibility text
- Subtask `1.2 / 23`:
  - preserve the issue `#14` semantic-policy handoff as the generator input
    contract
- Subtask `1.3 / 23`:
  - insert the accepted execution protocol and task list
- User manual modifications needed:
  - none expected for this documentation update
- Next step:
  - verify the baseline before code work

### Task `2 / 23` - Verify Baseline Before Generator Work

- Task summary:
  - prove issue `#14`, hotfix `#7`, normalization, and auxiliary-reference
    behavior remain stable before adding generator code
- Commands:
  - `uv run pytest -n auto tests`
- Subtask `2.1 / 23`:
  - run the full repository test suite with the fast contracted command
- Subtask `2.2 / 23`:
  - confirm semantic-policy, normalization, auxiliary-reference, and existing
    regression coverage pass through the full-suite run
- Subtask `2.3 / 23`:
  - document exact failures if any command fails
- User manual modifications needed:
  - none unless verification exposes required fixes
- Next step:
  - fix the generator output architecture

### Task `3 / 23` - Define Generator Output Architecture

- Task summary:
  - decide stable file boundaries for hand-maintained generator code, shared
    domain components, and generated domain artifacts
- Files expected to change when authorized:
  - `src/cvn_codegen/domain_model_generator.py`
  - `src/cvn_codegen/domain_model_types.py` if separate typed records are needed
  - `src/models/cvn/components.py`
  - generated domain output under `src/models/cvn/generated/`
- Subtask `3.1 / 23`:
  - keep hand-maintained generator logic in `src/cvn_codegen/`
- Subtask `3.2 / 23`:
  - keep reusable hand-maintained domain components in `src/models/cvn/`
- Subtask `3.3 / 23`:
  - keep generated domain model output under `src/models/cvn/generated/`
- Subtask `3.4 / 23`:
  - confirm `src/generated/` remains untouched
- User manual modifications needed:
  - code changes should be made by the user unless explicit code-edit approval is
    given
- Next step:
  - add required runtime dependency if needed

### Task `4 / 23` - Add Runtime Dependency

- Task summary:
  - make Pydantic an explicit project runtime dependency for generated domain
    model imports
- Files expected to change when authorized:
  - `pyproject.toml`
- Subtask `4.1 / 23`:
  - add `pydantic` to `[project].dependencies`
- Subtask `4.2 / 23`:
  - keep `xsdata-pydantic` in the `codegen` dependency group
- Subtask `4.3 / 23`:
  - run dependency sync if required by the local workflow
- User manual modifications needed:
  - code/config change should be made by the user unless explicit edit approval
    is given
- Next step:
  - design the generator intermediate representation

### Task `5 / 23` - Design Generator Intermediate Representation

- Task summary:
  - define typed generator records that translate normalized metadata and
    semantic policy into deterministic Python emission units
- Files expected to change when authorized:
  - `src/cvn_codegen/domain_model_types.py`
  - `src/cvn_codegen/domain_model_generator.py`
- Subtask `5.1 / 23`:
  - create `DomainGenerationUnit`
- Subtask `5.2 / 23`:
  - create `DomainFieldSpec`
- Subtask `5.3 / 23`:
  - create `DomainTypeSpec`
- Subtask `5.4 / 23`:
  - create `DomainEnumSpec`
- Subtask `5.5 / 23`:
  - create `DomainGenerationResult`
- Subtask `5.6 / 23`:
  - ensure the IR consumes `NormalizedCodeEntry` and `SemanticFieldPolicy`, not
    raw XML or raw XSD
- User manual modifications needed:
  - code changes should be made by the user unless explicit code-edit approval is
    given
- Next step:
  - build a semantic-policy index for generation

### Task `6 / 23` - Build Semantic Policy Index

- Task summary:
  - produce deterministic policy decisions for normalized entries before grouping
    them into output models
- Files expected to change when authorized:
  - `src/cvn_codegen/domain_model_generator.py`
- Subtask `6.1 / 23`:
  - add `build_semantic_policy_index(normalization_result, bundle)`
- Subtask `6.2 / 23`:
  - iterate `NormalizationResult.by_code` in sorted code order
- Subtask `6.3 / 23`:
  - call `build_semantic_field_policy(...)` for each normalized entry
- Subtask `6.4 / 23`:
  - preserve each `SemanticDecisionTrace`
- User manual modifications needed:
  - code changes should be made by the user unless explicit code-edit approval is
    given
- Next step:
  - group fields into domain model units

### Task `7 / 23` - Group Domain Model Units

- Task summary:
  - group normalized fields into domain generation units using tree-model context
    rather than flat code lists
- Files expected to change when authorized:
  - `src/cvn_codegen/domain_model_generator.py`
- Subtask `7.1 / 23`:
  - group entries by `TreePathEntry.tree_cvn_item_code`
- Subtask `7.2 / 23`:
  - use `tree_property_name` and `tree_indicator_name` to derive field context
- Subtask `7.3 / 23`:
  - create special groups for `Version`, `Agent`, manual-only entries, and
    tree-only entries
- Subtask `7.4 / 23`:
  - include the first scope: identification, contact information, basic personal
    data, and representative `CVNItem` blocks
- Subtask `7.5 / 23`:
  - include at least one representative block for each controlled-reference
    family classified upstream
- User manual modifications needed:
  - code changes should be made by the user unless explicit code-edit approval is
    given
- Next step:
  - resolve generated names and collisions

### Task `8 / 23` - Resolve Generated Names And Collisions

- Task summary:
  - produce stable Python names while preserving CVN traceability and Spanish
    domain labels
- Files expected to change when authorized:
  - `src/cvn_codegen/domain_model_generator.py`
- Subtask `8.1 / 23`:
  - reuse Spanish-first naming from `SemanticFieldPolicy.naming_policy`
- Subtask `8.2 / 23`:
  - produce `snake_case` field names
- Subtask `8.3 / 23`:
  - produce `PascalCase` model and enum names
- Subtask `8.4 / 23`:
  - resolve collisions by readable name, semantic context, then CVN code suffix
- Subtask `8.5 / 23`:
  - record collision handling in trace notes or diagnostics
- User manual modifications needed:
  - code changes should be made by the user unless explicit code-edit approval is
    given
- Next step:
  - map semantic base kinds to Python type expressions

### Task `9 / 23` - Map Semantic Base Kinds

- Task summary:
  - convert semantic base kinds into concrete Python type expressions without
    weakening traceability
- Files expected to change when authorized:
  - `src/cvn_codegen/domain_model_generator.py`
  - `src/models/cvn/components.py`
- Subtask `9.1 / 23`:
  - map `TEXT` to `str`
- Subtask `9.2 / 23`:
  - map `BOOLEAN` to `bool`
- Subtask `9.3 / 23`:
  - map `DECIMAL_NUMBER` to `Decimal`
- Subtask `9.4 / 23`:
  - map `DATE_LIKE` to a date-like component or traced `str` if precise
    granularity is not available
- Subtask `9.5 / 23`:
  - map `DURATION_LIKE` to a duration-like component or traced `str` if precise
    semantics are not available
- Subtask `9.6 / 23`:
  - map `UNKNOWN` to an explicit weak representation without pretending stronger
    validation
- User manual modifications needed:
  - code changes should be made by the user unless explicit code-edit approval is
    given
- Next step:
  - map strict enum candidates

### Task `10 / 23` - Map Strict Enum Candidates

- Task summary:
  - emit strict enum artifacts only when semantic policy explicitly permits them
- Files expected to change when authorized:
  - `src/cvn_codegen/domain_model_generator.py`
- Subtask `10.1 / 23`:
  - require `domain_shape_kind == STRICT_ENUM_CANDIDATE`
- Subtask `10.2 / 23`:
  - require `enum_eligibility == ELIGIBLE`
- Subtask `10.3 / 23`:
  - build enum members from `ReferenceTableEnumEvidence.normalized_codes`
- Subtask `10.4 / 23`:
  - build readable member names from preferred labels with deterministic fallback
    to `CODE_<normalized_code>`
- Subtask `10.5 / 23`:
  - preserve label maps and CVN trace metadata
- User manual modifications needed:
  - code changes should be made by the user unless explicit code-edit approval is
    given
- Next step:
  - map non-enum controlled references

### Task `11 / 23` - Map Non-Enum Controlled References

- Task summary:
  - emit explicit controlled-reference component shapes for every semantic family
    that must not become a strict enum
- Files expected to change when authorized:
  - `src/cvn_codegen/domain_model_generator.py`
  - `src/models/cvn/components.py`
- Subtask `11.1 / 23`:
  - map `OPEN_CODED_VALUE` to `OpenCodedValue`
- Subtask `11.2 / 23`:
  - map `MEASURE_OR_SCALE_VALUE` to `MeasureOrScaleValue`
- Subtask `11.3 / 23`:
  - map `IDENTIFIER_REFERENCE` to `IdentifierReference`
- Subtask `11.4 / 23`:
  - map `SCOPE_REFERENCE` to `ScopeReference`
- Subtask `11.5 / 23`:
  - map `REGISTRY_REFERENCE` to `RegistryReference`
- Subtask `11.6 / 23`:
  - map `VOCABULARY_REFERENCE` to `VocabularyReference`
- Subtask `11.7 / 23`:
  - map `HIERARCHICAL_CODE_REFERENCE` to `HierarchicalCodeReference`
- Subtask `11.8 / 23`:
  - map `SUBTYPE_BACKED_VALUE` to `SubtypeBackedValue`
- Subtask `11.9 / 23`:
  - map `UNRESOLVED_REFERENCE` to `UnresolvedReference`
- Subtask `11.10 / 23`:
  - map `UNDER_TRACED_REFERENCE` to `UnderTracedReference` only when normalized
    metadata entries reference those tables
- User manual modifications needed:
  - code changes should be made by the user unless explicit code-edit approval is
    given
- Next step:
  - close or document wrapper-policy application gap

### Task `12 / 23` - Handle Wrapper And Choice Policies

- Task summary:
  - verify whether issue `#15` can restore high-value wrapper and `xs:choice`
    semantics from available normalized metadata without violating the generator
    boundary
- Files expected to change when authorized:
  - `docs/roadmap/hotfixes/hotfix-8-wrapper-type-traceability-in-normalized-handoff.md`
  - `docs/roadmap/issues/issue-15-domain-model-generator.md`
  - `docs/pipeline/known_limitations.md` if the limitation remains
- Subtask `12.1 / 23`:
  - inspect whether `TreePathEntry.tree_value` exposes wrapper names such as
    `FlexibleDatesType`, `OfficialIdType`, `EntityTypeType`, and `EntityNameType`
    for real normalized entries
- Subtask `12.2 / 23`:
  - if wrapper evidence is insufficient, create a corrective hotfix record for
    wrapper type traceability in the normalized handoff
- Subtask `12.3 / 23`:
  - document that automatic wrapper-aware field attachment remains out of scope
    for issue `#15` until the hotfix supplies typed evidence
- Subtask `12.4 / 23`:
  - do not rederive semantic wrapper decisions outside the issue `#14` policy
    contract
- User manual modifications needed:
  - code and possible documentation changes should be made by the user unless
    explicit edit approval is given
- Next step:
  - create reusable domain components

### Task `13 / 23` - Create Reusable Domain Components

- Task summary:
  - add shared domain model building blocks only where they preserve semantic
    distinctions
- Files expected to change when authorized:
  - `src/models/cvn/components.py`
  - `src/models/cvn/__init__.py` if exports are needed
- Subtask `13.1 / 23`:
  - add `BaseCvnDomainModel`
- Subtask `13.2 / 23`:
  - add `CvnTrace`
- Subtask `13.3 / 23`:
  - add controlled-reference components for open coded, registry, vocabulary,
    hierarchical, subtype-backed, unresolved, and under-traced values
- Subtask `13.4 / 23`:
  - avoid adding wrapper-specific components for automatic field attachment until
    hotfix `#8` supplies typed wrapper evidence
- Subtask `13.5 / 23`:
  - avoid components that flatten distinct semantic classes into generic `str`
- User manual modifications needed:
  - code changes should be made by the user unless explicit code-edit approval is
    given
- Next step:
  - implement deterministic Python emission

### Task `14 / 23` - Implement Python Emitter

- Task summary:
  - render deterministic Python source files from domain generation specs
- Files expected to change when authorized:
  - `src/cvn_codegen/domain_model_generator.py`
- Subtask `14.1 / 23`:
  - add generated-file header warning that files are generated and should not be
    edited manually
- Subtask `14.2 / 23`:
  - emit stable imports
- Subtask `14.3 / 23`:
  - emit Pydantic model classes using `BaseModel`, `ConfigDict`, and `Field`
- Subtask `14.4 / 23`:
  - emit enum classes for eligible strict enums
- Subtask `14.5 / 23`:
  - emit trace metadata through `json_schema_extra` or equivalent explicit field
    metadata
- Subtask `14.6 / 23`:
  - emit one file per chosen model group plus generated package `__init__.py`
- User manual modifications needed:
  - code changes should be made by the user unless explicit code-edit approval is
    given
- Next step:
  - implement safe generated-output writer

### Task `15 / 23` - Implement Safe Generated-Output Writer

- Task summary:
  - write generated domain output reproducibly without touching structural
    bindings
- Files expected to change when authorized:
  - `src/cvn_codegen/domain_model_generator.py`
  - files under `src/models/cvn/generated/`
- Subtask `15.1 / 23`:
  - validate that the output path is under `src/models/cvn/generated/`
- Subtask `15.2 / 23`:
  - clean only the domain generated-output directory before regeneration
- Subtask `15.3 / 23`:
  - never delete or edit `src/generated/`
- Subtask `15.4 / 23`:
  - write files in sorted deterministic order
- User manual modifications needed:
  - code changes should be made by the user unless explicit code-edit approval is
    given
- Next step:
  - add the generator runner entry point

### Task `16 / 23` - Add Generator Runner Entry Point

- Task summary:
  - expose a repeatable entry point for generating domain models from canonical
    source paths
- Files expected to change when authorized:
  - `src/cvn_codegen/domain_model_generator.py`
- Subtask `16.1 / 23`:
  - add public `generate_domain_models(...)`
- Subtask `16.2 / 23`:
  - use `build_normalization_result(...)` with canonical auxiliary inputs
- Subtask `16.3 / 23`:
  - build or accept `SemanticPolicyBundle`
- Subtask `16.4 / 23`:
  - optionally support `python -m cvn_codegen.domain_model_generator`
- User manual modifications needed:
  - code changes should be made by the user unless explicit code-edit approval is
    given
- Next step:
  - add unit tests for generation IR

### Task `17 / 23` - Add IR Unit Tests

- Task summary:
  - validate grouping, field specs, name handling, and trace preservation before
    testing generated Python files
- Files expected to change when authorized:
  - `tests/test_domain_model_generator_unit.py`
- Subtask `17.1 / 23`:
  - test grouping by `tree_cvn_item_code`
- Subtask `17.2 / 23`:
  - test scalar field spec construction
- Subtask `17.3 / 23`:
  - test controlled-reference field spec construction
- Subtask `17.4 / 23`:
  - test naming collision resolution
- Subtask `17.5 / 23`:
  - test trace metadata preservation
- User manual modifications needed:
  - test changes should be made by the user unless explicit code-edit approval is
    given
- Next step:
  - add domain shape mapping tests

### Task `18 / 23` - Add Domain Shape Mapping Tests

- Task summary:
  - prove each semantic policy output maps to the expected concrete domain shape
- Files expected to change when authorized:
  - `tests/test_domain_model_generator_unit.py`
- Subtask `18.1 / 23`:
  - test `CVN_SEX_A` generates a strict enum spec
- Subtask `18.2 / 23`:
  - test `CVN_ENTITY_TYPE` does not generate a strict enum
- Subtask `18.3 / 23`:
  - test `ENTITY@Entity.xsd` maps to `RegistryReference`
- Subtask `18.4 / 23`:
  - test `THESAURUS@thesaurus.xsd` maps to `VocabularyReference`
- Subtask `18.5 / 23`:
  - test `UNESCO_CODES` maps to `HierarchicalCodeReference`
- Subtask `18.6 / 23`:
  - test `CVN_KNOW_A` maps to `SubtypeBackedValue`
- Subtask `18.7 / 23`:
  - test `CVN_AGENCY_C` maps to `UnresolvedReference`
- User manual modifications needed:
  - test changes should be made by the user unless explicit code-edit approval is
    given
- Next step:
  - add emitter and import tests

### Task `19 / 23` - Add Emitter And Import Tests

- Task summary:
  - prove generated Python source can be imported and carries trace metadata
- Files expected to change when authorized:
  - `tests/test_domain_model_generator_unit.py`
- Subtask `19.1 / 23`:
  - generate files in a temporary output directory
- Subtask `19.2 / 23`:
  - import generated modules from the temporary directory
- Subtask `19.3 / 23`:
  - instantiate a representative generated model
- Subtask `19.4 / 23`:
  - assert trace metadata includes `code`, `xml_paths`, `domain_shape_kind`, and
    `enum_eligibility`
- User manual modifications needed:
  - test changes should be made by the user unless explicit code-edit approval is
    given
- Next step:
  - add determinism tests

### Task `20 / 23` - Add Determinism Tests

- Task summary:
  - prove repeated generation from identical inputs produces identical files
- Files expected to change when authorized:
  - `tests/test_domain_model_generator_unit.py`
- Subtask `20.1 / 23`:
  - run generation twice into separate temporary directories
- Subtask `20.2 / 23`:
  - compare generated file paths
- Subtask `20.3 / 23`:
  - compare generated file bytes
- User manual modifications needed:
  - test changes should be made by the user unless explicit code-edit approval is
    given
- Next step:
  - generate the first real domain output

### Task `21 / 23` - Generate First Real Domain Output

- Task summary:
  - run the generator over the canonical source package and commit the first
    generated domain artifacts to `src/models/cvn/generated/`
- Files expected to change when authorized:
  - files under `src/models/cvn/generated/`
- Subtask `21.1 / 23`:
  - run the generator using canonical XML paths under
    `docs/CvnXML_v1.4.3_2.1_17012025/XML/`
- Subtask `21.2 / 23`:
  - inspect generated output for representative scalar, enum, and non-enum
    controlled-reference cases
- Subtask `21.3 / 23`:
  - verify generated imports
- Subtask `21.4 / 23`:
  - do not manually edit generated output
- User manual modifications needed:
  - generated output may be created by the generator only after code-edit
    authorization; manual edits to generated files are not allowed
- Next step:
  - update persistent documentation for issue closure

### Task `22 / 23` - Update Closure Documentation

- Task summary:
  - record implementation, verification, limitations, and downstream impact after
    generator work finishes
- Files involved:
  - `docs/roadmap/issues/issue-15-domain-model-generator.md`
  - `docs/context/current_status.md`
  - `docs/roadmap/cvn_generation_roadmap.md`
  - `docs/pipeline/known_limitations.md` if a new limitation appears
  - `PROJECT_GUIDE.md` only if human-facing orientation changes
- Subtask `22.1 / 23`:
  - record implementation performed
- Subtask `22.2 / 23`:
  - record verification commands and exact results
- Subtask `22.3 / 23`:
  - record findings and limitations
- Subtask `22.4 / 23`:
  - update issue status when implementation is verified
- Subtask `22.5 / 23`:
  - update roadmap and current status if issue state changes
- User manual modifications needed:
  - none expected for documentation updates when explicitly requested
- Next step:
  - run final verification

### Task `23 / 23` - Run Final Verification

- Task summary:
  - prove issue `#15` implementation and existing pipeline behavior are stable
- Commands:
  - `uv run pytest -n auto tests`
- Subtask `23.1 / 23`:
  - run the full repository test suite with the fast contracted command
- Subtask `23.2 / 23`:
  - confirm semantic-policy and domain-model generator coverage pass through the
    full-suite run
- Subtask `23.3 / 23`:
  - avoid documenting slower single-file test commands unless debugging a failure
- Subtask `23.4 / 23`:
  - record exact command results in issue documentation
- User manual modifications needed:
  - none unless verification failures expose required fixes
- Next step:
  - start issue `#16` only after issue `#15` is implemented and verified

## Adjustments Made During Implementation

- Issue `#15` implementation consumed `NormalizationResult` and
  `SemanticPolicyBundle` directly without re-reading raw XSD files or generated
  structural bindings for semantic rediscovery.
- Pre-implementation planning is now aligned with the agreed semantic policy
  contract from issue `#14`.
- The generator scope is clarified so semantic decisions come from
  `SemanticPolicyBundle`, not from raw XML, raw XSD, or regenerated
  auxiliary-source classification.
- The accepted execution protocol and detailed 23-task implementation plan have
  been recorded before generator code changes begin.
- Wrapper auto-attachment was evaluated during Task `12 / 23`; the initial issue
  `#15` implementation correctly avoided raw structural rediscovery and recorded
  hotfix `#8` as the required handoff fix.
- Hotfix `#8` is now implemented and supplies `StructuralTypeEvidence` through
  the normalized and semantic handoff.
- Domain generation execution decisions have been recorded in this document,
  including output architecture, test cadence, IR records, grouping, naming,
  base type mapping, enum handling, non-enum controlled-reference components,
  trace contract, and wrapper handoff boundaries.

## Implementation Performed

- The domain model generator is implemented in
  `src/cvn_codegen/domain_model_generator.py`.
- The generator intermediate representation is implemented in
  `src/cvn_codegen/domain_model_types.py`.
- Shared hand-maintained domain components are implemented in
  `src/models/cvn/components.py`, including `CvnTrace`,
  `BaseCvnDomainModel`, `BaseControlledReferenceValue`, and the non-enum
  controlled-reference value objects.
- The generator now performs deterministic policy indexing, grouping, naming,
  collision handling, semantic type mapping, enum emission, non-enum
  controlled-reference mapping, rendering, safe output writing, and canonical
  runner orchestration.
- Final generated domain output has been emitted under
  `src/models/cvn/generated/`.
- The canonical generation run produced `105` generated Python files.
- Generated package exports and module imports were verified for
  `models.cvn.generated`, `models.cvn.generated.enums`, and
  `models.cvn.generated.manual_only`.
- The implementation preserves CVN traceability through `cvn_trace` inheritance
  on generated domain models.
- Wrapper-aware automatic field attachment now consumes hotfix `#8` structural
  type evidence and shared wrapper value components.

## Verification

- Full repository verification passed with the contracted command:
  `uv run pytest -n auto tests`
- Observed final result:
  `215 passed in 208.54s (0:03:28)`
- Additional targeted verification performed during implementation included:
  - `uv run pytest -n auto tests/test_semantic_policy_unit.py tests/test_domain_model_generator_unit.py -v`
  - observed result: `123 passed in 213.66s (0:03:33)`
- Canonical generation entry point verification passed with:
  `uv run python -m cvn_codegen.domain_model_generator`
- Canonical generation emitted `105` files and subsequent sanity checks reported:
  - `compiled_files = 105`
  - `compile_errors = 0`
  - `has_cvn_trace = True`
  - `all_count = 116`
  - `all_unique_count = 116`
  - `duplicate_exports = 0`
  - `files_with_non_ascii = 0`

## Findings

- The issue `#14` to issue `#15` handoff is sufficient for deterministic domain
  emission of scalar, enum, and non-enum controlled-reference shapes.
- Final Python artifact shapes can be decided inside the generator without
  redefining upstream semantic classification.
- Wrapper-aware field attachment now uses the explicit upstream handoff from
  hotfix `#8`; issue `#15` still must not scan raw XSD files or generated
  structural bindings inside generator logic.
- Generated class-name collisions can occur across CVN item groups and need
  deterministic global resolution rather than per-file local cleanup.
- Generated-output cleanup must account for Python cache directories such as
  `__pycache__` to keep regeneration reproducible.

## Known Limitations

- Wrapper-aware field attachment requires normalization output enriched with
  `CVN.xsd` and `Common.xsd`; canonical generation provides those inputs.
- `DATE_LIKE` and `DURATION_LIKE` currently emit traced `str` values instead of
  stronger domain-specific wrapper components.
- Unknown semantic base kinds still fall back to `object` instead of a stronger
  validated domain type.

## Impact On Future Issues

- Issue `#16` must test generator behavior against `SemanticPolicyBundle`
  outputs rather than raw source classifications.
- Issue `#16` should add regression coverage for canonical generated output,
  importability, determinism, and the hotfix `#8` wrapper handoff.
- Issue `#17` must document `SemanticPolicyBundle` as the semantic source of
  truth for domain generation and the canonical command
  `uv run python -m cvn_codegen.domain_model_generator`.
- Hotfix `#8` is now the implemented corrective path for wrapper-aware field
  attachment without raw structural rediscovery.

## Status

- Status: completed
