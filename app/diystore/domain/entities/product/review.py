from datetime import datetime
from uuid import UUID
from uuid import uuid4

import pendulum
from pendulum.datetime import DateTime
from pydantic import BaseModel
from pydantic import Field
from pydantic import validator
from pydantic import Extra

from .types import ProductRating


class ProductReview(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    product_id: UUID = Field(...)
    client_id: UUID = Field(...)
    rating: ProductRating = Field(...)
    creation_date: DateTime = Field(...)
    feedback: str = Field(default=None, min_length=1, max_length=3000)

    class Config:
        frozen = True
        extra = Extra.forbid

    @staticmethod
    def _ensure_creation_date_is_not_future_date(date: DateTime):
        if date.is_future():
            raise ValueError("creation date should not refer to a future date")

    @staticmethod
    def _ensure_creation_date_is_utc_aware(date: DateTime):
        if not date.is_utc():
            raise ValueError("creation date must have UTC timezone")

    @validator("creation_date")
    def _validate_creation_date(cls, date: datetime):
        date = pendulum.instance(date, tz=date.tzinfo)
        cls._ensure_creation_date_is_not_future_date(date)
        cls._ensure_creation_date_is_utc_aware(date)
        return date
