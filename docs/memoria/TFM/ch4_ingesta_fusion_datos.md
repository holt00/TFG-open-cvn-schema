# Capítulo 4: Ingesta y fusión de fuentes heterogéneas

Estado: `EN_PROCESO`

## Objetivo del capítulo

Explicar cómo se adquieren, generan y aterrizan en bronze las dos fuentes de
datos del sistema (ORCID real y CVN sintético), y cómo se prepara desde el
aterrizaje mismo la fusión posterior entre ellas. Es el capítulo que
demuestra de forma más directa la adquisición y fusión de múltiples
fuentes.

## Contenido recomendado (ideas principales)

- **Doble mecanismo ORCID, explicado como decisión deliberada, no como dos
  features sueltas**: API pública (consultas puntuales, límite de tasa,
  usada para enriquecimiento dirigido) y fichero público masivo anual
  (volumen real, filtrado a un subconjunto manejable por afiliación en
  España). El capítulo debe justificar por qué se necesitan los dos y no
  solo uno: el API da profundidad por identificador, el fichero masivo da
  volumen real distribuible.
- **Por qué CVN sintético y no CVN real a volumen**: nota ética/privacidad
  ya introducida en el capítulo 1, desarrollada aquí con el mecanismo
  concreto -- currículos generados, válidos contra el esquema Open CVN
  oficial, sembrados con campos públicos reales tomados del subconjunto
  ORCID (nombre, afiliaciones, obras), de forma que una parte declara el
  mismo identificador ORCID que su semilla real. Ese enlace deliberado es
  la clave de unión que necesita la resolución de identidad del capítulo
  5: no es un efecto colateral, es el mecanismo de fusión diseñado desde el
  origen de los datos.
- **Aterrizaje en bronze con procedencia**: cada registro aterrizado lleva
  un sobre de procedencia (fuente, fecha de ingesta, identificador de
  ejecución); los registros que no superan una comprobación básica de
  calidad se separan a una zona de rechazados en vez de descartarse, con un
  umbral de tolerancia por ejecución.
- **Orquestación de la ingesta**: un único flujo de Airflow encadena las
  cuatro tareas (obtención del subconjunto ORCID masivo, generación de CVN
  sintético, enriquecimiento vía API, validación y aterrizaje), en el orden
  que exige la dependencia real entre ellas (el enriquecimiento necesita
  los identificadores ORCID que los CVN sintéticos ya declaran).
- **Calidad de datos proporcionada al alcance**: reutilización deliberada
  del validador Open CVN del TFG para el lado CVN (sin construir una
  librería de calidad de datos nueva), y comprobaciones basadas en reglas
  simples para el lado ORCID (campos obligatorios presentes, dígito de
  control del identificador ORCID válido).

## Elementos recomendados

- Diagrama de flujo de la ingesta: las cuatro tareas, sus dependencias y el
  aterrizaje en bronze.
- Tabla de las dos fuentes con su mecanismo, volumen típico y campo de
  enlace usado por la resolución de identidad.
- Fragmento de un registro de procedencia (simplificado) como ejemplo de
  código.

## Outcomes de aprendizaje cubiertos

`HA01` (principal), `CN02` (parcial: aterrizaje bronze).

## Fuentes principales

- issues `#94` (cliente API ORCID), `#95` (pipeline ORCID masivo), `#96`
  (generador CVN sintético), `#97` (aterrizaje bronze + DAG de ingesta)
- sección 10 (y parcialmente 9) de `docs/research/tfm/estado_del_arte_tfm.md`

## Estado de redacción

Sin empezar. Los cuatro issues fuente están completados; hay cifras reales
de volumen ya medidas (tamaño del subconjunto ORCID filtrado, tasa de
rechazo del aterrizaje) que deben verificarse contra el estado actual del
repositorio antes de citarse, no asumirse de esta guía.

Borrador de partida disponible: la sección "Fuentes de datos: ORCID real y
CVN sintético" se redactó inicialmente dentro del capítulo 2, pero el
usuario indicó que la estrategia concreta de ingesta/fusión de fuentes
corresponde a este capítulo, no al estado del arte de la plataforma; se
retiró de `docs/memoria/TFM/chapters/ch2.tex` y se deja aquí como texto de
partida, pendiente de adaptar:

> ORCID se sitúa dentro de un ecosistema más amplio de sistemas de
> información de investigación (CRIS). ORCID no es en sí mismo un CRIS
> completo; dentro de ese ecosistema, funciona como el identificador
> persistente de investigador que numerosos CRIS institucionales,
> incluidos los conformes a CERIF~\cite{eurocris_cerif}, usan como clave
> de interoperabilidad entre sistemas: exactamente el papel que cumple en
> este trabajo como clave de fusión entre el CVN sintético y el registro
> ORCID real. El uso de ORCID combina dos mecanismos complementarios y
> oficiales del propio proyecto ORCID, no una improvisación de este
> trabajo: la API pública, para consultas puntuales por identificador que
> demuestran fusión dirigida entre fuentes, y el fichero público de datos
> anual, usado como fuente de volumen real en lugar de tener que
> sintetizar también los datos de ORCID. Durante la implementación se
> constató una discrepancia entre la documentación pública de la API y su
> proceso de registro real: registrar una aplicación cliente exige
> describirla como herramienta de una organización miembro, lo que no
> encaja de forma directa con un proyecto académico personal; se resolvió
> empleando el nivel anónimo de esa misma API pública, sin que ello
> afectase a la demostración de fusión dirigida prevista.
>
> La decisión de generar el CVN de forma sintética, en lugar de tratarlo
> igual que ORCID como fuente de volumen real, se justificó ya por motivos
> de privacidad en el Capítulo 1: un currículo completo y real es
> información personal sin un corpus público legítimo del que obtenerse a
> volumen, a diferencia de un perfil ORCID, pensado explícitamente para
> publicación pública con control granular del propio investigador sobre
> su visibilidad~\cite{orcid_about}. La solución adoptada, generar
> documentos CVN sintéticos sembrados con campos públicos reales de ORCID,
> resuelve el problema de volumen sin ese riesgo y crea, como efecto
> colateral deseado, el enlace por identificador ORCID que la resolución
> de identidad (Capítulo 5) necesita como clave.

Pendiente al integrar este borrador: convertir "Capítulo 1"/"Capítulo 5" en
`\ref{cap:introduccion}`/`\ref{cap:procesamiento}`, y desarrollarlo con el
detalle propio de este capítulo (doble mecanismo ORCID, generación
sintética, aterrizaje en bronze) en vez de dejarlo al nivel resumido en que
se escribió para el capítulo 2.

## Historial de redacción

Redactado el capítulo completo en `docs/memoria/TFM/chapters/ch4.tex` a
partir de los issues `#94`-`#97`, verificados en detalle contra el propio
texto de cada issue antes de citar ninguna cifra, no asumidos de esta guía.
El borrador de partida se reescribió con el nivel de detalle propio de este
capítulo en lugar de integrarse literalmente, y se descartó el marco de
"CRIS/CERIF" que traía ese borrador, sin uso propio en este capítulo, para
no forzar un encaje conceptual que el capítulo 2 ya no necesita mantener.

Estructura final, cinco secciones: arquitectura de la ingesta, con la razón
del orden de las cuatro tareas del flujo de Airflow y la razón del pod
dedicado por tarea; adquisición de datos de ORCID, con el doble mecanismo
en `itemize` y las cifras reales del filtrado del fichero masivo; generación
de currículos CVN sintéticos, con el enlace deliberado por identificador
ORCID como clave de fusión y el hallazgo real de la validación en dos capas,
que descartó 179 de 200 documentos en la primera ejecución de prueba;
aterrizaje en bronze con procedencia, con el sobre de procedencia, la zona
de rechazados con su umbral y la decisión de aterrizar el fichero masivo una
sola vez por instantánea; verificación de extremo a extremo, con el mismo
patrón de doble comprobación del capítulo 3 y el hallazgo real sobre la
lectura de Spark que forzó la limpieza de una ejecución fallida.

Todas las cifras citadas se tomaron directamente de las secciones
`Verification`/`Findings`/`Adjustments Made During Implementation` de los
issues `#94`-`#97`, no de memoria. Bibliografía añadida: `orcid_public_api_docs`,
`figshare_docs`, `json_schema_org`, los tres nuevos para este capítulo.

Compilación verificada con `xelatex` + `bibtex` + `xelatex` ×2: sin cajas
`Overfull`/`Underfull` propias del capítulo, sin citas sin definir. Dos
correcciones de compilación durante la redacción, mismo patrón de error que
en los capítulos 1-3: una cita pegada al final de una etiqueta en negrita al
inicio de un ítem de `itemize` desbordó la caja por 7,9 puntos, y el primer
intento de solución, que dejaba dos citas seguidas sin palabras de por
medio, la empeoró a 211-230 puntos porque el nombre de autor de la nueva
entrada `figshare_docs` estaba protegido entre llaves dobles como una
cadena larga e indivisible. Solución definitiva: separar cada cita en su
propia frase, con palabras de sobra alrededor, y acortar el nombre de autor
de `figshare_docs` a `{{Figshare}}`, igual de corto que el resto de nombres
de organización ya usados en la bibliografía.

El capítulo ocupa aproximadamente 7 páginas de cuerpo, en línea con el
presupuesto restante de la memoria repartido entre los capítulos 4-7.

**Diagrama y tablas añadidos con TikZ**: a petición del usuario, que pidió
analizar en qué capítulos un diagrama o una tabla aclararían mejor el
texto que la prosa sola. Añadidos tres elementos:

- Figura 4.1, en la Sección 4.1, el orden de las cuatro tareas del flujo
  `ingest_validate`, con la dependencia entre la generación de CVN
  sintético y el enriquecimiento por API rotulada sobre la propia flecha
- Tabla 4.1, en la Sección 4.2, resume los dos mecanismos de ORCID
  (mecanismo, uso, volumen, límite de tasa), complementando el `itemize`
  existente en vez de sustituirlo, tal y como se recomendaba en la guía de
  este capítulo desde su redacción inicial
- Tabla 4.2, en la Sección 4.4: la frase que enumeraba los siete campos
  del sobre de procedencia dentro de una misma oración tenía exactamente
  el mismo problema que el usuario señaló dos veces en el capítulo 5, no
  detectado hasta esta revisión. Convertida a tabla en lugar de `itemize`
  porque son nombres de campo con su significado, un caso más tabular que
  enumerativo

La primera versión del diagrama del flujo tenía un problema de
composición: la etiqueta de tres líneas sobre la flecha entre
`generate_synthetic_cvn` y `fetch_orcid_api_enrichment` se solapaba con
las dos cajas adyacentes, porque la separación vertical entre esos dos
nodos era demasiado pequeña para el texto de la etiqueta. Corregido
ampliando esa separación de forma específica para ese par de nodos,
verificado visualmente extrayendo la página a imagen antes de darlo por
bueno.

Con estas adiciones y las del capítulo 3, el cuerpo del documento pasa de
35 a 39 páginas tras cinco capítulos, dejando unas 11 páginas para los
capítulos 6 y 7 dentro del límite de 50.
