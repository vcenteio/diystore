from uuid import UUID

from pydantic.dataclasses import dataclass

from ....dto import DTO


@dataclass
class GetProductReviewInputDTO(DTO):
    review_id: UUID
