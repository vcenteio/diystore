from enum import IntEnum

from pydantic import BaseModel

class OrderingProperty(IntEnum):
    PRICE = 1
    RATING = 2


class OrderingType(IntEnum):
    ASCENDING = 1
    DESCESDING = 2


class ProductOrderingCriteria(BaseModel):
    property: OrderingProperty
    type: OrderingType
