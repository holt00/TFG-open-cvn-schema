# Issue 8 - Epic: Automate CVN XML/XSD To Pydantic Translation

## Summary

Issue `#8` is the umbrella epic for building a reproducible translation pipeline
from the official CVN XML/XSD package to structural and later semantic Pydantic
models.

## Original Goal

- establish the full roadmap for automating translation from CVN XML/XSD
  artifacts to Pydantic with minimal manual intervention

## Original Plan

1. reproducible structural bindings from the official XSD package, including the
   canonical auxiliary schema families
2. normalized metadata from `SpecificationManual.xml` and `CVNTreeModel.xml`
3. additive auxiliary-reference resolution enrichment over normalized manual
   references
4. semantic mapping rules for domain generation over enriched normalized
   metadata
5. domain model generation from semantic policy and normalized metadata
6. test and document the full workflow

## Integration Checkpoints

1. structural bindings are reproducible from the canonical package for both core
   and auxiliary schema families
2. metadata layers can be cross-indexed by CVN code
3. normalized entries include machine-readable auxiliary-reference resolution
   metadata
4. semantic rules exist for typing, naming, controlled-reference treatment,
   multiplicity, and overrides
5. domain models can be regenerated from semantic policy and enriched
   normalized metadata
6. the workflow is documented and tested end-to-end

## Current Status

- Epic in progress
- `#11` and `#12` completed
- `#13` completed with additive auxiliary-reference resolution enrichment
- hotfix `#3` documented auxiliary modules recently added in the source bundle
  sent by FECYT
- hotfixes `#4`, `#5`, and `#6` record the corrective replanning required to
  integrate those modules into the structural, normalization, and semantic
  stages
- next pending work starts at issue `#14`, which must consume the enriched
  normalization output already implemented in issue `#13` rather than rebuild
  source-resolution logic from prose documentation

## Supporting Roadmap Document

- `docs/roadmap/cvn_generation_roadmap.md`
