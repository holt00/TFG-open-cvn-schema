# Issue 14 - Define Semantic Mapping Rules And Override Policy

## Summary

Issue `#14` defines the deterministic semantic policy that translates enriched
normalized CVN metadata into domain-oriented generation decisions for issue
`#15`.

The issue does not emit final domain models. Final domain model generation
remains deferred to issue `#15`.

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

Issue `#14` starts from the validated enriched normalization output implemented
in issue `#13` after hotfix `#5`, with auxiliary structural visibility already
in place from hotfix `#4`.

The corrected semantic-policy input includes at minimum:

- `code`
- `manual.manual_name`
- `manual.manual_short_name`
- `manual.manual_type`
- `manual.manual_multiplicity`
- `manual.manual_obligatory`
- `manual.manual_reference_table`
- `tree_paths[].xml_path`
- `reference_resolution.status`
- `reference_resolution.source_family`
- `reference_resolution.source_artifact`
- `reference_resolution.resolved_name`
- `reference_resolution.serialization_pattern`
- `reference_resolution.semantic_kind`
- `reference_resolution.trace`

Issue `#14` consumes that typed metadata. It must not rebuild source-family,
side-package, subtype-backed, hierarchical-reference, unresolved-reference, or
under-traced-table detection from prose documents or ad hoc table-name
inspection.

## Accepted Execution Protocol

The user accepted this execution plan before implementation starts.

At every execution step, the implementer must report:

- current task number and task name
- current subtask number and subtask name, when a subtask is being executed
- short initial summary of what the task or subtask will do
- short final result for the task or subtask
- whether the user must modify any file manually
- next step to follow

File-modification rule:

- documentation changes may be performed when explicitly requested
- code changes should be left for the user unless the user explicitly authorizes
  the agent to edit code
- generated code under `src/generated/` must not be edited manually

## Accepted Execution Plan

### Task `1 / 15` - Clean And Stabilize Issue Documentation

- Task summary:
  - remove merge-conflict markers, duplicated sections, and stale field names so
    issue `#14` has one authoritative plan
- Files involved:
  - `docs/roadmap/issues/issue-14-semantic-mapping-rules.md`
  - `docs/context/current_status.md` if conflict markers remain there
  - `docs/roadmap/cvn_generation_roadmap.md` if conflict markers remain there
- Subtask `1.1 / 15`:
  - resolve `<<<<<<<`, `=======`, and `>>>>>>>` markers
- Subtask `1.2 / 15`:
  - remove duplicated plan, implementation, verification, findings, and impact
    sections
- Subtask `1.3 / 15`:
  - align field names with the implemented normalization contract:
    `reference_resolution.source_artifact` and
    `reference_resolution.semantic_kind`
- Subtask `1.4 / 15`:
  - keep issue status as planned until implementation and verification finish
- User manual modifications needed:
  - none expected for documentation cleanup unless the user wants wording changes
- Next step:
  - verify the upstream normalization contract

### Task `2 / 15` - Verify Upstream Normalization Contract

- Task summary:
  - confirm the exact Python structures issue `#14` may consume from issue `#13`
- Files to inspect:
  - `src/cvn_codegen/normalization_types.py`
  - `src/cvn_codegen/normalization.py`
  - `src/cvn_codegen/auxiliary_sources/reference_resolution.py`
  - `tests/test_normalization_unit.py`
  - `tests/test_auxiliary_reference_resolution_unit.py`
- Subtask `2.1 / 15`:
  - confirm `ManualCodeEntry`, `TreePathEntry`, `NormalizedCodeEntry`, and
    `NormalizationResult`
- Subtask `2.2 / 15`:
  - confirm `ReferenceResolution`, `ReferenceResolutionTrace`,
    `ReferenceResolutionStatus`, `ReferenceSourceFamily`, `SerializationPattern`,
    and `SemanticReferenceKind`
- Subtask `2.3 / 15`:
  - confirm `build_normalization_result(...)` as the preferred consumer entry
    point
- Subtask `2.4 / 15`:
  - record any mismatch between planned semantic inputs and implemented contract
- User manual modifications needed:
  - none unless code contract differs from documented expectations
- Next step:
  - define the semantic policy contract

### Task `3 / 15` - Define Semantic Policy Contract

- Task summary:
  - design the typed structures that issue `#15` will consume mechanically
- Expected code location:
  - `src/cvn_codegen/semantic_policy.py`
- Subtask `3.1 / 15`:
  - define policy enums:
    `SemanticBaseKind`, `WrapperPolicyKind`, `PresenceKind`,
    `CardinalityKind`, `StructuralLimitationFlag`, `DomainShapeKind`,
    `PolicyConfidence`, and `EnumEligibility`
- Subtask `3.2 / 15`:
  - define policy records:
    `PolicyMetadata`, `SemanticDecisionTrace`, `BaseTypePolicy`,
    `ReferenceKindPolicy`, `NamingPolicy`, `MultiplicityPolicy`,
    `ChoiceWrapperPolicy`, `OverrideRule`, `ValidationCaseDefinition`,
    `SemanticFieldPolicy`, and `SemanticPolicyBundle`
- Subtask `3.3 / 15`:
  - expose deterministic lookup maps by CVN `code`, `xml_path`,
    `SemanticReferenceKind`, `SerializationPattern`, `manual_type`, and wrapper
    family
- User manual modifications needed:
  - code file must be created by the user unless explicit code-edit approval is
    given
- Next step:
  - build default semantic policy bundle

### Task `4 / 15` - Build Default Semantic Policy Bundle

- Task summary:
  - implement default reusable semantic policy values independent from concrete
    normalized entries
- Expected code location:
  - `src/cvn_codegen/semantic_policy.py`
- Subtask `4.1 / 15`:
  - create `build_default_semantic_policy_bundle()`
- Subtask `4.2 / 15`:
  - include base policies by `manual_type`
- Subtask `4.3 / 15`:
  - include reference-kind policies by `SemanticReferenceKind`
- Subtask `4.4 / 15`:
  - include serialization refinements by `SerializationPattern`
- Subtask `4.5 / 15`:
  - include wrapper policies for known high-value `xs:choice` wrappers
- User manual modifications needed:
  - code file must be edited by the user unless explicit code-edit approval is
    given
- Next step:
  - implement semantic field policy resolution

### Task `5 / 15` - Resolve Semantic Policy For One Normalized Entry

- Task summary:
  - define how one `NormalizedCodeEntry` becomes one `SemanticFieldPolicy`
- Expected code location:
  - `src/cvn_codegen/semantic_policy.py`
- Subtask `5.1 / 15`:
  - create `build_semantic_field_policy(entry, bundle)`
- Subtask `5.2 / 15`:
  - calculate `base_kind`
- Subtask `5.3 / 15`:
  - calculate `domain_shape_kind` and `fallback_shape_kind`
- Subtask `5.4 / 15`:
  - calculate `presence_kind` and `cardinality_kind`
- Subtask `5.5 / 15`:
  - calculate `enum_eligibility` and `policy_confidence`
- Subtask `5.6 / 15`:
  - attach `SemanticDecisionTrace` preserving CVN code, XML path, reference
    resolution, and rule sources
- User manual modifications needed:
  - code file must be edited by the user unless explicit code-edit approval is
    given
- Next step:
  - implement override precedence

### Task `6 / 15` - Implement Override Precedence

- Task summary:
  - make exceptions explicit, reviewable, and deterministic
- Expected code location:
  - `src/cvn_codegen/semantic_policy.py`
- Subtask `6.1 / 15`:
  - support override target `code + xml_path`
- Subtask `6.2 / 15`:
  - support override target `code`
- Subtask `6.3 / 15`:
  - support override target `xml_path`
- Subtask `6.4 / 15`:
  - support override target `reference_resolution.semantic_kind`
- Subtask `6.5 / 15`:
  - support override target `reference_resolution.serialization_pattern`
- Subtask `6.6 / 15`:
  - apply precedence order:
    `code + xml_path`, `code`, `xml_path`, `semantic_kind`,
    `serialization_pattern`, `manual_type`, wrapper, presence/cardinality,
    defaults
- Subtask `6.7 / 15`:
  - mark same-priority conflicts as `PolicyConfidence.REQUIRES_REVIEW`
- User manual modifications needed:
  - code file must be edited by the user unless explicit code-edit approval is
    given
- Next step:
  - implement naming policy

### Task `7 / 15` - Implement Naming Policy

- Task summary:
  - generate future domain-facing names while preserving source traceability
- Expected code location:
  - `src/cvn_codegen/semantic_policy.py`
- Subtask `7.1 / 15`:
  - use Spanish `manual_name` as the default label source
- Subtask `7.2 / 15`:
  - use `manual_short_name` only when clearer and non-ambiguous
- Subtask `7.3 / 15`:
  - normalize identifiers to ASCII
- Subtask `7.4 / 15`:
  - produce `snake_case` fields and modules
- Subtask `7.5 / 15`:
  - produce `PascalCase` class names
- Subtask `7.6 / 15`:
  - preserve acronyms such as `CVN`, `UNESCO`, `ORCID`, `DOI`, `ISBN`, `ISSN`,
    and `H`
- Subtask `7.7 / 15`:
  - resolve collisions by readable Spanish name, then semantic context, then CVN
    code suffix
- User manual modifications needed:
  - code file must be edited by the user unless explicit code-edit approval is
    given
- Next step:
  - implement base type policy

### Task `8 / 15` - Implement Base Type Policy

- Task summary:
  - map manual types to semantic base kinds without choosing final Python output
    types
- Expected code location:
  - `src/cvn_codegen/semantic_policy.py`
- Subtask `8.1 / 15`:
  - map `Alphanumeric` without resolved controlled reference to `TEXT`
- Subtask `8.2 / 15`:
  - map `Alphanumeric` with `reference_resolution.semantic_kind` to
    `CONTROLLED_REFERENCE`
- Subtask `8.3 / 15`:
  - map `Date` to `DATE_LIKE`
- Subtask `8.4 / 15`:
  - map `Double` to `DECIMAL_NUMBER`
- Subtask `8.5 / 15`:
  - map `Boolean` to `BOOLEAN`
- Subtask `8.6 / 15`:
  - map `Duration` to `DURATION_LIKE`
- Subtask `8.7 / 15`:
  - map missing or unknown types to `UNKNOWN`
- User manual modifications needed:
  - code file must be edited by the user unless explicit code-edit approval is
    given
- Next step:
  - implement reference-kind policy

### Task `9 / 15` - Implement Reference-Kind Policy

- Task summary:
  - map normalized `SemanticReferenceKind` values to domain shape decisions
- Expected code location:
  - `src/cvn_codegen/semantic_policy.py`
- Subtask `9.1 / 15`:
  - map `COMPACT_ENUM_LIKE_TABLE` to `STRICT_ENUM_CANDIDATE`, fallback
    `OPEN_CODED_VALUE`
- Subtask `9.2 / 15`:
  - map `COMPACT_SCALE_OR_MEASURE` to `MEASURE_OR_SCALE_VALUE`
- Subtask `9.3 / 15`:
  - map `IDENTIFIER_TYPE_TABLE` to `IDENTIFIER_REFERENCE`
- Subtask `9.4 / 15`:
  - map `SCOPE_TABLE` to `SCOPE_REFERENCE`
- Subtask `9.5 / 15`:
  - map `SUBTYPE_BACKED_CONTROLLED_FAMILY` to `SUBTYPE_BACKED_VALUE`
- Subtask `9.6 / 15`:
  - map `HIERARCHICAL_THEMATIC_CLASSIFICATION` to
    `HIERARCHICAL_CODE_REFERENCE`
- Subtask `9.7 / 15`:
  - map `SIDE_PACKAGE_REGISTRY` to `REGISTRY_REFERENCE`
- Subtask `9.8 / 15`:
  - map `SIDE_PACKAGE_THESAURUS_OR_VOCABULARY` to `VOCABULARY_REFERENCE`
- Subtask `9.9 / 15`:
  - map `UNRESOLVED_MANUAL_ONLY_REFERENCE` to `UNRESOLVED_REFERENCE`
- Subtask `9.10 / 15`:
  - map `UNDER_TRACED_REFERENCE_TABLE` to `UNDER_TRACED_REFERENCE`
- User manual modifications needed:
  - code file must be edited by the user unless explicit code-edit approval is
    given
- Next step:
  - implement enum eligibility

### Task `10 / 15` - Implement Enum Eligibility Policy

- Task summary:
  - decide when controlled references may become strict enum candidates
- Expected code location:
  - `src/cvn_codegen/semantic_policy.py`
- Subtask `10.1 / 15`:
  - mark direct compact `REFERENCE_TABLE` cases as eligible only when no risk
    flags exist
- Subtask `10.2 / 15`:
  - reject hierarchies, delegates, subtype-backed tables, side packages,
    unresolved references, and under-traced references
- Subtask `10.3 / 15`:
  - mark `CVN_SEX_A` as expected strict-enum candidate
- Subtask `10.4 / 15`:
  - mark `CVN_ENTITY_TYPE` as open or review-required rather than blind strict
    enum
- User manual modifications needed:
  - code file must be edited by the user unless explicit code-edit approval is
    given
- Next step:
  - implement wrapper policy

### Task `11 / 15` - Implement Wrapper And Choice Policy

- Task summary:
  - preserve high-value `xs:choice` semantics lost by structural bindings
- Expected code location:
  - `src/cvn_codegen/semantic_policy.py`
- Subtask `11.1 / 15`:
  - classify `FlexibleDatesType` as `CHOICE_OBJECT_CANDIDATE`
- Subtask `11.2 / 15`:
  - classify `OfficialIdType` as `CHOICE_OBJECT_CANDIDATE`
- Subtask `11.3 / 15`:
  - classify `EntityTypeType` as `CHOICE_OBJECT_CANDIDATE`
- Subtask `11.4 / 15`:
  - classify `EntityNameType` as `CHOICE_OBJECT_CANDIDATE`
- Subtask `11.5 / 15`:
  - attach `CHOICE_NOT_ENFORCED`, `LIST_MIN_OCCURS_WEAK`,
    `OBJECT_TYPED_ATTRIBUTE`, and `WRAPPER_ERGONOMICS` flags when applicable
- Subtask `11.6 / 15`:
  - collapse only wrappers that add no domain meaning and no required structural
    traceability
- User manual modifications needed:
  - code file must be edited by the user unless explicit code-edit approval is
    given
- Next step:
  - build representative validation inventory

### Task `12 / 15` - Build Representative Validation Inventory

- Task summary:
  - define real cases that prove the policy covers all semantic categories
- Files involved:
  - `src/cvn_codegen/semantic_policy.py`
  - `docs/roadmap/issues/issue-14-semantic-mapping-rules.md`
- Subtask `12.1 / 15`:
  - include simple scalar case `000.010.000.020`
- Subtask `12.2 / 15`:
  - include compact enum-like case `CVN_SEX_A` / `000.010.000.030`
- Subtask `12.3 / 15`:
  - include compact open or review case `CVN_ENTITY_TYPE`
- Subtask `12.4 / 15`:
  - include subtype-backed case `CVN_KNOW_A`
- Subtask `12.5 / 15`:
  - include side-package registry case `ENTITY@Entity.xsd`
- Subtask `12.6 / 15`:
  - include side-package vocabulary case `THESAURUS@thesaurus.xsd`
- Subtask `12.7 / 15`:
  - include hierarchical thematic case `UNESCO_CODES`
- Subtask `12.8 / 15`:
  - include unresolved case `CVN_AGENCY_C`
- Subtask `12.9 / 15`:
  - include under-traced cases `CVN_INTERVENTION_A` and `CVN_PRUEBA`
- Subtask `12.10 / 15`:
  - include wrapper cases `FlexibleDatesType`, `OfficialIdType`,
    `EntityTypeType`, and `EntityNameType`
- User manual modifications needed:
  - code inventory must be edited by the user unless explicit code-edit approval
    is given
- Next step:
  - add tests

### Task `13 / 15` - Add Semantic Policy Tests

- Task summary:
  - make issue `#14` behavior executable and protect handoff to issue `#15`
- Expected test location:
  - `tests/test_semantic_policy_unit.py`
- Subtask `13.1 / 15`:
  - test policy enums and default bundle construction
- Subtask `13.2 / 15`:
  - test base type mapping
- Subtask `13.3 / 15`:
  - test reference-kind mapping
- Subtask `13.4 / 15`:
  - test enum eligibility
- Subtask `13.5 / 15`:
  - test presence and cardinality mapping
- Subtask `13.6 / 15`:
  - test naming normalization and collision fallback
- Subtask `13.7 / 15`:
  - test override precedence and same-priority conflict behavior
- Subtask `13.8 / 15`:
  - test wrapper policies
- Subtask `13.9 / 15`:
  - test representative real cases through `build_normalization_result(...)`
    with auxiliary paths
- User manual modifications needed:
  - test file must be created by the user unless explicit code-edit approval is
    given
- Next step:
  - run verification commands

### Task `14 / 15` - Verify Implementation

- Task summary:
  - prove semantic policy works and existing normalization behavior did not
    regress
- Commands:
  - `uv run pytest tests/test_semantic_policy_unit.py -v`
  - `uv run pytest tests/test_manual_metadata_unit.py tests/test_tree_metadata_unit.py tests/test_normalization_report_unit.py tests/test_normalization_unit.py tests/test_auxiliary_source_loaders_unit.py tests/test_auxiliary_reference_resolution_unit.py -v`
  - `uv run pytest tests`
- Subtask `14.1 / 15`:
  - run semantic-policy tests
- Subtask `14.2 / 15`:
  - run normalization and auxiliary regression tests
- Subtask `14.3 / 15`:
  - run full test suite
- Subtask `14.4 / 15`:
  - document failures exactly if any command fails
- User manual modifications needed:
  - none unless tests expose code or doc changes required
- Next step:
  - update closure documentation

### Task `15 / 15` - Update Final Documentation And Handoff

- Task summary:
  - close issue `#14` with implementation details, verification, limitations, and
    issue `#15` handoff
- Files involved:
  - `docs/roadmap/issues/issue-14-semantic-mapping-rules.md`
  - `docs/context/current_status.md`
  - `docs/roadmap/cvn_generation_roadmap.md`
  - `docs/pipeline/known_limitations.md` only if a new limitation is found
- Subtask `15.1 / 15`:
  - record implementation performed
- Subtask `15.2 / 15`:
  - record verification commands and results
- Subtask `15.3 / 15`:
  - record findings and limitations
- Subtask `15.4 / 15`:
  - update issue status when implementation is verified
- Subtask `15.5 / 15`:
  - leave explicit handoff checklist for issue `#15`
- User manual modifications needed:
  - none expected for documentation closure unless the user wants wording changes
- Next step:
  - start issue `#15` only after issue `#14` is implemented and verified

## Established Semantic Policy Decisions

### Scope Boundary

Issue `#14` consumes only typed normalized metadata from issue `#13` as policy
inputs. Raw XML, raw XSD, and generated structural classes may be inspected for
human validation or override evidence, but they must not become base semantic
inputs.

If a repeated semantic decision needs raw source inspection, the missing data
belongs in issue `#13`. If the need is isolated and not generalizable, issue
`#14` may express it as an explicit override with trace evidence.

### Contract Families

The semantic policy contract should use explicit typed Python structures with
`dataclass` records and `Enum` values. The root contract should be an indexed
`SemanticPolicyBundle`.

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

### Policy Enums

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

Same-priority conflicts should produce `PolicyConfidence.REQUIRES_REVIEW`
rather than silently choosing one rule.

### Base Type Policy

Issue `#14` defines semantic base kinds, not final Python/domain output types.
Issue `#15` will map these semantic kinds to concrete generated Python
artifacts.

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
| `COMPACT_ENUM_LIKE_TABLE` | `STRICT_ENUM_CANDIDATE` | `OPEN_CODED_VALUE` | eligibility criteria required | `HIGH` or `REQUIRES_REVIEW` |
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

## Representative Inventory And Expected Results

| Case | Role | Expected policy result |
| --- | --- | --- |
| `000.010.000.020` / `Nombre` | simple scalar | `PLAIN_VALUE`, `TEXT`, enum ineligible |
| `CVN_SEX_A` / `000.010.000.030` | compact closed enum-like table | `STRICT_ENUM_CANDIDATE`, enum eligible |
| `CVN_ENTITY_TYPE` / `010.010.000.040` | compact open/review controlled table | `OPEN_CODED_VALUE`, enum review required |
| `CVN_KNOW_A` / `050.030.010.030` | subtype-backed family | `SUBTYPE_BACKED_VALUE`, enum ineligible |
| `ENTITY@Entity.xsd` / `010.010.000.020` | side-package registry | `REGISTRY_REFERENCE`, enum ineligible |
| `THESAURUS@thesaurus.xsd` / `010.010.000.260` | side-package vocabulary | `VOCABULARY_REFERENCE`, enum ineligible |
| `UNESCO_CODES` / `010.010.000.220` | hierarchical thematic classification | `HIERARCHICAL_CODE_REFERENCE`, enum ineligible |
| `CVN_AGENCY_C` / `060.010.000.030` | unresolved manual-only reference | `UNRESOLVED_REFERENCE`, review required |
| `CVN_INTERVENTION_A` | under-traced table, primary case | `UNDER_TRACED_REFERENCE`, review required |
| `CVN_PRUEBA` | under-traced table, secondary case | `UNDER_TRACED_REFERENCE`, review required |
| `FlexibleDatesType` | `xs:choice` date wrapper | `CHOICE_OBJECT_CANDIDATE` with limitation flags |
| `OfficialIdType` | `xs:choice` identifier wrapper | `CHOICE_OBJECT_CANDIDATE` with limitation flags |
| `EntityTypeType` | `xs:choice` entity type wrapper | `CHOICE_OBJECT_CANDIDATE` with limitation flags |
| `EntityNameType` | `xs:choice` entity name wrapper | `CHOICE_OBJECT_CANDIDATE` with limitation flags |

Under-traced tables may not produce generated domain fields in issue `#15`
unless future normalized entries reference them.

## Handoff Checklist For Issue `#15`

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

## Known Limitations

- `Subtype_Spa.xml` lacks a strict per-table bridge such as `CVN_KNOW_A` to
  subtype records.
- `CVN_AGENCY_C` remains unresolved from the source package alone.
- `CVN_INTERVENTION_A` and `CVN_PRUEBA` remain technically present but
  under-traced.
- Generated structural bindings do not enforce `xs:choice` mutual exclusivity.
- Generated list defaults do not reliably enforce every `minOccurs` constraint.
- Final domain model emission remains deferred to issue `#15`.

## Implementation Performed

- No semantic-policy code implementation has been performed yet.
- This document now records the accepted execution plan and reporting protocol
  for issue `#14`.

## Verification

- No code tests have been run for issue `#14` because no semantic-policy
  implementation exists yet.
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

## Impact On Future Issues

- Issue `#15` must consume `SemanticPolicyBundle` and generate concrete domain
  artifacts from semantic-policy outputs rather than redefining semantic
  classification.
- Issue `#16` must test semantic-policy behavior separately from generator
  output behavior.
- Issue `#17` must document `SemanticPolicyBundle` as the source-of-truth
  handoff between normalized metadata and domain generation.

## Status

- Status: planned with accepted execution policy
