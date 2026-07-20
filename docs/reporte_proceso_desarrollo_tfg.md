# Reporte del proceso de desarrollo del TFG

## 1. Planteamiento general

El TFG parte del problema de que, aunque el CVN es el formato normalizado en
Espana para representar curriculos academicos y de investigacion, su uso sigue
siendo dificil de automatizar. La elaboracion, mantenimiento, validacion,
adaptacion y exportacion de curriculos requiere todavia mucho trabajo manual.

El objetivo general del proyecto ha sido definir una base abierta y reproducible
para representar, validar, transformar, almacenar y exportar curriculos tomando
CVN como punto de partida, pero evitando que el XML oficial condicione todo el
modelo interno.

El resultado se ha desarrollado como una arquitectura por capas que separa:

- estructura XML oficial
- semantica curricular
- trazabilidad hacia CVN
- modelo conceptual agnostico
- formato JSON abierto
- parser y validador
- aplicacion local de gestion curricular

## 2. Investigacion inicial y estado del arte

Antes de empezar la implementacion se realizo una investigacion inicial sobre el
estado del arte en representacion de informacion curricular compleja. Esta fase
esta recogida en `docs/research/latex_project/representacion_datos_complejos.tex`
y sirvio para justificar por que el proyecto no debia limitarse a copiar CVN-XML,
ni tampoco adoptar directamente una infraestructura semantica pesada.

El primer bloque de investigacion estudio la propia norma CVN. Se identifico que
CVN funciona como un estandar para unificar la presentacion de datos curriculares
de investigadores y facilitar la interoperabilidad con bases de datos de
instituciones. Tambien se analizo el funcionamiento practico del editor CVN de
FECYT: el usuario genera un PDF que representa visualmente el curriculum, pero
ese PDF lleva incrustado un XML con la informacion estructurada. Ese XML permite
procesamiento automatico sin depender del texto visible del PDF. Ademas, el
documento puede estar firmado digitalmente por FECYT, lo que garantiza que sigue
la norma, pero tambien implica que las modificaciones deben hacerse a traves del
editor oficial si se quiere preservar esa validez.

Esta investigacion inicial detecto dos implicaciones importantes para el TFG:

- el XML embebido en PDF es una fuente mas fiable que el texto visible del PDF
- modificar directamente el PDF o reconstruirlo sin pasar por el flujo oficial
  puede romper la garantia de conformidad con CVN

### 2.1. Modelos conceptuales estudiados

Se estudiaron varios modelos conceptuales relacionados con informacion de
investigacion:

- CERIF: estandar europeo para gestion e intercambio de informacion de
  investigacion en sistemas CRIS, con un modelo muy normalizado y orientado a
  interoperabilidad institucional
- VIVO: ontologia basada en RDF y Web Semantica, pensada para publicar
  informacion academica como Linked Open Data
- ROH: Red de Ontologias Hercules, adaptada al contexto universitario espanol y
  compatible con CVN

La conclusion fue que estos modelos son potentes y expresivos, pero demasiado
complejos para el alcance practico del TFG. CERIF, VIVO y ROH estan pensados para
infraestructuras institucionales amplias, sistemas CRIS, ontologias y grafos de
conocimiento. Adoptarlos directamente habria introducido sobreingenieria,
dependencia de tecnologias pesadas y una curva de implementacion excesiva.

No obstante, la investigacion sobre ROH fue relevante porque mostro que ya existe
trabajo previo en Espana para conectar CVN con ontologias universitarias, e
incluso herramientas publicas para importar informacion CVN hacia ROH. Esto
reforzo la idea de mantener trazabilidad hacia CVN y de no perder semantica al
definir un formato abierto propio.

### 2.2. Formatos de serializacion estudiados

Tambien se compararon varios formatos de serializacion:

- XML
- JSON
- JSON-LD
- YAML

XML se identifico como el formato usado por CVN y como una opcion fuerte para
validacion estructural gracias a XSD. Sin embargo, tambien se observo que es mas
verboso, menos natural de manejar en Python, mas costoso de procesar y menos
comodo para interaccion con LLM por consumo de tokens.

JSON se considero una alternativa mas ligera, nativa para estructuras clave-valor,
facil de procesar en Python y adecuada para APIs, almacenamiento documental y
bases de datos NoSQL. Aunque JSON no incluye por si mismo una semantica fuerte,
JSON Schema permite definir estructura, tipos y restricciones de forma similar a
XSD para muchos casos practicos.

JSON-LD se estudio como extension para conectar JSON con grafos RDF mediante
`@context`. Se considero interesante para trabajo futuro, pero innecesario para
el MVP porque habria acercado el proyecto de nuevo a complejidad propia de Web
Semantica.

YAML se valoro por su legibilidad humana y porque es un superconjunto de JSON,
pero se descarto como formato principal porque su procesamiento puede ser mas
delicado, menos estandarizado para validacion de intercambio y menos adecuado
como contrato publico de datos.

La decision resultante fue usar JSON como formato final de intercambio y
almacenamiento, acompanado de JSON Schema y validacion Pydantic.

### 2.3. LinkML, UML/OCL y BESSER

La investigacion tambien incluyo LinkML como modelo hibrido. LinkML permite
definir esquemas en YAML y generar artefactos en distintos lenguajes y formatos,
incluyendo JSON Schema, SQL y documentacion. Se reconocio como una tecnologia
muy potente para proyectos colaborativos y semanticos complejos, pero se descarto
como dependencia principal porque el TFG solo necesitaba una parte pequena de sus
capacidades y su adopcion habria anadido pasos y complejidad innecesarios.

Despues se estudio el uso de UML como lenguaje de modelado agnostico y OCL para
restricciones. UML aportaba clases, atributos, multiplicidades, asociaciones,
agregaciones, composiciones y herencia. OCL permitia expresar restricciones que
UML por si solo no representa con suficiente detalle. Tambien se identifico
BESSER como herramienta capaz de transformar modelos UML/OCL en clases Pydantic.

Esta parte de la investigacion influyo en la direccion posterior del proyecto:
aunque finalmente no se adopto BESSER como nucleo de generacion, si se mantuvo la
idea de construir una capa conceptual agnostica antes de generar artefactos
concretos como diagramas, JSON Schema o modelos Pydantic.

### 2.4. Investigacion tecnica del paquete oficial CVN

Tras el estudio del estado del arte, se analizo el paquete oficial
`docs/CvnXML_v1.4.3_2.1_17012025/`. Se identifico que no era solo un conjunto de
XSD, sino un paquete mixto formado por documentacion humana, XML estructurado,
modelos tecnicos, esquemas de validacion y catalogos auxiliares.

Las fuentes principales analizadas fueron:

- `SpecificationManual.xml`: catalogo estructurado de campos CVN, con codigos,
  nombres, tipos, obligatoriedad, multiplicidad y tablas de referencia
- `CVNTreeModel.xml`: enlace tecnico entre codigos CVN y estructura XML
- `CVN.xsd`: esquema principal de validacion del XML CVN
- `Common.xsd`, `AuxTable.xsd` e `ISOUtilities.xsd`: tipos comunes y tablas
  auxiliares
- `Entity.xml`, `ReferenceTables.xml`, `Subtype_Spa.xml` y `Thesaurus.xml`:
  familias auxiliares necesarias para interpretar referencias del manual

La conclusion principal fue que no convenia construir el modelo final
directamente desde `CVN.xsd`, porque eso produciria un modelo demasiado ligado a
la serializacion XML. La estrategia correcta era separar dominio, reglas,
trazabilidad y serializacion.

## 3. Decision arquitectonica principal

La decision tecnica mas importante fue adoptar una arquitectura en capas:

```text
Paquete oficial CVN
-> bindings estructurales generados
-> normalizacion de metadatos
-> reglas semanticas
-> modelos de dominio Pydantic
-> modelo conceptual agnostico
-> JSON Schema, diagramas, parser y aplicacion
```

Esta arquitectura permite usar los XSD oficiales como fuente de
interoperabilidad, pero no como modelo conceptual final.

Se definieron responsabilidades claras en el repositorio:

- `src/generated/`: codigo generado automaticamente desde XSD
- `src/cvn_codegen/`: logica mantenida a mano para generacion, normalizacion y
  semantica
- `src/models/cvn/`: modelos de dominio
- `schemas/`: artefactos JSON Schema
- `src/open_cvn/`: parser, validador e importadores
- `src/open_cvn_app/`: aplicacion CLI local

Tambien se establecio una regla importante: no editar manualmente
`src/generated/`; cualquier cambio estructural debe venir de regenerar desde las
fuentes oficiales.

## 4. Automatizacion desde XML/XSD

La primera gran implementacion fue el pipeline de generacion estructural con
`xsdata`, que transforma los XSD oficiales en bindings Pydantic importables.

Se generaron bindings para:

- `CVN.xsd`
- `SpecificationManual.xsd`
- `CVNTreeModel_v1.0.xsd`
- `ReferenceTables.xsd`
- `Subtypes.xsd`
- `Entity_v1.4.xsd`
- `Thesaurus.xsd`

El runner principal se centralizo en:

```text
src/cvn_codegen/xsdata_runner.py
```

El comando canonico de generacion estructural es:

```bash
uv run python -m cvn_codegen.xsdata_runner all
```

Durante esta fase se detecto una inconsistencia relevante: `CVNTreeModel.xml` no
encaja completamente con `CVNTreeModel_v1.0.xsd`, porque el XML contiene algunos
elementos no declarados por el XSD. Esta discrepancia se documento como una
limitacion del paquete fuente, no como un error del proyecto.

## 5. Normalizacion de metadatos

Despues de generar la capa estructural, se implemento una capa de normalizacion
para unir la informacion funcional de `SpecificationManual.xml` con la
informacion tecnica de `CVNTreeModel.xml`.

La normalizacion genera entradas unificadas por codigo CVN y permite conservar
trazabilidad hacia las fuentes originales.

La linea base documentada incluye:

- `1457` codigos normalizados
- `1429` codigos presentes tanto en manual como en tree model
- `27` codigos solo en el manual
- `1` codigo solo en el tree model

Tambien se anadio resolucion de referencias auxiliares mediante
`ReferenceTables.xml`, `Subtype_Spa.xml`, `Entity.xml` y `Thesaurus.xml`. Esta
fase fue necesaria porque muchos campos CVN no son texto libre, sino referencias
a catalogos, entidades, tesauros o tablas auxiliares.

## 6. Reglas semanticas y modelos de dominio

Sobre la normalizacion se construyo una politica semantica que decide como debe
interpretarse cada campo CVN: texto, fecha, numero, enum cerrado, catalogo
abierto, referencia a entidad, tesauro, subtipo, referencia no resuelta o campo
con limitaciones estructurales.

Una decision clave fue no convertir automaticamente todas las tablas CVN en
enumeraciones. Algunas son pequenas y cerradas, pero otras son abiertas,
evolutivas o dependen de catalogos externos. Por eso se implemento una evaluacion
dinamica de elegibilidad para enum basada en evidencia de `ReferenceTables.xml`.

Ejemplos:

- `CVN_SEX_A` puede tratarse como enum cerrado
- `CVN_ENTITY_TYPE` se mantiene abierto por senales de catalogo no cerrado

Despues se implemento el generador de modelos de dominio:

```text
src/cvn_codegen/domain_model_generator.py
```

El comando canonico es:

```bash
uv run python -m cvn_codegen.domain_model_generator
```

La generacion actual produce `105` archivos bajo
`src/models/cvn/generated/`, conservando trazabilidad hacia codigos CVN, rutas
XML y decisiones semanticas.

## 7. Modelo conceptual agnostico

Tras generar los modelos de dominio, se investigo si era adecuado generar UML
directamente desde las clases Pydantic. La conclusion fue que no era una buena
base para documentacion conceptual final, porque las clases generadas contienen
detalles tecnicos que no deben convertirse automaticamente en dominio.

Por eso se creo una capa intermedia: el modelo conceptual agnostico.

Esta capa se implemento en:

```text
src/cvn_codegen/conceptual_model_extractor.py
src/cvn_codegen/conceptual_model_types.py
```

El modelo conceptual consume metadatos normalizados, politica semantica y
evidencia de generacion de dominio. A partir de el se generan diagramas,
JSON Schema y documentacion de trazabilidad.

## 8. Diagramas y JSON Schema

Se implemento generacion de diagramas UML-like con PlantUML desde el inventario
conceptual. Los diagramas no se generan directamente desde XML ni desde clases
Python, sino desde la capa conceptual.

Los artefactos se almacenan en:

```text
docs/diagrams/
```

Tambien se genero un JSON Schema canonico para el formato Open CVN:

```text
schemas/open_cvn.schema.json
```

El schema usa JSON Schema Draft 2020-12 y conserva trazabilidad mediante
extensiones `x-open-cvn-*`.

## 9. Formato Open CVN JSON

Una fase central fue definir un formato JSON propio, abierto y mas manejable que
el XML CVN original.

La raiz canonica del documento Open CVN JSON es:

```json
{
  "schema_version": "...",
  "metadata": {},
  "curriculum": {},
  "extensions": {}
}
```

El contenido curricular se organiza por areas conceptuales, no como una copia
literal del XML CVN. Esto facilita validacion, almacenamiento, transformacion y
exportacion.

## 10. Parser, validador e importadores

Sobre el formato Open CVN se implemento un contrato publico de parser y validador
en `src/open_cvn/`.

Las funciones principales son:

```python
parse_open_cvn_json(...)
validate_open_cvn_json(...)
parse_cvn_xml(...)
parse_cvn_pdf(...)
```

El sistema soporta:

- validacion de Open CVN JSON
- importacion de CVN XML con mapeo semantico parcial
- extraccion determinista de XML embebido en PDF
- fallback LLM opcional para PDFs sin XML extraible o validable

La validacion JSON se realiza en dos niveles: primero JSON Schema y despues
modelos Pydantic de runtime. Ademas, se anadieron advertencias semanticas
conservadoras para documentos estructuralmente validos pero potencialmente
sospechosos.

## 11. Aplicacion CLI local

Despues de completar la base de modelo, schema y parser, se desarrollo una
aplicacion local CLI-first. Se eligio una CLI en lugar de una interfaz grafica
pesada para construir primero un MVP simple, reproducible y verificable.

El comando principal es:

```bash
open-cvn
```

La aplicacion se implemento en:

```text
src/open_cvn_app/
```

Incluye:

- inicializacion de almacenamiento local
- importacion y exportacion de Open CVN JSON
- almacenamiento SQLite
- curriculum maestro
- versiones derivadas
- seleccion de secciones y entradas
- exportacion a LaTeX
- generacion opcional de PDF
- importacion PDF con fallback LLM opcional

## 12. Almacenamiento y versiones derivadas

La aplicacion usa SQLite como almacenamiento local. Esto evita depender de un
servicio externo y permite que el prototipo funcione como herramienta local.

Una funcionalidad importante es la distincion entre curriculum maestro y
versiones derivadas. El curriculum maestro contiene toda la informacion conocida,
mientras que las versiones derivadas permiten preparar curriculos adaptados a
distintos contextos mediante inclusion o exclusion de secciones y entradas.

Esta decision responde a una necesidad practica: no todos los CV enviados deben
contener todos los datos disponibles.

## 13. Exportacion a LaTeX y PDF

Se implemento exportacion determinista a LaTeX usando Jinja.

El template principal esta en:

```text
src/open_cvn_app/templates/latex/basic_cv.tex.jinja
```

Despues se anadio generacion opcional de PDF. El sistema busca motores TeX y
ofrece diagnosticos estructurados si no hay ninguno disponible. Tambien se anadio
el comando:

```bash
open-cvn pdf doctor
```

Esta parte demuestra el flujo completo desde datos curriculares estructurados
hasta un artefacto final presentable.

## 14. Importacion asistida con LLM

Como extension post-MVP, se anadio una importacion asistida con LLM para PDFs sin
XML CVN extraible o validable. Esta funcionalidad es opt-in porque los CV pueden
contener datos personales.

El uso de proveedores externos requiere consentimiento explicito mediante flags
como:

```bash
--allow-external-llm
```

El resultado producido por el LLM no se acepta directamente: debe validar contra
Open CVN JSON y se marca con procedencia en `extensions`. La decision fue tratar
el LLM como ayuda no autoritativa que requiere revision humana.

## 15. Pruebas y verificacion

El proyecto se desarrollo con una estrategia fuerte de pruebas automatizadas. Se
anadieron pruebas para generacion estructural, importabilidad, parseo,
normalizacion, resolucion auxiliar, politica semantica, generacion de modelos,
JSON Schema, parser, XML, PDF, SQLite, CLI, versiones, edicion, LaTeX, PDF, LLM y
flujos end-to-end.

El comando principal de verificacion es:

```bash
uv run pytest -n auto tests
```

La ultima linea base documentada indica:

```text
488 passed
```

Tambien se configuro GitHub Actions para ejecutar la suite en pull requests hacia
`main` y `development`.

## 16. Limitaciones documentadas

Durante el desarrollo se registraron limitaciones explicitamente para no ocultar
los bordes reales del sistema. Estas limitaciones no invalidan el proyecto; al
contrario, delimitan con precision que partes estan automatizadas con garantias,
que partes dependen de inconsistencias del paquete oficial y que partes requieren
curacion o trabajo futuro.

### 16.1. `CVNTreeModel.xml` no encaja completamente con su XSD

El paquete oficial incluye `CVNTreeModel.xml` como fuente tecnica para relacionar
codigos CVN con rutas dentro del XML final. En teoria, este fichero deberia
validar contra `CVNTreeModel_v1.0.xsd`. Sin embargo, durante las pruebas se
detecto que el XML contiene algunos elementos `<Type>` en posiciones que el XSD
no declara.

Esto significa que la fuente oficial contiene una discrepancia interna: el XML
real aporta informacion que no esta completamente descrita por su propio esquema.
La consecuencia practica es que el binding generado desde el XSD es correcto
respecto al esquema, pero no puede parsear todo el XML oficial sin encontrar esa
inconsistencia.

El proyecto lo gestiona tratando `CVNTreeModel.xml` como evidencia tecnica para
normalizacion y registrando la discrepancia como limitacion del paquete fuente,
no como fallo del pipeline. No se parchea manualmente `src/generated/` porque eso
romperia la reproducibilidad desde los XSD oficiales.

### 16.2. Los bindings generados no expresan perfectamente `xs:choice`

Algunos tipos XSD usan `xs:choice`, que significa que solo una de varias
alternativas puede aparecer en un punto concreto del XML. Al generar modelos
Pydantic desde XSD, esa restriccion no siempre se conserva como exclusividad
mutua estricta en Python.

La consecuencia es que la capa estructural generada puede aceptar objetos que no
representarian un XML valido si se aplicara estrictamente la regla original de
`xs:choice`. Esto afecta sobre todo a tipos envoltorio como fechas flexibles,
identificadores oficiales o nombres de entidad.

La decision fue no corregir manualmente los bindings generados. En su lugar, la
capa generada se mantiene como interoperabilidad estructural, y las reglas de uso
correctas se recuperan en la capa semantica y en los modelos de dominio.

### 16.3. Algunos `minOccurs` no se fuerzan en listas generadas

En XSD, `minOccurs` indica cuantas veces debe aparecer como minimo un elemento.
Sin embargo, cuando ciertos elementos repetidos se generan como listas Pydantic,
pueden quedar con `default_factory=list`. Eso permite construir en Python objetos
con listas vacias aunque el XSD indicara que debe haber al menos un elemento.

Esta limitacion afecta a la validacion estructural de objetos Python generados,
no necesariamente al diseno conceptual del formato Open CVN. Por eso se decidio
que la cardinalidad relevante para el usuario y para el formato abierto no debia
depender solo de los bindings generados, sino de la politica semantica, JSON
Schema y validacion runtime.

### 16.4. Algunos atributos generados quedan como `object`

Durante la generacion automatica, algunos atributos de los XSD oficiales no se
traducen a tipos Python concretos y quedan como `object`. Esto reduce la calidad
de la validacion y hace que esos campos sean menos ergonomicos para desarrollo.

La causa esta en la combinacion de estructuras XSD complejas, tipos genericos y
limitaciones de la herramienta de generacion. El impacto se controla evitando que
esos tipos debiles se conviertan directamente en el contrato publico del
proyecto. Por eso Open CVN JSON y los modelos runtime no exponen simplemente los
bindings generados, sino una representacion mas estable y semantica.

### 16.5. No todas las tablas CVN pueden convertirse de forma segura en enums

CVN contiene muchas tablas auxiliares. Algunas son pequenas, cerradas y estables,
por lo que pueden modelarse como enumeraciones. Otras son grandes, extensibles,
jerarquicas, delegadas a catalogos externos o contienen valores abiertos como
`otros`.

Convertir automaticamente todas las tablas en enums rigidos seria peligroso,
porque bloquearia valores validos o futuros que la norma puede permitir. Por eso
el proyecto implementa una evaluacion dinamica de elegibilidad basada en
evidencia: tamano de la tabla, codigos, etiquetas, duplicados, jerarquia, senales
de mundo abierto y presencia de delegaciones.

La consecuencia es que solo tablas con evidencia suficiente se generan como enums
cerrados. Las demas se mantienen como referencias abiertas, codelists o valores
controlados no estrictos.

### 16.6. `CVN_AGENCY_C` queda como referencia no resuelta

El manual CVN referencia ciertas tablas que no aparecen de forma limpia en los
artefactos auxiliares disponibles. Un caso documentado es `CVN_AGENCY_C`, que
aparece como referencia manual pero no tiene una correspondencia clara en
`ReferenceTables.xml` ni en los catalogos auxiliares incluidos.

Esto significa que el proyecto no puede afirmar, con la evidencia disponible,
que conoce todos los valores validos de esa referencia. La decision fue preservar
el caso como referencia no resuelta, manteniendo trazabilidad al nombre original,
en lugar de inventar una tabla, forzar un enum o perder la informacion.

### 16.7. `Subtype_Spa.xml` no ofrece un puente directo por familia de tabla

`Subtype_Spa.xml` contiene informacion de subtipos, pero esta organizada por
codigos de item de subtipo y no por nombres de familias de tabla como
`CVN_KNOW_A`. Esto permite demostrar que existe un catalogo de subtipos, pero no
permite enlazar de forma estricta cada familia de tabla con todos sus valores
validos.

La consecuencia es que las referencias subtipo se pueden clasificar como
subtype-backed, pero no se pueden promover automaticamente a enums cerrados por
familia concreta. El proyecto conserva esa evidencia de forma explicita y aplica
una politica conservadora.

### 16.8. La importacion XML es semantica parcial, no conversion completa

La importacion desde CVN XML reconoce estructuras y codigos CVN y puede poblar
secciones Open CVN como identidad, educacion, investigacion, experiencia
profesional, logros y otros. Sin embargo, no cubre todavia todos los posibles
campos, combinaciones y casos raros del ecosistema CVN.

Esto significa que el parser XML no debe presentarse como un conversor completo
de cualquier CVN real a Open CVN JSON. Su comportamiento actual es deliberado:
convierte lo reconocido, valida el resultado, conserva trazas y registra
diagnosticos para los elementos no mapeados.

La ventaja de esta decision es que no se pierde informacion silenciosamente. Los
datos que no se pueden mapear de forma segura quedan registrados como diagnostico
o en secciones de fallback.

### 16.9. JSON Schema no puede expresar todas las reglas semanticas del dominio

JSON Schema permite validar estructura, tipos, campos requeridos, arrays,
objetos, patrones y algunas enumeraciones. Sin embargo, no puede representar de
forma completa todas las reglas semanticas de CVN: dependencias entre campos,
obligatoriedad condicional, coherencia entre codigos y valores, significado de
catalogos externos o validaciones que dependen de contexto.

Por eso el proyecto usa JSON Schema como primera capa de validacion, pero no como
unica garantia. Despues se aplica validacion Pydantic y advertencias semanticas
conservadoras. Esta separacion permite que el formato sea interoperable sin
prometer que JSON Schema por si solo captura toda la logica del dominio.

### 16.10. La importacion con LLM es best-effort y requiere revision humana

La importacion asistida con LLM se introdujo como fallback para PDFs donde no hay
XML CVN extraible o validable. Esta tecnica puede ser util, pero no ofrece las
mismas garantias que leer XML estructurado oficial.

Un LLM puede omitir informacion, interpretar mal una seccion, inventar contenido
o producir datos incompletos. Por eso el sistema exige consentimiento explicito
para usar proveedores externos, valida localmente el JSON resultante y marca la
procedencia en `extensions`. El resultado no se considera autoritativo y debe ser
revisado por el usuario.

### 16.11. La generacion PDF depende de disponibilidad de motor TeX

La exportacion a LaTeX se puede realizar enteramente desde Python, pero convertir
el `.tex` en PDF requiere un motor TeX. El entorno puede tener `tectonic`,
`latexmk` o `pdflatex`, o puede no tener ninguno instalado.

Para reducir esta dependencia, el proyecto incluye descubrimiento de motores y
soporte para Tectonic gestionado cuando sea posible. Aun asi, la generacion PDF
puede depender de plataforma, red, cache o instalacion local. Por eso el sistema
incluye diagnosticos mediante `open-cvn pdf doctor` y devuelve errores
estructurados si no puede compilar.

### 16.12. Valor de las limitaciones para el TFG

Estas limitaciones forman parte del resultado tecnico del TFG porque muestran
donde estan las garantias automaticas y donde se necesita evidencia externa,
curacion manual o trabajo futuro. Tambien justifican varias decisiones de diseno:
mantener trazabilidad, separar capas, no editar codigo generado, validar en varios
niveles y distinguir entre datos deterministas, datos parcialmente mapeados y
datos asistidos por LLM.

## 17. Flujo completo actual

El flujo completo del proyecto queda resumido asi:

```text
Paquete oficial CVN
    |
    v
XSD + XML oficiales
    |
    v
Bindings estructurales Pydantic
    |
    v
Normalizacion de SpecificationManual.xml y CVNTreeModel.xml
    |
    v
Resolucion de catalogos auxiliares
    |
    v
Politica semantica
    |
    v
Modelos de dominio Pydantic
    |
    v
Modelo conceptual agnostico
    |
    v
JSON Schema + diagramas + formato Open CVN JSON
    |
    v
Parser y validador
    |
    v
Aplicacion CLI local
    |
    v
SQLite + versiones + exportacion JSON/LaTeX/PDF + importacion PDF/XML/LLM
```

## 18. Conclusion

El proyecto ha evolucionado desde una investigacion inicial del estandar CVN
hasta una herramienta tecnica completa para generar, validar, almacenar y
exportar curriculos en un formato abierto.

La aportacion principal no es solo generar codigo desde XSD, sino construir una
arquitectura reproducible que separa estructura XML, semantica curricular,
trazabilidad, modelo conceptual, JSON abierto, validacion y aplicacion local.

El resultado es una base solida para trabajar con curriculos academicos en
Espana, manteniendo compatibilidad conceptual con CVN pero evitando depender de
la forma XML oficial como modelo interno unico.
