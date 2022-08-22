from typing import Optional

from .inputdto import GetTerminalLevelCategoriesInputDTO
from .outputdto import GetTerminalLevelCategoriesOutputDTO
from ..repository import ProductRepository


def get_terminal_level_categories(
    input_dto: GetTerminalLevelCategoriesInputDTO, repository: ProductRepository
) -> Optional[GetTerminalLevelCategoriesOutputDTO]:
    categories = repository.get_terminal_level_categories(input_dto.parent_id)
    if categories is not None:
        return GetTerminalLevelCategoriesOutputDTO.from_categories(categories)
