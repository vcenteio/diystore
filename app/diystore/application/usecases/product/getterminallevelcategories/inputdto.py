from uuid import UUID

from pydantic.dataclasses import dataclass

from ....dto import DTO


@dataclass(frozen=True)
class GetTerminalLevelCategoriesInputDTO(DTO):
    parent_id: UUID
