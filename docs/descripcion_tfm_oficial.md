# Diseño de una arquitectura lakehouse escalable para la integración y análisis de información curricular académica

## Descripción y Objetivos

El Trabajo de Fin de Grado previo de este mismo autor definió un esquema de datos abierto (Open CVN) para el Curriculum Vitae Normalizado (CVN) español, junto con un analizador/validador y una aplicación local de gestión de currículos. Ese trabajo resuelve el problema a nivel de un único investigador y un único documento. Sin embargo, la gestión institucional de la actividad investigadora (evaluaciones, memorias de grupo, indicadores de producción científica) requiere integrar y analizar datos curriculares de muchos investigadores procedentes de fuentes heterogéneas, a un volumen y con una infraestructura que una aplicación local de escritorio no puede ofrecer.

Este Trabajo de Fin de Máster (TFM) tiene como objetivo diseñar y desplegar una plataforma lakehouse autoalojada, sobre Kubernetes, que ingiera datos curriculares y de trayectoria investigadora procedentes de dos fuentes: CVN, en formato Open CVN JSON validado contra el esquema JSON Schema definido en el TFG, y ORCID, con datos reales y públicos obtenidos tanto mediante su API pública como mediante su fichero público de datos a granel. La plataforma organizará la información en capas bronze, silver y gold preservando la procedencia de cada dato, la procesará mediante computación distribuida y, en caso de coincidir un registro procedente de CVN y uno procedente de ORCID (por identificador ORCID o, en su defecto, por nombre/afiliación normalizados), resolverá la identidad duplicada entre ambas fuentes; publicará además un conjunto reducido de indicadores de investigación en un cuadro de mando, acompañado de un benchmark de rendimiento acotado.

La pila tecnológica prevista es: clúster Kubernetes local (k3s); almacenamiento de objetos compatible con S3 (MinIO); formato de tabla lakehouse (Apache Iceberg) con catálogo Hadoop sobre el propio almacén de objetos; procesamiento distribuido con Apache Spark en modo Kubernetes; orquestación de los pipelines de ingesta y transformación con Apache Airflow; y publicación de los indicadores en Apache Superset sobre una base de datos PostgreSQL. El resultado esperado es una plataforma funcional de extremo a extremo (ingesta, transformación, publicación y visualización), reproducible desde cero, junto con la memoria correspondiente.

## Metodología y Competencias

El trabajo se estructura en las siguientes fases:

1. **Despliegue de la infraestructura base**: puesta en marcha del clúster Kubernetes (k3s) y de los servicios centrales (MinIO, PostgreSQL, Airflow) mediante Helm, con comprobación de que cada uno es accesible.
2. **Integración de Iceberg y Spark**: configuración de un catálogo Iceberg sobre MinIO y validación de que Spark, lanzado desde Airflow, puede escribir y leer tablas Iceberg de extremo a extremo.
3. **Ingesta de datos**: desarrollo de un cliente para la API pública de ORCID, de un proceso de descarga y filtrado del fichero público de datos de ORCID, y de un proceso de ingesta de currículos en formato Open CVN JSON; aterrizaje de ambas fuentes en la capa bronze con metadatos de procedencia.
4. **Transformación y resolución de identidades**: validación y normalización de bronze a silver (reutilizando el contrato de validación del TFG para el lado CVN), resolución de entidades duplicadas entre fuentes, y cálculo de un pequeño conjunto de indicadores de investigación en la capa gold.
5. **Visualización y evaluación de rendimiento**: despliegue de un cuadro de mando sobre los indicadores publicados y ejecución de un benchmark que mida el efecto del número de ejecutores Spark sobre el tiempo de procesamiento a distintas escalas de datos.
6. **Consolidación y documentación**: cierre de incidencias, elaboración de una guía de reproducibilidad y redacción de la memoria, mantenida de forma incremental a lo largo de todo el trabajo en lugar de al final.

Mediante la realización de este TFM se trabajarán las siguientes competencias específicas del Máster en Big Data y Cloud Computing:

| Código | Descripción |
| --- | --- |
| `CN02` | Conocer las arquitecturas para tratamiento masivo de datos y las técnicas de almacenamiento, orquestación de procesos y pipelines necesarias para construir soluciones avanzadas. |
| `HA01` | Analizar datos masivos en contextos reales, abordando desafíos como la adquisición de múltiples fuentes, la fusión y preparación de datos, y la explotación de los modelos e información generadas. |
| `HA02` | Aplicar técnicas de procesamiento distribuido y de optimización de recursos para la ejecución eficiente de cargas de trabajo de big data. |
| `HA03` | Orquestar procesos de ETL (Extract, Transform, Load) para adquirir y procesar datos masivos estructurados, semiestructurados y no estructurados de diversas fuentes, incluidos Data Lakes, y diseñar la arquitectura necesaria para almacenarlos de manera estructurada, asegurando una gestión eficiente y escalable del almacenamiento de datos. |
| `CP01` | Planificar y desplegar soluciones de big data en infraestructuras escalables, seleccionando y justificando la arquitectura tecnológica más adecuada para cada caso de uso. |
| `CP04` | Desarrollar trabajos de ingeniería informática originales y de naturaleza profesional en proyectos de big data y computación en la nube integrando los conocimientos, habilidades y competencias adquiridos en las enseñanzas. |

## Medios A Utilizar

Un PC con recursos suficientes de CPU, RAM y almacenamiento para ejecutar un clúster k3s local con MinIO, PostgreSQL, Airflow, Spark y Superset simultáneamente; Kubernetes (k3s) y Helm; el lenguaje de programación Python; acceso a la API pública de ORCID (registro gratuito de cliente) y al fichero público de datos de ORCID.

## Bibliografía

- Documentación de k3s: <https://docs.k3s.io/>
- Documentación de MinIO: <https://min.io/docs/>
- Apache Iceberg: <https://iceberg.apache.org/>
- Apache Spark on Kubernetes: <https://spark.apache.org/docs/latest/running-on-kubernetes.html>
- Apache Airflow: <https://airflow.apache.org/docs/>
- Apache Superset: <https://superset.apache.org/docs/intro>
- ORCID Public API v3.0: <https://info.orcid.org/documentation/features/public-api/>
- ORCID Public Data File: <https://orcid.org/blog/2017/03/22/orcid-public-data-file>
- Esquema Open CVN JSON y contrato de validación (TFG previo del autor): `docs/pipeline/open_cvn_json_format.md`, `docs/pipeline/parser_validator_contract.md`
