from typing import Optional
from pydantic import BaseModel

from ....dto import DTO
from .....domain.entities.product import TerminalLevelProductCategory


class GetTerminalLevelCategoryOutputDTO(BaseModel, DTO):
    id: str
    name: str
    description: Optional[str]
    parent_id: str

    @classmethod
    def from_category(cls, category: TerminalLevelProductCategory):
        return cls(
            id=category.id.hex,
            name=category.name,
            description=category.description,
            parent_id=category.get_parent_id().hex,
        )
