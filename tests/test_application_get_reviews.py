from uuid import uuid4

from diystore.domain.entities.product.stubs import ProductStub
from diystore.domain.entities.product.stubs import ProductReviewStub
from diystore.application.usecases.product import ProductRepository
from diystore.application.usecases.product import GetProductReviewsInputDTO
from diystore.application.usecases.product import GetProductReviewsOutputDTO
from diystore.application.usecases.product import get_reviews


def test_application_get_reviews_non_existent_product(
    mock_products_repository: ProductRepository,
):
    # GIVEN an id not associated with any product
    _id = uuid4()
    mock_products_repository.get_reviews.return_value = None

    # WHEN reviews associated with such id are queried
    input_dto = GetProductReviewsInputDTO(product_id=_id)
    output_dto = get_reviews(input_dto, mock_products_repository)

    # THEN no dto is returned
    assert output_dto is None


def test_application_get_reviews_product_with_no_reviews(
    mock_products_repository: ProductRepository,
):
    # GIVEN a product with no reviews
    product_id = uuid4()
    mock_products_repository.get_reviews.return_value = ()

    # WHEN reviews associated with a certain product are queried
    input_dto = GetProductReviewsInputDTO(product_id=product_id)
    output_dto = get_reviews(input_dto, mock_products_repository)

    # THEN a dto with no product information is returned
    assert output_dto.reviews == ()


def test_application_get_reviews_product_with_reviews(
    mock_products_repository: ProductRepository,
):
    # GIVEN a product with reviews
    product = ProductStub()
    reviews = ProductReviewStub.build_batch(3, product_id=product.id)
    mock_products_repository.get_reviews.return_value = reviews
    expected_output_dto = GetProductReviewsOutputDTO.from_entities(reviews)

    # WHEN its reviews are queried
    input_dto = GetProductReviewsInputDTO(product_id=product.id)
    output_dto = get_reviews(input_dto, mock_products_repository)

    # THEN a DTO containing information about all its reviews is returned
    assert output_dto == expected_output_dto
