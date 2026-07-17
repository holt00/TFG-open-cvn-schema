from __future__ import annotations

from decimal import Decimal, InvalidOperation

from open_cvn.xml_semantic_mapping import XmlFieldMapping


def convert_xml_value(raw_value: str, mapping: XmlFieldMapping) -> object:
    value = raw_value.strip()
    if not value:
        return {"raw_value": raw_value}

    if _is_controlled_reference(mapping):
        converted = {"source": mapping.source_reference, "raw_value": value}
        if _looks_like_code(value):
            converted["code"] = value
        else:
            converted["label"] = value
        return converted

    ref = mapping.schema.get("$ref")
    if ref == "#/$defs/FlexibleDateValue":
        return _flexible_date(value)
    if ref == "#/$defs/OfficialIdValue":
        return {"raw_value": value}
    if ref == "#/$defs/EntityNameValue":
        return {"raw_value": value}
    if ref == "#/$defs/EntityTypeValue":
        return {"raw_value": value}

    schema_type = mapping.schema.get("type")
    if schema_type == "array":
        return [value]
    if _schema_accepts_bool(schema_type):
        boolean = _boolean_or_none(value)
        if boolean is not None:
            return boolean
    if _schema_accepts_number(schema_type):
        decimal = _decimal_or_none(value)
        if decimal is not None:
            return decimal
    return value


def _is_controlled_reference(mapping: XmlFieldMapping) -> bool:
    shape = mapping.domain_shape_kind or ""
    return "reference" in shape or mapping.source_reference is not None


def _looks_like_code(value: str) -> bool:
    return bool(value) and not any(character.isspace() for character in value)


def _schema_accepts_bool(schema_type: object) -> bool:
    return schema_type == "boolean" or (isinstance(schema_type, list) and "boolean" in schema_type)


def _schema_accepts_number(schema_type: object) -> bool:
    if isinstance(schema_type, list):
        return bool({"number", "integer"} & set(schema_type))
    return schema_type in {"number", "integer"}


def _boolean_or_none(value: str) -> bool | None:
    normalized = value.strip().lower()
    if normalized in {"true", "1", "si", "sí"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    return None


def _decimal_or_none(value: str) -> int | float | None:
    try:
        decimal = Decimal(value.replace(",", "."))
    except InvalidOperation:
        return None
    if decimal == decimal.to_integral_value():
        return int(decimal)
    return float(decimal)


def _flexible_date(value: str) -> dict[str, object]:
    parts = value.split("-")
    result: dict[str, object] = {"raw_value": value}
    if len(parts) >= 1 and len(parts[0]) == 4 and parts[0].isdigit():
        result["year"] = int(parts[0])
    if len(parts) >= 2 and len(parts[1]) in {1, 2} and parts[1].isdigit():
        result["month"] = int(parts[1])
    if len(parts) >= 3 and len(parts[2]) in {1, 2} and parts[2].isdigit():
        result["day"] = int(parts[2])
    return result
