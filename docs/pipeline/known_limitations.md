# Known Limitations

## Purpose

This document records known limitations of the current pipeline so later issues
do not need to rediscover them.

## Limitation Classification Matrix

| Limitation | Category | Impact | Current Handling | Follow-Up Action | Blocker Status |
| --- | --- | --- | --- | --- | --- |
| `xs:choice` is not enforced as mutual exclusivity in generated structural bindings | `generated_binding_limitation` | Generated bindings can accept XML states invalid under the source XSD | Confined to structural interoperability; semantic/domain layers avoid treating generated bindings as the public Open CVN contract | Keep documentation and regression coverage; do not manually patch `src/generated/` | Accepted limitation, not MVP blocker |
| Wrapper type evidence requires XSD-enriched normalization | `generated_binding_limitation` | Custom normalization callers without XSD paths cannot attach wrapper-aware field shapes | Canonical generation provides `CVN.xsd` and `Common.xsd`; no-XSD behavior remains supported | Document boundary and keep enriched/no-XSD regression tests | Accepted limitation, not MVP blocker |
| Generated list defaults do not enforce every `minOccurs` cardinality | `generated_binding_limitation` | Structural object construction can accept empty lists where XSD expects values | Structural layer preserves generated behavior; Open CVN runtime models define the public JSON contract | Keep semantic cardinality policy outside generated bindings | Accepted limitation, not MVP blocker |
| Some generated attributes are typed as `object` | `generated_binding_limitation` | Weaker structural validation and poorer ergonomics | Avoid leaking weak generated types into Open CVN public models | Confirm boundary during issue `#71` | Accepted limitation, not MVP blocker |
| XML helper wrapper types are less ergonomic than primitives | `generated_binding_limitation` | Structural XML fidelity is usable but delicate for direct application code | Domain-facing wrapper components exist for canonical generation | Keep wrapper guidance and avoid direct generated-wrapper UX promises | Accepted limitation, not MVP blocker |
| `tree_model` requires `--unnest-classes` xsdata override | `generated_binding_limitation` | Structural generation is reproducible but target-specific | Documented runner behavior | Keep workflow documentation aligned | Accepted limitation, not MVP blocker |
| JSON Schema cannot express every CVN semantic rule | `runtime_validation_gap` | Schema-valid JSON can still miss curated semantic expectations | JSON Schema runs before Pydantic runtime validation; trace annotations preserve evidence | Evaluate conservative semantic warnings in issue `#71` | Not blocker if warnings remain clear |
| CVN XML import is semantic partial for recognized CVN items | `runtime_validation_gap` | XML import is not a complete official CVN XML-to-Open-CVN converter | Diagnostics preserve mapped/unmapped counts, trace, and fallback `other` entries | Improve documentation and add metrics only where useful | Accepted MVP constraint, not blocker |
| JSON Schema validation runs before runtime model validation | `documentation_gap` | Users may see schema errors before Pydantic errors for the same payload | Structured parser errors expose layer-specific codes | Document validation order clearly | Accepted UX limitation, not blocker |
| LLM-assisted PDF import is best-effort and provider-dependent | `runtime_validation_gap` | Schema-valid LLM output may be incomplete or factually wrong | External LLM use is opt-in, locally validated, and records provenance | Strengthen documentation and provenance if needed | Accepted MVP constraint, not blocker |
| Conceptual relationships require curation | `future_research` | Generated metadata cannot prove a full CVN ontology | Conceptual extraction emits conservative relationships only | Add curated rules only with stronger evidence | Not blocker |
| Domain-area diagrams can be verbose | `documentation_gap` | Large diagrams are difficult to use in slides or compact review contexts | Readable/reference split exists; PNGs are derived review artifacts | Use PNG audit from issue `#71` to add presentation views and split large readable diagrams | Not blocker |
| `CVNTreeModel.xml` diverges from `CVNTreeModel_v1.0.xsd` | `source_package_limitation` | Generated tree-model binding cannot fully parse canonical XML through the XSD alone | Normalization treats XML as source evidence and records mismatch | Preserve explicit documentation; do not hide mismatch | External constraint, not project bug |
| Auxiliary catalog families preserve historical packaging drift | `source_package_limitation` | Automated resolution cannot rely on filenames or schema locations alone | Repository-aware path mapping and auxiliary documentation | Keep links to source-package docs | External constraint, not project bug |
| `CVN_AGENCY_C` remains unresolved from the source package alone | `source_package_limitation` | Cannot promote this reference to a strict resolved enum/catalog from current evidence | Preserved as unresolved/manual-only reference | Revisit only if stronger official evidence appears | External constraint, not project bug |
| `Subtype_Spa.xml` lacks a direct table-family bridge | `source_package_limitation` | Subtype-backed families cannot be strictly bridged per table family | Classify as subtype-backed but enum-ineligible | Revisit only if reliable bridge evidence appears | External constraint, not project bug |
| Strict enum eligibility is evidence-backed but conservative | `future_research` | Some compact tables remain review-required instead of strict enums | Dynamic evidence controls eligibility; weak cases stay open | Add versioned overrides only with curated evidence | Not blocker |
| PDF generation depends on a TeX engine | `runtime_validation_gap` | A Python-only install cannot compile PDFs unless a usable engine is available | Current implementation discovers local `latexmk` or `pdflatex` | Issue `#71` should add managed Tectonic discovery/cache/download where practical, plus `pdf doctor` | Actionable hardening item |

## Structural Binding Limitations

### `xs:choice` Is Not Enforced As Mutual Exclusivity

- Affected areas include:
  - `FlexibleDatesType`
  - `OfficialIdType`
  - `EntityTypeType`
  - `EntityNameType`
- Impact:
  - generated Pydantic models may accept states that are invalid with respect to
    the source XSD
- Expected follow-up:
  - issue `#14` defines the semantic policy
  - issue `#15` should restore domain-facing semantics

### Wrapper Type Evidence Requires XSD-Enriched Normalization

- Affected wrapper families include:
  - `FlexibleDatesType`
  - `OfficialIdType`
  - `EntityTypeType`
  - `EntityNameType`
- Confirmed behavior:
  - hotfix `#8` adds typed `StructuralTypeEvidence` to the normalized handoff
    when normalization receives `cvn_xsd_path` and `common_xsd_path`
  - canonical domain generation provides those XSD paths and can attach wrapper
    policy without scanning raw XSD files inside generator logic
  - normalization calls that omit XSD paths preserve backward-compatible empty
    structural evidence and therefore cannot attach wrapper-aware field shapes
- Impact:
  - canonical issue `#15` generation can consume wrapper-aware domain shapes
  - custom callers that need wrapper attachment must use the XSD-enriched
    normalization path
- Expected follow-up:
  - issue `#16` should keep regression coverage for both enriched wrapper
    handoff behavior and no-XSD backward-compatible behavior

### `minOccurs` Is Not Enforced For Generated Lists

- Generated list fields with `default_factory=list` do not enforce the minimum
  cardinality implied by the XSD
- Impact:
  - empty lists may be accepted in object construction even when the XSD
    expects at least one element
- Expected follow-up:
  - issue `#14` records semantic cardinality policy
  - issue `#15` should decide concrete generated validation behavior

### Some Attributes Are Typed As `object`

- Seen in parts of `specification_manual` and `tree_model`
- Impact:
  - validation is weaker than the XSD suggests
  - ergonomics are worse for downstream code
- Expected follow-up:
  - issue `#14` defines semantic treatment outside generated bindings
  - issue `#15` should avoid leaking weak structural types into domain models

### XML Helper Types Are Less Ergonomic Than Primitives

- Wrappers such as `CVN_duration`, `CVN_gYear`, and `CVN_gYearMonth` map to XML
  helper types such as `XmlDuration` and `XmlPeriod`
- Impact:
  - structural fidelity is preserved, but programmatic usage is more delicate
- Expected follow-up:
  - issue `#14` defines semantic base-kind policy
  - issue `#15` should map these cases into usable domain-facing shapes

## Generation Process Limitations

### `tree_model` Needs A Target-Specific xsdata Override

- Default structural generation hit circular dependency problems
- Current workaround:
  - `--unnest-classes`
- Impact:
  - generation is reproducible, but not uniform across all three targets
- Expected follow-up:
  - keep documented through issue `#17`

## JSON Schema Generation Limitations

### Issue `#45` Provisional Root Was Replaced By Issue `#46`

- Confirmed behavior:
  - issue `#45` generates `schemas/open_cvn.schema.json` from the issue `#43`
    conceptual inventory
  - issue `#46` defines the canonical Open CVN JSON root shape and aligns the
    generated schema root to `schema_version`, `metadata`, `curriculum`, and
    `extensions`
  - direct Pydantic JSON Schema output is not used as the canonical root because
    it exposes generated Python class shapes
- Impact:
  - the schema is now aligned with the canonical issue `#46` JSON document layout
  - future parser work can consume the schema without inheriting the older
    root-level `policy_name` and `policy_version` prototype
- Expected follow-up:
  - issue `#47` should define parser contracts over the canonical issue `#46`
    JSON shape

### JSON Schema Cannot Express Every CVN Semantic Rule

- Confirmed behavior:
  - the generated schema represents types, required fields, arrays, wrapper
    shapes, and eligible closed vocabularies
  - open-world registries, thesauri, unresolved references, and curated domain
    relationships cannot be fully enforced by JSON Schema alone
- Impact:
  - issue `#49` validation work may need runtime checks in addition to JSON Schema
  - `x-open-cvn-*` extensions preserve trace for validators and tooling, but they
    are non-validating annotations
- Expected follow-up:
  - issue `#49` should distinguish JSON Schema validation from semantic validation
    that depends on external registries or curated project rules

## Parser And Import Limitations

### CVN XML Import Is Semantic Partial For Recognized CVN Items

- Confirmed behavior:
  - issue `#49` introduced CVN XML input reading, XML well-formedness checks,
    basic CVN evidence detection, XML path preservation, and CVN code-like trace
    preservation
  - issue `#70` maps recognized `CvnItem` group and field codes into Open CVN
    `identity`, `education`, `research`, `professional_experience`,
    `achievements`, and `other` sections using `schemas/open_cvn.schema.json`
    annotations
  - generated Open CVN JSON is validated through `validate_open_cvn_json(...)`
    before successful parser results are returned
  - unmapped CVN items and fields are preserved through trace, import diagnostics,
    and `curriculum.other[]` where applicable
  - arbitrary CVN XML records and rare source-package edge cases are not yet fully
    semantically mapped into domain entries
- Impact:
  - XML import now provides structured validation, trace preservation, and partial
    semantic population, but it is not a complete CVN XML-to-Open-CVN converter
  - downstream consumers should treat `mapping_status = "semantic_partial"` or
    `mapping_status = "trace_only"` as import diagnostics, not as proof that all
    curriculum content was converted
- Expected follow-up:
  - later work should add curated XML-to-domain mapping rules, richer controlled
    reference label resolution, and broader fixture coverage before treating the
    importer as a complete real-world CVN XML converter

### JSON Schema Validation Runs Before Runtime Model Validation

- Confirmed behavior:
  - issue `#49` validates Open CVN JSON against `schemas/open_cvn.schema.json`
    before applying Pydantic runtime model checks
  - documents rejected by the generated schema may never reach runtime model
    validation
- Impact:
  - some invalid JSON documents report `json_schema_validation_failure` even when
    the same payload would also violate runtime model rules
- Expected follow-up:
  - later validator UX work may add grouped multi-layer diagnostics if users need
    schema and runtime errors in the same result

### Open CVN Semantic Validation Is Warning-Oriented

- Confirmed behavior:
  - issue `#71` adds conservative semantic warnings after generated JSON Schema
    validation and Pydantic runtime validation pass
  - current checks warn about entry `type` prefixes that do not match their
    curriculum section, trace values that do not look like CVN codes, and
    controlled-reference-like objects that carry provenance without `code`,
    `label`, `raw_value`, or `uri`
- Impact:
  - accepted documents can return `valid_with_warnings` when they are structurally
    valid but semantically suspicious
  - unusual but valid future data is not rejected by these checks
- Expected follow-up:
  - promote a warning to a hard failure only if the rule becomes part of the
    documented public Open CVN contract

### LLM-Assisted PDF Import Is Best-Effort And Provider-Dependent

- Confirmed behavior:
  - issue `#69` adds an opt-in LLM fallback for PDF import when deterministic XML
    extraction is absent, incompatible, or not validatable
  - the fallback currently supports an OpenAI Responses-style provider adapter and
    uses mocked providers in automated tests
  - provider output is accepted only after local `validate_open_cvn_json(...)`
    validation succeeds
  - provenance is recorded under `extensions["x-open-cvn.llm_import"]`
- Impact:
  - JSON validity and schema validation do not prove that every extracted CV fact
    is complete or semantically correct
  - provider behavior, PDF visual quality, model capability, prompt adherence, and
    token limits can affect extracted content
  - users should review LLM-assisted imports before relying on them
- Expected follow-up:
  - future work may compare LLM output against deterministic XML imports when both
    are available
  - future work may add richer confidence/provenance fields or human review flows
    before treating LLM-assisted data as authoritative

### PDF Generation Uses Managed Tectonic When Available

- Confirmed behavior:
  - issue `#71` adds managed Tectonic discovery before system TeX engines
  - compiler discovery order is managed `tectonic`, system `tectonic`, `latexmk`,
    then `pdflatex`
  - the managed executable is cached under the Open CVN cache directory and can be
    diagnosed with `open-cvn pdf doctor`
- Impact:
  - typical Python application use no longer depends exclusively on a separately
    installed TeX distribution
  - first-use managed download still requires platform support and network access;
    offline environments need a cached managed executable or a system TeX engine
- Expected follow-up:
  - keep download URLs, version pins, and checksums current when upgrading the
    managed Tectonic version

## Conceptual Extraction Limitations

### Conceptual Relationships Require Curation

- Confirmed behavior:
  - issue `#43` builds a conceptual inventory from normalized metadata, semantic
    policy, and domain generation IR
  - generated field annotations and CVN tree grouping do not prove a complete
    domain ontology by themselves
  - the extractor therefore emits only conservative relationships and records a
    limitation instead of inventing hard associations
- Impact:
  - issue `#44` can render representative relationships from the conceptual IR
  - richer UML relationships may need explicit curated rules before they are
    treated as normative
- Expected follow-up:
  - issue `#44` should render only relationships present in the conceptual IR or
    explicitly curated for diagram output
  - later JSON format decisions in issue `#46` should not assume every generated
    field relation is a domain association

### Domain-Area Diagrams Can Be Verbose

- Confirmed behavior:
  - issue `#44` renders PlantUML diagrams from the issue `#43` conceptual
    inventory
  - splitting diagrams by conceptual domain area keeps the overview readable, but
    large areas such as research still contain many CVN-backed conceptual entities
    and attributes
  - detailed reference chunks use local `controlled references` notes rather than
    long global dependency edges to keep rendered PNGs inside frame
  - controlled vocabularies are summarized when large, but the source model itself
    remains broad
- Impact:
  - `.puml` sources are reproducible and traceable, but some area diagrams are
    better used as reference artifacts than compact presentation slides
  - PNGs are derived review artifacts; the canonical output remains PlantUML source
- Expected follow-up:
  - future curated conceptual modeling work may add smaller thematic diagrams or
    manually selected publication views without changing the canonical inventory

## Canonical Source Package Inconsistencies

### `CVNTreeModel.xml` Diverges From `CVNTreeModel_v1.0.xsd`

- Confirmed discrepancy:
  - the XML includes `<Type>` inside `Indicator`
  - the XSD only declares `Value` and `Child` inside `Indicator`
- Confirmed scope of the discrepancy:
  - the canonical XML contains `438` `Indicator` nodes with
    `mo:name="Type"`, which is compatible with the documented tree-model
    structure
  - only `2` real child elements named `<Type>` were found in the canonical XML
  - those `2` unexpected child elements appear under:
    - `Indicator mo:name="Type" mo:code="060.030.070.220"`
    - `Indicator mo:name="Type" mo:code="060.030.070.230"`
  - both unexpected child elements contain the value:
    `CVN_QualityTypeType@AuxTable.xsd`
- Comparison with the tree-model documentation:
  - `TreeModel_v1.0 20090331 v1.0.pdf` defines `Indicator` children as only
    `Value` and `Child`
  - the document does not describe `<Type>` as an allowed child element of
    `Indicator`
  - this makes the two `<Type>` elements a source inconsistency, not a
    documented feature of the tree model
- Practical consequence:
  - the generated `tree_model` binding is correct with respect to the XSD, but
    cannot fully parse the canonical XML file
- Normalization consequence:
  - issue `#13` should treat `xml_path` as a structural path built from
    `CVNTreeModel`, `Node`, `CVNItem`, `Property`, and `Indicator`
  - the unexpected `<Type>` child elements should be recorded as explicit
    mismatches or special-case findings, not folded into the standard structural
    path model
- Parse status:
  - `SpecificationManual.xml`: parse OK
  - `CVNTreeModel.xml`: parse blocked by XML/XSD mismatch
- Expected follow-up:
  - issue `#13` must treat the tree-model XML as a source of truth for
    normalization even when the XSD does not describe it completely

### Auxiliary Catalog Families Preserve Historical Packaging Drift

- affected families:
  - `Entity`
  - `ReferenceTables/Subtypes`
  - `Thesaurus`
- confirmed issues:
  - XML `schemaLocation` values assume colocated XSD files, while the preserved
    repository package stores XML and XSD in separate directories
  - several `Leeme*.txt` files mention filenames that do not exactly match the
    preserved repository filenames, such as `Subtypes.xml` instead of
    `Subtype_Spa.xml`, or lowercase thesaurus filenames that differ from the
    actual files
  - side families duplicate ISO helper schemas instead of using one fully shared
    physical artifact
  - `Subtypes` materials preserve version drift between PDF, XSD, and XML files
- impact:
  - package exploration and automated file resolution cannot rely on filenames or
    relative schema locations alone
  - tooling must resolve these families through repository-aware path mapping and
    documented semantic relationships
- expected follow-up:
  - issue `#14` defines semantic policy for side-package references
  - issue `#15` should decide which of these auxiliary artifacts become domain
    sources versus support registries
  - issue `#71` classifies this as an external source-package constraint and
    links readers to `docs/cvn_source_package_auxiliary_artifacts.md` for the
    preserved package layout and drift details

### Some Annex-I Table References Remain Unresolved From The Package Alone

- confirmed example:
  - `CVN_AGENCY_C` appears referenced from the manual material but does not map
    cleanly to a matching table in `ReferenceTables.xml`
- impact:
  - not every table name from the manual can yet be promoted to a strict
    machine-resolved enum or closed catalog using the source package alone
- expected follow-up:
  - issue `#14` defines open versus closed treatment for unresolved tables
  - issue `#15` should preserve such cases as explicit external or manual-only
    references unless stronger evidence is introduced
  - issue `#71` keeps this as a `source_package_limitation`; tooling must not hide
    it behind a lossy conversion or promote it to a strict enum without stronger
    official evidence

### `Subtype_Spa.xml` Does Not Provide A Direct Table-Family Bridge

- confirmed behavior:
  - `Subtype_Spa.xml` can be parsed and used to prove subtype catalog
    availability
  - the preserved XML is keyed by numeric subtype item codes such as `001`,
    `002`, and not by reference-table family names such as `CVN_KNOW_A`
- impact:
  - the current normalization layer can classify tables as subtype-backed and
    record that subtype catalog data is available, but it does not yet verify a
    strict per-table-family bridge directly from `Subtype_Spa.xml`
- expected follow-up:
  - issue `#14` treats subtype-backed families as enum-ineligible until stronger
    bridge evidence exists
  - later maintenance work may add a stricter bridge only if reliable evidence
    is introduced from the preserved source package
  - issue `#71` records this as an evidence limitation, not an implementation
    oversight, because the preserved subtype XML is not keyed by table-family
    names

### Strict Enum Eligibility Is Evidence-Backed But Conservative

- confirmed behavior:
  - hotfix `#7` adds per-table enum evidence from `ReferenceTables.xml` to the
    normalization-to-semantic handoff
  - issue `#14` now evaluates strict enum eligibility through typed evidence such
    as item count, code stability, label quality, hierarchy, delegate/open
    behavior, duplicate values, blank values, and other-like entries
  - compact direct tables can become `EnumEligibility.ELIGIBLE` when evidence
    shows a small closed table, as with `CVN_SEX_A`
  - compact tables with delegate/open-world behavior remain strict-enum
    ineligible, as with `CVN_ENTITY_TYPE` and `delegate_present`
- impact:
  - issue `#15` may generate strict enums only when semantic policy reports
    `EnumEligibility.ELIGIBLE`
  - `EnumEligibility.REVIEW_REQUIRED` and `EnumEligibility.INELIGIBLE` must not
    be treated as final strict-enum permission
- expected follow-up:
  - issue `#15` should consume the dynamic eligibility result without
    re-inspecting `ReferenceTables.xml`
  - future explicit overrides, if any, must remain versioned `OverrideRule` data
    rather than hidden table-name branches

## Documentation Rule

Whenever a new limitation is discovered, add it here and reference the issue
expected to address it.
