# Open CVN Conceptual Diagrams

## Purpose

This directory contains canonical PlantUML source diagrams generated from the
issue `#43` `ConceptualModelInventory`.

The diagrams are issue `#44` documentation artifacts. They explain the agnostic
curriculum model without treating generated Python classes, raw XML paths, or XSD
structures as the final domain model.

## Canonical Sources

The versioned `.puml` files are the canonical diagram artifacts. They now exist
in two complementary styles:

- readable views:
  - `open_cvn_conceptual_overview.puml`: compact overview for humans
  - `open_cvn_core.puml`
  - `open_cvn_identity.puml`
  - `open_cvn_professional_experience.puml`
  - `open_cvn_achievements.puml`
  - `open_cvn_education.puml`: index view for split education sections
  - `open_cvn_education_020.puml`
  - `open_cvn_education_030.puml`
  - `open_cvn_research.puml`: index view for split research sections
  - `open_cvn_research_050.puml`
  - `open_cvn_research_060.puml`
  - `open_cvn_other.puml`: index view for split fallback sections
  - `open_cvn_other_040.puml`
  - `open_cvn_other_no_tree.puml`
- reference views:
  - `open_cvn_conceptual_overview_reference.puml`
  - `open_cvn_core_reference.puml`
  - `open_cvn_identity_reference.puml`
  - `open_cvn_professional_experience_reference.puml`
  - `open_cvn_professional_experience_010_010_000_000_reference.puml`
  - `open_cvn_professional_experience_010_020_000_000_reference.puml`
  - `open_cvn_professional_experience_010_040_000_000_reference.puml`
  - `open_cvn_education_reference.puml`
  - `open_cvn_education_020_reference.puml`
  - `open_cvn_education_030_reference.puml`
  - `open_cvn_research_reference.puml`
  - `open_cvn_research_050_reference.puml`
  - `open_cvn_research_060_reference.puml`
  - `open_cvn_achievements_reference.puml`
  - `open_cvn_other_reference.puml`
  - `open_cvn_other_040_reference.puml`
  - `open_cvn_other_no_tree_reference.puml`

Readable views prioritize navigation and presentation. Reference views preserve
the fuller vocabulary and attribute inventory needed for detailed inspection,
but large or vocabulary-heavy reference areas now use compact index diagrams that
point to split detailed reference section files.

For the largest reference sections, the section-level reference diagram may also
be an index instead of a full-detail canvas. In those cases, open the listed
`..._part_XX_reference.puml` or rendered PNG files to inspect the actual detailed
content.

Rendered images are optional review artifacts. The `.puml` sources remain the
canonical versioned output.

## Regeneration

Run the canonical generator from the repository root:

```bash
uv run python -m cvn_codegen.conceptual_model_diagrams --output-dir docs/diagrams
```

The generator rebuilds the canonical conceptual inventory from the repository
source package and writes deterministic PlantUML text files for both readable and
reference views.

If local PNG review is needed and PlantUML is installed, render images with:

```bash
plantuml -tpng docs/diagrams/*.puml
```

## Navigation Order

For large reference outputs, use this drill-down order:

1. open the area reference index, for example `open_cvn_research_reference.puml`
2. open the section reference index it lists, for example
   `open_cvn_research_060_reference.puml`
3. open one of the detailed chunk files listed there, for example
   `open_cvn_research_060_part_01_reference.puml`

This avoids unreadable or cut-off single-canvas diagrams while preserving the
full reference detail in deterministic files.

Reference diagrams also use top-to-bottom stacking and local `controlled
references` notes next to each entity. This avoids long cross-canvas
entity-to-vocabulary edges that can look detached or push targets outside the
rendered PNG frame.

Detailed reference chunks do not render a global `Referenced Vocabularies` package.
Vocabulary membership is kept beside the owning entity instead, which makes large
education and research PNGs reviewable without dangling-looking dependency lines.

## Review Checklist

When reviewing regenerated diagrams, check:

- overview diagram remains readable as a package-level map
- detailed diagrams are grouped by conceptual domain area or split section, not
  Python modules
- class names are conceptual names, not `cvn_item_*` generated module names
- Pydantic implementation details such as `BaseCvnDomainModel`, `model_config`,
  and `Field(...)` do not appear
- readable views avoid large vocabulary fan-out and keep big areas split into
  smaller subdiagrams
- reference views keep fuller vocabulary and trace detail for auditability
- detailed reference chunks use local `controlled references` notes rather than
  global vocabulary nodes
- representative attributes preserve CVN code trace
- diagram notes preserve source reference evidence where useful

## Known Scope Limits

Relationships remain conservative because issue `#43` deliberately avoids
inventing a complete CVN ontology from generated field annotations alone. Large
domain areas, especially research, are expected to be verbose because they expose
many CVN-backed conceptual attributes.
