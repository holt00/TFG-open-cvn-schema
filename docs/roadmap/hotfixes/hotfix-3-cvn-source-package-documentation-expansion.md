# Hotfix 3 - CVN Source Package Documentation Expansion

## Summary

This maintenance record documents the documentation-only patch applied during the
session that expanded repository coverage of the canonical CVN source package,
including auxiliary modules recently added to the delivered source bundle sent
by FECYT.

## Motivation

The repository already documented the core CVN structural artifacts, but the
canonical source bundle sent by FECYT also included several recently added
auxiliary families and a large set of Annex I tables that were not documented
in equivalent depth.

That gap made later semantic work harder because future sessions would still need
to reopen the original package to understand:

- how side-package artifacts related to core CVN files
- which Annex I tables were technically represented
- which references were subtype-backed, hierarchical, or unresolved
- how current normalization output should be interpreted without changing the
  existing core

## Scope Of This Patch

This patch is documentation-only.

It does not change:

- structural bindings
- normalization contracts from issue `#13`
- tests or runtime code

It adds and updates persistent documentation so the repository can be resumed
without reconstructing source-package semantics from chat history.

## Documentation Added

The following persistent documents were added:

- `docs/cvn_source_package_auxiliary_artifacts.md`
- `docs/cvn_source_package_annex_table_coverage.md`
- `docs/cvn_annex_priority_table_families.md`
- `docs/cvn_annex_table_families_batch3.md`
- `docs/cvn_annex_table_families_batch4.md`
- `docs/cvn_annex_table_families_batch5.md`
- `docs/cvn_annex_table_families_batch6.md`
- `docs/cvn_annex_table_families_batch7.md`
- `docs/cvn_annex_table_families_batch8.md`
- `docs/cvn_serialization_patterns_reference.md`
- `docs/cvn_field_reference_traceability.md`

## Documentation Updated

The following repository entry or context documents were updated to point to the
new reference material and to keep the global context aligned:

- `PROJECT_GUIDE.md`
- `docs/context/project_context_index.md`
- `docs/context/current_status.md`
- `docs/pipeline/cvn_pydantic_generation_pipeline.md`
- `docs/pipeline/known_limitations.md`
- `docs/informe_estructura_cvnxml_v1.4.3.md`
- `docs/roadmap/issues/issue-14-semantic-mapping-rules.md`

## Main Outcomes

This patch established the following persistent knowledge in the repository.

### 1. Side-Package Families Are Now Explicitly Documented

The repository now documents the structure, role, and relationships of the
recently added auxiliary modules sent by FECYT:

- `Entity`
- `ReferenceTables/Subtypes`
- `Thesaurus`

### 2. Annex I Coverage Is Now Explicitly Classified

The repository now distinguishes between:

- tables represented directly in core XSD artifacts
- tables represented through side-package XML/XSD artifacts
- manual-only or unresolved references

### 3. Detailed Coverage Of `ReferenceTables.xml` Is Complete

All tables present in `ReferenceTables.xml` are now documented explicitly in the
repository, including:

- high-priority families such as `CVN_SOURCE_*`, `CVN_TITLE_*`, `CVN_PROJECT_*`,
  `CVN_ENTITY_TYPE`, and `UNESCO_CODES`
- subsequent batches covering participation, programmes, publications, support,
  events, activities, management, scope, language, time, qualification, access,
  subject, stays, dedication, prizes, thematic tables, geography, situation,
  agencies, collaboration, supervision, categories, and residual tables

### 4. Special Cases Are Now Explicitly Recorded

The repository now preserves the following cases as explicit documentation facts:

- `CVN_AGENCY_C` is referenced by the manual but does not have a clean matching
  table in `ReferenceTables.xml`
- `CVN_INTERVENTION_A` and `CVN_PRUEBA` exist in `ReferenceTables.xml` but do not
  currently show a clear use site in `SpecificationManual.xml`
- `CVN_KNOW_A` is a subtype-backed industrial-property table and must be treated
  as such in later semantic work

### 5. Serialization Patterns Are Now Documented Separately From The Core

The repository now records the main serialization patterns used by CVN tables,
including:

- `Filter/Value`
- `Quality/Measure`
- `Scope/Type`
- `ExternalPK/Type`
- `Entity/Type`
- `Dedication`
- `PhysicalDimension/Type`
- `Subject/Description`
- `Subtype@Subtypes.xsd`
- side-package catalog patterns
- unresolved manual-only references

### 6. Existing Normalization Output Now Has An Operational Interpretation Guide

The repository now documents how to interpret the already implemented
`ManualCodeEntry.manual_reference_table` field from issue `#13` without changing
the normalization core.

## Consistency Cleanup Performed

During the same session, documentation consistency issues were also corrected:

- outdated project snapshot in `project_context_index.md`
- outdated wording around issue `#13`
- missing issue `#25` mention in `PROJECT_GUIDE.md`
- incomplete implemented-issues list in `project_context_index.md`
- ambiguous reading-order wording in `current_status.md`
- missing cross-links between Annex coverage, serialization patterns, and field
  traceability documents
- mismatch between traceability examples and named serialization patterns
- excessive repetition in the status summary was compressed to a more stable form

## Impact On Later Issues

This patch does not implement issue `#14`, but it substantially reduces semantic
discovery work for it.

The new documentation should make it easier to:

- define semantic mapping rules without re-reading the whole source package
- classify table references correctly by technical pattern
- distinguish compact enums from hierarchical codelists and large registries
- keep future work compatible with the current normalization core

## Status

- Status: completed
