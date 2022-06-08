from uuid import UUID
from uuid import uuid4

from pydantic import BaseModel
from pydantic import AnyUrl
from pydantic import Field
from pydantic import constr


class ProductVendor(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: constr(strict=True, min_length=1, max_length=50) = Field(...)
    description: str = Field(default=None, min_length=1, max_length=3000)
    logo_url: AnyUrl = Field(default=None)
