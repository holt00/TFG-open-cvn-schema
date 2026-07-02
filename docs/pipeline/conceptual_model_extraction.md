# Conceptual Model Extraction

## Purpose

This document describes the issue `#43` conceptual extraction layer. The layer
builds an agnostic curriculum inventory from the existing normalized metadata,
semantic policy, and domain generation IR.

It is not a UML renderer, JSON Schema generator, or parser. Those outputs consume
the conceptual inventory in later issues.

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

## Consumers

Later issues should consume this IR as follows:

- issue `#44`: render PlantUML or Mermaid diagrams from the conceptual inventory
- issue `#45`: use the inventory to guide JSON Schema shape decisions
- issue `#46`: use the inventory to define the canonical Open CVN JSON structure

Consumers should not treat generated Python classes or raw CVN XML paths as the
final conceptual schema.
