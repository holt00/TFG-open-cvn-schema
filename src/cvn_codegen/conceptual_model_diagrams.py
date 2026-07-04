import argparse
import logging
from dataclasses import dataclass
from pathlib import Path

from cvn_codegen.conceptual_model_extractor import build_canonical_conceptual_model_inventory
from cvn_codegen.conceptual_model_types import (
    ConceptualAttribute,
    ConceptualCardinalityKind,
    ConceptualDomainArea,
    ConceptualEntity,
    ConceptualModelInventory,
    ConceptualRelationship,
    ConceptualRelationshipKind,
    ConceptualTrace,
    ConceptualVocabulary,
    ConceptualVocabularyKind,
)


logger = logging.getLogger(__name__)

DEFAULT_OUTPUT_DIR = Path("docs/diagrams")
MAX_INLINE_ENUM_VALUES = 20
READABLE_ATTRIBUTE_LIMIT = 8
LARGE_AREA_ENTITY_THRESHOLD = 10
LARGE_AREA_ATTRIBUTE_THRESHOLD = 80
LARGE_REFERENCE_VOCABULARY_PAIR_THRESHOLD = 12
LARGE_REFERENCE_SECTION_ENTITY_THRESHOLD = 6
LARGE_REFERENCE_SECTION_ATTRIBUTE_THRESHOLD = 120
OVERVIEW_SAMPLE_LIMIT = 3
DEPENDENCY_COLORS = (
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#17becf",
)


@dataclass(frozen=True)
class DiagramArtifact:
    """Represent one generated diagram source artifact."""

    filename: str
    title: str
    content: str


@dataclass(frozen=True)
class ReadableSection:
    """Represent one split readable section for a large area."""

    key: str
    title: str
    filename: str
    entities: tuple[ConceptualEntity, ...]


def render_conceptual_model_diagrams(
    inventory: ConceptualModelInventory,
) -> tuple[DiagramArtifact, ...]:
    """Render readable and reference PlantUML diagrams from a conceptual inventory."""
    artifacts = [render_overview_diagram(inventory)]
    for area in sorted(inventory.domain_areas, key=lambda item: item.area_id):
        artifacts.extend(render_readable_area_diagrams(inventory, area))
    artifacts.append(render_reference_overview_diagram(inventory))
    for area in sorted(inventory.domain_areas, key=lambda item: item.area_id):
        artifacts.extend(render_reference_area_diagrams(inventory, area))
    return tuple(artifacts)


def write_conceptual_model_diagrams(
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    *,
    inventory: ConceptualModelInventory | None = None,
) -> tuple[Path, ...]:
    """Write canonical PlantUML diagrams and return written paths."""
    resolved_inventory = inventory or build_canonical_conceptual_model_inventory()
    artifacts = render_conceptual_model_diagrams(resolved_inventory)
    output_dir.mkdir(parents=True, exist_ok=True)
    written_paths: list[Path] = []
    for artifact in artifacts:
        path = output_dir / artifact.filename
        path.write_text(artifact.content, encoding="utf-8")
        written_paths.append(path)
    return tuple(written_paths)


def render_overview_diagram(inventory: ConceptualModelInventory) -> DiagramArtifact:
    """Render human-readable conceptual overview."""
    entities_by_id = get_entities_by_id(inventory)
    lines = build_header("Open CVN Conceptual Overview")
    lines.extend(
        [
            "skinparam classAttributeIconSize 0",
            "hide empty members",
            "",
        ]
    )
    root_entities = collect_root_overview_entities(inventory)
    if root_entities:
        lines.append('package "Core Structure" as overview_core {')
        for entity in root_entities:
            lines.append(render_entity_declaration(entity, include_attributes=False, stereotype="entity"))
        lines.append("}")
        lines.append("")
    lines.append('package "Conceptual Areas" as conceptual_areas {')
    for area in sorted(inventory.domain_areas, key=lambda item: item.area_id):
        if area.area_id == "core":
            continue
        lines.extend(render_area_summary_block(area))
        lines.append("")
    lines.append("}")
    lines.append("")
    for relationship in sorted(inventory.relationships, key=lambda item: item.relationship_id):
        if relationship.source_id in entities_by_id and relationship.target_id in entities_by_id:
            if relationship.source_id == "core.curriculum" or relationship.target_id == "core.curriculum":
                lines.append(render_relationship(relationship))
    lines.append("")
    lines.extend(render_inventory_notes(inventory))
    lines.append("@enduml")
    return DiagramArtifact(
        filename="open_cvn_conceptual_overview.puml",
        title="Open CVN Conceptual Overview",
        content="\n".join(lines) + "\n",
    )


def render_readable_area_diagrams(
    inventory: ConceptualModelInventory,
    area: ConceptualDomainArea,
) -> tuple[DiagramArtifact, ...]:
    """Render readable diagrams for one area, splitting large areas into sections."""
    if not is_large_area(area):
        return (render_domain_area_diagram(inventory, area),)
    sections = build_readable_sections(area)
    artifacts = [render_large_area_index_diagram(area, sections)]
    artifacts.extend(
        render_readable_section_diagram(inventory, area, section)
        for section in sections
    )
    return tuple(artifacts)


def render_domain_area_diagram(
    inventory: ConceptualModelInventory,
    area: ConceptualDomainArea,
) -> DiagramArtifact:
    """Render one readable domain-area diagram."""
    return render_readable_entity_diagram(
        inventory,
        title=f"Open CVN - {area.name}",
        filename=f"open_cvn_{area.area_id}.puml",
        package_label=area.name,
        package_alias=area_alias(area.area_id),
        entities=tuple(sorted(area.entities, key=lambda item: item.entity_id)),
        attribute_limit=None,
    )


def render_large_area_index_diagram(
    area: ConceptualDomainArea,
    sections: tuple[ReadableSection, ...],
) -> DiagramArtifact:
    """Render compact index diagram for a large area."""
    lines = build_header(f"Open CVN - {area.name}")
    lines.extend(
        [
            "skinparam classAttributeIconSize 0",
            "hide empty members",
            "",
            f'package "{escape_text(area.name)}" as {area_alias(area.area_id)} {{',
        ]
    )
    for section in sections:
        lines.extend(render_section_summary_block(section))
        lines.append("")
    lines.append("}")
    lines.append("")
    lines.append("note bottom")
    lines.append(f"Readable index for {escape_text(area.name)}")
    lines.append("Detailed section files:")
    for section in sections:
        lines.append(f"- {escape_text(section.filename)}")
    lines.append("Reference view:")
    lines.append(f"- open_cvn_{area.area_id}_reference.puml")
    lines.append("end note")
    lines.append("@enduml")
    return DiagramArtifact(
        filename=f"open_cvn_{area.area_id}.puml",
        title=f"Open CVN - {area.name}",
        content="\n".join(lines) + "\n",
    )


def render_readable_section_diagram(
    inventory: ConceptualModelInventory,
    area: ConceptualDomainArea,
    section: ReadableSection,
) -> DiagramArtifact:
    """Render readable detail for one split section of a large area."""
    return render_readable_entity_diagram(
        inventory,
        title=f"Open CVN - {area.name} - {section.title}",
        filename=section.filename,
        package_label=f"{area.name} - {section.title}",
        package_alias=f"{area_alias(area.area_id)}_{normalize_alias(section.key)}",
        entities=section.entities,
        attribute_limit=READABLE_ATTRIBUTE_LIMIT,
    )


def render_readable_entity_diagram(
    inventory: ConceptualModelInventory,
    *,
    title: str,
    filename: str,
    package_label: str,
    package_alias: str,
    entities: tuple[ConceptualEntity, ...],
    attribute_limit: int | None,
) -> DiagramArtifact:
    """Render one readable entity-focused diagram."""
    area_entity_ids = {entity.entity_id for entity in entities}
    entities_by_id = get_entities_by_id(inventory)
    lines = build_header(title)
    lines.extend(
        [
            "skinparam classAttributeIconSize 0",
            "hide circle",
            "",
            f'package "{escape_text(package_label)}" as {package_alias} {{',
        ]
    )
    for entity in entities:
        lines.extend(render_entity_block(entity, include_trace=False, attribute_limit=attribute_limit))
        lines.append("")
    lines.append("}")
    lines.append("")
    external_entity_ids = get_external_relationship_entity_ids(inventory.relationships, area_entity_ids)
    for entity_id in external_entity_ids:
        if entity_id not in entities_by_id:
            continue
        lines.append(render_external_entity_declaration(entities_by_id[entity_id]))
    if external_entity_ids:
        lines.append("")
    for relationship in sorted(inventory.relationships, key=lambda item: item.relationship_id):
        if relationship.source_id in area_entity_ids or relationship.target_id in area_entity_ids:
            lines.append(render_relationship(relationship))
    lines.append("@enduml")
    return DiagramArtifact(
        filename=filename,
        title=title,
        content="\n".join(lines) + "\n",
    )


def render_reference_overview_diagram(inventory: ConceptualModelInventory) -> DiagramArtifact:
    """Render compact reference overview pointing to detailed reference files."""
    lines = build_header("Open CVN Conceptual Overview Reference")
    lines.extend(build_reference_layout_lines())
    lines.append('package "Reference Areas" as reference_areas {')
    for area in sorted(inventory.domain_areas, key=lambda item: item.area_id):
        lines.extend(render_reference_area_summary_block(area))
        lines.append("")
    lines.append("}")
    lines.append("")
    lines.extend(render_hidden_vertical_chain(reference_area_alias(area.area_id) for area in sorted(inventory.domain_areas, key=lambda item: item.area_id)))
    lines.append("")
    lines.extend(render_inventory_notes(inventory))
    lines.append("@enduml")
    return DiagramArtifact(
        filename="open_cvn_conceptual_overview_reference.puml",
        title="Open CVN Conceptual Overview Reference",
        content="\n".join(lines) + "\n",
    )


def render_reference_domain_area_diagram(
    inventory: ConceptualModelInventory,
    area: ConceptualDomainArea,
) -> DiagramArtifact:
    """Render full reference area diagram with vocabularies and trace notes."""
    return render_reference_entity_diagram(
        inventory,
        title=f"Open CVN - {area.name} Reference",
        filename=f"open_cvn_{area.area_id}_reference.puml",
        package_label=area.name,
        package_alias=area_alias(area.area_id),
        entities=tuple(sorted(area.entities, key=lambda item: item.entity_id)),
    )


def render_reference_area_diagrams(
    inventory: ConceptualModelInventory,
    area: ConceptualDomainArea,
) -> tuple[DiagramArtifact, ...]:
    """Render reference diagrams for one area, splitting large areas when needed."""
    if not requires_split_reference(area):
        return (render_reference_domain_area_diagram(inventory, area),)
    sections = build_reference_sections(area)
    artifacts = [render_large_area_reference_index_diagram(area, sections)]
    for section in sections:
        artifacts.append(render_reference_section_diagram(inventory, area, section))
        artifacts.extend(render_reference_subsection_diagrams(inventory, area, section))
    return tuple(artifacts)


def render_large_area_reference_index_diagram(
    area: ConceptualDomainArea,
    sections: tuple[ReadableSection, ...],
) -> DiagramArtifact:
    """Render compact index for split large-area reference diagrams."""
    lines = build_header(f"Open CVN - {area.name} Reference")
    lines.extend(
        [
            "skinparam classAttributeIconSize 0",
            "hide empty members",
            "",
            f'package "{escape_text(area.name)} Reference" as {area_alias(area.area_id)}_reference {{',
        ]
    )
    for section in sections:
        lines.extend(render_section_summary_block_reference(section))
        lines.append("")
    lines.append("}")
    lines.append("")
    lines.append("note bottom")
    lines.append(f"Reference index for {escape_text(area.name)}")
    lines.append("Detailed reference section files:")
    for section in sections:
        lines.append(f"- {escape_text(reference_filename_for_section(section))}")
    lines.append("end note")
    lines.append("@enduml")
    return DiagramArtifact(
        filename=f"open_cvn_{area.area_id}_reference.puml",
        title=f"Open CVN - {area.name} Reference",
        content="\n".join(lines) + "\n",
    )


def render_reference_section_diagram(
    inventory: ConceptualModelInventory,
    area: ConceptualDomainArea,
    section: ReadableSection,
) -> DiagramArtifact:
    """Render detailed split reference diagram for one section."""
    if requires_split_reference_section(section):
        chunks = split_reference_section(section)
        return render_reference_subsection_index_diagram(area, section, chunks)
    return render_reference_entity_diagram(
        inventory,
        title=f"Open CVN - {area.name} Reference - {section.title}",
        filename=reference_filename_for_section(section),
        package_label=f"{area.name} Reference - {section.title}",
        package_alias=f"{area_alias(area.area_id)}_{normalize_alias(section.key)}_reference",
        entities=section.entities,
    )


def render_reference_subsection_index_diagram(
    area: ConceptualDomainArea,
    section: ReadableSection,
    chunks: tuple[ReadableSection, ...],
) -> DiagramArtifact:
    """Render compact index when one reference section is still too large."""
    lines = build_header(f"Open CVN - {area.name} Reference - {section.title}")
    lines.extend(
        [
            "skinparam classAttributeIconSize 0",
            "hide empty members",
            "",
            f'package "{escape_text(area.name)} Reference - {section.title}" as {normalize_alias(section.key)}_reference_index {{',
        ]
    )
    for chunk in chunks:
        lines.extend(render_section_summary_block_reference(chunk))
        lines.append("")
    lines.append("}")
    lines.append("")
    lines.append("note bottom")
    lines.append(f"Reference subsection index for {escape_text(section.title)}")
    lines.append("Detailed subsection files:")
    for chunk in chunks:
        lines.append(f"- {escape_text(reference_filename_for_section(chunk))}")
    lines.append("end note")
    lines.append("@enduml")
    return DiagramArtifact(
        filename=reference_filename_for_section(section),
        title=f"Open CVN - {area.name} Reference - {section.title}",
        content="\n".join(lines) + "\n",
    )


def render_reference_subsection_diagrams(
    inventory: ConceptualModelInventory,
    area: ConceptualDomainArea,
    section: ReadableSection,
) -> tuple[DiagramArtifact, ...]:
    """Render deeper detailed files for one oversized reference section."""
    if not requires_split_reference_section(section):
        return ()
    chunks = split_reference_section(section)
    return tuple(
        render_reference_entity_diagram(
            inventory,
            title=f"Open CVN - {area.name} Reference - {chunk.title}",
            filename=reference_filename_for_section(chunk),
            package_label=f"{area.name} Reference - {chunk.title}",
            package_alias=f"{area_alias(area.area_id)}_{normalize_alias(chunk.key)}_reference",
            entities=chunk.entities,
        )
        for chunk in chunks
    )


def render_reference_entity_diagram(
    inventory: ConceptualModelInventory,
    *,
    title: str,
    filename: str,
    package_label: str,
    package_alias: str,
    entities: tuple[ConceptualEntity, ...],
) -> DiagramArtifact:
    """Render detailed reference diagram without side-note layout explosion."""
    area_entity_ids = {entity.entity_id for entity in entities}
    entities_by_id = get_entities_by_id(inventory)
    vocabularies_by_id = {item.vocabulary_id: item for item in inventory.vocabularies}
    lines = build_header(title)
    lines.extend(build_reference_layout_lines())
    lines.append(f'package "{escape_text(package_label)}" as {package_alias} {{')
    for entity in entities:
        lines.extend(render_entity_block(entity, include_trace=True, attribute_limit=None))
        vocabulary_note = render_entity_vocabulary_note(entity, vocabularies_by_id)
        if vocabulary_note:
            lines.extend(vocabulary_note)
        lines.append("")
    lines.append("}")
    lines.append("")
    lines.extend(render_hidden_vertical_chain(entity_alias(entity.entity_id) for entity in entities))
    if entities:
        lines.append("")
    external_entity_ids = get_external_relationship_entity_ids(inventory.relationships, area_entity_ids)
    for entity_id in external_entity_ids:
        if entity_id not in entities_by_id:
            continue
        lines.append(render_external_entity_declaration(entities_by_id[entity_id]))
    if external_entity_ids:
        lines.append("")
    for relationship in sorted(inventory.relationships, key=lambda item: item.relationship_id):
        if relationship.source_id in area_entity_ids or relationship.target_id in area_entity_ids:
            lines.append(render_relationship(relationship))
    if inventory.relationships:
        lines.append("")
    lines.append("@enduml")
    return DiagramArtifact(
        filename=filename,
        title=title,
        content="\n".join(lines) + "\n",
    )


def build_entity_vocabulary_pairs(
    entities: tuple[ConceptualEntity, ...],
) -> tuple[tuple[str, str], ...]:
    """Return unique entity-vocabulary pairs for compact reference edges."""
    pairs = {
        (entity.entity_id, attribute.vocabulary_id)
        for entity in entities
        for attribute in entity.attributes
        if attribute.vocabulary_id is not None
    }
    return tuple(sorted(pairs))


def render_entity_vocabulary_note(
    entity: ConceptualEntity,
    vocabularies_by_id: dict[str, ConceptualVocabulary],
) -> list[str]:
    """Render local vocabulary trace for one entity without long cross-canvas edges."""
    vocabulary_ids = tuple(
        sorted(
            {
                attribute.vocabulary_id
                for attribute in entity.attributes
                if attribute.vocabulary_id in vocabularies_by_id
            }
        )
    )
    if not vocabulary_ids:
        return []
    lines = [f"note right of {entity_alias(entity.entity_id)}", "controlled references:"]
    for vocabulary_id in vocabulary_ids:
        vocabulary = vocabularies_by_id[vocabulary_id]
        detail_parts = [
            vocabulary.kind.value,
            f"enum={vocabulary.enum_eligibility}",
        ]
        if vocabulary.item_count is not None:
            detail_parts.append(f"items={vocabulary.item_count}")
        lines.append(f"- {escape_text(vocabulary.name)} ({', '.join(detail_parts)})")
    lines.append("end note")
    return lines


def reference_filename_for_section(section: ReadableSection) -> str:
    """Return reference filename for a split readable section."""
    base_name = section.filename.removesuffix(".puml")
    return f"{base_name}_reference.puml"


def build_reference_layout_lines() -> list[str]:
    """Return shared layout directives for reference diagrams."""
    return [
        "skinparam classAttributeIconSize 0",
        "skinparam linetype ortho",
        "top to bottom direction",
        "hide empty members",
        "",
    ]


def render_hidden_vertical_chain(aliases) -> list[str]:
    """Render hidden links to encourage vertical stacking order."""
    alias_list = [alias for alias in aliases]
    lines: list[str] = []
    for source_alias, target_alias in zip(alias_list, alias_list[1:]):
        lines.append(f"{source_alias} -[hidden]down-> {target_alias}")
    return lines


def dependency_color(key: str) -> str:
    """Return deterministic color for dependency edges."""
    color_index = sum(ord(character) for character in key) % len(DEPENDENCY_COLORS)
    return DEPENDENCY_COLORS[color_index]


def reference_area_alias(area_id: str) -> str:
    """Return stable alias for reference-area summary nodes."""
    return f"reference_area_{normalize_alias(area_id)}"


def build_readable_sections(area: ConceptualDomainArea) -> tuple[ReadableSection, ...]:
    """Build deterministic readable sections for a large area."""
    grouped: dict[str, list[ConceptualEntity]] = {}
    for entity in area.entities:
        grouped.setdefault(get_section_key(entity), []).append(entity)
    sections: list[ReadableSection] = []
    for key in sorted(grouped):
        entities = tuple(sorted(grouped[key], key=lambda item: item.entity_id))
        sections.append(
            ReadableSection(
                key=key,
                title=build_section_title(area, key),
                filename=f"open_cvn_{area.area_id}_{normalize_alias(key)}.puml",
                entities=entities,
            )
        )
    return tuple(sections)


def build_reference_sections(area: ConceptualDomainArea) -> tuple[ReadableSection, ...]:
    """Build deterministic split sections for reference diagrams."""
    if area.area_id == "professional_experience":
        return tuple(
            ReadableSection(
                key=entity.source_group_key or entity.entity_id,
                title=entity.name,
                filename=f"open_cvn_{area.area_id}_{normalize_alias(entity.source_group_key or entity.entity_id)}.puml",
                entities=(entity,),
            )
            for entity in sorted(area.entities, key=lambda item: item.entity_id)
        )
    return build_readable_sections(area)


def is_large_area(area: ConceptualDomainArea) -> bool:
    """Return whether an area should be split for readable output."""
    entity_count = len(area.entities)
    attribute_count = sum(len(entity.attributes) for entity in area.entities)
    return (
        entity_count > LARGE_AREA_ENTITY_THRESHOLD
        or attribute_count > LARGE_AREA_ATTRIBUTE_THRESHOLD
    )


def requires_split_reference(area: ConceptualDomainArea) -> bool:
    """Return whether a reference area should be split for layout sanity."""
    if is_large_area(area):
        return True
    vocabulary_pair_count = len(build_entity_vocabulary_pairs(tuple(area.entities)))
    return vocabulary_pair_count > LARGE_REFERENCE_VOCABULARY_PAIR_THRESHOLD


def requires_split_reference_section(section: ReadableSection) -> bool:
    """Return whether one reference section still needs deeper splitting."""
    entity_count = len(section.entities)
    attribute_count = sum(len(entity.attributes) for entity in section.entities)
    return (
        entity_count > LARGE_REFERENCE_SECTION_ENTITY_THRESHOLD
        or attribute_count > LARGE_REFERENCE_SECTION_ATTRIBUTE_THRESHOLD
    )


def split_reference_section(section: ReadableSection) -> tuple[ReadableSection, ...]:
    """Split one oversized reference section into smaller deterministic chunks."""
    chunks: list[ReadableSection] = []
    current_entities: list[ConceptualEntity] = []
    current_attribute_count = 0
    part_number = 1
    for entity in section.entities:
        entity_attribute_count = len(entity.attributes)
        if current_entities and (
            len(current_entities) >= LARGE_REFERENCE_SECTION_ENTITY_THRESHOLD
            or current_attribute_count + entity_attribute_count > LARGE_REFERENCE_SECTION_ATTRIBUTE_THRESHOLD
        ):
            chunks.append(build_reference_chunk(section, tuple(current_entities), part_number))
            current_entities = []
            current_attribute_count = 0
            part_number += 1
        current_entities.append(entity)
        current_attribute_count += entity_attribute_count
    if current_entities:
        chunks.append(build_reference_chunk(section, tuple(current_entities), part_number))
    return tuple(chunks)


def build_reference_chunk(
    section: ReadableSection,
    entities: tuple[ConceptualEntity, ...],
    part_number: int,
) -> ReadableSection:
    """Build one chunked reference subsection descriptor."""
    chunk_key = f"{section.key}_part_{part_number:02d}"
    return ReadableSection(
        key=chunk_key,
        title=f"{section.title} Part {part_number}",
        filename=f"{section.filename.removesuffix('.puml')}_part_{part_number:02d}.puml",
        entities=entities,
    )


def collect_root_overview_entities(inventory: ConceptualModelInventory) -> tuple[ConceptualEntity, ...]:
    """Return core entities that make the overview readable."""
    entities_by_id = get_entities_by_id(inventory)
    preferred_ids = (
        "core.curriculum",
        "identity.person",
        "professional_experience.professionalsituation_010_010_000_000",
    )
    return tuple(
        entities_by_id[entity_id]
        for entity_id in preferred_ids
        if entity_id in entities_by_id
    )


def render_area_summary_block(area: ConceptualDomainArea) -> list[str]:
    """Render a compact overview summary for one conceptual area."""
    alias = f"summary_{normalize_alias(area.area_id)}"
    entity_names = ", ".join(entity.name for entity in area.entities[:OVERVIEW_SAMPLE_LIMIT])
    if len(area.entities) > OVERVIEW_SAMPLE_LIMIT:
        entity_names = f"{entity_names}, +{len(area.entities) - OVERVIEW_SAMPLE_LIMIT} more"
    return [
        f'class "{escape_text(area.name)}" as {alias} <<domain_area>> {{',
        f"  entities : {len(area.entities)}",
        f"  representative : {escape_text(entity_names)}",
        "}",
    ]


def render_reference_area_summary_block(area: ConceptualDomainArea) -> list[str]:
    """Render compact summary block for one reference area."""
    alias = reference_area_alias(area.area_id)
    entity_names = ", ".join(entity.name for entity in area.entities[:OVERVIEW_SAMPLE_LIMIT])
    if len(area.entities) > OVERVIEW_SAMPLE_LIMIT:
        entity_names = f"{entity_names}, +{len(area.entities) - OVERVIEW_SAMPLE_LIMIT} more"
    return [
        f'class "{escape_text(area.name)}" as {alias} <<reference_area>> {{',
        f"  entities : {len(area.entities)}",
        f"  file : open_cvn_{area.area_id}_reference.puml",
        f"  representative : {escape_text(entity_names)}",
        "}",
    ]


def render_section_summary_block(section: ReadableSection) -> list[str]:
    """Render a compact block for one readable split section."""
    alias = f"section_{normalize_alias(section.key)}"
    sample_names = ", ".join(entity.name for entity in section.entities[:OVERVIEW_SAMPLE_LIMIT])
    if len(section.entities) > OVERVIEW_SAMPLE_LIMIT:
        sample_names = f"{sample_names}, +{len(section.entities) - OVERVIEW_SAMPLE_LIMIT} more"
    return [
        f'class "{escape_text(section.title)}" as {alias} <<section>> {{',
        f"  entities : {len(section.entities)}",
        f"  file : {escape_text(section.filename)}",
        f"  representative : {escape_text(sample_names)}",
        "}",
    ]


def render_section_summary_block_reference(section: ReadableSection) -> list[str]:
    """Render compact block for one split reference section."""
    alias = f"reference_section_{normalize_alias(section.key)}"
    sample_names = ", ".join(entity.name for entity in section.entities[:OVERVIEW_SAMPLE_LIMIT])
    if len(section.entities) > OVERVIEW_SAMPLE_LIMIT:
        sample_names = f"{sample_names}, +{len(section.entities) - OVERVIEW_SAMPLE_LIMIT} more"
    return [
        f'class "{escape_text(section.title)}" as {alias} <<reference_section>> {{',
        f"  entities : {len(section.entities)}",
        f"  file : {escape_text(reference_filename_for_section(section))}",
        f"  representative : {escape_text(sample_names)}",
        "}",
    ]


def get_section_key(entity: ConceptualEntity) -> str:
    """Return deterministic split key for a readable large-area section."""
    if entity.source_group_key is None:
        return "core"
    if entity.source_group_key.startswith("__"):
        return "no_tree"
    return entity.source_group_key.split(".", 1)[0]


def build_section_title(area: ConceptualDomainArea, key: str) -> str:
    """Return readable title for one large-area section."""
    if key == "core":
        return "Core"
    if key == "no_tree":
        return "Fallback Concepts"
    return f"Section {key}"


def build_header(title: str) -> list[str]:
    """Return standard deterministic PlantUML header lines."""
    return [
        "@startuml",
        f"title {escape_text(title)}",
        "",
    ]


def render_entity_declaration(
    entity: ConceptualEntity,
    *,
    include_attributes: bool,
    stereotype: str,
) -> str:
    """Render a PlantUML class declaration for one conceptual entity."""
    alias = entity_alias(entity.entity_id)
    name = escape_text(entity.name)
    if not include_attributes:
        return f'class "{name}" as {alias} <<{stereotype}>>'
    return f'class "{name}" as {alias} <<{stereotype}>> {{'


def render_external_entity_declaration(entity: ConceptualEntity) -> str:
    """Render a lightweight declaration for a related entity outside the area."""
    return render_entity_declaration(entity, include_attributes=False, stereotype="external")


def render_entity_block(
    entity: ConceptualEntity,
    *,
    include_trace: bool,
    attribute_limit: int | None,
) -> list[str]:
    """Render a class block for readable or reference views."""
    lines = [render_entity_declaration(entity, include_attributes=True, stereotype="entity")]
    attributes = tuple(sorted(entity.attributes, key=lambda item: item.attribute_id))
    visible_attributes = attributes if attribute_limit is None else attributes[:attribute_limit]
    for attribute in visible_attributes:
        lines.append(
            f"  {render_attribute(attribute, include_trace=include_trace)}"
        )
    hidden_count = len(attributes) - len(visible_attributes)
    if hidden_count > 0:
        lines.append(f"  .. +{hidden_count} more attributes ..")
    lines.append("}")
    return lines


def render_attribute(attribute: ConceptualAttribute, *, include_trace: bool) -> str:
    """Render one conceptual attribute for a class member line."""
    markers = ", ".join((attribute.presence.value, attribute.cardinality.value))
    type_label = attribute.value_kind.value
    if attribute.wrapper_type_names:
        wrappers = ",".join(sorted(attribute.wrapper_type_names))
        type_label = f"{type_label}<{wrappers}>"
    cvn_suffix = ""
    if include_trace:
        cvn_codes = format_sample(attribute.trace.cvn_codes, limit=2)
        cvn_suffix = f" [CVN: {cvn_codes}]" if cvn_codes else ""
    return f"{escape_text(attribute.name)} : {escape_text(type_label)} <<{markers}>>{cvn_suffix}"


def render_relationship(relationship: ConceptualRelationship) -> str:
    """Render one conceptual relationship with cardinality labels."""
    arrow = {
        ConceptualRelationshipKind.COMPOSITION: "*--",
        ConceptualRelationshipKind.AGGREGATION: "o--",
        ConceptualRelationshipKind.ASSOCIATION: "--",
        ConceptualRelationshipKind.VOCABULARY_REFERENCE: "..>",
    }[relationship.kind]
    label = f" : {escape_text(relationship.label)}" if relationship.label else ""
    return (
        f'{entity_alias(relationship.source_id)} "{cardinality_label(relationship.source_cardinality)}" '
        f'{arrow} "{cardinality_label(relationship.target_cardinality)}" '
        f"{entity_alias(relationship.target_id)}{label}"
    )


def render_vocabulary_reference(entity: ConceptualEntity, attribute: ConceptualAttribute) -> str:
    """Render a dependency from an entity to an attribute vocabulary."""
    return (
        f"{entity_alias(entity.entity_id)} ..> {vocabulary_alias(attribute.vocabulary_id or '')} "
        f': {escape_text(attribute.name)}'
    )


def render_vocabulary_block(vocabulary: ConceptualVocabulary) -> list[str]:
    """Render a vocabulary as an enum or stereotyped class."""
    alias = vocabulary_alias(vocabulary.vocabulary_id)
    name = escape_text(vocabulary.name)
    stereotype = vocabulary_stereotype(vocabulary.kind)
    if vocabulary.kind == ConceptualVocabularyKind.ENUMERATION and 0 < len(vocabulary.values) <= MAX_INLINE_ENUM_VALUES:
        lines = [f'enum "{name}" as {alias} <<{stereotype}>> {{']
        for code, label in sorted(vocabulary.values, key=lambda item: item[0]):
            lines.append(f"  {escape_text(code)} : {escape_text(label)}")
        lines.append("}")
        return lines
    return [
        f'class "{name}" as {alias} <<{stereotype}>> {{',
        f"  source : {escape_text(vocabulary.source_reference)}",
        f"  kind : {vocabulary.kind.value}",
        f"  enumEligibility : {escape_text(vocabulary.enum_eligibility)}",
        *render_vocabulary_trace_fields(vocabulary),
        "}",
    ]


def render_vocabulary_trace_fields(vocabulary: ConceptualVocabulary) -> list[str]:
    """Render compact vocabulary trace fields inside class body."""
    lines: list[str] = []
    if vocabulary.item_count is not None:
        lines.append(f"  items : {vocabulary.item_count}")
    if vocabulary.trace.manual_reference_table:
        lines.append(f"  manualReference : {escape_text(vocabulary.trace.manual_reference_table)}")
    if vocabulary.trace.reference_source_artifact:
        lines.append(f"  artifact : {escape_text(vocabulary.trace.reference_source_artifact)}")
    if vocabulary.trace.semantic_reference_kind:
        lines.append(f"  semanticReference : {escape_text(vocabulary.trace.semantic_reference_kind)}")
    return lines


def render_inventory_notes(inventory: ConceptualModelInventory) -> list[str]:
    """Render overview metadata and limitations as notes."""
    lines = [
        "note bottom",
        f"Inventory: {escape_text(inventory.inventory_id)}",
        f"Source issue: {escape_text(inventory.source_issue)}",
        f"Policy: {escape_text(inventory.policy_name)} {escape_text(inventory.policy_version)}",
    ]
    if inventory.limitations:
        lines.append("Limitations:")
        for limitation in sorted(inventory.limitations, key=lambda item: item.limitation_id):
            lines.append(f"- {escape_text(limitation.message)}")
    lines.append("end note")
    return lines


def render_entity_note(entity: ConceptualEntity) -> list[str]:
    """Render concise trace note for one entity."""
    lines = [f"note right of {entity_alias(entity.entity_id)}"]
    lines.append(f"id: {escape_text(entity.entity_id)}")
    if entity.source_group_key and not entity.source_group_key.startswith("__"):
        lines.append(f"source group: {escape_text(entity.source_group_key)}")
    lines.extend(render_trace_lines(entity.trace))
    lines.append("end note")
    lines.append("")
    return lines


def render_vocabulary_note(vocabulary: ConceptualVocabulary) -> list[str]:
    """Render concise trace note for one vocabulary."""
    lines = [f"note right of {vocabulary_alias(vocabulary.vocabulary_id)}"]
    lines.append(f"id: {escape_text(vocabulary.vocabulary_id)}")
    if vocabulary.item_count is not None:
        lines.append(f"items: {vocabulary.item_count}")
    lines.extend(render_trace_lines(vocabulary.trace))
    lines.append("end note")
    lines.append("")
    return lines


def render_trace_lines(trace: ConceptualTrace) -> list[str]:
    """Render compact trace evidence lines."""
    lines: list[str] = []
    cvn_codes = format_sample(trace.cvn_codes, limit=5)
    if cvn_codes:
        lines.append(f"cvn: {escape_text(cvn_codes)}")
    if trace.manual_reference_table:
        lines.append(f"manual reference: {escape_text(trace.manual_reference_table)}")
    if trace.reference_source_artifact:
        lines.append(f"reference artifact: {escape_text(trace.reference_source_artifact)}")
    if trace.semantic_reference_kind:
        lines.append(f"semantic reference: {escape_text(trace.semantic_reference_kind)}")
    return lines


def get_entities_by_id(inventory: ConceptualModelInventory) -> dict[str, ConceptualEntity]:
    """Return conceptual entities indexed by stable ID."""
    return {
        entity.entity_id: entity
        for area in inventory.domain_areas
        for entity in area.entities
    }


def get_external_relationship_entity_ids(
    relationships: tuple[ConceptualRelationship, ...],
    area_entity_ids: set[str],
) -> tuple[str, ...]:
    """Return related entity IDs outside the current area."""
    external_ids: set[str] = set()
    for relationship in relationships:
        source_in_area = relationship.source_id in area_entity_ids
        target_in_area = relationship.target_id in area_entity_ids
        if source_in_area and not target_in_area:
            external_ids.add(relationship.target_id)
        if target_in_area and not source_in_area:
            external_ids.add(relationship.source_id)
    return tuple(sorted(external_ids))


def cardinality_label(cardinality: ConceptualCardinalityKind) -> str:
    """Return UML multiplicity label for conceptual cardinality."""
    if cardinality == ConceptualCardinalityKind.REPEATED:
        return "0..*"
    if cardinality == ConceptualCardinalityKind.SINGLE:
        return "1"
    return "?"


def vocabulary_stereotype(kind: ConceptualVocabularyKind) -> str:
    """Return PlantUML stereotype for conceptual vocabulary kind."""
    return {
        ConceptualVocabularyKind.ENUMERATION: "enumeration",
        ConceptualVocabularyKind.CODE_LIST: "code_list",
        ConceptualVocabularyKind.REGISTRY: "registry",
        ConceptualVocabularyKind.THESAURUS: "thesaurus",
        ConceptualVocabularyKind.HIERARCHICAL_CODE_LIST: "hierarchical_code_list",
        ConceptualVocabularyKind.SUBTYPE_BACKED_CODE_LIST: "subtype_backed_code_list",
        ConceptualVocabularyKind.UNRESOLVED_REFERENCE: "unresolved_reference",
        ConceptualVocabularyKind.UNDER_TRACED_REFERENCE: "under_traced_reference",
        ConceptualVocabularyKind.NONE: "vocabulary",
    }[kind]


def entity_alias(entity_id: str) -> str:
    """Return stable PlantUML alias for an entity ID."""
    return f"entity_{normalize_alias(entity_id)}"


def vocabulary_alias(vocabulary_id: str) -> str:
    """Return stable PlantUML alias for a vocabulary ID."""
    return f"vocabulary_{normalize_alias(vocabulary_id)}"


def area_alias(area_id: str) -> str:
    """Return stable PlantUML alias for a package/domain area."""
    return f"area_{normalize_alias(area_id)}"


def normalize_alias(value: str) -> str:
    """Normalize arbitrary stable IDs into PlantUML-safe aliases."""
    normalized = "".join(character if character.isalnum() else "_" for character in value.lower())
    normalized = "_".join(part for part in normalized.split("_") if part)
    return normalized or "unnamed"


def format_sample(values: tuple[str, ...], *, limit: int) -> str:
    """Return a deterministic compact sample from a tuple of values."""
    sorted_values = tuple(sorted(values))
    if not sorted_values:
        return ""
    sample = sorted_values[:limit]
    suffix = f", +{len(sorted_values) - limit} more" if len(sorted_values) > limit else ""
    return ", ".join(sample) + suffix


def escape_text(value: str | None) -> str:
    """Escape minimal text for deterministic PlantUML source output."""
    if value is None:
        return ""
    return value.replace("\\", "\\\\").replace('"', "'")


def build_arg_parser() -> argparse.ArgumentParser:
    """Build CLI parser for canonical diagram generation."""
    parser = argparse.ArgumentParser(description="Generate Open CVN conceptual PlantUML diagrams.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory where PlantUML files will be written.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run canonical conceptual diagram generation."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    args = build_arg_parser().parse_args(argv)
    written_paths = write_conceptual_model_diagrams(args.output_dir)
    for path in written_paths:
        logger.info("wrote PlantUML diagram %s", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
