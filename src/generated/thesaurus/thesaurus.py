from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from xsdata_pydantic.fields import field

from generated.thesaurus.isoutilities import Iso639

__NAMESPACE__ = "http://cv.normalizado.org/thesaurus"


class NameType(BaseModel):
    class Meta:
        name = "nameType"

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
    class Meta:
        name = "itemType"

    model_config = ConfigDict(defer_build=True)
    item_id: str = field(
        metadata={
            "name": "itemId",
            "type": "Element",
            "namespace": "",
        }
    )
    item_order: int = field(
        metadata={
            "name": "itemOrder",
            "type": "Element",
            "namespace": "",
        }
    )
    item_ancestor_id: None | str = field(
        default=None,
        metadata={
            "name": "itemAncestorId",
            "type": "Element",
            "namespace": "",
        },
    )
    item_description: list[NameType] = field(
        default_factory=list,
        metadata={
            "name": "itemDescription",
            "type": "Element",
            "namespace": "",
            "min_occurs": 1,
        },
    )
    item_note: None | NameType = field(
        default=None,
        metadata={
            "name": "itemNote",
            "type": "Element",
            "namespace": "",
        },
    )
    delegate: None | str = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "",
        },
    )


class Thesaurus(BaseModel):
    class Meta:
        namespace = "http://cv.normalizado.org/thesaurus"

    model_config = ConfigDict(defer_build=True)
    item: list[ItemType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "",
            "min_occurs": 1,
        },
    )
