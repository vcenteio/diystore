from typing import Optional

from pydantic import BaseModel

from ....dto import DTO
from .....domain.entities.product import ProductReview


class GetProductReviewOutputDTO(BaseModel, DTO):
    id: str
    product_id: str
    client_id: str
    rating: float
    creation_date: str
    feedback: Optional[str]

    @classmethod
    def from_entity(cls, review: ProductReview):
        return cls(
            id=review.id.hex,
            product_id=review.product_id.hex,
            client_id=review.client_id.hex,
            rating=review.rating,
            creation_date=review.creation_date.isoformat(),
            feedback=review.feedback
        )
