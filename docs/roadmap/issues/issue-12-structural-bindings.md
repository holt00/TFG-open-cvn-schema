# Issue 12 - Structural Pydantic Bindings From CVN XSDs

## Summary

Issue `#12` generated the structural Pydantic bindings for the three official
core schema concerns, was later corrected by hotfix `#4` to include auxiliary
schema families, standardized execution through a dedicated runner, and added
smoke tests for the generation workflow.

## Original Goal

- generate structural bindings from:
  - `CVN.xsd`
  - `SpecificationManual.xsd`
  - `CVNTreeModel_v1.0.xsd`
- verify importability and basic parse usage
- record structural limitations detected during generation

## Original Plan

1. generate `CVN.xsd` bindings under `src/generated/cvn/`
2. generate `SpecificationManual.xsd` bindings under
   `src/generated/specification_manual/`
3. generate `CVNTreeModel_v1.0.xsd` bindings under
   `src/generated/tree_model/`
4. verify local `include` and `import` resolution
5. verify generated modules can be imported
6. test at least one parse flow for `SpecificationManual.xml`
7. test at least one parse flow for `CVNTreeModel.xml`
8. record structural limitations and generation friction

## Adjustments Made During Implementation

The original plan was refined in several ways during execution:

1. a standardized runner was created before generation to make execution
   reproducible and testable
2. smoke tests were added as part of issue `#12` instead of waiting entirely
   for issue `#16`
3. editable packaging support was added so tests could import `cvn_codegen` and
   `generated.*` cleanly from the `src/` layout
4. generation had to be executed with `cwd=src` so package names such as
   `generated.cvn` mapped to `src/generated/cvn`
5. `tree_model` required a target-specific xsdata override (`--unnest-classes`)
   to avoid generation failure from circular dependencies
6. the parse goal for `CVNTreeModel.xml` was partially blocked by a mismatch
   between the canonical XML and its XSD, which had to be documented as a
   limitation instead of being silently patched in the structural layer

## Implementation Performed

### Standardized Runner

The following runner was introduced:

- `src/cvn_codegen/xsdata_runner.py`

Responsibilities implemented:

- resolve supported targets (`cvn`, `specification_manual`, `tree_model`,
  `reference_tables`, `subtypes`, `entity`, `thesaurus`, `all`)
- validate prerequisites
- clean the destination package before generation
- build deterministic xsdata commands
- execute generation from `src/`
- verify generated output

### Generated Structural Packages

Bindings were generated under:

- `src/generated/cvn/`
- `src/generated/specification_manual/`
- `src/generated/tree_model/`
- `src/generated/reference_tables/`
- `src/generated/subtypes/`
- `src/generated/entity/`
- `src/generated/thesaurus/`

### Tests Added

Runner tests were added under:

- `tests/test_xsdata_runner_unit.py`
- `tests/test_xsdata_runner_smoke.py`

## Verification

### Generation

Generation was successfully executed for:

- `CVN.xsd`
- `SpecificationManual.xsd`
- `CVNTreeModel_v1.0.xsd`
- `ReferenceTables.xsd`
- `Subtypes.xsd`
- `Entity_v1.4.xsd`
- `Thesaurus.xsd`

### Import Checks

The generated packages are importable:

- `generated`
- `generated.cvn`
- `generated.specification_manual`
- `generated.tree_model`
- `generated.reference_tables`
- `generated.subtypes`
- `generated.entity`
- `generated.thesaurus`

### Core Regression Checks After Auxiliary Expansion

- File-level core reproducibility remained stable after auxiliary generation:
  - `src/generated/cvn`: `5` Python files
  - `src/generated/specification_manual`: `3` Python files
  - `src/generated/tree_model`: `2` Python files
- Behavioral core checks remained stable:
  - runner tests passed
  - core imports remained valid

### Parse Smoke Checks

#### `SpecificationManual.xml`

- Result: success
- Parser: `xsdata_pydantic.bindings.XmlParser`
- Root class: `generated.specification_manual.SpecificationManual`

#### `CVNTreeModel.xml`

- Result: failure
- Root class: `generated.tree_model.CvntreeModel`
- Cause: the canonical XML contains `<Type>` inside `Indicator`, but
  `CVNTreeModel_v1.0.xsd` only declares `Value` and `Child` in that position

#### `ReferenceTables.xml`

- Result: success
- Parser: `xsdata_pydantic.bindings.XmlParser`
- Root class: `generated.reference_tables.reference_tables.ReferenceTables`

#### `Subtype_Spa.xml`

- Result: success
- Parser: `xsdata_pydantic.bindings.XmlParser`
- Root class: `generated.subtypes.subtypes.Cvnsubtype`

#### `Entity.xml`

- Result: success
- Parser: `xsdata_pydantic.bindings.XmlParser`
- Root class: `generated.entity.entity_v1_4.Entity`

#### `Thesaurus.xml`

- Result: success
- Parser: `xsdata_pydantic.bindings.XmlParser`
- Root class: `generated.thesaurus.thesaurus.Thesaurus`

## Findings

### Positive Results

- Structural bindings for all three source concerns can be generated
- Structural bindings for the four canonical auxiliary families can also be
  generated reproducibly
- Generated packages under `src/generated/` are importable
- The runner standardizes generation successfully
- `SpecificationManual.xml` can be parsed with the generated binding
- Auxiliary parse checks for `ReferenceTables.xml`, `Subtype_Spa.xml`,
  `Entity.xml`, and `Thesaurus.xml` are executable with generated bindings

### Detected Structural Limitations

- `xs:choice` semantics are not preserved as strict mutual exclusivity in the
  generated Pydantic models
- some `minOccurs` constraints are not enforced by generated list defaults
- some attributes are generated as `object`
- wrappers such as durations and year-like values are represented with XML
  helper types that are less ergonomic than plain primitives

### Detected Source Package Inconsistency

- `CVNTreeModel.xml` is not fully consistent with
  `CVNTreeModel_v1.0.xsd`
- confirmed example: `<Type>` appears inside `Indicator` in the XML, but the
  XSD does not allow that element there

## Known Limitations

Authoritative limitation record:

- `docs/pipeline/known_limitations.md`

Issue `#12` does not attempt to repair the structural layer beyond minimal,
justified generation overrides. Semantic cleanup belongs to later issues.

## Impact On Future Issues

- Issue `#13` must normalize metadata with awareness that the tree-model XML is
  not perfectly aligned with its XSD
- Issue `#13` and later semantic work can now rely on structural visibility for
  both core and auxiliary schema families
- Issue `#14` must define how to restore semantic meaning for `choice`, wrapper
  types, and multiplicity constraints
- Issue `#15` must emit domain models that correct the ergonomic limitations of
  the structural layer without mutating generated code
- Issue `#16` should preserve these edge cases through regression tests

## Status

- Status: implemented and verified as far as the structural layer allows
- Remaining caveat: the canonical `CVNTreeModel.xml` cannot be fully parsed with
  the generated XSD-faithful binding because the XML diverges from the XSD
