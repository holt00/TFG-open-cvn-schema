# CVN Annex Table Families Batch 7

## Purpose

This document continues the detailed Annex I reference set and records the table
families centered on agencies, collaboration, and cooperation.

This batch covers:

- `CVN_AGENCY_A`
- `CVN_AGENCY_B`
- `CVN_AGENCY_C`
- `CVN_COLLABORATION_A`
- `CVN_COOPERANTION_A`

This batch is especially important because it includes one of the few explicit
cases where the manual references a table that is not actually present as a
matching `ReferenceTables.xml` table.

## Family 1 - `CVN_AGENCY_*`

## Overview

The `CVN_AGENCY_*` family is not homogeneous.

- `CVN_AGENCY_A`: types of agencies or selection/evaluation bodies in R&D and
  related contexts
- `CVN_AGENCY_B`: source agency for impact indicators
- `CVN_AGENCY_C`: source agency for H-index, referenced by the manual but not
  materialized as a matching table in `ReferenceTables.xml`

This means the family already demonstrates a split between:

- fully materialized reference tables
- unresolved manual references

## `CVN_AGENCY_A`

### Table Metadata

- version: `1.0.2`
- source: `CVN`
- `XMLDataType`: `CVN_Value_Filter@AuxTable.xsd`
- `XMLProperty`: `Filter`
- `XMLIndicator`: `Value`

### Observed Structure

- items: `6`
- `Link=true`: `0`
- delegated items: `0`
- hierarchy: none

### Values

- `1060` -> `Agencias financiadoras de I+D+I públicas`
- `1070` -> `Agencias financiadoras de I+D+I privadas sin ánimo de lucro`
- `1080` -> `Agencias de selección de personal investigador o técnico o gestor de I+D+I`
- `1090` -> `Agencias de opinión oficial`
- `1100` -> `Agencias de opinión pública`
- `1110` -> `Agencias de evaluación del sistema de I+D+I`

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- `060.020.040.190` profile of recipient group in R&D management contexts

### Semantic Interpretation

This is a classifier of agency or institutional function, not a specific list of
named agencies.

It is appropriate as a small enum-like table, but only within the semantic scope
of agency category.

## `CVN_AGENCY_B`

### Table Metadata

- version: `1.0.2`
- source: `CVN`
- `XMLDataType`: `CVN_QualityAgencyType@AuxTable.xsd`
- `XMLProperty`: `Quality`
- `XMLIndicator`: `Agency`

### Observed Structure

- items: `4`
- `Link=true`: `1`
- delegated items: `0`
- hierarchy: none

### Values

- `000` -> `WOS (JCR)`
- `010` -> `SCOPUS (SJR)`
- `020` -> `INRECS`
- `OTHERS` -> `Otros`

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- `060.010.010.190` impact-source field for publications

### Semantic Interpretation

This is a compact bibliometric impact-source table.

Its semantics are close to, but not identical with, the `CVN_SOURCE_*` family:

- `CVN_SOURCE_A` classified citation-count sources
- `CVN_AGENCY_B` classifies impact-index source agencies or systems

That distinction should remain explicit in the semantic layer.

## `CVN_AGENCY_C`

### Observed Situation

The manual references `CVN_AGENCY_C`, but `ReferenceTables.xml` does not contain
a table named `CVN_AGENCY_C`.

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- `060.010.000.030` source of H-index

The surrounding manual fields define:

- value of H-index
- date of H-index application
- source of H-index

### Why It Matters

This is one of the clearest package inconsistencies for later semantic work.

`CVN_AGENCY_C` is not just undocumented in the repository. It appears absent from
the machine-readable `ReferenceTables.xml` material.

### Practical Semantic Treatment

For now, the safest treatment is:

- do not model it as a closed resolved enum
- document it as an unresolved manual-only table reference
- keep the source field open or explicitly backed by a manual-review policy

### Additional Note

`CVN_CATEGORY_A` and `CVN_CATEGORY_B` both declare `antecesorTable="CVN_AGENCY_B"`
in `ReferenceTables.xml`, which means future category-family work should be read
together with `CVN_AGENCY_B` rather than in isolation.

## Family 2 - `CVN_COLLABORATION_A`

### Table Metadata

- version: `1.0.2`
- source: `CVN`
- `XMLDataType`: `CVN_Value_Filter@AuxTable.xsd`
- `XMLProperty`: `Filter`
- `XMLIndicator`: `Value`

### Observed Structure

- items: `7`
- `Link=true`: `1`
- delegated items: `0`
- hierarchy: none

### Values

- `1010` -> `Publicaciones cofirmadas`
- `1020` -> `Cogestión`
- `1030` -> `Participación en convenios de colaboración de larga duración entre entidades`
- `840` -> `Proyectos coordinados`
- `900` -> `Redes con proyecto conjunto`
- `910` -> `Redes sin proyecto conjunto`
- `OTHERS` -> `Otros`

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- `060.020.020.010` mode of relationship in collaborations with other
  researchers or technologists

### Semantic Interpretation

This is a collaboration-mode classifier focused on institutional or project
relationship patterns.

It is broader than coauthorship alone and includes both joint publications and
networked or coordinated structures.

Recommended semantic treatment:

- enum candidate with `OTHERS`
- keep distinct from the narrower cooperation-class table

## Family 3 - `CVN_COOPERANTION_A`

### Naming Note

The table name preserves the spelling `COOPERANTION`, not `COOPERATION`.

This appears to be a historical naming artifact and should be preserved exactly
at the source-traceability level.

## Table Metadata

- version: `1.0.1`
- source: `CVN`
- `XMLDataType`: `CVN_Value_Filter@AuxTable.xsd`
- `XMLProperty`: `Filter`
- `XMLIndicator`: `Value`

### Observed Structure

- items: `6`
- `Link=true`: `0`
- delegated items: `0`
- hierarchy: none

### Values

- `070` -> `Coautoría de cooperación internacional`
- `080` -> `Coautoría de modos protegidos de tecnología`
- `090` -> `Coautoría de proyectos y de su desarrollo`
- `100` -> `Coautoría de publicaciones`
- `110` -> `Coautoría coop con terceras entidades nacionales`
- `120` -> `Colaboración en formación a terceros`

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- `050.010.000.160` class of collaboration inside research-group participation

### Semantic Interpretation

This is a narrower and more collaboration-form-specific table than
`CVN_COLLABORATION_A`.

It focuses on the nature of cooperation itself, especially coauthorship and
joint work patterns.

Recommended semantic treatment:

- enum candidate
- preserve the original source spelling for traceability
- expose a cleaner internal name only if later generation explicitly documents
  the aliasing rule

## Batch-7 Conclusions

This batch adds two especially relevant modeling lessons.

### Lesson 1 - Not Every Manual Reference Has A Matching Technical Table

`CVN_AGENCY_C` is the clearest current example.

This reinforces the repository rule already documented elsewhere:

- semantic generation must distinguish resolved machine-backed tables from
  manual-only unresolved references

### Lesson 2 - Collaboration And Cooperation Are Close But Not Equivalent

- `CVN_COLLABORATION_A` classifies broader collaboration modes
- `CVN_COOPERANTION_A` classifies more specific cooperation forms

These should not be collapsed into one generic field without losing semantic
resolution.

## Recommended Semantic Treatment For This Batch

### Strong Enum Candidates

- `CVN_AGENCY_A`
- `CVN_AGENCY_B`
- `CVN_COLLABORATION_A`
- `CVN_COOPERANTION_A`

### Unresolved Manual-Only Case

- `CVN_AGENCY_C`

This should remain explicitly unresolved until a technical backing source is
identified or an override policy is defined.

## Reading Path

This document should be read after:

- `docs/cvn_annex_priority_table_families.md`
- `docs/cvn_annex_table_families_batch3.md`
- `docs/cvn_annex_table_families_batch4.md`
- `docs/cvn_annex_table_families_batch5.md`
- `docs/cvn_annex_table_families_batch6.md`
