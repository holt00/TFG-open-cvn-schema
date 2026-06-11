# Issue 15 - Implement The Domain Pydantic Model Generator

## Summary

Issue `#15` will generate cleaner domain models from normalized metadata and
semantic mapping rules.

## Corrected Prerequisite Chain

Issue `#15` must consume two already prepared upstream layers:

1. auxiliary structural visibility from hotfix `#4`
2. enriched normalized metadata with `reference_resolution` from issue `#13`
   after hotfix `#5`

This issue must not redo source discovery or auxiliary-reference resolution.
Those responsibilities are already implemented upstream and should only be
consumed through the semantic policy finalized in issue `#14`.

## Original Goal

- emit readable, traceable, reproducible domain Pydantic models from the
  normalized metadata layer

## Original Plan

1. traverse `CVNItem`, `Property`, and `Indicator`
2. generate domain models for representative CVN blocks
3. factor reusable domain components where appropriate
4. preserve CVN code traceability in emitted code
5. keep output separate from structural bindings
6. make regeneration deterministic

## Corrected Generator Responsibilities

The generator design for issue `#15` must support distinct domain
representations for the controlled-reference classes already surfaced by
normalization and semantic policy.

At minimum, the generator must support:

1. strict enums or near-enums for closed compact tables
2. open coded-value representations for open controlled tables
3. structured external registry references for `Entity`-backed values
4. hierarchical subject or vocabulary references for `Thesaurus` and
   `UNESCO_CODES`
5. subtype-backed values with traceability to subtype codification support
6. explicit unresolved or under-traced reference representations when the
   package cannot support a stronger domain guarantee

The generator should prefer domain shapes that preserve semantic class
distinctions instead of flattening all controlled references to `str` plus
comments.

<<<<<<< Updated upstream
=======
## Corrected Generator Responsibilities

The generator design for issue `#15` must support distinct domain
representations for the controlled-reference classes already surfaced by
normalization and semantic policy.

At minimum, the generator must support:

1. strict enums or near-enums for closed compact tables
2. open coded-value representations for open controlled tables
3. structured external registry references for `Entity`-backed values
4. hierarchical subject or vocabulary references for `Thesaurus` and
   `UNESCO_CODES`
5. subtype-backed values with traceability to subtype codification support
6. explicit unresolved or under-traced reference representations when the
   package cannot support a stronger domain guarantee

The generator should prefer domain shapes that preserve semantic class
distinctions instead of flattening all controlled references to `str` plus
comments.

## Semantic Policy Handoff From Issue `#14`

Issue `#15` must treat the semantic policy contract from issue `#14` as its
generator input contract. The expected upstream policy artifact is
`SemanticPolicyBundle`.

The generator should consume these semantic-policy decisions directly:

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

Issue `#15` may decide concrete Python emission details, such as `Enum`,
`Literal`, Pydantic model classes, wrapper classes, or open coded-value records.
It must not change the semantic meaning established by issue `#14`.

The generator must not emit strict enums for policy outputs representing:

- registry references
- thesaurus or vocabulary references
- hierarchical code references
- subtype-backed values
- unresolved references
- under-traced references

Under-traced references should remain explicit in policy-aware generator logic,
but issue `#15` should not emit fields for under-traced tables unless normalized
metadata entries later reference those tables.

>>>>>>> Stashed changes
## Recommended First Scope

- identification
- contact information
- basic personal data
- a representative subset of `CVNItem` blocks
- at least one representative block for each major controlled-reference family
  already classified upstream

## Expected Outputs

- executable generator code
- first generated domain Pydantic models
- reusable shared domain components
- explicit traceability from generated domain artifacts back to CVN code and
  semantic-policy decisions where needed

## Generation Principle

- consume normalized metadata rather than generating from raw XSDs directly
- consume semantic policy from issue `#14` and enriched normalized metadata from
  issue `#13` rather than re-deriving source-of-truth rules in the generator
- keep `src/generated/` as structural layer and emit domain output separately

## Minimum Corrected Scope

Issue `#15` should document and implement at minimum:

1. traversal from normalized CVN item/group structure into generation units
2. deterministic mapping from semantic policy outputs to domain model shapes
3. different emitted shapes for enum-like, open coded, registry, thesaurus,
   hierarchical, subtype-backed, unresolved, and under-traced references
4. reusable domain components only where they preserve semantic meaning instead
   of erasing distinctions
5. regeneration determinism and traceability back to normalized input and CVN
   code

## Questions Still To Decide

1. whether strict enums should become Python `Enum`, `Literal`, or another
   constrained representation
2. what shape should represent `Entity`-backed references in generated domain
   models
3. what shape should represent hierarchical thesaurus and `UNESCO_CODES`
   references
4. how subtype-backed families should preserve subtype traceability in generated
   output
5. how unresolved or under-traced references should remain explicit without
   pretending stronger validation than repository can currently support

## Constraints To Respect

- issue `#13` already resolves auxiliary-reference source families and semantic
  kinds; generator must not duplicate that logic
- issue `#14` is responsible for semantic policy decisions; generator must
  implement those decisions, not redefine them
- generated domain artifacts must stay separate from structural bindings under
  `src/generated/`
- code-level traceability should remain preserved even when generated names and
  domain shapes differ from XML-oriented structures

## Adjustments Made During Implementation

- No implementation has been performed yet.
- Pre-implementation planning is now aligned with the agreed semantic policy
  contract from issue `#14`.
- The generator scope is clarified so semantic decisions come from
  `SemanticPolicyBundle`, not from raw XML, raw XSD, or regenerated
  auxiliary-source classification.

## Implementation Performed

- None yet. Issue `#15` remains pending until issue `#14` implementation is
  complete.

## Verification

- No code verification has been run for issue `#15`.
- Future verification must prove generated domain artifacts consume semantic
  policy outputs instead of redefining semantic classification in generator code.

## Findings

- The generator needs an explicit handoff boundary from issue `#14` to avoid
  duplicating reference-resolution and semantic-classification logic.
- Final Python artifact shapes are still an issue `#15` decision, but semantic
  categories and override outcomes are not.

## Known Limitations

- Domain model emission is not implemented yet.
- Concrete Python representations for strict enums, open coded values,
  registries, vocabularies, subtype-backed values, unresolved references, and
  under-traced references remain undecided until issue `#15` implementation.

## Impact On Future Issues

- Issue `#16` must test generator behavior against `SemanticPolicyBundle`
  outputs rather than raw source classifications.
- Issue `#17` must document `SemanticPolicyBundle` as the semantic source of
  truth for domain generation.

## Status

- Status: pending
