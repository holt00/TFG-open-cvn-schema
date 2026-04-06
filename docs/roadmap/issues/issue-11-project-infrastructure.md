# Issue 11 - Project Infrastructure For Code Generation

## Summary

Issue `#11` established the repository baseline required for the CVN generation
pipeline. It did not generate final bindings or domain models. Its role was to
fix the repository structure, generation tooling, and structural generation
policy so later issues could build on a stable foundation.

## Original Goal

- prepare the project infrastructure for reproducible code generation
- define the repository layout for generated code, manual pipeline logic, and
  future domain models
- standardize the use of `xsdata` and `xsdata-pydantic`

## Original Plan

1. adopt a `src/` layout
2. reserve `src/generated/` for generated structural bindings
3. reserve `src/cvn_codegen/` for hand-maintained pipeline logic
4. reserve `src/models/cvn/` for domain-facing models
5. define code generation dependencies separately from runtime dependencies
6. add a shared `xsdata` configuration file under `config/.xsdata.xml`
7. treat the structural layer as a faithful interoperability layer rather than
   the final domain model

## Adjustments Made During Implementation

The original infrastructure plan proved directionally correct, but by the time
issue `#12` started two operational adjustments were needed to make the
baseline fully usable:

1. `src/models/cvn/` had to be created explicitly to match the planned layout
2. editable packaging support was added so the `src/` layout would be importable
   during tests and local execution

These adjustments did not change the conceptual architecture of `#11`; they
made the baseline operational.

## Implementation Performed

### Repository Layout

The baseline layout established by issue `#11` is:

```text
src/
├── generated/
│   ├── cvn/
│   ├── specification_manual/
│   └── tree_model/
├── cvn_codegen/
└── models/
    └── cvn/
```

### Tooling Baseline

- dependency management: `uv`
- structural generation tooling: `xsdata[cli,lxml]`
- Pydantic binding support: `xsdata-pydantic`
- structural generation config: `config/.xsdata.xml`

### Packaging Baseline

To support the `src/` layout in practice, the repository now also has:

- a `setuptools` build backend in `pyproject.toml`
- editable installation support for local development
- `src/cvn_codegen/__init__.py` so the package is importable during tests and
  runner execution

## Verification

The infrastructure was validated by successfully using it in issue `#12` to:

- generate structural bindings under `src/generated/`
- import the runner from `cvn_codegen`
- run `pytest` against the runner tests

## Findings

- The original architectural decisions from issue `#11` were sufficient and did
  not require redesign
- The `src/` layout benefits from explicit packaging support when tests and
  module execution start relying on it

## Known Limitations

- Issue `#11` intentionally did not solve semantic modeling concerns
- It also did not define the full regeneration workflow end-to-end; that work
  continues through issues `#12` to `#17`

## Impact On Future Issues

- Issue `#12` reuses the exact structural package layout defined here
- Issues `#13` to `#15` depend on the separation between generated artifacts and
  manual pipeline logic
- Issue `#17` will document the workflow, but it is grounded in the structure
  introduced here

## Status

- Status: completed and validated as the operational baseline for the CVN
  generation roadmap
