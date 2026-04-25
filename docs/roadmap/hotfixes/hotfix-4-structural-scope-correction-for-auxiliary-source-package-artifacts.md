# Hotfix 4 - Structural Scope Correction For Auxiliary Source Package Artifacts

## Summary

Hotfix `#4` records the structural-generation retrofit required after the source
package documentation expansion from hotfix `#3`.

The repository already implemented the core structural layer for:

- `CVN.xsd`
- `SpecificationManual.xsd`
- `CVNTreeModel_v1.0.xsd`

But the canonical package also contains machine-readable auxiliary families that
were left outside the structural generation plan:

- `ReferenceTables.xsd`
- `Subtypes.xsd`
- `Entity_v1.4.xsd`
- `Thesaurus.xsd`
- repository-derived `UNESCOCodes.xsd`

This hotfix does not implement those changes. It documents exactly how issues
`#11` and `#12` must be corrected so the repository baseline matches the real
source package scope.

## Motivation

Hotfix `#3` established that the canonical CVN package is not only the core
manual, tree model, and CVN XSDs. It also contains auxiliary catalogs and
supporting schemas that are relevant to later semantic work.

Without this retrofit:

- issue `#14` would define semantic rules over incomplete technical inputs
- issue `#15` would need to model external catalogs without generated or
  reproducible structural access to their schemas
- issue `#16` would test only the core package and leave the auxiliary layer
  outside regression coverage

## Scope Of This Hotfix

This hotfix is a planning and correction record.

It does not itself:

- generate new bindings
- change `src/generated/`
- modify runner code
- modify tests

It defines the required corrective work for already created issues.

## Issues Affected

- issue `#11`
- issue `#12`

## Required Changes To Issue `#11`

Issue `#11` remains valid as the infrastructure baseline, but its documented
scope must be expanded so the reserved repository layout matches the canonical
package.

### Repository Layout Changes Required

The infrastructure documentation and intended layout must explicitly reserve
destination packages for the auxiliary structural families under
`src/generated/`.

At minimum, the repository must treat these as planned generated packages:

- `src/generated/reference_tables/`
- `src/generated/subtypes/`
- `src/generated/entity/`
- `src/generated/thesaurus/`

Optional but recommended if the isolated extracted artifact remains part of the
repository contract:

- `src/generated/unesco_codes/`

### Hand-Maintained Pipeline Areas Required

Issue `#11` should also be retroactively understood as reserving space for
hand-maintained support logic dedicated to auxiliary artifacts under
`src/cvn_codegen/`.

The expected future module families are:

- structural loading helpers for auxiliary XML/XSD families
- resolution helpers that connect `manual_reference_table` values to their
  backing artifacts
- normalization or indexing helpers for side-package catalogs

### Documentation Changes Required

Issue `#11` should be updated so its repository layout and future-impact section
explicitly state that the infrastructure baseline must support both:

- core structural bindings
- auxiliary catalog structural bindings

## Required Changes To Issue `#12`

Issue `#12` is the main issue that needs corrective scope expansion.

Its current plan generated structural bindings only for the three core XSD
concerns. The corrected scope must cover the auxiliary schemas that carry
machine-readable catalog semantics.

### New Generation Targets Required

`src/cvn_codegen/xsdata_runner.py` must be extended so `TARGET_TABLE` and the
supported target list include at least:

- `reference_tables`
- `subtypes`
- `entity`
- `thesaurus`

Optional but recommended if treated as a first-class repository artifact:

- `unesco_codes`

### Expected Target Mapping

The corrected target mapping should follow this pattern:

- `ReferenceTables.xsd` -> `generated.reference_tables`
- `Subtypes.xsd` -> `generated.subtypes`
- `Entity_v1.4.xsd` -> `generated.entity`
- `Thesaurus.xsd` -> `generated.thesaurus`
- `UNESCOCodes.xsd` -> `generated.unesco_codes`

### Runner Changes Required

The runner correction must include:

1. add the new targets to `TARGET_TABLE`
2. extend the stable execution order used by `all`
3. add per-target overrides only when a schema actually needs one
4. preserve the current safety checks for output directories
5. keep generation reproducible from `src/`

### Verification Changes Required

Issue `#12` must expand its verification section so it no longer stops at the
three core packages.

The corrected verification must include:

1. import checks for the new generated packages
2. smoke parsing where feasible for:
   - `ReferenceTables.xml`
   - `Subtype_Spa.xml`
   - `Entity.xml`
   - `Thesaurus.xml`
3. documented exceptions when preserved repository layout or source-package
   drift blocks direct parse success

### Test Changes Required

The following existing test modules must be expanded:

- `tests/test_xsdata_runner_unit.py`
- `tests/test_xsdata_runner_smoke.py`

The corrected tests must verify:

1. the new target names are resolvable
2. the runner command is built correctly for each new target
3. generation produces Python files for at least one auxiliary target in smoke
   coverage
4. failures caused by documented source-package drift are recorded as known
   behavior, not hidden

### Issue `#12` Documentation Corrections Required

The issue document for `#12` must be updated so it clearly distinguishes:

- core structural bindings already implemented
- auxiliary structural bindings still missing but now required by corrected scope

Its impact-on-future-issues section must also state that later semantic work
depends on both core and auxiliary structural visibility.

## Files Expected To Change When Applying This Hotfix

When hotfix `#4` is implemented for real, the minimum expected file set is:

- `src/cvn_codegen/xsdata_runner.py`
- `tests/test_xsdata_runner_unit.py`
- `tests/test_xsdata_runner_smoke.py`
- `docs/roadmap/issues/issue-11-project-infrastructure.md`
- `docs/roadmap/issues/issue-12-structural-bindings.md`
- `docs/context/current_status.md`
- `docs/roadmap/cvn_generation_roadmap.md`
- `docs/pipeline/cvn_pydantic_generation_pipeline.md`
- `PROJECT_GUIDE.md` if the visible repository layout summary changes

## Verification Strategy When Implemented

The implementation session that applies this hotfix should verify at minimum:

1. `uv run pytest tests/test_xsdata_runner_unit.py -v`
2. `uv run pytest tests/test_xsdata_runner_smoke.py -v`
3. direct import of all generated auxiliary packages
4. any successful auxiliary parse smoke checks that the preserved package layout
   allows

## Impact On Future Issues

- issue `#13` can no longer be treated as the final technical input boundary for
  semantic work
- issue `#14` should assume structural visibility of the auxiliary families, not
  only prose documentation about them
- issue `#16` must include regression coverage for auxiliary-target generation
- issue `#17` must document the full target set in the regeneration workflow

## Status

- Status: documented as required corrective work
- Implementation state: pending
