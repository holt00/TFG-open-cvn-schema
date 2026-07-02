# Issue 43 - Define Agnostic Conceptual Model Extraction Layer

## Summary

Issue `#43` defines an intermediate representation for agnostic curriculum
concepts derived from the generated/domain Pydantic layer and CVN trace metadata.

This issue is part of epic `#41`.

## Goal

- define a conceptual model inventory that is not tied to XML serialization,
  Python implementation details, or generated module structure
- preserve traceability to CVN codes, XML paths, reference resolution, and
  semantic policy decisions
- create the source layer from which UML and JSON schema work can proceed

## Background

The current domain generator emits traceable Pydantic artifacts, but the TFG
requires a representation that describes curriculum concepts rather than CVN XML
mechanics. A conceptual IR should sit between generated Pydantic models and
diagram/schema outputs.

## Proposed Conceptual IR Contents

The IR should represent:

- conceptual entities
- attributes
- relationships
- controlled vocabularies and reference families
- required/optional status
- cardinality
- value type
- source CVN code trace
- source XML path trace when relevant
- semantic policy decision trace
- known limitations or unresolved cases

## Planned Steps

1. inspect available domain generation metadata and `cvn_trace` values
2. define dataclasses or typed records for conceptual entities, fields,
   relationships, vocabularies, and trace data
3. decide grouping rules by curriculum domain areas instead of raw XML packages
4. map representative generated Pydantic fields into the conceptual IR
5. define deterministic ordering and stable identifiers
6. document which XML/Python details must be excluded from conceptual output
7. add tests if implementation is authorized

## Accepted Execution Protocol

The user accepted the execution plan before issue `#43` implementation starts.

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

### Task `1 / 17` - Confirm Issue Scope

- Task summary:
  - confirm the boundaries of issue `#43` before implementation work starts
- Files involved:
  - `docs/roadmap/issues/issue-41-epic-agnostic-schema-json-parser.md`
  - `docs/roadmap/issues/issue-42-research-pydantic-to-uml-options.md`
  - `docs/roadmap/issues/issue-43-agnostic-conceptual-model-extraction-layer.md`
  - `docs/roadmap/issues/issue-44-generate-uml-or-uml-like-diagrams.md`
- Subtask `1.1 / 17`:
  - confirm that issue `#43` defines the conceptual IR and extraction layer only
- Subtask `1.2 / 17`:
  - confirm that UML rendering, JSON Schema generation, and parser work remain
    out of scope
- Subtask `1.3 / 17`:
  - confirm that the conceptual IR must consume issue `#42` recommendations and
    stay agnostic to XML serialization and Python implementation details
- User manual modifications needed:
  - none expected for scope confirmation
- Next step:
  - inventory the real evidence sources available from the current pipeline

### Task `2 / 17` - Inventory Real Evidence Sources

- Task summary:
  - identify which existing pipeline outputs can provide conceptual-model facts
- Files involved:
  - `src/cvn_codegen/normalization_types.py`
  - `src/cvn_codegen/semantic_policy.py`
  - `src/cvn_codegen/domain_model_types.py`
  - `src/cvn_codegen/domain_model_generator.py`
- Subtask `2.1 / 17`:
  - inspect `NormalizationResult` and `NormalizedCodeEntry` for code, manual,
    tree, reference, and structural trace evidence
- Subtask `2.2 / 17`:
  - inspect `SemanticFieldPolicy` and `SemanticDecisionTrace` for semantic policy
    decisions and diagnostics
- Subtask `2.3 / 17`:
  - inspect `DomainGenerationResult`, `DomainGenerationUnit`, `DomainFieldSpec`,
    and `DomainEnumSpec` for current generated-domain grouping and field shape
- Subtask `2.4 / 17`:
  - record that generated Pydantic classes are validation or convenience evidence,
    not the conceptual source of truth
- User manual modifications needed:
  - none expected; this task is read-only unless code implementation is later
    authorized
- Next step:
  - define the conceptual IR contract

### Task `3 / 17` - Define Conceptual IR Contract

- Task summary:
  - design stable typed records for the agnostic conceptual inventory
- Files involved if implementation is authorized:
  - `src/cvn_codegen/conceptual_model_types.py`
- Proposed records:
  - `ConceptualModelInventory`
  - `ConceptualDomainArea`
  - `ConceptualEntity`
  - `ConceptualAttribute`
  - `ConceptualRelationship`
  - `ConceptualVocabulary`
  - `ConceptualTrace`
  - `ConceptualLimitation`
- Subtask `3.1 / 17`:
  - define top-level inventory metadata, source issue, source policy, and domain
    areas
- Subtask `3.2 / 17`:
  - define conceptual entity and attribute records with stable identifiers,
    domain names, descriptions, and source trace
- Subtask `3.3 / 17`:
  - define relationship, vocabulary, and limitation records without tying them to
    UML or JSON Schema output
- Subtask `3.4 / 17`:
  - ensure the contract is deterministic, ASCII-compatible, and independent from
    generated module names
- User manual modifications needed:
  - code changes are required only if implementation is authorized; otherwise the
    user performs them manually
- Next step:
  - define the IR enum vocabulary and semantic mappings

### Task `4 / 17` - Define IR Vocabulary And Semantic Mappings

- Task summary:
  - standardize the internal vocabulary used by conceptual attributes,
    relationships, and vocabularies
- Files involved if implementation is authorized:
  - `src/cvn_codegen/conceptual_model_types.py`
  - `src/cvn_codegen/conceptual_model_extractor.py`
- Proposed enums:
  - `ConceptualValueKind`
  - `ConceptualCardinalityKind`
  - `ConceptualPresenceKind`
  - `ConceptualVocabularyKind`
  - `ConceptualRelationshipKind`
  - `ConceptualConfidence`
- Subtask `4.1 / 17`:
  - map `SemanticBaseKind` to conceptual value kinds
- Subtask `4.2 / 17`:
  - map `DomainShapeKind` and `EnumEligibility` to conceptual vocabulary kinds
- Subtask `4.3 / 17`:
  - map `PresenceKind` and `CardinalityKind` to conceptual presence and
    cardinality
- Subtask `4.4 / 17`:
  - preserve policy confidence and review-required states as conceptual evidence,
    not hidden implementation details
- User manual modifications needed:
  - code changes are required only if implementation is authorized
- Next step:
  - define which XML and Python details must be excluded from conceptual output

### Task `5 / 17` - Define Conceptual Exclusion Rules

- Task summary:
  - prevent the IR from leaking raw XML, generated Python, or implementation noise
- Files involved:
  - `docs/pipeline/conceptual_model_extraction.md` if documentation is authorized
  - `src/cvn_codegen/conceptual_model_extractor.py` if implementation is
    authorized
- Subtask `5.1 / 17`:
  - exclude generated module names such as `cvn_item_050_020_010_000` from entity
    identifiers and conceptual grouping
- Subtask `5.2 / 17`:
  - exclude Python inheritance details such as `BaseCvnDomainModel`, `Field(...)`,
    and `model_config`
- Subtask `5.3 / 17`:
  - exclude raw XML wrapper mechanics unless they map to stable value objects such
    as `FlexibleDateValue` or `OfficialIdValue`
- Subtask `5.4 / 17`:
  - avoid one conceptual class per CVN code unless a code really represents a
    reusable curriculum concept
- User manual modifications needed:
  - none expected for documentation if explicitly authorized; code changes remain
    user-owned unless implementation is authorized
- Next step:
  - define domain-area grouping rules

### Task `6 / 17` - Define Domain-Area Grouping Rules

- Task summary:
  - group conceptual output by curriculum areas instead of XML packages or Python
    modules
- Files involved:
  - `docs/propuesta_modelado_uml_ocl_cvn.md`
  - `src/cvn_codegen/conceptual_model_extractor.py` if implementation is
    authorized
- Initial areas:
  - `core`
  - `common`
  - `identity`
  - `professional_experience`
  - `education`
  - `vocabularies`
- Subtask `6.1 / 17`:
  - derive initial grouping rules from CVN code prefixes and the UML/OCL proposal
- Subtask `6.2 / 17`:
  - map `000.*` identity fields into the identity area
- Subtask `6.3 / 17`:
  - map at least one academic or professional section into `education` or
    `professional_experience`
- Subtask `6.4 / 17`:
  - record ambiguous or future grouping decisions as limitations instead of
    forcing false precision
- User manual modifications needed:
  - code changes are required only if implementation is authorized
- Next step:
  - design field-to-attribute extraction

### Task `7 / 17` - Design Field-To-Attribute Extraction

- Task summary:
  - define how normalized and semantic field evidence becomes conceptual
    attributes
- Files involved if implementation is authorized:
  - `src/cvn_codegen/conceptual_model_extractor.py`
- Subtask `7.1 / 17`:
  - define stable attribute IDs from conceptual entity ID and CVN code
- Subtask `7.2 / 17`:
  - derive attribute names from semantic Spanish-first naming policy, not Python
    field declarations
- Subtask `7.3 / 17`:
  - attach presence, cardinality, value kind, wrapper value object, and field
    confidence
- Subtask `7.4 / 17`:
  - attach `ConceptualTrace` with CVN code, XML paths, manual reference table,
    source artifact, semantic kind, serialization pattern, and applied rules
- User manual modifications needed:
  - code changes are required only if implementation is authorized
- Next step:
  - design controlled-reference and vocabulary extraction

### Task `8 / 17` - Design Controlled-Reference And Vocabulary Extraction

- Task summary:
  - represent controlled references without forcing every table into strict enums
- Files involved if implementation is authorized:
  - `src/cvn_codegen/conceptual_model_extractor.py`
- Required representative cases:
  - `CVN_SEX_A`
  - `CVN_ENTITY_TYPE`
  - `CVN_KNOW_A`
  - `ENTITY@Entity.xsd`
  - `THESAURUS@thesaurus.xsd`
  - `UNESCO_CODES`
  - `CVN_AGENCY_C`
- Subtask `8.1 / 17`:
  - map eligible strict enums to conceptual enumerations
- Subtask `8.2 / 17`:
  - map ineligible or review-required reference tables to codelist-style
    vocabularies
- Subtask `8.3 / 17`:
  - map side-package registries, thesauri, hierarchical references, unresolved
    references, and under-traced references to distinct vocabulary kinds
- Subtask `8.4 / 17`:
  - preserve enum evidence and diagnostics without rendering all vocabulary values
    inline
- User manual modifications needed:
  - code changes are required only if implementation is authorized
- Next step:
  - design conceptual relationships

### Task `9 / 17` - Design Conceptual Relationships

- Task summary:
  - represent safe conceptual associations without inventing unsupported domain
    ontology
- Files involved if implementation is authorized:
  - `src/cvn_codegen/conceptual_model_types.py`
  - `src/cvn_codegen/conceptual_model_extractor.py`
- Subtask `9.1 / 17`:
  - define relationship kinds such as composition, aggregation, association, and
    vocabulary reference
- Subtask `9.2 / 17`:
  - add only safe root relationships such as `Curriculum -> Person`,
    `Curriculum -> ProfessionalSituation`, and `Curriculum -> EducationalExperience`
    when supported by the chosen representative inventory
- Subtask `9.3 / 17`:
  - connect attributes to conceptual vocabularies through traceable vocabulary
    references
- Subtask `9.4 / 17`:
  - record uncertain relationships as conceptual limitations instead of emitting
    hard associations
- User manual modifications needed:
  - code changes are required only if implementation is authorized
- Next step:
  - implement the extractor when code work is authorized

### Task `10 / 17` - Implement Conceptual Model Extractor

- Task summary:
  - build the deterministic in-memory conceptual inventory from existing pipeline
    outputs
- Files involved if implementation is authorized:
  - `src/cvn_codegen/conceptual_model_extractor.py`
- Proposed functions:
  - `build_conceptual_model_inventory(...)`
  - `build_conceptual_trace(...)`
  - `map_policy_to_value_kind(...)`
  - `map_policy_to_vocabulary_kind(...)`
  - `group_units_by_domain_area(...)`
- Subtask `10.1 / 17`:
  - implement extraction from `DomainGenerationResult.units` and
    `DomainGenerationResult.semantic_policies`
- Subtask `10.2 / 17`:
  - build stable conceptual entities and attributes for selected domain areas
- Subtask `10.3 / 17`:
  - build conceptual vocabularies from `DomainEnumSpec` and normalized reference
    resolution metadata
- Subtask `10.4 / 17`:
  - sort all output deterministically by area ID, entity ID, attribute ID,
    relationship ID, and vocabulary ID
- User manual modifications needed:
  - yes, unless the user explicitly authorizes the agent to edit code
- Next step:
  - add a canonical inventory entry point

### Task `11 / 17` - Add Canonical Inventory Entry Point

- Task summary:
  - provide a reusable way to build the canonical conceptual inventory from the
    repository source package
- Files involved if implementation is authorized:
  - `src/cvn_codegen/conceptual_model_extractor.py`
- Subtask `11.1 / 17`:
  - reuse canonical paths from the existing domain generation workflow where
    possible
- Subtask `11.2 / 17`:
  - run normalization with auxiliary sources and XSD wrapper evidence
- Subtask `11.3 / 17`:
  - build semantic policy index, domain generation result, and conceptual inventory
    without writing generated output
- Subtask `11.4 / 17`:
  - expose a function such as `build_canonical_conceptual_model_inventory()` for
    tests and later issue `#44`
- User manual modifications needed:
  - yes, unless the user explicitly authorizes the agent to edit code
- Next step:
  - create the representative conceptual inventory coverage

### Task `12 / 17` - Create Representative Inventory Coverage

- Task summary:
  - ensure issue `#43` produces representative conceptual coverage before later
    diagram work
- Files involved if implementation is authorized:
  - `src/cvn_codegen/conceptual_model_extractor.py`
  - `tests/test_generation_pipeline_conceptual_model.py`
- Required coverage:
  - personal data / identity section
  - at least one academic or professional section
  - controlled vocabulary examples
- Subtask `12.1 / 17`:
  - include identity concepts from `000.*` fields
- Subtask `12.2 / 17`:
  - include one education or professional-experience section with multiple fields
- Subtask `12.3 / 17`:
  - include representative scalar, controlled-reference, wrapper, and repeated
    attribute cases
- Subtask `12.4 / 17`:
  - keep the representative inventory domain-oriented rather than one-to-one with
    CVN item modules
- User manual modifications needed:
  - yes, unless the user explicitly authorizes the agent to edit code
- Next step:
  - add unit tests for the conceptual IR and extractor

### Task `13 / 17` - Add Unit Tests

- Task summary:
  - verify IR contracts and mapping logic with small deterministic fixtures
- Files involved if implementation is authorized:
  - `tests/test_conceptual_model_extractor_unit.py`
- Subtask `13.1 / 17`:
  - test dataclass contracts and stable sorting
- Subtask `13.2 / 17`:
  - test scalar, date-like, decimal, boolean, controlled-reference, and wrapper
    value-kind mappings
- Subtask `13.3 / 17`:
  - test presence and cardinality mappings
- Subtask `13.4 / 17`:
  - test trace preservation for code, XML paths, source artifact, semantic kind,
    serialization pattern, applied rules, and diagnostics
- Subtask `13.5 / 17`:
  - test vocabulary kind mapping for enum, codelist, registry, thesaurus,
    hierarchical, unresolved, and under-traced references
- User manual modifications needed:
  - yes, unless the user explicitly authorizes the agent to edit tests
- Next step:
  - add integration tests over the canonical pipeline

### Task `14 / 17` - Add Canonical Pipeline Integration Tests

- Task summary:
  - verify that the conceptual inventory builds from the real canonical CVN source
    package
- Files involved if implementation is authorized:
  - `tests/test_generation_pipeline_conceptual_model.py`
  - `tests/conftest.py` only if a shared fixture is useful
- Subtask `14.1 / 17`:
  - test canonical inventory is non-empty and deterministic
- Subtask `14.2 / 17`:
  - test all conceptual attributes preserve CVN code trace
- Subtask `14.3 / 17`:
  - test identity and one academic or professional area are present
- Subtask `14.4 / 17`:
  - test representative vocabularies are present with expected conceptual kinds
- Subtask `14.5 / 17`:
  - test entity identifiers do not leak generated module names such as
    `cvn_item_*`
- User manual modifications needed:
  - yes, unless the user explicitly authorizes the agent to edit tests
- Next step:
  - document extraction rules

### Task `15 / 17` - Document Conceptual Extraction Rules

- Task summary:
  - preserve the mapping rules so issue `#44`, issue `#45`, and issue `#46` can
    consume the IR without rediscovery
- Files involved if documentation is authorized:
  - `docs/pipeline/conceptual_model_extraction.md`
- Subtask `15.1 / 17`:
  - document source-of-truth order for conceptual extraction
- Subtask `15.2 / 17`:
  - document IR contract and domain-area grouping rules
- Subtask `15.3 / 17`:
  - document XML/Python exclusion rules
- Subtask `15.4 / 17`:
  - document controlled vocabulary treatment and unresolved cases
- Subtask `15.5 / 17`:
  - document known limitations and expected consumers in issue `#44`, issue `#45`,
    and issue `#46`
- User manual modifications needed:
  - none expected if documentation changes are explicitly authorized
- Next step:
  - update persistent project documentation

### Task `16 / 17` - Update Persistent Documentation

- Task summary:
  - record issue `#43` implementation outcome and keep roadmap context aligned
- Files involved:
  - `docs/roadmap/issues/issue-43-agnostic-conceptual-model-extraction-layer.md`
  - `docs/context/current_status.md`
  - `docs/roadmap/cvn_generation_roadmap.md`
  - `docs/pipeline/known_limitations.md` only if a new limitation is found
  - `PROJECT_GUIDE.md` only if human-facing orientation or document maps change
- Subtask `16.1 / 17`:
  - add implementation summary, artifacts, deviations, and verification to issue
    `#43`
- Subtask `16.2 / 17`:
  - update current status with issue `#43` outcome
- Subtask `16.3 / 17`:
  - update roadmap status if issue `#43` is completed
- Subtask `16.4 / 17`:
  - update known limitations only if implementation finds a durable new limitation
- Subtask `16.5 / 17`:
  - update `PROJECT_GUIDE.md` only if repository orientation changes
- User manual modifications needed:
  - none expected if documentation changes are explicitly authorized
- Next step:
  - verify the issue closure criteria

### Task `17 / 17` - Verify Issue Closure

- Task summary:
  - prove issue `#43` is ready for issue `#44` to consume
- Files and commands involved if implementation is authorized:
  - `uv run pytest -n auto tests/test_conceptual_model_extractor_unit.py tests/test_generation_pipeline_conceptual_model.py`
  - `uv run pytest -n auto tests`
- Subtask `17.1 / 17`:
  - run targeted conceptual-model tests
- Subtask `17.2 / 17`:
  - run the full repository test suite
- Subtask `17.3 / 17`:
  - manually review that concepts are domain-oriented, not XML- or Python-oriented
- Subtask `17.4 / 17`:
  - verify trace fields survive for representative entries
- Subtask `17.5 / 17`:
  - confirm issue `#44` can render diagrams from the IR without re-reading raw
    generated Python classes as the final conceptual schema
- User manual modifications needed:
  - none expected after verification; any required manual changes should have been
    recorded earlier
- Next step:
  - proceed to issue `#44` only after the user accepts issue `#43` closure

## Expected Output

- conceptual IR contract under `src/cvn_codegen/` if implementation is approved
- documentation of mapping rules from generated/domain metadata into the IR
- representative inventory for at least personal data and one academic/research
  section

## Implementation Summary

- Conceptual IR records are implemented in:
  - `src/cvn_codegen/conceptual_model_types.py`
- Conceptual extraction logic is implemented in:
  - `src/cvn_codegen/conceptual_model_extractor.py`
- The extractor consumes:
  - `DomainGenerationResult`
  - `NormalizedCodeEntry`
  - `SemanticFieldPolicy`
  - `SemanticDecisionTrace`
- The extractor exposes:
  - `build_conceptual_model_inventory(...)`
  - `build_canonical_conceptual_model_inventory()`
- The conceptual inventory includes:
  - stable domain areas
  - conceptual entities
  - conceptual attributes
  - conservative relationships
  - conceptual vocabularies
  - trace records
  - extraction limitations

## Implementation Adjustments

- A stable `core.curriculum` root entity was added so later diagram and JSON work
  has a conceptual root without depending on generated Python modules.
- `__no_cvn_item__` technical groups are remapped by field-code prefix when all
  contained fields belong to a known conceptual area. This is needed for identity
  fields that are not grouped under a regular CVN item in the tree model.
- Conceptual relationships remain conservative. The extractor records a limitation
  instead of inferring a complete domain ontology from generated field annotations.

## Artifacts Created

- `src/cvn_codegen/conceptual_model_types.py`
- `src/cvn_codegen/conceptual_model_extractor.py`
- `tests/test_conceptual_model_extractor_unit.py`
- `tests/test_generation_pipeline_conceptual_model.py`
- `docs/pipeline/conceptual_model_extraction.md`

## Verification Performed

- Targeted conceptual-model verification passed with:
  `uv run pytest -n auto tests/test_conceptual_model_extractor_unit.py tests/test_generation_pipeline_conceptual_model.py`
- Result:
  `13 passed in 74.28s (0:01:14)`
- Full-suite verification passed with:
  `uv run pytest -n auto tests`
- Result:
  `307 passed in 318.93s (0:05:18)`

## Verification

- tests for deterministic extraction if code is implemented
- manual review that generated concepts are domain-oriented, not XML-oriented
- trace fields preserved for representative entries

## Impact On Later Issues

- issue `#44` renders UML from this IR
- issue `#45` and issue `#46` can use this IR to guide JSON shape decisions

## Status

- Status: completed
