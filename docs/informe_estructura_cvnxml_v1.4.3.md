# Informe de estructura y uso del paquete CVN-XML v1.4.3

## Objetivo del informe

Este informe describe la estructura completa de la carpeta `docs/CvnXML_v1.4.3_2.1_17012025`, explica la funcion de cada fichero y propone una forma correcta de empezar a utilizar este material.

La idea principal es distinguir con claridad cuatro capas que aparecen mezcladas en el paquete:

1. **Documentacion funcional para lectura humana**
2. **Documentacion estructurada en XML para explotacion automatica**
3. **Modelado tecnico del arbol XML CVN**
4. **Esquemas XSD de validacion**

Si se entiende esta separacion, el paquete deja de parecer un conjunto de archivos heterogeneos y pasa a verse como una especificacion relativamente coherente.

---

## Resumen ejecutivo

La carpeta analizada contiene el material tecnico del estandar **CVN-XML** de FECYT para representar curriculos en formato interoperable.

El paquete no contiene ejemplos de curriculos reales, sino los elementos necesarios para:

- entender que campos existen en la norma
- saber como se organizan por modulos y subapartados
- conocer que tablas auxiliares deben usarse
- mapear esos campos a una representacion XML
- validar la estructura XML resultante

### Regla practica de lectura

- Si quieres **entender la norma**, empieza por el PDF principal.
- Si quieres **procesar automaticamente los campos**, usa `SpecificationManual.xml`.
- Si quieres **generar CVN-XML**, necesitas tambien `CVNTreeModel.xml`.
- Si quieres **validar el XML generado**, usa `CVN.xsd`.

---

## Estructura completa de la carpeta

```text
docs/CvnXML_v1.4.3_2.1_17012025/
├── Leeme.txt
├── Manual/
│   ├── Manual de Especificaciones Técnicas v1.4.3_v2.1.pdf
│   └── TreeModel_v1.0 20090331 v1.0.pdf
├── XML/
│   ├── SpecificationManual.xml
│   └── CVNTreeModel.xml
└── XSD/
    ├── CVN.xsd
    ├── Common.xsd
    ├── AuxTable.xsd
    ├── ISOUtilities.xsd
    ├── SpecificationManual.xsd
    └── CVNTreeModel_v1.0.xsd
```

---

## Vision global del paquete

### Capa 1. Manual funcional

Describe **que significa cada campo** del curriculo CVN.

Aqui se explica:

- el sistema de codificacion por bloques
- la estructura por modulos
- el tipo de cada dato
- la obligatoriedad
- la multiplicidad
- las tablas auxiliares y codigos asociados

### Capa 2. Manual estructurado en XML

Convierte el manual anterior en un formato **parseable por maquina**.

Esto permite:

- extraer automaticamente todos los campos
- construir catalogos
- generar documentacion derivada
- traducir la norma a otros formalismos como UML, OCL, JSON Schema o metamodelos propios

### Capa 3. Tree model

Explica **como se codifica tecnicamente** cada campo funcional dentro del XML CVN.

Es la pieza que une:

- el manual funcional
- y la estructura XML real

### Capa 4. XSD

Define **la forma legal del XML** para validacion estructural.

No sustituye al manual, porque muchas reglas de negocio no estan expresadas solo en XSD.

---

## Analisis fichero a fichero

## 1. Archivo raiz

### `docs/CvnXML_v1.4.3_2.1_17012025/Leeme.txt`

#### Funcion

Es un archivo de orientacion rapida. Actua como indice del paquete y resume, de forma muy breve, que contiene cada subcarpeta.

#### Lo que aporta

- confirma que el objetivo del paquete es la codificacion de curriculos en formato CVN-XML
- identifica las tres grandes familias de materiales: `XSD`, `XML` y `Manual`
- sirve para situarse rapido antes de entrar en el detalle

#### Limitaciones

- es demasiado breve
- tiene problemas de codificacion de caracteres
- no explica relaciones internas entre archivos

#### Uso recomendado

Utilizarlo solo como punto de partida. No debe considerarse una fuente normativa.

---

## 2. Carpeta `Manual/`

Esta carpeta contiene documentacion orientada a lectura humana.

### `docs/CvnXML_v1.4.3_2.1_17012025/Manual/Manual de Especificaciones Técnicas v1.4.3_v2.1.pdf`

#### Funcion

Es el **documento central** del estandar. Define el significado de los campos CVN y su organizacion funcional.

#### Contenido principal

Incluye:

- introduccion general al proyecto CVN
- glosario
- vision general del intercambio curricular
- estructura de la codificacion por niveles
- tipos de datos
- reglas generales de uso
- indice de modulos y apartados
- control de versiones
- detalle de miles de items curriculares
- anexo de tablas auxiliares

#### Que informacion contiene cada item

Para cada campo aparecen normalmente:

- codigo CVN
- nombre del campo
- nombre corto
- definicion
- tipo de dato
- obligatoriedad
- tabla de referencia asociada
- multiplicidad o repeticiones
- vinculacion con otros campos cuando procede

#### Ejemplo de utilidad practica

Si quieres entender que significa `010.010.000.170`, este PDF te dice que se trata de la **categoria profesional/puesto o cargo** dentro de la situacion profesional actual.

#### Por que es importante

Este archivo es la mejor fuente para construir un **modelo conceptual** del dominio CVN, porque describe la semantica del curriculo y no solo su estructura XML.

#### Uso recomendado

Es el primer archivo que deberias leer si quieres:

- entender el dominio
- construir un metamodelo
- traducir la norma a UML + OCL
- identificar clases de negocio y restricciones semanticas

---

### `docs/CvnXML_v1.4.3_2.1_17012025/Manual/TreeModel_v1.0 20090331 v1.0.pdf`

#### Funcion

Es el manual explicativo del modelo `CVNTreeModel`.

#### Que explica

Explica la estructura del XML de modelado que conecta:

- los campos del manual tecnico
- con las propiedades e indicadores del XML CVN

#### Conceptos clave que introduce

- `CVNTreeModel`
- `Node`
- `Property`
- `Indicator`
- `Value`
- `Child`

#### Interpretacion

Este documento no explica el significado curricular de los campos. Explica como se modelan tecnicamente dentro del arbol XML.

#### Valor para un modelado agnostico

Es util para:

- entender la capa tecnica de serializacion
- construir trazabilidad entre tu UML y el XML real
- separar el modelo conceptual del modelo de intercambio

#### Uso recomendado

Léelo despues del manual principal, no antes.

---

## 3. Carpeta `XML/`

Contiene versiones XML de la documentacion y del modelado. Es la parte mas util para explotacion automatica.

### `docs/CvnXML_v1.4.3_2.1_17012025/XML/SpecificationManual.xml`

#### Funcion

Es la representacion XML del manual funcional de especificaciones.

#### Que contiene

Un gran conjunto de elementos `Item`, cada uno con informacion como:

- `code`
- `Name`
- `Type`
- `Level`
- `Order`
- `Definition`
- `Obligatory`
- `ReferenceTable`
- `Multiplicity`
- `Length`
- `Extension`
- `Example`

Ademas, muchos textos aparecen en varios idiomas.

#### Por que es muy importante

Es probablemente la mejor base para convertir la norma a otros modelos formales, porque ya esta estructurada y evita tener que raspar manualmente el PDF.

#### Que tareas permite

- generar un catalogo de campos CVN
- construir tablas de trazabilidad codigo -> nombre -> tipo -> tabla
- detectar campos obligatorios y repetibles
- extraer referencias a tablas auxiliares
- preparar una transformacion a UML

#### Lo que no resuelve por si sola

No explica completamente como se serializa cada campo en el XML final. Para eso hace falta `CVNTreeModel.xml`.

#### Observaciones

Este archivo referencia tablas externas o no presentes en el paquete, entre ellas:

- `ENTITY@Entity.xsd`
- `THESAURUS@thesaurus.xsd`

Eso significa que el paquete no es del todo autosuficiente como ecosistema cerrado.

#### Uso recomendado

Tomarlo como **fuente maestra automatizable de semantica estructurada**.

---

### `docs/CvnXML_v1.4.3_2.1_17012025/XML/CVNTreeModel.xml`

#### Funcion

Es el modelo en arbol que enlaza cada codigo CVN con propiedades e indicadores del XML real.

#### Que hace realmente

Indica como un campo funcional del manual se representa usando elementos como:

- `Version`
- `Agent`
- `CvnItem`
- `Property`
- `Indicator`
- `Value`
- `Child`

Por ejemplo, para datos de identificacion personal muestra asociaciones con indicadores como:

- `GivenName`
- `FirstFamilyName`
- `SecondFamilyName`
- `BirthDate`
- `BirthCountry`

#### Por que es importante

Sin este archivo, puedes saber **que campo existe**, pero no exactamente **como encajarlo** en la estructura XML CVN.

#### Valor para UML + OCL

Es muy util para una **capa de trazabilidad o mapeo**, pero no deberia dictar directamente el modelo conceptual.

Lo correcto suele ser:

- construir primero el modelo conceptual agnostico
- usar despues este archivo para mapearlo al formato CVN-XML

#### Uso recomendado

Usarlo como **puente entre el dominio y la serializacion XML**.

---

## 4. Carpeta `XSD/`

Aqui estan los esquemas de validacion estructural.

### `docs/CvnXML_v1.4.3_2.1_17012025/XSD/CVN.xsd`

#### Funcion

Es el esquema principal para validar un documento CVN-XML.

#### Que define

- elemento raiz `CVN`
- nodo `Version`
- nodo `Agent`
- repeticion de `CvnItem`
- gran parte de los tipos complejos del documento final

#### Dependencias

Incluye:

- `Common.xsd`
- `AuxTable.xsd`

#### Interpretacion correcta

Este archivo describe la **forma del XML final**, pero no la semantica completa del dominio curricular.

#### Para que sirve bien

- validar XML generado
- estudiar la estructura de serializacion
- contrastar si un mapeo tecnico es coherente

#### Para que no sirve bien

- no es una buena base para extraer el modelo conceptual del dominio
- si partes solo de aqui, obtendras un modelo demasiado orientado a XML

---

### `docs/CvnXML_v1.4.3_2.1_17012025/XSD/Common.xsd`

#### Funcion

Biblioteca de tipos basicos comunes del espacio de nombres CVN.

#### Que define

- `CVN_string`
- `CVN_date`
- `CVN_duration`
- `CVN_ISO_3166`
- `CVN_ISO_639`
- tipos de email y otros envoltorios basicos

#### Uso practico

Es util para entender que los datos CVN suelen expresarse como tipos encapsulados con atributos adicionales como:

- `code`
- `obligatory`
- `multiplicity`
- `attribute`

#### Valor para UML

Ayuda a decidir:

- que atributos conceptuales son simples (`String`, `Date`, `Duration`, etc.)
- y cuales deben modelarse como tipos controlados o datatypes especificos

---

### `docs/CvnXML_v1.4.3_2.1_17012025/XSD/AuxTable.xsd`

#### Funcion

Contiene las tablas auxiliares codificadas como enumeraciones XSD.

#### Que incluye

Entre muchas otras:

- tipos de entidad
- convocatorias
- categorias
- tipos de publicacion
- dedicacion
- programas
- sexos
- codigos de experiencia
- codigos CVN de items curriculares

#### Importancia

Es una de las piezas mas importantes para cualquier transformacion a un modelo formal, porque expresa el universo de valores controlados.

#### Uso en UML

Puede traducirse a:

- `Enumeration`, si quieres un modelo estricto
- `CodeList`, si prefieres flexibilidad y evolucion futura
- clases de catalogo, si quieres metadatos adicionales

#### Recomendacion

No convertir automaticamente todas las tablas a enumeraciones UML sin analizar antes su estabilidad y volumen.

---

### `docs/CvnXML_v1.4.3_2.1_17012025/XSD/ISOUtilities.xsd`

#### Funcion

Contiene codigos ISO reutilizados por la norma.

#### Que aporta

- `ISO_639` para idiomas
- `ISO_3166` para paises

#### Valor para modelado

Permite decidir que atributos como `pais`, `nacionalidad` o `idioma` no son texto libre, sino referencias a catalogos normalizados.

---

### `docs/CvnXML_v1.4.3_2.1_17012025/XSD/SpecificationManual.xsd`

#### Funcion

Valida la estructura de `SpecificationManual.xml`.

#### Que define

La forma del manual XML:

- `SpecificationManual`
- `Manual`
- `Item`
- `Name`
- `Definition`
- `ReferenceTable`
- `VersionControl`

#### Utilidad

No es esencial para entender la semantica, pero si para:

- validar tu parser
- entender la estructura formal del manual XML
- asegurar que la extraccion automatica esta bien basada

---

### `docs/CvnXML_v1.4.3_2.1_17012025/XSD/CVNTreeModel_v1.0.xsd`

#### Funcion

Valida `CVNTreeModel.xml`.

#### Que formaliza

- `CVNTreeModel`
- `Node`
- `Property`
- `Indicator`
- nombres de propiedades permitidos

#### Utilidad

Sirve para confirmar la estructura del metamodelo tecnico usado por FECYT para enlazar campos curriculares con la serializacion XML.

---

## Relaciones internas entre los archivos

## Relacion funcional

```text
Manual PDF
   -> define significado de campos

SpecificationManual.xml
   -> estructura ese mismo catalogo en XML

CVNTreeModel.xml
   -> indica como cada campo se representa en el XML CVN

CVN.xsd
   -> valida la estructura del XML CVN final
```

## Relacion tecnica XSD

```text
CVN.xsd
  ├── incluye Common.xsd
  └── incluye AuxTable.xsd

Common.xsd
  └── incluye ISOUtilities.xsd

SpecificationManual.xml
  └── validado por SpecificationManual.xsd

CVNTreeModel.xml
  └── validado por CVNTreeModel_v1.0.xsd
```

---

## Como usar este paquete segun el objetivo

## Objetivo A. Entender la norma CVN

### Archivos principales

- `Manual/Manual de Especificaciones Técnicas v1.4.3_v2.1.pdf`
- `Leeme.txt`

### Resultado esperado

Comprender:

- la estructura modular del CV
- los campos existentes
- sus significados y restricciones generales

---

## Objetivo B. Parsear automaticamente el catalogo de campos

### Archivos principales

- `XML/SpecificationManual.xml`
- `XSD/SpecificationManual.xsd`
- `XSD/AuxTable.xsd`
- `XSD/ISOUtilities.xsd`

### Resultado esperado

Poder extraer:

- codigo
- nombre
- definicion
- tipo de dato
- obligatoriedad
- multiplicidad
- tabla de referencia

---

## Objetivo C. Generar CVN-XML

### Archivos principales

- `XML/CVNTreeModel.xml`
- `XSD/CVN.xsd`
- `XSD/Common.xsd`
- `XSD/AuxTable.xsd`

### Resultado esperado

Saber:

- que elementos XML usar
- como organizarlos
- como validarlos

---

## Objetivo D. Traducir CVN a UML + OCL

### Archivos necesarios

- `Manual/Manual de Especificaciones Técnicas v1.4.3_v2.1.pdf`
- `XML/SpecificationManual.xml`
- `XSD/AuxTable.xsd`
- `XSD/ISOUtilities.xsd`

### Archivos muy utiles pero secundarios

- `XML/CVNTreeModel.xml`
- `Manual/TreeModel_v1.0 20090331 v1.0.pdf`
- `XSD/CVN.xsd`

### Recomendacion metodologica

Para UML + OCL conviene separar:

1. **modelo conceptual del dominio**
2. **restricciones OCL**
3. **mapeo a CVN-XML**

No conviene derivar directamente el UML desde `CVN.xsd`, porque el resultado seria demasiado dependiente de XML.

---

## Que partes sobran si el objetivo es un modelado agnostico

## Sobran como base conceptual principal

- `XSD/CVN.xsd`
- `XML/CVNTreeModel.xml`

No porque sean inutiles, sino porque describen la serializacion y el modelado tecnico, no el dominio conceptual puro.

## Aun asi son utiles para

- mantener trazabilidad
- demostrar interoperabilidad con CVN
- justificar como tu modelo abstracto puede serializarse a XML

---

## Problemas y ambiguedades detectadas

## 1. Mezcla de versiones

Hay una discrepancia visible entre versiones documentales:

- la carpeta y el PDF apuntan a `v1.4.3_v2.1`
- `CVN.xsd` declara `Version: 1.4.1`
- `Common.xsd` declara `1.0.9`
- `SpecificationManual.xsd` declara `1.2.0`
- `CVNTreeModel_v1.0.xsd` pertenece claramente a un modelo antiguo de 2009

### Consecuencia

No puede asumirse que todas las piezas hayan evolucionado de forma uniforme.

---

## 2. Recursos externos no incluidos

El material hace referencia a recursos que no aparecen en la carpeta:

- `ENTITY@Entity.xsd`
- `THESAURUS@thesaurus.xsd`
- `Manual Técnico CVN`
- `Historico de correcciones en la normativa`

### Consecuencia

Algunas tablas o catálogos no estan completos dentro del paquete analizado.

---

## 3. Posible desfase entre semantica y mapeo tecnico

El manual funcional ha sido actualizado en 2025, pero el `TreeModel` procede de 2009.

### Consecuencia

Para una implementacion estricta conviene verificar si todos los campos recientes tienen un mapeo tecnico claro y vigente.

---

## 4. El XSD no expresa toda la logica de negocio

Aunque el XML pueda validar contra `CVN.xsd`, muchas condiciones del manual son en realidad reglas semanticas:

- campos "otros"
- obligatoriedad condicional
- coherencia entre tipo y valor
- significado funcional de ciertas combinaciones

### Consecuencia

Si quieres un modelado robusto, necesitaras capturar esas reglas fuera del XSD, por ejemplo con OCL.

---

## Recomendaciones para empezar a trabajar correctamente

## Recomendacion 1. Separar dominio y serializacion

No modeles CVN como si fuera solo XML.

- el PDF y `SpecificationManual.xml` te dan el dominio
- `CVNTreeModel.xml` y `CVN.xsd` te dan la serializacion

---

## Recomendacion 2. Empezar por modulos pequenos

Para cualquier traduccion o modelado, lo mas manejable es empezar por:

- `000` Identificacion y contacto
- `010` Situacion profesional
- `020` Formacion academica

Estos modulos ya muestran:

- datos simples
- entidades relacionadas
- fechas
- localizaciones
- tablas auxiliares
- multiplicidad
- campos condicionados

---

## Recomendacion 3. Construir una capa de trazabilidad

Para cada clase o atributo de tu modelo conviene guardar:

- codigo CVN original
- nombre del campo CVN
- tabla de referencia si existe
- nodo XML o propiedad tecnica asociada cuando sea necesario

Esto te permitira:

- justificar decisiones de modelado
- regenerar mapeos
- mantener interoperabilidad con la norma

---

## Recomendacion 4. Tratar las tablas como codelists, no siempre como enums rigidas

Algunas tablas son buenas candidatas a `Enumeration`, pero otras son muy grandes o potencialmente evolutivas.

En un modelo conceptual suele ser mejor distinguir entre:

- enumeraciones pequenas y cerradas
- codelists externas administradas por la norma

---

## Recomendacion 5. Validar siempre en dos niveles

- nivel estructural: contra XSD
- nivel semantico: contra reglas del manual

En un enfoque UML + OCL, el segundo nivel es especialmente importante.

---

## Propuesta de lectura recomendada

## Secuencia minima

1. `Leeme.txt`
2. `Manual/Manual de Especificaciones Técnicas v1.4.3_v2.1.pdf`
3. `XML/SpecificationManual.xml`
4. `XSD/AuxTable.xsd`
5. `XML/CVNTreeModel.xml`
6. `XSD/CVN.xsd`

## Secuencia si el objetivo es modelado agnostico

1. `Manual/Manual de Especificaciones Técnicas v1.4.3_v2.1.pdf`
2. `XML/SpecificationManual.xml`
3. `XSD/AuxTable.xsd`
4. `XSD/ISOUtilities.xsd`
5. `XML/CVNTreeModel.xml` solo para trazabilidad
6. `XSD/CVN.xsd` solo para contrastar serializacion

---

## Conclusiones finales

La carpeta `docs/CvnXML_v1.4.3_2.1_17012025` no es solo un conjunto de XSD, sino un paquete mixto con cuatro funciones muy distintas:

- **el PDF principal** define la semantica curricular
- **el manual XML** permite explotacion automatica
- **el tree model** describe el enlace con la estructura XML
- **los XSD** validan la forma del documento final y de la documentacion auxiliar

Para cualquier trabajo serio de modelado, especialmente si se quiere llegar a un modelo **agnostico al lenguaje** como UML + OCL, la estrategia correcta es:

- tomar como base la **semantica** del manual y del `SpecificationManual.xml`
- usar las **tablas auxiliares** como catalogos de valores controlados
- dejar el **tree model** y los **XSD** como capa de mapeo y validacion, no como fuente principal del dominio

En otras palabras: el valor real del paquete no esta en copiar su XML, sino en separar adecuadamente **conceptos**, **reglas** y **serializacion**.
