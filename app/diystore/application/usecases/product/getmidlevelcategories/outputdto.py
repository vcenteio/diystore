from typing import Iterable
from pydantic import BaseModel

from ..getmidlevelcategory import GetMidLevelCategoryOutputDTO
from .....domain.entities.product import MidLevelProductCategory
from ....dto import DTO


class GetMidLevelCategoriesOutputDTO(BaseModel, DTO):
    categories: tuple[GetMidLevelCategoryOutputDTO, ...]

    @classmethod
    def from_categories(cls, categories: Iterable[MidLevelProductCategory]):
        return cls(
            categories=(
                GetMidLevelCategoryOutputDTO.from_category(c) for c in categories
            )
        )
