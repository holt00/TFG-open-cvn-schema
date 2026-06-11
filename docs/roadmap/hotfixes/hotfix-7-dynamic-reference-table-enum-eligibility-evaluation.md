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
2. `CVN_ENTITY_TYPE` becomes `REVIEW_REQUIRED` dynamically
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

## Verification Strategy When Implemented

The implementation session that applies this hotfix must verify all of these:

1. `ReferenceTableMetadata` exposes dynamic enum-evidence fields
2. `ReferenceResolution` carries evidence for direct reference-table resolutions
3. issue `#14` no longer uses table-name hardcoding for enum eligibility
4. `CVN_SEX_A` passes dynamically as eligible
5. `CVN_ENTITY_TYPE` lands dynamically in review-required
6. subtype-backed, hierarchical, side-package, unresolved, and under-traced
   families remain non-eligible

Minimum commands:

```bash
uv run pytest tests/test_auxiliary_source_loaders_unit.py -v
uv run pytest tests/test_auxiliary_reference_resolution_unit.py -v
uv run pytest tests/test_semantic_policy_unit.py -v
uv run pytest -n auto tests
```

## Impact On Future Issues

- removes pressure to hardcode reviewed table names in issue `#14`
- gives issue `#15` a scalable strict-enum decision input
- gives issue `#16` a concrete dynamic-evaluation test target
- lets issue `#17` document a reproducible policy instead of a manually curated
  exception list

## Status

- Status: documented as required corrective work
- Implementation state: pending
