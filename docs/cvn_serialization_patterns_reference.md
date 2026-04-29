# CVN Serialization Patterns Reference

## Purpose

This document explains the recurring serialization patterns used by CVN for
controlled tables, external catalogs, and auxiliary references.

The main point is that the semantic meaning of a table is not captured only by
its name. It is also encoded in the technical projection metadata used by the
source package, especially in `ReferenceTables.xml`.

The most useful fields for identifying the pattern are:

- `XMLDataType`
- `XMLProperty`
- `XMLIndicator`

This document is meant to be a practical bridge between:

- the functional manual
- the auxiliary tables
- the technical XML serialization
- the future semantic mapping policy in issue `#14`

## Pattern 1 - `Filter/Value`

## Shape

- `XMLDataType`: usually `CVN_Value_Filter@AuxTable.xsd`
- `XMLProperty`: `Filter`
- `XMLIndicator`: `Value`

## Meaning

This is the most common serialization pattern for compact controlled tables.

It means the selected table value is carried as a generic filtered value in the
CVN XML, but the domain meaning must still come from the referenced table.

## Typical Examples

- `CVN_SUBJECT_A`
- `CVN_STAY_A`
- `CVN_STAY_B`
- `CVN_ACTIVITY_A`
- `CVN_ACTIVITY_D`
- `CVN_MANAGEMENT_A`
- `CVN_MANAGEMENT_TYPE_A`
- `CVN_SUMMONS_A`
- `CVN_SUMMONS_B`
- `CVN_PRIZE_A`
- `CVN_THEMATIC_A`
- `CVN_THEMATIC_B`
- `CVN_ACCESS_A`
- `CVN_EVALUATION_A`
- many more compact CVN tables

## Why It Matters

Two tables using `Filter/Value` are not necessarily semantically close.

For example:

- `CVN_SUBJECT_A` classifies subject type
- `CVN_STAY_A` classifies objective of a stay
- `CVN_ACCESS_A` classifies access procedure

They share a technical projection, not a shared domain concept.

## Pattern 2 - `Quality/Measure`

## Shape

- `XMLProperty`: `Quality`
- `XMLIndicator`: `Measure`

## Meaning

This pattern is used for normalized measures, scales, and evaluative levels.

## Typical Examples

- `CVN_LANGUAGE_B`
- `CVN_QUALIFICATION_B`

## Why It Matters

These tables are usually better interpreted as scales or ratings than as generic
categories.

They are among the safest candidates for strict enums in the semantic layer.

## Pattern 3 - `Scope/Type`

## Shape

- `XMLProperty`: `Scope`
- `XMLIndicator`: `Type`

## Meaning

This pattern classifies geographical or institutional scope.

## Typical Examples

- `CVN_SCOPE_A`
- `CVN_SCOPE_B`

## Why It Matters

Scope tables should usually become shared reusable domain concepts because they
are reused across many unrelated curriculum sections.

Also, `CVN_SCOPE_A` and `CVN_SCOPE_B` should not be merged automatically.

## Pattern 4 - `ExternalPK/Type`

## Shape

- `XMLProperty`: `ExternalPK`
- `XMLIndicator`: `Type`

## Meaning

This pattern classifies the type of external identifier, not the identifier
value itself.

## Typical Examples

- `CVN_SOURCE_B`
- `CVN_SOURCE_C`

## Why It Matters

The domain layer should preserve the distinction between:

- identifier type
- identifier value

This is especially important for publication identifiers and author identifiers.

## Pattern 5 - `Entity/Type`

## Shape

- `XMLProperty`: `Entity`
- `XMLIndicator`: `Type`

## Meaning

This pattern classifies the type of institution referenced by a CVN field.

## Typical Example

- `CVN_ENTITY_TYPE`

## Why It Matters

This is not the same as the `Entity` family itself.

- `CVN_ENTITY_TYPE` is a small type table
- `Entity.xml` is a large normalized institution registry

Both concepts must stay distinct in later semantic modeling.

## Pattern 6 - `Dedication`

## Shape

- `XMLDataType`: `CVN_DedicationType@AuxTable.xsd`
- `XMLProperty`: `Dedication`
- no `XMLIndicator`

## Meaning

This is a specialized dedicated pattern for work dedication regime.

## Typical Example

- `CVN_DEDICATION_A`

## Why It Matters

This table is small, stable, and heavily reused across different sections. It is
an excellent candidate for a shared domain enum.

## Pattern 7 - `PhysicalDimension/Type`

## Shape

- `XMLProperty`: `PhysicalDimension`
- `XMLIndicator`: `Type`

## Meaning

This pattern encodes the unit or dimension in which a quantity is expressed.

## Typical Example

- `CVN_TIME_A`

## Why It Matters

This is not a thematic classification. It determines the meaning of a numeric
value, such as whether teaching load is measured in hours or credits.

## Pattern 8 - `Subject/Description`

## Shape

- `XMLProperty`: `Subject`
- `XMLIndicator`: `Description`

## Meaning

This pattern is used for subject hierarchies or thematic classifications.

## Typical Example

- `UNESCO_CODES`

## Why It Matters

This pattern points to a hierarchical thematic vocabulary rather than a flat enum.

It should normally be treated as a lookup-backed classification tree.

## Pattern 9 - `Subtype@Subtypes.xsd`

## Shape

- `XMLDataType`: `Subtype@Subtypes.xsd`
- `XMLProperty`: `Subtype`
- usually no `XMLIndicator`

## Meaning

This is not a normal direct-value serialization.

The selected code is projected into the `Subtype` structure of the operational
CVN XML, potentially through one or two levels (`SubType1` / `SubType2`).

## Typical Examples

- `CVN_FORMATION_A`
- `CVN_TEACHING_A`
- `CVN_KNOW_A`
- `CVN_PROJECT_A`
- `CVN_PUBLICATION_A`
- `CVN_SUPPORT_A`
- `CVN_SUPPORT_B`
- `CVN_EVENT_A`
- `CVN_EVENT_B`
- `CVN_EVENT_C`
- `CVN_ACTIVITY_B`

## Why It Matters

This is one of the most important patterns in the package.

It means later semantic generation cannot treat all tables as direct enums.

Subtype-backed tables need:

- explicit traceability to subtype mapping rules
- awareness that the selected table code is not necessarily the final XML value
  written to the CVN item

## Pattern 9b - `Identification/PersonalIdentification`

## Shape

- `XMLProperty`: `Identification`
- `XMLIndicator`: `PersonalIdentification`

## Meaning

This pattern is used for compact identity-classification fields attached to the
personal-identification area of CVN.

## Typical Example

- `CVN_SEX_A`

## Why It Matters

It is technically distinct from the more generic `Filter/Value` tables and
should be described with its own source-traceability pattern rather than being
silently folded into an unrelated generic class.

## Pattern 10 - Catalog-Or-Registry Patterns

Some references do not behave like simple tables at all.

## Entity Registry Pattern

Representative artifacts:

- `Entity.xml`
- `Entity_v1.4.xsd`

Meaning:

- large normalized institution catalog
- structured records, not plain enum members

## Thesaurus Pattern

Representative artifacts:

- `Thesaurus.xml`
- `Thesaurus_Eng.xml`
- `Thesaurus_Spa.xml`
- `Thesaurus.xsd`

Meaning:

- hierarchical multilingual vocabulary
- external coded subject system, not a plain enum

## Why It Matters

When the manual references `ENTITY@Entity.xsd` or `THESAURUS@thesaurus.xsd`, the
semantic layer should not flatten them into ordinary small enums.

## Pattern 11 - Manual-Only Or Unresolved References

Some table references appear in `SpecificationManual.xml` but do not resolve to a
matching `ReferenceTables.xml` table.

## Example

- `CVN_AGENCY_C`

## Meaning

This is a source inconsistency or packaging gap.

## Why It Matters

Such references must remain explicitly documented as unresolved.

They should not be promoted to strict enums without additional evidence.

## Pattern 12 - Technically Present But Functionally Under-Traced Tables

Some tables exist in `ReferenceTables.xml` but are not currently referenced by
`SpecificationManual.xml`.

## Examples

- `CVN_INTERVENTION_A`
- `CVN_PRUEBA`

## Meaning

They are part of the source package and may still matter, but their current
manual traceability is weak or absent.

## Why It Matters

These should be preserved and documented, but usually assigned lower semantic
priority than heavily reused manual-backed tables.

## Practical Summary For Issue `#14`

The future semantic policy should treat the following as different classes:

1. compact direct-value tables
2. compact measure or scale tables
3. scope tables
4. identifier-type tables
5. shared cross-cutting enums
6. subtype-backed tables
7. hierarchical subject classifications
8. external structured catalogs or registries
9. unresolved manual-only references
10. technically present but under-traced tables

If these classes are flattened too early, later domain generation will lose part
of the semantics already present in the official package.

## Suggested Reading Companion Set

- `docs/cvn_source_package_auxiliary_artifacts.md`
- `docs/cvn_source_package_annex_table_coverage.md`
- `docs/cvn_field_reference_traceability.md`
- `docs/cvn_annex_priority_table_families.md`
- `docs/cvn_annex_table_families_batch3.md`
- `docs/cvn_annex_table_families_batch4.md`
- `docs/cvn_annex_table_families_batch5.md`
- `docs/cvn_annex_table_families_batch6.md`
- `docs/cvn_annex_table_families_batch7.md`
- `docs/cvn_annex_table_families_batch8.md`
