from uuid import UUID
from uuid import uuid4
from decimal import Decimal

from pydantic import BaseModel
from pydantic import Field
from pydantic import constr


class VAT(BaseModel):
    rate: Decimal = Field(ge=0, le=1, decimal_places=2)
    name: constr(min_length=2, max_length=20, strict=True) = Field(...)
    id: UUID = Field(default_factory=uuid4)

    class Config:
        validate_assignment = True

    def __mul__(self, other):
        return self.rate * other

    def __rmul__(self, other):
        return self.__mul__(other)
