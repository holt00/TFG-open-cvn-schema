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
<<<<<<< Updated upstream
| `#14` | Define semantic mapping rules and override policy | Pending | Depends on enriched normalization metadata from issue `#13` |
| `#15` | Implement the domain Pydantic model generator | Pending | Depends on `#13` and `#14` |
| `#16` | Add automated tests for the generation pipeline | Pending | Extend from smoke tests to pipeline tests |
| `#17` | Document and automate the complete workflow | Pending | Final workflow and documentation closure |
=======
| `#14` | Define semantic mapping rules and override policy | Planned with agreed execution policy | Semantic policy plan documented; implementation still pending and depends on enriched normalization metadata from issue `#13` after hotfix `#5` |
| `#15` | Implement the domain Pydantic model generator | Pending | Depends on `#14` semantic policy and consumes enriched normalized metadata rather than rediscovering sources |
| `#16` | Add automated tests for the generation pipeline | Pending | Must cover both core pipeline and auxiliary enrichment path |
| `#17` | Document and automate the complete workflow | Pending | Must document corrected full workflow including auxiliary stages |
>>>>>>> Stashed changes
| `#25` | GitHub Actions CI pipeline for PR testing on main and development | Completed | PRs to `main` and `development` now run the `tests` check |

Corrective planning after hotfixes `#4`, `#5`, and `#6`:

- hotfix `#4` structural-scope correction for issues `#11` and `#12` is now
  applied, including structural generation for the canonical auxiliary schema
  families (`reference_tables`, `subtypes`, `entity`, `thesaurus`)
- hotfix `#5` additive auxiliary-reference resolution layer is now implemented
  in issue `#13`, including normalization-grade loading of `ReferenceTables`,
  `Subtypes`, `Entity`, and `Thesaurus` artifacts
- issue `#14` must be started with those corrective documents in scope rather
  than using the older reduced pipeline assumption
- pending issue documents for `#14` to `#17` must therefore be read as consumers
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
<<<<<<< Updated upstream
=======
  - avoid re-deriving source-family or subtype-backed detection already handled
    by normalization
- Planning outcome:
  - typed semantic policy families, enum categories, override precedence,
    Spanish-first naming, strict enum eligibility, wrapper treatment, and
    representative validation cases are now documented in the issue record
>>>>>>> Stashed changes

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

## Required Companion Documents

- architecture: `docs/pipeline/cvn_pydantic_generation_pipeline.md`
- limitations: `docs/pipeline/known_limitations.md`
- current state: `docs/context/current_status.md`
