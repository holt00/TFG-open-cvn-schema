# Preguntas posibles del tribunal (TFM)

Material de estudio para el turno de preguntas. No forma parte de la exposición ni de las
notas del orador. Cada respuesta indica de dónde sale la información.

## Infraestructura

**¿Qué es el namespace de `tfm-lakehouse` y en qué afecta?**
Es una partición lógica del clúster de Kubernetes. Agrupa y aísla recursos (pods, servicios,
secretos) bajo un nombre. Afecta a tres cosas: los nombres de recursos solo deben ser únicos
dentro de él, los permisos y las cuotas se pueden aplicar por namespace, y el DNS interno lo
incluye (`servicio.tfm-lakehouse.svc`). No es aislamiento de seguridad fuerte por sí solo. No
hay que confundirlo con los namespaces de Iceberg (`lakehouse.silver`, `lakehouse.gold`), que
solo agrupan tablas.

**Si uso un único nodo y quiero escalar, ¿es fácil o automático?**
No es automático. k3s permite añadir nodos y Spark ya es distribuido, así que más ejecutores en
más nodos no cambia el código, y el ejecutor de Kubernetes de Airflow reparte los pods. Pero hay
trabajo previo: ahora el código, los esquemas y los datos de las tareas se montan desde el disco
del nodo (`hostPath`, decisión D2 de la issue #97) y habría que pasarlos a almacenamiento
compartido; MinIO tendría que desplegarse en modo distribuido; y habría que automatizar el
despliegue (infraestructura como código). Todo eso, y el estudio de cómo hacerlo, queda
completamente como trabajo futuro.

**¿Qué es Helm?**
El gestor de paquetes de Kubernetes. Un chart es una plantilla parametrizable de los manifiestos
de un servicio; con un fichero de valores se instala, actualiza o deshace con un comando. Aporta
reproducibilidad: versiones e imágenes fijadas y una instalación que se repite igual desde cero.

**¿Cuántos DAG hay?**
Tres en `dags/`. Dos mueven datos: `ingest_validate` (fuentes → bronze) y `transform_publish`
(bronze → silver → gold → PostgreSQL). El tercero, `issue93_spark_iceberg_smoke_test`, solo
verifica el mecanismo central (Spark lanzado desde Airflow que escribe y lee Iceberg en MinIO).

## Arquitectura y herramientas

**¿Qué es Iceberg y por qué se usa?**
Un formato de tabla abierto: una capa de metadatos (snapshots y manifiestos) sobre ficheros en
almacenamiento de objetos que los hace comportarse como una tabla. Da transacciones ACID,
evolución de esquema sin reescribir datos, lecturas consistentes mientras otro proceso escribe y
time travel. Se eligió porque no depende de un proveedor y se puede consultar desde otros motores
(Spark, Trino, Flink). Delta Lake rinde al máximo sobre Databricks y Hudi está pensado para
actualizaciones incrementales y streaming; este proyecto es un pipeline por lotes.

**¿Diferencia entre lakehouse y warehouse?**
Un data warehouse define el esquema antes de cargar (schema-on-write): consultas fiables, pero
ingerir una fuente nueva exige transformarla antes. Un data lake guarda todo tal cual llega e
interpreta al leer (schema-on-read): flexible y barato, pero sin metadatos transaccionales cae en
el «data swamp». El lakehouse pone una capa de tabla transaccional (Iceberg) sobre almacenamiento
de objetos barato: ambas ventajas en un solo sistema. El prefijo `warehouse/` de tu cubo es otra
cosa: la ruta donde Iceberg guarda sus tablas.

**¿Qué es la arquitectura medallion?**
Organizar los datos en capas de calidad creciente: bronze (crudo), silver (validado y
normalizado) y gold (agregado para consumo).

**¿Qué diferencia hay entre el bronze de fuera y el de dentro de Iceberg?**
El bronze real es el de fuera (`bronze/`): ficheros JSON Lines que escriben las tareas de
ingesta. El catálogo define también un namespace `lakehouse.bronze`, pero el pipeline no crea
tablas en él: `bronze_to_silver` lee los ficheros directamente y solo escribe silver y gold
como tablas Iceberg. Nota: la memoria (cap. 3) menciona los tres namespaces y el cap. 4 dice
que las tablas bronze de Iceberg se crearían en la transformación, pero el cap. 5 no lo hace.

## Datos

**¿Es lo mismo perfil ORCID que registro ORCID?**
Casi. Perfil es la ficha pública de la persona en ORCID. Registro es cada documento guardado en
bronze (un perfil de ORCID, una respuesta de la API o un CVN). Cada perfil da lugar a un registro.

**¿Por qué solo se usan 20.000 registros de ORCID y se pasa de 301.763 a 20.000?**
El fichero tiene 26.078.951 perfiles; se filtran los 301.763 con afiliación española, que es la
base de partida. Por ejecución se aterrizan los primeros 20.000 (límite por defecto): mantiene
cada ejecución diaria en un tamaño manejable, y el fichero no cambia entre ejecuciones. Es un
parámetro: se eleva para las pruebas de rendimiento.

**¿Por qué 10.000 CVN y por qué se baja a 1.000?**
No se baja: son dos ejecuciones. La ejecución por defecto genera 1.000 CVN; la de evaluación a
escala genera 10.000, una muestra suficientemente grande para medir la fusión (7.098 declaran su
ORCID y 2.902 no). Ambas conviven en bronze.

**¿De dónde salen 30.868 personas, 99.979 afiliaciones y 543.879 publicaciones?**
30.868 registros de persona = 19.469 de ORCID (fichero) + 399 de la API + 11.000 CVN (1.000 de la
ejecución por defecto + 10.000 de la de evaluación). Las afiliaciones y publicaciones son los
elementos contenidos dentro de esos registros.

**¿Por qué el trabajo falla si se llega al 5 % de rechazados?**
Unos pocos registros defectuosos son normales (en los primeros 20.000 de ORCID se rechazó el
2,66 %, casi todos por no tener apellido público) y se apartan con su error sin parar nada. Por
encima del umbral ya no son casos sueltos: indica un problema sistemático de origen o de lectura,
y seguir adelante dejaría un conjunto silenciosamente incompleto sobre el que se calcularían
indicadores equivocados. Fallar convierte el problema en un error visible. El valor del 5 % es un
parámetro de diseño, no una cifra calculada.

**¿Cómo se comprueba el dígito de control del ORCID?**
Un ORCID iD tiene 16 caracteres; el último es un dígito de control (0-9 o X) según ISO 7064
MOD 11-2 (`src/tfm_lakehouse/orcid_client/client.py`). Se recorren los 15 primeros dígitos con
`total = (total + dígito) × 2`; después `resto = total mod 11` y `resultado = (12 − resto) mod 11`;
si el resultado es 10 se escribe X. Si no coincide con el último carácter, el identificador es
inválido.

**¿Qué es la clave de bloqueo?**
Técnica de resolución de entidades: una clave barata (aquí, apellido normalizado + inicial del
nombre; «de la Torre, Ana» → «torre, a») y solo se comparan los registros con la misma clave.
Reduce las comparaciones y es la primera condición de R2.

**¿Qué significa «organizaciones como conjunto de palabras significativas»?**
Se quitan las palabras sin identidad («de», «la», «of», «the»…) y se ignora el orden, para
comparar organizaciones por solapamiento de palabras: «Universidad de Granada» y «Granada,
Universidad de» dan el mismo conjunto.

**¿Qué diferencia hay entre precisión y cobertura?**
Precisión: de las fusiones que hace R2, cuántas son correctas (138 de 144 = 95,8 %). Cobertura:
de los casos que R2 podía resolver, cuántos resuelve (138 de 186 = 74,2 %).

**¿La cobertura está en su techo o se podría mejorar con otro modelo?**
Con esta regla el máximo es el 74,7 %: 47 de los 186 casos no tienen ninguna afiliación y R2
exige una organización común. Otro modelo que use más señales (por ejemplo obras compartidas, o
uno probabilístico) podría superarlo; no se ha estudiado y queda como trabajo futuro.

## Gold y panel

**¿Por qué se deduplican las publicaciones?**
Una misma obra puede figurar varias veces en la misma persona (en su CVN y en su perfil de
ORCID). Sin deduplicar se contaría un 5,1 % de más (543.879 filas → 516.396 obras distintas).

**¿Por qué gold se copia a PostgreSQL y Superset no consulta Iceberg ni Spark?**
Superset se conecta directamente a PostgreSQL. Para leer Iceberg haría falta un motor de consulta
intermedio (Trino o Spark), un servicio más que operar. Decisión del capítulo 2: Superset sobre
base relacional, sin Trino.

**¿Qué es la publicación atómica y por qué importa?**
Los datos nuevos se cargan en tablas temporales, se comprueba que tienen las mismas filas que
gold y las tablas nuevas sustituyen a las publicadas en una única transacción. El panel ve las
tablas anteriores completas o las nuevas completas: nunca vacío ni a medio cargar.

**¿Qué es el motor de consulta del trabajo futuro y por qué no se usó?**
Un motor de consulta SQL como Trino, que consulta tablas Iceberg directamente. Daría una vía de
consulta independiente del panel y permitiría que Superset leyera gold sin copiarlo a PostgreSQL
(PostgreSQL dejaría de ser necesario, o solo se conservaría por el intercambio atómico). No se
usó porque todo el acceso a los datos ya se hace desde los trabajos de procesamiento y añadiría
un servicio más que operar (capítulo 2). Por eso Superset va a PostgreSQL.

**¿Qué significa observabilidad continua para producción?**
Poder saber cómo está el sistema por dentro a partir de lo que emite (métricas, registros y
alertas), recogido de forma permanente y guardado en el tiempo, por ejemplo con Prometheus y
Grafana. En el trabajo no se hizo: para el benchmark bastó el registro de eventos de Spark
(duración de cada etapa y uso de cada ejecutor). En producción permitiría detectar los fallos,
como los de Airflow que aquí se encontraron a mano, antes de que los vea un usuario.

**¿Por qué `transform_publish` se lanza a mano?**
Decisión D8 de la issue #99: `schedule=None`, para probar primero la cadena sin una pieza móvil
más y no esconder fallos detrás de un cron. Un disparo automático desde `ingest_validate` no se
construyó. La memoria no lo dice de forma explícita (solo el anexo A lanza el flujo con
`airflow dags trigger`).

**¿Por qué el formato de tabla necesita evolución de esquema?**
Capacidad de cambiar el esquema de una tabla (añadir, renombrar o quitar columnas) sin reescribir
los datos ni romper a los lectores. La memoria la justifica porque CVN y ORCID no comparten
esquema y sus fuentes cambian. En la práctica silver y gold se reconstruyen por completo
(`createOrReplace`), así que no se usa: es una capacidad que habilita el procesamiento
incremental (trabajo futuro). La razón principal de Iceberg es que es abierto, multimotor y con
transacciones.

## Rendimiento

**¿Qué recurso limita el rendimiento?**
La exposición lo presenta como limitaciones de hardware del único nodo local. El dato medido: el
uso de CPU del sistema nunca superó el 32,2 % y ese máximo coincidió con cuatro ejecutores, el
mismo punto donde el servicio de almacenamiento de objetos del propio nodo alcanzó también su
máximo, es decir, ejecutores y almacenamiento compiten por el mismo hardware. Atención: la
memoria (cap. 6) formula esto como «consistente con los datos pero no demostrado de forma
concluyente».

**¿Por qué «con el cuádruple de datos hacen falta cuatro ejecutores»?**
Con el cuádruple de datos y el dimensionamiento de memoria fijo por ejecutor, ni uno ni dos
ejecutores completan el trabajo de silver; solo se completa con cuatro.
