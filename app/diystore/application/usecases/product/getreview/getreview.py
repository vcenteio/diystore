from typing import Optional

from .inputdto import GetProductReviewInputDTO
from .outputdto import GetProductReviewOutputDTO
from ..repository import ProductRepository


def get_review(
    input_dto: GetProductReviewInputDTO, repository: ProductRepository
) -> Optional[GetProductReviewOutputDTO]:
    review = repository.get_review(input_dto.review_id)
    return GetProductReviewOutputDTO.from_entity(review) if review else None
