from cvn_codegen.conceptual_model_extractor import (
    build_conceptual_model_inventory,
    build_conceptual_trace,
    build_stable_identifier,
    map_cardinality_kind,
    map_confidence,
    map_policy_to_value_kind,
    map_policy_to_vocabulary_kind,
    map_presence_kind,
)
from cvn_codegen.conceptual_model_types import (
    ConceptualCardinalityKind,
    ConceptualConfidence,
    ConceptualPresenceKind,
    ConceptualValueKind,
    ConceptualVocabularyKind,
)
from cvn_codegen.domain_model_generator import (
    build_domain_field_spec,
    build_domain_generation_result,
    build_semantic_policy_index,
    group_entries_by_cvn_item_code,
)
from cvn_codegen.normalization_types import (
    ManualCodeEntry,
    NormalizationResult,
    NormalizedCodeEntry,
    ReferenceResolution,
    ReferenceResolutionStatus,
    ReferenceResolutionTrace,
    ReferenceSourceFamily,
    ReferenceTableEnumEvidence,
    SemanticReferenceKind,
    SerializationPattern,
    SourceTrace,
    StructuralTypeEvidence,
    TreePathEntry,
)
from cvn_codegen.semantic_policy import (
    CardinalityKind,
    PolicyConfidence,
    PresenceKind,
    build_default_semantic_policy_bundle,
    build_semantic_field_policy,
)


def build_reference_table_enum_evidence(
    *,
    table_name: str = "CVN_SEX_A",
    has_delegate: bool = False,
) -> ReferenceTableEnumEvidence:
    return ReferenceTableEnumEvidence(
        table_name=table_name,
        item_count=2,
        has_hierarchy=False,
        has_delegate=has_delegate,
        has_other_like_entry=False,
        has_duplicate_codes=False,
        has_duplicate_preferred_labels=False,
        has_blank_code=False,
        has_blank_preferred_label=False,
        normalized_codes=("000", "010"),
        preferred_labels=("Mujer", "Hombre"),
        normalized_preferred_labels=("MUJER", "HOMBRE"),
        open_world_signals=(),
    )


def build_reference_resolution(
    *,
    raw_reference: str = "CVN_SEX_A",
    source_family: ReferenceSourceFamily = ReferenceSourceFamily.REFERENCE_TABLE,
    semantic_kind: SemanticReferenceKind = SemanticReferenceKind.COMPACT_ENUM_LIKE_TABLE,
    serialization_pattern: SerializationPattern = SerializationPattern.FILTER_VALUE,
    evidence: ReferenceTableEnumEvidence | None = None,
) -> ReferenceResolution:
    return ReferenceResolution(
        raw_reference=raw_reference,
        status=ReferenceResolutionStatus.RESOLVED,
        source_family=source_family,
        source_artifact="ReferenceTables.xml",
        resolved_name=raw_reference,
        serialization_pattern=serialization_pattern,
        semantic_kind=semantic_kind,
        is_subtype_backed=source_family == ReferenceSourceFamily.SUBTYPE_BACKED_TABLE,
        subtype_metadata_present=None,
        diagnostic_message=None,
        trace=ReferenceResolutionTrace(
            manual_reference=raw_reference,
            resolved_from_artifact="ReferenceTables.xml",
            resolution_rule="test_reference_resolution",
        ),
        reference_table_enum_evidence=evidence,
    )


def build_entry(
    *,
    code: str = "000.010.000.020",
    manual_name: str = "Nombre",
    manual_type: str = "Alphanumeric",
    manual_obligatory: bool | None = False,
    manual_multiplicity: bool | None = False,
    tree_cvn_item_code: str | None = "000.010.000.000",
    reference_resolution: ReferenceResolution | None = None,
    structural_type_evidence: tuple[StructuralTypeEvidence, ...] = (),
) -> NormalizedCodeEntry:
    xml_path = f"/Node/CVNItem[@code='{tree_cvn_item_code}']/Property[@name='Test']"
    tree_paths = ()
    if tree_cvn_item_code is not None:
        tree_paths = (
            TreePathEntry(
                code=code,
                tree_cvn_item_code=tree_cvn_item_code,
                tree_property_name="Test",
                tree_indicator_name="Value",
                tree_value=None,
                xml_path=xml_path,
                trace=SourceTrace(
                    source_file="CVNTreeModel.xml",
                    xml_path=xml_path,
                    source_code=code,
                ),
            ),
        )
    return NormalizedCodeEntry(
        code=code,
        manual=ManualCodeEntry(
            code=code,
            manual_name=manual_name,
            manual_short_name=None,
            manual_type=manual_type,
            manual_obligatory=manual_obligatory,
            manual_multiplicity=manual_multiplicity,
            manual_reference_table=(
                None
                if reference_resolution is None
                else reference_resolution.raw_reference
            ),
        ),
        tree_paths=tree_paths,
        source_files=("SpecificationManual.xml", "CVNTreeModel.xml"),
        reference_resolution=reference_resolution,
        structural_type_evidence=structural_type_evidence,
    )


def build_policy_and_field(entry: NormalizedCodeEntry):
    bundle = build_default_semantic_policy_bundle()
    policy = build_semantic_field_policy(entry, bundle)
    field = build_domain_field_spec(
        policy=policy,
        resolved_field_name=policy.naming_policy.normalized_field_name,
    )
    return policy, field


def build_small_generation_result(entries: tuple[NormalizedCodeEntry, ...]):
    normalization_result = NormalizationResult(
        by_code={entry.code: entry for entry in entries},
        by_xml_path={},
        manual_only_codes=(),
        tree_only_codes=(),
        mismatches=(),
    )
    bundle = build_default_semantic_policy_bundle()
    policy_index = build_semantic_policy_index(normalization_result, bundle)
    grouped_entries = group_entries_by_cvn_item_code(normalization_result.by_code)
    return build_domain_generation_result(
        policy_index=policy_index,
        grouped_entries=grouped_entries,
    )


def test_build_stable_identifier_removes_python_and_xml_noise():
    assert build_stable_identifier("cvn_item_000_010", "Field(...) Class") == "cvn_item_000_010_field_class"


def test_mapping_functions_translate_semantic_policy_enums():
    assert map_presence_kind(PresenceKind.REQUIRED) == ConceptualPresenceKind.REQUIRED
    assert map_presence_kind(PresenceKind.OPTIONAL) == ConceptualPresenceKind.OPTIONAL
    assert map_cardinality_kind(CardinalityKind.REPEATED) == ConceptualCardinalityKind.REPEATED
    assert map_cardinality_kind(CardinalityKind.SINGLE) == ConceptualCardinalityKind.SINGLE
    assert map_confidence(PolicyConfidence.HIGH) == ConceptualConfidence.HIGH
    assert map_confidence(PolicyConfidence.REQUIRES_REVIEW) == ConceptualConfidence.REQUIRES_REVIEW


def test_map_policy_to_value_kind_maps_scalar_and_wrapper_shapes():
    text_policy, text_field = build_policy_and_field(build_entry())
    assert map_policy_to_value_kind(text_policy, text_field) == ConceptualValueKind.TEXT

    wrapper_evidence = StructuralTypeEvidence(
        element_name="OfficialId",
        declaring_type_name="PersonalIdentificationType",
        structural_type_name="OfficialIdType",
        xml_path="/Node/Agent/Property[@name='Identification']/Indicator[@name='OfficialId']",
        source_xsd_file="CVN.xsd",
        terminal_wrapper_type_name="OfficialIdType",
    )
    wrapper_policy, wrapper_field = build_policy_and_field(
        build_entry(
            code="000.010.000.100",
            manual_name="Documento identificativo",
            structural_type_evidence=(wrapper_evidence,),
        )
    )
    assert map_policy_to_value_kind(wrapper_policy, wrapper_field) == ConceptualValueKind.VALUE_OBJECT


def test_map_policy_to_vocabulary_kind_distinguishes_reference_shapes():
    eligible_entry = build_entry(
        code="000.010.000.030",
        manual_name="Sexo",
        reference_resolution=build_reference_resolution(
            raw_reference="CVN_SEX_A",
            evidence=build_reference_table_enum_evidence(),
        ),
    )
    eligible_policy, _field = build_policy_and_field(eligible_entry)
    assert map_policy_to_vocabulary_kind(eligible_policy) == ConceptualVocabularyKind.ENUMERATION

    registry_entry = build_entry(
        code="010.010.000.020",
        manual_name="Entidad empleadora",
        reference_resolution=build_reference_resolution(
            raw_reference="ENTITY@Entity.xsd",
            source_family=ReferenceSourceFamily.SIDE_PACKAGE_REGISTRY,
            semantic_kind=SemanticReferenceKind.SIDE_PACKAGE_REGISTRY,
            serialization_pattern=SerializationPattern.SIDE_PACKAGE_REGISTRY,
        ),
    )
    registry_policy, _field = build_policy_and_field(registry_entry)
    assert map_policy_to_vocabulary_kind(registry_policy) == ConceptualVocabularyKind.REGISTRY


def test_build_conceptual_trace_preserves_semantic_decision_evidence():
    entry = build_entry(
        code="000.010.000.030",
        manual_name="Sexo",
        reference_resolution=build_reference_resolution(
            raw_reference="CVN_SEX_A",
            evidence=build_reference_table_enum_evidence(),
        ),
    )
    policy, _field = build_policy_and_field(entry)

    trace = build_conceptual_trace(entry=entry, policy=policy)

    assert trace.cvn_codes == ("000.010.000.030",)
    assert trace.manual_reference_table == "CVN_SEX_A"
    assert trace.reference_source_artifact == "ReferenceTables.xml"
    assert trace.semantic_reference_kind == "compact_enum_like_table"
    assert "enum_evidence:strict_enum_eligible" in trace.applied_rules


def test_build_conceptual_model_inventory_builds_domain_oriented_entities():
    entries = (
        build_entry(code="000.010.000.020", manual_name="Nombre"),
        build_entry(
            code="000.010.000.030",
            manual_name="Sexo",
            reference_resolution=build_reference_resolution(
                raw_reference="CVN_SEX_A",
                evidence=build_reference_table_enum_evidence(),
            ),
        ),
        build_entry(
            code="010.010.000.020",
            manual_name="Entidad empleadora",
            tree_cvn_item_code="010.010.000.000",
            reference_resolution=build_reference_resolution(
                raw_reference="ENTITY@Entity.xsd",
                source_family=ReferenceSourceFamily.SIDE_PACKAGE_REGISTRY,
                semantic_kind=SemanticReferenceKind.SIDE_PACKAGE_REGISTRY,
                serialization_pattern=SerializationPattern.SIDE_PACKAGE_REGISTRY,
            ),
        ),
    )
    result = build_small_generation_result(entries)

    inventory = build_conceptual_model_inventory(result)

    areas = {area.area_id: area for area in inventory.domain_areas}
    assert "core" in areas
    assert "identity" in areas
    assert "professional_experience" in areas
    identity_entity = next(entity for entity in areas["identity"].entities if entity.entity_id == "identity.person")
    assert identity_entity.name == "Person"
    assert all("cvn_item" not in entity.entity_id for area in areas.values() for entity in area.entities)
    assert any(vocabulary.source_reference == "CVN_SEX_A" for vocabulary in inventory.vocabularies)
    assert any(relationship.source_id == "core.curriculum" for relationship in inventory.relationships)


def test_build_conceptual_model_inventory_is_deterministic():
    entries = (
        build_entry(code="000.010.000.030", manual_name="Sexo"),
        build_entry(code="000.010.000.020", manual_name="Nombre"),
    )
    result = build_small_generation_result(entries)

    assert build_conceptual_model_inventory(result) == build_conceptual_model_inventory(result)
