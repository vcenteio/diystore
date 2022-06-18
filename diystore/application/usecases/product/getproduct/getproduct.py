from typing import Optional

from .inputdto import GetProductInputDTO
from .outputdto import GetProductOutputDTO
from ..repository import ProductRepository


def _ensure_input_dto_correct_type(input_dto):
    if not isinstance(input_dto, GetProductInputDTO):
        raise TypeError(f"wrong type for input_dto: {type(input_dto).__name__}")


def _ensure_repository_correct_type(repository):
    if not isinstance(repository, ProductRepository):
        raise TypeError(f"wrong type for repository: {type(repository).__name__}")


def _validate_arguments(input_dto, repository):
    _ensure_input_dto_correct_type(input_dto)
    _ensure_repository_correct_type(repository)


def get_product_use_case(
    input_dto: GetProductInputDTO, repository: ProductRepository
) -> Optional[GetProductOutputDTO]:
    _validate_arguments(input_dto, repository)
    product = repository.get_product(input_dto.product_id)
    return GetProductOutputDTO.from_product(product) if product else None
