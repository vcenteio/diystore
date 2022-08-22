from pydantic import BaseModel

from .....domain.entities.product import ProductVendor
from ....dto import DTO


class GetProductVendorOutputDTO(BaseModel, DTO):
    id: str
    name: str
    description: str
    logo_url: str

    @classmethod
    def from_entity(cls, vendor: ProductVendor) -> "GetProductVendorOutputDTO":
        return cls(
            id=vendor.id.hex,
            name=vendor.name,
            description=vendor.description,
            logo_url=vendor.logo_url,
        )
