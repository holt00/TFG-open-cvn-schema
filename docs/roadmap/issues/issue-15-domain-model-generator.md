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

## Status

- Status: pending
