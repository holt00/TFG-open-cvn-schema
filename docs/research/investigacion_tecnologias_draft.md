---
title: "Investigacion de tecnologias (draft)"
date: "2026-02-04"
source_files:
  - docs/descripcion_tfg_oficial.txt
  - docs/research/draft.txt
---

# Contexto del TFG

El TFG propone definir un esquema de datos de bajo nivel para CV academicos (partiendo de CVN), con una representacion final basada en JSON, validacion en Python (Pydantic), exportacion a LaTeX y exploracion de LLMs para importar curriculos generados por la aplicacion de la FECYT. En el borrador (`docs/research/draft.txt`) aparecen tecnologias y recursos relacionados con el ecosistema de *Linked Open Data* y, en particular, con la **Red de Ontologias Hercules (ROH)** y su compatibilidad con **CVN**.

Este documento recopila y organiza una investigacion breve sobre dichas tecnologias, con enfasis en como encajan (o no) con el enfoque del TFG.

# 1. Red de Ontologias Hercules (ROH)

## 1.1 Que es ROH

La **Hercules Ontology Network / Red de Ontologias Hercules (ROH)** define entidades y relaciones para modelar informacion del dominio academico y de investigacion como un **grafo de conocimiento**.

Segun su documentacion, ROH:

- Reutiliza ontologias ampliamente usadas (p. ej. **VIVO**, **BIBO**, **SKOS**, FOAF, etc.) y las extiende con clases y propiedades propias para representar el dominio de forma mas completa.
- Se distribuye en varias serializaciones RDF: **JSON-LD**, **RDF/XML**, **N-Triples** y **Turtle**.
- Incluye documentacion y un planteamiento modular: un *core* generico y modulos verticales (por pais/dominio y vocabularios controlados) para especializaciones.

En la web oficial del proyecto Hercules (UMU) se referencia el repositorio publico principal y materiales formativos ("pildoras") sobre modelado y consulta de entidades de ROH (proyectos, personas investigadoras, organizaciones, financiacion, objetos y actividades de investigacion).

## 1.2 Arquitectura modular (core + modulos verticales)

La documentacion del repositorio `HerculesCRUE/ROH` describe:

- **Core module**: conceptos principales del dominio academico, agnostico al pais.
- **Modulos verticales**: especializaciones por pais (por ejemplo, terminos del sistema universitario espanol como figuras de profesorado) y **vocabularios controlados** (basados en SKOS) para areas de conocimiento, clasificaciones, universidades, etc.

Esto es relevante para el TFG porque sugiere un enfoque donde el esquema base (agnostico) se complementa con extensiones o perfiles (por version/pais/institucion), idea alineada con "mecanismos que contemplen la modificacion y ampliacion del formato en futuras versiones".

## 1.3 Licencia y reutilizacion

El repositorio `HerculesCRUE/ROH` publica licencia **GPL-3.0**.

Implicacion: si el TFG pretende incorporar ROH como dependencia directa (por ejemplo, copiando ontologias o codigo bajo GPL dentro del repositorio del TFG), hay que revisar el impacto de copyleft. Si solo se referencia ROH como estandar externo y se generan datos compatibles (sin incorporar codigo/archivos cubiertos por GPL), el riesgo suele ser menor, pero conviene documentar el modo de integracion.

## 1.4 ROH vs un esquema JSON propio

ROH representa el CV y el dominio academico en RDF/OWL; el TFG propone un **esquema JSON** propio (validable con Pydantic y almacenable en ficheros/NoSQL) y herramientas asociadas.

Estrategias posibles (no excluyentes):

- Mantener JSON como formato canonico del TFG, y definir **exportadores**/mapeos hacia RDF (p. ej. JSON-LD) para interoperar con ROH.
- Tomar ROH como referencia semantica (terminologia, entidades) y construir un modelo JSON que conserve trazabilidad hacia IRIs/clases ROH ("vocab mappings").

# 2. VIVO (estandar reutilizado)

**VIVO** es una plataforma y vocabulario de uso internacional orientado a describir informacion de investigacion y actividad academica, con base en tecnologias semanticas y estandares abiertos. La propia descripcion publica de VIVO destaca:

- Uso de estandares globales y tecnologias semanticas.
- Integracion y conexion de datos de multiples fuentes.
- Representacion estandarizada de informacion sobre investigacion, personal investigador, financiacion, produccion cientifica e impacto.

Relevancia para ROH: ROH declara explicitamente que reutiliza/afina entidades de VIVO (por ejemplo, `vivo:Project`, `vivo:AcademicDegree`, etc.).

Relevancia para el TFG: si se pretende que el esquema JSON tenga interoperabilidad a futuro con ecosistemas semanticos, VIVO es un punto de apoyo (terminologia y modelado).

# 3. Linked Open Data y pila del Web Semantica

El borrador menciona que ROH esta "basada en Linked Open Data". En la practica, suele implicar el siguiente conjunto de estandares:

## 3.1 RDF (Resource Description Framework)

RDF define el modelo de datos en forma de **tripletas** (sujeto, predicado, objeto) agrupadas en **grafos RDF**. Tambien define el concepto de **dataset RDF** (grafo por defecto + grafos nombrados).

Puntos clave:

- Identificadores globales: IRIs.
- Interoperabilidad: distintos formatos de serializacion pueden representar el mismo grafo.

## 3.2 Serializaciones RDF: Turtle y JSON-LD

- **Turtle** (W3C Recommendation, 2014): sintaxis textual concisa para escribir grafos RDF, muy usada para authoring y debug.
- **JSON-LD 1.1** (W3C Recommendation, 2020): forma de expresar Linked Data en JSON. Permite integrar datos semanticos en entornos ya basados en JSON, y sirve como puente entre un modelo "tipo JSON" y RDF.

Para el TFG, JSON-LD es especialmente relevante: permite que un formato JSON "evolucione" hacia Linked Data sin abandonar JSON.

## 3.3 SPARQL 1.1

**SPARQL 1.1** (W3C Recommendation, 2013) es el estandar para **consultar** y **actualizar** datos RDF (grafos). Se usa tipicamente sobre un *triplestore* o endpoint.

En el repositorio `deustohercules/CVN` se describe un enfoque de validacion basado en:

- Generar ficheros RDF (p. ej. `.ttl`).
- Ejecutar **preguntas SPARQL** predefinidas para comprobar propiedades del grafo.

## 3.4 OWL 2 y SKOS

- **OWL 2** (W3C Recommendation; overview 2012) es un lenguaje de ontologias para describir clases, propiedades e individuos, con semantica formal para razonamiento.
- **SKOS** (W3C Recommendation, 2009) es un modelo para **vocabularios controlados** (tesauros, taxonomias, esquemas de clasificacion). Es mas ligero que OWL para representar conceptos y relaciones (broader/narrower/related), etiquetas y notas.

ROH usa SKOS para modulos verticales de vocabularios (areas de conocimiento, clasificaciones, etc.), lo que encaja con necesidades de CV: listas controladas y taxonomias.

# 4. CVN, XML y conversion a tripletas ROH

## 4.1 Repositorio de conversion CVN -> ROH

El borrador referencia `https://github.com/deustohercules/CVN`, que documenta un **servicio conversor** de **XML CVN a tripletas ROH**.

Lo mas relevante (segun su README):

- Servicio HTTP que ofrece un endpoint `POST /v1/convert`.
- Parametros: `orcid` (obligatorio) y `format` (por defecto `xml`, con salidas como `turtle`, `nt`, `n3`, etc.).
- El cuerpo de la peticion es el fichero XML CVN (binario, UTF-8).
- El resultado puede guardarse como `.ttl` u otros formatos RDF.

Esto confirma que existe una via automatizada *XML CVN -> RDF/ROH* ya implementada y utilizable como referencia tecnica.

## 4.2 "El PDF lleva embebido un esquema XML"

El borrador indica que el PDF generado por CVN incluye embebido un XML que representa el curriculum y se usa para importacion y para la traduccion a ROH.

Interpretacion tecnica plausible:

- En PDF es posible incluir **ficheros adjuntos embebidos** ("file attachments") o metadata estructurada (p. ej. XMP). Muchas herramientas de formularios/exportacion incluyen XML como adjunto para facilitar importacion.

Como verificarlo (procedimiento orientativo):

- Extraer adjuntos embebidos del PDF (por ejemplo, con herramientas tipo `pdfdetach`/`poppler` o utilidades de inspeccion).
- Inspeccionar si aparece un `.xml` y si corresponde a la estructura CVN.

Implicacion para el TFG:

- Si el PDF efectivamente contiene el XML, una herramienta de importacion puede evitar OCR/LLM para la extraccion "visual" y centrarse en:
  - extraer el XML,
  - parsearlo/validarlo,
  - mapearlo al esquema JSON del TFG.
- El uso de LLM podria reservarse para:
  - normalizacion de campos ambiguos,
  - deduplicacion y enriquecimiento,
  - resolucion de inconsistencias,
  - casos donde falte el XML.

# 5. Implicaciones y oportunidades para el TFG

## 5.1 Interoperabilidad: JSON Schema/Pydantic vs RDF/ROH

El TFG se centra en un esquema JSON (con validacion Pydantic). ROH apunta a un stack semantico (RDF/OWL/SPARQL). Esto abre dos lineas complementarias:

- Diseñar el modelo JSON con posibilidad de exportacion futura a **JSON-LD**.
- Documentar un mapeo (parcial o total) entre el esquema del TFG y ROH/VIVO (por ejemplo, identificadores ORCID, publicaciones, proyectos, afiliaciones).

## 5.2 Reutilizar el trabajo existente de conversion CVN -> RDF

El conversor de `deustohercules/CVN` aporta:

- Un ejemplo practico de ingestión de XML CVN.
- Un ejemplo de como validar/chequear datos mediante consultas SPARQL.

Aunque el TFG no vaya a adoptar RDF como formato principal, este repositorio puede ayudar a:

- Identificar ambiguedades reales del CVN.
- Comparar cobertura (que partes del CVN quedan representadas).
- Derivar requisitos para el esquema JSON y su versionado.

## 5.3 Estrategia de importacion

Si la fuente real es:

- XML (directo o embebido en PDF), el parser de Python puede trabajar "estructurado".
- PDF sin XML, entonces el TFG puede justificar el uso de LLMs/OCR.

Por tanto, una decision tecnica temprana es priorizar una via de importacion *estructurada* cuando exista, y dejar el LLM para los casos en los que no.

# Referencias (URLs)

- TFG: `docs/descripcion_tfg_oficial.txt`
- Borrador de investigacion: `docs/research/draft.txt`

- ROH (documentacion): https://deustohercules.github.io/roh/roh/index.html
- ROH (repositorio principal): https://github.com/HerculesCRUE/ROH
- Hercules UMU (pagina "Ontologias"): https://www.um.es/web/hercules/ontologias

- Servicio CVN XML -> tripletas ROH: https://github.com/deustohercules/CVN
- Repo ROH fork referenciado en draft: https://github.com/deustohercules/ROH-1

- VIVO (home): https://vivoweb.org/

- W3C RDF 1.1 Concepts: https://www.w3.org/TR/rdf11-concepts/
- W3C SPARQL 1.1 Overview: https://www.w3.org/TR/sparql11-overview/
- W3C JSON-LD 1.1: https://www.w3.org/TR/json-ld11/
- W3C Turtle: https://www.w3.org/TR/turtle/
- W3C OWL 2 Overview: https://www.w3.org/TR/owl2-overview/
- W3C SKOS Reference: https://www.w3.org/TR/skos-reference/
