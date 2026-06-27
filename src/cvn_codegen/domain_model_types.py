from dataclasses import dataclass

from cvn_codegen.normalization_types import (
    NormalizedCodeEntry,
)
from cvn_codegen.semantic_policy import (
    SemanticFieldPolicy,
)


@dataclass(frozen=True)
class DomainFieldSpec:
    field_name: str
    python_type: str
    code: str
    xml_paths: tuple[str, ...]
    required: bool
    repeated: bool
    domain_shape_kind: str
    enum_eligibility: str
    trace: dict[str, object]


@dataclass(frozen=True)
class DomainEnumSpec:
    class_name: str
    source_reference: str
    members: tuple[tuple[str, str], ...]
    labels: dict[str, str]
    trace: dict[str, object]


@dataclass(frozen=True)
class DomainTypeSpec:
    type_name: str
    import_path: str | None = None
    enum_spec: DomainEnumSpec | None = None


@dataclass(frozen=True)
class DomainGenerationUnit:
    module_name: str
    class_name: str
    source_group_key: str
    fields: tuple[DomainFieldSpec, ...]


@dataclass(frozen=True)
class DomainGenerationResult:
    units: tuple[DomainGenerationUnit, ...]
    enums: tuple[DomainEnumSpec, ...]
    normalized_entries: tuple[NormalizedCodeEntry, ...]
    semantic_policies: tuple[SemanticFieldPolicy, ...]

