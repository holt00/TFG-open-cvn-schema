# Capítulo 6: Visualización, evaluación de rendimiento y endurecimiento

Estado: `EN_PROCESO`

## Objetivo del capítulo

Cerrar la demostración del sistema con tres piezas que en el TFG estaban
separadas (evaluación y limitaciones) pero que aquí se agrupan por
presupuesto de páginas: el panel de BI como resultado visible, el
benchmark de rendimiento como evaluación cuantitativa formal, y el
endurecimiento como evidencia de que el sistema se sometió a uso real, no
solo a una demo controlada.

## Contenido recomendado (ideas principales)

- **Panel de BI**: conexión de Superset a la base de datos PostgreSQL de
  gold (nunca a Iceberg/Spark directamente, coherente con la decisión
  arquitectónica del capítulo 2); los indicadores mostrados son agregados,
  sin nombres de personas; el panel se define como código versionado
  (exportación reproducible), no como configuración manual perdida en la
  interfaz.
- **Benchmark de rendimiento, presentado como una evaluación formal, no
  como una nota al margen**: metodología (variar número de ejecutores en un
  conjunto fijo de valores, variar la escala de datos en un conjunto fijo
  de factores, con calentamiento descartado y repeticiones por punto),
  aislamiento de la campaña de benchmark respecto a los datos de
  producción, verificación de que la salida es idéntica entre
  configuraciones (no solo que el tiempo cambia, sino que el resultado no
  se corrompe).
- **Resultado principal del benchmark, con su cifra exacta verificada**: el
  número de ejecutores no es solo una palanca de velocidad, es una palanca
  de *fiabilidad* a partir de cierta escala -- con el dimensionamiento de
  memoria fijo por ejecutor usado en este TFM, un único ejecutor deja de
  poder completar la etapa de transformación a partir de cierto volumen de
  datos (falla de forma determinista, no intermitente), mientras que más
  ejecutores no siempre reducen el tiempo de forma proporcional. Esta
  conclusión debe presentarse con su evidencia (curvas de tiempo, no solo
  la afirmación) y con la hipótesis más plausible sobre la causa (el
  almacenamiento de objetos compartido, no la CPU, como cuello de botella
  más probable), señalando explícitamente que no está demostrada de forma
  concluyente, solo respaldada por los datos disponibles.
- **Endurecimiento como demostración de robustez operativa real**: a
  diferencia de una limitación de diseño (aceptada de antemano), estos son
  fallos reales encontrados usando el sistema completo bajo condiciones
  reales (reinicio del servidor de tareas, arranque en frío simultáneo de
  varios servicios, reconstrucción completa del clúster desde cero en un
  entorno aislado). Deben presentarse como evidencia de rigor de
  evaluación, no como una lista de errores vergonzosos: encontrar y
  corregir un fallo de un componente externo (el orquestador) mediante
  diagnóstico y una recuperación operativa reproducible es en sí mismo un
  resultado del TFM.
- **Validación de reproducibilidad desde cero**: la plataforma se
  reconstruyó completa, siguiendo únicamente una guía escrita, en un
  entorno aislado que no tocó los datos de producción, como prueba final
  de que el sistema no depende de pasos manuales no documentados.

## Elementos recomendados

- Gráficas de tiempo de ejecución frente a número de ejecutores, una por
  escala de datos (el elemento central del capítulo).
- Tabla de eficiencia/aceleración derivada de las gráficas anteriores.
- Captura o descripción del panel de BI con sus indicadores.
- Tabla de hallazgos de endurecimiento: síntoma, causa raíz, corrección
  aplicada.

## Outcomes de aprendizaje cubiertos

`HA02`, `CP04` (principales), `CP01` (parcial: la reconstrucción desde cero
es en sí una prueba de planificación/despliegue).

## Fuentes principales

- issues `#100` (panel Superset), `#101` (benchmark), `#102` (endurecimiento)
- `docs/benchmark/results.md` (cifras y gráficas ya generadas)
- `docs/development/tfm_lakehouse_workflow.md` (guía de reproducibilidad
  validada)
- `docs/pipeline/known_limitations.md` (registro completo de hallazgos)
- secciones 5, 8, 11 de `docs/research/tfm/estado_del_arte_tfm.md`

## Estado de redacción

Sin empezar. Este es probablemente el capítulo con más material verificable
ya disponible (gráficas y cifras del benchmark ya generadas en
`docs/benchmark/`, hallazgos de endurecimiento ya documentados issue por
issue); el trabajo de redacción es principalmente de síntesis y selección,
no de generación de contenido nuevo.

Borrador de partida disponible: la sección "Observabilidad y captura de
resultados" se redactó inicialmente dentro del capítulo 2, pero el usuario
indicó que la estrategia de captura de métricas del benchmark corresponde
a este capítulo, no al estado del arte de la plataforma; se retiró de
`docs/memoria/TFM/chapters/ch2.tex` y se deja aquí como texto de partida,
pendiente de adaptar:

> Un banco de pruebas de rendimiento acotado necesita capturar métricas de
> ejecución (duración, uso de recursos, número de ejecutores) de forma
> reproducible. Una pila de observabilidad como Prometheus junto con
> Grafana~\cite{grafana_docs} es el estándar de facto en entornos
> Kubernetes, con exportadores tanto para Spark como para el propio
> clúster, y permitiría paneles en tiempo real y series históricas. Cada
> ejecución de Spark, sin embargo, ya escribe un registro de eventos
> detallado (duración de etapas, tareas y uso de ejecutores) que su propio
> servidor de historial puede interpretar sin infraestructura adicional.
> Dado que el banco de pruebas de este trabajo es una campaña acotada y no
> un requisito de monitorización continua en producción, instalar y operar
> una pila de observabilidad completa solo para capturar los datos de esa
> campaña puntual no estaba justificado; el propio registro de eventos de
> Spark contiene toda la información que dicha campaña necesita. Una pila
> de observabilidad continua queda documentada como trabajo futuro.

Pendiente al integrar este borrador: añadir la cita de Prometheus (aún sin
entrada en `docs/memoria/TFM/bib/ref.bib`, pendiente de verificar si se
llega a nombrar explícitamente aquí) y desarrollarlo con el detalle
metodológico propio de este capítulo (variables del benchmark, aislamiento
de la campaña, verificación de resultados idénticos entre
configuraciones), no dejarlo al nivel resumido en que se escribió para el
capítulo 2.

## Historial de redacción

Redactado el capítulo completo en `docs/memoria/TFM/chapters/ch6.tex` a
partir de los issues `#100`, `#101` y `#102`, releídos en su totalidad
antes de citar ninguna cifra, incluidas sus secciones `Adjustments Made
During Implementation`/`Verification`/`Findings`. Las cifras del banco de
pruebas se tomaron de `docs/benchmark/results.md`, no reconstruidas de
memoria.

Estructura final, cuatro secciones: panel de indicadores (Superset sobre
un rol de solo lectura dedicado, agregados sin nombres de personas, panel
como código verificado mediante borrado y reimportación completos,
verificación en directo durante una ejecución real del flujo de
transformación), metodología y resultados del banco de pruebas de
rendimiento (el borrador de partida sobre observabilidad integrado y
desarrollado, el hallazgo principal de que el número de ejecutores es una
palanca de fiabilidad antes que de velocidad, con la Figura 6.1 tomada
directamente de `docs/benchmark/benchmark_silver.png` y la Tabla 6.1 con
los exponentes de escalado de los tres trabajos), endurecimiento (los dos
hallazgos operativos reales del bloqueo del orquestador de flujos y del
cierre del servidor de su interfaz bajo carga, ambos reconfirmados de
forma independiente durante la propia redacción de la memoria, no solo
encontrados una vez), y verificación de extremo a extremo (la
reconstrucción completa en un clúster Kubernetes aislado y desechable, que
encontró y corrigió un nuevo fallo real de arranque concurrente de
PostgreSQL).

La gráfica del banco de pruebas es la única figura de este capítulo que no
se dibujó con TikZ. Es una figura real ya generada por el propio banco de
pruebas, copiada a `docs/memoria/TFM/figs/benchmark_silver.png`, y no una
reconstrucción, porque es la evidencia medida en sí misma, no un diagrama
explicativo.

Bibliografía: se retomó el borrador de partida sobre observabilidad,
originalmente descartado sin integrar, y se añadieron las entradas
`prometheus_docs` y `k3d_docs` a `docs/memoria/TFM/bib/ref.bib`,
verificadas contra su origen antes de citarlas. `grafana_docs` ya existía,
citada por primera vez en el capítulo 2 como alternativa de visualización
descartada, y se reutiliza aquí en un contexto de justificación distinto,
la observabilidad de la campaña de rendimiento y no el panel de
indicadores.

Compilación verificada con `xelatex` + `bibtex` + `xelatex` ×2: sin cajas
`Overfull`/`Underfull` propias del capítulo, sin citas sin definir, cero
paréntesis y cero punto y coma fuera del código TikZ. El capítulo ocupa 6
páginas de cuerpo, páginas 41 a 46, y deja el cuerpo total del documento
en 46 páginas tras seis capítulos, con 4 páginas de margen para el
capítulo 7 dentro del límite de 50.
