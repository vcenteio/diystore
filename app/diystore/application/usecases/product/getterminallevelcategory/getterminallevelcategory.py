from typing import Optional

from .inputdto import GetTerminalLevelCategoryInputDTO
from .outputdto import GetTerminalLevelCategoryOutputDTO
from ..repository import ProductRepository


def get_terminal_level_category(
    input_dto: GetTerminalLevelCategoryInputDTO, repository: ProductRepository
) -> Optional[GetTerminalLevelCategoryOutputDTO]:
    category = repository.get_terminal_level_category(input_dto.category_id)
    if category is None:
        return None
    return GetTerminalLevelCategoryOutputDTO.from_category(category)
