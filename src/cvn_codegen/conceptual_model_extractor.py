import re

from cvn_codegen.domain_model_generator import (
    build_domain_generation_result,
    build_semantic_policy_index,
    get_canonical_generation_paths,
    group_entries_by_cvn_item_code,
)
from cvn_codegen.domain_model_types import (
    DomainFieldSpec,
    DomainGenerationResult,
    DomainGenerationUnit,
)
from cvn_codegen.normalization import build_normalization_result
from cvn_codegen.normalization_types import (
    NormalizedCodeEntry,
    ReferenceResolution,
)
from cvn_codegen.semantic_policy import (
    CardinalityKind,
    DomainShapeKind,
    EnumEligibility,
    PolicyConfidence,
    PresenceKind,
    SemanticBaseKind,
    SemanticFieldPolicy,
    build_default_semantic_policy_bundle,
)
from cvn_codegen.conceptual_model_types import (
    ConceptualAttribute,
    ConceptualCardinalityKind,
    ConceptualConfidence,
    ConceptualDomainArea,
    ConceptualEntity,
    ConceptualLimitation,
    ConceptualModelInventory,
    ConceptualPresenceKind,
    ConceptualRelationship,
    ConceptualRelationshipKind,
    ConceptualTrace,
    ConceptualValueKind,
    ConceptualVocabulary,
    ConceptualVocabularyKind,
)


DOMAIN_AREA_NAMES = {
    "core": "CVN Core",
    "common": "CVN Common",
    "identity": "CVN Identity",
    "professional_experience": "CVN Professional Experience",
    "education": "CVN Education",
    "research": "CVN Research",
    "achievements": "CVN Achievements",
    "vocabularies": "CVN Vocabularies",
    "other": "Other CVN Concepts",
}

WRAPPER_VALUE_TYPES = {
    "FlexibleDateValue",
    "OfficialIdValue",
    "EntityTypeValue",
    "EntityNameValue",
}


def build_stable_identifier(*parts: str | None) -> str:
    """Build a deterministic ASCII identifier from arbitrary parts."""
    raw_value = "_".join(part for part in parts if part)
    normalized = re.sub(r"[^A-Za-z0-9]+", "_", raw_value).strip("_").lower()
    return normalized or "unnamed"


def build_conceptual_trace(
    *,
    entry: NormalizedCodeEntry | None = None,
    policy: SemanticFieldPolicy | None = None,
    codes: tuple[str, ...] = (),
    xml_paths: tuple[str, ...] = (),
    source_files: tuple[str, ...] = (),
) -> ConceptualTrace:
    """Build trace evidence for conceptual model records."""
    cvn_codes = codes
    resolved_xml_paths = xml_paths
    resolved_source_files = source_files
    manual_reference_table = None
    reference_source_family = None
    reference_source_artifact = None
    semantic_reference_kind = None
    serialization_pattern = None
    applied_rules: tuple[str, ...] = ()
    diagnostics: tuple[str, ...] = ()

    if entry is not None:
        cvn_codes = (entry.code,)
        resolved_xml_paths = tuple(path.xml_path for path in entry.tree_paths)
        resolved_source_files = entry.source_files
        if entry.manual is not None:
            manual_reference_table = entry.manual.manual_reference_table

    if policy is not None:
        cvn_codes = (policy.code,)
        resolved_xml_paths = policy.xml_paths
        manual_reference_table = policy.decision_trace.manual_reference_table
        reference_source_family = policy.decision_trace.reference_source_family
        reference_source_artifact = policy.decision_trace.reference_source_artifact
        if policy.decision_trace.semantic_reference_kind is not None:
            semantic_reference_kind = policy.decision_trace.semantic_reference_kind.value
        if policy.decision_trace.serialization_pattern is not None:
            serialization_pattern = policy.decision_trace.serialization_pattern.value
        applied_rules = policy.decision_trace.applied_rules
        diagnostics = policy.decision_trace.diagnostics

    return ConceptualTrace(
        cvn_codes=tuple(sorted(cvn_codes)),
        xml_paths=tuple(sorted(resolved_xml_paths)),
        source_files=tuple(sorted(resolved_source_files)),
        manual_reference_table=manual_reference_table,
        reference_source_family=reference_source_family,
        reference_source_artifact=reference_source_artifact,
        semantic_reference_kind=semantic_reference_kind,
        serialization_pattern=serialization_pattern,
        applied_rules=applied_rules,
        diagnostics=diagnostics,
    )


def map_policy_to_value_kind(policy: SemanticFieldPolicy, field: DomainFieldSpec) -> ConceptualValueKind:
    """Map semantic policy and emitted field shape to conceptual value kind."""
    base_type = field.python_type.removeprefix("list[").removesuffix("]")
    if base_type in WRAPPER_VALUE_TYPES:
        return ConceptualValueKind.VALUE_OBJECT
    if policy.base_kind == SemanticBaseKind.TEXT:
        return ConceptualValueKind.TEXT
    if policy.base_kind == SemanticBaseKind.BOOLEAN:
        return ConceptualValueKind.BOOLEAN
    if policy.base_kind == SemanticBaseKind.DECIMAL_NUMBER:
        return ConceptualValueKind.DECIMAL_NUMBER
    if policy.base_kind == SemanticBaseKind.DATE_LIKE:
        return ConceptualValueKind.DATE_LIKE
    if policy.base_kind == SemanticBaseKind.DURATION_LIKE:
        return ConceptualValueKind.DURATION_LIKE
    if policy.base_kind == SemanticBaseKind.CONTROLLED_REFERENCE:
        return ConceptualValueKind.CONTROLLED_REFERENCE
    return ConceptualValueKind.UNKNOWN


def map_presence_kind(presence_kind: PresenceKind) -> ConceptualPresenceKind:
    """Map semantic presence into conceptual presence."""
    if presence_kind == PresenceKind.REQUIRED:
        return ConceptualPresenceKind.REQUIRED
    if presence_kind == PresenceKind.OPTIONAL:
        return ConceptualPresenceKind.OPTIONAL
    return ConceptualPresenceKind.UNKNOWN


def map_cardinality_kind(cardinality_kind: CardinalityKind) -> ConceptualCardinalityKind:
    """Map semantic cardinality into conceptual cardinality."""
    if cardinality_kind == CardinalityKind.REPEATED:
        return ConceptualCardinalityKind.REPEATED
    if cardinality_kind == CardinalityKind.SINGLE:
        return ConceptualCardinalityKind.SINGLE
    return ConceptualCardinalityKind.UNKNOWN


def map_confidence(confidence: PolicyConfidence) -> ConceptualConfidence:
    """Map semantic policy confidence into conceptual confidence."""
    return ConceptualConfidence(confidence.value)


def map_policy_to_vocabulary_kind(policy: SemanticFieldPolicy) -> ConceptualVocabularyKind:
    """Map controlled-reference policy to conceptual vocabulary kind."""
    if policy.enum_eligibility == EnumEligibility.ELIGIBLE:
        return ConceptualVocabularyKind.ENUMERATION
    if policy.domain_shape_kind == DomainShapeKind.SUBTYPE_BACKED_VALUE:
        return ConceptualVocabularyKind.SUBTYPE_BACKED_CODE_LIST
    if policy.domain_shape_kind == DomainShapeKind.HIERARCHICAL_CODE_REFERENCE:
        return ConceptualVocabularyKind.HIERARCHICAL_CODE_LIST
    if policy.domain_shape_kind == DomainShapeKind.REGISTRY_REFERENCE:
        return ConceptualVocabularyKind.REGISTRY
    if policy.domain_shape_kind == DomainShapeKind.VOCABULARY_REFERENCE:
        return ConceptualVocabularyKind.THESAURUS
    if policy.domain_shape_kind == DomainShapeKind.UNRESOLVED_REFERENCE:
        return ConceptualVocabularyKind.UNRESOLVED_REFERENCE
    if policy.domain_shape_kind == DomainShapeKind.UNDER_TRACED_REFERENCE:
        return ConceptualVocabularyKind.UNDER_TRACED_REFERENCE
    if policy.base_kind == SemanticBaseKind.CONTROLLED_REFERENCE:
        return ConceptualVocabularyKind.CODE_LIST
    return ConceptualVocabularyKind.NONE


def get_domain_area_id_for_group_key(group_key: str) -> str:
    """Map CVN group keys to initial conceptual domain areas."""
    if group_key.startswith("000."):
        return "identity"
    if group_key.startswith("010."):
        return "professional_experience"
    if group_key.startswith("020.") or group_key.startswith("030."):
        return "education"
    if group_key.startswith("050.") or group_key.startswith("060."):
        return "research"
    if group_key.startswith("070.") or group_key.startswith("080."):
        return "achievements"
    if group_key.startswith("__"):
        return "other"
    return "other"


def get_domain_area_id_for_unit(unit: DomainGenerationUnit) -> str:
    """Map a generation unit to a conceptual area using field codes if needed."""
    if not unit.source_group_key.startswith("__"):
        return get_domain_area_id_for_group_key(unit.source_group_key)
    field_codes = tuple(field.code for field in unit.fields)
    if field_codes and all(code.startswith("000.") for code in field_codes):
        return "identity"
    return "other"


def get_entity_name_for_unit(unit: DomainGenerationUnit, area_id: str) -> str:
    """Return a conceptual entity name for a generation unit."""
    if area_id == "identity":
        return "Person"
    if area_id == "professional_experience" and unit.source_group_key == "010.010.000.000":
        return "ProfessionalSituation"
    if area_id == "education":
        return unit.class_name or "EducationalExperience"
    return unit.class_name or "CurricularItem"


def get_entity_id_for_unit(unit: DomainGenerationUnit, area_id: str) -> str:
    """Return stable conceptual entity identifier without generated module names."""
    if area_id == "identity":
        return "identity.person"
    entity_name = get_entity_name_for_unit(unit, area_id)
    return f"{area_id}.{build_stable_identifier(entity_name, unit.source_group_key)}"


def build_vocabulary_id(source_reference: str) -> str:
    """Build stable vocabulary identifier from a source reference."""
    return f"vocabularies.{build_stable_identifier(source_reference)}"


def get_source_reference(entry: NormalizedCodeEntry) -> str | None:
    """Return the best source reference for a normalized entry."""
    resolution = entry.reference_resolution
    if resolution is None:
        return None
    return resolution.resolved_name or resolution.raw_reference


def build_conceptual_attribute(
    *,
    entity_id: str,
    field: DomainFieldSpec,
    entry: NormalizedCodeEntry,
    policy: SemanticFieldPolicy,
) -> ConceptualAttribute:
    """Build a conceptual attribute from one domain field and semantic policy."""
    source_reference = get_source_reference(entry)
    vocabulary_id = None
    if source_reference is not None and policy.base_kind == SemanticBaseKind.CONTROLLED_REFERENCE:
        vocabulary_id = build_vocabulary_id(source_reference)
    return ConceptualAttribute(
        attribute_id=f"{entity_id}.{build_stable_identifier(field.field_name, field.code)}",
        name=field.field_name,
        source_label=policy.naming_policy.source_label,
        value_kind=map_policy_to_value_kind(policy, field),
        presence=map_presence_kind(policy.presence_kind),
        cardinality=map_cardinality_kind(policy.cardinality_kind),
        python_type_hint=field.python_type,
        domain_shape_kind=policy.domain_shape_kind.value,
        enum_eligibility=policy.enum_eligibility.value,
        confidence=map_confidence(policy.policy_confidence),
        trace=build_conceptual_trace(entry=entry, policy=policy),
        vocabulary_id=vocabulary_id,
        wrapper_type_names=policy.wrapper_type_names,
    )


def build_entity_trace(entries: tuple[NormalizedCodeEntry, ...]) -> ConceptualTrace:
    """Build aggregate trace for a conceptual entity."""
    return build_conceptual_trace(
        codes=tuple(entry.code for entry in entries),
        xml_paths=tuple(path.xml_path for entry in entries for path in entry.tree_paths),
        source_files=tuple(
            source_file
            for entry in entries
            for source_file in entry.source_files
        ),
    )


def build_conceptual_entity(
    *,
    unit: DomainGenerationUnit,
    entries_by_code: dict[str, NormalizedCodeEntry],
    policies_by_code: dict[str, SemanticFieldPolicy],
) -> ConceptualEntity:
    """Build one conceptual entity from a domain generation unit."""
    area_id = get_domain_area_id_for_unit(unit)
    entity_id = get_entity_id_for_unit(unit, area_id)
    attributes = tuple(
        sorted(
            (
                build_conceptual_attribute(
                    entity_id=entity_id,
                    field=field,
                    entry=entries_by_code[field.code],
                    policy=policies_by_code[field.code],
                )
                for field in unit.fields
            ),
            key=lambda attribute: attribute.attribute_id,
        )
    )
    entries = tuple(entries_by_code[field.code] for field in unit.fields)
    return ConceptualEntity(
        entity_id=entity_id,
        name=get_entity_name_for_unit(unit, area_id),
        domain_area_id=area_id,
        source_group_key=unit.source_group_key,
        attributes=attributes,
        trace=build_entity_trace(entries),
        description=f"Conceptual entity extracted from CVN group {unit.source_group_key}.",
    )


def group_entities_by_domain_area(
    entities: tuple[ConceptualEntity, ...],
) -> tuple[ConceptualDomainArea, ...]:
    """Group conceptual entities by domain area."""
    grouped: dict[str, list[ConceptualEntity]] = {}
    for entity in entities:
        grouped.setdefault(entity.domain_area_id, []).append(entity)
    return tuple(
        ConceptualDomainArea(
            area_id=area_id,
            name=DOMAIN_AREA_NAMES.get(area_id, area_id.replace("_", " ").title()),
            entities=tuple(sorted(grouped[area_id], key=lambda entity: entity.entity_id)),
            description=f"Conceptual area for {DOMAIN_AREA_NAMES.get(area_id, area_id)}.",
        )
        for area_id in sorted(grouped)
    )


def build_vocabulary_values(
    source_reference: str,
    result: DomainGenerationResult,
) -> tuple[tuple[str, str], ...]:
    """Return enum values for eligible strict vocabularies when available."""
    for enum_spec in result.enums:
        if enum_spec.source_reference == source_reference:
            return tuple(
                (code_value, enum_spec.labels.get(code_value, member_name))
                for member_name, code_value in enum_spec.members
            )
    return ()


def get_reference_item_count(resolution: ReferenceResolution | None) -> int | None:
    """Return known reference-table item count when available."""
    if resolution is None or resolution.reference_table_enum_evidence is None:
        return None
    return resolution.reference_table_enum_evidence.item_count


def build_conceptual_vocabularies(
    result: DomainGenerationResult,
    policies_by_code: dict[str, SemanticFieldPolicy],
) -> tuple[ConceptualVocabulary, ...]:
    """Build conceptual vocabularies from controlled-reference entries."""
    vocabularies_by_id: dict[str, ConceptualVocabulary] = {}
    for entry in result.normalized_entries:
        policy = policies_by_code[entry.code]
        source_reference = get_source_reference(entry)
        if source_reference is None or policy.base_kind != SemanticBaseKind.CONTROLLED_REFERENCE:
            continue
        vocabulary_id = build_vocabulary_id(source_reference)
        if vocabulary_id in vocabularies_by_id:
            continue
        vocabularies_by_id[vocabulary_id] = ConceptualVocabulary(
            vocabulary_id=vocabulary_id,
            name=source_reference,
            kind=map_policy_to_vocabulary_kind(policy),
            source_reference=source_reference,
            enum_eligibility=policy.enum_eligibility.value,
            confidence=map_confidence(policy.policy_confidence),
            trace=build_conceptual_trace(entry=entry, policy=policy),
            item_count=get_reference_item_count(entry.reference_resolution),
            values=build_vocabulary_values(source_reference, result),
        )
    return tuple(sorted(vocabularies_by_id.values(), key=lambda item: item.vocabulary_id))


def build_root_relationships(entities: tuple[ConceptualEntity, ...]) -> tuple[ConceptualRelationship, ...]:
    """Build conservative root relationships for representative conceptual areas."""
    relationships: list[ConceptualRelationship] = []
    entity_ids = {entity.entity_id for entity in entities}
    empty_trace = build_conceptual_trace()
    root_id = "core.curriculum"
    for target_id, label in (
        ("identity.person", "owner"),
        ("professional_experience.professionalsituation_010_010_000_000", "professionalSituations"),
    ):
        if target_id not in entity_ids:
            continue
        relationships.append(
            ConceptualRelationship(
                relationship_id=f"{root_id}.{label}",
                source_id=root_id,
                target_id=target_id,
                kind=ConceptualRelationshipKind.COMPOSITION,
                source_cardinality=ConceptualCardinalityKind.SINGLE,
                target_cardinality=(
                    ConceptualCardinalityKind.SINGLE
                    if target_id == "identity.person"
                    else ConceptualCardinalityKind.REPEATED
                ),
                trace=empty_trace,
                label=label,
            )
        )
    return tuple(sorted(relationships, key=lambda relationship: relationship.relationship_id))


def build_core_curriculum_entity() -> ConceptualEntity:
    """Build the stable conceptual root entity for the curriculum."""
    return ConceptualEntity(
        entity_id="core.curriculum",
        name="Curriculum",
        domain_area_id="core",
        source_group_key=None,
        attributes=(),
        trace=build_conceptual_trace(),
        description="Root conceptual entity for the Open CVN curriculum model.",
    )


def build_conceptual_limitations(
    result: DomainGenerationResult,
) -> tuple[ConceptualLimitation, ...]:
    """Build conservative limitations known at conceptual extraction time."""
    manual_only_codes = tuple(
        entry.code
        for entry in result.normalized_entries
        if not entry.tree_paths
    )
    limitations = [
        ConceptualLimitation(
            limitation_id="conceptual_relationships_require_curation",
            message=(
                "Conceptual relationships are conservative; generated field "
                "annotations alone do not prove complete domain associations."
            ),
            trace=build_conceptual_trace(),
        ),
    ]
    if manual_only_codes:
        limitations.append(
            ConceptualLimitation(
                limitation_id="manual_only_codes_without_xml_paths",
                message="Some manual codes lack tree-model XML paths.",
                trace=build_conceptual_trace(codes=manual_only_codes),
            )
        )
    return tuple(sorted(limitations, key=lambda limitation: limitation.limitation_id))


def build_conceptual_model_inventory(
    result: DomainGenerationResult,
    *,
    inventory_id: str = "open_cvn_conceptual_model",
) -> ConceptualModelInventory:
    """Build the agnostic conceptual model inventory from domain generation IR."""
    entries_by_code = {entry.code: entry for entry in result.normalized_entries}
    policies_by_code = {policy.code: policy for policy in result.semantic_policies}
    extracted_entities = tuple(
        sorted(
            (
                build_conceptual_entity(
                    unit=unit,
                    entries_by_code=entries_by_code,
                    policies_by_code=policies_by_code,
                )
                for unit in result.units
            ),
            key=lambda entity: entity.entity_id,
        )
    )
    entities = tuple(sorted((build_core_curriculum_entity(), *extracted_entities), key=lambda entity: entity.entity_id))
    metadata = build_default_semantic_policy_bundle().metadata
    return ConceptualModelInventory(
        inventory_id=inventory_id,
        source_issue="#43",
        policy_name=metadata.policy_name,
        policy_version=metadata.policy_version,
        domain_areas=group_entities_by_domain_area(entities),
        relationships=build_root_relationships(entities),
        vocabularies=build_conceptual_vocabularies(result, policies_by_code),
        limitations=build_conceptual_limitations(result),
    )


def build_canonical_conceptual_model_inventory() -> ConceptualModelInventory:
    """Build the canonical conceptual inventory from the repository source package."""
    canonical_paths = get_canonical_generation_paths()
    normalization_result = build_normalization_result(
        specification_manual_path=canonical_paths["specification_manual"],
        tree_model_path=canonical_paths["tree_model"],
        reference_tables_path=canonical_paths["reference_tables"],
        subtypes_path=canonical_paths["subtypes"],
        entity_path=canonical_paths["entity"],
        thesaurus_path=canonical_paths["thesaurus"],
        cvn_xsd_path=canonical_paths["cvn_xsd"],
        common_xsd_path=canonical_paths["common_xsd"],
    )
    bundle = build_default_semantic_policy_bundle()
    policy_index = build_semantic_policy_index(normalization_result, bundle)
    grouped_entries = group_entries_by_cvn_item_code(normalization_result.by_code)
    result = build_domain_generation_result(
        policy_index=policy_index,
        grouped_entries=grouped_entries,
    )
    return build_conceptual_model_inventory(result)
