from unittest.mock import Mock
from uuid import uuid4

from .conftest import TerminalLevelProductCategoryStub
from diystore.domain.entities.product import TerminalLevelProductCategory
from diystore.application.usecases.product import ProductRepository
from diystore.application.usecases.product import get_terminal_level_category
from diystore.application.usecases.product import GetTerminalLevelCategoryInputDTO
from diystore.application.usecases.product import GetTerminalLevelCategoryOutputDTO


def test_application_get_terminal_level_category_non_existing_category(
    mock_products_repository: ProductRepository,
):
    # GIVEN an id associated with no terminal level category
    category_id = uuid4()
    mock_products_repository.get_terminal_level_category = Mock(return_value=None)

    # WHEN a terminal level category is requested with such id
    input_dto = GetTerminalLevelCategoryInputDTO(category_id=category_id)
    output_dto = get_terminal_level_category(input_dto, mock_products_repository)

    # THEN no category is returned
    assert output_dto is None


def test_application_get_terminal_level_category_existing_category(
    mock_products_repository: ProductRepository,
):
    # GIVEN an id associated with a terminal level category
    category: TerminalLevelProductCategory = TerminalLevelProductCategoryStub()
    mock_products_repository.get_terminal_level_category = Mock(return_value=category)

    # WHEN a terminal level category is requested with such id
    input_dto = GetTerminalLevelCategoryInputDTO(category_id=category.id)
    output_dto = get_terminal_level_category(input_dto, mock_products_repository)

    # THEN a output DTO is returned
    assert isinstance(output_dto, GetTerminalLevelCategoryOutputDTO)
    assert output_dto.id == category.id.hex
    assert output_dto.name == category.name
    assert output_dto.description == category.description
    assert output_dto.parent_id == category.get_parent_id().hex
