# Hotfix 7 - Dynamic Reference Table Enum Eligibility Evaluation

## Summary

Hotfix `#7` records the corrective work required because issue `#14` currently
has enough normalized metadata to classify manual references by semantic family,
but it still does not have enough machine-readable evidence to evaluate strict
enum eligibility dynamically across all `ReferenceTables.xml` tables.

The current semantic policy work can safely say that a reference is a compact
enum-like controlled table, but it cannot yet decide, in a generic and
evidence-backed way, whether that table should be treated as:

- a strict closed enum candidate
- a review-required compact controlled set
- an open-coded value that should not be emitted as a strict enum

This gap led to an undesirable implementation temptation: temporary
table-specific hardcoding for cases such as `CVN_SEX_A` or `CVN_ENTITY_TYPE`.

That shortcut must not become the long-term policy. The repository needs a
dynamic evaluation path over all relevant `ReferenceTables.xml` tables so future
semantic and generation work can scale without accumulating ad hoc exceptions.

This hotfix defines exactly how to add that evidence path while keeping the
architectural rule that issue `#14` consumes normalized typed metadata instead
of reopening raw auxiliary-source inspection on every semantic decision.

## Motivation

The repository already contains two important partial layers:

1. issue `#13` resolves `manual_reference_table` to typed auxiliary-source
   metadata and exposes `reference_resolution`
2. issue `#14` maps `SemanticReferenceKind` and `SerializationPattern` to
   domain-shape candidates

What is still missing is a third layer between them:

- machine-readable enum-eligibility evidence extracted from
  `ReferenceTables.xml`

Without that layer, issue `#14` cannot answer these questions generically for
all compact enum-like tables:

- does table have hierarchy?
- does table use delegate-based open behavior?
- does table include obvious "other" catch-all items?
- are codes and preferred labels stable enough for enum emission?
- is table small enough to be a practical strict enum candidate?

If this hotfix is not applied:

- issue `#14` will remain conservative but semantically incomplete
- issue `#15` will either overuse `REVIEW_REQUIRED` or drift into hardcoded
  table-name logic
- future contributors will not know where strict enum eligibility is meant to be
  evaluated

## Scope Of This Hotfix

This hotfix is both a planning correction and an implementation contract.

It does not require full domain-model generation. It does require extending the
normalization-to-semantic handoff so issue `#14` can evaluate enum eligibility
dynamically and reproducibly for every relevant table materialized in
`ReferenceTables.xml`.

This hotfix includes:

- extension of normalization-grade `ReferenceTables.xml` metadata
- additive enum-evidence fields in typed normalization contracts
- deterministic dynamic enum-eligibility evaluation rules
- replacement of table-specific hardcoding with evidence-backed policy
- tests and validation cases for reviewed representative tables

This hotfix does not include:

- changes to `src/generated/`
- semantic-policy decisions for side-package registries or thesauri beyond their
  already defined ineligibility
- domain-model generation output in issue `#15`
- fuzzy or LLM-based interpretation of table meaning

## Issues Affected

- issue `#13`
- issue `#14`
- issue `#15` as downstream consumer
- issue `#16` for test coverage
- issue `#17` for workflow documentation

## Core Problem Statement

### What Exists Today

The current `ReferenceTableMetadata` extracted in
`src/cvn_codegen/auxiliary_sources/reference_tables_metadata.py` already carries:

- `table_name`
- `version`
- `ancestor_table`
- `source`
- `xml_data_type`
- `xml_property`
- `xml_indicator`
- `item_count`
- `has_hierarchy`
- `has_delegate`

That is enough for semantic-kind classification, but not enough for strict enum
eligibility.

The current `ReferenceResolution` in `src/cvn_codegen/normalization_types.py`
does not expose table-level evidence such as:

- normalized item codes
- preferred labels
- duplicate-code detection
- duplicate-label detection
- presence of obvious "other" / catch-all entries
- explicit open-world signals for enum emission

### What Must Be True After This Hotfix

After this hotfix is implemented, issue `#14` must be able to evaluate enum
eligibility for all resolved `REFERENCE_TABLE` compact enum-like tables without
hardcoding specific table names in semantic policy logic.

The only acceptable table-specific exceptions after this hotfix are:

- explicit review overrides stored as versioned `OverrideRule` data
- not hidden `if table_name == ...` branches inside semantic-policy code

## Required Changes To Issue `#13`

Issue `#13` remains the correct stage for extracting and normalizing the
evidence needed by issue `#14`.

Issue `#14` must not scan `ReferenceTables.xml` ad hoc for every semantic
decision. It should consume typed evidence already attached to normalized
entries.

### Contract Extension Required

`src/cvn_codegen/normalization_types.py` must be extended with an additive typed
record that carries enum-eligibility evidence for reference tables.

The preferred exact name is:

- `ReferenceTableEnumEvidence`

The preferred exact attachment point is:

- `ReferenceResolution.reference_table_enum_evidence`

This field must be:

- `None` for non-`ReferenceTables.xml` sources
- populated for resolved direct `REFERENCE_TABLE` and
  `SUBTYPE_BACKED_TABLE` cases

### New Type Required

Issue `#13` should add this typed structure or a field-equivalent contract with
the same information:

```python
@dataclass(frozen=True)
class ReferenceTableEnumEvidence:
    table_name: str
    item_count: int
    has_hierarchy: bool
    has_delegate: bool
    has_other_like_entry: bool
    has_duplicate_codes: bool
    has_duplicate_preferred_labels: bool
    has_blank_code: bool
    has_blank_preferred_label: bool
    normalized_codes: tuple[str, ...]
    preferred_labels: tuple[str, ...]
    normalized_preferred_labels: tuple[str, ...]
    open_world_signals: tuple[str, ...]
```

The exact field names may differ only if all of the above facts remain present
and testable.

### `ReferenceTableMetadata` Extension Required

`src/cvn_codegen/auxiliary_sources/reference_tables_metadata.py` must be
extended so `ReferenceTableMetadata` itself exposes enough raw normalized facts
to build `ReferenceTableEnumEvidence` deterministically.

At minimum, add these fields to `ReferenceTableMetadata`:

- `item_codes: tuple[str, ...]`
- `preferred_labels: tuple[str, ...]`
- `normalized_codes: tuple[str, ...]`
- `normalized_preferred_labels: tuple[str, ...]`
- `has_blank_code: bool`
- `has_blank_preferred_label: bool`
- `has_duplicate_codes: bool`
- `has_duplicate_preferred_labels: bool`
- `has_other_like_entry: bool`
- `open_world_signals: tuple[str, ...]`

### Preferred Label Extraction Rule

When building table metadata from `ReferenceTables.xml`, each item must select a
preferred label deterministically from the available multilingual `NameDetail`
values.

Use this order:

1. Spanish label if present
2. English label if Spanish is missing
3. first available label otherwise

The implementation must not leave preferred-label selection implicit.

### Normalization Rules For Evidence

When computing dynamic enum evidence, normalize codes and labels with explicit,
repository-local deterministic rules.

Minimum normalization required:

1. strip leading and trailing whitespace
2. collapse repeated internal whitespace to single spaces
3. convert labels to ASCII-compatible uppercase for signal detection
4. preserve original preferred labels separately from normalized labels
5. preserve original item codes separately from normalized codes

### Open-World Signal Detection Rules

The implementation must compute `has_other_like_entry` and
`open_world_signals` deterministically.

Use these minimum signals:

#### Label-Based Other-Like Tokens

After normalization to uppercase ASCII, treat these exact tokens as open-world
signals when used as a full label or clear standalone term:

- `OTRO`
- `OTRA`
- `OTROS`
- `OTRAS`
- `OTHER`
- `OTHERS`
- `RESTO`
- `NO CONSTA`
- `SIN ESPECIFICAR`

#### Structural Open Signals

Also record open-world signals for:

- any table with `has_delegate=True`
- any item with blank preferred label
- any item with blank code

The implementation should store the actual matched reasons in
`open_world_signals`, for example:

- `label_token:OTHERS`
- `delegate_present`
- `blank_preferred_label`

### Duplicate Detection Rules

`has_duplicate_codes` must be `True` when normalized item codes repeat.

`has_duplicate_preferred_labels` must be `True` when normalized preferred labels
repeat after empty labels are excluded.

These duplicate flags do not automatically make the table ineligible, but they
must block automatic `ELIGIBLE` and downgrade the table to review-required.

### Wiring Required In Reference Resolution

`src/cvn_codegen/auxiliary_sources/reference_resolution.py` must attach
`ReferenceTableEnumEvidence` whenever a manual reference resolves to
`ReferenceTables.xml`.

That means `resolve_manual_reference(...)` must:

1. keep current source-family and semantic-kind behavior unchanged
2. build enum evidence from `ReferenceTableMetadata`
3. attach that evidence to `ReferenceResolution`
4. preserve `None` for non-reference-table source families

## Required Changes To Issue `#14`

Issue `#14` must stop using hardcoded reference-name logic for strict enum
eligibility.

### Current Undesired State

The current semantic-policy direction risks either:

- hardcoding reviewed cases such as `CVN_SEX_A`
- or leaving every compact enum-like table as permanently
  `REVIEW_REQUIRED`

Neither is sufficient.

### Correct Enum Eligibility Evaluation Function

`src/cvn_codegen/semantic_policy.py` must add one deterministic helper with
equivalent behavior to:

```python
def evaluate_reference_table_enum_eligibility(
    evidence: ReferenceTableEnumEvidence | None,
    source_family: ReferenceSourceFamily | None,
    semantic_kind: SemanticReferenceKind | None,
    is_subtype_backed: bool,
) -> tuple[EnumEligibility, PolicyConfidence, tuple[str, ...]]:
    ...
```

The helper must return:

- final `EnumEligibility`
- final `PolicyConfidence`
- machine-readable rule reasons or blockers

### Exact Eligibility Rules Required

The function must evaluate rules in this order.

#### Immediate Ineligibility

Return `INELIGIBLE` when any of these are true:

1. `source_family` is not `REFERENCE_TABLE`
2. `semantic_kind` is not `COMPACT_ENUM_LIKE_TABLE`
3. `is_subtype_backed` is `True`
4. `evidence is None`
5. `evidence.has_hierarchy` is `True`
6. `evidence.has_delegate` is `True`

These cases are not review candidates for strict enum emission. They are not
closed compact tables.

#### Review Required

Return `REVIEW_REQUIRED` when immediate ineligibility does not apply, but any of
these are true:

1. `evidence.has_other_like_entry` is `True`
2. `evidence.has_blank_code` is `True`
3. `evidence.has_blank_preferred_label` is `True`
4. `evidence.has_duplicate_codes` is `True`
5. `evidence.has_duplicate_preferred_labels` is `True`
6. `evidence.item_count == 0`
7. `evidence.item_count > 64`

The `64` threshold must be versioned as a named repository constant, for
example:

- `MAX_STRICT_ENUM_ITEM_COUNT = 64`

This threshold is not a semantic truth of CVN. It is a repository policy limit
for practical strict-enum generation.

#### Eligible

Return `ELIGIBLE` only when all of these are true:

1. source family is direct `REFERENCE_TABLE`
2. semantic kind is `COMPACT_ENUM_LIKE_TABLE`
3. not subtype-backed
4. no hierarchy
5. no delegate
6. no other-like/open-world label
7. no blank codes
8. no blank preferred labels
9. no duplicate codes
10. no duplicate preferred labels
11. `1 <= item_count <= MAX_STRICT_ENUM_ITEM_COUNT`

### Domain Shape Interaction Required

Dynamic enum evaluation must not silently flatten semantic kinds.

Use these exact outputs:

1. if enum eligibility is `ELIGIBLE`:
   - keep `domain_shape_kind=STRICT_ENUM_CANDIDATE`
   - set `policy_confidence=HIGH`
2. if enum eligibility is `REVIEW_REQUIRED`:
   - keep `domain_shape_kind=STRICT_ENUM_CANDIDATE`
   - keep fallback `OPEN_CODED_VALUE`
   - set `policy_confidence=REQUIRES_REVIEW`
3. if enum eligibility is `INELIGIBLE` because the table is not a compact direct
   enum candidate:
   - let the reference-kind matrix already drive non-enum shapes

Important correction:

This hotfix does **not** require issue `#14` to convert every reviewed compact
table into `OPEN_CODED_VALUE` immediately. It only requires dynamic eligibility
evaluation instead of hardcoding.

That means `CVN_ENTITY_TYPE` should no longer be hardcoded in semantic policy.
It should land in `REVIEW_REQUIRED` unless machine-readable open-world evidence
forces a stronger result.

### Validation Expectation Correction Required

Issue `#14` validation cases must stop treating reviewed examples as hardcoded
special cases.

Update expectations as follows:

1. `CVN_SEX_A`
   - expected `EnumEligibility.ELIGIBLE`
   - expected confidence `HIGH`
   - result must come from dynamic evidence, not `if table_name == "CVN_SEX_A"`
2. `CVN_ENTITY_TYPE`
   - expected `EnumEligibility.REVIEW_REQUIRED`
   - expected confidence `REQUIRES_REVIEW`
   - result must come from dynamic evidence, not hardcoded table-name override

## Required Changes To Tests

### Extend Auxiliary Loader Tests

`tests/test_auxiliary_source_loaders_unit.py` must add assertions proving that
`ReferenceTableMetadata` now exposes enum-evidence fields.

Minimum new checks:

1. `CVN_SEX_A` has non-empty `item_codes`
2. `CVN_SEX_A` has non-empty `preferred_labels`
3. `CVN_SEX_A` reports `has_hierarchy is False`
4. `CVN_SEX_A` reports `has_delegate is False`

### Extend Resolution Tests

`tests/test_auxiliary_reference_resolution_unit.py` must add checks that:

1. resolved reference-table cases attach non-`None`
   `reference_table_enum_evidence`
2. side-package and unresolved cases attach `None`
3. subtype-backed cases still attach evidence but remain semantically ineligible

### Add Semantic Policy Tests

When issue `#16` or the issue `#14` test phase adds semantic-policy tests, the
minimum required dynamic enum checks are:

1. `CVN_SEX_A` becomes `ELIGIBLE` dynamically
2. `CVN_ENTITY_TYPE` becomes `INELIGIBLE` dynamically because canonical evidence
   includes `delegate_present`
3. subtype-backed `CVN_KNOW_A` remains `INELIGIBLE`
4. hierarchical `UNESCO_CODES` remains `INELIGIBLE`
5. side-package registry references remain `INELIGIBLE`
6. unresolved references remain `INELIGIBLE`

## Files Expected To Change When Applying This Hotfix

Minimum code files:

- `src/cvn_codegen/normalization_types.py`
- `src/cvn_codegen/auxiliary_sources/reference_tables_metadata.py`
- `src/cvn_codegen/auxiliary_sources/reference_resolution.py`
- `src/cvn_codegen/semantic_policy.py`
- `tests/test_auxiliary_source_loaders_unit.py`
- `tests/test_auxiliary_reference_resolution_unit.py`
- future semantic-policy tests under `tests/`

Minimum documentation files:

- `docs/roadmap/issues/issue-14-semantic-mapping-rules.md`
- `docs/context/current_status.md`
- `docs/pipeline/known_limitations.md` if a new limitation appears
- `docs/roadmap/cvn_generation_roadmap.md` if issue state changes

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

### Task `1 / 15` - Add Loader Metadata Tests

- Task summary:
  - add failing tests proving `ReferenceTableMetadata` exposes dynamic enum
    evidence derived from `ReferenceTables.xml`
- Files involved:
  - `tests/test_auxiliary_source_loaders_unit.py`
- Subtask `1.1 / 15`:
  - assert `CVN_SEX_A` has non-empty `item_codes`, non-empty
    `preferred_labels`, normalized codes `("000", "010")`, no hierarchy, no
    delegate, no blank codes, no blank preferred labels, no duplicate codes, and
    no duplicate preferred labels
- Subtask `1.2 / 15`:
  - assert `CVN_ENTITY_TYPE` reports `has_delegate is True`,
    `has_other_like_entry is True`, and `open_world_signals` includes
    `delegate_present` plus at least one label-token signal
- Subtask `1.3 / 15`:
  - run `uv run pytest tests/test_auxiliary_source_loaders_unit.py -v`
- Expected result before implementation:
  - tests fail because the enum-evidence fields do not exist yet
- User manual modifications needed:
  - code test changes should be made by the user unless explicit code-edit
    approval is given
- Next step:
  - extend `ReferenceTableMetadata`

### Task `2 / 15` - Extend `ReferenceTableMetadata`

- Task summary:
  - enrich reference-table metadata with deterministic codes, labels, duplicate
    flags, blank flags, other-like detection, and open-world signals
- Files involved:
  - `src/cvn_codegen/auxiliary_sources/reference_tables_metadata.py`
- Subtask `2.1 / 15`:
  - add these dataclass fields:
    `item_codes`, `preferred_labels`, `normalized_codes`,
    `normalized_preferred_labels`, `has_blank_code`,
    `has_blank_preferred_label`, `has_duplicate_codes`,
    `has_duplicate_preferred_labels`, `has_other_like_entry`, and
    `open_world_signals`
- Subtask `2.2 / 15`:
  - add repository-local helpers to strip whitespace, collapse repeated internal
    whitespace, normalize item codes, and normalize labels to ASCII-compatible
    uppercase
- Subtask `2.3 / 15`:
  - add deterministic preferred-label selection: Spanish label first, English
    label second, first available label otherwise
- Subtask `2.4 / 15`:
  - detect label tokens `OTRO`, `OTRA`, `OTROS`, `OTRAS`, `OTHER`, `OTHERS`,
    `RESTO`, `NO CONSTA`, and `SIN ESPECIFICAR` as open-world signals when they
    appear as full labels or clear standalone terms
- Subtask `2.5 / 15`:
  - add structural open-world signals `delegate_present`, `blank_code`, and
    `blank_preferred_label`
- Subtask `2.6 / 15`:
  - compute duplicate-code flags from normalized codes and duplicate-label flags
    from normalized non-empty preferred labels
- Subtask `2.7 / 15`:
  - run `uv run pytest tests/test_auxiliary_source_loaders_unit.py -v`
- Expected result after implementation:
  - loader tests pass
- User manual modifications needed:
  - code changes should be made by the user unless explicit code-edit approval is
    given
- Next step:
  - extend reference-resolution tests

### Task `3 / 15` - Add Reference-Resolution Evidence Tests

- Task summary:
  - add failing tests proving `ReferenceResolution` carries enum evidence only
    for `ReferenceTables.xml` resolutions
- Files involved:
  - `tests/test_auxiliary_reference_resolution_unit.py`
- Subtask `3.1 / 15`:
  - assert `NO_REFERENCE`, side-package registry, side-package thesaurus, and
    unresolved references attach `reference_table_enum_evidence is None`
- Subtask `3.2 / 15`:
  - assert direct table `CVN_SEX_A` attaches non-`None` evidence with
    `table_name == "CVN_SEX_A"` and `item_count == 2`
- Subtask `3.3 / 15`:
  - assert subtype-backed table `CVN_KNOW_A` attaches non-`None` evidence while
    keeping `source_family == ReferenceSourceFamily.SUBTYPE_BACKED_TABLE`
- Subtask `3.4 / 15`:
  - run `uv run pytest tests/test_auxiliary_reference_resolution_unit.py -v`
- Expected result before implementation:
  - tests fail because `ReferenceResolution.reference_table_enum_evidence` does
    not exist yet
- User manual modifications needed:
  - code test changes should be made by the user unless explicit code-edit
    approval is given
- Next step:
  - add the typed enum-evidence contract

### Task `4 / 15` - Add `ReferenceTableEnumEvidence` Contract

- Task summary:
  - extend the normalization contract with an additive typed evidence record
- Files involved:
  - `src/cvn_codegen/normalization_types.py`
- Subtask `4.1 / 15`:
  - add frozen dataclass `ReferenceTableEnumEvidence` with fields:
    `table_name`, `item_count`, `has_hierarchy`, `has_delegate`,
    `has_other_like_entry`, `has_duplicate_codes`,
    `has_duplicate_preferred_labels`, `has_blank_code`,
    `has_blank_preferred_label`, `normalized_codes`, `preferred_labels`,
    `normalized_preferred_labels`, and `open_world_signals`
- Subtask `4.2 / 15`:
  - add `reference_table_enum_evidence: ReferenceTableEnumEvidence | None = None`
    at the end of `ReferenceResolution` to preserve existing constructors
- Subtask `4.3 / 15`:
  - run `uv run pytest tests/test_auxiliary_reference_resolution_unit.py tests/test_semantic_policy_unit.py -v`
- Expected result after this task:
  - constructor compatibility remains stable; resolution tests may still fail
    until evidence wiring is implemented
- User manual modifications needed:
  - code changes should be made by the user unless explicit code-edit approval is
    given
- Next step:
  - attach evidence during reference resolution

### Task `5 / 15` - Attach Evidence In Reference Resolution

- Task summary:
  - populate `ReferenceResolution.reference_table_enum_evidence` from
    `ReferenceTableMetadata` for all resolved `ReferenceTables.xml` cases
- Files involved:
  - `src/cvn_codegen/auxiliary_sources/reference_resolution.py`
- Subtask `5.1 / 15`:
  - add helper `build_reference_table_enum_evidence(table_metadata)` that copies
    the normalized facts from `ReferenceTableMetadata` into
    `ReferenceTableEnumEvidence`
- Subtask `5.2 / 15`:
  - attach evidence in the `table_metadata is not None` branch of
    `resolve_manual_reference(...)`
- Subtask `5.3 / 15`:
  - preserve `None` evidence in `NO_REFERENCE`, `ENTITY@Entity.xsd`,
    `THESAURUS@thesaurus.xsd`, and unresolved branches
- Subtask `5.4 / 15`:
  - run `uv run pytest tests/test_auxiliary_reference_resolution_unit.py -v`
- Expected result after implementation:
  - reference-resolution evidence tests pass
- User manual modifications needed:
  - code changes should be made by the user unless explicit code-edit approval is
    given
- Next step:
  - add semantic-policy eligibility tests

### Task `6 / 15` - Add Direct Semantic Eligibility Tests

- Task summary:
  - add failing semantic-policy tests for dynamic enum eligibility independent of
    table-name hardcoding
- Files involved:
  - `tests/test_semantic_policy_unit.py`
- Subtask `6.1 / 15`:
  - import `ReferenceTableEnumEvidence`,
    `evaluate_reference_table_enum_eligibility`, and
    `MAX_STRICT_ENUM_ITEM_COUNT`
- Subtask `6.2 / 15`:
  - test closed compact evidence equivalent to `CVN_SEX_A` returns
    `EnumEligibility.ELIGIBLE` and `PolicyConfidence.HIGH`
- Subtask `6.3 / 15`:
  - test evidence with other-like/open-world signal but no immediate blocker
    returns `EnumEligibility.REVIEW_REQUIRED` and
    `PolicyConfidence.REQUIRES_REVIEW`
- Subtask `6.4 / 15`:
  - test subtype-backed `CVN_KNOW_A` context returns `EnumEligibility.INELIGIBLE`
- Subtask `6.5 / 15`:
  - test hierarchical `UNESCO_CODES` evidence returns
    `EnumEligibility.INELIGIBLE`
- Subtask `6.6 / 15`:
  - test side-package, unresolved, and `evidence is None` contexts return
    `EnumEligibility.INELIGIBLE`
- Subtask `6.7 / 15`:
  - run `uv run pytest tests/test_semantic_policy_unit.py -v`
- Expected result before implementation:
  - tests fail because the helper and constant do not exist yet
- User manual modifications needed:
  - code test changes should be made by the user unless explicit code-edit
    approval is given
- Next step:
  - implement the dynamic eligibility helper

### Task `7 / 15` - Implement Dynamic Eligibility Helper

- Task summary:
  - implement deterministic enum eligibility evaluation from typed evidence
- Files involved:
  - `src/cvn_codegen/semantic_policy.py`
- Subtask `7.1 / 15`:
  - import `ReferenceSourceFamily` and `ReferenceTableEnumEvidence`
- Subtask `7.2 / 15`:
  - add `MAX_STRICT_ENUM_ITEM_COUNT = 64`
- Subtask `7.3 / 15`:
  - add `evaluate_reference_table_enum_eligibility(...)` with the accepted
    signature and return type
- Subtask `7.4 / 15`:
  - implement immediate ineligibility reasons:
    `source_family_not_reference_table`,
    `semantic_kind_not_compact_enum_like_table`, `subtype_backed`,
    `missing_enum_evidence`, `hierarchy_present`, and `delegate_present`
- Subtask `7.5 / 15`:
  - implement review-required reasons: `other_like_entry`, `blank_code`,
    `blank_preferred_label`, `duplicate_codes`, `duplicate_preferred_labels`,
    `empty_table`, and `item_count_above_limit`
- Subtask `7.6 / 15`:
  - implement eligible result with reason `strict_enum_eligible`
- Subtask `7.7 / 15`:
  - run `uv run pytest tests/test_semantic_policy_unit.py -v`
- Expected result after implementation:
  - direct semantic eligibility helper tests pass
- User manual modifications needed:
  - code changes should be made by the user unless explicit code-edit approval is
    given
- Next step:
  - replace temporary semantic-policy bridge

### Task `8 / 15` - Replace Temporary Enum Policy

- Task summary:
  - remove temporary table-name-based review logic and use dynamic evidence in
    field-policy resolution
- Files involved:
  - `src/cvn_codegen/semantic_policy.py`
- Subtask `8.1 / 15`:
  - remove `TEMPORARY_REVIEW_REQUIRED_REFERENCES`
- Subtask `8.2 / 15`:
  - remove `apply_temporary_enum_review_policy(...)`
- Subtask `8.3 / 15`:
  - call `evaluate_reference_table_enum_eligibility(...)` from
    `build_semantic_field_policy(...)` using
    `reference_resolution.reference_table_enum_evidence`,
    `reference_resolution.source_family`, `reference_resolution.semantic_kind`,
    and `reference_resolution.is_subtype_backed`
- Subtask `8.4 / 15`:
  - if eligibility is `ELIGIBLE`, keep `STRICT_ENUM_CANDIDATE` and set
    confidence `HIGH`
- Subtask `8.5 / 15`:
  - if eligibility is `REVIEW_REQUIRED`, keep `STRICT_ENUM_CANDIDATE`, keep
    fallback `OPEN_CODED_VALUE`, and set confidence `REQUIRES_REVIEW`
- Subtask `8.6 / 15`:
  - if eligibility is `INELIGIBLE` for non-compact or non-direct references,
    preserve matrix-driven non-enum shapes
- Subtask `8.7 / 15`:
  - append helper reasons to `SemanticDecisionTrace.applied_rules` with an
    `enum_evidence:` prefix
- Subtask `8.8 / 15`:
  - run `uv run pytest tests/test_semantic_policy_unit.py -v`
- Expected result after implementation:
  - semantic policy no longer depends on temporary table-name constants
- User manual modifications needed:
  - code changes should be made by the user unless explicit code-edit approval is
    given
- Next step:
  - update semantic-policy tests and validation inventory

### Task `9 / 15` - Update Semantic Policy Tests And Inventory

- Task summary:
  - replace temporary-policy expectations with dynamic evidence expectations
- Files involved:
  - `tests/test_semantic_policy_unit.py`
  - `src/cvn_codegen/semantic_policy.py`
- Subtask `9.1 / 15`:
  - replace `test_temporary_enum_review_policy_marks_cvn_sex_a_as_review_required`
    with a dynamic-evidence test expecting `CVN_SEX_A` to be `ELIGIBLE` with
    `HIGH` confidence
- Subtask `9.2 / 15`:
  - replace `test_temporary_enum_review_policy_marks_cvn_entity_type_as_review_required`
    with a dynamic-evidence test that proves the result comes from evidence, not
    table-name hardcoding
- Subtask `9.3 / 15`:
  - update generic compact enum-like test without evidence to expect the helper's
    `INELIGIBLE` result for missing evidence
- Subtask `9.4 / 15`:
  - update validation inventory so `compact_closed_enum_sex` expects
    `EnumEligibility.ELIGIBLE` and `PolicyConfidence.HIGH`
- Subtask `9.5 / 15`:
  - update `compact_open_entity_type` according to the resolved policy decision
    for delegate-backed open behavior
- Subtask `9.6 / 15`:
  - run `uv run pytest tests/test_semantic_policy_unit.py -v`
- Expected result after implementation:
  - semantic-policy tests pass with dynamic evidence
- User manual modifications needed:
  - code and test changes should be made by the user unless explicit code-edit
    approval is given
- Next step:
  - resolve the `CVN_ENTITY_TYPE` delegate-policy contradiction explicitly

### Task `10 / 15` - Resolve `CVN_ENTITY_TYPE` Policy Contradiction

- Task summary:
  - make the execution record explicit about the known tension between the exact
    immediate-ineligibility rule and the older validation expectation for
    `CVN_ENTITY_TYPE`
- Files involved:
  - `docs/roadmap/hotfixes/hotfix-7-dynamic-reference-table-enum-eligibility-evaluation.md`
  - `docs/roadmap/issues/issue-14-semantic-mapping-rules.md` during closure
- Subtask `10.1 / 15`:
  - record observed canonical evidence: `CVN_ENTITY_TYPE` has `17` items,
    `has_delegate is True`, and contains code/label evidence for `OTHERS`
- Subtask `10.2 / 15`:
  - choose and document the final policy before code is considered complete
- Subtask `10.3 / 15`:
  - recommended decision: respect the exact immediate-ineligibility rule, so
    `CVN_ENTITY_TYPE` is `INELIGIBLE` due to `delegate_present`; record this as
    an implementation adjustment to the older `REVIEW_REQUIRED` expectation
- Subtask `10.4 / 15`:
  - if the user instead requires the older expectation, move `has_delegate` from
    immediate ineligibility to review-required before implementation proceeds
- User manual modifications needed:
  - none expected if documentation changes are authorized; code policy changes
    still require explicit code-edit approval
- Next step:
  - add integration tests with real source data

### Task `11 / 15` - Add Real-Source Integration Tests

- Task summary:
  - validate dynamic enum decisions using the canonical auxiliary bundle and real
    `ReferenceTables.xml` records
- Files involved:
  - `tests/test_semantic_policy_unit.py`
  - possibly `tests/test_auxiliary_reference_resolution_unit.py`
- Subtask `11.1 / 15`:
  - use `build_auxiliary_source_bundle(...)` and `resolve_manual_reference(...)`
    to obtain real resolution for `CVN_SEX_A`
- Subtask `11.2 / 15`:
  - assert `CVN_SEX_A` real evidence reaches `EnumEligibility.ELIGIBLE`
- Subtask `11.3 / 15`:
  - assert `CVN_ENTITY_TYPE` real evidence exposes `delegate_present` and
    other-like/open-world signals
- Subtask `11.4 / 15`:
  - assert `CVN_KNOW_A` real subtype-backed resolution remains enum-ineligible
- Subtask `11.5 / 15`:
  - assert `UNESCO_CODES` real hierarchical resolution remains enum-ineligible
- Subtask `11.6 / 15`:
  - run `uv run pytest tests/test_semantic_policy_unit.py tests/test_auxiliary_reference_resolution_unit.py -v`
- Expected result after implementation:
  - representative real-source dynamic cases pass
- User manual modifications needed:
  - code test changes should be made by the user unless explicit code-edit
    approval is given
- Next step:
  - run targeted regression tests

### Task `12 / 15` - Run Targeted Regression Tests

- Task summary:
  - prove loader, resolution, semantic policy, and normalization-report behavior
    remain stable
- Commands:
  - `uv run pytest tests/test_auxiliary_source_loaders_unit.py -v`
  - `uv run pytest tests/test_auxiliary_reference_resolution_unit.py -v`
  - `uv run pytest tests/test_semantic_policy_unit.py -v`
  - `uv run pytest -n auto tests/test_normalization_report_unit.py tests/test_normalization_unit.py -v`
- Subtask `12.1 / 15`:
  - run auxiliary loader tests
- Subtask `12.2 / 15`:
  - run auxiliary reference-resolution tests
- Subtask `12.3 / 15`:
  - run semantic-policy tests
- Subtask `12.4 / 15`:
  - run normalization regression tests
- Subtask `12.5 / 15`:
  - document exact failures if any command fails
- User manual modifications needed:
  - none unless tests expose code or doc fixes required
- Next step:
  - update closure documentation

### Task `13 / 15` - Update Closure Documentation

- Task summary:
  - close the hotfix documentation and align downstream project docs
- Files involved:
  - `docs/roadmap/hotfixes/hotfix-7-dynamic-reference-table-enum-eligibility-evaluation.md`
  - `docs/roadmap/issues/issue-14-semantic-mapping-rules.md`
  - `docs/context/current_status.md`
  - `docs/pipeline/known_limitations.md`
  - `docs/roadmap/cvn_generation_roadmap.md`
- Subtask `13.1 / 15`:
  - update this hotfix record with implementation performed, verification
    commands, findings, and status
- Subtask `13.2 / 15`:
  - update issue `#14` to remove temporary review-required policy language and
    describe dynamic enum evidence
- Subtask `13.3 / 15`:
  - update `docs/context/current_status.md` to mark hotfix `#7` implemented
- Subtask `13.4 / 15`:
  - update `docs/pipeline/known_limitations.md` by removing or refining the
    limitation that dynamic strict enum evidence is missing
- Subtask `13.5 / 15`:
  - update `docs/roadmap/cvn_generation_roadmap.md` if the hotfix state changes
    issue or roadmap wording
- User manual modifications needed:
  - none expected for documentation changes when explicitly requested
- Next step:
  - run full verification

### Task `14 / 15` - Run Full Verification

- Task summary:
  - verify the full repository after the hotfix implementation and documentation
    updates
- Commands:
  - `uv run pytest tests/test_auxiliary_source_loaders_unit.py -v`
  - `uv run pytest tests/test_auxiliary_reference_resolution_unit.py -v`
  - `uv run pytest tests/test_semantic_policy_unit.py -v`
  - `uv run pytest -n auto tests`
- Subtask `14.1 / 15`:
  - run auxiliary loader tests
- Subtask `14.2 / 15`:
  - run auxiliary reference-resolution tests
- Subtask `14.3 / 15`:
  - run semantic-policy tests
- Subtask `14.4 / 15`:
  - run the full repository test suite
- Subtask `14.5 / 15`:
  - record exact command results in the hotfix and issue documentation
- User manual modifications needed:
  - none unless verification fails and code changes are still reserved for the
    user
- Next step:
  - validate final acceptance checklist

### Task `15 / 15` - Validate Acceptance Checklist

- Task summary:
  - confirm the hotfix objective is complete and safe for issue `#15` to consume
- Acceptance checks:
  - `ReferenceTableMetadata` exposes dynamic enum-evidence fields
  - `ReferenceResolution.reference_table_enum_evidence` exists
  - direct `ReferenceTables.xml` and subtype-backed table resolutions attach
    evidence
  - non-reference-table families attach `None`
  - `semantic_policy.py` no longer contains `TEMPORARY_REVIEW_REQUIRED_REFERENCES`
  - `semantic_policy.py` no longer contains table-name branches for
    `CVN_SEX_A` or `CVN_ENTITY_TYPE`
  - `CVN_SEX_A` becomes enum-eligible through evidence
  - `CVN_KNOW_A`, `UNESCO_CODES`, side-package references, unresolved
    references, and under-traced references remain enum-ineligible
  - `CVN_ENTITY_TYPE` is decided by evidence-backed rules, not hardcoding
  - documentation records any implementation adjustment from the original plan
- User manual modifications needed:
  - none expected after all prior tasks are complete
- Next step:
  - start issue `#15` only after acceptance and verification are complete

## Verification Strategy When Implemented

The implementation session that applies this hotfix must verify all of these:

1. `ReferenceTableMetadata` exposes dynamic enum-evidence fields
2. `ReferenceResolution` carries evidence for direct reference-table resolutions
3. issue `#14` no longer uses table-name hardcoding for enum eligibility
4. `CVN_SEX_A` passes dynamically as eligible
5. `CVN_ENTITY_TYPE` is decided dynamically from evidence; current canonical
   evidence makes it enum-ineligible because `delegate_present` is an immediate
   blocker
6. subtype-backed, hierarchical, side-package, unresolved, and under-traced
   families remain non-eligible

Minimum commands:

```bash
uv run pytest tests/test_auxiliary_source_loaders_unit.py -v
uv run pytest tests/test_auxiliary_reference_resolution_unit.py -v
uv run pytest tests/test_semantic_policy_unit.py -v
uv run pytest -n auto tests
```

## Implementation Performed

- `ReferenceTableMetadata` now exposes normalization-grade enum evidence derived
  from `ReferenceTables.xml`, including item codes, preferred labels,
  normalized codes, normalized preferred labels, duplicate flags, blank flags,
  other-like detection, and open-world signals.
- Preferred labels are selected deterministically from multilingual
  `NameDetail` values using Spanish first, English second, and the first
  available label otherwise.
- `ReferenceTableEnumEvidence` is now part of the typed normalization contract.
- `ReferenceResolution.reference_table_enum_evidence` now carries evidence for
  resolved direct `ReferenceTables.xml` tables and subtype-backed tables.
- Non-reference-table families still carry `None` evidence, including
  side-package registry, side-package thesaurus, no-reference, and unresolved
  cases.
- `semantic_policy.py` now evaluates strict enum eligibility through
  `evaluate_reference_table_enum_eligibility(...)` and
  `MAX_STRICT_ENUM_ITEM_COUNT = 64`.
- The previous temporary review-required policy for `CVN_SEX_A` and
  `CVN_ENTITY_TYPE` has been replaced by evidence-backed rules.

## Implementation Adjustment

- The original validation expectation said `CVN_ENTITY_TYPE` should land in
  `REVIEW_REQUIRED`.
- Canonical source inspection during implementation showed that
  `CVN_ENTITY_TYPE` has `17` items, `has_delegate is True`, and contains
  open-world evidence such as `OTHERS`.
- The accepted execution decision was to keep the exact immediate-ineligibility
  rule for delegates.
- Therefore `CVN_ENTITY_TYPE` now lands in `INELIGIBLE` dynamically with
  `delegate_present` as the blocker instead of landing in `REVIEW_REQUIRED`.
- This is not a hardcoded table-name exception; it follows the generic delegate
  rule from normalized evidence.

## Verification Performed

- The user reported targeted verification passed with these commands:
  - `uv run pytest tests/test_auxiliary_source_loaders_unit.py -q`
  - `uv run pytest tests/test_auxiliary_reference_resolution_unit.py -q`
  - `uv run pytest tests/test_semantic_policy_unit.py -q`
  - `uv run pytest -n auto tests/test_normalization_report_unit.py tests/test_normalization_unit.py -q`
- Targeted documented verification passed with:
  - `uv run pytest -n auto tests/test_auxiliary_source_loaders_unit.py tests/test_auxiliary_reference_resolution_unit.py tests/test_semantic_policy_unit.py tests/test_normalization_report_unit.py tests/test_normalization_unit.py -v`
  - result: `95 passed in 364.71s (0:06:04)`
- Full repository verification passed with:
  - `uv run pytest -n auto tests`
  - result: `146 passed in 404.14s (0:06:44)`

## Impact On Future Issues

- removes pressure to hardcode reviewed table names in issue `#14`
- gives issue `#15` a scalable strict-enum decision input
- gives issue `#16` a concrete dynamic-evaluation test target
- lets issue `#17` document a reproducible policy instead of a manually curated
  exception list

## Status

- Status: implemented and verified
- Implementation state: completed
