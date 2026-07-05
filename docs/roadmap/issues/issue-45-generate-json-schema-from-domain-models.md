# Issue 45 - Generate JSON Schema From Domain Models

## Summary

Issue `#45` researches and implements JSON Schema generation from the
domain-oriented Pydantic layer.

This issue is part of epic `#41`.

## Goal

- generate JSON Schema for the Open CVN data representation
- use Pydantic v2 JSON Schema support where suitable
- preserve semantic trace and version metadata where useful
- document limitations of generated JSON Schema

## Background

Pydantic v2 supports JSON Schema generation through `model_json_schema()`,
`TypeAdapter.json_schema()`, and `models_json_schema(...)`. The expected standard
baseline is JSON Schema Draft 2020-12.

The project must decide whether the JSON Schema is generated directly from the
current domain Pydantic models or from a refined Open CVN root model defined in
issue `#46`.

## Planned Steps

1. inspect current generated domain model hierarchy
2. research Pydantic JSON Schema modes: `validation` and `serialization`
3. evaluate `models_json_schema(...)` for multi-model schema generation
4. define schema metadata: title, version, description, `$id`, and `$schema`
5. decide how to handle `$defs`, references, enums, unions, optional fields, and
   lists
6. decide how much CVN trace metadata belongs in JSON Schema
7. implement schema generation if approved
8. write generated schema output to a documented location
9. add tests for determinism and JSON validity

## Approved Execution Plan

The approved implementation plan is to generate a reproducible JSON Schema
artifact for Open CVN from the issue `#43` conceptual inventory, while using
Pydantic v2 JSON Schema support as technical evidence and compatibility support
rather than as the final conceptual root shape.

The canonical generated artifact will be:

```text
schemas/open_cvn.schema.json
```

The implementation must preserve this boundary:

- `src/cvn_codegen/`: hand-maintained schema generation logic
- `schemas/`: generated JSON Schema artifact
- `src/models/cvn/generated/`: generated Pydantic domain models, not edited by hand
- `src/generated/`: generated structural bindings, not edited by hand

### Execution Reporting Protocol

For each implementation step, the worker must report:

1. current task and subtask identifier
2. short summary of what the task or subtask does
3. whether any files need user modification
4. next step to follow

Code and documentation edits must be proposed before execution when the user has
reserved manual file modification for themselves.

### Task 1 - Pydantic JSON Schema Spike

Summary:
inspect current generated domain models and confirm how Pydantic v2 emits JSON
Schema for representative generated models, shared components, enums, optional
fields, lists, and model references.

Subtasks:

1. Inspect `models.cvn.generated.__all__` and representative generated modules.
2. Identify Pydantic `BaseModel` classes and enum classes exported by the domain
   package.
3. Evaluate `model_json_schema(mode="validation")` for representative models.
4. Evaluate `model_json_schema(mode="serialization")` for representative models.
5. Evaluate `pydantic.json_schema.models_json_schema(...)` for multi-model
   generation.
6. Record the implementation decision: use `validation` mode as the default
   schema-generation mode unless a later test proves serialization mode is more
   appropriate.

Expected findings:

- Pydantic emits Draft 2020-12-compatible schemas.
- Direct Pydantic schema output is useful for component evidence.
- Direct generated Pydantic model schemas are not the final conceptual root
  because they expose implementation-oriented generated class/module shapes.

### Task 2 - Define JSON Schema Artifact Contract

Summary:
define the stable metadata and root layout for the generated Open CVN JSON Schema
artifact.

Subtasks:

1. Define JSON Schema metadata:
   - `$schema`: `https://json-schema.org/draft/2020-12/schema`
   - `$id`: `https://open-cvn.local/schema/open-cvn.schema.json`
   - `title`: `Open CVN JSON Schema`
   - `description`: generated schema from conceptual inventory and domain
     Pydantic evidence
2. Use `SemanticPolicyBundle.metadata.policy_name` and
   `SemanticPolicyBundle.metadata.policy_version` as schema policy metadata.
3. Define a provisional root object with:
   - `schema_version`
   - `policy_name`
   - `policy_version`
   - `curriculum`
4. Store generated definitions under `$defs`.
5. Mark the root shape as provisional until issue `#46` defines the canonical
   Open CVN JSON shape.

Expected result:
a deterministic artifact contract that supports issue `#49` validation research
without prematurely replacing issue `#46`.

### Task 3 - Implement JSON Schema Generator Module

Summary:
create a hand-maintained generator module that builds the schema from the
canonical conceptual inventory and writes the canonical schema artifact.

Files:

- Create: `src/cvn_codegen/json_schema_generator.py`

Required functions:

- `build_json_schema_metadata(inventory)`
- `build_schema_for_attribute(attribute)`
- `build_schema_for_entity(entity)`
- `build_schema_for_vocabulary(vocabulary)`
- `build_open_cvn_json_schema(inventory)`
- `write_json_schema(output_path, schema)`
- `generate_open_cvn_json_schema(output_path=Path("schemas/open_cvn.schema.json"))`
- `main()`

Implementation requirements:

- Consume `build_canonical_conceptual_model_inventory()` from
  `cvn_codegen.conceptual_model_extractor` for canonical generation.
- Emit deterministic dictionaries and arrays by sorting identifiers.
- Write JSON with `indent=2`, `sort_keys=True`, and a trailing newline.
- Avoid raw XML/XSD rediscovery in the schema generator.
- Do not manually edit generated domain models.

### Task 4 - Map Conceptual Types To JSON Schema

Summary:
map issue `#43` conceptual attribute types and cardinality into JSON Schema
shapes.

Mapping rules:

- `text` -> `{"type": "string"}`
- `date_like` -> `{"type": "string"}`
- `duration_like` -> `{"type": "string"}`
- `boolean` -> `{"type": "boolean"}`
- `decimal_number` -> `{"type": "number"}`
- `controlled_reference` -> object with `code`, `label`, and optional
  source-reference metadata
- `value_object` -> `$ref` to shared wrapper definitions when wrapper type names
  identify `FlexibleDateValue`, `OfficialIdValue`, `EntityTypeValue`, or
  `EntityNameValue`
- `unknown` -> permissive schema plus an `x-open-cvn-limitation` extension

Cardinality and presence rules:

- `repeated` attributes become arrays.
- required single attributes appear under parent `required`.
- optional attributes allow `null`.
- unknown presence does not become required.

### Task 5 - Preserve CVN Trace In Schema Extensions

Summary:
carry CVN trace and semantic evidence into JSON Schema as non-validating
extensions.

Required extensions where evidence exists:

- `x-open-cvn-code`
- `x-open-cvn-xml-paths`
- `x-open-cvn-domain-shape-kind`
- `x-open-cvn-enum-eligibility`
- `x-open-cvn-source-reference`
- `x-open-cvn-confidence`
- `x-open-cvn-vocabulary-kind`

Rules:

- Extensions must not change validation semantics.
- Trace should remain deterministic and sorted where collections are used.
- CVN trace should not be promoted to required data fields unless the model
  already defines such a field.

### Task 6 - Render Vocabularies And Enums

Summary:
represent conceptual vocabularies from the issue `#43` inventory without closing
open-world references incorrectly.

Rules:

- `ConceptualVocabularyKind.ENUMERATION` with known values emits a closed `enum`.
- Direct compact enum example `CVN_SEX_A` must emit enum values.
- `CVN_ENTITY_TYPE` must not emit a closed enum because semantic evidence marks
  it enum-ineligible.
- subtype-backed, hierarchical, registry, thesaurus, unresolved, and under-traced
  references must remain open object/reference shapes.
- Each vocabulary definition should preserve `source_reference`,
  `enum_eligibility`, and vocabulary kind through `x-open-cvn-*` extensions.

### Task 7 - Add Unit Tests

Summary:
add focused tests for schema metadata, type mapping, trace extensions, and
determinism without requiring the full canonical source-package pipeline.

Files:

- Create: `tests/test_json_schema_generator_unit.py`

Required tests:

- schema metadata declares Draft 2020-12.
- optional string attributes allow `null`.
- repeated attributes become arrays.
- unknown attributes preserve an explicit limitation extension.
- trace extensions are emitted for representative attributes.
- schema generation is deterministic for the same in-memory inventory.

### Task 8 - Add Canonical Pipeline JSON Schema Tests

Summary:
add integration tests that build the canonical conceptual inventory and verify the
Open CVN JSON Schema artifact behavior.

Files:

- Create: `tests/test_generation_pipeline_json_schema.py`

Required tests:

- generated schema is JSON serializable.
- generated schema declares `$schema`, `$id`, `title`, and policy metadata.
- `$defs` is non-empty.
- root curriculum and identity/person conceptual definitions are present.
- `CVN_SEX_A` is represented as a closed enum.
- `CVN_ENTITY_TYPE` is not represented as a closed enum.
- writing the schema twice produces identical bytes.
- module CLI can write to a temporary output path.

### Task 9 - Generate Canonical JSON Schema Artifact

Summary:
run the generator and commit the generated schema artifact under `schemas/`.

Files:

- Create: `schemas/open_cvn.schema.json`

Command:

```bash
uv run python -m cvn_codegen.json_schema_generator
```

Checks:

- artifact is valid JSON.
- artifact has deterministic ordering.
- artifact includes expected metadata.
- artifact does not require manual edits.

### Task 10 - Update Persistent Documentation

Summary:
document the schema-generation approach, workflow command, and known limitations.

Files:

- Create: `docs/pipeline/json_schema_generation.md`
- Modify: `docs/development/regeneration_workflow.md`
- Modify: `docs/pipeline/cvn_pydantic_generation_pipeline.md`
- Modify: `docs/pipeline/known_limitations.md`
- Modify: `PROJECT_GUIDE.md` if the document map or repository orientation now
  references the `schemas/` artifact directory

Required documentation content:

- schema source is conceptual inventory plus domain/Pydantic evidence.
- direct generated Pydantic schemas are not the final conceptual root.
- command to regenerate the schema.
- generated artifact path.
- Draft 2020-12 baseline.
- issue `#46` owns the future canonical JSON shape refinement.
- issue `#49` can consume the artifact for validation research.

### Task 11 - Update Roadmap And Issue State

Summary:
record implementation results and move project state forward after code,
artifact, tests, and docs are complete.

Files:

- Modify: `docs/roadmap/issues/issue-45-generate-json-schema-from-domain-models.md`
- Modify: `docs/context/current_status.md`
- Modify: `docs/roadmap/cvn_generation_roadmap.md`

Required updates:

- mark issue `#45` as completed.
- record implementation decisions and any deviations from this plan.
- record generated artifacts and verification commands.
- update next planned work to issue `#46`.

### Task 12 - Verification

Summary:
verify targeted JSON Schema behavior, canonical artifact generation, and full
repository regression suite.

Commands:

```bash
uv run pytest -n auto tests/test_json_schema_generator_unit.py tests/test_generation_pipeline_json_schema.py -v
uv run python -m cvn_codegen.json_schema_generator
uv run pytest -n auto tests
```

Expected results:

- targeted JSON Schema tests pass.
- canonical schema generation succeeds.
- full test suite passes.

If full-suite verification is not practical in the session, record the exact
reason and the strongest executed substitute verification in this issue document.

## Risks And Constraints

- Direct Pydantic JSON Schema output can expose implementation-oriented generated
  class shapes; the issue `#45` artifact must therefore use conceptual inventory
  as the canonical root source.
- Issue `#46` may redefine the final Open CVN JSON shape; issue `#45` must label
  its root shape as provisional.
- JSON Schema cannot express every CVN semantic invariant or external registry
  rule; preserve such facts through documentation and `x-open-cvn-*` extensions.
- The schema may be large; use `$defs`, references, and deterministic ordering.

## Expected Output

- documented JSON Schema generation approach
- generated Open CVN JSON Schema artifact or prototype
- command to regenerate schema
- tests for schema generation if implementation is approved

## Implementation Summary

- JSON Schema generation is implemented in
  `src/cvn_codegen/json_schema_generator.py`
- The canonical generated artifact is:
  `schemas/open_cvn.schema.json`
- The schema generation approach is documented in:
  `docs/pipeline/json_schema_generation.md`
- The generator uses the issue `#43` conceptual inventory as the canonical root
  source and treats Pydantic v2 JSON Schema support as technical evidence rather
  than as the final conceptual root output
- The artifact declares JSON Schema Draft 2020-12 explicitly
- The artifact preserves CVN trace and semantic evidence through non-validating
  `x-open-cvn-*` extensions
- `CVN_SEX_A` is emitted as an eligible closed enum-backed vocabulary definition
- `CVN_ENTITY_TYPE` remains open because semantic policy marks it
  enum-ineligible

## Implementation Verification

- Targeted JSON Schema verification command:
  `uv run pytest -n auto tests/test_json_schema_generator_unit.py tests/test_generation_pipeline_json_schema.py -v`
- Targeted JSON Schema verification result:
  `13 passed in 109.45s (0:01:49)`
- Canonical schema generation command:
  `uv run python -m cvn_codegen.json_schema_generator`
- Canonical schema generation result:
  `Generated JSON Schema: schemas/open_cvn.schema.json`
- Full-suite verification command:
  `uv run pytest -n auto tests`
- Full-suite verification result:
  `326 passed in 780.28s (0:13:00)`

Additional manual schema checks were executed after implementation:

- canonical regeneration with:
  `uv run python -m cvn_codegen.json_schema_generator`
- JSON parsing of `schemas/open_cvn.schema.json`
- metadata verification for `$schema`, `$id`, and `title`
- `$defs` presence verification; current generated schema contains `182`
  definitions
- internal `$ref` resolution check; no broken local `$defs` references found
- presence verification for `core.curriculum` and `identity.person`
- `CVN_SEX_A` vocabulary verification; emitted as a closed enum with `2` values
- `CVN_ENTITY_TYPE` vocabulary verification; remains open and has
  `x-open-cvn-enum-eligibility: ineligible`
- temporary CLI output verification with:
  `uv run python -m cvn_codegen.json_schema_generator --output-path /tmp/opencode/open_cvn.schema.json`
- byte-for-byte comparison between temporary output and
  `schemas/open_cvn.schema.json`
- historical issue `#45` provisional root example shape verification with:
  `schema_version`, `policy_name`, `policy_version`, and empty `curriculum`

Issue `#46` later replaced this provisional root with the canonical Open CVN JSON
root shape: `schema_version`, `metadata`, `curriculum`, and `extensions`.

External JSON Schema meta-schema validation with the `jsonschema` Python package
was not executed because `jsonschema` is not installed in the project
environment.

## Verification

- schema is valid JSON
- schema declares expected draft metadata
- generation is deterministic
- representative model definitions appear under `$defs`
- schema supports validation needs for issue `#49`

## Impact On Later Issues

- issue `#46` uses findings to define canonical JSON shape
- issue `#49` uses schema for JSON import validation

## Status

- Status: completed
