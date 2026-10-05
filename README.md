# Open CVN

Esquema de datos abierto para curriculos academicos (basado en el CVN espanol)
y plataforma lakehouse para integrarlos y analizarlos.

## Descripcion

Este repositorio contiene dos trabajos academicos sucesivos sobre el mismo
proyecto, ambos de la Universidad de Castilla-La Mancha (ESIIAB):

- un **Trabajo de Fin de Grado (TFG)**, terminado y defendido, que define un
  formato abierto de curriculo y las herramientas para generarlo, validarlo,
  almacenarlo y exportarlo
- un **Trabajo de Fin de Master (TFM)**, con la implementacion terminada y la
  memoria en redaccion, que construye sobre esa base una plataforma lakehouse
  autoalojada para integrar y analizar informacion curricular

El problema de partida es que, aunque el CVN existe como formato normalizado,
la elaboracion, mantenimiento y adaptacion de curriculos a distintos contextos
sigue consumiendo mucho tiempo y dificulta el desarrollo de herramientas
abiertas interoperables. Una de las causas es la ausencia de una definicion de
bajo nivel suficientemente clara para representar y procesar estos datos.

## El TFG (terminado)

El TFG definio un esquema de datos que permite la gestion automatizada de
curriculos academicos y de investigacion en Espana, construyendo un pipeline
completo por capas:

1. bindings Pydantic estructurales generados desde el paquete oficial CVN
   XML/XSD (`src/generated/`)
2. una capa de normalizacion que indexa cada campo por su codigo CVN y lo
   resuelve contra los catalogos de referencia auxiliares
   (`src/cvn_codegen/normalization.py`)
3. una capa de politica semantica que traduce esa evidencia en decisiones
   deterministas de tipado y nomenclatura
   (`src/cvn_codegen/semantic_policy.py`)
4. un generador de modelos de dominio finales
   (`src/cvn_codegen/domain_model_generator.py`, salida en
   `src/models/cvn/generated/`)
5. un modelo conceptual agnostico del que salen los diagramas UML-like y un
   JSON Schema (`docs/diagrams/`, `schemas/open_cvn.schema.json`)
6. el formato canonico **Open CVN JSON** y un contrato unificado de
   parser/validador con importacion desde PDF, XML y JSON (`src/open_cvn/`)
7. una aplicacion CLI local con almacenamiento SQLite, versiones de curriculo
   maestras/derivadas, exportacion a LaTeX/PDF e importacion opcional asistida
   por LLM (`src/open_cvn_app/`)

Su registro de desarrollo (issues `#11` a `#71`) esta cerrado y archivado en
`docs/context/tfg/current_status.md` y
`docs/roadmap/tfg/cvn_generation_roadmap.md`; no se anaden nuevas entradas ahi.

## El TFM (implementacion terminada, memoria en redaccion)

El TFM construye sobre esa base sin sustituirla. Su alcance esta definido en el
epic `docs/roadmap/tfm/issues/issue-89-epic-tfm-lakehouse-platform.md`: una
plataforma lakehouse autoalojada sobre Kubernetes (k3s) para datos
curriculares, con ingesta de CVN sintetico y datos reales de ORCID.

| Capa | Tecnologia | Codigo / configuracion |
| --- | --- | --- |
| Cluster | k3s (local) | `infra/k3s/` |
| Almacenamiento | MinIO + Apache Iceberg (catalogo Hadoop) | `infra/helm-values/`, `infra/spark-conf/` |
| Procesamiento | Apache Spark (`spark-submit`) | `src/tfm_lakehouse/spark_jobs/` |
| Orquestacion | Apache Airflow (`KubernetesExecutor`) | `dags/` |
| Servicio | PostgreSQL + Apache Superset | `infra/superset/` |

Flujo de datos, en capas bronze / silver / gold:

1. **Ingesta** (`ingest_validate`): cliente de la API publica de ORCID, subconjunto
   filtrado del fichero masivo de ORCID y generador de CVN sintetico valido
   contra el esquema; aterrizaje en bronze con sobre de procedencia
2. **Bronze -> silver**: validacion por fuente y resolucion de entidades
   determinista entre fuentes, evaluada contra la verdad de referencia del
   generador sintetico
3. **Silver -> gold** (`transform_publish`): indicadores de investigacion
   (publicaciones por investigador y ano, linea temporal de afiliaciones, pares
   de colaboracion) publicados a PostgreSQL con intercambio atomico
4. **Visualizacion**: panel de Superset sobre agregados, sin nombres personales
5. **Evaluacion**: benchmark acotado de Spark segun numero de ejecutores y
   escala de datos (`docs/benchmark/`)

Los issues `#90` a `#102` estan completados. El issue `#103` (ensamblado de la
memoria) esta en curso: los siete capitulos y los seis anexos estan redactados
en `docs/memoria/TFM/`; queda la revision final y el ajuste al limite de paginas.
El estado detallado esta en `docs/context/tfm/current_status.md` y
`docs/roadmap/tfm/tfm_roadmap.md`.

## Puesta en marcha

Requisitos: `uv` y Python 3.14.

```bash
uv sync --group codegen --group testing
uv pip install -e .
uv run pytest -n auto tests
```

- Regeneracion completa del pipeline CVN: `docs/development/regeneration_workflow.md`
- Plataforma lakehouse de principio a fin (requiere WSL2 con systemd, Docker,
  `kubectl` y `helm`): `docs/development/tfm_lakehouse_workflow.md`
- Los DAGs de Airflow fijan en `REPO_ROOT` la ruta del repositorio; hay que
  editarla en `dags/ingest_validate.py` y `dags/transform_publish.py` al
  clonarlo en otra ruta (ver el documento anterior)

## Memorias

Los PDF de las memorias (TFG y TFM) **no se publican** en este repositorio. Su
fuente LaTeX esta en `docs/memoria/TFG/` y `docs/memoria/TFM/`. La declaracion
de autoria usa un DNI que se lee de `include/datos_personales.tex`, fichero
local ignorado por git; sin el, la memoria compila con un valor ficticio. Para
usar el propio, copiar `include/datos_personales.example.tex` a
`include/datos_personales.tex` y editarlo.

## Punto de entrada

Para obtener el contexto del proyecto y el estado real de implementacion, leer:

1. `PROJECT_GUIDE.md`
2. `docs/context/project_context_index.md`
3. `docs/context/tfm/current_status.md` (estado activo, TFM)

## Documentos clave

### TFM (activo)

- guia principal del proyecto: `PROJECT_GUIDE.md`
- indice de contexto del proyecto: `docs/context/project_context_index.md`
- estado actual del proyecto: `docs/context/tfm/current_status.md`
- roadmap activo: `docs/roadmap/tfm/tfm_roadmap.md`
- epic del TFM (issue `#89`):
  `docs/roadmap/tfm/issues/issue-89-epic-tfm-lakehouse-platform.md`
- flujo de trabajo y reproducibilidad de la plataforma:
  `docs/development/tfm_lakehouse_workflow.md`
- resultados del benchmark: `docs/benchmark/results.md`
- estado del arte y justificacion tecnologica:
  `docs/research/tfm/estado_del_arte_tfm.md`
- guia de contribucion y setup: `CONTRIBUTING.md`

### TFG (cerrado, base sobre la que se construye el TFM)

- arquitectura del pipeline heredado:
  `docs/pipeline/cvn_pydantic_generation_pipeline.md`
- roadmap completo del TFG: `docs/roadmap/tfg/cvn_generation_roadmap.md`
- registro de estado completo del TFG: `docs/context/tfg/current_status.md`
- reporte del proceso de desarrollo del TFG:
  `docs/reporte_proceso_desarrollo_tfg.md`
- estructura y trazabilidad de la memoria del TFG:
  `docs/memoria/TFG/estructura_memoria_tfg.md`
- limitaciones conocidas: `docs/pipeline/known_limitations.md`

## Autoria y licencia

Autor: Carlos Martinez Jaen. Director: Luis De La Ossa Jimenez. Escuela
Superior de Ingenieria Informatica de Albacete (ESIIAB), Universidad de
Castilla-La Mancha.

Licencia GPL-3.0, ver `LICENSE`. El paquete CVN XML/XSD de
`docs/CvnXML_v1.4.3_2.1_17012025/` es material oficial de la FECYT incluido como
fuente de referencia y no esta cubierto por esa licencia.
