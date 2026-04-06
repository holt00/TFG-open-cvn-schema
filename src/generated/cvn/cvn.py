from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from xsdata_pydantic.fields import field

from generated.cvn.aux_table import (
    CvnAccessToType,
    CvnAuthorizationTypeType,
    CvnCategoryTypeType,
    CvnCodeCvnitemIdtype,
    CvnCollaboratorTypeType,
    CvnDedicationType,
    CvnDurationTypeType,
    CvnEconomicDimensionTypeType,
    CvnEditionTypeType,
    CvnEntityScopeType,
    CvnEntityTypeType,
    CvnExperienceTypeType,
    CvnExternalPktypeType,
    CvnFilterTypeType,
    CvnFreeNormTypeType,
    CvnGenderType,
    CvnJuridicalScopeType,
    CvnMomentDateType,
    CvnMomentPlaceType,
    CvnPhysicalDimensionalTypeType,
    CvnQualityAgencyType,
    CvnQualityMomentType,
    CvnQualityTypeType,
    CvnRegion,
    CvnResultTypeType,
    CvnScopeTypeType,
    CvnTelcomTypeType,
    CvnTitleCategory,
    CvnValueEdCurrencyType,
    CvnValueFilter,
    CvnValueRoll,
    CvnValueSubType1,
    CvnValueSubType2,
)
from generated.cvn.common import (
    CvnBoolean,
    CvnDate,
    CvnDuration,
    CvnInternetEmailAddressType,
    CvnIso639,
    CvnIso3166,
    CvnString,
    ExtensionType,
    FlexibleDatesType,
)

__NAMESPACE__ = "http://cv.normalizado.org/cvn"


class EntityNameType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    item: list[str] = field(
        default_factory=list,
        metadata={
            "name": "Item",
            "type": "Element",
            "namespace": "",
        },
    )
    others: list[str] = field(
        default_factory=list,
        metadata={
            "name": "Others",
            "type": "Element",
            "namespace": "",
        },
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


class AccessToType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    item: CvnAccessToType = field(
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


class AuthorizationTypeType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    item: CvnAuthorizationTypeType = field(
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


class CvuserType(BaseModel):
    class Meta:
        name = "CVUserType"

    model_config = ConfigDict(defer_build=True)
    user: CvnString = field(
        metadata={
            "name": "User",
            "type": "Element",
            "namespace": "",
        }
    )
    password: CvnString = field(
        metadata={
            "name": "Password",
            "type": "Element",
            "namespace": "",
        }
    )
    update_date: FlexibleDatesType = field(
        metadata={
            "name": "UpdateDate",
            "type": "Element",
            "namespace": "",
        }
    )


class CategoryTypeType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    item: CvnCategoryTypeType = field(
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


class CodeCvnitemType(BaseModel):
    class Meta:
        name = "CodeCVNItemType"

    model_config = ConfigDict(defer_build=True)
    item: CvnCodeCvnitemIdtype = field(
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


class CodeRegionType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    item: CvnRegion = field(
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


class CollaboratorTypeType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    item: CvnCollaboratorTypeType = field(
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


class CurrencyTypeType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    item: CvnValueEdCurrencyType = field(
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


class DedicationType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    item: CvnDedicationType = field(
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


class DigitalSignatureType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    cvnitem_id: None | CvnString = field(
        default=None,
        metadata={
            "name": "CVNItemID",
            "type": "Element",
            "namespace": "",
        },
    )
    signature: None | CvnString = field(
        default=None,
        metadata={
            "name": "Signature",
            "type": "Element",
            "namespace": "",
        },
    )
    agency: None | CvnString = field(
        default=None,
        metadata={
            "name": "Agency",
            "type": "Element",
            "namespace": "",
        },
    )
    type_value: None | CvnString = field(
        default=None,
        metadata={
            "name": "Type",
            "type": "Element",
            "namespace": "",
        },
    )


class EconomicDimensionTypeType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    item: CvnEconomicDimensionTypeType = field(
        metadata={
            "name": "Item",
            "type": "Element",
            "namespace": "",
        }
    )
    others: None | str = field(
        default=None,
        metadata={
            "name": "Others",
            "type": "Element",
            "namespace": "",
        },
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


class EditionTypeType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    item: CvnEditionTypeType = field(
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


class EntityScopeType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    item: CvnEntityScopeType = field(
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


class EntityTypeType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    item: list[CvnEntityTypeType] = field(
        default_factory=list,
        metadata={
            "name": "Item",
            "type": "Element",
            "namespace": "",
        },
    )
    others: list[str] = field(
        default_factory=list,
        metadata={
            "name": "Others",
            "type": "Element",
            "namespace": "",
        },
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


class ExperienceTypeType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    item: CvnExperienceTypeType = field(
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


class ExternalPktypeType(BaseModel):
    class Meta:
        name = "ExternalPKTypeType"

    model_config = ConfigDict(defer_build=True)
    item: CvnExternalPktypeType = field(
        metadata={
            "name": "Item",
            "type": "Element",
            "namespace": "",
        }
    )
    others: None | str = field(
        default=None,
        metadata={
            "name": "Others",
            "type": "Element",
            "namespace": "",
        },
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


class FilterTypeType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    item: CvnFilterTypeType = field(
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


class FilterValueType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    item: CvnValueFilter = field(
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


class GenderType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    item: CvnGenderType = field(
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


class JuridicalScopeType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    item: CvnJuridicalScopeType = field(
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


class LanguageType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    language_name: CvnString = field(
        metadata={
            "name": "LanguageName",
            "type": "Element",
            "namespace": "",
        }
    )
    language_code: CvnIso639 = field(
        metadata={
            "name": "LanguageCode",
            "type": "Element",
            "namespace": "",
        }
    )


class LocalPktype(BaseModel):
    class Meta:
        name = "LocalPKType"

    model_config = ConfigDict(defer_build=True)
    code: None | CvnString = field(
        default=None,
        metadata={
            "name": "Code",
            "type": "Element",
            "namespace": "",
        },
    )
    agency: None | CvnString = field(
        default=None,
        metadata={
            "name": "Agency",
            "type": "Element",
            "namespace": "",
        },
    )


class LocationType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    volume: None | CvnString = field(
        default=None,
        metadata={
            "name": "Volume",
            "type": "Element",
            "namespace": "",
        },
    )
    number: None | CvnString = field(
        default=None,
        metadata={
            "name": "Number",
            "type": "Element",
            "namespace": "",
        },
    )
    initial_page: None | CvnString = field(
        default=None,
        metadata={
            "name": "InitialPage",
            "type": "Element",
            "namespace": "",
        },
    )
    final_page: None | CvnString = field(
        default=None,
        metadata={
            "name": "FinalPage",
            "type": "Element",
            "namespace": "",
        },
    )
    digital_location_code: None | CvnString = field(
        default=None,
        metadata={
            "name": "DigitalLocationCode",
            "type": "Element",
            "namespace": "",
        },
    )


class MomentDateType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    item: CvnMomentDateType = field(
        metadata={
            "name": "Item",
            "type": "Element",
            "namespace": "",
        }
    )
    others: None | str = field(
        default=None,
        metadata={
            "name": "Others",
            "type": "Element",
            "namespace": "",
        },
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


class MomentPlaceType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    item: CvnMomentPlaceType = field(
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


class OfficialIdType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    dni: None | CvnString = field(
        default=None,
        metadata={
            "name": "DNI",
            "type": "Element",
            "namespace": "",
        },
    )
    passport: None | CvnString = field(
        default=None,
        metadata={
            "name": "Passport",
            "type": "Element",
            "namespace": "",
        },
    )
    nie: None | CvnString = field(
        default=None,
        metadata={
            "name": "NIE",
            "type": "Element",
            "namespace": "",
        },
    )
    others: None | str = field(
        default=None,
        metadata={
            "name": "Others",
            "type": "Element",
            "namespace": "",
        },
    )


class PhotoType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    bitmap: None | CvnString = field(
        default=None,
        metadata={
            "name": "Bitmap",
            "type": "Element",
            "namespace": "",
        },
    )
    format: None | CvnString = field(
        default=None,
        metadata={
            "name": "Format",
            "type": "Element",
            "namespace": "",
        },
    )


class PhysicalDimensionalTypeType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    item: CvnPhysicalDimensionalTypeType = field(
        metadata={
            "name": "Item",
            "type": "Element",
            "namespace": "",
        }
    )
    others: None | str = field(
        default=None,
        metadata={
            "name": "Others",
            "type": "Element",
            "namespace": "",
        },
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


class QualityAgencyType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    item: CvnQualityAgencyType = field(
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


class QualityMomentType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    item: CvnQualityMomentType = field(
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


class QualityTypeType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    item: CvnQualityTypeType = field(
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


class ResultTypeType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    item: CvnResultTypeType = field(
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


class RollValueType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    item: CvnValueRoll = field(
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


class ScopeTypeType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    item: None | CvnScopeTypeType = field(
        default=None,
        metadata={
            "name": "Item",
            "type": "Element",
            "namespace": "",
        },
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


class SubType1Type(BaseModel):
    model_config = ConfigDict(defer_build=True)
    item: CvnValueSubType1 = field(
        metadata={
            "name": "Item",
            "type": "Element",
            "namespace": "",
        }
    )
    others: None | str = field(
        default=None,
        metadata={
            "name": "Others",
            "type": "Element",
            "namespace": "",
        },
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


class SubType2Type(BaseModel):
    model_config = ConfigDict(defer_build=True)
    item: CvnValueSubType2 = field(
        metadata={
            "name": "Item",
            "type": "Element",
            "namespace": "",
        }
    )
    others: None | str = field(
        default=None,
        metadata={
            "name": "Others",
            "type": "Element",
            "namespace": "",
        },
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


class SubjectTypeType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    item: CvnFreeNormTypeType = field(
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


class TelcomNumberType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    international_code: None | CvnString = field(
        default=None,
        metadata={
            "name": "InternationalCode",
            "type": "Element",
            "namespace": "",
        },
    )
    number: CvnString = field(
        metadata={
            "name": "Number",
            "type": "Element",
            "namespace": "",
        }
    )
    extension: None | CvnString = field(
        default=None,
        metadata={
            "name": "Extension",
            "type": "Element",
            "namespace": "",
        },
    )
    type_value: None | CvnTelcomTypeType = field(
        default=None,
        metadata={
            "name": "Type",
            "type": "Attribute",
        },
    )


class TitleType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    name: CvnString = field(
        metadata={
            "name": "Name",
            "type": "Element",
            "namespace": "",
        }
    )
    identification: None | CvnString = field(
        default=None,
        metadata={
            "name": "Identification",
            "type": "Element",
            "namespace": "",
        },
    )
    type_value: None | CvnFreeNormTypeType = field(
        default=None,
        metadata={
            "name": "Type",
            "type": "Element",
            "namespace": "",
        },
    )
    category: None | CvnTitleCategory = field(
        default=None,
        metadata={
            "name": "Category",
            "type": "Element",
            "namespace": "",
        },
    )


class ValidationType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    value: CvnBoolean = field(
        metadata={
            "name": "Value",
            "type": "Element",
            "namespace": "",
        }
    )
    agency: None | CvnString = field(
        default=None,
        metadata={
            "name": "Agency",
            "type": "Element",
            "namespace": "",
        },
    )
    source: None | CvnString = field(
        default=None,
        metadata={
            "name": "Source",
            "type": "Element",
            "namespace": "",
        },
    )
    date: None | CvnDate = field(
        default=None,
        metadata={
            "name": "Date",
            "type": "Element",
            "namespace": "",
        },
    )


class Author(BaseModel):
    model_config = ConfigDict(defer_build=True)
    given_name: None | CvnString = field(
        default=None,
        metadata={
            "name": "GivenName",
            "type": "Element",
            "namespace": "",
        },
    )
    first_family_name: None | CvnString = field(
        default=None,
        metadata={
            "name": "FirstFamilyName",
            "type": "Element",
            "namespace": "",
        },
    )
    second_family_name: None | CvnString = field(
        default=None,
        metadata={
            "name": "SecondFamilyName",
            "type": "Element",
            "namespace": "",
        },
    )
    signature: CvnString = field(
        metadata={
            "name": "Signature",
            "type": "Element",
            "namespace": "",
        }
    )
    normalized_identification: None | CvnString = field(
        default=None,
        metadata={
            "name": "NormalizedIdentification",
            "type": "Element",
            "namespace": "",
        },
    )
    local_pk: list[LocalPktype] = field(
        default_factory=list,
        metadata={
            "name": "LocalPK",
            "type": "Element",
            "namespace": "",
        },
    )
    signature_order: None | CvnString = field(
        default=None,
        metadata={
            "name": "SignatureOrder",
            "type": "Element",
            "namespace": "",
        },
    )
    country_code: None | CvnIso3166 = field(
        default=None,
        metadata={
            "name": "CountryCode",
            "type": "Element",
            "namespace": "",
        },
    )
    roll: None | CvnValueRoll = field(
        default=None,
        metadata={
            "name": "Roll",
            "type": "Element",
            "namespace": "",
        },
    )


class AuthorizationType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    value: None | CvnString = field(
        default=None,
        metadata={
            "name": "Value",
            "type": "Element",
            "namespace": "",
        },
    )
    type_value: AuthorizationTypeType = field(
        metadata={
            "name": "Type",
            "type": "Element",
            "namespace": "",
        }
    )


class CollaboratorType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    type_value: CollaboratorTypeType = field(
        metadata={
            "name": "Type",
            "type": "Element",
            "namespace": "",
        }
    )
    value: None | CvnString = field(
        default=None,
        metadata={
            "name": "Value",
            "type": "Element",
            "namespace": "",
        },
    )
    category: CategoryTypeType = field(
        metadata={
            "name": "Category",
            "type": "Element",
            "namespace": "",
        }
    )


class ContactType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    telephone: list[TelcomNumberType] = field(
        default_factory=list,
        metadata={
            "name": "Telephone",
            "type": "Element",
            "namespace": "",
        },
    )
    fax: None | TelcomNumberType = field(
        default=None,
        metadata={
            "name": "Fax",
            "type": "Element",
            "namespace": "",
        },
    )
    internet_email_address: None | CvnInternetEmailAddressType = field(
        default=None,
        metadata={
            "name": "InternetEmailAddress",
            "type": "Element",
            "namespace": "",
        },
    )
    personal_web: None | CvnString = field(
        default=None,
        metadata={
            "name": "PersonalWeb",
            "type": "Element",
            "namespace": "",
        },
    )


class DateType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    moment: MomentDateType = field(
        metadata={
            "name": "Moment",
            "type": "Element",
            "namespace": "",
        }
    )
    only_date: None | FlexibleDatesType = field(
        default=None,
        metadata={
            "name": "OnlyDate",
            "type": "Element",
            "namespace": "",
        },
    )
    start_date: None | FlexibleDatesType = field(
        default=None,
        metadata={
            "name": "StartDate",
            "type": "Element",
            "namespace": "",
        },
    )
    end_date: None | FlexibleDatesType = field(
        default=None,
        metadata={
            "name": "EndDate",
            "type": "Element",
            "namespace": "",
        },
    )
    duration: None | CvnDuration = field(
        default=None,
        metadata={
            "name": "Duration",
            "type": "Element",
            "namespace": "",
        },
    )
    duration_type: None | CvnDurationTypeType = field(
        default=None,
        metadata={
            "name": "DurationType",
            "type": "Element",
            "namespace": "",
        },
    )


class EconomicDimensionType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    value: None | CvnString = field(
        default=None,
        metadata={
            "name": "Value",
            "type": "Element",
            "namespace": "",
        },
    )
    currency_type: CurrencyTypeType = field(
        metadata={
            "name": "CurrencyType",
            "type": "Element",
            "namespace": "",
        }
    )
    type_value: EconomicDimensionTypeType = field(
        metadata={
            "name": "Type",
            "type": "Element",
            "namespace": "",
        }
    )


class EditionType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    text: None | CvnString = field(
        default=None,
        metadata={
            "name": "Text",
            "type": "Element",
            "namespace": "",
        },
    )
    type_value: EditionTypeType = field(
        metadata={
            "name": "Type",
            "type": "Element",
            "namespace": "",
        }
    )


class EntityIdtype(BaseModel):
    class Meta:
        name = "EntityIDType"

    model_config = ConfigDict(defer_build=True)
    local_pk: list[LocalPktype] = field(
        default_factory=list,
        metadata={
            "name": "LocalPK",
            "type": "Element",
            "namespace": "",
        },
    )
    cvnpk: None | CvnString = field(
        default=None,
        metadata={
            "name": "CVNPK",
            "type": "Element",
            "namespace": "",
        },
    )


class ExternalPktype(BaseModel):
    class Meta:
        name = "ExternalPKType"

    model_config = ConfigDict(defer_build=True)
    type_value: None | ExternalPktypeType = field(
        default=None,
        metadata={
            "name": "Type",
            "type": "Element",
            "namespace": "",
        },
    )
    code: None | CvnString = field(
        default=None,
        metadata={
            "name": "Code",
            "type": "Element",
            "namespace": "",
        },
    )


class FilterType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    type_value: FilterTypeType = field(
        metadata={
            "name": "Type",
            "type": "Element",
            "namespace": "",
        }
    )
    value: None | FilterValueType = field(
        default=None,
        metadata={
            "name": "Value",
            "type": "Element",
            "namespace": "",
        },
    )
    others: None | CvnString = field(
        default=None,
        metadata={
            "name": "Others",
            "type": "Element",
            "namespace": "",
        },
    )


class Idtype(BaseModel):
    class Meta:
        name = "IDType"

    model_config = ConfigDict(defer_build=True)
    cvnpk: None | CvnString = field(
        default=None,
        metadata={
            "name": "CVNPK",
            "type": "Element",
            "namespace": "",
        },
    )
    code_cvnitem: CodeCvnitemType = field(
        metadata={
            "name": "CodeCVNItem",
            "type": "Element",
            "namespace": "",
        }
    )
    experience_type: None | ExperienceTypeType = field(
        default=None,
        metadata={
            "name": "ExperienceType",
            "type": "Element",
            "namespace": "",
        },
    )
    result_type: None | ResultTypeType = field(
        default=None,
        metadata={
            "name": "ResultType",
            "type": "Element",
            "namespace": "",
        },
    )


class PhysicalDimensionType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    value: None | CvnString = field(
        default=None,
        metadata={
            "name": "Value",
            "type": "Element",
            "namespace": "",
        },
    )
    type_value: PhysicalDimensionalTypeType = field(
        metadata={
            "name": "Type",
            "type": "Element",
            "namespace": "",
        }
    )


class QualityType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    measure: None | CvnString = field(
        default=None,
        metadata={
            "name": "Measure",
            "type": "Element",
            "namespace": "",
        },
    )
    type_value: QualityTypeType = field(
        metadata={
            "name": "Type",
            "type": "Element",
            "namespace": "",
        }
    )
    max_value: None | CvnString = field(
        default=None,
        metadata={
            "name": "MaxValue",
            "type": "Element",
            "namespace": "",
        },
    )
    moment: None | QualityMomentType = field(
        default=None,
        metadata={
            "name": "Moment",
            "type": "Element",
            "namespace": "",
        },
    )
    agency: None | QualityAgencyType = field(
        default=None,
        metadata={
            "name": "Agency",
            "type": "Element",
            "namespace": "",
        },
    )
    date: None | FlexibleDatesType = field(
        default=None,
        metadata={
            "name": "Date",
            "type": "Element",
            "namespace": "",
        },
    )
    others: None | CvnString = field(
        default=None,
        metadata={
            "name": "Others",
            "type": "Element",
            "namespace": "",
        },
    )


class RegionType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    code: None | CodeRegionType = field(
        default=None,
        metadata={
            "name": "Code",
            "type": "Element",
            "namespace": "",
        },
    )
    name: None | CvnString = field(
        default=None,
        metadata={
            "name": "Name",
            "type": "Element",
            "namespace": "",
        },
    )


class RollType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    value: None | RollValueType = field(
        default=None,
        metadata={
            "name": "Value",
            "type": "Element",
            "namespace": "",
        },
    )
    others: None | CvnString = field(
        default=None,
        metadata={
            "name": "Others",
            "type": "Element",
            "namespace": "",
        },
    )
    signature: None | CvnString = field(
        default=None,
        metadata={
            "name": "Signature",
            "type": "Element",
            "namespace": "",
        },
    )
    signature_order: None | CvnString = field(
        default=None,
        metadata={
            "name": "SignatureOrder",
            "type": "Element",
            "namespace": "",
        },
    )


class ScopeType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    type_value: None | ScopeTypeType = field(
        default=None,
        metadata={
            "name": "Type",
            "type": "Element",
            "namespace": "",
        },
    )
    others: None | CvnString = field(
        default=None,
        metadata={
            "name": "Others",
            "type": "Element",
            "namespace": "",
        },
    )


class SubjectType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    type_value: SubjectTypeType = field(
        metadata={
            "name": "Type",
            "type": "Element",
            "namespace": "",
        }
    )
    subject_list: None | CvnString = field(
        default=None,
        metadata={
            "name": "SubjectList",
            "type": "Element",
            "namespace": "",
        },
    )
    subject_agency: None | CvnString = field(
        default=None,
        metadata={
            "name": "SubjectAgency",
            "type": "Element",
            "namespace": "",
        },
    )
    description: None | SubjectType.Description = field(
        default=None,
        metadata={
            "name": "Description",
            "type": "Element",
            "namespace": "",
        },
    )

    class Description(BaseModel):
        model_config = ConfigDict(defer_build=True)
        primary: list[CvnString] = field(
            default_factory=list,
            metadata={
                "name": "Primary",
                "type": "Element",
                "namespace": "",
            },
        )
        secondary: list[CvnString] = field(
            default_factory=list,
            metadata={
                "name": "Secondary",
                "type": "Element",
                "namespace": "",
            },
        )
        tertiary: list[CvnString] = field(
            default_factory=list,
            metadata={
                "name": "Tertiary",
                "type": "Element",
                "namespace": "",
            },
        )


class SubtypeType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    sub_type1: SubType1Type = field(
        metadata={
            "name": "SubType1",
            "type": "Element",
            "namespace": "",
        }
    )
    sub_type2: None | SubType2Type = field(
        default=None,
        metadata={
            "name": "SubType2",
            "type": "Element",
            "namespace": "",
        },
    )


class UrlType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    value: None | CvnString = field(
        default=None,
        metadata={
            "name": "Value",
            "type": "Element",
            "namespace": "",
        },
    )
    access_to: AccessToType = field(
        metadata={
            "name": "AccessTo",
            "type": "Element",
            "namespace": "",
        }
    )


class AddressType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    city: None | CvnString = field(
        default=None,
        metadata={
            "name": "City",
            "type": "Element",
            "namespace": "",
        },
    )
    streets: None | CvnString = field(
        default=None,
        metadata={
            "name": "Streets",
            "type": "Element",
            "namespace": "",
        },
    )
    other_information: None | CvnString = field(
        default=None,
        metadata={
            "name": "OtherInformation",
            "type": "Element",
            "namespace": "",
        },
    )
    postal_code: None | CvnString = field(
        default=None,
        metadata={
            "name": "PostalCode",
            "type": "Element",
            "namespace": "",
        },
    )
    region: None | RegionType = field(
        default=None,
        metadata={
            "name": "Region",
            "type": "Element",
            "namespace": "",
        },
    )
    country_code: None | CvnIso3166 = field(
        default=None,
        metadata={
            "name": "CountryCode",
            "type": "Element",
            "namespace": "",
        },
    )
    province: None | AddressType.Province = field(
        default=None,
        metadata={
            "name": "Province",
            "type": "Element",
            "namespace": "",
        },
    )

    class Province(BaseModel):
        model_config = ConfigDict(defer_build=True)
        code: None | CvnString = field(
            default=None,
            metadata={
                "name": "Code",
                "type": "Element",
                "namespace": "",
            },
        )
        name: None | CvnString = field(
            default=None,
            metadata={
                "name": "Name",
                "type": "Element",
                "namespace": "",
            },
        )


class AncestorEntityType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    entity_name: CvnString = field(
        metadata={
            "name": "EntityName",
            "type": "Element",
            "namespace": "",
        }
    )
    entity_id: None | EntityIdtype = field(
        default=None,
        metadata={
            "name": "EntityID",
            "type": "Element",
            "namespace": "",
        },
    )
    level: None | CvnString = field(
        default=None,
        metadata={
            "name": "Level",
            "type": "Element",
            "namespace": "",
        },
    )


class DiffusionType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    title: TitleType = field(
        metadata={
            "name": "Title",
            "type": "Element",
            "namespace": "",
        }
    )
    location: None | LocationType = field(
        default=None,
        metadata={
            "name": "Location",
            "type": "Element",
            "namespace": "",
        },
    )
    external_pk: None | ExternalPktype = field(
        default=None,
        metadata={
            "name": "ExternalPK",
            "type": "Element",
            "namespace": "",
        },
    )
    date: FlexibleDatesType = field(
        metadata={
            "name": "Date",
            "type": "Element",
            "namespace": "",
        }
    )
    diffusion: list[CvnBoolean] = field(
        default_factory=list,
        metadata={
            "name": "Diffusion",
            "type": "Element",
            "namespace": "",
        },
    )


class PersonalIdentificationType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    photo: None | PhotoType = field(
        default=None,
        metadata={
            "name": "Photo",
            "type": "Element",
            "namespace": "",
        },
    )
    given_name: None | CvnString = field(
        default=None,
        metadata={
            "name": "GivenName",
            "type": "Element",
            "namespace": "",
        },
    )
    first_family_name: None | CvnString = field(
        default=None,
        metadata={
            "name": "FirstFamilyName",
            "type": "Element",
            "namespace": "",
        },
    )
    second_family_name: None | CvnString = field(
        default=None,
        metadata={
            "name": "SecondFamilyName",
            "type": "Element",
            "namespace": "",
        },
    )
    signature: list[CvnString] = field(
        default_factory=list,
        metadata={
            "name": "Signature",
            "type": "Element",
            "namespace": "",
        },
    )
    official_id: None | OfficialIdType = field(
        default=None,
        metadata={
            "name": "OfficialId",
            "type": "Element",
            "namespace": "",
        },
    )
    normalized_identification: None | CvnString = field(
        default=None,
        metadata={
            "name": "NormalizedIdentification",
            "type": "Element",
            "namespace": "",
        },
    )
    local_pk: list[LocalPktype] = field(
        default_factory=list,
        metadata={
            "name": "LocalPK",
            "type": "Element",
            "namespace": "",
        },
    )
    nacionality: list[CvnIso3166] = field(
        default_factory=list,
        metadata={
            "name": "Nacionality",
            "type": "Element",
            "namespace": "",
        },
    )
    birth_date: None | CvnDate = field(
        default=None,
        metadata={
            "name": "BirthDate",
            "type": "Element",
            "namespace": "",
        },
    )
    birth_country: None | CvnIso3166 = field(
        default=None,
        metadata={
            "name": "BirthCountry",
            "type": "Element",
            "namespace": "",
        },
    )
    birth_region: None | RegionType = field(
        default=None,
        metadata={
            "name": "BirthRegion",
            "type": "Element",
            "namespace": "",
        },
    )
    birth_city: None | CvnString = field(
        default=None,
        metadata={
            "name": "BirthCity",
            "type": "Element",
            "namespace": "",
        },
    )
    gender: None | GenderType = field(
        default=None,
        metadata={
            "name": "Gender",
            "type": "Element",
            "namespace": "",
        },
    )


class PlaceType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    moment: MomentPlaceType = field(
        metadata={
            "name": "Moment",
            "type": "Element",
            "namespace": "",
        }
    )
    city: None | CvnString = field(
        default=None,
        metadata={
            "name": "City",
            "type": "Element",
            "namespace": "",
        },
    )
    region: None | RegionType = field(
        default=None,
        metadata={
            "name": "Region",
            "type": "Element",
            "namespace": "",
        },
    )
    postal_code: None | CvnString = field(
        default=None,
        metadata={
            "name": "PostalCode",
            "type": "Element",
            "namespace": "",
        },
    )
    country_code: None | CvnIso3166 = field(
        default=None,
        metadata={
            "name": "CountryCode",
            "type": "Element",
            "namespace": "",
        },
    )


class EntityType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    entity_scope: None | EntityScopeType = field(
        default=None,
        metadata={
            "name": "EntityScope",
            "type": "Element",
            "namespace": "",
        },
    )
    juridical_scope: None | JuridicalScopeType = field(
        default=None,
        metadata={
            "name": "JuridicalScope",
            "type": "Element",
            "namespace": "",
        },
    )
    type_value: None | EntityTypeType = field(
        default=None,
        metadata={
            "name": "Type",
            "type": "Element",
            "namespace": "",
        },
    )
    entity_name: list[EntityNameType] = field(
        default_factory=list,
        metadata={
            "name": "EntityName",
            "type": "Element",
            "namespace": "",
        },
    )
    entity_id: None | EntityIdtype = field(
        default=None,
        metadata={
            "name": "EntityID",
            "type": "Element",
            "namespace": "",
        },
    )
    ancestor_entity: list[AncestorEntityType] = field(
        default_factory=list,
        metadata={
            "name": "AncestorEntity",
            "type": "Element",
            "namespace": "",
        },
    )
    roll: None | CvnString = field(
        default=None,
        metadata={
            "name": "Roll",
            "type": "Element",
            "namespace": "",
        },
    )


class VersionIdtype(BaseModel):
    class Meta:
        name = "VersionIDType"

    model_config = ConfigDict(defer_build=True)
    cvn_identification: None | CvnString = field(
        default=None,
        metadata={
            "name": "CVN_Identification",
            "type": "Element",
            "namespace": "",
        },
    )
    personal_identification: None | PersonalIdentificationType = field(
        default=None,
        metadata={
            "name": "PersonalIdentification",
            "type": "Element",
            "namespace": "",
        },
    )
    authorization: list[AuthorizationType] = field(
        default_factory=list,
        metadata={
            "name": "Authorization",
            "type": "Element",
            "namespace": "",
        },
    )
    surrender: list[AuthorizationType] = field(
        default_factory=list,
        metadata={
            "name": "Surrender",
            "type": "Element",
            "namespace": "",
        },
    )
    date: CvnDate = field(
        metadata={
            "name": "Date",
            "type": "Element",
            "namespace": "",
        }
    )
    cvlanguage: None | LanguageType = field(
        default=None,
        metadata={
            "name": "CVLanguage",
            "type": "Element",
            "namespace": "",
        },
    )
    digital_signature: list[DigitalSignatureType] = field(
        default_factory=list,
        metadata={
            "name": "DigitalSignature",
            "type": "Element",
            "namespace": "",
        },
    )
    codification_version: None | CvnString = field(
        default=None,
        metadata={
            "name": "CodificationVersion",
            "type": "Element",
            "namespace": "",
        },
    )
    cvuser: None | CvuserType = field(
        default=None,
        metadata={
            "name": "CVUser",
            "type": "Element",
            "namespace": "",
        },
    )
    extension_field: list[ExtensionType] = field(
        default_factory=list,
        metadata={
            "name": "ExtensionField",
            "type": "Element",
            "namespace": "",
        },
    )


class CvnItemType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    cvn_item_id: Idtype = field(
        metadata={
            "name": "CvnItemID",
            "type": "Element",
            "namespace": "",
        }
    )
    subtype: None | SubtypeType = field(
        default=None,
        metadata={
            "name": "Subtype",
            "type": "Element",
            "namespace": "",
        },
    )
    title: list[TitleType] = field(
        default_factory=list,
        metadata={
            "name": "Title",
            "type": "Element",
            "namespace": "",
        },
    )
    description: list[CvnString] = field(
        default_factory=list,
        metadata={
            "name": "Description",
            "type": "Element",
            "namespace": "",
        },
    )
    subject: list[SubjectType] = field(
        default_factory=list,
        metadata={
            "name": "Subject",
            "type": "Element",
            "namespace": "",
        },
    )
    filter: list[FilterType] = field(
        default_factory=list,
        metadata={
            "name": "Filter",
            "type": "Element",
            "namespace": "",
        },
    )
    edition: list[EditionType] = field(
        default_factory=list,
        metadata={
            "name": "Edition",
            "type": "Element",
            "namespace": "",
        },
    )
    link: list[CvnItemType] = field(
        default_factory=list,
        metadata={
            "name": "Link",
            "type": "Element",
            "namespace": "",
        },
    )
    entity: list[EntityType] = field(
        default_factory=list,
        metadata={
            "name": "Entity",
            "type": "Element",
            "namespace": "",
        },
    )
    date: list[DateType] = field(
        default_factory=list,
        metadata={
            "name": "Date",
            "type": "Element",
            "namespace": "",
        },
    )
    author: list[Author] = field(
        default_factory=list,
        metadata={
            "name": "Author",
            "type": "Element",
            "namespace": "",
        },
    )
    dedication: list[DedicationType] = field(
        default_factory=list,
        metadata={
            "name": "Dedication",
            "type": "Element",
            "namespace": "",
        },
    )
    roll: None | RollType = field(
        default=None,
        metadata={
            "name": "Roll",
            "type": "Element",
            "namespace": "",
        },
    )
    collaborator: list[CollaboratorType] = field(
        default_factory=list,
        metadata={
            "name": "Collaborator",
            "type": "Element",
            "namespace": "",
        },
    )
    place: list[PlaceType] = field(
        default_factory=list,
        metadata={
            "name": "Place",
            "type": "Element",
            "namespace": "",
        },
    )
    economic_dimension: list[EconomicDimensionType] = field(
        default_factory=list,
        metadata={
            "name": "EconomicDimension",
            "type": "Element",
            "namespace": "",
        },
    )
    physical_dimension: list[PhysicalDimensionType] = field(
        default_factory=list,
        metadata={
            "name": "PhysicalDimension",
            "type": "Element",
            "namespace": "",
        },
    )
    location: list[LocationType] = field(
        default_factory=list,
        metadata={
            "name": "Location",
            "type": "Element",
            "namespace": "",
        },
    )
    external_pk: list[ExternalPktype] = field(
        default_factory=list,
        metadata={
            "name": "ExternalPK",
            "type": "Element",
            "namespace": "",
        },
    )
    local_pk: list[LocalPktype] = field(
        default_factory=list,
        metadata={
            "name": "LocalPK",
            "type": "Element",
            "namespace": "",
        },
    )
    scope: list[ScopeType] = field(
        default_factory=list,
        metadata={
            "name": "Scope",
            "type": "Element",
            "namespace": "",
        },
    )
    diffusion: list[DiffusionType] = field(
        default_factory=list,
        metadata={
            "name": "Diffusion",
            "type": "Element",
            "namespace": "",
        },
    )
    quality: list[QualityType] = field(
        default_factory=list,
        metadata={
            "name": "Quality",
            "type": "Element",
            "namespace": "",
        },
    )
    url: list[UrlType] = field(
        default_factory=list,
        metadata={
            "name": "Url",
            "type": "Element",
            "namespace": "",
        },
    )
    language: list[LanguageType] = field(
        default_factory=list,
        metadata={
            "name": "Language",
            "type": "Element",
            "namespace": "",
        },
    )
    validation: None | ValidationType = field(
        default=None,
        metadata={
            "name": "Validation",
            "type": "Element",
            "namespace": "",
        },
    )
    contact: list[ContactType] = field(
        default_factory=list,
        metadata={
            "name": "Contact",
            "type": "Element",
            "namespace": "",
        },
    )
    collection: list[CvnString] = field(
        default_factory=list,
        metadata={
            "name": "Collection",
            "type": "Element",
            "namespace": "",
        },
    )


class IdentificationType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    personal_identification: None | PersonalIdentificationType = field(
        default=None,
        metadata={
            "name": "PersonalIdentification",
            "type": "Element",
            "namespace": "",
        },
    )
    entity_identification: None | EntityType = field(
        default=None,
        metadata={
            "name": "EntityIdentification",
            "type": "Element",
            "namespace": "",
        },
    )
    external_pk: list[ExternalPktype] = field(
        default_factory=list,
        metadata={
            "name": "ExternalPK",
            "type": "Element",
            "namespace": "",
        },
    )


class VersionType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    version_id: VersionIdtype = field(
        metadata={
            "name": "VersionID",
            "type": "Element",
            "namespace": "",
        }
    )


class AgentType(BaseModel):
    model_config = ConfigDict(defer_build=True)
    identification: None | IdentificationType = field(
        default=None,
        metadata={
            "name": "Identification",
            "type": "Element",
            "namespace": "",
        },
    )
    address: None | AddressType = field(
        default=None,
        metadata={
            "name": "Address",
            "type": "Element",
            "namespace": "",
        },
    )
    contact: list[ContactType] = field(
        default_factory=list,
        metadata={
            "name": "Contact",
            "type": "Element",
            "namespace": "",
        },
    )


class Cvn(BaseModel):
    class Meta:
        name = "CVN"
        namespace = "http://cv.normalizado.org/cvn"

    model_config = ConfigDict(defer_build=True)
    version: VersionType = field(
        metadata={
            "name": "Version",
            "type": "Element",
            "namespace": "",
        }
    )
    agent: AgentType = field(
        metadata={
            "name": "Agent",
            "type": "Element",
            "namespace": "",
        }
    )
    cvn_item: list[CvnItemType] = field(
        default_factory=list,
        metadata={
            "name": "CvnItem",
            "type": "Element",
            "namespace": "",
        },
    )
