from decimal import Decimal
from uuid import UUID
from typing import Optional

from pydantic import BaseModel
from pydantic import Field
from pydantic import validator
from pydantic import PrivateAttr

from .discount import Discount
from .vat import VAT
from ...helpers import optional


class ProductPrice(BaseModel):
    value: Decimal = Field(ge=0.01, le=999_999.99, decimal_places=2)
    vat: VAT = Field(...)
    discount: Discount = Field(default=None)
    _rounding_template: Decimal = PrivateAttr(default=Decimal("1.00"))

    class Config:
        validate_assignment = True

    @validator("value", pre=True)
    def _ensure_correct_type(cls, value):
        if not isinstance(value, (Decimal, int, float, str)):
            raise ValueError("value should be of type Decimal, int, float or str")
        return value

    def _apply_discount(self) -> Decimal:
        return self.value - (self.value * self.discount)

    def _add_vat(self, value: Decimal) -> Decimal:
        return value + (value * self.vat)

    def _round(self, value: Decimal) -> Decimal:
        return value.quantize(self._rounding_template)

    def calculate_without_discount(self) -> Decimal:
        return self._round(self._add_vat(self.value))

    def calculate(self) -> Decimal:
        try:
            v = self._apply_discount()
        except TypeError:
            v = self.value
        return self._round(self._add_vat(v))

    @optional(e=AttributeError)
    def get_discount_id(self) -> Optional[UUID]:
        return self.discount.id

    @optional(e=AttributeError)
    def get_discount_id_in_bytes_format(self) -> Optional[bytes]:
        return self.discount.id.bytes

    @optional(e=AttributeError)
    def get_discount_rate(self) -> Optional[Decimal]:
        return self.discount.rate

    def get_vat_id(self) -> UUID:
        return self.vat.id

    def get_vat_rate(self) -> Decimal:
        return self.vat.rate
