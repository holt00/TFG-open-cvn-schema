# CVN Field Reference Traceability

## Purpose

This document explains how to trace a CVN field from the normalized manual layer
already implemented in the repository to the technical source artifact that
backs its controlled values and to the serialization pattern used in the official
package.

Its goal is operational:

- help later semantic work remain compatible with what is already implemented
- avoid reopening the source package every time a field needs to be classified
- provide a stable interpretation layer without modifying the current core
  normalization logic

## Compatibility With The Current Implementation

The current repository implementation already exposes the key anchor needed for
this traceability work:

- `ManualCodeEntry.manual_reference_table`

This field is populated from `SpecificationManual.xml` during issue `#13`
normalization and is therefore the canonical bridge from a CVN field to its
controlled table or auxiliary catalog.

That means this document is intentionally additive.

It does not redefine the normalization layer. It explains how to interpret the
references already extracted by it.

## Source Of Truth Layers

When a CVN field has a `manual_reference_table`, the repository should resolve it
through the following source-of-truth order.

### Level 1 - `ReferenceTables.xml`

If the reference name exists as a table in `XML/ReferenceTables.xml`, that XML is
the primary machine-readable source for:

- codes
- multilingual labels
- hierarchy through `AntecesorCode`
- delegation through `Delegate`
- technical projection metadata such as:
  - `XMLDataType`
  - `XMLProperty`
  - `XMLIndicator`

### Level 2 - Side Packages

If the manual reference points to an auxiliary family rather than a simple table,
the source of truth is the relevant side package.

#### Entity

Manual form:

- `ENTITY@Entity.xsd`

Backing artifacts:

- `XML/Entity.xml`
- `XSD/Entity_v1.4.xsd`
- helpers `EntityUtilities_v1.4.xsd`, `ISOUtilitiesENTITY.xsd`,
  `CVNUtilities_v1.0.xsd`

#### Thesaurus

Manual form:

- `THESAURUS@thesaurus.xsd`

Backing artifacts:

- `XML/Thesaurus.xml`
- `XML/Thesaurus_Eng.xml`
- `XML/Thesaurus_Spa.xml`
- `XSD/Thesaurus.xsd`

### Level 3 - Manual-Only Or Unresolved Cases

If the manual reference does not resolve cleanly to `ReferenceTables.xml` or to
one of the side packages, it must remain documented as unresolved.

Known example:

- `CVN_AGENCY_C`

## Resolution Procedure

For any normalized field, use this procedure.

1. read `ManualCodeEntry.code`
2. read `ManualCodeEntry.manual_reference_table`
3. resolve the reference according to the rules below
4. identify the serialization pattern
5. classify the field as one of these semantic kinds:
   - compact enum-like table
   - hierarchical codelist
   - large registry or managed catalog
   - side-package external catalog
   - manual-only unresolved reference
   - technically present but functionally under-traced table

## Resolution Rules

### Rule 1 - Exact Match In `ReferenceTables.xml`

If the manual reference table name exists in `ReferenceTables.xml`, resolve it to:

- table metadata in `ReferenceTables.xml`
- the corresponding `ReferenceTables.xsd` structure
- subtype support if `XMLDataType` is `Subtype@Subtypes.xsd`

Examples:

- `CVN_SEX_A`
- `CVN_TITLE_B`
- `CVN_PROJECT_A`
- `CVN_LANGUAGE_B`
- `UNESCO_CODES`

### Rule 2 - Exact Side-Package Reference

If the manual reference is an explicit auxiliary-package reference string, use
the side package instead of looking for a same-named table in `ReferenceTables`.

Examples:

- `ENTITY@Entity.xsd`
- `THESAURUS@thesaurus.xsd`

### Rule 3 - Unresolved Manual Reference

If the manual uses a reference table name that has no matching `ReferenceTables`
table and no side-package backing, document it as unresolved.

Example:

- `CVN_AGENCY_C`

### Rule 4 - Technically Present But Functionally Under-Traced Table

If a table exists in `ReferenceTables.xml` but the manual does not appear to use
it, keep it documented but lower its priority for semantic generation.

Examples:

- `CVN_INTERVENTION_A`
- `CVN_PRUEBA`

## Serialization Pattern Map

The following pattern names are the ones that matter most for repository work.

### `Filter/Value`

Meaning:

- compact direct controlled value carried as a generic filtered value

Examples:

- `CVN_SUBJECT_A`
- `CVN_STAY_A`
- `CVN_STAY_B`
- `CVN_ACTIVITY_A`
- `CVN_SUMMONS_B`

### `Quality/Measure`

Meaning:

- normalized level or result scale

Examples:

- `CVN_LANGUAGE_B`
- `CVN_QUALIFICATION_B`

### `Scope/Type`

Meaning:

- geographical or institutional scope type

Examples:

- `CVN_SCOPE_A`
- `CVN_SCOPE_B`

### `ExternalPK/Type`

Meaning:

- type of external identifier

Examples:

- `CVN_SOURCE_B`
- `CVN_SOURCE_C`

### `Entity/Type`

Meaning:

- compact type of institution

Example:

- `CVN_ENTITY_TYPE`

### `Dedication`

Meaning:

- dedication regime without a generic indicator node

Example:

- `CVN_DEDICATION_A`

### `PhysicalDimension/Type`

Meaning:

- dimension of quantitative measurement

Example:

- `CVN_TIME_A`

### `Subject/Description`

Meaning:

- hierarchical subject classification

Example:

- `UNESCO_CODES`

### `Subtype@Subtypes.xsd`

Meaning:

- selected value is projected into the `Subtype` structure instead of being used
  as a plain direct controlled value

Examples:

- `CVN_FORMATION_A`
- `CVN_TEACHING_A`
- `CVN_KNOW_A`
- `CVN_PROJECT_A`
- `CVN_PUBLICATION_A`
- `CVN_SUPPORT_A`
- `CVN_EVENT_B`

### Side-Package Registry Or Vocabulary

Meaning:

- the reference is backed by a separate structured XML/XSD family rather than a
  compact table in `ReferenceTables.xml`

Examples:

- `ENTITY@Entity.xsd`
- `THESAURUS@thesaurus.xsd`

### Manual-Only Unresolved Reference

Meaning:

- reference appears in the manual but has no clean technical backing in the
  current package

Example:

- `CVN_AGENCY_C`

## Representative Field Traceability Examples

## Example 1 - Personal Identification Field

- field code: `000.010.000.030`
- field name: `Sexo`
- manual reference table: `CVN_SEX_A`
- technical source:
  - `ReferenceTables.xml`
  - `ReferenceTables.xsd`
- serialization pattern:
  - identification or personal-identification specific pattern
- semantic class:
  - compact enum-like table

## Example 2 - Institution-Valued Field

- field code: `010.010.000.020`
- field name: `Entidad empleadora`
- manual reference table: `ENTITY@Entity.xsd`
- technical source:
  - `Entity.xml`
  - `Entity_v1.4.xsd`
- serialization pattern:
  - side-package registry
- semantic class:
  - structured external entity catalog

## Example 3 - Author Identifier Type

- field code: `000.010.000.270`
- field name: `Tipo de identificador digital de autor`
- manual reference table: `CVN_SOURCE_C`
- technical source:
  - `ReferenceTables.xml`
- serialization pattern:
  - `ExternalPK/Type`
- semantic class:
  - compact identifier-type table

## Example 4 - Publication Type Using Subtype Serialization

- field code: `060.010.010.010`
- field name: `Tipo de producción`
- manual reference table: `CVN_PUBLICATION_A`
- technical source:
  - `ReferenceTables.xml`
  - `Subtypes.xsd`
  - `Subtype_Spa.xml`
- serialization pattern:
  - `Subtype@Subtypes.xsd`
- semantic class:
  - subtype-backed controlled family

## Example 5 - Subject Specialization Field

- field code: `010.010.000.220`
- field name: `Código Unesco: especialización primaria`
- manual reference table: `UNESCO_CODES`
- technical source:
  - `ReferenceTables.xml`
- serialization pattern:
  - `Subject/Description`
- semantic class:
  - hierarchical subject taxonomy

## Example 6 - H-Index Source With Unresolved Backing

- field code: `060.010.000.030`
- field name: `Fuente de índice H`
- manual reference table: `CVN_AGENCY_C`
- technical source:
  - no clean matching table in `ReferenceTables.xml`
- serialization pattern:
  - unresolved manual-only reference
- semantic class:
  - unresolved reference requiring explicit policy

## Recommended Modeling Policy

To remain compatible with the current implementation, later work should follow
these rules.

1. keep `ManualCodeEntry.manual_reference_table` as the stable starting point
2. resolve semantics outside the current normalization core
3. do not change issue `#13` structures unless a later issue explicitly needs it
4. prefer additive interpretation layers over invasive changes to the existing
   normalization output
5. preserve source-traceability names even when a cleaner internal name is used
   in documentation

## What This Document Enables

With the current repository state, this document now makes it possible to:

- classify a field's controlled-value source without reopening the raw package
- know whether a field points to:
  - a compact table
  - a hierarchical table
  - a subtype-backed family
  - a side-package registry
  - an unresolved reference
- keep future semantic work compatible with the already implemented
  normalization core

## Read Together With

- `docs/cvn_source_package_auxiliary_artifacts.md`
- `docs/cvn_source_package_annex_table_coverage.md`
- `docs/cvn_serialization_patterns_reference.md`
- `docs/cvn_annex_priority_table_families.md`
- `docs/cvn_annex_table_families_batch3.md`
- `docs/cvn_annex_table_families_batch4.md`
- `docs/cvn_annex_table_families_batch5.md`
- `docs/cvn_annex_table_families_batch6.md`
- `docs/cvn_annex_table_families_batch7.md`
- `docs/cvn_annex_table_families_batch8.md`
