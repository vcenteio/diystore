from decimal import Decimal
from typing import Optional

from pydantic import BaseModel
from pydantic import Field
from pydantic import conlist

from ...helpers import round_decimal
from .review import ProductReview


class ProductRating(BaseModel):
    reviews: conlist(ProductReview) = Field(default=[], repr=False)

    class Config:
        validate_assignment = True

    def get_reviews(self) -> list[ProductReview]:
        return self.reviews

    def calculate(self) -> Optional[Decimal]:
        n = len(self.reviews)
        if n < 2:
            return self.reviews[0].rating if n else None
        rating_avg = sum([review.rating for review in self.reviews]) / n
        return round_decimal(rating_avg, "1.0")

    def add_review(self, review: ProductReview):
        if not isinstance(review, ProductReview):
            raise TypeError(f"invalid review object type")
        self.reviews.append(review)
