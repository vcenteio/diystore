from uuid import UUID

from pydantic import BaseModel

from ....dto import DTO


class GetProductInputDTO(BaseModel, DTO):
    product_id: UUID
