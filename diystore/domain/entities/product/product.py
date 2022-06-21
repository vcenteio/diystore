from uuid import UUID
from uuid import uuid4
from decimal import Decimal
from datetime import datetime
from typing import Union
from typing import Optional

import pendulum
from pendulum.datetime import DateTime
from pydantic import BaseModel
from pydantic import Field
from pydantic import constr
from pydantic import conint
from pydantic import validator
from pydantic import Extra

from .price import ProductPrice
from .discount import Discount
from .vat import VAT
from .dimensions import ProductDimensions
from .categories import (
    MidLevelProductCategory,
    TerminalLevelProductCategory,
    TopLevelProductCategory,
)
from .review import ProductReview
from .types import EAN13
from .types import ProductRating
from .photo import ProductPhotoUrl
from .vendor import ProductVendor
from ...helpers import round_decimal


class Product(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    ean: EAN13 = Field(...)
    name: constr(strict=True, min_length=1, max_length=50) = Field(...)
    description: str = Field(min_length=1, max_length=3000, default=None, repr=False)
    price: ProductPrice = Field(...)
    quantity: conint(strict=True, ge=0, le=1_000_000) = Field(...)
    creation_date: DateTime = Field(...)
    dimensions: ProductDimensions = Field(default=None)
    color: constr(min_length=1, max_length=30, to_lower=True) = Field(default=None)
    material: constr(min_length=1, max_length=30, to_lower=True) = Field(default=None)
    country_of_origin: constr(min_length=1, max_length=60) = Field(...)
    warranty: conint(strict=True, ge=0, le=10) = Field(...)
    category: TerminalLevelProductCategory = Field(...)
    rating: ProductRating = Field(default=None)
    reviews: Optional[list[ProductReview]] = Field(default=[])
    photo_url: ProductPhotoUrl = Field(default=None)
    vendor: ProductVendor = Field(...)

    class Config:
        validate_assignment = True
        extra = Extra.forbid

    @validator("ean", pre=True)
    def _validate_ean(cls, ean):
        if not isinstance(ean, (str, int)):
            raise ValueError(f"ean must be str or int, not {ean.__class__.__name__}")
        return ean

    @staticmethod
    def _convert_datetime_to_correct_type(date: datetime) -> DateTime:
        return pendulum.instance(date)

    @staticmethod
    def _ensure_datetime_is_not_future(date: DateTime):
        if date.is_future():
            raise ValueError("creation_date should not be a future date")

    @staticmethod
    def _ensure_datetime_is_utc(date: DateTime):
        if not date.is_utc():
            raise ValueError("creation_date should have UTC timezone")

    @validator("creation_date", pre=True)
    def _validate_creation_date_pre(cls, date):
        if isinstance(date, int):
            raise TypeError("creation_date argument should not be an int")
        return date

    @validator("creation_date")
    def _validate_creation_date(cls, date):
        date = cls._convert_datetime_to_correct_type(date)
        cls._ensure_datetime_is_utc(date)
        cls._ensure_datetime_is_not_future(date)
        return date

    @validator("color", "material", "description", "country_of_origin", pre=True)
    def _validate_non_strict_constr(cls, v, field):
        if not isinstance(v, str) and v is not None:
            raise TypeError(
                f"{field.name} should be str or None, not {v.__class__.__name__}"
            )
        return v

    @staticmethod
    def _ensure_value_is_not_none(value):
        if value is None:
            raise ValueError("None is not an allowed value")

    @staticmethod
    def _ensure_category_is_correct_type(category):
        if not isinstance(category, (TerminalLevelProductCategory, dict)):
            raise TypeError(
                "category argument must be a TerminalLevelProductCategory object "
                "or a valid dict"
            )

    @validator("category", pre=True)
    def _validate_category(cls, category):
        cls._ensure_value_is_not_none(category)
        cls._ensure_category_is_correct_type(category)
        return category

    def get_id_in_bytes_format(self) -> bytes:
        return self.id.bytes

    def get_final_price(self, with_discount: bool = True) -> Decimal:
        if with_discount:
            return self.price.calculate()
        return self.price.calculate_without_discount()

    def get_base_price(self) -> Decimal:
        return self.price.value

    def set_base_price(self, price: Decimal):
        self.price.value = price

    def get_discount_id(self) -> UUID:
        return self.price.get_discount_id()

    def get_discount_id_in_bytes_format(self) -> bytes:
        return self.price.get_discount_id().bytes

    def get_discount_rate(self):
        return self.price.get_discount_rate()

    def get_discount(self):
        return self.price.discount

    def set_discount(self, discount: Discount):
        self.price.discount = discount

    def get_vat_id(self) -> UUID:
        return self.price.get_vat_id()

    def get_vat_id_in_bytes_format(self) -> bytes:
        return self.price.get_vat_id().bytes

    def get_vat_rate(self) -> Decimal:
        return self.price.get_vat_rate()

    def get_vat(self) -> VAT:
        return self.price.vat

    def set_vat(self, vat: VAT):
        self.price.vat = vat

    def get_dimensions_str(self) -> str:
        return self.dimensions.get_str()

    def get_dimensions_dict(self) -> dict:
        return self.dimensions.dict()

    def get_height(self) -> Decimal:
        return self.dimensions.height

    def get_width(self) -> Decimal:
        return self.dimensions.width

    def get_length(self) -> Decimal:
        return self.dimensions.length

    def set_dimensions(
        self,
        height: Union[Decimal, float, int, str],
        width: Union[Decimal, float, int, str],
        length: Union[Decimal, float, int, str],
    ):
        self.dimensions.height = height
        self.dimensions.width = width
        self.dimensions.length = length

    def get_category_id(self) -> UUID:
        return self.category.id

    def get_category_id_in_bytes_format(self) -> bytes:
        return self.category.id.bytes

    def get_category_name(self) -> str:
        return self.category.name

    def get_category_description(self) -> str:
        return self.category.description

    def get_parent_category(self) -> MidLevelProductCategory:
        return self.category.parent

    def set_parent_category(self, category: Union[MidLevelProductCategory, dict]):
        self.category.parent = category

    def get_parent_category_id(self) -> UUID:
        return self.category.get_parent_id()

    def get_parent_category_name(self) -> str:
        return self.category.get_parent_name()

    def get_parent_category_description(self) -> str:
        return self.category.get_parent_description()

    def get_top_category(self) -> TopLevelProductCategory:
        return self.category.get_top_level_category()

    def set_top_category(self, category: Union[TopLevelProductCategory, dict]):
        self.category.set_top_level_category(category)

    def get_top_category_id(self) -> UUID:
        return self.category.get_top_level_category_id()

    def get_top_category_name(self) -> str:
        return self.category.get_top_level_category_name()

    def get_top_category_description(self) -> str:
        return self.category.get_top_level_category_description()

    def get_client_rating(self) -> Optional[ProductRating]:
        return self.rating

    def update_client_rating(self):
        self.rating = self.calculate_rating(self.reviews)

    def get_client_reviews(self) -> list[ProductReview]:
        return self.reviews

    def _append_review(self, review: ProductReview):
        if not isinstance(review, ProductReview):
            raise TypeError(f"invalid review object type")
        self.reviews.append(review)

    @staticmethod
    def calculate_rating(reviews: list[ProductReview]):
        n = len(reviews)
        if n < 2:
            return reviews[0].rating if n else None
        else:
            rating_avg = sum([review.rating for review in reviews]) / n
            return round_decimal(rating_avg, "1.0")

    def add_client_review(self, review: ProductReview):
        self._append_review(review)
        self.rating = self.calculate_rating(self.reviews)

    def delete_client_review(self, review_id: UUID):
        if not isinstance(review_id, UUID):
            raise TypeError("review_id must be a UUID object")
        old_reviews = self.reviews
        new_reviews = [rev for rev in self.reviews if rev.id != review_id]
        if len(old_reviews) == len(new_reviews):
            raise ValueError(f"no review with id {review_id!r}")
        self.reviews = new_reviews
        self.rating = self.calculate_rating(self.reviews)

    def get_thumbnail_photo_url(self) -> str:
        return str(self.photo_url.thumbnail)

    def get_medium_size_photo_url(self) -> str:
        return str(self.photo_url.medium)

    def get_large_size_photo_url(self) -> str:
        return str(self.photo_url.large)

    def get_vendor_id(self) -> UUID:
        return self.vendor.id

    def get_vendor_id_in_bytes_format(self) -> bytes:
        return self.vendor.id.bytes

    def get_vendor_name(self) -> str:
        return self.vendor.name

    def get_vendor_description(self) -> str:
        return self.vendor.description

    def get_vendor_logo_url(self) -> str:
        return str(self.vendor.logo_url)
