# Capítulo 5: Procesamiento distribuido: transformación, resolución de entidades e indicadores

Estado: `EN_PROCESO`

## Objetivo del capítulo

Describir la parte computacionalmente más densa del sistema: cómo bronze se
valida y normaliza a silver, cómo se resuelve la identidad de una misma
persona entre las dos fuentes, y cómo silver se agrega a los indicadores de
gold que después se publican. Es el capítulo donde más se demuestra el
procesamiento distribuido y la orquestación ETL.

## Contenido recomendado (ideas principales)

- **Bronze -> silver, validación por fuente**: cada fuente (CVN, ORCID
  masivo, ORCID API) se valida con sus propias reglas antes de normalizarse
  a una forma común; el lado CVN reutiliza el contrato de parser/validador
  del TFG en vez de reimplementar validación.
- **Resolución de identidad, presentada como lo que realmente es: una
  decisión de diseño con límites medidos, no un algoritmo mágico**:
  determinista, en dos reglas por orden de fuerza de evidencia -- primero
  identificador ORCID compartido (evidencia fuerte), después coincidencia
  de nombre y afiliación normalizados (evidencia más débil, con al menos
  una relajación de nombre permitida y organización igual tras
  normalización). Debe presentarse el resultado medido contra un conjunto
  de verdad de referencia generado por el propio sistema (precisión y
  cobertura, con sus cifras exactas verificadas en el momento de
  redactar), y explicar honestamente qué error queda (falsos positivos por
  homónimos con una organización compartida) y por qué no se sube a un
  95%+ artificialmente.
- **Por qué determinista y no un modelo de aprendizaje automático**:
  proporcionalidad al alcance, auditabilidad de cada enlace (cada decisión
  de fusión lleva su propia evidencia), y el volumen de datos del TFM no
  justifica entrenar y validar un modelo por separado.
- **Silver -> gold: cálculo de indicadores de investigación** (número
  reducido, dos o tres, elegido deliberadamente pequeño): publicaciones por
  investigador y año, línea temporal de afiliaciones, pares de colaboración
  detectados por coautoría. Cada indicador debe presentarse con su
  limitación de validez explícita (por ejemplo: colaboración solo
  detectable cuando ambas partes comparten el mismo identificador de obra).
- **Publicación atómica a PostgreSQL**: tablas de staging más un
  intercambio atómico de nombres, para que el panel de BI nunca vea una
  tabla a medio publicar ni un estado intermedio de una ejecución en curso.
- **Reconstrucción completa en cada ejecución, no incremental**: decisión
  deliberada de simplicidad frente a procesamiento incremental, aceptada
  como limitación de escalabilidad, con su coste medido (tiempo de
  ejecución del capítulo 6).
- **Orquestación en cadena**: un único flujo de Airflow encadena
  transformación, cálculo de indicadores y publicación, con parámetros
  explícitos (número de ejecutores, memoria, particiones de mezcla) que el
  capítulo 6 usa como variable del benchmark.

## Elementos recomendados

- Diagrama de las tres etapas (bronze->silver, silver->gold, publicación) con
  entrada, salida y tecnología de cada una.
- Tabla de resultados de la resolución de identidad (precisión, cobertura,
  tamaño del conjunto de evaluación), con cifras verificadas al redactar.
- Tabla de los indicadores de gold con su definición y su limitación de
  validez.
- Fragmento de código o pseudocódigo del intercambio atómico de tablas.

## Outcomes de aprendizaje cubiertos

`HA02`, `HA03` (principales), `HA01` (parcial: la propia resolución de
identidad es el resultado de la fusión).

## Fuentes principales

- issues `#98` (validación y resolución de identidad), `#99` (indicadores y
  publicación)
- secciones 5, 6, 9 de `docs/research/tfm/estado_del_arte_tfm.md`

## Estado de redacción

Sin empezar. Las cifras de precisión/cobertura de la resolución de
identidad y los recuentos de las tablas gold están ya medidos en el issue
`#98`/`#99`; deben re-verificarse contra el estado real del repositorio
antes de citarse en la memoria, siguiendo el mismo criterio que aplicó el
TFG en su capítulo 5.

Borrador de partida disponible: la sección "Resolución de identidad entre
fuentes" se redactó inicialmente dentro del capítulo 2, pero el usuario
indicó que esa decisión de estrategia (determinista frente a
probabilística/ML) corresponde a este capítulo, no al estado del arte de
la plataforma; se retiró de `docs/memoria/TFM/chapters/ch2.tex` y se deja
aquí como texto de partida, pendiente de adaptar (referencias cruzadas,
cifras reales verificadas, integración con el resto del capítulo):

> Fusionar el registro de un mismo investigador presente tanto en ORCID
> como en un documento CVN es el núcleo del problema de integración
> planteado en el Capítulo 1. El estado del arte de la resolución de
> entidades ofrece, a grandes rasgos, tres familias de enfoque: la
> coincidencia determinista por reglas explícitas (por ejemplo, un
> identificador único compartido y, en su ausencia, nombre normalizado y
> afiliación compartida), la vinculación probabilística de registros
> (formalizada por Fellegi y Sunter~\cite{fellegi_sunter_1969} y
> disponible en herramientas como Splink~\cite{splink_docs}), que calcula
> una probabilidad de coincidencia combinando múltiples campos con pesos
> calibrados, y la resolución basada en aprendizaje automático o
> representaciones vectoriales (disponible, por ejemplo, en la biblioteca
> `dedupe`~\cite{dedupe_docs}), que aprende una función de similitud a
> partir de ejemplos etiquetados.
>
> La opción adoptada es la coincidencia determinista, con el identificador
> ORCID en primer lugar y nombre/afiliación normalizados como regla de
> repliegue cuando dicho identificador no está declarado. El identificador
> ORCID es, por diseño, un identificador global de investigador de baja
> ambigüedad cuando está presente: desambiguar autores de forma inequívoca
> es precisamente el objetivo fundacional de ORCID, lo que hace
> innecesario el aparato estadístico de la vinculación probabilística
> cuando dicho identificador existe. Para los casos sin identificador
> declarado, un enfoque determinista con evidencia explícita por tipo de
> enlace produce resultados auditables y explicables campo a campo, una
> propiedad especialmente valiosa en un trabajo académico donde cada
> decisión debe poder justificarse de forma directa, frente a una
> puntuación de un modelo de aprendizaje automático que resulta más
> difícil de defender línea a línea. [cifras de precisión/cobertura reales
> del issue #98 van aquí, verificadas al redactar] La vinculación
> probabilística y la resolución basada en aprendizaje automático quedan
> documentadas como trabajo futuro.

Pendiente al integrar este borrador: citar las cifras reales de
precisión/cobertura (el párrafo de origen las dejaba como marcador),
convertir la referencia a "Capítulo 1" en `\ref{cap:introduccion}`, y
comprobar que `fellegi_sunter_1969`, `splink_docs` y `dedupe_docs` (ya en
`docs/memoria/TFM/bib/ref.bib`) se citan por primera vez aquí y no quedan
duplicados si algún capítulo anterior los menciona de pasada.

## Historial de redacción

Redactado el capítulo completo en `docs/memoria/TFM/chapters/ch5.tex` a
partir de los issues `#98` y `#99`, releídos en su totalidad antes de
citar ninguna cifra, incluidas sus secciones `Adjustments Made During
Implementation`/`Verification`/`Findings`, no solo el resumen inicial.
El borrador de partida sobre resolución de identidad se integró
reescrito, con las cifras reales sustituyendo el marcador que dejaba, y
la referencia a "Capítulo 1" convertida en `\ref{cap:introduccion}`.

Estructura final, cinco secciones: arquitectura de la transformación
(los tres trabajos de Spark encadenados en `transform_publish`, la
restricción de Python 3.10 del entorno de Spark), validación y
normalización de bronze a silver (las tres capas de validación CVN, la
validación ORCID, la normalización de nombres y organizaciones), resolución
de identidad entre fuentes (las tres familias del estado del arte citadas,
las tres reglas R1/R2/R3, las cifras reales medidas contra el conjunto de
verdad de referencia sintético, y por qué la precisión del 95,8% se
retiene como el límite honesto del diseño en lugar de perseguir
artificialmente el objetivo inicial del 99%), cálculo de indicadores y
publicación en PostgreSQL (la deduplicación de publicaciones necesaria
antes de contarlas, la comprobación previa del indicador de colaboración,
el mecanismo de tablas de preproducción e intercambio atómico verificado
matando el proceso de publicación a mitad de carga), y verificación de
extremo a extremo (el mismo patrón de doble comprobación de los capítulos
anteriores, más la comprobación de sensibilidad de los indicadores a los
errores conocidos de la resolución de identidad).

Bibliografía: los tres citas del borrador de partida,
`fellegi_sunter_1969`, `splink_docs` y `dedupe_docs`, se usan aquí por
primera vez en la memoria, sin duplicados en capítulos anteriores. Se
corrigió proactivamente la entrada `splink_docs` en
`docs/memoria/TFM/bib/ref.bib` antes de citarla: su campo de autor tenía
un nombre largo con paréntesis dentro de llaves dobles, el mismo patrón
que causó el desbordamiento de 211-230 puntos del capítulo 4 con la cita
de Figshare. Se acortó a `{{UK Ministry of Justice}}`, igual de corto que
el resto de nombres de organización ya usados en la bibliografía, antes
de que el problema pudiera reaparecer.

Un desbordamiento de caja de 99,6 puntos apareció en la primera
compilación, no por una cita sino por tres nombres de trabajo en
`\texttt{}` con guion bajo encadenados en una misma frase sin ninguna
palabra de por medio entre ellos. Se corrigió repartiendo los tres
nombres en frases separadas, una por trabajo, en lugar de todos juntos en
una enumeración dentro de la misma frase.

Compilación verificada con `xelatex` + `bibtex` + `xelatex` ×2, en ese
orden: la primera compilación de esta sesión se hizo con `bibtex` antes
del primer `xelatex`, lo que dejó las tres citas nuevas como no definidas
porque el fichero `.aux` todavía no las conocía. Repetido en el orden
correcto, sin cajas `Overfull`/`Underfull` propias del capítulo y sin
citas sin definir. El capítulo ocupa unas 7 páginas de cuerpo, y el total
del documento queda en 35 páginas de cuerpo tras cinco capítulos, dentro
del presupuesto restante de la memoria para los capítulos 6 y 7.

**Revisión de enumeraciones**: el usuario señaló que la sección 5.2 volvía
a caer en enumeraciones largas dentro de la misma frase, el mismo patrón
ya corregido en el capítulo 2. Se convirtieron a `itemize` las tres capas
de validación del documento CVN y los dos frentes de normalización,
manteniendo la validación de ORCID, el umbral de rechazo y las cifras de
cierre como prosa porque no son una enumeración paralela. Recompilado sin
cajas nuevas y con el número de páginas del documento sin cambios.

**Mismo problema en 5.3, más diagramas y tablas donde aclaran el texto**:
el usuario señaló que la sección 5.3 tenía el mismo problema de
enumeraciones largas, y pidió además que, en cualquier punto de la
memoria donde ayude a aclarar un concepto, se añadan tablas o diagramas,
con una tecnología de diagramas fiable y estéticamente cuidada, avisando
de cualquier cambio de este tipo.

- se convirtieron a `itemize` las tres familias de enfoque de resolución
  de entidades y las tres reglas R1/R2/R3, antes en dos párrafos densos
- tecnología de diagramas elegida: TikZ, ya cargado transitivamente en la
  plantilla a través de `todonotes` pero ahora declarado explícitamente en
  `docs/memoria/TFM/include/configuracion.tex` junto con las librerías
  `positioning`, `arrows.meta`, `shapes.geometric` y `calc`. Se descartó
  PlantUML, la tecnología que usa la memoria del TFG para sus diagramas
  conceptuales, porque el binario `plantuml` no está instalado en este
  entorno y instalarlo exigiría `sudo` o descargar un `.jar` externo. TikZ
  no necesita ninguna herramienta nueva, compila en la misma pasada de
  `xelatex` que el resto del documento, y hereda automáticamente la
  paleta de colores ya definida en `include/colores.tex`
- se añadió la Figura 5.1, un diagrama de flujo de decisión con TikZ que
  resume visualmente el orden R1 -> R2 -> R3, y la Tabla 5.1, que resume
  en forma tabular las cifras de precisión y cobertura que antes solo
  aparecían dispersas en el texto corrido
- verificado visualmente extrayendo las páginas 56 y 57 del PDF compilado
  a imagen: el diagrama y la tabla se renderizan con claridad, con el
  mismo esquema de color azul/gris del resto de la memoria
- corregidos dos problemas de compilación al añadir el contenido nuevo:
  una cita pegada a una etiqueta en negrita dentro de un `itemize` volvió
  a desbordar la caja, esta vez de forma persistente pese a separar la
  cita en su propia frase y a quitar el espacio no divisible antes de
  `\cite{}`. Se resolvió con `\sloppy` aplicado localmente a ese
  `itemize`, el mecanismo estándar de LaTeX para estas cajas
  particularmente tercas. La cabecera «Cobertura» de la tabla también
  desbordaba por una columna demasiado estrecha, corregida ampliándola, y
  la columna «Evidencia» mostraba un espaciado feo por justificación en
  una columna estrecha, corregida con `\raggedright` en esa columna
- el usuario señaló además, en un mensaje aparte, un uso excesivo y a
  veces ambiguo de pronombres posesivos y demostrativos en el capítulo 5.
  Se revisaron todos los usos de «su», «sus», «esta», «ese» y «ella» del
  capítulo y se sustituyeron por el sustantivo explícito los que no
  ataban con claridad a su antecedente, entre ellos «su memoria» de los
  ejecutores, «su necesidad» del mecanismo de validación por entidad,
  «sus reglas» de los registros de ORCID, «su clave de bloqueo» del CVN
  de la regla R2, y el pronombre suelto «ella» al final del párrafo sobre
  el coste de una fusión equivocada. Regla añadida a la sección
  "Principios de redacción" de `estructura_memoria_tfm.md`, aplicable al
  resto de capítulos
- se corrigió también una frase confusa en la sección 5.4 sobre la
  deduplicación de publicaciones, señalada aparte por el usuario, dividida
  en dos frases más cortas y directas
- recompilado con `xelatex` + `bibtex` + `xelatex` ×2 tras cada corrección:
  sin cajas `Overfull`/`Underfull` propias del capítulo, sin citas sin
  definir, cuerpo del documento sin cambios en 35 páginas tras cinco
  capítulos, el diagrama y la tabla nuevos no empujaron ninguna sección a
  una página adicional
