from pydantic import BaseModel

from ..getproduct import GetProductOutputDTO


class GetProductsOutputDTO(BaseModel):
    products: list[GetProductOutputDTO]
