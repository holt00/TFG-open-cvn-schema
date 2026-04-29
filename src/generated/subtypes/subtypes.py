from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from xsdata_pydantic.fields import field

from generated.subtypes.isoutilities import Iso639

__NAMESPACE__ = "http://cv.normalizado.org/CVNSubtype"


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


class ItemType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    name: NameType = field(
        metadata={
            "name": "Name",
            "type": "Element",
            "namespace": "",
        }
    )
    code_subtype1: str = field(
        metadata={
            "name": "CodeSubtype1",
            "type": "Element",
            "namespace": "",
        }
    )
    code_subtype2: None | str = field(
        default=None,
        metadata={
            "name": "CodeSubtype2",
            "type": "Element",
            "namespace": "",
        },
    )


class Cvnsubtype(BaseModel):
    class Meta:
        name = "CVNSubtype"
        namespace = "http://cv.normalizado.org/CVNSubtype"

    model_config = ConfigDict(defer_build=True)
    subtype: Cvnsubtype.Subtype = field(
        metadata={
            "name": "Subtype",
            "type": "Element",
            "namespace": "",
        }
    )

    class Subtype(BaseModel):
        model_config = ConfigDict(defer_build=True)
        item: list[Cvnsubtype.Subtype.Item] = field(
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
