from uuid import uuid4

from diystore.domain.entities.product.stubs import MidLevelProductCategoryStub
from diystore.domain.entities.product.stubs import TopLevelProductCategoryStub
from diystore.application.usecases.product import ProductRepository
from diystore.application.usecases.product import get_mid_level_categories
from diystore.application.usecases.product import GetMidLevelCategoryOutputDTO
from diystore.application.usecases.product import GetMidLevelCategoriesInputDTO
from diystore.application.usecases.product import GetMidLevelCategoriesOutputDTO


def test_application_get_mid_level_categories_non_existent_parent_category(
    mock_products_repository: ProductRepository,
):
    # GIVEN an id associated with no parent category
    parent_id = uuid4()
    mock_products_repository.get_mid_level_categories.return_value = None

    # WHEN the existing mid categories associated with such id are requested
    input_dto = GetMidLevelCategoriesInputDTO(parent_id=parent_id)
    output_dto = get_mid_level_categories(input_dto, mock_products_repository)

    # THEN no DTO is returned
    assert output_dto is None


def test_application_get_mid_level_categories_no_categories(
    mock_products_repository: ProductRepository,
):
    # GIVEN a repository with no mid level categories
    mock_products_repository.get_mid_level_categories.return_value = ()

    # WHEN the existing categories are requested
    input_dto = GetMidLevelCategoriesInputDTO(parent_id=uuid4())
    output_dto = get_mid_level_categories(input_dto, mock_products_repository)

    # THEN a DTO with no categories is returned
    assert isinstance(output_dto, GetMidLevelCategoriesOutputDTO)
    assert output_dto.categories == ()


def test_application_get_mid_level_categories_existing_categories(
    mock_products_repository: ProductRepository,
):
    # GIVEN a repository with existing mid level categories
    parent = TopLevelProductCategoryStub()
    mid_categories = MidLevelProductCategoryStub.build_batch(3, parent=parent)
    mock_products_repository.get_mid_level_categories.return_value = mid_categories

    # WHEN the existing categories are requested
    input_dto = GetMidLevelCategoriesInputDTO(parent_id=parent.id)
    output_dto = get_mid_level_categories(input_dto, mock_products_repository)

    # THEN a DTO with all the mid categories' associated with parent's id is returned
    expected = GetMidLevelCategoriesOutputDTO.from_categories(mid_categories)
    assert isinstance(output_dto, GetMidLevelCategoriesOutputDTO)
    for category in output_dto.categories:
        assert isinstance(category, GetMidLevelCategoryOutputDTO)
        assert category in expected.categories
    assert len(output_dto.categories) == len(expected.categories)
