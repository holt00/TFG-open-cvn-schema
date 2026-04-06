from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict
from xsdata_pydantic.fields import field

from generated.specification_manual.isoutilities import Iso639

__NAMESPACE__ = "http://cv.normalizado.org/SpecificationManual"


class FieldType(Enum):
    LEVEL = "Level"
    NAME = "Name"
    SHORT_NAME = "ShortName"
    TYPE = "Type"
    DEFINITION = "Definition"
    OBLIGATORY = "Obligatory"
    REFERENCE_TABLE = "ReferenceTable"
    LINK = "Link"
    MULTIPLICITY = "Multiplicity"
    LENGTH = "Length"
    EXTENSION = "Extension"
    EXAMPLE = "Example"
    DELEGATE = "Delegate"


class NameType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    name_detail: list[NameType.NameDetail] = field(
        default_factory=list,
        metadata={
            "name": "NameDetail",
            "type": "Element",
            "namespace": "",
            "min_occurs": 1,
        },
    )

    class NameDetail(BaseModel):
        model_config = ConfigDict(defer_build=True)
        name: str = field(
            metadata={
                "name": "Name",
                "type": "Element",
                "namespace": "",
            }
        )
        short_name: None | str = field(
            default=None,
            metadata={
                "name": "ShortName",
                "type": "Element",
                "namespace": "",
            },
        )
        lang: Iso639 = field(
            metadata={
                "type": "Attribute",
            }
        )


class TextType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    text: list[TextType.Text] = field(
        default_factory=list,
        metadata={
            "name": "Text",
            "type": "Element",
            "namespace": "",
        },
    )

    class Text(BaseModel):
        model_config = ConfigDict(defer_build=True)
        value: str = field(default="")
        lang: Iso639 = field(
            metadata={
                "type": "Attribute",
            }
        )


class VersionType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    field_value: list[FieldType] = field(
        default_factory=list,
        metadata={
            "name": "Field",
            "type": "Element",
            "namespace": "",
            "min_occurs": 1,
        },
    )


class ItemType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    name: NameType = field(
        metadata={
            "name": "Name",
            "type": "Element",
            "namespace": "",
        }
    )
    type_value: str = field(
        metadata={
            "name": "Type",
            "type": "Element",
            "namespace": "",
        }
    )
    level: None | str = field(
        default=None,
        metadata={
            "name": "Level",
            "type": "Element",
            "namespace": "",
        },
    )
    order: int = field(
        metadata={
            "name": "Order",
            "type": "Element",
            "namespace": "",
        }
    )
    definition: None | TextType = field(
        default=None,
        metadata={
            "name": "Definition",
            "type": "Element",
            "namespace": "",
        },
    )
    obligatory: bool = field(
        metadata={
            "name": "Obligatory",
            "type": "Element",
            "namespace": "",
        }
    )
    reference_table: None | str = field(
        default=None,
        metadata={
            "name": "ReferenceTable",
            "type": "Element",
            "namespace": "",
        },
    )
    link: None | str = field(
        default=None,
        metadata={
            "name": "Link",
            "type": "Element",
            "namespace": "",
        },
    )
    multiplicity: bool = field(
        metadata={
            "name": "Multiplicity",
            "type": "Element",
            "namespace": "",
        }
    )
    length: None | int = field(
        default=None,
        metadata={
            "name": "Length",
            "type": "Element",
            "namespace": "",
        },
    )
    extension: None | TextType = field(
        default=None,
        metadata={
            "name": "Extension",
            "type": "Element",
            "namespace": "",
        },
    )
    example: None | TextType = field(
        default=None,
        metadata={
            "name": "Example",
            "type": "Element",
            "namespace": "",
        },
    )
    delegate: None | str = field(
        default=None,
        metadata={
            "name": "Delegate",
            "type": "Element",
            "namespace": "",
        },
    )


class SpecificationManual(BaseModel):
    class Meta:
        namespace = "http://cv.normalizado.org/SpecificationManual"

    model_config = ConfigDict(defer_build=True)
    manual: SpecificationManual.Manual = field(
        metadata={
            "name": "Manual",
            "type": "Element",
            "namespace": "",
        }
    )
    version_control: None | SpecificationManual.VersionControl = field(
        default=None,
        metadata={
            "name": "VersionControl",
            "type": "Element",
            "namespace": "",
        },
    )

    class Manual(BaseModel):
        model_config = ConfigDict(defer_build=True)
        item: list[SpecificationManual.Manual.Item] = field(
            default_factory=list,
            metadata={
                "name": "Item",
                "type": "Element",
                "namespace": "",
                "min_occurs": 1,
            },
        )
        version: object = field(
            metadata={
                "type": "Attribute",
            }
        )

        class Item(ItemType):
            model_config = ConfigDict(defer_build=True)
            code: object = field(
                metadata={
                    "type": "Attribute",
                }
            )

    class VersionControl(BaseModel):
        model_config = ConfigDict(defer_build=True)
        version_detail: list[
            SpecificationManual.VersionControl.VersionDetail
        ] = field(
            default_factory=list,
            metadata={
                "name": "VersionDetail",
                "type": "Element",
                "namespace": "",
                "min_occurs": 1,
            },
        )

        class VersionDetail(BaseModel):
            model_config = ConfigDict(defer_build=True)
            item: list[
                SpecificationManual.VersionControl.VersionDetail.Item
            ] = field(
                default_factory=list,
                metadata={
                    "name": "Item",
                    "type": "Element",
                    "namespace": "",
                    "min_occurs": 1,
                },
            )
            version: object = field(
                metadata={
                    "type": "Attribute",
                }
            )

            class Item(VersionType):
                model_config = ConfigDict(defer_build=True)
                code: None | object = field(
                    default=None,
                    metadata={
                        "type": "Attribute",
                    },
                )
