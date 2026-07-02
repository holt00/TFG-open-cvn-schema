from dataclasses import dataclass
from enum import Enum


class ConceptualValueKind(str, Enum):
    """Classify the domain-facing value kind for a conceptual attribute."""

    TEXT = "text"
    BOOLEAN = "boolean"
    DECIMAL_NUMBER = "decimal_number"
    DATE_LIKE = "date_like"
    DURATION_LIKE = "duration_like"
    CONTROLLED_REFERENCE = "controlled_reference"
    VALUE_OBJECT = "value_object"
    UNKNOWN = "unknown"


class ConceptualPresenceKind(str, Enum):
    """Classify whether a conceptual attribute is required."""

    REQUIRED = "required"
    OPTIONAL = "optional"
    UNKNOWN = "unknown"


class ConceptualCardinalityKind(str, Enum):
    """Classify whether a conceptual attribute is single or repeated."""

    SINGLE = "single"
    REPEATED = "repeated"
    UNKNOWN = "unknown"


class ConceptualVocabularyKind(str, Enum):
    """Classify the conceptual treatment for controlled vocabularies."""

    ENUMERATION = "enumeration"
    CODE_LIST = "code_list"
    REGISTRY = "registry"
    THESAURUS = "thesaurus"
    HIERARCHICAL_CODE_LIST = "hierarchical_code_list"
    SUBTYPE_BACKED_CODE_LIST = "subtype_backed_code_list"
    UNRESOLVED_REFERENCE = "unresolved_reference"
    UNDER_TRACED_REFERENCE = "under_traced_reference"
    NONE = "none"


class ConceptualRelationshipKind(str, Enum):
    """Classify relationships between conceptual entities or vocabularies."""

    COMPOSITION = "composition"
    AGGREGATION = "aggregation"
    ASSOCIATION = "association"
    VOCABULARY_REFERENCE = "vocabulary_reference"


class ConceptualConfidence(str, Enum):
    """Classify confidence in conceptual extraction decisions."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    REQUIRES_REVIEW = "requires_review"


@dataclass(frozen=True)
class ConceptualTrace:
    """Preserve CVN and semantic-policy evidence for one conceptual element."""

    cvn_codes: tuple[str, ...]
    xml_paths: tuple[str, ...]
    source_files: tuple[str, ...]
    manual_reference_table: str | None = None
    reference_source_family: str | None = None
    reference_source_artifact: str | None = None
    semantic_reference_kind: str | None = None
    serialization_pattern: str | None = None
    applied_rules: tuple[str, ...] = ()
    diagnostics: tuple[str, ...] = ()


@dataclass(frozen=True)
class ConceptualAttribute:
    """Represent a domain-facing attribute in the conceptual model."""

    attribute_id: str
    name: str
    source_label: str | None
    value_kind: ConceptualValueKind
    presence: ConceptualPresenceKind
    cardinality: ConceptualCardinalityKind
    python_type_hint: str
    domain_shape_kind: str
    enum_eligibility: str
    confidence: ConceptualConfidence
    trace: ConceptualTrace
    vocabulary_id: str | None = None
    wrapper_type_names: tuple[str, ...] = ()


@dataclass(frozen=True)
class ConceptualEntity:
    """Represent a curriculum concept grouped independently from XML modules."""

    entity_id: str
    name: str
    domain_area_id: str
    source_group_key: str | None
    attributes: tuple[ConceptualAttribute, ...]
    trace: ConceptualTrace
    description: str | None = None


@dataclass(frozen=True)
class ConceptualRelationship:
    """Represent a relationship between conceptual entities or vocabularies."""

    relationship_id: str
    source_id: str
    target_id: str
    kind: ConceptualRelationshipKind
    source_cardinality: ConceptualCardinalityKind
    target_cardinality: ConceptualCardinalityKind
    trace: ConceptualTrace
    label: str | None = None


@dataclass(frozen=True)
class ConceptualVocabulary:
    """Represent a controlled vocabulary or external reference family."""

    vocabulary_id: str
    name: str
    kind: ConceptualVocabularyKind
    source_reference: str
    enum_eligibility: str
    confidence: ConceptualConfidence
    trace: ConceptualTrace
    item_count: int | None = None
    values: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class ConceptualLimitation:
    """Record unresolved or deliberately conservative conceptual decisions."""

    limitation_id: str
    message: str
    trace: ConceptualTrace


@dataclass(frozen=True)
class ConceptualDomainArea:
    """Group conceptual entities by curriculum domain area."""

    area_id: str
    name: str
    entities: tuple[ConceptualEntity, ...]
    description: str | None = None


@dataclass(frozen=True)
class ConceptualModelInventory:
    """Top-level conceptual model inventory consumed by later outputs."""

    inventory_id: str
    source_issue: str
    policy_name: str
    policy_version: str
    domain_areas: tuple[ConceptualDomainArea, ...]
    relationships: tuple[ConceptualRelationship, ...]
    vocabularies: tuple[ConceptualVocabulary, ...]
    limitations: tuple[ConceptualLimitation, ...]
