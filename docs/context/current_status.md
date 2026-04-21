# Current Status

## Status Date

- Last updated: 2026-04-21

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

### Hotfix `#1`

- `src/cvn_codegen/xsdata_runner.py` now reports operational status through
  `logging` instead of `print`
- `print` is reserved for direct console interaction examples and ad hoc shell
  snippets
- project conventions now explicitly require f-strings for string interpolation
  in repository code instead of old `%`-style formatting

### Issue `#13`

- normalization output contract is implemented through typed structures in
  `src/cvn_codegen/normalization_types.py`
- extraction from `SpecificationManual.xml` is implemented in
  `src/cvn_codegen/manual_metadata.py`
- extraction from `CVNTreeModel.xml` is implemented in
  `src/cvn_codegen/tree_metadata.py`
- normalization orchestration is implemented in
  `src/cvn_codegen/normalization.py`
- mismatch reporting is implemented in
  `src/cvn_codegen/normalization_report.py`
- nested `CVNItem` traversal under `Property` is implemented to match the
  documented tree-model structure and restore the expected overlap counts
- normalization-related verification passes for:
  - `tests/test_manual_metadata_unit.py`
  - `tests/test_tree_metadata_unit.py`
  - `tests/test_normalization_report_unit.py`
  - `tests/test_normalization_unit.py`
- verified normalization baseline:
  - total normalized codes: `1457`
  - manual-only codes: `27`
  - tree-only codes: `1`
  - overlapping codes: `1429`
- current mismatch reporting includes:
  - codes present only in `SpecificationManual.xml`
  - codes present only in `CVNTreeModel.xml`
  - the two documented unexpected `<Type>` child elements in
    `CVNTreeModel.xml`

### Issue `#25`

- a GitHub Actions workflow now exists at `.github/workflows/pr-tests.yml`
- pull requests targeting `main` or `development` now run the repository test
  suite automatically when opened, reopened, or updated
- the workflow installs the documented `uv` environment, performs the editable
  install, and runs `uv run pytest tests`
- the workflow job is named `tests` so GitHub can report a stable PR check
- all automated repository tests are expected to live under `tests/`
- merge blocking depends on GitHub branch protection or rulesets marking the
  `tests` check as required

## Current Technical Baseline

- Build backend: `setuptools`
- Source layout: `src/`
- Editable install used for local development
- Structural code generation is executed from `src/` so the package name
  `generated.*` resolves to `src/generated/*`
- `tree_model` generation requires a target-specific override

## Next Planned Issue

- Next issue to start: `#14`
- Issue document to read first:
  - `docs/roadmap/issues/issue-14-semantic-mapping-rules.md`

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

Run the full repository test suite:

```bash
uv run pytest tests
```

## Files Future Sessions Must Read

1. `docs/context/project_context_index.md`
2. `docs/context/current_status.md`
3. `docs/roadmap/cvn_generation_roadmap.md`
4. `docs/roadmap/issues/issue-11-project-infrastructure.md`
5. `docs/roadmap/issues/issue-12-structural-bindings.md`
6. `docs/roadmap/issues/issue-13-normalization.md`
7. `docs/roadmap/issues/issue-25-github-actions-ci-pipeline-for-pr-testing-on-main-and-development.md`
8. `docs/pipeline/known_limitations.md`
9. `docs/roadmap/hotfixes/hotfix-1-runner-logging-convention.md`
