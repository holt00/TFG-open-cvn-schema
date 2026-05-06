from dataclasses import dataclass
from pathlib import Path
from cvn_codegen.auxiliary_sources.entity_metadata import (
    EntityCatalogMetadata,
    load_entity_catalog_metadata,
)
from cvn_codegen.auxiliary_sources.reference_tables_metadata import (
    ReferenceTableMetadata,
    load_reference_tables_metadata,
)
from cvn_codegen.auxiliary_sources.subtypes_metadata import (
    SubtypeMetadata,
    load_subtypes_metadata,
)
from cvn_codegen.auxiliary_sources.thesaurus_metadata import (
    ThesaurusCatalogMetadata,
    load_thesaurus_catalog_metadata,
)

@dataclass(frozen=True)
class AuxiliarySourceBundle:
    """Aggregate normalization-grade metadata from auxiliary source families."""
    reference_tables_by_name: dict[str, ReferenceTableMetadata]
    subtypes_by_source_code: dict[str, SubtypeMetadata]
    entity_catalog: EntityCatalogMetadata | None
    thesaurus_catalog: ThesaurusCatalogMetadata | None
    under_traced_table_names: frozenset[str] = frozenset(
        {"CVN_INTERVENTION_A", "CVN_PRUEBA"}
    )
def build_auxiliary_source_bundle(
    reference_tables_path: Path,
    subtypes_path: Path,
    entity_path: Path | None = None,
    thesaurus_path: Path | None = None,
) -> AuxiliarySourceBundle:
    """Build the auxiliary-source metadata bundle used by normalization.
    Args:
        reference_tables_path (Path): Path to the canonical
            ``ReferenceTables.xml`` file.
        subtypes_path (Path): Path to the canonical ``Subtype_Spa.xml`` file.
        entity_path (Path | None): Path to the canonical ``Entity.xml`` file
            when entity metadata should be loaded.
        thesaurus_path (Path | None): Path to the canonical ``Thesaurus.xml``
            file when thesaurus metadata should be loaded.
    Returns:
        AuxiliarySourceBundle: Aggregated auxiliary metadata bundle for the
        normalization resolution layer.
    """
    reference_tables_by_name = load_reference_tables_metadata(reference_tables_path)
    subtypes_by_source_code = load_subtypes_metadata(subtypes_path)
    entity_catalog = None
    if entity_path is not None:
        entity_catalog = load_entity_catalog_metadata(entity_path)
    thesaurus_catalog = None
    if thesaurus_path is not None:
        thesaurus_catalog = load_thesaurus_catalog_metadata(thesaurus_path)
    return AuxiliarySourceBundle(
        reference_tables_by_name=reference_tables_by_name,
        subtypes_by_source_code=subtypes_by_source_code,
        entity_catalog=entity_catalog,
        thesaurus_catalog=thesaurus_catalog,
    )