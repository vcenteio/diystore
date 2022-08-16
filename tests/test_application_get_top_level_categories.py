from unittest.mock import Mock

from .conftest import TopLevelProductCategoryStub
from diystore.application.usecases.product import get_top_level_categories
from diystore.application.usecases.product import GetTopLevelCategoriesOutputDTO
from diystore.application.usecases.product import GetTopLevelCategoryOutputDTO
from diystore.application.usecases.product import ProductRepository


def test_application_get_top_level_categories_no_categories(
    mock_products_repository: ProductRepository,
):
    # GIVEN a repository with no top level categories
    mock_products_repository.get_top_level_categories = Mock(return_value=tuple())

    # WHEN the existing categories are requested
    output_dto = get_top_level_categories(mock_products_repository)

    # THEN a DTO with no categories is returned
    assert isinstance(output_dto, GetTopLevelCategoriesOutputDTO)
    assert output_dto.categories == tuple()


def test_application_get_top_level_categories_existing_categories(
    mock_products_repository: ProductRepository,
):
    # GIVEN a repository with existing top level categories
    top_categories = TopLevelProductCategoryStub.build_batch(3)
    mock_products_repository.get_top_level_categories = Mock(
        return_value=top_categories
    )

    # WHEN the existing categories are requested
    output_dto = get_top_level_categories(mock_products_repository)

    # THEN a DTO with all the top categories' DTO's is returned
    expected = GetTopLevelCategoriesOutputDTO.from_categories(top_categories)
    assert isinstance(output_dto, GetTopLevelCategoriesOutputDTO)
    for category in output_dto.categories:
        assert isinstance(category, GetTopLevelCategoryOutputDTO)
        assert category in expected.categories
    assert len(output_dto.categories) == len(expected.categories)
