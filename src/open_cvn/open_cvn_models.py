from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


OPEN_CVN_SCHEMA_VERSION = "0.1.0"
OPEN_CVN_MAJOR_VERSION = 0


class OpenCvnPolicyMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    version: str


class OpenCvnMetadata(BaseModel):
    model_config = ConfigDict(extra="allow")

    language: str | None = None
    source: dict[str, Any] | None = None
    created_at: str | None = None
    updated_at: str | None = None
    generator: dict[str, Any] | None = None
    policy: OpenCvnPolicyMetadata


class OpenCvnTrace(BaseModel):
    model_config = ConfigDict(extra="allow")

    cvn_codes: list[str] = Field(default_factory=list)
    xml_paths: list[str] = Field(default_factory=list)
    source_files: list[str] = Field(default_factory=list)
    source_artifacts: list[str] = Field(default_factory=list)
    manual_reference_table: str | None = None
    semantic_reference_kind: str | None = None
    serialization_pattern: str | None = None
    domain_shape_kind: str | None = None
    confidence: str | None = None


class OpenCvnEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str | None = None
    type: str
    data: dict[str, Any]
    trace: OpenCvnTrace | None = None
    extensions: dict[str, Any] | None = None


class OpenCvnCurriculum(BaseModel):
    model_config = ConfigDict(extra="allow")

    identity: dict[str, Any] = Field(default_factory=dict)
    education: list[OpenCvnEntry] = Field(default_factory=list)
    research: list[OpenCvnEntry] = Field(default_factory=list)
    professional_experience: list[OpenCvnEntry] = Field(default_factory=list)
    achievements: list[OpenCvnEntry] = Field(default_factory=list)
    other: list[OpenCvnEntry] = Field(default_factory=list)


class OpenCvnDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str
    metadata: OpenCvnMetadata
    curriculum: OpenCvnCurriculum
    extensions: dict[str, Any] | None = None

    @field_validator("schema_version")
    @classmethod
    def _validate_schema_version(cls, value: str) -> str:
        major_version = _major_version(value)
        if major_version != OPEN_CVN_MAJOR_VERSION:
            raise ValueError(
                f"Unsupported Open CVN major version: {value}. Expected major {OPEN_CVN_MAJOR_VERSION}."
            )
        return value


def is_newer_compatible_version(schema_version: str) -> bool:
    if _major_version(schema_version) != OPEN_CVN_MAJOR_VERSION:
        return False
    return schema_version != OPEN_CVN_SCHEMA_VERSION


def _major_version(schema_version: str) -> int:
    try:
        return int(schema_version.split(".", maxsplit=1)[0])
    except (AttributeError, ValueError) as exc:
        raise ValueError(f"Invalid Open CVN schema version: {schema_version}") from exc
