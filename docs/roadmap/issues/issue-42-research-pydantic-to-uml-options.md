# Issue 42 - Research Pydantic-To-UML Options

## Summary

Issue `#42` researches how to transform the generated and domain-oriented
Pydantic model layer into UML or UML-like documentation that supports an
agnostic curriculum model.

This issue is part of epic `#41`.

## Goal

- compare available approaches for generating diagrams from many Pydantic models
- decide whether diagrams should be generated from Python classes directly or
  from a conceptual intermediate representation
- avoid producing XML-centric or Python-centric diagrams that obscure the domain

## Background

The current repository can generate domain Pydantic artifacts under
`src/models/cvn/generated/`. Those models preserve traceability and are useful
for validation, but they are not automatically the final conceptual schema.

The TFG requires an agnostic representation of curriculum data. UML must show
curriculum concepts, relationships, cardinality, controlled vocabularies, and
traceability without copying CVN XML structure blindly.

## Research Questions

1. Can existing Python UML tools handle many generated Pydantic classes without
   producing unreadable diagrams?
2. Does Pyreverse produce useful output for this repository, or is it too
   implementation-centric?
3. Is PlantUML or Mermaid a better rendering target for generated conceptual
   diagrams?
4. What Pydantic metadata is available for extracting fields, types,
   relationships, required/optional status, and nested model references?
5. Should the project generate UML from code directly, or from a curated
   conceptual IR created in issue `#43`?

## Candidate Tools And Formats

- Pyreverse from Pylint
- PlantUML class diagrams
- Mermaid class diagrams
- custom Pydantic model introspection
- custom conceptual model IR rendered to one or more diagram formats

## Planned Steps

1. inspect generated domain Pydantic modules and representative model sizes
2. research Pyreverse behavior for large Python/Pydantic projects
3. research PlantUML and Mermaid as text diagram targets
4. prototype or document how a model graph could be extracted from Pydantic
   metadata
5. compare direct-code diagram generation against conceptual-IR diagram
   generation
6. record a recommendation for issue `#43` and issue `#44`

## Expected Output

- research summary document or section in this issue record
- decision on direct code diagrams vs conceptual IR diagrams
- recommended diagram target or targets
- known limitations and tool risks

## Verification

- confirm research references are recorded
- confirm recommendation is explicit enough for issue `#43` to start
- no code implementation required unless a tiny local experiment is explicitly
  approved

## Impact On Later Issues

- issue `#43` uses the chosen extraction direction
- issue `#44` uses the chosen diagram rendering target

## Status

- Status: planned
