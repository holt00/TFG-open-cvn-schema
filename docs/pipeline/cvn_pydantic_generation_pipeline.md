# Pipeline tecnico para traduccion automatica de CVN XML/XSD a Pydantic

## Objetivo

Este documento describe la arquitectura tecnica propuesta para traducir de forma automatica los artefactos oficiales de CVN a modelos Pydantic con la minima intervencion manual posible.

La propuesta separa dos necesidades distintas:

1. interoperabilidad con el XML CVN oficial,
2. generacion de modelos de dominio mas limpios y reutilizables dentro del proyecto.

La idea central es evitar un error comun: intentar obtener el modelo de dominio final directamente desde `CVN.xsd`. El paquete oficial no contiene una sola capa semantica, sino varias capas complementarias que deben procesarse de forma coordinada.

---

## Paquete fuente canonico

La fuente canonica del pipeline es:

```text
docs/CvnXML_v1.4.3_2.1_17012025/
|- XML/
|  |- SpecificationManual.xml
|  `- CVNTreeModel.xml
`- XSD/
   |- CVN.xsd
   |- Common.xsd
   |- AuxTable.xsd
   |- ISOUtilities.xsd
   |- SpecificationManual.xsd
   `- CVNTreeModel_v1.0.xsd
```

Estos ficheros deben entenderse como tres capas relacionadas pero no equivalentes.

### Capa 1. Estructura XML final

- `XSD/CVN.xsd` define el XML CVN intercambiado por sistemas compatibles.
- El elemento raiz es `CVN`.
- Sus bloques principales son `Version`, `Agent` y una lista repetible de `CvnItem`.

### Capa 2. Tipos tecnicos y valores controlados

- `XSD/Common.xsd` define wrappers y tipos comunes como `CVN_string`, `CVN_date`, `CVN_ISO_639`, `CVN_ISO_3166` y `FlexibleDatesType`.
- `XSD/AuxTable.xsd` define tablas auxiliares internas del ecosistema CVN.
- `XSD/ISOUtilities.xsd` define tablas ISO reutilizadas, especialmente idiomas y paises.

### Capa 3. Metadata funcional y tecnica

- `XML/SpecificationManual.xml` contiene el manual funcional procesable por maquina.
- `XML/CVNTreeModel.xml` describe como se materializan los codigos CVN en el XML tecnico real.
- `XSD/SpecificationManual.xsd` y `XSD/CVNTreeModel_v1.0.xsd` validan esas dos capas XML.

---

## Relaciones observadas entre archivos

Las relaciones tecnicas relevantes detectadas en el analisis son:

- `XSD/CVN.xsd` incluye `Common.xsd` y `AuxTable.xsd`.
- `XSD/Common.xsd` incluye `ISOUtilities.xsd`.
- `XSD/SpecificationManual.xsd` importa el namespace CVN para tipar los idiomas (`lang`) usando `ISOUtilities.xsd`.
- `XSD/CVNTreeModel_v1.0.xsd` define su propio namespace y no cuelga del namespace principal de CVN.
- `XML/SpecificationManual.xml` se valida con `XSD/SpecificationManual.xsd`.
- `XML/CVNTreeModel.xml` se valida con `XSD/CVNTreeModel_v1.0.xsd`.
- `XML/CVNTreeModel.xml` actua como puente entre los codigos funcionales del manual y la estructura XML definida en `CVN.xsd`.

La relacion conceptual es:

```text
SpecificationManual.xml
  -> significado funcional de los codigos CVN

CVNTreeModel.xml
  -> mapeo tecnico de esos codigos a nodos XML

CVN.xsd + Common.xsd + AuxTable.xsd + ISOUtilities.xsd
  -> forma valida del XML y tipos controlados
```

---

## Hallazgos tecnicos relevantes del analisis

### Complejidad estructural de los XSD

Se observaron los siguientes volumenes aproximados:

- `CVN.xsd`: 74 `complexType`, 232 `element`, 125 `attribute`, 3 `choice`
- `Common.xsd`: 11 `complexType`, 1 `choice`
- `AuxTable.xsd`: 33 `simpleType`, casi todo enumeraciones
- `ISOUtilities.xsd`: 2 `simpleType`, pero con enumeraciones muy grandes

Aspectos importantes:

- no se detectaron `xs:any`, `xs:union`, `xs:list` ni mixed content,
- si existe recursion en `Link -> CvnItemType`,
- hay wrappers repetitivos con forma `Item + atributos metadata`,
- hay pocos `choice`, pero estan en zonas importantes,
- el volumen de enums es alto.

### Choices relevantes

Los `choice` identificados afectan a modelado y code generation:

- `OfficialIdType`
- `EntityTypeType`
- `EntityNameType`
- `FlexibleDatesType`

No son suficientes como para bloquear la generacion automatica, pero deben tratarse de forma explicita en la capa semantica.

### Enums grandes

Valores observados:

- `ISO_639`: 428 valores
- `ISO_3166`: 312 valores
- `CVN_Region`: 280 valores
- otras tablas auxiliares con decenas o centenares de valores

Esto implica que la capa estructural puede generar mucho codigo y que la capa de dominio debe decidir con cuidado que tablas se convierten en `Enum` y cuales se mantienen como `str`.

### Particularidad de namespaces

`XML/SpecificationManual.xml` tiene namespace en la raiz y vacia el namespace en los descendientes con `xmlns=""`.

Esto es importante porque:

- el parseo naive con XML suele fallar o dar resultados inconsistentes,
- conviene usar bindings o una logica de parseo que respete exactamente la semantica del documento.

### Cobertura de metadata

Conteos observados:

- `SpecificationManual.xml`: 1456 elementos `Item` y 1456 codigos unicos
- `CVNTreeModel.xml`: 101 nodos `CVNItem`, 939 `Property`, 4635 `Indicator`
- `CVNTreeModel.xml`: 1430 codigos unicos
- solapamiento manual/tree model: 1429 codigos
- codigos en manual no presentes en tree model: 27
- codigo en tree model no presente en manual: `030.010.000.250`

Consecuencia tecnica: el cruce entre ambas capas es muy alto y permite una generacion automatica fiable, pero no perfecta. El pipeline debe reportar discrepancias y no asumir paridad total.

### Situacion de reference tables

`SpecificationManual.xml` utiliza 557 referencias a tablas y 75 nombres de tabla distintos.

Hay dos grupos:

1. tablas internas resolubles con el paquete local:
   - `ISO_3166`
   - `ISO_639`
   - tablas CVN de `AuxTable.xsd`

2. tablas externas o no resueltas con el paquete actual:
   - `ENTITY@Entity.xsd`
   - `THESAURUS@thesaurus.xsd`
   - `UNESCO_CODES`

Estas ultimas no deben bloquear el pipeline. Deben quedar reflejadas como referencias externas y, en la capa de dominio, normalmente modelarse como `str` o placeholders tipados ligeros.

---

## Principio arquitectonico del pipeline

El pipeline no debe intentar resolver todo en una sola pasada.

La arquitectura correcta es de dos pasos:

```text
XSD oficiales
  -> generacion automatica de bindings estructurales Pydantic

SpecificationManual.xml + CVNTreeModel.xml
  -> normalizacion de metadata
  -> reglas semanticas + overrides
  -> generacion automatica de modelos de dominio Pydantic
```

Con esto se separan dos responsabilidades:

- la capa estructural replica fielmente el XML oficial,
- la capa de dominio ofrece modelos mas limpios para la logica del proyecto.

---

## Arquitectura objetivo en el repositorio

Una estructura recomendada es:

```text
src/
├── generated/
│   ├── cvn/
│   ├── specification_manual/
│   └── tree_model/
├── cvn_codegen/
│   ├── load_spec.py
│   ├── load_tree.py
│   ├── normalize.py
│   ├── mapping.py
│   ├── overrides.py
│   └── emit_models.py
└── models/
    └── cvn/
```

### Responsabilidades por paquete

#### `src/generated/`

Contiene codigo generado automaticamente desde XSD. No se edita manualmente.

- `generated.cvn`: bindings del XML CVN final
- `generated.specification_manual`: bindings del manual XML
- `generated.tree_model`: bindings del tree model XML

#### `src/cvn_codegen/`

Contiene la logica del pipeline semantico.

- `load_spec.py`: parseo del manual funcional
- `load_tree.py`: parseo del tree model
- `normalize.py`: indices y estructuras normalizadas
- `mapping.py`: reglas de transformacion de metadata a tipos de dominio
- `overrides.py`: excepciones explicitas y controladas
- `emit_models.py`: escritura de modelos Pydantic de dominio

#### `src/models/cvn/`

Contiene modelos de dominio emitidos o componentes comunes estables que el proyecto quiera exponer como API interna.

---

## Herramientas recomendadas

### Code generation estructural

Herramienta recomendada:

- `xsdata`
- `xsdata-pydantic`

Motivos:

- trabajan directamente con XSD/XML,
- soportan namespaces,
- permiten salida Pydantic,
- reducen mucho la intervencion manual para la capa estructural.

### Comandos orientativos

```bash
uv add --dev "xsdata[cli,lxml]" xsdata-pydantic

xsdata generate docs/CvnXML_v1.4.3_2.1_17012025/XSD/CVN.xsd \
  --output pydantic \
  --package src.generated.cvn

xsdata generate docs/CvnXML_v1.4.3_2.1_17012025/XSD/SpecificationManual.xsd \
  --output pydantic \
  --package src.generated.specification_manual

xsdata generate docs/CvnXML_v1.4.3_2.1_17012025/XSD/CVNTreeModel_v1.0.xsd \
  --output pydantic \
  --package src.generated.tree_model
```

### Ajustes recomendados de generacion

- usar una configuracion versionada de `xsdata`,
- mantener separados los paquetes generados,
- activar opciones como `unnest-classes` si mejoran la legibilidad,
- revisar el impacto de enums gigantes antes de decidir politicas finales de dominio.

---

## Flujo tecnico detallado

### Fase 1. Generacion de bindings estructurales

Entrada:

- `CVN.xsd`
- `SpecificationManual.xsd`
- `CVNTreeModel_v1.0.xsd`

Salida:

- modelos Pydantic estructurales importables

Objetivo:

- parsear XML oficiales,
- serializar de vuelta si es necesario,
- evitar parseo manual repetitivo en fases posteriores.

Notas:

- esta fase no intenta crear el modelo conceptual final,
- wrappers, recursion y nombres tecnicos se aceptan como parte del binding.

### Fase 2. Parseo del manual funcional

Entrada:

- `XML/SpecificationManual.xml`

Extracciones minimas:

- `code`
- nombres multilenguaje
- `ShortName`
- `Type`
- `Obligatory`
- `Multiplicity`
- `ReferenceTable`
- `Link`
- `Delegate`

Objetivo:

- convertir el manual en un indice funcional por codigo.

### Fase 3. Parseo del tree model

Entrada:

- `XML/CVNTreeModel.xml`

Extracciones minimas:

- `CVNItem`
- `Property`
- `Indicator`
- `Child`
- `Value`
- `code`
- `name`

Objetivo:

- reconstruir la ruta tecnica del XML para cada codigo o grupo de codigos.

### Fase 4. Normalizacion y cruce

Objetivo:

- combinar la semantica del manual con la estructura tecnica del tree model.

Vistas recomendadas:

1. indice por `code`
2. indice por `cvn_item_code`
3. vista orientada a ruta XML

Campos normalizados sugeridos:

- `code`
- `manual_name`
- `manual_short_name`
- `manual_type`
- `manual_obligatory`
- `manual_multiplicity`
- `manual_reference_table`
- `tree_cvn_item_code`
- `tree_property_name`
- `tree_indicator_name`
- `tree_value`
- `xml_path`
- `source_file`

Resultado esperado:

- una capa intermedia estable para que el generador semantico no dependa de la estructura cruda del XML.

### Fase 5. Reglas semanticas y overrides

Objetivo:

- traducir metadata CVN a tipos de dominio legibles y estables.

Decisiones que deben quedar fijadas:

- que wrappers colapsan a primitivas,
- que tablas se convierten en `Enum`,
- que referencias externas se modelan como `str`,
- como se trata la multiplicidad,
- como se nombran clases y campos,
- como se registran excepciones pequenas y controladas.

Principio recomendado:

- reglas generales primero,
- overrides solo para casos concretos que no encajen bien.

### Fase 6. Emision de modelos de dominio

Objetivo:

- generar clases Pydantic mas expresivas que los bindings estructurales.

Primer alcance recomendado:

- `Version` / `Agent`
- identificacion personal
- contacto
- campos personales basicos
- un subconjunto representativo de `CVNItem`

Propiedades esperadas del generador:

- salida determinista,
- trazabilidad al codigo CVN,
- separacion entre emitido y manual,
- posibilidad de regenerar sin diffs ruidosos.

### Fase 7. Tests y verificacion

El pipeline debe probar:

- parseo de `SpecificationManual.xml`,
- parseo de `CVNTreeModel.xml`,
- indices por codigo,
- presencia de discrepancias conocidas,
- importacion de modulos generados,
- al menos un flujo end-to-end completo.

### Fase 8. Documentacion y automatizacion

Debe quedar un workflow claro para:

1. instalar dependencias,
2. generar bindings estructurales,
3. parsear y normalizar metadata,
4. aplicar reglas y overrides,
5. emitir modelos de dominio,
6. ejecutar pruebas.

---

## Reglas tecnicas recomendadas para el dominio

### Tipos

Reglas base recomendadas:

- `Alphanumeric` -> `str`
- booleanos CVN -> `bool`
- fechas completas -> `date`
- codigos ISO internos -> `Enum` o alias tipado segun la politica final
- multiplicidad verdadera -> `list[T]`
- campo opcional no multiple -> `T | None`

### Wrappers

Muchos tipos del XSD estructural son wrappers tecnicos como:

- `CVN_string`
- `CVN_date`
- `CVN_ISO_639`
- `CVN_ISO_3166`

En la capa de dominio normalmente deben colapsarse a tipos simples o enums, salvo que haya un motivo claro para conservar la envoltura.

### Enums

Politica recomendada inicial:

- tablas internas estables e incluidas en el paquete -> considerar `Enum`
- referencias externas no resueltas -> `str`

Esto evita bloquear el pipeline por falta de tablas externas.

### Naming

La capa estructural puede conservar nombres tecnicos.

La capa de dominio debe priorizar:

- nombres estables,
- legibilidad para Python,
- trazabilidad al codigo CVN,
- reutilizacion de componentes comunes.

### Traceability

Cada clase o campo generado deberia conservar alguna referencia a:

- codigo CVN,
- ruta XML tecnica,
- fuente de metadata.

Esto es importante para depurar, regenerar y justificar el modelado en el contexto academico del TFG.

---

## Riesgos y limitaciones conocidas

### Riesgos tecnicos

- recursion en `Link -> CvnItemType`
- clases anonimas o nombres poco ergonomicos en la capa generada
- volumen de enums en tablas ISO y auxiliares
- referencias externas no resueltas desde el paquete local
- diferencia parcial entre manual funcional y tree model

### Mitigaciones propuestas

- mantener la capa estructural separada del dominio,
- reportar discrepancias en vez de ocultarlas,
- usar overrides pequenos y bien documentados,
- no tipar fuerte referencias externas hasta disponer de una fuente canonica,
- hacer el generador idempotente y cubierto por pruebas.

---

## Criterios de exito del pipeline

Se considerara que el pipeline esta bien establecido cuando:

- los bindings estructurales se puedan regenerar desde los XSD,
- el manual y el tree model puedan cruzarse automaticamente por `code`,
- existan reglas explicitas de mapeo semantico,
- los modelos de dominio se regeneren sin intervencion manual relevante,
- las limitaciones conocidas queden documentadas,
- el flujo completo tenga pruebas automatizadas.

---

## Relacion con la hoja de ruta por issues

Este documento se alinea con la hoja de ruta definida en `AGENTS.md`:

- `#8`: epic de integracion del pipeline
- `#11`: infraestructura y configuracion
- `#12`: bindings estructurales desde XSD
- `#13`: parseo y normalizacion de metadata
- `#14`: reglas de mapeo y overrides
- `#15`: generador de dominio
- `#16`: pruebas del pipeline
- `#17`: documentacion y automatizacion final

En otras palabras, este documento describe la arquitectura tecnica; `AGENTS.md` define como ejecutar esa arquitectura en forma de roadmap operativo.
