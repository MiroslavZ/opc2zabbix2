import logging
from decimal import Decimal
from typing import Any
from asyncua.ua import VariantType


_logger = logging.getLogger(__name__)


def convert_to_type(value: Any, type: VariantType) -> Any:
    result = value
    try:
        match type:
            case VariantType.Boolean:
                result = bool(value)
            case VariantType.Byte:
                result = bytes(value)
            case VariantType.Int16, VariantType.UInt16, VariantType.Int32, VariantType.UInt32, VariantType.Int64, VariantType.UInt64:
                result = int(value)
            case VariantType.Float:
                result = float(value)
            case VariantType.Double:
                result = Decimal(value)
            case VariantType.String:
                result = str(value)
    except:
        _logger.warning(f"Unable to convert {value} to type {type}")
    return result