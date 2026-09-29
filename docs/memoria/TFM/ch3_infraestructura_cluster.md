# Capítulo 3: Infraestructura: despliegue del clúster y servicios base

Estado: `EN_PROCESO`

## Objetivo del capítulo

Describir cómo se construye la base de infraestructura sobre la que corre
todo lo demás: el clúster Kubernetes, los servicios centrales (MinIO,
PostgreSQL, Airflow), el catálogo Iceberg y la ejecución de Spark sobre
Kubernetes orquestada por Airflow, con la arquitectura general de capas que
el resto de capítulos particulariza.

## Contenido recomendado (ideas principales)

- **Arquitectura general por capas**, presentada una vez aquí y referenciada
  después: cliente/orquestador (Airflow) -> motor de cómputo distribuido
  (Spark sobre k8s) -> almacenamiento de objetos con formato de tabla
  (MinIO + Iceberg) -> capa de publicación (PostgreSQL) -> capa de
  visualización (Superset). Diagrama de despliegue, no solo de flujo de
  datos.
- **k3s como sustrato**: instalación como servicio systemd en un único
  nodo, backend de red `host-gw` (evita un problema conocido de VXLAN/UDP
  bajo el entorno WSL2 usado en desarrollo, detalle a explicar sin
  presentarlo como algo trivial: es una decisión de compatibilidad con el
  entorno real), namespace dedicado.
- **Servicios base por Helm**: MinIO (almacenamiento de objetos, un único
  bucket, prefijo de aterrizaje `bronze` -- se aprovisionó inicialmente
  también con `silver`/`gold`, retirados al comprobarse que esas dos capas
  se generan directamente como tablas Iceberg y nunca aterrizan ficheros
  crudos propios, ver el ajuste de issue `#91`), una instancia de
  PostgreSQL dedicada a la futura capa gold (separada deliberadamente de la
  base de datos de metadatos propia de Airflow, para no acoplar ambos
  sistemas), Airflow con `KubernetesExecutor` (cada tarea es su propio pod,
  sin Celery/Redis).
- **Catálogo Iceberg**: catálogo Hadoop (basado en rutas) sobre un prefijo
  dedicado de MinIO, deliberadamente distinto del prefijo de aterrizaje
  de datos crudos, para que los directorios internos de Iceberg nunca se
  mezclen con ficheros aterrizados directamente.
- **Ejecución de Spark desde Airflow**: el propio pod de la tarea de
  Airflow (`KubernetesPodOperator`) actúa como *driver* de Spark en modo
  `client`, lanzando `spark-submit` contra el clúster; una imagen Spark
  propia con las dependencias de Iceberg/S3A ya integradas; permisos RBAC
  explícitos para que el *driver* pueda crear y limpiar sus propios pods
  ejecutores.
- **Verificación end-to-end del mecanismo central**: antes de construir
  nada de negocio sobre esta base, se comprobó con un trabajo mínimo que
  escribe y relee una tabla Iceberg a través del catálogo, verificado
  además por un pod independiente que no participó en la escritura --
  principio de verificación que se repite en capítulos posteriores.
- **Reproducibilidad como objetivo de diseño**, no solo como documentación
  a posteriori: el sistema se diseñó para poder reconstruirse desde cero
  siguiendo una guía escrita, verificada en la práctica (ver capítulo 6).

## Elementos recomendados

- Diagrama de arquitectura de despliegue (clúster, namespace, servicios,
  flujos de red entre ellos).
- Tabla de servicios desplegados: nombre, tecnología, versión, rol.
- Fragmento de configuración representativo (por ejemplo, la propiedad de
  catálogo Iceberg clave) como código, no como captura de pantalla.

## Outcomes de aprendizaje cubiertos

`CN02`, `CP01`, `HA03` (parcial: orquestación).

## Fuentes principales

- issues `#90` (k3s), `#91` (servicios base), `#92` (catálogo Iceberg),
  `#93` (Spark desde Airflow)
- `docs/development/tfm_lakehouse_workflow.md` (pasos de despliegue reales,
  verificados)
- secciones 1, 3, 4, 7 de `docs/research/tfm/estado_del_arte_tfm.md`

## Estado de redacción

Primer borrador redactado en `docs/memoria/TFM/chapters/ch3.tex`, siguiendo
el estilo mapi, revisado con `elimina-marcas-ia` (sin patrones detectados
en la primera pasada) y aplicando todas las normas ya establecidas: sin
créditos ECTS/plazos/horas/páginas en el texto final, sin autorreferencia
a instrucciones del usuario, enumeraciones en `itemize` (los tres
hallazgos de la Sección 3.5) en vez de dentro de una misma frase.

Seis secciones: arquitectura de despliegue (con tabla de servicios y
versiones), clúster k3s, servicios base (MinIO/PostgreSQL/Airflow, con el
hallazgo operativo real de la migración de Bitnami a `bitnamilegacy`),
catálogo Iceberg sobre MinIO, ejecución de Spark desde Airflow (con los
tres problemas reales encontrados y corregidos: credenciales del
controlador no aplicadas en modo `client`, punto de entrada de la imagen
sustituido en vez de invocado como argumento, permiso `deletecollection`
ausente), y verificación de extremo a extremo (el patrón de doble
comprobación -- trabajo propio más pod independiente -- que se reutilizará
en los capítulos siguientes). No se repiten las justificaciones
tecnológicas ya hechas en el capítulo 2; cada decisión se referencia hacia
allí en vez de rejustificarse.

Se añadieron 3 entradas nuevas a `docs/memoria/TFM/bib/ref.bib` (Docker,
Helm, y la fuente primaria del hallazgo de Bitnami), verificadas contra su
origen. Se encontró y corrigió, antes de darlo por terminado, el mismo
error de citas dentro de tablas/líneas largas que ya había aparecido en el
capítulo 2 (`~\cite{}` sin poder partir de línea): se quitaron las citas
de la tabla de servicios (ya citados en prosa) y se separaron en dos
frases dos citas que quedaban demasiado juntas en un mismo párrafo.

Capítulo compacto: ~5 páginas de cuerpo, dejando margen para los capítulos
con más resultados propios (5, 6). Verificado visualmente (extracción de
páginas del PDF) que ninguna tabla ni título queda huérfano.

**Revisión de puntuación y frase**: el usuario señaló, con un ejemplo
concreto de este capítulo, que una frase con demasiados incisos entre
paréntesis resultaba confusa. Se reescribió el capítulo completo aplicando
tres reglas nuevas, ya recogidas en `estructura_memoria_tfm.md`, que
aplican a partir de ahora a todo el texto final de la memoria: sin
paréntesis en ningún punto, sin punto y coma, y sin mencionar que algo "ya
fue justificado" en otra sección cuando eso ya se explicó allí. Se
corrigió también, de nuevo, el mismo patrón de cita `~\cite{}` sin punto
de ruptura de línea, esta vez en varias entradas de la tabla de servicios
y en dos frases con citas adyacentes.

**Corrección del diseño del cubo de MinIO**: el capítulo describía
inicialmente el cubo `lakehouse` con tres prefijos de aterrizaje,
`bronze`/`silver`/`gold`. Se comprobó, revisando issues `#91`-`#99`, que
ningún componente construido ni previsto escribe nunca ficheros crudos
bajo `silver`/`gold`: esas dos capas se generan enteramente como tablas
Iceberg. Se corrigió el diseño real del cubo, `infra/helm-values/minio-
values.yaml` y `infra/spark-conf/README.md`, dejando un único prefijo de
aterrizaje, `bronze`, y se dejó constancia del ajuste en
`docs/roadmap/tfm/issues/issue-91-core-services-deployment.md`. El
capítulo se reescribió para narrarlo como la evolución de diseño que fue,
no como un hallazgo de la propia redacción de la memoria.
