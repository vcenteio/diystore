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
        if isinstance(parent, dict):
            return TopLevelProductCategory(**parent)
        return parent


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
        if isinstance(parent, dict):
            return MidLevelProductCategory(**parent)
        return parent

    def get_mid_level_category(self):
        return self.parent

    def get_top_level_category(self):
        return self.parent.parent
