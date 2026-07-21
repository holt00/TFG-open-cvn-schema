# Estructura acordada para la memoria del TFG

## Proposito del documento

Este documento recoge la estructura acordada para redactar la memoria del Trabajo
Fin de Grado del proyecto Open CVN. Su funcion es servir como guia antes de
empezar la redaccion de los capitulos definitivos en LaTeX.

La propuesta parte de dos fuentes:

- la memoria de referencia ubicada en `Mapi_TFG_ESIIAB_UCLM__ESP_/`, usada como
  ejemplo de memoria de la misma carrera y escuela
- el estado real del proyecto Open CVN, documentado en el repositorio y en
  `docs/reporte_proceso_desarrollo_tfg.md`

La memoria no debe superar los ocho capitulos principales. Despues del ultimo
capitulo se reservara espacio para anexos, bibliografia y declaracion de uso de
Inteligencia Artificial.

## Observaciones sobre la memoria de referencia

La memoria de referencia de Mapi sigue una estructura academica clasica para un
TFG de ingenieria:

1. Introduccion general
2. Estado del arte
3. Datos y representacion de la informacion
4. Arquitectura propuesta
5. Implementacion
6. Resultados experimentales
7. Conclusiones

Ademas, incluye elementos formales antes y despues del cuerpo principal:

- portada
- segunda portada
- dedicatoria
- declaracion de autoria
- resumen
- agradecimientos
- indice general
- indice de figuras
- indice de tablas
- bibliografia
- declaracion de uso de Inteligencia Artificial

La estructura de Mapi no se copiara literalmente, porque el proyecto Open CVN no
es un trabajo experimental de aprendizaje profundo, sino un trabajo de ingenieria
de datos, modelado, generacion de artefactos, validacion y aplicacion software.
Sin embargo, si se seguira su logica narrativa: presentar primero el problema,
despues el contexto teorico, despues el diseno, despues la implementacion,
despues la verificacion y finalmente las conclusiones.

## Funcion de cada capitulo en la memoria de referencia

### Capitulo 1: Introduccion general

En la memoria de Mapi, este capitulo cumple varias funciones:

- contextualiza el area de estudio
- explica la motivacion y el problema que se quiere resolver
- define el objetivo general y los objetivos especificos
- relaciona el trabajo con las competencias de la especialidad
- enumera las contribuciones principales
- explica la estructura del resto de la memoria

Para Open CVN, este capitulo debe cumplir exactamente esa misma funcion, pero
centrado en el problema de la representacion, validacion, transformacion,
almacenamiento y exportacion de curriculos academicos tomando CVN como punto de
partida.

### Capitulo 2: Estado del arte

En la memoria de Mapi, el estado del arte no se limita a enumerar trabajos
previos. Tambien introduce los conceptos tecnicos necesarios para entender la
propuesta posterior. Presenta fundamentos, alternativas, limitaciones del area y
termina posicionando el trabajo propio dentro de ese contexto.

Para Open CVN, este capitulo debe cubrir CVN, FECYT, interoperabilidad curricular,
modelos de informacion de investigacion, formatos de serializacion y tecnologias
de modelado o validacion.

### Capitulo 3: Datos y representacion de la informacion

En la memoria de Mapi, este capitulo define con precision los datos de entrada,
su origen, su particion, su preprocesamiento y la representacion de salida.

Para Open CVN no hay un dataset experimental equivalente, pero si hay fuentes de
datos y artefactos oficiales. Por tanto, esta funcion se integrara en el capitulo
dedicado al analisis del ecosistema CVN y a las decisiones de diseno. Ahi deben
describirse los XSD, XML, tablas auxiliares, manuales y demas fuentes oficiales
que alimentan el sistema.

### Capitulo 4: Arquitectura propuesta

En la memoria de Mapi, este capitulo explica la arquitectura conceptual del
sistema antes de hablar de implementacion concreta. Describe componentes,
relaciones, parametros, flujo de datos y decisiones de diseno.

Para Open CVN, este papel lo asumira el capitulo de arquitectura general. Debe
explicar la arquitectura por capas desde el paquete oficial CVN hasta la
aplicacion CLI local.

### Capitulo 5: Implementacion

En la memoria de Mapi, este capitulo baja la arquitectura a codigo: entorno,
dependencias, modulos, pipeline, entrenamiento, configuracion experimental,

Para Open CVN, la implementacion se dividira en dos capitulos porque el proyecto
tiene dos bloques muy diferenciados:

- pipeline de generacion, normalizacion, semantica y modelos
- formato Open CVN, parser, validador, almacenamiento, CLI y exportacion

### Capitulo 6: Resultados experimentales

En la memoria de Mapi, este capitulo explica como se evalua el sistema, presenta
resultados, los interpreta, compara experimentos y reconoce limitaciones
metodologicas.

Para Open CVN, este capitulo se adaptara como verificacion, resultados y
validaciones, comandos reproducibles, cobertura funcional y garantias reales del
sistema.

### Capitulo 7: Conclusiones

En la memoria de Mapi, el capitulo final resume el trabajo, enumera
contribuciones, conecta con competencias, reconoce limitaciones y propone trabajo
futuro.

Para Open CVN, este capitulo debe cerrar la memoria del mismo modo, destacando el
valor del proyecto como base abierta, reproducible y trazable para trabajar con
curriculos academicos en Espana.

## Estructura acordada para Open CVN

La estructura elegida es una adaptacion de la propuesta "Investigacion +
Ingenieria", limitada a ocho capitulos. Se agrupan el analisis tecnico del
ecosistema CVN y las decisiones de diseno porque estan estrechamente relacionados:
las decisiones arquitectonicas del proyecto surgen directamente de las
limitaciones detectadas en el paquete oficial CVN.

La estructura final acordada es:

1. Introduccion
2. Investigacion inicial y estado del arte
3. Analisis del ecosistema CVN y decisiones de diseno
4. Arquitectura general de Open CVN
5. Implementacion del pipeline de generacion y normalizacion
6. Formato Open CVN, parser, validador y aplicacion local
7. Verificacion, resultados y discusion
8. Conclusiones, limitaciones y trabajo futuro

Despues del capitulo 8 se incluiran anexos, bibliografia y declaracion de uso de
Inteligencia Artificial.

## Convencion de estado de capitulos

Cada capitulo debe incluir un identificador de estado inmediatamente debajo del
titulo. Este identificador permite saber rapidamente si el capitulo esta sin
redactar, en redaccion o terminado.

Estados permitidos:

- `PENDIENTE`: el capitulo esta planificado, pero aun no se ha redactado.
- `EN_PROCESO`: el capitulo esta siendo redactado o revisado.
- `COMPLETADO`: el capitulo esta redactado y revisado para la version actual de
  la memoria.

Formato obligatorio:

```text
Estado: PENDIENTE | EN_PROCESO | COMPLETADO
```

Estado inicial de la memoria:

| Capitulo | Estado |
|---|---|
| 1. Introduccion | `PENDIENTE` |
| 2. Investigacion inicial y estado del arte | `PENDIENTE` |
| 3. Analisis del ecosistema CVN y decisiones de diseno | `PENDIENTE` |
| 4. Arquitectura general de Open CVN | `PENDIENTE` |
| 5. Implementacion del pipeline de generacion y normalizacion | `PENDIENTE` |
| 6. Formato Open CVN, parser, validador y aplicacion local | `PENDIENTE` |
| 7. Verificacion, resultados y discusion | `PENDIENTE` |
| 8. Conclusiones, limitaciones y trabajo futuro | `PENDIENTE` |

## Capitulo 1: Introduccion

Estado: `PENDIENTE`

### Objetivo del capitulo

Presentar el problema general, justificar la motivacion del TFG, delimitar el
alcance del proyecto y explicar que aporta Open CVN.

### Contenido recomendado

- Contexto del CVN como formato normalizado en Espana para representar
  curriculos academicos y de investigacion.
- Problema de partida: aunque CVN existe, su uso sigue siendo dificil de
  automatizar, validar, adaptar, almacenar y transformar mediante herramientas
  abiertas.
- Motivacion practica: reducir trabajo manual, facilitar interoperabilidad,
  permitir versiones derivadas de un curriculum y disponer de un formato abierto
  mas manejable que el XML oficial.
- Objetivo general: definir una base abierta y reproducible para representar,
  validar, transformar, almacenar y exportar curriculos tomando CVN como punto de
  partida.
- Objetivos especificos:
  - estudiar el formato CVN y sus limitaciones
  - analizar el paquete oficial XML/XSD y sus fuentes auxiliares
  - generar bindings estructurales reproducibles desde XSD
  - normalizar metadatos funcionales y tecnicos
  - definir reglas semanticas y modelos de dominio
  - construir un formato Open CVN JSON
  - generar JSON Schema y artefactos conceptuales
  - implementar parser, validador y aplicacion CLI local
  - soportar almacenamiento SQLite, versiones derivadas y exportacion
  - explorar importacion desde XML, PDF y LLM opcional
- Competencias del grado trabajadas durante el desarrollo.
- Contribuciones principales del TFG.
- Estructura del documento.

### Figuras o tablas recomendadas

- Tabla de objetivos especificos y capitulos donde se tratan.
- Esquema muy simple del flujo general del proyecto.

## Capitulo 2: Investigacion inicial y estado del arte

Estado: `PENDIENTE`

### Objetivo del capitulo

Demostrar que el proyecto parte de un analisis previo del dominio y de las
alternativas existentes, y justificar por que se adopta una solucion propia,
pragmatica y basada en JSON/Python/Pydantic en lugar de copiar CVN-XML o adoptar
una infraestructura semantica pesada.

### Contenido recomendado

- Funcion de CVN y de FECYT en el contexto academico espanol.
- Funcionamiento practico del CVN PDF con XML embebido.
- Implicaciones de trabajar con PDF, XML embebido y firma o conformidad oficial.
- Modelos conceptuales estudiados:
  - CERIF
  - VIVO
  - ROH
- Comparacion de formatos de serializacion:
  - XML
  - JSON
  - JSON Schema
  - JSON-LD
  - YAML
- Tecnologias de modelado y generacion estudiadas:
  - LinkML
  - UML/OCL
  - BESSER
  - Pydantic
- Justificacion de las decisiones:
  - no copiar directamente CVN-XML como modelo interno
  - no adoptar una ontologia pesada como nucleo del MVP
  - usar JSON como formato abierto de intercambio
  - usar JSON Schema y Pydantic para validacion
  - mantener trazabilidad hacia CVN

### Figuras o tablas recomendadas

- Tabla comparativa XML / JSON / JSON-LD / YAML.
- Tabla comparativa CERIF / VIVO / ROH / Open CVN.
- Tabla de tecnologias descartadas o usadas parcialmente y motivo.

## Capitulo 3: Analisis del ecosistema CVN y decisiones de diseno

Estado: `PENDIENTE`

### Objetivo del capitulo

Explicar que contiene realmente el paquete oficial CVN, que problemas tecnicos se
detectaron y como esas observaciones condujeron a las decisiones principales de
diseno del proyecto.

### Contenido recomendado

- Descripcion del paquete oficial `docs/CvnXML_v1.4.3_2.1_17012025/`.
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
- Papel de cada fuente dentro del proyecto.
- Problemas encontrados:
  - `CVNTreeModel.xml` no encaja completamente con su XSD
  - algunos `xs:choice` no se expresan perfectamente en bindings generados
  - algunos `minOccurs` no se fuerzan en listas generadas
  - algunos atributos generados quedan como `object`
  - no todas las tablas CVN son enums cerrados
  - referencias no resueltas como `CVN_AGENCY_C`
  - `Subtype_Spa.xml` no ofrece siempre un puente directo por familia de tabla
- Decision principal: separar estructura XML oficial, semantica curricular,
  trazabilidad, modelo conceptual, formato JSON y aplicacion.
- Principios de diseno:
  - reproducibilidad desde fuentes oficiales
  - no editar manualmente codigo generado
  - trazabilidad desde Open CVN hacia CVN
  - validacion en varios niveles
  - politica conservadora ante informacion ambigua
  - distincion entre conversion determinista, mapeo parcial y ayuda LLM

### Figuras o tablas recomendadas

- Tabla de fuentes CVN y uso dentro del proyecto.
- Tabla de limitaciones detectadas y respuesta de diseno.
- Diagrama que muestre por que `CVN.xsd` no debe convertirse directamente en el
  modelo de dominio final.

## Capitulo 4: Arquitectura general de Open CVN

Estado: `PENDIENTE`

### Objetivo del capitulo

Presentar la arquitectura conceptual completa del sistema antes de entrar en la
implementacion concreta.

### Contenido recomendado

- Vision general de la arquitectura por capas:

```text
Paquete oficial CVN
-> XSD + XML oficiales
-> bindings estructurales Pydantic
-> normalizacion de SpecificationManual.xml y CVNTreeModel.xml
-> resolucion de catalogos auxiliares
-> politica semantica
-> modelos de dominio Pydantic
-> modelo conceptual agnostico
-> JSON Schema + diagramas + formato Open CVN JSON
-> parser y validador
-> aplicacion CLI local
-> SQLite + versiones + exportacion JSON/LaTeX/PDF + importacion PDF/XML/LLM
```

- Responsabilidad de cada capa.
- Separacion entre artefactos generados y logica mantenida a mano.
- Estructura del repositorio:
  - `src/generated/`: bindings generados automaticamente
  - `src/cvn_codegen/`: logica de generacion, normalizacion y semantica
  - `src/models/cvn/`: modelos de dominio
  - `schemas/`: JSON Schema
  - `src/open_cvn/`: parser, validador e importadores
  - `src/open_cvn_app/`: aplicacion CLI local
- Contratos entre capas.
- Razonamiento arquitectonico:
  - por que se usan bindings generados solo como capa estructural
  - por que se introduce normalizacion
  - por que se introduce una politica semantica
  - por que se crea un modelo conceptual agnostico
  - por que Open CVN JSON es el contrato final de intercambio

### Figuras o tablas recomendadas

- Diagrama principal de arquitectura por capas.
- Tabla de modulos del repositorio y responsabilidades.
- Diagrama de flujo desde CVN oficial hasta PDF exportado.

## Capitulo 5: Implementacion del pipeline de generacion y normalizacion

Estado: `PENDIENTE`

### Objetivo del capitulo

Describir como se implementa la parte tecnica que transforma el paquete oficial
CVN en artefactos Python, metadatos normalizados, modelos de dominio, modelo
conceptual, diagramas y JSON Schema.

### Contenido recomendado

- Entorno de desarrollo y dependencias principales.
- Generacion estructural con `xsdata`.
- Runner de generacion:
  - `src/cvn_codegen/xsdata_runner.py`
  - comando canonico `uv run python -m cvn_codegen.xsdata_runner all`
- Paquetes generados:
  - `src/generated/cvn`
  - `src/generated/specification_manual`
  - `src/generated/tree_model`
  - `src/generated/reference_tables`
  - `src/generated/subtypes`
  - `src/generated/entity`
  - `src/generated/thesaurus`
- Normalizacion de metadatos:
  - extraccion de `SpecificationManual.xml`
  - extraccion de `CVNTreeModel.xml`
  - union por codigo CVN
  - preservacion de trazabilidad
- Resolucion auxiliar:
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
- Modelo conceptual agnostico.
- Generacion de diagramas y JSON Schema.

### Resultados tecnicos que pueden mencionarse

- `1457` codigos normalizados.
- `1429` codigos presentes tanto en manual como en tree model.
- `27` codigos solo en el manual.
- `1` codigo solo en el tree model.
- `105` archivos generados bajo `src/models/cvn/generated/`.

### Figuras o tablas recomendadas

- Tabla de etapas del pipeline, entrada, salida y modulo responsable.
- Fragmento pequeno de ejemplo de metadato normalizado.
- Diagrama de trazabilidad de un campo desde CVN hasta Open CVN.

## Capitulo 6: Formato Open CVN, parser, validador y aplicacion local

Estado: `PENDIENTE`

### Objetivo del capitulo

Explicar el resultado funcional del proyecto: el formato abierto, la validacion,
los parsers, la aplicacion local y los flujos de importacion/exportacion.

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

- Organizacion curricular por areas conceptuales en lugar de copiar literalmente
  la estructura XML CVN.
- JSON Schema:
  - ubicacion `schemas/open_cvn.schema.json`
  - uso de JSON Schema Draft 2020-12
  - extensiones de trazabilidad `x-open-cvn-*`
- Parser y validador:
  - `parse_open_cvn_json(...)`
  - `validate_open_cvn_json(...)`
  - validacion JSON Schema
  - validacion runtime con Pydantic
  - advertencias semanticas conservadoras
- Importacion:
  - Open CVN JSON
  - CVN XML con mapeo semantico parcial
  - CVN PDF mediante XML embebido
  - fallback LLM opcional para PDFs sin XML extraible o validable
- Aplicacion CLI local:
  - comando `open-cvn`
  - inicializacion de almacenamiento
  - importacion y exportacion
  - almacenamiento SQLite
  - curriculum maestro
  - versiones derivadas
  - seleccion de secciones y entradas
  - exportacion a LaTeX
  - generacion opcional de PDF
- Seguridad y privacidad:
  - LLM solo con consentimiento explicito
  - resultados LLM no autoritativos
  - validacion obligatoria del resultado importado

### Figuras o tablas recomendadas

- Esquema de la estructura Open CVN JSON.
- Diagrama de flujo de importacion PDF/XML/LLM.
- Tabla de comandos principales de la CLI.
- Ejemplo reducido de curriculum maestro y version derivada.

## Capitulo 7: Verificacion, resultados y discusion

Estado: `PENDIENTE`

### Objetivo del capitulo

Demostrar que el sistema se ha validado de forma reproducible y discutir que
garantias ofrece realmente.

Este capitulo sustituye al capitulo de resultados experimentales de la memoria de
Mapi. En Open CVN no se deben inventar metricas experimentales de rendimiento si
no existen; los resultados deben ser resultados de ingenieria: pruebas,
validaciones, artefactos generados, flujos funcionales y limitaciones verificadas.

### Contenido recomendado

- Estrategia general de verificacion.
- Suite de pruebas automatizadas.
- Comando principal:

```bash
uv run pytest -n auto tests
```

- Ultima linea base documentada:

```text
488 passed
```

- Tipos de pruebas:
  - generacion estructural
  - importabilidad de bindings
  - parseo de fuentes oficiales
  - normalizacion
  - resolucion de referencias auxiliares
  - politica semantica
  - generacion de modelos de dominio
  - generacion de JSON Schema
  - parser y validador Open CVN
  - importacion XML
  - extraccion PDF
  - almacenamiento SQLite
  - CLI
  - versiones maestras y derivadas
  - edicion y seleccion
  - exportacion LaTeX
  - generacion PDF
  - fallback LLM
  - flujos end-to-end
- GitHub Actions para PRs hacia `main` y `development`.
- Discusion de resultados:
  - que partes son reproducibles
  - que partes dependen de inconsistencias del paquete oficial
  - que garantias proporciona JSON Schema
  - que garantias proporciona Pydantic
  - que queda como diagnostico o advertencia
  - que no debe presentarse como conversion completa

### Figuras o tablas recomendadas

- Tabla de categorias de pruebas y objetivo de cada una.
- Tabla de comandos de verificacion.
- Tabla de garantias del sistema frente a limitaciones conocidas.

## Capitulo 8: Conclusiones, limitaciones y trabajo futuro

Estado: `PENDIENTE`

### Objetivo del capitulo

Cerrar la memoria sintetizando el trabajo realizado, las contribuciones, las
competencias desarrolladas, las limitaciones y las lineas futuras.

### Contenido recomendado

- Resumen del trabajo:
  - estudio del ecosistema CVN
  - diseno de arquitectura por capas
  - generacion estructural reproducible
  - normalizacion y politica semantica
  - modelos de dominio
  - modelo conceptual
  - Open CVN JSON
  - parser, validador y aplicacion local
  - almacenamiento, versiones y exportacion
- Contribuciones principales:
  - reinterpretacion practica del paquete oficial CVN
  - separacion entre XML estructural y dominio curricular
  - formato JSON abierto y validable
  - trazabilidad hacia CVN
  - herramienta local funcional
  - importacion determinista y fallback LLM controlado
- Competencias desarrolladas.
- Limitaciones:
  - inconsistencias entre `CVNTreeModel.xml` y su XSD
  - expresividad limitada de bindings generados
  - referencias auxiliares no resueltas
  - importacion XML semantica parcial
  - JSON Schema no captura toda la semantica del dominio
  - LLM best-effort y con revision humana obligatoria
  - generacion PDF dependiente de motor TeX
- Trabajo futuro:
  - completar mapeo semantico XML CVN
  - ampliar validaciones de dominio
  - mejorar cobertura de tablas auxiliares
  - probar con curriculos reales
  - construir interfaz grafica
  - explorar JSON-LD o integracion con modelos semanticos
  - integracion con fuentes institucionales

### Figuras o tablas recomendadas

- Tabla de contribuciones frente a objetivos iniciales.
- Tabla de limitaciones y trabajo futuro asociado.

## Anexos previstos

Despues del capitulo 8 se reservara espacio para anexos. Los anexos deben incluir
informacion util pero demasiado extensa para el cuerpo principal.

Anexos recomendados:

- Anexo A: instalacion, entorno y comandos principales.
- Anexo B: estructura completa del formato Open CVN JSON.
- Anexo C: ejemplo completo de curriculum Open CVN.
- Anexo D: tablas de trazabilidad entre campos Open CVN y codigos CVN.
- Anexo E: listado o resumen extendido de pruebas automatizadas.
- Anexo F: ejemplos de uso de la CLI.
- Anexo G: limitaciones tecnicas detalladas del paquete oficial CVN.
- Anexo H: ejemplos de importacion desde XML, PDF y fallback LLM.

Los anexos no cuentan como capitulos principales y permiten mantener la memoria
dentro del limite acordado de ocho capitulos.

## Elementos formales finales

Despues de los anexos deben incluirse los elementos formales correspondientes:

- bibliografia
- declaracion de uso de Inteligencia Artificial

La declaracion de uso de IA debe indicar que las herramientas de IA se han usado
como apoyo en tareas de redaccion, organizacion, revision tecnica o asistencia al
desarrollo, y que todo el contenido final ha sido revisado y validado por el
autor, que conserva la responsabilidad completa sobre el trabajo.

## Recomendacion de redaccion

La memoria debe mantener un tono academico y tecnico similar al de la memoria de
referencia, pero evitando presentar el proyecto como una simple herramienta de
software. La aportacion principal debe formularse como una arquitectura abierta,
trazable y reproducible para trabajar con curriculos academicos en Espana a
partir del ecosistema CVN.

Cada capitulo debe empezar con un parrafo introductorio que explique su funcion y
termine conectando con el capitulo siguiente. Esta tecnica se usa de forma clara
en la memoria de referencia y ayuda a que la memoria tenga continuidad narrativa.
