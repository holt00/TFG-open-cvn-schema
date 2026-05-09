from dataclasses import dataclass
from pathlib import Path

from xsdata_pydantic.bindings import XmlParser

from generated.thesaurus.thesaurus import Thesaurus
@dataclass(frozen=True)
class ThesaurusCatalogMetadata:
    """Store normalization-grade metadata for the canonical thesaurus."""
    source_artifact: str
    item_count: int
    languages: tuple[str, ...]
    has_hierarchy: bool
    root_item_count: int | None
    is_vocabulary: bool
def load_thesaurus_xml(thesaurus_path: Path) -> Thesaurus:
    """Load and parse the canonical ``Thesaurus.xml`` file.
    Args:
        thesaurus_path (Path): Path to the canonical ``Thesaurus.xml`` file.
    Returns:
        Thesaurus: Parsed thesaurus root object.
    Raises:
        ValueError: If ``thesaurus_path`` is not a ``Path``.
        FileNotFoundError: If the target XML file does not exist.
    """
    if not isinstance(thesaurus_path, Path):
        raise ValueError(
            f"thesaurus_path must be a Path object, got {type(thesaurus_path)} instead."
        )
    if not thesaurus_path.is_file():
        raise FileNotFoundError(
            f"Thesaurus file not found at path: {thesaurus_path}"
        )
    xml_parser = XmlParser()
    thesaurus = xml_parser.from_path(thesaurus_path, Thesaurus)
    return thesaurus
def extract_thesaurus_languages(thesaurus: Thesaurus) -> tuple[str, ...]:
    """Extract the sorted set of language codes observed in thesaurus labels.
    Args:
        thesaurus (Thesaurus): Parsed thesaurus root object.
    Returns:
        tuple[str, ...]: Sorted tuple of observed language codes.
    """
    languages: set[str] = set()
    for item in thesaurus.item:
        for description in item.item_description:
            for detail in description.name_detail:
                language_code = getattr(detail.lang, "value", detail.lang)
                if language_code is None:
                    continue
                normalized_language_code = str(language_code).strip()
                if normalized_language_code:
                    languages.add(normalized_language_code)
    return tuple(sorted(languages))
def _count_root_items(thesaurus: Thesaurus) -> int:
    """Count thesaurus items without a parent identifier."""
    return sum(
        1
        for item in thesaurus.item
        if item.item_ancestor_id is None or not str(item.item_ancestor_id).strip()
    )
def load_thesaurus_catalog_metadata(
    thesaurus_path: Path,
) -> ThesaurusCatalogMetadata:
    """Load normalization-grade metadata for the canonical thesaurus.
    Args:
        thesaurus_path (Path): Path to the canonical ``Thesaurus.xml`` file.
    Returns:
        ThesaurusCatalogMetadata: Reduced metadata view used by the
        normalization resolution layer.
    """
    thesaurus = load_thesaurus_xml(thesaurus_path)
    has_hierarchy = any(
        item.item_ancestor_id is not None and str(item.item_ancestor_id).strip()
        for item in thesaurus.item
    )
    return ThesaurusCatalogMetadata(
        source_artifact=thesaurus_path.name,
        item_count=len(thesaurus.item),
        languages=extract_thesaurus_languages(thesaurus),
        has_hierarchy=has_hierarchy,
        root_item_count=_count_root_items(thesaurus),
        is_vocabulary=True,
    )
