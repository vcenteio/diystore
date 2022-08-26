from uuid import uuid4

from diystore.domain.entities.product.stubs import TerminalLevelProductCategoryStub
from diystore.domain.entities.product.stubs import MidLevelProductCategoryStub
from diystore.application.usecases.product import ProductRepository
from diystore.application.usecases.product import get_terminal_level_categories
from diystore.application.usecases.product import GetTerminalLevelCategoriesOutputDTO
from diystore.application.usecases.product import GetTerminalLevelCategoriesInputDTO
from diystore.application.usecases.product import GetTerminalLevelCategoryOutputDTO


def test_application_get_terminal_level_categories_non_existent_parent_category(
    mock_products_repository: ProductRepository,
):
    # GIVEN an id associated with no parent category
    parent_id = uuid4()
    mock_products_repository.get_terminal_level_categories.return_value = None

    # WHEN the existing terminal categories associated with such id are requested
    input_dto = GetTerminalLevelCategoriesInputDTO(parent_id=parent_id)
    output_dto = get_terminal_level_categories(input_dto, mock_products_repository)

    # THEN no DTO is returned
    assert output_dto is None


def test_application_get_terminal_level_categories_no_categories(
    mock_products_repository: ProductRepository,
):
    # GIVEN a repository with no terminal categories
    mock_products_repository.get_terminal_level_categories.return_value = ()

    # WHEN the existing terminal categories are requested
    input_dto = GetTerminalLevelCategoriesInputDTO(parent_id=uuid4())
    output_dto = get_terminal_level_categories(input_dto, mock_products_repository)

    # THEN a DTO with no categories is returned
    assert isinstance(output_dto, GetTerminalLevelCategoriesOutputDTO)
    assert output_dto.categories == ()


def test_application_get_terminal_level_categories_existing_categories(
    mock_products_repository: ProductRepository,
):
    # GIVEN a repository with existing terminal categories
    parent = MidLevelProductCategoryStub()
    terminal_categories = TerminalLevelProductCategoryStub.build_batch(3, parent=parent)
    mock_products_repository.get_terminal_level_categories.return_value = (
        terminal_categories
    )

    # WHEN the existing terminal categories are requested
    input_dto = GetTerminalLevelCategoriesInputDTO(parent_id=parent.id)
    output_dto = get_terminal_level_categories(input_dto, mock_products_repository)

    # THEN a DTO with all the terminal categories associated with the parent id is returned
    expected = GetTerminalLevelCategoriesOutputDTO.from_categories(terminal_categories)
    assert isinstance(output_dto, GetTerminalLevelCategoriesOutputDTO)
    for category in output_dto.categories:
        assert isinstance(category, GetTerminalLevelCategoryOutputDTO)
        assert category in expected.categories
    assert len(output_dto.categories) == len(expected.categories)
