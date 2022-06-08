from uuid import UUID
from uuid import uuid4

from pydantic import BaseModel
from pydantic import Field
from pydantic import constr
from pydantic import validator
from pydantic import Extra


class ProductCategory(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: constr(strict=True, min_length=2, max_length=50) = Field(...)
    description: str

    class Config:
        extra = Extra.forbid
        validate_assignment = True


class TopLevelProductCategory(ProductCategory):
    description: constr(strict=True, min_length=1, max_length=3000) = Field(
        default=None, repr=False
    )


class MidLevelProductCategory(ProductCategory):
    description: constr(strict=True, min_length=1, max_length=300) = Field(
        default=None, repr=False
    )
    parent: TopLevelProductCategory = Field(...)

    @validator("parent", pre=True, always=True)
    def _validate_parent(cls, parent):
        if not isinstance(parent, (TopLevelProductCategory, dict)):
            raise ValueError(
                "parent must be a TopLevelProductCategory object or a valid dict"
            )
        return parent
    
    def get_parent_id(self) -> UUID:
        return self.parent.id
    
    def get_parent_name(self) -> str:
        return self.parent.name

    def get_parent_description(self) -> str:
        return self.parent.description


class TerminalLevelProductCategory(ProductCategory):
    description: constr(strict=True, min_length=1, max_length=300) = Field(
        default=None,
        repr=False,
    )
    parent: MidLevelProductCategory = Field(...)

    @validator("parent", pre=True, always=True)
    def _validate_parent(cls, parent):
        if not isinstance(parent, (MidLevelProductCategory, dict)):
            raise ValueError(
                "parent must be a MidLevelProductCategory object or a valid dict"
            )
        return parent
    
    def get_parent_id(self) -> UUID:
        return self.parent.id

    def get_parent_name(self) -> str:
        return self.parent.name
    
    def get_parent_description(self) -> str:
        return self.parent.description

    def get_top_level_category(self) -> TopLevelProductCategory:
        return self.parent.parent

    def set_top_level_category(self, category: TopLevelProductCategory):
        self.parent.parent = category
    
    def get_top_level_category_id(self) -> UUID:
        return self.parent.get_parent_id()

    def get_top_level_category_name(self) -> str:
        return self.parent.get_parent_name()
    
    def get_top_level_category_description(self) -> str:
        return self.parent.get_parent_description()
