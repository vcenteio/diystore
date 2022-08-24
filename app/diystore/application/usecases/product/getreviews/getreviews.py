from typing import Optional

from .inputdto import GetProductReviewsInputDTO
from .outputdto import GetProductReviewsOutputDTO
from ..repository import ProductRepository


def get_reviews(
    input_dto: GetProductReviewsInputDTO, repository: ProductRepository
) -> Optional[GetProductReviewsOutputDTO]:
    reviews = repository.get_reviews(input_dto.product_id)
    if reviews is not None:
        return GetProductReviewsOutputDTO.from_entities(reviews)
    return None
