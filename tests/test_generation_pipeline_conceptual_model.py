from cvn_codegen.conceptual_model_extractor import build_conceptual_model_inventory
from cvn_codegen.conceptual_model_types import ConceptualVocabularyKind
from cvn_codegen.domain_model_generator import (
    build_domain_generation_result,
    build_semantic_policy_index,
    group_entries_by_cvn_item_code,
)
from cvn_codegen.normalization_types import NormalizationResult
from cvn_codegen.semantic_policy import build_default_semantic_policy_bundle


def build_canonical_conceptual_inventory(normalization_result: NormalizationResult):
    bundle = build_default_semantic_policy_bundle()
    policy_index = build_semantic_policy_index(normalization_result, bundle)
    grouped_entries = group_entries_by_cvn_item_code(normalization_result.by_code)
    generation_result = build_domain_generation_result(
        policy_index=policy_index,
        grouped_entries=grouped_entries,
    )
    return build_conceptual_model_inventory(generation_result)


def collect_entities_by_id(inventory):
    return {
        entity.entity_id: entity
        for area in inventory.domain_areas
        for entity in area.entities
    }


def test_conceptual_pipeline_builds_non_empty_inventory(
    canonical_normalization_result: NormalizationResult,
):
    inventory = build_canonical_conceptual_inventory(canonical_normalization_result)

    assert inventory.inventory_id == "open_cvn_conceptual_model"
    assert inventory.source_issue == "#43"
    assert inventory.domain_areas
    assert inventory.vocabularies
    assert inventory.limitations


def test_conceptual_pipeline_preserves_cvn_code_trace_for_attributes(
    canonical_normalization_result: NormalizationResult,
):
    inventory = build_canonical_conceptual_inventory(canonical_normalization_result)
    attributes = [
        attribute
        for area in inventory.domain_areas
        for entity in area.entities
        for attribute in entity.attributes
    ]

    assert attributes
    assert all(attribute.trace.cvn_codes for attribute in attributes)
    assert any(attribute.trace.cvn_codes == ("000.010.000.030",) for attribute in attributes)


def test_conceptual_pipeline_groups_representative_domain_areas(
    canonical_normalization_result: NormalizationResult,
):
    inventory = build_canonical_conceptual_inventory(canonical_normalization_result)
    areas = {area.area_id: area for area in inventory.domain_areas}

    assert "core" in areas
    assert "identity" in areas
    assert "professional_experience" in areas
    assert "education" in areas or "research" in areas

    entities = collect_entities_by_id(inventory)
    assert "core.curriculum" in entities
    assert "identity.person" in entities
    assert entities["identity.person"].attributes


def test_conceptual_pipeline_keeps_entity_ids_agnostic_to_generated_modules(
    canonical_normalization_result: NormalizationResult,
):
    inventory = build_canonical_conceptual_inventory(canonical_normalization_result)
    entities = collect_entities_by_id(inventory)

    assert all("cvn_item" not in entity_id for entity_id in entities)
    assert all("BaseCvnDomainModel" not in entity.name for entity in entities.values())


def test_conceptual_pipeline_classifies_representative_vocabularies(
    canonical_normalization_result: NormalizationResult,
):
    inventory = build_canonical_conceptual_inventory(canonical_normalization_result)
    vocabularies_by_reference = {
        vocabulary.source_reference: vocabulary
        for vocabulary in inventory.vocabularies
    }

    assert vocabularies_by_reference["CVN_SEX_A"].kind == ConceptualVocabularyKind.ENUMERATION
    assert vocabularies_by_reference["CVN_ENTITY_TYPE"].kind == ConceptualVocabularyKind.CODE_LIST
    assert vocabularies_by_reference["CVN_KNOW_A"].kind == ConceptualVocabularyKind.SUBTYPE_BACKED_CODE_LIST
    assert vocabularies_by_reference["ENTITY@Entity.xsd"].kind == ConceptualVocabularyKind.REGISTRY
    assert vocabularies_by_reference["THESAURUS@thesaurus.xsd"].kind == ConceptualVocabularyKind.THESAURUS
    assert vocabularies_by_reference["UNESCO_CODES"].kind == ConceptualVocabularyKind.HIERARCHICAL_CODE_LIST
    assert vocabularies_by_reference["CVN_AGENCY_C"].kind == ConceptualVocabularyKind.UNRESOLVED_REFERENCE


def test_conceptual_pipeline_is_deterministic(
    canonical_normalization_result: NormalizationResult,
):
    inventory_a = build_canonical_conceptual_inventory(canonical_normalization_result)
    inventory_b = build_canonical_conceptual_inventory(canonical_normalization_result)

    assert inventory_a == inventory_b
