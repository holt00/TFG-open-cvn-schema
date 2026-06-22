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

## Impact On Issue `#15`

Issue `#15` may continue without automatic wrapper field attachment if it records
this limitation clearly.

Until this hotfix is implemented, issue `#15` should:

- keep wrapper policy decisions visible as semantic-policy metadata
- avoid pretending wrapper-aware fields were attached automatically
- avoid raw XSD or generated-binding scans in generator code
- leave generated wrapper-specific field shapes as future work dependent on this
  hotfix

## Verification Strategy When Implemented

Use the repository fast-test command as the default verification command:

```bash
uv run pytest -n auto tests
```

Targeted single-file commands should be used only when debugging a specific
failure.

## Status

- Status: planned
- Implementation state: not started
