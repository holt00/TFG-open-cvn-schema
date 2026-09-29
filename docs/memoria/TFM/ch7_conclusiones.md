# Capítulo 7: Conclusiones, competencias y trabajo futuro

Estado: `PENDIENTE`

## Objetivo del capítulo

Cerrar la memoria retomando los objetivos del capítulo 1, valorando su
cumplimiento con evidencia concreta de los capítulos 3-6, dejando constancia
explícita de los seis *learning outcomes* del máster, y proponiendo trabajo
futuro honesto (lo que se dejó fuera por presupuesto de tiempo, no por
imposibilidad técnica). Nota de redacción: esta razón (presupuesto de
tiempo/ECTS) es válida como referencia interna de planificación en esta
guía, pero el texto final del capítulo 7 no debe citar ECTS, plazos ni
horas; ahí la razón debe formularse como alcance decidido deliberadamente
(ver capítulo 1 y capítulo 2 para el mismo criterio ya aplicado).

## Contenido recomendado (ideas principales)

- **Resumen del trabajo**, breve, en dos o tres bloques (problema y
  motivación; arquitectura desplegada; resultados), siguiendo el mismo
  patrón que el TFG adoptó en su capítulo 8 tras revisar una memoria de
  referencia.
- **Cumplimiento de objetivos**: tabla objetivo por objetivo (los del
  capítulo 1) con su nivel de cumplimiento, distinguiendo lo cumplido sin
  matices de lo cumplido con garantías parciales (por ejemplo, la
  resolución de identidad tiene una cobertura medida por debajo de lo
  ideal, y debe reflejarse así, no ocultarse).
- **Contribuciones principales**, en prosa narrativa (no solo una lista),
  cada una con referencia al capítulo donde se demuestra: la plataforma
  lakehouse desplegada y verificada end-to-end; el mecanismo de fusión
  ORCID-CVN sintético diseñado desde el origen del dato; la resolución de
  identidad determinista con evidencia auditable; el benchmark que
  demuestra el número de ejecutores como palanca de fiabilidad, no solo de
  velocidad; la guía de reproducibilidad validada por una reconstrucción
  real desde cero.
- **Competencias/*learning outcomes* desarrollados**: tabla con los seis
  outcomes (`CN02`, `HA01`, `HA02`, `HA03`, `CP01`, `CP04`) y su evidencia
  concreta, capítulo por capítulo, cerrando la promesa que el capítulo 1
  dejó pendiente (mismo patrón que la Tabla 8.2 del TFG con `CM1/CM2/CM5/CM6`).
- **Limitaciones y trabajo futuro**, distinguiendo su origen (igual que hizo
  el TFG entre limitación del paquete CVN y limitación de alcance propio,
  aquí entre limitación de la infraestructura de terceros usada y
  limitación de alcance decidida por presupuesto de tiempo/ECTS -- en el
  texto final del capítulo, formulada como alcance decidido
  deliberadamente, no citando ECTS ni presupuesto de tiempo):
  - origen infraestructura de terceros: el fallo conocido y sin corrección
    oficial disponible del orquestador (documentado y con una recuperación
    operativa reproducible, no un parche de código)
  - origen alcance propio: sin capa de consulta interactiva (Trino); sin
    observabilidad centralizada (Prometheus/Grafana); despliegue de un solo
    nodo local en vez de un clúster real en la nube (justificado en el
    capítulo 2; sin infraestructura como código -- Terraform -- para ese
    paso); procesamiento no incremental (reconstrucción completa en cada
    ejecución); resolución de identidad sin aprendizaje automático
  - cada limitación debe llevar su trabajo futuro asociado, ya esbozado en
    el epic `#89` como "future work" explícito
- **Conclusión general**: sintetiza el problema de partida, la arquitectura
  construida capa a capa, el cumplimiento del objetivo general apoyado en
  evidencia reproducible, y cierra posicionando la plataforma completa
  (no el panel de BI ni un componente aislado) como la aportación
  principal del TFM.

## Elementos recomendados

- Tabla de cumplimiento de objetivos.
- Tabla de *learning outcomes* con evidencia.
- Tabla de limitaciones y trabajo futuro por origen.

## Outcomes de aprendizaje cubiertos

Los seis, de forma consolidada (capítulo de cierre).

## Fuentes principales

- capítulo 1 de esta misma guía (objetivos que se retoman aquí)
- `docs/roadmap/tfm/issues/issue-89-epic-tfm-lakehouse-platform.md`,
  secciones "Scope Priority / Cut List" y cualquier "future work" explícito
- `docs/pipeline/known_limitations.md` (registro de limitaciones por origen)

## Estado de redacción

Sin empezar. Depende de que los capítulos 1-6 estén al menos en borrador
para poder referenciarlos con `\ref{}` en vez de texto literal, siguiendo la
misma convención que usó el TFG mientras redactaba capítulos fuera de orden.
