from typing import Iterable
from pydantic import BaseModel

from ..getterminallevelcategory import GetTerminalLevelCategoryOutputDTO
from .....domain.entities.product import TerminalLevelProductCategory
from ....dto import DTO


class GetTerminalLevelCategoriesOutputDTO(BaseModel, DTO):
    categories: tuple[GetTerminalLevelCategoryOutputDTO, ...]

    @classmethod
    def from_categories(cls, categories: Iterable[TerminalLevelProductCategory]):
        return cls(
            categories=(
                GetTerminalLevelCategoryOutputDTO.from_category(c) for c in categories
            )
        )
