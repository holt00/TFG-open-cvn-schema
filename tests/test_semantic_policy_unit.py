from pathlib import Path

from cvn_codegen.normalization_types import (
    ManualCodeEntry,
    NormalizedCodeEntry,
    ReferenceResolution,
    ReferenceResolutionStatus,
    ReferenceResolutionTrace,
    ReferenceSourceFamily,
    SemanticReferenceKind,
    SerializationPattern,
    SourceTrace,
    TreePathEntry,
    ReferenceTableEnumEvidence,
)
from cvn_codegen.semantic_policy import (
    CardinalityKind,
    DomainShapeKind,
    EnumEligibility,
    OverrideRule,
    PolicyConfidence,
    PresenceKind,
    SemanticBaseKind,
    SemanticPolicyBundle,
    StructuralLimitationFlag,
    WrapperPolicyKind,
    MAX_STRICT_ENUM_ITEM_COUNT,
    evaluate_reference_table_enum_eligibility,
    build_default_semantic_policy_bundle,
    build_semantic_field_policy,
    get_choice_wrapper_policy,
    get_wrapper_auto_application_limitation,
    select_applicable_override,
    validate_wrapper_case,
)

from cvn_codegen.auxiliary_sources.bundle import build_auxiliary_source_bundle
from cvn_codegen.auxiliary_sources.reference_resolution import resolve_manual_reference

REPO_ROOT = Path(__file__).resolve().parent.parent
CANONICAL_XML_DIR = (
    REPO_ROOT / "docs" / "CvnXML_v1.4.3_2.1_17012025" / "XML"
)
REFERENCE_TABLES_XML = CANONICAL_XML_DIR / "ReferenceTables.xml"
SUBTYPES_XML = CANONICAL_XML_DIR / "Subtype_Spa.xml"
ENTITY_XML = CANONICAL_XML_DIR / "Entity.xml"
THESAURUS_XML = CANONICAL_XML_DIR / "Thesaurus.xml"



def build_normalized_entry(
    *,
    code: str = "000.000.000.000",
    manual_type: str | None = "Alphanumeric",
    reference_resolution: ReferenceResolution | None = None,
    manual_obligatory: bool | None = False,
    manual_multiplicity: bool | None = False,
    manual_name: str | None = "Nombre de prueba",
    manual_short_name: str | None = "Prueba",
    xml_path: str | None = None,
) -> NormalizedCodeEntry:
    manual_entry = None
    if manual_type is not None:
        manual_entry = ManualCodeEntry(
            code=code,
            manual_name=manual_name,
            manual_short_name=manual_short_name,
            manual_type=manual_type,
            manual_obligatory=manual_obligatory,
            manual_multiplicity=manual_multiplicity,
            manual_reference_table=None,
        )

    tree_paths: tuple[TreePathEntry, ...] = ()
    source_files: tuple[str, ...] = ("SpecificationManual.xml",)
    if xml_path is not None:
        tree_paths = (
            TreePathEntry(
                code=code,
                tree_cvn_item_code=None,
                tree_property_name="TestProperty",
                tree_indicator_name="TestIndicator",
                tree_value=None,
                xml_path=xml_path,
                trace=SourceTrace(
                    source_file="CVNTreeModel.xml",
                    xml_path=xml_path,
                    source_code=code,
                ),
            ),
        )
        source_files = ("CVNTreeModel.xml", "SpecificationManual.xml")

    return NormalizedCodeEntry(
        code=code,
        manual=manual_entry,
        tree_paths=tree_paths,
        source_files=source_files,
        reference_resolution=reference_resolution,
    )

def build_reference_resolution(
    *,
    raw_reference: str = "CVN_TEST",
    semantic_kind: SemanticReferenceKind = SemanticReferenceKind.COMPACT_ENUM_LIKE_TABLE,
    serialization_pattern: SerializationPattern = SerializationPattern.FILTER_VALUE,
    source_family: ReferenceSourceFamily = ReferenceSourceFamily.REFERENCE_TABLE,
    reference_table_enum_evidence: ReferenceTableEnumEvidence | None = None,
) -> ReferenceResolution:
    return ReferenceResolution(
        raw_reference=raw_reference,
        status=ReferenceResolutionStatus.RESOLVED,
        source_family=source_family,
        source_artifact="ReferenceTables.xml",
        resolved_name=raw_reference,
        serialization_pattern=serialization_pattern,
        semantic_kind=semantic_kind,
        is_subtype_backed=False,
        subtype_metadata_present=None,
        diagnostic_message=None,
        trace=ReferenceResolutionTrace(
            manual_reference=raw_reference,
            resolved_from_artifact="ReferenceTables.xml",
            resolution_rule="test_reference_resolution",
        ),
        reference_table_enum_evidence=reference_table_enum_evidence,
    )

def build_reference_table_enum_evidence(
    *,
    table_name: str = "CVN_TEST",
    item_count: int = 2,
    has_hierarchy: bool = False,
    has_delegate: bool = False,
    has_other_like_entry: bool = False,
    has_duplicate_codes: bool = False,
    has_duplicate_preferred_labels: bool = False,
    has_blank_code: bool = False,
    has_blank_preferred_label: bool = False,
) -> ReferenceTableEnumEvidence:
    return ReferenceTableEnumEvidence(
        table_name=table_name,
        item_count=item_count,
        has_hierarchy=has_hierarchy,
        has_delegate=has_delegate,
        has_other_like_entry=has_other_like_entry,
        has_duplicate_codes=has_duplicate_codes,
        has_duplicate_preferred_labels=has_duplicate_preferred_labels,
        has_blank_code=has_blank_code,
        has_blank_preferred_label=has_blank_preferred_label,
        normalized_codes=("000", "010"),
        preferred_labels=("Uno", "Dos"),
        normalized_preferred_labels=("UNO", "DOS"),
        open_world_signals=(),
    )

def build_real_auxiliary_bundle():
    return build_auxiliary_source_bundle(
        reference_tables_path=REFERENCE_TABLES_XML,
        subtypes_path=SUBTYPES_XML,
        entity_path=ENTITY_XML,
        thesaurus_path=THESAURUS_XML,
    )


def test_build_default_semantic_policy_bundle_returns_expected_shape():
    # Arrange / Act
    bundle = build_default_semantic_policy_bundle()

    # Assert
    assert isinstance(bundle, SemanticPolicyBundle)
    assert bundle.metadata.source_issue == "#14"
    assert bundle.metadata.policy_name == "default_cvn_semantic_policy"
    assert bundle.base_type_policies_by_manual_type
    assert bundle.reference_kind_policies
    assert bundle.serialization_pattern_refinements
    assert bundle.wrapper_policies_by_name
    assert bundle.validation_cases

def test_build_semantic_field_policy_maps_alphanumeric_to_text():
    # Arrange
    bundle = build_default_semantic_policy_bundle()
    entry = build_normalized_entry(manual_type="Alphanumeric")

    # Act
    field_policy = build_semantic_field_policy(entry, bundle)

    # Assert
    assert field_policy.base_kind == SemanticBaseKind.TEXT


def test_build_semantic_field_policy_maps_date_to_date_like():
    # Arrange
    bundle = build_default_semantic_policy_bundle()
    entry = build_normalized_entry(manual_type="Date")

    # Act
    field_policy = build_semantic_field_policy(entry, bundle)

    # Assert
    assert field_policy.base_kind == SemanticBaseKind.DATE_LIKE


def test_build_semantic_field_policy_maps_double_to_decimal_number():
    # Arrange
    bundle = build_default_semantic_policy_bundle()
    entry = build_normalized_entry(manual_type="Double")

    # Act
    field_policy = build_semantic_field_policy(entry, bundle)

    # Assert
    assert field_policy.base_kind == SemanticBaseKind.DECIMAL_NUMBER


def test_build_semantic_field_policy_maps_boolean_to_boolean():
    # Arrange
    bundle = build_default_semantic_policy_bundle()
    entry = build_normalized_entry(manual_type="Boolean")

    # Act
    field_policy = build_semantic_field_policy(entry, bundle)

    # Assert
    assert field_policy.base_kind == SemanticBaseKind.BOOLEAN


def test_build_semantic_field_policy_maps_duration_to_duration_like():
    # Arrange
    bundle = build_default_semantic_policy_bundle()
    entry = build_normalized_entry(manual_type="Duration")

    # Act
    field_policy = build_semantic_field_policy(entry, bundle)

    # Assert
    assert field_policy.base_kind == SemanticBaseKind.DURATION_LIKE


def test_build_semantic_field_policy_maps_unknown_manual_type_to_unknown():
    # Arrange
    bundle = build_default_semantic_policy_bundle()
    entry = build_normalized_entry(manual_type="UnexpectedType")

    # Act
    field_policy = build_semantic_field_policy(entry, bundle)

    # Assert
    assert field_policy.base_kind == SemanticBaseKind.UNKNOWN

def test_build_semantic_field_policy_maps_controlled_reference_to_controlled_base_kind():
    # Arrange
    bundle = build_default_semantic_policy_bundle()
    entry = build_normalized_entry(
        manual_type="Alphanumeric",
        reference_resolution=build_reference_resolution(),
    )

    # Act
    field_policy = build_semantic_field_policy(entry, bundle)

    # Assert
    assert field_policy.base_kind == SemanticBaseKind.CONTROLLED_REFERENCE


def test_build_semantic_field_policy_maps_compact_enum_like_table():
    # Arrange
    bundle = build_default_semantic_policy_bundle()
    entry = build_normalized_entry(
        reference_resolution=build_reference_resolution(
            raw_reference="CVN_GENERIC_ENUM",
            semantic_kind=SemanticReferenceKind.COMPACT_ENUM_LIKE_TABLE,
            serialization_pattern=SerializationPattern.FILTER_VALUE,
        ),
    )

    # Act
    field_policy = build_semantic_field_policy(entry, bundle)

    # Assert
    assert field_policy.domain_shape_kind == DomainShapeKind.STRICT_ENUM_CANDIDATE
    assert field_policy.fallback_shape_kind == DomainShapeKind.OPEN_CODED_VALUE
    assert field_policy.enum_eligibility == EnumEligibility.INELIGIBLE
    assert field_policy.policy_confidence == PolicyConfidence.HIGH
    assert "enum_evidence:missing_enum_evidence" in field_policy.decision_trace.applied_rules


def test_build_semantic_field_policy_maps_scale_or_measure_table():
    # Arrange
    bundle = build_default_semantic_policy_bundle()
    entry = build_normalized_entry(
        reference_resolution=build_reference_resolution(
            semantic_kind=SemanticReferenceKind.COMPACT_SCALE_OR_MEASURE,
            serialization_pattern=SerializationPattern.QUALITY_MEASURE,
        ),
    )

    # Act
    field_policy = build_semantic_field_policy(entry, bundle)

    # Assert
    assert field_policy.domain_shape_kind == DomainShapeKind.MEASURE_OR_SCALE_VALUE
    assert field_policy.enum_eligibility == EnumEligibility.REVIEW_REQUIRED
    assert field_policy.policy_confidence == PolicyConfidence.MEDIUM


def test_build_semantic_field_policy_maps_identifier_type_table():
    # Arrange
    bundle = build_default_semantic_policy_bundle()
    entry = build_normalized_entry(
        reference_resolution=build_reference_resolution(
            semantic_kind=SemanticReferenceKind.IDENTIFIER_TYPE_TABLE,
            serialization_pattern=SerializationPattern.EXTERNAL_PK_TYPE,
        ),
    )

    # Act
    field_policy = build_semantic_field_policy(entry, bundle)

    # Assert
    assert field_policy.domain_shape_kind == DomainShapeKind.IDENTIFIER_REFERENCE
    assert field_policy.enum_eligibility == EnumEligibility.INELIGIBLE


def test_build_semantic_field_policy_maps_scope_table():
    # Arrange
    bundle = build_default_semantic_policy_bundle()
    entry = build_normalized_entry(
        reference_resolution=build_reference_resolution(
            semantic_kind=SemanticReferenceKind.SCOPE_TABLE,
            serialization_pattern=SerializationPattern.SCOPE_TYPE,
        ),
    )

    # Act
    field_policy = build_semantic_field_policy(entry, bundle)

    # Assert
    assert field_policy.domain_shape_kind == DomainShapeKind.SCOPE_REFERENCE
    assert field_policy.enum_eligibility == EnumEligibility.REVIEW_REQUIRED


def test_build_semantic_field_policy_maps_subtype_backed_family():
    # Arrange
    bundle = build_default_semantic_policy_bundle()
    entry = build_normalized_entry(
        reference_resolution=build_reference_resolution(
            semantic_kind=SemanticReferenceKind.SUBTYPE_BACKED_CONTROLLED_FAMILY,
            serialization_pattern=SerializationPattern.SUBTYPE,
            source_family=ReferenceSourceFamily.SUBTYPE_BACKED_TABLE,
        ),
    )

    # Act
    field_policy = build_semantic_field_policy(entry, bundle)

    # Assert
    assert field_policy.domain_shape_kind == DomainShapeKind.SUBTYPE_BACKED_VALUE
    assert field_policy.enum_eligibility == EnumEligibility.INELIGIBLE


def test_build_semantic_field_policy_maps_hierarchical_classification():
    # Arrange
    bundle = build_default_semantic_policy_bundle()
    entry = build_normalized_entry(
        reference_resolution=build_reference_resolution(
            raw_reference="UNESCO_CODES",
            semantic_kind=SemanticReferenceKind.HIERARCHICAL_THEMATIC_CLASSIFICATION,
            serialization_pattern=SerializationPattern.SUBJECT_DESCRIPTION,
        ),
    )

    # Act
    field_policy = build_semantic_field_policy(entry, bundle)

    # Assert
    assert field_policy.domain_shape_kind == DomainShapeKind.HIERARCHICAL_CODE_REFERENCE
    assert field_policy.enum_eligibility == EnumEligibility.INELIGIBLE


def test_build_semantic_field_policy_maps_side_package_registry():
    # Arrange
    bundle = build_default_semantic_policy_bundle()
    entry = build_normalized_entry(
        reference_resolution=build_reference_resolution(
            raw_reference="ENTITY@Entity.xsd",
            semantic_kind=SemanticReferenceKind.SIDE_PACKAGE_REGISTRY,
            serialization_pattern=SerializationPattern.SIDE_PACKAGE_REGISTRY,
            source_family=ReferenceSourceFamily.SIDE_PACKAGE_REGISTRY,
        ),
    )

    # Act
    field_policy = build_semantic_field_policy(entry, bundle)

    # Assert
    assert field_policy.domain_shape_kind == DomainShapeKind.REGISTRY_REFERENCE
    assert field_policy.enum_eligibility == EnumEligibility.INELIGIBLE


def test_build_semantic_field_policy_maps_side_package_vocabulary():
    # Arrange
    bundle = build_default_semantic_policy_bundle()
    entry = build_normalized_entry(
        reference_resolution=build_reference_resolution(
            raw_reference="THESAURUS@thesaurus.xsd",
            semantic_kind=SemanticReferenceKind.SIDE_PACKAGE_THESAURUS_OR_VOCABULARY,
            serialization_pattern=SerializationPattern.SIDE_PACKAGE_THESAURUS,
            source_family=ReferenceSourceFamily.SIDE_PACKAGE_THESAURUS,
        ),
    )

    # Act
    field_policy = build_semantic_field_policy(entry, bundle)

    # Assert
    assert field_policy.domain_shape_kind == DomainShapeKind.VOCABULARY_REFERENCE
    assert field_policy.enum_eligibility == EnumEligibility.INELIGIBLE


def test_build_semantic_field_policy_maps_unresolved_reference():
    # Arrange
    bundle = build_default_semantic_policy_bundle()
    entry = build_normalized_entry(
        reference_resolution=build_reference_resolution(
            raw_reference="CVN_AGENCY_C",
            semantic_kind=SemanticReferenceKind.UNRESOLVED_MANUAL_ONLY_REFERENCE,
            serialization_pattern=SerializationPattern.UNRESOLVED,
            source_family=ReferenceSourceFamily.UNRESOLVED_MANUAL_ONLY,
        ),
    )

    # Act
    field_policy = build_semantic_field_policy(entry, bundle)

    # Assert
    assert field_policy.domain_shape_kind == DomainShapeKind.UNRESOLVED_REFERENCE
    assert field_policy.enum_eligibility == EnumEligibility.INELIGIBLE


def test_build_semantic_field_policy_maps_under_traced_reference():
    # Arrange
    bundle = build_default_semantic_policy_bundle()
    entry = build_normalized_entry(
        reference_resolution=build_reference_resolution(
            raw_reference="CVN_INTERVENTION_A",
            semantic_kind=SemanticReferenceKind.UNDER_TRACED_REFERENCE_TABLE,
            serialization_pattern=SerializationPattern.FILTER_VALUE,
        ),
    )

    # Act
    field_policy = build_semantic_field_policy(entry, bundle)

    # Assert
    assert field_policy.domain_shape_kind == DomainShapeKind.UNDER_TRACED_REFERENCE
    assert field_policy.enum_eligibility == EnumEligibility.INELIGIBLE

def test_dynamic_enum_evidence_marks_cvn_sex_a_as_eligible():
    # Arrange
    bundle = build_default_semantic_policy_bundle()
    entry = build_normalized_entry(
        code="000.010.000.030",
        reference_resolution=build_reference_resolution(
            raw_reference="CVN_SEX_A",
            semantic_kind=SemanticReferenceKind.COMPACT_ENUM_LIKE_TABLE,
            serialization_pattern=SerializationPattern.FILTER_VALUE,
            reference_table_enum_evidence=build_reference_table_enum_evidence(
                table_name="CVN_SEX_A",
                item_count=2,
            ),
        ),
    )

    # Act
    field_policy = build_semantic_field_policy(entry, bundle)

    # Assert
    assert field_policy.domain_shape_kind == DomainShapeKind.STRICT_ENUM_CANDIDATE
    assert field_policy.enum_eligibility == EnumEligibility.ELIGIBLE
    assert field_policy.policy_confidence == PolicyConfidence.HIGH
    assert (
        "enum_evidence:strict_enum_eligible"
        in field_policy.decision_trace.applied_rules
    )

def test_dynamic_enum_evidence_requires_review_for_other_like_entry():
    # Arrange
    bundle = build_default_semantic_policy_bundle()
    entry = build_normalized_entry(
        code="010.010.000.040",
        reference_resolution=build_reference_resolution(
            raw_reference="CVN_OTHER_LIKE_TABLE",
            semantic_kind=SemanticReferenceKind.COMPACT_ENUM_LIKE_TABLE,
            serialization_pattern=SerializationPattern.FILTER_VALUE,
            reference_table_enum_evidence=build_reference_table_enum_evidence(
                table_name="CVN_OTHER_LIKE_TABLE",
                item_count=17,
                has_other_like_entry=True,
            ),
        ),
    )

    # Act
    field_policy = build_semantic_field_policy(entry, bundle)

    # Assert
    assert field_policy.domain_shape_kind == DomainShapeKind.STRICT_ENUM_CANDIDATE
    assert field_policy.enum_eligibility == EnumEligibility.REVIEW_REQUIRED
    assert field_policy.policy_confidence == PolicyConfidence.REQUIRES_REVIEW
    assert (
        "enum_evidence:other_like_entry"
        in field_policy.decision_trace.applied_rules
    )


def test_generic_compact_enum_like_table_is_ineligible_without_enum_evidence():
    # Arrange
    bundle = build_default_semantic_policy_bundle()
    entry = build_normalized_entry(
        reference_resolution=build_reference_resolution(
            raw_reference="CVN_GENERIC_TABLE",
            semantic_kind=SemanticReferenceKind.COMPACT_ENUM_LIKE_TABLE,
            serialization_pattern=SerializationPattern.FILTER_VALUE,
        ),
    )

    # Act
    field_policy = build_semantic_field_policy(entry, bundle)

    # Assert
    assert field_policy.domain_shape_kind == DomainShapeKind.STRICT_ENUM_CANDIDATE
    assert field_policy.enum_eligibility == EnumEligibility.INELIGIBLE
    assert field_policy.policy_confidence == PolicyConfidence.HIGH
    assert (
        "enum_evidence:missing_enum_evidence"
        in field_policy.decision_trace.applied_rules
    )

def test_build_semantic_field_policy_maps_required_presence():
    # Arrange
    bundle = build_default_semantic_policy_bundle()
    entry = build_normalized_entry(manual_obligatory=True)

    # Act
    field_policy = build_semantic_field_policy(entry, bundle)

    # Assert
    assert field_policy.presence_kind == PresenceKind.REQUIRED


def test_build_semantic_field_policy_maps_optional_presence():
    # Arrange
    bundle = build_default_semantic_policy_bundle()
    entry = build_normalized_entry(manual_obligatory=False)

    # Act
    field_policy = build_semantic_field_policy(entry, bundle)

    # Assert
    assert field_policy.presence_kind == PresenceKind.OPTIONAL


def test_build_semantic_field_policy_maps_unknown_presence():
    # Arrange
    bundle = build_default_semantic_policy_bundle()
    entry = build_normalized_entry(manual_obligatory=None)

    # Act
    field_policy = build_semantic_field_policy(entry, bundle)

    # Assert
    assert field_policy.presence_kind == PresenceKind.UNKNOWN


def test_build_semantic_field_policy_maps_repeated_cardinality():
    # Arrange
    bundle = build_default_semantic_policy_bundle()
    entry = build_normalized_entry(manual_multiplicity=True)

    # Act
    field_policy = build_semantic_field_policy(entry, bundle)

    # Assert
    assert field_policy.cardinality_kind == CardinalityKind.REPEATED


def test_build_semantic_field_policy_maps_single_cardinality():
    # Arrange
    bundle = build_default_semantic_policy_bundle()
    entry = build_normalized_entry(manual_multiplicity=False)

    # Act
    field_policy = build_semantic_field_policy(entry, bundle)

    # Assert
    assert field_policy.cardinality_kind == CardinalityKind.SINGLE


def test_build_semantic_field_policy_maps_unknown_cardinality():
    # Arrange
    bundle = build_default_semantic_policy_bundle()
    entry = build_normalized_entry(manual_multiplicity=None)

    # Act
    field_policy = build_semantic_field_policy(entry, bundle)

    # Assert
    assert field_policy.cardinality_kind == CardinalityKind.UNKNOWN

def test_build_semantic_field_policy_uses_spanish_manual_name_for_field_name():
    # Arrange
    bundle = build_default_semantic_policy_bundle()
    entry = build_normalized_entry(manual_name="Título del proyecto")

    # Act
    field_policy = build_semantic_field_policy(entry, bundle)

    # Assert
    assert field_policy.naming_policy.normalized_field_name == "titulo_del_proyecto"
    assert field_policy.naming_policy.source_label == "Título del proyecto"


def test_build_semantic_field_policy_falls_back_to_short_name_for_naming():
    # Arrange
    bundle = build_default_semantic_policy_bundle()
    entry = build_normalized_entry(
        manual_name=None,
        manual_short_name="Nombre corto",
    )

    # Act
    field_policy = build_semantic_field_policy(entry, bundle)

    # Assert
    assert field_policy.naming_policy.normalized_field_name == "nombre_corto"
    assert field_policy.naming_policy.source_label == "Nombre corto"


def test_build_semantic_field_policy_falls_back_to_code_for_missing_labels():
    # Arrange
    bundle = build_default_semantic_policy_bundle()
    entry = build_normalized_entry(
        code="000.010.000.020",
        manual_name=None,
        manual_short_name=None,
    )

    # Act
    field_policy = build_semantic_field_policy(entry, bundle)

    # Assert
    assert field_policy.naming_policy.normalized_field_name == "field_000_010_000_020"
    assert field_policy.naming_policy.source_label == "000.010.000.020"


def test_build_semantic_field_policy_preserves_acronyms_in_class_name():
    # Arrange
    bundle = build_default_semantic_policy_bundle()
    entry = build_normalized_entry(manual_name="Código UNESCO")

    # Act
    field_policy = build_semantic_field_policy(entry, bundle)

    # Assert
    assert field_policy.naming_policy.normalized_class_name == "CodigoUNESCO"

def test_select_applicable_override_prefers_code_and_xml_path_over_code_only():
    # Arrange
    entry = build_normalized_entry(
        code="000.010.000.030",
        xml_path="/CVNTreeModel/Node/Test",
    )
    overrides = (
        OverrideRule(
            rule_id="code_only",
            target_code="000.010.000.030",
            enum_eligibility=EnumEligibility.INELIGIBLE,
        ),
        OverrideRule(
            rule_id="code_and_path",
            target_code="000.010.000.030",
            target_xml_path="/CVNTreeModel/Node/Test",
            enum_eligibility=EnumEligibility.REVIEW_REQUIRED,
        ),
    )

    # Act
    selection = select_applicable_override(entry, overrides)

    # Assert
    assert selection.selected_override is not None
    assert selection.selected_override.rule_id == "code_and_path"
    assert selection.conflict_detected is False


def test_select_applicable_override_prefers_code_over_xml_path_only():
    # Arrange
    entry = build_normalized_entry(
        code="000.010.000.030",
        xml_path="/CVNTreeModel/Node/Test",
    )
    overrides = (
        OverrideRule(
            rule_id="xml_path_only",
            target_xml_path="/CVNTreeModel/Node/Test",
            enum_eligibility=EnumEligibility.INELIGIBLE,
        ),
        OverrideRule(
            rule_id="code_only",
            target_code="000.010.000.030",
            enum_eligibility=EnumEligibility.REVIEW_REQUIRED,
        ),
    )

    # Act
    selection = select_applicable_override(entry, overrides)

    # Assert
    assert selection.selected_override is not None
    assert selection.selected_override.rule_id == "code_only"
    assert selection.conflict_detected is False


def test_select_applicable_override_detects_same_rank_conflict():
    # Arrange
    entry = build_normalized_entry(code="000.010.000.030")
    overrides = (
        OverrideRule(
            rule_id="code_override_a",
            target_code="000.010.000.030",
            enum_eligibility=EnumEligibility.INELIGIBLE,
        ),
        OverrideRule(
            rule_id="code_override_b",
            target_code="000.010.000.030",
            enum_eligibility=EnumEligibility.REVIEW_REQUIRED,
        ),
    )

    # Act
    selection = select_applicable_override(entry, overrides)

    # Assert
    assert selection.selected_override is None
    assert selection.conflict_detected is True
    assert selection.matched_rule_ids == (
        "code_override_a",
        "code_override_b",
    )


def test_build_semantic_field_policy_applies_override_outputs():
    # Arrange
    bundle = build_default_semantic_policy_bundle()
    bundle = SemanticPolicyBundle(
        metadata=bundle.metadata,
        base_type_policies_by_manual_type=bundle.base_type_policies_by_manual_type,
        reference_kind_policies=bundle.reference_kind_policies,
        serialization_pattern_refinements=bundle.serialization_pattern_refinements,
        wrapper_policies_by_name=bundle.wrapper_policies_by_name,
        overrides=(
            OverrideRule(
                rule_id="force_open_value",
                target_code="000.010.000.030",
                domain_shape_kind=DomainShapeKind.OPEN_CODED_VALUE,
                enum_eligibility=EnumEligibility.REVIEW_REQUIRED,
                presence_kind=PresenceKind.REQUIRED,
                cardinality_kind=CardinalityKind.REPEATED,
                normalized_name="nombre_forzado",
            ),
        ),
        validation_cases=bundle.validation_cases,
    )
    entry = build_normalized_entry(code="000.010.000.030")

    # Act
    field_policy = build_semantic_field_policy(entry, bundle)

    # Assert
    assert field_policy.domain_shape_kind == DomainShapeKind.OPEN_CODED_VALUE
    assert field_policy.enum_eligibility == EnumEligibility.REVIEW_REQUIRED
    assert field_policy.presence_kind == PresenceKind.REQUIRED
    assert field_policy.cardinality_kind == CardinalityKind.REPEATED
    assert field_policy.naming_policy.normalized_field_name == "nombre_forzado"
    assert "Applied override rule 'force_open_value'." in field_policy.notes

def test_get_choice_wrapper_policy_resolves_known_choice_wrappers():
    # Arrange
    bundle = build_default_semantic_policy_bundle()
    wrapper_names = (
        "FlexibleDatesType",
        "OfficialIdType",
        "EntityTypeType",
        "EntityNameType",
    )

    for wrapper_name in wrapper_names:
        # Act
        wrapper_policy = get_choice_wrapper_policy(wrapper_name, bundle)

        # Assert
        assert wrapper_policy is not None
        assert wrapper_policy.wrapper_policy_kind == (
            WrapperPolicyKind.CHOICE_OBJECT_CANDIDATE
        )
        assert (
            StructuralLimitationFlag.CHOICE_NOT_ENFORCED
            in wrapper_policy.structural_limitation_flags
        )


def test_get_choice_wrapper_policy_returns_none_for_unknown_wrapper():
    # Arrange
    bundle = build_default_semantic_policy_bundle()

    # Act
    wrapper_policy = get_choice_wrapper_policy("UnknownWrapperType", bundle)

    # Assert
    assert wrapper_policy is None


def test_validate_wrapper_case_resolves_wrapper_validation_cases():
    # Arrange
    bundle = build_default_semantic_policy_bundle()
    wrapper_cases = tuple(
        validation_case
        for validation_case in bundle.validation_cases
        if validation_case.wrapper_name is not None
    )

    # Act / Assert
    assert wrapper_cases
    for validation_case in wrapper_cases:
        wrapper_policy = validate_wrapper_case(validation_case, bundle)
        assert wrapper_policy is not None
        assert wrapper_policy.confidence == validation_case.expected_confidence


def test_get_wrapper_auto_application_limitation_documents_current_limit():
    # Act
    limitation = get_wrapper_auto_application_limitation()

    # Assert
    assert "NormalizedCodeEntry" in limitation
    assert "does not expose structural wrapper type names" in limitation

def test_validation_inventory_has_required_case_ids():
    # Arrange
    bundle = build_default_semantic_policy_bundle()
    case_ids = {validation_case.case_id for validation_case in bundle.validation_cases}

    # Assert
    assert "simple_scalar_name" in case_ids
    assert "compact_closed_enum_sex" in case_ids
    assert "compact_open_entity_type" in case_ids
    assert "subtype_backed_know" in case_ids
    assert "entity_side_package_registry" in case_ids
    assert "thesaurus_side_package_vocabulary" in case_ids
    assert "unesco_hierarchical_thematic" in case_ids
    assert "agency_unresolved_manual_only" in case_ids
    assert "intervention_under_traced" in case_ids
    assert "prueba_under_traced" in case_ids
    assert "flexible_dates_choice_wrapper" in case_ids
    assert "official_id_choice_wrapper" in case_ids
    assert "entity_type_choice_wrapper" in case_ids
    assert "entity_name_choice_wrapper" in case_ids


def test_validation_inventory_reference_cases_have_expected_outputs():
    # Arrange
    bundle = build_default_semantic_policy_bundle()
    reference_cases = tuple(
        validation_case
        for validation_case in bundle.validation_cases
        if validation_case.reference_name is not None
    )

    # Act / Assert
    assert reference_cases
    for validation_case in reference_cases:
        assert validation_case.expected_domain_shape_kind is not None
        assert validation_case.expected_enum_eligibility is not None
        assert validation_case.expected_confidence is not None


def test_validation_inventory_wrapper_cases_have_wrapper_names():
    # Arrange
    bundle = build_default_semantic_policy_bundle()
    wrapper_cases = tuple(
        validation_case
        for validation_case in bundle.validation_cases
        if validation_case.wrapper_name is not None
    )

    # Act / Assert
    assert wrapper_cases
    for validation_case in wrapper_cases:
        assert validation_case.expected_confidence is not None
        assert validate_wrapper_case(validation_case, bundle) is not None


def test_evaluate_reference_table_enum_eligibility_marks_closed_compact_table_eligible():

    # Arrange
    evidence = build_reference_table_enum_evidence(
        table_name="CVN_SEX_A",
        item_count=2,
    )
    # Act
    eligibility, confidence, reasons = evaluate_reference_table_enum_eligibility(
        evidence=evidence,
        source_family=ReferenceSourceFamily.REFERENCE_TABLE,
        semantic_kind=SemanticReferenceKind.COMPACT_ENUM_LIKE_TABLE,
        is_subtype_backed=False,
    )
    # Assert
    assert eligibility == EnumEligibility.ELIGIBLE
    assert confidence == PolicyConfidence.HIGH
    assert reasons == ("strict_enum_eligible",)

def test_evaluate_reference_table_enum_eligibility_requires_review_for_other_like_entry():
    # Arrange
    evidence = build_reference_table_enum_evidence(
        has_other_like_entry=True,
    )
    # Act
    eligibility, confidence, reasons = evaluate_reference_table_enum_eligibility(
        evidence=evidence,
        source_family=ReferenceSourceFamily.REFERENCE_TABLE,
        semantic_kind=SemanticReferenceKind.COMPACT_ENUM_LIKE_TABLE,
        is_subtype_backed=False,
    )
    # Assert
    assert eligibility == EnumEligibility.REVIEW_REQUIRED
    assert confidence == PolicyConfidence.REQUIRES_REVIEW
    assert "other_like_entry" in reasons

def test_evaluate_reference_table_enum_eligibility_rejects_subtype_backed_table():
    # Arrange
    evidence = build_reference_table_enum_evidence(table_name="CVN_KNOW_A")
    # Act
    eligibility, confidence, reasons = evaluate_reference_table_enum_eligibility(
        evidence=evidence,
        source_family=ReferenceSourceFamily.SUBTYPE_BACKED_TABLE,
        semantic_kind=SemanticReferenceKind.SUBTYPE_BACKED_CONTROLLED_FAMILY,
        is_subtype_backed=True,
    )
    # Assert
    assert eligibility == EnumEligibility.INELIGIBLE
    assert confidence == PolicyConfidence.HIGH
    assert "source_family_not_reference_table" in reasons
    assert "semantic_kind_not_compact_enum_like_table" in reasons
    assert "subtype_backed" in reasons

def test_evaluate_reference_table_enum_eligibility_rejects_hierarchical_table():
    # Arrange
    evidence = build_reference_table_enum_evidence(
        table_name="UNESCO_CODES",
        item_count=2513,
        has_hierarchy=True,
    )
    # Act
    eligibility, confidence, reasons = evaluate_reference_table_enum_eligibility(
        evidence=evidence,
        source_family=ReferenceSourceFamily.REFERENCE_TABLE,
        semantic_kind=SemanticReferenceKind.HIERARCHICAL_THEMATIC_CLASSIFICATION,
        is_subtype_backed=False,
    )
    # Assert
    assert eligibility == EnumEligibility.INELIGIBLE
    assert confidence == PolicyConfidence.HIGH
    assert "semantic_kind_not_compact_enum_like_table" in reasons
    assert "hierarchy_present" in reasons

def test_evaluate_reference_table_enum_eligibility_rejects_side_package_registry():
    # Act
    eligibility, confidence, reasons = evaluate_reference_table_enum_eligibility(
        evidence=None,
        source_family=ReferenceSourceFamily.SIDE_PACKAGE_REGISTRY,
        semantic_kind=SemanticReferenceKind.SIDE_PACKAGE_REGISTRY,
        is_subtype_backed=False,
    )
    # Assert
    assert eligibility == EnumEligibility.INELIGIBLE
    assert confidence == PolicyConfidence.HIGH
    assert "source_family_not_reference_table" in reasons
    assert "missing_enum_evidence" in reasons

def test_evaluate_reference_table_enum_eligibility_rejects_unresolved_reference():
    # Act
    eligibility, confidence, reasons = evaluate_reference_table_enum_eligibility(
        evidence=None,
        source_family=ReferenceSourceFamily.UNRESOLVED_MANUAL_ONLY,
        semantic_kind=SemanticReferenceKind.UNRESOLVED_MANUAL_ONLY_REFERENCE,
        is_subtype_backed=False,
    )
    # Assert
    assert eligibility == EnumEligibility.INELIGIBLE
    assert confidence == PolicyConfidence.HIGH
    assert "source_family_not_reference_table" in reasons
    assert "missing_enum_evidence" in reasons

def test_evaluate_reference_table_enum_eligibility_rejects_missing_evidence():
    # Act
    eligibility, confidence, reasons = evaluate_reference_table_enum_eligibility(
        evidence=None,
        source_family=ReferenceSourceFamily.REFERENCE_TABLE,
        semantic_kind=SemanticReferenceKind.COMPACT_ENUM_LIKE_TABLE,
        is_subtype_backed=False,
    )
    # Assert
    assert eligibility == EnumEligibility.INELIGIBLE
    assert confidence == PolicyConfidence.HIGH
    assert "missing_enum_evidence" in reasons

def test_max_strict_enum_item_count_is_repository_policy_constant():
    # Assert
    assert MAX_STRICT_ENUM_ITEM_COUNT == 64

def test_real_cvn_sex_a_enum_evidence_is_eligible():
    # Arrange
    auxiliary_bundle = build_real_auxiliary_bundle()
    resolution = resolve_manual_reference(
        raw_reference="CVN_SEX_A",
        auxiliary_bundle=auxiliary_bundle,
    )

    # Act
    eligibility, confidence, reasons = evaluate_reference_table_enum_eligibility(
        evidence=resolution.reference_table_enum_evidence,
        source_family=resolution.source_family,
        semantic_kind=resolution.semantic_kind,
        is_subtype_backed=resolution.is_subtype_backed,
    )

    # Assert
    assert resolution.reference_table_enum_evidence is not None
    assert resolution.reference_table_enum_evidence.table_name == "CVN_SEX_A"
    assert resolution.reference_table_enum_evidence.item_count == 2
    assert resolution.reference_table_enum_evidence.has_delegate is False
    assert resolution.reference_table_enum_evidence.has_hierarchy is False
    assert eligibility == EnumEligibility.ELIGIBLE
    assert confidence == PolicyConfidence.HIGH
    assert reasons == ("strict_enum_eligible",)


def test_real_cvn_entity_type_enum_evidence_is_ineligible_by_delegate():
    # Arrange
    auxiliary_bundle = build_real_auxiliary_bundle()
    resolution = resolve_manual_reference(
        raw_reference="CVN_ENTITY_TYPE",
        auxiliary_bundle=auxiliary_bundle,
    )

    # Act
    eligibility, confidence, reasons = evaluate_reference_table_enum_eligibility(
        evidence=resolution.reference_table_enum_evidence,
        source_family=resolution.source_family,
        semantic_kind=resolution.semantic_kind,
        is_subtype_backed=resolution.is_subtype_backed,
    )

    # Assert
    assert resolution.reference_table_enum_evidence is not None
    assert resolution.reference_table_enum_evidence.table_name == "CVN_ENTITY_TYPE"
    assert resolution.reference_table_enum_evidence.item_count == 17
    assert resolution.reference_table_enum_evidence.has_delegate is True
    assert (
        "delegate_present"
        in resolution.reference_table_enum_evidence.open_world_signals
    )
    assert eligibility == EnumEligibility.INELIGIBLE
    assert confidence == PolicyConfidence.HIGH
    assert "delegate_present" in reasons


def test_real_cvn_know_a_subtype_backed_table_remains_ineligible():
    # Arrange
    auxiliary_bundle = build_real_auxiliary_bundle()
    resolution = resolve_manual_reference(
        raw_reference="CVN_KNOW_A",
        auxiliary_bundle=auxiliary_bundle,
    )

    # Act
    eligibility, confidence, reasons = evaluate_reference_table_enum_eligibility(
        evidence=resolution.reference_table_enum_evidence,
        source_family=resolution.source_family,
        semantic_kind=resolution.semantic_kind,
        is_subtype_backed=resolution.is_subtype_backed,
    )

    # Assert
    assert resolution.reference_table_enum_evidence is not None
    assert resolution.reference_table_enum_evidence.table_name == "CVN_KNOW_A"
    assert eligibility == EnumEligibility.INELIGIBLE
    assert confidence == PolicyConfidence.HIGH
    assert "source_family_not_reference_table" in reasons
    assert "subtype_backed" in reasons


def test_real_unesco_codes_hierarchical_table_remains_ineligible():
    # Arrange
    auxiliary_bundle = build_real_auxiliary_bundle()
    resolution = resolve_manual_reference(
        raw_reference="UNESCO_CODES",
        auxiliary_bundle=auxiliary_bundle,
    )

    # Act
    eligibility, confidence, reasons = evaluate_reference_table_enum_eligibility(
        evidence=resolution.reference_table_enum_evidence,
        source_family=resolution.source_family,
        semantic_kind=resolution.semantic_kind,
        is_subtype_backed=resolution.is_subtype_backed,
    )

    # Assert
    assert resolution.reference_table_enum_evidence is not None
    assert resolution.reference_table_enum_evidence.table_name == "UNESCO_CODES"
    assert resolution.reference_table_enum_evidence.has_hierarchy is True
    assert eligibility == EnumEligibility.INELIGIBLE
    assert confidence == PolicyConfidence.HIGH
    assert "semantic_kind_not_compact_enum_like_table" in reasons
    assert "hierarchy_present" in reasons
