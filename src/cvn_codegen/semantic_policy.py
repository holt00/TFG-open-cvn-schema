from dataclasses import dataclass
from enum import Enum


from cvn_codegen.normalization_types import (
    NormalizedCodeEntry,
    SemanticReferenceKind,
    SerializationPattern,
)


class SemanticBaseKind(str, Enum):
    """Classify the semantic base kind inferred from normalized manual metadata."""

    TEXT = "text"
    CONTROLLED_REFERENCE = "controlled_reference"
    DATE_LIKE = "date_like"
    DECIMAL_NUMBER = "decimal_number"
    BOOLEAN = "boolean"
    DURATION_LIKE = "duration_like"
    UNKNOWN = "unknown"

class WrapperPolicyKind(str, Enum):
    """Classify how structural XML wrapper types should be handled semantically."""

    COLLAPSE = "collapse"
    VALUE_OBJECT_CANDIDATE = "value_object_candidate"
    CHOICE_OBJECT_CANDIDATE = "choice_object_candidate"
    PRESERVE_STRUCTURAL_TRACE = "preserve_structural_trace"

class PresenceKind(str, Enum):
    """Classify semantic field presence."""

    REQUIRED = "required"
    OPTIONAL = "optional"
    UNKNOWN = "unknown"

class CardinalityKind(str, Enum):
    """Classify semantic field cardinality."""

    SINGLE = "single"
    REPEATED = "repeated"
    UNKNOWN = "unknown"

class StructuralLimitationFlag(str, Enum):
    """Record structural limitations that semantic policy must preserve."""

    CHOICE_NOT_ENFORCED = "choice_not_enforced"
    LIST_MIN_OCCURS_WEAK = "list_min_occurs_weak"
    OBJECT_TYPED_ATTRIBUTE = "object_typed_attribute"
    WRAPPER_ERGONOMICS = "wrapper_ergonomics"

class DomainShapeKind(str, Enum):
    """Classify intended domain-facing representation shape."""

    PLAIN_VALUE = "plain_value"
    STRICT_ENUM_CANDIDATE = "strict_enum_candidate"
    OPEN_CODED_VALUE = "open_coded_value"
    MEASURE_OR_SCALE_VALUE = "measure_or_scale_value"
    IDENTIFIER_REFERENCE = "identifier_reference"
    SCOPE_REFERENCE = "scope_reference"
    SUBTYPE_BACKED_VALUE = "subtype_backed_value"
    HIERARCHICAL_CODE_REFERENCE = "hierarchical_code_reference"
    REGISTRY_REFERENCE = "registry_reference"
    VOCABULARY_REFERENCE = "vocabulary_reference"
    UNRESOLVED_REFERENCE = "unresolved_reference"
    UNDER_TRACED_REFERENCE = "under_traced_reference"

class PolicyConfidence(str, Enum):
    """Classify confidence in a semantic policy decision."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    REQUIRES_REVIEW = "requires_review"

class EnumEligibility(str, Enum):
    """Classify whether a controlled reference may become a strict enum."""

    ELIGIBLE = "eligible"
    INELIGIBLE = "ineligible"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class PolicyMetadata:
    """Describe the semantic policy bundle version and scope."""

    policy_name: str
    policy_version: str
    source_issue: str
    notes: tuple[str, ...] = ()

@dataclass(frozen=True)
class SemanticDecisionTrace:
    """Preserve traceability for one semantic policy decision."""

    code: str
    xml_paths: tuple[str, ...]
    manual_reference_table: str | None
    reference_source_family: str | None
    reference_source_artifact: str | None
    serialization_pattern: SerializationPattern | None
    semantic_reference_kind: SemanticReferenceKind | None
    applied_rules: tuple[str, ...]
    diagnostics: tuple[str, ...] = ()

@dataclass(frozen=True)
class BaseTypePolicy:
    """Map one normalized manual type to a semantic base kind."""

    manual_type: str | None
    base_kind: SemanticBaseKind
    confidence: PolicyConfidence
    notes: tuple[str, ...] = ()

@dataclass(frozen=True)
class ReferenceKindPolicy:
    """Map one normalized reference kind to a domain-shape decision."""

    semantic_reference_kind: SemanticReferenceKind
    domain_shape_kind: DomainShapeKind
    fallback_shape_kind: DomainShapeKind
    enum_eligibility: EnumEligibility
    confidence: PolicyConfidence
    notes: tuple[str, ...] = ()

@dataclass(frozen=True)
class NamingPolicy:
    """Describe domain-facing naming decisions for one normalized entry."""

    normalized_field_name: str
    normalized_class_name: str | None
    naming_confidence: PolicyConfidence
    source_label: str | None
    notes: tuple[str, ...] = ()

@dataclass(frozen=True)
class MultiplicityPolicy:
    """Describe semantic presence and cardinality for one normalized entry."""

    presence_kind: PresenceKind
    cardinality_kind: CardinalityKind
    confidence: PolicyConfidence
    notes: tuple[str, ...] = ()

@dataclass(frozen=True)
class ChoiceWrapperPolicy:
    """Describe semantic handling for one structural wrapper type."""

    wrapper_name: str
    wrapper_policy_kind: WrapperPolicyKind
    structural_limitation_flags: tuple[StructuralLimitationFlag, ...]
    confidence: PolicyConfidence
    notes: tuple[str, ...] = ()

@dataclass(frozen=True)
class OverrideRule:
    """Represent one explicit semantic-policy override."""

    rule_id: str
    target_code: str | None = None
    target_xml_path: str | None = None
    target_semantic_reference_kind: SemanticReferenceKind | None = None
    target_serialization_pattern: SerializationPattern | None = None
    domain_shape_kind: DomainShapeKind | None = None
    fallback_shape_kind: DomainShapeKind | None = None
    enum_eligibility: EnumEligibility | None = None
    policy_confidence: PolicyConfidence | None = None
    wrapper_policy_kind: WrapperPolicyKind | None = None
    presence_kind: PresenceKind | None = None
    cardinality_kind: CardinalityKind | None = None
    normalized_name: str | None = None
    structural_limitation_flags: tuple[StructuralLimitationFlag, ...] = ()
    notes: tuple[str, ...] = ()

@dataclass(frozen=True)
class ValidationCaseDefinition:
    """Describe one representative case used to validate semantic policy."""

    case_id: str
    role: str
    code: str | None = None
    reference_name: str | None = None
    wrapper_name: str | None = None
    expected_base_kind: SemanticBaseKind | None = None
    expected_domain_shape_kind: DomainShapeKind | None = None
    expected_enum_eligibility: EnumEligibility | None = None
    expected_confidence: PolicyConfidence | None = None
    notes: tuple[str, ...] = ()

@dataclass(frozen=True)
class SemanticFieldPolicy:
    """Store final semantic policy decision for one normalized field."""

    code: str
    xml_paths: tuple[str, ...]
    base_kind: SemanticBaseKind
    domain_shape_kind: DomainShapeKind
    fallback_shape_kind: DomainShapeKind | None
    enum_eligibility: EnumEligibility
    presence_kind: PresenceKind
    cardinality_kind: CardinalityKind
    policy_confidence: PolicyConfidence
    naming_policy: NamingPolicy
    structural_limitation_flags: tuple[StructuralLimitationFlag, ...]
    decision_trace: SemanticDecisionTrace
    notes: tuple[str, ...] = ()

@dataclass(frozen=True)
class SemanticPolicyBundle:
    """Store the complete semantic policy contract consumed by later generation."""

    metadata: PolicyMetadata
    base_type_policies_by_manual_type: dict[str, BaseTypePolicy]
    reference_kind_policies: dict[SemanticReferenceKind, ReferenceKindPolicy]
    serialization_pattern_refinements: dict[
        SerializationPattern,
        ReferenceKindPolicy,
    ]
    wrapper_policies_by_name: dict[str, ChoiceWrapperPolicy]
    overrides: tuple[OverrideRule, ...] = ()
    validation_cases: tuple[ValidationCaseDefinition, ...] = ()

def build_default_semantic_policy_bundle() -> SemanticPolicyBundle:
    """Build the default semantic policy bundle for issue #14."""

    return SemanticPolicyBundle(
        metadata=PolicyMetadata(
            policy_name="default_cvn_semantic_policy",
            policy_version="0.1.0",
            source_issue="#14",
            notes=(
                "Default semantic policy for enriched CVN normalization output.",
                "Final domain model generation remains deferred to issue #15.",
            ),
        ),
        base_type_policies_by_manual_type={
            "Alphanumeric": BaseTypePolicy(
                manual_type="Alphanumeric",
                base_kind=SemanticBaseKind.TEXT,
                confidence=PolicyConfidence.HIGH,
                notes=(
                    "Alphanumeric maps to text unless a resolved controlled reference is present.",
                ),
            ),
            "Date": BaseTypePolicy(
                manual_type="Date",
                base_kind=SemanticBaseKind.DATE_LIKE,
                confidence=PolicyConfidence.HIGH,
            ),
            "Double": BaseTypePolicy(
                manual_type="Double",
                base_kind=SemanticBaseKind.DECIMAL_NUMBER,
                confidence=PolicyConfidence.HIGH,
            ),
            "Boolean": BaseTypePolicy(
                manual_type="Boolean",
                base_kind=SemanticBaseKind.BOOLEAN,
                confidence=PolicyConfidence.HIGH,
            ),
            "Duration": BaseTypePolicy(
                manual_type="Duration",
                base_kind=SemanticBaseKind.DURATION_LIKE,
                confidence=PolicyConfidence.HIGH,
            ),
        },
        reference_kind_policies={
            SemanticReferenceKind.COMPACT_ENUM_LIKE_TABLE: ReferenceKindPolicy(
                semantic_reference_kind=SemanticReferenceKind.COMPACT_ENUM_LIKE_TABLE,
                domain_shape_kind=DomainShapeKind.STRICT_ENUM_CANDIDATE,
                fallback_shape_kind=DomainShapeKind.OPEN_CODED_VALUE,
                enum_eligibility=EnumEligibility.REVIEW_REQUIRED,
                confidence=PolicyConfidence.REQUIRES_REVIEW,
                notes=(
                    "Compact enum-like tables need eligibility checks before strict enum generation.",
                ),
            ),
            SemanticReferenceKind.COMPACT_SCALE_OR_MEASURE: ReferenceKindPolicy(
                semantic_reference_kind=SemanticReferenceKind.COMPACT_SCALE_OR_MEASURE,
                domain_shape_kind=DomainShapeKind.MEASURE_OR_SCALE_VALUE,
                fallback_shape_kind=DomainShapeKind.OPEN_CODED_VALUE,
                enum_eligibility=EnumEligibility.REVIEW_REQUIRED,
                confidence=PolicyConfidence.MEDIUM,
            ),
            SemanticReferenceKind.IDENTIFIER_TYPE_TABLE: ReferenceKindPolicy(
                semantic_reference_kind=SemanticReferenceKind.IDENTIFIER_TYPE_TABLE,
                domain_shape_kind=DomainShapeKind.IDENTIFIER_REFERENCE,
                fallback_shape_kind=DomainShapeKind.OPEN_CODED_VALUE,
                enum_eligibility=EnumEligibility.INELIGIBLE,
                confidence=PolicyConfidence.MEDIUM,
            ),
            SemanticReferenceKind.SCOPE_TABLE: ReferenceKindPolicy(
                semantic_reference_kind=SemanticReferenceKind.SCOPE_TABLE,
                domain_shape_kind=DomainShapeKind.SCOPE_REFERENCE,
                fallback_shape_kind=DomainShapeKind.OPEN_CODED_VALUE,
                enum_eligibility=EnumEligibility.REVIEW_REQUIRED,
                confidence=PolicyConfidence.MEDIUM,
            ),
            SemanticReferenceKind.SUBTYPE_BACKED_CONTROLLED_FAMILY: ReferenceKindPolicy(
                semantic_reference_kind=SemanticReferenceKind.SUBTYPE_BACKED_CONTROLLED_FAMILY,
                domain_shape_kind=DomainShapeKind.SUBTYPE_BACKED_VALUE,
                fallback_shape_kind=DomainShapeKind.SUBTYPE_BACKED_VALUE,
                enum_eligibility=EnumEligibility.INELIGIBLE,
                confidence=PolicyConfidence.MEDIUM,
                notes=(
                    "Subtype_Spa.xml proves subtype catalog availability but not a strict per-table bridge.",
                ),
            ),
            SemanticReferenceKind.HIERARCHICAL_THEMATIC_CLASSIFICATION: ReferenceKindPolicy(
                semantic_reference_kind=SemanticReferenceKind.HIERARCHICAL_THEMATIC_CLASSIFICATION,
                domain_shape_kind=DomainShapeKind.HIERARCHICAL_CODE_REFERENCE,
                fallback_shape_kind=DomainShapeKind.HIERARCHICAL_CODE_REFERENCE,
                enum_eligibility=EnumEligibility.INELIGIBLE,
                confidence=PolicyConfidence.HIGH,
            ),
            SemanticReferenceKind.SIDE_PACKAGE_REGISTRY: ReferenceKindPolicy(
                semantic_reference_kind=SemanticReferenceKind.SIDE_PACKAGE_REGISTRY,
                domain_shape_kind=DomainShapeKind.REGISTRY_REFERENCE,
                fallback_shape_kind=DomainShapeKind.REGISTRY_REFERENCE,
                enum_eligibility=EnumEligibility.INELIGIBLE,
                confidence=PolicyConfidence.HIGH,
            ),
            SemanticReferenceKind.SIDE_PACKAGE_THESAURUS_OR_VOCABULARY: ReferenceKindPolicy(
                semantic_reference_kind=SemanticReferenceKind.SIDE_PACKAGE_THESAURUS_OR_VOCABULARY,
                domain_shape_kind=DomainShapeKind.VOCABULARY_REFERENCE,
                fallback_shape_kind=DomainShapeKind.VOCABULARY_REFERENCE,
                enum_eligibility=EnumEligibility.INELIGIBLE,
                confidence=PolicyConfidence.HIGH,
            ),
            SemanticReferenceKind.UNRESOLVED_MANUAL_ONLY_REFERENCE: ReferenceKindPolicy(
                semantic_reference_kind=SemanticReferenceKind.UNRESOLVED_MANUAL_ONLY_REFERENCE,
                domain_shape_kind=DomainShapeKind.UNRESOLVED_REFERENCE,
                fallback_shape_kind=DomainShapeKind.UNRESOLVED_REFERENCE,
                enum_eligibility=EnumEligibility.INELIGIBLE,
                confidence=PolicyConfidence.REQUIRES_REVIEW,
            ),
            SemanticReferenceKind.UNDER_TRACED_REFERENCE_TABLE: ReferenceKindPolicy(
                semantic_reference_kind=SemanticReferenceKind.UNDER_TRACED_REFERENCE_TABLE,
                domain_shape_kind=DomainShapeKind.UNDER_TRACED_REFERENCE,
                fallback_shape_kind=DomainShapeKind.UNDER_TRACED_REFERENCE,
                enum_eligibility=EnumEligibility.INELIGIBLE,
                confidence=PolicyConfidence.REQUIRES_REVIEW,
            ),
        },
        serialization_pattern_refinements={
            SerializationPattern.QUALITY_MEASURE: ReferenceKindPolicy(
                semantic_reference_kind=SemanticReferenceKind.COMPACT_SCALE_OR_MEASURE,
                domain_shape_kind=DomainShapeKind.MEASURE_OR_SCALE_VALUE,
                fallback_shape_kind=DomainShapeKind.OPEN_CODED_VALUE,
                enum_eligibility=EnumEligibility.REVIEW_REQUIRED,
                confidence=PolicyConfidence.MEDIUM,
            ),
            SerializationPattern.EXTERNAL_PK_TYPE: ReferenceKindPolicy(
                semantic_reference_kind=SemanticReferenceKind.IDENTIFIER_TYPE_TABLE,
                domain_shape_kind=DomainShapeKind.IDENTIFIER_REFERENCE,
                fallback_shape_kind=DomainShapeKind.OPEN_CODED_VALUE,
                enum_eligibility=EnumEligibility.INELIGIBLE,
                confidence=PolicyConfidence.MEDIUM,
            ),
            SerializationPattern.SCOPE_TYPE: ReferenceKindPolicy(
                semantic_reference_kind=SemanticReferenceKind.SCOPE_TABLE,
                domain_shape_kind=DomainShapeKind.SCOPE_REFERENCE,
                fallback_shape_kind=DomainShapeKind.OPEN_CODED_VALUE,
                enum_eligibility=EnumEligibility.REVIEW_REQUIRED,
                confidence=PolicyConfidence.MEDIUM,
            ),
            SerializationPattern.SUBTYPE: ReferenceKindPolicy(
                semantic_reference_kind=SemanticReferenceKind.SUBTYPE_BACKED_CONTROLLED_FAMILY,
                domain_shape_kind=DomainShapeKind.SUBTYPE_BACKED_VALUE,
                fallback_shape_kind=DomainShapeKind.SUBTYPE_BACKED_VALUE,
                enum_eligibility=EnumEligibility.INELIGIBLE,
                confidence=PolicyConfidence.MEDIUM,
                notes=(
                    "Subtype serialization requires subtype-backed representation.",
                ),
            ),
            SerializationPattern.SIDE_PACKAGE_REGISTRY: ReferenceKindPolicy(
                semantic_reference_kind=SemanticReferenceKind.SIDE_PACKAGE_REGISTRY,
                domain_shape_kind=DomainShapeKind.REGISTRY_REFERENCE,
                fallback_shape_kind=DomainShapeKind.REGISTRY_REFERENCE,
                enum_eligibility=EnumEligibility.INELIGIBLE,
                confidence=PolicyConfidence.HIGH,
            ),
            SerializationPattern.SIDE_PACKAGE_THESAURUS: ReferenceKindPolicy(
                semantic_reference_kind=SemanticReferenceKind.SIDE_PACKAGE_THESAURUS_OR_VOCABULARY,
                domain_shape_kind=DomainShapeKind.VOCABULARY_REFERENCE,
                fallback_shape_kind=DomainShapeKind.VOCABULARY_REFERENCE,
                enum_eligibility=EnumEligibility.INELIGIBLE,
                confidence=PolicyConfidence.HIGH,
            ),
            SerializationPattern.UNRESOLVED: ReferenceKindPolicy(
                semantic_reference_kind=SemanticReferenceKind.UNRESOLVED_MANUAL_ONLY_REFERENCE,
                domain_shape_kind=DomainShapeKind.UNRESOLVED_REFERENCE,
                fallback_shape_kind=DomainShapeKind.UNRESOLVED_REFERENCE,
                enum_eligibility=EnumEligibility.INELIGIBLE,
                confidence=PolicyConfidence.REQUIRES_REVIEW,
            ),
            SerializationPattern.SUBJECT_DESCRIPTION: ReferenceKindPolicy(
                semantic_reference_kind=SemanticReferenceKind.HIERARCHICAL_THEMATIC_CLASSIFICATION,
                domain_shape_kind=DomainShapeKind.HIERARCHICAL_CODE_REFERENCE,
                fallback_shape_kind=DomainShapeKind.HIERARCHICAL_CODE_REFERENCE,
                enum_eligibility=EnumEligibility.INELIGIBLE,
                confidence=PolicyConfidence.HIGH,
            ),
        },
        wrapper_policies_by_name={
            "FlexibleDatesType": ChoiceWrapperPolicy(
                wrapper_name="FlexibleDatesType",
                wrapper_policy_kind=WrapperPolicyKind.CHOICE_OBJECT_CANDIDATE,
                structural_limitation_flags=(
                    StructuralLimitationFlag.CHOICE_NOT_ENFORCED,
                    StructuralLimitationFlag.WRAPPER_ERGONOMICS,
                ),
                confidence=PolicyConfidence.HIGH,
                notes=(
                    "Flexible date wrapper represents meaningful date-granularity choice.",
                ),
            ),
            "OfficialIdType": ChoiceWrapperPolicy(
                wrapper_name="OfficialIdType",
                wrapper_policy_kind=WrapperPolicyKind.CHOICE_OBJECT_CANDIDATE,
                structural_limitation_flags=(
                    StructuralLimitationFlag.CHOICE_NOT_ENFORCED,
                    StructuralLimitationFlag.WRAPPER_ERGONOMICS,
                ),
                confidence=PolicyConfidence.HIGH,
                notes=(
                    "Official identifier wrapper represents mutually exclusive identifier alternatives.",
                ),
            ),
            "EntityTypeType": ChoiceWrapperPolicy(
                wrapper_name="EntityTypeType",
                wrapper_policy_kind=WrapperPolicyKind.CHOICE_OBJECT_CANDIDATE,
                structural_limitation_flags=(
                    StructuralLimitationFlag.CHOICE_NOT_ENFORCED,
                    StructuralLimitationFlag.WRAPPER_ERGONOMICS,
                ),
                confidence=PolicyConfidence.HIGH,
                notes=(
                    "Entity type wrapper carries semantic choice over entity classification.",
                ),
            ),
            "EntityNameType": ChoiceWrapperPolicy(
                wrapper_name="EntityNameType",
                wrapper_policy_kind=WrapperPolicyKind.CHOICE_OBJECT_CANDIDATE,
                structural_limitation_flags=(
                    StructuralLimitationFlag.CHOICE_NOT_ENFORCED,
                    StructuralLimitationFlag.WRAPPER_ERGONOMICS,
                ),
                confidence=PolicyConfidence.HIGH,
                notes=(
                    "Entity name wrapper carries semantic choice over entity-name variants.",
                ),
            ),
        },
        overrides=(),
        validation_cases=(
            ValidationCaseDefinition(
                case_id="simple_scalar_name",
                role="simple scalar field",
                code="000.010.000.020",
                expected_base_kind=SemanticBaseKind.TEXT,
                expected_domain_shape_kind=DomainShapeKind.PLAIN_VALUE,
                expected_enum_eligibility=EnumEligibility.INELIGIBLE,
                expected_confidence=PolicyConfidence.HIGH,
            ),
            ValidationCaseDefinition(
                case_id="compact_closed_enum_sex",
                role="compact closed enum-like table",
                code="000.010.000.030",
                reference_name="CVN_SEX_A",
                expected_base_kind=SemanticBaseKind.CONTROLLED_REFERENCE,
                expected_domain_shape_kind=DomainShapeKind.STRICT_ENUM_CANDIDATE,
                expected_enum_eligibility=EnumEligibility.ELIGIBLE,
                expected_confidence=PolicyConfidence.HIGH,
            ),
            ValidationCaseDefinition(
                case_id="compact_open_entity_type",
                role="compact open or review controlled table",
                code="010.010.000.040",
                reference_name="CVN_ENTITY_TYPE",
                expected_base_kind=SemanticBaseKind.CONTROLLED_REFERENCE,
                expected_domain_shape_kind=DomainShapeKind.OPEN_CODED_VALUE,
                expected_enum_eligibility=EnumEligibility.REVIEW_REQUIRED,
                expected_confidence=PolicyConfidence.REQUIRES_REVIEW,
            ),
            ValidationCaseDefinition(
                case_id="subtype_backed_know",
                role="subtype-backed controlled family",
                code="050.030.010.030",
                reference_name="CVN_KNOW_A",
                expected_base_kind=SemanticBaseKind.CONTROLLED_REFERENCE,
                expected_domain_shape_kind=DomainShapeKind.SUBTYPE_BACKED_VALUE,
                expected_enum_eligibility=EnumEligibility.INELIGIBLE,
                expected_confidence=PolicyConfidence.MEDIUM,
            ),
            ValidationCaseDefinition(
                case_id="entity_side_package_registry",
                role="side-package registry reference",
                code="010.010.000.020",
                reference_name="ENTITY@Entity.xsd",
                expected_base_kind=SemanticBaseKind.CONTROLLED_REFERENCE,
                expected_domain_shape_kind=DomainShapeKind.REGISTRY_REFERENCE,
                expected_enum_eligibility=EnumEligibility.INELIGIBLE,
                expected_confidence=PolicyConfidence.HIGH,
            ),
            ValidationCaseDefinition(
                case_id="thesaurus_side_package_vocabulary",
                role="side-package vocabulary reference",
                code="010.010.000.260",
                reference_name="THESAURUS@thesaurus.xsd",
                expected_base_kind=SemanticBaseKind.CONTROLLED_REFERENCE,
                expected_domain_shape_kind=DomainShapeKind.VOCABULARY_REFERENCE,
                expected_enum_eligibility=EnumEligibility.INELIGIBLE,
                expected_confidence=PolicyConfidence.HIGH,
            ),
            ValidationCaseDefinition(
                case_id="unesco_hierarchical_thematic",
                role="hierarchical thematic classification",
                code="010.010.000.220",
                reference_name="UNESCO_CODES",
                expected_base_kind=SemanticBaseKind.CONTROLLED_REFERENCE,
                expected_domain_shape_kind=DomainShapeKind.HIERARCHICAL_CODE_REFERENCE,
                expected_enum_eligibility=EnumEligibility.INELIGIBLE,
                expected_confidence=PolicyConfidence.HIGH,
            ),
            ValidationCaseDefinition(
                case_id="agency_unresolved_manual_only",
                role="unresolved manual-only reference",
                code="060.010.000.030",
                reference_name="CVN_AGENCY_C",
                expected_base_kind=SemanticBaseKind.CONTROLLED_REFERENCE,
                expected_domain_shape_kind=DomainShapeKind.UNRESOLVED_REFERENCE,
                expected_enum_eligibility=EnumEligibility.INELIGIBLE,
                expected_confidence=PolicyConfidence.REQUIRES_REVIEW,
            ),
            ValidationCaseDefinition(
                case_id="intervention_under_traced",
                role="under-traced reference table",
                reference_name="CVN_INTERVENTION_A",
                expected_domain_shape_kind=DomainShapeKind.UNDER_TRACED_REFERENCE,
                expected_enum_eligibility=EnumEligibility.INELIGIBLE,
                expected_confidence=PolicyConfidence.REQUIRES_REVIEW,
            ),
            ValidationCaseDefinition(
                case_id="prueba_under_traced",
                role="under-traced reference table",
                reference_name="CVN_PRUEBA",
                expected_domain_shape_kind=DomainShapeKind.UNDER_TRACED_REFERENCE,
                expected_enum_eligibility=EnumEligibility.INELIGIBLE,
                expected_confidence=PolicyConfidence.REQUIRES_REVIEW,
            ),
            ValidationCaseDefinition(
                case_id="flexible_dates_choice_wrapper",
                role="xs:choice date wrapper",
                wrapper_name="FlexibleDatesType",
                expected_confidence=PolicyConfidence.HIGH,
            ),
            ValidationCaseDefinition(
                case_id="official_id_choice_wrapper",
                role="xs:choice identifier wrapper",
                wrapper_name="OfficialIdType",
                expected_confidence=PolicyConfidence.HIGH,
            ),
            ValidationCaseDefinition(
                case_id="entity_type_choice_wrapper",
                role="xs:choice entity type wrapper",
                wrapper_name="EntityTypeType",
                expected_confidence=PolicyConfidence.HIGH,
            ),
            ValidationCaseDefinition(
                case_id="entity_name_choice_wrapper",
                role="xs:choice entity name wrapper",
                wrapper_name="EntityNameType",
                expected_confidence=PolicyConfidence.HIGH,
            ),
        ),
    )


def build_semantic_field_policy(
    entry: NormalizedCodeEntry,
    bundle: SemanticPolicyBundle,
) -> SemanticFieldPolicy:
    """Build the semantic policy decision for one normalized CVN entry."""

    manual_entry = entry.manual
    reference_resolution = entry.reference_resolution
    xml_paths = tuple(tree_path.xml_path for tree_path in entry.tree_paths)
    manual_type = None
    manual_reference_table = None
    manual_name = None
    if manual_entry is not None:
        manual_type = manual_entry.manual_type
        manual_reference_table = manual_entry.manual_reference_table
        manual_name = manual_entry.manual_name
    base_kind = SemanticBaseKind.UNKNOWN
    base_confidence = PolicyConfidence.REQUIRES_REVIEW
    base_rule = "base_type_unknown"
    base_type_policy = None
    if manual_type is not None:
        base_type_policy = bundle.base_type_policies_by_manual_type.get(manual_type)
    if (
        manual_type == "Alphanumeric"
        and reference_resolution is not None
        and reference_resolution.semantic_kind is not None
    ):
        base_kind = SemanticBaseKind.CONTROLLED_REFERENCE
        base_confidence = PolicyConfidence.HIGH
        base_rule = "alphanumeric_with_controlled_reference"
    elif base_type_policy is not None:
        base_kind = base_type_policy.base_kind
        base_confidence = base_type_policy.confidence
        base_rule = f"manual_type:{manual_type}"
    
    domain_shape_kind = DomainShapeKind.PLAIN_VALUE
    fallback_shape_kind = None
    enum_eligibility = EnumEligibility.INELIGIBLE
    policy_confidence = base_confidence
    reference_rule = "no_reference"
    reference_kind_policy = None
    semantic_kind = None
    if reference_resolution is not None:
        semantic_kind = reference_resolution.semantic_kind

    if semantic_kind is not None:
        reference_kind_policy = bundle.reference_kind_policies.get(
            semantic_kind
        )
    if reference_kind_policy is not None and semantic_kind is not None:
        domain_shape_kind = reference_kind_policy.domain_shape_kind
        fallback_shape_kind = reference_kind_policy.fallback_shape_kind
        enum_eligibility = reference_kind_policy.enum_eligibility
        policy_confidence = reference_kind_policy.confidence
        reference_rule = f"semantic_kind:{semantic_kind.value}"
    serialization_refinement = None
    reference_serialization_pattern = None
    if reference_resolution is not None:
        reference_serialization_pattern = reference_resolution.serialization_pattern

    if reference_serialization_pattern is not None:
        serialization_refinement = bundle.serialization_pattern_refinements.get(
            reference_serialization_pattern
        )
    if (
        serialization_refinement is not None
        and reference_serialization_pattern is not None
    ):
        domain_shape_kind = serialization_refinement.domain_shape_kind
        fallback_shape_kind = serialization_refinement.fallback_shape_kind
        enum_eligibility = serialization_refinement.enum_eligibility
        policy_confidence = serialization_refinement.confidence
        reference_rule = (
            f"serialization_pattern:{reference_serialization_pattern.value}"
        )
    presence_kind = PresenceKind.UNKNOWN
    cardinality_kind = CardinalityKind.UNKNOWN
    multiplicity_rule = "multiplicity_unknown"
    if manual_entry is not None:
        if manual_entry.manual_obligatory is True:
            presence_kind = PresenceKind.REQUIRED
        elif manual_entry.manual_obligatory is False:
            presence_kind = PresenceKind.OPTIONAL
        if manual_entry.manual_multiplicity is True:
            cardinality_kind = CardinalityKind.REPEATED
        elif manual_entry.manual_multiplicity is False:
            cardinality_kind = CardinalityKind.SINGLE
        multiplicity_rule = "manual_presence_and_cardinality"
    
    source_label = manual_name
    normalized_field_name = entry.code.replace(".", "_")
    naming_policy = NamingPolicy(
        normalized_field_name=normalized_field_name,
        normalized_class_name=None,
        naming_confidence=PolicyConfidence.MEDIUM,
        source_label=source_label,
        notes=(
            "Temporary code-based name; full Spanish-first naming policy is implemented in task 7.",
        ),
    )
    structural_limitation_flags: tuple[StructuralLimitationFlag, ...] = ()
    
    reference_source_family = None
    reference_source_artifact = None
    serialization_pattern = None
    semantic_reference_kind = None
    diagnostics: tuple[str, ...] = ()
    if reference_resolution is not None:
        reference_source_family = (
            None
            if reference_resolution.source_family is None
            else reference_resolution.source_family.value
        )
        reference_source_artifact = reference_resolution.source_artifact
        serialization_pattern = reference_resolution.serialization_pattern
        semantic_reference_kind = reference_resolution.semantic_kind
        if reference_resolution.diagnostic_message is not None:
            diagnostics = (reference_resolution.diagnostic_message,)
    decision_trace = SemanticDecisionTrace(
        code=entry.code,
        xml_paths=xml_paths,
        manual_reference_table=manual_reference_table,
        reference_source_family=reference_source_family,
        reference_source_artifact=reference_source_artifact,
        serialization_pattern=serialization_pattern,
        semantic_reference_kind=semantic_reference_kind,
        applied_rules=(
            base_rule,
            reference_rule,
            multiplicity_rule,
            "naming:code_placeholder",
        ),
        diagnostics=diagnostics,
    )
    return SemanticFieldPolicy(
        code=entry.code,
        xml_paths=xml_paths,
        base_kind=base_kind,
        domain_shape_kind=domain_shape_kind,
        fallback_shape_kind=fallback_shape_kind,
        enum_eligibility=enum_eligibility,
        presence_kind=presence_kind,
        cardinality_kind=cardinality_kind,
        policy_confidence=policy_confidence,
        naming_policy=naming_policy,
        structural_limitation_flags=structural_limitation_flags,
        decision_trace=decision_trace,
    )
