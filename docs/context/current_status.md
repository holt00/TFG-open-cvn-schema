# Current Status

## Status Date

- Last updated: 2026-07-06

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
- auxiliary-source loading and resolution support is now implemented under:
  - `src/cvn_codegen/auxiliary_sources/`
- normalized aggregate entries now include additive
  `reference_resolution` metadata for manual references when auxiliary-source
  inputs are provided
- nested `CVNItem` traversal under `Property` is implemented to match the
  documented tree-model structure and restore the expected overlap counts
- normalization-related verification passes for:
  - `tests/test_manual_metadata_unit.py`
  - `tests/test_tree_metadata_unit.py`
  - `tests/test_normalization_report_unit.py`
  - `tests/test_normalization_unit.py`
  - `tests/test_auxiliary_source_loaders_unit.py`
  - `tests/test_auxiliary_reference_resolution_unit.py`
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
  - unresolved auxiliary references
  - documented under-traced auxiliary tables
- current auxiliary-reference resolution explicitly covers:
  - direct `ReferenceTables.xml` tables
  - subtype-backed table families through auxiliary catalog availability
  - side-package registry references backed by `Entity.xml`
  - side-package thesaurus references backed by `Thesaurus.xml`
  - hierarchical thematic cases such as `UNESCO_CODES`
- currently unresolved auxiliary references reported by normalization include:
  - `CVN_AGENCY_C`
- documented under-traced auxiliary tables now reported explicitly:
  - `CVN_INTERVENTION_A`
  - `CVN_PRUEBA`

### Issue `#25`

- a GitHub Actions workflow now exists at `.github/workflows/pr-tests.yml`
- pull requests targeting `main` or `development` now run the repository test
  suite automatically when opened, reopened, or updated
- the workflow installs the documented `uv` environment, performs the editable
  install, and runs `uv run pytest -n auto tests`
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
  part of the canonical source bundle recently delivered by FECYT and not
  merely external placeholders
- the limitation register now records:
  - historical packaging drift in the auxiliary families
  - unresolved Annex-I table references such as `CVN_AGENCY_C`

### Hotfix `#4`

- the hotfix corrective scope for issues `#11` and `#12` is now implemented for
  canonical auxiliary source-package families
- structural generation targets now include:
  - `ReferenceTables.xsd`
  - `Subtypes.xsd`
  - `Entity_v1.4.xsd`
  - `Thesaurus.xsd`
- generated packages now exist under:
  - `src/generated/reference_tables`
  - `src/generated/subtypes`
  - `src/generated/entity`
  - `src/generated/thesaurus`
- runner and smoke/unit test coverage were expanded for auxiliary targets
- auxiliary parse checks are executable for:
  - `ReferenceTables.xml`
  - `Subtype_Spa.xml`
  - `Entity.xml`
  - `Thesaurus.xml`
- core regression validation after auxiliary integration passed with both:
  - file-level checks (`cvn=5`, `specification_manual=3`, `tree_model=2`)
  - behavioral checks (runner tests, imports, parse checks)

### Hotfix `#5`

- the corrective hotfix for extending issue `#13` with an additive
  auxiliary-reference resolution layer is now implemented
- the implemented retrofit resolves `ManualCodeEntry.manual_reference_table`
  against:
  - `ReferenceTables.xml`
  - `Subtype_Spa.xml`
  - `Entity.xml`
  - `Thesaurus*.xml`
- the normalization contract now includes additive resolution metadata through:
  - `ReferenceResolution`
  - `ReferenceResolutionTrace`
- the normalization orchestration now accepts auxiliary-source inputs and
  enriches `NormalizedCodeEntry` values with `reference_resolution`
- dedicated loader and resolution tests now exist for the hotfix implementation
- current documented implementation limits remain:
  - `Subtype_Spa.xml` proves subtype catalog availability but does not expose a
    direct table-family key such as `CVN_KNOW_A`
  - side-package resolution remains artifact-level and not domain-level

### Hotfix `#6`

- a corrective hotfix record now exists for replanning issue `#8` and pending
  issues `#14` to `#17` around the auxiliary-source integration stage introduced
  by the modules recently added in the bundle sent by FECYT
- the documented required roadmap correction now makes explicit that the pending
  semantic work depends on:
  - structural visibility of auxiliary families
  - auxiliary-reference resolution over normalized manual metadata
- the affected pending issue documents and roadmap records are now updated so
  they describe semantic and workflow work as consumers of the already
  implemented hotfix `#4` and hotfix `#5` layers instead of future discovery
  tasks

### Hotfix `#7`

- the corrective hotfix for replacing table-specific semantic enum decisions
  with dynamic `ReferenceTables.xml` evidence is implemented and verified
- `ReferenceTableMetadata` now exposes item-code, preferred-label, duplicate,
  blank, other-like, hierarchy, delegate, and open-world-signal evidence
- `ReferenceResolution.reference_table_enum_evidence` now carries typed evidence
  for direct `ReferenceTables.xml` and subtype-backed table resolutions
- `semantic_policy.py` now evaluates strict enum eligibility dynamically through
  `evaluate_reference_table_enum_eligibility(...)` instead of temporary
  table-name-specific review handling
- `CVN_SEX_A` is dynamically enum-eligible; `CVN_ENTITY_TYPE` is dynamically
  enum-ineligible because canonical evidence includes `delegate_present`
- full-suite verification passed with `uv run pytest -n auto tests`
  and result `146 passed in 404.14s (0:06:44)`

### Issue `#14`

- the semantic mapping rules issue is implemented in
  `src/cvn_codegen/semantic_policy.py`
- semantic-policy unit tests are implemented in
  `tests/test_semantic_policy_unit.py`
- the implemented policy consumes the issue `#13` normalization contract,
  including `reference_resolution.source_artifact` and
  `reference_resolution.semantic_kind`
- issue `#14` created explicit typed policy contracts under
  `src/cvn_codegen/` without editing `src/generated/`
- the implemented policy covers:
  - semantic base kinds
  - controlled-reference domain shapes
  - strict enum eligibility
  - wrapper and `xs:choice` treatment
  - presence and cardinality mapping
  - Spanish-first domain naming
  - deterministic override precedence
  - representative validation cases for handoff into issue `#15`
- issue `#14` now uses dynamic enum evidence from hotfix `#7` for compact
  enum-like `ReferenceTables.xml` cases instead of temporary review-required
  handling
- strict enum eligibility is evidence-backed for direct reference tables:
  `CVN_SEX_A` is eligible, while `CVN_ENTITY_TYPE` is ineligible due to
  `delegate_present`
- the user reported that the semantic-policy tests, regression tests, and full
  repository test suite passed after the original issue `#14` implementation
- final domain model emission is now implemented by completed issue `#15`

### Hotfix `#8`

- the corrective hotfix for wrapper type traceability is implemented and verified
- the authoritative record exists at
  `docs/roadmap/hotfixes/hotfix-8-wrapper-type-traceability-in-normalized-handoff.md`
- `src/cvn_codegen/structural_type_trace.py` now resolves structural type
  evidence from `CVN.xsd`, `Common.xsd`, and normalized `CVNTreeModel.xml`
  paths
- normalized entries can now carry `StructuralTypeEvidence` through
  `TreePathEntry.structural_type_evidence` and
  `NormalizedCodeEntry.structural_type_evidence`
- canonical domain generation passes `CVN.xsd` and `Common.xsd` into
  normalization so wrapper evidence is available without generator-side raw XSD
  scanning
- semantic policy now attaches wrapper policies for terminal wrapper evidence
  from `FlexibleDatesType`, `OfficialIdType`, `EntityTypeType`, and
  `EntityNameType`
- shared wrapper value components now exist for `FlexibleDateValue`,
  `OfficialIdValue`, `EntityTypeValue`, and `EntityNameValue`
- child alternatives such as `DNI` preserve ancestor wrapper trace without being
  treated as terminal wrapper fields
- full-suite verification passed with `uv run pytest -n auto tests`
  and result `228 passed in 189.76s (0:03:09)`

### Issue `#15`

- the domain model generator issue is implemented in
  `src/cvn_codegen/domain_model_generator.py`
- generator intermediate representation records are implemented in
  `src/cvn_codegen/domain_model_types.py`
- shared hand-maintained domain components are implemented in
  `src/models/cvn/components.py`
- final generated domain output is emitted under `src/models/cvn/generated/`
- the canonical generation command is:
  `uv run python -m cvn_codegen.domain_model_generator`
- the canonical generation run produced `105` generated Python files
- the generated package imports were verified for:
  - `models.cvn.generated`
  - `models.cvn.generated.enums`
  - `models.cvn.generated.manual_only`
- generated domain models inherit `cvn_trace` from `BaseCvnDomainModel`
- controlled-reference families now emit distinct domain shapes for strict enums,
  open coded values, measure-or-scale values, identifier references, scope
  references, subtype-backed values, hierarchical references, registry
  references, vocabulary references, unresolved references, and under-traced
  references
- wrapper-aware fields now consume hotfix `#8` structural type evidence and map
  to shared wrapper value components when canonical XSD enrichment is provided
- latest full-suite verification passed with `uv run pytest -n auto tests`
  and result `228 passed in 189.76s (0:03:09)`

### Issue `#16`

- automated generation pipeline tests are implemented under `tests/`
- shared canonical test fixtures now exist in `tests/conftest.py` for canonical
  XML/XSD paths, auxiliary bundles, XSD-enriched normalization, and temporary
  domain output
- new pipeline coverage includes:
  - core and auxiliary structural generation targets
  - real XML parse smoke behavior for specification manual and auxiliary sources
  - documented `CVNTreeModel.xml` parse mismatch behavior
  - canonical normalization baseline and enriched auxiliary-reference resolution
  - representative reference regressions for direct, subtype-backed,
    side-package, hierarchical, unresolved, and under-traced references
  - semantic policy integration, override precedence, Spanish-first naming, trace
    preservation, and wrapper handoff behavior
  - canonical domain generator behavior, importability, rendered-output
    determinism, ASCII output, and end-to-end generation
  - explicit source coverage for manual items, tree codes, auxiliary catalog
    items, normalized entries, semantic policies, domain generation, and core
    `AuxTable.xsd` structural enums
- xsdata generation tests now use a test-only file lock in
  `tests/xsdata_generation_lock.py` so shared `src/generated/*` regeneration is
  serialized under `pytest -n auto`
- targeted issue `#16` verification passed with:
  `uv run pytest -n auto tests/test_generation_pipeline_structural.py tests/test_generation_pipeline_parse_smoke.py tests/test_generation_pipeline_normalization_integration.py tests/test_generation_pipeline_reference_regressions.py tests/test_generation_pipeline_semantic_integration.py tests/test_generation_pipeline_wrapper_handoff.py tests/test_generation_pipeline_domain_generation.py tests/test_generation_pipeline_e2e.py -v`
  and result `61 passed in 146.76s (0:02:26)`
- final full-suite verification passed with `uv run pytest -n auto tests`
- final full-suite verification after the source-coverage audit passed with
  `uv run pytest -n auto tests` and result `294 passed in 277.77s (0:04:37)`

### Issue `#17`

- complete workflow documentation is implemented
- the contributor-facing regeneration guide now exists at:
  - `docs/development/regeneration_workflow.md`
- the pipeline architecture documentation now describes the full implemented
  workflow from canonical source inputs through structural generation,
  normalization, auxiliary-reference resolution, structural type evidence,
  semantic policy, domain generation, tests, and CI
- the documented canonical command sequence is:
  - `uv sync --group codegen --group testing`
  - `uv pip install -e .`
  - `uv run python -m cvn_codegen.xsdata_runner all`
  - `uv run python -m cvn_codegen.domain_model_generator`
  - `uv run pytest -n auto tests`
- workflow documentation records `SemanticPolicyBundle` as the semantic source of
  truth for domain generation
- workflow documentation records the controlled-reference source-of-truth order,
  wrapper handoff through `StructuralTypeEvidence`, generated-output boundaries,
  verification matrix, and known limitations
- baseline verification during issue `#17` passed with:
  - `uv run pytest -n auto tests`
  - result: `294 passed in 297.99s (0:04:57)`
- canonical domain generator verification during issue `#17` passed with:
  - `uv run python -m cvn_codegen.domain_model_generator`
  - result: `Generated 105 files`

### Issue `#42`

- Pydantic-to-UML research is completed and recorded in:
  - `docs/roadmap/issues/issue-42-research-pydantic-to-uml-options.md`
- current generated domain inventory was measured from the repository:
  - generated Python files excluding `__init__.py`: `104`
  - generated domain model classes: `103`
  - generated enum classes: `13`
  - shared component classes: `17`
  - generated domain model fields: `1487`
- direct UML generation from generated Python classes is not recommended for
  final conceptual documentation
- Pyreverse was evaluated through a tiny local experiment under `/tmp/opencode`
  and classified as diagnostic-only for this repository
- Pydantic metadata can expose useful technical facts such as field names, type
  annotations, required flags, list defaults, shared value objects, and JSON
  Schema `$defs`, but it does not provide enough field-level CVN trace or
  conceptual grouping by itself
- issue `#43` should define a conceptual intermediate representation consuming
  normalized metadata, semantic policy, and generated-domain evidence rather than
  treating generated Python classes as the final schema
- issue `#44` should render diagrams from that conceptual IR, with PlantUML as the
  recommended primary target and Mermaid as an optional Markdown-friendly
  secondary target

### Issue `#43`

- the agnostic conceptual model extraction layer is implemented under
  `src/cvn_codegen/`
- conceptual IR records now exist in:
  - `src/cvn_codegen/conceptual_model_types.py`
- conceptual extraction logic now exists in:
  - `src/cvn_codegen/conceptual_model_extractor.py`
- the extractor consumes `DomainGenerationResult`, `NormalizedCodeEntry`,
  `SemanticFieldPolicy`, and `SemanticDecisionTrace` instead of treating generated
  Python classes as the final schema
- the inventory includes domain areas, conceptual entities, attributes,
  conservative relationships, vocabularies, trace data, and limitations
- a stable `core.curriculum` root entity is emitted for later diagram and JSON
  schema work
- identity fields under technical placeholder groups are remapped by CVN code
  prefix so `000.*` fields form a conceptual identity area
- conceptual extraction rules are documented in:
  - `docs/pipeline/conceptual_model_extraction.md`
- targeted verification passed with:
  `uv run pytest -n auto tests/test_conceptual_model_extractor_unit.py tests/test_generation_pipeline_conceptual_model.py`
- targeted verification result:
  `13 passed in 74.28s (0:01:14)`
- full-suite verification passed with:
  `uv run pytest -n auto tests`
- full-suite verification result:
  `307 passed in 318.93s (0:05:18)`

### Issue `#44`

- UML-like diagram generation from the agnostic conceptual inventory is
  implemented under `src/cvn_codegen/`
- PlantUML rendering logic now exists in:
  - `src/cvn_codegen/conceptual_model_diagrams.py`
- The renderer consumes `ConceptualModelInventory` from issue `#43`; it does not
  generate final diagrams directly from generated Python classes, raw XML, or raw
  XSD structure
- Canonical generated PlantUML sources now exist under:
  - `docs/diagrams/`
- Generated diagram sources now include two complementary views:
  - readable views for navigation and presentation
  - reference views for fuller attribute, vocabulary, and trace detail
- Detailed reference chunks now render controlled-vocabulary membership as local
  notes next to each entity instead of long global dependency edges, avoiding
  dangling-looking lines and PNG clipping in large education/research chunks
- Large areas such as education, research, and fallback `other` concepts now
  generate readable split subdiagrams in addition to area-level index views;
  oversized reference sections can drill down to `..._part_XX_reference.puml`
  detail chunks
- Rendered PNGs are optional review artifacts derived from the canonical `.puml`
  sources
- Diagram regeneration and review guidance is documented in:
  - `docs/diagrams/README.md`
  - `docs/development/regeneration_workflow.md`
- Targeted diagram verification passed with:
  `uv run pytest -n auto tests/test_conceptual_model_diagrams_unit.py tests/test_generation_pipeline_conceptual_diagrams.py`
- Targeted verification result:
  `6 passed in 63.21s (0:01:03)`
- Full-suite verification passed with:
  `uv run pytest -n auto tests`
- Full-suite verification result:
  `313 passed in 715.42s (0:11:55)`

### Issue `#45`

- JSON Schema generation from the agnostic conceptual inventory is implemented
  under `src/cvn_codegen/`
- JSON Schema generation logic now exists in:
  - `src/cvn_codegen/json_schema_generator.py`
- The generator consumes `ConceptualModelInventory` from issue `#43`; it does not
  use raw XML, raw XSD, generated structural bindings, or generated Python class
  names as the canonical root shape
- Pydantic v2 JSON Schema support was evaluated during the implementation spike:
  - current generated domain package exports `103` Pydantic model classes
  - current generated domain package exports `13` enum classes
  - Pydantic emits useful component schemas but does not add `$schema`
    automatically
- The canonical generated JSON Schema artifact now exists at:
  - `schemas/open_cvn.schema.json`
- The artifact declares JSON Schema Draft 2020-12 and includes Open CVN metadata,
  conceptual entity definitions, vocabulary definitions, shared wrapper value
  definitions, and non-validating `x-open-cvn-*` trace extensions
- Controlled vocabulary treatment is evidence-backed:
  - `CVN_SEX_A` is emitted as a closed enum-backed vocabulary definition
  - `CVN_ENTITY_TYPE` remains open because semantic policy marks it
    enum-ineligible
- The issue `#45` generation approach is documented in:
  - `docs/pipeline/json_schema_generation.md`
- Targeted JSON Schema verification passed with:
  `uv run pytest -n auto tests/test_json_schema_generator_unit.py tests/test_generation_pipeline_json_schema.py -v`
- Targeted verification result:
  `13 passed in 109.45s (0:01:49)`
- Full-suite verification passed with:
  `uv run pytest -n auto tests`
- Full-suite verification result:
  `326 passed in 780.28s (0:13:00)`
- Additional manual schema checks passed for:
  - canonical regeneration without artifact drift
  - JSON parsing
  - root metadata
  - `$defs` presence and internal `$ref` resolution
  - `core.curriculum` and `identity.person` definitions
  - `CVN_SEX_A` closed enum behavior
  - `CVN_ENTITY_TYPE` open reference behavior
  - temporary CLI output byte-for-byte equality
  - historical issue `#45` provisional root example shape
- issue `#46` later replaced the issue `#45` provisional root with the canonical
  Open CVN JSON root: `schema_version`, `metadata`, `curriculum`, and
  `extensions`
- External `jsonschema` meta-schema validation was not executed because the
  `jsonschema` package is not installed in the project environment

### Issue `#46`

- the canonical Open CVN JSON format is documented in:
  - `docs/pipeline/open_cvn_json_format.md`
- mapping notes from conceptual inventory and schema annotations to runtime JSON
  are documented in:
  - `docs/pipeline/open_cvn_json_mapping.md`
- representative JSON examples now exist under:
  - `examples/open_cvn/`
- the canonical JSON root shape is now:
  - `schema_version`
  - `metadata`
  - `curriculum`
  - `extensions`
- semantic policy metadata now lives under `metadata.policy` instead of root-level
  `policy_name` and `policy_version`
- curriculum content is grouped by conceptual domain area, with `identity` as a
  single object and repeated sections represented as arrays of entries
- controlled references use a common runtime shape while keeping enum-ineligible,
  unresolved, registry, thesaurus, hierarchical, and subtype-backed references
  open
- the JSON Schema generator now emits the issue `#46` canonical root shape while
  preserving conceptual `$defs`
- targeted issue `#46` verification passed with:
  `uv run pytest -n auto tests/test_json_schema_generator_unit.py tests/test_generation_pipeline_json_schema.py tests/test_open_cvn_json_format_examples.py -v`
- targeted verification result:
  `21 passed in 159.97s (0:02:39)`
- full-suite verification passed with:
  `uv run pytest -n auto tests`
- full-suite verification result:
  `334 passed in 890.21s (0:14:50)`

### Issue `#47`

- the unified parser and validator contract is implemented under:
  - `src/open_cvn/`
- the public contract module is:
  - `src/open_cvn/parser_contract.py`
- the public package exports:
  - `CvnSourceFormat`
  - `CvnValidationStatus`
  - `CvnIssueSeverity`
  - `CvnErrorCode`
  - `CvnParseIssue`
  - `CvnParseTrace`
  - `CvnParseResult`
  - `parse_cvn_pdf(...)`
  - `parse_cvn_xml(...)`
  - `parse_open_cvn_json(...)`
  - `validate_open_cvn_json(...)`
- public parser and validator functions intentionally raise `NotImplementedError`
  because real parsing and validation are deferred to issues `#48` and `#49`
- parser result invariants now require error-bearing results to use `invalid` or
  `failed`, and `valid_with_warnings` results to include warning issues
- the contract documentation exists at:
  - `docs/pipeline/parser_validator_contract.md`
- contract-only tests exist at:
  - `tests/test_parser_validator_contract_unit.py`
- targeted issue `#47` verification passed with:
  `uv run pytest -n auto tests/test_parser_validator_contract_unit.py -v`
- targeted verification result:
  `14 passed in 2.07s`
- full-suite verification passed with:
  `uv run pytest -n auto tests`
- full-suite verification result:
  `348 passed in 857.18s (0:14:17)`

### Issue `#48`

- deterministic CVN XML extraction from PDF inputs is implemented behind the
  public issue `#47` contract
- the PDF extraction helper exists at:
  - `src/open_cvn/pdf_xml_extraction.py`
- `parse_cvn_pdf(...)` in `src/open_cvn/parser_contract.py` now accepts PDF paths
  and PDF bytes and returns `CvnParseResult`
- PyMuPDF is now a runtime dependency for PDF embedded-file and XML metadata
  access
- implemented extraction sources are:
  - embedded PDF files
  - PDF XML metadata when it contains CVN XML evidence
- extracted candidates must be well-formed XML and plausibly CVN-related before
  being returned
- successful PDF extraction returns `validation_status=not_run` because XML
  import, XML-to-domain mapping, and Open CVN validation remain deferred to issue
  `#49`
- PDF failure behavior is structured through the issue `#47` error contract:
  - unreadable PDF inputs return `unreadable_file`
  - readable PDFs without extractable CVN XML return
    `pdf_without_extractable_xml`
  - unsupported input shapes return `unsupported_input_format`
- no OCR, page text reconstruction, LLM reconstruction, or domain validation is
  attempted in the PDF path
- synthetic PyMuPDF PDF tests cover embedded XML, XML metadata, PDFs without XML,
  unreadable inputs, unsupported mapping inputs, and no page-text fallback
- targeted issue `#48` verification passed with:
  `uv run pytest -n auto tests/test_pdf_xml_extraction_unit.py tests/test_parser_validator_contract_unit.py -v`
- targeted verification result:
  `20 passed in 2.64s`
- full-suite verification passed with:
  `uv run pytest -n auto tests`
- full-suite verification result:
  `354 passed in 850.95s (0:14:10)`

### Issue `#49`

- Open CVN JSON import validation is implemented behind the issue `#47` public
  parser contract
- CVN XML import validation is implemented behind the issue `#47` public parser
  contract
- new runtime modules exist under:
  - `src/open_cvn/import_utils.py`
  - `src/open_cvn/json_import.py`
  - `src/open_cvn/open_cvn_models.py`
  - `src/open_cvn/xml_import.py`
- `parse_open_cvn_json(...)` now accepts path, inline JSON string, JSON bytes, and
  mapping inputs
- `validate_open_cvn_json(...)` validates the generated
  `schemas/open_cvn.schema.json` Draft 2020-12 artifact before applying Pydantic
  runtime model checks
- JSON import failures are reported through structured issue `#47` errors:
  - `invalid_json`
  - `json_schema_validation_failure`
  - `pydantic_validation_failure`
- `parse_cvn_xml(...)` now accepts path, inline XML string, and XML bytes inputs
- CVN XML import performs well-formedness checks, CVN plausibility checks, XML path
  trace extraction, and CVN code-like trace extraction
- plausible CVN XML currently maps to a conservative Open CVN trace-only document
  with import diagnostics under `extensions["x-open-cvn.import"]`
- full semantic XML-to-domain mapping remains a documented limitation because the
  runtime importer does not yet have enough curated mapping behavior for arbitrary
  CVN XML records
- synthetic JSON and XML fixtures exist under:
  - `tests/fixtures/open_cvn/`
  - `tests/fixtures/cvn_xml/`
- targeted issue `#49` verification passed with:
  `uv run pytest -n auto tests/test_open_cvn_json_import_unit.py tests/test_cvn_xml_import_unit.py tests/test_parser_validator_contract_unit.py -v`
- targeted verification result:
  `28 passed in 16.04s`
- full-suite verification passed with:
  `uv run pytest -n auto tests`
- full-suite verification result:
  `369 passed in 347.12s (0:05:47)`

## Current Technical Baseline

- Build backend: `setuptools`
- Source layout: `src/`
- Editable install used for local development
- Structural code generation is executed from `src/` so the package name
  `generated.*` resolves to `src/generated/*`
- `tree_model` generation requires a target-specific override

## Next Planned Work

- Next work item after issue `#49` closure: continue the post-parser Open CVN
  roadmap, including richer XML semantic mapping or downstream import/export
  behavior when a later issue defines that scope

## Blocking Or Relevant Limitations

- Structural bindings do not preserve `xs:choice` semantics as strict mutual
  exclusivity in Pydantic
- Some `minOccurs` constraints are not enforced by generated list defaults
- Some attributes are generated as `object`
- `CVNTreeModel.xml` contains `<Type>` under `Indicator`, but
  `CVNTreeModel_v1.0.xsd` does not declare that child element
- `Subtype_Spa.xml` does not provide a direct table-family bridge for strict
  per-table subtype verification in the current normalization layer
- strict enum eligibility for compact `ReferenceTables.xml` tables now uses
  hotfix `#7` evidence in the normalization-to-semantic handoff
- wrapper-aware domain attachment requires normalization runs that provide
  `cvn_xsd_path` and `common_xsd_path`; canonical generation provides them
- issue `#49` XML import is currently trace-only for plausible CVN XML and does
  not yet perform full semantic XML-to-domain mapping

All of these are documented in:

- `docs/pipeline/known_limitations.md`

## Useful Commands

Synchronize the environment, including multicore pytest support:

```bash
uv sync --group codegen --group testing
uv pip install -e .
```

Run structural generation:

```bash
uv run python -m cvn_codegen.xsdata_runner all
```

Run canonical domain generation:

```bash
uv run python -m cvn_codegen.domain_model_generator
```

Run canonical conceptual diagram generation:

```bash
uv run python -m cvn_codegen.conceptual_model_diagrams --output-dir docs/diagrams
```

Run canonical JSON Schema generation:

```bash
uv run python -m cvn_codegen.json_schema_generator
```

Run the full repository test suite with multicore pytest:

```bash
uv run pytest -n auto tests
```

Use the full-suite multicore command as the default verification command. Use
single-file pytest commands only when debugging a specific failure.

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
6. `docs/development/regeneration_workflow.md`
7. `docs/pipeline/known_limitations.md`
8. `docs/pipeline/parser_validator_contract.md`
9. `docs/roadmap/hotfixes/`
10. `docs/cvn_source_package_auxiliary_artifacts.md`
11. `docs/cvn_source_package_annex_table_coverage.md`
12. `docs/cvn_annex_priority_table_families.md`
13. `docs/cvn_annex_table_families_batch3.md`
14. `docs/cvn_annex_table_families_batch4.md`
15. `docs/cvn_annex_table_families_batch5.md`
16. `docs/cvn_annex_table_families_batch6.md`
17. `docs/cvn_annex_table_families_batch7.md`
18. `docs/cvn_annex_table_families_batch8.md`
19. `docs/cvn_serialization_patterns_reference.md`
20. `docs/cvn_field_reference_traceability.md`
21. `docs/roadmap/hotfixes/hotfix-4-structural-scope-correction-for-auxiliary-source-package-artifacts.md`
22. `docs/roadmap/hotfixes/hotfix-5-normalization-resolution-layer-for-auxiliary-reference-sources.md`
23. `docs/roadmap/hotfixes/hotfix-6-roadmap-realignment-for-auxiliary-catalog-semantic-integration.md`
