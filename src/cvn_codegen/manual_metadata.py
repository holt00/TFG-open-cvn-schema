from pathlib import Path
from xsdata_pydantic.bindings import XmlParser
from generated.specification_manual.specification_manual import (
    NameType,
    SpecificationManual,
)
from cvn_codegen.normalization_types import (
    ManualCodeEntry,
    SourceTrace,
)
import logging

logger = logging.getLogger(__name__)


def load_specification_manual(specification_manual_path: Path) -> SpecificationManual:
    """Load and parse the canonical specification manual XML file.

    Args:
        specification_manual_path (Path): Path to the canonical
            ``SpecificationManual.xml`` file.

    Returns:
        SpecificationManual: Parsed specification manual root object.

    Raises:
        ValueError: If ``specification_manual_path`` is not a ``Path``.
        FileNotFoundError: If the target XML file does not exist.
    """

    if not isinstance(specification_manual_path, Path):
        raise ValueError(
            f"specification_manual_path must be a Path object, got {type(specification_manual_path)} instead."
        )

    if not specification_manual_path.is_file():
        raise FileNotFoundError(
            f"Specification manual file not found at path: {specification_manual_path}"
        )

    xml_parser = XmlParser()
    specification_manual = xml_parser.from_path(
        specification_manual_path, SpecificationManual
    )
    return specification_manual


def select_name_detail(
    name_details: list[NameType.NameDetail], preferred_language: str = "spa"
) -> NameType.NameDetail | None:
    """Select the preferred localized name entry from a manual item.

    Args:
        name_details (list[NameType.NameDetail]): Available localized name
            entries for a manual item.
        preferred_language (str): Preferred ISO 639 language code to select.
            Defaults to ``"spa"``.

    Returns:
        NameType.NameDetail | None: The preferred localized entry if present,
        otherwise the first available entry, or ``None`` when the list is
        empty.
    """

    if not name_details:
        return None
    for detail in name_details:
        if getattr(detail.lang, "value", detail.lang) == preferred_language:
            return detail
    return name_details[0]


def build_manual_code_entry(
    item: SpecificationManual.Manual.Item,
) -> ManualCodeEntry:
    """Transform a specification manual item into a normalized entry.

    Args:
        item (SpecificationManual.Manual.Item): Parsed manual item from the
            structural binding.

    Returns:
        ManualCodeEntry: Normalized metadata entry keyed by CVN code.

    Raises:
        ValueError: If the item code is empty after normalization.
    """
    code = str(item.code).strip()

    if not code:
        raise ValueError(f"Item code is empty for item {item.name}")

    selected_name_detail = select_name_detail(
        item.name.name_detail, preferred_language="spa"
    )

    manual_name = None
    manual_short_name = None

    if selected_name_detail:
        manual_name = selected_name_detail.name
        manual_short_name = selected_name_detail.short_name

    return ManualCodeEntry(
        code=code,
        manual_name=manual_name,
        manual_short_name=manual_short_name,
        manual_type=item.type_value,
        manual_obligatory=item.obligatory,
        manual_multiplicity=item.multiplicity,
        manual_reference_table=item.reference_table,
        manual_level=item.level,
        manual_order=item.order,
        manual_link=item.link,
        manual_length=item.length,
        trace=SourceTrace(
            source_file="SpecificationManual.xml",
            xml_path=f"/SpecificationManual/Manual/Item[@code='{code}']",
            source_code=code,
        ),
    )


def extract_manual_entries(
    specification_manual: SpecificationManual,
) -> dict[str, ManualCodeEntry]:
    """Build an index of normalized manual entries keyed by CVN code.

    Args:
        specification_manual (SpecificationManual): Parsed specification manual
            root object.

    Returns:
        dict[str, ManualCodeEntry]: Dictionary of normalized manual entries
        keyed by CVN code.

    Raises:
        ValueError: If duplicate CVN codes are found in the manual.
    """
    entry_ny_code: dict[str, ManualCodeEntry] = {}

    for item in specification_manual.manual.item:
        entry: ManualCodeEntry = build_manual_code_entry(item)
        if entry.code in entry_ny_code:
            logger.warning(
                f"Duplicate code '{entry.code}' found in specification manual."
            )
            raise ValueError(
                f"Duplicate code '{entry.code}' found in specification manual."
            )
        entry_ny_code[entry.code] = entry

    return entry_ny_code
