# Capítulo 2: Estado del arte y decisiones arquitectónicas

Estado: `EN_PROCESO`

## Objetivo del capítulo

Construir el marco teórico y tecnológico necesario para entender por qué se
eligió cada componente de la plataforma, comparándolo con las alternativas
reales del ecosistema, y cerrar posicionando la arquitectura adoptada. Es el
capítulo que en el TFG estaba repartido en dos (antecedentes + análisis del
ecosistema); aquí va unido porque el TFM no tiene un "ecosistema de origen"
tan extenso como CVN que analizar por separado.

## Contenido recomendado (ideas principales)

Basado directamente en `docs/research/tfm/estado_del_arte_tfm.md`, que ya
contiene el desarrollo comparativo completo con referencias bibliográficas.
Este capítulo lo resume y lo conecta con las decisiones realmente tomadas
(la tabla "Technology Stack Decision Record" del epic `#89`), no repite el
documento de investigación palabra por palabra.

- **De los sistemas de almacenamiento analítico al lakehouse**: evolución
  data warehouse -> data lake -> lakehouse, qué problema resuelve cada
  transición, por qué el lakehouse es el punto de partida natural para este
  TFM.
- **Formato de tabla**: Apache Iceberg frente a Delta Lake y Apache Hudi;
  por qué Iceberg (gobernanza Apache, soporte multi-motor, semántica real
  de lakehouse) y por qué catálogo Hadoop (basado en rutas) en vez de Hive
  Metastore/REST/Nessie (sin servicio de catálogo adicional que desplegar
  y depurar dentro del presupuesto de tiempo -- en el texto final,
  formulado como coste de operación evitado, no citando el presupuesto).
- **Almacenamiento de objetos**: MinIO frente a HDFS y almacenamiento cloud
  nativo; por qué MinIO (compatible S3, autoalojado, sustrato natural de
  data lake).
- **Sustrato de orquestación de contenedores**: Kubernetes (k3s) frente a
  Docker Swarm y despliegue sin orquestador; por qué k8s (soporte de
  primera clase en todo el resto del stack, habilidad esperada en un
  programa de Big Data y Computación en la Nube).
- **Único nodo local frente a clúster real en la nube** (pendiente de
  redactar; esta es la exposición completa de la decisión, con la
  justificación que debe usarse -- no enmarcarla como una limitación de
  tiempo, sino como una decisión técnica propia de un entorno de
  desarrollo): desplegar sobre una única máquina local durante la fase de
  desarrollo permite construir, probar y depurar la plataforma completa sin
  incurrir en el coste de mantener encendida infraestructura en la nube
  mientras el sistema todavía cambia con frecuencia. La arquitectura no
  depende de esa máquina concreta: todos los servicios se despliegan con
  Helm sobre Kubernetes estándar, sin atajos específicos del entorno local
  salvo los documentados explícitamente (por ejemplo, el backend de red
  `host-gw` de k3s bajo WSL2, ver capítulo 3), de modo que el mismo
  despliegue es replicable sobre un clúster Kubernetes real en la nube
  cambiando la infraestructura subyacente, no la definición de los
  servicios. El paso de una máquina local a un despliegue en la nube queda
  así documentado como una extensión directa, no como un rediseño, y se
  deja como trabajo futuro por quedar fuera del alcance evaluado en este
  documento.
- **Procesamiento distribuido**: Apache Spark frente a Flink y Dask/Ray;
  `spark-submit` en modo Kubernetes lanzado desde Airflow, frente al Spark
  Kubernetes Operator (evita instalar y operar CRDs adicionales).
- **Orquestación de flujos ETL**: Apache Airflow (`KubernetesExecutor`)
  frente a Prefect, Dagster y Luigi; por qué evita levantar Celery+Redis
  como servicios adicionales.
- **Capa de consulta interactiva**: por qué se decide *no* incluir Trino
  (recorte de alcance explícito, documentado como trabajo futuro) y usar
  solo Spark SQL.
- **Capa de BI**: Apache Superset conectado a PostgreSQL, frente a Superset
  conectado directamente a Iceberg/Spark vía Trino o Spark Thrift Server;
  por qué materializar en PostgreSQL como último paso de publicación evita
  necesitar una capa de consulta interactiva solo para el panel.
- **Resolución de identidad**: determinista (basado en reglas y evidencia)
  frente a probabilística/ML; por qué determinista es proporcionado al
  alcance y auditable, con sus límites de precisión/recall explícitos.
- **Fuentes de datos**: ORCID y el ecosistema CRIS (Current Research
  Information Systems) como contexto; la decisión, deliberada, de no
  recolectar CVN reales a volumen por motivos de privacidad, y en su lugar
  generar CVN sintéticos sembrados con datos ORCID reales.
- **Observabilidad y captura del benchmark**: registros de Spark / Spark
  History Server frente a Prometheus + Grafana; por qué no se monta un
  stack de observabilidad completo para un benchmark acotado.
- **Síntesis final**: tabla-resumen de todas las decisiones con la
  alternativa rechazada y el motivo (reutilizable directamente de la tabla
  "Technology Stack Decision Record" del epic, adaptada a prosa académica).

## Elementos recomendados

- Tabla de decisión tecnológica completa (componente elegido / alternativas
  rechazadas / motivo), la pieza central del capítulo.
- Posible diagrama de la arquitectura lakehouse genérica (bronze/silver/gold)
  antes de particularizarla al caso propio en el capítulo 3.
- Tabla comparativa Iceberg/Delta/Hudi (ya desarrollada en la sección 2 del
  documento de estado del arte, puede reutilizarse adaptada).

## Outcomes de aprendizaje cubiertos

`CN02`, `CP01`.

## Fuentes principales

- `docs/research/tfm/estado_del_arte_tfm.md` (documento completo, fuente
  primaria de este capítulo)
- `docs/roadmap/tfm/issues/issue-89-epic-tfm-lakehouse-platform.md`,
  sección "Technology Stack Decision Record"

## Estado de redacción

Primer borrador redactado en `docs/memoria/TFM/chapters/ch2.tex`, siguiendo
el estilo mapi y revisado con `elimina-marcas-ia` (se corrigieron 18
incisos con doble guion `--...--` y tres construcciones "no X sino Y"
acumuladas, ninguna de ellas presente en el estilo del TFG de referencia).

La justificación del despliegue en un único nodo local frente a un clúster
real en la nube, pendiente desde el capítulo 1, se redactó en la Sección
"Sustrato de orquestación de contenedores y entorno de despliegue" con el
argumento acordado: coste evitado durante el desarrollo activo y
reproducibilidad directa hacia un despliegue en la nube real, sin mencionar
presupuesto de tiempo ni ECTS. Todas las demás justificaciones que en el
documento de investigación se apoyaban en "presupuesto de tiempo" o "20
días" se reformularon en el capítulo final por proporcionalidad de alcance,
manteniendo esas cifras solo en esta guía y en `estado_del_arte_tfm.md`.

**Segunda revisión, a partir de comentarios del usuario tras leer el
primer borrador**: reestructuración sustancial, no solo de estilo.

- El estado del arte se reorganizó de párrafos densos que comparaban varias
  tecnologías a la vez (difíciles de seguir) a un párrafo propio por
  alternativa -- definición, cita, punto fuerte, límite frente al proyecto
  --, siguiendo el mismo patrón que usa `docs/memoria/TFG/chapters/ch2.tex`
  para CERIF/VIVO/ROH o para XML/JSON/JSON-LD: no listas con viñetas, sino
  prosa desarrollada, una idea por párrafo, cerrada con una tabla de
  síntesis.
- La sección de formato de tabla (Iceberg/Delta/Hudi) se reescribió por
  completo: cada justificación explica ahora qué aporta técnicamente cada
  propiedad (particionado oculto, *snapshot isolation*, etc.) y por qué le
  importa a este proyecto en concreto, no solo el nombre de la propiedad.
- Las tres secciones que trataban decisiones de *estrategia de desarrollo*
  en vez de arquitectura de plataforma -- resolución de identidad, fuentes
  de datos (ORCID/CVN), observabilidad -- se retiraron de este capítulo por
  indicación explícita del usuario y se trasladaron como borrador de
  partida a las guías de los capítulos donde sí corresponden:
  `ch5_procesamiento_distribuido.md` (resolución de identidad),
  `ch4_ingesta_fusion_datos.md` (fuentes de datos) y
  `ch6_visualizacion_evaluacion_endurecimiento.md` (observabilidad). El
  capítulo quedó en ocho secciones (lakehouse; formato de tabla e Iceberg
  con su catálogo; almacenamiento de objetos; orquestación de contenedores
  y entorno de despliegue, con su subsección de red; procesamiento
  distribuido; orquestación ETL; consulta interactiva y visualización;
  síntesis), y la tabla de síntesis final se recortó a juego.
- Se añadieron 15 entradas nuevas a `docs/memoria/TFM/bib/ref.bib`
  (verificadas contra su fuente oficial, igual que las anteriores) para que
  toda tecnología mencionada -- incluidas las alternativas descartadas:
  HDFS, Hive Metastore, Docker Swarm, Flink, Dask, Ray, el *Spark
  Kubernetes Operator*, Prefect, Dagster, Luigi, Trino, Grafana, Power BI,
  Tableau, Metabase -- quede referenciada, no solo las opciones finalmente
  adoptadas.
- Corrección de plantilla, aplicable a todos los capítulos futuros:
  `docs/memoria/TFM/include/configuracion.tex` ganó `\usepackage{float}`
  (para el especificador `[H]`, que fija la posición de una tabla corta en
  vez de dejarla flotar lejos de su primera mención), `\clubpenalty`/
  `\widowpenalty` a 10000 (evita líneas viudas/huérfanas) y `\raggedbottom`
  (evita que esa restricción de viudas/huérfanas fuerce huecos verticales
  enormes entre párrafos al intentar rellenar la página hasta el margen).
  Verificado visualmente, extrayendo las páginas del PDF compilado antes y
  después de cada cambio.

**Tercera revisión, recorte de extensión**: con capítulos 1-2 redactados,
el cuerpo del documento ya ocupaba ~20 páginas de las 50 permitidas; el
usuario pidió resumir. Este capítulo era el más expandible (revisión
comparativa de tecnología, no resultados propios), así que absorbió la
mayor parte del recorte: de ~13 a ~8 páginas de cuerpo. Método: mismo
párrafo-por-alternativa que exigió la revisión anterior, pero cada
párrafo más corto (una propiedad técnica destacada en vez de tres,
explicaciones parentéticas más breves); la subsección "Modo de red en el
entorno de desarrollo" se plegó dentro del párrafo de la decisión de k3s
en vez de mantenerse como subsección propia; los párrafos de "opción
adoptada" se redujeron a una frase de conclusión en vez de reexplicar la
comparación ya hecha. Ninguna alternativa, cita ni tabla se eliminó: solo
se comprimió la prosa. Verificado que el recorte no reintrodujo problemas
de estilo (`--...--`, "no X sino Y" acumulado) ni de composición
(viudas/huérfanas, tablas mal situadas).

**Cuarta revisión**: el usuario pidió usar enumeraciones en puntos
separados (`itemize`) en vez de enumerar varias alternativas dentro de una
misma frase o párrafo. Convertidas a `itemize` las comparaciones sin tabla
propia: catálogo de Iceberg (4 opciones), sustrato de orquestación de
contenedores (3), motor de procesamiento distribuido (3), orquestador ETL
(4) y capa de visualización (4). Las dos comparaciones que ya tenían tabla
dedicada (formato de tabla; síntesis final) se dejaron en prosa breve, ya
que la tabla cumple ahí el mismo papel de separar cada opción. Al hacerlo
se encontró y corrigió un error real: varias entradas `~\cite{...}` dentro
de los nuevos `\item` no podían partir de línea por el espacio irrompible
(`~`), y con las citas largas de `{Apache Software Foundation}` (p. ej.
`[Apache Software Foundation, 2026h]`) esto producía una línea que se
salía del margen casi 4,5\,cm en la sección de Spark; se sustituyó
`~\cite{` por `\space\cite{` (espacio normal) en todo el capítulo, no solo
en el punto afectado, para no dejar el mismo riesgo en el resto de citas.
Verificado visualmente tras el cambio: ninguna otra línea se sale del
margen. El cuerpo pasó de ~14 a ~16 páginas por el espaciado propio de
`itemize`, un coste aceptado explícitamente a cambio de la claridad
pedida.

**Quinta revisión**: el título de la Sección 2.8 ("Síntesis y arquitectura
resultante") quedaba huérfano al final de una página, con la Tabla 2.2
(posicionada con `[H]`) empezando sola en la página siguiente. Corregido
añadiendo `\usepackage{needspace}` a
`docs/memoria/TFM/include/configuracion.tex` (a nivel de plantilla, para
cualquier capítulo futuro) y `\Needspace{9cm}` justo antes de esa sección,
de forma que si no cabe el título más la tabla completa, el salto de
página ocurre antes del título, no después. Verificado visualmente.

**Sexta revisión, puntuación y frase**: aplicadas las tres reglas nuevas
que el usuario pidió tras leer el capítulo 3, recogidas en
`estructura_memoria_tfm.md`: sin paréntesis en ningún punto del texto
(las definiciones de sigla se reformularon con «en adelante»/«siglas
de», los incisos técnicos se integraron en la frase o se convirtieron en
frases nuevas más cortas), sin punto y coma (sustituidos por punto y
frase nueva), y sin mencionar que una decisión "ya fue justificada" en
otra sección, dado que el lector ya lo sabe con la sola referencia
cruzada. Revisión también de comas en frases con varias cláusulas.
Verificado que la reescritura no reintrodujo el patrón de cita `~\cite{}`
sin punto de ruptura de línea, y se corrigieron dos casos que sí
reaparecieron al reescribir dos incisos de `itemize` de las secciones de
Spark y Airflow.

Pendiente, no bloqueante: las referencias cruzadas a los capítulos 3-7
(`cap:infraestructura`, `cap:ingesta`, `cap:procesamiento`,
`cap:visualizacion`) quedarán sin resolver hasta que esos capítulos existan
con su propio `\label`.
