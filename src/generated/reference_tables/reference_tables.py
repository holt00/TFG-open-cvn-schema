from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from xsdata_pydantic.fields import field

from generated.reference_tables.isoutilities import Iso639

__NAMESPACE__ = "http://cv.normalizado.org/referenceTables"


class TableTtype(BaseModel):
    pass
    model_config = ConfigDict(defer_build=True)


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
    code: str = field(
        metadata={
            "name": "Code",
            "type": "Element",
            "namespace": "",
        }
    )
    order: int = field(
        metadata={
            "name": "Order",
            "type": "Element",
            "namespace": "",
        }
    )
    name: NameType = field(
        metadata={
            "name": "Name",
            "type": "Element",
            "namespace": "",
        }
    )
    antecesor_code: None | str = field(
        default=None,
        metadata={
            "name": "AntecesorCode",
            "type": "Element",
            "namespace": "",
        },
    )
    link: bool = field(
        metadata={
            "name": "Link",
            "type": "Element",
            "namespace": "",
        }
    )
    item_note: None | NameType = field(
        default=None,
        metadata={
            "name": "ItemNote",
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


class ReferenceTables(BaseModel):
    class Meta:
        namespace = "http://cv.normalizado.org/referenceTables"

    model_config = ConfigDict(defer_build=True)
    table: list[ReferenceTables.Table] = field(
        default_factory=list,
        metadata={
            "name": "Table",
            "type": "Element",
            "namespace": "",
            "min_occurs": 1,
        },
    )

    class Table(TableTtype):
        model_config = ConfigDict(defer_build=True)
        item: list[ItemType] = field(
            default_factory=list,
            metadata={
                "name": "Item",
                "type": "Element",
                "namespace": "",
                "min_occurs": 1,
            },
        )
        name: object = field(
            metadata={
                "type": "Attribute",
            }
        )
        version: object = field(
            metadata={
                "type": "Attribute",
            }
        )
        antecesor_table: None | object = field(
            default=None,
            metadata={
                "name": "antecesorTable",
                "type": "Attribute",
            },
        )
        source: None | object = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )
        xmldata_type: None | object = field(
            default=None,
            metadata={
                "name": "XMLDataType",
                "type": "Attribute",
            },
        )
        xmlproperty: None | object = field(
            default=None,
            metadata={
                "name": "XMLProperty",
                "type": "Attribute",
            },
        )
        xmlindicator: None | object = field(
            default=None,
            metadata={
                "name": "XMLIndicator",
                "type": "Attribute",
            },
        )
