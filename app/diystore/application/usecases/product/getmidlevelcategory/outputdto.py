from pydantic import BaseModel

from ....dto import DTO
from .....domain.entities.product.categories import MidLevelProductCategory


class GetMidLevelCategoryOutputDTO(BaseModel, DTO):
    id: str
    name: str
    description: str
    parent_id: str

    @classmethod
    def from_category(cls, category: MidLevelProductCategory):
        return cls(
            id=category.id.hex,
            name=category.name,
            description=category.description,
            parent_id=category.get_parent_id().hex,
        )
