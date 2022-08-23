from typing import Iterable
from pydantic import BaseModel

from ....dto import DTO
from ..getvendor import GetProductVendorOutputDTO
from .....domain.entities.product.vendor import ProductVendor


class GetProductVendorsOutputDTO(BaseModel, DTO):
    vendors: tuple[GetProductVendorOutputDTO, ...]

    @classmethod
    def from_entities(cls, vendors: Iterable[ProductVendor]):
        return cls(vendors=(GetProductVendorOutputDTO.from_entity(v) for v in vendors))
