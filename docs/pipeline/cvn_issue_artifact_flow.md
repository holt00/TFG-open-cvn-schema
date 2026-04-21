# CVN Issue Artifact And Data Flow

## Purpose

This document explains which official CVN artifacts are used in each roadmap
issue and how data flows from the canonical package to the future domain models
and JSON-oriented outputs.

## Canonical Source Artifacts

The canonical package is:

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

## Roadmap View By Issue

### Issue `#11` - Project Infrastructure

- Main role:
  prepare repository structure and reproducible generation tooling
- Main artifacts used:
  - repository layout under `src/`
  - generation config under `config/.xsdata.xml`
- Output:
  - `src/generated/`
  - `src/cvn_codegen/`
  - `src/models/cvn/`

### Issue `#12` - Structural Bindings

- Main role:
  generate structural Python bindings that mirror the official XSDs
- Main artifacts used:
  - `XSD/CVN.xsd`
  - `XSD/Common.xsd`
  - `XSD/AuxTable.xsd`
  - `XSD/ISOUtilities.xsd`
  - `XSD/SpecificationManual.xsd`
  - `XSD/CVNTreeModel_v1.0.xsd`
- Output:
  - `src/generated/cvn/`
  - `src/generated/specification_manual/`
  - `src/generated/tree_model/`
  - `src/cvn_codegen/xsdata_runner.py`
- What this output means:
  - the project can represent the official XML/XSD structure in Python
  - this layer preserves structure, not final domain semantics

### Issue `#13` - Metadata Normalization

- Main role:
  build a normalized metadata layer that explains what each CVN `code` means and
  where it lives in the XML structure
- Main artifacts used:
  - `XML/SpecificationManual.xml`
  - `XML/CVNTreeModel.xml`
  - generated bindings from issue `#12` where usable
- Output:
  - normalized metadata structures under `src/cvn_codegen/`
  - indexes by CVN `code`
  - indexes by technical `xml_path`
  - mismatch reporting between manual and tree model
- What this output means:
  - the project gains a reusable semantic bridge between official metadata and
    future domain generation

### Issue `#14` - Semantic Mapping Rules

- Main role:
  define deterministic rules that translate normalized CVN metadata into a
  cleaner domain-oriented model
- Main artifacts used:
  - normalized output from issue `#13`
  - structural bindings from issue `#12`
  - known limitations and override decisions
- Output:
  - mapping policy for names, types, multiplicity, enums, wrappers, and
    overrides
- What this output means:
  - the project decides how to move from official CVN metadata to domain
    semantics

### Issue `#15` - Domain Model Generator

- Main role:
  generate domain-oriented Pydantic models from normalized metadata and mapping
  rules
- Main artifacts used:
  - normalized metadata from issue `#13`
  - semantic rules from issue `#14`
  - structural knowledge from issue `#12`
- Output:
  - generated or assembled models under `src/models/cvn/`
- What this output means:
  - the repository gains the first domain-facing representation suitable for
    JSON-oriented usage and later application logic

### Issue `#16` - Pipeline Tests

- Main role:
  validate the structural, normalization, semantic, and generation layers
- Main artifacts used:
  - canonical XML and XSD files
  - outputs from issues `#12` to `#15`
- Output:
  - reproducible tests for the full pipeline

### Issue `#17` - Workflow Documentation

- Main role:
  document and automate the end-to-end regeneration workflow
- Main artifacts used:
  - all previously implemented layers
  - persistent repository documentation
- Output:
  - final documented workflow and regeneration entry points

## Data Flow Overview

### Layered Flow

```text
Official CVN package
  |
  +-> XSD/CVN.xsd + related XSDs
  |     -> issue #12
  |     -> structural bindings in src/generated/cvn
  |
  +-> XML/SpecificationManual.xml
  |     -> issue #13
  |     -> normalized semantic metadata by code
  |
  `-> XML/CVNTreeModel.xml
        -> issue #13
        -> normalized technical path metadata by code and xml_path

normalized metadata (#13)
  + structural baseline (#12)
  -> semantic mapping rules (#14)
  -> domain Pydantic models (#15)
  -> validation, JSON serialization, and downstream tools
```

### Detailed Flow

```text
XSD/CVN.xsd
  + Common.xsd
  + AuxTable.xsd
  `+ ISOUtilities.xsd
    -> xsdata generation (#12)
    -> generated.cvn

XSD/SpecificationManual.xsd
  + XML/SpecificationManual.xml
    -> parseable structural binding (#12)
    -> manual metadata extraction (#13)
    -> normalized manual entries

XSD/CVNTreeModel_v1.0.xsd
  + XML/CVNTreeModel.xml
    -> structural binding generated (#12)
    -> XML/XSD mismatch documented
    -> tolerant metadata extraction (#13)
    -> normalized tree entries with xml_path

normalized manual entries
  + normalized tree entries
    -> joined by CVN code (#13)
    -> mismatch reports (#13)
    -> semantic rule inputs (#14)

semantic rule inputs
  + mapping policy (#14)
    -> domain model generator (#15)
    -> Pydantic domain models in src/models/cvn

Pydantic domain models
  -> JSON-oriented representation
  -> future parser/validator goals from the TFG description
  -> future local storage, export, and downstream tools
```

## Why Issue `#13` Does Not Use Final CVN Instance Files Yet

- `#13` is not focused on parsing end-user CVN documents yet
- `#13` first builds the semantic bridge needed to understand those documents
- `SpecificationManual.xml` explains the meaning of each `code`
- `CVNTreeModel.xml` explains the technical location of each `code`
- only after that bridge exists can later issues create domain models that are
  suitable for JSON-oriented validation and application logic

## Practical Reading Guide

To understand the current pipeline state quickly:

1. read `docs/pipeline/cvn_pydantic_generation_pipeline.md`
2. read this file for artifact-to-issue mapping
3. read `docs/roadmap/issues/issue-13-normalization.md`
4. read `docs/pipeline/known_limitations.md`
