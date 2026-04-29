# CVN Annex Table Coverage

## Purpose

This document explains how the auxiliary tables listed in Annex I of the CVN
technical manual are represented across the official source bundle shipped in the
repository.

The goal is practical:

- identify which tables are already machine-readable inside the package
- distinguish core-package tables from side-package catalogs
- make explicit which tables remain unresolved or only visible in the manual

This avoids treating Annex I as a monolithic block and gives later pipeline
stages a clearer source-of-truth policy.

## Scope

The analysis is based on:

- `Manual de Especificaciones Técnicas v1.4.3_v2.1.pdf`, Annex I from page 308
- `XSD/AuxTable.xsd`
- `XSD/ISOUtilities.xsd`
- `XML/ReferenceTables.xml`
- `XML/Entity.xml`
- `XML/Thesaurus*.xml`
- supporting family-specific XSDs and manuals

This is a coverage map, not an exhaustive item-by-item dump of every enum value.

## Coverage Model

Annex tables fall into three practical categories.

### Category 1 - Directly Represented In Core XSD Artifacts

These tables are encoded directly in the core schemas used by the main CVN
document model.

Typical examples:

- `ISO_3166`
- `ISO_639`
- CVN helper types from `AuxTable.xsd`

Examples of directly encoded CVN controlled sets in `AuxTable.xsd`:

- `CVN_SOURCE_B`
- `CVN_LANGUAGE_B`
- `CVN_ACCESS_A`
- `CVN_ACTIVITY_A`
- `CVN_ACTIVITY_B`
- `CVN_CATEGORY_A`
- `CVN_DEDICATION_A`
- `CVN_DURATION_A`
- `CVN_ENTITY_TYPE`
- `CVN_EVALUATION_A`
- `CVN_EVENT_A`
- `CVN_EVENT_B`
- `CVN_EVENT_C`
- `CVN_FORMATION_A`
- `CVN_KNOW_A`
- `CVN_MANAGEMENT_A`
- `CVN_MANAGEMENT_TYPE_A`
- `CVN_PARTICIPATION_*`
- `CVN_PRIZE_A`
- `CVN_PROGRAMME_*`
- `CVN_PROJECT_*`
- `CVN_PUBLICATION_A`
- `CVN_QUALIFICATION_*`
- `CVN_SEX_A`
- `CVN_SITUATION_A`
- `CVN_STAY_*`
- `CVN_SUBJECT_A`
- `CVN_SUMMONS_*`
- `CVN_SUPPORT_*`
- `CVN_TEACHING_*`
- `CVN_THEMATIC_*`
- `CVN_TIME_A`
- `CVN_TITLE_*`

### Why This Matters

These tables are the safest candidates for direct structural extraction and for
future semantic treatment as package-native controlled values.

They are the least ambiguous part of Annex I from an automation perspective.

## Category 2 - Represented In Side Packages

These tables are not necessarily encoded directly inside the core CVN schema, but
they are still represented in machine-readable auxiliary packages bundled with
the source package.

### 2.1 ReferenceTables And Subtypes

The strongest machine-readable representation of Annex I is the
`ReferenceTables` family.

`XML/ReferenceTables.xml` contains 73 tables, including:

- `CVN_SEX_A`
- `CVN_TITLE_B`
- `CVN_LANGUAGE_B`
- `CVN_PUBLICATION_A`
- `CVN_SUMMONS_A`
- `CVN_SUMMONS_B`
- `CVN_ENTITY_TYPE`
- `CVN_SOURCE_A`
- `CVN_SOURCE_B`
- `CVN_SOURCE_C`
- `CVN_SOURCE_DATO`
- `CVN_REGION`
- `CVN_PROVINCE`
- `UNESCO_CODES`
- `ISO_3166`
- `ISO_639`

This means Annex I is not only in the PDF. A substantial part of it is already
serialized in XML and backed by `ReferenceTables.xsd`.

For the specific case of `UNESCO_CODES`, the repository now also includes a
standalone extracted representation derived from `ReferenceTables.xml`:

- `docs/CvnXML_v1.4.3_2.1_17012025/XML/UNESCO_CODES.xml`
- `docs/CvnXML_v1.4.3_2.1_17012025/XSD/UNESCOCodes.xsd`

These files are repository-derived extraction artifacts, created to isolate the
UNESCO subject classification as its own reusable XML/XSD pair while preserving
all item-level fields present in the packaged source table.

`Subtype_Spa.xml` is not a replacement for Annex I, but a derived codification
layer used when a table value must be projected into `Subtype` fields in the
operational CVN XML.

### 2.2 Entity Family

The manual repeatedly references `ENTITY@Entity.xsd` for entity-valued fields.

In the repository, the actual backing family is:

- `XSD/Entity_v1.4.xsd`
- `XML/Entity.xml`
- helper schemas `EntityUtilities_v1.4.xsd`, `ISOUtilitiesENTITY.xsd`, and
  `CVNUtilities_v1.0.xsd`

This family does not correspond to a simple enum table. It is a normalized
registry of institutions and organizations.

Therefore, whenever Annex I references entity-based values, the correct reading
is usually:

- not a closed enum
- but a catalog-backed external reference with structured metadata

### 2.3 Thesaurus Family

The manual references `THESAURUS@thesaurus.xsd` for keyword-like controlled
fields.

In the repository, the backing family is:

- `XSD/Thesaurus.xsd`
- `XML/Thesaurus.xml`
- `XML/Thesaurus_Eng.xml`
- `XML/Thesaurus_Spa.xml`

This family is not a flat code list. It is a hierarchical multilingual thesaurus
for subject and keyword codification.

### Why Category 2 Matters

These tables are machine-readable, but they should not all be treated the same
way as inline core enums.

They split into several semantic kinds:

- strict auxiliary tables
- hierarchical tables
- entity catalogs
- subtype projection maps
- multilingual thesauri

Future semantic generation should therefore preserve this distinction.

## Category 3 - Manual-Only Or Unresolved From The Package Alone

Some Annex references cannot be traced cleanly to a machine-readable backing
artifact in the current package, or remain ambiguous enough that the package
alone does not provide a confident closed-world interpretation.

### Confirmed Example: `CVN_AGENCY_C`

The table name `CVN_AGENCY_C` appears referenced in the manual material, but no
clear matching table was found in `ReferenceTables.xml`.

This makes it a known unresolved case from the package alone.

### Other Practical Cases

Any Annex table that is only visible in the manual PDF and cannot be traced to:

- `AuxTable.xsd`
- `ReferenceTables.xml`
- `Entity.xml`
- `Thesaurus.xml`

should remain in this category until proven otherwise.

### Why Category 3 Matters

These tables should not be turned into strict generated enums or treated as fully
resolved references without an explicit policy.

For the current project stage, the safest treatment is:

- document the gap explicitly
- keep the representation open or manually reviewed
- defer strict semantic closure to later issues only if stronger evidence is
  obtained

## Practical Mapping Rules For The Project

The following source-of-truth policy is the most useful one for the repository.

### Rule 1 - Prefer Core XSD Tables When They Exist

If a table is encoded directly in `AuxTable.xsd` or `ISOUtilities.xsd`, it
belongs to the core structural layer.

### Rule 2 - Prefer `ReferenceTables.xml` For Annex-I Table Materialization

If a table is listed in Annex I and also present in `ReferenceTables.xml`, then
`ReferenceTables.xml` is the best machine-readable source of the table's items,
labels, hierarchy, and delegation behavior.

### Rule 3 - Treat `Entity` As A Registry, Not As A Flat Enum

When the manual references `ENTITY@Entity.xsd`, the right semantic model is a
structured external registry of institutions.

### Rule 4 - Treat `Thesaurus` As A Hierarchical Vocabulary, Not As A Flat Enum

When the manual references `THESAURUS@thesaurus.xsd`, the right semantic model is
a multilingual hierarchical subject vocabulary.

### Rule 5 - Record Unresolved Tables Explicitly

If a table name cannot be traced to a concrete XML/XSD representation, it must be
kept as a documented unresolved case.

## Tables With Especially High Importance For Later Issues

The following categories are especially relevant for issue `#14` and issue `#15`.

### High Priority - Controlled Tables With Strong Semantic Impact

- `CVN_ENTITY_TYPE`
- `CVN_PUBLICATION_A`
- `CVN_PARTICIPATION_*`
- `CVN_PROJECT_*`
- `CVN_TITLE_*`
- `CVN_SUMMONS_*`
- `CVN_SOURCE_*`

### High Priority - Large Or Hierarchical Vocabularies

- `UNESCO_CODES`
- `CVN_REGION`
- `CVN_PROVINCE`
- `Thesaurus`

### High Priority - Externalized Structured Catalogs

- `Entity`
- `ReferenceTables`
- `Subtype`

## Particularities To Keep In Mind

### Annex I Is Split Across Several Technical Sources

The auxiliary tables in the manual do not live in one single technical file.

They are distributed across:

- core helper XSDs
- `ReferenceTables`
- `Entity`
- `Thesaurus`

### The Official Package Preserves Historical Drift

There are visible mismatches in:

- filenames mentioned by `Leeme` files versus actual repository filenames
- schema versions between XSD, XML, and PDF companions
- relative `schemaLocation` values versus repository layout

This means coverage should be documented semantically, not inferred only from
literal path names.

### Not Every Manual Reference Implies A Closed Enum

Some references point to:

- enumerations
- hierarchical tables
- subtype maps
- registries
- thesauri

Later semantic work should keep these categories distinct.

## Summary

Annex I is only partially embedded in the core XSD layer.

The actual technical representation of Annex tables across the package is:

1. core XSD-native tables for the main structural layer
2. side-package catalogs for reference tables, entities, subtypes, and thesauri
3. a smaller residual set of unresolved or manual-only cases

For repository work, the correct interpretation is therefore:

- Annex I is not a single source
- the package already contains substantial structured backing for it
- but that backing is distributed and not perfectly homogeneous

This document should be read together with:

- `docs/cvn_source_package_auxiliary_artifacts.md`
- `docs/cvn_annex_priority_table_families.md`
- `docs/cvn_annex_table_families_batch3.md`
- `docs/cvn_annex_table_families_batch4.md`
- `docs/cvn_annex_table_families_batch5.md`
- `docs/cvn_annex_table_families_batch6.md`
- `docs/cvn_annex_table_families_batch7.md`
- `docs/cvn_annex_table_families_batch8.md`
- `docs/cvn_serialization_patterns_reference.md`
- `docs/cvn_field_reference_traceability.md`
- `docs/informe_estructura_cvnxml_v1.4.3.md`
- `docs/pipeline/known_limitations.md`
