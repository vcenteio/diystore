from typing import Iterable

from pydantic import BaseModel

from ....dto import DTO
from .....domain.entities.product import TopLevelProductCategory
from ..gettoplevelcategory.outputdto import GetTopLevelCategoryOutputDTO


class GetTopLevelCategoriesOutputDTO(DTO, BaseModel):
    categories: tuple[GetTopLevelCategoryOutputDTO, ...]

    class Config:
        frozen = True

    @classmethod
    def from_categories(cls, categories: Iterable[TopLevelProductCategory]):
        return cls(
            categories=(
                GetTopLevelCategoryOutputDTO.from_category(c) for c in categories
            )
        )
