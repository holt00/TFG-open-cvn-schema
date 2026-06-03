# Issue 17 - Document And Automate The Complete Workflow

## Summary

Issue `#17` will leave the repository with a clear, reproducible, documented
workflow for regenerating structural bindings, normalized metadata, and domain
models.

## Corrected Prerequisite Chain

Issue `#17` must document full workflow as it actually exists after hotfixes
`#4` and `#5`, not older reduced core-only workflow.

The documented workflow must therefore include both:

1. auxiliary structural generation stages already added to repository
2. auxiliary-reference resolution enrichment already added to normalization
   stage

## Original Goal

- document the architecture and automate the complete CVN regeneration workflow

## Original Plan

1. document the architecture and source relationships
2. document the workflow step by step
3. document known limitations and external dependencies
4. provide a clear regeneration entry point
5. update repository documentation
6. leave one obvious workflow for future contributors

## Corrected Workflow Stages That Must Be Documented

The final workflow documentation must explicitly include:

1. generation of core structural bindings
2. generation of auxiliary structural bindings
3. normalization of manual and tree metadata
4. auxiliary-source loading and deterministic reference-resolution enrichment
5. semantic policy application over enriched normalized metadata
6. domain-model generation
7. pipeline verification and CI coverage

## Controlled-Reference Source-Of-Truth Order

The workflow documentation must explain the effective source-of-truth order for
controlled references already materialized by normalization logic:

1. explicit side-package references such as `ENTITY@Entity.xsd` and
   `THESAURUS@thesaurus.xsd`
2. direct `ReferenceTables.xml` matches where applicable
3. subtype-backed classification through `Subtype@Subtypes.xsd`
4. hierarchical thematic classification where technical metadata supports it
5. unresolved documented exceptions and under-traced tables

## Expected Documentation Outcome

- one obvious regeneration workflow
- explicit documentation of authoritative inputs and generated outputs
- explicit documentation of known limitations and unresolved external tables
- sufficient guidance for another contributor to rerun the complete workflow
  from a clean checkout
- explicit documentation of repository boundaries between structural fidelity,
  normalization/resolution logic, semantic policy, and domain outputs

## Repository Boundaries To Document

- `src/generated/` remains structural fidelity layer generated from canonical
  schemas
- `src/cvn_codegen/` contains hand-maintained loading, normalization,
  resolution, semantic-policy, and generation logic
- `src/models/cvn/` remains target location for future domain-oriented outputs

## Known Limits That Must Stay Visible

- `CVN_AGENCY_C` remains unresolved from package alone
- subtype catalog availability does not always expose a strict per-table key for
  direct subtype verification
- known XML/XSD mismatch behavior, such as `CVNTreeModel.xml`, must remain
  documented as validated limitation rather than hidden failure

## Status

- Status: pending
