from typing import Iterable

from pydantic import BaseModel

from ....dto import DTO
from ..getreview.outputdto import GetProductReviewOutputDTO
from .....domain.entities.product import ProductReview


class GetProductReviewsOutputDTO(BaseModel, DTO):
    reviews: tuple[GetProductReviewOutputDTO, ...]

    @classmethod
    def from_entities(cls, reviews: Iterable[ProductReview]):
        return cls(reviews=(GetProductReviewOutputDTO.from_entity(r) for r in reviews))
