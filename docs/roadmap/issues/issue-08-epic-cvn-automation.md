# Issue 8 - Epic: Automate CVN XML/XSD To Pydantic Translation

## Summary

Issue `#8` is the umbrella epic for building a reproducible translation pipeline
from the official CVN XML/XSD package to structural and later semantic Pydantic
models.

## Original Goal

- establish the full roadmap for automating translation from CVN XML/XSD
  artifacts to Pydantic with minimal manual intervention

## Original Plan

1. reproducible structural bindings from the official XSD package
2. normalized metadata from `SpecificationManual.xml` and `CVNTreeModel.xml`
3. semantic mapping rules for domain generation
4. domain model generation from normalized metadata
5. test and document the full workflow

## Integration Checkpoints

1. structural bindings are reproducible from the canonical package
2. metadata layers can be cross-indexed by CVN code
3. semantic rules exist for typing, naming, enums, multiplicity, and overrides
4. domain models can be regenerated from normalized metadata
5. the workflow is documented and tested end-to-end

## Current Status

- Epic in progress
- `#11` and `#12` completed
- hotfix `#3` documented auxiliary modules recently added in the source bundle
  sent by FECYT
- hotfixes `#4`, `#5`, and `#6` record the corrective replanning required to
  integrate those modules into the structural, normalization, and semantic
  stages

## Supporting Roadmap Document

- `docs/roadmap/cvn_generation_roadmap.md`
