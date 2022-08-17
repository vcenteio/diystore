from unittest.mock import Mock
from uuid import uuid4

from .conftest import MidLevelProductCategoryStub
from diystore.domain.entities.product import MidLevelProductCategory
from diystore.application.usecases.product import ProductRepository
from diystore.application.usecases.product import get_mid_level_category
from diystore.application.usecases.product import GetMidLevelCategoryInputDTO
from diystore.application.usecases.product import GetMidLevelCategoryOutputDTO


def test_application_get_mid_level_category_non_existing_category(
    mock_products_repository: ProductRepository,
):
    mock_products_repository.get_mid_level_category = Mock(return_value=None)
    input_dto = GetMidLevelCategoryInputDTO(category_id=uuid4())
    output_dto = get_mid_level_category(input_dto, mock_products_repository)
    assert output_dto is None


def test_application_get_mid_level_category_existing_category(
    mock_products_repository: ProductRepository,
):
    category: MidLevelProductCategory = MidLevelProductCategoryStub()
    mock_products_repository.get_mid_level_category = Mock(return_value=category)
    input_dto = GetMidLevelCategoryInputDTO(category_id=category.id)
    output_dto = get_mid_level_category(input_dto, mock_products_repository)

    assert isinstance(output_dto, GetMidLevelCategoryOutputDTO)
    assert output_dto.id == category.id.hex
    assert output_dto.name == category.name
    assert output_dto.description == category.description
    assert output_dto.parent_id == category.get_parent_id().hex
