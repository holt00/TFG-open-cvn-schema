# CVN Annex Table Families Batch 4

## Purpose

This document continues the detailed Annex I reference set and records the next
group of table families relevant to semantic interpretation of the CVN package.

This batch covers:

- `CVN_ACTIVITY_*`
- `CVN_MANAGEMENT_*`
- `CVN_SCOPE_*`
- `CVN_LANGUAGE_B`
- `CVN_TIME_A`
- `CVN_QUALIFICATION_*`
- `CVN_ACCESS_A`
- `CVN_EVALUATION_A`

The analysis is based on the real content of:

- `XML/ReferenceTables.xml`
- `XML/SpecificationManual.xml`

## Family 1 - `CVN_ACTIVITY_*`

## Overview

The `CVN_ACTIVITY_*` family does not encode one generic abstract activity. It is
split across context-specific meanings.

- `CVN_ACTIVITY_A`: modality of evaluation or review activity in R&D contexts
- `CVN_ACTIVITY_B`: training activity type, serialized through `Subtype`
- `CVN_ACTIVITY_D`: type of evaluated period or recognized activity

## `CVN_ACTIVITY_A`

### Table Metadata

- version: `1.0.1`
- source: `CVN`
- `XMLDataType`: `CVN_Value_Filter@AuxTable.xsd`
- `XMLProperty`: `Filter`
- `XMLIndicator`: `Value`

### Observed Structure

- items: `4`
- `Link=true`: `1`
- delegated items: `0`
- hierarchy: none

### Values

- `580` -> `Participación en comités editoriales`
- `590` -> `Participación en tribunales`
- `760` -> `Revisión de artículos en revistas científicas o tecnológicas`
- `OTHERS` -> `Otros`

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- `060.020.060.060` modality of evaluation/review activity

### Semantic Interpretation

This is a compact classifier for scientific evaluation and review activities.

Recommended treatment:

- enum candidate
- keep `OTHERS` support because the manual explicitly leaves room for open
  categories

## `CVN_ACTIVITY_B`

### Table Metadata

- version: `1.0.1`
- source: `CVN`
- `XMLDataType`: `Subtype@Subtypes.xsd`
- `XMLProperty`: `Subtype`

### Observed Structure

- items: `4`
- `Link=true`: `1`
- delegated items: `0`
- hierarchy: none

### Values

- `011` -> `Curso`
- `051` -> `Prácticas`
- `184` -> `Estancias`
- `OTHERS` -> `Otros`

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- `020.020.000.010` type of specialized training

### Semantic Interpretation

This table is small, but important because it uses subtype serialization instead
of the usual filter/value pattern.

Recommended treatment:

- subtype-aware enum candidate

## `CVN_ACTIVITY_D`

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

- `000` -> `Investigación`
- `010` -> `Transferencia de conocimiento`
- `020` -> `Docencia`
- `OTHERS` -> `Otros`

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- `060.030.070.170` type of evaluated activity in recognized periods of work

### Semantic Interpretation

This is a high-level activity-domain classifier.

It is more abstract than `CVN_ACTIVITY_A` and `CVN_ACTIVITY_B`, and should stay
separate from them.

## Family 2 - `CVN_MANAGEMENT_*`

## Overview

This family has two different but related levels:

- `CVN_MANAGEMENT_A`: type of management activity in R&D
- `CVN_MANAGEMENT_TYPE_A`: scope of direction or management activity in the
  professional situation block

## `CVN_MANAGEMENT_A`

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

- `360` -> `Gestión de acciones y proyectos de I+D+I`
- `370` -> `Gestión de entidad`
- `380` -> `Gestión de eventos organizados`
- `390` -> `Gestión de grupo de investigación`
- `400` -> `Gestión de programa de investigación`
- `OTHERS` -> `Otros`

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- `060.020.040.070` typology of management activity

### Semantic Interpretation

This is a specialized R&D management classifier.

## `CVN_MANAGEMENT_TYPE_A`

### Table Metadata

- version: `1.0.0`
- source: `CVN`
- `XMLDataType`: `CVN_Value_Filter@AuxTable.xsd`
- `XMLProperty`: `Filter`
- `XMLIndicator`: `Value`

### Observed Structure

- items: `5`
- `Link=true`: `0`
- delegated items: `0`

### Values

- `000` -> `Universitaria`
- `010` -> `OPIs`
- `020` -> `Comunidades Autónomas`
- `030` -> `Administración General del Estado`
- `OTHERS` -> `Otros`

### Usage In `SpecificationManual.xml`

Observed references: `2`

Canonical uses:

- `010.010.000.290`
- `010.020.000.290`

These are the "scope of management activity" fields in professional situation
records.

### Semantic Interpretation

This is broader and more institutionally scoped than `CVN_MANAGEMENT_A`.

## Family 3 - `CVN_SCOPE_*`

## Overview

The `CVN_SCOPE_*` family expresses geographical or institutional scope, but in
two distinct contextual variants.

- `CVN_SCOPE_A`: compact territorial scope
- `CVN_SCOPE_B`: expanded scope including international-organizational and
  cooperation categories

## `CVN_SCOPE_A`

### Table Metadata

- version: `1.0.1`
- source: `CVN`
- `XMLDataType`: `CVN_ScopeTypeType@AuxTable.xsd`
- `XMLProperty`: `Scope`
- `XMLIndicator`: `Type`

### Observed Structure

- items: `5`
- `Link=true`: `1`
- delegated items: `0`

### Values

- `000` -> `Autonómica`
- `010` -> `Nacional`
- `020` -> `Unión Europea`
- `030` -> `Internacional no UE`
- `OTHERS` -> `Otros`

### Usage In `SpecificationManual.xml`

Observed references: `14`

This is one of the most reused scope tables in the manual.

It appears in contexts such as:

- project scope
- committee scope
- activity scope
- collaboration scope
- network scope
- organization scope

### Semantic Interpretation

Reusable geographic scope enum candidate.

## `CVN_SCOPE_B`

### Table Metadata

- version: `1.0.2`
- source: `CVN`
- `XMLDataType`: `CVN_ScopeTypeType@AuxTable.xsd`
- `XMLProperty`: `Scope`
- `XMLIndicator`: `Type`

### Observed Structure

- items: `7`
- `Link=true`: `1`
- delegated items: `0`

### Values

- `000` -> `Autonómica`
- `010` -> `Nacional`
- `020` -> `Unión Europea`
- `040` -> `OMS`
- `050` -> `Otros organismos internacionales`
- `060` -> `Cooperación con países en desarrollo`
- `OTHERS` -> `Otros`

### Usage In `SpecificationManual.xml`

Observed references: `2`

Used where scope must distinguish special international or health-related
institutional spaces.

### Semantic Interpretation

This is not just a larger `CVN_SCOPE_A`. It encodes domain-specific
international-scope categories such as WHO and development cooperation.

## Family 4 - `CVN_LANGUAGE_B`

### Table Metadata

- version: `1.0.0`
- source: `CVN`
- `XMLDataType`: `CVN_LANGUAGE_B@ReferenceTables.xsd`
- `XMLProperty`: `Quality`
- `XMLIndicator`: `Measure`

### Observed Structure

- items: `6`
- `Link=true`: `0`
- delegated items: `0`

### Values

- `A1`
- `A2`
- `B1`
- `B2`
- `C1`
- `C2`

### Usage In `SpecificationManual.xml`

Observed references: `5`

Used in the five language-skill dimensions:

- listening comprehension
- reading comprehension
- spoken interaction
- spoken expression
- written expression

### Semantic Interpretation

This is a strict closed scale and one of the cleanest enum candidates in the
entire package.

## Family 5 - `CVN_TIME_A`

### Table Metadata

- version: `1.0.0`
- source: `CVN`
- `XMLDataType`: `CVN_PhysicalDimensionalTypeType@AuxTable.xsd`
- `XMLProperty`: `PhysicalDimension`
- `XMLIndicator`: `Type`

### Observed Structure

- items: `2`
- `Link=true`: `0`
- delegated items: `0`

### Values

- `000` -> `Créditos`
- `010` -> `Horas`

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- type of hours/ECTS credits in teaching records

### Semantic Interpretation

Binary physical-dimension classifier; strict enum candidate.

## Family 6 - `CVN_QUALIFICATION_*`

## `CVN_QUALIFICATION_A`

### Table Metadata

- version: `1.0.0`
- source: `CVN`
- `XMLDataType`: `CVN_Value_Filter@AuxTable.xsd`
- `XMLProperty`: `Filter`
- `XMLIndicator`: `Value`

### Observed Structure

- items: `2`
- `Link=true`: `0`
- delegated items: `0`

### Values

- `000` -> `Éxito`
- `010` -> `Fallido`

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- result in relation to an innovative company generated from industrial property

### Semantic Interpretation

Very small result-status enum.

## `CVN_QUALIFICATION_B`

### Table Metadata

- version: `1.0.0`
- source: `CVN`
- `XMLDataType`: `CVN_QUALIFICATION_B@ReferenceTables.xsd`
- `XMLProperty`: `Quality`
- `XMLIndicator`: `Measure`

### Observed Structure

- items: `4`
- `Link=true`: `0`
- delegated items: `0`

### Values

- `000` -> `Aprobado`
- `010` -> `Notable`
- `020` -> `Sobresaliente`
- `030` -> `Matrícula de Honor`

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- average academic record qualification

### Semantic Interpretation

Compact academic-grade enum.

## Family 7 - `CVN_ACCESS_A`

### Table Metadata

- version: `1.0.0`
- source: `CVN`
- `XMLDataType`: `CVN_Value_Filter@AuxTable.xsd`
- `XMLProperty`: `Filter`
- `XMLIndicator`: `Value`

### Observed Structure

- items: `7`
- `Link=true`: `1`
- delegated items: `0`

### Representative Values

- `130` -> `Con o sin publicidad de la decisión`
- `140` -> `Con reconocimiento expreso de los méritos que concurren`
- `610` -> `Por concurso`
- `630` -> `Por designación de quien corresponda sin concurrencia`
- `640` -> `Por méritos públicos`
- `650` -> `Por votación entre diversos candidatos`
- `OTHERS` -> `Otros`

### Usage In `SpecificationManual.xml`

Observed references: `2`

Used in:

- system of access to evaluation/review posts
- system of access to management posts

### Semantic Interpretation

This table classifies selection or appointment procedure.

## Family 8 - `CVN_EVALUATION_A`

### Table Metadata

- version: `1.0.1`
- source: `CVN`
- `XMLDataType`: `CVN_Value_Filter@AuxTable.xsd`
- `XMLProperty`: `Filter`
- `XMLIndicator`: `Value`

### Observed Structure

- items: `4`
- `Link=true`: `1`
- delegated items: `0`

### Values

- `290` -> `Encuesta`
- `320` -> `Evaluación externa`
- `330` -> `Evaluación interna`
- `OTHERS` -> `Otros`

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- type of teaching-quality evaluation

### Semantic Interpretation

Small evaluation-method enum candidate.

## Batch-4 Conclusions

This batch adds three more important semantic patterns.

### Pattern 1 - Several Small Tables Are Clean Closed Scales

Especially:

- `CVN_LANGUAGE_B`
- `CVN_TIME_A`
- `CVN_QUALIFICATION_A`
- `CVN_QUALIFICATION_B`

These are among the safest strict-enum candidates in the package.

### Pattern 2 - Administrative Procedure And Scope Are Reused Cross-Cuttingly

- `CVN_ACCESS_A`
- `CVN_SCOPE_A`
- `CVN_SCOPE_B`

These appear across different domains and should likely become shared reusable
domain enums rather than local one-off types.

### Pattern 3 - Some Families Share Names But Not Semantics

As already seen in previous batches, names alone are not enough:

- `CVN_ACTIVITY_A/B/D` are unrelated enough to require separate treatment
- `CVN_MANAGEMENT_A` and `CVN_MANAGEMENT_TYPE_A` operate at different semantic
  layers
- `CVN_SCOPE_A` and `CVN_SCOPE_B` overlap but are not interchangeable

## Recommended Semantic Treatment For This Batch

### Strong Enum Candidates

- `CVN_LANGUAGE_B`
- `CVN_TIME_A`
- `CVN_QUALIFICATION_A`
- `CVN_QUALIFICATION_B`
- `CVN_EVALUATION_A`

### Reusable Shared Domain Enums

- `CVN_SCOPE_A`
- `CVN_SCOPE_B`
- `CVN_ACCESS_A`
- `CVN_MANAGEMENT_TYPE_A`

### Context-Specific Enums That Should Stay Separated

- `CVN_ACTIVITY_A`
- `CVN_ACTIVITY_B`
- `CVN_ACTIVITY_D`
- `CVN_MANAGEMENT_A`

## Reading Path

This document should be read after:

- `docs/cvn_annex_priority_table_families.md`
- `docs/cvn_annex_table_families_batch3.md`

and together with:

- `docs/cvn_source_package_annex_table_coverage.md`
