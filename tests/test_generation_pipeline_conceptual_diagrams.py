from cvn_codegen.conceptual_model_diagrams import render_conceptual_model_diagrams
from cvn_codegen.conceptual_model_extractor import build_conceptual_model_inventory
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


def test_conceptual_diagram_pipeline_renders_canonical_plantuml(
    canonical_normalization_result: NormalizationResult,
):
    inventory = build_canonical_conceptual_inventory(canonical_normalization_result)

    artifacts = render_conceptual_model_diagrams(inventory)
    combined = "\n".join(artifact.content for artifact in artifacts)
    filenames = {artifact.filename for artifact in artifacts}

    assert "open_cvn_conceptual_overview.puml" in filenames
    assert "open_cvn_conceptual_overview_reference.puml" in filenames
    assert "open_cvn_core.puml" in filenames
    assert "open_cvn_identity.puml" in filenames
    assert "open_cvn_identity_reference.puml" in filenames
    assert any(filename.startswith("open_cvn_research") for filename in filenames)
    assert any(filename.startswith("open_cvn_research_050") for filename in filenames)
    assert any(filename.startswith("open_cvn_research_reference") for filename in filenames)
    assert 'class "Curriculum" as entity_core_curriculum <<entity>>' in combined
    assert 'class "Person" as entity_identity_person <<entity>>' in combined
    assert "CVN_SEX_A" in combined
    assert "000.010.000.030" in combined


def test_conceptual_diagram_pipeline_is_deterministic_and_avoids_implementation_noise(
    canonical_normalization_result: NormalizationResult,
):
    inventory = build_canonical_conceptual_inventory(canonical_normalization_result)

    first = render_conceptual_model_diagrams(inventory)
    second = render_conceptual_model_diagrams(inventory)
    combined = "\n".join(artifact.content for artifact in first)

    assert first == second
    assert "cvn_item" not in combined
    assert "BaseCvnDomainModel" not in combined
    assert "model_config" not in combined
    assert "Field(" not in combined
    assert "open_cvn_research_reference.puml" in filenames(first)


def filenames(artifacts):
    return {artifact.filename for artifact in artifacts}
