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

## Adjustments Made During Implementation

The original plan was refined in several important ways during execution:

1. `SpecificationManual.xml` was normalized through the generated structural
   binding, but `CVNTreeModel.xml` had to be normalized through tolerant direct
   XML traversal because the canonical XML does not fully conform to its XSD
2. the normalization layer was implemented as a set of typed modules under
   `src/cvn_codegen/` instead of a single monolithic script
3. `xml_path` was defined as a structural path rooted at `CVNTreeModel`, built
   only from the documented tree-model nodes and excluding `Value` and other
   non-structural content
4. mismatch reporting was intentionally limited for issue `#13` to known and
   documented source inconsistencies plus source-overlap mismatches, instead of
   introducing a broader dynamic anomaly-detection framework
5. the initial tree-model traversal was incomplete because it ignored nested
   `CVNItem` elements under `Property`; this was corrected after the stronger
   baseline-count integration test exposed the discrepancy with the documented
   overlap counts

## Implementation Performed

The following hand-maintained modules were implemented for issue `#13`:

- `src/cvn_codegen/normalization_types.py`
  - typed normalization contracts and mismatch kinds
- `src/cvn_codegen/manual_metadata.py`
  - extraction and normalization of `SpecificationManual.xml`
- `src/cvn_codegen/tree_metadata.py`
  - tolerant extraction and traversal of `CVNTreeModel.xml`
- `src/cvn_codegen/normalization.py`
  - orchestration of both sources into unified normalized views
- `src/cvn_codegen/normalization_report.py`
  - mismatch construction and aggregation

The implemented normalization layer now provides:

- a normalized per-code view through `NormalizedCodeEntry`
- a normalized per-path view through grouped `TreePathEntry` values
- explicit source-overlap sets:
  - `manual_only_codes`
  - `tree_only_codes`
- explicit mismatch records through `NormalizationMismatch`

The recommended internal API entry point for later issues is:

- `cvn_codegen.normalization.build_normalization_result(...)`

The following test modules were added or extended during issue `#13`:

- `tests/test_manual_metadata_unit.py`
- `tests/test_tree_metadata_unit.py`
- `tests/test_normalization_report_unit.py`
- `tests/test_normalization_unit.py`

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

- completed
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

### Step `9` - Tests

- completed
- normalization-related test coverage now exists for:
  - `manual_metadata.py`
  - `tree_metadata.py`
  - `normalization.py`
  - `normalization_report.py`
- dedicated mismatch-report tests pass
- dedicated normalization orchestration tests pass
- a stronger baseline-count integration assertion was added and now passes
- the previous count mismatch was caused by incomplete tree-model traversal:
  nested `CVNItem` elements under `Property` were not being traversed even
  though the tree-model specification allows them
- after fixing nested `CVNItem` traversal, the normalization layer now matches
  the documented baseline:
  - total normalized codes: `1457`
  - manual-only codes: `27`
  - tree-only codes: `1`
  - overlapping codes: `1429`
- normalization-related verification executed successfully for:
  - `tests/test_manual_metadata_unit.py`
  - `tests/test_tree_metadata_unit.py`
  - `tests/test_normalization_report_unit.py`
  - `tests/test_normalization_unit.py`
- result:
  - `42` tests passed

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

- Issue status: completed
- Current step: none
- Last completed step: step `11` - update persistent project documentation and
  close issue `#13`
- Next milestone: issue `#14` - define semantic mapping rules and override
  policy

## Verification

Normalization-related verification was executed with:

```bash
uv run pytest tests/test_manual_metadata_unit.py tests/test_tree_metadata_unit.py tests/test_normalization_report_unit.py tests/test_normalization_unit.py -v
```

Result:

- `42` tests passed

Verified normalization baseline after the nested `CVNItem` traversal fix:

- total normalized codes: `1457`
- manual-only codes: `27`
- tree-only codes: `1`
- overlapping codes: `1429`
- documented tree-only code still present:
  - `030.010.000.250`
- documented unexpected tree structure mismatches still present:
  - `060.030.070.220`
  - `060.030.070.230`

## Findings

### Positive Results

- the normalization layer now reproduces the documented overlap counts from the
  project architecture notes
- the canonical source package can now be traversed and normalized end-to-end
  without relying on invalid repairs to generated code
- mismatch reporting is explicit and integrated into the final normalization
  result
- the normalization API is stable enough for later semantic mapping work

### Important Implementation Finding

- `Property` nodes in `CVNTreeModel.xml` may contain nested `CVNItem` elements,
  as described in the tree-model documentation
- those nested `CVNItem` branches must be traversed to obtain the documented
  overlap counts
- without that traversal, many valid tree-modeled codes are incorrectly
  classified as manual-only

### Controlled Scope Finding

- issue `#13` can responsibly stop at known documented mismatches and source
  overlap reporting
- broader dynamic anomaly discovery is useful future work, but not required to
  make the normalization layer reusable for issue `#14`

## Known Limitations

- the canonical `CVNTreeModel.xml` still diverges from its documented and XSD
  model through two unexpected child `<Type>` elements
- mismatch reporting for issue `#13` is intentionally limited to:
  - `MANUAL_ONLY_CODE`
  - `TREE_ONLY_CODE`
  - known `UNEXPECTED_TREE_ELEMENT` cases
- richer structural anomaly discovery is deferred

Authoritative limitation record:

- `docs/pipeline/known_limitations.md`

## Impact On Future Issues

- issue `#14` should consume normalized metadata through
  `build_normalization_result(...)` as the preferred integration entry point
- issue `#14` can now assume that the documented code overlap baseline has been
  verified in tests
- issue `#14` should define the semantic policy for any anomalies that are known
  but intentionally left outside the current mismatch scope
- issue `#15` can build on a stable per-code and per-path normalization layer
  without needing to know extraction details from the source XML files

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

- Status: completed and verified
