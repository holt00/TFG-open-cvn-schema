# CVN Annex Table Families Batch 5

## Purpose

This document continues the detailed Annex I reference set and records the next
group of table families relevant to semantic interpretation of the CVN package.

This batch covers:

- `CVN_SUBJECT_A`
- `CVN_STAY_A`
- `CVN_STAY_B`
- `CVN_DEDICATION_A`
- `CVN_DURATION_A`
- `CVN_FORMATION_A`
- `CVN_TEACHING_A`
- `CVN_TEACHING_B`
- `CVN_PRIZE_A`
- `CVN_THEMATIC_A`
- `CVN_THEMATIC_B`

The analysis is based on the real content of:

- `XML/ReferenceTables.xml`
- `XML/SpecificationManual.xml`

## Family 1 - `CVN_SUBJECT_A`

### Table Metadata

- version: `1.0.3`
- source: `CVN`
- `XMLDataType`: `CVN_Value_Filter@AuxTable.xsd`
- `XMLProperty`: `Filter`
- `XMLIndicator`: `Value`

### Observed Structure

- items: `7`
- `Link=true`: `1`
- delegated items: `1`
- hierarchy: none

### Representative Values

- `000` -> `Troncal`
- `010` -> `Obligatoria`
- `020` -> `Optativa`
- `030` -> `Libre configuración`
- `050` -> `Doctorado/a`
- `060` -> `Otros` delegated to `OTHERS`
- `OTHERS` -> `Otros`, with `Link=true`

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- `030.010.000.190` type of subject in teaching records

### Semantic Interpretation

This is a compact academic-subject classification table.

Important detail:

- the package keeps both `060` and `OTHERS` in an explicit delegation relation,
  so the semantic layer should preserve compatibility metadata and not assume
  they are two independent categories

## Family 2 - `CVN_STAY_*`

## Overview

The `CVN_STAY_*` family splits two different dimensions of a stay.

- `CVN_STAY_A`: objective or condition of the stay
- `CVN_STAY_B`: type of stay by activity domain

## `CVN_STAY_A`

### Table Metadata

- version: `1.0.2`
- source: `CVN`
- `XMLDataType`: `CVN_Value_Filter@AuxTable.xsd`
- `XMLProperty`: `Filter`
- `XMLIndicator`: `Value`

### Observed Structure

- items: `5`
- `Link=true`: `1`
- delegated items: `0`

### Values

- `150` -> `Contratado/a`
- `250` -> `Doctorado/a`
- `450` -> `Invitado/a`
- `670` -> `Posdoctoral`
- `OTHERS` -> `Otros`

### Usage In `SpecificationManual.xml`

Observed references: `2`

Used in:

- objective of academic stay fields
- objective of scientific or research stay fields

### Semantic Interpretation

This is a compact stay-status or stay-purpose classifier.

## `CVN_STAY_B`

### Table Metadata

- version: `1.0.2`
- source: `CVN`
- `XMLDataType`: `CVN_Value_Filter@AuxTable.xsd`
- `XMLProperty`: `Filter`
- `XMLIndicator`: `Value`

### Observed Structure

- items: `4`
- `Link=true`: `0`
- delegated items: `0`

### Values

- `010` -> `Investigación`
- `020` -> `Innovación`
- `030` -> `Docencia`
- `040` -> `Desarrollo Tecnológico`

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- type of stay in research-center stay records

### Semantic Interpretation

This is a clean activity-domain classifier for stays and a strong enum candidate.

## Family 3 - `CVN_DEDICATION_A`

### Table Metadata

- version: `1.0.1`
- source: `CVN`
- `XMLDataType`: `CVN_DedicationType@AuxTable.xsd`
- `XMLProperty`: `Dedication`
- `XMLIndicator`: none

### Observed Structure

- items: `2`
- `Link=true`: `0`
- delegated items: `0`

### Values

- `020` -> `Tiempo completo`
- `030` -> `Tiempo parcial`

### Usage In `SpecificationManual.xml`

Observed references: `6`

Used across:

- current professional situation
- past professional situation
- teaching innovation projects
- health innovation projects
- planning and management projects
- competitive R&D projects

### Semantic Interpretation

This is one of the most reusable cross-cutting tables in the package.

Recommended treatment:

- shared enum candidate used across multiple domain sections

## Family 4 - `CVN_DURATION_A`

### Table Metadata

- version: `1.0.2`
- source: `CVN`
- `XMLDataType`: `CVN_Value_Filter@AuxTable.xsd`
- `XMLProperty`: `Filter`
- `XMLIndicator`: `Value`

### Observed Structure

- items: `2`
- `Link=true`: `0`
- delegated items: `0`

### Values

- `1120` -> `Por tiempo determinado`
- `1130` -> `De duración indeterminada o indefinida`

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- type of labor relationship duration in teaching innovation projects

### Semantic Interpretation

Simple binary temporal-regime classifier.

## Family 5 - `CVN_FORMATION_A`

### Table Metadata

- version: `1.0.2`
- source: `CVN`
- `XMLDataType`: `Subtype@Subtypes.xsd`
- `XMLProperty`: `Subtype`

### Observed Structure

- items: `4`
- `Link=true`: `0`
- delegated items: `0`

### Values

- `034` -> `Máster`
- `050` -> `Postgrado`
- `178` -> `Extensión Universitaria`
- `179` -> `Especialidad`

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- `020.010.030.010` type of postgraduate formation

### Semantic Interpretation

This is a small postgraduate formation family, but it uses subtype-based
serialization and therefore belongs with the subtype-aware group of tables.

## Family 6 - `CVN_TEACHING_*`

## Overview

The `CVN_TEACHING_*` family separates:

- `CVN_TEACHING_A`: broad teaching kind
- `CVN_TEACHING_B`: teaching modality

## `CVN_TEACHING_A`

### Table Metadata

- version: `1.0.0`
- source: `CVN`
- `XMLDataType`: `Subtype@Subtypes.xsd`
- `XMLProperty`: `Subtype`

### Observed Structure

- items: `3`
- `Link=true`: `0`
- delegated items: `0`

### Values

- `014` -> `Docencia internacional`
- `015` -> `Docencia no oficial`
- `016` -> `Docencia oficial`

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- `030.010.000.010` broad type of academic teaching

### Semantic Interpretation

This is a compact teaching-kind classifier using subtype serialization.

## `CVN_TEACHING_B`

### Table Metadata

- version: `1.0.2`
- source: `CVN`
- `XMLDataType`: `CVN_Value_Filter@AuxTable.xsd`
- `XMLProperty`: `Filter`
- `XMLIndicator`: `Value`

### Observed Structure

- items: `6`
- `Link=true`: `1`
- delegated items: `0`

### Values

- `060` -> `Clínico`
- `700` -> `Prácticas de Laboratorio`
- `705` -> `Práctica (Aula-Problemas)`
- `840` -> `Teórica presencial`
- `860` -> `Virtual`
- `OTHERS` -> `Otros`

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- `030.010.000.170` teaching modality

### Semantic Interpretation

This is a modality table, not a teaching-domain or teaching-level table.

## Family 7 - `CVN_PRIZE_A`

### Table Metadata

- version: `1.0.0`
- source: `CVN`
- `XMLDataType`: `CVN_Value_Filter@AuxTable.xsd`
- `XMLProperty`: `Filter`
- `XMLIndicator`: `Value`

### Observed Structure

- items: `3`
- `Link=true`: `0`
- delegated items: `0`

### Values

- `000` -> `Premio extraordinario de licenciatura`
- `010` -> `Premio fin de carrera`
- `OTHERS` -> `Otros`

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- university-study prize fields

### Semantic Interpretation

Small academic-prize classifier.

## Family 8 - `CVN_THEMATIC_*`

## Overview

The `CVN_THEMATIC_*` family appears in two clearly different contexts.

- `CVN_THEMATIC_A`: thematic orientation of teaching-support events
- `CVN_THEMATIC_B`: type of artistic or professional contribution

## `CVN_THEMATIC_A`

### Table Metadata

- version: `1.0.2`
- source: `CVN`
- `XMLDataType`: `CVN_Value_Filter@AuxTable.xsd`
- `XMLProperty`: `Filter`
- `XMLIndicator`: `Value`

### Observed Structure

- items: `2`
- `Link=true`: `0`
- delegated items: `0`

### Values

- `010` -> `Formación Docente`
- `020` -> `Otra Temáctica`

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- thematic orientation of teaching-support courses and seminars

### Semantic Interpretation

Simple binary thematic classifier.

## `CVN_THEMATIC_B`

### Table Metadata

- version: `1.0.2`
- source: `CVN`
- `XMLDataType`: `CVN_Value_Filter@AuxTable.xsd`
- `XMLProperty`: `Filter`
- `XMLIndicator`: `Value`

### Observed Structure

- items: `5`
- `Link=true`: `0`
- delegated items: `0`

### Values

- `010` -> `Creación artística y creativa`
- `020` -> `Proyecto arquitectónico, urbanístico, patrimoniales o de ingeniería`
- `030` -> `Proyecto artístico`
- `040` -> `Proyecto de conservación o restauración`
- `OTHERS` -> `Otros`

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- type of artistic or professional contribution

### Semantic Interpretation

Compact thematic or contribution-type classifier for artistic and professional
output.

## Batch-5 Conclusions

This batch strengthens two more semantic patterns.

### Pattern 1 - Some Small Tables Are Reused Across Many Domains

Especially:

- `CVN_DEDICATION_A`
- `CVN_STAY_A`
- `CVN_STAY_B`

These look small, but they recur in several independent curriculum blocks and
should therefore be modeled as shared domain enums.

### Pattern 2 - Several Apparently Simple Tables Still Depend On `Subtype`

Affected in this batch:

- `CVN_FORMATION_A`
- `CVN_TEACHING_A`

and, from prior batches, also publication, support, and event tables.

This confirms that subtype-aware policy remains a cross-cutting requirement for
issue `#14`.

## Recommended Semantic Treatment For This Batch

### Strong Shared Enum Candidates

- `CVN_DEDICATION_A`
- `CVN_DURATION_A`
- `CVN_STAY_A`
- `CVN_STAY_B`
- `CVN_PRIZE_A`
- `CVN_THEMATIC_A`
- `CVN_THEMATIC_B`

### Enum Candidates With Compatibility Detail

- `CVN_SUBJECT_A`
  - because of explicit delegation from `060` to `OTHERS`

### Subtype-Aware Controlled Families

- `CVN_FORMATION_A`
- `CVN_TEACHING_A`

### Context-Specific Mode Classifier

- `CVN_TEACHING_B`

## Reading Path

This document should be read after:

- `docs/cvn_annex_priority_table_families.md`
- `docs/cvn_annex_table_families_batch3.md`
- `docs/cvn_annex_table_families_batch4.md`
