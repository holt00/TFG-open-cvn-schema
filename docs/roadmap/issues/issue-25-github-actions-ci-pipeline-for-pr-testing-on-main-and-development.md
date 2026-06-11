# Issue 25 - GitHub Actions CI Pipeline For PR Testing On Main And Development

## Summary

Issue `#25` adds a GitHub Actions workflow that runs the repository test suite
for pull requests targeting `main` and `development`, so proposed changes are
validated before merge.

## Original Goal

- create automated pull-request test execution for the repository
- run the full test suite from `tests/` whenever a PR is opened or updated
- expose a pass/fail GitHub check that can be required to block merging until
  tests pass

## Original Plan

1. add a GitHub Actions workflow under `.github/workflows/`
2. trigger it on `pull_request` for `main` and `development`
3. set up the documented repository environment with `uv` and Python `3.14`
4. install dependencies and the editable package
5. run the automated tests from `tests/`
6. update persistent documentation so future contributors know the CI behavior

## Adjustments Made During Implementation

1. the workflow was kept to a single `ubuntu-latest` job because the repository
   documents only one Python baseline: `3.14`
2. the workflow uses `.python-version` through `actions/setup-python` so the CI
   runner stays aligned with the repository baseline without duplicating the
   version string in multiple places
3. merge blocking is documented as a GitHub branch-protection or ruleset concern
   outside the workflow file itself; the workflow provides the `tests` status
   check that can be marked as required in the GitHub UI

## Implementation Performed

The following workflow was added:

- `.github/workflows/pr-tests.yml`

Implemented behavior:

- runs on `pull_request` targeting:
  - `main`
  - `development`
- runs for pull-request lifecycle events:
  - `opened`
  - `reopened`
  - `synchronize`
- checks out the repository
- sets up Python from `.python-version`
- installs `uv`
- synchronizes the repository environment with:
  - `uv sync --group codegen --group testing`
- installs the editable project package with:
  - `uv pip install -e .`
- runs the full automated test suite from `tests/` with:
  - `uv run pytest -n auto tests`

The workflow job is named `tests` so GitHub can expose a stable pull-request
check name for repository rules.

## Verification

Implementation verification for issue `#25` is based on the same command the
workflow executes:

```bash
uv run pytest -n auto tests
```

Expected GitHub verification after the workflow file is pushed:

1. open or update a pull request targeting `main` or `development`
2. confirm the `tests` workflow job appears in the PR checks
3. confirm the check passes when the suite passes
4. confirm the check fails when a test in `tests/` fails

## Findings

### Positive Results

- the repository now has a single documented CI entry point for pull-request
  test execution
- the workflow follows the same `uv`-based environment setup already documented
  for local development
- using `uv run pytest -n auto tests` keeps the CI scope aligned with the
  repository while using all available GitHub-hosted runner cores
  convention that all automated tests live under `tests/`

### Operational Finding

- the workflow itself reports status back to pull requests, but merge blocking is
  enforced only after the repository owner marks the `tests` check as required
  through GitHub branch protection or rulesets

## Known Limitations

- issue `#25` adds pull-request test automation only; it does not add release,
  push, lint, or matrix CI workflows
- merge blocking depends on GitHub repository settings and cannot be enforced by
  workflow YAML alone

## Impact On Future Issues

- future test additions should remain under `tests/` so they are included by the
  CI entry point without extra workflow maintenance
- issue `#16` can build on this workflow with broader coverage for:
  - auxiliary structural generation tests
  - normalization-resolution regression tests
  - future semantic-policy and domain-generator tests
- issue `#17` can reference this workflow as part of the final documented
  contributor and regeneration workflow

## Status

- Status: implemented
