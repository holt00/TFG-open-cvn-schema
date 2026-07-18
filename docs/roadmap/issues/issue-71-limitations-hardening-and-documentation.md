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

### Task 1 - Scope And Baseline Audit

- Subtask 1.1: read `docs/pipeline/known_limitations.md` and list each limitation
  with one classification category.
- Subtask 1.2: read `docs/context/current_status.md` and confirm no limitation is
  missing from the current-status blocking limitations section.
- Subtask 1.3: read `docs/roadmap/cvn_generation_roadmap.md` and confirm issue
  `#71` should be represented as follow-up work after issue `#70`.
- Subtask 1.4: confirm `docs/memoria/` remains out of scope.
- Subtask 1.5: record baseline git status before edits, preserving unrelated
  untracked or user-owned files.

Expected output: confirmed limitation inventory and issue boundary.

### Task 2 - Build A Limitation Classification Matrix

- Subtask 2.1: add a classification matrix to `docs/pipeline/known_limitations.md`.
- Subtask 2.2: include columns for limitation, category, impact, current handling,
  follow-up action, and blocker status.
- Subtask 2.3: mark official source-package inconsistencies as non-project bugs.
- Subtask 2.4: mark generated binding limitations as confined to the structural
  interoperability layer when Open CVN runtime models avoid leaking the weakness.
- Subtask 2.5: mark runtime validation gaps that should be addressed in later tasks
  of this issue.

Expected output: future readers can understand what is blocked, accepted, or
actionable without reading every issue record.

### Task 3 - Document Official Source Package Constraints

- Subtask 3.1: expand the `CVNTreeModel.xml` mismatch explanation if needed.
- Subtask 3.2: ensure `CVN_AGENCY_C` is documented as unresolved from the source
  package alone.
- Subtask 3.3: ensure `Subtype_Spa.xml` bridge limitations are documented as an
  evidence problem, not an implementation oversight.
- Subtask 3.4: ensure auxiliary packaging drift is linked from the limitation
  register to the auxiliary artifact documentation.

Expected output: source-package limitations are auditable and defensible.

### Task 4 - Confirm Generated Binding Weaknesses Are Confined

- Subtask 4.1: inspect current Open CVN runtime models and generated domain
  components to verify weak structural types do not define the public JSON root.
- Subtask 4.2: add documentation explaining that `src/generated/` remains an
  interoperability layer, not the final Open CVN contract.
- Subtask 4.3: add tests only if inspection finds a public Open CVN model accepting
  an invalid wrapper or malformed value that should be rejected.
- Subtask 4.4: do not edit generated files manually.

Expected output: clear boundary between structural fidelity and Open CVN runtime
contract.

### Task 5 - Evaluate Minimal Runtime Semantic Validation

- Subtask 5.1: decide whether a small `src/open_cvn/semantic_validation.py` module
  is justified.
- Subtask 5.2: if implemented, validate only conservative rules:
  - section-compatible entry `type` prefixes
  - plausible CVN trace code format
  - controlled references carrying at least `code`, `label`, or `raw_value`
  - supported `schema_version` major version
- Subtask 5.3: return warnings rather than hard failures unless a rule is already
  part of the public Open CVN contract.
- Subtask 5.4: add focused tests in `tests/test_open_cvn_semantic_validation_unit.py`
  if a new module is created.
- Subtask 5.5: document the difference between JSON Schema validation, Pydantic
  validation, and Open CVN semantic validation.

Expected output: either a documented decision not to add runtime semantic
validation yet, or a small tested validation layer.

### Task 6 - Improve XML Semantic Partial Import Diagnostics

- Subtask 6.1: inspect `src/open_cvn/xml_semantic_import.py` diagnostics for
  counts of items and fields seen, mapped, and unmapped.
- Subtask 6.2: add missing counters only if current diagnostics are incomplete.
- Subtask 6.3: add synthetic fixtures only for non-personal XML scenarios that
  increase section coverage or unmapped preservation confidence.
- Subtask 6.4: update parser workflow documentation so `semantic_partial` is
  described as expected MVP behavior.

Expected output: XML import limitations are measurable rather than vague.

### Task 7 - Improve PDF Generation Diagnostics

- Subtask 7.1: review current missing-compiler behavior in `src/open_cvn_app/pdf.py`.
- Subtask 7.2: update `docs/development/pdf_generation_workflow.md` with install
  guidance for supported TeX engines.
- Subtask 7.3: decide whether to add a CLI diagnostic command such as
  `open-cvn pdf doctor`.
- Subtask 7.4: if a diagnostic command is added, cover available and missing
  compiler cases with mocked tests.
- Subtask 7.5: keep automated tests independent from a real local TeX installation.

Expected output: PDF generation dependency failures are explicit and user-actionable.

### Task 8 - Improve LLM Import Limitation And Provenance Handling

- Subtask 8.1: review LLM provenance stored under
  `extensions["x-open-cvn.llm_import"]`.
- Subtask 8.2: document that schema-valid LLM output is not proof of factual
  completeness or correctness.
- Subtask 8.3: add warning/provenance fields only if current results do not make
  LLM origin visible enough to downstream users.
- Subtask 8.4: preserve the current explicit opt-in requirement through
  `--allow-external-llm`.
- Subtask 8.5: keep provider calls mocked in automated tests.

Expected output: LLM import remains privacy-conscious, opt-in, validated, and
clearly non-authoritative.

### Task 9 - Add Presentation-Friendly Diagram Guidance

- Subtask 9.1: document the difference between reference diagrams and presentation
  diagrams in `docs/diagrams/README.md` if not already clear.
- Subtask 9.2: decide whether to create a small curated diagram set under
  `docs/diagrams/presentation/`.
- Subtask 9.3: if curated diagrams are added, keep canonical generated diagrams
  unchanged and document curated diagrams as human-facing views.

Expected output: diagram verbosity is managed without losing canonical traceability.

### Task 10 - Update Entry Points And Roadmap

- Subtask 10.1: update `docs/context/current_status.md` with issue `#71` as the
  current follow-up issue.
- Subtask 10.2: update `docs/roadmap/cvn_generation_roadmap.md` with issue `#71`
  status and scope.
- Subtask 10.3: update `PROJECT_GUIDE.md` if the project orientation or document
  map changes.
- Subtask 10.4: update `docs/context/project_context_index.md` if the issue map
  changes.
- Subtask 10.5: update `AGENTS.md` only if operational rules or map entries change.

Expected output: future sessions can discover issue `#71` and its purpose.

### Task 11 - Targeted Verification

- Subtask 11.1: run targeted tests for any runtime code changed in this issue.
- Subtask 11.2: if XML import diagnostics changed, run:
  `uv run pytest -n auto tests/test_xml_semantic_import_unit.py tests/test_cvn_xml_import_unit.py -v`.
- Subtask 11.3: if JSON semantic validation changed, run:
  `uv run pytest -n auto tests/test_open_cvn_json_import_unit.py tests/test_parser_validator_contract_unit.py -v`.
- Subtask 11.4: if PDF diagnostics changed, run:
  `uv run pytest -n auto tests/test_open_cvn_app_pdf_unit.py tests/test_open_cvn_app_cli_unit.py -v`.
- Subtask 11.5: if LLM provenance changed, run:
  `uv run pytest -n auto tests/test_llm_import_unit.py tests/test_llm_providers_unit.py -v`.

Expected output: targeted tests pass for all touched runtime paths.

### Task 12 - Full Verification And Closure

- Subtask 12.1: run `uv run pytest -n auto tests`.
- Subtask 12.2: record the exact result in this issue document.
- Subtask 12.3: record implementation notes and deviations in this issue document.
- Subtask 12.4: update `docs/context/current_status.md` with the final issue `#71`
  result.
- Subtask 12.5: mark this issue completed only after documentation and verification
  are both aligned.

Expected output: issue `#71` closes with documented limitations, any implemented
hardening, and verification evidence.

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

- Status: planned
