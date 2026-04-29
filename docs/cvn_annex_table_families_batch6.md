# CVN Annex Table Families Batch 6

## Purpose

This document continues the detailed Annex I reference set and records the table
families centered on personal identification, geographical localization, and
professional situation.

This batch covers:

- `CVN_REGION`
- `CVN_PROVINCE`
- `CVN_SEX_A`
- `CVN_SITUATION_A`
- `CVN_SITUATION_B`

These tables are small or medium in isolation, but highly transversal in the
manual and especially important for normalization and future domain modeling.

## Family 1 - `CVN_REGION`

### Table Metadata

- version: `1.0.3`
- `antecesorTable`: `ISO_3166`
- source: `NUTS-Eurostat`
- `XMLDataType`: `CVN_Region@AuxTable.xsd`
- `XMLProperty`: none recorded in the table metadata
- `XMLIndicator`: none recorded in the table metadata

### Observed Structure

- items: `280`
- `Link=true`: `1`
- delegated items: `0`
- items with `AntecesorCode`: `279`

### Representative Values

- `AT13` -> `Wien`, antecedent `40` (Austria)
- `BE22` -> `Prov. Limburg (B)`, antecedent `56` (Belgium)
- `CY00` -> `Kypros / Kibris`, antecedent `196` (Cyprus)
- `CZ04` -> `Severozapad`, antecedent `203` (Czech Republic)
- `CZZZ` -> `Extra-Regio`, antecedent `203`
- `DE21` -> `Oberbayern`, antecedent `276` (Germany)
- `ES11` -> `Galicia`, antecedent `724` (Spain)
- `OTHERS` is also present as a generic escape value in the full table

### Usage In `SpecificationManual.xml`

Observed references: `102`

This is one of the most reused tables in the entire manual.

It appears in almost every block where a location can be attached to:

- birth and contact data
- employing entities
- educational institutions
- teaching activities
- healthcare entities
- project locations
- organization and committee records
- publication metadata

### Semantic Interpretation

This is not a simple country table.

It is a regional taxonomy derived from NUTS/Eurostat and anchored to ISO 3166.

Recommended semantic treatment:

- treat as a reusable hierarchical geographic codelist
- preserve both code and label
- preserve linkage to parent country through `AntecesorCode`
- allow explicit representation of `Extra-Regio` and `OTHERS`

### Important Modeling Note

Because the table is reused over one hundred times in the manual, it should not
be modeled as a local enum inside one domain section. It deserves a shared
geographic-reference concept.

## Family 2 - `CVN_PROVINCE`

### Table Metadata

- version: `1.0.0`
- `antecesorTable`: `CVN_REGION`
- source: `CVN`
- `XMLDataType`: `CVN_Value_Filter@AuxTable.xsd`
- `XMLProperty`: `Filter`
- `XMLIndicator`: `Value`

### Observed Structure

- items: `50`
- `Link=true`: `0`
- delegated items: `0`
- items with `AntecesorCode`: `50`

### Representative Values

- `000` -> `La Coruña`, antecedent `ES11`
- `040` -> `Asturias`, antecedent `ES12`
- `050` -> `Cantabria`, antecedent `ES13`
- `100` -> `La Rioja`, antecedent `ES23`
- `150` -> `Ávila`, antecedent `ES41`
- `250` -> `Ciudad Real`, antecedent `ES42`
- `300` -> `Cáceres`, antecedent `ES43`

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- contact province in the personal identification block

### Semantic Interpretation

This is a Spain-specific province codelist layered on top of `CVN_REGION`.

Recommended semantic treatment:

- hierarchical geographic codelist
- likely a specialized child layer of the same shared geographic-reference model
  used for `CVN_REGION`

## Family 3 - `CVN_SEX_A`

### Table Metadata

- version: `1.0.1`
- source: `CVN`
- `XMLDataType`: `CVN_GenderType@AuxTable.xsd`
- `XMLProperty`: `Identification`
- `XMLIndicator`: `PersonalIdentification`

### Observed Structure

- items: `2`
- `Link=true`: `0`
- delegated items: `0`

### Values

- `000` -> `Hombre`
- `010` -> `Mujer`

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- `000.010.000.030` sex in personal identification

### Semantic Interpretation

This is a very small legacy binary identification table.

It should be documented carefully because:

- it is structurally simple
- but semantically sensitive
- and future domain models may want to preserve source fidelity while exposing a
  clearer or more modern abstraction policy

For the current repository phase, it should be treated as a source-faithful
controlled table, not reinterpreted yet.

## Family 4 - `CVN_SITUATION_*`

## Overview

The `CVN_SITUATION_*` family splits two distinct meanings of “situation”:

- `CVN_SITUATION_A`: employment or contract situation
- `CVN_SITUATION_B`: family or leave-related legal situation attached to other
  curriculum contexts

They should not be merged just because they share the same family stem.

## `CVN_SITUATION_A`

### Table Metadata

- version: `1.0.2`
- source: `CVN`
- `XMLDataType`: `CVN_Value_Filter@AuxTable.xsd`
- `XMLProperty`: `Filter`
- `XMLIndicator`: `Value`

### Observed Structure

- items: `8`
- `Link=true`: `1`
- delegated items: `0`

### Representative Values

- `040` -> `Becario/a (pre o posdoctoral, otros)`
- `160` -> `Contrato laboral indefinido`
- `170` -> `Contrato laboral temporal`
- `260` -> `Emérito/a`
- `300` -> `Estatuario/a`
- `350` -> `Funcionario/a`
- `440` -> `Interino/a`
- `OTHERS` -> `Otros`

### Usage In `SpecificationManual.xml`

Observed references: `2`

Canonical uses:

- `010.010.000.190` contract modality in current professional situation
- `010.020.000.200` contract modality in past professional situation

### Semantic Interpretation

This is a compact employment-status or contract-regime classifier.

Recommended semantic treatment:

- enum candidate with explicit `OTHERS` escape path

## `CVN_SITUATION_B`

### Table Metadata

- version: `1.0.2`
- source: `CVN`
- `XMLDataType`: `CVN_Value_Filter@AuxTable.xsd`
- `XMLProperty`: `Filter`
- `XMLIndicator`: `Value`

### Observed Structure

- items: `17`
- `Link=true`: `1`
- delegated items: `0`

### Representative Values

- `040` -> `Guarda con fines de adopción`
- `160` -> `Incapacidad temporal durante embarazo`
- `170` -> `Suspensión de contrato por riesgo durante embarazo`
- `260` -> `Acogimiento permanente`
- `300` -> `Incapacidad temporal`
- `350` -> `Nacimiento de hijo/a`
- `440` -> `Cuidado de hijo/a en adopción`
- `OTHERS` -> `Otros`

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- `070.010`-related evaluated periods and similar personal recognition contexts
  where leave or personal-situation effects are recorded in CVN

### Semantic Interpretation

This table is much more specific and administrative than `CVN_SITUATION_A`.

It belongs to legal, family, or leave situations rather than employment
contract-type semantics.

## Cross-Family Conclusions

This batch highlights two especially important modeling lessons.

### Lesson 1 - Geography Is A Shared Hierarchical Layer

`CVN_REGION` and `CVN_PROVINCE` are not isolated convenience tables.

Together they form a layered geographic system:

- countries via `ISO_3166`
- regions via `CVN_REGION`
- Spanish provinces via `CVN_PROVINCE`

This should likely become a shared domain reference layer rather than scattered
enums on individual fields.

### Lesson 2 - Family Stems Do Not Guarantee Shared Semantics

`CVN_SITUATION_A` and `CVN_SITUATION_B` are clearly different semantic tables.

The first is employment-focused.
The second is administrative or personal-status-focused.

The semantic layer should therefore keep them distinct even if both appear under
the same naming family.

## Recommended Semantic Treatment For This Batch

### Shared Domain Reference Layer

- `CVN_REGION`
- `CVN_PROVINCE`

### Small Controlled Tables With Stable Semantics

- `CVN_SEX_A`
- `CVN_SITUATION_A`
- `CVN_SITUATION_B`

### Extra Caution Required

- `CVN_SEX_A`

This table is structurally trivial but semantically sensitive, so future domain
policy should distinguish source fidelity from any future presentation-layer
adaptation.

## Reading Path

This document should be read after:

- `docs/cvn_annex_priority_table_families.md`
- `docs/cvn_annex_table_families_batch3.md`
- `docs/cvn_annex_table_families_batch4.md`
- `docs/cvn_annex_table_families_batch5.md`
