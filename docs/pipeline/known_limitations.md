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
| The bronze -> silver job runs on the Spark image's Python 3.10, not the repository's 3.14 | `infra_limitation` | The repository's own code must stay Python 3.10 compatible, and the job's dependencies are not exactly `uv.lock`'s (`rpds-py 2026.6.3` needs Python >=3.11); PySpark cannot run on the host, so DataFrame code is verified in the image | `ast.parse(feature_version=(3, 10))` test plus forbidden-name checks; pins in `requirements-silver.txt`; Spark tests run in the image and skip without Docker | Revisit when the Spark image moves to a Spark/Python pair that supports a newer Python | Accepted, not a blocker |
| Entity resolution is deterministic and deliberately conservative | `resolution_quality_limitation` | Rule R2 (name and affiliation) measured precision 95.8% and recall 74.2% at 10,000 documents, below the plan's 99% precision target; recall is capped by CVNs with no affiliation; a person with two ORCID iDs is two entities | Unique-candidate rule, at most one name relaxation, organizations equal after normalization; each link's `evidence` carries `name_match` and `shared_organizations` | `#99` may filter weak merges (for example two shared organizations, which were 78 of 78 correct); no ML per the epic | Accepted, target not met, not a blocker |
| Silver extracts only the entity types the synthetic generator produces | `data_scope_limitation` | Other CVN sections are validated but not extracted; only Spain's numeric country code is mapped to `ES`; ORCID work summaries carry no authors | Four CVN entity types (identity, professional experience, education, publications) plus ORCID affiliations and works | Extend the extractors only if `#99`'s indicators need more | Not a blocker |
| Silver is rebuilt in full on every run | `scalability_limitation` | No incremental processing; adequate at 20,000 bulk records but not for the whole ORCID subset (about 42 GB) | `createOrReplace` of six tables from a deterministic function of bronze; identical input gives identical content | Measure runtime and scaling in `#101` | Not a blocker |
| Resolution quality is measured only against the synthetic generator's ground truth | `measurement_limitation` | Figures are optimistic for real curricula (four name variants only, seed iD as the only notion of "same person"); few documents have a counterpart at the default landing (16 of 288 at 1,000 documents, 186 at 10,000) | `evaluation.py` reports evaluable documents, false merges and recall by variant | None for this TFM | Not a blocker |
| The collaboration indicator is a DOI-only lower bound | `indicator_validity_limitation` | Silver has no co-author entities, so `collaboration_pairs` links two entities only when both report the same DOI; 25 of 9,540 pairs (0.26%) are one person seen twice (rule-R2 misses) | `has_cvn_member` separates the 5,092 real-data-only pairs; a DOI reported by more than 200 entities is skipped and counted | None for this TFM; author-name resolution would need its own stage | Not a blocker |
| Gold deduplicates publications only within each kind of key | `indicator_validity_limitation` | A work with a DOI in one record and none in another counts twice; 1.2% of works have no usable year and are excluded from the per-year indicator only | Key is the DOI, else a hash of title and year; the exclusions are counted in `gold_run` | None required | Not a blocker |
| Career figures are lower bounds from known years | `data_scope_limitation` | 18% of affiliations have no start year and 33% no end year; a stay is never extended to today, so `career_span_years` is a lower bound and can be null | Employment stays only, known years only; records of one stay are merged by organization and start year | None for this TFM | Not a blocker |
| Gold is rebuilt in full and PostgreSQL keeps only the latest publish | `scalability_limitation` | No incremental processing and no history in PostgreSQL; the JDBC write options carry the password to the executors | `createOrReplace` of five tables; staging tables and one atomic swap; `gold_run` records the silver snapshots read | `#101` measures runtime; `#102` reviews credential handling | Not a blocker |
| Gold indicators inherit entity-resolution errors | `resolution_quality_limitation` | A false rule-R2 merge mixes two people's publications; measured effect of undoing the 75 single-organization R2 merges: entities +0.25%, distinct publications +0.07%, per-year rows +0.13%, collaboration pairs +0.58% | Indicators use all links; `entity_link.evidence` allows a stricter filter without a re-run | None for this TFM | Not a blocker |
| Superset is deployed from a Helm chart its maintainers have deprecated | `infra_supply_chain_limitation` | Chart `superset/superset` 0.22.8 (Superset 6.1.0) is marked `deprecated: true` and the official path is now a `v1alpha1` Kubernetes Operator; the chart's PostgreSQL and Redis subcharts run frozen `bitnamilegacy` images | Chart, image and driver versions pinned; own image with `psycopg2` baked in; the dashboard itself is a versioned export, so it survives a change of deployment method | Move to the operator when it leaves `v1alpha1`; hardening is `#102` | Accepted, not a blocker |
| The Superset deployment is local, single-replica and unhardened | `infra_gotcha` | One replica of each component, no TLS or SSO, reached only through `kubectl port-forward`; Superset's metadata (2 Gi PVC on `local-path`) has no backup; the first `helm install` exceeded Helm's default 5-minute timeout because the chart's PostgreSQL takes about 2 minutes to boot, leaving a healthy release marked `failed`; the image is built on the host and imported by hand | Credentials only in Kubernetes Secrets; `superset_ro` is read-only; install with `--timeout 15m`; the dashboard is rebuilt from `infra/superset/assets/` | `#102` (hardening) | Accepted for a local cluster |
| The dashboard shows aggregates over a lower-bound indicator and disables its data cache | `indicator_validity_limitation` | Charts leave out publications before 1980 (443), stays with no start year or outside 1970-2026 (16,231 of 94,431) and the collaboration lower bound of `#99`; with `cache_timeout = -1` every view queries PostgreSQL, which is fine for these aggregates and would not scale to large tables; no chart names a person | Each chart's description states what it leaves out; the caching choice is one field of the connection | Re-enable caching with an explicit refresh if the tables grow | Accepted |
| The Spark-in-Docker tests fail when too many run at once | `test_environment_limitation` | `-n auto` (16 workers) started up to 16 Spark containers together, so runs failed with a 600-900 s `TimeoutExpired` or with `CANNOT_OPEN_SOCKET`; the full suite took 32-33 min with 4-9 failures, also on an idle machine with the cluster stopped | `tests/spark_image.py` lets four containers run at once across the pytest workers (`SPARK_TEST_SLOTS` to change it) and removes the container of an aborted run | None | Resolved in issue `#100`: `uv run pytest -n auto tests` gave 828 passed, 2 skipped in 10 min 15 s in one run |

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

### The Bronze -> Silver Job Runs On The Spark Image's Python 3.10, Not The Repository's 3.14

- discovered during issue `#98` (Bronze -> Silver)
- the Spark image runs Python 3.10.12 and PySpark 3.5 requires driver and executors
  to share a minor version (and does not support 3.14), while the repository
  requires `>=3.14`. The job therefore runs the repository's own code
  (`src/open_cvn/`, `src/tfm_lakehouse/`) on 3.10, which works because that code
  happens to be 3.10 compatible; a test parses the Spark-side modules with
  `ast.parse(feature_version=(3, 10))` and forbids `tomllib`, `datetime.UTC`,
  `StrEnum` and any import of `tfm_lakehouse.bronze`, but it cannot catch a
  standard-library name added after 3.10
- `infra/spark-conf/requirements-silver.txt` pins the three direct dependencies
  to `uv.lock`'s versions but the transitive ones to what pip resolves for
  Python 3.10, because `uv.lock`'s `rpds-py 2026.6.3` requires Python >=3.11; the
  validation is therefore not run on exactly the locked dependency set
- PySpark is not a project dependency and cannot be installed on the host, so the
  DataFrame code is verified by running it in the Spark image
  (`tests/test_silver_*_spark.py`, skipped without Docker and the image, hence
  not in CI)
- the silver image must be imported into k3s by hand with `sudo` when
  `requirements-silver.txt` changes
- expected follow-up: revisit when the Spark image moves to a Spark/Python
  combination that supports a newer Python

### Entity Resolution Is Deterministic And Deliberately Conservative

- discovered during issue `#98`
- rule R1 (same ORCID iD) is exact; rule R2 (name and affiliation, for records
  without an iD) merges only when exactly one entity qualifies, so ambiguous records
  stay split. A wrong merge would corrupt every downstream indicator; a missed one
  only splits an entity
- organizations must be equal after normalization (case, accents, stop words,
  appended URLs, word order). Measured on real names, no partial-similarity
  threshold separates the same institution with a campus suffix (Jaccard 0.60 and
  0.40) from two different institutions (0.67, `Universitat de València` against
  `Universitat Politècnica de València`), so partial matches are off by default;
  translations of one institution (`University of the Basque Country` against
  `Universidad del País Vasco`, 0.00) are not matched
- records without an iD are never merged with each other, and a record without
  an affiliation cannot be matched by name alone
- name compatibility covers equal names, a dropped second surname, a leading
  initial, and an initial spelled out later (`Ana M` against `Ana María`, found in
  the real data), but **not both a relaxed given name and a shortened family name at
  once** (measured: 8 of 8 such merges joined different people); a dropped given name,
  transliterations and nicknames are not covered
- measured at scale (issue `#98`, Task 8.5, 10,000 synthetic CVNs, 186 documents
  with a counterpart in silver): rule R1 places 7,098 of 7,098 declaring documents in
  their entity; rule R2 reaches **precision 95.8% and recall 74.2%** (138 correct and 6
  false merges of 144). The precision target of 99% set in the plan was **not met**: the
  6 false merges are different people with the same name and one shared organization,
  indistinguishable with this evidence. Every merge with two or more shared
  organizations was correct (78 of 78) but demanding it for all merges cuts recall to
  41.9%; each link's `evidence` carries `name_match` and `shared_organizations` so a
  consumer can choose that trade-off
- recall is capped by the data: documents with no affiliation cannot be matched by
  name alone (47 of the 186 evaluable ones, ceiling 74.7%)
- a person with two ORCID iDs (duplicate profiles exist) is treated as two entities by
  rule R1 and may be merged with one of them by rule R2
- an iD-merged CVN whose name matches none of the ORCID records sharing its iD is
  kept in the entity and flagged `name_conflict`
- no probabilistic or ML resolution, per the epic
- expected follow-up: none required; future work if recall matters more than
  precision

### Silver Extracts Only The Entity Types The Synthetic Generator Produces

- discovered during issue `#98`
- CVN extraction reads identity, professional experience, education (degrees and
  doctorates) and scientific publications, the four entity types issue `#96`
  generates; other CVN sections are validated but not extracted, and a real CV's
  other publication or affiliation entity types would be ignored
- CVN countries are numeric ISO 3166 codes and only Spain (`724`) is mapped to
  `ES`; the others stay null (country is not used for matching)
- a CVN declaring several distinct ORCID iDs keeps the first and records a warning
- ORCID works are one per work group (the summaries of a group are the same work
  reported by several sources); ORCID work summaries carry no author list, so
  `authors` is empty for them
- expected follow-up: extend the extractors only if issue `#99`'s indicators need
  more (they did not)

### Silver Is Rebuilt In Full On Every Run

- discovered during issue `#98`
- each run reads the current bronze, deduplicates on `record_id` (latest
  `landed_at`, then `ingestion_run_id`) and replaces the six silver tables
  (`createOrReplace`); there is no incremental processing, and Iceberg keeps the
  previous snapshots but nothing exposes them yet
- adequate at this volume (20,000 bulk records); it does not scale to the whole
  ORCID subset (about 42 GB) without incremental processing
- expected follow-up: issue `#101` measures the runtime and the scaling

### Resolution Quality Is Measured Only Against The Synthetic Generator's Ground Truth

- discovered during issue `#98`
- precision and recall are computed against the manifest of the synthetic CVN
  generator, whose name variants are exactly the four issue `#96` produces
  (accents stripped, given name reduced to an initial, family name upper-cased, only the
  first surname); real-world variation is broader, so the figures are optimistic for
  real curricula
- only documents whose seed iD is carried by another record in silver can be
  evaluated: seeds are drawn uniformly from the 301,763-record subset while bronze
  holds a capped sample, so at the default 1,000 documents only 16 of 288 were
  evaluable (all 16 correct) and it took a 10,000-document run to reach 186; the seed
  iD is also the only notion of "same person", so two profiles of one person count as
  a false merge
- expected follow-up: none for this TFM

### The Collaboration Indicator Is A DOI-Only Lower Bound

- discovered during issue `#99`
- silver has no co-author entities (ORCID work summaries carry no author list, and a CVN's
  `authors` are name strings), so `gold.collaboration_pairs` links two entities only when
  both report the same DOI; collaborations on works without a DOI, or reported by only one
  of the two people, are missed
- a person whose CVN was not merged with their ORCID record (rule R2 recall is 74.2%, issue
  `#98`) reports the same DOIs as their own ORCID entity and appears as a collaboration with
  themselves: measured on the real silver against the generator's ground truth, 25 of 9,540
  pairs (0.26%); a production run has no ground truth to remove them. `has_cvn_member` lets
  a consumer keep only pairs of real ORCID data (5,092 of the 9,540)
- a DOI reported by more entities than `--max-entities-per-doi` (default 200) is left out
  of the pairs to bound the cost; it is counted in `gold_run` (none on the current data,
  the maximum is 14 entities per DOI)
- expected follow-up: none for this TFM; author-name resolution over CVN `authors` would need
  its own entity-resolution stage

### Gold Deduplicates Publications Only Within Each Kind Of Key

- discovered during issue `#99`
- a work is identified by its DOI when it has one, otherwise by a hash of its normalized
  title and year; the same work reported with a DOI by one record and without by another
  of the same entity counts twice, and a work whose copies disagree on the year counts once
  per year in the title-keyed case
- a publication year is usable only between 1900 and the run's year plus one (`--max-year`);
  works outside it (1.2% have no year, 16 more are out of range in the current silver) are
  real works in `dim_researcher` and the pairs but are excluded from
  `publications_per_researcher_year`; the run counts them in
  `gold_run.publications_without_year`
- the fused records of one entity inflate a naive count by 5.1% on the current silver (27,483
  of 543,879 rows); this is why the deduplication exists
- expected follow-up: none required

### Career Figures Are Lower Bounds From Known Years

- discovered during issue `#99`
- 18% of the silver affiliations have no start year and 33% no end year (ongoing or unknown);
  `dim_researcher.career_*` use employment stays with known years only and never extend a stay
  to today, so `career_span_years` is a lower bound and is null when no employment has a start
  year; a stay whose records disagree on the end year takes the latest one
- `affiliation_timeline` merges an entity's records by organization and start year; the same
  institution written differently in two records (a campus suffix, a translation) stays two
  organizations, for the reason issue `#98` recorded for entity resolution
- end years reach 2036 in the source data (planned end dates) and are kept as reported
- expected follow-up: none for this TFM

### Gold Is Rebuilt In Full And Only The Latest Publish Is In PostgreSQL

- discovered during issue `#99`
- each run recomputes every gold table from the current silver (`createOrReplace`) and the
  publish replaces the PostgreSQL tables through staging tables and one transaction; Iceberg
  keeps the previous gold snapshots (and `gold_run` records the silver snapshot ids each run
  read), but PostgreSQL holds only the latest, and nothing exposes the history to Superset
- the PostgreSQL password reaches the executors that write over JDBC inside the write's
  options rather than through an environment variable; Spark redacts `password` options in
  its plans, but an operator with access to the driver's configuration should assume the
  password is visible there (acceptable for a local, non-exposed cluster)
- expected follow-up: `#102` (hardening) for credential handling; `#101` measures the runtime

### Gold Indicators Inherit Entity-Resolution Errors

- discovered during issue `#99`
- every indicator is computed over all entity links, so a false rule-R2 merge (precision 95.8%, issue
  `#98`) puts two people's publications and affiliations under one researcher; `entity_link.evidence`
  carries `name_match` and `shared_organizations`, so a stricter reading needs no re-run of silver
- measured on the real silver: undoing the 75 of 164 R2 merges that rest on a single shared organization
  changes entities by +0.25%, distinct publications by +0.07%, per-year rows by +0.13% and collaboration
  pairs by +0.58% (38 of the 55 new pairs are the split record paired with the entity it was taken from);
  the indicators are insensitive to R2's precision at this scale, so the default was not changed
- the measurement covers only the merges this data contains; another sample would give other counts
- expected follow-up: none for this TFM

### Superset Is Deployed From A Deprecated Helm Chart

- discovered during issue `#100`
- the `superset/superset` chart (0.22.8, Superset 6.1.0) has `deprecated: true` in its `Chart.yaml` and the
  official Kubernetes installation page says it is not recommended for new deployments; the official method
  is the Apache Superset Kubernetes Operator (`v1alpha1`, v0.2.0 of 2026-08-11, with breaking changes, no
  bundled PostgreSQL or Redis, custom resources to install)
- the chart was kept on purpose (the original plan, no CRDs, bundled PostgreSQL and Redis) and pinned; its
  subcharts run `docker.io/bitnamilegacy` images, the same frozen registry as the `#91` services
- the official image is a "lean" build with no database driver, so the deployment needs its own image
  (`tfm-lakehouse/superset:6.1.0-pg`), built on the host and imported into k3s by hand
- expected follow-up: the operator as future work; `#102` for hardening

### The Superset Deployment Is Local, Single-Replica And Unhardened

- discovered during issue `#100`
- one replica of the web server, PostgreSQL and Redis, the Celery worker scaled to zero (only synchronous
  queries are used), no TLS or single sign-on, and access only through `kubectl port-forward`; Superset's
  metadata lives on a 2 Gi `local-path` volume with no backup, which is why the dashboard is kept as an
  export under version control
- the first `helm install` was marked `failed` although every pod was healthy: the chart's PostgreSQL took
  about two minutes to boot the first time, the post-install Job outlasted Helm's default 5-minute timeout,
  and the web pod restarted once while the Job was still creating the metadata tables; `helm upgrade
  --timeout 15m` fixed the status and the documented install command carries the flag
- the admin password, `SECRET_KEY` and the metadata database password live in the Secret `superset-secrets`;
  the read-only role's password is in `superset-gold-ro-credentials` and, encrypted with the `SECRET_KEY`, in
  Superset's own metadata (losing the key loses the stored connection password)
- expected follow-up: `#102` (hardening)

### The Dashboard Shows Aggregates Over A Lower-Bound Indicator And Disables Its Data Cache

- discovered during issue `#100`
- each chart states in its description what it leaves out: I1 drops the 443 publications before 1980, I3 the
  16,231 of 94,431 stays with no start year or outside 1970-2026, and I2 is the DOI-only lower bound of `#99`
  restricted to pairs with no synthetic-CVN member (5,092 of 9,540); no chart names a person, because
  `dim_researcher` holds real names from public ORCID records and the screenshots go into a public memoria
- the chart's generated configuration caches query results for 24 hours, which would hide a new
  `transform_publish` run, so the connection sets `cache_timeout = -1` and every view queries PostgreSQL; that
  costs nothing on these aggregates (0.5-0.8 s per chart) and would not scale to large tables
- what was shown to work on the real cluster: a reader polling the four charts during a full DAG run saw no
  error and no empty result, and the run id changed in one step; the publish's lock is held for milliseconds
  and the reader sampled every few seconds, so that shows no sustained window rather than proving none
- expected follow-up: none for this TFM

### The Spark-In-Docker Tests Fail When Too Many Run At Once

- discovered during issue `#100`
- `uv run pytest -n auto tests` starts one worker per core (16); the Spark tests of issues `#98` and `#99`
  (17 tests in three files) each run a JVM and a Python process in Docker, so up to 16 run at the same time. Two
  failure kinds appear: `subprocess.TimeoutExpired` on the `docker run` (limits of 600 and 900 s), and
  `PySparkRuntimeError: [CANNOT_OPEN_SOCKET] ... Connection refused` after the JVM's `serve-DataFrame` thread logs
  `Accept timed out` (the Python process did not connect to the JVM's socket within its timeout, which is what a
  starved process does); the logs show single Spark stages taking 20-80 s
- first seen in two runs of the full suite (9 then 4 failures, a different set each time, 32-33 min against 9 min 53
  s at the end of `#99`), when the cluster's own load (Airflow's probes start a Python interpreter every few seconds)
  was thought to be the cause; on 2026-09-21, with the cluster stopped and the machine idle, the three Spark files
  run with `-n auto` failed as well (5 failed, 2 errors, 17 min 22 s), so the concurrency of the Spark containers is
  the cause and the cluster's load only makes it worse
- the same 17 tests all pass with `-n 4` (5 min 20 s, idle machine, cluster stopped); earlier reruns with `-n 2` (7
  cases) and `-n 4` (14 tests) also passed; no assertion ever failed
- resolved in issue `#100` (decision D14): `tests/spark_image.py` limits the Spark containers that run at once to
  four across all pytest workers (lock files; `SPARK_TEST_SLOTS` changes the number) and removes the container of a
  run that is aborted, which a timeout used to leave running; `uv run pytest -n auto tests`, exactly as documented,
  then gave 828 passed and 2 skipped in 10 min 15 s in a single run on an idle machine with the cluster stopped
  (32-33 minutes and failures before); six tests in `tests/test_spark_image_slots_unit.py` cover the mechanism
- if the machine has fewer cores or the Spark image gets heavier, `SPARK_TEST_SLOTS=2` is the first thing to try

## Documentation Rule

Whenever a new limitation is discovered, add it here and reference the issue
expected to address it.
