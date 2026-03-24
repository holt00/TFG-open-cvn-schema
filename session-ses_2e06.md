# Índice paso a paso para issue 11 CVN

**Session ID:** ses_2e06af124ffeRAUmwKM7dZaXGr
**Created:** 3/24/2026, 12:22:35 PM
**Updated:** 3/24/2026, 1:04:52 PM

---

## User

utilizabndo la descripcion encontrada en @AGENTS.md sobre las tareas a realizar al igual que la informacion de como realizarla encontrada en @docs/pipeline/cvn_pydantic_generation_pipeline.md . Debes indicarme como proceder en el apartado correspondiente al issue 11. debe estar indicado paso a paso, primero indicamen un indice en el que expongas todos los pasos y una pequeña descripcion de los mismos, pero nada mas. Una vez que aprueve el indice iremos paso a paso completando las cosas, unicamente se realizara un paso por mensaje y no se pasara al siguiente paso hasta que no te lo indique yo

---

## Assistant (Build · gpt-5.4 · 13.6s)

_Thinking:_

**Providing steps in Spanish**

It looks like the user is asking for an index with all the steps described briefly, and I think the answer should be in Spanish. I don’t need any tools for this, so I just need to present a clear numbered list. 

I’ll focus on detailing step 11 from the documentation, breaking it down into concise descriptions. This way, I give the user exactly what they're looking for, without any extra information!

Indice propuesto para abordar el issue `#11`:

1. Definir el objetivo y el alcance del issue
- Alinear exactamente que debe dejar resuelto `#11` y que se pospone para `#12` en adelante.

2. Revisar el estado actual del repositorio
- Identificar si ya existen `pyproject.toml`, `src/`, configuraciones parciales o decisiones previas que haya que respetar.

3. Decidir la estructura base del proyecto
- Fijar la organizacion inicial de `src/` separando claramente codigo generado, codigo del pipeline y modelos de dominio.

4. Definir las dependencias necesarias y su criterio de versionado
- Determinar que paquetes hacen falta para la infraestructura inicial y como dejarlos fijados para reproducibilidad.

5. Preparar `pyproject.toml` para la fase de generacion
- Incorporar dependencias, grupos de desarrollo y configuracion minima coherente con el pipeline.

6. Crear el arbol inicial de paquetes y modulos
- Materializar la estructura de directorios y archivos base para `generated`, `cvn_codegen` y `models/cvn`.

7. Establecer la configuracion versionada de `xsdata`
- Añadir un fichero de configuracion centralizado para evitar generacion ad hoc desde CLI sin control.

8. Definir la ubicacion oficial de la logica de codegen
- Confirmar que los scripts/modulos del pipeline viviran en `src/cvn_codegen/` y con que responsabilidades iniciales.

9. Documentar la separacion entre codigo generado y codigo manual
- Dejar escrita la norma de no editar manualmente los artefactos generados y como regenerarlos despues.

10. Verificar que la estructura soporta las dos capas del pipeline
- Comprobar que la infraestructura ya permite alojar tanto bindings estructurales como generacion semantica posterior.

11. Dejar preparado el cierre del issue `#11`
- Validar que quedan cubiertos los entregables esperados: dependencias, estructura, configuracion y convenciones documentadas.

---

## User

el plan es correcot, vamos con el paso 1

---

## Assistant (Plan · gpt-5.4 · 10.9s)

_Thinking:_

**Explaining objectives in Spanish**

I need to respond in Spanish since that seems to be the user's preference. My first step is to clearly explain the objectives and scope of issue 11 based on the documents provided. I want to keep it concise yet still useful for understanding. It’s important that I focus on clarity and relevance without making unnecessary edits or additions. Let's make sure to address the key points effectively!

Perfecto. Vamos con el paso 1.

**Paso 1 - Definir el objetivo y el alcance del issue `#11`**

El objetivo de `#11` es dejar preparada la infraestructura minima y reproducible para arrancar el pipeline de generacion CVN -> Pydantic, sin entrar todavia en la generacion real de modelos desde los XSD.

Esto significa que en este issue debe quedar resuelto:

- la base del proyecto para trabajar con code generation de forma ordenada;
- la separacion entre codigo generado y codigo manual;
- la ubicacion oficial de la logica del pipeline;
- la configuracion inicial necesaria para `xsdata`;
- las dependencias fijadas para que el entorno sea reproducible.

Y esto significa tambien lo que no pertenece todavia a `#11`:

- no generar aun los bindings estructurales desde `CVN.xsd`, `SpecificationManual.xsd` o `CVNTreeModel_v1.0.xsd`;
- no implementar aun el parseo del manual ni del tree model;
- no definir todavia las reglas semanticas finales del dominio;
- no emitir aun modelos Pydantic de dominio.

En otras palabras, `#11` debe dejar el terreno preparado para que `#12` pueda generar bindings estructurales sin tener que rediseñar el repositorio, mover carpetas o rehacer configuraciones.

Resultado esperado al cerrar este paso conceptual:

- sabemos exactamente que entregables debe producir `#11`;
- sabemos que limites no debemos sobrepasar para no mezclar trabajo de issues posteriores;
- tomamos como principio base la arquitectura en dos capas descrita en `AGENTS.md` y en `docs/pipeline/cvn_pydantic_generation_pipeline.md`: capa estructural por un lado, capa semantica por otro.

Si quieres, en el siguiente mensaje pasamos al paso 2: revisar el estado actual del repositorio.

---

## User

vamos a pasar al paso 2

---

## Assistant (Plan · gpt-5.4 · 6.7s)

_Thinking:_

**Inspecting the repository**

I need to perform a read-only inspection of the repository. To do that, I'll probably use a read or glob function. I'm thinking through the best way to approach this, especially since I want to ensure I get the details right without any unnecessary changes. It's important for me to handle it carefully, and I hope this approach works well! Let’s see how it goes!

**Tool: glob**

**Input:**
```json
{
  "pattern": "**/*",
  "path": "/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema"
}
```

**Output:**
```
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/index.lock
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/FETCH_HEAD
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/index
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/logs/refs/heads/issue-11-preparar-la-infraestructura-del-proyecto
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/logs/HEAD
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/refs/heads/issue-11-preparar-la-infraestructura-del-proyecto
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/docs/pipeline/cvn_pydantic_generation_pipeline.md
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/AGENTS.md
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/ORIG_HEAD
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/HEAD
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/logs/refs/remotes/origin/issue-11-preparar-la-infraestructura-del-proyecto
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/objects/52/cbe357d1c8cd4666698bbd66b104da769c60f8
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/objects/07/ec3d34de770b4fc98d8ac30ff88a01f2b696cc
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/objects/83/65bb96b3e8bc05a79dfd056bbe2d29dffaf8c7
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/objects/57/50f00696f3a1ef07c35db9d166c5b9b609cd0f
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/objects/6f/22256dfd24114b5514b6a741647b5459bbe100
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/objects/3e/6fe8009a2f34fb41330c9d92b5d09ca05f8a55
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/pyproject.toml
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/config
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/logs/refs/heads/11-issue-11-preparar-la-infraestructura-del-proyecto
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/refs/heads/11-issue-11-preparar-la-infraestructura-del-proyecto
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/docs/CvnXML_v1.4.3_2.1_17012025/CVN_README.md
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/logs/refs/remotes/origin/development
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/refs/remotes/origin/development
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/logs/refs/remotes/origin/11-issue-11-preparar-la-infraestructura-del-proyecto
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/logs/refs/remotes/origin/issue6-contacto-con-cvn
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/objects/7a/169756e3b7d146fd31d97c3d5bf5f749bfaf6e
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/objects/61/e9de52f66ca04edea05690837774dfc6dc963b
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/objects/a8/fd92d1062e9bb3d3246063550cfa5bf707c014
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/objects/bc/1dd12c2be2611f5f81396280ab3bdffe5dbdc5
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/objects/77/fcda28ee149868a95f9e00c426ee036d4f79d2
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/logs/refs/heads/issue6-contacto-con-cvn
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/refs/heads/issue6-contacto-con-cvn
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/objects/67/4353a7f7357b10489cb532462bc98f7e424b07
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/COMMIT_EDITMSG
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/objects/a9/2a1699a71ce130efdfe37564466598b42aa7cd
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/objects/53/474b5ab3c8ae34890b3d045f4b35f3b8e91e71
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/objects/fd/2f5cfdf076687a9b1df3debf793d3304330109
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/objects/71/5147f650d3ee3781c2ee97ec840feb4b69e79a
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/docs/informe_estructura_cvnxml_v1.4.3.md
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/docs/propuesta_modelado_uml_ocl_cvn.md
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/opencode
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/objects/34/f1e8da11e38072b56fba95b5d39e70c431eee0
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/objects/85/4d590c1e1d200c55446bc1d1c847cbc40afc1b
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/objects/6a/7ee1d4634ea264a080515e24cd6dc5d5949312
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/objects/41/5450d2065a94f9d0dac148bb1a469e4b43db9f
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/objects/bc/76cb35306b61862f3d227617a1cfbd4e54b43b
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/objects/52/3ab6231b5885abca7937211d667f043afeb5e0
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/objects/7f/47a02b07eb751e3ee2ef18c299b2729c07f6c9
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/objects/0d/53a790fb3793b095092318ce2117272aeec017
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/objects/38/6edf23091969646197a0940185397dbb726865
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/objects/cd/62afe23b459ada56849dd056e461c1d997bbe2
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/objects/01/b76da233e829ed99d6b1489ae2d005ab6e2dbf
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/docs/CvnXML_v1.4.3_2.1_17012025/XSD/SpecificationManual.xsd
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/docs/CvnXML_v1.4.3_2.1_17012025/XSD/ISOUtilities.xsd
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/docs/CvnXML_v1.4.3_2.1_17012025/XSD/CVNTreeModel_v1.0.xsd
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/docs/CvnXML_v1.4.3_2.1_17012025/XSD/CVN.xsd
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/docs/CvnXML_v1.4.3_2.1_17012025/XSD/Common.xsd
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/docs/CvnXML_v1.4.3_2.1_17012025/XSD/AuxTable.xsd
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/docs/CvnXML_v1.4.3_2.1_17012025/XML/SpecificationManual.xml
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/docs/CvnXML_v1.4.3_2.1_17012025/XML/CVNTreeModel.xml
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/docs/CvnXML_v1.4.3_2.1_17012025/Manual/TreeModel_v1.0 20090331 v1.0.pdf
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/docs/CvnXML_v1.4.3_2.1_17012025/Manual/Manual de Especificaciones Técnicas v1.4.3_v2.1.pdf
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/docs/CvnXML_v1.4.3_2.1_17012025/Leeme.txt
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/uv.lock
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/references/posibles_herramientas.md
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/references/enlaces_tutoriales.md
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/docs/research/latex_project/representacion_datos_complejos.tex
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/docs/research/latex_project/bibliografia.bib
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/docs/research/draft.txt
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/docs/descripcion_tfg_oficial.txt
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/TODO.md
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/README.md
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/LICENSE
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.python-version
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.gitignore
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/logs/refs/heads/main
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/refs/heads/main
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/refs/remotes/origin/HEAD
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/logs/refs/remotes/origin/HEAD
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/packed-refs
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/objects/pack/pack-c7303ec8ee514eac54aa84495fa42608a954b3a3.rev
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/objects/pack/pack-c7303ec8ee514eac54aa84495fa42608a954b3a3.idx
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/objects/pack/pack-c7303ec8ee514eac54aa84495fa42608a954b3a3.pack
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/info/exclude
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/description
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/hooks/pre-receive.sample
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/hooks/pre-merge-commit.sample
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/hooks/prepare-commit-msg.sample
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/hooks/sendemail-validate.sample
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/hooks/applypatch-msg.sample
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/hooks/fsmonitor-watchman.sample
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/hooks/pre-applypatch.sample
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/hooks/push-to-checkout.sample
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/hooks/update.sample
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/hooks/commit-msg.sample
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/hooks/pre-push.sample
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/hooks/pre-rebase.sample
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/hooks/post-update.sample
/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/.git/hooks/pre-commit.sample

(Results are truncated: showing first 100 results. Consider using a more specific path or pattern.)
```

**Tool: bash**

**Input:**
```json
{
  "command": "git status --short",
  "workdir": "/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema",
  "description": "Shows concise git status"
}
```

**Output:**
```
M  pyproject.toml

```

---

## Assistant (Plan · gpt-5.4 · 11.5s)

_Thinking:_



**Tool: read**

**Input:**
```json
{
  "filePath": "/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/pyproject.toml"
}
```

**Output:**
```
<path>/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/pyproject.toml</path>
<type>file</type>
<content>1: [project]
2: name = "tfg-open-cvn-schema"
3: version = "0.1.0"
4: description = "Add your description here"
5: readme = "README.md"
6: requires-python = ">=3.14"
7: dependencies = []

(End of file - total 7 lines)
</content>
```

**Tool: glob**

**Input:**
```json
{
  "pattern": "src/**",
  "path": "/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema"
}
```

**Output:**
```
No files found
```

**Tool: read**

**Input:**
```json
{
  "filePath": "/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/README.md",
  "limit": 200
}
```

**Output:**
```
<path>/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema/README.md</path>
<type>file</type>
<content>1: # Especificación de formato y herramientas para procesamiento de CV académico (Open CVN)
2: 
3: ## Descripción
4: 
5: Este Trabajo de Fin de Grado (TFG) tiene como objetivo definir un esquema de representación agnóstico al lenguaje para la representación de currículos en el ámbito universitario y de investigación en España. El proyecto busca solucionar la falta de estándares de bajo nivel en el formato CVN actual, facilitando el desarrollo de herramientas abiertas. Además, el proyecto tiene como objetivo la creación de una herramienta para la importación, modificación, almacenado y exportación utilizando el nuevo formato.
6: 
7: ## Objetivos
8: 
9: 1. **Definición de Esquema:** Crear un formato agnóstico y extensible para CVs académicos.
10: 2. **Validación:** Implementar un validador en Python usando **Pydantic**.
11: 3. **Exportación:** Desarrollar herramientas para exportar a LaTeX.
12: 4. **Importación Inteligente:** Utilizar LLMs para migrar CVNs existentes (PDF/FECYT) al nuevo formato.
13: 

(End of file - total 13 lines)
</content>
```

---

## Assistant (Plan · gpt-5.4 · 12.2s)

_Thinking:_

**Summarizing the current state**

I want to summarize step 2 based on where I currently am. I'll need to mention that there's a dirty `pyproject` file, which could be relevant to the ongoing task. I could also check the TODO list for additional context, but it might not be strictly necessary for this summary. Keeping it straightforward will help track my progress effectively!

**Paso 2 - Revisar el estado actual del repositorio**

He revisado el estado actual y, para el issue `#11`, la situacion de partida es esta:

- Existe `pyproject.toml`, pero esta casi vacio: define nombre, version, `readme`, `requires-python = ">=3.14"` y no tiene dependencias todavia.
- No existe aun `src/`; ahora mismo la base de paquetes que pide `#11` no esta creada.
- Ya existe la documentacion clave que vamos a usar como referencia:
  - `AGENTS.md`
  - `docs/pipeline/cvn_pydantic_generation_pipeline.md`
  - `docs/CvnXML_v1.4.3_2.1_17012025/...` con los XSD y XML canonicos
- `README.md` existe, pero por ahora solo describe el proyecto a alto nivel; no documenta aun la infraestructura del pipeline ni las normas de codigo generado.
- El repositorio ya tiene `uv.lock`, asi que el flujo con `uv` ya forma parte del proyecto y encaja con lo esperado en `AGENTS.md`.
- El arbol actual esta claramente en fase temprana de preparacion: mucha documentacion y fuentes CVN, pero aun sin implementacion base del pipeline.

Punto importante para no pisar trabajo existente:

- `git status --short` muestra `M  pyproject.toml`, asi que ese archivo ya tiene cambios locales respecto al ultimo commit. Cuando llegue el momento de editarlo, habra que hacerlo con cuidado y revisar su contenido actualizado antes de tocar nada.

Conclusion de este paso:

- La infraestructura pedida por `#11` no esta montada todavia.
- La prioridad real del issue es construir la base del proyecto a partir de una situacion casi vacia, pero respetando que `pyproject.toml` ya esta en estado modificado.

Si quieres, en el siguiente mensaje pasamos al paso 3: decidir la estructura base del proyecto.

---

