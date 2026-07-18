# Issue 71 - Limitations Hardening And Documentation

## Summary

Issue `#71` audits, classifies, documents, and selectively hardens the known
limitations that remain after issue `#70` semantic CVN XML import.

The goal is not to remove every limitation. Some limitations come from the
official CVN source package, from generated structural bindings, or from the MVP
scope. This issue should make those boundaries explicit and improve the cases
where a small runtime validation, diagnostic, fixture, or documentation change
reduces practical risk.

The `docs/memoria/` directory is intentionally out of scope for this issue.

## Current Context

The repository currently has completed implementation records for:

- reproducible CVN structural generation
- metadata normalization and auxiliary-reference resolution
- semantic policy and domain model generation
- conceptual inventory and PlantUML diagram generation
- Open CVN JSON Schema and canonical JSON format
- parser and validator contract for PDF, XML, and JSON inputs
- deterministic PDF XML extraction
- Open CVN JSON validation and CVN XML semantic partial import
- CLI-first local application MVP with SQLite storage
- master and derived curriculum versions
- JSON, LaTeX, and optional PDF export
- opt-in LLM-assisted PDF import fallback

The latest documented full-suite verification after issue `#70` is:

```text
uv run pytest -n auto tests
477 passed in 985.71s (0:16:25)
```

## Goal

- classify every current known limitation by source and impact
- distinguish blockers from accepted MVP constraints
- document official-source inconsistencies as external constraints, not project
  bugs
- harden runtime behavior where a small validation or diagnostic change provides
  value
- improve XML import coverage reporting for semantic partial imports
- improve PDF and LLM user-facing diagnostics and documentation
- make the project state easier to defend in future TFG documentation and review

## Non-Goals

- do not modify or complete `docs/memoria/`
- do not claim complete CVN XML-to-Open-CVN conversion
- do not manually edit `src/generated/`
- do not hide official source-package inconsistencies behind lossy conversions
- do not promote unresolved or weakly evidenced reference tables to strict enums
- do not require LLM output to be treated as authoritative
- do not require local PDF generation to pass when no TeX compiler is installed
- do not introduce a GUI or non-CLI application surface

## Limitation Classification

Use these categories throughout this issue:

| Category | Meaning | Expected Treatment |
| --- | --- | --- |
| `source_package_limitation` | Constraint or inconsistency in the official CVN package | Document, preserve trace, avoid pretending it is solved |
| `generated_binding_limitation` | Weakness inherited from structural code generation | Keep confined to generated/interoperability layer |
| `runtime_validation_gap` | Behavior that can be improved with Open CVN runtime checks | Add focused validation or warnings |
| `documentation_gap` | Behavior already correct but insufficiently explained | Update persistent docs |
| `future_research` | Needs external evidence, curated rules, or broader fixtures | Record follow-up without blocking MVP |

## Current Known Limitations To Review

### Official Source Package Limitations

- `CVNTreeModel.xml` contains two `<Type>` child elements under `Indicator` that
  are not declared by `CVNTreeModel_v1.0.xsd`.
- Auxiliary catalog families preserve historical packaging drift in filenames,
  schema locations, and duplicated helper artifacts.
- `CVN_AGENCY_C` appears in manual material but does not map cleanly to a matching
  `ReferenceTables.xml` table.
- `Subtype_Spa.xml` proves subtype catalog availability but does not provide a
  direct bridge from table-family names such as `CVN_KNOW_A` to subtype entries.

### Generated Binding Limitations

- `xs:choice` is not enforced as strict mutual exclusivity in generated Pydantic
  structural bindings.
- Some generated list defaults do not enforce `minOccurs` cardinality.
- Some generated attributes are typed as `object`.
- XML helper wrapper types are less ergonomic than Open CVN domain-facing values.

### Open CVN Runtime And Import Limitations

- JSON Schema cannot express every CVN semantic rule.
- CVN XML import is semantic partial for recognized items, not a complete converter
  for all possible official CVN XML records and edge cases.
- PDF import can use embedded XML deterministically, but arbitrary PDFs without
  usable XML require opt-in LLM fallback or remain unsupported.
- PDF generation requires a local `latexmk` or `pdflatex` executable.
- LLM-assisted PDF import is best-effort, provider-dependent, and requires user
  review even after local Open CVN JSON validation.

### Conceptual Documentation Limitations

- Generated conceptual diagrams can be large and verbose, especially for broad
  domain areas such as research.
- Detailed diagrams are better as reference artifacts than as compact presentation
  material.

## Planned Files

- Modify `docs/pipeline/known_limitations.md`.
- Modify `docs/context/current_status.md`.
- Modify `docs/roadmap/cvn_generation_roadmap.md`.
- Modify `PROJECT_GUIDE.md` if human-facing orientation changes.
- Modify `docs/context/project_context_index.md` if the issue map changes.
- Modify `AGENTS.md` only if operational maps or rules change.
- Modify `docs/development/parser_workflow.md` for XML import diagnostics and
  semantic partial behavior.
- Modify `docs/development/pdf_generation_workflow.md` for compiler requirements
  and diagnostics.
- Modify `docs/development/llm_import_workflow.md` for best-effort LLM limitations
  and provenance guidance.
- Modify `docs/diagrams/README.md` if presentation/reference diagram guidance is
  added.
- Optionally create `src/open_cvn/semantic_validation.py` if runtime semantic
  validation is implemented.
- Optionally modify `src/open_cvn/json_import.py` if semantic validation is wired
  into Open CVN JSON import.
- Optionally modify `src/open_cvn/parser_contract.py` only if new warning or error
  codes are needed.
- Optionally modify `src/open_cvn/xml_semantic_import.py` if XML import diagnostics
  need stronger coverage metrics.
- Optionally modify `src/open_cvn_app/pdf.py` and `src/open_cvn_app/cli.py` if PDF
  diagnostics or a `pdf doctor` command are implemented.
- Optionally modify `src/open_cvn/llm_import.py` if LLM provenance or warning
  metadata needs strengthening.
- Add or update focused tests under `tests/` only for implemented runtime changes.

## Execution Plan

This plan is executed with explicit progress markers. Every work update should
state the current `Task N/Subtask N.M`, summarize the subtask before doing it,
and end by saying whether the user needs to modify any file plus the next step.
Code changes should normally be left for the user unless the user explicitly
asks the agent to implement them.

### Task 1 - Scope, Baseline, And Work Ownership

Summary: confirm issue boundaries, preserve user-owned files, and keep the
implementation workflow explicit.

- Subtask 1.1: read `git status --short` before edits and record unrelated
  changed files as user-owned. Current known baseline includes modified
  `initial_prompt.md`, which must not be reverted or changed by this issue.
- Subtask 1.2: confirm `docs/memoria/` remains out of scope.
- Subtask 1.3: confirm `src/generated/` remains out of scope for manual edits.
- Subtask 1.4: record that documentation changes may be done by the agent, while
  code changes should be performed by the user unless explicitly delegated.

Expected output: safe baseline and clear ownership of code edits.

### Task 2 - Limitation Inventory And Classification Matrix

Summary: make all current limitations defensible through one auditable matrix.

- Subtask 2.1: read `docs/pipeline/known_limitations.md` and list each current
  limitation.
- Subtask 2.2: add a classification matrix to `docs/pipeline/known_limitations.md`
  with columns for limitation, category, impact, current handling, follow-up
  action, and blocker status.
- Subtask 2.3: classify official CVN source-package inconsistencies as
  `source_package_limitation`, not project bugs.
- Subtask 2.4: classify generated binding weaknesses as
  `generated_binding_limitation` confined to the structural interoperability
  layer when the Open CVN runtime contract avoids leaking them.
- Subtask 2.5: classify Open CVN checks, XML diagnostics, PDF generation, LLM
  provenance, and diagram usability as `runtime_validation_gap` or
  `documentation_gap` according to the final implementation.

Expected output: future readers can distinguish blockers, accepted MVP limits,
and actionable hardening items.

### Task 3 - Official Source Package Constraints

Summary: document source-package problems as external constraints with trace.

- Subtask 3.1: expand or confirm the `CVNTreeModel.xml` versus
  `CVNTreeModel_v1.0.xsd` mismatch explanation.
- Subtask 3.2: confirm `CVN_AGENCY_C` remains unresolved from the preserved
  source package alone.
- Subtask 3.3: confirm `Subtype_Spa.xml` proves subtype catalog availability but
  does not provide a direct bridge from table-family names such as `CVN_KNOW_A`.
- Subtask 3.4: link auxiliary packaging drift from the limitation register to the
  auxiliary artifact documentation.

Expected output: source-package limitations are auditable and defensible.

### Task 4 - Generated Binding Boundary Review

Summary: keep structural fidelity separate from the public Open CVN contract.

- Subtask 4.1: inspect Open CVN runtime models and generated domain components to
  verify weak structural types do not define the public JSON root.
- Subtask 4.2: document that `src/generated/` remains an interoperability layer,
  not the final Open CVN contract.
- Subtask 4.3: add tests only if inspection finds a public Open CVN model accepting
  an invalid wrapper or malformed value that should already be rejected.
- Subtask 4.4: do not edit generated files manually.

Expected output: clear boundary between generated structural bindings and runtime
Open CVN validation.

### Task 5 - Minimal Runtime Semantic Validation Decision

Summary: add only conservative semantic warnings if they reduce risk without
rejecting valid unusual documents.

- Subtask 5.1: decide whether a small `src/open_cvn/semantic_validation.py` module
  is justified.
- Subtask 5.2: if implemented by the user, validate only conservative warning
  rules: section-compatible entry `type` prefixes, plausible CVN trace code
  format, and controlled references carrying at least `code`, `label`, or
  `raw_value`.
- Subtask 5.3: keep these checks as warnings unless a rule is already part of the
  public Open CVN contract.
- Subtask 5.4: if implemented, add focused tests in
  `tests/test_open_cvn_semantic_validation_unit.py` and regression coverage in
  `tests/test_open_cvn_json_import_unit.py`.
- Subtask 5.5: document the difference between JSON Schema validation, Pydantic
  validation, and optional Open CVN semantic warnings.

Expected output: either a documented decision not to add runtime semantic
validation yet, or a small tested warning layer.

### Task 6 - XML Semantic Partial Import Diagnostics

Summary: make semantic partial XML import measurable rather than vague.

- Subtask 6.1: inspect `src/open_cvn/xml_semantic_import.py` diagnostics. Current
  known diagnostics already include `items_seen`, `items_mapped`,
  `items_unmapped`, `fields_seen`, `fields_mapped`, `fields_unmapped`, and
  `unmapped_codes`.
- Subtask 6.2: if implemented by the user, add only missing high-value metrics
  such as `mapped_sections`, `section_counts`, or mapping coverage percentages.
- Subtask 6.3: add synthetic non-personal XML fixtures only if they increase
  section coverage or unmapped preservation confidence.
- Subtask 6.4: update `docs/development/parser_workflow.md` so
  `semantic_partial` and `trace_only` are described as expected MVP diagnostics,
  not proof of complete CVN conversion.

Expected output: XML import limitations are measurable and documented.

### Task 7 - Python-Managed TeX Engine For PDF Generation

Summary: make PDF generation work from Python-managed requirements where feasible,
without relying only on a system TeX install.

- Subtask 7.1: document the dependency research result: PyPI packages such as
  `PyLaTeX`, `latex`, `latex2pdf`, and PyPI `tinytex` do not provide a reliable
  LaTeX engine; the real `tectonic` project ships a single executable rather than
  a usable PyPI engine package.
- Subtask 7.2: update the intended compiler discovery order to prefer a managed
  `tectonic` executable, then system `tectonic`, then `latexmk`, then `pdflatex`.
- Subtask 7.3: if implemented by the user, add a managed Tectonic binary download
  and cache layer, with platform detection, version pinning, hash verification
  when practical, and a cache path such as `~/.cache/open-cvn/tectonic/`.
- Subtask 7.4: preserve offline behavior: if no cached managed engine and no
  system engine exists, fail with an actionable diagnostic rather than silently
  skipping PDF generation.
- Subtask 7.5: keep automated tests independent from a real local TeX install and
  from real network access by mocking downloader, cache, compiler lookup, and
  runner behavior.
- Subtask 7.6: update `docs/development/pdf_generation_workflow.md` to explain
  managed Tectonic, cache behavior, offline behavior, system fallback, and
  remaining limitations.

Expected output: PDF generation no longer depends exclusively on a separately
installed system TeX distribution when the managed Tectonic path is available.

### Task 8 - PDF Doctor Command

Summary: give users one command to diagnose local PDF generation readiness.

- Subtask 8.1: if implemented by the user, add `open-cvn pdf doctor` to inspect
  managed Tectonic cache availability, system `tectonic`, `latexmk`, `pdflatex`,
  cache path, and recommended next action.
- Subtask 8.2: ensure `pdf doctor` does not compile a real document by default.
- Subtask 8.3: add mocked CLI and PDF unit tests for available engine, missing
  engine, cached managed engine, and unavailable managed download scenarios.
- Subtask 8.4: document `pdf doctor` in `docs/development/pdf_generation_workflow.md`.

Expected output: PDF generation dependency failures become user-actionable before
running a full export.

### Task 9 - LLM Import Limitation And Provenance Handling

Summary: keep LLM import visibly non-authoritative and review-required.

- Subtask 9.1: review provenance stored under
  `extensions["x-open-cvn.llm_import"]`.
- Subtask 9.2: document that schema-valid LLM output is not proof of factual
  completeness or correctness.
- Subtask 9.3: if implemented by the user, add explicit provenance fields such as
  `review_required: true` and `authoritative: false` only if current provenance is
  not visible enough to downstream users.
- Subtask 9.4: preserve the explicit opt-in requirement through
  `--allow-external-llm`.
- Subtask 9.5: keep provider calls mocked in automated tests.

Expected output: LLM import remains privacy-conscious, opt-in, locally validated,
and clearly non-authoritative.

### Task 10 - Diagram PNG Audit And Generator Improvements

Summary: use the existing rendered PNGs to identify concrete diagram usability
problems, then improve generated diagrams without manual diagram edits.

- Subtask 10.1: audit existing `docs/diagrams/*.png` dimensions. Current observed
  high-risk renders include `open_cvn_research_060.png` at `3660 x 1571`,
  `open_cvn_other_040.png` at `3062 x 1065`, `open_cvn_education_030.png` at
  `3033 x 1318`, and tall reference chunks such as
  `open_cvn_research_050_part_02_reference.png` at `1678 x 2269`.
- Subtask 10.2: classify diagram size and readability as `documentation_gap`, not
  a pipeline correctness bug.
- Subtask 10.3: if implemented by the user, modify
  `src/cvn_codegen/conceptual_model_diagrams.py` so large readable views are split
  as well as large reference views. Priority split targets are `research_060`,
  `other_040`, and `education_030`.
- Subtask 10.4: if implemented by the user, add presentation-friendly generated
  diagrams such as `open_cvn_presentation_overview.puml` and a compact import or
  workflow view. These should contain few boxes, no attributes, and be suitable
  for TFG slides or memory figures.
- Subtask 10.5: if implemented by the user, improve rendered labels for fallback
  names such as `PublicacionNombre030090000330` by using a shorter human label and
  preserving the CVN code in attributes or notes, while keeping PlantUML aliases
  deterministic.
- Subtask 10.6: keep `.puml` files as canonical generated artifacts and treat PNGs
  as derived review artifacts.
- Subtask 10.7: update `docs/diagrams/README.md` with the three diagram tiers:
  readable, reference, and presentation.

Expected output: diagram output remains traceable, while large PNGs become easier
to inspect and presentation use gets a compact generated option.

### Task 11 - Entry Points, Roadmap, And Persistent Docs

Summary: make issue `#71` discoverable from future sessions.

- Subtask 11.1: update `docs/context/current_status.md` with issue `#71` as the
  current or completed follow-up issue.
- Subtask 11.2: update `docs/roadmap/cvn_generation_roadmap.md` with issue `#71`
  status and scope.
- Subtask 11.3: update `docs/context/project_context_index.md` so issue `#71` is
  listed in the roadmap map.
- Subtask 11.4: update `PROJECT_GUIDE.md` only if human-facing orientation or the
  document map changes.
- Subtask 11.5: update `AGENTS.md` only if operational rules or map entries
  change.

Expected output: future sessions can discover issue `#71`, its purpose, and its
status.

### Task 12 - Targeted Verification

Summary: run only verification relevant to touched areas before the full suite.

- Subtask 12.1: if semantic validation changed, run
  `uv run pytest -n auto tests/test_open_cvn_semantic_validation_unit.py tests/test_open_cvn_json_import_unit.py tests/test_parser_validator_contract_unit.py -v`.
- Subtask 12.2: if XML diagnostics changed, run
  `uv run pytest -n auto tests/test_xml_semantic_import_unit.py tests/test_cvn_xml_import_unit.py -v`.
- Subtask 12.3: if PDF engine or doctor behavior changed, run
  `uv run pytest -n auto tests/test_open_cvn_app_pdf_unit.py tests/test_open_cvn_app_cli_unit.py -v`.
- Subtask 12.4: if LLM provenance changed, run
  `uv run pytest -n auto tests/test_llm_import_unit.py tests/test_llm_providers_unit.py -v`.
- Subtask 12.5: if diagrams changed, run
  `uv run pytest -n auto tests/test_conceptual_model_diagrams_unit.py tests/test_generation_pipeline_conceptual_diagrams.py -v`.

Expected output: targeted tests pass for all touched runtime or generation paths.

### Task 13 - Full Verification And Closure

Summary: close issue `#71` only after docs, any user-made code changes, and tests
are aligned.

- Subtask 13.1: run `uv run pytest -n auto tests`.
- Subtask 13.2: record the exact result in this issue document.
- Subtask 13.3: record implementation notes and deviations in this issue document.
- Subtask 13.4: update `docs/context/current_status.md` with the final issue `#71`
  result.
- Subtask 13.5: mark this issue completed only after documentation and
  verification are both aligned.

Expected output: issue `#71` closes with classified limitations, selected
hardening, PDF engine strategy, diagram PNG audit, and verification evidence.

## Acceptance Criteria

- Every limitation currently listed in `docs/pipeline/known_limitations.md` is
  classified by source and impact.
- Limitations caused by the official CVN package are documented as external source
  constraints.
- Generated binding weaknesses are clearly separated from the Open CVN public JSON
  contract.
- XML import is documented as semantic partial, with diagnostics sufficient to
  measure mapped and unmapped content.
- PDF generation documentation clearly explains local TeX compiler requirements.
- LLM import documentation clearly explains opt-in behavior, provider dependency,
  validation limits, provenance, and user review needs.
- Any runtime code change has focused tests.
- `src/generated/` is not manually edited.
- `docs/memoria/` is not modified by this issue.
- Persistent project context and roadmap documents are updated if issue `#71`
  status changes.
- Full repository verification is run or any inability to run it is explicitly
  documented.

## Expected Output

- updated limitation register with classification and blocker status
- clearer documentation for official source-package constraints
- optional small runtime validation or diagnostics improvements where justified
- improved XML semantic partial import documentation and possibly coverage metrics
- improved PDF generation and LLM import limitation documentation
- roadmap and current-status updates for issue `#71`
- verification record

## Risks And Constraints

- Some limitations should remain documented rather than patched because patching
  would misrepresent the official CVN source package.
- Adding too much semantic validation could reject valid-but-unusual CVN-derived
  Open CVN documents; prefer warnings for conservative checks.
- Adding curated diagram views must not replace canonical generated diagrams.
- LLM output can pass schema validation while remaining factually incomplete.
- PDF generation cannot be guaranteed on machines without a local TeX engine.

## Status

- Status: completed
- Completed on: 2026-07-18

## Implementation Notes

- Added a classified limitation matrix to `docs/pipeline/known_limitations.md`
  covering official source-package constraints, generated binding limits,
  runtime validation gaps, documentation gaps, and future-research items.
- Documented official-source constraints as external limitations, including the
  `CVNTreeModel.xml`/`CVNTreeModel_v1.0.xsd` mismatch, unresolved
  `CVN_AGENCY_C`, subtype-family bridging limits, and auxiliary packaging drift.
- Documented the boundary between `src/generated/` structural interoperability
  bindings and the public Open CVN JSON runtime contract.
- Implemented conservative Open CVN semantic warnings after JSON Schema and
  Pydantic validation for section/type consistency, plausible CVN trace codes,
  and empty controlled-reference values.
- Extended semantic partial CVN XML import diagnostics with mapping coverage,
  mapped sections, and section counts.
- Added managed Tectonic support for PDF generation with cache discovery,
  optional download, hash verification, system fallback, and `open-cvn pdf
  doctor` diagnostics.
- Marked LLM-assisted imports explicitly as `review_required: true` and
  `authoritative: false` in provenance metadata.
- Improved conceptual diagram generation with split readable views, a compact
  presentation overview diagram, deterministic label cleanup, and updated diagram
  tier documentation.

## Deviations From Original Plan

- Runtime code changes were implemented by the agent after the user authorized
  end-to-end implementation. The original issue text said code changes should
  normally be left to the user unless explicitly delegated.
- PDF generation hardening went beyond documentation by adding a managed Tectonic
  binary strategy. It still preserves offline failure behavior and does not make
  PDF generation mandatory when no compiler is available.
- Diagram hardening changed the generator and regenerated canonical `.puml`
  artifacts; PNG files remain derived review artifacts and were not treated as
  canonical sources.
- `src/generated/` was not manually edited.
- `docs/memoria/` was not modified.

## Verification

- Targeted semantic validation, XML diagnostics, PDF, CLI, LLM, and diagram
  verification passed with:
  `uv run pytest -n auto tests/test_open_cvn_semantic_validation_unit.py tests/test_open_cvn_json_import_unit.py tests/test_parser_validator_contract_unit.py tests/test_xml_semantic_import_unit.py tests/test_cvn_xml_import_unit.py tests/test_open_cvn_app_pdf_unit.py tests/test_open_cvn_app_cli_unit.py tests/test_llm_import_unit.py tests/test_llm_providers_unit.py tests/test_conceptual_model_diagrams_unit.py tests/test_generation_pipeline_conceptual_diagrams.py -v`
- Targeted verification result: `108 passed in 69.88s (0:01:09)`
- Full-suite verification passed with: `uv run pytest -n auto tests`
- Full-suite verification result: `488 passed in 845.43s (0:14:05)`
