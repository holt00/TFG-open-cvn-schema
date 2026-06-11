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

<<<<<<< Updated upstream
=======
## Corrected Workflow Stages That Must Be Documented

The final workflow documentation must explicitly include:

1. generation of core structural bindings
2. generation of auxiliary structural bindings
3. normalization of manual and tree metadata
4. auxiliary-source loading and deterministic reference-resolution enrichment
5. semantic policy application over enriched normalized metadata
6. domain-model generation
7. pipeline verification and CI coverage

The semantic policy stage should be documented as the handoff from normalized
metadata to domain generation:

```text
normalized metadata + auxiliary reference resolution
-> SemanticPolicyBundle
-> domain generator
-> domain-oriented Pydantic artifacts
```

The workflow must make clear that `SemanticPolicyBundle` is the source of truth
for generator semantics. Raw XML, raw XSD, and generated structural bindings may
support validation and traceability, but they are not the source for redefining
semantic policy in later stages.

## Controlled-Reference Source-Of-Truth Order

The workflow documentation must explain the effective source-of-truth order for
controlled references already materialized by normalization logic:

1. explicit side-package references such as `ENTITY@Entity.xsd` and
   `THESAURUS@thesaurus.xsd`
2. direct `ReferenceTables.xml` matches where applicable
3. subtype-backed classification through `Subtype@Subtypes.xsd`
4. hierarchical thematic classification where technical metadata supports it
5. unresolved documented exceptions and under-traced tables

>>>>>>> Stashed changes
## Expected Documentation Outcome

- one obvious regeneration workflow
- explicit documentation of authoritative inputs and generated outputs
- explicit documentation of known limitations and unresolved external tables
- sufficient guidance for another contributor to rerun the complete workflow
  from a clean checkout
<<<<<<< Updated upstream
=======
- explicit documentation of repository boundaries between structural fidelity,
  normalization/resolution logic, semantic policy, and domain outputs

## Semantic Policy Documentation Requirements

The final workflow documentation must describe these issue `#14` policy outputs
because issue `#15` and issue `#16` depend on them:

- `domain_shape_kind`
- `fallback_shape_kind`
- `enum_eligibility`
- `policy_confidence`
- `wrapper_policy`
- `presence_kind`
- `cardinality_kind`
- `normalized_name`
- `naming_confidence`
- `structural_limitation_flags`
- `SemanticDecisionTrace`

The workflow documentation must also explain:

- Spanish-first domain naming and deterministic identifier normalization
- versioned and reviewable override policy
- strict-enum eligibility limits
- open coded-value fallback behavior
- wrapper and `xs:choice` treatment
- preservation of CVN source identifiers in trace metadata
- separation between semantic policy decisions and concrete Python emission
  choices

## Repository Boundaries To Document

- `src/generated/` remains structural fidelity layer generated from canonical
  schemas
- `src/cvn_codegen/` contains hand-maintained loading, normalization,
  resolution, semantic-policy, and generation logic
- `src/models/cvn/` remains target location for future domain-oriented outputs

Traceability documentation should identify these values as the minimum chain
from source metadata to domain output:

- CVN `code`
- `xml_path`
- `reference_resolution.trace`
- `SemanticDecisionTrace`

## Known Limitations

- `CVN_AGENCY_C` remains unresolved from package alone
- subtype catalog availability does not always expose a strict per-table key for
  direct subtype verification
- `CVN_INTERVENTION_A` and `CVN_PRUEBA` remain technically present but
  under-traced
- structural bindings do not enforce `xs:choice` mutual exclusivity
- generated list defaults do not reliably enforce every `minOccurs` constraint
- known XML/XSD mismatch behavior, such as `CVNTreeModel.xml`, must remain
  documented as validated limitation rather than hidden failure
>>>>>>> Stashed changes

## Adjustments Made During Implementation

- No implementation has been performed yet.
- Pre-implementation planning is now aligned with the issue `#14` semantic
  policy contract and the issue `#15` generator handoff.
- The future workflow documentation scope now treats semantic policy application
  as an explicit pipeline stage.

## Implementation Performed

- None yet. Issue `#17` remains pending until semantic policy, domain generator,
  and test coverage are implemented.

## Verification

- No workflow verification has been run for issue `#17`.
- Future verification must confirm that the documented commands regenerate or
  validate structural bindings, normalization, semantic policy, domain outputs,
  and tests from a clean checkout.

## Findings

- Workflow documentation must prevent future contributors from treating raw XML,
  raw XSD, or generated structural bindings as semantic-policy sources after
  issue `#14` establishes `SemanticPolicyBundle`.
- The final workflow needs separate explanations for structural fidelity,
  normalization/resolution, semantic policy, generation, and verification.

## Impact On Future Issues

- Issue `#17` should use issue `#14`, issue `#15`, and issue `#16` records as
  source documents for the final workflow.
- Human-facing entry guidance should be updated only if the final workflow
  changes repository orientation, reading order, or document map.

## Status

- Status: pending
