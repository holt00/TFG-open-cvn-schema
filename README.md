# Open CVN

## Descripcion

Este repositorio contiene dos trabajos academicos sucesivos sobre el mismo
proyecto: un Trabajo de Fin de Grado (TFG), ya terminado, defendido y
entregado, y un Trabajo de Fin de Master (TFM) que se esta construyendo ahora
sobre esa base. Ambos giran en torno a definir un esquema de datos abierto
para la representacion de curriculos en el ambito universitario y de
investigacion en Espana, tomando como punto de partida el formato CVN.

El problema de partida es que, aunque el CVN existe como formato normalizado,
la elaboracion, mantenimiento y adaptacion de curriculos a distintos contextos
sigue consumiendo mucho tiempo y dificulta el desarrollo de herramientas
abiertas interoperables. Una de las causas es la ausencia de una definicion de
bajo nivel suficientemente clara para representar y procesar estos datos.

## El TFG (Terminado)

El TFG definio un esquema de datos que permite la gestion automatizada de
curriculos academicos y de investigacion en Espana, construyendo, en este
mismo repositorio, un pipeline completo por capas:

1. bindings Pydantic estructurales generados directamente desde el paquete
   oficial CVN XML/XSD (`src/generated/`)
2. una capa de normalizacion que indexa cada campo por su codigo CVN y lo
   resuelve contra los catalogos de referencia auxiliares
   (`src/cvn_codegen/normalization.py`)
3. una capa de politica semantica que traduce esa evidencia normalizada en
   decisiones deterministas de tipado y nomenclatura
   (`src/cvn_codegen/semantic_policy.py`)
4. un generador de modelos de dominio final, consumibles a mano
   (`src/cvn_codegen/domain_model_generator.py`, salida en
   `src/models/cvn/generated/`)
5. una capa de modelo conceptual agnostica usada para generar diagramas
   UML-like y un JSON Schema (`src/cvn_codegen/conceptual_model_extractor.py`,
   `docs/diagrams/`, `schemas/open_cvn.schema.json`)
6. un formato canonico "Open CVN JSON" con un contrato unificado de
   parser/validador que soporta importacion desde PDF, XML y JSON
   (`src/open_cvn/`)
7. una aplicacion CLI local sobre todo lo anterior, con almacenamiento SQLite,
   versiones de curriculo maestras/derivadas, exportacion a LaTeX/PDF, e
   importacion opcional asistida por LLM (`src/open_cvn_app/`)

La memoria del TFG esta escrita, firmada y defendida
(`docs/memoria/TFG.pdf` / `TFG_signed.pdf`). El registro completo de su
desarrollo (issues `#11` a `#71`) esta cerrado y archivado en
`docs/context/current_status.md` y
`docs/roadmap/cvn_generation_roadmap.md`; no se anaden nuevas entradas ahi.

## El TFM (En Marcha)

El TFM se construye sobre esa base ya entregada, no la sustituye ni la repite.
Su alcance esta definido en el epic
`docs/roadmap/issues/issue-89-epic-tfm-lakehouse-platform.md` (issue de
GitHub `#89`): una plataforma lakehouse autoalojada sobre Kubernetes para
datos curriculares (MinIO, Iceberg, Spark, Airflow, PostgreSQL, Superset),
con ingesta de CVN sintetico y datos reales de ORCID. El estado activo del
proyecto esta en `docs/context/tfm_current_status.md` y
`docs/roadmap/tfm_roadmap.md`.

## Punto De Entrada

Para obtener el contexto del proyecto y el estado real de implementacion, leer:

1. `PROJECT_GUIDE.md`
2. `docs/context/project_context_index.md`
3. `docs/context/tfm_current_status.md` (estado activo, TFM)

## Documentos Clave

### TFM (activo)

- guia principal del proyecto: `PROJECT_GUIDE.md`
- indice de contexto del proyecto: `docs/context/project_context_index.md`
- estado actual del proyecto: `docs/context/tfm_current_status.md`
- roadmap activo: `docs/roadmap/tfm_roadmap.md`
- epic del TFM (definido, issue de GitHub `#89`):
  `docs/roadmap/issues/issue-89-epic-tfm-lakehouse-platform.md`
- guia de contribucion y setup: `CONTRIBUTING.md`

### TFG (cerrado, base sobre la que se construye el TFM)

- arquitectura del pipeline heredado:
  `docs/pipeline/cvn_pydantic_generation_pipeline.md`
- roadmap completo del TFG (cerrado): `docs/roadmap/cvn_generation_roadmap.md`
- registro de estado completo del TFG (cerrado):
  `docs/context/current_status.md`
- reporte del proceso de desarrollo del TFG:
  `docs/reporte_proceso_desarrollo_tfg.md`
- estructura y trazabilidad de la memoria del TFG (completada):
  `docs/memoria/estructura_memoria_tfg.md`
- limitaciones conocidas heredadas: `docs/pipeline/known_limitations.md`

