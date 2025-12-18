# Lista de Tareas Iniciales

## Fase 1: Investigación y Estado del Arte

### 1. Investigación de Modelado Agnóstico (Nivel Conceptual)

* [ ] **Diferenciación de Niveles de Abstracción:**
* [ ] Estudiar la separación entre **Modelo Conceptual** (Entidad-Relación), **Modelo Lógico** (Estructura de tipos) y **Modelo Físico** (Serialización JSON/XML).
* [ ] Investigar el concepto de **Independencia de Datos** (objetivo principal del TFG).

* [ ] **Lenguajes de Modelado Universal:**
* [ ] Revisar **UML (Unified Modeling Language)** para diagramas de clases: representar la jerarquía de méritos académicos sin código.
* [ ] Analizar **IDLs (Interface Description Languages)**: Cómo herramientas como Protocol Buffers o Apache Thrift definen datos antes de generar código.

* [ ] **Patrones de Estructuración de Datos:**
* [ ] Investigar el uso de **Ontologías** para representar el conocimiento académico (vCard, FOAF - Friend of a Friend).
* [ ] Estudiar **Metamodelo de Datos**: Definir las reglas que definen el formato (MOF - Meta-Object Facility).

### 2. Investigación de Formatos de Representación (Nivel Físico)

* [ ] **Comparativa de Serialización:**
* [ ] Analizar **JSON Schema** vs **XML (XSD)**: pros y contras en extensibilidad.
* [ ] Estudiar **YAML** como alternativa de configuración y su mapeo a JSON.
* [ ] Investigar **Protocol Buffers (Protobuf)** y su enfoque en la eficiencia frente a la legibilidad.

* [ ] **Datos Enlazados y Semántica:**
* [ ] Profundizar en **JSON-LD**: Cómo convertir un JSON simple en un grafo de conocimiento académico

### 3. Estándares y Normativas (Contexto Académico)

* [ ] **Investigación CVN (España):**
* [ ] Mapear los campos del PDF de FECYT a una estructura de árbol lógica.
* [ ] Identificar "campos fantasma" (datos que existen en el PDF pero no están bien estructurados en el XML).

* [ ] **Estado del Arte Internacional:**
* [ ] **ORCID:** Analizar su API y cómo estructuran las contribuciones.
* [ ] **EuroPass:** Revisar su esquema XML/JSON para interoperabilidad europea.
* [ ] **CERIF (Common European Research Information Format):** Estándar de la UE para información de investigación.

### 4. Herramientas de Implementación

* [ ] **Validación en Runtime:**
* [ ] Tutoriales de **Pydantic V2**: Enfoque en `BaseModel`, `TypeAdapter` y validadores personalizados.

* [ ] **Generación de Código:**
* [ ] Investigar herramientas de generación de código a partir de esquemas (ej: `datamodel-code-generator` para pasar de JSON Schema a Pydantic).

## Fase 2: Formación Técnica

* [ ] **Aprendizaje Pydantic:**

  * [ ] Completar tutorial oficial: "Pydantic Models".
  * [ ] Crear un script de prueba "Hello World" con validación de tipos estricta.
  * [ ] Estudiar serialización/deserialización JSON en Pydantic.

## Fase 3: Definición Preliminar

* [ ] Crear borrador de campos mínimos obligatorios para un Investigador.
* [ ] Definir estructura de carpetas definitiva en `/src`.
