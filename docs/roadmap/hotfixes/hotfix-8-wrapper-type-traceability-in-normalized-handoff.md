# Hotfix 8 - Wrapper Type Traceability In Normalized Handoff

## Summary

Hotfix `#8` records a corrective gap discovered during issue `#15` planning and
implementation: the current normalized metadata handoff does not expose enough
wrapper-type evidence for the domain generator to attach high-value `xs:choice`
wrapper semantics to fields without re-reading raw structural sources.

Issue `#14` already defines semantic policy entries for important wrapper types:

1. `FlexibleDatesType`
2. `OfficialIdType`
3. `EntityTypeType`
4. `EntityNameType`

However, issue `#15` cannot apply those wrapper policies automatically from the
current `NormalizedCodeEntry` and `TreePathEntry` contracts. The normalized tree
metadata currently preserves CVN codes, XML paths, property names, indicator
names, and selected `<Value>` content, but it does not carry the structural type
name assigned by `CVN.xsd` or generated structural bindings.

## Motivation

Issue `#15` must consume normalized metadata and `SemanticPolicyBundle` outputs.
It must not rediscover semantic meaning by scanning raw XSD files or generated
structural bindings inside the domain generator.

Wrapper-aware domain generation needs a reliable typed handoff from an upstream
stage. Without that handoff, the generator has only two bad choices:

1. ignore wrapper policy during field attachment
2. violate the architecture boundary by inspecting raw `CVN.xsd` or
   `src/generated/` structures directly

This hotfix exists so a future implementation can fix the handoff boundary
instead of adding ad hoc generator-side source discovery.

## Observed Evidence

During issue `#15` work, wrapper discovery was checked against the current
repository artifacts.

Findings:

- `FlexibleDatesType`, `OfficialIdType`, `EntityTypeType`, and `EntityNameType`
  are present in `XSD/CVN.xsd` and generated structural bindings under
  `src/generated/cvn/`
- those wrapper names are present in `src/cvn_codegen/semantic_policy.py` as
  semantic wrapper-policy validation cases
- canonical `CVNTreeModel.xml` normalized through
  `load_and_extract_tree_entries(...)` produced `5051` tree entries and `33`
  unique non-empty `tree_value` values
- exact wrapper-name matches in `TreePathEntry.tree_value`: `0`
- partial wrapper-name matches in `TreePathEntry.tree_value`: `0`
- observed `tree_value` values are CVN value literals or reference names such as
  `000`, `010`, `CVN`, `EUR`, `OTHERS`, `THESAURUS_CODES`, `UNESCO`, and
  `UNESCO_CODES`, not wrapper type names

### Evidence Probe Used During Issue `#15`

The wrapper-evidence check was obtained with this repository-local probe:

```bash
uv run python - <<'PY'
from pathlib import Path

from cvn_codegen.tree_metadata import load_and_extract_tree_entries

tree_model_path = Path("docs/CvnXML_v1.4.3_2.1_17012025/XML/CVNTreeModel.xml")
entries = load_and_extract_tree_entries(tree_model_path)
wrappers = {
    "FlexibleDatesType",
    "OfficialIdType",
    "EntityTypeType",
    "EntityNameType",
}

exact_matches = [entry for entry in entries if entry.tree_value in wrappers]
partial_matches = [
    entry
    for entry in entries
    if entry.tree_value
    and any(wrapper in entry.tree_value for wrapper in wrappers)
]
tree_values = sorted({entry.tree_value for entry in entries if entry.tree_value})

print(f"total_entries={len(entries)}")
print(f"unique_tree_values={len(tree_values)}")
print(f"exact_wrapper_matches={len(exact_matches)}")
print(f"partial_wrapper_matches={len(partial_matches)}")
print("tree_values=")
for tree_value in tree_values:
    print(tree_value)
PY
```

Observed result:

```text
total_entries=5051
unique_tree_values=33
exact_wrapper_matches=0
partial_wrapper_matches=0
tree_values=
000
010
020
030
040
050
060
070
080
090
100
110
120
130
150
160
170
180
190
230
250
310
490
500
520
540
800
CVN
EUR
OTHERS
THESAURUS_CODES
UNESCO
UNESCO_CODES
```

This result supports the issue `#15` decision to avoid generator-side wrapper
attachment until a future handoff exposes wrapper type evidence explicitly.

## Scope Of This Hotfix

This hotfix is a planning and implementation contract for a future corrective
patch. It does not need to be completed inside issue `#15` unless wrapper-aware
field attachment becomes a hard acceptance criterion for that issue.

This hotfix should include:

- an upstream structural-to-normalized traceability bridge for wrapper type names
- additive typed metadata that lets issue `#14` or issue `#15` associate a
  normalized field with a wrapper policy without raw XSD inspection
- tests proving wrapper evidence exists for representative `FlexibleDatesType`,
  `OfficialIdType`, `EntityTypeType`, and `EntityNameType` cases
- documentation updates explaining that the domain generator consumes wrapper
  handoff data instead of rediscovering wrappers

This hotfix should not include:

- manual edits to `src/generated/`
- generator-side scanning of raw `CVN.xsd` as the permanent solution
- broad redesign of normalization unrelated to wrapper traceability
- domain-model emission beyond whatever tests are needed to prove the handoff

## Issues Affected

- issue `#13` if the normalized metadata contract is extended directly
- issue `#14` if `SemanticPolicyBundle` receives wrapper-to-field attachment
  evidence
- issue `#15` as downstream domain generator consumer
- issue `#16` for generator and handoff test coverage
- issue `#17` for workflow documentation

## Required Design Decision

The future implementation must choose where wrapper type evidence enters the
pipeline.

Preferred options:

1. extend normalization with structural type metadata keyed by XML path or code
2. add a separate structural trace index consumed by semantic policy and domain
   generation

The chosen design must preserve this boundary:

- raw XSD and generated structural bindings may be inspected by an upstream
  extraction step
- issue `#15` generator logic should consume typed wrapper evidence, not raw
  structural files

## Acceptance Criteria

The hotfix is complete when all of these are true:

1. normalized or semantic-policy handoff exposes wrapper evidence for fields that
   use `FlexibleDatesType`, `OfficialIdType`, `EntityTypeType`, and
   `EntityNameType`
2. domain generation can decide wrapper-aware field shapes from typed handoff
   data alone
3. the generator no longer needs to inspect raw XSD or generated structural
   classes for wrapper attachment
4. tests cover at least one real representative field for each wrapper family
5. issue `#15` documentation is updated to remove or narrow the temporary
   limitation once the handoff exists

## Execution Plan

This section is the accepted implementation plan for hotfix `#8`. During
execution, progress must be reported by task and, when applicable, by subtask,
using the identifiers below.

### Execution Reporting Protocol

Each work update for this hotfix must include:

1. current task identifier and title
2. current subtask identifier when work is inside a subtask
3. short summary of what the task or subtask will do before starting it
4. final note stating whether the user must modify any file
5. next step to follow

When code files must change, the default expectation is that the user performs
the modification unless explicitly delegated otherwise. Documentation-only edits
may be made by repository agents when requested.

### Chosen Design

Use an upstream structural-to-normalized bridge:

```text
CVN.xsd + Common.xsd + CVNTreeModel.xml
  -> structural wrapper trace index
  -> normalized metadata handoff
  -> semantic policy wrapper attachment
  -> domain generator wrapper-aware field decisions
```

The domain generator must consume typed handoff data. It must not inspect raw
XSD files or generated structural bindings to attach wrapper semantics.

### H8-T01 - Structural Trace Contract

Summary: define the additive typed metadata needed to carry structural wrapper
evidence through normalization without changing generated bindings.

Subtasks:

1. `H8-T01.1`: add a `StructuralTypeEvidence` dataclass to
   `src/cvn_codegen/normalization_types.py`
2. `H8-T01.2`: include source fields such as `element_name`,
   `declaring_type_name`, `structural_type_name`, `xml_path`, and
   `source_xsd_file`
3. `H8-T01.3`: include wrapper-specific fields such as
   `terminal_wrapper_type_name` and `ancestor_wrapper_type_names`
4. `H8-T01.4`: extend `TreePathEntry` with optional structural evidence
5. `H8-T01.5`: extend `NormalizedCodeEntry` with aggregated structural evidence

User file modification required: yes, code files under `src/cvn_codegen/`.

Next step: implement structural trace extraction in `H8-T02`.

### H8-T02 - Structural Trace Extraction Module

Summary: create an upstream extractor that reads canonical XSD structure and
builds a deterministic type-resolution map independent from the domain
generator.

Subtasks:

1. `H8-T02.1`: create `src/cvn_codegen/structural_type_trace.py`
2. `H8-T02.2`: parse `CVN.xsd` and `Common.xsd` with namespace-safe XML logic
3. `H8-T02.3`: extract `complexType -> child element -> child type` mappings
4. `H8-T02.4`: extract root element mappings for `Version`, `Agent`, and
   `CvnItem`
5. `H8-T02.5`: resolve `TreePathEntry.xml_path` segments against the structural
   map
6. `H8-T02.6`: detect terminal wrapper types among `FlexibleDatesType`,
   `OfficialIdType`, `EntityTypeType`, and `EntityNameType`
7. `H8-T02.7`: preserve ancestor wrapper evidence without treating descendants
   as terminal wrapper fields

User file modification required: yes, code file under `src/cvn_codegen/`.

Next step: wire extracted evidence into normalization in `H8-T03`.

### H8-T03 - Normalization Integration

Summary: enrich tree entries and normalized aggregate entries with structural
evidence before semantic policy consumes them.

Subtasks:

1. `H8-T03.1`: update `build_tree_path_entry(...)` to accept optional structural
   evidence
2. `H8-T03.2`: add XSD path parameters to the normalization entry point, likely
   `cvn_xsd_path` and `common_xsd_path`
3. `H8-T03.3`: enrich tree entries after loading `CVNTreeModel.xml` and before
   indexing by code and XML path
4. `H8-T03.4`: aggregate structural evidence from `TreePathEntry` values into
   each `NormalizedCodeEntry`
5. `H8-T03.5`: preserve previous behavior when XSD paths are not provided

User file modification required: yes, code files under `src/cvn_codegen/`.

Next step: attach wrapper policies in semantic layer in `H8-T04`.

### H8-T04 - Semantic Policy Attachment

Summary: consume normalized structural evidence and attach existing wrapper
policies to real normalized fields.

Subtasks:

1. `H8-T04.1`: extend `SemanticDecisionTrace` with wrapper type names
2. `H8-T04.2`: extend `SemanticFieldPolicy` with applied wrapper policy data
3. `H8-T04.3`: resolve wrapper policies using `wrapper_policies_by_name`
4. `H8-T04.4`: add wrapper applied rules such as `wrapper_type:<name>`
5. `H8-T04.5`: copy wrapper structural limitation flags into field policy
6. `H8-T04.6`: replace or narrow the old automatic wrapper-application
   limitation text

User file modification required: yes, code file `src/cvn_codegen/semantic_policy.py`.

Next step: expose wrapper-aware decisions to domain generation in `H8-T05`.

### H8-T05 - Domain Generator Consumption

Summary: make domain generation decide wrapper-aware field shapes from semantic
handoff data only.

Subtasks:

1. `H8-T05.1`: extend `DomainFieldSpec` with wrapper type names or equivalent
   wrapper metadata
2. `H8-T05.2`: include wrapper evidence in `DomainFieldSpec.trace`
3. `H8-T05.3`: pass canonical `CVN.xsd` and `Common.xsd` paths through
   `get_canonical_generation_paths()` and `generate_domain_models()`
4. `H8-T05.4`: update field type resolution to use semantic wrapper evidence,
   not raw structural files
5. `H8-T05.5`: ensure generated output remains deterministic

User file modification required: yes, code files under `src/cvn_codegen/`.

Next step: add shared domain wrapper value components in `H8-T06`.

### H8-T06 - Shared Domain Wrapper Components

Summary: add minimal reusable domain value objects for wrapper-aware generated
fields without broad domain-model redesign.

Subtasks:

1. `H8-T06.1`: add `FlexibleDateValue` to `src/models/cvn/components.py`
2. `H8-T06.2`: add `OfficialIdValue` to `src/models/cvn/components.py`
3. `H8-T06.3`: add `EntityTypeValue` to `src/models/cvn/components.py`
4. `H8-T06.4`: add `EntityNameValue` to `src/models/cvn/components.py`
5. `H8-T06.5`: update generated-module import collection for these components
6. `H8-T06.6`: avoid editing `src/generated/` manually

User file modification required: yes, code file `src/models/cvn/components.py`
and generator code under `src/cvn_codegen/`.

Next step: add targeted tests in `H8-T07`.

### H8-T07 - Unit And Integration Tests

Summary: prove wrapper evidence exists for representative real fields and flows
from extraction to generator handoff.

Subtasks:

1. `H8-T07.1`: add tests for `structural_type_trace.py`
2. `H8-T07.2`: cover `OfficialIdType` with code `000.010.000.100`
3. `H8-T07.3`: cover `EntityTypeType` with a representative `Type` field, such
   as `010.010.000.040`
4. `H8-T07.4`: cover `EntityNameType` with a representative `EntityName` field,
   such as `010.010.000.020`
5. `H8-T07.5`: cover `FlexibleDatesType` with a representative date field, such
   as `010.010.000.180` or `020.010.010.130`
6. `H8-T07.6`: verify child alternatives such as `DNI`, `Passport`, and `Others`
   keep ancestor wrapper trace but do not become terminal wrapper fields
7. `H8-T07.7`: update normalization tests for structural evidence aggregation
8. `H8-T07.8`: update semantic-policy tests for wrapper auto-attachment
9. `H8-T07.9`: update domain-generator tests for wrapper-aware Python types and
   trace metadata

User file modification required: yes, test files under `tests/`.

Next step: regenerate and verify outputs in `H8-T08`.

### H8-T08 - Generation And Verification

Summary: regenerate domain output and run targeted plus full regression checks.

Subtasks:

1. `H8-T08.1`: run targeted tests for structural trace, normalization, semantic
   policy, and domain generator modules
2. `H8-T08.2`: run canonical domain generation with
   `uv run python -m cvn_codegen.domain_model_generator`
3. `H8-T08.3`: verify generated package imports for `models.cvn.generated`
4. `H8-T08.4`: run full test suite with `uv run pytest -n auto tests`
5. `H8-T08.5`: record exact verification commands and results in this hotfix
   document after implementation

User file modification required: no code edit required during verification;
generated domain files may change as command output.

Next step: update persistent documentation in `H8-T09`.

### H8-T09 - Documentation Updates

Summary: align roadmap, current status, limitation register, and downstream issue
records once implementation is verified.

Subtasks:

1. `H8-T09.1`: update this hotfix document with implementation notes,
   artifacts, verification results, and final status
2. `H8-T09.2`: update `docs/context/current_status.md`
3. `H8-T09.3`: update `docs/pipeline/known_limitations.md` to remove or narrow
   the wrapper-handoff limitation
4. `H8-T09.4`: update
   `docs/pipeline/cvn_pydantic_generation_pipeline.md` with the new upstream
   structural trace bridge
5. `H8-T09.5`: update
   `docs/roadmap/issues/issue-15-domain-model-generator.md` to remove or narrow
   the temporary limitation
6. `H8-T09.6`: update `docs/roadmap/cvn_generation_roadmap.md` if the hotfix
   status is tracked there
7. `H8-T09.7`: update `AGENTS.md` because its current document map omits
   hotfix `#8`
8. `H8-T09.8`: sweep `PROJECT_GUIDE.md`,
   `docs/context/project_context_index.md`, and `docs/context/current_status.md`
   for consistency

User file modification required: yes, documentation files listed above.

Next step: mark hotfix complete only after code, tests, generation, and docs all
match the acceptance criteria.

## Implementation Performed

Hotfix `#8` is implemented as an upstream structural-to-normalized trace bridge.

Implemented artifacts:

- `StructuralTypeEvidence` in `src/cvn_codegen/normalization_types.py`
- optional `TreePathEntry.structural_type_evidence`
- aggregated `NormalizedCodeEntry.structural_type_evidence`
- `src/cvn_codegen/structural_type_trace.py` for XSD-backed structural type
  resolution
- normalization enrichment through optional `cvn_xsd_path` and `common_xsd_path`
  parameters on `build_normalization_result(...)`
- semantic wrapper attachment from normalized `structural_type_evidence`
- wrapper policy trace fields in `SemanticDecisionTrace` and
  `SemanticFieldPolicy`
- wrapper-aware domain field specs and trace metadata in the domain generator
- canonical generator path handoff for `CVN.xsd` and `Common.xsd`
- shared domain wrapper components in `src/models/cvn/components.py`:
  `FlexibleDateValue`, `OfficialIdValue`, `EntityTypeValue`, and
  `EntityNameValue`
- targeted structural trace tests in `tests/test_structural_type_trace_unit.py`

The domain generator now consumes typed semantic-policy handoff data and does not
inspect raw XSD files or generated structural bindings for wrapper attachment.

## Impact On Issue `#15`

Issue `#15` no longer needs to defer wrapper-aware automatic field attachment for
the four wrapper families covered by this hotfix.

Current behavior:

- canonical generation passes `CVN.xsd` and `Common.xsd` into normalization
- normalized entries expose terminal wrapper evidence for representative
  `FlexibleDatesType`, `OfficialIdType`, `EntityTypeType`, and `EntityNameType`
  fields
- semantic policy attaches wrapper policies from `SemanticPolicyBundle`
- domain generation maps wrapper-aware fields to shared wrapper value components
- child alternatives such as `DNI` preserve ancestor wrapper trace without being
  treated as terminal wrapper fields

Boundary preserved:

- raw XSD files are inspected only by the upstream structural trace step
- generated structural bindings under `src/generated/` are not edited manually
- the domain generator consumes normalized and semantic handoff data only

## Verification Strategy When Implemented

Use the repository fast-test command as the default verification command:

```bash
uv run pytest -n auto tests
```

Targeted single-file commands should be used only when debugging a specific
failure.

## Verification Performed

- Targeted hotfix verification passed with:
  `uv run pytest -n auto tests/test_structural_type_trace_unit.py tests/test_normalization_unit.py tests/test_semantic_policy_unit.py tests/test_domain_model_generator_unit.py`
- Observed targeted result:
  `152 passed in 118.80s (0:01:58)`
- Canonical generation passed with:
  `uv run python -m cvn_codegen.domain_model_generator`
- Observed generation result:
  `Generated 105 files`
- Generated import smoke passed for:
  - `models.cvn.generated`
  - `models.cvn.generated.enums`
  - `models.cvn.generated.manual_only`
- Full repository verification passed with:
  `uv run pytest -n auto tests`
- Observed full-suite result:
  `228 passed in 189.76s (0:03:09)`

## Status

- Status: completed
- Implementation state: implemented and verified
