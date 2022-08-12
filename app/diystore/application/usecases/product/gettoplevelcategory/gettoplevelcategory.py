from typing import Optional

from .inputdto import GetTopLevelCategoryInputDTO
from .outputdto import GetTopLevelCategoryOutputDTO
from ..repository import ProductRepository


def _ensure_input_dto_correct_type(input_dto):
    if not isinstance(input_dto, GetTopLevelCategoryInputDTO):
        raise TypeError(f"wrong type for input_dto: {type(input_dto).__name__}")


def get_top_level_category(
    input_dto: GetTopLevelCategoryInputDTO, repository: ProductRepository
) -> Optional[GetTopLevelCategoryOutputDTO]:
    _ensure_input_dto_correct_type(input_dto)
    category = repository.get_top_level_category(input_dto.category_id)
    return GetTopLevelCategoryOutputDTO.from_category(category) if category else None
