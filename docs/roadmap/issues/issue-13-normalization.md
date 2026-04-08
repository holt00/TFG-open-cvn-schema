# Issue 13 - Normalize Specification Manual And Tree Model Metadata

## Summary

Issue `#13` will build a normalized metadata layer from
`SpecificationManual.xml` and `CVNTreeModel.xml`.

## Original Goal

- parse and normalize both metadata XML sources into reusable Python
  structures keyed by CVN code and by technical path

## Original Plan

1. parse `SpecificationManual.xml`
2. parse `CVNTreeModel.xml`
3. build indexes keyed by CVN code
4. extract XML paths from the tree model
5. compare overlap and detect unresolved codes
6. expose the normalized result through reusable structures
7. preserve traceability back to source XML and source code references

## Source-Specific Requirements

- treat `SpecificationManual.xml` as the source of labels, types,
  obligatoriness, multiplicity, and reference-table assignments
- treat `CVNTreeModel.xml` as the bridge from CVN code to technical XML path
- preserve both a per-code view and a per-path view
- report mismatches instead of assuming perfect parity

## Suggested Normalized Fields

- `code`
- `manual_name`
- `manual_short_name`
- `manual_type`
- `manual_obligatory`
- `manual_multiplicity`
- `manual_reference_table`
- `tree_cvn_item_code`
- `tree_property_name`
- `tree_indicator_name`
- `tree_value`
- `xml_path`
- `source_file`

## Expected Outputs

- normalized metadata objects or dictionaries
- code-based indexes
- overlap report between manual and tree model
- list of unresolved references and mismatches

## Agreed Execution Plan

The implementation of issue `#13` will follow this agreed execution process.

### Main Objective

- build a normalized metadata layer from `SpecificationManual.xml` and
  `CVNTreeModel.xml` that can be consumed by later issues through stable views
  keyed by CVN `code` and by technical `xml_path`
- preserve traceability to the source XML files and make mismatches explicit
  instead of hiding them

### Execution Steps

1. define the normalization output contract
2. design the minimal module structure under `src/cvn_codegen/`
3. implement extraction from `SpecificationManual.xml`
4. implement extraction from `CVNTreeModel.xml`
5. define and document `xml_path` construction rules
6. unify both sources into normalized views
7. implement consistency and mismatch reporting
8. expose a reusable internal API for later issues
9. add unit and integration tests
10. document decisions, deviations, and newly discovered limits
11. update persistent documentation and any additional files required to keep
    the repository coherent

### Execution Notes

- the issue is now considered started
- development will proceed step by step
- code under `src/generated/` must not be edited manually
- hand-maintained normalization logic belongs in `src/cvn_codegen/`
- `src/models/cvn/` remains out of scope for this issue

## Current Execution State

- Issue status: in progress
- Current step: step `1` - define the normalization output contract
- Next milestone after step `1`: design the minimal module structure for the
  normalization layer

## Known Inputs From Earlier Issues

- structural bindings exist for the manual and tree-model XSDs
- `SpecificationManual.xml` parse smoke works
- `CVNTreeModel.xml` does not fully conform to its XSD, so normalization may
  need to treat the XML as a canonical source even when the binding cannot parse
  it directly in every case

## Recommended References Before Starting

- `docs/roadmap/issues/issue-12-structural-bindings.md`
- `docs/pipeline/known_limitations.md`
- `docs/pipeline/cvn_pydantic_generation_pipeline.md`

## Status

- Status: in progress
