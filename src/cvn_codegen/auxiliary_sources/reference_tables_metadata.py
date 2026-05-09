from dataclasses import dataclass
from pathlib import Path
from xsdata_pydantic.bindings import XmlParser
from generated.reference_tables.reference_tables import ReferenceTables
@dataclass(frozen=True)
class ReferenceTableMetadata:
    """Store normalization-grade metadata for one reference table."""
    table_name: str
    version: str | None
    ancestor_table: str | None
    source: str | None
    xml_data_type: str | None
    xml_property: str | None
    xml_indicator: str | None
    item_count: int
    has_hierarchy: bool
    has_delegate: bool
def load_reference_tables_xml(reference_tables_path: Path) -> ReferenceTables:
    """Load and parse the canonical ``ReferenceTables.xml`` file.
    Args:
        reference_tables_path (Path): Path to the canonical
            ``ReferenceTables.xml`` file.
    Returns:
        ReferenceTables: Parsed reference-tables root object.
    Raises:
        ValueError: If ``reference_tables_path`` is not a ``Path``.
        FileNotFoundError: If the target XML file does not exist.
    """
    if not isinstance(reference_tables_path, Path):
        raise ValueError(
            f"reference_tables_path must be a Path object, got {type(reference_tables_path)} instead."
        )
    if not reference_tables_path.is_file():
        raise FileNotFoundError(
            f"Reference tables file not found at path: {reference_tables_path}"
        )
    xml_parser = XmlParser()
    reference_tables = xml_parser.from_path(reference_tables_path, ReferenceTables)
    return reference_tables
def build_reference_table_metadata(
    table: ReferenceTables.Table,
) -> ReferenceTableMetadata:
    """Build normalization-grade metadata for one reference table.
    Args:
        table (ReferenceTables.Table): Parsed reference-table entry from the
            structural binding.
    Returns:
        ReferenceTableMetadata: Reduced metadata view used by the normalization
        resolution layer.
    Raises:
        ValueError: If the table name is empty after normalization.
    """
    table_name = str(table.name).strip()
    if not table_name:
        raise ValueError("Reference table name is empty or whitespace.")
    # Hierarchy and delegation matter later for semantic-kind classification.
    has_hierarchy = any(item.antecesor_code is not None for item in table.item)
    has_delegate = any(item.delegate is not None for item in table.item)
    return ReferenceTableMetadata(
        table_name=table_name,
        version=None if table.version is None else str(table.version).strip(),
        ancestor_table=(
            None
            if table.antecesor_table is None
            else str(table.antecesor_table).strip()
        ),
        source=None if table.source is None else str(table.source).strip(),
        xml_data_type=(
            None if table.xmldata_type is None else str(table.xmldata_type).strip()
        ),
        xml_property=(
            None if table.xmlproperty is None else str(table.xmlproperty).strip()
        ),
        xml_indicator=(
            None if table.xmlindicator is None else str(table.xmlindicator).strip()
        ),
        item_count=len(table.item),
        has_hierarchy=has_hierarchy,
        has_delegate=has_delegate,
    )
def load_reference_tables_metadata(
    reference_tables_path: Path,
) -> dict[str, ReferenceTableMetadata]:
    """Load and index normalization-grade metadata for all reference tables.
    Args:
        reference_tables_path (Path): Path to the canonical
            ``ReferenceTables.xml`` file.
    Returns:
        dict[str, ReferenceTableMetadata]: Reference-table metadata indexed by
        table name.
    Raises:
        ValueError: If duplicate table names are found in the canonical source.
    """
    reference_tables = load_reference_tables_xml(reference_tables_path)
    metadata_by_name: dict[str, ReferenceTableMetadata] = {}
    for table in reference_tables.table:
        metadata = build_reference_table_metadata(table)
        if metadata.table_name in metadata_by_name:
            raise ValueError(
                f"Duplicate reference table name '{metadata.table_name}' found in ReferenceTables.xml."
            )
        metadata_by_name[metadata.table_name] = metadata
    return metadata_by_name