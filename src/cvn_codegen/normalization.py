"""Normalization orchestration utilities for Issue #13.

This module combines normalized manual metadata and normalized tree-model
metadata into repository-level views keyed by CVN code and technical XML path.
"""

from pathlib import Path

from cvn_codegen.manual_metadata import (
    extract_manual_entries,
    load_specification_manual,
)
from cvn_codegen.tree_metadata import (
    index_tree_entries_by_code,
    index_tree_entries_by_xml_path,
    load_and_extract_tree_entries,
)
from cvn_codegen.normalization_types import (
    ManualCodeEntry,
    NormalizedCodeEntry,
    NormalizationResult,
    TreePathEntry,
)
from cvn_codegen.normalization_report import collect_normalization_mismatches
from cvn_codegen.structural_type_trace import (
    build_structural_type_index,
    enrich_tree_entries_with_structural_type_evidence,
)

from cvn_codegen.auxiliary_sources import build_auxiliary_source_bundle
from cvn_codegen.auxiliary_sources.bundle import AuxiliarySourceBundle
from cvn_codegen.auxiliary_sources.reference_resolution import (
    resolve_manual_reference,
)

def collect_all_code(
    manual_entries_by_code: dict[str, ManualCodeEntry],
    tree_entries_by_code: dict[str, tuple[TreePathEntry, ...]],
) -> tuple[str, ...]:
    """Collect the full set of CVN codes from manual and tree-model sources.

    Args:
        manual_entries_by_code (dict[str, ManualCodeEntry]): Manual entries
            indexed by CVN code.
        tree_entries_by_code (dict[str, tuple[TreePathEntry, ...]]): Tree-model
            entries grouped by CVN code.

    Returns:
        tuple[str, ...]: Sorted tuple containing every unique code found in
            either source.

    Raises:
        ValueError: If either input is not a dictionary.
    """
    
    if not isinstance(manual_entries_by_code, dict):
        raise ValueError(
            f"Expected manual_entries_by_code to be a dict, but got {type(manual_entries_by_code)}."
        )
    if not isinstance(tree_entries_by_code, dict):
        raise ValueError(
            f"Expected tree_entries_by_code to be a dict, but got {type(tree_entries_by_code)}."
        )
    
    manual_keys = set(manual_entries_by_code.keys())
    tree_keys = set(tree_entries_by_code.keys())

    all_codes = manual_keys.union(tree_keys)

    all_codes_sorted_tuple = tuple(sorted(all_codes))

    return all_codes_sorted_tuple


def build_normalized_code(
    code: str,
    manual_entries_by_code: dict[str, ManualCodeEntry],
    tree_entries_by_code: dict[str, tuple[TreePathEntry, ...]],
    auxiliary_bundle: AuxiliarySourceBundle | None = None,
) -> NormalizedCodeEntry:
    """Build the normalized view for a single CVN code.

    Args:
        code (str): CVN code to normalize.
        manual_entries_by_code (dict[str, ManualCodeEntry]): Manual entries
            indexed by CVN code.
        tree_entries_by_code (dict[str, tuple[TreePathEntry, ...]]): Tree-model
            entries grouped by CVN code.

    Returns:
        NormalizedCodeEntry: Aggregated normalized entry for requested code.

    Raises:
        ValueError: If the provided code is empty after normalization.
    """

    normalized_code = code.strip()

    if not normalized_code:
        raise ValueError("Code is empty or whitespace.")
    
    manual_entry = manual_entries_by_code.get(normalized_code)
    tree_paths = tree_entries_by_code.get(normalized_code, ())
    source_files_set: set[str] = set()
    if manual_entry is not None:
        source_files_set.add("SpecificationManual.xml")
    if tree_paths:
        source_files_set.update(entry.trace.source_file for entry in tree_paths)
    reference_resolution = None
    if manual_entry is not None and auxiliary_bundle is not None:
        reference_resolution = resolve_manual_reference(
            raw_reference=manual_entry.manual_reference_table,
            auxiliary_bundle=auxiliary_bundle,
            manual_code=manual_entry.code,
        )
    structural_type_evidence = tuple(
        entry.structural_type_evidence
        for entry in tree_paths
        if entry.structural_type_evidence is not None
    )
    return NormalizedCodeEntry(
        code=normalized_code,
        manual=manual_entry,
        tree_paths=tree_paths,
        source_files=tuple(sorted(source_files_set)),
        reference_resolution=reference_resolution,
        structural_type_evidence=structural_type_evidence,
    )

def build_normalized_code_index(
    manual_entries_by_code: dict[str, ManualCodeEntry],
    tree_entries_by_code: dict[str, tuple[TreePathEntry, ...]],
    auxiliary_bundle: AuxiliarySourceBundle | None = None,
) -> dict[str, NormalizedCodeEntry]:
    """Build the normalized index keyed by CVN code.

    Args:
        manual_entries_by_code (dict[str, ManualCodeEntry]): Manual entries
            indexed by CVN code.
        tree_entries_by_code (dict[str, tuple[TreePathEntry, ...]]): Tree-model
            entries grouped by CVN code.

    Returns:
        dict[str, NormalizedCodeEntry]: Normalized entries indexed by CVN code.
    """

    all_codes = collect_all_code(manual_entries_by_code, tree_entries_by_code)

    normalized_entries_by_code: dict[str, NormalizedCodeEntry] = {}

    for code in all_codes:
        normalized_entry = build_normalized_code(
            code,
            manual_entries_by_code,
            tree_entries_by_code,
            auxiliary_bundle=auxiliary_bundle,
        )
        normalized_entries_by_code[code] = normalized_entry
    
    return normalized_entries_by_code

def build_normalization_result(
    specification_manual_path: Path,
    tree_model_path: Path,
    *,
    reference_tables_path: Path | None = None,
    subtypes_path: Path | None = None,
    entity_path: Path | None = None,
    thesaurus_path: Path | None = None,
    cvn_xsd_path: Path | None = None,
    common_xsd_path: Path | None = None,
) -> NormalizationResult:

    """Run the normalization orchestration for the canonical metadata sources.

    Args:
        specification_manual_path (Path): Path to the canonical
            ``SpecificationManual.xml`` file.
        tree_model_path (Path): Path to the canonical ``CVNTreeModel.xml``
            file.

    Returns:
        NormalizationResult: Aggregated normalization result containing:
            - normalized entries by code
            - tree entries by XML path
            - codes present only in the manual
            - codes present only in the tree model
            - mismatch collection
    """
    
    specification_manual = load_specification_manual(specification_manual_path)

    manual_entries_by_code = extract_manual_entries(specification_manual)

    tree_entries = load_and_extract_tree_entries(tree_model_path)

    if cvn_xsd_path is not None and common_xsd_path is not None:
        structural_type_index = build_structural_type_index(
            cvn_xsd_path=cvn_xsd_path,
            common_xsd_path=common_xsd_path,
        )
        tree_entries = enrich_tree_entries_with_structural_type_evidence(
            tree_entries=tree_entries,
            structural_type_index=structural_type_index,
        )

    tree_entries_by_code = index_tree_entries_by_code(tree_entries)

    tree_entries_by_xml_path = index_tree_entries_by_xml_path(tree_entries)

    auxiliary_bundle: AuxiliarySourceBundle | None = None
    if reference_tables_path is not None and subtypes_path is not None:
        auxiliary_bundle = build_auxiliary_source_bundle(
            reference_tables_path=reference_tables_path,
            subtypes_path=subtypes_path,
            entity_path=entity_path,
            thesaurus_path=thesaurus_path,
        )

    normalized_entries_by_code = build_normalized_code_index(
        manual_entries_by_code,
        tree_entries_by_code,
        auxiliary_bundle=auxiliary_bundle,
    )

    manual_codes = set(manual_entries_by_code)
    tree_codes = set(tree_entries_by_code)

    manual_only_codes = tuple(sorted(manual_codes - tree_codes))
    tree_only_codes = tuple(sorted(tree_codes - manual_codes))

    mismatches = collect_normalization_mismatches(
            manual_only_codes=manual_only_codes,
            tree_only_codes=tree_only_codes,
            normalized_entries_by_code=normalized_entries_by_code,
            auxiliary_bundle=auxiliary_bundle,
        )
    
    return NormalizationResult(
        by_code=normalized_entries_by_code,
        by_xml_path=tree_entries_by_xml_path,
        manual_only_codes=manual_only_codes,
        tree_only_codes=tree_only_codes,
        mismatches=mismatches,
    )
