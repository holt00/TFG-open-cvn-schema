# CVN_README

## Que contiene esta carpeta

Esta carpeta reúne la documentacion tecnica de **CVN-XML**, el formato de intercambio curricular promovido por FECYT para representar un curriculum vitae normalizado.

El conjunto no contiene curriculums de ejemplo. Contiene la **norma**, su **representacion en XML** y los **esquemas XSD** necesarios para entenderla y validarla.

En la practica, el paquete se puede leer en cuatro capas:

- **Manual funcional**: explica que campos existen y que significan.
- **Manual XML**: expresa ese mismo contenido en un formato procesable por maquina.
- **Modelo de arbol**: indica como se mapean los campos funcionales al XML real.
- **Esquemas XSD**: validan la estructura de los XML.

## Estructura general

```text
docs/CvnXML_v1.4.3_2.1_17012025/
|- Leeme.txt
|- CVN_README.md
|- Manual/
|  |- Manual de Especificaciones Tecnicas v1.4.3_v2.1.pdf
|  `- TreeModel_v1.0 20090331 v1.0.pdf
|- XML/
|  |- SpecificationManual.xml
|  `- CVNTreeModel.xml
`- XSD/
   |- CVN.xsd
   |- Common.xsd
   |- AuxTable.xsd
   |- ISOUtilities.xsd
   |- SpecificationManual.xsd
   `- CVNTreeModel_v1.0.xsd
```

## Archivos y utilidad

### `Leeme.txt`

Es una guia rapida del paquete. Resume en pocas lineas que hay en cada subcarpeta. Sirve para ubicarse, pero no entra en detalle.

### `Manual/Manual de Especificaciones Tecnicas v1.4.3_v2.1.pdf`

Es el documento principal de la norma. Define los campos CVN, su significado, su organizacion por modulos, el tipo de dato, la obligatoriedad, la repeticion y las tablas auxiliares asociadas.

Es el mejor punto de partida para entender la norma a nivel funcional.

### `Manual/TreeModel_v1.0 20090331 v1.0.pdf`

Explica el esquema `CVNTreeModel`. No describe el significado curricular de los campos, sino la forma en que esos campos se representan tecnicamente en el XML.

Es util para entender el paso entre la norma funcional y la serializacion XML.

### `XML/SpecificationManual.xml`

Es la version XML del manual de especificaciones. Contiene los items curriculares estructurados con elementos como codigo, nombre, definicion, tipo, obligatoriedad o tabla de referencia.

Sirve para explotar la norma automaticamente sin depender del PDF.

### `XML/CVNTreeModel.xml`

Es el modelo de arbol que enlaza cada codigo CVN con propiedades e indicadores del XML final. Es la pieza que conecta los campos del manual con la estructura real del documento CVN-XML.

### `XSD/CVN.xsd`

Es el esquema principal del CVN-XML final. Define el elemento raiz `CVN` y la estructura general del documento, incluyendo bloques como `Version`, `Agent` y `CvnItem`.

### `XSD/Common.xsd`

Define tipos comunes reutilizables, como cadenas, fechas, duraciones, idiomas o paises. Actua como biblioteca base para el esquema principal.

### `XSD/AuxTable.xsd`

Contiene tablas auxiliares y listas controladas de valores: tipos de entidad, categorias, convocatorias, publicaciones, codigos CVN y otros catalogos usados por la norma.

### `XSD/ISOUtilities.xsd`

Contiene codigos ISO reutilizados por CVN, especialmente idiomas (`ISO_639`) y paises (`ISO_3166`).

### `XSD/SpecificationManual.xsd`

Valida la estructura de `XML/SpecificationManual.xml`.

### `XSD/CVNTreeModel_v1.0.xsd`

Valida la estructura de `XML/CVNTreeModel.xml`.

## Como se relacionan entre si

La relacion entre archivos puede resumirse asi:

```text
Manual de Especificaciones Tecnicas.pdf
  -> define la norma y el significado de los campos

SpecificationManual.xml
  -> representa ese manual en XML
  -> se valida con SpecificationManual.xsd

TreeModel_v1.0.pdf
  -> explica el modelo de arbol

CVNTreeModel.xml
  -> mapea los campos CVN al XML real
  -> se valida con CVNTreeModel_v1.0.xsd

CVN.xsd
  -> valida el XML CVN final
  -> usa Common.xsd y AuxTable.xsd

Common.xsd
  -> usa ISOUtilities.xsd
```

## Orden recomendado de lectura

- **Para entender la norma**: `Manual/Manual de Especificaciones Tecnicas v1.4.3_v2.1.pdf`
- **Para procesarla automaticamente**: `XML/SpecificationManual.xml`
- **Para ver el mapeo tecnico al XML**: `XML/CVNTreeModel.xml`
- **Para validar estructura**: `XSD/CVN.xsd`

## Resumen

Esta carpeta combina documentacion para lectura humana y ficheros tecnicos para tratamiento automatico. En conjunto permite:

- entender los campos del CVN
- conocer sus tablas y tipos de dato
- mapear esos campos al XML CVN
- validar los XML generados

En pocas palabras: el PDF principal explica **que significa** cada campo, `SpecificationManual.xml` lo hace **procesable**, `CVNTreeModel.xml` muestra **como se representa** y los XSD indican **que estructura es valida**.
