# CVN Annex Table Families Batch 8

## Purpose

This document closes the detailed Annex I reference sweep across the remaining
table families that still required dedicated treatment.

This batch covers:

- `CVN_KNOW_A`
- `CVN_INTERVENTION_A`
- `CVN_SUPERVISION_A`
- `CVN_SUPERVISION_B`
- `CVN_CATEGORY_A`
- `CVN_CATEGORY_B`
- `CVN_PRUEBA`

This batch is slightly different from earlier ones because it includes two
tables that are present in `ReferenceTables.xml` but do not appear to be
referenced by `SpecificationManual.xml`:

- `CVN_INTERVENTION_A`
- `CVN_PRUEBA`

It also includes `CVN_KNOW_A`, which is a compact but important subtype-backed
table for industrial property classes.

## Family 0 - `CVN_KNOW_A`

### Table Metadata

- version: `1.0.0`
- source: `CVN`
- `XMLDataType`: `Subtype@Subtypes.xsd`
- `XMLProperty`: `Subtype`
- `XMLIndicator`: none

### Observed Structure

- items: `6`
- `Link=true`: `1`
- delegated items: `0`
- hierarchy: none

### Values

- `109` -> `Diseños industriales`
- `122` -> `Marcas`
- `126` -> `Modelo de utilidad`
- `141` -> `Patente de invención`
- `177` -> `Variedades vegetales`
- `OTHERS` -> `Otros`

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- `050.030.010.030` type of industrial property

### Semantic Interpretation

This is a compact industrial-property classifier, but it uses subtype-based
serialization rather than the more common filter/value pattern.

That makes it relevant both for semantic modeling of industrial and intellectual
property and for the repository-wide subtype policy.

## Family 1 - `CVN_INTERVENTION_A`

### Table Metadata

- version: `1.0.0`
- source: `CVN`
- `XMLDataType`: `CVN_Value_Filter@AuxTable.xsd`
- `XMLProperty`: `Filter`
- `XMLIndicator`: `Value`

### Observed Structure

- items: `4`
- `Link=true`: `0`
- delegated items: `0`
- hierarchy: none

### Values

- `000` -> `Ponente`
- `010` -> `Por invitación`
- `020` -> `Poster`
- `OTHERS` -> `Otros`

### Usage In `SpecificationManual.xml`

Observed references: `0`

### Semantic Interpretation

This table looks like a compact intervention or presentation-mode classifier.

It is semantically close to event participation and presentation tables, but at
least in the current source package it is not referenced from
`SpecificationManual.xml`.

### Practical Status

For the project, this should be treated as:

- technically present in the source package
- semantically under-traced from the manual layer

It should not be discarded, but it should also not be treated as a confirmed
high-importance table until a clearer use site is identified.

## Family 2 - `CVN_SUPERVISION_*`

## Overview

The `CVN_SUPERVISION_*` family models how participation or contribution happened
in relation to events.

- `CVN_SUPERVISION_A`: richer event access or intervention mode table
- `CVN_SUPERVISION_B`: very small event-intervention table

## `CVN_SUPERVISION_A`

### Table Metadata

- version: `1.0.1`
- source: `CVN`
- `XMLDataType`: `CVN_Value_Filter@AuxTable.xsd`
- `XMLProperty`: `Filter`
- `XMLIndicator`: `Value`

### Observed Structure

- items: `5`
- `Link=true`: `1`
- delegated items: `0`

### Values

- `000` -> `Acceso por inscripción libre`
- `770` -> `Revisión previa a la aceptación`
- `879` -> `Por invitación`
- `880` -> `En representación de`
- `OTHERS` -> `Otros`

### Usage In `SpecificationManual.xml`

Observed references: `2`

Used in:

- `060.010.020.060` intervention mode in congress submissions
- `060.010.040.040` intervention mode in dissemination activities

### Semantic Interpretation

This is not a content-type table. It captures the access mode or representational
mode through which the participation happened.

Recommended semantic treatment:

- enum candidate
- should remain separate from `CVN_PARTICIPATION_E`, because the latter models
  participation role, while `CVN_SUPERVISION_A` models access or intervention
  channel

## `CVN_SUPERVISION_B`

### Table Metadata

- version: `1.0.1`
- source: `CVN`
- `XMLDataType`: `CVN_Value_Filter@AuxTable.xsd`
- `XMLProperty`: `Filter`
- `XMLIndicator`: `Value`

### Observed Structure

- items: `2`
- `Link=true`: `0`
- delegated items: `0`

### Values

- `600` -> `Ponente`
- `879` -> `Por invitación`

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- `060.010.030.040` intervention mode in non-congress scientific events

### Semantic Interpretation

This is a much narrower intervention-mode table than `CVN_SUPERVISION_A`.

It should likely remain context-scoped instead of being merged mechanically with
`CVN_SUPERVISION_A`.

## Family 3 - `CVN_CATEGORY_*`

## Overview

The `CVN_CATEGORY_*` family is related to ranking or recognition categories, but
its two visible tables belong to different semantic spaces.

- `CVN_CATEGORY_A`: publication indexing or impact-category space
- `CVN_CATEGORY_B`: evaluated-period recognition or formal program category

Both tables declare `antecesorTable="CVN_AGENCY_B"`, which creates an explicit
technical dependency on the bibliometric-source family.

## `CVN_CATEGORY_A`

### Table Metadata

- version: `1.0.0`
- `antecesorTable`: `CVN_AGENCY_B`
- source: `CVN`
- `XMLDataType`: `CVN_Value_Filter@AuxTable.xsd`
- `XMLProperty`: `Filter`
- `XMLIndicator`: `Value`

### Observed Structure

- items: `547`
- `Link=true`: `0`
- delegated items: `0`
- items with `AntecesorCode`: `547`

### Representative Values

- `000010` -> `Science Edition - ACOUSTICS`
- `000020` -> `Science Edition - AGRICULTURAL ECONOMICS & POLICY`
- `000030` -> `Science Edition - AGRICULTURAL ENGINEERING`
- `000060` -> `Science Edition - AGRONOMY`
- `000080` -> `Science Edition - ANATOMY & MORPHOLOGY`
- `000110` -> `Science Edition - ASTRONOMY & ASTROPHYSICS`

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- `060.010.010.240` category of publication or journal classification

### Semantic Interpretation

This is a large controlled category catalog for indexed publication categories.

The explicit parent relation to `CVN_AGENCY_B` strongly suggests that category
codes are meaningful only relative to the source agency or indexing system.

Recommended semantic treatment:

- not a flat global enum
- better represented as a lookup catalog whose interpretation may depend on the
  impact-source system

## `CVN_CATEGORY_B`

### Table Metadata

- version: `1.0.0`
- `antecesorTable`: `CVN_AGENCY_B`
- source: `CVN`
- `XMLDataType`: `CVN_Value_Filter@AuxTable.xsd`
- `XMLProperty`: `Filter`
- `XMLIndicator`: `Value`

### Observed Structure

- items: `3`
- `Link=true`: `0`
- delegated items: `0`

### Values

- `010` -> `Sexenio CNEAI`
- `020` -> `Quinquenio`
- `OTHERS` -> `Otros`

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- `060.030.070.160` name of recognition program or evaluated-period action

### Semantic Interpretation

This is a compact formal-recognition category table.

Unlike `CVN_CATEGORY_A`, it behaves like a small stable enum candidate.

## Family 4 - `CVN_PRUEBA`

### Table Metadata

- version: `1.0.0`
- source: `CVN`
- `XMLDataType`: `CVN_Value_Filter@AuxTable.xsd`
- `XMLProperty`: `Filter`
- `XMLIndicator`: `Value`

### Observed Structure

- items: `4`
- `Link=true`: `0`
- delegated items: `0`

### Values

- `000` -> `WOS`
- `001` -> `GOOGLE SCHOLAR`
- `010` -> `SCOPUS`
- `OTHERS` -> `Otros`

### Usage In `SpecificationManual.xml`

Observed references: `0`

### Semantic Interpretation

This looks like a test or provisional bibliometric-source table, or a side
artifact related to citation or quality-source classification.

At least in the current source package, it is present technically but has no
clear manual trace.

### Practical Status

For the repository, this should be treated as:

- technically present
- currently unreferenced from `SpecificationManual.xml`
- lower semantic priority than `CVN_SOURCE_A` or `CVN_AGENCY_B`

## Batch-8 Conclusions

This final batch closes the detailed table sweep with three useful conclusions.

### Conclusion 1 - The Package Contains More Than The Manual Currently Uses

`CVN_INTERVENTION_A` and `CVN_PRUEBA` are concrete examples of tables that exist
in `ReferenceTables.xml` but do not currently appear referenced from
`SpecificationManual.xml`.

That means the source package should be treated as:

- richer than the immediately visible manual references
- but not all technically present tables have equal semantic status

### Conclusion 2 - `CVN_CATEGORY_A` Is Closer To A Lookup Catalog Than To An Enum

Its size, parent dependency, and indexing-system semantics make it materially
different from the small compact tables documented elsewhere.

### Conclusion 3 - `CVN_SUPERVISION_*` Should Stay Distinct From Participation

The supervision tables classify access or intervention mode, while the
participation tables classify roles or contribution types.

Even though both appear in event contexts, they should remain distinct in the
semantic layer.

## Recommended Semantic Treatment For This Batch

### Strong Enum Candidates

- `CVN_SUPERVISION_A`
- `CVN_SUPERVISION_B`
- `CVN_CATEGORY_B`

### Lookup Catalog Candidate

- `CVN_CATEGORY_A`

### Present But Functionally Under-Traced Tables

- `CVN_INTERVENTION_A`
- `CVN_PRUEBA`

### Strong Enum Candidate With Subtype Serialization

- `CVN_KNOW_A`

These should be preserved in documentation and source coverage, but kept below
the priority level of heavily reused and manual-backed tables.

## Reading Path

This document should be read after:

- `docs/cvn_annex_priority_table_families.md`
- `docs/cvn_annex_table_families_batch3.md`
- `docs/cvn_annex_table_families_batch4.md`
- `docs/cvn_annex_table_families_batch5.md`
- `docs/cvn_annex_table_families_batch6.md`
- `docs/cvn_annex_table_families_batch7.md`
