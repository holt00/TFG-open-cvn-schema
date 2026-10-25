# TFG: esquema abierto y herramientas para curriculos CVN

Punto de entrada para trabajar **solo con el TFG**. No hace falta Kubernetes,
Spark ni nada del TFM.

- Memoria (PDF): [`docs/memoria/pdf/TFG.pdf`](docs/memoria/pdf/TFG.pdf)
- Fuente LaTeX de la memoria: [`docs/memoria/TFG/`](docs/memoria/TFG/)
- Estado: terminado y defendido. Su registro (issues `#11`-`#71`) esta cerrado.
- Volver al [README](README.md) | Ir al [TFM](TFM.md)

## Que hace

Define el formato abierto **Open CVN JSON** y construye, a partir del paquete
oficial CVN XML/XSD de la FECYT, todo lo necesario para generarlo, validarlo,
almacenarlo y exportarlo:

```text
XSD oficial -> bindings -> normalizacion -> politica semantica -> modelos de dominio
                                                   |
                           modelo conceptual -> diagramas + JSON Schema
                                                   |
        PDF / XML / JSON -> parser y validador -> Open CVN JSON -> CLI (SQLite, LaTeX, PDF)
```

## Puesta en marcha

Requisitos: [`uv`](https://docs.astral.sh/uv/) y Python 3.14.

```bash
uv sync --group codegen --group testing
uv pip install -e .
uv run pytest -n auto tests
```

## Casos de uso

### Usar la aplicacion de curriculos

```bash
uv run open-cvn --help
uv run open-cvn store init --path /tmp/open-cvn-demo.sqlite
uv run open-cvn json import examples/open_cvn/research_entry.json \
  --store /tmp/open-cvn-demo.sqlite --as-master
uv run open-cvn versions derive public --store /tmp/open-cvn-demo.sqlite
uv run open-cvn json export /tmp/public.json --store /tmp/open-cvn-demo.sqlite
```

Flujo completo (versiones, seleccion de entradas, LaTeX y PDF):
[`application_mvp_workflow.md`](docs/development/application_mvp_workflow.md).

### Importar y validar un CVN

PDF, XML o JSON a Open CVN JSON con el contrato unico de parser/validador:
[`parser_workflow.md`](docs/development/parser_workflow.md).

### Regenerar el pipeline desde el XSD

```bash
uv run python -m cvn_codegen.xsdata_runner all
uv run python -m cvn_codegen.domain_model_generator
uv run python -m cvn_codegen.json_schema_generator
```

Orden y verificacion completos:
[`regeneration_workflow.md`](docs/development/regeneration_workflow.md).
`src/generated/` no se edita a mano.

## Mapa del codigo

| Ruta | Contenido |
| --- | --- |
| `src/cvn_codegen/` | pipeline de generacion (normalizacion, politica semantica, modelos) |
| `src/generated/` | bindings estructurales generados |
| `src/models/cvn/` | modelos de dominio generados y componentes compartidos |
| `src/open_cvn/` | parser/validador y formato canonico Open CVN JSON |
| `src/open_cvn_app/` | aplicacion CLI local |
| `schemas/`, `examples/open_cvn/` | JSON Schema y documentos de ejemplo |
| `docs/diagrams/` | diagramas conceptuales UML-like |

## Documentacion

- Arquitectura del pipeline:
  [`cvn_pydantic_generation_pipeline.md`](docs/pipeline/cvn_pydantic_generation_pipeline.md)
- Formato Open CVN JSON: [`open_cvn_json_format.md`](docs/pipeline/open_cvn_json_format.md)
- Contrato parser/validador:
  [`parser_validator_contract.md`](docs/pipeline/parser_validator_contract.md)
- Limitaciones conocidas: [`known_limitations.md`](docs/pipeline/known_limitations.md)
- Decisiones de arquitectura: [`docs/adr/`](docs/adr/)
- Roadmap cerrado: [`cvn_generation_roadmap.md`](docs/roadmap/tfg/cvn_generation_roadmap.md)
- Registro de estado cerrado: [`current_status.md`](docs/context/tfg/current_status.md)
