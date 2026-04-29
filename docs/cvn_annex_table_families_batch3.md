# CVN Annex Table Families Batch 3

## Purpose

This document continues the detailed reference work started in
`docs/cvn_annex_priority_table_families.md` and records the next group of Annex I
table families that have strong semantic impact on the CVN model.

This batch covers:

- `CVN_PARTICIPATION_*`
- `CVN_SUMMONS_*`
- `CVN_PROGRAMME_*`
- `CVN_PUBLICATION_A`
- `CVN_SUPPORT_*`
- `CVN_EVENT_*`

As in the previous batch, the analysis combines:

- `ReferenceTables.xml`
- `SpecificationManual.xml`
- table metadata embedded in `ReferenceTables.xml`

## Family 1 - `CVN_PARTICIPATION_*`

## Overview

The `CVN_PARTICIPATION_*` family is semantically broad. It does not encode one
single universal notion of participation. Instead, it captures several context-
specific participation vocabularies that are reused across projects, events,
publications, committees, and teaching or health activities.

This is one of the clearest cases where table-name similarity can hide several
distinct domain roles.

## `CVN_PARTICIPATION_A`

### Table Metadata

- version: `1.0.0`
- source: `CVN`
- `XMLDataType`: `CVN_Value_Filter@AuxTable.xsd`
- `XMLProperty`: `Filter`
- `XMLIndicator`: `Value`

### Observed Structure

- items: `5`
- `Link=true`: `1`
- delegated items: `1`
- hierarchy: none

### Representative Values

- `050` -> `Investigador principal`
- `060` -> `Miembro de equipo`
- `210` -> `Colaborador`
- `260` -> `Coordinador`
- `OTHERS` -> `Otros`

Observed delegated case:

- `210` delegates to `OTHERS`

### Usage In `SpecificationManual.xml`

Observed references: `4`

Used in contexts such as:

- participation in teaching innovation projects
- participation in health innovation projects
- participation in planning or management projects
- participation in research projects where a broad participation category is
  enough and no role-specific taxonomy is needed

### Semantic Interpretation

This is a compact generic project-participation classifier.

Recommended semantic treatment:

- enum candidate with `OTHERS`
- preserve delegation metadata because `Colaborador` is encoded through a
  delegated legacy entry

## `CVN_PARTICIPATION_B`

### Table Metadata

- version: `1.0.1`
- source: `CVN`
- `XMLDataType`: `CVN_Value_Roll@AuxTable.xsd`
- `XMLProperty`: `Roll`
- `XMLIndicator`: `Value`

### Observed Structure

- items: `7`
- `Link=true`: `1`
- delegated items: `0`
- hierarchy: none

### Representative Values

- `270` -> `Coordinador/a científico/a`
- `280` -> `Coordinador del proyecto total, red o consorcio`
- `290` -> `Coordinador/a gerente`
- `490` -> `Investigador/a`
- `870` -> `Técnico/a`
- `890` -> `Titulado/a universitario/a en formación`
- `OTHERS` -> `Otros`

### Usage In `SpecificationManual.xml`

Observed references: `3`

Used in research and transfer contexts such as:

- contribution role in competitive R&D projects
- contribution role in non-competitive R&D projects
- contribution role in specialized transfer or expert activities

### Semantic Interpretation

This is a role taxonomy, not just a participation flag.

The use of `Roll` rather than `Filter` is a clue that the package treats it as a
contribution-role classifier.

Recommended semantic treatment:

- enum candidate for project role
- keep separate from generic participation tables such as
  `CVN_PARTICIPATION_A`

## `CVN_PARTICIPATION_C`

### Table Metadata

- version: `1.0.1`
- source: `CVN`
- `XMLDataType`: `CVN_Value_Roll@AuxTable.xsd`
- `XMLProperty`: `Roll`
- `XMLIndicator`: `Value`

### Observed Structure

- items: `5`
- `Link=true`: `1`
- delegated items: `0`
- hierarchy: none

### Representative Values

- `230` -> `Comisario/a de exposición`
- `650` -> `Organizador`
- `740` -> `Presidente`
- `830` -> `Secretario/a`
- `OTHERS` -> `Otros`

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- organization of R&D activities and events

### Semantic Interpretation

This is a small role vocabulary for organization and governance of activities.

Recommended semantic treatment:

- enum candidate
- keep distinct from scientific contribution roles and event participation roles

## `CVN_PARTICIPATION_E`

### Table Metadata

- version: `1.0.0`
- source: `CVN`
- `XMLDataType`: `CVN_Value_Filter@AuxTable.xsd`
- `XMLProperty`: `Filter`
- `XMLIndicator`: `Value`

### Observed Structure

- items: `10`
- `Link=true`: `1`
- delegated items: `2`
- hierarchy: none

### Representative Values

- `050` -> `Organizativo - Presidente Comité`
- `060` -> `Organizativo - Comité científico y organizador`
- `070` -> `Organizativo - Otros`
- `080` -> `Participativo - Plenaria`
- `730` -> `Participativo - Ponencia invitada/ Keynote`
- `960` -> `Participativo - Ponencia oral (comunicación oral)`
- `970` -> `Participativo - Póster`
- `980` -> `Comité organizador`
- `990` -> `Comité científico`
- `OTHERS` -> `Participativo - Otros`

Observed delegated cases:

- `980` delegates to `060`
- `990` delegates to `060`

### Usage In `SpecificationManual.xml`

Observed references: `5`

Used in event and congress participation contexts across:

- teaching events
- scientific congresses
- health-related events
- teaching support courses

### Semantic Interpretation

This table mixes two axes:

- organizational participation
- participatory presentation mode

It is still manageable as a single enum, but the domain layer may want to expose
it under a specific event-participation concept rather than a general-purpose
`participation` field.

## `CVN_PARTICIPATION_F`

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

- `875` -> `Coordinación`
- `876` -> `Cooperación`

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- associated project type in non-competitive R&D contexts

### Semantic Interpretation

Very small binary classifier.

Recommended semantic treatment:

- enum candidate
- better documented as relation mode than as generic participation

## `CVN_PARTICIPATION_G`

### Table Metadata

- version: `1.0.3`
- source: `CVN`
- `XMLDataType`: `CVN_Value_Roll@AuxTable.xsd`
- `XMLProperty`: `Roll`
- `XMLIndicator`: `Value`

### Observed Structure

- items: `11`
- `Link=true`: `0`
- delegated items: `0`

### Representative Values

- article with external review
- article without external review
- chapter of book
- complete book
- critical review or recension
- scientific or technical dissemination document
- dissemination publication
- review bibliography
- scientific edition
- editor/coeditor

### Usage In `SpecificationManual.xml`

Observed references: `2`

Used in:

- scientific and technical publications
- teaching or pedagogical publication contexts

### Semantic Interpretation

This is not merely authorship position. It is a publication-contribution role and
publication-nature hybrid.

Recommended semantic treatment:

- enum candidate, but scoped specifically to publication contribution
- do not merge with project or event participation tables

## `CVN_PARTICIPATION_H`

### Table Metadata

- version: `1.0.4`
- source: `CVN`
- `XMLDataType`: `CVN_Value_Filter@AuxTable.xsd`
- `XMLProperty`: `Filter`
- `XMLIndicator`: `Value`

### Observed Structure

- items: `5`
- `Link=true`: `1`
- delegated items: `0`

### Representative Values

- `970` -> `Tutor/a de residentes`
- `980` -> `Profesor/a en curso para residentes`
- `990` -> `Sesiones clínicas`
- `1000` -> `Talleres`
- `OTHERS` -> `Otros`

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- health specialized teaching participation

### Semantic Interpretation

This is a narrowly scoped health-training participation vocabulary.

## Family 2 - `CVN_SUMMONS_*`

## Overview

The `CVN_SUMMONS_*` family separates:

- `CVN_SUMMONS_A`: purpose or funding objective of aid/bursary
- `CVN_SUMMONS_B`: type of call, especially competitive versus non-competitive

## `CVN_SUMMONS_A`

### Table Metadata

- version: `1.0.1`
- source: `CVN`
- `XMLDataType`: `CVN_Value_Filter@AuxTable.xsd`
- `XMLProperty`: `Filter`
- `XMLIndicator`: `Value`

### Observed Structure

- items: `3`
- `Link=true`: `1`
- delegated items: `0`

### Values

- `670` -> `Posdoctoral`
- `710` -> `Predoctoral`
- `OTHERS` -> `Otros`

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- purpose of aid or bursary obtained

### Semantic Interpretation

Compact funding-purpose classifier.

## `CVN_SUMMONS_B`

### Table Metadata

- version: `1.0.0`
- source: `CVN`
- `XMLDataType`: `CVN_Value_Filter@AuxTable.xsd`
- `XMLProperty`: `Filter`
- `XMLIndicator`: `Value`

### Observed Structure

- items: `3`
- `Link=true`: `1`
- delegated items: `0`

### Values

- `1040` -> `Competitivo`
- `1050` -> `No competitivo`
- `OTHERS` -> `Otros`

### Usage In `SpecificationManual.xml`

Observed references: `4`

Used in:

- teaching funding calls
- innovation projects
- health planning projects

### Semantic Interpretation

This is a cross-cutting procurement or call-procedure classifier.

Recommended semantic treatment:

- enum candidate
- reusable across many funding-like contexts

## Family 3 - `CVN_PROGRAMME_*`

## Overview

The `CVN_PROGRAMME_*` tables are also context-scoped.

- `CVN_PROGRAMME_A`: academic level or kind of degree program for teaching
- `CVN_PROGRAMME_B`: type of healthcare training program
- `CVN_PROGRAMME_C`: tutoring or educational support program type

## `CVN_PROGRAMME_A`

### Table Metadata

- version: `1.0.2`
- source: `CVN`
- `XMLDataType`: `CVN_Value_Filter@AuxTable.xsd`
- `XMLProperty`: `Filter`
- `XMLIndicator`: `Value`

### Observed Structure

- items: `9`
- `Link=true`: `1`
- delegated items: `0`

### Representative Values

- `020` -> `Arquitectura`
- `030` -> `Arquitectura técnica`
- `240` -> `Diplomatura`
- `250` -> `Doctorado/a`
- `420` -> `Ingeniería`
- `430` -> `Ingeniería Técnica`
- `470` -> `Licenciatura`
- `480` -> `Máster oficial`
- `OTHERS` -> `Otros`

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- type of teaching program in academic teaching records

### Semantic Interpretation

Compact academic-program classifier.

## `CVN_PROGRAMME_B`

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

- `720` -> `Programa clínico`
- `730` -> `Programa Gestión de Servicios Sanitarios`
- `750` -> `Programa de Salud Pública`
- `OTHERS` -> `Otros`

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- healthcare tutoring or supervision program type

### Semantic Interpretation

Small health-program enum.

## `CVN_PROGRAMME_C`

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

### Representative Values

- `180` -> `Cooperación educativa`
- `250` -> `Doctorado/a`
- `340` -> `Formación personal docente`
- `490` -> `Mejora rendimiento`
- `740` -> `Programa de movilidad`
- `OTHERS` -> `Otros`

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- tutoring-program type in academic tutoring records

### Semantic Interpretation

This is a support-program classifier rather than a degree-title table.

## Family 4 - `CVN_PUBLICATION_A`

### Table Metadata

- version: `1.0.3`
- source: `CVN`
- `XMLDataType`: `Subtype@Subtypes.xsd`
- `XMLProperty`: `Subtype`

### Observed Structure

- items: `18`
- `Link=true`: `1`
- delegated items: `2`
- hierarchy: none

### Representative Values

- `004` -> `Capítulo de libro`
- `018` -> `Informe científico-técnico`
- `020` -> `Artículo científico`
- `032` -> `Libro o monografía científica`
- `075` -> `Artículos en prensa`
- `202` -> `Artículo de enciclopedia`
- `203` -> `Artículo de divulgación`
- `204` -> `Traducción`
- `205` -> `Reseña`
- `206` -> `Revisión bibliográfica`
- `207` -> `Libro de divulgación`
- `208` -> `Edición científica`
- `209` -> `Diccionario científico`
- `210` -> `Software de investigación`
- `211` -> `Set de datos`
- `OTHERS` -> `Otros`

### Usage In `SpecificationManual.xml`

Observed references: `6`

Used in:

- scientific publications
- teaching event publication types
- health publication types
- dissemination activity publication types

### Semantic Interpretation

This table is especially important because it demonstrates that CVN already
folds modern research outputs such as software and datasets into its publication-
type layer.

Also important:

- serialization uses `Subtype`
- this is not just a simple `Filter` enum

Recommended semantic treatment:

- small controlled publication-output family
- subtype-aware handling required

## Family 5 - `CVN_SUPPORT_*`

## `CVN_SUPPORT_A`

### Table Metadata

- version: `1.0.1`
- source: `CVN`
- `XMLDataType`: `Subtype@Subtypes.xsd`
- `XMLProperty`: `Subtype`

### Observed Structure

- items: `10`
- `Link=true`: `1`
- delegated items: `0`

### Representative Values

- `004` -> `Capítulos de libros`
- `032` -> `Libro`
- `053` -> `Software de investigación`
- `074` -> `Artículo/s`
- `180` -> `Apuntes`
- `185` -> `Juegos didácticos`
- `200` -> `Manual`
- `201` -> `Libro de prácticas`
- `211` -> `Set de datos`
- `OTHERS` -> `Otros`

### Usage In `SpecificationManual.xml`

Observed references: `2`

Used in:

- material docente
- clinical or assistance documentation support material contexts where support
  format matters

### Semantic Interpretation

This is a support-medium taxonomy with subtype serialization.

It overlaps conceptually with `CVN_PUBLICATION_A`, but it is scoped to support
material rather than publication identity as such.

## `CVN_SUPPORT_B`

### Table Metadata

- version: `1.0.4`
- source: `CVN`
- `XMLDataType`: `Subtype@Subtypes.xsd`
- `XMLProperty`: `Subtype`

### Observed Structure

- items: `4`
- `Link=true`: `0`
- delegated items: `0`

### Values

- `006` -> `Catálogo de obra artística`
- `018` -> `Documento o Informe científico-técnico`
- `032` -> `Libro`
- `057` -> `Revista`

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- support type in scientific and technical publication records

### Semantic Interpretation

This is a more compact support-medium table focused on publication support or
carrier type.

## Family 6 - `CVN_EVENT_*`

## Overview

The `CVN_EVENT_*` family again splits by context.

- `CVN_EVENT_A`: dissemination events
- `CVN_EVENT_B`: congresses and similar event formats
- `CVN_EVENT_C`: jornadas, seminars, workshops, and courses outside the congress
  scope

All three use subtype serialization.

## `CVN_EVENT_A`

### Table Metadata

- version: `1.0.1`
- source: `CVN`
- `XMLDataType`: `Subtype@Subtypes.xsd`
- `XMLProperty`: `Subtype`

### Observed Structure

- items: `4`
- `Link=true`: `1`

### Values

- `181` -> `Entrevistas en medios comunicación`
- `182` -> `Ferias y exhibiciones`
- `183` -> `Conferencias impartidas`
- `OTHERS` -> `Otros`

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- dissemination activity events

## `CVN_EVENT_B`

### Table Metadata

- version: `1.0.1`
- source: `CVN`
- `XMLDataType`: `Subtype@Subtypes.xsd`
- `XMLProperty`: `Subtype`

### Observed Structure

- items: `6`
- `Link=true`: `1`

### Values

- `008` -> `Congreso`
- `031` -> `Jornada`
- `063` -> `Seminario`
- `064` -> `Curso`
- `065` -> `Taller`
- `OTHERS` -> `Otros`

### Usage In `SpecificationManual.xml`

Observed references: `4`

Used in:

- teaching-oriented events
- health-oriented congresses
- scientific congresses

### Semantic Interpretation

This is the most generic event-format table in the family and is heavily reused.

## `CVN_EVENT_C`

### Table Metadata

- version: `1.0.1`
- source: `CVN`
- `XMLDataType`: `Subtype@Subtypes.xsd`
- `XMLProperty`: `Subtype`

### Observed Structure

- items: `5`
- `Link=true`: `1`

### Values

- `011` -> `Curso`
- `031` -> `Jornada`
- `063` -> `Seminario`
- `065` -> `Taller de Trabajo`
- `OTHERS` -> `Otros`

### Usage In `SpecificationManual.xml`

Observed references: `1`

Canonical use:

- works presented in non-congress scientific events

### Semantic Interpretation

This table is narrower than `CVN_EVENT_B` and should likely remain scoped to its
specific section instead of being globally merged with it.

## Batch-3 Conclusions

This batch reinforces three patterns already visible in the package.

### Pattern 1 - Many Event, Support, And Publication Tables Serialize Through `Subtype`

Affected in this batch:

- `CVN_SUPPORT_A`
- `CVN_SUPPORT_B`
- `CVN_EVENT_A`
- `CVN_EVENT_B`
- `CVN_EVENT_C`
- `CVN_PUBLICATION_A`

This means later semantic modeling must not assume every controlled table is
serialized through the same `Filter/Value` mechanism.

### Pattern 2 - `Participation` Is Context-Dependent

The table family contains:

- generic participation
- contribution role
- organization role
- event participation mode
- publication contribution mode
- health specialized teaching participation

These should not be flattened into one generic concept.

### Pattern 3 - Small Tables Still Need Open-Value Policy

Most tables in this batch are small enough to be enum candidates, but many still
carry:

- `OTHERS`
- `Link=true`
- occasional `Delegate`

So even compact enums need an explicit extension and compatibility policy.

## Recommended Semantic Treatment For This Batch

### Strong Enum Candidates

- `CVN_SUMMONS_A`
- `CVN_SUMMONS_B`
- `CVN_PROGRAMME_A`
- `CVN_PROGRAMME_B`
- `CVN_PROGRAMME_C`
- `CVN_PARTICIPATION_F`

### Enum Candidates With Important Scope Boundaries

- `CVN_PARTICIPATION_A`
- `CVN_PARTICIPATION_B`
- `CVN_PARTICIPATION_C`
- `CVN_PARTICIPATION_E`
- `CVN_PARTICIPATION_G`
- `CVN_PARTICIPATION_H`

### Subtype-Aware Controlled Families

- `CVN_PUBLICATION_A`
- `CVN_SUPPORT_A`
- `CVN_SUPPORT_B`
- `CVN_EVENT_A`
- `CVN_EVENT_B`
- `CVN_EVENT_C`

These are controlled values, but their serialization path and semantic role need
to stay coupled to subtype policy.
