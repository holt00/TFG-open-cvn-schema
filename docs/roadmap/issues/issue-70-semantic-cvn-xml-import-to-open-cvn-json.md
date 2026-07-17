# Issue 70 - Semantic CVN XML Import To Open CVN JSON

## Summary

Issue `#70` implements a semantic CVN XML import layer so deterministic XML
imports populate Open CVN JSON curriculum sections instead of returning only a
trace-only empty curriculum document.

This issue follows issue `#69`, where PDF import became deterministic-first and
LLM-assisted only as fallback. The current blocker is that embedded XML can be
detected and parsed, but `parse_cvn_xml(...)` still maps plausible CVN XML to an
empty Open CVN document with `mapping_status = "trace_only"`.

## Problem

Current behavior in `src/open_cvn/xml_import.py`:

- checks XML well-formedness
- detects basic CVN evidence
- extracts XML paths and CVN code-like values
- returns valid Open CVN JSON with empty curriculum sections
- stores diagnostics under `extensions["x-open-cvn.import"]`

Current limitation:

- CVN XML content is not converted into semantic Open CVN entries
- PDF import with embedded XML succeeds deterministically but may not populate the
  CV content
- issue `#69` LLM fallback is not reached when XML exists and validates, so users
  can receive a structurally valid but mostly empty import

## Goal

- convert plausible CVN XML into populated Open CVN JSON sections
- keep deterministic XML import ahead of LLM fallback
- use existing generated schema and conceptual/domain metadata instead of manual
  one-off mapping for every CVN field
- preserve unmapped source data through trace and extension metadata
- validate every generated Open CVN JSON document through
  `validate_open_cvn_json(...)`
- keep MVP behavior conservative and auditable

## Non-Goals

- do not implement a perfect full CVN XML converter for every source-package edge
  case in one issue
- do not use LLMs for XML semantic mapping
- do not remove issue `#69` LLM fallback
- do not silently drop unknown CVN fields
- do not manually hardcode all `1457` known CVN codes
- do not edit generated files under `src/generated/`
- do not commit personal CV XML/PDF fixtures

## Target Behavior

For CVN XML with recognized `CvnItem` records:

```text
CVN XML
-> parse XML
-> extract CvnItem groups and field values
-> map CVN group/field codes to Open CVN entities/fields
-> convert values to canonical JSON shapes
-> validate Open CVN JSON
-> return populated parse result
```

Example output should move from this trace-only shape:

```json
{
  "curriculum": {
    "identity": {},
    "education": [],
    "research": [],
    "professional_experience": [],
    "achievements": [],
    "other": []
  },
  "extensions": {
    "x-open-cvn.import": {
      "mapping_status": "trace_only"
    }
  }
}
```

To a semantic partial shape:

```json
{
  "curriculum": {
    "identity": {},
    "education": [
      {
        "id": "education-020-010-010-000-001",
        "type": "education.estudios_de_1o_y_2o_ciclo_y_antiguos_ciclos_licenciados_diplomados_ingenieros_superiores_ingenieros_tecnicos_arquitectos",
        "data": {
          "nombre_del_titulo": {
            "raw_value": "Doctorado en Informatica"
          }
        },
        "trace": {
          "cvn_codes": ["020.010.010.000"],
          "confidence": "medium"
        }
      }
    ],
    "research": [],
    "professional_experience": [],
    "achievements": [],
    "other": []
  },
  "extensions": {
    "x-open-cvn.xml_import": {
      "mapping_status": "semantic_partial",
      "items_seen": 1,
      "items_mapped": 1,
      "fields_seen": 1,
      "fields_mapped": 1,
      "fields_unmapped": 0
    }
  }
}
```

Exact field names depend on the generated schema annotations and conceptual
inventory, not on this example.

## Architecture Direction

The importer should use metadata already produced by previous pipeline issues:

- `schemas/open_cvn.schema.json` exposes entity and field annotations such as:
  - `x-open-cvn-entity-id`
  - `x-open-cvn-domain-area-id`
  - `x-open-cvn-source-group-key`
  - `x-open-cvn-code`
  - `x-open-cvn-domain-shape-kind`
  - `x-open-cvn-vocabulary-kind`
- `docs/pipeline/open_cvn_json_format.md` defines runtime JSON sections and entry
  shape
- `docs/pipeline/open_cvn_json_mapping.md` explains conceptual-to-JSON mapping
- `src/cvn_codegen/conceptual_model_extractor.py` and
  `src/cvn_codegen/domain_model_generator.py` show how domain areas, entities,
  attributes, and CVN codes are derived

The implementation should build a runtime mapping index from the generated JSON
Schema rather than re-running the generation pipeline at import time.

## Planned Files

- Create `src/open_cvn/xml_semantic_mapping.py`
  - loads `schemas/open_cvn.schema.json`
  - builds CVN code to Open CVN entity/field mapping
  - exposes typed mapping records
- Create `src/open_cvn/xml_semantic_extraction.py`
  - extracts `CvnItem` groups and field values from CVN XML
  - supports namespaces and simplified synthetic fixtures
  - preserves XML path and raw values
- Create `src/open_cvn/xml_value_conversion.py`
  - converts extracted XML values into Open CVN JSON-compatible primitive,
    controlled-reference, and wrapper shapes
- Create `src/open_cvn/xml_semantic_import.py`
  - orchestrates mapping, extraction, value conversion, Open CVN document building,
    validation, and import diagnostics
- Modify `src/open_cvn/xml_import.py`
  - replace trace-only default with semantic partial import
  - preserve structured errors and parser contract behavior
- Modify `src/open_cvn/parser_contract.py` only if an additional error code or
  warning code is required
- Modify `tests/test_cvn_xml_import_unit.py`
- Modify `tests/test_pdf_xml_extraction_unit.py`
- Modify `tests/test_open_cvn_app_cli_unit.py`
- Add `tests/test_xml_semantic_mapping_unit.py`
- Add `tests/test_xml_semantic_extraction_unit.py`
- Add `tests/test_xml_value_conversion_unit.py`
- Add `tests/test_xml_semantic_import_unit.py`
- Add synthetic XML fixtures under `tests/fixtures/cvn_xml/`
- Update `docs/pipeline/known_limitations.md`
- Update `docs/pipeline/parser_validator_contract.md`
- Update `docs/development/parser_workflow.md`
- Update `docs/development/llm_import_workflow.md`
- Update `docs/context/current_status.md`
- Update `docs/roadmap/cvn_generation_roadmap.md`
- Update entry-point maps if this issue is added to the repository index

## Execution Plan

### Task 1 - Baseline And Scope Confirmation

Summary: confirm current trace-only behavior, record target behavior, and avoid
guessing XML structures beyond observed fixtures and generated schema evidence.

- [ ] Subtask 1.1: Read `src/open_cvn/xml_import.py`,
  `schemas/open_cvn.schema.json`, `docs/pipeline/open_cvn_json_format.md`, and
  `docs/pipeline/open_cvn_json_mapping.md`.
- [ ] Subtask 1.2: Read current XML/PDF/import tests:
  `tests/test_cvn_xml_import_unit.py`, `tests/test_pdf_xml_extraction_unit.py`,
  and `tests/test_open_cvn_app_cli_unit.py`.
- [ ] Subtask 1.3: Run baseline tests:
  `uv run pytest -n auto tests/test_cvn_xml_import_unit.py tests/test_pdf_xml_extraction_unit.py tests/test_open_cvn_app_cli_unit.py -v`.
- [ ] Subtask 1.4: Record any implementation deviation from this plan in this
  issue file before changing scope.

### Task 2 - Runtime Mapping Index From JSON Schema

Summary: build a deterministic index that maps CVN source group and field codes
to canonical Open CVN JSON sections, entity types, and data field names.

- [ ] Subtask 2.1: Create `src/open_cvn/xml_semantic_mapping.py`.
- [ ] Subtask 2.2: Define immutable records:
  - `XmlEntityMapping`
  - `XmlFieldMapping`
  - `XmlSemanticMappingIndex`
- [ ] Subtask 2.3: Load `schemas/open_cvn.schema.json` from repository root using
  the same path approach as `src/open_cvn/json_import.py`.
- [ ] Subtask 2.4: Inspect `$defs` for entity schemas with
  `x-open-cvn-entity-id`, `x-open-cvn-domain-area-id`, and
  `x-open-cvn-source-group-key`.
- [ ] Subtask 2.5: Inspect entity `properties` for fields with
  `x-open-cvn-code`.
- [ ] Subtask 2.6: Build indexes:
  - `entities_by_group_code`
  - `fields_by_code`
  - `fields_by_group_code`
- [ ] Subtask 2.7: Add tests proving known group/field mappings exist for
  representative identity, education, and research codes.

### Task 3 - XML Semantic Extraction

Summary: extract CvnItem groups, field candidates, XML paths, and raw values from
CVN XML without depending on generated bindings.

- [ ] Subtask 3.1: Create `src/open_cvn/xml_semantic_extraction.py`.
- [ ] Subtask 3.2: Define records:
  - `ExtractedXmlField`
  - `ExtractedXmlItem`
  - `XmlSemanticExtractionResult`
- [ ] Subtask 3.3: Implement namespace-safe local-name helpers.
- [ ] Subtask 3.4: Detect simplified fixture items such as
  `<CVNItem code="020.010.010.000">`.
- [ ] Subtask 3.5: Detect official-like items such as
  `<CvnItem><CvnItemID><CodeCVNItem>020.010.010.000</CodeCVNItem>`.
- [ ] Subtask 3.6: Extract descendant field candidates from attributes, child
  code nodes, and text matching `000.000.000.000`.
- [ ] Subtask 3.7: Attach source XML paths and raw text values.
- [ ] Subtask 3.8: Add tests for synthetic namespace and non-namespace XML.

### Task 4 - Value Conversion

Summary: convert raw XML values into Open CVN JSON-compatible values using mapping
metadata and conservative conversion rules.

- [ ] Subtask 4.1: Create `src/open_cvn/xml_value_conversion.py`.
- [ ] Subtask 4.2: Convert text values to strings.
- [ ] Subtask 4.3: Convert booleans from `true`, `false`, `1`, `0`, `si`, `no`,
  `sí`, and `no`.
- [ ] Subtask 4.4: Convert decimal values when Python `Decimal` accepts the raw
  string.
- [ ] Subtask 4.5: Convert date-like values to `FlexibleDateValue` shape with
  `raw_value`, `year`, `month`, and `day` when possible.
- [ ] Subtask 4.6: Convert controlled references to `{code, label, source,
  raw_value}` where schema mapping exposes source evidence.
- [ ] Subtask 4.7: Convert wrapper-like fields for `EntityNameValue`,
  `EntityTypeValue`, `OfficialIdValue`, and `FlexibleDateValue` when the mapping
  metadata indicates wrapper shape.
- [ ] Subtask 4.8: Preserve unconverted values as `raw_value` instead of losing
  them.
- [ ] Subtask 4.9: Add tests for every conversion rule.

### Task 5 - Open CVN Document Builder

Summary: build a valid Open CVN JSON document with populated `identity`,
`education`, `research`, `professional_experience`, `achievements`, and `other`
sections.

- [ ] Subtask 5.1: Create `src/open_cvn/xml_semantic_import.py`.
- [ ] Subtask 5.2: Build the standard root shape:
  - `schema_version`
  - `metadata.source`
  - `metadata.policy`
  - `curriculum`
  - `extensions`
- [ ] Subtask 5.3: For mapped identity items, merge converted fields into
  `curriculum.identity`.
- [ ] Subtask 5.4: For mapped repeated entities, append entries to the matching
  curriculum section.
- [ ] Subtask 5.5: Generate deterministic entry IDs such as
  `education-020-010-010-000-001`.
- [ ] Subtask 5.6: Set entry `type` from `XmlEntityMapping.entity_id`.
- [ ] Subtask 5.7: Add entry trace with `cvn_codes`, `xml_paths`, and
  `confidence`.
- [ ] Subtask 5.8: Put unmapped items in `curriculum.other[]` with type
  `other.unmapped_cvn_item` and raw trace metadata.
- [ ] Subtask 5.9: Add `extensions["x-open-cvn.xml_import"]` with counts:
  - `mapping_status`
  - `items_seen`
  - `items_mapped`
  - `items_unmapped`
  - `fields_seen`
  - `fields_mapped`
  - `fields_unmapped`
  - `unmapped_codes`
- [ ] Subtask 5.10: Validate generated document through
  `validate_open_cvn_json(...)` before returning success.

### Task 6 - Parser Integration

Summary: make `parse_cvn_xml(...)` return semantic partial Open CVN JSON by
default while preserving structured failures.

- [ ] Subtask 6.1: Modify `src/open_cvn/xml_import.py` to call semantic importer
  after CVN evidence detection.
- [ ] Subtask 6.2: Keep XML well-formedness and non-CVN errors unchanged.
- [ ] Subtask 6.3: Return `valid` or `valid_with_warnings` when semantic document
  validates.
- [ ] Subtask 6.4: Return `xml_semantically_unmappable` when mapping fails in a
  way that prevents valid Open CVN JSON creation.
- [ ] Subtask 6.5: Preserve legacy trace metadata in parser trace and import
  extensions.
- [ ] Subtask 6.6: Ensure `parse_cvn_pdf(..., validate_extracted_xml=True)` uses
  semantic XML output before any LLM fallback.

### Task 7 - Synthetic Fixtures

Summary: add small non-personal XML fixtures that prove semantic mapping without
committing real CV data.

- [ ] Subtask 7.1: Add `tests/fixtures/cvn_xml/semantic_identity.xml`.
- [ ] Subtask 7.2: Add `tests/fixtures/cvn_xml/semantic_education.xml`.
- [ ] Subtask 7.3: Add `tests/fixtures/cvn_xml/semantic_research.xml`.
- [ ] Subtask 7.4: Add `tests/fixtures/cvn_xml/semantic_unmapped.xml`.
- [ ] Subtask 7.5: Keep fixture values synthetic, minimal, and non-personal.

### Task 8 - Unit And Integration Tests

Summary: prove mapping, extraction, conversion, semantic import, parser behavior,
PDF handoff, and CLI storage behavior.

- [ ] Subtask 8.1: Add `tests/test_xml_semantic_mapping_unit.py`.
- [ ] Subtask 8.2: Add `tests/test_xml_semantic_extraction_unit.py`.
- [ ] Subtask 8.3: Add `tests/test_xml_value_conversion_unit.py`.
- [ ] Subtask 8.4: Add `tests/test_xml_semantic_import_unit.py`.
- [ ] Subtask 8.5: Update `tests/test_cvn_xml_import_unit.py` so plausible XML no
  longer expects only `mapping_status = "trace_only"`.
- [ ] Subtask 8.6: Update `tests/test_pdf_xml_extraction_unit.py` so PDF with
  compatible XML imports populated semantic JSON without LLM.
- [ ] Subtask 8.7: Update `tests/test_open_cvn_app_cli_unit.py` so
  `open-cvn pdf import` with embedded XML stores semantic JSON without
  `--llm-provider`.
- [ ] Subtask 8.8: Add regression test proving LLM fallback is only used when XML
  is absent, incompatible, or cannot validate.

### Task 9 - Documentation Updates

Summary: update persistent documentation so future sessions do not rediscover the
old trace-only limitation.

- [ ] Subtask 9.1: Update `docs/pipeline/known_limitations.md` from
  `trace_only` to `semantic_partial` limitation.
- [ ] Subtask 9.2: Update `docs/pipeline/parser_validator_contract.md` XML and PDF
  sections.
- [ ] Subtask 9.3: Update `docs/development/parser_workflow.md`.
- [ ] Subtask 9.4: Update `docs/development/llm_import_workflow.md` to explain
  that embedded XML can now produce semantic partial Open CVN JSON before LLM.
- [ ] Subtask 9.5: Update `docs/context/current_status.md`.
- [ ] Subtask 9.6: Update `docs/roadmap/cvn_generation_roadmap.md`.
- [ ] Subtask 9.7: Update `PROJECT_GUIDE.md`, `AGENTS.md`, and
  `docs/context/project_context_index.md` if the issue map changes.

### Task 10 - Verification And Closure

Summary: run targeted and full verification, then record final status.

- [ ] Subtask 10.1: Run semantic XML unit tests:
  `uv run pytest -n auto tests/test_xml_semantic_mapping_unit.py tests/test_xml_semantic_extraction_unit.py tests/test_xml_value_conversion_unit.py tests/test_xml_semantic_import_unit.py -v`.
- [ ] Subtask 10.2: Run parser/PDF/CLI regression tests:
  `uv run pytest -n auto tests/test_cvn_xml_import_unit.py tests/test_pdf_xml_extraction_unit.py tests/test_open_cvn_app_cli_unit.py -v`.
- [ ] Subtask 10.3: Run MVP workflow tests:
  `uv run pytest -n auto tests/test_open_cvn_app_mvp_workflow.py -v`.
- [ ] Subtask 10.4: Run full repository suite:
  `uv run pytest -n auto tests`.
- [ ] Subtask 10.5: Record verification results and final implementation notes in
  this issue file.

## Acceptance Criteria

- `parse_cvn_xml(...)` no longer maps plausible CVN XML only to empty curriculum
  sections when recognized semantic data is present.
- XML with recognized education or research `CvnItem` records creates entries in
  `curriculum.education[]` or `curriculum.research[]`.
- Identity records merge into `curriculum.identity` when recognized.
- PDF import with embedded compatible XML uses semantic XML import before LLM.
- LLM fallback remains available only when XML is absent, incompatible, or not
  validatable.
- Unmapped CVN items or fields are preserved in trace/extensions or
  `curriculum.other[]`.
- Generated Open CVN JSON validates through `validate_open_cvn_json(...)`.
- No personal CV XML or PDF fixtures are committed.
- Full test suite passes.

## Risks And Constraints

- Official CVN XML can vary structurally. This issue should target conservative
  semantic partial import, not complete perfect import.
- JSON Schema validation proves document shape, not factual correctness.
- Some fields may remain unmapped until curated rules are added.
- Controlled references may need richer label resolution in later work.
- Wrapper conversion may be incomplete for rare source patterns.

## Expected Output

- semantic XML import modules under `src/open_cvn/`
- populated Open CVN JSON for representative XML fixtures
- deterministic PDF XML import producing populated Open CVN JSON where possible
- tests proving no LLM call is needed when embedded XML maps successfully
- updated documentation replacing the old trace-only limitation with a semantic
  partial import limitation

## Status

- Status: planned
