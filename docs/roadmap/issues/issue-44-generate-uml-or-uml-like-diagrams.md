# Issue 44 - Generate UML Or UML-Like Diagrams

## Summary

Issue `#44` generates UML or UML-like diagrams from the agnostic conceptual model
defined in issue `#43`.

This issue is part of epic `#41`.

## Goal

- generate readable diagrams for the agnostic curriculum model
- group diagrams by curriculum domain areas
- preserve enough traceability to connect diagram elements back to CVN evidence

## Background

Direct diagrams from generated Python classes may be too large and too tied to
implementation structure. This issue should consume the conceptual IR from issue
`#43` unless issue `#42` proves direct code diagrams are suitable.

## Candidate Outputs

- PlantUML class diagrams
- Mermaid class diagrams
- Markdown documentation embedding diagram source
- rendered images only if tooling is added and documented

## Planned Steps

1. select diagram target based on issue `#42` recommendation
2. define diagram grouping strategy by domain area
3. render conceptual entities and attributes
4. render relationships and cardinalities
5. render controlled vocabularies and reference families without overloading
   diagrams
6. include trace notes or stereotypes where useful
7. add generation command and tests if implementation is authorized
8. document how to regenerate diagrams

## Accepted Execution Protocol

The user accepted the execution plan before issue `#44` implementation starts.

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

### Task `1 / 15` - Confirm Issue Scope

- Task summary:
  - confirm issue `#44` boundaries before implementation work starts
- Files involved:
  - `docs/roadmap/issues/issue-42-research-pydantic-to-uml-options.md`
  - `docs/roadmap/issues/issue-43-agnostic-conceptual-model-extraction-layer.md`
  - `docs/roadmap/issues/issue-44-generate-uml-or-uml-like-diagrams.md`
  - `docs/pipeline/conceptual_model_extraction.md`
- Subtask `1.1 / 15`:
  - confirm PlantUML is the primary issue `#44` target from issue `#42`
- Subtask `1.2 / 15`:
  - confirm Mermaid is optional and secondary, not required for issue closure unless
    explicitly authorized later
- Subtask `1.3 / 15`:
  - confirm diagrams must consume `ConceptualModelInventory` from issue `#43`
- Subtask `1.4 / 15`:
  - confirm direct generated-Python, generated-domain, raw XML, and raw XSD diagrams
    are out of scope for final documentation
- User manual modifications needed:
  - none expected for scope confirmation
- Next step:
  - define the output artifact layout

### Task `2 / 15` - Define Diagram Output Layout

- Task summary:
  - choose deterministic locations and names for canonical diagram artifacts
- Files involved if implementation is authorized:
  - `docs/diagrams/`
  - `docs/diagrams/open_cvn_conceptual_overview.puml`
  - `docs/diagrams/open_cvn_identity.puml`
  - `docs/diagrams/open_cvn_professional_experience.puml`
  - `docs/diagrams/open_cvn_education.puml`
  - `docs/diagrams/open_cvn_research.puml`
  - `docs/diagrams/open_cvn_achievements.puml`
  - optional Markdown index under `docs/`
- Subtask `2.1 / 15`:
  - define `.puml` sources as the canonical versioned output
- Subtask `2.2 / 15`:
  - define one overview diagram plus one diagram per conceptual domain area
- Subtask `2.3 / 15`:
  - decide whether to create a vocabulary-focused diagram only if area diagrams
    become overloaded
- Subtask `2.4 / 15`:
  - record that rendered image files are optional and only added if tooling is
    documented
- User manual modifications needed:
  - documentation output directories and files require modification only if
    implementation is authorized
- Next step:
  - define the renderer input and output contract

### Task `3 / 15` - Define Diagram Rendering Contract

- Task summary:
  - specify exactly how the renderer consumes the conceptual inventory and emits
    PlantUML text
- Files involved if implementation is authorized:
  - `src/cvn_codegen/conceptual_model_diagrams.py`
  - `src/cvn_codegen/conceptual_model_types.py`
  - `src/cvn_codegen/conceptual_model_extractor.py`
- Subtask `3.1 / 15`:
  - define `ConceptualModelInventory` as the only semantic input to the renderer
- Subtask `3.2 / 15`:
  - define PlantUML text as deterministic renderer output
- Subtask `3.3 / 15`:
  - define renderable inventory elements: entities, attributes, relationships,
    vocabularies, traces, and limitations
- Subtask `3.4 / 15`:
  - define non-goals: full ontology inference, raw XML diagrams, raw Python class
    diagrams, and mandatory rendered image generation
- User manual modifications needed:
  - code changes are required only if implementation is authorized
- Next step:
  - define domain grouping and diagram taxonomy

### Task `4 / 15` - Define Domain Grouping And Diagram Taxonomy

- Task summary:
  - map conceptual domain areas into readable diagram packages and files
- Files involved:
  - `docs/pipeline/conceptual_model_extraction.md`
  - `docs/propuesta_modelado_uml_ocl_cvn.md`
  - `src/cvn_codegen/conceptual_model_diagrams.py` if implementation is authorized
- Subtask `4.1 / 15`:
  - use existing conceptual areas: `core`, `identity`,
    `professional_experience`, `education`, `research`, and `achievements`
- Subtask `4.2 / 15`:
  - define overview diagram around `core.curriculum` and high-level domain links
- Subtask `4.3 / 15`:
  - define detailed diagrams by domain area rather than XML package or generated
    module
- Subtask `4.4 / 15`:
  - define fallback behavior for ambiguous or future domain areas without forcing
    false precision
- User manual modifications needed:
  - code changes are required only if implementation is authorized
- Next step:
  - define entity and attribute rendering rules

### Task `5 / 15` - Render Conceptual Entities And Attributes

- Task summary:
  - define and implement how conceptual entities and attributes appear in PlantUML
- Files involved if implementation is authorized:
  - `src/cvn_codegen/conceptual_model_diagrams.py`
  - `tests/test_conceptual_model_diagrams_unit.py`
- Subtask `5.1 / 15`:
  - render each `ConceptualEntity` as a PlantUML class using its conceptual name,
    not generated module names
- Subtask `5.2 / 15`:
  - render each `ConceptualAttribute` with normalized name and conceptual value
    kind
- Subtask `5.3 / 15`:
  - render required or optional status and single or repeated cardinality in a
    compact readable form
- Subtask `5.4 / 15`:
  - include wrapper value object information only when it represents stable domain
    meaning
- Subtask `5.5 / 15`:
  - ensure raw XML paths and Pydantic implementation details do not appear in class
    bodies
- User manual modifications needed:
  - code and test changes are required only if implementation is authorized
- Next step:
  - define relationship rendering rules

### Task `6 / 15` - Render Relationships And Cardinalities

- Task summary:
  - render only conservative relationships supported by the conceptual inventory
- Files involved if implementation is authorized:
  - `src/cvn_codegen/conceptual_model_diagrams.py`
  - `tests/test_conceptual_model_diagrams_unit.py`
- Subtask `6.1 / 15`:
  - render explicit conceptual relationships with source and target classes
- Subtask `6.2 / 15`:
  - render relationship cardinality labels when present in the IR
- Subtask `6.3 / 15`:
  - render safe root links from `Curriculum` to representative concepts when
    already present in the conceptual inventory
- Subtask `6.4 / 15`:
  - avoid inferring dense UML associations from generated field annotations alone
- User manual modifications needed:
  - code and test changes are required only if implementation is authorized
- Next step:
  - define controlled vocabulary rendering rules

### Task `7 / 15` - Render Controlled Vocabularies And Reference Families

- Task summary:
  - preserve vocabulary semantics without making diagrams unreadable
- Files involved if implementation is authorized:
  - `src/cvn_codegen/conceptual_model_diagrams.py`
  - `tests/test_conceptual_model_diagrams_unit.py`
- Subtask `7.1 / 15`:
  - render compact strict enum vocabularies as UML enums when values are safe to
    inline
- Subtask `7.2 / 15`:
  - render large or open-world vocabularies as referenced stereotyped classes or
    notes
- Subtask `7.3 / 15`:
  - distinguish enumeration, code list, subtype-backed code list, registry,
    thesaurus, hierarchical code list, unresolved reference, and under-traced
    families
- Subtask `7.4 / 15`:
  - add readable links or notes from attributes to vocabularies without flooding
    the diagrams
- User manual modifications needed:
  - code and test changes are required only if implementation is authorized
- Next step:
  - define traceability rendering rules

### Task `8 / 15` - Render Traceability Notes

- Task summary:
  - preserve useful CVN evidence while keeping diagrams readable
- Files involved if implementation is authorized:
  - `src/cvn_codegen/conceptual_model_diagrams.py`
  - `tests/test_conceptual_model_diagrams_unit.py`
- Subtask `8.1 / 15`:
  - include conceptual IDs and representative CVN evidence as PlantUML notes or
    stereotypes
- Subtask `8.2 / 15`:
  - include attribute-level CVN code trace where it improves reviewability
- Subtask `8.3 / 15`:
  - include vocabulary source identifiers for controlled reference families
- Subtask `8.4 / 15`:
  - keep raw XML paths out of the main diagram body unless they are deliberately
    shown as trace notes
- User manual modifications needed:
  - code and test changes are required only if implementation is authorized
- Next step:
  - enforce deterministic output

### Task `9 / 15` - Enforce Deterministic Rendering

- Task summary:
  - make generated diagram files reproducible across repeated runs
- Files involved if implementation is authorized:
  - `src/cvn_codegen/conceptual_model_diagrams.py`
  - `tests/test_conceptual_model_diagrams_unit.py`
  - `tests/test_generation_pipeline_conceptual_diagrams.py`
- Subtask `9.1 / 15`:
  - sort domain areas, entities, attributes, relationships, and vocabularies by
    stable identifiers
- Subtask `9.2 / 15`:
  - define stable PlantUML aliases for class names that require escaping or
    normalization
- Subtask `9.3 / 15`:
  - keep output ASCII-compatible unless existing source labels require otherwise
- Subtask `9.4 / 15`:
  - verify two consecutive renders of the same inventory produce identical text
- User manual modifications needed:
  - code and test changes are required only if implementation is authorized
- Next step:
  - add the generation command

### Task `10 / 15` - Add Canonical Diagram Generation Command

- Task summary:
  - provide a documented way to regenerate canonical diagram sources
- Files involved if implementation is authorized:
  - `src/cvn_codegen/conceptual_model_diagrams.py`
  - possibly `src/cvn_codegen/diagram_generator.py` or a module-level CLI entrypoint
  - `docs/development/regeneration_workflow.md`
- Subtask `10.1 / 15`:
  - build the canonical conceptual inventory through the issue `#43` canonical
    entrypoint
- Subtask `10.2 / 15`:
  - write all canonical `.puml` files to the selected output directory
- Subtask `10.3 / 15`:
  - report clear errors when upstream canonical source inputs are unavailable
- Subtask `10.4 / 15`:
  - document the exact command for contributors
- User manual modifications needed:
  - code changes are required only if implementation is authorized; documentation
    changes may be performed when explicitly requested
- Next step:
  - add targeted unit tests

### Task `11 / 15` - Add Unit And Golden Tests

- Task summary:
  - prove individual rendering rules and stable text output on small fixtures
- Files involved if implementation is authorized:
  - `tests/test_conceptual_model_diagrams_unit.py`
- Subtask `11.1 / 15`:
  - test entity and attribute rendering
- Subtask `11.2 / 15`:
  - test relationship and cardinality rendering
- Subtask `11.3 / 15`:
  - test vocabulary stereotype and trace note rendering
- Subtask `11.4 / 15`:
  - test deterministic ordering and absence of generated implementation names
- Subtask `11.5 / 15`:
  - keep expected PlantUML snippets focused enough to avoid brittle full-file
    snapshots where not needed
- User manual modifications needed:
  - test changes are required only if implementation is authorized
- Next step:
  - add canonical pipeline tests

### Task `12 / 15` - Add Canonical Pipeline Tests

- Task summary:
  - verify issue `#44` works against the canonical conceptual inventory from issue
    `#43`
- Files involved if implementation is authorized:
  - `tests/test_generation_pipeline_conceptual_diagrams.py`
  - `docs/diagrams/*.puml` if generated outputs are committed
- Subtask `12.1 / 15`:
  - build the canonical conceptual inventory
- Subtask `12.2 / 15`:
  - generate canonical PlantUML diagram text
- Subtask `12.3 / 15`:
  - verify representative domain areas and root `Curriculum` appear
- Subtask `12.4 / 15`:
  - verify generated Python names, Pydantic implementation details, and raw XML
    structure do not define the diagrams
- Subtask `12.5 / 15`:
  - verify traceability evidence remains available in representative diagram output
- User manual modifications needed:
  - test and generated documentation-output changes are required only if
    implementation is authorized
- Next step:
  - document the regeneration workflow and manual review checklist

### Task `13 / 15` - Document Diagram Regeneration And Review

- Task summary:
  - explain how contributors regenerate and evaluate the diagrams
- Files involved:
  - `docs/development/regeneration_workflow.md`
  - optional diagram overview documentation under `docs/`
  - `docs/roadmap/issues/issue-44-generate-uml-or-uml-like-diagrams.md`
- Subtask `13.1 / 15`:
  - add the exact generation command and expected output paths
- Subtask `13.2 / 15`:
  - document that `.puml` files are canonical and rendered images are optional
- Subtask `13.3 / 15`:
  - add a manual readability review checklist
- Subtask `13.4 / 15`:
  - document the PlantUML-first target and Mermaid-secondary decision
- User manual modifications needed:
  - documentation changes may be performed when explicitly requested
- Next step:
  - update persistent issue and project status documents

### Task `14 / 15` - Update Persistent Documentation

- Task summary:
  - close issue `#44` in the repository documentation once implementation is
    complete
- Files involved:
  - `docs/roadmap/issues/issue-44-generate-uml-or-uml-like-diagrams.md`
  - `docs/context/current_status.md`
  - `docs/roadmap/cvn_generation_roadmap.md`
  - `docs/pipeline/known_limitations.md` if a new limitation is found
  - `PROJECT_GUIDE.md` only if the human-facing document map or orientation changes
- Subtask `14.1 / 15`:
  - record implementation summary and generated artifacts in issue `#44`
- Subtask `14.2 / 15`:
  - record deviations from this accepted plan, if any
- Subtask `14.3 / 15`:
  - update current status and roadmap status after verification
- Subtask `14.4 / 15`:
  - update known limitations only for durable limitations discovered during the
    work
- Subtask `14.5 / 15`:
  - update `PROJECT_GUIDE.md` only if contributor orientation changes
- User manual modifications needed:
  - documentation changes may be performed when explicitly requested
- Next step:
  - run final verification and closure checks

### Task `15 / 15` - Verify Issue Closure

- Task summary:
  - prove issue `#44` is complete and ready to support later JSON-schema work
- Files and commands involved if implementation is authorized:
  - targeted diagram tests, for example
    `uv run pytest -n auto tests/test_conceptual_model_diagrams_unit.py tests/test_generation_pipeline_conceptual_diagrams.py`
  - full suite: `uv run pytest -n auto tests`
  - generated diagram files under the selected output directory
- Subtask `15.1 / 15`:
  - run targeted diagram-generation tests
- Subtask `15.2 / 15`:
  - run full repository verification
- Subtask `15.3 / 15`:
  - regenerate diagrams twice or otherwise verify deterministic output
- Subtask `15.4 / 15`:
  - manually review representative diagrams for readability
- Subtask `15.5 / 15`:
  - verify diagrams do not mirror raw XML structure or generated Python classes as
    final domain concepts
- Subtask `15.6 / 15`:
  - verify traceability back to CVN source identifiers remains available
- User manual modifications needed:
  - none expected after verification; any required manual changes should have been
    recorded earlier
- Next step:
  - proceed to issue `#45` only after the user accepts issue `#44` closure

## Expected Output

- generated or maintained diagram sources under `docs/` or a dedicated diagram
  output directory
- contributor documentation explaining diagram generation
- deterministic output when generated by code

## Implementation Summary

- PlantUML diagram rendering is implemented in:
  - `src/cvn_codegen/conceptual_model_diagrams.py`
- The renderer consumes:
  - `ConceptualModelInventory`
  - `ConceptualDomainArea`
  - `ConceptualEntity`
  - `ConceptualAttribute`
  - `ConceptualRelationship`
  - `ConceptualVocabulary`
  - `ConceptualTrace`
- The renderer exposes:
  - `render_conceptual_model_diagrams(...)`
  - `write_conceptual_model_diagrams(...)`
  - a CLI entrypoint through `python -m cvn_codegen.conceptual_model_diagrams`
- Canonical generated PlantUML sources are stored under:
  - `docs/diagrams/`
- Diagram regeneration and review guidance is documented in:
  - `docs/diagrams/README.md`
  - `docs/development/regeneration_workflow.md`
- Optional rendered PNG review artifacts can be produced locally with PlantUML;
  `.puml` files remain the canonical output.

## Implementation Objective

The implementation creates reproducible UML-like documentation from the issue
`#43` conceptual inventory. Its purpose is to make the agnostic Open CVN model
reviewable without rendering raw XML structures, generated Python modules, or
Pydantic implementation details as the conceptual domain.

## Change Rationale

- Issue `#42` selected PlantUML as the primary diagram target and kept Mermaid as
  optional secondary output.
- Issue `#43` already provides the conceptual source of truth through
  `ConceptualModelInventory`.
- Generating diagrams from the conceptual IR preserves CVN traceability while
  avoiding direct Python or XML class diagrams.

## Implementation Adjustments

- Mermaid output was not implemented in this issue. The accepted plan treated it
  as optional, and PlantUML is enough to satisfy the primary issue goal.
- A fallback `open_cvn_other.puml` diagram is generated because the canonical
  conceptual inventory contains conservative fallback concepts not yet assigned
  to a more specific area.
- Readable and reference views are generated together. Readable views optimize for
  navigation and presentation; reference views preserve fuller attribute,
  vocabulary, and trace detail.
- Large areas such as education, research, and fallback `other` concepts are split
  into readable section subdiagrams to avoid unreadable single-canvas outputs.
- Reference views for education, research, fallback `other`, and vocabulary-heavy
  professional experience are emitted as compact index diagrams plus split
  detailed reference section files.
- When one split reference section is still too large for a single canvas, the
  renderer emits a second-level subsection index plus `..._part_XX_reference`
  detail files.
- Reference overview and detailed reference layouts now use top-to-bottom stacking
  directives plus local `controlled references` notes per entity, avoiding long
  entity-to-vocabulary edges that can appear detached or push targets outside the
  rendered PNG frame.
- Detailed reference chunks intentionally do not render a global `Referenced
  Vocabularies` package; vocabulary membership is colocated with each entity for
  visual reviewability.
- Area diagrams declare related external entities when conservative cross-area
  relationships are rendered, so links such as `Curriculum` to `Person` remain
  understandable inside per-area diagrams.
- Technical placeholder source groups such as `__no_cvn_item__` are intentionally
  omitted from diagram notes to avoid leaking implementation grouping into the
  conceptual documentation.

## Artifacts Created

- `src/cvn_codegen/conceptual_model_diagrams.py`
- `tests/test_conceptual_model_diagrams_unit.py`
- `tests/test_generation_pipeline_conceptual_diagrams.py`
- `docs/diagrams/README.md`
- `docs/diagrams/open_cvn_conceptual_overview.puml`
- `docs/diagrams/open_cvn_achievements.puml`
- `docs/diagrams/open_cvn_core.puml`
- `docs/diagrams/open_cvn_education.puml`
- `docs/diagrams/open_cvn_education_020.puml`
- `docs/diagrams/open_cvn_education_030.puml`
- `docs/diagrams/open_cvn_identity.puml`
- `docs/diagrams/open_cvn_other.puml`
- `docs/diagrams/open_cvn_other_040.puml`
- `docs/diagrams/open_cvn_other_no_tree.puml`
- `docs/diagrams/open_cvn_professional_experience.puml`
- `docs/diagrams/open_cvn_professional_experience_010_010_000_000_reference.puml`
- `docs/diagrams/open_cvn_professional_experience_010_020_000_000_reference.puml`
- `docs/diagrams/open_cvn_professional_experience_010_040_000_000_reference.puml`
- `docs/diagrams/open_cvn_research.puml`
- `docs/diagrams/open_cvn_research_050.puml`
- `docs/diagrams/open_cvn_research_060.puml`
- `docs/diagrams/open_cvn_conceptual_overview_reference.puml`
- `docs/diagrams/open_cvn_achievements_reference.puml`
- `docs/diagrams/open_cvn_core_reference.puml`
- `docs/diagrams/open_cvn_education_reference.puml`
- `docs/diagrams/open_cvn_identity_reference.puml`
- `docs/diagrams/open_cvn_other_reference.puml`
- `docs/diagrams/open_cvn_professional_experience_reference.puml`
- `docs/diagrams/open_cvn_research_reference.puml`
- plus deterministic split section and part files under `docs/diagrams/`, such as
  `open_cvn_education_020_part_01_reference.puml` and
  `open_cvn_research_060_part_04_reference.puml`

## Findings

- The conceptual inventory is sufficient to render domain-area diagrams without
  re-reading raw XML, XSD, or generated Python classes.
- The overview diagram is readable as a package-level conceptual map.
- The identity and professional-experience readable views are compact enough to
  inspect directly without vocabulary fan-out dominating the canvas.
- Large areas remain broad at the reference level, but readable split subdiagrams
  are substantially easier to inspect than single-canvas full-detail outputs.
- Vocabulary membership is preserved in local entity notes rather than global
  vocabulary nodes in detailed reference chunks, which prevents dangling-looking
  dependency lines in rendered PNGs.

## Known Limitations

- Relationship rendering remains conservative because the conceptual inventory
  does not claim to be a complete ontology.
- Reference diagrams for large areas can still be long even after conceptual
  grouping.
- Rendered images are not generated or versioned by default; `.puml` files remain
  the canonical artifacts. Local PNGs are useful for review but are derived from
  the `.puml` sources.
- Mermaid remains a future optional publication target.

## Verification

- generated diagrams are reproducible
- diagrams are readable for representative sections
- diagrams do not mirror raw XML structure as domain classes
- traceability back to CVN source identifiers remains available

## Verification Performed

- Targeted diagram-generation verification passed with:
  `uv run pytest -n auto tests/test_conceptual_model_diagrams_unit.py tests/test_generation_pipeline_conceptual_diagrams.py`
- Targeted verification result:
  `6 passed in 63.21s (0:01:03)`
- Full-suite verification passed with:
  `uv run pytest -n auto tests`
- Full-suite verification result:
  `313 passed in 715.42s (0:11:55)`
- Deterministic regeneration was verified by comparing SHA-256 checksums before
  and after rerunning:
  `uv run python -m cvn_codegen.conceptual_model_diagrams --output-dir docs/diagrams`
- Representative diagram inspection covered:
  - overview package grouping
  - identity class attributes and vocabulary references
  - research-area verbosity
  - education and research reference chunks that previously exposed detached or
    clipped vocabulary dependency lines
  - absence of generated implementation names in `.puml` output
  - CVN code trace presence in attributes and notes

## Impact On Later Issues

- supports TFG explanation of agnostic model
- informs JSON schema shape in issue `#46`

## Status

- Status: completed
