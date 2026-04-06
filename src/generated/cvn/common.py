from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from xsdata.models.datatype import XmlDate, XmlDuration, XmlPeriod
from xsdata_pydantic.fields import field

from generated.cvn.isoutilities import (
    Iso639,
    Iso3166,
)

__NAMESPACE__ = "http://cv.normalizado.org/cvn"


class CvnInternetEmailAddressType(BaseModel):
    class Meta:
        name = "CVN_InternetEmailAddressType"

    model_config = ConfigDict(defer_build=True)
    item: str = field(
        metadata={
            "name": "Item",
            "type": "Element",
            "namespace": "",
            "pattern": r"(.*@.*)",
        }
    )
    code: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    obligatory: None | bool = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    multiplicity: None | bool = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    attribute: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class CvnBoolean(BaseModel):
    class Meta:
        name = "CVN_boolean"

    model_config = ConfigDict(defer_build=True)
    item: bool = field(
        metadata={
            "name": "Item",
            "type": "Element",
            "namespace": "",
        }
    )
    code: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    obligatory: None | bool = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    multiplicity: None | bool = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    attribute: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class CvnDate(BaseModel):
    class Meta:
        name = "CVN_date"

    model_config = ConfigDict(defer_build=True)
    item: XmlDate = field(
        metadata={
            "name": "Item",
            "type": "Element",
            "namespace": "",
        }
    )
    code: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    obligatory: None | bool = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    multiplicity: None | bool = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    attribute: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class CvnDuration(BaseModel):
    class Meta:
        name = "CVN_duration"

    model_config = ConfigDict(defer_build=True)
    item: XmlDuration = field(
        metadata={
            "name": "Item",
            "type": "Element",
            "namespace": "",
        }
    )
    code: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    obligatory: None | bool = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    multiplicity: None | bool = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    attribute: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class CvnGYear(BaseModel):
    class Meta:
        name = "CVN_gYear"

    model_config = ConfigDict(defer_build=True)
    item: XmlPeriod = field(
        metadata={
            "name": "Item",
            "type": "Element",
            "namespace": "",
        }
    )
    code: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    obligatory: None | bool = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    multiplicity: None | bool = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    attribute: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class CvnGYearMonth(BaseModel):
    class Meta:
        name = "CVN_gYearMonth"

    model_config = ConfigDict(defer_build=True)
    item: XmlPeriod = field(
        metadata={
            "name": "Item",
            "type": "Element",
            "namespace": "",
        }
    )
    code: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    obligatory: None | bool = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    multiplicity: None | bool = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    attribute: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class CvnString(BaseModel):
    class Meta:
        name = "CVN_string"

    model_config = ConfigDict(defer_build=True)
    item: str = field(
        metadata={
            "name": "Item",
            "type": "Element",
            "namespace": "",
        }
    )
    code: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    obligatory: None | bool = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    multiplicity: None | bool = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    attribute: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class CvnIso3166(BaseModel):
    class Meta:
        name = "CVN_ISO_3166"

    model_config = ConfigDict(defer_build=True)
    item: Iso3166 = field(
        metadata={
            "name": "Item",
            "type": "Element",
            "namespace": "",
        }
    )
    code: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    obligatory: None | bool = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    multiplicity: None | bool = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    attribute: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class CvnIso639(BaseModel):
    class Meta:
        name = "CVN_ISO_639"

    model_config = ConfigDict(defer_build=True)
    item: Iso639 = field(
        metadata={
            "name": "Item",
            "type": "Element",
            "namespace": "",
        }
    )
    code: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    obligatory: None | bool = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    multiplicity: None | bool = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    attribute: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class ExtensionType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    name: CvnString = field(
        metadata={
            "name": "Name",
            "type": "Element",
            "namespace": "",
        }
    )
    value: CvnString = field(
        metadata={
            "name": "Value",
            "type": "Element",
            "namespace": "",
        }
    )
    type_value: CvnString = field(
        metadata={
            "name": "Type",
            "type": "Element",
            "namespace": "",
        }
    )


class FlexibleDatesType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    day_month_year: None | CvnDate = field(
        default=None,
        metadata={
            "name": "DayMonthYear",
            "type": "Element",
            "namespace": "",
        },
    )
    month_year: None | CvnGYearMonth = field(
        default=None,
        metadata={
            "name": "MonthYear",
            "type": "Element",
            "namespace": "",
        },
    )
    year: None | CvnGYear = field(
        default=None,
        metadata={
            "name": "Year",
            "type": "Element",
            "namespace": "",
        },
    )
