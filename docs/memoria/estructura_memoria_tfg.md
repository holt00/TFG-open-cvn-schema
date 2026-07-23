# Estructura y trazabilidad de la memoria del TFG

## Proposito del documento

Este documento recoge la estructura acordada para redactar la memoria del Trabajo
Fin de Grado del proyecto Open CVN. Es una guia interna de planificacion y
trazabilidad, no forma parte del texto final de la memoria.

La memoria final debe ser un documento academico autocontenido, profesional y
preparado para ser evaluado por un tribunal. No debe mencionar que su estructura
procede de otros trabajos, memorias, guias, conversaciones o documentos de
orientacion. Cualquier concepto, dato, decision o afirmacion relevante debe estar
explicado dentro de la propia memoria o respaldado mediante bibliografia,
documentacion oficial, resultados verificables o anexos.

## Principios obligatorios de redaccion

- La memoria debe autocontenerse: todo elemento citado, figura, tabla, resultado,
  comando, decision tecnica o limitacion debe explicarse en el cuerpo del trabajo,
  en la bibliografia o en los anexos.
- No deben aparecer referencias a memorias de otros alumnos, guias de consejos,
  conversaciones, prompts, herramientas de asistencia o criterios informales de
  redaccion.
- No deben incluirse menciones a Inteligencia Artificial, herramientas de IA o
  asistencia automatica salvo que exista una exigencia normativa explicita de la
  universidad o del tribunal.
- No deben hacerse suposiciones no justificadas. Las afirmaciones deben apoyarse
  en evidencia tecnica, documentacion oficial, bibliografia o resultados del
  propio proyecto.
- El tono debe ser academico, tecnico y sobrio. La memoria debe presentar el
  trabajo como una contribucion de Computacion, no como una simple aplicacion de
  gestion.
- La redacción final debe emplear un lenguaje formal y académico en todo momento.
  Deben evitarse formulaciones coloquiales, ambiguas o propias de notas de trabajo.
- Antes de redactar, reescribir, ampliar o revisar contenido LaTeX de los
  capitulos, debe usarse la skill local `tfg-mapi-style` como guia de calidad de
  redaccion academica. Esta regla no autoriza copiar literalmente el estilo,
  formulas o contenido de ningun documento externo; la skill debe emplearse para
  asimilar criterios de claridad, progresion argumental, formalidad y prudencia
  tecnica.
- La memoria debe estar escrita en español correcto, con tildes y grafías
  normativas. En particular, deben escribirse correctamente términos como
  `España`, `español`, `también`, `información`, `currículo`, `académico`,
  `capítulo`, `validación` o `transformación` en el texto LaTeX final.
- El proyecto LaTeX debe compilarse con soporte explícito de español. La
  configuración vigente usa XeLaTeX con `polyglossia` y
  `\setmainlanguage{spanish}` en `docs/memoria/include/configuracion.tex`; esta
  configuración debe conservarse salvo que se sustituya por una alternativa
  equivalente y justificada.
- La fuente principal del documento debe ser portable en TeX Live. La versión
  vigente usa `TeX Gyre Termes` en `docs/memoria/TFG.tex` para evitar depender de
  fuentes del sistema no instaladas en todos los entornos.
- Los conceptos técnicos deben introducirse antes de utilizarse como argumento. En
  particular, no deben aparecer menciones a XML, XSD, serialización u otros
  detalles internos de CVN antes de explicar que el CVN tratado por el proyecto no
  se limita a un documento visual, sino que se apoya en artefactos estructurados.
- La redaccion no debe presentar XML como la base unica del trabajo. Debe quedar
  claro que el proyecto se basa en la norma CVN y en su ecosistema de artefactos
  oficiales; XML es el mecanismo de representacion e intercambio utilizado por CVN
  para serializar los datos, no el unico objeto conceptual del proyecto.
- La aplicación CLI debe presentarse como una herramienta funcional y demostrador
  del enfoque, pero la aportación principal es la arquitectura computacional para
  representar, validar, transformar y exportar información curricular compleja.
- La motivación de la memoria debe permanecer alineada con
  `docs/descripcion_tfg_oficial.txt`: el proyecto responde a la necesidad de
  definir una representación de bajo nivel que permita crear herramientas abiertas
  para agilizar la creación, mantenimiento, actualización y adaptación de
  currículos CVN en el ámbito universitario e investigador. Esta motivación debe
  aparecer de forma explícita en la introducción y conectarse con la posibilidad
  de evolución colaborativa del formato.
- Las limitaciones deben explicarse de forma profesional. No deben ocultarse, pero
  deben presentarse como parte del analisis tecnico del dominio y de las garantias
  reales del sistema.
- La bibliografia debe anotarse durante la redaccion del estado del arte y de los
  capitulos tecnicos, no al final.
- Cada capitulo principal debe redactarse en un fichero LaTeX independiente bajo
  `docs/memoria/chapters/`. El fichero principal `docs/memoria/TFG.tex` solo debe
  incluir los capitulos que esten siendo redactados o ya esten completos.
- Cuando un capitulo necesite una fuente bibliografica que no exista todavia en
  `docs/memoria/bib/ref.bib`, debe identificarse de forma explicita antes de
  consolidar la redaccion. No deben dejarse afirmaciones tecnicas relevantes sin
  cita si dependen de informacion externa al propio proyecto.
- La bibliografia del documento de investigacion inicial puede reutilizarse como
  punto de partida, pero las entradas deben revisarse y adaptarse al fichero
  bibliografico final de la memoria antes de citarlas.

## Enfoque academico del TFG

El trabajo se encuadra en la intensificacion de Computacion. Por tanto, la
memoria debe priorizar los siguientes ejes:

- representacion computable de informacion curricular compleja
- analisis de estructuras XML/XSD y artefactos oficiales heterogeneos
- generacion automatica de modelos y artefactos a partir de fuentes formales
- normalizacion y trazabilidad de metadatos
- separacion entre estructura de serializacion y modelo de dominio
- validacion formal mediante JSON Schema y modelos Pydantic
- transformacion entre formatos estructurados
- definicion de una arquitectura reproducible por capas
- evaluacion tecnica mediante pruebas automatizadas, verificaciones de
  consistencia y flujos end-to-end

La memoria no debe estar enfocada principalmente como un TFG de Ingenieria del
Software basado en requisitos de usuario, sprints, usabilidad o producto final.
Esos elementos pueden aparecer cuando sean utiles, especialmente en anexos o en la
descripcion de la herramienta, pero no deben desplazar el nucleo computacional del
trabajo.

## Estructura final acordada

La memoria tendra un maximo de ocho capitulos principales:

1. Introduccion, motivacion y objetivos
2. Antecedentes y estado del arte
3. Analisis del ecosistema CVN y propuesta de solucion
4. Metodologia, herramientas y arquitectura general
5. Implementacion del pipeline de generacion y normalizacion
6. Formato Open CVN, validacion y herramienta de gestion
7. Evaluacion, resultados y discusion
8. Conclusiones, competencias y trabajo futuro

Despues del capitulo 8 se reservara espacio para anexos y bibliografia.

Los ficheros LaTeX previstos para los capitulos son:

| Capitulo | Fichero |
|---|---|
| 1. Introduccion, motivacion y objetivos | `docs/memoria/chapters/ch1.tex` |
| 2. Antecedentes y estado del arte | `docs/memoria/chapters/ch2.tex` |
| 3. Analisis del ecosistema CVN y propuesta de solucion | `docs/memoria/chapters/ch3.tex` |
| 4. Metodologia, herramientas y arquitectura general | `docs/memoria/chapters/ch4.tex` |
| 5. Implementacion del pipeline de generacion y normalizacion | `docs/memoria/chapters/ch5.tex` |
| 6. Formato Open CVN, validacion y herramienta de gestion | `docs/memoria/chapters/ch6.tex` |
| 7. Evaluacion, resultados y discusion | `docs/memoria/chapters/ch7.tex` |
| 8. Conclusiones, competencias y trabajo futuro | `docs/memoria/chapters/ch8.tex` |

## Convencion de estado de capitulos

Cada capitulo debe incluir un identificador de estado inmediatamente debajo del
titulo en este documento de trazabilidad. Este identificador permite saber si el
capitulo esta sin redactar, en redaccion o terminado.

Estados permitidos:

- `PENDIENTE`: el capitulo esta planificado, pero aun no se ha redactado.
- `EN_PROCESO`: el capitulo esta siendo redactado o revisado.
- `COMPLETADO`: el capitulo esta redactado y revisado para la version actual de
  la memoria.

Formato obligatorio:

```text
Estado: PENDIENTE | EN_PROCESO | COMPLETADO
```

Estado inicial:

| Capitulo | Estado |
|---|---|
| 1. Introduccion, motivacion y objetivos | `EN_PROCESO` |
| 2. Antecedentes y estado del arte | `EN_PROCESO` |
| 3. Analisis del ecosistema CVN y propuesta de solucion | `EN_PROCESO` |
| 4. Metodologia, herramientas y arquitectura general | `EN_PROCESO` |
| 5. Implementacion del pipeline de generacion y normalizacion | `PENDIENTE` |
| 6. Formato Open CVN, validacion y herramienta de gestion | `PENDIENTE` |
| 7. Evaluacion, resultados y discusion | `PENDIENTE` |
| 8. Conclusiones, competencias y trabajo futuro | `PENDIENTE` |

## Capitulo 1: Introduccion, motivacion y objetivos

Estado: `EN_PROCESO`

Estado de redaccion actual: el primer borrador completo del capitulo existe en
`docs/memoria/chapters/ch1.tex` y esta incluido en `docs/memoria/TFG.tex`. La
compilacion completa de la memoria con `xelatex`, `bibtex`, `xelatex` y
`xelatex` genera `docs/memoria/TFG.pdf` sin errores bloqueantes, sin referencias
indefinidas y sin citas indefinidas. El capitulo permanece en `EN_PROCESO` hasta
su revisión de contenido. La introducción se ha revisado para aplicar un registro
formal y académico, corregir grafías españolas en el texto LaTeX, presentar XML,
XSD y la serialización oficial solo después de explicar que CVN se apoya en
artefactos estructurados, no solo en un documento visual, y conectar la motivación
con la necesidad oficial de herramientas abiertas que agilicen la creación,
mantenimiento, actualización y adaptación de currículos CVN. La configuración de
fuente del documento usa `TeX Gyre Termes`, disponible en TeX Live, en lugar de
depender de fuentes externas del sistema. El capitulo tambien se ha reescrito con
un registro academico mas elaborado, progresivo y prudente, siguiendo las reglas
internas de estilo `tfg-mapi-style` sin copiar formulas textuales externas. En
esta revisión se han alineado las competencias citadas con la descripción oficial
del TFG: `CM1`, `CM2`, `CM5` y `CM6`. Tras una revisión de contenido posterior, el
capítulo incorpora ahora un objetivo específico, una contribución y menciones
explícitas en el alcance y en la estructura del documento sobre los mecanismos de
importación deterministas y asistidos por modelos de lenguaje (LLM), alineados con
la exigencia normativa explícita de la descripción oficial del TFG y con el
trabajo ya implementado en las issues `#69` y `#70`. La tabla de objetivos y
capítulos se ha renumerado en consecuencia (`OE9` importación, `OE10`
verificación).

### Objetivo del capitulo

Presentar el problema general, justificar la motivacion del TFG, delimitar el
alcance del proyecto y establecer los objetivos que se retomaran en las
conclusiones.

### Contenido recomendado

- Contexto del CVN como formato normalizado en Espana para representar
  curriculos academicos y de investigacion.
- Problema de partida: aunque CVN existe, su uso automatizado sigue siendo
  complejo por la dependencia del XML oficial, la heterogeneidad de los artefactos
  asociados, la dificultad de validacion y la necesidad de adaptar curriculos a
  distintos contextos.
- Motivacion computacional: representar conocimiento curricular complejo de forma
  estructurada, validable, transformable y trazable.
- Objetivo general: disenar e implementar una arquitectura computacional abierta
  para representar, validar, transformar, almacenar y exportar curriculos
  academicos tomando CVN como fuente de referencia.
- Objetivos especificos:
  - analizar el ecosistema CVN y sus artefactos XML/XSD auxiliares
  - estudiar alternativas de representacion, modelado y validacion de datos
    curriculares complejos
  - generar bindings estructurales reproducibles desde los XSD oficiales
  - normalizar metadatos funcionales y tecnicos de CVN
  - definir reglas semanticas conservadoras con trazabilidad hacia las fuentes
  - generar modelos de dominio y artefactos conceptuales
  - definir un formato Open CVN JSON validable
  - implementar parser, validador e importadores deterministas cuando sea posible
  - construir una herramienta local que demuestre el flujo completo de gestion y
    exportacion
  - verificar el sistema mediante pruebas automatizadas y flujos end-to-end
- Competencias de Computacion cubiertas por el trabajo.
- Contribuciones principales.
- Estructura del documento.

### Elementos recomendados

- Tabla de objetivos especificos y capitulos donde se tratan.
- Tabla de competencias y evidencias dentro del proyecto.
- Esquema general del flujo Open CVN.

## Capitulo 2: Antecedentes y estado del arte

Estado: `EN_PROCESO`

Estado de redaccion actual: el primer borrador completo del capitulo existe en
`docs/memoria/chapters/ch2.tex` y esta incluido en `docs/memoria/TFG.tex`. El
capitulo se ha redactado con el registro academico definido para el documento,
usando `tfg-mapi-style` como guia de calidad. Tras revision de alcance, el
capitulo evita repetir la introduccion general del Capitulo 1 y no desarrolla el
ecosistema CVN, que queda reservado para el Capitulo 3. CVN se mantiene solo como
referencia contextual minima dentro del estado del arte. El capitulo se ha
ampliado con fuentes oficiales y documentacion primaria sobre XML 1.0, XSD 1.1,
JSON Schema, Pydantic, JSON-LD 1.1, ORCID y RO-Crate, e incorpora una indicacion
explicita de que UML se usara como notacion principal para representar el esquema
conceptual. La compilacion completa de la memoria con `xelatex`, `bibtex`,
`xelatex` y `xelatex` genera `docs/memoria/TFG.pdf` con 40 paginas, sin errores
bloqueantes, sin referencias indefinidas y sin citas indefinidas. El capitulo
permanece en `EN_PROCESO` hasta su revision de contenido.

Tras una primera revision de contenido, se depuraron dos entradas bibliograficas
sin cita real (`w3c_xml`, `json_ld_org`) y se incorporaron dos de los elementos
recomendados pendientes: una tabla comparativa de modelos de interoperabilidad
curricular (CERIF, VIVO, ROH) en la seccion de interoperabilidad y una tabla
comparativa de formatos de serializacion y validacion (XML/XSD, JSON+JSON Schema,
JSON-LD, YAML) en la seccion correspondiente. El diagrama UML reducido previsto
para este capitulo se pospone deliberadamente a un capitulo posterior, una vez
exista el modelo conceptual completo del dominio del que derivarlo. La
compilacion completa de la memoria con `xelatex`, `bibtex`, `xelatex` y `xelatex`
tras estos cambios genera `docs/memoria/TFG.pdf` con 42 paginas, sin errores
bloqueantes, sin referencias indefinidas y sin citas indefinidas.

### Objetivo del capitulo

Construir el contexto teorico y tecnico necesario para entender el problema,
partiendo de lo general hacia lo particular. El capitulo debe terminar
posicionando la solucion propuesta y justificando por que se adopta una
arquitectura propia, abierta y validable.

### Contenido recomendado

- Gestion de curriculos academicos e investigadores como problema de
  representacion de informacion compleja.
- Interoperabilidad curricular y sistemas de informacion de investigacion.
- Modelos conceptuales y semanticos relacionados:
  - CERIF
  - VIVO
  - ROH
- Formatos de serializacion y validacion:
  - XML y XSD
  - JSON
  - JSON Schema
  - JSON-LD
  - YAML
- Tecnologias y enfoques de modelado:
  - LinkML
  - UML/OCL
  - BESSER
  - Pydantic
- Uso de UML como notacion principal para representar el esquema conceptual del
  dominio antes de su materializacion en modelos ejecutables y esquemas de
  validacion.
- Discusion razonada de alternativas:
  - por que no se adopta una infraestructura semantica pesada como nucleo del TFG
  - por que JSON, JSON Schema y Pydantic encajan con los objetivos practicos del
    proyecto

### Elementos recomendados

- Tabla comparativa de formatos de serializacion y validacion.
- Tabla comparativa de modelos o enfoques conceptuales.
- Diagrama UML reducido que ilustre el papel del modelado conceptual en la
  solucion.
- Resumen final que conecte los antecedentes con la propuesta de solucion.

## Capitulo 3: Analisis del ecosistema CVN y propuesta de solucion

Estado: `EN_PROCESO`

Estado de redaccion actual: el primer borrador completo del capitulo existe en
`docs/memoria/chapters/ch3.tex` y esta incluido en `docs/memoria/TFG.tex`. El
capitulo describe las cuatro capas del paquete oficial CVN (manual PDF, manual
XML, modelo en arbol, XSD) mas las tres familias auxiliares (Entity,
ReferenceTables/Subtypes, Thesaurus), analiza el XML embebido en los PDF CVN,
detalla cuatro categorias de limitaciones tecnicas con evidencia concreta
(discrepancia `<Type>` no declarada en el modelo de arbol, construcciones XSD
que no se trasladan de forma perfecta a estructuras ejecutables, tablas
auxiliares no siempre cerradas, referencias sin tabla equivalente y deriva de
empaquetado), presenta la arquitectura Open CVN por capas y cierra con el
alcance y las exclusiones. Los identificadores de issues y las rutas del
repositorio se mantienen fuera del texto final, tal y como exige la regla de
autocontencion.

El capitulo incorpora dos figuras y dos tablas generadas especificamente para
la memoria: `docs/memoria/figs/open_cvn_source_separation.png` (diagrama de
separacion entre el paquete CVN y Open CVN, con fuente PlantUML propia en
`docs/memoria/figs/open_cvn_source_separation.puml`) y
`docs/memoria/figs/open_cvn_presentation_overview.png` (vista UML compacta
renderizada desde el `.puml` de presentacion ya existente en
`docs/diagrams/open_cvn_presentation_overview.puml`, issue `#44`). Las
referencias hacia los capitulos 6 y 7, que todavia no existen como ficheros,
se han escrito como texto literal ("Capitulo 6", "Capitulo 7") en lugar de
`\ref{}`, siguiendo la misma convencion ya usada en los capitulos 1 y 2 para
evitar referencias indefinidas.

La compilacion completa de la memoria con `xelatex`, `bibtex`, `xelatex` y
`xelatex` genera `docs/memoria/TFG.pdf` con 54 paginas, sin errores
bloqueantes, sin referencias indefinidas, sin citas indefinidas y sin
`overfull hbox`. El capitulo permanece en `EN_PROCESO` hasta su revision de
contenido.

### Objetivo del capitulo

Explicar que contiene realmente el ecosistema CVN usado como fuente, que
limitaciones tecnicas se detectan y como esas limitaciones justifican la
propuesta Open CVN.

### Contenido recomendado

- Descripcion del paquete oficial CVN usado como fuente del proyecto.
- Funcion de CVN y FECYT en el contexto academico espanol.
- Fuentes principales analizadas:
  - `CVN.xsd`
  - `SpecificationManual.xml`
  - `CVNTreeModel.xml`
  - `Common.xsd`
  - `AuxTable.xsd`
  - `ISOUtilities.xsd`
  - `ReferenceTables.xml`
  - `Subtype_Spa.xml`
  - `Entity.xml`
  - `Thesaurus.xml`
- Papel de cada fuente dentro del sistema.
- Papel del XML embebido en documentos CVN PDF y sus implicaciones para el
  procesamiento automatico cuando exista informacion estructurada reutilizable.
- Limitaciones y dificultades detectadas:
  - discrepancias entre XML y XSD en determinados artefactos
  - estructuras XSD que no se trasladan de forma perfecta a modelos Python
  - cardinalidades que requieren interpretacion semantica adicional
  - atributos generados con tipos demasiado genericos
  - tablas auxiliares que no siempre son enumeraciones cerradas
  - referencias no resueltas o insuficientemente trazables
  - separacion insuficiente entre estructura XML y significado curricular
- Propuesta de solucion:
  - por que no basta con copiar CVN-XML como modelo interno
  - por que la trazabilidad hacia CVN es necesaria para no perder semantica
  - arquitectura por capas
  - generacion reproducible desde fuentes oficiales
  - normalizacion de metadatos
  - politica semantica conservadora
  - modelos de dominio y modelo conceptual
  - uso de UML para representar el esquema conceptual derivado del analisis del
    dominio
  - formato Open CVN JSON
  - parser, validador y herramienta local como demostracion del flujo completo
- Alcance y exclusiones:
  - que partes se automatizan con garantias
  - que partes se mantienen como mapeo parcial
  - que partes quedan documentadas como limitaciones o trabajo futuro

### Elementos recomendados

- Tabla de fuentes CVN, informacion que aportan y uso dentro del proyecto.
- Tabla de limitaciones detectadas y respuesta de diseno.
- Diagrama que muestre la separacion entre CVN-XML y el modelo Open CVN.
- Diagrama UML del esquema conceptual o de una parte representativa del dominio.

## Capitulo 4: Metodologia, herramientas y arquitectura general

Estado: `EN_PROCESO`

Estado de redaccion actual: el primer borrador completo del capitulo existe en
`docs/memoria/chapters/ch4.tex` y esta incluido en `docs/memoria/TFG.tex`. El
capitulo describe la metodologia en cinco fases (analisis inicial, exploracion
de artefactos oficiales, diseno incremental de capas, implementacion
reproducible, verificacion automatizada) con documentacion continua de
decisiones y limitaciones como criterio transversal; justifica con cita
bibliografica cada herramienta empleada (Python, `uv`, `xsdata` + extension
Pydantic, Pydantic, JSON Schema, SQLite, Jinja, `pytest` + `pytest-xdist`, Git y
GitHub Actions); presenta la arquitectura general por capas agrupada en cuatro
bloques con un diagrama PlantUML propio de la memoria y su correspondencia con
los modulos reales del repositorio; y cierra explicando los contratos entre
capas y el razonamiento arquitectonico (capa estructural como fidelidad hacia
el XML oficial, sin limpieza semantica manual sobre codigo generado). A
diferencia de los capitulos 1-3, este capitulo si nombra explicitamente rutas
del repositorio (`src/generated/`, `src/cvn_codegen/`, `src/models/cvn/`,
`schemas/`, `src/open_cvn/`, `src/open_cvn_app/`), porque su contenido
recomendado lo exige de forma explicita; no se mencionan en cambio numeros de
issue o hotfix ni documentos internos de planificacion.

Se anadieron seis entradas bibliograficas nuevas a `docs/memoria/bib/ref.bib`
(`xsdata_docs`, `uv_docs`, `pytest_docs`, `sqlite_docs`, `jinja_docs`,
`github_actions_docs`), todas citadas en el propio capitulo. El diagrama de
arquitectura se genero como PlantUML propio de la memoria en
`docs/memoria/figs/open_cvn_layered_architecture.puml`, renderizado a
`docs/memoria/figs/open_cvn_layered_architecture.png`. Las referencias a los
capitulos 5 y 7, que todavia no existen como ficheros, se escribieron como
texto literal en lugar de `\ref{}`, siguiendo la misma convencion ya usada en
capitulos anteriores.

La compilacion completa de la memoria con `xelatex`, `bibtex`, `xelatex` y
`xelatex` genera `docs/memoria/TFG.pdf` con 63 paginas, sin errores
bloqueantes, sin referencias indefinidas, sin citas indefinidas y sin
`overfull hbox`. El capitulo permanece en `EN_PROCESO` hasta su revision de
contenido.

Tras una revision de claridad, la seccion 4.3 (arquitectura general por capas)
se reestructuro en cuatro subsecciones numeradas (4.3.1 a 4.3.4, una por
bloque de la figura), cada una con un desglose en lista de las etapas
concretas que agrupa (entrada, proceso, salida y modulo responsable). Esto
sustituye los dos parrafos densos originales por una explicacion mas granular
sin invadir el detalle de implementacion reservado al Capitulo 5. El parrafo
de transicion hacia la Tabla 4.2 se simplifico para evitar repetir la
separacion de modulos ya explicada en las subsecciones. La compilacion tras
este cambio sigue generando `docs/memoria/TFG.pdf` con 63 paginas, sin
errores, referencias, citas indefinidas ni `overfull hbox`.

### Objetivo del capitulo

Explicar el proceso tecnico seguido, las herramientas empleadas y la arquitectura
global antes de entrar en los detalles de implementacion.

### Contenido recomendado

- Metodologia adaptada a un TFG de Computacion:
  - analisis inicial del dominio y de formatos
  - exploracion de artefactos oficiales
  - diseno incremental de capas
  - implementacion reproducible
  - verificacion automatizada
  - documentacion continua de decisiones y limitaciones
- Herramientas principales:
  - Python
  - Pydantic
  - xsdata
  - JSON Schema
  - SQLite
  - Jinja/LaTeX para exportacion
  - pytest
  - Git y GitHub Actions
- Arquitectura por capas:

```text
Paquete oficial CVN
-> XSD + XML oficiales
-> bindings estructurales Pydantic
-> normalizacion de metadatos
-> resolucion de referencias auxiliares
-> politica semantica
-> modelos de dominio Pydantic
-> modelo conceptual agnostico
-> JSON Schema + formato Open CVN JSON
-> parser y validador
-> herramienta local
-> almacenamiento y exportacion
```

- Responsabilidad de cada capa.
- Separacion entre codigo generado y codigo mantenido manualmente.
- Estructura del repositorio:
  - `src/generated/`
  - `src/cvn_codegen/`
  - `src/models/cvn/`
  - `schemas/`
  - `src/open_cvn/`
  - `src/open_cvn_app/`
- Contratos entre capas y razonamiento arquitectonico.

### Elementos recomendados

- Diagrama principal de arquitectura por capas.
- Tabla de herramientas y justificacion de uso.
- Tabla de modulos del repositorio y responsabilidades.

## Capitulo 5: Implementacion del pipeline de generacion y normalizacion

Estado: `PENDIENTE`

### Objetivo del capitulo

Describir como se implementa la parte computacional que transforma fuentes CVN en
artefactos estructurados, metadatos normalizados, modelos de dominio, modelo
conceptual, diagramas y JSON Schema.

### Contenido recomendado

- Generacion estructural con `xsdata`.
- Runner de generacion y comandos reproducibles.
- Paquetes generados desde XSD.
- Extraccion desde `SpecificationManual.xml`.
- Extraccion desde `CVNTreeModel.xml`.
- Normalizacion por codigo CVN.
- Resolucion auxiliar mediante:
  - `ReferenceTables.xml`
  - `Subtype_Spa.xml`
  - `Entity.xml`
  - `Thesaurus.xml`
- Politica semantica:
  - texto
  - fecha
  - numero
  - enum cerrado
  - catalogo abierto
  - referencia a entidad
  - tesauro
  - subtipo
  - referencia no resuelta
- Generacion de modelos de dominio Pydantic.
- Extraccion del modelo conceptual agnostico.
- Generacion de diagramas y JSON Schema.
- Mecanismos de trazabilidad desde campo generado hasta fuente CVN.

### Resultados tecnicos que pueden mencionarse

- Numero de codigos normalizados.
- Numero de codigos presentes en manual y modelo de arbol.
- Numero de codigos presentes solo en una fuente.
- Numero de modelos o archivos generados.
- Casos relevantes de referencias resueltas y no resueltas.

Estos valores deben comprobarse antes de redactar la version final y no deben
presentarse si no coinciden con la linea base vigente del repositorio.

### Elementos recomendados

- Tabla de etapas del pipeline, entrada, salida y modulo responsable.
- Fragmento reducido de metadato normalizado.
- Diagrama de trazabilidad de un campo desde CVN hasta Open CVN.

## Capitulo 6: Formato Open CVN, validacion y herramienta de gestion

Estado: `PENDIENTE`

### Objetivo del capitulo

Explicar el resultado funcional del proyecto sin desplazar el foco
computacional: el formato abierto, la validacion, los parsers, los importadores y
la herramienta local que demuestra el uso del sistema.

### Contenido recomendado

- Definicion del formato Open CVN JSON.
- Estructura raiz canonica:

```json
{
  "schema_version": "...",
  "metadata": {},
  "curriculum": {},
  "extensions": {}
}
```

- Organizacion curricular por areas conceptuales.
- JSON Schema:
  - ubicacion del schema
  - version de JSON Schema usada
  - extensiones de trazabilidad
- Parser y validador:
  - lectura de Open CVN JSON
  - validacion estructural
  - validacion runtime
  - advertencias semanticas conservadoras
- Importacion:
  - Open CVN JSON
  - CVN XML con mapeo semantico parcial
  - CVN PDF cuando sea posible extraer informacion estructurada
- Herramienta local:
  - inicializacion de almacenamiento
  - importacion y exportacion
  - SQLite
  - curriculum maestro
  - versiones derivadas
  - seleccion de secciones y entradas
  - exportacion a LaTeX
  - generacion opcional de PDF
- Alcance funcional y garantias reales de cada flujo.

### Elementos recomendados

- Esquema de la estructura Open CVN JSON.
- Diagrama de flujo de importacion y validacion.
- Tabla de comandos principales de la herramienta.
- Ejemplo reducido de curriculum maestro y version derivada.

## Capitulo 7: Evaluacion, resultados y discusion

Estado: `PENDIENTE`

### Objetivo del capitulo

Demostrar que el sistema se ha evaluado de forma reproducible y discutir que
garantias proporciona. La evaluacion debe ser tecnica y adecuada a Computacion:
validacion, consistencia, reproducibilidad, cobertura funcional y flujos
end-to-end.

### Contenido recomendado

- Diseno de la evaluacion.
- Niveles de evaluacion:
  - evaluacion estructural de artefactos generados
  - evaluacion de normalizacion y trazabilidad
  - evaluacion de politica semantica
  - evaluacion de JSON Schema y validacion runtime
  - evaluacion de parsers e importadores
  - evaluacion de almacenamiento y versiones
  - evaluacion de exportacion
  - evaluacion end-to-end de flujos completos
- Suite de pruebas automatizadas.
- Comando principal de verificacion.
- Resultados de pruebas con la linea base vigente.
- Integracion continua si aplica.
- Discusion:
  - que partes son reproducibles
  - que partes ofrecen garantias fuertes
  - que partes son parciales
  - que limitaciones proceden del paquete CVN
  - que limitaciones proceden del alcance del TFG
  - que no debe presentarse como conversion completa o validacion semantica total

### Elementos recomendados

- Tabla de categorias de pruebas y objetivo de cada una.
- Tabla de comandos de verificacion.
- Tabla de garantias del sistema frente a limitaciones conocidas.
- Resumen de resultados verificables.

## Capitulo 8: Conclusiones, competencias y trabajo futuro

Estado: `PENDIENTE`

### Objetivo del capitulo

Cerrar la memoria retomando los objetivos del capitulo 1, justificando su grado
de cumplimiento, relacionando el trabajo con las competencias de Computacion y
presentando limitaciones y lineas futuras.

### Contenido recomendado

- Cumplimiento del objetivo general.
- Cumplimiento de cada objetivo especifico en el mismo orden en que se presento
  en el capitulo 1.
- Contribuciones principales:
  - analisis computacional del ecosistema CVN
  - separacion entre XML estructural y dominio curricular
  - arquitectura reproducible por capas
  - normalizacion y trazabilidad
  - formato JSON abierto y validable
  - parser, validador y herramienta local
  - evaluacion tecnica mediante pruebas y flujos reproducibles
- Competencias desarrolladas y evidencia concreta de cada una.
- Limitaciones:
  - inconsistencias entre artefactos CVN
  - expresividad limitada de algunos bindings generados
  - referencias auxiliares no resueltas
  - importacion XML semantica parcial
  - JSON Schema no captura toda la semantica del dominio
  - generacion PDF dependiente de motor TeX
- Trabajo futuro:
  - completar mapeo semantico XML CVN
  - ampliar validaciones de dominio
  - mejorar cobertura de tablas auxiliares
  - evaluar con curriculos reales
  - desarrollar una interfaz grafica si se considera necesario
  - estudiar extensiones semanticas como JSON-LD
  - integracion con fuentes institucionales
  - estudiar la incorporacion de restricciones OCL (Object Constraint Language)
    sobre los diagramas conceptuales para expresar invariantes de dominio no
    representables en UML puro (ver nota de investigacion mas abajo)

### Elementos recomendados

- Tabla de objetivos y grado de cumplimiento.
- Tabla de competencias y evidencias.
- Tabla de limitaciones y trabajo futuro asociado.

### Nota de investigacion: estudio sobre incorporacion de OCL en los diagramas conceptuales

Esta nota registra los hallazgos de una sesion de analisis (sin modificacion de
codigo ni de diagramas) que evaluo si anadir restricciones OCL a los diagramas
PlantUML de `docs/diagrams/` mejoraria su claridad y legibilidad. Se deja aqui
como base para que un desarrollo futuro del capitulo 8 (o de la propia capa de
extraccion conceptual) pueda retomarlo sin repetir el analisis.

Estado actual observado en `docs/diagrams/*.puml`:

- Los diagramas ya codifican presencia y cardinalidad por atributo mediante
  estereotipos (`<<required, single>>`, `<<optional, repeated>>`), tipado
  conceptual (`value_object<X>`, `controlled_reference`, `date_like`,
  `duration_like`) y multiplicidades en las composiciones.
- Las relaciones son deliberadamente conservadoras desde el issue `#43`
  (`docs/diagrams/README.md`, seccion "Known Scope Limits"): un diagrama de
  clases UML solo puede expresar estructura, tipo y cardinalidad por atributo
  aislado, no reglas que combinen varios atributos entre si.

Patrones candidatos a formalizacion OCL, identificados con evidencia concreta
en los propios `.puml`:

1. Patron "valor controlado + campo `_otros`", el mas frecuente (aparece en
   casi todas las areas): por ejemplo `modalidad_de_contrato` /
   `modalidad_de_contrato_otros` y `tipo_de_entidad` / `tipo_de_entidad_otros`
   en `open_cvn_professional_experience.puml`; `ambito_del_congreso` /
   `ambito_del_congreso_otros` e `intervencion_por` / `intervencion_por_indicar`
   en `open_cvn_research_060_part_01.puml`; `tipo_de_identificador_digital_de_autor`
   / `tipo_de_identificador_digital_de_autor_otros` en `open_cvn_identity.puml`.
   La regla de dominio implicita es que si el valor controlado seleccionado es
   "Otros", el campo de texto libre deberia ser obligatorio, algo que hoy no se
   ve porque ambos campos aparecen como `optional`. Ejemplo de invariante:

   ```
   context CargosYActividadesDesempenadosConAnterioridad
   inv OtrosRequeridoSiTipoEsOtros:
     self.tipo_de_entidad = TipoEntidad::Otros implies
       self.tipo_de_entidad_otros->notEmpty()
   ```

2. Rangos de fechas: `fecha_de_inicio` y `fecha_de_finalizacion` aparecen como
   atributos independientes sin relacion de orden expresada (por ejemplo en
   `open_cvn_professional_experience.puml` y en `AmbitoDelCongreso` /
   `AmbitoDelEvento` dentro de `open_cvn_research_060_part_01.puml`).
   Invariante propuesta:

   ```
   context CargosYActividadesDesempenadosConAnterioridad
   inv InicioAntesDeFin:
     self.fecha_de_inicio <= self.fecha_de_finalizacion
   ```

3. Colecciones paralelas con cardinalidad implicita compartida: en
   `EntidadesParticipantes` (`open_cvn_research_060_part_01.puml`) varios
   atributos `repeated` (ciudad, pais, tipo de entidad por cada entidad
   participante) deberian mantener longitudes iguales entre si, algo que UML
   no permite anclar entre dos atributos multivaluados del mismo tipo.

Hallazgo relevante sobre el estado del codigo generado: se comprobo que
`src/generated` y `src/models/cvn/generated` no contienen ningun
`@field_validator` ni `@model_validator`; los unicos validadores del proyecto
estan en `src/open_cvn/parser_contract.py` y `src/open_cvn/open_cvn_models.py`,
y no cubren estos casos. Es decir, estas reglas no estan implementadas
actualmente ni en el codigo ni en los diagramas: formalizarlas en OCL supondria
documentar conocimiento de dominio nuevo, inferido de la convencion de nombres
CVN y del XSD, y no transcribir validaciones ya existentes y probadas. Cualquier
desarrollo futuro debe tratar estas invariantes como propuestas derivadas de
convencion, no como reglas certificadas, para mantener la misma disciplina
conservadora que ya aplica el inventario conceptual.

Recomendaciones para que un desarrollo futuro lo aborde correctamente:

- No anadir las invariantes OCL a mano en los ficheros `.puml` existentes,
  porque son salida determinista regenerada desde `ConceptualModelInventory`
  (`docs/pipeline/conceptual_model_extraction.md`); escribirlas a mano se
  perderia en la siguiente regeneracion del generador
  (`cvn_codegen.conceptual_model_diagrams`).
- La via correcta es extender el IR conceptual
  (`src/cvn_codegen/conceptual_model_types.py`) con un nuevo registro, por
  ejemplo `ConceptualConstraint`, y anadir al extractor
  (`src/cvn_codegen/conceptual_model_extractor.py`) una heuristica que
  reconozca los patrones estructurales anteriores (pares campo/`campo_otros`,
  pares de fechas inicio/fin) en lugar de inventar semantica libre no
  respaldada por evidencia.
- Incorporar las invariantes solo en las vistas de referencia (no en las
  vistas readable ni en la presentation), como bloques de nota junto a cada
  entidad, siguiendo la convencion ya existente de notas locales de
  "controlled references" descrita en `docs/diagrams/README.md`.
- Evitar generar una invariante por cada ocurrencia del patron `_otros` para
  no agravar el problema de diagramas sobredimensionados ya detectado en el
  issue `#71` (`docs/diagrams/README.md` documenta PNGs como
  `open_cvn_research_060.png` a 3660x1571 px); es preferible documentar la
  regla generica una vez y referenciarla desde cada entidad afectada.
- Valorar si la ausencia de validadores detectada debe alimentar tambien un
  hotfix o issue de endurecimiento (hardening) del pipeline de generacion de
  modelos, y no unicamente la documentacion conceptual.

## Anexos previstos

Despues del capitulo 8 se reservara espacio para anexos. Los anexos deben incluir
informacion util pero demasiado extensa para el cuerpo principal. Los anexos no
cuentan como capitulos principales.

Anexos recomendados:

- Anexo A: instalacion, entorno y comandos principales.
- Anexo B: estructura completa del formato Open CVN JSON.
- Anexo C: ejemplo completo de curriculum Open CVN.
- Anexo D: tablas de trazabilidad entre campos Open CVN y codigos CVN.
- Anexo E: resumen extendido de pruebas automatizadas.
- Anexo F: ejemplos de uso de la herramienta local.
- Anexo G: limitaciones tecnicas detalladas del paquete oficial CVN.
- Anexo H: ejemplos de importacion y exportacion.
- Anexo I: desarrollo del proyecto por fases tecnicas o issues, si se decide
  incluir trazabilidad del proceso de desarrollo.

## Bibliografia

La bibliografia debe incluir exclusivamente fuentes citadas o utilizadas de forma
efectiva en la memoria. Debe recoger documentacion oficial, articulos, estandares,
herramientas y trabajos relacionados necesarios para justificar las decisiones del
TFG.

Debe evitarse incluir referencias decorativas o no utilizadas en el texto.

## Regla final de calidad

Antes de dar por completado cualquier capitulo, debe comprobarse que:

- el capitulo puede entenderse sin conocer documentos internos del repositorio
- las decisiones estan justificadas
- las figuras y tablas se explican en el texto
- los resultados son reproducibles o estan claramente delimitados
- las limitaciones se presentan con precision
- no aparecen referencias a guias, memorias externas, conversaciones ni fuentes
  informales
- no aparecen menciones a herramientas de IA salvo exigencia normativa explicita
- el capitulo conecta con los objetivos del TFG y con el enfoque de Computacion
