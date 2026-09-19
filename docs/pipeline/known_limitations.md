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
| Bitnami-sourced Helm chart images are pinned to the frozen `bitnamilegacy` registry | `infra_supply_chain_limitation` | MinIO and the dedicated PostgreSQL instance receive no further security patches; upstream MinIO/Bitnami distribution both restructured in 2025-2026 | Every affected image reference pinned to an explicit, verified-pullable `bitnamilegacy` tag rather than a chart default | Re-evaluate (paid Bitnami Secure Images, self-built image, or alternative) before any deployment beyond the local dev cluster | Accepted limitation for a local-only TFM cluster, not a blocker |
| `spark.kubernetes.driver.*` pod-spec properties are no-ops in `client` deploy mode | `infra_gotcha` | Driver-side credentials/service-account config silently does nothing; `spark-submit` neither errors nor warns | Driver pod-spec config (credentials, service account) set directly on the submitting pod's own spec (the `KubernetesPodOperator` pod, in Airflow's case) instead | Apply the same pattern in issues `#97`/`#99`; do not set `spark.kubernetes.driver.*` pod-spec properties expecting them to affect a `client`-mode driver | Resolved for issue `#93`'s job; a standing gotcha for any future `client`-mode Spark-on-k8s job |
| RBAC `deletecollection` is a separate verb from `delete` | `infra_gotcha` | A `Role` granting `delete` but not `deletecollection` lets a Spark driver create pods but not clean them up on shutdown via its own label-selector bulk delete | `infra/spark-conf/spark-rbac.yaml`'s `Role` grants both, plus `persistentvolumeclaims` alongside `pods`/`services`/`configmaps` | Grant `deletecollection` on the same resources in any future namespaced `Role` for a Spark driver | Resolved for issue `#93` |
| ORCID registered Public API client registration is blocked for a non-member individual project | `external_api_limitation` | Cannot use the OAuth2 client-credentials tier (100k reads/day per `client_id`); stuck on the anonymous tier's lower cap | `src/tfm_lakehouse/orcid_client/` uses `pub.orcid.org`'s anonymous, unauthenticated tier (25k reads/day, 12 req/s per IP) instead | Re-check registration eligibility, or a university-sponsored Member API key, only if a later issue needs sustained volume beyond the anonymous cap | Accepted limitation for issues `#94`/`#96`/`#97`'s per-iD lookup scope, not a blocker |
| The `ingest_validate` DAG mounts code and data from the repository checkout with hostPath | `infra_limitation` | The DAG only works on a single-node k3s that shares a disk with the checkout, and `REPO_ROOT` in the DAG file is an absolute path of this machine | Chosen deliberately (issue `#97`, D2): code edits need no image rebuild and no `sudo` import; verified working on `/mnt/e` | Bake the code into the image, or pack the subset into MinIO first, before any multi-node or cloud deployment | Accepted for the local-only TFM cluster, not a blocker |
| Only a capped, deterministic sample of the ORCID bulk subset is landed into bronze by default | `data_scope_limitation` | The 301,763-record subset is roughly 42 GB of XML (estimate); the default DAG run lands the first 20,000 records in bucket order (2.7 GB), not a random sample | `bulk_max_records` DAG parameter (0 lands all); the snapshot lands once, and the cap is part of the snapshot id | Land everything (about 1 hour and 40 GB, extrapolated) if `#101`'s benchmark needs the volume | Default confirmed by the user, not a blocker |
| Reading all of `bronze/` as one Spark dataset mixes payload types | `reader_gotcha` | `payload` is an XML string for ORCID bulk and a JSON object for the other sources, so `spark.read.json("bronze/")` collapses it to `string` | Each source has its own `source=<name>` path; `_manifest.json` and `_rejected/` are skipped by Spark readers | Issue `#98` reads each source separately | Standing gotcha for `#98` |
| The Airflow api-server can be killed by its own liveness probe under load | `infra_fragility` | Every task starting during the restart fails with `Connection refused` from the executor's worker pod, before any task code runs; the failed worker pods stay in `Error` | Re-trigger with a new run id and delete the leftover worker pods | Relax the probe (`timeout`, `failureThreshold`) or size the pod in issue `#102` | Observed once in issue `#97`, not a blocker |
| Unpausing a cron-scheduled Airflow 3 DAG creates the latest missed run at once | `infra_gotcha` | The `ingest_validate` DAG ran its 00:00 schedule the moment it was unpaused at 15:52 UTC | Know it before unpausing; the DAG is idempotent per run id | Unpause just before the scheduled time when an immediate run is unwanted | Standing gotcha for `#99`'s DAG |

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

## Infrastructure Limitations (TFM)

### Bitnami-Sourced Images Pinned To The Frozen `bitnamilegacy` Registry

- discovered during issue `#91` (Core Services Deployment)
- Broadcom's "Bitnami Secure Images" transition (effective 2025-08-28,
  catalog cutover 2025-09-29) shrank Bitnami's free Helm chart/image
  catalog; every image a pre-cutover chart version references may no
  longer resolve, and non-latest tags on `docker.io/bitnami/*` are being
  removed over time
- affected here: the MinIO chart (`oci://registry-1.docker.io/bitnamicharts/minio`,
  including its separate console/object-browser image, easy to miss) and
  the dedicated PostgreSQL chart
  (`oci://registry-1.docker.io/bitnamicharts/postgresql`) deployed in
  issue `#91`
- current handling: every affected image reference is pinned to an
  explicit `docker.io/bitnamilegacy/<image>:<tag>`, verified pullable
  anonymously (Docker Hub API tag listing + a `registry-1.docker.io`
  bearer-token manifest check) before use; see
  `infra/helm-values/README.md` for the exact tags and verification
  commands used
- independent confirmation: MinIO's own upstream distribution changed too
  (official `minio/minio`/`minio/mc` images pulled from Docker Hub October
  2025, GitHub repo archived February 2026), and the official
  `apache-airflow/airflow` chart's own embedded metadata-Postgres subchart
  already defaults to a `bitnamilegacy/postgresql` pin upstream,
  independently corroborating this as the maintained community path
  rather than an issue-specific workaround
- expected follow-up: not required for the TFM's local-only cluster scope;
  re-evaluate before any deployment beyond the local dev machine (a paid
  Bitnami Secure Images subscription, self-built images, or an alternative
  distribution)

### Iceberg Hadoop-Catalog Configuration Is Pinned And Now Proven End-To-End (Resolved)

- discovered during issue `#92` (Iceberg Catalog On MinIO); resolved during
  issue `#93` (Spark Job Execution From Airflow)
- issue `#92`'s own original plan deferred jar-version pinning to "the
  Spark version chosen in issue `#93`", while issue `#93`'s own plan
  expected to inherit "the Iceberg/S3A dependencies from issue `#92`" —
  neither issue had actually picked a Spark version, a circular dependency
  resolved by locking the full version set (Spark `3.5.9`,
  `iceberg-spark-runtime-3.5_2.12:1.11.0`, `hadoop-aws:3.3.4`,
  `aws-java-sdk-bundle:1.12.262`) inside issue `#92` itself
- both items this entry originally left open are now resolved:
  1. issue `#93` unpacked the real `spark-3.5.9-bin-hadoop3.tgz` and
     confirmed it bundles Hadoop `3.3.4` client jars exactly
     (`hadoop-client-api-3.3.4.jar`, `hadoop-client-runtime-3.3.4.jar`) —
     no jar-pin revision was needed
  2. issue `#93` built a Spark image, ran a real job through
     `infra/spark-conf/iceberg-catalog.conf` via Airflow, and independently
     re-queried the written table from a separate pod, confirming the
     catalog genuinely works end to end (see that issue's Verification
     section for the full detail, including `ICEBERG_SMOKE_TEST_ROW_COUNT=2`
     and the independent `INDEPENDENT_VERIFY_ROW_COUNT=2` re-query)
- one correction surfaced along the way: the `fs.s3a.aws.credentials.provider`
  class name issue `#92` locked
  (`org.apache.hadoop.fs.s3a.EnvironmentVariableCredentialsProvider`) does
  not exist anywhere in `hadoop-aws:3.3.4`; corrected to the real class,
  `com.amazonaws.auth.EnvironmentVariableCredentialsProvider`, shipped in
  `aws-java-sdk-bundle`
- both issue `#92` and issue `#93` are now `Completed`

### `spark.kubernetes.driver.*` Pod-Spec Properties Are No-Ops In `client` Deploy Mode

- discovered during issue `#93` (Spark Job Execution From Airflow)
- confirmed behavior: this cluster's `client` deploy-mode choice (the
  submitting pod itself becomes the Spark driver) means Spark never builds
  a driver pod spec of its own -- that only happens in `cluster` mode. Any
  `spark.kubernetes.driver.*` property that configures a *pod spec*
  (`secretKeyRef`, `authenticate.driver.serviceAccountName`, and likely
  others in that family) is therefore silently ignored for the driver;
  `spark-submit` neither errors nor warns
- impact: a job can appear correctly configured (properties file has the
  right keys) while the driver actually runs with none of that
  configuration applied, discovered only when something the driver needs
  (AWS credentials, in issue `#93`'s case) turns out missing at runtime
- current handling: driver-side pod-spec config is set directly on the
  submitting pod's own spec instead -- in Airflow's case, on the
  `KubernetesPodOperator`'s `env_vars`/`service_account_name` in the DAG
  file, not via `infra/spark-conf/iceberg-catalog.conf`. Executor-side
  `spark.kubernetes.executor.*` properties are unaffected by this and work
  normally, since Spark always creates executor pods itself regardless of
  driver deploy mode
- expected follow-up: issues `#97`/`#99` (also `client`-mode jobs from
  Airflow, per the epic's stack decision) must apply the same pattern, not
  rediscover this

### RBAC `deletecollection` Is A Separate Verb From `delete`

- discovered during issue `#93` (Spark Job Execution From Airflow)
- confirmed behavior: on shutdown, a Spark driver bulk-deletes its own
  executor pods, services, configmaps, and PVCs by label selector, which
  Kubernetes RBAC treats as the `deletecollection` verb -- distinct from
  `delete`, which only covers deleting a single named resource
- impact: a `Role` granting `create`/`get`/`list`/`watch`/`delete` but not
  `deletecollection` lets the driver create and run executors successfully,
  but its own cleanup step then fails with `Forbidden`, and the driver pod
  ends in `Error` even though the actual job succeeded -- easy to
  misdiagnose as a job failure rather than a cleanup-permission gap
- current handling: `infra/spark-conf/spark-rbac.yaml`'s `Role` grants
  `deletecollection` alongside `delete` on `pods`/`services`/`configmaps`/
  `persistentvolumeclaims`
- expected follow-up: grant `deletecollection` on the same resources in any
  future namespaced `Role` written for a Spark driver (issues `#97`/`#99`)

### ORCID Registered Public API Client Registration Is Blocked For A Non-Member Individual Project

- discovered during issue `#94` (ORCID API Client)
- the original plan assumed a free, individually-registrable ORCID Public
  API client (`client_id`/`client_secret`, OAuth2 client-credentials,
  `/read-public` scope). Checking the actual registration form
  (`orcid.org` -> Developer Tools -> register a public API client) showed
  it asks for the app to be described as a tool used by a registered ORCID
  member organization; a personal TFM project does not fit that
  description
- this contradicts ORCID's own documentation, which states individuals can
  hold Public API credentials independent of membership; the discrepancy
  was observed on the live form but not resolved against ORCID's written
  policy, since the anonymous tier makes it moot for this issue's scope
- current handling: `src/tfm_lakehouse/orcid_client/` calls
  `pub.orcid.org/v3.0/{orcid-id}/{record,works,employments,educations}`
  unauthenticated, with no `client_id` or OAuth token. This is documented
  ORCID behavior (the token only raises the rate limit; it is not required
  for access) and was verified against the real API, not just mocks
- impact: capped at 25k reads/day and 12 requests/second per IP address,
  versus 100k reads/day per `client_id` on the registered tier
- expected follow-up: not required for issues `#94`, `#96`, or `#97` as
  currently scoped, since all three are low-volume, per-iD lookups rather
  than whole-registry crawling (issue `#95`'s bulk data file already
  covers that case, also without needing a key); re-evaluate registered-
  client registration or a university-sponsored Member API key only if a
  later issue needs sustained volume beyond the anonymous cap

### ORCID Bulk Subset Is A Point-In-Time, Country-Affiliation Snapshot With Serialization Assumptions

- discovered during issue `#95` (ORCID Bulk Data File Pipeline)
- the subset comes from the ORCID 2025 Public Data File
  (`ORCID_2025_10_summaries.tar.gz`), which ORCID publishes once a year; it
  is a frozen October 2025 snapshot, not a live view, and later profile
  changes are only visible through issue `#94`'s per-iD API client
- membership means "has at least one employment or education entry whose
  organization country is `ES`" (any date, including past or student
  entries), not "currently affiliated with a Spanish institution" and not
  "Spanish researcher". Records with no public affiliation, or whose
  affiliations are all outside Spain, are excluded even if the person works
  in Spain
- the byte-level prefilter assumes ORCID serializes the country as
  `<common:country>XX</common:country>`. This held for every entry
  inspected and for a 100k-entry sample compared against a full-parse run
  (identical matches), but it is an assumption about the file's formatting,
  not a documented guarantee; a future edition that changed the serialization
  would under-match silently
- the MD5 check runs after the single streaming pass, so a mismatch raises
  after the filtered files were already written; the output directory must
  then be treated as invalid and regenerated
- expected follow-up: none required for the TFM's scope; re-run against the
  next annual file if fresher data is ever needed

### Synthetic CVN Documents Combine Real Public ORCID Data With Invented Personal Data

- discovered during issue `#96` (Synthetic CVN Generator)
- each synthetic curriculum is seeded from a real ORCID record: the real
  name, affiliations, publication titles/years/DOIs are reused. Everything
  else about the person is invented (sex, birth date, phone, email,
  contract type, working hours, job duties), independently of the real
  person. The ORCID Public Data File is CC0, but ORCID states that the
  privacy and publicity rights of the people in it remain, so the generator
  only reads public name/affiliation/work fields (never biography, emails,
  or URLs), uses phone numbers in a non-existent `000` range and
  `@example.invalid` addresses, omits DNI and nationality entirely, and marks
  every document with `metadata.source.synthetic = true`
- consequence: a document can show a real, named researcher with invented
  attributes. It is acceptable inside this private lakehouse and the
  git-ignored `data/` directory, but the output should not be published or
  presented as real CVN data
- unlinked documents (no ORCID iD) still carry the seed's real publication
  titles and DOIs, so they stay linkable to the seed by content
- the linked/unlinked split (`orcid_link_ratio`) and the sidecar manifest
  are ground truth for issue `#98`'s entity-resolution checks, not
  something a real CVN corpus would provide

### Synthetic CVN Coverage Is Deliberately Narrow

- discovered during issue `#96`
- only four entity types are generated (`identity.person`, degree and
  doctorate education, past and current professional positions, scientific
  publications); the other ~100 schema entity types stay empty
- ORCID work types without a faithful `CVN_PUBLICATION_A` equivalent
  (conference papers, preprints, working papers, theses, ...) become
  `OTHERS` with the ORCID type kept in `tipo_de_produccion_otros`
- ORCID summaries carry no co-author lists, so a publication's author list
  contains only the curriculum owner
- degree and doctorate names are controlled references to the large open
  tables `CVN_TITLE_B`/`CVN_TITLE_C`; the generator writes the free-text
  label and `raw_value` without a `code`, because ORCID's text cannot be
  matched to a table code without inventing one
- only Spanish organizations receive an `ISO_3166` country reference (code
  `724`, verified); other countries are omitted because ORCID gives ISO
  alpha-2 codes and the CVN table uses numeric ones, and that mapping was
  not verified
- variation between documents seeded from the same ORCID record (only when
  the pool is exhausted) comes from the publication subset, the invented
  filler, and name variants; employments and education are identical.
  Publication years are never altered, since that would falsify real data

### Open CVN JSON Schema Does Not Enforce Entity Shapes, And Disagrees With The XML Importer On Dates

- discovered during issue `#96`
- `schemas/open_cvn.schema.json` declares `curriculum.identity` and every
  entry's `data` as free-form objects, so `validate_open_cvn_json(...)`
  accepts invented field names and missing required fields. Each entity's
  own `$defs` schema is strict (`additionalProperties: false` plus required
  fields) but is never applied by the TFG's validation path. Issue `#96`
  applies it in its own validation layer
  (`src/tfm_lakehouse/synthetic_cvn/validation.py`); issue `#98`'s CVN-side
  validation should do the same if it needs real conformity
- `FlexibleDateValue` declares `year`/`month`/`day` as strings, but the XML
  semantic importer (`open_cvn.xml_value_conversion._flexible_date`) emits
  integers. Both pass the document schema; only the per-entity check would
  flag the importer's output. The synthetic generator follows the schema
  (strings)
- the schema also requires some fields that have no sensible value, e.g.
  `titulo_homologado_fecha_de_homologacion` on doctorates (required, not
  nullable); the generator emits an empty date object
- TFG code was not modified; if `#98` ingests both real-importer and
  synthetic documents it must accept both date representations

### The `ingest_validate` DAG Depends On hostPath And A Manually Imported Image

- discovered during issue `#97` (Bronze Landing & `ingest_validate` DAG)
- the DAG's pods mount `src/`, `schemas/` and `data/` from the repository
  checkout with `hostPath`, so it only works on a single-node k3s running on the
  machine that holds the checkout, and `REPO_ROOT` in `dags/ingest_validate.py` is
  an absolute path of this machine
- the image `tfm-lakehouse/ingest:py3.14` must be imported into k3s by hand
  (`docker save ... | sudo k3s ctr images import -`, which needs `sudo`) whenever
  `pyproject.toml` or `uv.lock` change; code changes need no rebuild
- `validate_open_cvn_json` and the issue `#96` validation layer resolve
  `schemas/open_cvn.schema.json` relative to the repository root, so any pod that
  runs them must mount `schemas/` next to `src/`
- expected follow-up: replace hostPath before any deployment beyond the local dev
  cluster

### Only A Capped, Deterministic Sample Of The ORCID Bulk Subset Is Landed By Default

- discovered during issue `#97`
- the ORCID XML averages 137 KB per record (median 44 KB) on a 500-file sample, so
  the whole subset is roughly 42 GB (an estimate); MinIO's PVC is 8 Gi
  (`local-path` does not enforce it) and a daily schedule would re-land the same
  static file every day
- the DAG lands the bulk snapshot once per snapshot and cap, and by default only
  the first 20,000 records in bucket-then-name order; that is a deterministic,
  not a random, sample. 531 of them (2.66%) fail the landing check, all for a
  missing public name
- the 20,000 default was confirmed by the user; it is a demo-sized choice, not a requirement
- expected follow-up: land everything (`bulk_max_records=0`) if issue `#101` needs
  the volume

### Reading Bronze As One Dataset Mixes Payload Types

- discovered during issue `#97`
- `spark.read.json("bronze/")` returns all sources but infers `payload` as
  `string`, because ORCID bulk payloads are XML strings and the other sources are
  JSON objects; a read of one source (`bronze/source=<name>/`) keeps the natural
  type
- Spark reads every part file under `bronze/` whether or not the partition has a
  manifest, which is why a failed landing removes its landed shards instead of
  relying on the manifest's absence
- the same synthetic document can appear in several `ingestion_date` partitions
  (fixed seed plus a daily schedule); it keeps the same `record_id`
- expected follow-up: issue `#98` reads each source separately and deduplicates on
  `record_id`

### The Airflow api-server Can Be Killed By Its Own Liveness Probe

- discovered during issue `#97`
- its liveness probe (`timeout=5s`, five failures) killed the container (exit code
  137) at the moment the first DAG run started, and the executor's worker pods got
  `Connection refused` from `http://airflow-api-server:8080/execution/`; both runs
  then failed before any task started. The pod already had 4 restarts when the
  issue began
- failed executor worker pods are not deleted by Airflow and had to be removed by
  hand; a re-trigger with a new run id passed
- expected follow-up: issue `#102` (hardening) should relax the probe or give the
  pod resources

### Unpausing A Cron-Scheduled Airflow 3 DAG Creates The Latest Missed Run At Once

- discovered during issue `#97`
- Airflow 3 runs a cron schedule at the cron time (the logical date is the trigger
  time), and with `catchup=False` the scheduler creates the latest missed run, so
  unpausing `ingest_validate` at 15:52 UTC fired the run for 00:00 that day
  immediately
- harmless for this DAG (idempotent per run id, bulk source skipped after the first
  landing); issue `#99`'s DAG should account for it

## Documentation Rule

Whenever a new limitation is discovered, add it here and reference the issue
expected to address it.
