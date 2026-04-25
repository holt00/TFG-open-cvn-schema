# Current Status

## Status Date

- Last updated: 2026-04-25

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

### Hotfix `#2`

- `PROJECT_GUIDE.md` now exists as the human-oriented repository entry point
- `README.md` and `CONTRIBUTING.md` now direct human readers to
  `PROJECT_GUIDE.md` instead of `AGENTS.md`
- the documentation update protocol now explicitly requires updating
  `PROJECT_GUIDE.md` when the human-facing project guidance or documentation map
  changes
- `AGENTS.md` remains the agent-specific entry point and now references the
  human guide as its counterpart

### Hotfix `#3`

- the repository now contains persistent documentation covering the auxiliary
  families of the canonical CVN source package and the full detailed sweep of
  `ReferenceTables.xml`
- the repository now contains dedicated references for:
  - serialization patterns
  - field-to-table traceability from the normalized manual layer
- documentation consistency issues across entry-point and context files were
  corrected so that current status, roadmap references, and reading order remain
  aligned
- a maintenance record for this documentation-only patch exists at:
  - `docs/roadmap/hotfixes/hotfix-3-cvn-source-package-documentation-expansion.md`

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

### Source Package Documentation Expansion

- the canonical CVN source package is now documented beyond the core structural
  subset
- new persistent reference documents added in this documentation expansion are:
  - `docs/cvn_source_package_auxiliary_artifacts.md`
  - `docs/cvn_source_package_annex_table_coverage.md`
  - `docs/cvn_annex_priority_table_families.md`
  - `docs/cvn_annex_table_families_batch3.md`
  - `docs/cvn_annex_table_families_batch4.md`
  - `docs/cvn_annex_table_families_batch5.md`
  - `docs/cvn_annex_table_families_batch6.md`
  - `docs/cvn_annex_table_families_batch7.md`
  - `docs/cvn_annex_table_families_batch8.md`
  - `docs/cvn_serialization_patterns_reference.md`
  - `docs/cvn_field_reference_traceability.md`
- the repository now records the role and relationships of the auxiliary
  families:
  - `Entity`
  - `ReferenceTables/Subtypes`
  - `Thesaurus`
- detailed coverage of the tables present in `ReferenceTables.xml` is now
  complete
- `CVN_AGENCY_C` is now explicitly documented as a manual reference without a
  clean matching table in `ReferenceTables.xml`
- `CVN_KNOW_A` is now documented as a subtype-backed industrial-property table
- `CVN_INTERVENTION_A` and `CVN_PRUEBA` are now explicitly documented as tables
  present in `ReferenceTables.xml` without clear current use in
  `SpecificationManual.xml`
- the auxiliary artifact documentation now also records real XML usage patterns
  for `Entity.xml` and `Thesaurus.xml`
- the repository now documents how to interpret the already-implemented
  `ManualCodeEntry.manual_reference_table` field without changing the existing
  normalization core
- the pipeline architecture documentation now reflects that these families are
  part of the canonical source bundle and not merely external placeholders
- the limitation register now records:
  - historical packaging drift in the auxiliary families
  - unresolved Annex-I table references such as `CVN_AGENCY_C`

### Hotfix `#4`

- a corrective hotfix record now exists for extending the structural scope of
  issues `#11` and `#12` to the auxiliary source-package families
- the documented required retrofit covers structural generation targets for:
  - `ReferenceTables.xsd`
  - `Subtypes.xsd`
  - `Entity_v1.4.xsd`
  - `Thesaurus.xsd`
  - optional repository-derived `UNESCOCodes.xsd`
- the hotfix is documentation-only and does not yet modify runner code,
  generated packages, or tests

### Hotfix `#5`

- a corrective hotfix record now exists for extending issue `#13` with an
  additive auxiliary-reference resolution layer
- the documented required retrofit covers resolution of
  `ManualCodeEntry.manual_reference_table` against:
  - `ReferenceTables.xml`
  - `Subtype_Spa.xml`
  - `Entity.xml`
  - `Thesaurus*.xml`
- the hotfix is documentation-only and does not yet modify normalization code or
  tests

### Hotfix `#6`

- a corrective hotfix record now exists for replanning issue `#8` and pending
  issues `#14` to `#17` around the auxiliary-source integration stage
- the documented required roadmap correction now makes explicit that the pending
  semantic work depends on:
  - structural visibility of auxiliary families
  - auxiliary-reference resolution over normalized manual metadata
- the hotfix is documentation-only and does not yet modify the pending issue
  files themselves

## Current Technical Baseline

- Build backend: `setuptools`
- Source layout: `src/`
- Editable install used for local development
- Structural code generation is executed from `src/` so the package name
  `generated.*` resolves to `src/generated/*`
- `tree_model` generation requires a target-specific override

## Next Planned Issue

- Next issue to start: `#14`
- Required corrective references before starting:
  - `docs/roadmap/hotfixes/hotfix-4-structural-scope-correction-for-auxiliary-source-package-artifacts.md`
  - `docs/roadmap/hotfixes/hotfix-5-normalization-resolution-layer-for-auxiliary-reference-sources.md`
  - `docs/roadmap/hotfixes/hotfix-6-roadmap-realignment-for-auxiliary-catalog-semantic-integration.md`
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

## Files Future Sessions Should Read After The Entry Points

Read the standard entry points first:

1. `AGENTS.md`
2. `PROJECT_GUIDE.md`
3. `docs/context/project_context_index.md`
4. `docs/context/current_status.md`

Then continue with these supporting files as needed:

1. `docs/roadmap/cvn_generation_roadmap.md`
2. `docs/roadmap/issues/issue-11-project-infrastructure.md`
3. `docs/roadmap/issues/issue-12-structural-bindings.md`
4. `docs/roadmap/issues/issue-13-normalization.md`
5. `docs/roadmap/issues/issue-25-github-actions-ci-pipeline-for-pr-testing-on-main-and-development.md`
6. `docs/pipeline/known_limitations.md`
7. `docs/roadmap/hotfixes/`
8. `docs/cvn_source_package_auxiliary_artifacts.md`
9. `docs/cvn_source_package_annex_table_coverage.md`
10. `docs/cvn_annex_priority_table_families.md`
11. `docs/cvn_annex_table_families_batch3.md`
12. `docs/cvn_annex_table_families_batch4.md`
13. `docs/cvn_annex_table_families_batch5.md`
14. `docs/cvn_annex_table_families_batch6.md`
15. `docs/cvn_annex_table_families_batch7.md`
16. `docs/cvn_annex_table_families_batch8.md`
17. `docs/cvn_serialization_patterns_reference.md`
18. `docs/cvn_field_reference_traceability.md`
19. `docs/roadmap/hotfixes/hotfix-4-structural-scope-correction-for-auxiliary-source-package-artifacts.md`
20. `docs/roadmap/hotfixes/hotfix-5-normalization-resolution-layer-for-auxiliary-reference-sources.md`
21. `docs/roadmap/hotfixes/hotfix-6-roadmap-realignment-for-auxiliary-catalog-semantic-integration.md`
