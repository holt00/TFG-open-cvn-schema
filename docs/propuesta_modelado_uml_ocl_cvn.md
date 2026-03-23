# Propuesta de modelado UML + OCL para CVN

## Objetivo

Este documento propone una estrategia practica para traducir el material de `docs/CvnXML_v1.4.3_2.1_17012025` a un modelo **UML + OCL** agnostico al lenguaje y desacoplado de la serializacion XML.

El objetivo no es copiar el XML CVN en UML, sino construir un **modelo conceptual de dominio** reutilizable que:

- represente el significado real de la informacion curricular
- pueda serializarse despues a CVN-XML
- permita definir restricciones semanticas con OCL
- mantenga trazabilidad con los codigos CVN originales

---

## Principio de modelado

## Regla principal

No modelar **la estructura XML** como si fuera **el dominio**.

En CVN hay que separar tres cosas:

1. **Conceptos del dominio curricular**
2. **Restricciones de negocio**
3. **Mecanismo tecnico de intercambio XML**

En consecuencia:

- el **UML** debe representar conceptos del dominio
- el **OCL** debe capturar reglas semanticas
- el **mapeo a XML** debe quedar en una capa aparte

---

## Fuentes que debes usar

## Fuentes principales para el modelo conceptual

- `docs/CvnXML_v1.4.3_2.1_17012025/Manual/Manual de Especificaciones Técnicas v1.4.3_v2.1.pdf`
- `docs/CvnXML_v1.4.3_2.1_17012025/XML/SpecificationManual.xml`
- `docs/CvnXML_v1.4.3_2.1_17012025/XSD/AuxTable.xsd`
- `docs/CvnXML_v1.4.3_2.1_17012025/XSD/ISOUtilities.xsd`

## Fuentes secundarias para trazabilidad tecnica

- `docs/CvnXML_v1.4.3_2.1_17012025/XML/CVNTreeModel.xml`
- `docs/CvnXML_v1.4.3_2.1_17012025/XSD/CVN.xsd`
- `docs/CvnXML_v1.4.3_2.1_17012025/Manual/TreeModel_v1.0 20090331 v1.0.pdf`

## Interpretacion recomendada

- `Manual PDF` -> semantica de negocio
- `SpecificationManual.xml` -> catalogo estructurado de campos
- `AuxTable.xsd` -> codelists y enumeraciones
- `CVNTreeModel.xml` -> mapeo tecnico campo -> XML
- `CVN.xsd` -> validacion estructural del XML final

---

## Lo que no conviene hacer

## Error 1. Partir de `CVN.xsd`

Si el UML nace del XSD, el resultado tendera a ser XML-centrico:

- `Title`
- `Description`
- `Entity`
- `Date`
- `Subject`
- `Filter`

Eso es util para serializacion, pero pobre como modelo de dominio.

## Error 2. Convertir cada codigo CVN en una clase

Los codigos CVN son muy buenos para trazabilidad y documentacion, pero no necesariamente equivalen a clases conceptuales.

Ejemplo:

- `000.010.000.010` y `000.010.000.020` no deben generar clases independientes; son atributos de una entidad `Person` o `PersonalIdentification`.

## Error 3. Tomar el arbol de `CVNTreeModel` como ontologia del dominio

Ese arbol es un modelo de codificacion tecnica, no un modelo conceptual neutral.

---

## Estrategia general recomendada

## Vision en 4 capas

### Capa A. Modelo conceptual UML

Contiene clases de dominio limpias y estables.

### Capa B. Restricciones OCL

Contiene reglas semanticas, de obligatoriedad y coherencia.

### Capa C. Codelists y vocabularios controlados

Representa catálogos como paises, idiomas, tipos de entidad, etc.

### Capa D. Mapeo a CVN

Relaciona clases y atributos UML con:

- codigo CVN
- tabla de referencia CVN
- elemento XML CVN si procede

---

## Proceso de trabajo sugerido

## Fase 1. Extraer el inventario conceptual

Debes recorrer el manual y agrupar campos por conceptos de negocio, no por estructura XML.

### Ejemplo

Los campos:

- apellidos
- nombre
- sexo
- nacionalidad
- fecha de nacimiento

deben llevarte a una entidad tipo `Person` o `PersonalIdentification`.

## Fase 2. Detectar entidades transversales reutilizables

Muchas partes de CVN reutilizan patrones comunes:

- entidad organizativa
- localizacion
- periodo temporal
- identificador digital
- publicacion
- palabras clave

Esas piezas no deben duplicarse por modulo.

## Fase 3. Construir paquetes UML

Agrupa por areas funcionales y por reutilizacion.

## Fase 4. Traducir tablas a enumeraciones o codelists

No todo debe ser enum estricto. Algunas tablas son mejores como catalogos externos.

## Fase 5. Añadir restricciones OCL

Empieza por:

- obligatoriedad simple
- obligatoriedad condicional
- coherencia temporal
- restricciones del tipo "otros"

## Fase 6. Añadir trazabilidad

Mantén una tabla de trazabilidad entre:

- elemento UML
- codigo CVN
- nombre del campo
- tabla CVN asociada
- serializacion XML si existe

---

## Propuesta de paquetes UML

Una opcion razonable para un primer modelo es la siguiente.

```text
CVNCore
CVNIdentity
CVNCommon
CVNEducation
CVNProfessionalExperience
CVNTeaching
CVNHealth
CVNResearch
CVNAchievements
CVNVocabularies
CVNMapping
```

---

## Paquete `CVNCore`

Contiene la raiz del modelo.

### Clases propuestas

- `Curriculum`
- `CurriculumVersion`
- `CurriculumOwner`
- `CurricularItem` <<abstract>>

### Idea

`Curriculum` agrega la informacion principal del CV.

Ejemplo conceptual:

- un `Curriculum` pertenece a un `CurriculumOwner`
- un `Curriculum` tiene multiples `CurricularItem`

---

## Paquete `CVNCommon`

Contiene elementos reutilizables en varios modulos.

### Clases propuestas

- `Entity`
- `Location`
- `Address`
- `Period`
- `ContactInfo`
- `Identifier`
- `DigitalIdentifier`
- `Keyword`
- `LanguageCompetence`

### Objetivo

Evitar que cada modulo cree su propia version de entidad, fecha o localizacion.

---

## Paquete `CVNIdentity`

Contiene la informacion personal del titular del curriculum.

### Clases propuestas

- `Person`
- `PersonalIdentification`
- `OfficialDocument`
- `AuthorIdentifier`

### Atributos razonables de `Person`

- `givenName : String`
- `firstFamilyName : String [0..1]`
- `secondFamilyName : String [0..1]`
- `gender : GenderCode [0..1]`
- `nationality : CountryCode [0..1]`
- `birthDate : PartialDate [0..1]`
- `birthPlace : Location [0..1]`

### Relacion con CVN

Este paquete cubre sobre todo el bloque `000.*`.

---

## Paquete `CVNEducation`

Contiene la formacion academica y especializada.

### Clases propuestas

- `AcademicDegree` <<abstract>>
- `UniversityDegree`
- `Doctorate`
- `PostgraduateDegree`
- `SpecializedTraining`
- `HealthSpecialization`
- `HealthResearchTraining`
- `TeachingImprovementCourse`
- `LanguageSkill`

### Posible abstracta reutilizable

`EducationalExperience` con:

- `title`
- `awardingEntity`
- `location`
- `startDate`
- `endDate`
- `duration`

---

## Paquete `CVNProfessionalExperience`

### Clases propuestas

- `ProfessionalSituation` <<abstract>>
- `CurrentProfessionalSituation`
- `PastProfessionalSituation`
- `ProfessionalSummary`
- `EmploymentRelation`

### Atributos habituales

- `employer : Entity`
- `professionalCategory : String`
- `contractType : ContractTypeCode [0..1]`
- `dedication : DedicationCode [0..1]`
- `startDate : PartialDate`
- `endDate : PartialDate [0..1]`
- `functionsDescription : String [0..1]`

---

## Paquete `CVNTeaching`

### Clases propuestas

- `TeachingActivity`
- `AcademicTeaching`
- `HealthTeaching`
- `SupervisedWork`
- `AcademicTutoring`
- `TeachingMaterial`
- `TeachingInnovationProject`
- `TeachingEventContribution`

### Comentario

Este bloque es grande y conviene apoyarse mucho en la abstraccion `PublicationLikeContribution` si quieres reutilizar estructuras.

---

## Paquete `CVNHealth`

### Clases propuestas

- `HealthActivity`
- `InternationalHealthActivity`
- `HealthTrainingActivity`
- `HealthProtocolMaterial`
- `HealthInnovationProject`
- `HealthEventContribution`

### Comentario

La parte sanitaria repite muchos patrones de experiencia, evento, publicacion y organizacion.

---

## Paquete `CVNResearch`

### Clases propuestas

- `ResearchActivity`
- `ResearchGroupParticipation`
- `ResearchProject` <<abstract>>
- `CompetitiveProject`
- `NonCompetitiveProject`
- `ResearchResult` <<abstract>>
- `Publication`
- `ConferenceContribution`
- `DisseminationActivity`
- `ResearchStay`
- `TechnologyTransferActivity`
- `IndustrialProperty`

### Comentario

Probablemente este sera el paquete mas importante para tu TFG si quieres un modelo general de CV academico.

---

## Paquete `CVNAchievements`

### Clases propuestas

- `Award`
- `Recognition`
- `Accreditation`
- `Grant`
- `EvaluatedPeriod`
- `FreeSummary`
- `LeadershipMerit`

---

## Paquete `CVNVocabularies`

### Contenido

Aqui iran los codigos controlados.

### Opciones de modelado

- `Enumeration`
- `CodeList`
- clase catalogo con instancias externas

### Recomendacion concreta

- usa `Enumeration` para conjuntos pequenos y estables
- usa `CodeList` para tablas muy grandes o potencialmente cambiantes

### Ejemplos claros de `Enumeration`

- `GenderCode`
- `DedicationCode`
- `PublicationIdentifierType`

### Ejemplos claros de `CodeList`

- `UNESCOCode`
- `AcademicTitleCode`
- `ProgramCode`
- `EntityTypeCode`

---

## Paquete `CVNMapping`

Este paquete no es de dominio; es de trazabilidad.

### Clases propuestas

- `CvnTrace`
- `CvnFieldBinding`
- `CvnXmlBinding`

### Campos utiles

- `cvnCode : String`
- `cvnName : String`
- `referenceTable : String [0..1]`
- `xmlProperty : String [0..1]`
- `xmlIndicator : String [0..1]`
- `sourceDocument : String`

### Ventaja

Permite que tu modelo UML siga siendo limpio, mientras mantienes compatibilidad documental con CVN.

---

## Clases base recomendadas

Hay ciertas abstracciones que simplifican mucho el modelo.

## `CurricularItem` <<abstract>>

Puede contener:

- `title : String [0..1]`
- `description : String [0..1]`
- `keywords : Keyword[*]`
- `location : Location [0..1]`
- `period : Period [0..1]`
- `relatedEntities : Entity[*]`

## `PublicationLikeContribution` <<abstract>>

Puede contener:

- `publicationTitle : String [0..1]`
- `containerTitle : String [0..1]`
- `publicationDate : PartialDate [0..1]`
- `isbnIssn : String[*]`
- `digitalIdentifiers : PublicationIdentifier[*]`
- `correspondingAuthor : Boolean`

## `OrganizationBoundActivity` <<abstract>>

Puede contener:

- `hostEntity : Entity [0..1]`
- `entityType : EntityTypeCode [0..1]`
- `location : Location [0..1]`

## `TimeBoundActivity` <<abstract>>

Puede contener:

- `startDate : PartialDate [0..1]`
- `endDate : PartialDate [0..1]`
- `duration : DurationValue [0..1]`

---

## Que restricciones deben ir a OCL

No todo debe resolverse con tipos UML. Muchas reglas de CVN son claramente OCL.

## Tipos de restricciones utiles

- obligatoriedad simple
- obligatoriedad condicional
- exclusividad entre campos
- coherencia temporal
- consistencia entre codigo y texto libre
- restricciones de cardinalidad de negocio

---

## Ejemplos de OCL recomendados

## 1. Regla tipo "otros"

```ocl
context AuthorIdentifier
inv OtherTypeRequiresText:
    self.identifierType = IdentifierTypeCode::other implies
    self.otherIdentifierType <> null and self.otherIdentifierType.trim() <> ''
```

## 2. Fechas coherentes

```ocl
context Period
inv StartBeforeEnd:
    self.startDate <> null and self.endDate <> null implies
    self.startDate <= self.endDate
```

## 3. Tesis con entidad y titulo

```ocl
context Doctorate
inv DoctorateHasMinimumInformation:
    self.thesisTitle <> null and self.awardingEntity <> null
```

## 4. Documento oficial mutuamente excluyente

```ocl
context PersonalIdentification
inv SingleOfficialDocumentKind:
    Set{self.dni, self.nie, self.passport}->excluding(null)->size() <= 1
```

## 5. Publicacion con identificador condicionado

```ocl
context PublicationIdentifier
inv ValueMustExist:
    self.value <> null and self.value.trim() <> ''
```

## 6. Curriculum con titular

```ocl
context Curriculum
inv HasOwner:
    self.owner <> null
```

---

## Tipos de datos recomendados

## Tipos simples

- `String`
- `Boolean`
- `Integer`
- `Real`

## Tipos propios recomendables

- `PartialDate`
  - porque CVN admite fecha completa, mes-anio o anio
- `DurationValue`
  - porque la duracion sigue una semantica propia
- `CountryCode`
- `LanguageCode`
- `UNESCOCode`
- `ExternalIdentifierValue`

## Nota importante

No conviertas todos los tipos CVN en clases si no hace falta. Muchos pueden ser `DataType` UML.

---

## Como tratar las tablas auxiliares

## Criterio 1. Enumeration UML

Usala cuando:

- el numero de valores sea pequeno
- el conjunto sea estable
- tenga significado fuerte en el dominio

### Ejemplos

- `GenderCode`
- `TeachingModalityCode`
- `DedicationCode`

## Criterio 2. CodeList

Usala cuando:

- el listado sea grande
- el catalogo sea mantenido externamente
- quieras desacoplarte del detalle operativo

### Ejemplos

- `AcademicTitleCode`
- `UNESCOCode`
- `CVNCategoryCode`
- `ProgramCode`

## Criterio 3. Clase catalogo

Usala cuando necesites:

- codigo
- etiqueta
- idioma
- version
- metadatos de origen

---

## Nivel de granularidad recomendado

## Opcion A. Modelo muy fino

Cada microcampo del CVN se representa individualmente.

### Ventajas

- trazabilidad maxima
- transformacion mas directa

### Inconvenientes

- modelo muy grande
- dificil de mantener
- excesivo para un metamodelo agnostico

## Opcion B. Modelo intermedio

Agrupas campos que conceptualmente forman una unidad.

### Ventajas

- equilibrio entre fidelidad y simplicidad
- mejor para UML + OCL

### Recomendacion

Es la mejor opcion para tu caso.

## Opcion C. Modelo muy abstracto

Captura solo macroconceptos.

### Inconveniente

Pierdes trazabilidad y detalle operativo.

---

## Paquetes iniciales minimos para una primera iteracion

Si quieres empezar sin ahogarte, la mejor primera version es esta.

## Iteracion 1

- `CVNCore`
- `CVNCommon`
- `CVNIdentity`
- `CVNProfessionalExperience`
- `CVNEducation`
- `CVNVocabularies`

## Casos de uso cubiertos

- identificacion personal
- contacto
- situacion profesional actual y anterior
- titulaciones universitarias
- doctorado
- otra formacion de posgrado

## Ventaja

Con esa primera iteracion ya tienes suficientes patrones para:

- entidades
- localizaciones
- periodos
- codelists
- campos condicionales
- reglas OCL

---

## Ejemplo de mini modelo inicial

```text
Curriculum
  - owner : Person [1]
  - professionalSituations : ProfessionalSituation[*]
  - educationRecords : EducationalExperience[*]

Person
  - givenName : String
  - firstFamilyName : String [0..1]
  - secondFamilyName : String [0..1]
  - gender : GenderCode [0..1]
  - nationality : CountryCode [0..1]
  - birthDate : PartialDate [0..1]
  - digitalIdentifiers : AuthorIdentifier[*]

ProfessionalSituation <<abstract>>
  - employer : Entity [0..1]
  - professionalCategory : String [0..1]
  - dedication : DedicationCode [0..1]
  - contractType : ContractTypeCode [0..1]
  - period : Period [0..1]

EducationalExperience <<abstract>>
  - title : String [0..1]
  - awardingEntity : Entity [0..1]
  - location : Location [0..1]
  - issueDate : PartialDate [0..1]

Doctorate extends EducationalExperience
  - thesisTitle : String [0..1]
  - supervisors : Person[*]
  - internationalMention : Boolean [0..1]
```

---

## Trazabilidad recomendada

La trazabilidad debe existir desde el principio.

## Formato minimo de tabla

| Elemento UML | Tipo | Codigo CVN | Nombre CVN | Tabla CVN | XML Property | XML Indicator |
|---|---|---:|---|---|---|---|
| `Person.givenName` | atributo | `000.010.000.020` | Nombre | - | `Identification` | `GivenName` |
| `Person.firstFamilyName` | atributo | `000.010.000.010` | Apellidos | - | `Identification` | `FirstFamilyName` |
| `ProfessionalSituation.professionalCategory` | atributo | `010.010.000.170` | Categoria profesional | - | `Title` | `Name` |

## Ventaja

Asi puedes justificar cada decision de abstraccion sin perder la referencia normativa.

---

## Como documentarlo bien en la memoria

## Estructura sugerida

### 1. Motivacion

Explica por que un modelo conceptual es preferible a un modelo XML-centrico.

### 2. Fuentes normativas

Explica que archivos has usado y con que funcion.

### 3. Criterios de abstraccion

Explica:

- que has agrupado
- que has dejado como atributo
- que has convertido en clase
- que has dejado como catalogo externo

### 4. UML del dominio

Presenta diagramas por paquetes.

### 5. OCL

Agrupa reglas por tipo:

- integridad estructural
- consistencia temporal
- dependencia condicional
- restricciones semanticas

### 6. Trazabilidad con CVN

Incluye una matriz como la anterior.

### 7. Mapeo a serializacion

Explica como se pasaria del modelo conceptual a CVN-XML.

---

## Recomendacion final de enfoque

La mejor estrategia para ti es esta:

- construye primero un **modelo UML de dominio intermedio**
- añade despues **restricciones OCL** para las reglas semanticas
- mantén una **tabla de trazabilidad** contra CVN
- deja el **mapeo XML** como capa separada

En una frase:

> CVN debe ser tu fuente normativa, no tu forma final de pensar el dominio.

Si modelas el dominio primero y el XML despues, tu resultado sera mucho mas limpio, reutilizable y verdaderamente agnostico al lenguaje.

---

## Siguiente paso recomendado

La siguiente iteracion natural seria crear un tercer documento con una propuesta ya casi ejecutable:

1. diagrama de paquetes definitivo
2. lista de clases iniciales con atributos
3. primeras 20 restricciones OCL priorizadas
4. tabla de trazabilidad inicial para `000`, `010` y `020`
