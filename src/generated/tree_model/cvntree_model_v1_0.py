from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict
from xsdata_pydantic.fields import field

__NAMESPACE__ = "http://cv.normalizado.org/CVNTreeModel"


class PropertyName(Enum):
    CVN_ITEM_ID = "CvnItemID"
    SUBTYPE = "Subtype"
    TITLE = "Title"
    DESCRIPTION = "Description"
    SUBJECT = "Subject"
    FILTER = "Filter"
    EDITION = "Edition"
    LINK = "Link"
    ENTITY = "Entity"
    DATE = "Date"
    AUTHOR = "Author"
    DEDICATION = "Dedication"
    ROLL = "Roll"
    COLLABORATOR = "Collaborator"
    PLACE = "Place"
    ECONOMIC_DIMENSION = "EconomicDimension"
    PHYSICAL_DIMENSION = "PhysicalDimension"
    LOCATION = "Location"
    EXTERNAL_PK = "ExternalPK"
    LOCAL_PK = "LocalPK"
    SCOPE = "Scope"
    DIFFUSION = "Diffusion"
    QUALITY = "Quality"
    URL = "Url"
    LANGUAGE = "Language"
    VALIDATION = "Validation"
    CONTACT = "Contact"
    COLLECTION = "Collection"
    IDENTIFICATION = "Identification"
    ADDRESS = "Address"
    VERSION_ID = "VersionID"


class PropertyType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    property: list[PropertyTypeProperty] = field(
        default_factory=list,
        metadata={
            "name": "Property",
            "type": "Element",
            "namespace": "http://cv.normalizado.org/CVNTreeModel",
            "min_occurs": 1,
        },
    )


class CvntreeModelNodeCvnitem(PropertyType):
    class Meta:
        global_type = False

    model_config = ConfigDict(defer_build=True)
    code: None | object = field(
        default=None,
        metadata={
            "type": "Attribute",
            "namespace": "http://cv.normalizado.org/CVNTreeModel",
        },
    )


class IndicatorTypeCvnitem(PropertyType):
    class Meta:
        global_type = False

    model_config = ConfigDict(defer_build=True)
    code: None | object = field(
        default=None,
        metadata={
            "type": "Attribute",
            "namespace": "http://cv.normalizado.org/CVNTreeModel",
        },
    )


class CvntreeModelNode(BaseModel):
    class Meta:
        global_type = False

    model_config = ConfigDict(defer_build=True)
    version: PropertyType = field(
        metadata={
            "name": "Version",
            "type": "Element",
            "namespace": "http://cv.normalizado.org/CVNTreeModel",
        }
    )
    agent: PropertyType = field(
        metadata={
            "name": "Agent",
            "type": "Element",
            "namespace": "http://cv.normalizado.org/CVNTreeModel",
        }
    )
    cvnitem: list[CvntreeModelNodeCvnitem] = field(
        default_factory=list,
        metadata={
            "name": "CVNItem",
            "type": "Element",
            "namespace": "http://cv.normalizado.org/CVNTreeModel",
            "min_occurs": 1,
        },
    )


class IndicatorType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    cvnitem: None | IndicatorTypeCvnitem = field(
        default=None,
        metadata={
            "name": "CVNItem",
            "type": "Element",
            "namespace": "http://cv.normalizado.org/CVNTreeModel",
        },
    )
    indicator: list[IndicatorTypeIndicator] = field(
        default_factory=list,
        metadata={
            "name": "Indicator",
            "type": "Element",
            "namespace": "http://cv.normalizado.org/CVNTreeModel",
        },
    )


class CvntreeModel(BaseModel):
    class Meta:
        name = "CVNTreeModel"
        namespace = "http://cv.normalizado.org/CVNTreeModel"

    model_config = ConfigDict(defer_build=True)
    node: CvntreeModelNode = field(
        metadata={
            "name": "Node",
            "type": "Element",
        }
    )
    version: object = field(
        metadata={
            "type": "Attribute",
            "namespace": "http://cv.normalizado.org/CVNTreeModel",
        }
    )


class IndicatorTypeIndicator(BaseModel):
    class Meta:
        global_type = False

    model_config = ConfigDict(defer_build=True)
    value: None | str = field(
        default=None,
        metadata={
            "name": "Value",
            "type": "Element",
            "namespace": "http://cv.normalizado.org/CVNTreeModel",
        },
    )
    child: None | IndicatorType = field(
        default=None,
        metadata={
            "name": "Child",
            "type": "Element",
            "namespace": "http://cv.normalizado.org/CVNTreeModel",
        },
    )
    name: object = field(
        metadata={
            "type": "Attribute",
            "namespace": "http://cv.normalizado.org/CVNTreeModel",
        }
    )
    code: None | object = field(
        default=None,
        metadata={
            "type": "Attribute",
            "namespace": "http://cv.normalizado.org/CVNTreeModel",
        },
    )


class PropertyTypeProperty(IndicatorType):
    class Meta:
        global_type = False

    model_config = ConfigDict(defer_build=True)
    name: PropertyName = field(
        metadata={
            "type": "Attribute",
            "namespace": "http://cv.normalizado.org/CVNTreeModel",
        }
    )
    code: None | object = field(
        default=None,
        metadata={
            "type": "Attribute",
            "namespace": "http://cv.normalizado.org/CVNTreeModel",
        },
    )
