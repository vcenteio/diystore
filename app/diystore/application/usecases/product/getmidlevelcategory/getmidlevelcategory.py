from .inputdto import GetMidLevelCategoryInputDTO
from .outputdto import GetMidLevelCategoryOutputDTO
from ..repository import ProductRepository


def get_mid_level_category(
    input_dto: GetMidLevelCategoryInputDTO, repository: ProductRepository
) -> GetMidLevelCategoryOutputDTO:
    category = repository.get_mid_level_category(input_dto.category_id)
    return GetMidLevelCategoryOutputDTO.from_category(category) if category else None
