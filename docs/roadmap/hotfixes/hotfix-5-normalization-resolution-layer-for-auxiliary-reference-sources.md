# Hotfix 5 - Normalization Resolution Layer For Auxiliary Reference Sources

## Summary

Hotfix `#5` records the normalization retrofit required after hotfix `#3`
showed that `ManualCodeEntry.manual_reference_table` points to several kinds of
machine-readable sources introduced through auxiliary modules recently added in
the source bundle sent by FECYT, not only to opaque strings awaiting later
manual interpretation.

Issue `#13` successfully normalized `SpecificationManual.xml` and
`CVNTreeModel.xml`, but it deliberately stopped before resolving the technical
backing of manual reference tables against:

- `ReferenceTables.xml`
- `Subtype_Spa.xml`
- `Entity.xml`
- `Thesaurus*.xml`
- repository-derived `UNESCO_CODES.xml`

This hotfix documents exactly how issue `#13` must be extended without breaking
its already validated core baseline.

## Motivation

The current normalization layer is structurally correct but semantically too
shallow for the updated repository understanding.

Today the code extracts:

- `manual_reference_table`

But it does not yet compute:

- whether that reference resolves to `ReferenceTables.xml`
- whether it is subtype-backed through `Subtypes.xsd`
- whether it points to a side-package registry such as `Entity`
- whether it points to a thesaurus
- whether it is unresolved from the package alone

That gap would force issue `#14` to rebuild source resolution logic from scratch
instead of consuming a stable normalized layer.

## Scope Of This Hotfix

This hotfix remains focused on issue `#13`, but it is no longer only a passive
planning record.

The normalization retrofit described here has now been implemented.

The implementation scope of this hotfix is intentionally narrow and must stay
centered on normalization enrichment, not on structural-generation expansion or
roadmap replanning already covered elsewhere.

This hotfix does include:

- additive enrichment of the normalization output from issue `#13`
- machine-readable resolution of `ManualCodeEntry.manual_reference_table`
- loading and indexing of canonical auxiliary XML sources needed for that
  resolution
- classification of serialization patterns from auxiliary technical metadata
- classification of semantic reference kinds needed by later semantic work
- explicit mismatch reporting for unresolved, ambiguous, subtype-missing, and
  under-traced cases

This hotfix does not include:

- structural-generation target expansion already implemented through hotfix `#4`
- roadmap replanning for issues `#14` to `#17` documented by hotfix `#6`
- final semantic policy decisions such as open-versus-closed treatment
- domain-model generation or rich domain normalization of auxiliary catalogs

It converts the documentation knowledge established by hotfix `#3` into stable
normalized metadata consumable by later issues.

## Issues Affected

- issue `#13`

## Required Changes To Issue `#13`

Issue `#13` should remain marked as completed for the core normalization layer,
but its document and implementation plan must now be expanded to include an
additive resolution layer over auxiliary references.

### Corrected Execution Objective

The real objective of this hotfix is not only to keep
`manual_reference_table` as a documented anchor, but to transform that anchor
into executable normalization metadata so issue `#14` does not need to rebuild
source-resolution logic from prose documents.

This means the implementation must absorb the operational knowledge established
by hotfix `#3` that was still only documented, while staying within the
technical boundaries of issue `#13` and without duplicating hotfix `#4` or
hotfix `#6`.

### Contract Changes Required

The normalization contract in `src/cvn_codegen/normalization_types.py` must be
extended with additive fields rather than by replacing the current structures.

At minimum, the normalization output needs a typed representation for:

1. reference resolution status
2. resolved source family
3. resolved source artifact name
4. serialization pattern classification
5. semantic reference kind
6. subtype-backing flag or subtype metadata

The preferred design is to keep `ManualCodeEntry` as the normalized extraction
view of `SpecificationManual.xml` and to attach the richer auxiliary-reference
resolution metadata to `NormalizedCodeEntry`, which is the repository-level
aggregate consumed by later stages.

The design must preserve backward compatibility for current consumers of:

- `ManualCodeEntry`
- `NormalizedCodeEntry`
- `NormalizationResult`

### New Types Required

Issue `#13` should add typed structures equivalent in intent to the following:

- a reference-source enum or constrained type
- a serialization-pattern enum or constrained type
- a semantic-reference-kind enum or constrained type
- a reference-resolution trace type when needed for artifact traceability
- a reference-resolution record attached to normalized entries

The exact names may vary, but the contract must support these categories:

1. direct `ReferenceTables` table
2. subtype-backed table
3. side-package registry
4. side-package thesaurus
5. hierarchical thematic table
6. unresolved manual-only reference
7. technically present but under-traced table

At minimum, the implementation should support a record equivalent in intent to:

1. raw manual reference value
2. resolution status
3. resolved source family
4. resolved artifact name
5. resolved technical or logical source name
6. serialization pattern classification
7. semantic reference kind
8. subtype-backing indicator
9. subtype-support indicator or subtype metadata summary
10. traceability and diagnostics

### New Hand-Maintained Modules Required

Issue `#13` currently spreads normalization across a small flat set of modules.
For the hotfix implementation, that flat shape no longer needs to be preserved
strictly.

The preferred implementation is now a small dedicated subpackage under
`src/cvn_codegen/` for auxiliary-source support and resolution.

The following responsibilities must be added under `src/cvn_codegen/`:

- loading and indexing of `ReferenceTables.xml`
- loading and indexing of `Subtype_Spa.xml`
- loading and indexing of `Entity.xml` for normalization-grade registry
  traceability
- loading and indexing of `Thesaurus*.xml` for normalization-grade vocabulary
  traceability
- resolution of `manual_reference_table` against those sources
- classification of serialization patterns from machine-readable metadata
- classification of semantic reference kinds from the resolved source family and
  technical metadata

The logic must stay outside `src/generated/`.

The preferred module split is equivalent in intent to:

- `auxiliary_sources/reference_tables_metadata.py`
- `auxiliary_sources/subtypes_metadata.py`
- `auxiliary_sources/entity_metadata.py`
- `auxiliary_sources/thesaurus_metadata.py`
- `auxiliary_sources/reference_resolution.py`

Exact filenames may vary, but the separation of responsibilities should remain
clear.

### Canonical Auxiliary Parse Scope Required

To make hotfix `#5` fully absorb the actionable knowledge from hotfix `#3`, the
implementation must parse the canonical auxiliary sources at least to the depth
needed for deterministic normalization resolution.

#### `ReferenceTables.xml`

The implementation must parse and index at minimum:

1. table name
2. version
3. `antecesorTable`
4. `source`
5. `XMLDataType`
6. `XMLProperty`
7. `XMLIndicator`
8. item count
9. hierarchical-table signals such as item-level `AntecesorCode`
10. delegation signals such as item-level `Delegate`

#### `Subtype_Spa.xml`

The implementation must parse and index at minimum:

1. source item code
2. preferred name
3. `CodeSubtype1`
4. optional `CodeSubtype2`
5. whether second-level subtype support exists

#### `Entity.xml`

`Entity.xml` must now be parsed during hotfix `#5`, not deferred, but only to a
normalization-grade depth.

That means the implementation must at minimum:

1. verify successful parse of the canonical registry
2. expose stable artifact-level traceability for entity-backed references
3. build a minimal registry index or equivalent lookup support
4. preserve that `Entity` is a structured external registry, not a compact enum

This hotfix does not require full semantic normalization of every entity record.

#### `Thesaurus*.xml`

The implementation must parse the canonical thesaurus family at least to the
depth needed to classify thesaurus-backed references as hierarchical controlled
vocabularies.

The bilingual `Thesaurus.xml` should be treated as the primary canonical source
unless a stronger implementation reason requires a different source-of-truth
policy.

At minimum, the implementation must preserve:

1. artifact traceability
2. hierarchical nature through `itemAncestorId`
3. multilingual nature
4. distinction from compact enum-like tables

### Orchestration Changes Required

`build_normalization_result(...)` in `src/cvn_codegen/normalization.py` must be
expanded so the final normalized result includes auxiliary-reference resolution.

The corrected orchestration must:

1. keep the current code-overlap logic unchanged
2. keep the current `xml_path` logic unchanged
3. build auxiliary indexes from machine-readable source files
4. resolve each `manual_reference_table` deterministically
5. attach the resolution result to the normalized output
6. preserve source traceability for every resolved reference

The corrected orchestration should also preserve backward compatibility for the
current core call style while allowing auxiliary-source loading to be integrated
without changing the validated overlap logic from issue `#13`.

The current code-overlap baseline must remain unchanged:

- total normalized codes: `1457`
- manual-only codes: `27`
- tree-only codes: `1`
- overlapping codes: `1429`

### Resolution Procedure Required

The implementation must resolve manual references through a deterministic
source-of-truth order compatible with the repository documentation established by
hotfix `#3`.

At minimum, the resolution procedure must support:

1. empty or missing reference
2. exact explicit side-package references such as `ENTITY@Entity.xsd`
3. exact explicit side-package references such as `THESAURUS@thesaurus.xsd`
4. exact table match in `ReferenceTables.xml`
5. subtype-backed classification through `Subtype@Subtypes.xsd`
6. hierarchical thematic classification where technical metadata supports it
7. unresolved manual-only references
8. technically present but under-traced table reporting

This deterministic source-resolution layer is the main implementation objective
of the hotfix.

### Serialization-Pattern Classification Required

The implementation must materialize the repository reference taxonomy from
`docs/cvn_serialization_patterns_reference.md` into typed machine-readable
normalization metadata.

At minimum, the classification contract must support categories equivalent in
intent to:

1. `Filter/Value`
2. `Quality/Measure`
3. `Scope/Type`
4. `ExternalPK/Type`
5. `Entity/Type`
6. `Dedication`
7. `PhysicalDimension/Type`
8. `Subject/Description`
9. `Subtype@Subtypes.xsd`
10. side-package registry
11. side-package thesaurus
12. unresolved manual-only reference
13. technically present but under-traced table

Derivation should prefer technical metadata from `ReferenceTables.xml` over
hardcoded table-name-only logic, except where side-package reference strings or
explicit documented exceptions require direct handling.

### Semantic-Reference-Kind Classification Required

To capture the actionable repository knowledge from hotfix `#3` without pulling
issue `#14` semantic policy work forward, the normalization layer must at least
classify resolved references into stable semantic kinds.

The contract must support categories equivalent in intent to:

1. compact enum-like table
2. compact scale or measure table
3. identifier-type table
4. scope table
5. subtype-backed controlled family
6. hierarchical thematic classification
7. side-package registry
8. side-package thesaurus or vocabulary
9. unresolved manual-only reference
10. technically present but under-traced table

This classification is still normalization metadata, not final domain policy.

### Mismatch And Limitation Reporting Changes Required

`src/cvn_codegen/normalization_report.py` and
`NormalizationMismatchKind` must be extended so the normalization layer can
explicitly report the new source-resolution findings.

At minimum, the corrected mismatch taxonomy must support:

- unresolved manual reference
- ambiguous auxiliary resolution
- subtype-backed reference lacking expected subtype support
- technically present but under-traced table

Known repository cases that must be represented explicitly:

- `CVN_AGENCY_C` as unresolved manual-only reference
- `CVN_INTERVENTION_A` as technically present but currently under-traced
- `CVN_PRUEBA` as technically present but currently under-traced
- `CVN_KNOW_A` as an explicitly subtype-backed table family

### Repository Knowledge From Hotfix `#3` That Must Become Executable

The implementation must explicitly absorb the following repository facts already
documented by hotfix `#3`, because leaving them as prose-only knowledge would
defeat the purpose of the normalization enrichment:

1. `UNESCO_CODES` must be classifiable as a hierarchical thematic table rather
   than a plain compact enum
2. `CVN_KNOW_A` must be classifiable as subtype-backed
3. `CVN_AGENCY_C` must remain explicit as unresolved from the package alone
4. `CVN_INTERVENTION_A` and `CVN_PRUEBA` must remain explicit as technically
   present but functionally under-traced
5. side-package references must remain distinguishable from compact tables
6. `manual_reference_table` must stop being treated as only an opaque string in
   downstream normalized output

### Test Changes Required

The following current tests must be expanded or complemented:

- `tests/test_manual_metadata_unit.py`
- `tests/test_normalization_report_unit.py`
- `tests/test_normalization_unit.py`

Adding a dedicated auxiliary-resolution unit test module is strongly recommended.

The corrected test scope must verify at minimum:

1. direct table resolution from `manual_reference_table`
2. recognition of subtype-backed tables
3. recognition of side-package registry references
4. recognition of thesaurus references
5. unresolved manual-only classification
6. preservation of the current overlap baseline counts from issue `#13`
7. explicit handling of `UNESCO_CODES` as hierarchical thematic classification
8. explicit handling of `CVN_KNOW_A` as subtype-backed
9. explicit reporting of `CVN_INTERVENTION_A` and `CVN_PRUEBA` as under-traced
10. backward compatibility of the current core normalization entry point

### Documentation Corrections Required For Issue `#13`

The issue document for `#13` must be updated so it clearly distinguishes two
layers:

1. completed core normalization of manual/tree sources
2. started auxiliary-reference resolution enrichment required by hotfix `#5`

The issue must no longer imply that `manual_reference_table` is sufficient as a
final semantic input by itself.

It must also make explicit that issue `#13` now has a second additive execution
phase that converts the repository's documented auxiliary-source knowledge into
normalized machine-readable resolution metadata.

## Agreed Action Plan

The implementation of this hotfix will follow the corrected execution path
below.

### Phase `1` - Preserve Validated Core Baseline

1. keep the current overlap logic unchanged
2. keep the current `xml_path` logic unchanged
3. preserve the validated code-count baseline from issue `#13`

### Phase `2` - Extend The Normalization Contract

1. add typed resolution-status metadata
2. add typed source-family metadata
3. add typed serialization-pattern metadata
4. add typed semantic-reference-kind metadata
5. attach reference-resolution metadata to normalized aggregate entries

### Phase `3` - Add Auxiliary Source Loaders

1. load and index `ReferenceTables.xml`
2. load and index `Subtype_Spa.xml`
3. parse `Entity.xml` to normalization-grade depth
4. parse `Thesaurus.xml` and companion projections to normalization-grade depth

### Phase `4` - Implement Deterministic Reference Resolution

1. resolve explicit side-package references
2. resolve direct table references from `ReferenceTables.xml`
3. detect subtype-backed references from technical metadata
4. classify hierarchical thematic references
5. preserve unresolved and under-traced cases explicitly

### Phase `5` - Materialize Documented Pattern Taxonomy

1. classify serialization patterns from auxiliary technical metadata
2. classify semantic reference kinds without collapsing them into final domain
   policy
3. convert the key documentation facts from hotfix `#3` into executable
   normalized metadata

### Phase `6` - Extend Reporting And Tests

1. extend mismatch taxonomy for auxiliary-resolution findings
2. add or expand tests for direct, subtype-backed, registry, thesaurus,
   unresolved, and under-traced cases
3. verify regression safety of the core normalization baseline

### Phase `7` - Update Persistent Documentation

1. update `docs/roadmap/issues/issue-13-normalization.md`
2. update `docs/context/current_status.md`
3. update `docs/roadmap/cvn_generation_roadmap.md`
4. update `docs/pipeline/known_limitations.md` only if new limits are found

## Files Expected To Change When Applying This Hotfix

When hotfix `#5` is implemented for real, the minimum expected file set is:

- `src/cvn_codegen/normalization_types.py`
- `src/cvn_codegen/normalization.py`
- `src/cvn_codegen/normalization_report.py`
- one or more new modules or a small subpackage under `src/cvn_codegen/` for
  auxiliary-source loading and resolution
- `tests/test_manual_metadata_unit.py`
- `tests/test_normalization_report_unit.py`
- `tests/test_normalization_unit.py`
- dedicated auxiliary-resolution tests if split into a new module
- `docs/roadmap/issues/issue-13-normalization.md`
- `docs/context/current_status.md`
- `docs/roadmap/cvn_generation_roadmap.md`
- `docs/pipeline/known_limitations.md` if new resolution limits are discovered

## Verification Strategy When Implemented

The implementation session that applies this hotfix should verify at minimum:

1. `uv run pytest tests/test_manual_metadata_unit.py -v`
2. `uv run pytest tests/test_normalization_report_unit.py -v`
3. `uv run pytest tests/test_normalization_unit.py -v`
4. dedicated auxiliary-resolution tests if created
5. preservation of the validated baseline counts from issue `#13`
6. correct classification of the documented special cases from hotfix `#3`
7. successful normalization-grade parse coverage for `Entity.xml` and canonical
   thesaurus inputs used by the implementation

## Implemented Outcome

The current repository implementation now provides the following validated
additive layer over the original issue `#13` baseline.

### Contract Outcome

- `src/cvn_codegen/normalization_types.py` now includes typed auxiliary
  resolution metadata through:
  - `ReferenceResolutionStatus`
  - `ReferenceSourceFamily`
  - `SerializationPattern`
  - `SemanticReferenceKind`
  - `ReferenceResolutionTrace`
  - `ReferenceResolution`
- `NormalizedCodeEntry` now carries additive `reference_resolution` metadata
  without replacing `ManualCodeEntry.manual_reference_table`

### Auxiliary Loader Outcome

- normalization-grade auxiliary-source support now exists under
  `src/cvn_codegen/auxiliary_sources/`
- canonical auxiliary metadata can now be loaded for:
  - `ReferenceTables.xml`
  - `Subtype_Spa.xml`
  - `Entity.xml`
  - `Thesaurus.xml`
- a reusable `AuxiliarySourceBundle` now aggregates those inputs for the
  normalization stage

### Resolution Outcome

- manual reference resolution is now implemented as a deterministic layer over
  normalized manual entries
- the current implementation resolves and classifies at minimum:
  - direct `ReferenceTables.xml` tables such as `CVN_SEX_A`
  - subtype-backed families such as `CVN_KNOW_A`
  - side-package registry references such as `ENTITY@Entity.xsd`
  - side-package thesaurus references such as `THESAURUS@thesaurus.xsd`
  - hierarchical thematic references such as `UNESCO_CODES`
  - unresolved documented exceptions such as `CVN_AGENCY_C`
  - under-traced documented tables such as `CVN_INTERVENTION_A` and
    `CVN_PRUEBA`

### Reporting Outcome

- `src/cvn_codegen/normalization_report.py` now reports auxiliary-resolution
  findings in addition to the original core mismatch set
- the current auxiliary-resolution mismatch categories implemented are:
  - unresolved manual reference
  - ambiguous auxiliary resolution
  - missing subtype support
  - under-traced reference table

### Verification Outcome

- the validated normalization baseline from issue `#13` is preserved:
  - total normalized codes: `1457`
  - manual-only codes: `27`
  - tree-only codes: `1`
  - overlapping codes: `1429`
- the current implementation reports the following mismatch distribution when
  auxiliary sources are enabled:
  - `27` `MANUAL_ONLY_CODE`
  - `1` `TREE_ONLY_CODE`
  - `2` `UNEXPECTED_TREE_ELEMENT`
  - `1` `UNRESOLVED_MANUAL_REFERENCE`
  - `2` `UNDER_TRACED_REFERENCE_TABLE`

### Documented Implementation Limits Still Present

- `Subtype_Spa.xml` proves subtype catalog availability but does not provide a
  direct table-family key such as `CVN_KNOW_A` for strict per-table subtype
  verification
- the current unresolved auxiliary-reference set therefore includes:
  - `CVN_AGENCY_C`

## Impact On Future Issues

- issue `#14` should consume resolved auxiliary-reference metadata instead of
  re-deriving the source-of-truth rules from prose documents
- issue `#15` can generate different domain shapes for enums, registries,
  thesauri, and subtype-backed families from normalized data rather than from ad
  hoc logic
- issue `#16` must include regression tests for reference-resolution behavior
- issue `#17` must document normalization as a richer stage than simple manual
  and tree cross-indexing

## Status

- Status: implemented and verified with documented limitations
- Implementation state: completed
