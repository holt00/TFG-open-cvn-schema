from dataclasses import dataclass
from pathlib import Path
from xsdata_pydantic.bindings import XmlParser
from generated.subtypes.subtypes import Cvnsubtype, NameType

@dataclass(frozen=True)
class SubtypeMetadata:
    """Store normalization-grade metadata for one subtype-backed source code."""
    source_code: str
    preferred_name: str | None
    code_subtype1: str
    code_subtype2: str | None
    has_second_level: bool
def load_subtypes_xml(subtypes_path: Path) -> Cvnsubtype:
    """Load and parse the canonical ``Subtype_Spa.xml`` file.
    Args:
        subtypes_path (Path): Path to the canonical ``Subtype_Spa.xml`` file.
    Returns:
        Cvnsubtype: Parsed subtype root object.
    Raises:
        ValueError: If ``subtypes_path`` is not a ``Path``.
        FileNotFoundError: If the target XML file does not exist.
    """
    if not isinstance(subtypes_path, Path):
        raise ValueError(
            f"subtypes_path must be a Path object, got {type(subtypes_path)} instead."
        )
    if not subtypes_path.is_file():
        raise FileNotFoundError(
            f"Subtype file not found at path: {subtypes_path}"
        )
    xml_parser = XmlParser()
    subtypes = xml_parser.from_path(subtypes_path, Cvnsubtype)
    return subtypes
def _select_preferred_name(
    name_details: list[NameType.NameDetail],
    preferred_language: str = "spa",
) -> str | None:
    """Select the preferred localized subtype name.
    Args:
        name_details (list[NameType.NameDetail]): Available
            localized name entries for one subtype item.
        preferred_language (str): Preferred ISO 639 language code to select.
            Defaults to ``"spa"``.
    Returns:
        str | None: Preferred localized name, first available name, or ``None``
        when no name details are present.
    """
    if not name_details:
        return None
    for detail in name_details:
        if getattr(detail.lang, "value", detail.lang) == preferred_language:
            return detail.name
    return name_details[0].name
def build_subtype_metadata(
    item: Cvnsubtype.Subtype.Item,
) -> SubtypeMetadata:
    """Build normalization-grade metadata for one subtype item.
    Args:
        item (Cvnsubtype.Subtype.Item): Parsed subtype item from the structural
            binding.
    Returns:
        SubtypeMetadata: Reduced metadata view used by the normalization
        resolution layer.
    Raises:
        ValueError: If the source code is empty after normalization.
    """
    source_code = str(item.code).strip()
    if not source_code:
        raise ValueError("Subtype source code is empty or whitespace.")
    code_subtype1 = item.code_subtype1.strip()
    if not code_subtype1:
        raise ValueError(
            f"Subtype item '{source_code}' has an empty CodeSubtype1 value."
        )
    code_subtype2 = None
    if item.code_subtype2 is not None:
        stripped_code_subtype2 = item.code_subtype2.strip()
        if stripped_code_subtype2:
            code_subtype2 = stripped_code_subtype2
    preferred_name = _select_preferred_name(item.name.name_detail)
    return SubtypeMetadata(
        source_code=source_code,
        preferred_name=preferred_name,
        code_subtype1=code_subtype1,
        code_subtype2=code_subtype2,
        has_second_level=code_subtype2 is not None,
    )
def load_subtypes_metadata(
    subtypes_path: Path,
) -> dict[str, SubtypeMetadata]:
    """Load and index normalization-grade metadata for all subtype items.
    Args:
        subtypes_path (Path): Path to the canonical ``Subtype_Spa.xml`` file.
    Returns:
        dict[str, SubtypeMetadata]: Subtype metadata indexed by source code.
    Raises:
        ValueError: If duplicate subtype source codes are found in the canonical
            source.
    """
    subtypes = load_subtypes_xml(subtypes_path)
    metadata_by_source_code: dict[str, SubtypeMetadata] = {}
    for item in subtypes.subtype.item:
        metadata = build_subtype_metadata(item)
        if metadata.source_code in metadata_by_source_code:
            raise ValueError(
                f"Duplicate subtype source code '{metadata.source_code}' found in Subtype_Spa.xml."
            )
        metadata_by_source_code[metadata.source_code] = metadata
    return metadata_by_source_code