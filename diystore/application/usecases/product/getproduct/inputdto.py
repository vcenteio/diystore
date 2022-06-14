from uuid import UUID

from pydantic import BaseModel


class GetProductInputDTO(BaseModel):
    product_id: UUID
