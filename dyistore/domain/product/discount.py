from decimal import Decimal
from uuid import UUID
from uuid import uuid4
from datetime import datetime

from pydantic import Field
from pydantic import BaseModel
from pydantic import validator
from pydantic import constr
from pendulum import now


class Discount(BaseModel):
    rate: Decimal = Field(le=1, gt=0, decimal_places=2)
    name: constr(strict=True, max_length=50) = Field()
    creation_date: datetime = Field(default_factory=lambda: now("UTC"))
    expiry_date: datetime = Field(default_factory=lambda: now("UTC").add(months=1))
    id: UUID = Field(default_factory=uuid4)

    @validator("creation_date", always=True)
    def creation_date_cannot_be_in_the_future(cls, date):
        if date > now("UTC"):
            raise ValueError("creation_date should not be a future date")
        return date

    @validator("expiry_date", always=True)
    def expiry_date_must_be_greater_than_creation_date(cls, date, values):
        if "creation_date" in values and date <= values["creation_date"]:
            raise ValueError("expiry_date must be greater than creation_date")
        return date
