# Estado del arte y justificación tecnológica del TFM

## Propósito de este documento

Este documento es un **documento de investigación de apoyo**, no parte del
texto final de la memoria. Su función es la misma que cumplió
`docs/research/` para el TFG (ver `docs/reporte_proceso_desarrollo_tfg.md`,
que describe cómo la investigación inicial en `docs/research/` alimentó el
capítulo de estado del arte de la memoria del TFG): reunir en un solo lugar
la revisión comparativa del ecosistema tecnológico relevante para el TFM y la
justificación razonada de cada decisión de arquitectura, para que el
capítulo "Estado del arte" de la memoria del TFM (issue `#103`, ver
`docs/roadmap/tfm/issues/issue-103-memoria-assembly.md`) se redacte a partir
de este análisis en lugar de reconstruirse de memoria al final del proyecto.

Vive en `docs/research/tfm/` en lugar de en `docs/research/` directamente
porque ese directorio, aunque no forma parte todavía de la taxonomía formal
descrita en `docs/documentation/documentation_conventions.md`, contiene
material de investigación específico del TFG (`draft.txt`,
`latex_project/`); separarlo en subcarpetas `tfg/`/`tfm/` sigue la misma
convención ya aplicada a `docs/roadmap/` y `docs/context/` en
`docs/roadmap/tfm/hotfixes/hotfix-10-tfg-tfm-documentation-folder-separation.md`,
sin tocar ni reorganizar el contenido del TFG ya cerrado.

Este documento **no sustituye** la tabla "Technology Stack Decision Record"
de `docs/roadmap/tfm/issues/issue-89-epic-tfm-lakehouse-platform.md`; la
**extiende**. Aquella tabla resume, en un renglón por decisión, la elección,
la alternativa rechazada y una razón breve. Aquí se desarrolla el contexto
de cada familia tecnológica (qué problema resuelve, qué alternativas existen
en el estado actual del ecosistema y por qué se descartan) con el detalle
argumental que exige un capítulo de estado del arte académico, y se cierra
con una síntesis que remite de vuelta a la tabla del epic.

## Alcance y método

La revisión se organiza por capa de la arquitectura, siguiendo el mismo
orden que la tabla de decisiones del epic `#89`, y para cada capa se sigue
el mismo esquema:

1. qué problema resuelve esa capa dentro de una arquitectura lakehouse;
2. qué alternativas son relevantes en el estado actual del ecosistema
   (no una enumeración exhaustiva, sino las opciones que un proyecto de
   estas características razonablemente consideraría);
3. por qué se elige la opción usada en este TFM, atendiendo simultáneamente
   a: (a) los resultados de aprendizaje que el epic mapea explícitamente
   (`CN02`, `HA01`, `HA02`, `HA03`, `CP01`, `CP04`), (b) las restricciones
   académicas duras del epic (6 ECTS, 20 días, ~120-140 horas, clúster local
   de una sola máquina), y (c) la madurez/soporte de la opción en el resto
   del ecosistema elegido, no solo en aislado.

Las decisiones ya verificadas empíricamente durante la implementación (por
ejemplo, los hallazgos de los issues `#90`-`#102`) se citan como evidencia
adicional cuando refuerzan o matizan la justificación de origen, pero este
documento no repite el detalle operativo de esos issues; remite a ellos.

## 1. De los sistemas de almacenamiento analítico al lakehouse

Un sistema de información de investigación que integra currículos (CVN) y
perfiles de investigador (ORCID) necesita almacenar datos con dos exigencias
en tensión: la escala y variedad propias de un *data lake* (documentos
semiestructurados, volumen creciente, múltiples fuentes con esquemas
distintos) y las garantías transaccionales y de gobierno de datos propias de
un *data warehouse* (consistencia, control de esquema, consultas analíticas
fiables para publicar indicadores).

- **Data warehouse clásico** (modelado dimensional a la Kimball/Inmon, motor
  relacional propietario o gestionado): fuerte en consistencia y consulta
  analítica, pero exige *schema-on-write*, lo que penaliza la ingesta de
  fuentes heterogéneas como CVN (documentos JSON anidados) y ORCID (XML/JSON
  con estructuras propias) sin un proceso de transformación previo costoso.
- **Data lake clásico** (HDFS o almacenamiento de objetos con ficheros Parquet/
  ORC sueltos, *schema-on-read*): flexible para ingerir cualquier fuente, pero
  sin metadatos transaccionales corre el riesgo bien documentado del *data
  swamp*: lecturas inconsistentes durante reescrituras, ausencia de control de
  esquema, sin *time travel* para auditar cambios.
- **Lakehouse**: arquitectura que añade una capa de metadatos transaccionales
  (formato de tabla abierto) sobre almacenamiento de objetos barato, dando
  transacciones ACID, evolución de esquema controlada y *time travel* sin
  necesitar mover los datos a un motor relacional cerrado. La formulación de
  referencia de este patrón es Armbrust et al., *"Lakehouse: A New Generation
  of Open Source Systems and Architecture for Data Warehousing and Data
  Analytics"* (CIDR 2021), que documenta precisamente la convergencia de
  ambos mundos.

**Decisión**: arquitectura lakehouse (MinIO + Apache Iceberg + Spark), con
capas bronce/plata/oro. Justificación: (a) es exactamente lo que `CN02`
("arquitecturas de tratamiento masivo, almacenamiento y pipelines") pide
demostrar; (b) evita mantener dos sistemas de almacenamiento distintos
(un lago para ingesta y un almacén separado para BI), lo que no cabría en
el presupuesto de 120-140 horas; (c) las tres capas bronce/plata/oro dan un
lugar natural para conservar procedencia por fuente (bronce), aplicar
resolución de identidad y calidad de datos (plata), y publicar agregados
listos para consumo (oro), que es precisamente la fusión multi-fuente que
pide `HA01`.

## 2. Formato de tabla: Apache Iceberg frente a Delta Lake y Apache Hudi

Un lakehouse necesita un **formato de tabla abierto**: una capa de metadatos
(esquema, particiones, snapshots) sobre ficheros Parquet/ORC/Avro en
almacenamiento de objetos, que dé transacciones ACID y evolución de esquema
sin depender de un metastore propietario. Los tres formatos con adopción
real en el ecosistema son:

| Formato | Origen y gobierno | Punto fuerte | Ajuste con este TFM |
| --- | --- | --- | --- |
| **Apache Iceberg** | Nacido en Netflix para superar los límites de las tablas Hive a escala de petabytes; proyecto de nivel superior de la Apache Software Foundation, gobierno multi-vendedor | Soporte multi-motor amplio (Spark, Trino, Flink, Presto, Dremio), particionado oculto, evolución de esquema y de partición sin reescritura, *snapshot isolation* | Sin acoplamiento a un único proveedor; el mismo catálogo puede consumirse en el futuro desde Trino sin cambiar el formato de tabla |
| **Delta Lake (OSS)** | Nacido en Databricks; donado a la Linux Foundation en 2019 | Excelente integración con el ecosistema Databricks/Spark; funciones avanzadas (p. ej. `MERGE`/`OPTIMIZE` afinados) suelen requerir el runtime propietario para su versión más completa | Fuera de un entorno Databricks, el soporte multi-motor histórico ha sido más limitado que el de Iceberg |
| **Apache Hudi** | Nacido en Uber, orientado a *upserts*/CDC de baja latencia sobre streams | Óptimo para cargas de actualización incremental frecuente (streaming, CDC) | El TFM es un pipeline **por lotes** (`ingest_validate` diario, `transform_publish` manual) que reconstruye plata/oro por completo en cada ejecución (ver `docs/pipeline/known_limitations.md`, "Silver Is Rebuilt In Full On Every Run" / "Gold Is Rebuilt In Full..."); no hay necesidad de *upserts* incrementales de baja latencia, así que la ventaja diferencial de Hudi no aplica aquí |

**Decisión**: Apache Iceberg. Justificación adicional a la tabla anterior:
neutralidad de proveedor (gobierno Apache, no ligado a un único vendedor
comercial), semántica de lakehouse real (evolución de esquema, *time
travel*) suficiente para las necesidades del proyecto, y es la opción que el
propio usuario confirmó explícitamente como aceptable "si es más fácil y no
rompe los requisitos mínimos" (registrado en el epic `#89`). Delta Lake OSS
quedó como alternativa razonable pero secundaria, dado el menor historial de
soporte multi-motor fuera de Databricks; Hudi se descarta por no encajar con
el patrón de carga por lotes del proyecto.

### 2.1. Catálogo de Iceberg: catálogo Hadoop frente a Hive Metastore, catálogo REST y Nessie

Iceberg necesita un catálogo que resuelva nombres de tabla a la ubicación de
su metadato raíz. Las opciones habituales:

- **Hive Metastore**: el catálogo históricamente más extendido, pero exige
  desplegar y operar un servicio adicional (metastore + base de datos
  relacional propia) solo para resolución de nombres.
- **Catálogo REST** (especificación *Iceberg REST Catalog*, implementada por
  motores como Tabular/Databricks Unity Catalog/Polaris): el camino que el
  propio proyecto Iceberg promueve como futuro estándar de interoperabilidad
  entre motores, pero de nuevo exige desplegar y mantener un servicio
  adicional.
- **Nessie** (Project Nessie, de Dremio): catálogo versionado al estilo Git
  (ramas, *commits*, *time travel* a nivel de catálogo completo, no solo de
  tabla), muy atractivo para flujos multi-escritor con control de versiones
  explícito, pero de nuevo un servicio adicional a desplegar y depurar.
- **Catálogo Hadoop (basado en ruta)**: el catálogo más simple posible;
  resuelve el nombre de tabla directamente contra una convención de rutas en
  el propio almacenamiento de objetos (`s3a://lakehouse/warehouse/...`), sin
  ningún servicio adicional.

**Decisión**: catálogo Hadoop. Justificación: dentro del presupuesto de 20
días, no hay margen para depurar un servicio de catálogo adicional cuando el
proyecto tiene un único escritor por capa (los jobs de Spark orquestados por
Airflow) y no necesita versionado de catálogo a nivel de repositorio. La
capacidad de Nessie de versionar el catálogo completo, y la interoperabilidad
multi-motor de un catálogo REST, son ventajas reales pero se documentan
explícitamente como trabajo futuro en el epic (`docs/roadmap/tfm/issues/issue-89-epic-tfm-lakehouse-platform.md`,
"Known Limitations"), no descartadas por falta de mérito técnico sino por
proporcionalidad de alcance a 6 ECTS.

## 3. Almacenamiento de objetos: MinIO frente a HDFS y almacenamiento cloud nativo

- **HDFS**: la opción "clásica" de Big Data, pero acopla almacenamiento y
  cómputo en los mismos nodos, lo que contradice el propio patrón lakehouse
  (que separa deliberadamente almacenamiento barato de cómputo elástico) y
  añade una pieza operativa más (NameNode/DataNodes) a un clúster de un solo
  nodo con presupuesto de tiempo ajustado.
- **Almacenamiento cloud nativo** (Amazon S3, Google Cloud Storage, Azure
  Blob Storage): es la opción de producción real para un lakehouse, pero
  incompatible con la decisión de alcance "clúster local únicamente" del
  epic (coste, dependencia de una cuenta cloud, y pérdida del carácter
  autoalojado y reproducible del proyecto sin coste que exige el calendario
  de 20 días).
- **MinIO**: servidor de objetos autoalojado, compatible con la API S3
  (protocolo `s3a://` idéntico al que usarían Spark/Iceberg contra AWS S3
  real). Es la sugerencia original del propio usuario, registrada en el epic.

**Decisión**: MinIO. Justificación: compatibilidad de API con S3 real
significa que el mismo código de los *jobs* de Spark (`spark-conf/
iceberg-catalog.conf`, issue `#92`) funcionaría sin cambios apuntando a un
bucket S3 real, lo que demuestra en la práctica la separación
almacenamiento/cómputo que pide `CN02` sin incurrir en coste ni en una
dependencia externa que rompería la reproducibilidad exigida por el
*quickstart* de `docs/development/tfm_lakehouse_workflow.md` (issue `#102`).

## 4. Sustrato de orquestación de contenedores: Kubernetes (k3s) frente a Docker Swarm y despliegue sin orquestador

- **Despliegue directo (sin orquestador de contenedores)**: instalar cada
  servicio (MinIO, PostgreSQL, Airflow, Spark, Superset) como proceso o
  contenedor suelto en la máquina. Es la opción más simple de depurar, pero
  pierde el modelo declarativo de despliegue (valores de Helm como
  infraestructura como código versionada) y no ejercita ninguna de las
  competencias de "Computación en la Nube" que el programa exige evaluar.
- **Docker Swarm**: orquestador de contenedores más simple que Kubernetes,
  pero prácticamente ausente del stack de herramientas oficial del
  ecosistema Big Data actual: ni Apache Spark, ni Apache Airflow, ni Apache
  Superset publican soporte de despliegue nativo para Swarm equivalente al
  que sí publican para Kubernetes (chart de Helm oficial de Airflow y de
  Superset; *backend* de programación nativo de Kubernetes en Spark desde la
  versión 2.3).
- **Kubernetes**: el estándar de facto para orquestación de contenedores
  (proyecto insignia de la CNCF), con soporte de primera clase en cada una
  de las demás piezas elegidas.

**Decisión**: Kubernetes, distribución **k3s**. Justificación de Kubernetes
frente a Swarm: es la habilidad esperada en un programa de "Big Data y
Computación en la Nube" y cada otro componente elegido ya ofrece soporte Kubernetes
de primera clase, evitando reinventar despliegues no oficiales. Justificación
de k3s en particular frente a una instalación de Kubernetes completa
(`kubeadm`) o herramientas de desarrollo local como `minikube`/`kind`: k3s es
una distribución de Kubernetes **certificada y conforme** (Rancher/SUSE),
empaquetada como binario único con una huella de recursos reducida, apta
para ejecutarse en una sola máquina de desarrollo, pero sin dejar de ser
Kubernetes real: todo manifiesto o *chart* de Helm escrito contra k3s en este
TFM es portable sin cambios a un clúster multi-nodo o a un Kubernetes
gestionado en la nube, que es exactamente el camino de trabajo futuro que el
epic deja documentado ("Multi-node / real cloud VMs via Terraform").

### 4.1. Modo de red: `host-gw` frente al *backend* Flannel por defecto

Detalle operativo verificado en el propio issue `#90` (`docs/roadmap/tfm/issues/issue-90-k3s-cluster-bring-up.md`):
bajo WSL2, el *backend* VXLAN por defecto de Flannel tiene problemas
conocidos de encapsulado UDP; se seleccionó `--flannel-backend=host-gw`
específicamente para evitarlos. Se documenta aquí porque es una decisión de
infraestructura condicionada por el entorno de desarrollo concreto (WSL2), no
una limitación de Kubernetes en sí, y no debe generalizarse como argumento en
contra de k3s en otros entornos.

## 5. Procesamiento distribuido: Apache Spark frente a Apache Flink y Dask/Ray

- **Apache Flink**: motor *stream-first*, pensado para procesamiento de baja
  latencia y CDC continuo. El TFM no tiene esa forma: `ingest_validate` es
  un DAG con periodicidad diaria y `transform_publish` es de disparo manual
  (ver `dags/`), es decir, procesamiento por lotes programado, no un flujo
  continuo de eventos. Adoptar Flink añadiría la complejidad operativa de su
  topología *JobManager*/*TaskManager* sin que el proyecto explote su ventaja
  diferencial.
- **Dask / Ray**: motores de cómputo distribuido nativos de Python, con una
  curva de adopción más suave para código Python puro, pero con un soporte de
  Iceberg nativo mucho menos maduro y una presencia mucho menor que Spark en
  arquitecturas lakehouse de referencia y en la bibliografía/currícula de Big
  Data.
- **Apache Spark**: motor de procesamiento distribuido de referencia para
  lotes, con integración nativa y madura con Iceberg
  (`iceberg-spark-runtime`, usada y fijada en el issue `#92`), *backend* de
  programación nativo sobre Kubernetes (sin necesitar el *Spark Kubernetes
  Operator*, ver más abajo), y descrito en la publicación de referencia
  Zaharia et al., *"Apache Spark: A Unified Engine for Big Data Processing"*
  (Communications of the ACM, 2016) como un motor unificado para procesamiento
  por lotes, streaming, SQL y aprendizaje automático sobre un mismo modelo de
  ejecución.

**Decisión**: Apache Spark, lanzado con `spark-submit` en modo Kubernetes
(`client`) desde Airflow, sin el *Spark Kubernetes Operator*. Justificación:
Spark es el motor que `HA02` ("procesamiento distribuido y optimización de
recursos") espera evidenciar de forma directa, y su integración con Iceberg
es la más probada del ecosistema. Se descarta el *Spark Kubernetes Operator*
—que gestiona aplicaciones Spark mediante *Custom Resource Definitions*—
porque añade un controlador adicional que instalar, actualizar y depurar
dentro del presupuesto de 20 días, mientras que `spark-submit` en modo
`client` desde un `KubernetesPodOperator` de Airflow sigue programando
ejecutores como pods reales de Kubernetes (procesamiento genuinamente
distribuido, ver el benchmark del issue `#101`) sin esa pieza extra. El
propio issue `#93` documenta, como hallazgo empírico, que ciertas propiedades
`spark.kubernetes.driver.*` son no-operativas en modo `client` y tuvieron que
moverse a la especificación del pod del propio `KubernetesPodOperator`: un
coste de aprendizaje real de esta elección, asumido y resuelto, y ya
registrado en `docs/pipeline/known_limitations.md`.

## 6. Orquestación de flujos ETL: Apache Airflow frente a Prefect, Dagster y Luigi

| Orquestador | Punto fuerte | Por qué no se elige aquí |
| --- | --- | --- |
| **Prefect** | Ergonomía de desarrollo local moderna, definición de flujos como código Python idiomático | Menor madurez de despliegue nativo en Kubernetes en producción (frente al *chart* oficial y al `KubernetesExecutor` de Airflow) y mucha menor presencia en la currícula/bibliografía de Big Data en el momento de esta revisión |
| **Dagster** | Modelo de "activos de datos" con linaje explícito entre pasos, atractivo para *pipelines* de lago de datos | Ecosistema más joven; la ventaja de linaje explícito es real pero no crítica para un pipeline de solo tres etapas (bronce/plata/oro) con procedencia ya resuelta a nivel de tabla por Iceberg y por las convenciones `cvn_trace`/`x-open-cvn-*` heredadas del TFG |
| **Luigi** | Simplicidad, orientado a tareas con dependencias | Sin interfaz de administración ni API REST comparable, y sin un executor nativo de Kubernetes mantenido equivalente al `KubernetesExecutor` de Airflow |
| **Apache Airflow** | Orquestador incumbente, *chart* de Helm oficial, `KubernetesExecutor` de primera clase | — |

**Decisión**: Apache Airflow, con `KubernetesExecutor`. Justificación:
sugerencia original del propio usuario (registrada en el epic), satisface
directamente `HA03` ("orquestación ETL y almacenamiento escalable"), y es la
opción con mayor madurez de despliegue Kubernetes-nativo disponible sin
añadir servicios extra. Frente al `CeleryExecutor` (la otra opción madura de
Airflow), el `KubernetesExecutor` evita levantar y operar un *broker*
adicional (Redis/RabbitMQ) y un *backend* de resultados: cada tarea se
ejecuta como su propio pod, reutilizando el propio clúster como sustrato de
ejecución en lugar de añadir una pieza más. Prefect y Dagster quedan
documentados aquí como alternativas legítimas y en ascenso, no descartadas
por carencia técnica sino por la proporción entre su curva de adopción y el
presupuesto de 20 días del TFM.

## 7. Capa de consulta interactiva: Spark SQL frente a Trino/Presto

Trino (originalmente PrestoSQL) es un motor de consulta SQL federado de baja
latencia, diseñado para consultas interactivas ad hoc directamente sobre
tablas Iceberg, sin pasar por la sobrecarga de arranque de un *job* de Spark.
Estaba en el planteamiento original del proyecto (mencionado explícitamente
en el epic), pero se descarta para este alcance: exigiría desplegar y afinar
un servicio adicional (coordinador + *workers* de Trino) únicamente para
ofrecer una vía de consulta interactiva que el proyecto no necesita, porque
Superset no consulta la capa oro directamente (ver más abajo) y todo el
acceso programático a los datos ya se hace desde los propios *jobs* de Spark.
Queda documentado como trabajo futuro explícito.

## 8. Capa de BI: Apache Superset frente a Metabase, Grafana y herramientas propietarias

- **Grafana**: excelente para paneles de observabilidad y series
  temporales, pero peor ajuste para gráficos analíticos agregados sobre un
  esquema dimensional relacional (publicaciones por año, series de
  afiliación, pares de colaboración), que es la forma real de los
  indicadores de este TFM (ver issue `#99`).
- **Power BI / Tableau**: herramientas de BI propietarias con licencia
  comercial; incompatibles con la naturaleza autoalojada y de coste cero del
  resto de la plataforma, y con el requisito de reproducibilidad completa
  desde cero documentado en `docs/development/tfm_lakehouse_workflow.md`
  (issue `#102`).
- **Metabase**: alternativa de código abierto comparable, con una curva de
  entrada más simple, pero con un modelo de panel/gráfico menos expresivo
  para exportar el panel completo como código versionado. Este TFM necesitaba
  precisamente eso: el panel de Superset se gestiona como "*dashboard as
  code*" (`infra/superset/assets/`, un script de importación por API REST,
  issue `#100`), de forma que el panel completo es reproducible por completo
  desde el repositorio, no un artefacto manual imposible de versionar.
- **Apache Superset**: herramienta de BI de código abierto con conector
  nativo de PostgreSQL y *chart* de Helm.

**Decisión**: Apache Superset, conectado a PostgreSQL (no directamente a
Iceberg/Spark). Justificación de Superset: coherente con la postura
autoalojada y de código abierto del resto de la pila, y su modelo de
exportación de panel encaja con la exigencia de reproducibilidad del
proyecto. Justificación de la conexión vía PostgreSQL en lugar de un
conector directo a Iceberg (a través de Trino o de un *Spark Thrift
Server*): ya se ha descartado Trino por alcance (sección 7), y levantar un
*Spark Thrift Server* solo para dar a Superset una vía de consulta habría
sido una pieza operativa adicional para el mismo fin; como las tablas de la
capa oro ya están agregadas y son pequeñas en el momento de publicarse,
materializarlas en PostgreSQL como último paso del *pipeline*
(`publish_gold_to_postgres`, issue `#99`) da a Superset un conector nativo
sin fricción, sin necesitar ningún servicio intermedio adicional. El propio
issue `#100` documenta un hallazgo relevante para el estado del arte: el
*chart* de Helm `superset/superset` está **obsoleto** en el momento de esta
revisión (la vía oficial pasa ahora por un operador `v1alpha1`), lo que se
gestionó fijando la versión del *chart* y construyendo una imagen propia con
el controlador de PostgreSQL, en lugar de migrar a un operador todavía en
maduración dentro del presupuesto de tiempo disponible.

## 9. Resolución de identidad (entity resolution): determinista frente a probabilística/ML

La fusión de un mismo investigador presente tanto en ORCID como en un CVN
sintético (o en varios documentos CVN) es el núcleo de `HA01`. El estado del
arte de resolución de entidades ofrece, a grandes rasgos, tres familias de
enfoque:

- **Coincidencia determinista por reglas**: se declaran reglas explícitas
  de coincidencia (p. ej., mismo identificador único; si no hay
  identificador, nombre normalizado y afiliación compartida) y se aplican en
  ese orden.
- **Vinculación probabilística de registros** (modelo de Fellegi-Sunter y
  herramientas como Splink): calcula una probabilidad de coincidencia
  combinando múltiples campos con pesos aprendidos o calibrados, útil cuando
  no existe ningún identificador único fiable entre las fuentes.
- **Resolución de entidades basada en aprendizaje automático/embeddings**
  (p. ej. la biblioteca `dedupe`, o enfoques de *deep entity resolution*):
  aprende una función de similitud a partir de ejemplos etiquetados o de
  representaciones vectoriales, útil a gran escala y con datos muy ruidosos.

**Decisión**: coincidencia determinista, ORCID iD en primer lugar y
nombre/afiliación como regla de repliegue (`src/tfm_lakehouse/silver/`,
issue `#98`). Justificación: el ORCID iD es, por diseño, un identificador
global de investigador de baja ambigüedad cuando está presente —el propio
objetivo fundacional de ORCID es desambiguar autores de forma inequívoca—,
lo que hace que un enfoque puramente determinista basado en él sea
suficiente y no necesite el aparato estadístico de la vinculación
probabilística cuando el identificador existe. Para los casos sin ORCID iD
declarado, un enfoque determinista con evidencia explícita por enlace
(`name_match`, `shared_organizations`, ver el issue `#98`) produce
resultados auditables y explicables campo a campo, algo especialmente
valioso en un trabajo académico donde cada decisión debe poder justificarse
ante un tribunal, frente a una puntuación de un modelo de aprendizaje
automático que es más difícil de defender línea a línea con el presupuesto
de tiempo disponible. La medición empírica de este enfoque (precisión 95,8
%, cobertura 74,2 % sobre el conjunto de verdad del generador sintético,
issue `#98`) confirma que, dentro del alcance de datos del proyecto, la
sencillez determinista no sacrificó calidad de forma significativa. La
vinculación probabilística y la resolución basada en aprendizaje automático
quedan documentadas como trabajo futuro explícito en el epic ("ML-based or
probabilistic entity resolution").

## 10. Fuentes de datos: ORCID, sistemas CRIS y la decisión de no usar CVN reales

ORCID se sitúa dentro de un ecosistema más amplio de **sistemas de
información de investigación** (*Current Research Information Systems*,
CRIS), cuyo objetivo es interoperar información curricular, de publicaciones
y de afiliación entre instituciones y financiadores. Dos referencias
habituales de ese ecosistema son **CERIF** (*Common European Research
Information Format*, mantenido por euroCRIS, un modelo de datos común para
interoperabilidad entre sistemas CRIS institucionales) y **VIVO** (una
plataforma CRIS de código abierto basada en ontologías para representar redes
de investigadores). ORCID no es en sí mismo un CRIS completo, sino el
identificador persistente de investigador que numerosos CRIS institucionales
(incluidos los conformes a CERIF) usan como clave de interoperabilidad entre
sistemas —exactamente el papel que cumple en este TFM como clave de fusión
entre el CVN sintético y el registro ORCID real (issue `#96`).

Sobre por qué el CVN no se trató igual que ORCID (fuente real de volumen) y
en su lugar se generó de forma sintética: un CVN completo y real es un
documento de datos personales (identidad, formación, carrera profesional)
que, a diferencia de un perfil ORCID —pensado explícitamente para publicación
pública y control granular del propio investigador sobre su visibilidad—, no
tiene un corpus público legítimo del que obtenerse a volumen; reunir muchos
CVN reales sin consentimiento habría sido un problema de protección de datos
personales genuino para un repositorio público y defendido en abierto en
GitHub. La solución adoptada —generar documentos CVN sintéticos, válidos
frente a `schemas/open_cvn.schema.json`, alimentados con campos públicos
reales de ORCID (nombre, afiliaciones, obras)— resuelve el problema de
volumen sin ese riesgo y, como efecto colateral deseado, crea de forma
natural el enlace por ORCID iD entre el CVN sintético y el registro ORCID
real que la resolución de identidad de la sección 9 necesita como clave. El
issue `#96` documenta además la mitigación adoptada para el resto de campos
de identidad no derivados de ORCID (teléfonos y correos claramente ficticios,
sin DNI ni nacionalidad, marca `metadata.source.synthetic = true` en cada
documento).

Sobre el uso dual de ORCID: la API pública (consultas puntuales por
identificador, usada para demostrar fusión dirigida, `HA01`) y el fichero
público de datos anual (*Public Data File*, usado para volumen real en lugar
de tener que sintetizar también los datos de ORCID) son dos mecanismos
complementarios y oficiales del propio ORCID, no una improvisación del
proyecto; el issue `#94` documenta además un hallazgo relevante para el
estado del arte de esta fuente: el registro de un cliente autenticado de la
API pública de ORCID exige describir la aplicación como una herramienta de
una organización miembro registrada, lo que no encaja con un proyecto
académico personal —una discrepancia con la propia documentación de ORCID
(que indica que particulares pueden tener credenciales de la API pública
independientemente de la membresía), no resuelta más allá de constatarla—,
resuelta usando el nivel anónimo/no autenticado de esa misma API pública.

## 11. Observabilidad y captura del benchmark: registros de Spark frente a Prometheus + Grafana

Un banco de pruebas de rendimiento acotado (issue `#101`) necesita capturar
métricas de ejecución (duración, uso de recursos, número de ejecutores) de
forma reproducible. Las dos vías habituales:

- **Prometheus + Grafana**: pila de observabilidad estándar de facto en
  Kubernetes, con exportadores para Spark y para el propio clúster,
  permitiendo paneles en tiempo real y series históricas.
- **Registros de Spark / exportación del Spark History Server**: cada
  ejecución de Spark ya escribe un registro de eventos detallado
  (duración de etapas, tareas, uso de ejecutores) que el propio Spark
  History Server puede interpretar sin infraestructura adicional.

**Decisión**: registros de Spark / exportación del History Server, sin
desplegar Prometheus+Grafana. Justificación: el benchmark del issue `#101`
es una campaña acotada y no un requisito de monitorización continua en
producción; instalar y configurar una pila de observabilidad completa solo
para capturar los datos de un banco de pruebas puntual no estaba
justificado dentro del presupuesto de 20 días, y el propio registro de
eventos de Spark ya contiene toda la información que la campaña necesitó
(`src/tfm_lakehouse/benchmark/eventlog.py`). Queda documentado como trabajo
futuro explícito en el epic.

## 12. Síntesis

La tabla siguiente recoge, para cada decisión ya resumida en la tabla
"Technology Stack Decision Record" del epic `#89`, cuál fue el motor
principal de la justificación desarrollada en las secciones anteriores.

| Decisión | Alternativa principal descartada | Motor principal de la justificación |
| --- | --- | --- |
| Arquitectura lakehouse | Data warehouse + data lake separados | Alineación directa con `CN02`; presupuesto de tiempo |
| Apache Iceberg | Delta Lake, Apache Hudi | Neutralidad de proveedor; soporte multi-motor; patrón de carga por lotes (no CDC) |
| Catálogo Hadoop | Hive Metastore, catálogo REST, Nessie | Simplicidad operativa; un solo escritor por capa; proporcionalidad a 6 ECTS |
| MinIO | HDFS, S3/GCS/Azure reales | Separación almacenamiento/cómputo demostrable sin coste ni dependencia externa |
| Kubernetes (k3s) | Docker Swarm, despliegue directo | Resultado de aprendizaje del programa; soporte de primera clase en el resto de la pila; portabilidad a multi-nodo/cloud |
| Apache Spark, `spark-submit` sin operador | Apache Flink, Dask/Ray, Spark Kubernetes Operator | Patrón por lotes del proyecto; integración madura con Iceberg; menor superficie operativa |
| Apache Airflow, `KubernetesExecutor` | Prefect, Dagster, Luigi, `CeleryExecutor` | Alineación con `HA03`; despliegue Kubernetes-nativo maduro; sin servicios extra |
| Spark SQL (sin Trino) | Trino/Presto | Proporcionalidad de alcance; no hay necesidad real de consulta interactiva federada |
| Superset sobre PostgreSQL | Metabase, Grafana, BI propietario; conector directo a Iceberg | Postura autoalojada/código abierto; panel como código; sin servicio intermedio adicional |
| Resolución determinista (ORCID iD primero) | Vinculación probabilística, ML/embeddings | Auditabilidad y explicabilidad de cada decisión; ORCID iD como identificador de baja ambigüedad |
| CVN sintético seeded con ORCID real | Recolección de CVN reales a volumen | Ética/privacidad: sin corpus público legítimo de CVN reales |
| Registros de Spark (sin Prometheus/Grafana) | Pila de observabilidad completa | Alcance de un banco de pruebas puntual, no monitorización continua |

## Referencias

Convertidas a entradas BibTeX en `docs/memoria/TFM/bib/ref.bib`, verificadas
contra la fuente primaria de cada una (no solo transcritas de memoria) al
hacerlo; la clave BibTeX de cada referencia se indica entre corchetes.
Correcciones hechas durante esa verificación: la referencia 1 tenía el
título original de Armbrust et al. mal transcrito ("Open Source Systems and
Architecture..." en vez de "Open Platforms that Unify..."), y la 2 no traía
el listado completo de 14 autores ni las páginas exactas; ambas corregidas
aquí contra la fuente (el PDF oficial de CIDR y los metadatos de Crossref,
respectivamente).

1. Armbrust, M., Ghodsi, A., Xin, R., Zaharia, M. (2021). *Lakehouse: A New
   Generation of Open Platforms that Unify Data Warehousing and Advanced
   Analytics*. 11th Annual Conference on Innovative Data Systems Research
   (CIDR '21), 11-15 de enero de 2021, en línea.
   [`armbrust_lakehouse_2021`]
2. Zaharia, M., Xin, R. S., Wendell, P., Das, T., Armbrust, M., Dave, A.,
   Meng, X., Rosen, J., Venkataraman, S., Franklin, M. J., Ghodsi, A.,
   Gonzalez, J., Shenker, S., Stoica, I. (2016). *Apache Spark: A Unified
   Engine for Big Data Processing*. Communications of the ACM, 59(11),
   56-65. [`zaharia_spark_2016`]
3. Apache Software Foundation. Documentación oficial de Apache Iceberg
   (especificación de tabla, catálogos, motores soportados).
   [`apache_iceberg_docs`]
4. Apache Software Foundation. Documentación oficial de Spark sobre
   Kubernetes (programación nativa, integración con Iceberg).
   [`apache_spark_k8s_docs`]
5. Apache Software Foundation. Documentación oficial del proveedor
   `cncf.kubernetes` de Apache Airflow (`KubernetesExecutor`).
   [`apache_airflow_k8s_docs`]
6. Apache Software Foundation. Documentación oficial de Apache Superset.
   [`apache_superset_docs`]
7. Delta Lake Project, Linux Foundation. Documentación oficial de Delta
   Lake OSS. [`delta_lake_docs`]
8. Apache Software Foundation. Documentación oficial de Apache Hudi.
   [`apache_hudi_docs`]
9. Project Nessie. Documentación oficial de Nessie como catálogo
   versionado para Iceberg. [`project_nessie_docs`]
10. K3s Project Authors (originado en Rancher Labs/SUSE). Documentación
    oficial de k3s. [`k3s_docs`]
11. Cloud Native Computing Foundation (CNCF). Página del proyecto
    Kubernetes (graduado en la CNCF desde el 6 de marzo de 2018).
    [`cncf_kubernetes`]
12. MinIO, Inc. Repositorio oficial de MinIO en GitHub (verificado como
    fuente más estable que la documentación web, que en septiembre de 2026
    redirige mayoritariamente a contenido comercial de "AIStor"; el
    repositorio conserva la descripción técnica del proyecto de código
    abierto). [`minio_github`]
13. ORCID. *What Is ORCID?* (documentación pública sobre el proyecto,
    identificador persistente y control de privacidad por el propio
    investigador) [`orcid_about`], y *ORCID Public Data File 2025*
    (DOI `10.6084/m9.figshare.30375589`), cuyo volumen se verificó
    empíricamente en este proyecto: 26\,078\,951 registros escaneados
    (`docs/roadmap/tfm/issues/issue-95-orcid-bulk-data-file-pipeline.md`)
    [`orcid_public_data_file_2025`]. Ver también los hallazgos empíricos
    propios registrados en
    `docs/roadmap/tfm/issues/issue-94-orcid-api-client.md` y
    `docs/roadmap/tfm/issues/issue-95-orcid-bulk-data-file-pipeline.md`.
14. euroCRIS. *Main Features of CERIF (Common European Research Information
    Format)*, modelo de datos común para sistemas de información de
    investigación. [`eurocris_cerif`]
15. VIVO Project. Plataforma CRIS de código abierto basada en ontologías.
    [`vivo_project`]
16. Fellegi, I. P., Sunter, A. B. (1969). *A Theory for Record Linkage*.
    Journal of the American Statistical Association, 64(328), 1183-1210.
    DOI `10.1080/01621459.1969.10501049`. [`fellegi_sunter_1969`]
17. Splink (Ministry of Justice, Reino Unido, Analytical Services).
    Biblioteca de vinculación probabilística de registros como referencia
    del estado del arte en resolución de entidades probabilística.
    [`splink_docs`]
18. `dedupe` (DataMade). Biblioteca de resolución de entidades basada en
    aprendizaje automático activo, como referencia del estado del arte en
    resolución de entidades basada en ML. [`dedupe_docs`]

## Relación con otros documentos

- `docs/roadmap/tfm/issues/issue-89-epic-tfm-lakehouse-platform.md`: tabla
  de decisiones resumida que este documento desarrolla.
- `docs/roadmap/tfm/issues/issue-103-memoria-assembly.md`: issue de la
  memoria que debe citar este documento al redactar el capítulo "Estado del
  arte".
- `docs/pipeline/known_limitations.md`: hallazgos empíricos de
  implementación (sección "Infrastructure Limitations (TFM)" y siguientes)
  que refuerzan o matizan varias de las justificaciones anteriores.
- `docs/context/tfm/current_status.md`: registro de qué issue produjo cada
  hallazgo citado aquí.
