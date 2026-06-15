from dataclasses import dataclass
from pathlib import Path
import re
import unicodedata

from xsdata_pydantic.bindings import XmlParser
from generated.reference_tables.reference_tables import ReferenceTables, ItemType

OTHER_LIKE_LABEL_TOKENS = frozenset(
    {
        "OTRO",
        "OTRA",
        "OTROS",
        "OTRAS",
        "OTHER",
        "OTHERS",
        "RESTO",
        "NO CONSTA",
        "SIN ESPECIFICAR",
    }
)

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
    item_codes: tuple[str, ...]
    preferred_labels: tuple[str, ...]
    normalized_codes: tuple[str, ...]
    normalized_preferred_labels: tuple[str, ...]
    has_blank_code: bool
    has_blank_preferred_label: bool
    has_duplicate_codes: bool
    has_duplicate_preferred_labels: bool
    has_other_like_entry: bool
    open_world_signals: tuple[str, ...]
    

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
    item_codes = tuple(str(item.code) for item in table.item)
    preferred_labels = tuple(_select_preferred_label(item) for item in table.item)
    normalized_codes = tuple(_normalize_code(code) for code in item_codes)
    normalized_preferred_labels = tuple(
        _normalize_label_for_signal_detection(label)
        for label in preferred_labels
    )
    has_blank_code = any(not code for code in normalized_codes)
    has_blank_preferred_label = any(
        not label for label in normalized_preferred_labels
    )
    non_empty_normalized_labels = tuple(
        label for label in normalized_preferred_labels if label
    )
    has_duplicate_codes = _has_duplicates(normalized_codes)
    has_duplicate_preferred_labels = _has_duplicates(non_empty_normalized_labels)
    open_world_signals = _collect_open_world_signals(
        normalized_preferred_labels=normalized_preferred_labels,
        has_delegate=has_delegate,
        has_blank_code=has_blank_code,
        has_blank_preferred_label=has_blank_preferred_label,
    )

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

        item_codes=item_codes,
        preferred_labels=preferred_labels,
        normalized_codes=normalized_codes,
        normalized_preferred_labels=normalized_preferred_labels,
        has_blank_code=has_blank_code,
        has_blank_preferred_label=has_blank_preferred_label,
        has_duplicate_codes=has_duplicate_codes,
        has_duplicate_preferred_labels=has_duplicate_preferred_labels,
        has_other_like_entry=any(
            signal.startswith("label_token:")
            for signal in open_world_signals
        ),
        open_world_signals=open_world_signals,
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

def _collapse_whitespace(value: str) -> str:
    return " ".join(value.strip().split())
def _normalize_code(value: str) -> str:
    return _collapse_whitespace(value)
def _normalize_label_for_signal_detection(value: str) -> str:
    collapsed = _collapse_whitespace(value)
    ascii_value = unicodedata.normalize("NFKD", collapsed)
    ascii_value = ascii_value.encode("ascii", "ignore").decode("ascii")
    return ascii_value.upper()
def _get_language_name(language: object) -> str:
    language_name = getattr(language, "name", None)
    if language_name is not None:
        return str(language_name).upper()
    return str(language).rsplit(".", maxsplit=1)[-1].upper()

def _select_preferred_label(item: ItemType) -> str:
    name_details = tuple(item.name.name_detail)
    if not name_details:
        return ""
    labels_by_language = {
        _get_language_name(name_detail.lang): str(name_detail.name)
        for name_detail in name_details
    }
    for language in ("SPA", "ENG"):
        label = labels_by_language.get(language)
        if label is not None:
            return _collapse_whitespace(label)
    return _collapse_whitespace(str(name_details[0].name))


def _has_standalone_token(label: str, token: str) -> bool:
    pattern = rf"(^|[^A-Z0-9]){re.escape(token)}([^A-Z0-9]|$)"
    return re.search(pattern, label) is not None
def _collect_open_world_signals(
    *,
    normalized_preferred_labels: tuple[str, ...],
    has_delegate: bool,
    has_blank_code: bool,
    has_blank_preferred_label: bool,
) -> tuple[str, ...]:
    signals: list[str] = []
    for label in normalized_preferred_labels:
        for token in OTHER_LIKE_LABEL_TOKENS:
            if _has_standalone_token(label, token):
                signals.append(f"label_token:{token}")
    if has_delegate:
        signals.append("delegate_present")
    if has_blank_code:
        signals.append("blank_code")
    if has_blank_preferred_label:
        signals.append("blank_preferred_label")
    return tuple(dict.fromkeys(signals))
def _has_duplicates(values: tuple[str, ...]) -> bool:
    return len(values) != len(set(values))

