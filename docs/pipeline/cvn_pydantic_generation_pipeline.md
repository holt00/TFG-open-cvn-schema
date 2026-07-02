# CVN Pydantic Generation Pipeline

## Purpose

This document describes the technical architecture of the CVN generation
pipeline and the current structural implementation baseline.

## Canonical Source Package

The canonical source package is:

```text
docs/CvnXML_v1.4.3_2.1_17012025/
|- Leeme.txt
|- LeemeENTITY.txt
|- LeemeREFERENCETABLES.txt
|- LeemeTHESAURUS.txt
|- CVN_README.md
|- Manual/
|  |- Manual de Especificaciones Técnicas v1.4.3_v2.1.pdf
|  |- TreeModel_v1.0 20090331 v1.0.pdf
|  |- Entidades_esquema_Entity_v1.4.xsd_2008-07-04 v1.0.pdf
|  |- ReferenceTables.pdf
|  |- Subtypes_v1.1.pdf
|  `- Tesauros 2008-01-23 v1.0.pdf
|- XML/
|  |- SpecificationManual.xml
|  |- CVNTreeModel.xml
|  |- Entity.xml
|  |- ReferenceTables.xml
|  |- Subtype_Spa.xml
|  |- Thesaurus.xml
|  |- Thesaurus_Eng.xml
|  `- Thesaurus_Spa.xml
`- XSD/
   |- CVN.xsd
   |- Common.xsd
   |- AuxTable.xsd
   |- ISOUtilities.xsd
   |- SpecificationManual.xsd
   |- CVNTreeModel_v1.0.xsd
   |- Entity_v1.4.xsd
   |- EntityUtilities_v1.4.xsd
   |- ISOUtilitiesENTITY.xsd
   |- CVNUtilities_v1.0.xsd
   |- ReferenceTables.xsd
   |- ISOUtilitiesREFERENCETABLES.xsd
   |- Subtypes.xsd
   |- Thesaurus.xsd
   `- ISOUtilitiesTHESAURUS.xsd
```

These artifacts represent three different but related layers, plus a set of
auxiliary catalog families that the core CVN package references indirectly.

### Layer 1 - Final CVN XML Structure

- `XSD/CVN.xsd` defines the XML exchanged by CVN systems
- root element: `CVN`
- main blocks: `Version`, `Agent`, repeated `CvnItem`

### Layer 2 - Technical Reusable Types And Controlled Values

- `XSD/Common.xsd` defines wrappers such as `CVN_string`, `CVN_date`,
  `CVN_ISO_639`, `CVN_ISO_3166`, and `FlexibleDatesType`
- `XSD/AuxTable.xsd` defines CVN auxiliary controlled values
- `XSD/ISOUtilities.xsd` defines ISO code tables reused elsewhere

### Layer 3 - Functional And Technical Metadata

- `XML/SpecificationManual.xml` is the functional manual in XML form
- `XML/CVNTreeModel.xml` maps functional CVN codes to technical XML paths
- `XSD/SpecificationManual.xsd` validates the manual XML
- `XSD/CVNTreeModel_v1.0.xsd` validates the tree model XML

### Layer 4 - Auxiliary Catalog Families

- `XML/Entity.xml` and `XSD/Entity_v1.4.xsd` define a normalized institution and
  organization registry used by CVN through references such as
  `ENTITY@Entity.xsd`
- `XML/ReferenceTables.xml` and `XSD/ReferenceTables.xsd` materialize a large
  portion of the Annex I auxiliary tables in XML form
- `XML/Subtype_Spa.xml` and `XSD/Subtypes.xsd` define the codification layer for
  `Subtype` values derived from auxiliary tables
- `XML/Thesaurus.xml`, `XML/Thesaurus_Eng.xml`, `XML/Thesaurus_Spa.xml`, and
  `XSD/Thesaurus.xsd` define the hierarchical keyword thesaurus referenced from
  fields such as `THESAURUS@thesaurus.xsd`

## Observed Relationships Between Files

- `XSD/CVN.xsd` includes `Common.xsd` and `AuxTable.xsd`
- `XSD/Common.xsd` includes `ISOUtilities.xsd`
- `XSD/SpecificationManual.xsd` imports the CVN namespace for language typing
- `XSD/CVNTreeModel_v1.0.xsd` uses its own namespace
- `XML/SpecificationManual.xml` is validated by `XSD/SpecificationManual.xsd`
- `XML/CVNTreeModel.xml` is validated by `XSD/CVNTreeModel_v1.0.xsd` in
  principle, although a documented inconsistency exists in practice
- `XML/Entity.xml` is validated by `XSD/Entity_v1.4.xsd` in conceptual terms,
  although the preserved repository layout differs from the relative
  `schemaLocation` strings used in the original files
- `XML/ReferenceTables.xml` is validated by `XSD/ReferenceTables.xsd`
- `XML/Subtype_Spa.xml` is validated by `XSD/Subtypes.xsd`
- `XML/Thesaurus*.xml` is validated by `XSD/Thesaurus.xsd`

The conceptual relationship is:

```text
SpecificationManual.xml
  -> functional meaning of CVN codes

CVNTreeModel.xml
  -> technical mapping of those codes into XML nodes and paths

CVN.xsd + Common.xsd + AuxTable.xsd + ISOUtilities.xsd
  -> valid XML structure and controlled value types

Entity.xml + Entity_v1.4.xsd + helpers
  -> normalized external entity registry used by CVN references

ReferenceTables.xml + ReferenceTables.xsd
  -> machine-readable auxiliary tables corresponding to Annex I

Subtype_Spa.xml + Subtypes.xsd
  -> codification bridge from auxiliary table values to `Subtype`

Thesaurus.xml + Thesaurus.xsd
  -> hierarchical multilingual keyword vocabulary
```

## Observed Structural Characteristics

### Complexity Snapshot

- `CVN.xsd`: 74 `complexType`, 232 `element`, 125 `attribute`, 3 `choice`
- `Common.xsd`: 11 `complexType`, 1 `choice`
- `AuxTable.xsd`: 33 `simpleType`
- `ISOUtilities.xsd`: large enumerations for ISO codes

### Relevant Structural Friction

- recursion through `Link -> CvnItemType`
- repeated wrappers using `Item` plus metadata attributes
- a small number of important `choice` constructs
- very large enums

### Metadata Coverage

- `SpecificationManual.xml`: 1456 `Item` elements and 1456 unique codes
- `CVNTreeModel.xml`: 101 `CVNItem`, 939 `Property`, 4635 `Indicator`
- `CVNTreeModel.xml`: 1430 unique codes
- overlap between manual and tree model: 1429 codes
- codes in manual but not tree model: 27
- code in tree model but not manual: `030.010.000.250`

### Reference Table Situation

Resolvable internally in the core or auxiliary package:

- `ISO_3166`
- `ISO_639`
- tables in `AuxTable.xsd`
- tables in `ReferenceTables.xml`
- `UNESCO_CODES`

Available as side-package registries rather than direct core XSD enums:

- `ENTITY@Entity.xsd` -> represented by `Entity_v1.4.xsd` and `Entity.xml`
- `THESAURUS@thesaurus.xsd` -> represented by `Thesaurus.xsd` and
  `Thesaurus*.xml`

Still unresolved or requiring explicit semantic policy:

- some manual references do not map cleanly to a side-package table from the
  package alone, for example `CVN_AGENCY_C`

## Architecture Decision

The repository uses a two-layer architecture:

```text
Official XSDs
  -> structural Pydantic bindings

SpecificationManual.xml + CVNTreeModel.xml
  + optional CVN.xsd/Common.xsd structural type trace
  -> normalization
  -> semantic mapping rules and overrides
  -> domain Pydantic models
```

This means:

- `src/generated/` is an interoperability layer
- future semantic cleanup belongs outside `src/generated/`
- `SemanticPolicyBundle` is the source of truth for generator semantics
- the domain generator must not re-derive semantic policy from raw XML, raw XSD,
  or generated structural bindings

The complete implemented handoff is:

```text
normalized metadata + auxiliary reference resolution + structural type evidence
-> SemanticPolicyBundle
-> domain generator
-> domain-oriented Pydantic artifacts
```

### Current Normalization Entry Point

- the recommended repository entry point for normalized metadata is:
  - `cvn_codegen.normalization.build_normalization_result(...)`
- this entry point returns the integrated normalization layer used by later
  roadmap issues, including:
  - normalized entries by CVN code
  - tree entries by technical XML path
  - optional structural type evidence when `cvn_xsd_path` and `common_xsd_path`
    are provided
  - source-exclusive code sets
  - currently documented mismatch reporting
- canonical domain generation provides `CVN.xsd` and `Common.xsd` to this entry
  point so wrapper policies can be attached without generator-side raw XSD
  inspection
- lower-level helper functions inside `cvn_codegen.normalization` remain
  importable when needed, but they are not the preferred integration surface for
  later stages

## Repository Layout

```text
src/
├── generated/
│   ├── cvn/
│   ├── reference_tables/
│   ├── subtypes/
│   ├── entity/
│   ├── specification_manual/
│   ├── thesaurus/
│   └── tree_model/
├── cvn_codegen/
└── models/
    └── cvn/
```

### Responsibilities

- `src/generated/`: generated structural bindings
- `src/cvn_codegen/`: hand-maintained loading, normalization, resolution,
  semantic-policy, and generation logic
- `src/models/cvn/components.py`: hand-maintained shared domain components
- `src/models/cvn/generated/`: generated domain-oriented model output

Do not edit `src/generated/` manually. Regenerate it from the canonical XSDs.

Do not edit `src/models/cvn/generated/` manually. Regenerate it through the
domain generator.

## Complete Regeneration Workflow

The contributor-facing workflow is documented in:

- `docs/development/regeneration_workflow.md`

The command sequence is:

```bash
uv sync --group codegen --group testing
uv pip install -e .
uv run python -m cvn_codegen.xsdata_runner all
uv run python -m cvn_codegen.domain_model_generator
uv run pytest -n auto tests
```

The implemented workflow stages are:

1. core structural binding generation from `CVN.xsd`,
   `SpecificationManual.xsd`, and `CVNTreeModel_v1.0.xsd`
2. auxiliary structural binding generation from `ReferenceTables.xsd`,
   `Subtypes.xsd`, `Entity_v1.4.xsd`, and `Thesaurus.xsd`
3. normalization of `SpecificationManual.xml` and `CVNTreeModel.xml`
4. auxiliary-source loading and deterministic reference-resolution enrichment
5. XSD-enriched structural type evidence for wrapper handoff
6. semantic policy application over enriched normalized metadata
7. domain model generation under `src/models/cvn/generated/`
8. local and CI verification through `uv run pytest -n auto tests`

### Controlled-Reference Source Order

Normalization materializes controlled-reference meaning before semantic policy
consumes it. The effective source-of-truth order is:

1. explicit side-package references such as `ENTITY@Entity.xsd` and
   `THESAURUS@thesaurus.xsd`
2. direct `ReferenceTables.xml` matches where applicable
3. subtype-backed classification through `Subtype@Subtypes.xsd`
4. hierarchical thematic classification where technical metadata supports it
5. unresolved documented exceptions and under-traced tables

Representative cases include `CVN_SEX_A`, `CVN_ENTITY_TYPE`, `CVN_KNOW_A`,
`ENTITY@Entity.xsd`, `THESAURUS@thesaurus.xsd`, `UNESCO_CODES`, `CVN_AGENCY_C`,
`CVN_INTERVENTION_A`, and `CVN_PRUEBA`.

### Semantic Policy Contract

The domain generator consumes issue `#14` semantic-policy outputs directly:

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

Semantic policy owns Spanish-first naming, deterministic identifier
normalization, override precedence, strict-enum eligibility, open coded-value
fallback behavior, wrapper treatment, and trace preservation.

### Domain Generation Contract

The canonical domain generation command is:

```bash
uv run python -m cvn_codegen.domain_model_generator
```

The current canonical output emits `105` files under
`src/models/cvn/generated/`, including `enums.py`, `manual_only.py`,
`tree_without_item.py`, and `cvn_item_*` modules. Generated files are expected to
be deterministic, importable, ASCII-only under the current policy, and traceable
back to CVN `code`, XML paths, reference-resolution trace, and semantic-policy
decisions.

### Wrapper Handoff

Canonical domain generation passes `CVN.xsd` and `Common.xsd` into normalization
so normalized entries can carry `StructuralTypeEvidence`. Semantic policy maps
terminal wrapper evidence to shared components such as `FlexibleDateValue`,
`OfficialIdValue`, `EntityTypeValue`, and `EntityNameValue`.

Normalization calls that omit `CVN.xsd` and `Common.xsd` preserve empty
structural type evidence and cannot attach wrapper-aware field shapes.

## Current Structural Generation Workflow

### Shared Config

- config file: `config/.xsdata.xml`
- package base: `generated`
- output format: `pydantic`

### Standard Runner

- runner module: `src/cvn_codegen/xsdata_runner.py`
- supported targets:
  - `cvn`
  - `specification_manual`
  - `tree_model`
  - `reference_tables`
  - `subtypes`
  - `entity`
  - `thesaurus`
  - `all`

The runner:

- validates prerequisites
- cleans output directories
- executes xsdata from `src/`
- verifies generated output

### Target Packages

- `generated.cvn` -> `src/generated/cvn`
- `generated.specification_manual` -> `src/generated/specification_manual`
- `generated.tree_model` -> `src/generated/tree_model`
- `generated.reference_tables` -> `src/generated/reference_tables`
- `generated.subtypes` -> `src/generated/subtypes`
- `generated.entity` -> `src/generated/entity`
- `generated.thesaurus` -> `src/generated/thesaurus`

### Target-Specific Override

- `tree_model` uses `--unnest-classes`
- reason: avoid generation failure caused by circular dependencies under the
  default settings

## Verification Status

### Generation

- `CVN.xsd`: generated successfully
- `SpecificationManual.xsd`: generated successfully
- `CVNTreeModel_v1.0.xsd`: generated successfully with target-specific override
- `ReferenceTables.xsd`: generated successfully
- `Subtypes.xsd`: generated successfully
- `Entity_v1.4.xsd`: generated successfully
- `Thesaurus.xsd`: generated successfully

### Importability

- `generated.cvn`: import OK
- `generated.specification_manual`: import OK
- `generated.tree_model`: import OK
- `generated.reference_tables`: import OK
- `generated.subtypes`: import OK
- `generated.entity`: import OK
- `generated.thesaurus`: import OK

### Parse Smoke

- `SpecificationManual.xml`: parse OK
- `CVNTreeModel.xml`: parse fails due to source XML/XSD inconsistency, not due
  to a broken generated module
- `ReferenceTables.xml`: parse OK
- `Subtype_Spa.xml`: parse OK
- `Entity.xml`: parse OK
- `Thesaurus.xml`: parse OK

### Tests And CI

- full local verification command: `uv run pytest -n auto tests`
- latest issue `#17` baseline verification before workflow documentation:
  `294 passed in 297.99s (0:04:57)`
- pull-request CI runs the same full-suite command through
  `.github/workflows/pr-tests.yml`
- the CI job name is `tests`
- xsdata regeneration tests are serialized under xdist by
  `tests/xsdata_generation_lock.py`

## Known Limitations

See the authoritative limitation register:

- `docs/pipeline/known_limitations.md`
