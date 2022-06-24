from pydantic import BaseModel
from pydantic import AnyUrl
from pydantic import Field


class ProductPhotoUrl(BaseModel):
    thumbnail: AnyUrl = Field(...)
    medium: AnyUrl = Field(...)
    large: AnyUrl = Field(...)
