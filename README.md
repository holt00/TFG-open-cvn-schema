# Especificación de formato y herramientas para procesamiento de CV académico (Open CVN)

## Descripción

Este Trabajo de Fin de Grado (TFG) tiene como objetivo definir un esquema de datos (basado en JSON) para la representación de currículos en el ámbito universitario y de investigación en España. El proyecto busca solucionar la falta de estándares de bajo nivel en el formato CVN actual, facilitando el desarrollo de herramientas abiertas.

## Objetivos

1. **Definición de Esquema:** Crear un formato agnóstico y extensible para CVs académicos.
2. **Validación:** Implementar un validador en Python usando **Pydantic**.
3. **Exportación:** Desarrollar herramientas para exportar a LaTeX.
4. **Importación Inteligente:** Utilizar LLMs para migrar CVNs existentes (PDF/FECYT) al nuevo formato.

## Tecnologías

* **Lenguaje:** Python 3.x (A decidir aun)
* **Validación:** Pydantic
* **Base de Datos:** MongoDB (NoSQL)
* **IA:** OpenAI API / Groq
* **Documentación:** LaTeX

<!--## Instalación
```bash
pip install -r requirements.txt
```
-->
