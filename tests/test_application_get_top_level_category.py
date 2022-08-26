import pytest

from diystore.domain.entities.product.stubs import TopLevelProductCategoryStub
from diystore.application.usecases.product import ProductRepository
from diystore.application.usecases.product import get_top_level_category
from diystore.application.usecases.product import GetTopLevelCategoryInputDTO


def test_application_get_top_level_category_wrong_input_dto_type(
    mock_products_repository: ProductRepository,
):
    # GIVEN an invalid input DTO
    # WHEN it is used as argument for the use case
    # THEN an error should be raised
    with pytest.raises(TypeError):
        get_top_level_category(1, mock_products_repository)


def test_application_get_top_level_category_existent_category_with_description(
    mock_products_repository: ProductRepository,
):
    # GIVEN an existent category with description
    category = TopLevelProductCategoryStub()

    # WHEN a valid input DTO is used together with a valid repository
    input_dto = GetTopLevelCategoryInputDTO(category_id=category.id)
    mock_products_repository.get_top_level_category.return_value = category

    # THEN a valid output DTO is returned with description
    output_dto = get_top_level_category(input_dto, mock_products_repository)
    assert output_dto.id == category.id.hex
    assert output_dto.name == category.name
    assert output_dto.description == category.description is not None


def test_application_get_top_level_category_existent_category_without_description(
    mock_products_repository: ProductRepository,
):
    # GIVEN an existent category with no description
    category = TopLevelProductCategoryStub(description=None)

    # WHEN a valid input DTO is used together with a valid repository
    input_dto = GetTopLevelCategoryInputDTO(category_id=category.id)
    mock_products_repository.get_top_level_category.return_value = category

    # THEN a valid output DTO is returned with no description
    output_dto = get_top_level_category(input_dto, mock_products_repository)
    assert output_dto.id == category.id.hex
    assert output_dto.name == category.name
    assert output_dto.description is category.description is None