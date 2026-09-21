# Development Setup

## Prerequisites

- `uv`
- Python `3.14`

## Environment Setup

Pin Python if needed:

```bash
uv python pin 3.14
```

Create and synchronize the environment:

```bash
uv sync --group codegen --group testing
uv pip install -e .
```

The editable install is required so the `src/` layout is importable during
tests and local execution.

## Dependency Groups

- `codegen`: structural generation tooling, including `xsdata` and
  `xsdata-pydantic`
- `testing`: test dependencies, including `pytest` and `pytest-xdist` for
  multicore test execution

The project should use dependency groups whenever it is reasonably possible and
useful to separate concerns. As a rule:

- keep true runtime dependencies in `[project.dependencies]`
- keep structural generation tooling in `[dependency-groups].codegen`
- keep test-only tooling in `[dependency-groups].testing`

Create a new dependency group when a set of tools is clearly non-runtime and has
its own execution context, maintenance needs, or reproducibility constraints.

## Managing Dependencies

Add a dependency:

```bash
uv add <package-name>
```

Add a development-only dependency group member by editing `pyproject.toml` and
running:

```bash
uv sync --group codegen --group testing
```

When adding a new tool, prefer placing it in an existing dependency group if it
belongs clearly to code generation or testing. Create a new group only when the
tooling serves a separate workflow that would otherwise blur repository setup.

## Common Commands

For the complete regeneration workflow, see:

- `docs/development/regeneration_workflow.md`

### Structural Generation

Run one target:

```bash
uv run python -m cvn_codegen.xsdata_runner cvn
uv run python -m cvn_codegen.xsdata_runner specification_manual
uv run python -m cvn_codegen.xsdata_runner tree_model
```

Run all structural targets:

```bash
uv run python -m cvn_codegen.xsdata_runner all
```

### Tests

Use multicore pytest for default verification:

```bash
uv run pytest -n auto tests
```

All automated tests should live under `tests/` so the local and CI entry point
remains:

```bash
uv run pytest -n auto tests
```

Use targeted single-file commands only when debugging a specific failure. Keep
routine verification on `uv run pytest -n auto tests`.

Use `uv run pytest -n auto --durations=20 tests` when investigating slow tests.
Use plain non-parallel `pytest` only when debugging order-dependent or
process-isolation failures.

#### Spark tests (Docker)

The TFM's Spark jobs (`src/tfm_lakehouse/spark_jobs/`, issues `#98` and `#99`) are tested by running them in local mode
inside the project's Spark images, because PySpark cannot be installed on the host's Python 3.14. The tests are
`tests/test_silver_job_spark.py`, `tests/test_silver_resolution_spark.py` and `tests/test_gold_jobs_spark.py`; they
share `tests/spark_image.py`. They skip themselves when Docker or the images are missing (build them as described in
`infra/spark-conf/README.md`), and the gold ones also need the `postgres:17` image.

Each run is a JVM plus a Python process, so `tests/spark_image.py` lets at most four of them run at once across all
pytest workers (`pytest -n auto` starts one worker per core, and sixteen at once starved each other into timeouts and
`CANNOT_OPEN_SOCKET` errors, issue `#100`). The number comes from `SPARK_TEST_SLOTS` (default 4; use `2` on a smaller
machine). A run that is aborted has its container removed. With the cluster stopped and nothing else running, the whole
suite takes about 10 minutes; with the cluster's own load it can take longer.

### Parse Smoke Checks

Parse `SpecificationManual.xml`:

```bash
uv run python - <<'PY'
from pathlib import Path
from xsdata_pydantic.bindings import XmlParser
from generated.specification_manual import SpecificationManual

parser = XmlParser()
result = parser.from_path(
    Path("docs/CvnXML_v1.4.3_2.1_17012025/XML/SpecificationManual.xml"),
    SpecificationManual,
)
print(type(result).__name__)
PY
```

Parse `CVNTreeModel.xml` only as a known-limitation check:

```bash
uv run python - <<'PY'
from pathlib import Path
from xsdata_pydantic.bindings import XmlParser
from generated.tree_model import CvntreeModel

parser = XmlParser()
result = parser.from_path(
    Path("docs/CvnXML_v1.4.3_2.1_17012025/XML/CVNTreeModel.xml"),
    CvntreeModel,
)
print(type(result).__name__)
PY
```

This currently fails because the XML canonical file diverges from its XSD. See
`docs/pipeline/known_limitations.md`.

### Generic Python Execution Patterns

```bash
uv run python path/to/script.py
uv run python -m package.module
uv run --python 3.14 python path/to/script.py
```

### Code Quality

Ruff is not yet configured as a committed project baseline. When it is added,
its commands should also be documented here.

## Generated Code Policy

- Do not edit `src/generated/` manually
- Regenerate from source XSDs instead
- Keep manual logic in `src/cvn_codegen/`
- Keep future domain models in `src/models/cvn/`
