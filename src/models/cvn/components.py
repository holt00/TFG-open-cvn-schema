from __future__ import annotations
from pydantic import BaseModel, ConfigDict

class BaseControlledReferenceValue(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: str | None = None
    label: str | None = None

class OpenCodedValue(BaseControlledReferenceValue):
    pass

class MeasureOrScaleValue(BaseControlledReferenceValue):
    pass

class IdentifierReference(BaseControlledReferenceValue):
    pass

class ScopeReference(BaseControlledReferenceValue):
    pass

class SubtypeBackedValue(BaseControlledReferenceValue):
    pass

class HierarchicalCodeReference(BaseControlledReferenceValue):
    parent_code: str | None = None

class RegistryReference(BaseControlledReferenceValue):
    registry_id: str | None = None

class VocabularyReference(BaseControlledReferenceValue):
    vocabulary_source: str | None = None

class UnresolvedReference(BaseControlledReferenceValue):
    raw_reference: str | None = None
    
class UnderTracedReference(BaseControlledReferenceValue):
    raw_reference: str | None = None