from typing import Optional

from .inputdto import GetMidLevelCategoriesInputDTO
from .outputdto import GetMidLevelCategoriesOutputDTO
from ..repository import ProductRepository


def get_mid_level_categories(
    input_dto: GetMidLevelCategoriesInputDTO, repository: ProductRepository
) -> Optional[GetMidLevelCategoriesOutputDTO]:
    categories = repository.get_mid_level_categories(input_dto.parent_id)
    if categories is not None:
        return GetMidLevelCategoriesOutputDTO.from_categories(categories)
    return None
