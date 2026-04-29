# CVN Annex Priority Table Families

## Purpose

This document records the high-priority auxiliary table families that are most
relevant to the current and upcoming semantic work in the repository.

The focus is intentionally narrow:

- `CVN_SOURCE_*`
- `CVN_TITLE_*`
- `CVN_PROJECT_*`
- `CVN_ENTITY_TYPE`
- `UNESCO_CODES`

These families matter more than most Annex I tables because they have a high
impact on:

- identifier modeling
- domain naming
- enum versus open-catalog decisions
- treatment of hierarchical vocabularies
- representation of institutions and titles

## Method

The analysis below combines:

- the manual semantics exposed through `SpecificationManual.xml`
- the machine-readable tables in `ReferenceTables.xml`
- the structural metadata attached to each table in `ReferenceTables.xml`

For each family, this document records:

- purpose
- table-level metadata
- observed size and structure
- where it is used in the manual metadata
- semantic implications for later issues

## Family 1 - `CVN_SOURCE_*`

## Overview

The `CVN_SOURCE_*` tables are not one single concept. They split into four
different roles.

- `CVN_SOURCE_A`: citation source
- `CVN_SOURCE_B`: digital publication identifier type
- `CVN_SOURCE_C`: digital author identifier type
- `CVN_SOURCE_DATO`: provenance source of imported data

The shared idea is origin or identifier source, but each table is tied to a
different semantic use.

## `CVN_SOURCE_A`

### Table Metadata

- table name: `CVN_SOURCE_A`
- version: `1.0.0`
- source: `CVN`
- `XMLDataType`: `CVN_Value_Filter@AuxTable.xsd`
- `XMLProperty`: `Filter`
- `XMLIndicator`: `Value`

### Observed Table Shape

- items: `5`
- hierarchy: none
- delegated items: none
- `Link=true`: none
- languages: `cat`, `eng`, `eus`, `fra`, `glg`, `spa`

### Observed Values

- `000` -> `WOS`
- `010` -> `SCOPUS`
- `020` -> `PUBMED`
- `030` -> `IN-RECS`
- `OTHERS` -> `Otros`

### Usage In `SpecificationManual.xml`

Observed references: `3`

Its documented use is as the source consulted to obtain citation counts.

This matches fields such as:

- `060.010.010.320` source of citations in publications
- and equivalent citation-source fields in publication-like sections

### Semantic Interpretation

This table is a small, mostly closed catalog of bibliometric and citation lookup
sources.

Recommended semantic treatment:

- strong enum candidate
- keep `OTHERS` support because the manual explicitly allows open extension

## `CVN_SOURCE_B`

### Table Metadata

- table name: `CVN_SOURCE_B`
- version: `1.0.0`
- source: `CVN`
- `XMLDataType`: `CVN_ExternalPKTypeType@AuxTable.xsd`
- `XMLProperty`: `ExternalPK`
- `XMLIndicator`: `Type`

### Observed Table Shape

- items: `4`
- hierarchy: none
- delegated items: none
- `Link=true`: none
- languages: `cat`, `eng`, `eus`, `fra`, `glg`, `spa`

### Observed Values

- `040` -> `DOI`
- `120` -> `Handle`
- `130` -> `PMID`
- `OTHERS` -> `Otros`

### Usage In `SpecificationManual.xml`

Observed references: `10`

This table is used in the manual for publication-level digital identifiers.

Typical places include:

- scientific publications
- conference communications
- teaching publications
- health-related publications

### Semantic Interpretation

This table represents the type of a publication external identifier, not the
identifier value itself.

Recommended semantic treatment:

- enum candidate for identifier type
- pair with a string value field for the actual identifier
- preserve `OTHERS` as open extension path

## `CVN_SOURCE_C`

### Table Metadata

- table name: `CVN_SOURCE_C`
- version: `1.0.0`
- source: `CVN`
- `XMLDataType`: `CVN_ExternalPKTypeType@AuxTable.xsd`
- `XMLProperty`: `ExternalPK`
- `XMLIndicator`: `Type`

### Observed Table Shape

- items: `4`
- hierarchy: none
- delegated items: none
- `Link=true`: none
- languages: `cat`, `eng`, `eus`, `fra`, `glg`, `spa`

### Observed Values

- `140` -> `ORCID`
- `150` -> `ScopusID`
- `160` -> `ResearcherID`
- `OTHERS` -> `Otros`

### Usage In `SpecificationManual.xml`

Observed references: `1`

This table is used for the author digital identifier type in the personal
identification block.

The canonical manual location is the `000.010.000.270` family discussed in the
manual excerpt.

### Semantic Interpretation

This is a small author-identifier type catalog.

Recommended semantic treatment:

- enum candidate
- semantically distinct from publication identifiers even if the structural
  pattern is similar

## `CVN_SOURCE_DATO`

### Table Metadata

- table name: `CVN_SOURCE_DATO`
- version: `1.0.1`
- source: `CVN`
- `XMLDataType`: `CVN_Value_Filter@AuxTable.xsd`
- `XMLProperty`: `Filter`
- `XMLIndicator`: `Value`

### Observed Table Shape

- items: `6`
- hierarchy: none
- delegated items: none
- `Link=true`: none
- languages: `cat`, `eng`, `eus`, `fra`, `glg`, `spa`

### Observed Values

- `140` -> `ORCID`
- `150` -> `SCOPUS`
- `160` -> `WOS`
- `170` -> `PUBMED`
- `180` -> `RECOLECTA`
- `190` -> `EPO`

### Usage In `SpecificationManual.xml`

Observed references: `1`

The manual definition says this table identifies the source from which data was
imported into CVN from external databases or external systems.

This is distinct from both citation source and identifier type.

### Semantic Interpretation

This is provenance metadata.

Recommended semantic treatment:

- enum candidate for origin system
- should remain separate from identifier-type fields and citation-source fields

## Cross-Family Notes For `CVN_SOURCE_*`

The package preserves two structural patterns under the same naming family.

### Pattern A - External Identifier Type

- `CVN_SOURCE_B`
- `CVN_SOURCE_C`

These map to `ExternalPK` and identify what kind of identifier is being used.

### Pattern B - Lookup Or Provenance Source

- `CVN_SOURCE_A`
- `CVN_SOURCE_DATO`

These identify where metric data or imported records came from.

This distinction must be preserved in issue `#14`, otherwise the domain layer may
collapse separate concepts into one generic `source` enum.

## Family 2 - `CVN_TITLE_*`

## Overview

The `CVN_TITLE_*` family spans several layers of academic title representation.

- `CVN_TITLE_A`: high-level title category
- `CVN_TITLE_B`: concrete university qualifications
- `CVN_TITLE_C`: doctoral programs
- `CVN_TITLE_D`: postgraduate titles

This family is one of the largest and most semantically heterogeneous parts of
the package.

## `CVN_TITLE_A`

### Table Metadata

- table name: `CVN_TITLE_A`
- version: `1.0.1`
- `antecesorTable`: `ISO_3166`
- source: `CVN`
- `XMLDataType`: `CVN_Value_Filter@AuxTable.xsd`
- `XMLProperty`: `Filter`
- `XMLIndicator`: `Value`

### Observed Table Shape

- items: `4`
- antecedent links: `4`
- delegated items: none
- `Link=true`: `1`
- languages: `cat`, `eng`, `eus`, `fra`, `glg`, `spa`

### Observed Values

- `940` -> `Doctor`
- `950` -> `Titulado Superior`
- `960` -> `Titulado Medio`
- `OTHERS` -> `Otros`

### Notable Behavior

Every item carries `AntecesorCode=724`, which points to Spain in `ISO_3166`.

This means the table is modeled as country-scoped, even though semantically it
acts like a generic academic level selector.

`OTHERS` has `Link=true`, meaning the table explicitly expects free-text
completion for out-of-catalog values.

### Usage In `SpecificationManual.xml`

Observed references: `1`

The canonical use is `020.010.010.010`, the academic level of the university
studies.

### Semantic Interpretation

This is a small classification table.

Recommended semantic treatment:

- enum candidate
- but document the country-scoping oddity as a technical artifact rather than a
  domain rule

## `CVN_TITLE_B`

### Table Metadata

- table name: `CVN_TITLE_B`
- version: `1.0.5`
- `antecesorTable`: `CVN_TITLE_A`
- source: `MEC`
- `XMLDataType`: `CVN_TITLE_B@ReferenceTables.xsd`
- `XMLProperty`: `Title`
- `XMLIndicator`: `Identification`

### Observed Table Shape

- items: `2,765`
- antecedent links: `2,765`
- delegated items: `54`
- `Link=true`: `1`
- languages: `cat`, `eng`, `eus`, `fra`, `glg`, `spa`

### Functional Role

This table contains concrete official university qualifications and related
historical degrees.

The values include:

- modern degree titles such as `Graduado o Graduada en ...`
- historical licenciatura, diplomatura, ingeniería, and arquitectura titles
- double and multiple degrees
- own titles and other special cases

### Hierarchical Meaning

The table depends on `CVN_TITLE_A`.

That means each concrete title is classified under a higher-level title family,
typically:

- `950` higher degree
- `960` middle degree
- sometimes other structural groupings depending on preserved historical data

### Usage In `SpecificationManual.xml`

Observed references: `3`

Key uses include:

- `020.010.010.030` name of university title
- `020.010.010.150` foreign title reference
- `030.010.000.020` teaching qualification title

### Semantic Interpretation

This is not a normal enum in the narrow sense. It is a large evolving catalog.

Recommended semantic treatment:

- treat as external codelist or catalog, not as a generated Python enum with
  thousands of members
- preserve `code`, `label`, `ancestor`, and `delegate`
- expose by lookup model or value object

## `CVN_TITLE_C`

### Table Metadata

- table name: `CVN_TITLE_C`
- version: `1.0.4`
- `antecesorTable`: `ISO_3166`
- source: `MEC - CCU`
- `XMLDataType`: `CVN_TITLE_C@ReferenceTables.xsd`
- `XMLProperty`: `Title`
- `XMLIndicator`: `Identification`

### Observed Table Shape

- items: `3,102`
- antecedent links: `3,102`
- delegated items: `766`
- `Link=true`: `1`
- languages: `cat`, `eng`, `eus`, `fra`, `glg`, `spa`

### Functional Role

This table contains doctoral program titles.

Examples visible in the XML and manual dump:

- thematic doctoral programs
- official postgraduate doctoral-program labels
- older and newer official naming forms

The very high number of delegated items suggests that this catalog preserves a
large amount of historical renaming and normalization drift.

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- `020.010.020.010` program of doctorado

### Semantic Interpretation

This is a large educational registry with strong historical drift.

Recommended semantic treatment:

- treat as external catalog
- preserve delegation chains because they likely encode historical replacement of
  program names

## `CVN_TITLE_D`

### Table Metadata

- table name: `CVN_TITLE_D`
- version: `1.0.3`
- `antecesorTable`: `ISO_3166`
- source: `MEC - CCU`
- `XMLDataType`: `CVN_TITLE_D@ReferenceTables.xsd`
- `XMLProperty`: `Title`
- `XMLIndicator`: `Identification`

### Observed Table Shape

- items: `4,467`
- antecedent links: `4,467`
- delegated items: `698`
- `Link=true`: `2`
- languages: `cat`, `eng`, `eus`, `fra`, `glg`, `spa`

### Functional Role

This table contains postgraduate titles, especially masters and other advanced
postgraduate qualifications.

Examples visible in the XML:

- `Master in ...`
- `Máster en ...`
- `Máster Universitario en ...`
- Erasmus Mundus and European masters
- specialized institutional postgraduate titles

The size and number of delegated items make it one of the most dynamic title
catalogs in the package.

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- `020.010.030.020` postgraduate qualification title

### Semantic Interpretation

This table should be treated as a large managed codelist, not as a simple enum.

### Cross-Family Notes For `CVN_TITLE_*`

The title family mixes two different semantic scales.

#### Small Classification Layer

- `CVN_TITLE_A`

#### Large Registry Layer

- `CVN_TITLE_B`
- `CVN_TITLE_C`
- `CVN_TITLE_D`

For the domain layer this means:

- `CVN_TITLE_A` can be modeled as a compact type classifier
- `CVN_TITLE_B/C/D` should be modeled as registries or codelists with lookup and
  delegation support

## Family 3 - `CVN_PROJECT_*`

## Overview

The `CVN_PROJECT_*` family separates three different concepts.

- `CVN_PROJECT_A`: type of academic work or supervised project, encoded through
  `Subtype`
- `CVN_PROJECT_B`: type of health-related project area
- `CVN_PROJECT_C`: modality of R&D project

## `CVN_PROJECT_A`

### Table Metadata

- table name: `CVN_PROJECT_A`
- version: `1.0.2`
- source: `CVN`
- `XMLDataType`: `Subtype@Subtypes.xsd`
- `XMLProperty`: `Subtype`

### Observed Table Shape

- items: `7`
- hierarchy: none
- delegated items: none
- `Link=true`: `1`
- languages: `cat`, `eng`, `eus`, `fra`, `glg`, `spa`

### Observed Values

- `055` -> end of course project / `Proyecto Final de Carrera`
- `066` -> minor thesis / `Tesina`
- `067` -> doctoral thesis / `Tesis Doctoral`
- `071` -> work leading to DEA
- `072` -> `Trabajo fin de grado`
- `073` -> `Trabajo fin de máster`
- `OTHERS` -> others, with `Link=true`

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- `030.040.000.010` type of supervised academic project

### Semantic Interpretation

This is a small domain enum with a special serialization rule: it maps through
`Subtype`, not a normal `Filter` pattern.

This makes it especially important for issue `#14` because it is one of the
clearest examples of a table whose semantic values are serialized through the
subtype system.

## `CVN_PROJECT_B`

### Table Metadata

- table name: `CVN_PROJECT_B`
- version: `1.0.1`
- source: `CVN`
- `XMLDataType`: `CVN_Value_Filter@AuxTable.xsd`
- `XMLProperty`: `Filter`
- `XMLIndicator`: `Value`

### Observed Table Shape

- items: `5`
- hierarchy: none
- delegated items: none
- `Link=true`: `1`
- languages: `cat`, `eng`, `eus`, `fra`, `glg`, `spa`

### Observed Values

- `060` -> clinical
- `410` -> healthcare management
- `780` -> public health
- `790` -> clinical support services
- `OTHERS` -> others, with `Link=true`

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- `040.110.000.080` type of health innovation project

### Semantic Interpretation

Compact enum candidate with explicit open extension path.

## `CVN_PROJECT_C`

### Table Metadata

- table name: `CVN_PROJECT_C`
- version: `1.0.2`
- source: `CVN`
- `XMLDataType`: `CVN_Value_Filter@AuxTable.xsd`
- `XMLProperty`: `Filter`
- `XMLIndicator`: `Value`

### Observed Table Shape

- items: `6`
- hierarchy: none
- delegated items: none
- `Link=true`: `0`
- languages: `cat`, `eng`, `eus`, `fra`, `glg`, `spa`

### Observed Values

- `190` -> demonstration, pilot, conceptual formulation, process or service
  design
- `200` -> basic research
- `210` -> industrial research
- `220` -> research and development, including translational
- `310` -> technical feasibility study
- `878` -> pre-competitive development activity

### Usage In `SpecificationManual.xml`

Observed references: `2`

Canonical uses:

- `050.020.010.030` modality of competitive R&D project
- `050.020.020.030` modality of non-competitive R&D project

### Semantic Interpretation

This is a compact project-modality classifier and a strong enum candidate.

Unlike `CVN_PROJECT_A`, it does not rely on subtype serialization.

## Family 4 - `CVN_ENTITY_TYPE`

## Table Metadata

- table name: `CVN_ENTITY_TYPE`
- version: `1.0.3`
- source: `CVN`
- `XMLDataType`: `CVN_EntityTypeType@AuxTable.xsd`
- `XMLProperty`: `Entity`
- `XMLIndicator`: `Type`

## Observed Table Shape

- items: `17`
- hierarchy: none
- delegated items: `1`
- `Link=true`: `1`
- languages: `cat`, `eng`, `eus`, `fra`, `glg`, `spa`

## Observed Values

Includes categories such as:

- `000` university
- `010` university research institute
- `020` university centers and assimilated structures
- `030` university department
- `040` foundation
- `050` state agency
- `060` public research body
- `080` business entity
- `090` national health system management body
- `100` healthcare institutions
- `110` technological centre
- `120` R&D centre
- `130` associations and groupings
- `140` CIBER
- `150` centers for innovation and technology
- `OTHERS` organization, others

## Notable Behavior

- `OTHERS` has `Link=true`, so the table explicitly allows free-text extension
- the table contains one delegated item, which means at least one category was
  retained for backward compatibility and redirected logically

## Usage In `SpecificationManual.xml`

Observed references: `78`

This is one of the most reused reference tables in the entire manual.

It appears across:

- professional situation
- education records
- teaching records
- health activity records
- research projects
- organizational and committee participation
- funding and evaluation entities

## Semantic Interpretation

This is a compact but central classification table.

Recommended semantic treatment:

- enum candidate
- preserve support for:
  - `OTHERS`
  - delegated values
- likely deserves a shared domain value object or enum used across many model
  sections

## Family 5 - `UNESCO_CODES`

## Table Metadata

- table name: `UNESCO_CODES`
- version: `1.0.1`
- `antecesorTable`: `UNESCO_CODES`
- source: `UNESCO`
- `XMLDataType`: `UNESCO_CODES@ReferenceTables.xsd`
- `XMLProperty`: `Subject`
- `XMLIndicator`: `Description`

## Observed Table Shape

- items: `2,513`
- antecedent links: `2,489`
- delegated items: `0`
- `Link=true`: `0`
- languages: `cat`, `eng`, `eus`, `fra`, `glg`, `spa`

## Structural Nature

This table is self-hierarchical.

The parent table is itself and most items carry `AntecesorCode`, which means the
catalog is a deep subject hierarchy, not a flat code list.

The beginning of the catalog already shows the pattern clearly:

- `110000` logic
- `110100` application of logic
- `110200` deductive logic
- `110204` formalized languages

The manual excerpt and XML also show broad high-level subject areas such as:

- logic
- mathematics
- astronomy and astrophysics
- physics
- chemistry
- life sciences
- earth sciences
- engineering
- social sciences
- arts and humanities

## Usage In `SpecificationManual.xml`

Observed references: `15`

Typical uses include:

- primary, secondary, and tertiary specialization fields in professional
  situation
- equivalent specialization fields in stays and activity descriptions

## Semantic Interpretation

This table should not be treated as a normal enum.

Recommended semantic treatment:

- hierarchical external subject classification
- lookup-backed code system
- preserve parent-child structure
- consider language-neutral code plus localized label resolution

## Cross-Family Conclusions

These priority families break down into three semantic classes.

### Small Enum-Like Families

- `CVN_SOURCE_A`
- `CVN_SOURCE_B`
- `CVN_SOURCE_C`
- `CVN_SOURCE_DATO`
- `CVN_PROJECT_A`
- `CVN_PROJECT_B`
- `CVN_PROJECT_C`
- `CVN_ENTITY_TYPE`
- `CVN_TITLE_A`

These are relatively small and mostly stable, but several still expose an
`OTHERS` escape hatch.

### Large Registry Families

- `CVN_TITLE_B`
- `CVN_TITLE_C`
- `CVN_TITLE_D`

These are too large and too historically dynamic to be comfortable strict enums.
They behave more like managed academic registries.

### Hierarchical Classification Family

- `UNESCO_CODES`

This is a deep subject taxonomy and should be modeled accordingly.

## Implications For Issue `#14`

Issue `#14` should preserve the following distinctions explicitly.

1. small identifier-source enums versus provenance-source enums
2. compact academic-level classification versus large academic-title registries
3. subtype-driven project classification versus ordinary filter-based project
   modality classification
4. compact entity-type classification versus full `Entity` registry references
5. hierarchical subject classification versus flat controlled vocabularies

If these distinctions are collapsed too early, later domain generation will lose
important semantics that are already present in the official source package.
