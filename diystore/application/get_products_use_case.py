from enum import IntEnum
from uuid import UUID
from decimal import Decimal

from pydantic import Field
from pydantic import BaseModel
from pydantic import validator
from pydantic import constr
from pydantic import conint

from .repository import Repository
from ..domain.helpers import round_decimal


class OrderingProperty(IntEnum):
    PRICE = 1
    RATING = 2


class OrderingType(IntEnum):
    ASCENDING = 1
    DESCESDING = 2


class ProductOrderingCriteria(BaseModel):
    property: OrderingProperty
    type: OrderingType


class GetProductsInputDTO(BaseModel):
    category_id: UUID = Field(...)
    price_min: Decimal = Field(default=0, ge=0, le=1_000_000)
    price_max: Decimal = Field(default=1_000_000, ge=0, le=1_000_000)
    rating_min: Decimal = Field(default=0, ge=0, le=5)
    rating_max: Decimal = Field(default=5, ge=0, le=5)
    ordering_criteria: ProductOrderingCriteria = Field(default=None)
    with_discounts: bool = Field(default=False)

    @validator("price_min", "price_max")
    def _validate_price_min_max(cls, price):
        return round_decimal(price, "1.00")

    @validator("rating_min", "rating_max")
    def _validate_rating_min_max(cls, rating):
        return round_decimal(rating, "1.0")

