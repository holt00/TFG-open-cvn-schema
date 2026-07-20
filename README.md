# Open CVN

## Descripcion

Este repositorio contiene un Trabajo de Fin de Grado orientado a definir un
esquema de datos abierto para la representacion de curriculos en el ambito
universitario y de investigacion en Espana, tomando como punto de partida el
formato CVN.

El problema de partida es que, aunque el CVN existe como formato normalizado,
la elaboracion, mantenimiento y adaptacion de curriculos a distintos contextos
sigue consumiendo mucho tiempo y dificulta el desarrollo de herramientas
abiertas interoperables. Una de las causas es la ausencia de una definicion de
bajo nivel suficientemente clara para representar y procesar estos datos.

## Objetivo Del Proyecto

El objetivo general del TFG es definir un esquema de datos que permita la
gestion automatizada de curriculos academicos y de investigacion en Espana.

Ese objetivo se descompone en varias lineas de trabajo:

1. estudiar el formato CVN actual y analizar sus limitaciones
2. proponer un formato de bajo nivel agnostico respecto al formato final de
   representacion
3. definir un esquema final basado en JSON, apto para ficheros de texto y bases
   de datos NoSQL
4. desarrollar una aplicacion en Python para lectura y validacion de curriculos
   utilizando Pydantic
5. desarrollar herramientas de almacenamiento local y exportacion a LaTeX
6. explorar el uso de LLM para importar curriculos generados por herramientas
   externas como la aplicacion de la FECYT

## Alcance Actual Del Repositorio

La infraestructura que actualmente se esta construyendo para generar modelos
Pydantic es solo una parte del proyecto total. En esta fase, el foco del
repositorio esta en sentar la base tecnica del pipeline que permitira:

1. traducir los artefactos oficiales CVN XML/XSD a bindings estructurales
   Pydantic
2. normalizar la metadata funcional y tecnica del paquete oficial
3. generar mas adelante modelos de dominio reutilizables y un esquema final mas
   limpio

Esta base es necesaria para el parser/validador en Python, pero no agota el TFG:
todavia quedan por delante la definicion del modelo final, la capa JSON, la
exportacion a LaTeX, y la futura exploracion de una herramienta de importacion
basada en LLM.

## Direccion Tecnica Actual

El repositorio sigue una arquitectura de dos capas:

1. bindings estructurales generados a partir del paquete oficial CVN
2. modelos semanticos y de dominio que se generaran sobre metadata normalizada

La arquitectura, el estado actual y el roadmap se documentan en el propio
repositorio para que futuras sesiones no dependan de reconstruir el contexto a
partir del chat o de issues externos.

## Punto De Entrada

Para obtener el contexto del proyecto y el estado real de implementacion, leer:

1. `PROJECT_GUIDE.md`
2. `docs/context/project_context_index.md`
3. `docs/context/current_status.md`

## Documentos Clave

- guia principal del proyecto:
  `PROJECT_GUIDE.md`
- indice de contexto del proyecto:
  `docs/context/project_context_index.md`
- estado actual del proyecto:
  `docs/context/current_status.md`
- reporte del proceso de desarrollo del TFG:
  `docs/reporte_proceso_desarrollo_tfg.md`
- arquitectura del pipeline:
  `docs/pipeline/cvn_pydantic_generation_pipeline.md`
- roadmap completo:
  `docs/roadmap/cvn_generation_roadmap.md`
- guia de contribucion y setup:
  `CONTRIBUTING.md`

