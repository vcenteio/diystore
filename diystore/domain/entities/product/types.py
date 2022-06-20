import re
from decimal import Decimal

from ...helpers import round_decimal


class ProductRating(Decimal):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, (Decimal, int, str, float)):
            raise TypeError("Rating init value should be a Decimal, int, str or float")
        value = Decimal(v)
        if value < 0 or value > 5:
            raise ValueError("Rating should be between 0 and 5")
        return cls(round_decimal(value, "1.0"))

    def __repr__(self) -> str:
        return f"Rating({super().__str__()})"


class EAN13(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not re.match(r"^\d{13}$", str(v)):
            raise ValueError(
                f"EAN13 value should be composed of 13 digits; passed argument: {v}"
            )
        return cls(v)
