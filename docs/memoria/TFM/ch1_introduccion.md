# Capítulo 1: Introducción, motivación y objetivos

Estado: `EN_PROCESO`

## Objetivo del capítulo

Presentar el problema que aborda el TFM, justificar su motivación, delimitar
el alcance y fijar los objetivos que se retomarán en las conclusiones
(capítulo 7). Es el capítulo que sitúa el trabajo dentro del Máster en Big
Data y Computación en la Nube, distinto del encuadre del TFG en Computación.

## Contenido recomendado (ideas principales)

- **Contexto y continuidad con el TFG**: el TFM no repite ni sustituye el
  TFG, construye sobre su entrega ya cerrada (el pipeline de generación
  Open CVN, el formato canónico, el contrato de parser/validador y la
  aplicación CLI). Debe quedar explícito que Open CVN se usa aquí como una
  de las dos fuentes de datos del sistema, no como objeto de estudio.
- **Problema de partida**: la información curricular y de investigación (CVN
  español, perfiles ORCID) vive en fuentes heterogéneas, de distinto
  volumen y distinta naturaleza (documentos estructurados de un lado,
  registros públicos masivos de otro), y no existe una plataforma abierta
  de referencia que las integre, procese distribuidamente y publique
  indicadores agregados sobre ellas.
- **Motivación**: demostrar, con una plataforma real desplegada (no un
  diseño en papel), las competencias de un perfil de Big Data y Computación
  en la Nube:
  levantar infraestructura distribuida, ingerir y fusionar fuentes
  heterogéneas, procesar a escala con tolerancia a fallos, y evaluar el
  sistema con datos y cifras reales, no simuladas.
- **Objetivo general**: diseñar, desplegar y evaluar una plataforma
  *lakehouse* autoalojada sobre Kubernetes que ingiera datos curriculares
  (CVN sintético) y de investigación (ORCID real), los procese de forma
  distribuida por capas bronze/silver/gold con resolución de identidad
  entre fuentes, y publique un conjunto reducido de indicadores en un
  panel de BI, evaluando el sistema con un benchmark de rendimiento acotado.
- **Objetivos específicos** (candidatos, uno por fase del proyecto):
  - desplegar un clúster Kubernetes local con los servicios base
    (almacenamiento de objetos, base de datos relacional, orquestador)
  - integrar un catálogo Iceberg sobre almacenamiento de objetos y probar
    la ejecución de Spark sobre Kubernetes orquestada por Airflow
  - construir un cliente y un pipeline de ingesta para datos ORCID reales
    (API pública y fichero público masivo)
  - generar un conjunto de currículos CVN sintéticos, válidos contra el
    esquema oficial, sembrados con datos públicos reales, evitando
    recolectar CVN reales por motivos de privacidad
  - implementar la validación, normalización y resolución determinista de
    identidad entre fuentes en la transición bronze -> silver
  - calcular indicadores de investigación agregados y publicarlos de forma
    atómica en una base de datos relacional en la transición silver ->
    gold
  - visualizar los indicadores en un panel de BI
  - medir el efecto del número de ejecutores Spark sobre el tiempo de
    ejecución y la fiabilidad a distintas escalas de datos
  - encontrar y corregir defectos de robustez operativa mediante uso
    real del sistema completo ("dogfooding"), documentando una guía de
    reproducción desde cero
- **Nota ética/privacidad**, debe aparecer explícita: por qué no se usan
  CVN reales a volumen (dato personal sin corpus público legítimo) y por
  qué ORCID sí se usa como dato real (perfiles públicos por diseño).
- **Estructura del documento**: resumen de los 7 capítulos.

## Elementos recomendados

- Tabla de objetivos específicos y capítulo(s) donde se tratan (mismo
  patrón que la Tabla del capítulo 1 del TFG).
- Tabla de *learning outcomes* del máster y evidencia esperada (ver
  `estructura_memoria_tfm.md`, tabla de correspondencia).
- Esquema general de alto nivel del flujo de datos (fuentes -> bronze ->
  silver -> gold -> BI), a un nivel muy resumido; el esquema detallado por
  capas va en el capítulo 3/5.

## Outcomes de aprendizaje cubiertos

Ninguno de forma primaria (capítulo introductorio); debe mencionar los seis
para anticipar dónde se demuestran.

## Fuentes principales

- `docs/roadmap/tfm/issues/issue-89-epic-tfm-lakehouse-platform.md`
  (Learning Outcomes Targeted, Original Goal)
- `docs/context/tfm/current_status.md` (sección "What The TFM Adds")

## Estado de redacción

Primer borrador redactado en `docs/memoria/TFM/chapters/ch1.tex`, siguiendo
el estilo de la memoria del TFG (`.claude/skills/tfg-mapi-style`) adaptado a
la plantilla oficial de TFM. Cubre todo el contenido recomendado anterior:
contexto y continuidad con el TFG, problema de partida, motivación,
objetivo general y nueve objetivos específicos con su tabla de
correspondencia a capítulos, nota ética/privacidad sobre CVN sintético
frente a ORCID real, tabla de resultados de aprendizaje del máster, y
estructura del documento.

Por decisión explícita del usuario, el capítulo no menciona créditos ECTS,
plazos, horas de desarrollo ni el límite de páginas del documento: son
condiciones de gestión del proyecto, no argumentos de la memoria. La
sección que originalmente presentaba esas restricciones también justificaba
de paso el despliegue en un único nodo local frente a un clúster en la nube
real; esa justificación se retira de este capítulo y se traslada al
capítulo 2 (ver su guía, sección "Sustrato de orquestación de
contenedores"), donde se argumenta por motivos técnicos propios de un
entorno de desarrollo (coste y reproducibilidad hacia un despliegue en la
nube), no por presupuesto de tiempo.

Segunda revisión: por decisión explícita del usuario, los objetivos
(general y específicos) se reformularon de forma agnóstica respecto a la
arquitectura y las tecnologías concretas (sin nombrar Kubernetes, k3s,
Iceberg, Spark, Airflow, MinIO, PostgreSQL, Superset ni las capas
bronze/silver/gold); cada objetivo describe únicamente el qué, no el cómo.
La tabla de correspondencia a capítulos se actualizó en paralelo. La
elección tecnológica que satisface cada objetivo se presenta y justifica en
el Capítulo 2, no en este capítulo.

Tercera revisión: la generación sintética de CVN dejó de listarse como
objetivo (OE4 original); es una consecuencia de no tener acceso a un corpus
de CVN reales y de poder usar solo datos públicos sin comprometer la
privacidad de nadie, no una meta en sí misma -- esa razón ya estaba bien
formulada en la Sección "Aspectos éticos y de privacidad", el problema
estaba solo en que los objetivos la repetían como si fuera un fin propio.
El objetivo correspondiente pasó a ser "incorporar currículos CVN a la
plataforma, validados frente a Open CVN" (qué se incorpora, no cómo se
obtiene), y el antiguo OE5 se reformuló explícitamente como "integrar
ORCID con CVN por medio de Open CVN", siguiendo la formulación exacta que
pidió el usuario. Además, se activó `\usepackage[section]{placeins}` en
`docs/memoria/TFM/include/configuracion.tex` (estaba comentado en la
plantilla original) porque la Tabla 1.2 flotaba hasta la mitad de la
Sección 1.6 en vez de quedarse en la 1.5 donde se referencia; este cambio
es a nivel de plantilla, aplica a todos los capítulos futuros, no solo a
este.

Cuarta revisión: bibliografía. La Sección "Problema de partida y
motivación" ahora cita cuatro fuentes verificadas contra su origen primario
(`orcid_about`, `orcid_public_data_file_2025`, `eurocris_cerif`,
`vivo_project`), sustituyendo afirmaciones antes sin respaldo (p. ej. "decenas
de millones de registros" de ORCID, ahora la cifra exacta ya verificada
empíricamente por este mismo proyecto: 26\,078\,951 registros, issue `#95`).
`docs/memoria/TFM/bib/ref.bib` ya contiene, además, las 20 entradas
convertidas desde `docs/research/tfm/estado_del_arte_tfm.md`, listas para
cuando los capítulos 2-6 las citen.

Quinta revisión: recorte de extensión. Con 2 de 7 capítulos escritos, el
documento ya llevaba ~20 páginas de cuerpo sobre un máximo de 50; el
usuario pidió resumir. Este capítulo se ajustó de 7 a ~6 páginas
(contexto y motivación más concisos, ética condensada sin perder el
argumento, descripciones de capítulo en "Estructura del documento"
resumidas a una frase cada una), sin quitar ningún objetivo, tabla ni
sección. Ver la nota equivalente, más detallada, en
`ch2_estado_del_arte_y_decisiones.md`, donde el recorte fue mayor.

Sexta revisión: el usuario pidió usar enumeraciones en puntos separados en
vez de listas dentro de una misma frase. En la Sección "Problema de
partida y motivación", los dos casos afectados, los requisitos
arquitectónicos que exige integrar CVN y ORCID, y las acciones que
demuestra la plataforma, se convirtieron de listas con comas dentro de
una frase a `itemize` con un punto por elemento. Esto añadió algo menos
de una página al capítulo, revirtiendo parte del recorte de la revisión
anterior. Se aceptó como coste explícito a cambio de la claridad pedida.

Séptima revisión, puntuación y frase: aplicadas las tres reglas nuevas
recogidas en `estructura_memoria_tfm.md` tras el ejemplo que el usuario
señaló en el capítulo 3: sin paréntesis en ningún punto del texto, sin
punto y coma, y sin mencionar que algo "ya fue justificado" en otra
sección. Las definiciones de sigla, TFM, TFG, ORCID y CRIS, se
reformularon con «en adelante» o «siglas de» en vez de paréntesis. La
lista de campos sembrados desde ORCID, antes entre paréntesis, se integró
en la frase.

Portada y preámbulo (`docs/memoria/TFM/include/opciones.tex`,
`docs/memoria/TFM/elements/portada.tex`, `docs/memoria/TFM/elements/preambulo.tex`)
ya están completos: autor, título provisional del epic `#89`, director (el
mismo que el TFG, Luis De La Ossa Jiménez; el TFM no tiene codirector), DNI
en la declaración de autoría (el mismo que el TFG) y nombre del máster,
confirmados por el usuario.

Pendiente, no bloqueante para capítulos siguientes:
- las referencias cruzadas `Capítulo~\ref{cap:conclusiones}` quedarán sin
  resolver hasta que se redacte el capítulo 7 (con su `\label`); esperado
  mientras la redacción avance capítulo a capítulo (`cap:estado_arte` ya
  se resuelve, el capítulo 2 existe desde la revisión anterior);
- vigilar la extensión total al redactar cada capítulo siguiente: con
  capítulos 1-2 en ~14 páginas de cuerpo, quedan ~36 páginas para los 5
  capítulos restantes (~7 de media cada uno) antes de tocar el máximo de
  50.
