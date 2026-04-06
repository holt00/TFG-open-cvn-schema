# Current Status

## Status Date

- Last updated: 2026-04-06

## Completed Or Stabilized Work

### Issue `#11`

- Repository structure for the CVN generation pipeline is in place
- `src/generated/` is the destination for generated structural bindings
- `src/cvn_codegen/` is the location for hand-maintained pipeline logic
- `src/models/cvn/` exists as the target location for future domain models
- `config/.xsdata.xml` exists as the shared structural generation config
- `pyproject.toml` contains the code generation dependency group

### Issue `#12`

- Structural bindings are generated for:
  - `CVN.xsd`
  - `SpecificationManual.xsd`
  - `CVNTreeModel_v1.0.xsd`
- Generated packages exist under:
  - `src/generated/cvn`
  - `src/generated/specification_manual`
  - `src/generated/tree_model`
- A standardized generation runner exists at:
  - `src/cvn_codegen/xsdata_runner.py`
- Unit tests and smoke tests for the runner exist under `tests/`
- Package imports for generated bindings are working
- Real parse smoke result:
  - `SpecificationManual.xml`: OK
  - `CVNTreeModel.xml`: fails due to XML/XSD mismatch, documented in
    `docs/pipeline/known_limitations.md`

## Current Technical Baseline

- Build backend: `setuptools`
- Source layout: `src/`
- Editable install used for local development
- Structural code generation is executed from `src/` so the package name
  `generated.*` resolves to `src/generated/*`
- `tree_model` generation requires a target-specific override

## Next Planned Issue

- Next issue to start: `#13`
- Issue document to read first:
  - `docs/roadmap/issues/issue-13-normalization.md`

## Blocking Or Relevant Limitations

- Structural bindings do not preserve `xs:choice` semantics as strict mutual
  exclusivity in Pydantic
- Some `minOccurs` constraints are not enforced by generated list defaults
- Some attributes are generated as `object`
- `CVNTreeModel.xml` contains `<Type>` under `Indicator`, but
  `CVNTreeModel_v1.0.xsd` does not declare that child element

All of these are documented in:

- `docs/pipeline/known_limitations.md`

## Useful Commands

Synchronize the environment:

```bash
uv sync --group codegen --group testing
uv pip install -e .
```

Run structural generation:

```bash
uv run python -m cvn_codegen.xsdata_runner all
```

Run runner tests:

```bash
uv run pytest tests/test_xsdata_runner_unit.py -v
uv run pytest tests/test_xsdata_runner_smoke.py -v
```

## Files Future Sessions Must Read

1. `docs/context/project_context_index.md`
2. `docs/context/current_status.md`
3. `docs/roadmap/cvn_generation_roadmap.md`
4. `docs/roadmap/issues/issue-11-project-infrastructure.md`
5. `docs/roadmap/issues/issue-12-structural-bindings.md`
6. `docs/pipeline/known_limitations.md`
