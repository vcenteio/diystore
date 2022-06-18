from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from pydantic import PrivateAttr

from ...helpers import round_decimal
from .review import ProductReview


class ProductRating(BaseModel):
    _reviews: list[ProductReview] = PrivateAttr(default=[])
    _value: Decimal = PrivateAttr(default=None)

    def __init__(self, reviews: list[ProductReview] = []):
        super().__init__()
        self.set_reviews(reviews)

    def _update_rating(self):
        n = len(self._reviews)
        if n < 2:
            self._value = self._reviews[0].rating if n else None
        else:
            rating_avg = sum([review.rating for review in self._reviews]) / n
            self._value = round_decimal(rating_avg, "1.0")

    def get_rating(self) -> Optional[Decimal]:
        return self._value

    def get_reviews(self) -> list[ProductReview]:
        return self._reviews

    def _append_review(self, review: ProductReview):
        if not isinstance(review, ProductReview):
            raise TypeError(f"invalid review object type")
        self._reviews.append(review)

    def add_review(self, review: ProductReview):
        self._append_review(review)
        self._update_rating()

    def set_reviews(self, reviews: list[ProductReview]):
        if not isinstance(reviews, (list, tuple, set)):
            raise TypeError("reviews must be a list, a tuple or a set")
        old_reviews, self._reviews = self._reviews, []
        try:
            for review in reviews:
                self._append_review(review)
        except TypeError as e:
            self._reviews = old_reviews
            raise e
        else:
            self._update_rating()

    def delete_review(self, _id: UUID):
        if not isinstance(_id, UUID):
            raise TypeError("_id must be a UUID object")
        old_reviews = self._reviews
        new_reviews = [rev for rev in self.get_reviews() if rev.id != _id]
        if len(old_reviews) == len(new_reviews):
            raise ValueError(f"no review with id {_id!r}")
        self._reviews = new_reviews
        self._update_rating()
