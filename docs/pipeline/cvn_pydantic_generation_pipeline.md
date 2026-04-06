# CVN Pydantic Generation Pipeline

## Purpose

This document describes the technical architecture of the CVN generation
pipeline and the current structural implementation baseline.

## Canonical Source Package

The canonical source package is:

```text
docs/CvnXML_v1.4.3_2.1_17012025/
|- XML/
|  |- SpecificationManual.xml
|  `- CVNTreeModel.xml
`- XSD/
   |- CVN.xsd
   |- Common.xsd
   |- AuxTable.xsd
   |- ISOUtilities.xsd
   |- SpecificationManual.xsd
   `- CVNTreeModel_v1.0.xsd
```

These artifacts represent three different but related layers.

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

## Observed Relationships Between Files

- `XSD/CVN.xsd` includes `Common.xsd` and `AuxTable.xsd`
- `XSD/Common.xsd` includes `ISOUtilities.xsd`
- `XSD/SpecificationManual.xsd` imports the CVN namespace for language typing
- `XSD/CVNTreeModel_v1.0.xsd` uses its own namespace
- `XML/SpecificationManual.xml` is validated by `XSD/SpecificationManual.xsd`
- `XML/CVNTreeModel.xml` is validated by `XSD/CVNTreeModel_v1.0.xsd` in
  principle, although a documented inconsistency exists in practice

The conceptual relationship is:

```text
SpecificationManual.xml
  -> functional meaning of CVN codes

CVNTreeModel.xml
  -> technical mapping of those codes into XML nodes and paths

CVN.xsd + Common.xsd + AuxTable.xsd + ISOUtilities.xsd
  -> valid XML structure and controlled value types
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

Resolvable internally:

- `ISO_3166`
- `ISO_639`
- tables in `AuxTable.xsd`

External or unresolved:

- `ENTITY@Entity.xsd`
- `THESAURUS@thesaurus.xsd`
- `UNESCO_CODES`

## Architecture Decision

The repository uses a two-layer architecture:

```text
Official XSDs
  -> structural Pydantic bindings

SpecificationManual.xml + CVNTreeModel.xml
  -> normalization
  -> semantic mapping rules and overrides
  -> domain Pydantic models
```

This means:

- `src/generated/` is an interoperability layer
- future semantic cleanup belongs outside `src/generated/`

## Repository Layout

```text
src/
├── generated/
│   ├── cvn/
│   ├── specification_manual/
│   └── tree_model/
├── cvn_codegen/
└── models/
    └── cvn/
```

### Responsibilities

- `src/generated/`: generated structural bindings
- `src/cvn_codegen/`: hand-maintained pipeline logic and generation runner
- `src/models/cvn/`: future domain-oriented model output

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

### Target-Specific Override

- `tree_model` uses `--unnest-classes`
- reason: avoid generation failure caused by circular dependencies under the
  default settings

## Verification Status

### Generation

- `CVN.xsd`: generated successfully
- `SpecificationManual.xsd`: generated successfully
- `CVNTreeModel_v1.0.xsd`: generated successfully with target-specific override

### Importability

- `generated.cvn`: import OK
- `generated.specification_manual`: import OK
- `generated.tree_model`: import OK

### Parse Smoke

- `SpecificationManual.xml`: parse OK
- `CVNTreeModel.xml`: parse fails due to source XML/XSD inconsistency, not due
  to a broken generated module

## Known Limitations

See the authoritative limitation register:

- `docs/pipeline/known_limitations.md`
