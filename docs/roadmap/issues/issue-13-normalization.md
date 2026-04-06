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

- Status: pending
