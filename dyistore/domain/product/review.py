from datetime import datetime
from decimal import Decimal
from uuid import UUID
from uuid import uuid4

from pydantic import BaseModel
from pydantic import Field
from pydantic import validator
from pydantic import Extra
import pendulum
from pendulum.datetime import DateTime

from ..helpers import round_decimal


class ProductReview(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    product_id: UUID = Field(...)
    client_id: UUID = Field(...)
    rating: Decimal = Field(decimal_places=1, ge=0, le=5)
    creation_date: datetime = Field(...)
    feedback: str = Field(default=None, min_length=1, max_length=3000)

    class Config:
        frozen = True
        extra = Extra.forbid

    @validator("rating")
    def _round_rating(cls, rating):
        return round_decimal(rating, "1.0")

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
