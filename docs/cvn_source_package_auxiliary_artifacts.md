# CVN Source Package Auxiliary Artifacts

## Purpose

This document explains the auxiliary families that accompany the core CVN XML
package and that are required to understand the full official source bundle.

The project documentation already covered the core functional and structural
files:

- `SpecificationManual.xml`
- `CVNTreeModel.xml`
- `CVN.xsd`
- `Common.xsd`
- `AuxTable.xsd`
- `ISOUtilities.xsd`

This document covers the side packages that were present in the canonical source
bundle but had not yet been documented in comparable detail:

- the `Entity` family
- the `ReferenceTables` and `Subtypes` family
- the `Thesaurus` family

These families are not optional background material. They carry controlled
catalogs, multilingual labels, and supporting schemas that are referenced by
the main CVN manual and are relevant to later semantic mapping work.

## Position Inside The Canonical Package

The canonical source bundle now needs to be read as two related zones.

### Core CVN Specification Zone

- `Manual/Manual de Especificaciones Técnicas v1.4.3_v2.1.pdf`
- `Manual/TreeModel_v1.0 20090331 v1.0.pdf`
- `XML/SpecificationManual.xml`
- `XML/CVNTreeModel.xml`
- `XSD/CVN.xsd`
- `XSD/Common.xsd`
- `XSD/AuxTable.xsd`
- `XSD/ISOUtilities.xsd`
- `XSD/SpecificationManual.xsd`
- `XSD/CVNTreeModel_v1.0.xsd`

### Auxiliary Catalog And Supporting Zone

- `LeemeENTITY.txt`
- `XML/Entity.xml`
- `XSD/Entity_v1.4.xsd`
- `XSD/EntityUtilities_v1.4.xsd`
- `XSD/ISOUtilitiesENTITY.xsd`
- `XSD/CVNUtilities_v1.0.xsd`
- `Manual/Entidades_esquema_Entity_v1.4.xsd_2008-07-04 v1.0.pdf`
- `HTML/Entity_v1.4.html`
- `LeemeREFERENCETABLES.txt`
- `XML/ReferenceTables.xml`
- `XML/Subtype_Spa.xml`
- `XSD/ReferenceTables.xsd`
- `XSD/ISOUtilitiesREFERENCETABLES.xsd`
- `XSD/Subtypes.xsd`
- `Manual/ReferenceTables.pdf`
- `Manual/Subtypes_v1.1.pdf`
- `LeemeTHESAURUS.txt`
- `XML/Thesaurus.xml`
- `XML/Thesaurus_Eng.xml`
- `XML/Thesaurus_Spa.xml`
- `XSD/Thesaurus.xsd`
- `XSD/ISOUtilitiesTHESAURUS.xsd`
- `Manual/Tesauros 2008-01-23 v1.0.pdf`
- `HTML/Thesaurus.html`

## Family 1 - Entity

## What It Is

The `Entity` family defines the normalization model used by CVN to represent
 institutions, organizations, centers, departments, and other institutional
 actors.

It is not the main CVN curriculum schema. It is a companion entity catalog and
entity schema that the functional manual references through expressions such as
`ENTITY@Entity.xsd`.

In practice, it provides:

- a normalized entity registry in XML form
- a dedicated XSD to validate that registry
- auxiliary controlled codes for entity nature, function, and type
- region, province, and street type helpers reused in entity addresses

## Files And Roles

### `LeemeENTITY.txt`

Quick orientation file for the family.

What it tells us:

- the family is intended for entity codification in CVN
- `Entity_v1.4.xsd` is described as a more advanced schema than the older
  `Entity.xsd`
- the exported entities remain the same, but the schema exposes more detail
- the package includes manual, XML, XSD, and HTML views

### `Manual/Entidades_esquema_Entity_v1.4.xsd_2008-07-04 v1.0.pdf`

Human-readable explanation of `Entity_v1.4.xsd`.

Its value is high because it states the intended semantics of fields that would
otherwise be visible only as schema mechanics.

Important semantic points captured in the PDF:

- an entity is an institution, corporation, or company assigned a unique
  identifier for terminology normalization
- each normalized entity is represented by one `item`
- `ItemId` is the unique entity identifier and the document states that EAN-128
  is intended for the coding strategy
- entity function may be hierarchical through one or more `ItemAncestorId`
- `Delegate` means logical deactivation and redirection to a new `ItemId`

### `XSD/Entity_v1.4.xsd`

Main schema of the family.

Root element:

- `Entity`

Top-level structure:

- repeated `item`
- root attribute `version`

Each `item` can contain:

- `ItemId`
- `Nature`
- repeated `Function`
- `Type`
- `ItemAddress`
- repeated `ItemDescription`
- `Synonym`
- `URL`
- repeated `ItemNote`
- `Delegate`

The schema therefore models a single entity as a registry record with identity,
classification, address, multilingual naming, aliases, optional notes, and a
logical-redirection mechanism.

### `XSD/EntityUtilities_v1.4.xsd`

Controlled-value helper schema for the entity family.

It defines:

- `CVN_ENTITY_NATURE`
  - `000` public
  - `010` private
  - `020` mixed
- `CVN_ENTITY_FUNCTION`
  - `000` research
  - `010` work
  - `020` teaching
  - `030` health
- `CVN_ENTITY_TYPE`
  - entity categories such as university, institute, foundation, public
    research body, enterprise, health institution, technology center, and
    others

This file is especially important because the values used in the entity package
line up with values referenced from the main CVN package through
`CVN_ENTITY_TYPE`.

### `XSD/ISOUtilitiesENTITY.xsd`

Entity-family copy of ISO controlled values.

The practical role observed in the package is to provide:

- `ISO_639` for multilingual text attributes
- `ISO_3166` and related country-code support

The existence of a family-specific ISO utility file means the official source
bundle duplicated ISO support instead of centralizing it in one shared artifact.

### `XSD/CVNUtilities_v1.0.xsd`

Shared CVN helper catalog reused by the entity package.

The most relevant role visible in this context is that it provides CVN-level
codes such as:

- `CVN_Region`
- `CVN_Province`
- `CVN_STREET_TYPE`

This means entity addresses are not free-form only. They can combine text with
CVN-normalized geopolitical and street-type codes.

### `XML/Entity.xml`

XML instance containing the actual entity catalog.

Observed characteristics from the instance:

- root `Entity` with namespace `http://cv.normalizado.org/entity`
- repeated `item` records using `xmlns=""` for local elements
- multilingual descriptions through `ItemDescription lang="spa"` and, in the
  full file, potentially other languages
- many institutional acronyms such as `CAEND`, `CAR`, `CCHS`, `CINN`, `CIN2`
- address blocks containing country code, city, street, and optional region or
  province

The file behaves as a normalized institutional authority file rather than a
small support list.

Observed scale of the catalog in the preserved XML:

- `16,459` entity records
- language-tagged descriptions observed in:
  - `spa`
  - `cat`
  - `eng`
  - `eus`
  - `glg`
- observed distribution of entity `Type` values includes strong presence of:
  - `080` entity enterprise
  - `100` health institutions
  - `020` university centers and assimilated structures
  - `OTHERS`
- observed function-code distribution includes all four declared function
  classes:
  - `000` research
  - `010` work
  - `020` teaching
  - `030` health

### Real XML Usage Patterns

The preserved XML does not use all schema flexibilities equally.

Observed recurrent patterns:

- all records have `ItemId`
- all records have exactly one `ItemAddress`
- all records have exactly one `Synonym` element, but in most cases that element
  is empty and behaves like a materialized optional container
- `Function`, `Type`, `Nature`, and `URL` appear together in a large enriched
  subset of records, but are absent in many minimal reference records
- `Function` is never repeated in practice even though the XSD allows repeated
  occurrences
- `ItemAncestorId` is effectively singular in practice, even though the XSD
  allows repetition
- `ItemNote` is at most one per entity in the observed data, despite the schema
  allowing repetition
- multilingual `ItemDescription` follows a real-world pattern of either:
  - only `spa`
  - or a five-language bundle with `spa`, `cat`, `eng`, `eus`, `glg`

Observed practical consequences:

- the XML contains both minimal and enriched record profiles
- empty optional nodes often mean “no data” rather than intentional semantic
  content
- a semantic importer should normalize empty present nodes to null-like values

### Address And Identifier Particularities

Observed data behavior makes the following points explicit.

- `CountryCode` is consistently present and overwhelmingly fixed to Spain in the
  observed data
- `Region` and `Province` often exist as empty nodes rather than being omitted
- `PostalCode` appears only in a structured subset of addresses
- `ItemNote` is heavily used as a vehicle for support-side identifiers and, in
  practice, behaves more like an external identifier attachment than like a free
  narrative note
- some URLs are placeholders and not genuine institutional URLs, so semantic
  validation of URL quality must happen outside the XSD layer

### Implications For Semantic Modeling

The observed XML suggests at least two logical record profiles:

- minimal registry entries used as lightweight references
- enriched registry entries with classification, address detail, URL, and
  additional support metadata

This matters for later issues because it suggests that a future domain layer may
need:

- a normalized entity reference concept
- optional enrichment facets
- explicit relationship handling for `Delegate` and ancestor links

### `HTML/Entity_v1.4.html`

HTML rendering of the schema.

This is useful as a navigation aid but does not add normative content beyond the
PDF and XSD.

## Internal Model Of An Entity Record

An entity record combines the following semantic layers.

### Identity Layer

- `ItemId`

### Classification Layer

- `Nature`
- one or more `Function`
- `Type`

### Localization Layer

- `ItemAddress`
  - `CountryCode`
  - repeated `AddressType` by language
  - optional `Region`, `Province`, `PostalCode`, `City`, `Street`, and
    `OtherInformation`

### Naming Layer

- repeated `ItemDescription`
  - `Acronym`
  - `Text`
  - language attribute

### Alias And Maintenance Layer

- `Synonym`
- `ItemNote`
- `Delegate`
- `URL`

## Relationship With The Main CVN Package

The main CVN manual and XML schemas repeatedly refer to entities as controlled
values attached to curriculum fields.

Examples already visible in the project:

- many `SpecificationManual.xml` fields reference `ENTITY@Entity.xsd`
- entity type codes align with `CVN_ENTITY_TYPE`

That means the entity family should be treated as the technical backing for a
large class of institution-valued CVN fields, even though it is packaged
outside the core six files.

## Particularities And Inconsistencies

### Schema Location And Repository Layout Diverge

`Entity.xml` points to `Entity_v1.4.xsd` as if the XSD were colocated with the
XML. In the repository, the XML lives under `XML/` and the schema under `XSD/`.

This is a packaging-layout mismatch in the preserved source bundle.

### Mixed Namespace Style

The root uses the entity namespace, but each `item` resets the default
namespace to empty.

This matches the schema's unqualified local-element strategy but makes the XML
look more irregular than typical namespace-consistent documents.

### Duplicate Utility Strategy

The package keeps family-specific helper schemas such as
`ISOUtilitiesENTITY.xsd` while also relying on broader CVN helper files.

This duplication matters for tooling because identical conceptual tables may
exist in several physical files.

### `Delegate` Carries Operational Semantics

The manual clarifies that `Delegate` is not just a synonym field. It marks a
logical deactivation and points to the replacement `ItemId`.

Any future semantic importer should preserve this as redirection metadata.

## Family 2 - ReferenceTables And Subtypes

## What It Is

This family carries CVN controlled values in structured XML form.

It is the machine-readable representation of the auxiliary tables described in
Annex I of the technical manual, plus a dedicated subtype mapping used by the
operational CVN XML.

In practice, it provides two tightly related resources:

- `ReferenceTables`: catalog of auxiliary tables and their items
- `Subtypes`: bridge from auxiliary-table codes to the `Subtype` property used
  in CVN items

## Files And Roles

### `LeemeREFERENCETABLES.txt`

Quick orientation file.

It states that:

- `ReferenceTables.xsd` validates reference tables
- `Subtypes.xsd` validates curriculum subtypes
- `ReferenceTables.xml` represents tables from the manual's Annex I
- `Subtypes` encodes subtype values

The file contains one naming discrepancy: it speaks about `Subtypes.xml`, while
the actual file in the package is `Subtype_Spa.xml`.

### `Manual/ReferenceTables.pdf`

Human-readable specification of the reference-table model.

This document is essential to understand not just the XML shape but the intended
meaning of:

- table metadata
- item metadata
- hierarchical dependencies through `AntecesorCode`
- delegation through `Delegate`
- the `Link` flag that marks values requiring free-text complement

### `Manual/Subtypes_v1.1.pdf`

Human-readable explanation of how subtype codification works.

Key semantic role:

- explains how a code taken from a reference table is mapped into one or two
  subtype levels in the final CVN XML
- documents `Subtype/SubType1/Item` and `Subtype/SubType2/Item` as the target
  serialization form

### `XSD/ReferenceTables.xsd`

Main schema of the reference-table family.

Root:

- `ReferenceTables`

Structure:

- repeated `Table`
  - repeated `Item`

Per-table metadata includes:

- `name`
- `version`
- `antecesorTable`
- `source`
- `XMLDataType`
- `XMLProperty`
- `XMLIndicator`

Per-item structure includes:

- `Code`
- `Order`
- multilingual `Name`
- `AntecesorCode`
- `Link`
- `ItemNote`
- `Delegate`

This makes the schema useful for both functional documentation and technical
mapping back to CVN XML or XSD constructs.

### `XSD/ISOUtilitiesREFERENCETABLES.xsd`

Family-specific ISO helper schema.

Its direct role is mostly support for multilingual labels through `ISO_639`, and
possibly country coding when tables require it.

### `XSD/Subtypes.xsd`

Schema for subtype mapping.

Root:

- `CVNSubtype`

Structure:

- `Subtype`
  - repeated `Item`

Each subtype item contains:

- attribute `code`: source auxiliary-table code
- `Name`
- `CodeSubtype1`
- optional `CodeSubtype2`

This schema does not encode the full table itself. It encodes the projection of
table values into the subtype slots used by CVN items.

### `XML/ReferenceTables.xml`

Large XML instance that materializes 73 tables and 14,815 item records.

Observed classes of tables include:

- CVN-specific controlled sets such as `CVN_SEX_A`, `CVN_TITLE_B`,
  `CVN_LANGUAGE_B`, `CVN_PUBLICATION_A`, `CVN_SUMMONS_A`, `CVN_SUMMONS_B`
- geopolitical or language standards such as `ISO_3166` and `ISO_639`
- large scientific classification sets such as `UNESCO_CODES`
- metadata-support tables such as `CVN_SOURCE_B`, `CVN_SOURCE_DATO`,
  `CVN_ENTITY_TYPE`, `CVN_THEMATIC_A`, `CVN_THEMATIC_B`

Important operational traits observed in the XML:

- many tables are hierarchical
- `AntecesorCode` is heavily used
- `Delegate` is used as logical redirection
- `ItemNote` is defined structurally but not materially used in the current XML

### `XML/Subtype_Spa.xml`

Spanish-language instance of subtype mappings.

Observed properties:

- `version="1.4.0"`
- 211 regular subtype items plus `OTHERS`
- 90 distinct first-level subtype codes
- 122 items with second-level subtype values

This file is effectively the codification rulebook for `Subtype` values in CVN,
but only in Spanish in the bundled source package.

## Relationship Between Both Subfamilies

The relationship is not merely thematic.

It is operational:

1. a CVN field points to a reference table
2. a table item code is selected
3. `Subtype_Spa.xml` tells which `SubType1` and optional `SubType2` must be
   serialized for that code

This is especially important for values used in publications, projects,
teaching, support types, events, and industrial or intellectual property.

## Relationship With Annex I

`ReferenceTables.xml` is the structured XML representation of Annex I from the
technical manual.

That means Annex I should not be treated only as PDF prose. For most tables, the
project can rely on this XML family as the technical source of record for:

- codes
- labels
- hierarchy
- logical deprecations through delegation

## Particularities And Inconsistencies

### File Naming Drift

- the TXT file mentions `Subtypes.xml`
- the actual file is `Subtype_Spa.xml`

### Version Drift

- `ReferenceTables.xsd` is version `1.0.1`
- `Subtypes.xsd` is version `1.0.0`
- `Subtypes_v1.1.pdf` describes version `1.1`
- `Subtype_Spa.xml` is version `1.4.0`

This means the subtype family evolved over time and the package preserves mixed
version labels.

### PDF And XML Are Not Fully Synchronized

The subtype PDF documents values only up to a lower range than the XML actually
contains. The XML includes later subtype codes such as encyclopedia article,
dissemination article, translation, review, scientific edition, research
software, and dataset.

### `schemaLocation` Layout Mismatch

As with the entity family, XML files reference XSD names as if they were
colocated, but in the repository they are split across `XML/` and `XSD/`.

### Duplicate ISO Utility Strategy

The package contains `ISOUtilitiesREFERENCETABLES.xsd` even though imports and
other package pieces also rely on other ISO utility files.

### Unresolved Table Cases Still Exist

The package resolves a large part of Annex I, but not every referenced table can
be traced cleanly from the package alone. One concrete known example is
`CVN_AGENCY_C`, which appears referenced in the manual but is not clearly backed
by a matching table in `ReferenceTables.xml`.

## Family 3 - Thesaurus

## What It Is

The thesaurus family defines the controlled vocabulary used by CVN for keyword
and subject codification.

It is not a flat keyword list. It is a hierarchical scientific thesaurus with
multilingual labels.

This family is the technical backing for CVN fields that use thesaurus-based
keywords, especially where the manual references `THESAURUS@thesaurus.xsd`.

## Files And Roles

### `LeemeTHESAURUS.txt`

Quick orientation file for the family.

It states that:

- the package is used for keyword codification
- `Thesaurus.xsd` validates the thesaurus XML
- the XML is available in bilingual and monolingual variants
- the HTML file is a rendered schema view

The file itself contains case and naming drift compared with the actual files in
the repository, for example `Thesaurus_eng.xml` versus `Thesaurus_Eng.xml`.

### `Manual/Tesauros 2008-01-23 v1.0.pdf`

Human-readable explanation of the thesaurus model.

Most important semantic points:

- the thesaurus is intended for codifying keywords
- the structure is hierarchical
- the identifier encodes hierarchical position
- aliases, notes, and logical delegation are part of the model even if sparsely
  used in the bundled XML

### `XSD/Thesaurus.xsd`

Main thesaurus schema.

Root:

- `Thesaurus`

Repeated element:

- `item`

Each item contains:

- `itemId`
- `itemOrder`
- optional `itemAncestorId`
- repeated multilingual `itemDescription`
- optional `itemNote`
- optional `delegate`

`itemDescription` is based on a multilingual type with one or more `NameDetail`
elements carrying:

- `Name`
- optional `ShortName`
- `lang`

### `XSD/ISOUtilitiesTHESAURUS.xsd`

Family-specific ISO helper schema, mainly used to validate `lang` through
`ISO_639`.

### `XML/Thesaurus.xml`

Bilingual thesaurus instance.

Observed characteristics:

- 6,178 total items
- 4 root categories
- maximum observed depth of 8 hierarchy levels
- same identifier set as the monolingual variants

The four roots correspond to major disciplinary macroareas such as physics and
chemistry, life sciences and health, engineering, and humanities and social
sciences.

### Real XML Usage Patterns

The preserved thesaurus XML shows several stable practical patterns.

- `itemId` values are stable 24-digit numeric identifiers
- hierarchical structure is expressed through `itemAncestorId`
- the four observed roots anchor the entire taxonomy and the remaining nodes
  descend from them
- the bilingual file and the monolingual files share the same logical item set
  and differ mainly in language projection

The real XML does not use all schema affordances equally.

Observed behavior:

- `itemNote` appears to be absent in normal data use
- `delegate` appears absent in normal data use
- `ShortName` is structurally supported but not a major differentiator in the
  preserved dataset
- multilingual modeling is implemented in practice by repeating description
  blocks per language rather than packing all languages into one more compact
  structure

### Implications For Semantic Modeling

The thesaurus should be treated as:

- a hierarchical external subject vocabulary
- a code-and-label system with multilingual resolution
- a reusable semantic asset distinct from ordinary CVN enums

This means later issues should preserve at minimum:

- stable code
- parent-child structure
- preferred-language label resolution
- the possibility of treating the bilingual XML as canonical and the mono-language
  XML files as projections

### `XML/Thesaurus_Eng.xml`

English-only projection of the thesaurus.

It keeps the same logical items and identifiers but only includes English labels.

### `XML/Thesaurus_Spa.xml`

Spanish-only projection of the thesaurus.

It keeps the same logical items and identifiers but only includes Spanish labels.

### `HTML/Thesaurus.html`

HTML representation of the schema.

Useful as a navigation aid, but secondary to the XSD and PDF.

## Multilingual Model

The family is multilingual by design.

Language is expressed with `NameDetail/@lang` and validated with `ISO_639`.

The package preserves three publication forms of the same logical thesaurus:

- bilingual combined file
- English-only file
- Spanish-only file

This matters for future tooling because it enables either:

- one canonical multilingual import
- or per-language projections depending on use case

## Hierarchical Nature

The thesaurus is clearly hierarchical.

Evidence:

- `itemAncestorId` links each term to its parent
- the manual describes hierarchical organization
- observed `itemId` values are 24-digit numeric strings with hierarchical block
  behavior and right-zero padding

This means the thesaurus is closer to a scientific taxonomy or subject tree than
to a simple tag list.

## Relationship With The Main CVN Package

The main CVN package does not import `Thesaurus.xsd` directly into `CVN.xsd` as
a typed foreign schema. Instead, thesaurus usage is indirect and conventional.

Relevant pattern in the core CVN model:

- subject or keyword structures use string wrappers with optional coded values
- controlled usage depends on functional metadata from the manual

Operational consequence:

- future tooling should treat thesaurus IDs as controlled external codes carried
  by CVN value wrappers, not as XSD-native enum values inside the main CVN
  schema

## Particularities And Inconsistencies

### File Naming Drift

- the TXT file uses `Thesaurus_eng.xml` and `Thesaurus_esp.xml`
- the repository files are `Thesaurus_Eng.xml` and `Thesaurus_Spa.xml`

### Import Name Drift

`Thesaurus.xsd` imports `ISOUtilities.xsd`, but the repository also ships a
family-specific `ISOUtilitiesTHESAURUS.xsd`.

### Mixed Namespace Style

As in other auxiliary families, XML root elements use the family namespace but
local `item` records reset the default namespace to empty. This is valid given
the schema settings, but structurally irregular.

### Structurally Supported But Mostly Unused Fields

The schema supports:

- `itemNote`
- `delegate`
- `ShortName`

In the bundled XML, these fields appear to be sparsely used or absent in normal
catalog records.

### Real Data Quality Issues Exist

The real thesaurus content contains spelling or normalization issues in some
labels. Future tooling should therefore distinguish:

- schema validity
- semantic cleanliness of labels

## Cross-Family Relationship Summary

The three auxiliary families play distinct roles.

### Entity

- normalized institution and organization registry

### ReferenceTables/Subtypes

- official controlled-value catalogs and subtype codification rules

### Thesaurus

- hierarchical keyword vocabulary

Together they supply the parts of the official source package that are not fully
captured by the core CVN structural schemas, but are necessary to interpret many
manual references correctly.

## Recommended Reading Order For These Families

1. `LeemeENTITY.txt`
2. `Manual/Entidades_esquema_Entity_v1.4.xsd_2008-07-04 v1.0.pdf`
3. `XSD/Entity_v1.4.xsd`
4. `XML/Entity.xml`
5. `LeemeREFERENCETABLES.txt`
6. `Manual/ReferenceTables.pdf`
7. `Manual/Subtypes_v1.1.pdf`
8. `XSD/ReferenceTables.xsd`
9. `XML/ReferenceTables.xml`
10. `XML/Subtype_Spa.xml`
11. `LeemeTHESAURUS.txt`
12. `Manual/Tesauros 2008-01-23 v1.0.pdf`
13. `XSD/Thesaurus.xsd`
14. `XML/Thesaurus.xml`

## Why These Families Matter To Later Issues

They directly affect later semantic work because they answer questions that the
core structural bindings alone cannot settle cleanly.

Examples:

- which institution-valued fields point to an external entity catalog
- which manual reference tables already have machine-readable XML backing
- which subtype encodings are derived from auxiliary-table codes
- which keyword fields rely on a hierarchical thesaurus rather than a flat enum

That makes these families especially relevant for:

- issue `#14` semantic mapping rules
- issue `#15` domain model generation
- future documentation work around CVN controlled values and external references
