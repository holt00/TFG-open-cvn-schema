# Open CVN JSON Mapping Notes

## Purpose

This document records how issue `#43` conceptual evidence and issue `#45` JSON
Schema evidence map into the issue `#46` canonical Open CVN JSON format.

## Conceptual Inventory To JSON

`ConceptualModelInventory` maps to one Open CVN JSON document.

- `inventory.policy_name` maps to `metadata.policy.name`
- `inventory.policy_version` maps to `metadata.policy.version`
- `ConceptualDomainArea.area_id` maps to a `curriculum` section
- `ConceptualEntity` maps to either `curriculum.identity` or a repeated section
  entry
- `ConceptualAttribute` maps to a field under `data` or, for identity, under
  `curriculum.identity`
- `ConceptualVocabulary` maps to controlled-reference validation and source
  metadata
- `ConceptualTrace` maps to runtime `trace` metadata where source evidence is
  useful for auditing

## Entity Mapping

`core.curriculum` represents the conceptual root and maps to the runtime
`curriculum` object.

`identity.person` maps to `curriculum.identity` because the person identity is a
single owner record rather than a repeated entry.

Other conceptual entities map to entries in their domain-area array:

```text
education.* -> curriculum.education[]
research.* -> curriculum.research[]
professional_experience.* -> curriculum.professional_experience[]
achievements.* -> curriculum.achievements[]
other.* -> curriculum.other[]
```

The entry `type` should be a stable semantic identifier. It may be derived from
the conceptual entity identifier, but it must not expose generated module names.

## Attribute Mapping

`ConceptualAttribute.name` maps to a JSON field name. It should be stable,
semantic, and `snake_case`.

`ConceptualValueKind` maps as follows:

| Conceptual value kind | JSON shape |
| --- | --- |
| `text` | string |
| `date_like` | string or `FlexibleDateValue` when wrapper evidence exists |
| `duration_like` | string |
| `boolean` | boolean |
| `decimal_number` | number |
| `controlled_reference` | controlled-reference object |
| `value_object` | shared wrapper object |
| `unknown` | permissive value plus limitation trace |

`ConceptualCardinalityKind.REPEATED` maps to arrays.

`ConceptualPresenceKind.REQUIRED` should be enforced by schema and parser
profiles when the requirement is reliable. Optional and unknown presence allow the
field to be omitted.

## Controlled Reference Mapping

`ConceptualVocabularyKind.ENUMERATION` with eligible enum evidence may validate
`code` as a closed enum.

Other vocabulary kinds remain open:

- `code_list`
- `registry`
- `thesaurus`
- `hierarchical_code_list`
- `subtype_backed_code_list`
- `unresolved_reference`
- `under_traced_reference`

Canonical controlled-reference fields are:

- `code`
- `label`
- `source`
- `raw_value`
- `uri`
- `reference_status`

Representative mappings:

- `CVN_SEX_A` maps to an enum-backed controlled reference
- `CVN_ENTITY_TYPE` maps to an open controlled reference
- `UNESCO_CODES` maps to a hierarchical code-list controlled reference
- `THESAURUS@thesaurus.xsd` maps to a thesaurus controlled reference
- `ENTITY@Entity.xsd` maps to a registry controlled reference
- `CVN_AGENCY_C` maps to an unresolved controlled reference

## Trace Mapping

Issue `#45` schema extensions map to runtime trace fields as follows:

| JSON Schema annotation | Runtime trace field |
| --- | --- |
| `x-open-cvn-code` | `cvn_codes[]` |
| `x-open-cvn-xml-paths` | `xml_paths[]` |
| `x-open-cvn-source-reference` | `manual_reference_table` or `source_artifacts[]` |
| `x-open-cvn-domain-shape-kind` | `domain_shape_kind` |
| `x-open-cvn-confidence` | `confidence` |
| `x-open-cvn-vocabulary-kind` | controlled-reference `source` and trace evidence |

Trace can be omitted from hand-authored documents, but importers should preserve
it when source evidence exists.

## Exclusions

The canonical JSON format must not expose these as document structure:

- generated Python module names such as `cvn_item_050_020_010_000`
- generated Pydantic class names as required runtime type names
- raw XML wrapper mechanics unless represented as shared value objects
- one JSON object per CVN code when a stable conceptual entry exists

CVN codes remain trace metadata, not the primary JSON shape.
