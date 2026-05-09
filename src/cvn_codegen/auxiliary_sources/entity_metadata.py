from dataclasses import dataclass
from pathlib import Path
from xsdata_pydantic.bindings import XmlParser
from generated.entity.entity_v1_4 import Entity
@dataclass(frozen=True)
class EntityCatalogMetadata:
    """Store normalization-grade metadata for the canonical entity registry."""
    source_artifact: str
    item_count: int
    languages: tuple[str, ...]
    has_delegate: bool
    is_registry: bool
    item_ids: frozenset[str]
def load_entity_xml(entity_path: Path) -> Entity:
    """Load and parse the canonical ``Entity.xml`` file.
    Args:
        entity_path (Path): Path to the canonical ``Entity.xml`` file.
    Returns:
        Entity: Parsed entity root object.
    Raises:
        ValueError: If ``entity_path`` is not a ``Path``.
        FileNotFoundError: If the target XML file does not exist.
    """
    if not isinstance(entity_path, Path):
        raise ValueError(
            f"entity_path must be a Path object, got {type(entity_path)} instead."
        )
    if not entity_path.is_file():
        raise FileNotFoundError(f"Entity file not found at path: {entity_path}")
    xml_parser = XmlParser()
    entity = xml_parser.from_path(entity_path, Entity)
    return entity
def extract_entity_languages(entity: Entity) -> tuple[str, ...]:
    """Extract the sorted set of language codes observed in entity descriptions.
    Args:
        entity (Entity): Parsed entity root object.
    Returns:
        tuple[str, ...]: Sorted tuple of observed language codes.
    """
    languages: set[str] = set()
    for item in entity.item:
        for description in item.item_description:
            if description.lang is None:
                continue
            language_code = getattr(description.lang, "value", description.lang)
            if language_code is None:
                continue
            normalized_language_code = str(language_code).strip()
            if normalized_language_code:
                languages.add(normalized_language_code)
    return tuple(sorted(languages))
def load_entity_catalog_metadata(entity_path: Path) -> EntityCatalogMetadata:
    """Load normalization-grade metadata for the canonical entity registry.
    Args:
        entity_path (Path): Path to the canonical ``Entity.xml`` file.
    Returns:
        EntityCatalogMetadata: Reduced metadata view used by the normalization
        resolution layer.
    """
    entity = load_entity_xml(entity_path)
    item_ids = frozenset(
        str(item.item_id).strip()
        for item in entity.item
        if str(item.item_id).strip()
    )
    has_delegate = any(item.delegate is not None for item in entity.item)
    return EntityCatalogMetadata(
        source_artifact=entity_path.name,
        item_count=len(entity.item),
        languages=extract_entity_languages(entity),
        has_delegate=has_delegate,
        is_registry=True,
        item_ids=item_ids,
    )