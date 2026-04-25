# Hotfix 5 - Normalization Resolution Layer For Auxiliary Reference Sources

## Summary

Hotfix `#5` records the normalization retrofit required after hotfix `#3`
showed that `ManualCodeEntry.manual_reference_table` points to several kinds of
machine-readable sources, not only to opaque strings awaiting later manual
interpretation.

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

This hotfix is a planning and correction record.

It does not itself:

- modify normalization code
- change tests
- add new runtime behavior

It defines the required corrective work for issue `#13`.

## Issues Affected

- issue `#13`

## Required Changes To Issue `#13`

Issue `#13` should remain marked as completed for the core normalization layer,
but its document and implementation plan must now be expanded to include an
additive resolution layer over auxiliary references.

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

The design must preserve backward compatibility for current consumers of:

- `ManualCodeEntry`
- `NormalizedCodeEntry`
- `NormalizationResult`

### New Types Required

Issue `#13` should add typed structures equivalent in intent to the following:

- a reference-source enum or constrained type
- a serialization-pattern enum or constrained type
- a reference-resolution record attached to manual entries or normalized entries

The exact names may vary, but the contract must support these categories:

1. direct `ReferenceTables` table
2. subtype-backed table
3. side-package registry
4. side-package thesaurus
5. hierarchical thematic table
6. unresolved manual-only reference
7. technically present but under-traced table

### New Hand-Maintained Modules Required

Issue `#13` currently spreads normalization across a small flat set of modules.
That remains acceptable, but the following new responsibilities must be added
under `src/cvn_codegen/`:

- loading and indexing of `ReferenceTables.xml`
- loading and indexing of `Subtype_Spa.xml`
- loading and indexing of `Entity.xml` where needed for source classification
- loading and indexing of `Thesaurus*.xml` where needed for source
  classification
- resolution of `manual_reference_table` against those sources
- classification of serialization patterns from machine-readable metadata

This can be implemented either as new dedicated modules or as a small
subpackage, but the logic must stay outside `src/generated/`.

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

### Test Changes Required

The following current tests must be expanded or complemented:

- `tests/test_manual_metadata_unit.py`
- `tests/test_normalization_report_unit.py`
- `tests/test_normalization_unit.py`

The corrected test scope must verify at minimum:

1. direct table resolution from `manual_reference_table`
2. recognition of subtype-backed tables
3. recognition of side-package registry references
4. recognition of thesaurus references
5. unresolved manual-only classification
6. preservation of the current overlap baseline counts from issue `#13`

### Documentation Corrections Required For Issue `#13`

The issue document for `#13` must be updated so it clearly distinguishes two
layers:

1. completed core normalization of manual/tree sources
2. pending auxiliary-reference resolution enrichment required by hotfix `#5`

The issue must no longer imply that `manual_reference_table` is sufficient as a
final semantic input by itself.

## Files Expected To Change When Applying This Hotfix

When hotfix `#5` is implemented for real, the minimum expected file set is:

- `src/cvn_codegen/normalization_types.py`
- `src/cvn_codegen/normalization.py`
- `src/cvn_codegen/normalization_report.py`
- one or more new modules under `src/cvn_codegen/` for auxiliary-source loading
  and resolution
- `tests/test_manual_metadata_unit.py`
- `tests/test_normalization_report_unit.py`
- `tests/test_normalization_unit.py`
- `docs/roadmap/issues/issue-13-normalization.md`
- `docs/context/current_status.md`
- `docs/roadmap/cvn_generation_roadmap.md`
- `docs/pipeline/known_limitations.md` if new resolution limits are discovered

## Verification Strategy When Implemented

The implementation session that applies this hotfix should verify at minimum:

1. `uv run pytest tests/test_manual_metadata_unit.py -v`
2. `uv run pytest tests/test_normalization_report_unit.py -v`
3. `uv run pytest tests/test_normalization_unit.py -v`
4. preservation of the validated baseline counts from issue `#13`
5. correct classification of the documented special cases from hotfix `#3`

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

- Status: documented as required corrective work
- Implementation state: pending
