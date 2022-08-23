from uuid import uuid4

from .conftest import ProductReviewStub
from diystore.application.usecases.product import GetProductReviewInputDTO
from diystore.application.usecases.product import GetProductReviewOutputDTO
from diystore.application.usecases.product import get_review
from diystore.application.usecases.product import ProductRepository


def test_application_get_review_non_existent_review(
    mock_products_repository: ProductRepository,
):
    # GIVEN an id associated with no existing review
    _id = uuid4()
    repo = mock_products_repository
    repo.get_review.return_value = None

    # WHEN a review is queried with such id
    input_dto = GetProductReviewInputDTO(review_id=_id)
    output_dto = get_review(input_dto, repo)

    # THEN no review is returned
    assert output_dto is None


def test_application_get_review_existent_review(
    mock_products_repository: ProductRepository,
):
    # GIVEN an id associated with an existing review
    review = ProductReviewStub()
    mock_products_repository.get_review.return_value = review
    
    # WHEN a review is queried with such id
    input_dto = GetProductReviewInputDTO(review_id=review.id)
    output_dto = get_review(input_dto, mock_products_repository)

    # THEN the correct review is returned
    assert isinstance(output_dto, GetProductReviewOutputDTO)
    assert output_dto.id == review.id.hex
    assert output_dto.product_id == review.product_id.hex
    assert output_dto.client_id == review.client_id.hex
    assert output_dto.rating == float(review.rating)
    assert output_dto.creation_date == review.creation_date.isoformat()
    assert output_dto.feedback == review.feedback
