# CVN Generation Roadmap

## Purpose

This roadmap is the persistent implementation guide for the CVN XML/XSD to
Pydantic pipeline.

## Epic Scope

Epic reference: issue `#8`

Goal:

- establish a reproducible workflow that starts from the official CVN package,
  generates structural bindings, normalizes semantic metadata, and eventually
  emits domain-oriented Pydantic models

## Roadmap Rules

- follow issue order unless a user explicitly requests otherwise
- keep generated and hand-maintained code separated
- document implementation deviations from the original plan
- prefer reproducible artifacts over implicit knowledge

## Issue Status Overview

| Issue | Title | Status | Notes |
| --- | --- | --- | --- |
| `#11` | Project infrastructure for code generation | Completed | Baseline repository layout and config established |
| `#12` | Generate structural Pydantic bindings from CVN XSDs | Completed with documented limitations | Tree model XML/XSD mismatch remains documented |
| `#13` | Parse and normalize `SpecificationManual.xml` and `CVNTreeModel.xml` | Completed | Core normalization and auxiliary-reference resolution enrichment implemented; baseline overlap counts preserved |
| `#14` | Define semantic mapping rules and override policy | Completed | Semantic policy bundle, resolver, overrides, naming, wrapper policies, validation inventory, and tests implemented |
| `#15` | Implement the domain Pydantic model generator | Completed | Generator, shared components, wrapper-aware handoff, generated output, and verification are implemented |
| `#16` | Add automated tests for the generation pipeline | Completed | Pipeline, source coverage, wrapper, generator, importability, determinism, and E2E tests implemented |
| `#17` | Document and automate the complete workflow | Completed | Complete workflow guide, architecture updates, command sequence, verification matrix, and known limitations documented |
| `#26` | Epic for remaining Open CVN work | Planned | Placeholder epic only; details intentionally deferred after issue `#17` closure |
| `#25` | GitHub Actions CI pipeline for PR testing on main and development | Completed | PRs to `main` and `development` now run the `tests` check |
| `#41` | Epic: agnostic CVN schema, JSON schema, and parser | Completed | Conceptual IR, PlantUML diagrams, JSON Schema, Open CVN JSON format, parser contract, PDF/XML/JSON parser paths, tests, and workflow docs implemented |
| `#42` | Research Pydantic-to-UML options | Completed | Recommends conceptual IR first, PlantUML primary target, Mermaid secondary target, Pyreverse diagnostic only |
| `#43` | Define agnostic conceptual model extraction layer | Completed | Conceptual IR, extractor, targeted/full-suite tests, and extraction documentation implemented |
| `#44` | Generate UML or UML-like diagrams | Completed | PlantUML now emits readable and reference views under `docs/diagrams/`; Mermaid remains optional future output |
| `#45` | Generate JSON Schema from domain models | Completed | JSON Schema Draft 2020-12 artifact now generated from conceptual inventory under `schemas/open_cvn.schema.json` |
| `#46` | Define canonical Open CVN JSON format | Completed | Canonical root, metadata, curriculum sections, entries, trace, extensions, examples, and schema alignment implemented |
| `#47` | Define unified parser and validator contract | Completed | Public `open_cvn` contract package, structured result/error/trace models, deferred parser signatures, docs, and tests implemented |
| `#48` | Extract CVN XML from PDF inputs | Completed | Deterministic PDF XML extraction implemented behind `parse_cvn_pdf(...)` with embedded-file and XML metadata support |
| `#49` | Validate XML and JSON import paths | Completed | JSON Schema plus Pydantic Open CVN JSON validation implemented; CVN XML well-formedness, trace extraction, and trace-only Open CVN mapping implemented |
| `#50` | Add tests and documentation for parser workflow | Completed | Parser workflow docs, coverage audit, `pydantic_validation_failure` regression, drift checks, and full-suite verification completed |
| `#60` | Epic: CV management application | Planned | MVP application roadmap for local storage, master/derived versions, JSON import/export, LaTeX/PDF export, and post-MVP LLM spike expanded |
| `#61` | Application MVP scope and CLI shell | Completed | CLI-first prototype shell, command surface, console script, placeholders, and smoke tests implemented |
| `#62` | Local storage with SQLite | Completed | SQLite store initialization, schema metadata, curriculum repository, diagnostics, CLI store init, and tests implemented |
| `#63` | Master and derived curriculum versions | Completed | Schema v2 migration, master/derived repository operations, selection materialization, CLI commands, and tests implemented |
| `#64` | Open CVN JSON import/export workflow | Completed | CLI JSON import/export implemented using the public parser/validator, SQLite storage, master/derived materialization, deterministic export formatting, and tests |
| `#65` | Curriculum editing and selection MVP | Completed | Section/entry listing, derived metadata, immediate selection validation, unsupported field-edit messaging, and tests implemented |
| `#66` | LaTeX export from Open CVN | Completed | Jinja-based deterministic `.tex` export from stored master or derived Open CVN versions implemented |
| `#67` | PDF generation and preview handoff | Planned | Optional local TeX compilation and generated-PDF path handoff |
| `#68` | Application MVP tests and documentation | Planned | End-to-end MVP tests, user docs, and epic `#60` closure |
| `#69` | LLM-assisted import spike | Planned | Post-MVP exploration for PDFs without deterministic XML extraction |

Corrective planning after hotfixes `#4`, `#5`, and `#6`:

- hotfix `#4` structural-scope correction for issues `#11` and `#12` is now
  applied, including structural generation for the canonical auxiliary schema
  families (`reference_tables`, `subtypes`, `entity`, `thesaurus`)
- hotfix `#5` additive auxiliary-reference resolution layer is now implemented
  in issue `#13`, including normalization-grade loading of `ReferenceTables`,
  `Subtypes`, `Entity`, and `Thesaurus` artifacts
- issue `#14` has been completed with those corrective documents in scope rather
  than using the older reduced pipeline assumption
- pending issue documents for `#15` to `#17` must therefore be read as consumers
  of already-implemented upstream structural and normalization layers, not as
  discovery plans for those layers

## Original Integration Checkpoints

1. structural bindings reproducible from the canonical XSD package
2. manual and tree-model metadata cross-indexable by CVN code
3. normalized metadata includes deterministic auxiliary-reference resolution and
   classification
4. mapping rules for typing, naming, controlled-reference treatment,
   multiplicity, and overrides
5. domain models regenerable from semantic policy and enriched normalized
   metadata
6. documented and tested end-to-end workflow

## Issue Summaries

### Issue `#11`

- Goal:
  establish the infrastructure baseline for reproducible structural generation
- Core scope:
  - define the `src/` repository layout
  - separate generated code, manual pipeline logic, and future domain models
  - define the structural generation dependency baseline
  - version the shared xsdata configuration
  - fix the policy that the structural layer is an interoperability layer, not
    the final domain model
- Expected outputs:
  - `src/generated/`
  - `src/cvn_codegen/`
  - `src/models/cvn/`
  - `config/.xsdata.xml`
  - reproducible code generation baseline

Authoritative record:

- `docs/roadmap/issues/issue-11-project-infrastructure.md`

### Issue `#12`

- Goal:
  generate structural Pydantic bindings that mirror the official CVN XML
  schemas
- Required scope:
  - generate from `CVN.xsd`
  - generate from `SpecificationManual.xsd`
  - generate from `CVNTreeModel_v1.0.xsd`
  - generate from `ReferenceTables.xsd`
  - generate from `Subtypes.xsd`
  - generate from `Entity_v1.4.xsd`
  - generate from `Thesaurus.xsd`
  - verify include/import resolution
  - verify module importability
  - test real parsing flows where possible
  - record structural limitations detected during generation
- Implemented outcome:
  - standardized xsdata runner added
  - structural bindings generated for core and canonical auxiliary concerns
  - runner tests added
  - `SpecificationManual.xml` parse verified
  - `CVNTreeModel.xml` mismatch documented

Authoritative record:

- `docs/roadmap/issues/issue-12-structural-bindings.md`

## Documented Maintenance Hotfixes

### Hotfix `#1`

- Goal:
  replace operational `print` usage in the xsdata runner with `logging` and
  document the repository convention for logging and string interpolation
- Scope:
  - define a module logger in `src/cvn_codegen/xsdata_runner.py`
  - replace runner progress and error `print` calls with the appropriate
    logging level
  - document that `print` is reserved for direct console interaction
  - document f-strings as the project standard for interpolated strings

Authoritative record:

- `docs/roadmap/hotfixes/hotfix-1-runner-logging-convention.md`

### Hotfix `#2`

- Goal:
  introduce `PROJECT_GUIDE.md` as the human repository entry point and align
  the documentation maintenance protocol with that change
- Scope:
  - create a human-oriented entry point equivalent in practical guidance to
    `AGENTS.md`
  - stop routing human readers through `AGENTS.md` from top-level docs
  - distinguish human and agent reading orders in the persistent context docs
  - require updating `PROJECT_GUIDE.md` when human-facing repository guidance
    changes

Authoritative record:

- `docs/roadmap/hotfixes/hotfix-2-human-project-entrypoint.md`

### Hotfix `#3`

- Goal:
  document the canonical source package beyond the core structural subset and
  preserve the auxiliary-family and Annex-I coverage analysis needed by later
  issues

Authoritative record:

- `docs/roadmap/hotfixes/hotfix-3-cvn-source-package-documentation-expansion.md`

### Hotfix `#4`

- Goal:
  correct the structural scope of issues `#11` and `#12` so the repository
  infrastructure and structural generation plan cover the auxiliary source
  package families

Authoritative record:

- `docs/roadmap/hotfixes/hotfix-4-structural-scope-correction-for-auxiliary-source-package-artifacts.md`

### Hotfix `#5`

- Goal:
  correct issue `#13` so normalization grows from plain manual/tree alignment
  into an additive resolution layer over auxiliary reference sources
- Implemented outcome:
  - normalization contract enriched with typed auxiliary-reference metadata
  - normalization orchestration extended with optional auxiliary-source inputs
  - deterministic resolution now covers direct tables, subtype-backed families,
    side-package registries, side-package thesauri, hierarchical thematic
    references, unresolved cases, and under-traced documented tables

Authoritative record:

- `docs/roadmap/hotfixes/hotfix-5-normalization-resolution-layer-for-auxiliary-reference-sources.md`

### Hotfix `#6`

- Goal:
  realign the roadmap for issues `#8`, `#14`, `#15`, `#16`, and `#17` around
  the auxiliary catalog integration now known to be required

Authoritative record:

- `docs/roadmap/hotfixes/hotfix-6-roadmap-realignment-for-auxiliary-catalog-semantic-integration.md`

### Hotfix `#7`

- Goal:
  replace hardcoded semantic enum decisions with dynamic
  `ReferenceTables.xml` evidence carried through the normalization-to-semantic
  handoff
- Implemented outcome:
  - normalization metadata and reference resolution now carry dynamic enum
    evidence for `ReferenceTables.xml` cases
  - semantic policy now evaluates strict enum eligibility from evidence rather
    than temporary table-specific review handling
  - `CVN_SEX_A` is eligible from dynamic evidence, while `CVN_ENTITY_TYPE` is
    ineligible because canonical evidence includes `delegate_present`
  - full repository verification passed after implementation

Authoritative record:

- `docs/roadmap/hotfixes/hotfix-7-dynamic-reference-table-enum-eligibility-evaluation.md`

### Hotfix `#8`

- Goal:
  restore wrapper-type traceability in the normalized or semantic handoff so
  domain generation can attach wrapper-aware field shapes without re-reading raw
  structural sources
- Current status:
  - implemented and verified after issue `#15`
  - canonical domain generation now consumes typed wrapper evidence without raw
    structural rediscovery in generator logic

Authoritative record:

- `docs/roadmap/hotfixes/hotfix-8-wrapper-type-traceability-in-normalized-handoff.md`

## Future Work Focus

### Issue `#13`

- Goal:
  build a normalized metadata layer consumable by the future domain-model
  generator
- Required scope:
  - parse both metadata XML sources
  - build indexes keyed by CVN `code`
  - extract technical XML paths from the tree model
  - compare overlap and detect mismatches
  - expose reusable normalized structures with source traceability

### Issue `#14`

- Goal:
  define deterministic mapping rules from normalized CVN metadata to domain
  models
- Required scope:
  - consume enriched `reference_resolution` metadata from issue `#13`
  - type mapping rules
  - semantic policy per normalized reference kind
  - naming rules
  - `choice` and wrapper treatment
  - explicit override mechanism
  - semantic treatment for auxiliary reference families and serialization
    patterns described by hotfixes `#5` and `#6`
  - avoid re-deriving source-family or subtype-backed detection already handled
    by normalization
- Implemented outcome:
  - typed semantic policy families, enum categories, override precedence,
    Spanish-first naming, dynamic enum eligibility, wrapper treatment, and
    representative validation cases are implemented and tested
  - hotfix `#7` supplies dynamic strict enum eligibility over compact
    `ReferenceTables.xml` evidence

### Issue `#15`

- Goal:
  implement the domain model generator over normalized metadata and semantic
  rules
- Required scope:
  - traverse `CVNItem`, `Property`, and `Indicator`
  - emit first representative domain models
  - factor reusable shared domain components where appropriate
  - keep output deterministic and traceable
  - generate distinct domain representations for enums, open coded values,
    subtype-backed tables, registries, thesauri, hierarchical references,
    unresolved references, and under-traced references
  - consume semantic policy and normalized reference classifications rather than
    re-discovering auxiliary-source meaning in generator code
  - preserve `SemanticDecisionTrace` in generated artifacts or metadata so CVN
    source traceability survives the domain-generation step
- Implemented outcome:
  - deterministic domain generation is implemented from normalized metadata and
    `SemanticPolicyBundle`
  - shared domain components exist for non-enum controlled-reference families
  - canonical generated output is emitted under `src/models/cvn/generated/`
  - the canonical generator run emits `105` Python files
  - full repository verification passed after implementation
  - wrapper-aware automatic field attachment consumes hotfix `#8` structural type
    evidence

### Issue `#16`

- Goal:
  add reproducible automated tests for the structural and semantic pipeline
- Required scope:
  - fixtures from canonical XML files
  - parsing tests
  - normalization tests
  - auxiliary-resolution tests
  - semantic mapping tests
  - generator output tests per semantic class
  - import tests
  - end-to-end pipeline coverage
  - regression coverage for auxiliary structural targets and reference-resolution
    behavior
- Implemented outcome:
  - shared canonical test fixtures cover source-package paths, auxiliary bundles,
    enriched normalization, and temporary generated domain output
  - pipeline tests now cover structural generation, parse smoke behavior,
    normalization integration, reference regressions, semantic policy,
    wrapper handoff, domain generation, source coverage, importability,
    determinism, and E2E flow
  - xsdata regeneration tests are serialized under xdist with a test-only lock
  - full repository verification passed with `uv run pytest -n auto tests`

### Issue `#17`

- Goal:
  document and automate the full regeneration workflow
- Required scope:
  - architecture documentation
  - step-by-step generation workflow
  - limitation documentation
  - obvious regeneration entry point
  - final repository documentation updates
  - explicit documentation of auxiliary structural generation and
    auxiliary-reference resolution stages
  - explicit source-of-truth order for controlled-reference resolution and
    fallback behavior
- Implemented outcome:
  - complete contributor-facing regeneration guide added at
    `docs/development/regeneration_workflow.md`
  - pipeline architecture documentation now covers structural generation,
    normalization, auxiliary-reference resolution, structural type evidence,
    semantic policy, domain generation, tests, and CI
  - `SemanticPolicyBundle` is documented as the semantic source of truth for
    domain generation
  - generated-output boundaries, controlled-reference source order, wrapper
    handoff, verification matrix, and known limitations are documented

### Issue `#26`

- Goal:
  create a placeholder epic for remaining Open CVN work after issue `#17`
- Current scope:
  - create the epic record only
  - defer detailed planning until the user explicitly requests it
- Planned authoritative record:
  - `docs/roadmap/issues/issue-26-epic-remaining-open-cvn-work.md`

### Issue `#25`

- Goal:
  add a GitHub Actions pull-request test workflow for `main` and `development`
- Required scope:
  - run on pull requests targeting `main` and `development`
  - use the documented Python and `uv` environment
  - execute all automated tests under `tests/`
  - expose a stable status check for branch protection

Authoritative record:

- `docs/roadmap/issues/issue-25-github-actions-ci-pipeline-for-pr-testing-on-main-and-development.md`

### Issue `#42`

- Goal:
  research how to transform the generated and domain-oriented Pydantic model
  layer into UML or UML-like documentation that supports an agnostic curriculum
  model
- Implemented outcome:
  - generated domain model inventory was measured from the current repository
  - Pyreverse was evaluated and classified as diagnostic-only
  - PlantUML was recommended as the primary issue `#44` diagram target
  - Mermaid was recorded as a secondary Markdown-friendly target
  - direct final UML generation from generated Python classes was rejected
  - issue `#43` was directed toward a conceptual intermediate representation over
    normalized metadata, semantic policy, and generated-domain evidence

Authoritative record:

- `docs/roadmap/issues/issue-42-research-pydantic-to-uml-options.md`

### Issue `#43`

- Goal:
  define an agnostic conceptual model extraction layer between generated/domain
  Pydantic evidence and later diagram or JSON outputs
- Implemented outcome:
  - conceptual IR records are implemented in
    `src/cvn_codegen/conceptual_model_types.py`
  - conceptual extraction logic is implemented in
    `src/cvn_codegen/conceptual_model_extractor.py`
  - the extractor consumes normalization, semantic policy, and domain generation
    IR evidence instead of treating generated Python classes as the final schema
  - the inventory preserves CVN code, XML path, reference resolution, semantic
    policy, vocabulary, and limitation trace data
  - conceptual extraction rules are documented in
    `docs/pipeline/conceptual_model_extraction.md`
  - targeted conceptual-model tests and the full repository suite pass

Authoritative record:

- `docs/roadmap/issues/issue-43-agnostic-conceptual-model-extraction-layer.md`

### Issue `#44`

- Goal:
  generate readable UML or UML-like diagrams from the agnostic conceptual model
  inventory defined in issue `#43`
- Implemented outcome:
  - PlantUML rendering is implemented in
    `src/cvn_codegen/conceptual_model_diagrams.py`
  - the renderer consumes `ConceptualModelInventory` instead of generated Python,
    raw XML, or raw XSD structure as final diagram input
  - canonical `.puml` sources are generated under `docs/diagrams/`
  - readable diagrams provide a compact overview, small-area detailed views, and
    split subdiagrams for large areas such as education, research, and fallback
    concepts
  - reference diagrams preserve fuller vocabulary, attribute, and trace detail for
    auditability
  - large reference diagrams use index files, split `..._part_XX_reference.puml`
    chunks, and local `controlled references` notes instead of long global
    entity-to-vocabulary edges
  - diagram regeneration and review are documented in `docs/diagrams/README.md`
    and `docs/development/regeneration_workflow.md`
  - targeted diagram tests and full-suite verification pass

Authoritative record:

- `docs/roadmap/issues/issue-44-generate-uml-or-uml-like-diagrams.md`

### Issue `#45`

- Goal:
  generate a JSON Schema artifact for the Open CVN data representation from the
  domain/conceptual generation layer
- Implemented outcome:
  - JSON Schema generation is implemented in
    `src/cvn_codegen/json_schema_generator.py`
  - the generator consumes the issue `#43` conceptual inventory as the canonical
    root source and avoids exposing generated Python module names as the final
    schema shape
  - Pydantic v2 JSON Schema support was evaluated and retained as technical
    evidence rather than the canonical root output
  - the generated artifact is `schemas/open_cvn.schema.json`
  - the artifact declares JSON Schema Draft 2020-12, preserves Open CVN trace
    through `x-open-cvn-*` extensions, and keeps enum-ineligible references open
  - targeted JSON Schema tests passed

Authoritative record:

- `docs/roadmap/issues/issue-45-generate-json-schema-from-domain-models.md`

### Issue `#46`

- Goal:
  define the canonical Open CVN JSON document format that later parser and
  validation work will consume
- Implemented outcome:
  - the canonical JSON format is documented in
    `docs/pipeline/open_cvn_json_format.md`
  - mapping notes are documented in `docs/pipeline/open_cvn_json_mapping.md`
  - representative JSON examples exist under `examples/open_cvn/`
  - the generated JSON Schema root now follows the canonical issue `#46` shape:
    `schema_version`, `metadata`, `curriculum`, and `extensions`
  - policy metadata now lives under `metadata.policy`
  - runtime trace and extension conventions are documented for future parser work
  - targeted JSON Schema and example tests passed

Authoritative record:

- `docs/roadmap/issues/issue-46-define-canonical-open-cvn-json-format.md`

## Required Companion Documents

- architecture: `docs/pipeline/cvn_pydantic_generation_pipeline.md`
- JSON Schema generation: `docs/pipeline/json_schema_generation.md`
- limitations: `docs/pipeline/known_limitations.md`
- current state: `docs/context/current_status.md`

## Post-Parser Application Epic

Epic `#60` is the planned MVP application layer after epic `#41` completion.

Authoritative records:

- `docs/roadmap/issues/issue-60-epic-cv-management-application.md`
- `docs/roadmap/issues/issue-61-application-mvp-scope-and-cli-shell.md`
- `docs/roadmap/issues/issue-62-local-storage-sqlite-repository.md`
- `docs/roadmap/issues/issue-63-master-and-derived-curriculum-versions.md`
- `docs/roadmap/issues/issue-64-open-cvn-json-import-export-workflow.md`
- `docs/roadmap/issues/issue-65-curriculum-editing-and-selection-mvp.md`
- `docs/roadmap/issues/issue-66-latex-export-from-open-cvn.md`
- `docs/roadmap/issues/issue-67-pdf-generation-and-preview-handoff.md`
- `docs/roadmap/issues/issue-68-application-mvp-tests-and-documentation.md`
- `docs/roadmap/issues/issue-69-llm-assisted-import-spike.md`
