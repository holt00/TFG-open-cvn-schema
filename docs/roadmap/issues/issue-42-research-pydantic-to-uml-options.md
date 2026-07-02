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

## Accepted Execution Protocol

The user accepted this execution plan before issue `#42` research starts.

At every execution step, the implementer must report:

1. current task number and task name
2. current subtask number and subtask name, when a subtask is being executed
3. short initial summary of what the task or subtask will do
4. short final result for the task or subtask
5. whether the user must modify any file manually
6. next step to follow

File-modification rule:

- documentation changes may be performed when explicitly requested
- code changes should be left for the user unless the user explicitly authorizes
  the agent to edit code
- generated code under `src/generated/` must not be edited manually
- generated domain code under `src/models/cvn/generated/` must not be edited
  manually

## Accepted Execution Plan

### Task `1 / 14` - Confirm Issue Scope

- Task summary:
  - confirm issue `#42` boundaries against epic `#41`, issue `#43`, issue `#44`,
    and the current generated-domain baseline
- Files involved:
  - `docs/roadmap/issues/issue-42-research-pydantic-to-uml-options.md`
  - `docs/roadmap/issues/issue-41-epic-agnostic-schema-json-parser.md`
  - `docs/roadmap/issues/issue-43-agnostic-conceptual-model-extraction-layer.md`
  - `docs/roadmap/issues/issue-44-generate-uml-or-uml-like-diagrams.md`
- Subtask `1.1 / 14`:
  - confirm issue `#42` is research-only unless a tiny local experiment is
    explicitly approved
- Subtask `1.2 / 14`:
  - confirm issue `#42` must recommend a direction for issue `#43` and a diagram
    target for issue `#44`
- Subtask `1.3 / 14`:
  - record any scope adjustment if the research discovers a mismatch with epic
    `#41`
- User manual modifications needed:
  - none expected for scope confirmation
- Next step:
  - inventory the generated domain model layer

### Task `2 / 14` - Inventory Current Domain Models

- Task summary:
  - measure the generated Pydantic model layer so tool evaluation is based on the
    real repository size instead of assumptions
- Files involved:
  - `src/models/cvn/components.py`
  - `src/models/cvn/generated/`
  - `src/cvn_codegen/domain_model_generator.py`
  - `src/cvn_codegen/domain_model_types.py`
- Subtask `2.1 / 14`:
  - count generated modules, generated model classes, enum classes, and shared
    component classes
- Subtask `2.2 / 14`:
  - inspect representative models from identity, professional, education,
    research, and vocabulary-heavy areas
- Subtask `2.3 / 14`:
  - record how fields currently encode scalar values, wrappers, controlled
    references, repeated fields, and required fields
- Subtask `2.4 / 14`:
  - identify obvious noise sources for Python class diagrams, such as generated
    module names and implementation helper inheritance
- User manual modifications needed:
  - none expected; this task is read-only
- Next step:
  - analyze what Pydantic metadata can expose for diagram extraction

### Task `3 / 14` - Analyze Available Pydantic Metadata

- Task summary:
  - determine what can be extracted from Pydantic v2 models without re-reading raw
    CVN XML or XSD files
- Files involved:
  - `src/models/cvn/components.py`
  - `src/models/cvn/generated/`
  - `src/cvn_codegen/domain_model_types.py`
- Subtask `3.1 / 14`:
  - inspect `model_fields`, annotations, defaults, and required/optional flags for
    representative generated models
- Subtask `3.2 / 14`:
  - inspect whether `cvn_trace` or field metadata preserves CVN code, XML path,
    base kind, domain shape, enum eligibility, and source reference
- Subtask `3.3 / 14`:
  - inspect how enums and shared controlled-reference components can be identified
    through Python type annotations
- Subtask `3.4 / 14`:
  - record which conceptual facts are available from Pydantic alone and which
    facts still need normalized or semantic-policy metadata
- User manual modifications needed:
  - none expected; this task is read-only unless the user approves a small local
    script or experiment
- Next step:
  - evaluate Pyreverse as a direct-code UML option

### Task `4 / 14` - Evaluate Pyreverse

- Task summary:
  - decide whether Pyreverse can produce useful diagrams for this repository or
    whether it is only useful as a technical dependency graph
- Files involved:
  - `src/models/cvn/components.py`
  - `src/models/cvn/generated/`
  - `pyproject.toml` only if the user later approves adding tooling, which is not
    expected for issue `#42`
- Subtask `4.1 / 14`:
  - research Pyreverse capabilities for class diagrams over large Python packages
- Subtask `4.2 / 14`:
  - evaluate likely noise from generated classes, Pydantic internals, shared base
    classes, imports, and enum modules
- Subtask `4.3 / 14`:
  - if explicitly approved, run a tiny local experiment outside tracked project
    outputs and record the result
- Subtask `4.4 / 14`:
  - classify Pyreverse as suitable, partially useful, or unsuitable for agnostic
    conceptual UML
- User manual modifications needed:
  - none expected; any dependency or experiment output must be approved first
- Next step:
  - evaluate PlantUML as a generated diagram target

### Task `5 / 14` - Evaluate PlantUML

- Task summary:
  - assess whether PlantUML is an appropriate text target for conceptual class
    diagrams generated from an intermediate model
- Files involved:
  - no repository files expected during research
  - future issue `#44` may create `.puml` files under `docs/` or a dedicated
    diagram output directory
- Subtask `5.1 / 14`:
  - research PlantUML class diagram support for packages, classes, attributes,
    relations, cardinalities, stereotypes, and notes
- Subtask `5.2 / 14`:
  - evaluate how PlantUML can represent controlled vocabularies and CVN trace
    notes without overloading diagrams
- Subtask `5.3 / 14`:
  - record tooling implications, including renderer availability and whether raw
    `.puml` source can remain the canonical output
- Subtask `5.4 / 14`:
  - decide whether PlantUML should be the primary or secondary issue `#44` target
- User manual modifications needed:
  - none expected during research
- Next step:
  - evaluate Mermaid as an alternative diagram target

### Task `6 / 14` - Evaluate Mermaid

- Task summary:
  - assess whether Mermaid class diagrams are sufficient for readable,
    repository-native UML-like documentation
- Files involved:
  - no repository files expected during research
  - future issue `#44` may embed Mermaid diagrams in Markdown documentation
- Subtask `6.1 / 14`:
  - research Mermaid class diagram support for classes, attributes, relationships,
    multiplicities, annotations, and namespaces
- Subtask `6.2 / 14`:
  - evaluate GitHub rendering benefits against expressiveness limits for large
    conceptual diagrams
- Subtask `6.3 / 14`:
  - record whether Mermaid can carry traceability and controlled vocabulary
    information cleanly or should remain a lightweight publication target
- Subtask `6.4 / 14`:
  - decide whether Mermaid should be the primary or secondary issue `#44` target
- User manual modifications needed:
  - none expected during research
- Next step:
  - evaluate custom Pydantic introspection

### Task `7 / 14` - Evaluate Custom Pydantic Introspection

- Task summary:
  - determine whether repository code can extract a model graph directly from
    Pydantic classes and whether that graph is conceptual enough
- Files involved:
  - `src/models/cvn/components.py`
  - `src/models/cvn/generated/`
  - `src/cvn_codegen/domain_model_types.py`
  - `src/cvn_codegen/domain_model_generator.py`
- Subtask `7.1 / 14`:
  - define the minimal graph extractable from Pydantic classes: model, field,
    type, multiplicity, required flag, enum, and component reference
- Subtask `7.2 / 14`:
  - compare extracted Python class graph with the domain concepts expected by the
    TFG and `docs/propuesta_modelado_uml_ocl_cvn.md`
- Subtask `7.3 / 14`:
  - identify where direct Pydantic introspection leaks Python implementation or
    generated CVN item grouping into the diagram
- Subtask `7.4 / 14`:
  - record whether direct introspection is useful as an input to issue `#43`, as a
    fallback, or not recommended
- User manual modifications needed:
  - none expected; implementation belongs to issue `#43` only if authorized later
- Next step:
  - evaluate a conceptual intermediate representation as the preferred path

### Task `8 / 14` - Evaluate Conceptual Intermediate Representation

- Task summary:
  - define why an agnostic conceptual IR may be needed before UML or JSON schema
    outputs
- Files involved:
  - `docs/propuesta_modelado_uml_ocl_cvn.md`
  - `docs/roadmap/issues/issue-43-agnostic-conceptual-model-extraction-layer.md`
  - `src/cvn_codegen/domain_model_types.py`
  - `src/cvn_codegen/semantic_policy.py`
  - `src/cvn_codegen/normalization_types.py`
- Subtask `8.1 / 14`:
  - identify conceptual IR entities needed for curriculum concepts, fields,
    relationships, vocabularies, cardinalities, and trace data
- Subtask `8.2 / 14`:
  - identify implementation details that must be excluded from conceptual output,
    such as XML wrapper mechanics, generated module names, and raw CVN item class
    proliferation
- Subtask `8.3 / 14`:
  - map current repository evidence sources to IR fields: generated Pydantic
    models, normalized metadata, semantic policy, and `cvn_trace`
- Subtask `8.4 / 14`:
  - define the minimum recommendation that issue `#43` needs to start
- User manual modifications needed:
  - none expected during research
- Next step:
  - compare all strategies through a decision matrix

### Task `9 / 14` - Compare Diagram Generation Strategies

- Task summary:
  - compare direct-code and conceptual-IR approaches using explicit criteria
- Files involved:
  - `docs/roadmap/issues/issue-42-research-pydantic-to-uml-options.md`
- Subtask `9.1 / 14`:
  - compare Pyreverse direct diagrams, custom direct Pydantic diagrams, and
    conceptual-IR-driven diagrams
- Subtask `9.2 / 14`:
  - score or rank each option by readability, domain agnosticism, traceability,
    reproducibility, maintainability, dependency cost, and fit for TFG
- Subtask `9.3 / 14`:
  - compare PlantUML and Mermaid as rendering targets independently from the
    extraction strategy
- Subtask `9.4 / 14`:
  - identify which option is suitable for issue `#43` and which option is
    suitable for issue `#44`
- User manual modifications needed:
  - none expected for documentation update when explicitly requested
- Next step:
  - decide whether a tiny local experiment is useful

### Task `10 / 14` - Define Optional Tiny Local Experiment

- Task summary:
  - decide whether issue `#42` needs practical evidence beyond documentation and
    static inspection
- Files involved:
  - no tracked repository files expected
  - temporary files, if approved, must stay under `/tmp/opencode`
- Subtask `10.1 / 14`:
  - select a tiny representative subset of generated models if an experiment is
    approved
- Subtask `10.2 / 14`:
  - run Pyreverse or create a throwaway PlantUML/Mermaid sketch only when
    explicitly approved by the user
- Subtask `10.3 / 14`:
  - evaluate readability, noise, and trace preservation from the experiment
- Subtask `10.4 / 14`:
  - record that no productive repository code was added
- User manual modifications needed:
  - none expected unless the user chooses to perform the experiment manually
- Next step:
  - write the final recommendation

### Task `11 / 14` - Record Final Recommendation

- Task summary:
  - provide a concrete decision for issues `#43` and `#44`
- Files involved:
  - `docs/roadmap/issues/issue-42-research-pydantic-to-uml-options.md`
- Subtask `11.1 / 14`:
  - decide whether UML should be generated from Python classes directly or from a
    curated conceptual IR
- Subtask `11.2 / 14`:
  - recommend a primary diagram target and optional secondary target
- Subtask `11.3 / 14`:
  - specify what issue `#43` must build or define before issue `#44` renders
    diagrams
- Subtask `11.4 / 14`:
  - specify which direct-code tools, if any, remain useful as diagnostics rather
    than final documentation
- User manual modifications needed:
  - none expected for documentation update when explicitly requested
- Next step:
  - record known limitations and tool risks

### Task `12 / 14` - Record Risks And Limitations

- Task summary:
  - preserve research risks so later issues do not rediscover them
- Files involved:
  - `docs/roadmap/issues/issue-42-research-pydantic-to-uml-options.md`
  - `docs/pipeline/known_limitations.md` only if a new pipeline limitation is
    discovered
- Subtask `12.1 / 14`:
  - record risks from generated model volume and diagram readability
- Subtask `12.2 / 14`:
  - record risks from implementation-centric Python diagrams
- Subtask `12.3 / 14`:
  - record risks from incomplete semantic cardinality or relationship evidence
    when using Pydantic alone
- Subtask `12.4 / 14`:
  - record target-specific risks for PlantUML and Mermaid
- User manual modifications needed:
  - none expected unless new limitation requires manual review before adding to
    `known_limitations.md`
- Next step:
  - update issue documentation and status

### Task `13 / 14` - Update Persistent Documentation

- Task summary:
  - close issue `#42` research in repository documentation once the recommendation
    is complete
- Files involved:
  - `docs/roadmap/issues/issue-42-research-pydantic-to-uml-options.md`
  - `docs/context/current_status.md`
  - `docs/roadmap/cvn_generation_roadmap.md` if the issue status changes there
  - `docs/pipeline/known_limitations.md` if a new limitation was found
  - `PROJECT_GUIDE.md` only if human-facing orientation changes
- Subtask `13.1 / 14`:
  - add research summary and comparison matrix to issue `#42`
- Subtask `13.2 / 14`:
  - add final recommendation for issue `#43` and issue `#44`
- Subtask `13.3 / 14`:
  - update issue status after research verification
- Subtask `13.4 / 14`:
  - update current status and roadmap records if applicable
- Subtask `13.5 / 14`:
  - update known limitations only if research found a durable pipeline limitation
- User manual modifications needed:
  - none expected for documentation updates when explicitly requested
- Next step:
  - verify issue `#42` closure criteria

### Task `14 / 14` - Verify Research Closure

- Task summary:
  - verify that issue `#42` has enough evidence and decisions for issue `#43` to
    start without ambiguity
- Files involved:
  - `docs/roadmap/issues/issue-42-research-pydantic-to-uml-options.md`
- Subtask `14.1 / 14`:
  - confirm research references are recorded
- Subtask `14.2 / 14`:
  - confirm direct-code versus conceptual-IR recommendation is explicit
- Subtask `14.3 / 14`:
  - confirm recommended diagram target or targets are explicit
- Subtask `14.4 / 14`:
  - confirm known risks and limitations are recorded
- Subtask `14.5 / 14`:
  - confirm no code implementation was added unless explicitly approved
- User manual modifications needed:
  - none expected
- Next step:
  - start issue `#43` only after the user accepts issue `#42` closure

## Expected Output

- research summary document or section in this issue record
- decision on direct code diagrams vs conceptual IR diagrams
- recommended diagram target or targets
- known limitations and tool risks

## Research References

- Pyreverse documentation, Pylint `pyreverse` additional tool:
  `https://pylint.readthedocs.io/en/stable/additional_tools/pyreverse/index.html`
- PlantUML class diagram documentation:
  `https://plantuml.com/class-diagram`
- Mermaid class diagram documentation:
  `https://mermaid.js.org/syntax/classDiagram.html`
- GitHub Markdown diagram rendering documentation:
  `https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams`
- Repository domain modeling background:
  `docs/propuesta_modelado_uml_ocl_cvn.md`

## Research Summary

### Current Domain Model Inventory

The current generated domain layer is large enough that direct class diagrams over
Python code are likely to become unreadable without curation.

Observed inventory from `src/models/cvn/generated/` and
`src/models/cvn/components.py`:

- generated Python files excluding `__init__.py`: `104`
- generated domain model classes: `103`
- generated enum classes: `13`
- shared component classes: `17`
- generated domain model fields: `1487`
- generated model field count range: `1` to `48`
- average generated model fields: `14.44`

Representative large generated models include:

- `FormacionAcademicaImpartida`: `48` fields
- `ProyectosDeIDIFinanciadosEnConvocatoriasCompetitivasDeAdministracionesOEntidadesPublicasYPrivadas`:
  `35` fields
- `PublicacionesDocumentosCientificosYTecnicos`: `33` fields
- `ContratosConveniosOProyectosDeIDINoCompetitivosConAdministracionesOEntidadesPublicasOPrivadas`:
  `32` fields
- `PropiedadIndustrialEIntelectual`: `32` fields

The generated model layer is useful as an implementation and traceability source,
but it still reflects CVN item grouping and generator naming decisions. That makes
it unsuitable as the final conceptual UML source by itself.

### Pydantic Metadata Findings

Pydantic v2 model metadata can expose useful structural facts:

- class names
- field names
- field annotations
- required versus optional status
- repeated fields through `list[...]` annotations and `default_factory=list`
- referenced shared value objects, such as `EntityNameValue`, `EntityTypeValue`,
  `FlexibleDateValue`, `OfficialIdValue`, `HierarchicalCodeReference`,
  `VocabularyReference`, and other controlled-reference components
- JSON Schema `$defs` for shared component references

Pydantic metadata is not enough for the conceptual target because:

- generated classes are grouped by CVN item/module shape, not stable curriculum
  concepts
- field-level CVN trace is not emitted into the generated Python field metadata
  even though generator IR records field trace internally
- relationships between conceptual entities such as `Person`, `Curriculum`,
  `EducationalExperience`, `ProfessionalSituation`, or `Publication` cannot be
  reliably inferred from annotations alone
- controlled-reference semantics are visible only as emitted component types or
  enums, while the richer decision evidence lives upstream in normalized metadata
  and `SemanticFieldPolicy`

### Pyreverse Evaluation

Pyreverse can generate DOT class diagrams from repository Python modules and can
be useful for implementation diagnostics.

A tiny local experiment was run outside tracked repository outputs:

```text
uvx --from pylint pyreverse --output dot --project cvn_sample --output-directory /tmp/opencode src/models/cvn/generated/cvn_item_010_010_000_000.py src/models/cvn/components.py
```

Temporary outputs:

- `/tmp/opencode/classes_cvn_sample.dot`
- `/tmp/opencode/packages_cvn_sample.dot`

Observed result:

- Pyreverse emitted class records and inheritance edges.
- Shared Pydantic implementation details such as `model_config` appeared in the
  diagram.
- Generated class attributes appeared, but many component relationships were not
  promoted to clear UML associations.
- The output remained Python/package-centric rather than curriculum-domain-centric.

Conclusion:

- Pyreverse is not recommended as the final UML generation path.
- Pyreverse may remain useful as a temporary diagnostic tool for Python dependency
  or inheritance inspection.

### PlantUML Evaluation

PlantUML is a strong target for generated conceptual diagrams because it supports:

- classes, enums, abstract classes, stereotypes, and notes
- package and namespace grouping
- associations, dependencies, inheritance, composition, and aggregation
- labels and cardinalities on relations
- field-level and link-level notes
- hiding, removing, tagging, and splitting large diagrams
- text-first source files that can be versioned deterministically

PlantUML is the best fit when the repository needs expressive UML-like output for
the TFG explanation and for diagrams grouped by curriculum domain area.

Primary limitation:

- rendering requires PlantUML-compatible tooling or a viewer, although raw `.puml`
  files can remain the canonical versioned source.

### Mermaid Evaluation

Mermaid class diagrams support:

- classes and class members
- relationships and multiplicities
- namespaces
- annotations such as `<<Enumeration>>` and `<<Abstract>>`
- notes
- Markdown fenced-code rendering on GitHub

Mermaid is useful as a lightweight repository-native publication target, because
GitHub renders Mermaid diagrams directly in Markdown contexts.

Primary limitation:

- Mermaid is less expressive than PlantUML for heavily annotated, large,
  traceability-rich UML documentation.

### Custom Pydantic Introspection Evaluation

A custom extractor over generated Pydantic classes could extract a technical
model graph containing:

- generated model class
- field name
- field type
- required/optional flag
- repeated/single flag
- enum reference
- shared component reference

This can help issue `#43` bootstrap evidence, but it should not be the only source
of truth for the conceptual model. The extractor must be combined with normalized
metadata and semantic policy data to recover CVN code trace, source references,
domain-shape decisions, wrapper policies, controlled-reference families, and
semantic confidence.

### Conceptual IR Evaluation

The recommended direction is a conceptual intermediate representation before any
diagram rendering.

Issue `#43` should define an IR that represents:

- conceptual entities
- conceptual fields or attributes
- relationships and relationship cardinality
- value types
- controlled vocabularies and reference families
- required/optional and repeated/single status
- CVN code trace
- XML path trace when useful
- semantic policy decision trace
- unresolved or weakly supported cases

The IR should exclude:

- raw generated module names such as `cvn_item_050_020_010_000`
- Python inheritance details such as `BaseCvnDomainModel`
- Pydantic implementation details such as `model_config` and `Field(...)`
- raw XML wrapper mechanics except where they map to stable value objects
- one-class-per-CVN-code or one-class-per-CVN-item output when that obscures the
  curriculum concept

## Comparison Matrix

| Option | Readability | Domain agnosticism | Traceability | Automation fit | Recommendation |
| --- | --- | --- | --- | --- | --- |
| Pyreverse over generated Python | Low for final docs | Low | Low to medium | Medium | Diagnostic only |
| Custom direct Pydantic introspection | Medium | Low to medium | Medium if enriched | Medium | Auxiliary input only |
| Conceptual IR plus PlantUML | High | High | High | High | Primary path |
| Conceptual IR plus Mermaid | Medium to high | High | Medium | High | Secondary publication path |

## Final Recommendation

### Decision: Do Not Generate Final UML Directly From Python Classes

Final UML or UML-like diagrams should not be generated directly from the generated
Pydantic class layer.

Reason:

- direct Python diagrams preserve implementation shape, generated module names,
  Pydantic details, and CVN item grouping
- the TFG needs an agnostic curriculum model, not a diagram of generated Python
  files
- the information needed for good conceptual diagrams spans generated Pydantic
  code, normalized metadata, semantic policy, and CVN trace data

### Decision: Use A Conceptual IR From Issue `#43`

Issue `#43` should define and, if authorized, implement a conceptual extraction
layer. That layer should consume the existing domain generation evidence and
semantic handoff instead of re-deriving meaning from raw XML/XSD files or relying
only on Python annotations.

Recommended sources for issue `#43`:

- `NormalizationResult`
- `NormalizedCodeEntry`
- `SemanticFieldPolicy`
- `SemanticDecisionTrace`
- `DomainGenerationResult` or equivalent generator evidence when field grouping
  and emitted shape are needed
- generated Pydantic classes only as a validation or convenience source

### Decision: Use PlantUML As Primary Diagram Target

Issue `#44` should use PlantUML as the primary rendering target because it best
supports expressive class diagrams, packages, stereotypes, notes, cardinality,
and trace annotations.

Recommended output shape for issue `#44`:

- versioned `.puml` sources as canonical diagram artifacts
- diagrams grouped by curriculum domain areas, not generated Python packages
- optional rendered images only if tooling is added and documented

### Decision: Keep Mermaid As Secondary Markdown Target

Mermaid should be considered a secondary output for smaller, reader-friendly
diagrams embedded in Markdown, especially where GitHub-native rendering matters.

Mermaid should not be the only target if the project needs dense trace notes,
large package diagrams, or richer visual styling.

## Risks And Limitations

- Generated Pydantic models are too numerous and too implementation-oriented for
  direct final UML.
- Pyreverse diagrams can include Pydantic implementation details and miss useful
  conceptual associations from type annotations.
- Pydantic metadata alone does not preserve enough field-level CVN trace in the
  current generated files.
- Conceptual relationships require curation; they cannot be inferred perfectly
  from generated field annotations.
- Controlled vocabularies can overload diagrams if all values are rendered inline.
- PlantUML adds an external rendering dependency if rendered images are required.
- Mermaid is convenient in GitHub Markdown but less expressive for large,
  trace-heavy UML documentation.

## Impact On Issue `#43`

Issue `#43` should proceed with the conceptual IR approach. It should not treat
generated Python classes as the final conceptual schema. It should define explicit
records for curriculum entities, fields, relationships, vocabulary references,
cardinality, and trace data.

## Impact On Issue `#44`

Issue `#44` should render diagrams from the issue `#43` conceptual IR. It should
prefer PlantUML as the primary target and optionally generate Mermaid diagrams for
small Markdown-friendly views.

## Verification

- confirm research references are recorded
- confirm recommendation is explicit enough for issue `#43` to start
- no code implementation required unless a tiny local experiment is explicitly
  approved

## Verification Performed

- Research references are recorded in this issue document.
- Generated domain model inventory was measured from the current repository.
- A tiny local Pyreverse experiment was run under `/tmp/opencode` only; no tracked
  repository output was created.
- The recommendation is explicit: use a conceptual IR for issue `#43`; do not use
  direct generated Python diagrams as final UML.
- The recommended primary target for issue `#44` is PlantUML.
- Mermaid is recorded as a secondary Markdown-friendly target.
- No productive code implementation was added.

## Impact On Later Issues

- issue `#43` uses the chosen extraction direction
- issue `#44` uses the chosen diagram rendering target

## Status

- Status: completed
