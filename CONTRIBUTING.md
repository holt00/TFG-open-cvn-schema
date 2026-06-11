# Contributing

## Purpose

This repository is documented with a persistent context model so that new work
sessions can resume quickly without reconstructing prior decisions from issue
threads or agent prompts.

Before starting any implementation work, read these files in order:

1. `PROJECT_GUIDE.md`
2. `docs/context/project_context_index.md`
3. `docs/context/current_status.md`
4. The issue file you are going to work on under `docs/roadmap/issues/`

## Development Setup

### Prerequisites

- `uv`
- Python `3.14`

### Environment

```bash
uv sync --group codegen --group testing
uv pip install -e .
```

Dependency groups are part of the repository convention and should be used
whenever possible and useful to keep runtime, code generation, and testing
concerns separated. Current groups are:

- `codegen`: structural generation tooling
- `testing`: test tooling

Keep true runtime dependencies in `[project.dependencies]` and prefer groups
for non-runtime tooling.

### Common Commands

Run the structural code generation runner:

```bash
uv run python -m cvn_codegen.xsdata_runner cvn
uv run python -m cvn_codegen.xsdata_runner specification_manual
uv run python -m cvn_codegen.xsdata_runner tree_model
uv run python -m cvn_codegen.xsdata_runner all
```

Run tests with multicore pytest:

```bash
uv run pytest -n auto tests
```

Run targeted single-file checks while iterating:

```bash
uv run pytest tests/test_xsdata_runner_unit.py -v
uv run pytest tests/test_xsdata_runner_smoke.py -v
```

All automated tests should be added under `tests/`.

## Pull Request CI

Pull requests targeting `main` and `development` run the automated repository
test suite through GitHub Actions.

The CI entry point is:

```bash
uv run pytest -n auto tests
```

The workflow reports a `tests` check back to the pull request. Repository branch
protection or rulesets can mark that check as required so merges are blocked
until the test suite passes.

## Documentation Update Protocol

Every issue that changes the repository must update documentation in the same
session. At minimum, update:

1. The issue document under `docs/roadmap/issues/`
2. `docs/context/current_status.md`
3. `docs/pipeline/known_limitations.md` if a new limitation was discovered
4. `docs/roadmap/cvn_generation_roadmap.md` if the roadmap state changed
5. `PROJECT_GUIDE.md` when the human-facing project entry guidance,
   documentation map, contributor reading order, or repository orientation
   changes

Update `AGENTS.md` only when the documentation map or the operational rules for
agents change.

The detailed documentation conventions live in:

- `docs/documentation/documentation_conventions.md`
