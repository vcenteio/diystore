from decimal import Decimal

from pydantic import BaseModel
from pydantic import Field
from pydantic import validator

from ..helpers import round_decimal


class ProductDimensions(BaseModel):
    height: Decimal = Field(gt=0, lt=100_000, decimal_places=1)
    width: Decimal = Field(gt=0, lt=100_000, decimal_places=1)
    length: Decimal = Field(gt=0, lt=100_000, decimal_places=1)

    class Config:
        validate_assignment = True

    @validator("height", "width", "length", always=True)
    def _round_dimension(cls, d: Decimal):
        return round_decimal(d, "1.0")

    def get_str(self):
        return self.__str__()
    
    def __str__(self):
        return f"{self.height} X {self.width} X {self.length}"
