from typing import Iterable

from pydantic import BaseModel

from ..getproduct import GetProductOutputDTO
from .....domain.entities.product import Product


class GetProductsOutputDTO(BaseModel):
    products: list[GetProductOutputDTO]

    @classmethod
    def from_products(cls, products: Iterable[Product]):
        return cls(products=[GetProductOutputDTO.from_product(p) for p in products])
