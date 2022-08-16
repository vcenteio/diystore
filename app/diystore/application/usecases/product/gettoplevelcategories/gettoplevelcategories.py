from .outputdto import GetTopLevelCategoriesOutputDTO
from ..repository import ProductRepository


def get_top_level_categories(repository: ProductRepository) -> GetTopLevelCategoriesOutputDTO:
    categories = repository.get_top_level_categories()
    return GetTopLevelCategoriesOutputDTO.from_categories(categories)
