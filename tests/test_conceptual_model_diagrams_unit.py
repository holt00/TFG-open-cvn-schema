from pathlib import Path

from cvn_codegen.conceptual_model_diagrams import (
    render_conceptual_model_diagrams,
    render_domain_area_diagram,
    render_overview_diagram,
    write_conceptual_model_diagrams,
)
from cvn_codegen.conceptual_model_types import (
    ConceptualAttribute,
    ConceptualCardinalityKind,
    ConceptualConfidence,
    ConceptualDomainArea,
    ConceptualEntity,
    ConceptualModelInventory,
    ConceptualPresenceKind,
    ConceptualRelationship,
    ConceptualRelationshipKind,
    ConceptualTrace,
    ConceptualValueKind,
    ConceptualVocabulary,
    ConceptualVocabularyKind,
)


def build_trace(*codes: str, reference: str | None = None) -> ConceptualTrace:
    return ConceptualTrace(
        cvn_codes=codes,
        xml_paths=("/Node/CVNItem/Property",) if codes else (),
        source_files=("SpecificationManual.xml",),
        manual_reference_table=reference,
        reference_source_artifact="ReferenceTables.xml" if reference else None,
        semantic_reference_kind="compact_enum_like_table" if reference else None,
    )


def build_inventory() -> ConceptualModelInventory:
    vocabulary = ConceptualVocabulary(
        vocabulary_id="vocabularies.cvn_sex_a",
        name="CVN_SEX_A",
        kind=ConceptualVocabularyKind.ENUMERATION,
        source_reference="CVN_SEX_A",
        enum_eligibility="eligible",
        confidence=ConceptualConfidence.HIGH,
        trace=build_trace("000.010.000.030", reference="CVN_SEX_A"),
        item_count=2,
        values=(("000", "Mujer"), ("010", "Hombre")),
    )
    person = ConceptualEntity(
        entity_id="identity.person",
        name="Person",
        domain_area_id="identity",
        source_group_key="000.010.000.000",
        attributes=(
            ConceptualAttribute(
                attribute_id="identity.person.name_000_010_000_020",
                name="name",
                source_label="Nombre",
                value_kind=ConceptualValueKind.TEXT,
                presence=ConceptualPresenceKind.OPTIONAL,
                cardinality=ConceptualCardinalityKind.SINGLE,
                python_type_hint="str | None",
                domain_shape_kind="scalar",
                enum_eligibility="not_applicable",
                confidence=ConceptualConfidence.HIGH,
                trace=build_trace("000.010.000.020"),
            ),
            ConceptualAttribute(
                attribute_id="identity.person.sex_000_010_000_030",
                name="sex",
                source_label="Sexo",
                value_kind=ConceptualValueKind.CONTROLLED_REFERENCE,
                presence=ConceptualPresenceKind.OPTIONAL,
                cardinality=ConceptualCardinalityKind.SINGLE,
                python_type_hint="CvnSexA | None",
                domain_shape_kind="strict_enum",
                enum_eligibility="eligible",
                confidence=ConceptualConfidence.HIGH,
                trace=build_trace("000.010.000.030", reference="CVN_SEX_A"),
                vocabulary_id="vocabularies.cvn_sex_a",
            ),
        ),
        trace=build_trace("000.010.000.020", "000.010.000.030"),
        description="Person identity data.",
    )
    curriculum = ConceptualEntity(
        entity_id="core.curriculum",
        name="Curriculum",
        domain_area_id="core",
        source_group_key=None,
        attributes=(),
        trace=build_trace(),
        description="Root curriculum entity.",
    )
    return ConceptualModelInventory(
        inventory_id="open_cvn_conceptual_model",
        source_issue="#43",
        policy_name="default_semantic_policy",
        policy_version="1.0",
        domain_areas=(
            ConceptualDomainArea(area_id="core", name="CVN Core", entities=(curriculum,)),
            ConceptualDomainArea(area_id="identity", name="CVN Identity", entities=(person,)),
        ),
        relationships=(
            ConceptualRelationship(
                relationship_id="core.curriculum.owner",
                source_id="core.curriculum",
                target_id="identity.person",
                kind=ConceptualRelationshipKind.COMPOSITION,
                source_cardinality=ConceptualCardinalityKind.SINGLE,
                target_cardinality=ConceptualCardinalityKind.SINGLE,
                trace=build_trace(),
                label="owner",
            ),
        ),
        vocabularies=(vocabulary,),
        limitations=(),
    )


def test_render_overview_diagram_groups_entities_by_domain_area():
    diagram = render_overview_diagram(build_inventory())

    assert diagram.filename == "open_cvn_conceptual_overview.puml"
    assert 'package "Core Structure" as overview_core' in diagram.content
    assert 'package "Conceptual Areas" as conceptual_areas' in diagram.content
    assert 'class "Curriculum" as entity_core_curriculum <<entity>>' in diagram.content
    assert 'class "Person" as entity_identity_person <<entity>>' in diagram.content
    assert 'class "CVN Identity" as summary_identity <<domain_area>>' in diagram.content
    assert 'entity_core_curriculum "1" *-- "1" entity_identity_person : owner' in diagram.content


def test_render_domain_area_diagram_includes_attributes_vocabularies_and_trace():
    inventory = build_inventory()
    identity_area = next(area for area in inventory.domain_areas if area.area_id == "identity")

    diagram = render_domain_area_diagram(inventory, identity_area)

    assert diagram.filename == "open_cvn_identity.puml"
    assert "name : text <<optional, single>>" in diagram.content
    assert "sex : controlled_reference <<optional, single>>" in diagram.content
    assert "CVN_SEX_A" not in diagram.content
    assert "manual reference: CVN_SEX_A" not in diagram.content
    assert "entity_identity_person ..> vocabulary_vocabularies_cvn_sex_a : sex" not in diagram.content


def test_render_conceptual_model_diagrams_is_deterministic_and_agnostic():
    inventory = build_inventory()

    first = render_conceptual_model_diagrams(inventory)
    second = render_conceptual_model_diagrams(inventory)
    combined = "\n".join(artifact.content for artifact in first)

    assert first == second
    assert "cvn_item" not in combined
    assert "BaseCvnDomainModel" not in combined
    assert "Field(" not in combined
    assert "open_cvn_identity_reference.puml" in {artifact.filename for artifact in first}
    assert "open_cvn_presentation_overview.puml" in {artifact.filename for artifact in first}


def test_write_conceptual_model_diagrams_writes_all_artifacts(tmp_path: Path):
    written_paths = write_conceptual_model_diagrams(
        tmp_path,
        inventory=build_inventory(),
    )

    assert sorted(path.name for path in written_paths) == [
        "open_cvn_conceptual_overview.puml",
        "open_cvn_conceptual_overview_reference.puml",
        "open_cvn_core.puml",
        "open_cvn_core_reference.puml",
        "open_cvn_identity.puml",
        "open_cvn_identity_reference.puml",
        "open_cvn_presentation_overview.puml",
    ]
    assert all(path.exists() for path in written_paths)
    assert (tmp_path / "open_cvn_identity.puml").read_text(encoding="utf-8").startswith("@startuml")
