"""Auxiliary source helpers for cvn_codegen.

This package groups support modules used by code generation tasks.
"""

from cvn_codegen.auxiliary_sources.bundle import (
    AuxiliarySourceBundle,
    build_auxiliary_source_bundle,
)
from cvn_codegen.auxiliary_sources.entity_metadata import EntityCatalogMetadata
from cvn_codegen.auxiliary_sources.reference_tables_metadata import (
    ReferenceTableMetadata,
)
from cvn_codegen.auxiliary_sources.subtypes_metadata import SubtypeMetadata
from cvn_codegen.auxiliary_sources.thesaurus_metadata import (
    ThesaurusCatalogMetadata,
)
__all__ = [
    "AuxiliarySourceBundle",
    "EntityCatalogMetadata",
    "ReferenceTableMetadata",
    "SubtypeMetadata",
    "ThesaurusCatalogMetadata",
    "build_auxiliary_source_bundle",
]