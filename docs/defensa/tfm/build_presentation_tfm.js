/*
 * Generador de la presentacion de defensa del TFM (indice A, estilo "Plano tecnico").
 *
 * Contenido basado en docs/memoria/TFM/chapters/*.tex y en las figuras de
 * docs/memoria/TFM/figs/. Salida: docs/defensa/tfm/presentacion_tfm.pptx
 *
 *   NODE_PATH=<ruta a node_modules con pptxgenjs y sharp> \
 *     node docs/defensa/tfm/build_presentation_tfm.js
 */
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");
const sharp = require("sharp");

const ROOT = path.resolve(__dirname, "..", "..", "..");
const FIGS = path.join(ROOT, "docs", "memoria", "TFM", "figs");
const OUT = process.env.OUT_PATH || path.join(__dirname, "presentacion_tfm.pptx");
const SKILL_THEME = process.env.APPLY_THEME_JS; // ruta a apply_theme.js
const PRINT = process.env.PRINT === "1"; // version de impresion: fondo blanco

// ---------------------------------------------------------------------------
// Tema (estilo 2, plano tecnico): azul de plano, acero, ambar como unico acento
// ---------------------------------------------------------------------------
const THEME_DARK = {
  name: "TFM Plano tecnico",
  headFontFace: "Calibri",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "0E2238", lt1: "FFFFFF", dk2: "1A3556", lt2: "E8EEF5",
    accent1: "F2A541", accent2: "4D7194", accent3: "9FB3C8",
    accent4: "6FB7A0", accent5: "7FB2E5", accent6: "CBD7E4",
    hlink: "F2A541", folHlink: "9FB3C8",
  },
};
// Version de impresion: mismos papeles de color, pero invertidos (dk = superficies claras, lt = texto oscuro)
const THEME_PRINT = {
  name: "TFM Plano tecnico impresion",
  headFontFace: "Calibri",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "FFFFFF", lt1: "10243A", dk2: "EEF3F8", lt2: "10243A",
    accent1: "A85A00", accent2: "7A93AE", accent3: "44566A",
    accent4: "2E7D5B", accent5: "2F6EA8", accent6: "2B3E52",
    hlink: "A85A00", folHlink: "44566A",
  },
};
const THEME = PRINT ? THEME_PRINT : THEME_DARK;
// Colores que se escriben como hexadecimal (numero de pagina, graficos, bordes de tabla, capas medallion)
const PAL = PRINT
  ? { num: "A85A00", foot: "44566A", title: "10243A", border: "7A93AE", chartA: "C97A0A", chartB: "2F6EA8", chartText: "10243A", chartMuted: "44566A", grid: "D5DDE6",
      bronze: "A0551E", silver: "6B7886", gold: "A87A00", white: "FFFFFF" }
  : { num: "F2A541", foot: "9FB3C8", title: "FFFFFF", border: "4D7194", chartA: "F2A541", chartB: "7FB2E5", chartText: "E8EEF5", chartMuted: "9FB3C8", grid: "2C4A6B",
      bronze: "D08A4E", silver: "C3CBD6", gold: "F2C14E", white: "FFFFFF" };
const MONO = "Consolas";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "Defensa del TFM: arquitectura lakehouse para información curricular académica";
pres.author = "Carlos Martínez Jaén";
const C = pres.SchemeColor;
const SH = pres.ShapeType;

const L = 0.6;          // margen izquierdo
const W = 12.13;        // ancho util
const GAP = 0.15;

// ---------------------------------------------------------------------------
// Fondo con cuadricula de plano (se genera como imagen)
// ---------------------------------------------------------------------------
async function buildBackground() {
  const w = 1920, h = 1080, step = 80;
  let lines = "";
  for (let x = step; x < w; x += step) lines += `<line x1="${x}" y1="0" x2="${x}" y2="${h}"/>`;
  for (let y = step; y < h; y += step) lines += `<line x1="0" y1="${y}" x2="${w}" y2="${y}"/>`;
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}">
    <rect width="${w}" height="${h}" fill="#0E2238"/>
    <g stroke="#FFFFFF" stroke-opacity="0.05" stroke-width="1.5">${lines}</g></svg>`;
  const buf = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function txt(slide, text, o) {
  slide.addText(text, Object.assign({
    isTextBox: true, margin: 0, fontFace: "Calibri", fontSize: 16,
    color: C.background1, valign: "top", align: "left",
  }, o));
}
function mono(slide, text, o) {
  txt(slide, text, Object.assign({ fontFace: MONO, fontSize: 12, color: C.accent1, charSpacing: 1 }, o));
}
function card(slide, x, y, w, h, name, o) {
  slide.addShape(SH.rect, Object.assign({
    x, y, w, h, objectName: name,
    fill: { color: C.text2 }, line: { color: C.accent2, width: 0.75 },
  }, o));
}
function arrowRight(slide, x, y, w, name) {
  slide.addShape(SH.line, { x, y, w, h: 0, objectName: name,
    line: { color: C.accent1, width: 2, endArrowType: "triangle" } });
}
function arrowDown(slide, x, y, h, name) {
  slide.addShape(SH.line, { x, y, w: 0, h, objectName: name,
    line: { color: C.accent1, width: 2, endArrowType: "triangle" } });
}
function plainLine(slide, x, y, w, h, name) {
  slide.addShape(SH.line, { x, y, w, h, objectName: name, line: { color: C.accent2, width: 1.25 } });
}
function bullets(items, o) {
  return items.map((t, i) => ({
    text: t,
    options: Object.assign({ bullet: { indent: 16 }, breakLine: i < items.length - 1, paraSpaceAfter: 6 }, o),
  }));
}
function stat(slide, x, y, w, h, big, label, name) {
  card(slide, x, y, w, h, name);
  txt(slide, big, { x: x + 0.2, y: y + 0.15, w: w - 0.4, h: 0.65, fontSize: w < 2.4 ? 26 : 32, bold: true, color: C.accent1 });
  txt(slide, label, { x: x + 0.2, y: y + 0.85, w: w - 0.4, h: h - 0.95, fontSize: 14, color: C.accent6 });
}

// Notas del orador: un titulo que introduce la diapositiva y, debajo, solo el texto a decir, separado por ideas.
// Una entrada por diapositiva, en el mismo orden que la presentacion.
const NOTES = [
  { // 1
    p: [
      "Buenos días. Me llamo Carlos Martínez Jaén y voy a presentar mi Trabajo Fin de Máster, dirigido por Luis De La Ossa Jiménez.",
      "El trabajo se titula «Diseño de una arquitectura lakehouse escalable para la integración y análisis de información curricular académica».",
    ],
  },
  { // 2
    p: [
      "La exposición tiene ocho bloques, que cubren los cuatro apartados de la normativa: objetivos, metodología, contenido y conclusiones.",
      "Los bloques 1 y 2 presentan el contexto y los objetivos, y el bloque 3 la metodología y la arquitectura. Los bloques 4 a 7 son el contenido, capa a capa, y el bloque 8 recoge las conclusiones y el trabajo futuro.",
    ],
  },
  { // 3
    p: [
      "Este trabajo continúa mi Trabajo Fin de Grado. En él resolví cómo representar un currículo: una capa estructural generada de los esquemas oficiales de CVN, un formato abierto, Open CVN JSON, y un contrato de validación.",
      "Lo que quedaba por resolver era la escala. Este trabajo construye una plataforma que ingiere, fusiona y procesa datos de dos fuentes, CVN y ORCID, y publica indicadores en un panel.",
      "Open CVN se reutiliza como fuente de datos. El objeto de estudio de este trabajo es cómo se ingiere, valida y procesa dentro de una plataforma distribuida.",
    ],
  },
  { // 4
    p: [
      "La información de un investigador está repartida en fuentes de naturaleza muy distinta. CVN es el currículum normalizado de una persona: un documento individual y estructurado, pensado para convocatorias y evaluaciones. ORCID es un registro público a escala global: solo su fichero de 2025 contiene más de 26 millones de perfiles.",
      "Este trabajo integra ambas fuentes en una plataforma abierta, autoalojada y reproducible, y publica indicadores agregados. Para ello hay que cubrir cinco requisitos.",
      "• Almacenamiento escalable, que crezca con el volumen de ORCID.",
      "• Un formato de tabla que admita cambios de esquema y conserve la trazabilidad, porque CVN y ORCID no comparten esquema.",
      "• Orquestación reproducible de los flujos de ingesta, transformación y publicación.",
      "• Procesamiento distribuido y tolerante a fallos.",
      "• Y resolución de identidad, para fusionar los registros que son la misma persona.",
      "Cada requisito indica el bloque donde lo desarrollo. No es solo un problema de formato, sino de arquitectura.",
    ],
  },
  { // 5
    p: [
      "El objetivo general es diseñar, desplegar y evaluar una plataforma que integre CVN y ORCID, los procese de forma distribuida con resolución de identidad entre fuentes y publique indicadores en un panel, evaluándola con un benchmark de rendimiento acotado.",
      "Lo desarrollo en nueve objetivos específicos, y cada tarjeta indica el bloque en el que lo explico.",
      "Antes de continuar, fijo los criterios con los que se juzgará el resultado, para que más adelante quede claro qué se cumple y qué no.",
      "• En la fusión de identidades, el objetivo era alcanzar un 99 % de precisión. Fijé ese umbral antes de medir.",
      "• En la calidad de los datos, si más del 5 % de los registros de una fuente se rechaza, la tarea falla.",
      "En las conclusiones retomaré los objetivos en este mismo orden.",
    ],
  },
  { // 6
    p: [
      "El método sigue cuatro pasos.",
      "Primero, construir por capas: empiezo por la infraestructura y compruebo el mecanismo central de procesamiento antes de construir ningún flujo. Después añado cada capa de datos sobre la anterior.",
      "Segundo, usar datos reales. ORCID aporta perfiles públicos reales. Los CVN se generan a partir de esos perfiles, porque un currículo completo es información personal y no es legítimo recolectar currículos de terceros.",
      "Tercero, verificar cada capa. El resultado de cada fase se comprueba por una vía distinta de la que lo produjo. Uso tres: el resultado del propio trabajo, una lectura de los datos desde otro proceso y un recálculo independiente en Python.",
      "Y cuarto, poder reconstruirlo. Existe una guía escrita para levantar toda la plataforma desde cero, y la validé reconstruyéndola en un clúster aislado.",
    ],
  },
  { // 7
    p: [
      "Para cada requisito elegí una herramienta, y el motivo de cada elección está en la tabla.",
      "• Almacenamiento: MinIO, que usa el mismo protocolo S3 que un proveedor de nube real, sin coste ni dependencia externa.",
      "• Formato de tabla: Iceberg, un formato abierto que se puede consultar desde otros motores sin cambiarlo.",
      "• Orquestación: Airflow, que se despliega de forma nativa en Kubernetes.",
      "• Procesamiento: Spark, adecuado para el procesamiento por lotes y bien integrado con Iceberg.",
      "• Resolución de identidad: reglas deterministas, que dejan una evidencia explícita de por qué se fusiona cada registro.",
      "• Despliegue y consulta: k3s en un solo nodo, por coste y reproducibilidad, y Superset sobre PostgreSQL, que permite definir el panel como código.",
      "El criterio común es que todo sea autoalojado, reproducible desde cero y con buen soporte entre componentes.",
      "Además, MinIO, Airflow y Spark son herramientas que trabajé durante el máster. Y Airflow y Superset las uso también en mi día a día en el trabajo, por eso las prioricé frente a otras similares.",
    ],
  },
  { // 8
    p: [
      "Esta es la arquitectura del trabajo. Sigue el patrón llamado arquitectura medallion, que organiza los datos en tres capas: bronze, silver y gold.",
      "Los datos entran desde ORCID y CVN y aterrizan en bronze: son datos crudos, tal como llegan, con su procedencia.",
      "Después pasan por una validación y por la resolución de entidades, y se almacenan en tablas Iceberg en la capa silver.",
      "A continuación se agregan para calcular los indicadores, y ese resultado se guarda en la capa gold, que sigue siendo tablas Iceberg en MinIO.",
      "Por último, los datos de gold se traspasan a PostgreSQL para que Superset pueda leerlos de ahí con facilidad.",
      "Dos flujos de Airflow, que en Airflow se llaman DAG, mueven los datos. ingest_validate lleva los datos de las fuentes a bronze. transform_publish los lleva de bronze a silver, de silver a gold y, finalmente, a PostgreSQL.",
      "A partir de aquí iremos explicando cada una de estas capas.",
    ],
  },
  { // 9
    p: [
      "Todo se ejecuta sobre un clúster Kubernetes ligero, k3s, de un único nodo local. La fila superior muestra los servicios: Airflow, Spark, MinIO con Iceberg, PostgreSQL y Superset.",
      "Todos los recursos viven dentro de un namespace de Kubernetes llamado tfm-lakehouse. Un namespace es un espacio dentro del clúster que agrupa y aísla recursos, como los pods, los servicios y los secretos.",
      "• Un pod por tarea. Airflow usa el ejecutor de Kubernetes: cada tarea, y cada trabajo de Spark, se lanza como un pod propio dentro del namespace.",
      "• Reproducible con Helm. Helm es el gestor de paquetes de Kubernetes: cada servicio se instala desde una plantilla llamada chart, con las versiones de cada imagen fijadas.",
      "• Mecanismo verificado. Antes de construir ningún flujo comprobé que Spark, lanzado desde Airflow, escribe y lee tablas Iceberg en MinIO. Para ello existe un tercer DAG, aparte de los dos de datos.",
    ],
  },
  { // 10
    p: [
      "Este diagrama muestra cómo se organiza el almacenamiento dentro de MinIO. Todo está en un único cubo, lakehouse, con dos zonas: una fuera de Iceberg y otra dentro.",
      "• Fuera de Iceberg está el prefijo bronze: ficheros crudos, tal como llegan, que escriben directamente las tareas de ingesta.",
      "• Dentro de Iceberg está el prefijo warehouse, el catálogo. Contiene solo las tablas que gestiona Iceberg, silver y gold, que escriben los trabajos de Spark. Cada capa es un namespace de Iceberg, una agrupación de tablas; no hay que confundirlo con el namespace de Kubernetes.",
      "Se mantienen separados porque, si se mezclaran ficheros crudos con tablas, Iceberg podría encontrarse con ficheros que no son suyos y fallar.",
      "La diferencia real entre el bronze de fuera y el de dentro: el bronze real, donde están los datos, es el de fuera. En el catálogo existe también un namespace bronze, pero está reservado y sin tablas, porque el pipeline lee bronze directamente de los ficheros.",
      "A la derecha, fijé imágenes y versiones concretas: las de MinIO y PostgreSQL para obtenerlas gratis, y las de Spark, Iceberg y Hadoop porque tienen que ser compatibles entre sí.",
    ],
  },
  { // 11
    p: [
      "Los datos de ORCID se obtienen de dos formas, con usos distintos.",
      "• La API pública consulta un perfil concreto por su identificador, para actualizar los datos de las personas que declaran los CVN.",
      "• El fichero anual es un volcado de todos los perfiles públicos y da el volumen real de partida.",
      "El fichero contiene 26.078.951 perfiles. Me quedo con los que declaran una afiliación en España: 301.763.",
      "Los CVN se generan a partir de esos perfiles, reutilizando su nombre, afiliaciones y obras. El 70 % declara el ORCID del perfil de origen y el resto solo conserva nombre y afiliaciones; esa diferencia permite medir después la fusión. Genero 10.000 para evaluarla con una muestra suficiente; es un parámetro, por defecto son 1.000.",
      "Tres términos que usaré a partir de ahora:",
      "• Perfil: la ficha pública de una persona en ORCID.",
      "• Registro: cada documento que se guarda en bronze, sea un perfil de ORCID, una respuesta de la API o un CVN. Cada perfil da lugar a un registro.",
      "• Publicación: una obra, como un artículo o un libro, dentro de un perfil o de un CVN.",
    ],
  },
  { // 12
    p: [
      "Todo aterriza en bronze mediante el flujo ingest_validate, con cuatro tareas, cada una en su propio pod. El orden importa: el enriquecimiento con la API consulta los identificadores ORCID que declaran los CVN, por eso va después de generarlos.",
      "Cada registro lleva consigo sus datos de procedencia: de qué fuente viene, cuándo se obtuvo y se guardó, qué ejecución lo guardó y si superó la comprobación inicial.",
      "En cada ejecución se procesan los primeros 20.000 de los 301.763 perfiles. Es un límite configurable que mantiene cada ejecución manejable; se amplía en las pruebas de rendimiento. Se aceptaron 19.469 registros y se rechazaron 531, casi todos sin apellido público.",
      "Los rechazados van a una zona aparte con sus errores. Si superan el 5 % de una fuente, la tarea falla: unos pocos defectuosos son normales, pero una proporción alta indica un fallo sistemático de origen, y es preferible parar a continuar con datos incompletos sin que nadie lo note.",
      "Respecto a los CVN, la ejecución por defecto genera 1.000 y la de evaluación, 10.000: son dos ejecuciones distintas, y los datos de ambas quedan en bronze.",
    ],
  },
  { // 13
    p: [
      "El primer trabajo de Spark transforma bronze en silver. Aclaro de dónde salen las cifras.",
      "Silver recoge todo lo que hay en bronze: 19.469 registros de ORCID del fichero, 399 de la API y 11.000 CVN, que son los 1.000 por defecto más los 10.000 de la evaluación. En total, 30.868 registros de persona.",
      "Dentro de esos registros hay 99.979 afiliaciones y 543.879 publicaciones: son los elementos que contienen los propios registros, porque cada persona tiene varias afiliaciones y muchas publicaciones.",
      "Cada registro pasa por tres comprobaciones:",
      "• Formato: el documento cumple el esquema Open CVN.",
      "• Contenido: cada elemento, como una publicación o una formación, tiene los campos propios de su tipo.",
      "• Reglas: por ejemplo, que el ORCID tenga un dígito de control válido, el último carácter, calculado a partir de los anteriores para detectar errores de transcripción, y que las fechas sean coherentes.",
      "En esta ejecución no se rechazó ninguno. Los que fallen van a una tabla de rechazados con la regla incumplida.",
      "Después se normalizan los datos para poder compararlos.",
      "• Nombres: sin acentos ni partículas. «de la Torre, Ana» pasa a la clave «torre, a».",
      "• Organizaciones: solo las palabras con significado, sin importar el orden. «Universidad de Granada» y «Granada, Universidad de» se reconocen como la misma.",
    ],
  },
  { // 14
    p: [
      "Ahora hay que resolver qué registros son la misma persona, con reglas deterministas aplicadas por orden de fuerza de la evidencia.",
      "• R1: dos registros con el mismo ORCID válido son la misma persona.",
      "• R2, para un CVN sin ORCID: busca una persona ya identificada por R1 con la misma clave de bloqueo, un nombre compatible y alguna organización en común, y exige que sea la única candidata.",
      "La clave de bloqueo es el apellido normalizado más la inicial del nombre: permite comparar solo los registros que la comparten, en lugar de todos contra todos. Y nombre compatible significa que puede variar el nombre o el apellido, pero no ambos.",
      "• R3: sin evidencia, la persona queda como entidad propia.",
      "Medí el resultado contra la verdad de referencia del propio generador, sobre 10.000 CVN. R1 acierta en sus 7.098 casos. Para R2 hay dos medidas:",
      "• Precisión: de las fusiones que hace R2, cuántas son correctas. Es del 95,8 %: 138 de 144.",
      "• Cobertura: de los casos que R2 podía resolver, cuántos resuelve. Es del 74,2 %: 138 de 186.",
      "El objetivo de precisión del 99 % no se alcanza en R2. Se prioriza la precisión porque una fusión errónea contamina los indicadores, mientras que una fusión no hecha solo divide a una persona en dos.",
      "Con esta regla la cobertura máxima es el 74,7 %, porque 47 de los 186 casos no tienen afiliación y R2 necesita una organización para comparar. Superarlo requeriría otro tipo de evidencia, por ejemplo un modelo probabilístico: queda como trabajo futuro.",
    ],
  },
  { // 15
    p: [
      "El segundo trabajo de Spark calcula tres indicadores en la capa gold: las publicaciones por año, los pares de colaboración entre personas que comparten una obra y la línea temporal de afiliaciones.",
      "En el primero hay que deduplicar: una misma publicación puede figurar dos veces en la misma persona, en su CVN y en su perfil de ORCID. Sin deduplicar se contarían de más: de 543.879 filas se pasa a 516.396 obras distintas, un 5,1 % menos.",
      "Los datos de gold se copian después a PostgreSQL, porque Superset se conecta directamente a PostgreSQL y lee de ahí con facilidad. Para leer Iceberg haría falta un motor de consulta intermedio, como Spark o Trino, un servicio más que operar.",
      "La copia se hace en tres pasos, para que el panel nunca vea datos incompletos.",
      "• Primero, los datos nuevos se cargan en tablas temporales, sin tocar las publicadas.",
      "• Segundo, se comprueba que PostgreSQL tiene las mismas filas que gold.",
      "• Tercero, las tablas nuevas sustituyen a las anteriores en una única transacción. Es lo importante: el panel nunca se queda vacío ni a medio cargar; ve las tablas anteriores completas o las nuevas completas.",
      "Un recálculo independiente en Python no halló ninguna discrepancia en 306.599 filas. Y si se deshacen las fusiones más débiles de R2, los indicadores cambian como máximo un 0,58 %.",
    ],
  },
  { // 16
    p: [
      "Este es el panel de Superset. Lee la capa gold desde PostgreSQL y muestra siempre agregados, nunca nombres de personas: las publicaciones por año, la línea temporal de afiliaciones, las colaboraciones entre personas con datos reales de ORCID y una tabla de procedencia que indica de qué ejecución sale cada cifra.",
      "Superset consulta PostgreSQL y no Iceberg ni Spark porque se conecta a PostgreSQL de forma directa. Para leer Iceberg haría falta un motor de consulta en medio, como Trino o Spark, que añadiría un servicio más. La conexión, además, usa un usuario de solo lectura.",
      "El panel está definido como código: lo borré por completo y, al reimportarlo, quedó idéntico.",
      "Y comprobé que se actualiza sin estados intermedios: lancé el flujo completo de transformación mientras un proceso consultaba el panel de forma continua. Durante 1.040 segundos y 238 consultas no hubo ningún error ni respuesta vacía.",
    ],
  },
  { // 17
    p: [
      "Medí cómo afecta el número de ejecutores de Spark al rendimiento, con tres volúmenes de datos, 1x, 2x y 4x, y 1, 2 y 4 ejecutores en cada uno. Se descarta la primera ejecución de cada volumen, cada configuración se repite tres veces y se comprueba que todas dan el mismo contenido final.",
      "El gráfico muestra la eficiencia: la aceleración dividida entre el número de ejecutores, donde 1,0 sería un reparto perfecto.",
      "• En silver, con 2 ejecutores la aceleración es de 1,50 veces y con 4, de 1,63, lejos de la ideal.",
      "• En el cálculo de indicadores la eficiencia cae hasta 0,23, porque los datos ya están agregados y hay poco que repartir.",
      "El hallazgo principal es de fiabilidad: con el doble de datos, un solo ejecutor agota la memoria en silver y no termina, y con el cuádruple de datos hacen falta cuatro ejecutores. A partir de cierto volumen, los ejecutores no solo dan velocidad: permiten terminar.",
      "El cuello de botella son las limitaciones de hardware del único nodo local: la CPU nunca superó el 32,2 %, y ese máximo coincidió con los cuatro ejecutores.",
    ],
  },
  { // 18
    p: [
      "Estos fallos aparecieron al usar el sistema completo, no en una demostración controlada.",
      "• Bloqueo del orquestador. El servidor de tareas de Airflow dejó de arrancar por un error conocido, sin corrección oficial, al reconciliar una tarea huérfana. La solución fue marcar la tarea como fallida y reiniciar. Reapareció días después y se resolvió igual.",
      "• Interfaz de Airflow bajo carga. Sin recursos reservados, su comprobación de salud la reiniciaba. Se corrigió reservando CPU y memoria.",
      "• PostgreSQL sin el usuario de gold. Apareció al reconstruir en un clúster nuevo: el primer arranque se interrumpió y no creó el usuario. Se corrigió reinicializando el servicio.",
      "Corregir un fallo de un componente externo es, en sí mismo, un resultado del trabajo.",
      "Por último, reconstruí toda la plataforma desde cero con solo la guía escrita, en un clúster aislado con k3d, sin tocar el clúster real. Los dos flujos y el panel funcionaron de extremo a extremo.",
    ],
  },
  { // 19
    p: [
      "Distingo dos niveles de garantía.",
      "Fuertes y verificadas:",
      "• El mecanismo central, comprobado con el registro del trabajo y con una lectura desde otro pod.",
      "• La ingesta, cuyas cifras coincidieron con una lectura independiente con Spark.",
      "• Gold, con cero discrepancias frente a un recálculo en Python y una segunda ejecución idéntica.",
      "• La publicación, que quedó intacta al detener el proceso a mitad de la carga.",
      "• La reproducibilidad, con una reconstrucción desde cero siguiendo solo la guía.",
      "Parciales y documentadas:",
      "• La identidad sin ORCID: 95,8 % de precisión frente al 99 % fijado, y 74,2 % de cobertura.",
      "• El rendimiento, limitado por el hardware del único nodo local.",
      "• El fallo del orquestador, resuelto con una receta operativa.",
      "• Un alcance deliberado: un solo nodo y reconstrucción completa de silver y gold en cada ejecución.",
      "El despliegue en un clúster real y el estudio de cómo escalar no forman parte de este trabajo: quedan completamente como trabajo futuro.",
    ],
  },
  { // 20
    p: [
      "Retomo los nueve objetivos en el orden en que los planteé. Ocho se dan por cumplidos: la infraestructura, el mecanismo central, los datos reales de ORCID, los CVN validados, los indicadores, el panel, el benchmark y la robustez operativa.",
      "Uno, la integración de ORCID con CVN, se cumple con garantías parciales: la meta era un 99 % de precisión, y la regla sin ORCID llega al 95,8 %, con un 74,2 % de cobertura.",
      "Las contribuciones principales son cinco:",
      "• Una plataforma lakehouse verificada de extremo a extremo.",
      "• Una fusión entre ORCID y CVN diseñada desde el origen del dato.",
      "• Una resolución de identidad determinista, con evidencia auditable.",
      "• El hallazgo de que el número de ejecutores de Spark es una palanca de fiabilidad y no solo de velocidad.",
      "• Una guía de reproducibilidad validada con una reconstrucción real.",
      "El objetivo general se considera cumplido, y la única salvedad está medida, no oculta.",
    ],
  },
  { // 21
    p: [
      "Este trabajo demuestra, con una plataforma desplegada y medida, que ORCID y CVN pueden integrarse en un lakehouse autoalojado y reproducible, con la identidad resuelta entre fuentes y con evidencia reproducible de su rendimiento y su robustez. Las limitaciones proceden de un componente externo o son decisiones de alcance.",
      "Como trabajo futuro, en primer lugar, el despliegue en un clúster real y el estudio de cómo escalar, que quedan completamente pendientes. Después:",
      "• Incorporar la corrección oficial del orquestador cuando exista.",
      "• Un motor de consulta SQL sobre Iceberg, como Trino. Permitiría consultar gold directamente desde Superset, sin copiarlo a PostgreSQL, y daría una vía de consulta independiente del panel.",
      "• Monitorización permanente en producción, con métricas, registros y alertas, por ejemplo con Prometheus y Grafana. Hoy basta el registro de eventos de Spark, pero en producción permitiría detectar los fallos antes de que los vea un usuario.",
      "• Procesamiento incremental sobre los snapshots de Iceberg, en lugar de reconstruir silver y gold en cada ejecución.",
      "• Y vinculación probabilística o con aprendizaje automático para la resolución de identidad.",
    ],
  },
  { // 22
    p: [
      "Muchas gracias por su atención. Quedo a disposición del tribunal para las preguntas.",
    ],
  },
];
const SLIDE_TITLES = [
  "Presentación del trabajo", "Índice de la presentación", "El TFG resolvió el formato; falta la escala",
  "Integrar ORCID y CVN exige cinco requisitos", "Nueve objetivos en cuatro bloques de trabajo", "Método: construir, verificar y reproducir",
  "Herramientas elegidas para cada requisito", "Arquitectura medallion: bronze, silver y gold", "Un clúster k3s de un nodo aloja los servicios",
  "Almacenamiento: dentro y fuera de Iceberg", "ORCID aporta el volumen y los CVN, el enlace", "Todo aterriza en bronze con su procedencia",
  "Silver: solo entra lo validado, con rastro", "Fusión de identidades: precisión medida", "Gold: indicadores publicados de forma atómica",
  "Panel de indicadores sin estados intermedios", "Más ejecutores dan fiabilidad, no solo velocidad", "Endurecimiento: fallos reales corregidos",
  "Garantías fuertes donde el proceso es determinista", "Ocho objetivos cumplidos y uno parcial", "Conclusión y líneas de trabajo futuro", "Cierre",
];
// Cada nota empieza con un titulo que introduce la diapositiva; despues, solo el texto a decir.
function buildNote(i) {
  return [`Diapositiva ${i + 1} · ${SLIDE_TITLES[i]}`, "", NOTES[i].p.join("\n\n")].join("\n");
}
const hdr = (t) => ({ text: t, options: { fontFace: MONO, fontSize: 12, bold: true, color: C.accent1, fill: { color: C.text1 } } });
const cell = (t, b, i, size) => ({ text: t, options: { fontSize: size || 15, bold: !!b, color: b ? C.background1 : C.accent6, fill: { color: i % 2 ? C.text1 : C.text2 } } });
// Lista con etiqueta en negrita al principio de cada punto, un punto por idea
function points(items, o) {
  const runs = [];
  items.forEach((it, i) => {
    const last = i === items.length - 1;
    runs.push({ text: it[0] + " ", options: Object.assign({ bold: true, color: C.accent1, paraSpaceAfter: 8 }, o) });
    runs.push({ text: it[1], options: Object.assign({ color: C.accent6, breakLine: !last, paraSpaceAfter: 8 }, o) });
  });
  return runs;
}

let n = 0;
let acc = 0;
const durations = [];
function newSlide(layoutName, blockName, kicker, title, time) {
  n += 1;
  const [tm, ts] = time.split(":").map(Number);
  durations.push(tm * 60 + ts);
  const s = pres.addSlide({ masterName: layoutName, sectionTitle: blockName });
  if (kicker) mono(s, kicker, { x: L, y: 0.3, w: 10, h: 0.3, objectName: "Bloque de la exposicion" });
  if (title) s.addText(title, { placeholder: "title" });
  s.addNotes(buildNote(n - 1));
  return s;
}

async function main() {
  const BG = await buildBackground();
  const BGOPT = PRINT ? { color: "FFFFFF" } : { data: BG };
  const num = { x: 12.0, y: 6.95, w: 0.73, h: 0.3, fontFace: MONO, fontSize: 12, color: PAL.num, align: "right" };
  pres.defineSlideMaster({ title: "PORTADA", background: BGOPT, slideNumber: num });
  pres.defineSlideMaster({
    title: "CONTENIDO", background: BGOPT, slideNumber: num,
    objects: [
      { text: { text: "TFM · Carlos Martínez Jaén", options: { x: L, y: 6.95, w: 5, h: 0.3, margin: 0, fontFace: MONO, fontSize: 10, color: PAL.foot } } },
      { placeholder: { options: { name: "title", type: "title", x: L, y: 0.62, w: W, h: 0.85, margin: 0, fontFace: "Calibri", fontSize: 32, bold: true, color: PAL.title, align: "left", valign: "top" }, text: "" } },
    ],
  });

  const BL = ["Motivación y contexto", "Objetivos", "Metodología y arquitectura", "Infraestructura", "Ingesta de datos",
    "Procesamiento distribuido", "Evaluación y resultados", "Conclusiones y trabajo futuro"];
  const K = (i) => `${i} · ${BL[i - 1].toUpperCase()}`;
  const lg = path.join(FIGS, "logouclm.jpg");
  const mw = (W - GAP) / 2;
  const iw = (W - 2 * GAP) / 3;

  // ---- 1. Portada --------------------------------------------------------
  pres.addSection({ title: BL[0] });
  let s = newSlide("PORTADA", BL[0], null, null, "0:20");
  mono(s, "TRABAJO FIN DE MÁSTER", { x: 0.8, y: 0.85, w: 8, h: 0.3, fontSize: 14, charSpacing: 3 });
  txt(s, "Diseño de una arquitectura lakehouse escalable para la integración y análisis de información curricular académica",
    { x: 0.8, y: 1.55, w: 9.2, h: 2.5, fontSize: 38, bold: true, objectName: "Titulo del trabajo" });
  txt(s, "Carlos Martínez Jaén", { x: 0.8, y: 4.3, w: 9, h: 0.45, fontSize: 22, bold: true });
  txt(s, "Director: Luis De La Ossa Jiménez", { x: 0.8, y: 4.8, w: 9, h: 0.35, fontSize: 16, color: C.accent3 });
  txt(s, "Máster en Big Data y Computación en la Nube · Octubre de 2026", { x: 0.8, y: 5.2, w: 9, h: 0.35, fontSize: 16, color: C.accent3 });
  s.addShape(SH.roundRect, { x: 10.2, y: 0.6, w: 2.53, h: 1.25, rectRadius: 0.08, fill: { color: PAL.white }, line: { color: PRINT ? PAL.border : PAL.white, width: PRINT ? 0.75 : 0 }, objectName: "Placa del logotipo" });
  s.addImage({ path: lg, x: 10.38, y: 0.76, w: 2.17, h: 0.936, altText: "Logotipo de la Universidad de Castilla-La Mancha", objectName: "Logotipo UCLM" });
  ["Airflow", "Spark", "MinIO + Iceberg", "PostgreSQL", "Superset"].forEach((c, i, arr) => {
    const x = 0.8 + i * 2.45;
    s.addShape(SH.rect, { x, y: 6.05, w: 2.0, h: 0.5, fill: { color: C.text1 }, line: { color: C.accent2, width: 1 }, objectName: "Nodo " + c });
    txt(s, c, { x, y: 6.05, w: 2.0, h: 0.5, fontFace: MONO, fontSize: 12, color: C.accent6, align: "center", valign: "middle" });
    if (i < arr.length - 1) arrowRight(s, x + 2.05, 6.3, 0.35, "Flecha " + (i + 1));
  });

  // ---- 2. Indice (8 bloques numerados) --------------------------------------
  s = newSlide("CONTENIDO", BL[0], "ÍNDICE", "Índice de la presentación", "0:30");
  const sub = ["Del formato al problema de la escala", "Un objetivo general y nueve específicos", "Método, herramientas y capas",
    "Clúster, servicios y almacenamiento", "ORCID, CVN y bronze", "Silver, identidad y gold",
    "Panel, rendimiento y robustez", "Cumplimiento, límites y futuro"];
  BL.forEach((b, i) => {
    const col = Math.floor(i / 4), row = i % 4;
    const x = L + col * (mw + GAP), y = 1.8 + row * 1.2;
    card(s, x, y, mw, 1.05, "Bloque " + (i + 1));
    mono(s, String(i + 1), { x: x + 0.3, y, w: 0.6, h: 1.05, fontSize: 28, valign: "middle" });
    txt(s, b, { x: x + 1.1, y: y + 0.15, w: mw - 1.3, h: 0.45, fontSize: 20, bold: true });
    txt(s, sub[i], { x: x + 1.1, y: y + 0.6, w: mw - 1.3, h: 0.35, fontSize: 14, color: C.accent6 });
  });

  // ---- 3. Contexto: TFG -> TFM ------------------------------------------
  s = newSlide("CONTENIDO", BL[0], K(1), "El TFG resolvió el formato; falta la escala", "0:40");
  const cwid = 5.5;
  card(s, L, 1.85, cwid, 3.3, "Tarjeta TFG");
  mono(s, "TFG · CERRADO", { x: L + 0.3, y: 2.05, w: 4.8, h: 0.3 });
  txt(s, bullets(["Capa estructural reproducible, generada de los esquemas oficiales de CVN", "Formato abierto Open CVN JSON, con su esquema", "Contrato de validación y convenciones de procedencia"]),
    { x: L + 0.3, y: 2.5, w: 4.9, h: 2.5, fontSize: 17 });
  arrowRight(s, L + cwid + 0.2, 3.5, 0.83, "Flecha TFG a TFM");
  card(s, L + W - cwid, 1.85, cwid, 3.3, "Tarjeta TFM");
  mono(s, "TFM · ESTE TRABAJO", { x: L + W - cwid + 0.3, y: 2.05, w: 4.8, h: 0.3 });
  txt(s, bullets(["Plataforma que ingiere, fusiona y procesa datos a escala", "Dos fuentes: CVN y ORCID", "Indicadores publicados en un panel de visualización"]),
    { x: L + W - cwid + 0.3, y: 2.5, w: 4.9, h: 2.5, fontSize: 17 });
  card(s, L, 5.45, W, 1.1, "Banda de reutilizacion");
  txt(s, "Open CVN se reutiliza como fuente de datos, no como objeto de estudio. Este trabajo cuenta cómo se ingiere, valida y procesa dentro de una plataforma distribuida.",
    { x: L + 0.3, y: 5.55, w: W - 0.6, h: 0.9, fontSize: 18, valign: "middle" });

  // ---- 4. Problema -> cinco requisitos ----------------------------------
  s = newSlide("CONTENIDO", BL[0], K(1), "Integrar ORCID y CVN exige cinco requisitos", "1:00");
  const pw = 5.3;
  card(s, L, 1.85, pw, 1.6, "Tarjeta CVN");
  txt(s, "CVN", { x: L + 0.25, y: 1.98, w: 4.8, h: 0.4, fontSize: 22, bold: true, color: C.accent1 });
  txt(s, "Documento individual y estructurado, pensado para convocatorias y evaluaciones", { x: L + 0.25, y: 2.45, w: 4.8, h: 0.9, fontSize: 16 });
  txt(s, "+", { x: L + pw, y: 1.85, w: W - 2 * pw, h: 1.6, fontSize: 44, bold: true, color: C.accent1, align: "center", valign: "middle" });
  card(s, L + W - pw, 1.85, pw, 1.6, "Tarjeta ORCID");
  txt(s, "ORCID", { x: L + W - pw + 0.25, y: 1.98, w: 4.8, h: 0.4, fontSize: 22, bold: true, color: C.accent1 });
  txt(s, "Registro público a escala global: más de 26 millones de perfiles en su fichero de 2025", { x: L + W - pw + 0.25, y: 2.45, w: 4.8, h: 0.9, fontSize: 16 });
  txt(s, "Este trabajo las integra en una plataforma abierta, autoalojada y reproducible, y publica indicadores agregados.",
    { x: L, y: 3.7, w: W, h: 0.65, fontSize: 18, bold: true, valign: "middle" });
  mono(s, "INTEGRARLAS EXIGE · BLOQUE QUE LO DESARROLLA", { x: L, y: 4.55, w: 8, h: 0.3 });
  const caps = [["Almacenamiento escalable", "BLOQUE 4"], ["Formato de tabla con evolución de esquema y trazabilidad", "BLOQUE 4"],
    ["Orquestación reproducible de flujos", "BLOQUES 4 Y 5"], ["Procesamiento distribuido tolerante a fallos", "BLOQUE 6"], ["Resolución de identidad entre fuentes", "BLOQUE 6"]];
  const rw = (W - 4 * GAP) / 5;
  caps.forEach((c, i) => {
    const x = L + i * (rw + GAP);
    card(s, x, 4.9, rw, 1.65, "Requisito " + (i + 1));
    txt(s, c[0], { x: x + 0.15, y: 4.98, w: rw - 0.3, h: 1.05, fontSize: 15, bold: true });
    mono(s, "→ " + c[1], { x: x + 0.15, y: 6.15, w: rw - 0.3, h: 0.3, fontSize: 10, color: C.accent3 });
  });

  // ---- 5. Objetivos (cada uno con su bloque) ------------------------------
  pres.addSection({ title: BL[1] });
  s = newSlide("CONTENIDO", BL[1], K(2), "Nueve objetivos en cuatro bloques de trabajo", "1:25");
  card(s, L, 1.8, W, 1.3, "Objetivo general");
  mono(s, "OBJETIVO GENERAL", { x: L + 0.25, y: 1.92, w: 4, h: 0.25 });
  txt(s, "Diseñar, desplegar y evaluar una plataforma que integre CVN y ORCID, los procese de forma distribuida con resolución de identidad entre fuentes y publique indicadores en un panel, evaluada con un benchmark de rendimiento acotado.",
    { x: L + 0.25, y: 2.22, w: W - 0.5, h: 0.85, fontSize: 16 });
  const oes = [
    ["OE1 · BLOQUE 4", "Desplegar la infraestructura base de la plataforma"],
    ["OE2 · BLOQUE 4", "Validar de extremo a extremo el procesamiento distribuido"],
    ["OE3 · BLOQUE 5", "Incorporar datos reales de ORCID"],
    ["OE4 · BLOQUE 5", "Incorporar CVN validados frente al formato Open CVN"],
    ["OE5 · BLOQUE 6", "Integrar ORCID y CVN resolviendo la identidad (objetivo: 99 % de precisión)"],
    ["OE6 · BLOQUE 6", "Calcular y publicar indicadores de forma consistente"],
    ["OE7 · BLOQUE 7", "Visualizar los indicadores en un panel accesible"],
    ["OE8 · BLOQUE 7", "Medir el efecto del paralelismo sobre tiempo y fiabilidad"],
    ["OE9 · BLOQUE 7", "Encontrar y corregir fallos operativos y reproducir desde cero"],
  ];
  const ow = (W - 2 * GAP) / 3;
  oes.forEach((o, i) => {
    const x = L + (i % 3) * (ow + GAP), y = 3.3 + Math.floor(i / 3) * 1.12;
    card(s, x, y, ow, 1.0, o[0].slice(0, 3));
    mono(s, o[0], { x: x + 0.15, y: y + 0.08, w: ow - 0.3, h: 0.25 });
    txt(s, o[1], { x: x + 0.15, y: y + 0.36, w: ow - 0.3, h: 0.6, fontSize: 14 });
  });

  // ---- 6. Metodo: cuatro pasos ---------------------------------------------
  pres.addSection({ title: BL[2] });
  s = newSlide("CONTENIDO", BL[2], K(3), "Método: construir, verificar y reproducir", "1:00");
  const steps = [
    ["1", "Construir por capas", "Primero la infraestructura y el mecanismo central de procesamiento. Después, cada capa de datos sobre la anterior."],
    ["2", "Usar datos reales", "ORCID aporta perfiles públicos reales. Los CVN se generan a partir de ellos para no emplear currículos de personas reales."],
    ["3", "Verificar cada capa", "El resultado de cada fase se comprueba por una vía distinta de la que lo produjo."],
    ["4", "Reconstruir desde cero", "Una guía escrita permite levantar toda la plataforma. Se validó reconstruyéndola en un clúster aislado."],
  ];
  const stw = (W - 3 * 0.5) / 4;
  steps.forEach((st, i) => {
    const x = L + i * (stw + 0.5);
    card(s, x, 1.85, stw, 3.25, "Paso " + st[0]);
    mono(s, st[0], { x: x + 0.25, y: 1.95, w: 1, h: 0.6, fontSize: 30 });
    txt(s, st[1], { x: x + 0.25, y: 2.65, w: stw - 0.5, h: 0.7, fontSize: 19, bold: true });
    txt(s, st[2], { x: x + 0.25, y: 3.4, w: stw - 0.5, h: 1.65, fontSize: 14, color: C.accent6 });
    if (i < steps.length - 1) arrowRight(s, x + stw + 0.05, 3.35, 0.4, "Flecha paso " + st[0]);
  });
  mono(s, "VERIFICACIONES QUE SE USAN EN EL TRABAJO", { x: L, y: 5.35, w: 8, h: 0.3 });
  ["Resultado del propio trabajo", "Lectura desde otro proceso", "Recálculo independiente en Python"].forEach((v, i) => {
    const x = L + i * (iw + GAP);
    s.addShape(SH.rect, { x, y: 5.75, w: iw, h: 0.8, fill: { color: C.text1 }, line: { color: C.accent2, width: 1 }, objectName: "Verificacion " + (i + 1) });
    txt(s, v, { x: x + 0.15, y: 5.75, w: iw - 0.3, h: 0.8, fontSize: 16, bold: true, align: "center", valign: "middle" });
  });

  // ---- 7. Herramientas por requisito -------------------------------------------
  s = newSlide("CONTENIDO", BL[2], K(3), "Herramientas elegidas para cada requisito", "1:00");
  const dec = [
    ["Almacenamiento escalable", "MinIO (protocolo S3)", "Mismo protocolo que un proveedor real, sin coste ni dependencia externa. Frente a HDFS y nube pública."],
    ["Formato de tabla con trazabilidad", "Apache Iceberg", "Abierto y consultable desde otros motores sin cambios. Frente a Delta Lake y Hudi."],
    ["Orquestación reproducible", "Apache Airflow", "Despliegue nativo en Kubernetes, sin servicios adicionales. Frente a Prefect, Dagster y Luigi."],
    ["Procesamiento distribuido", "Apache Spark", "Encaja con el procesamiento por lotes e integra bien con Iceberg. Frente a Flink, Dask y Ray."],
    ["Resolución de identidad", "Reglas deterministas", "Dejan evidencia explícita y auditable de cada fusión. Frente a la vinculación probabilística."],
    ["Despliegue y consulta", "k3s de un nodo y Superset", "Menor coste y más reproducibilidad; panel definido como código. Frente a un clúster real y Trino."],
  ];
  s.addTable([[hdr("REQUISITO"), hdr("HERRAMIENTA"), hdr("MOTIVO")]].concat(dec.map((r, i) => [cell(r[0], false, i, 15), cell(r[1], true, i, 15), cell(r[2], false, i, 14)])),
    { x: L, y: 1.75, w: W, colW: [3.0, 2.9, 6.23], rowH: [0.4, 0.62, 0.62, 0.62, 0.62, 0.62, 0.62], margin: [0, 0.15, 0, 0.15], valign: "middle",
      border: { type: "solid", pt: 0.75, color: PAL.border }, fontFace: "Calibri", objectName: "Tabla de herramientas" });
  txt(s, "Criterio común: autoalojado, reproducible desde cero y con buen soporte entre componentes.",
    { x: L, y: 6.0, w: W, h: 0.35, fontSize: 15, italic: true, color: C.accent3, valign: "middle" });
  txt(s, "Experiencia previa: MinIO, Airflow y Spark, del máster; Airflow y Superset, de mi trabajo diario.",
    { x: L, y: 6.4, w: W, h: 0.35, fontSize: 15, italic: true, color: C.accent3, valign: "middle" });

  // ---- 8. Arquitectura medallion --------------------------------------------------
  s = newSlide("CONTENIDO", BL[2], K(3), "Arquitectura medallion: bronze, silver y gold", "1:00");
  const arch = [
    ["FUENTES", "ORCID y CVN", C.accent3, "BLOQUE 5"],
    ["BRONZE", "Datos crudos, tal como llegan, con su procedencia", PAL.bronze, "BLOQUE 5"],
    ["SILVER", "Datos validados y con la identidad resuelta, en tablas Iceberg", PAL.silver, "BLOQUE 6"],
    ["GOLD", "Datos agregados para calcular los indicadores, en tablas Iceberg", PAL.gold, "BLOQUE 6"],
    ["POSTGRESQL Y PANEL", "Gold se copia a PostgreSQL y Superset lo lee desde ahí", C.accent1, "BLOQUE 7"],
  ];
  const aw = 2.17, ag = 0.32;
  arch.forEach((a, i) => {
    const x = L + i * (aw + ag);
    s.addShape(SH.rect, { x, y: 1.85, w: aw, h: 2.5, fill: { color: C.text2 }, line: { color: a[2], width: 1.75 }, objectName: "Capa " + a[0] });
    mono(s, a[3], { x: x + 0.1, y: 1.95, w: aw - 0.2, h: 0.25, fontSize: 10, color: C.accent3, align: "center" });
    txt(s, a[0], { x: x + 0.1, y: 2.3, w: aw - 0.2, h: 0.7, fontSize: 18, bold: true, color: a[2], align: "center", valign: "middle" });
    txt(s, a[1], { x: x + 0.15, y: 3.05, w: aw - 0.3, h: 1.25, fontSize: 15, color: C.accent6, align: "center" });
    if (i < arch.length - 1) arrowRight(s, x + aw + 0.03, 3.1, ag - 0.06, "Flecha capa " + (i + 1));
  });
  mono(s, "DOS FLUJOS DE AIRFLOW (DAG) MUEVEN LOS DATOS", { x: L, y: 4.65, w: 9, h: 0.3, fontSize: 11 });
  const brk = (x0, x1, y, label, name) => {
    s.addShape(SH.rect, { x: x0, y, w: x1 - x0, h: 0.55, fill: { color: C.text1 }, line: { color: C.accent2, width: 1 }, objectName: name });
    mono(s, label, { x: x0, y, w: x1 - x0, h: 0.55, fontSize: 14, align: "center", valign: "middle", color: C.accent6 });
  };
  brk(L, L + 2 * aw + ag, 5.05, "ingest_validate: fuentes → bronze", "Flujo ingest_validate");
  brk(L + aw + ag, L + 5 * aw + 4 * ag, 5.75, "transform_publish: bronze → silver → gold → PostgreSQL", "Flujo transform_publish");

  // ---- 9. Infraestructura ---------------------------------------------------------------
  pres.addSection({ title: BL[3] });
  s = newSlide("CONTENIDO", BL[3], K(4), "Un clúster k3s de un nodo aloja los servicios", "1:15");
  const nodes = [["Airflow", "orquestación", "chart 1.22.0"], ["Spark", "sobre Kubernetes", "versión 3.5.9"],
    ["MinIO + Iceberg", "almacenamiento", "chart 17.0.21 · Iceberg 1.11.0"], ["PostgreSQL", "capa gold", "chart 18.11.3"], ["Superset", "visualización", "chart de Helm"]];
  nodes.forEach((nd, i) => {
    const x = L + i * (aw + ag);
    card(s, x, 1.8, aw, 1.55, "Servicio " + nd[0]);
    txt(s, nd[0], { x: x + 0.1, y: 1.9, w: aw - 0.2, h: 0.45, fontSize: 16, bold: true, align: "center" });
    txt(s, nd[1], { x: x + 0.1, y: 2.35, w: aw - 0.2, h: 0.35, fontSize: 15, color: C.accent6, align: "center" });
    mono(s, nd[2], { x: x + 0.1, y: 2.75, w: aw - 0.2, h: 0.5, fontSize: 11, color: C.accent3, align: "center" });
    if (i < nodes.length - 1) arrowRight(s, x + aw + 0.03, 2.6, ag - 0.06, "Flecha servicio " + (i + 1));
  });
  card(s, L, 3.55, W, 1.3, "Banda del cluster y namespace");
  mono(s, "k3s v1.36.4 · un único nodo local", { x: L + 0.3, y: 3.65, w: W - 0.6, h: 0.3, fontSize: 13, color: C.accent6 });
  txt(s, points([["Namespace tfm-lakehouse.", "Espacio dentro del clúster que agrupa y aísla todos los recursos de la plataforma: pods, servicios y secretos."]]),
    { x: L + 0.3, y: 4.0, w: W - 0.6, h: 0.75, fontSize: 16 });
  [["Un pod por tarea", "Airflow usa KubernetesExecutor: cada tarea y cada trabajo de Spark se lanza como un pod propio dentro del namespace."],
   ["Reproducible con Helm", "Helm es el gestor de paquetes de Kubernetes. Cada servicio se instala desde un chart, con las versiones de cada imagen fijadas."],
   ["Mecanismo verificado", "Antes de construir los flujos se comprobó que Spark, lanzado desde Airflow, escribe y lee tablas Iceberg en MinIO."]].forEach((c, i) => {
    const x = L + i * (iw + GAP);
    card(s, x, 5.05, iw, 1.65, "Nota " + (i + 1));
    txt(s, c[0], { x: x + 0.2, y: 5.12, w: iw - 0.4, h: 0.35, fontSize: 16, bold: true, color: C.accent1 });
    txt(s, c[1], { x: x + 0.2, y: 5.5, w: iw - 0.4, h: 1.15, fontSize: 14 });
  });

  // ---- 10. Almacenamiento: dentro y fuera de Iceberg ---------------------------------------
  s = newSlide("CONTENIDO", BL[3], K(4), "Almacenamiento: dentro y fuera de Iceberg", "1:10");
  mono(s, "ORGANIZACIÓN DEL CUBO lakehouse EN MINIO", { x: L, y: 1.75, w: 6.1, h: 0.3, fontSize: 11 });
  s.addShape(SH.rect, { x: L, y: 2.1, w: 6.2, h: 4.55, fill: { color: C.text1 }, line: { color: C.accent2, width: 1.25 }, objectName: "Cubo lakehouse" });
  // zona fuera de Iceberg
  s.addShape(SH.rect, { x: L + 0.2, y: 2.3, w: 2.2, h: 4.15, fill: { color: C.text2 }, line: { color: C.accent3, width: 1.25, dashType: "dash" }, objectName: "Zona fuera de Iceberg" });
  mono(s, "FUERA DE ICEBERG", { x: L + 0.2, y: 2.4, w: 2.2, h: 0.3, fontSize: 11, color: C.accent3, align: "center" });
  s.addShape(SH.rect, { x: L + 0.4, y: 2.85, w: 1.8, h: 1.9, fill: { color: C.text1 }, line: { color: PAL.bronze, width: 2 }, objectName: "bronze fuera de Iceberg" });
  mono(s, "bronze/", { x: L + 0.4, y: 2.95, w: 1.8, h: 0.35, fontSize: 14, bold: true, color: PAL.bronze, align: "center" });
  txt(s, "Ficheros crudos (JSON Lines), tal como llegan de las fuentes", { x: L + 0.5, y: 3.35, w: 1.6, h: 1.3, fontSize: 13, color: C.accent6, align: "center" });
  // zona dentro de Iceberg
  s.addShape(SH.rect, { x: L + 2.6, y: 2.3, w: 3.4, h: 4.15, fill: { color: C.text2 }, line: { color: C.accent1, width: 1.75 }, objectName: "Zona dentro de Iceberg" });
  mono(s, "DENTRO DE ICEBERG", { x: L + 2.6, y: 2.4, w: 3.4, h: 0.3, fontSize: 11, color: C.accent1, align: "center" });
  mono(s, "warehouse/ · catálogo", { x: L + 2.6, y: 2.72, w: 3.4, h: 0.3, fontSize: 12, bold: true, color: C.accent6, align: "center" });
  [["lakehouse.bronze", "reservado, sin tablas", PAL.bronze, true], ["lakehouse.silver", "tablas Iceberg", PAL.silver, false], ["lakehouse.gold", "tablas Iceberg", PAL.gold, false]].forEach((nsb, i) => {
    const y = 3.15 + i * 1.07;
    s.addShape(SH.rect, { x: L + 2.8, y, w: 3.0, h: 0.92, fill: { color: C.text1 }, line: { color: nsb[2], width: 2, dashType: nsb[3] ? "dash" : "solid" }, objectName: "Namespace " + nsb[0] });
    mono(s, nsb[0], { x: L + 2.8, y: y + 0.1, w: 3.0, h: 0.35, fontSize: 13, bold: true, color: nsb[2], align: "center" });
    txt(s, nsb[1], { x: L + 2.8, y: y + 0.48, w: 3.0, h: 0.35, fontSize: 13, color: C.accent6, align: "center" });
  });
  card(s, 7.0, 1.8, 5.73, 2.75, "Por que se separan");
  mono(s, "POR QUÉ SE SEPARAN", { x: 7.25, y: 1.9, w: 5.2, h: 0.3, fontSize: 11 });
  txt(s, points([
    ["Fuera:", "los ficheros crudos los escriben directamente las tareas de ingesta, sin pasar por Iceberg."],
    ["Dentro:", "solo hay tablas gestionadas por el catálogo, que escriben los trabajos de Spark."],
    ["Separados", "para que Iceberg no encuentre ficheros ajenos entre sus tablas."],
    ["Bronze:", "el real es el de fuera; el namespace bronze del catálogo está reservado, pero el pipeline lee los ficheros directamente."],
  ]), { x: 7.25, y: 2.25, w: 5.25, h: 2.25, fontSize: 14 });
  card(s, 7.0, 4.7, 5.73, 1.25, "Imagenes y versiones fijadas");
  txt(s, points([["Imágenes y versiones fijadas.", "Las de MinIO y PostgreSQL se obtienen de forma gratuita; las de Spark, Iceberg y Hadoop son compatibles entre sí."]]),
    { x: 7.25, y: 4.78, w: 5.25, h: 1.1, fontSize: 14, valign: "middle" });
  card(s, 7.0, 6.05, 5.73, 0.65, "WSL2");
  txt(s, points([["WSL2.", "k3s necesita systemd y la red host-gw."]]), { x: 7.25, y: 6.05, w: 5.25, h: 0.65, fontSize: 14, valign: "middle" });

  // ---- 11. Datos de partida -----------------------------------------------------------------
  pres.addSection({ title: BL[4] });
  s = newSlide("CONTENIDO", BL[4], K(5), "ORCID aporta el volumen y los CVN, el enlace", "1:20");
  const colw = 5.98, colX = [L, L + colw + 0.17];
  [
    { h: "ORCID · DATOS REALES", b: [["API pública:", "consulta un perfil concreto por su identificador, para actualizar los datos de las personas que declaran los CVN."], ["Fichero anual:", "volcado de todos los perfiles públicos. Da el volumen real de partida."]],
      st: [["26.078.951", "perfiles en el fichero de ORCID"], ["301.763", "perfiles con afiliación en España, los que nos quedamos"]] },
    { h: "CVN · GENERADOS A PARTIR DE ORCID", b: [["Generación:", "parte de los perfiles filtrados y reutiliza su nombre, afiliaciones y obras públicas."], ["Enlace:", "el 70 % declara el ORCID del perfil de origen; el resto solo conserva nombre y afiliaciones."]],
      st: [["10.000", "CVN para evaluar la fusión a escala (por defecto, 1.000)"], ["70 %", "declaran el ORCID del perfil del que parten"]] },
  ].forEach((c, i) => {
    const x = colX[i];
    card(s, x, 1.8, colw, 3.4, "Columna " + c.h);
    mono(s, c.h, { x: x + 0.3, y: 1.9, w: colw - 0.6, h: 0.3, fontSize: 11 });
    txt(s, points(c.b), { x: x + 0.3, y: 2.25, w: colw - 0.6, h: 1.35, fontSize: 14 });
    c.st.forEach((st, j) => {
      const sx = x + 0.3 + j * 2.7;
      s.addShape(SH.rect, { x: sx, y: 3.65, w: 2.55, h: 1.4, fill: { color: C.text1 }, line: { color: C.accent2, width: 0.75 }, objectName: "Dato " + st[0] });
      txt(s, st[0], { x: sx + 0.15, y: 3.7, w: 2.25, h: 0.55, fontSize: 26, bold: true, color: C.accent1 });
      txt(s, st[1], { x: sx + 0.15, y: 4.28, w: 2.25, h: 0.75, fontSize: 13, color: C.accent6 });
    });
  });
  mono(s, "TRES TÉRMINOS QUE SE USAN EN ADELANTE", { x: L, y: 5.32, w: 8, h: 0.3, fontSize: 11 });
  [["Perfil", "Ficha pública de una persona en ORCID: nombre, afiliaciones y obras."],
   ["Registro", "Cada documento que se guarda en bronze: un perfil de ORCID, una respuesta de la API o un CVN."],
   ["Publicación", "Una obra (artículo, libro…) que figura dentro de un perfil o de un CVN."]].forEach((d, i) => {
    const x = L + i * (iw + GAP);
    card(s, x, 5.65, iw, 1.1, "Definicion " + d[0]);
    txt(s, points([[d[0] + ":", d[1]]]), { x: x + 0.2, y: 5.7, w: iw - 0.4, h: 1.0, fontSize: 13, valign: "middle" });
  });

  // ---- 12. Bronze con procedencia -------------------------------------------------------------
  s = newSlide("CONTENIDO", BL[4], K(5), "Todo aterriza en bronze con su procedencia", "1:10");
  mono(s, "FLUJO ingest_validate · UN POD POR TAREA", { x: L, y: 1.8, w: 5.6, h: 0.3, fontSize: 11 });
  ["Subconjunto ORCID masivo", "Generación de CVN", "Enriquecimiento vía API de ORCID", "Validación y aterrizaje en bronze"].forEach((tk, i, arr) => {
    const y = 2.2 + i * 1.1;
    card(s, L, y, 5.3, 0.75, "Tarea " + (i + 1));
    mono(s, String(i + 1), { x: L + 0.2, y, w: 0.4, h: 0.75, fontSize: 18, valign: "middle" });
    txt(s, tk, { x: L + 0.7, y, w: 4.4, h: 0.75, fontSize: 16, bold: true, valign: "middle" });
    if (i < arr.length - 1) arrowDown(s, L + 2.65, y + 0.78, 0.29, "Flecha tarea " + (i + 1));
  });
  txt(s, points([
    ["Procedencia.", "Cada registro lleva consigo de qué fuente viene, cuándo se obtuvo y se guardó, qué ejecución lo guardó y si superó la comprobación."],
    ["Límite por ejecución.", "Se procesan 20.000 de los 301.763 perfiles filtrados, para mantener cada ejecución en un tamaño manejable. Es configurable."],
    ["Rechazos.", "Los registros rechazados van a una zona aparte con sus errores. Si superan el 5 % de una fuente, la tarea falla."],
  ]), { x: 6.4, y: 1.8, w: 6.33, h: 2.75, fontSize: 14 });
  [["19.469", "registros ORCID aceptados de los 20.000 procesados"], ["531", "registros rechazados"], ["1.000", "CVN por defecto (10.000 en la evaluación)"]].forEach((st, i) => {
    stat(s, 6.4 + i * 2.18, 4.65, 1.97, 2.0, st[0], st[1], "Cifra " + st[0]);
  });

  // ---- 13. Silver -------------------------------------------------------------------------------
  pres.addSection({ title: BL[5] });
  s = newSlide("CONTENIDO", BL[5], K(6), "Silver: solo entra lo validado, con rastro", "1:15");
  const vw = (W - 2 * 0.5) / 3;
  [["COMPROBACIÓN 1 · FORMATO", "Formato", "El documento cumple el esquema Open CVN"], ["COMPROBACIÓN 2 · CONTENIDO", "Contenido", "Cada elemento (publicación, formación…) tiene los campos propios de su tipo"], ["COMPROBACIÓN 3 · REGLAS", "Reglas", "ORCID con dígito de control válido y fechas coherentes"]].forEach((v, i) => {
    const x = L + i * (vw + 0.5);
    card(s, x, 1.8, vw, 1.6, "Comprobacion " + (i + 1));
    mono(s, v[0], { x: x + 0.2, y: 1.9, w: vw - 0.4, h: 0.25, fontSize: 10 });
    txt(s, v[1], { x: x + 0.2, y: 2.18, w: vw - 0.4, h: 0.4, fontSize: 19, bold: true });
    txt(s, v[2], { x: x + 0.2, y: 2.62, w: vw - 0.4, h: 0.75, fontSize: 14, color: C.accent6 });
    if (i < 2) arrowRight(s, x + vw + 0.05, 2.6, 0.4, "Flecha comprobacion " + (i + 1));
  });
  card(s, L, 3.55, 7.5, 1.6, "Normalizacion");
  mono(s, "NORMALIZACIÓN: PARA PODER COMPARAR", { x: L + 0.25, y: 3.63, w: 6, h: 0.25, fontSize: 11 });
  txt(s, points([
    ["Nombres:", "sin acentos ni partículas. «de la Torre, Ana» pasa a la clave «torre, a»."],
    ["Organizaciones:", "solo las palabras con significado, sin importar el orden. «Universidad de Granada» y «Granada, Universidad de» quedan iguales."],
  ]), { x: L + 0.25, y: 3.95, w: 7.0, h: 1.15, fontSize: 14 });
  card(s, L + 7.65, 3.55, W - 7.65, 1.6, "Rechazados");
  mono(s, "LO QUE FALLA", { x: L + 7.9, y: 3.63, w: 3, h: 0.25, fontSize: 11 });
  txt(s, "Va a una tabla de rechazados con la regla incumplida. Si supera el 5 % de una fuente, el trabajo falla.",
    { x: L + 7.9, y: 3.95, w: W - 8.15, h: 1.15, fontSize: 14 });
  const sw4 = (W - 3 * GAP) / 4;
  [["30.868", "registros de persona: 19.469 ORCID, 399 API y 11.000 CVN"], ["99.979", "afiliaciones dentro de esos registros"], ["543.879", "publicaciones dentro de esos registros"], ["0", "registros rechazados"]].forEach((st, i) => {
    stat(s, L + i * (sw4 + GAP), 5.3, sw4, 1.5, st[0], st[1], "Cifra silver " + st[0]);
  });

  // ---- 14. Resolucion de identidad ----------------------------------------------------------------
  s = newSlide("CONTENIDO", BL[5], K(6), "Fusión de identidades: precisión medida", "1:30");
  const lw = 5.7;
  card(s, L, 1.8, lw, 1.05, "Regla R1");
  mono(s, "R1 · EVIDENCIA FUERTE", { x: L + 0.2, y: 1.88, w: 5, h: 0.25, fontSize: 11 });
  txt(s, "Mismo identificador ORCID válido: fusiona.", { x: L + 0.2, y: 2.2, w: lw - 0.4, h: 0.55, fontSize: 14 });
  card(s, L, 3.0, lw, 2.55, "Regla R2");
  mono(s, "R2 · CVN SIN ORCID", { x: L + 0.2, y: 3.08, w: 5, h: 0.25, fontSize: 11 });
  txt(s, "Busca una persona ya identificada por R1 que cumpla todo esto:", { x: L + 0.2, y: 3.38, w: lw - 0.4, h: 0.3, fontSize: 14 });
  txt(s, bullets([
    "Misma clave de bloqueo: apellido normalizado + inicial del nombre",
    "Nombre compatible: puede variar el nombre o el apellido, no ambos",
    "Alguna organización en común",
    "Una única candidata",
  ], { paraSpaceAfter: 3 }), { x: L + 0.2, y: 3.72, w: lw - 0.4, h: 1.75, fontSize: 14 });
  card(s, L, 5.7, lw, 0.95, "Regla R3");
  mono(s, "R3 · SIN EVIDENCIA", { x: L + 0.2, y: 5.78, w: 5, h: 0.25, fontSize: 11 });
  txt(s, "Ninguna de las anteriores: entidad propia.", { x: L + 0.2, y: 6.1, w: lw - 0.4, h: 0.5, fontSize: 14 });
  const rx = L + lw + 0.2, rwid = W - lw - 0.2;
  const tc = (t, o) => ({ text: t, options: Object.assign({ fontSize: 15, color: C.background1, align: "center", fill: { color: C.text2 } }, o) });
  const th = (t) => ({ text: t, options: { fontFace: MONO, fontSize: 11, bold: true, color: C.accent1, align: "center", fill: { color: C.text1 } } });
  s.addTable([
    [th("REGLA"), th("EVALUABLES"), th("CORRECTAS"), th("PRECISIÓN"), th("COBERTURA")],
    [tc("R1", { bold: true }), tc("7.098"), tc("7.098"), tc("100 %", { bold: true, color: C.accent4 }), tc("100 %", { bold: true, color: C.accent4 })],
    [tc("R2", { bold: true }), tc("186"), tc("138"), tc("95,8 %", { bold: true, color: C.accent1 }), tc("74,2 %", { bold: true, color: C.accent1 })],
  ], { x: rx, y: 1.8, w: rwid, colW: [0.8, 1.35, 1.25, 1.3, rwid - 4.7], rowH: 0.5, margin: [0, 0.05, 0, 0.05], valign: "middle",
    border: { type: "solid", pt: 0.75, color: PAL.border }, objectName: "Resultados de la resolucion" });
  mono(s, "SOBRE 10.000 CVN · VERDAD DE REFERENCIA DEL GENERADOR", { x: rx, y: 3.38, w: rwid, h: 0.25, fontSize: 10, color: C.accent3 });
  card(s, rx, 3.75, rwid, 1.45, "Definiciones");
  txt(s, points([
    ["Precisión:", "de las fusiones que hace R2, cuántas son correctas (138 de 144)."],
    ["Cobertura:", "de los casos que R2 puede resolver, cuántos resuelve (138 de 186)."],
  ]), { x: rx + 0.2, y: 3.85, w: rwid - 0.4, h: 1.3, fontSize: 14, valign: "middle" });
  card(s, rx, 5.35, rwid, 1.3, "Resultado frente al objetivo");
  txt(s, points([
    ["Objetivo:", "el 99 % de precisión no se alcanza en R2."],
    ["Cobertura:", "47 de los 186 casos no tienen afiliación y R2 necesita una organización para comparar."],
  ]), { x: rx + 0.2, y: 5.4, w: rwid - 0.4, h: 1.2, fontSize: 14, valign: "middle" });

  // ---- 15. Gold -----------------------------------------------------------------------------------------
  s = newSlide("CONTENIDO", BL[5], K(6), "Gold: indicadores publicados de forma atómica", "1:15");
  [["I1", "Publicaciones por año"], ["I2", "Pares de colaboración entre personas que comparten una obra"], ["I3", "Línea temporal de afiliaciones"]].forEach((d, i) => {
    const x = L + i * (iw + GAP);
    card(s, x, 1.8, iw, 1.2, "Indicador " + d[0]);
    mono(s, d[0], { x: x + 0.25, y: 1.88, w: 1, h: 0.3, fontSize: 15 });
    txt(s, d[1], { x: x + 0.25, y: 2.2, w: iw - 0.5, h: 0.75, fontSize: 15, bold: true });
  });
  mono(s, "COPIA DE GOLD A POSTGRESQL: SUPERSET LEE DE AHÍ DIRECTAMENTE, SIN MOTOR DE CONSULTA INTERMEDIO", { x: L, y: 3.15, w: W, h: 0.25, fontSize: 11, color: C.accent3 });
  [["1 · Carga aparte", "Los datos nuevos se cargan en tablas temporales, sin tocar las ya publicadas."],
   ["2 · Comprobación", "Se verifica que PostgreSQL tiene las mismas filas que gold en Iceberg."],
   ["3 · Intercambio único", "Las tablas nuevas sustituyen a las anteriores en una sola transacción: el panel nunca queda vacío ni a medio cargar."]].forEach((p, i) => {
    const x = L + i * (iw + GAP);
    s.addShape(SH.rect, { x, y: 3.5, w: iw, h: 1.45, fill: { color: C.text1 }, line: { color: C.accent2, width: 1 }, objectName: "Paso " + (i + 1) });
    txt(s, p[0], { x: x + 0.2, y: 3.58, w: iw - 0.4, h: 0.35, fontSize: 15, bold: true, color: C.accent1 });
    txt(s, p[1], { x: x + 0.2, y: 3.97, w: iw - 0.4, h: 0.95, fontSize: 14 });
  });
  [["5,1 %", "de publicaciones se contaría de más sin deduplicar: una misma obra figura en el CVN y en el perfil ORCID de la persona"],
   ["0", "discrepancias en 306.599 filas frente a un recálculo independiente"],
   ["0,58 %", "desplazamiento máximo al deshacer las fusiones de R2 con evidencia más débil"]].forEach((st, i) => {
    stat(s, L + i * (iw + GAP), 5.1, iw, 1.65, st[0], st[1], "Cifra gold " + (i + 1));
  });

  // ---- 16. Panel -------------------------------------------------------------------------------------------
  pres.addSection({ title: BL[6] });
  s = newSlide("CONTENIDO", BL[6], K(7), "Panel de indicadores sin estados intermedios", "1:10");
  s.addShape(SH.rect, { x: L, y: 1.8, w: 8.1, h: 3.98, fill: { color: PAL.white }, line: { color: C.accent2, width: 1 }, objectName: "Placa de la figura" });
  s.addImage({ path: path.join(FIGS, "panel_superset.png"), x: L + 0.1, y: 1.9, w: 7.9, h: 7.9 / 2.0908, altText: "Panel de Superset con publicaciones por año, afiliaciones, pares de colaboración y procedencia", objectName: "Captura del panel" });
  txt(s, points([
    ["Solo agregados,", "nunca nombres de personas."],
    ["Superset consulta PostgreSQL,", "no Iceberg ni Spark: se conecta a ella directamente. Leer Iceberg exigiría un motor de consulta intermedio, como Trino o Spark."],
  ], { paraSpaceAfter: 4 }), { x: L, y: 5.9, w: 8.1, h: 0.85, fontSize: 13 });
  mono(s, "EL PANEL MUESTRA", { x: 9.0, y: 1.8, w: 3.7, h: 0.3 });
  txt(s, bullets(["Publicaciones por año", "Línea temporal de afiliaciones", "Colaboraciones solo entre datos reales de ORCID", "Procedencia de la ejecución"]),
    { x: 9.0, y: 2.2, w: 3.73, h: 2.4, fontSize: 16 });
  stat(s, 9.0, 4.75, 3.73, 1.95, "1.040 s", "y 238 consultas durante una ejecución completa, sin errores ni respuestas vacías", "Cifra panel");

  // ---- 17. Benchmark ------------------------------------------------------------------------------------------
  s = newSlide("CONTENIDO", BL[6], K(7), "Más ejecutores dan fiabilidad, no solo velocidad", "1:20");
  card(s, L, 1.8, 6.6, 1.85, "Como se midio");
  mono(s, "CÓMO SE MIDIÓ", { x: L + 0.25, y: 1.88, w: 5, h: 0.25, fontSize: 11 });
  txt(s, bullets([
    "Tres volúmenes de datos (1x, 2x y 4x), con 1, 2 y 4 ejecutores en cada uno",
    "Primera ejecución de cada volumen descartada (calentamiento)",
    "Tres repeticiones, intercaladas entre configuraciones",
    "Mismo contenido final en todas las configuraciones comparables",
  ], { paraSpaceAfter: 3 }), { x: L + 0.25, y: 2.18, w: 6.15, h: 1.4, fontSize: 14 });
  card(s, L, 3.8, 6.6, 2.9, "Marco del grafico");
  s.addChart(pres.charts.BAR, [
    { name: "Validación y normalización (silver)", labels: ["1 ejecutor", "2 ejecutores", "4 ejecutores"], values: [1.0, 0.75, 0.41] },
    { name: "Cálculo de indicadores (gold)", labels: ["1 ejecutor", "2 ejecutores", "4 ejecutores"], values: [1.0, 0.53, 0.23] },
  ], {
    x: L + 0.1, y: 3.85, w: 6.4, h: 2.8, barDir: "col", barGapWidthPct: 60, chartColors: [PAL.chartA, PAL.chartB],
    showTitle: true, title: "Eficiencia = aceleración ÷ ejecutores (1,0 = ideal)", titleColor: PAL.chartText, titleFontSize: 12, titleFontFace: "Calibri",
    showValue: true, dataLabelPosition: "outEnd", dataLabelColor: PAL.chartText, dataLabelFontSize: 11, dataLabelFormatCode: "0.00", dataLabelFontFace: "Calibri",
    catAxisLabelColor: PAL.chartText, catAxisLabelFontSize: 12, catAxisLabelFontFace: "Calibri",
    valAxisLabelColor: PAL.chartMuted, valAxisLabelFontSize: 11, valAxisLabelFontFace: "Calibri", valAxisMinVal: 0, valAxisMaxVal: 1.2, valAxisMajorUnit: 0.4, valAxisLabelFormatCode: "0.0",
    valGridLine: { color: PAL.grid, size: 0.75 }, catGridLine: { style: "none" }, catAxisLineShow: false,
    showLegend: true, legendPos: "b", legendColor: PAL.chartText, legendFontSize: 11, legendFontFace: "Calibri",
    plotArea: { fill: { color: "1A3556", transparency: 100 } },
  });
  [["1,50 → 1,63", "Aceleración de silver con 2 y 4 ejecutores respecto a 1; la ideal sería 2 y 4.", true],
   ["Fiabilidad", "Con el doble de datos, un solo ejecutor agota la memoria en silver. Con el cuádruple de datos hacen falta cuatro ejecutores.", false],
   ["Cuello de botella", "Las limitaciones de hardware del único nodo local: la CPU no pasó del 32,2 % y el pico coincidió con cuatro ejecutores.", false]].forEach((b, i) => {
    const y = 1.8 + i * 1.65;
    card(s, 7.45, y, 5.28, 1.5, "Hallazgo rendimiento " + (i + 1));
    txt(s, b[0], { x: 7.7, y: y + 0.1, w: 4.8, h: 0.5, fontSize: b[2] ? 26 : 19, bold: true, color: C.accent1 });
    txt(s, b[1], { x: 7.7, y: y + 0.65, w: 4.8, h: 0.82, fontSize: 14, color: C.accent6 });
  });

  // ---- 18. Endurecimiento -----------------------------------------------------------------------------------------
  s = newSlide("CONTENIDO", BL[6], K(7), "Endurecimiento: fallos reales corregidos", "1:00");
  [["Bloqueo del orquestador", "ERROR DE AIRFLOW SIN CORRECCIÓN", "Fallo conocido al reconciliar una tarea huérfana. Receta operativa: marcarla como fallida y reiniciar. Reapareció días después y se resolvió igual."],
   ["Interfaz de Airflow bajo carga", "SIN RESERVA DE RECURSOS", "Su comprobación de salud lo reiniciaba. Solución: reserva explícita de CPU y memoria y tiempos de salud más holgados."],
   ["PostgreSQL sin usuario gold", "HALLADO AL RECONSTRUIR", "Un primer arranque interrumpido no se reintenta. Solución: reinicializar el servicio."]].forEach((h, i) => {
    const x = L + i * (iw + GAP);
    card(s, x, 1.85, iw, 3.3, "Fallo " + (i + 1));
    mono(s, h[1], { x: x + 0.25, y: 2.0, w: iw - 0.5, h: 0.3, fontSize: 10, color: C.accent3 });
    txt(s, h[0], { x: x + 0.25, y: 2.35, w: iw - 0.5, h: 0.75, fontSize: 18, bold: true, color: C.accent1 });
    txt(s, h[2], { x: x + 0.25, y: 3.15, w: iw - 0.5, h: 1.9, fontSize: 14, color: C.accent6 });
  });
  card(s, L, 5.4, W, 1.25, "Reconstruccion desde cero");
  mono(s, "RECONSTRUCCIÓN DESDE CERO", { x: L + 0.3, y: 5.5, w: 6, h: 0.25, fontSize: 11 });
  txt(s, "Solo con la guía escrita y en un clúster k3d aislado con la misma versión de Kubernetes, ambos flujos y el panel funcionaron de extremo a extremo sin tocar el clúster real.",
    { x: L + 0.3, y: 5.8, w: W - 0.6, h: 0.8, fontSize: 16 });

  // ---- 19. Garantias fuertes y parciales ----------------------------------------------------------------------------
  s = newSlide("CONTENIDO", BL[6], K(7), "Garantías fuertes donde el proceso es determinista", "1:10");
  const strong = ["Mecanismo central: Spark desde Airflow sobre Iceberg y MinIO, comprobado con el registro del trabajo y con la lectura desde otro pod",
    "Ingesta: una lectura independiente con Spark coincide con los recuentos",
    "Gold: 0 discrepancias en 306.599 filas y segunda ejecución idéntica",
    "Publicación: matar el proceso a mitad dejó lo publicado intacto",
    "Reproducibilidad: reconstrucción desde cero con solo la guía escrita"];
  const partial = ["Identidad sin ORCID: 95,8 % de precisión y 74,2 % de cobertura",
    "Rendimiento limitado por el hardware del único nodo local",
    "Fallo del orquestador sin corrección oficial, resuelto con una receta operativa",
    "Alcance deliberado: un nodo local y reconstrucción completa de silver y gold en cada ejecución"];
  [["GARANTÍAS FUERTES Y VERIFICADAS", strong, C.accent4], ["GARANTÍAS PARCIALES Y DOCUMENTADAS", partial, C.accent1]].forEach((c, i) => {
    const x = L + i * (mw + GAP);
    card(s, x, 1.85, mw, 4.2, "Columna " + c[0]);
    mono(s, c[0], { x: x + 0.3, y: 2.0, w: mw - 0.6, h: 0.3, color: c[2] });
    txt(s, bullets(c[1], { paraSpaceAfter: 8 }), { x: x + 0.3, y: 2.5, w: mw - 0.6, h: 3.4, fontSize: 15 });
  });
  txt(s, "Las cifras proceden de un único nodo local: el despliegue en un clúster real y el estudio de cómo escalar quedan completamente como trabajo futuro.",
    { x: L, y: 6.15, w: W, h: 0.6, fontSize: 16, italic: true, color: C.accent3, valign: "middle" });

  // ---- 20. Conclusiones: objetivos y contribuciones -------------------------------------------------------------------
  pres.addSection({ title: BL[7] });
  s = newSlide("CONTENIDO", BL[7], K(8), "Ocho objetivos cumplidos y uno parcial", "1:15");
  ["Infraestructura", "Mecanismo central", "ORCID real", "CVN", "Fusión de fuentes", "Indicadores", "Panel", "Benchmark", "Robustez"].forEach((o, i) => {
    const x = L + (i % 3) * 2.15, y = 1.85 + Math.floor(i / 3) * 1.1;
    const part = i === 4;
    card(s, x, y, 2.0, 1.0, "Estado OE" + (i + 1));
    mono(s, "OE" + (i + 1), { x: x + 0.15, y: y + 0.08, w: 0.8, h: 0.25, fontSize: 11 });
    mono(s, part ? "PARCIAL" : "CUMPLIDO", { x: x + 0.7, y: y + 0.08, w: 1.2, h: 0.25, fontSize: 10, align: "right", color: part ? C.accent1 : C.accent4 });
    txt(s, o, { x: x + 0.15, y: y + 0.4, w: 1.75, h: 0.55, fontSize: 14, bold: true });
  });
  txt(s, "OE5: la regla sin ORCID llega al 95,8 % de precisión y al 74,2 % de cobertura, por debajo del 99 % fijado. El objetivo general se considera cumplido.",
    { x: L, y: 5.2, w: 6.3, h: 1.3, fontSize: 14, color: C.accent3 });
  card(s, 7.2, 1.85, 5.53, 4.8, "Contribuciones");
  mono(s, "CONTRIBUCIONES", { x: 7.45, y: 2.0, w: 5, h: 0.3 });
  txt(s, bullets(["Plataforma lakehouse verificada de extremo a extremo", "Fusión ORCID y CVN diseñada desde el origen del dato",
    "Resolución de identidad determinista, con evidencia auditable", "El número de ejecutores de Spark es palanca de fiabilidad, no solo de velocidad",
    "Guía de reproducibilidad validada con una reconstrucción real"], { paraSpaceAfter: 10 }), { x: 7.45, y: 2.45, w: 5.05, h: 4.0, fontSize: 16 });

  // ---- 21. Conclusion y trabajo futuro ------------------------------------------------------------------------------------
  s = newSlide("CONTENIDO", BL[7], K(8), "Conclusión y líneas de trabajo futuro", "1:05");
  card(s, L, 1.85, 6.2, 4.8, "Conclusion");
  mono(s, "CONCLUSIÓN", { x: L + 0.3, y: 2.0, w: 5, h: 0.3 });
  txt(s, "Este trabajo demuestra, con una plataforma desplegada y medida, que ORCID y CVN pueden integrarse en un lakehouse autoalojado y reproducible, con la identidad resuelta entre fuentes y con evidencia reproducible de su rendimiento y su robustez.",
    { x: L + 0.3, y: 2.45, w: 5.6, h: 2.8, fontSize: 19, bold: true });
  txt(s, "Las limitaciones proceden de un componente externo o son decisiones deliberadas de alcance.",
    { x: L + 0.3, y: 5.4, w: 5.6, h: 1.1, fontSize: 15, color: C.accent3 });
  mono(s, "TRABAJO FUTURO", { x: 7.1, y: 1.9, w: 5, h: 0.3 });
  ["Despliegue en un clúster real y estudio de cómo escalar", "Incorporar la corrección oficial del orquestador cuando exista",
    "Motor de consulta SQL sobre Iceberg (como Trino): consultar gold sin copiarlo a PostgreSQL",
    "Monitorización permanente en producción: métricas, registros y alertas", "Procesamiento incremental sobre snapshots de Iceberg", "Vinculación probabilística o con aprendizaje automático"].forEach((f, i) => {
    const y = 2.3 + i * 0.72;
    card(s, 7.1, y, 5.63, 0.62, "Trabajo futuro " + (i + 1));
    mono(s, String(i + 1), { x: 7.3, y, w: 0.4, h: 0.62, fontSize: 16, valign: "middle" });
    txt(s, f, { x: 7.8, y, w: 4.8, h: 0.62, fontSize: 14, valign: "middle" });
  });

  // ---- 22. Cierre ----------------------------------------------------------------------------------------------------------------
  s = newSlide("PORTADA", BL[7], null, null, "0:00");
  mono(s, "FIN DE LA EXPOSICIÓN · TURNO DE PREGUNTAS", { x: 0.8, y: 2.3, w: 10, h: 0.35, fontSize: 14, charSpacing: 3 });
  txt(s, "Gracias", { x: 0.8, y: 2.8, w: 10, h: 1.4, fontSize: 66, bold: true, objectName: "Agradecimiento" });
  txt(s, "Arquitectura lakehouse escalable para la integración y análisis de información curricular académica",
    { x: 0.8, y: 4.4, w: 8.5, h: 0.9, fontSize: 18, color: C.accent3 });
  txt(s, "Carlos Martínez Jaén", { x: 0.8, y: 5.45, w: 8, h: 0.4, fontSize: 18, bold: true });

  await pres.writeFile({ fileName: OUT });
  if (SKILL_THEME) {
    const { applyTheme } = require(SKILL_THEME);
    await applyTheme(OUT, THEME);
  }
  if (process.env.SHOW_TIMES) {
    NOTES.forEach((x, i) => {
      const words = x.p.join(" ").split(/\s+/).length;
      console.log(i + 1, words + " pal", "~" + Math.round(words / 150 * 60) + " s", "asignado " + durations[i] + " s");
    });
    console.log("total asignado", Math.floor(durations.reduce((a, b) => a + b, 0) / 60), "min", durations.reduce((a, b) => a + b, 0) % 60);
  }
  console.log("OK", OUT, n, "diapositivas");
}
main().catch((e) => { console.error(e); process.exit(1); });
