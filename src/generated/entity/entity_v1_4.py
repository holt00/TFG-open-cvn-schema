from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from xsdata_pydantic.fields import field

from generated.entity.cvnutilities_v1_0 import (
    CvnProvince,
    CvnRegion,
    CvnStreetType,
)
from generated.entity.entity_utilities_v1_4 import (
    CvnEntityFunction,
    CvnEntityNature,
    CvnEntityType,
)
from generated.entity.isoutilities import (
    Iso639,
    Iso3166,
)

__NAMESPACE__ = "http://cv.normalizado.org/entity"


class DescriptionType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    acronym: None | str = field(
        default=None,
        metadata={
            "name": "Acronym",
            "type": "Element",
            "namespace": "",
        },
    )
    text: str = field(
        metadata={
            "name": "Text",
            "type": "Element",
            "namespace": "",
        }
    )
    lang: None | Iso639 = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class NoteType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    item: str = field(
        metadata={
            "name": "Item",
            "type": "Element",
            "namespace": "",
        }
    )
    code: str = field(
        metadata={
            "name": "Code",
            "type": "Element",
            "namespace": "",
        }
    )
    description: list[NoteType.Description] = field(
        default_factory=list,
        metadata={
            "name": "Description",
            "type": "Element",
            "namespace": "",
        },
    )

    class Description(BaseModel):
        model_config = ConfigDict(defer_build=True)
        value: str = field(default="")
        lang: None | Iso639 = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )


class ProvinceType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    code: None | CvnProvince = field(
        default=None,
        metadata={
            "name": "Code",
            "type": "Element",
            "namespace": "",
        },
    )
    name: None | str = field(
        default=None,
        metadata={
            "name": "Name",
            "type": "Element",
            "namespace": "",
        },
    )


class RegionType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    code: None | CvnRegion = field(
        default=None,
        metadata={
            "name": "Code",
            "type": "Element",
            "namespace": "",
        },
    )
    name: None | str = field(
        default=None,
        metadata={
            "name": "Name",
            "type": "Element",
            "namespace": "",
        },
    )


class AddressType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    region: None | RegionType = field(
        default=None,
        metadata={
            "name": "Region",
            "type": "Element",
            "namespace": "",
        },
    )
    province: None | ProvinceType = field(
        default=None,
        metadata={
            "name": "Province",
            "type": "Element",
            "namespace": "",
        },
    )
    postal_code: None | str = field(
        default=None,
        metadata={
            "name": "PostalCode",
            "type": "Element",
            "namespace": "",
        },
    )
    city: None | str = field(
        default=None,
        metadata={
            "name": "City",
            "type": "Element",
            "namespace": "",
        },
    )
    street: None | AddressType.Street = field(
        default=None,
        metadata={
            "name": "Street",
            "type": "Element",
            "namespace": "",
        },
    )
    other_information: None | str = field(
        default=None,
        metadata={
            "name": "OtherInformation",
            "type": "Element",
            "namespace": "",
        },
    )
    lang: None | Iso639 = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )

    class Street(BaseModel):
        model_config = ConfigDict(defer_build=True)
        value: str = field(default="")
        type_value: None | CvnStreetType = field(
            default=None,
            metadata={
                "name": "type",
                "type": "Attribute",
            },
        )


class DirectionType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    country_code: Iso3166 = field(
        metadata={
            "name": "CountryCode",
            "type": "Element",
            "namespace": "",
        }
    )
    address_type: list[AddressType] = field(
        default_factory=list,
        metadata={
            "name": "AddressType",
            "type": "Element",
            "namespace": "",
        },
    )


class ItemType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    item_id: str = field(
        metadata={
            "name": "ItemId",
            "type": "Element",
            "namespace": "",
        }
    )
    nature: None | CvnEntityNature = field(
        default=None,
        metadata={
            "name": "Nature",
            "type": "Element",
            "namespace": "",
        },
    )
    function: list[ItemType.Function] = field(
        default_factory=list,
        metadata={
            "name": "Function",
            "type": "Element",
            "namespace": "",
        },
    )
    type_value: None | CvnEntityType = field(
        default=None,
        metadata={
            "name": "Type",
            "type": "Element",
            "namespace": "",
        },
    )
    item_address: DirectionType = field(
        metadata={
            "name": "ItemAddress",
            "type": "Element",
            "namespace": "",
        }
    )
    item_description: list[DescriptionType] = field(
        default_factory=list,
        metadata={
            "name": "ItemDescription",
            "type": "Element",
            "namespace": "",
            "min_occurs": 1,
        },
    )
    synonym: None | ItemType.Synonym = field(
        default=None,
        metadata={
            "name": "Synonym",
            "type": "Element",
            "namespace": "",
        },
    )
    url: None | str = field(
        default=None,
        metadata={
            "name": "URL",
            "type": "Element",
            "namespace": "",
        },
    )
    item_note: list[NoteType] = field(
        default_factory=list,
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

    class Synonym(BaseModel):
        model_config = ConfigDict(defer_build=True)
        denomination: list[str] = field(
            default_factory=list,
            metadata={
                "name": "Denomination",
                "type": "Element",
                "namespace": "",
            },
        )

    class Function(BaseModel):
        model_config = ConfigDict(defer_build=True)
        code: CvnEntityFunction = field(
            metadata={
                "name": "Code",
                "type": "Element",
                "namespace": "",
            }
        )
        item_ancestor_id: list[str] = field(
            default_factory=list,
            metadata={
                "name": "ItemAncestorId",
                "type": "Element",
                "namespace": "",
            },
        )


class Entity(BaseModel):
    class Meta:
        namespace = "http://cv.normalizado.org/entity"

    model_config = ConfigDict(defer_build=True)
    item: list[ItemType] = field(
        default_factory=list,
        metadata={
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
