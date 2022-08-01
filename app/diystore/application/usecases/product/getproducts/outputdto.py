from typing import Iterable

from pydantic import BaseModel

from ..getproduct import GetProductOutputDTO
from ....dto import DTO
from .....domain.entities.product import Product


class GetProductsOutputDTO(BaseModel, DTO):
    products: tuple[GetProductOutputDTO, ...]

    @classmethod
    def from_products(cls, products: Iterable[Product]):
        return cls(products=(GetProductOutputDTO.from_product(p) for p in products))
