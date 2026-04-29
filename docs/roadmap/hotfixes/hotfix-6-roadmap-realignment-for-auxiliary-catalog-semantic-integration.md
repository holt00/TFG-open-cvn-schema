# Hotfix 6 - Roadmap Realignment For Auxiliary Catalog Semantic Integration

## Summary

Hotfix `#6` records the roadmap correction required after hotfixes `#4` and
`#5`.

The original roadmap for issues `#14` to `#17` assumed that the repository would
reach semantic work after only two technical preparation stages:

1. structural bindings for the core schemas
2. normalization of `SpecificationManual.xml` and `CVNTreeModel.xml`

After the auxiliary source-package analysis from hotfix `#3`, that sequencing is
no longer sufficient. Future issues must explicitly incorporate the auxiliary
catalog families recently added in the source bundle sent by FECYT and the
resolution layer built over them.

This hotfix does not implement those future issues. It documents exactly how the
already created issue set must be replanned.

## Motivation

If the roadmap is left unchanged:

- issue `#14` would try to define semantic policy over incomplete normalized
  inputs
- issue `#15` would likely mix discovery work with generation work
- issue `#16` would test a pipeline that still lacks the now-documented
  auxiliary-source integration stage
- issue `#17` would document an incomplete workflow

## Scope Of This Hotfix

This hotfix is a planning and correction record.

It does not itself:

- implement issue `#14`
- implement issue `#15`
- implement issue `#16`
- implement issue `#17`

It defines the required replanning for those issues and for the roadmap-level
documents that describe them.

## Issues Affected

- issue `#8`
- issue `#14`
- issue `#15`
- issue `#16`
- issue `#17`
- issue `#25` as CI impact only

## Required Changes To Issue `#8`

The epic summary in issue `#8` must be updated because its current state and
integration checkpoints are historically outdated.

The corrected epic narrative must state that the technical foundation now has
three preparation layers before domain-model generation can proceed safely:

1. core and auxiliary structural bindings
2. core normalization of manual and tree sources
3. auxiliary reference-resolution enrichment over normalized manual references

The epic current-status section must also stop saying that issue `#13` is the
next planned issue.

## Required Changes To Issue `#14`

Issue `#14` needs the largest scope correction among pending issues.

### New Required Input Assumption

Issue `#14` must no longer assume that semantic policy begins from only:

- manual type
- multiplicity
- `manual_reference_table`
- `xml_path`

It must now explicitly consume the enriched normalization output from hotfix
`#5`, including resolved source family and serialization-pattern metadata.

### New Decision Areas Required

The issue plan for `#14` must explicitly classify references into at least these
semantic kinds:

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

### New Policy Outputs Required

The final semantic policy for issue `#14` must define:

1. open versus closed treatment per reference kind
2. enum eligibility rules
3. registry-reference treatment for `Entity`
4. hierarchical vocabulary treatment for `Thesaurus` and `UNESCO_CODES`
5. subtype-backed treatment for `Subtype@Subtypes.xsd`
6. fallback policy for unresolved references such as `CVN_AGENCY_C`

## Required Changes To Issue `#15`

Issue `#15` must be replanned so it does not flatten all controlled references
into the same generation strategy.

### New Generator Responsibilities Required

The generator design for `#15` must support distinct domain representations for:

1. strict enums or near-enums
2. open coded values
3. structured external registry references
4. hierarchical subject or thesaurus references
5. subtype-backed values with traceability to subtype codification
6. unresolved references that must remain explicit in the domain layer

### New Output Principle Required

Issue `#15` should explicitly prefer domain shapes that preserve semantic class
distinctions instead of collapsing everything to `str` plus comments.

## Required Changes To Issue `#16`

Issue `#16` must be expanded so its test matrix covers the newly explicit
auxiliary-reference stage.

### New Coverage Categories Required

The corrected test plan must include:

1. generation tests for auxiliary structural targets
2. normalization-resolution tests for auxiliary references
3. regression coverage for subtype-backed tables
4. regression coverage for side-package references
5. regression coverage for unresolved references
6. end-to-end tests proving that semantic generation consumes the enriched
   normalization layer correctly

## Required Changes To Issue `#17`

Issue `#17` must document the complete workflow as it actually exists after the
roadmap correction.

### Workflow Stages That Must Be Documented

The final workflow documentation must explicitly include:

1. generation of core structural bindings
2. generation of auxiliary structural bindings
3. normalization of manual and tree metadata
4. auxiliary reference-resolution enrichment
5. semantic policy application
6. domain-model generation
7. pipeline verification and CI coverage

It must also explain the source-of-truth order for controlled references:

1. core XSD tables where applicable
2. `ReferenceTables.xml`
3. side-package registries and vocabularies
4. unresolved documented exceptions

## Required Changes To Issue `#25`

Issue `#25` does not need a new workflow file for this correction, but its
impact-on-future-issues section should be updated so it explicitly states that
CI will automatically pick up:

- new auxiliary-generation tests
- new normalization-resolution tests
- future semantic-pipeline tests

as long as those tests remain under `tests/`.

## Roadmap-Level Changes Required

The roadmap document must be updated so the dependency narrative reflects the
corrected sequence.

At minimum, it must state that:

- issue `#14` depends on the corrected outputs described by hotfixes `#4` and
  `#5`
- issue `#15` depends on the corrected semantic policy from issue `#14`
- issue `#16` must test both the original core pipeline and the auxiliary-source
  enrichment path
- issue `#17` must document the corrected full workflow, not the earlier reduced
  one

## Files Expected To Change When Applying This Hotfix

When hotfix `#6` is implemented for real, the minimum expected documentation set
to update is:

- `docs/roadmap/issues/issue-08-epic-cvn-automation.md`
- `docs/roadmap/issues/issue-14-semantic-mapping-rules.md`
- `docs/roadmap/issues/issue-15-domain-model-generator.md`
- `docs/roadmap/issues/issue-16-generation-pipeline-tests.md`
- `docs/roadmap/issues/issue-17-workflow-documentation.md`
- `docs/roadmap/issues/issue-25-github-actions-ci-pipeline-for-pr-testing-on-main-and-development.md`
- `docs/roadmap/cvn_generation_roadmap.md`
- `docs/context/current_status.md`
- `PROJECT_GUIDE.md` if the contributor reading path changes

## Verification Strategy When Implemented

This hotfix is a roadmap correction, so verification is documentation-based.

The implementation session that applies it should verify that:

1. every affected issue document reflects the corrected prerequisite chain
2. the roadmap and epic summary no longer describe outdated sequencing
3. future contributors can identify the auxiliary-reference stage before issue
   `#14` starts

## Impact On Future Issues

- reduces the risk that issue `#14` and issue `#15` mix source discovery with
  semantic policy design
- makes issue `#16` test planning more realistic
- ensures issue `#17` documents the complete workflow instead of the older core
  subset only

## Status

- Status: documented as required corrective work
- Implementation state: pending
