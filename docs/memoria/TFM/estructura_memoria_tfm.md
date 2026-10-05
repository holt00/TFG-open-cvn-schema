# Estructura y trazabilidad de la memoria del TFM

## Propósito de este documento

Guía interna de planificación y trazabilidad para redactar la memoria del
Trabajo de Fin de Máster (TFM), equivalente funcional de
`docs/memoria/TFG/estructura_memoria_tfg.md` para el TFG. No forma parte del
texto final de la memoria.

A diferencia de la versión TFG (un único fichero con todos los capítulos),
esta versión reparte cada capítulo en su propio fichero Markdown bajo
`docs/memoria/TFM/`, para que la guía y el registro de avance de cada
capítulo se mantengan juntos en el mismo sitio. El índice completo está en
la sección "Capítulos" de este documento.

## Relación con el resto de la documentación viva

Esta guía no sustituye a la documentación operativa del proyecto; la
resume y apunta a ella como fuente primaria de datos verificables:

- estado y avance del TFM, entrada por entrada: `docs/context/tfm/current_status.md`
- roadmap con dependencias entre issues: `docs/roadmap/tfm/tfm_roadmap.md`
- epic con las decisiones de arquitectura, constraints académicos y outcomes
  objetivo: `docs/roadmap/tfm/issues/issue-89-epic-tfm-lakehouse-platform.md`
- estado del arte y justificación tecnológica (fuente principal del
  capítulo 2): `docs/research/tfm/estado_del_arte_tfm.md`
- documento de reproducibilidad completo del clúster:
  `docs/development/tfm_lakehouse_workflow.md`
- registro de limitaciones conocidas: `docs/pipeline/known_limitations.md`
- cada issue individual (`#90`-`#103`) bajo `docs/roadmap/tfm/issues/`, cuyas
  secciones `Implementation Performed`/`Findings`/`Verification` son la
  fuente primaria de cifras y hallazgos citables

Cualquier cifra que se traslade a la memoria final debe verificarse contra
estos documentos (o contra el propio repositorio) en el momento de
redactarla, no reutilizarse de memoria, siguiendo el mismo criterio que ya
se aplicó en el TFG.

## Principios de redacción (heredados del TFG, con matices propios del TFM)

Se mantienen los principios obligatorios de
`docs/memoria/TFG/estructura_memoria_tfg.md` (autocontención, sin mención a
IA/herramientas de asistencia salvo exigencia normativa, registro académico
formal, español correcto, bibliografía anotada durante la redacción, cada
afirmación técnica respaldada). Matices específicos del TFM:

- el TFM pertenece al Máster en Big Data y Computación en la Nube, no a la
  intensificación de Computación del TFG; el eje argumental de cada
  capítulo debe alinearse con los seis *learning outcomes* del máster
  (`CN02`, `HA01`, `HA02`, `HA03`, `CP01`, `CP04`, definidos en el epic
  `#89`), no con las competencias `CM1/CM2/CM5/CM6` del TFG
- el TFM no redefine el formato Open CVN ni el ecosistema CVN: los
  consume como base ya cerrada del TFG. La memoria debe dejarlo claro en
  la introducción y no repetir contenido del capítulo 3 o 6 de la memoria
  del TFG
- el límite de 50 páginas y las 6 ECTS (la mitad del TFG) exigen una
  estructura proporcionalmente más compacta: menos capítulos que el TFG (7
  frente a 8), fusionando bloques que en el TFG estaban separados
  (antecedentes + arquitectura; evaluación + endurecimiento). Esta cifra es
  una referencia de planificación interna de esta guía, útil para
  dimensionar cada capítulo mientras se redacta; el texto final de la
  memoria (los capítulos en `chapters/*.tex`) no debe citar créditos ECTS,
  plazos, horas de desarrollo ni el número de páginas del documento, por
  ser condiciones de gestión del proyecto y no argumentos académicos. Esta
  restricción aplica solo al texto final; el resto de documentos de esta
  carpeta (guías de capítulo, este mismo fichero) pueden seguir citando
  estas cifras con normalidad
- reglas de puntuación y frase, pedidas explícitamente por el usuario tras
  leer los capítulos 1-3, aplicables a todo el texto final de la memoria
  (`chapters/*.tex`), no a las guías de planificación:
  - no usar paréntesis en ningún punto del texto. Ni para definir siglas
    (usar «en adelante SIGLA» o «siglas de/en inglés de»), ni para
    incisos o ejemplos (integrarlos en la frase o crear una frase nueva
    y más corta), ni para referencias cruzadas
  - no usar punto y coma. Usar punto y empezar una frase nueva
  - no repetir que algo "ya fue justificado" o "ya se explicó" en otra
    sección o capítulo. Si algo ya se justificó antes, no debe
    mencionarse otra vez esa justificación, el lector ya lo sabe. Una
    referencia cruzada sin esa coletilla, del tipo "Sección~\ref{...}",
    solo se mantiene cuando aporta navegación real
  - cuidado con la puntuación de las comas, especialmente en frases con
    varias cláusulas encadenadas
  - no abusar de pronombres posesivos ("su", "sus") ni demostrativos
    ("esta", "ese", "ella") cuando el antecedente no queda inmediato y
    evidente. Nombrar explícitamente el sustantivo en lugar del pronombre
    siempre que la frase se aleje del antecedente, mezcle varios sujetos
    posibles, o el pronombre pueda leerse apuntando a más de una cosa
- a diferencia del TFG, el TFM sí debe presentar hallazgos operativos reales
  de un sistema desplegado y sometido a carga (fallos de infraestructura
  encontrados y corregidos, no solo limitaciones de diseño), porque forma
  parte de lo que demuestra `CP01`/`CP04`

## Capítulos

| # | Capítulo | Fichero | Estado |
| --- | --- | --- | --- |
| 1 | Introducción, motivación y objetivos | `ch1_introduccion.md` | `EN_PROCESO` |
| 2 | Estado del arte y decisiones arquitectónicas | `ch2_estado_del_arte_y_decisiones.md` | `EN_PROCESO` |
| 3 | Infraestructura: despliegue del clúster y servicios base | `ch3_infraestructura_cluster.md` | `EN_PROCESO` |
| 4 | Ingesta y fusión de fuentes heterogéneas | `ch4_ingesta_fusion_datos.md` | `EN_PROCESO` |
| 5 | Procesamiento distribuido: transformación, resolución de entidades e indicadores | `ch5_procesamiento_distribuido.md` | `EN_PROCESO` |
| 6 | Visualización, evaluación de rendimiento y endurecimiento | `ch6_visualizacion_evaluacion_endurecimiento.md` | `EN_PROCESO` |
| 7 | Conclusiones, competencias y trabajo futuro | `ch7_conclusiones.md` | `EN_PROCESO` |

Estados permitidos, mismo convenio que el TFG: `PENDIENTE` (planificado, sin
redactar), `EN_PROCESO` (en redacción o revisión), `COMPLETADO` (redactado y
revisado para la versión actual).

### Anexos

Situados tras la bibliografía, como en el TFG. Cada anexo respalda una afirmación de los capítulos.

| Anexo | Título | Fuente principal | Estado |
| --- | --- | --- | --- |
| A | Guía de reproducibilidad de la plataforma | `docs/development/tfm_lakehouse_workflow.md` | `EN_PROCESO` |
| B | Resultados completos del banco de pruebas | `docs/benchmark/` | `EN_PROCESO` |
| C | Modelo de datos de la plataforma | `silver/schemas.py`, `gold/schemas.py` | `EN_PROCESO` |
| D | Resolución de identidad en detalle | issue `#98` | `EN_PROCESO` |
| E | Registro de limitaciones | `docs/pipeline/known_limitations.md` | `EN_PROCESO` |
| F | Repositorio del proyecto y guía de uso | repositorio | `EN_PROCESO` |

## Por qué esta estructura y no la del TFG calcada

El TFG dedica capítulos enteros a explicar qué es CVN y a definir el formato
Open CVN, porque esa definición es su aportación central. El TFM no define
ningún formato nuevo: reutiliza Open CVN ya cerrado como una de sus dos
fuentes de datos. Ese hueco se sustituye aquí por los capítulos que sí son
la aportación real del TFM -- infraestructura Kubernetes, ingesta/fusión
multi-fuente, procesamiento distribuido con Spark, y evaluación de
rendimiento -- que no tienen equivalente en la estructura del TFG.

## Correspondencia entre capítulos y issues/documentos fuente

| Capítulo | Issues fuente | Documento de investigación |
| --- | --- | --- |
| 1 | `#89` (epic) | -- |
| 2 | `#89` (tabla de decisión tecnológica) | `docs/research/tfm/estado_del_arte_tfm.md` (completo) |
| 3 | `#90`, `#91`, `#92`, `#93` | secciones 1, 3, 4, 7 del estado del arte |
| 4 | `#94`, `#95`, `#96`, `#97` | secciones 9 (parcial), 10 del estado del arte |
| 5 | `#98`, `#99` | secciones 5, 6, 9 del estado del arte |
| 6 | `#100`, `#101`, `#102` | secciones 5, 8, 11 del estado del arte |
| 7 | todas | sección 12 (síntesis) del estado del arte |

## Correspondencia entre capítulos y *learning outcomes*

| Outcome | Descripción | Capítulos donde se evidencia |
| --- | --- | --- |
| `CN02` | Arquitecturas de tratamiento masivo, almacenamiento y pipelines | 2, 3 |
| `HA01` | Adquisición, fusión y análisis de múltiples fuentes | 4, 5 |
| `HA02` | Procesamiento distribuido y optimización de recursos | 5, 6 |
| `HA03` | Orquestación ETL y almacenamiento escalable | 3, 5 |
| `CP01` | Planificación y despliegue de una solución Big Data | 2, 3, 6 |
| `CP04` | Proyecto profesional original de Big Data | 6, 7 |

Cada capítulo debe, al redactarse, dejar constancia explícita de qué
outcome cubre y con qué evidencia concreta, igual que el TFG hizo con sus
competencias en la Tabla 8.2 de su capítulo de conclusiones.
