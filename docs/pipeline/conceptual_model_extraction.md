# Conceptual Model Extraction

## Purpose

This document describes the issue `#43` conceptual extraction layer. The layer
builds an agnostic curriculum inventory from the existing normalized metadata,
semantic policy, and domain generation IR.

It is not a UML renderer, JSON Schema generator, or parser. Those outputs consume
the conceptual inventory in later issues.

## Why This Layer Exists

The previous pipeline stages already generate domain-oriented Pydantic artifacts,
but those artifacts are still implementation products. They preserve CVN trace and
validation behavior, but they are not the final agnostic curriculum schema.

Issue `#43` adds a conceptual extraction layer so the project can move from
generated Python models toward a reusable Open CVN model. The layer separates:

- curriculum concepts from generated Python modules
- domain attributes from raw CVN XML paths
- controlled vocabularies from low-level serialization details
- traceability evidence from final diagram or JSON representation choices

The objective is to create a stable source inventory for UML, JSON Schema, and the
future canonical Open CVN JSON format without forcing those outputs to inspect raw
XML/XSD files or generated Pydantic classes directly.

## Changes Introduced By Issue `#43`

Issue `#43` introduced these repository changes:

- `src/cvn_codegen/conceptual_model_types.py` defines the conceptual IR contract
- `src/cvn_codegen/conceptual_model_extractor.py` builds the conceptual inventory
  from existing pipeline evidence
- `tests/test_conceptual_model_extractor_unit.py` verifies mapping helpers,
  trace preservation, vocabulary classification, deterministic IDs, and entity
  extraction on small fixtures
- `tests/test_generation_pipeline_conceptual_model.py` verifies the conceptual
  inventory against the canonical source package
- this document records the extraction rules and the expected direction for later
  roadmap issues

The new code is hand-maintained pipeline logic. It belongs under
`src/cvn_codegen/`. It does not modify `src/generated/` or
`src/models/cvn/generated/`.

## Data Flow

The implemented data flow is:

```text
SpecificationManual.xml + CVNTreeModel.xml + auxiliary sources + XSD wrapper evidence
-> NormalizationResult
-> SemanticFieldPolicy
-> DomainGenerationResult
-> ConceptualModelInventory
```

The conceptual extractor starts after the semantic and domain-generation handoff.
It reuses decisions already made by earlier issues rather than duplicating them.

This means:

- normalization owns CVN source alignment and reference resolution
- semantic policy owns type, naming, controlled-reference, wrapper, and
  cardinality decisions
- domain generation IR owns the already-resolved field grouping used by generated
  Pydantic models
- conceptual extraction owns the agnostic inventory consumed by documentation and
  schema-design work

## Source Order

Conceptual extraction uses this source order:

1. `NormalizationResult` and `NormalizedCodeEntry` for CVN codes, manual fields,
   tree paths, auxiliary reference resolution, and structural wrapper evidence
2. `SemanticFieldPolicy` and `SemanticDecisionTrace` for domain-shape decisions,
   presence, cardinality, confidence, applied rules, and diagnostics
3. `DomainGenerationResult`, `DomainGenerationUnit`, `DomainFieldSpec`, and
   `DomainEnumSpec` for the already-resolved generated-domain grouping and field
   type handoff
4. generated Pydantic classes only as validation or convenience evidence, not as
   the conceptual source of truth

The extractor must not re-derive semantic meaning from raw XML, raw XSD, or
generated structural bindings when the existing pipeline already exposes typed
evidence.

## IR Contract

The conceptual IR is implemented under `src/cvn_codegen/` with these records:

- `ConceptualModelInventory`: top-level inventory consumed by later issues
- `ConceptualDomainArea`: group of related curriculum concepts
- `ConceptualEntity`: domain-facing curriculum concept
- `ConceptualAttribute`: field or attribute belonging to a concept
- `ConceptualRelationship`: conservative link between conceptual elements
- `ConceptualVocabulary`: enum, codelist, registry, thesaurus, or unresolved
  reference family
- `ConceptualTrace`: CVN code, XML path, source, reference, and semantic-policy
  trace data
- `ConceptualLimitation`: unresolved or deliberately conservative extraction
  decision

All records are deterministic and independent from final rendering targets.

## Conceptual Inventory Contents

`ConceptualModelInventory` currently records:

- inventory metadata: stable inventory ID, source issue, policy name, and policy
  version
- domain areas: `core`, `identity`, `professional_experience`, `education`,
  `research`, `achievements`, and fallback areas when needed
- conceptual entities: stable domain concepts such as `Curriculum`, `Person`, and
  `ProfessionalSituation`
- conceptual attributes: field names, source labels, value kinds, presence,
  cardinality, wrapper evidence, vocabulary links, confidence, and trace data
- conservative relationships: root links only when current evidence supports them
- conceptual vocabularies: enum, codelist, registry, thesaurus, hierarchical,
  subtype-backed, unresolved, and under-traced reference families
- limitations: explicit records for conservative or unresolved decisions

The inventory is in memory. Issue `#43` does not create a generated serialized
artifact. Later issues may decide whether to render `.puml`, Markdown, JSON, or
other outputs from this inventory.

## Domain Grouping

The first implemented grouping strategy is intentionally conservative:

- `000.*` fields map to `identity`
- `010.*` fields map to `professional_experience`
- `020.*` and `030.*` fields map to `education`
- `050.*` and `060.*` fields map to `research`
- `070.*` and `080.*` fields map to `achievements`
- a stable `core.curriculum` root entity is added for later diagram and JSON work
- technical placeholder groups such as `__no_cvn_item__` are remapped by their
  field codes when possible

This keeps the output domain-oriented without pretending that all conceptual
relationships are fully inferred.

## Stable Identifiers

The extractor generates stable IDs for areas, entities, attributes, relationships,
and vocabularies.

Identifier rules:

- use lowercase ASCII tokens
- remove punctuation and implementation-only separators
- include CVN group or code evidence where needed for uniqueness
- avoid generated Python module names as conceptual identifiers
- keep source CVN codes inside `ConceptualTrace`, not as the primary domain name

Example distinction:

- conceptual entity ID: `identity.person`
- source trace code: `000.010.000.020`
- excluded implementation detail: `cvn_item_*`

This distinction lets later diagrams or JSON schemas keep readable conceptual
names while preserving formal traceability back to CVN.

## Exclusion Rules

Conceptual output excludes these implementation details:

- generated module names such as `cvn_item_050_020_010_000`
- Pydantic implementation details such as `Field(...)`, `model_config`, and
  `BaseCvnDomainModel`
- raw XML wrapper mechanics, except where wrapper evidence maps to stable value
  objects such as `FlexibleDateValue` or `OfficialIdValue`
- one conceptual class per CVN code when a code is only an attribute

The output preserves XML paths as trace data only. XML paths do not define the
domain grouping.

## Controlled Vocabularies

Controlled references are represented as conceptual vocabularies, not always as
strict enums.

Representative mappings are:

- eligible strict enum candidates become `enumeration`, for example `CVN_SEX_A`
- ineligible or review-required compact reference tables become `code_list`, for
  example `CVN_ENTITY_TYPE`
- subtype-backed references become `subtype_backed_code_list`, for example
  `CVN_KNOW_A`
- side-package registries become `registry`, for example `ENTITY@Entity.xsd`
- side-package thesauri become `thesaurus`, for example
  `THESAURUS@thesaurus.xsd`
- hierarchical thematic references become `hierarchical_code_list`, for example
  `UNESCO_CODES`
- unresolved manual references become `unresolved_reference`, for example
  `CVN_AGENCY_C`

Enum values are only carried inline when the semantic policy and enum evidence
allow a strict generated enum. Larger or open-world vocabularies remain referenced
by source evidence.

## Relationships

The extractor emits only conservative relationships that are safe enough for the
current evidence. It adds a root `Curriculum` concept and links known
representative concepts such as `Person` and `ProfessionalSituation` when present.

Richer domain associations require curation in later conceptual modeling work.
The current IR records that limitation explicitly instead of inventing hard
relationships from generated field annotations alone.

## Current Limitations

The implemented layer is intentionally conservative.

Current limitations:

- relationships are not a complete ontology of the CVN domain
- domain-area grouping is based on current CVN prefix rules and may need curation
  as the conceptual model matures
- generated-domain grouping is useful evidence, but not always the final
  conceptual grouping
- fields without regular CVN item grouping require code-prefix fallback rules
- large or open-world controlled vocabularies are referenced instead of expanded
  inline

These limits are deliberate. They prevent issue `#43` from turning generated code
or XML structure into a false conceptual model.

## Verification

Issue `#43` verification covered two levels:

- targeted conceptual tests:
  `uv run pytest -n auto tests/test_conceptual_model_extractor_unit.py tests/test_generation_pipeline_conceptual_model.py`
- full repository regression suite:
  `uv run pytest -n auto tests`

Verified properties include:

- deterministic conceptual inventory creation
- CVN code trace preservation for attributes
- identity and representative curriculum areas are present
- generated module names are not used as conceptual entity IDs
- representative vocabulary families are classified correctly
- full repository behavior still passes after adding the conceptual layer

## Consumers

Later issues should consume this IR as follows:

- issue `#44`: render PlantUML or Mermaid diagrams from the conceptual inventory
- issue `#45`: use the inventory to guide JSON Schema shape decisions
- issue `#46`: use the inventory to define the canonical Open CVN JSON structure

Consumers should not treat generated Python classes or raw CVN XML paths as the
final conceptual schema.

## Direction After Issue `#43`

The project direction after issue `#43` is:

1. issue `#44` renders readable UML or UML-like diagrams from
   `ConceptualModelInventory`, preferably PlantUML first
2. issue `#45` uses the conceptual inventory to guide JSON Schema generation
   decisions instead of relying only on Pydantic's technical schema output
3. issue `#46` defines the canonical Open CVN JSON format around conceptual
   entities, vocabularies, and trace rules
4. later parser issues can validate PDF/XML/JSON imports against that agnostic
   model while preserving CVN traceability

The strategic goal is to keep XML, Python, UML, and JSON as representations over a
shared conceptual model, not competing definitions of the curriculum domain.
