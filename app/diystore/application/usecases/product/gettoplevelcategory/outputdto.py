from uuid import UUID
from typing import Optional

from pydantic import BaseModel

from ....dto import DTO
from .....domain.entities.product import TopLevelProductCategory


class GetTopLevelCategoryOutputDTO(BaseModel, DTO):
    id: str
    name: str
    description: Optional[str]

    class Config:
        frozen = True

    @classmethod
    def from_category(cls, category: TopLevelProductCategory):
        return cls(
            id=category.id.hex, name=category.name, description=category.description
        )
