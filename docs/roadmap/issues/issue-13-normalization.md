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

## Progress So Far

### Step `1` - Normalization Output Contract

- completed
- the normalization layer is designed around typed reusable structures rather
  than a single flat dictionary
- the agreed output contract is based on:
  - `ManualCodeEntry`
  - `TreePathEntry`
  - `NormalizedCodeEntry`
  - `NormalizationMismatch`
  - `NormalizationResult`
- `NormalizationMismatch.kind` uses an enum-like constrained design through
  `NormalizationMismatchKind`

### Step `2` - Minimal Module Structure

- completed
- the agreed structure under `src/cvn_codegen/` is:
  - `normalization_types.py`
  - `manual_metadata.py`
  - `tree_metadata.py`
  - `normalization.py`
  - `normalization_report.py`
- the structure is intentionally flat for now, while keeping future migration to
  a normalization subpackage cheap if the project grows

### Step `3` - Extraction From `SpecificationManual.xml`

- completed
- implemented in `src/cvn_codegen/manual_metadata.py`
- current responsibilities covered:
  - load and parse `SpecificationManual.xml`
  - select the preferred localized `NameDetail`
  - build normalized `ManualCodeEntry` instances
  - expose a code-indexed view of manual entries
- current tests exist for:
  - file loading
  - preferred language selection
  - known code mapping
  - duplicate detection
  - canonical entry count expectations

### Step `4` - Extraction From `CVNTreeModel.xml`

- completed
- implemented in `src/cvn_codegen/tree_metadata.py`
- the tree model is parsed with direct XML traversal rather than the generated
  structural binding because the canonical XML does not fully conform to its XSD
- current responsibilities covered:
  - load and parse `CVNTreeModel.xml`
  - strip namespaces and read local attributes
  - build stable tree-path entries
  - recursively traverse `Property` and `Indicator`
  - extract entries from `Version`, `Agent`, and `CVNItem`
  - expose grouping by `code` and by `xml_path`
- unit tests exist for the tree traversal and indexing layer

### Step `5` - `xml_path` Convention

- completed
- a repository-level convention for `xml_path` has been defined and validated
  against the available tree-model documentation and the canonical XML

### Step `6` - Unified Normalized Views

- completed
- the normalization orchestration layer has started in
  `src/cvn_codegen/normalization.py`
- the current implementation already covers:
  - collection of the full code universe from manual and tree-model sources
  - construction of a normalized per-code view through
    `NormalizedCodeEntry`
  - assembly of a normalized code index
  - orchestration of the full loading and normalization flow into
    `NormalizationResult`
- dedicated tests exist for `normalization.py`

### Step `7` - Consistency And Mismatch Reporting

- completed
- mismatch reporting is now implemented in
  `src/cvn_codegen/normalization_report.py`
- the current implementation covers:
  - reusable mismatch construction through `build_mismatch`
  - `MANUAL_ONLY_CODE` reporting
  - `TREE_ONLY_CODE` reporting
  - explicit structural reporting for the two known unexpected `<Type>` child
    elements in `CVNTreeModel.xml`
  - combined mismatch aggregation for inclusion in `NormalizationResult`
- the normalization orchestration layer now populates
  `NormalizationResult.mismatches`
- tests now exist for:
  - `normalization_report.py`
  - mismatch integration in `normalization.py`
- current known reported structural cases:
  - `060.030.070.220`
  - `060.030.070.230`
- scope decision for issue `#13`:
  - the current mismatch set is considered sufficient for this issue
  - issue `#13` should report known documented source inconsistencies and
    source-overlap mismatches, but should not expand yet into a broader dynamic
    anomaly-detection framework
  - richer mismatch discovery may be added later if needed, but it is not a
    blocker for completing the normalization stage of issue `#13`

### Step `8` - Reusable Internal API

- in progress
- the agreed API strategy for issue `#13` is:
  - use `build_normalization_result(...)` from
    `src/cvn_codegen/normalization.py` as the recommended consumer entry point
  - keep helper functions importable when later issues need partial reuse, but
    treat them as secondary helpers rather than the preferred integration path
- current official entry point:
  - `from cvn_codegen.normalization import build_normalization_result`
- current API guarantees for later issues:
  - normalized view by CVN `code`
  - normalized view by technical `xml_path`
  - explicit `manual_only_codes`
  - explicit `tree_only_codes`
  - explicit known mismatch collection
- current helper functions remain importable for advanced or partial reuse:
  - `collect_all_code(...)`
  - `build_normalized_code(...)`
  - `build_normalized_code_index(...)`
- scope decision for this step:
  - no additional convenience wrapper such as
    `build_normalization_result_from_canonical_sources()` will be added for now
  - explicit path-based orchestration remains preferred because it is clearer,
    easier to test, and less tightly coupled to repository constants
- expected downstream use:
  - issue `#14` should consume normalization primarily through
    `build_normalization_result(...)`
  - direct imports from extraction modules should be avoided unless a later step
    has a specific need for lower-level access

## Agreed `xml_path` Convention

### Purpose

- `xml_path` is the normalized structural path used to identify where a code is
  modeled inside `CVNTreeModel.xml`
- it is meant for traceability, grouping, and later semantic processing
- it is not intended to duplicate the semantic content already carried by
  `code`, `tree_value`, or manual metadata fields

### Structural Scope

- `xml_path` is an absolute structural path rooted at `CVNTreeModel`
- it is built only from the standard structural nodes of the documented tree
  model:
  - `CVNTreeModel`
  - `Node`
  - `Version`
  - `Agent`
  - `CVNItem`
  - `Property`
  - `Indicator`

### Segment Rules

- the root must always begin with:
  - `/CVNTreeModel/Node`
- `Version` and `Agent` are represented by their literal node names:
  - `/CVNTreeModel/Node/Version/...`
  - `/CVNTreeModel/Node/Agent/...`
- `CVNItem` is represented with its `code` when available:
  - `CVNItem[@code='010.010.000.000']`
- `Property` is represented with its technical `name` when available:
  - `Property[@name='Identification']`
- `Indicator` is represented with its technical `name` when available:
  - `Indicator[@name='Gender']`
- when `name` is missing, the segment falls back to the plain node name:
  - `Property`
  - `Indicator`

### Exclusions

- `Value` is not part of `xml_path`
- the `code` of `Property` is not part of `xml_path`
- the `code` of `Indicator` is not part of `xml_path`
- default-value semantics are not part of `xml_path`
- unexpected source nodes that are not part of the documented structural model
  are not part of `xml_path`

### Examples

- example path for a direct agent field:
  - `/CVNTreeModel/Node/Agent/Property[@name='Identification']/Indicator[@name='PersonalIdentification']/Indicator[@name='Gender']`
- example path for a CVN item field:
  - `/CVNTreeModel/Node/CVNItem[@code='010.010.000.000']/Property[@name='Title']/Indicator[@name='Name']`
- when an indicator carries a `Value`, that value is stored in `tree_value`, not
  appended to the path

## Validation Of The `xml_path` Convention

### Validation Against `TreeModel_v1.0 20090331 v1.0.pdf`

- the document defines the official structural model using:
  - `CVNTreeModel`
  - `Node`
  - `Version`
  - `Agent`
  - `CVNItem`
  - `Property`
  - `Indicator`
- for `Property`, the document identifies:
  - `name`
  - `code`
- for `Indicator`, the document identifies:
  - `name`
  - `code`
  - `Value`
  - `Child`
- this supports the decision to use:
  - `@code` only for `CVNItem`
  - `@name` for `Property`
  - `@name` for `Indicator`
  - no `Value` in the path itself

### Validation Against The Technical Specification Manual

- the technical specification manual is code-centric and describes fields through
  semantic metadata such as:
  - code
  - short name
  - type
  - obligatoriness
  - reference tables
  - multiplicity and linkage
- this confirms that `xml_path` should remain a structural locator, while the
  semantic meaning of each field continues to come from `SpecificationManual.xml`

## Confirmed Tree-Model Source Inconsistency Relevant To `xml_path`

- the canonical `CVNTreeModel.xml` contains `438` `Indicator` nodes with
  `mo:name="Type"`, which is structurally normal
- however, only `2` real child elements named `<Type>` were found in the
  canonical XML
- those `2` unexpected child elements appear under:
  - `Indicator mo:name="Type" mo:code="060.030.070.220"`
  - `Indicator mo:name="Type" mo:code="060.030.070.230"`
- both unexpected child elements contain:
  - `CVN_QualityTypeType@AuxTable.xsd`
- `TreeModel_v1.0 20090331 v1.0.pdf` documents `Indicator` children as only:
  - `Value`
  - `Child`
- this means the two `<Type>` elements behave as source inconsistencies, not as
  a documented feature of the tree model
- as a consequence, those nodes must be treated as mismatches or special-case
  findings during normalization, not as part of the standard `xml_path` model

## Current Execution State

- Issue status: in progress
- Current step: step `8` - expose a reusable internal API for later issues
- Last completed step: step `7` - implement consistency and mismatch reporting
- Next milestone after step `8`: finalize test coverage and then update
  persistent project documentation for issue `#13`

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
