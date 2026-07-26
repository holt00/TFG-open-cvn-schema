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
| 5. Implementacion del pipeline de generacion y normalizacion | `EN_PROCESO` |
| 6. Formato Open CVN, validacion y herramienta de gestion | `EN_PROCESO` |
| 7. Evaluacion, resultados y discusion | `EN_PROCESO` |
| 8. Conclusiones, competencias y trabajo futuro | `EN_PROCESO` |

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
`overfull hbox`.

En una revision de claridad de todo el documento (identica a la aplicada en
5.4, 6.5 y 7.1/7.4), la seccion 3.5 (alcance y exclusiones) se reescribio: los
tres parrafos, cada uno una enumeracion corrida de 2 a 5 elementos, se
convirtieron en tres listas independientes (automatizado con garantias /
mapeo parcial / limitaciones documentadas), cada una con su frase de apertura
y las frases de cierre originales intactas. El capitulo permanece en
`EN_PROCESO` hasta su revision de contenido.

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

Estado: `EN_PROCESO`

Estado de redaccion actual: el primer borrador completo del capitulo existe en
`docs/memoria/chapters/ch5.tex` y esta incluido en `docs/memoria/TFG.tex`. El
capitulo desarrolla, etapa a etapa, el pipeline ya presentado a nivel
arquitectonico en el capitulo 4: generacion estructural (con el runner y el
override de `tree_model` ya documentado como limitacion en el capitulo 3),
normalizacion por codigo CVN, resolucion de referencias auxiliares, politica
semantica (nueve formas semanticas base), generacion de modelos de dominio y
del modelo conceptual, y generacion de JSON Schema con el mecanismo de
trazabilidad `x-open-cvn-*`.

Todas las cifras presentadas se verificaron directamente contra el paquete
oficial vigente en el repositorio antes de redactarlas (no se reutilizaron sin
comprobar los valores ya citados en `docs/context/current_status.md`):
`1457` entradas normalizadas totales, `27` codigos solo en el manual, `1` solo
en el arbol, `1429` en ambas fuentes, `33` discrepancias registradas; de las
1457 entradas, `557` declaran una tabla de referencia en el manual (desglosadas
en 9 categorias de evidencia de resolucion que suman 557, con exactamente `1`
referencia no resuelta, el caso ya documentado de `CVN_AGENCY_C` en el codigo
`060.010.000.030`) y `900` no declaran tabla; la generacion de dominio produce
`105` archivos; el JSON Schema generado contiene `182` definiciones, de las
cuales `74` son vocabularios controlados.

El capitulo incluye los tres elementos recomendados: una tabla de resultados
de resolucion auxiliar, un fragmento de codigo reducido (entorno `code` del
documento) con el metadato normalizado simplificado del campo de sexo
(codigo `000.010.000.030`, tabla `CVN_SEX_A`), una figura de trazabilidad
completa de ese mismo campo desde `SpecificationManual.xml`/`CVNTreeModel.xml`
hasta su definicion final en el JSON Schema Open CVN (PlantUML propio en
`docs/memoria/figs/open_cvn_field_traceability.puml`), y una tabla de sintesis
de las ocho etapas del pipeline con entrada, salida y modulo responsable.

La compilacion completa de la memoria con `xelatex`, `bibtex`, `xelatex` y
`xelatex` genera `docs/memoria/TFG.pdf` con 69 paginas, sin errores
bloqueantes, sin referencias indefinidas, sin citas indefinidas y sin
`overfull hbox` relevante (solo un desbordamiento de 2pt en una linea de
titulo, imperceptible).

Tras una revision de claridad, la seccion 5.4 (politica semantica) se
reescribio: ahora abre explicando por que hace falta una etapa de decision
semantica (los XSD no distinguen texto libre de valores controlados), se
divide en tres subsecciones (5.4.1 formas semanticas reconocidas, con una
tabla de las 9 formas y un ejemplo real verificado para cada una; 5.4.2
enumeracion cerrada frente a catalogo abierto, con el contraste verificado
entre `CVN_SEX_A` -2 valores, elegible- y `CVN_ENTITY_TYPE` -17 valores pero
con delegado y etiqueta duplicada, ineligible-, mostrando que el tamano de la
tabla no es el criterio; 5.4.3 presencia, nomenclatura y traza). El ejemplo de
`CVN_ENTITY_TYPE` se verifico en vivo contra el paquete oficial (codigo
`010.010.000.040`, evidencia con `has_delegate=True`) antes de redactarlo. La
compilacion tras este cambio genera `docs/memoria/TFG.pdf` con 71 paginas,
sin errores, referencias o citas indefinidas (los mismos dos desbordamientos
menores de menos de 2pt persisten, imperceptibles).

La seccion 5.5 (generacion de modelos de dominio y del modelo conceptual)
tambien se reescribio para aclarar, sin alargarla en exceso, que la etapa
produce dos artefactos con proposito distinto y no uno: los modelos de
dominio Pydantic (implementacion en Python, con el desglose verificado de los
105 archivos: 101 modulos por concepto curricular, un modulo de campos solo
del manual, un modulo de nodos del arbol sin item, y un modulo de 13
enumeraciones) y, por separado, el modelo conceptual agnostico que reutiliza
esa misma informacion sin volver a leer XML/XSD. El cierre de la seccion
retoma el ejemplo del campo de sexo (entidad conceptual `Person`, area
`identity`) para enlazarlo con su aparicion final en la seccion de JSON
Schema. El capitulo permanece en `EN_PROCESO` hasta su revision de contenido.

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

Estado: `EN_PROCESO`

Estado de redaccion actual: el primer borrador completo del capitulo existe en
`docs/memoria/chapters/ch6.tex` y esta incluido en `docs/memoria/TFG.tex`. El
capitulo cubre la estructura raiz de Open CVN JSON, la forma comun de las
referencias controladas (reutilizando el ejemplo de sexo/`CVN_SEX_A` ya usado
en el capitulo 5), el contrato de parser/validador (cinco estados de
validacion, avisos semanticos conservadores), la importacion desde JSON/XML/PDF
(incluyendo el fallback LLM opcional, presentado como parte constitutiva del
sistema y no como asistencia de redaccion, igual que en el capitulo 1), y la
herramienta local (modelo maestro/version derivada, comandos principales).
Cierra con una seccion explicita de alcance y garantias que distingue lo
determinista de lo parcial, preparando la evaluacion del capitulo 7.

Incluye los cuatro elementos recomendados: un fragmento de codigo con la
estructura raiz minima; un diagrama de flujo de importacion/validacion nuevo,
propio de la memoria, en `docs/memoria/figs/open_cvn_import_validation_flow.puml`;
una tabla de comandos principales de la herramienta; y dos fragmentos de
codigo con un curriculum maestro reducido (identidad + una entrada de
investigacion) y su version derivada tras excluir esa entrada, con la
extension `x-open-cvn.versioning` verificada contra la forma real emitida por
`storage.py`. Los ejemplos JSON reutilizan los ficheros reales de
`examples/open_cvn/` (`identity.json`, `research_entry.json`) en lugar de
inventar datos nuevos.

Al escribir este capitulo se completaron tambien tres referencias cruzadas
pendientes: las menciones literales "Capitulo 6" en los capitulos 3 y 5 se
convirtieron a `\ref{cap:formato_herramienta}` ahora que la etiqueta existe,
siguiendo la convencion ya establecida de usar texto literal solo mientras el
capitulo de destino no existe.

La compilacion completa de la memoria con `xelatex`, `bibtex`, `xelatex` y
`xelatex` genera `docs/memoria/TFG.pdf` con 79 paginas, sin errores
bloqueantes, sin referencias indefinidas, sin citas indefinidas y sin
`overfull hbox` relevante (mismos desbordamientos triviales <2pt en lineas de
titulo).

Se detecto que el Codigo 6.1 (estructura raiz minima) se desplazaba al inicio
de la pagina siguiente mientras el parrafo que lo introducia continuaba
fluyendo en la pagina actual, partiendo visualmente una misma frase ("...las
rutas XML de los" / "que procede.") con el flotante intercalado entre ambas
mitades. Se corrigio anadiendo `\usepackage{float}` en
`docs/memoria/include/configuracion.tex` (tras `newfloat`) y cambiando el
especificador de ese `code` concreto de `[htbp]` a `[H]`, que fuerza la
posicion exacta y evita que un flotante corto adelante al parrafo que lo
sigue en el texto.

El mismo patron reaparecio, mas severo, al final de la seccion 6.4: la Tabla
6.1 (comandos) y los Codigos 6.2 y 6.3 (curriculum maestro/version derivada)
se desplazaban por delante de la frase final de la seccion, partiendola en
dos mitades separadas por los tres flotantes. El especificador `[H]` (via
`\usepackage{float}`) resolvio el corte de frase en los cuatro flotantes,
pero a costa de huecos en blanco muy visibles cuando un flotante no cabia
entero en el resto de la pagina.

La solucion final combina dos cambios y revierte `[H]` a `[htbp]` en los
cuatro flotantes:

- reordenacion del texto para que ningun parrafo sensible quede *despues* de
  un flotante dentro de la misma seccion: en la seccion 6.1, el Codigo 6.1
  se movio al final (tras explicar raiz, areas curriculares y referencias
  controladas); en la seccion 6.4, el parrafo de cierre sobre trazabilidad de
  versiones derivadas se fusiono con el parrafo que introduce los Codigos 6.2
  y 6.3, y la Tabla 6.1 se desplazo tambien al final de la seccion, justo
  antes de los codigos
- compactacion de los flotantes de la seccion 6.4: la Tabla 6.1 paso a
  `\arraystretch{1.1}` con columnas reequilibradas (menos filas partidas en
  dos lineas) y los Codigos 6.2/6.3 pasaron de `\small` a `\footnotesize`,
  con lo que ahora caben juntos en una sola pagina sin hueco relevante

Con ningun parrafo colgando tras un flotante, `[htbp]` ya no puede partir
ninguna frase, y al no forzarse `[H]` tampoco aparecen huecos en blanco
grandes: como mucho queda el margen inferior normal de una pagina cuando el
siguiente flotante no cabe entero, algo habitual y no distinguible de
cualquier otro salto de pagina del documento. La compilacion final genera
`docs/memoria/TFG.pdf` con 79 paginas, sin errores, referencias o citas
indefinidas (mismos desbordamientos triviales <2pt de antes).

La seccion 6.5 (alcance funcional y garantias) tambien se reescribio para
mayor claridad: el parrafo unico original mezclaba los cuatro flujos
(validacion Open CVN JSON, importacion XML, importacion asistida por LLM,
generacion de PDF) en una sola frase larga por cada uno. Ahora abre con una
frase que anticipa que los cuatro flujos se situan en puntos distintos entre
garantia determinista y aproximacion parcial, y desarrolla cada flujo como
un item en negrita independiente, explicando en cada caso el porque de su
nivel de garantia (determinismo verificable, mapeo creciente sobre casos
cubiertos, dependencia de un proveedor externo con validacion previa
obligatoria, dependencia de un motor LaTeX sin bloquear el resto de flujos).

En la misma revision de claridad documento-completo que afecto a 3.5, el
parrafo de apertura de 6.1 (los cuatro campos raiz de Open CVN JSON:
`schema_version`, `metadata`, `curriculum`, `extensions`, enumerados dentro
de una sola frase con punto y coma) se convirtio en una lista de 4 items, uno
por campo. El capitulo permanece en `EN_PROCESO` hasta su revision de
contenido.

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

Estado: `EN_PROCESO`

Estado de redaccion actual: el primer borrador completo del capitulo existe en
`docs/memoria/chapters/ch7.tex` y esta incluido en `docs/memoria/TFG.tex`. El
capitulo organiza la evaluacion en ocho niveles alineados con las capas de la
arquitectura del capitulo 4 (artefactos generados, normalizacion y
trazabilidad, politica semantica, JSON Schema y validacion runtime, parsers e
importadores, almacenamiento y versiones, exportacion, flujos de extremo a
extremo), presenta el comando unico de verificacion, y cierra con una
discusion que distingue explicitamente las limitaciones que proceden del
paquete oficial CVN de las que proceden de una decision deliberada de alcance
del TFG, evitando presentar el sistema como una conversion completa o una
validacion semantica total.

Todas las cifras se verificaron ejecutando la bateria completa antes de
redactarlas, no reutilizando numeros de sesiones anteriores: se lanzo
`uv run pytest -n auto tests` en segundo plano y se registro con precision su
categorizacion (mediante `--collect-only -q` por subconjuntos de ficheros de
test, sumando exactamente 488, igual al total real) y su resultado final:
`488 passed in 692.80s (0:11:32)`. La categorizacion en 8 niveles se
distribuye como: artefactos generados 146 (estructural 38 + modelos de
dominio/conceptual/diagramas 108), normalizacion y trazabilidad 90, politica
semantica 76, JSON Schema y validacion runtime 25, parsers e importadores 63,
almacenamiento y versiones 25, exportacion 19, extremo a extremo 44.

El capitulo incluye los cuatro elementos recomendados: tabla de categorias de
pruebas con objetivo y numero de pruebas por nivel; codigo con el comando
principal de verificacion; tabla de garantias del sistema frente a
limitaciones conocidas (distinguiendo origen paquete CVN vs. origen alcance
TFG); y un resumen de resultados verificables integrado en el cierre del
capitulo. Ningun flotante quedo con parrafo sensible detras (misma leccion
aplicada en el capitulo 6), por lo que no fue necesario forzar `[H]` en
ningun caso.

La compilacion completa de la memoria con `xelatex`, `bibtex`, `xelatex` y
`xelatex` genera `docs/memoria/TFG.pdf` con 85 paginas, sin errores
bloqueantes, sin referencias indefinidas, sin citas indefinidas y sin
`overfull hbox` relevante (mismos desbordamientos triviales <4pt en lineas de
titulo/codigo).

La seccion 7.1 tambien se reviso para mayor claridad: la frase que enumeraba
los ocho niveles de evaluacion dentro de un unico parrafo corrido se
convirtio en una lista con un item en negrita por nivel (etiqueta +
responsabilidad concreta que verifica), siguiendo el mismo patron ya aplicado
en 5.4 y 6.5.

La seccion 7.4 (discusion de garantias y limitaciones) tenia el mismo
problema en sus dos parrafos centrales: las tres limitaciones de origen
paquete CVN y las cuatro de origen alcance TFG estaban enumeradas dentro de
frases largas y corridas. Se convirtieron en dos listas independientes (una
por origen de la limitacion), cada item con etiqueta en negrita y una frase
breve de explicacion, manteniendo las frases de apertura y cierre de cada
parrafo para no perder la transicion argumental hacia la Tabla 7.2. Se
comprobo que ningun flotante quedo con parrafo sensible detras tras el
cambio (misma cautela que en el capitulo 6). La compilacion final genera
`docs/memoria/TFG.pdf` con 87 paginas, sin errores, referencias o citas
indefinidas (mismos desbordamientos triviales <4pt de antes). El capitulo
permanece en `EN_PROCESO` hasta su revision de contenido.

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

Estado: `EN_PROCESO`

Estado de redaccion actual: el primer borrador completo del capitulo existe en
`docs/memoria/chapters/ch8.tex` y esta incluido en `docs/memoria/TFG.tex`,
como ultimo capitulo del cuerpo principal antes de anexos y bibliografia. El
capitulo retoma con `\ref{}` (no texto literal) todos los capitulos
anteriores, ya que al ser el capitulo final no quedan referencias hacia
adelante pendientes. Cubre, en orden: cumplimiento del objetivo general y de
los diez objetivos especificos del capitulo 1 (Tabla 8.1, con `OE9`
marcado como "cumplido con garantias parciales" y el resto "cumplido",
coherente con la discusion de garantias del capitulo 7); las siete
contribuciones anunciadas en el capitulo 1, ahora presentadas como
demostradas con referencia al capitulo donde cada una se evidencia; las
cuatro competencias `CM1/CM2/CM5/CM6` con evidencia concreta (Tabla 8.2),
cerrando la promesa explicita que el propio capitulo 1 dejo pendiente;
y limitaciones con su trabajo futuro asociado (Tabla 8.3), incluyendo una
explicacion algo mas extensa y autocontenida (sin rutas de repositorio ni
numeros de issue) sobre la posible incorporacion futura de restricciones OCL,
con dos patrones ilustrativos genericos (valor controlado + campo "otros"
condicionalmente obligatorio; orden entre fecha de inicio y fecha de fin) en
lugar de citar los ficheros `.puml` o modulos internos reales que motivaron
esta nota en el documento de planificacion. Cierra con un parrafo final que
sintetiza la conclusion del TFG completo.

Durante la redaccion se detecto y corrigio, antes de dar el capitulo por
terminado, el mismo patron de flotante-adelantandose-a-parrafo ya visto en
los capitulos 6 y 7: la Tabla 8.1 se desplazaba por delante del parrafo sobre
`OE9` que la seguia en el texto, partiendo una frase. Se corrigio moviendo
ese parrafo antes de la tabla (en vez de forzar `[H]`), dejando la tabla
como ultimo elemento de la seccion 8.1, igual que ya son las Tablas 8.2 y
8.3 dentro de sus respectivas secciones.

La compilacion completa de la memoria con `xelatex`, `bibtex`, `xelatex` y
`xelatex` genera `docs/memoria/TFG.pdf` con 93 paginas, sin errores
bloqueantes, sin referencias indefinidas, sin citas indefinidas y sin
`overfull hbox` nuevos (mismos desbordamientos triviales <4pt ya presentes en
capitulos anteriores).

Se detecto que el capitulo carecia de una seccion final de conclusiones
propiamente dicha: el cierre quedaba reducido a un unico parrafo al final de
la seccion 8.4 (limitaciones y trabajo futuro), sin seccion propia. Se anadio
la seccion 8.5 "Conclusiones", que sintetiza el trabajo completo retomando,
con `\ref{}` a cada capitulo correspondiente, el problema de partida, la
arquitectura construida capa a capa, el cumplimiento del objetivo general
apoyado en la evidencia reproducible del capitulo 7, el balance entre
limitaciones documentadas y conclusion general, y un cierre final que
posiciona la arquitectura por capas (no el formato JSON ni la herramienta
local) como la aportacion principal del TFG. El parrafo de cierre que antes
vivia al final de 8.4 se traslado y amplio dentro de esta nueva seccion. La
compilacion tras este cambio sigue generando `docs/memoria/TFG.pdf` con 93
paginas, sin errores, referencias o citas indefinidas.

A peticion del usuario, se comparo el capitulo de conclusiones de una
memoria TFG de referencia local (usada como base de la skill de estilo
`tfg-mapi-style`, nunca citada ni copiada literalmente en el texto final)
para identificar diferencias de contenido y de formato. Cambios aplicados
como resultado:

- se anadio una nueva seccion inicial 8.1 "Resumen del trabajo", ausente
  hasta ahora, con tres etiquetas en negrita en linea ("Problema y
  motivacion.", "Arquitectura desarrollada.", "Resultados.") en lugar de
  subsecciones, siguiendo el mismo patron de la memoria de referencia para
  sintetizar el trabajo antes de entrar en el detalle objetivo por objetivo
- la seccion de contribuciones (ahora 8.3) se reescribio de una lista
  `itemize` con una frase por item a parrafos narrativos con transiciones
  ordinales ("La primera es...", "La segunda es...", ... "La septima y
  ultima es..."), igual que la memoria de referencia trata sus
  contribuciones, conservando el mismo contenido y las mismas referencias a
  capitulos
- las secciones de limitaciones y trabajo futuro no se modificaron porque ya
  coincidian en formato (listas `itemize` con etiqueta en negrita) con la
  memoria de referencia
- la tabla de competencias (ahora Tabla 8.2) se mantuvo, porque la propia
  guia de la memoria (`estructura_memoria_tfg.md`) exige explicitamente una
  "Tabla de competencias y evidencias" como elemento recomendado, aunque la
  memoria de referencia use parrafos narrativos en su lugar
- se recorto el primer parrafo de la seccion 8.6 "Conclusiones" para
  eliminar la redundancia con la nueva seccion 8.1, dejando que la seccion
  de cierre se centre en la valoracion final en lugar de repetir el resumen

Las secciones del capitulo quedan renumeradas: 8.1 Resumen del trabajo, 8.2
Cumplimiento de los objetivos, 8.3 Contribuciones principales, 8.4
Competencias desarrolladas, 8.5 Limitaciones y trabajo futuro, 8.6
Conclusiones. La compilacion final genera `docs/memoria/TFG.pdf` con 93
paginas, sin errores, referencias o citas indefinidas (mismos
desbordamientos triviales <4pt de antes).

Se detecto que la seccion 8.5 (limitaciones y trabajo futuro) se apoyaba
casi por completo en una tabla de celdas de una frase, sin la explicacion
previa en prosa que si tienen las tablas equivalentes de los capitulos 3 y
7 (unicamente la restriccion OCL tenia parrafo propio). Se desarrollo un
parrafo explicativo para cada una de las seis limitaciones (que es, por que
existe -paquete oficial vs. alcance del TFG- y que trabajo futuro se deriva,
con referencia cruzada al capitulo donde se documento originalmente), y la
tabla se desplazo al final de la seccion como resumen de referencia rapida
en vez de ser el vehiculo principal de la explicacion. Esto tambien resolvio
por diseño cualquier riesgo de que la tabla se adelantara a un parrafo
sensible, porque ya no queda texto explicativo despues de ella dentro de la
seccion.

La compilacion tras este cambio genera `docs/memoria/TFG.pdf` con 95
paginas, sin errores, referencias o citas indefinidas (mismos
desbordamientos triviales <4pt de antes).

El capitulo permanece en `EN_PROCESO` hasta su revision de contenido. Con
este capitulo queda completo el cuerpo principal de los ocho capitulos
acordados; quedan pendientes los anexos y la revision final de contenido de
todos los capitulos.

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

Despues del capitulo 8 se reserva espacio para anexos. Los anexos deben incluir
informacion util pero demasiado extensa para el cuerpo principal. Los anexos no
cuentan como capitulos principales.

Estado actual: cuatro anexos redactados, con titulo y numeracion manual
("Anexo A: ...", no la numeracion automatica `\appendix`/"Apendice" de
LaTeX), situados al final del documento tras la bibliografia y la
declaracion de uso de IA, precedidos por una pagina de anuncio
`\chapter*{Anexos}` con entrada propia en el indice:

- Anexo A (`docs/memoria/chapters/anexo_a.tex`): instalacion, entorno y
  comandos principales. Corresponde al "Anexo A" de la lista original.
- Anexo B (`docs/memoria/chapters/anexo_b.tex`): estructura completa del
  formato Open CVN JSON. Corresponde al "Anexo B" de la lista original.
- Anexo C (`docs/memoria/chapters/anexo_i.tex`): desarrollo del proyecto
  por fases tecnicas, con trazabilidad explicita a issues y hotfixes.
  Corresponde al "Anexo I" de la lista original; es la unica excepcion
  documentada a la regla de autocontencion, porque su proposito especifico es
  registrar la trazabilidad del proceso de desarrollo.
- Anexo D (`docs/memoria/chapters/anexo_d.tex`): enlace al repositorio
  (`https://github.com/holt00/TFG-open-cvn-schema`) y guia de orientacion
  sobre su estructura y punto de entrada. No incluye imagenes.

No se incluye el "Anexo C: ejemplo completo de curriculum Open CVN" de la
lista original porque no se dispone de un curriculum real para ese fin.

Anexos restantes de la lista original, no redactados por ahora (pendientes,
no descartados):

- Anexo: tablas de trazabilidad entre campos Open CVN y codigos CVN.
- Anexo: resumen extendido de pruebas automatizadas.
- Anexo: ejemplos de uso de la herramienta local.
- Anexo: limitaciones tecnicas detalladas del paquete oficial CVN.
- Anexo: ejemplos de importacion y exportacion.

Se evaluo tambien anadir un anexo con los diagramas UML principales del
modelo conceptual Open CVN; se descarto por ahora porque varios diagramas
generados son demasiado grandes para una pagina legible (vease
`docs/diagrams/README.md`) y porque ya existe una vista UML compacta en la
Figura del Capitulo 3.

## Declaracion de uso de Inteligencia Artificial

Anadida en `TFG.tex`, despues de la bibliografia y antes de `\end{document}`,
como `\chapter*{}` con entrada en el indice, siguiendo la ubicacion adoptada
por la tesis de referencia usada para estilo. Declara el uso de modelos de
OpenAI y de Anthropic como apoyo en busqueda de documentacion tecnica,
redaccion academica y revision de coherencia entre capitulos, y establece que
todo resultado generado por IA generativa ha sido revisado por el autor y que
el resto de aspectos del trabajo son responsabilidad exclusiva suya.

## Erratas corregidas en el titulo oficial

El macro `\titulo` en `docs/memoria/include/opciones.tex` contenia dos
erratas ("curriculumn vitae" y "el ambito academico") que se propagaban a
portada, segunda portada y declaracion de autoria. Corregidas en el macro y,
por separado, en el texto literal de la declaracion de autoria en
`docs/memoria/elements/preambulo.tex`, que no usa el macro.

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
