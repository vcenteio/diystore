from typing import Callable
from functools import partial

from .inputdto import GetProductsInputDTO
from .outputdto import GetProductsOutputDTO
from ..repository import ProductRepository
from ..getproduct.outputdto import GetProductOutputDTO
from ..orderingcriteria import OrderingProperty
from ..orderingcriteria import OrderingType


def _validate_input_dto_type(input_dto: GetProductsInputDTO):
    if not isinstance(input_dto, GetProductsInputDTO):
        raise TypeError("input DTO must be of type GetProductsInputDTO")


def _has_ordering_criteria(input_dto: GetProductsInputDTO):
    return input_dto.ordering_criteria is not None


def _is_ordering_type_rating(input_dto: GetProductsInputDTO):
    criteria = input_dto.ordering_criteria
    return criteria.property is OrderingProperty.RATING


def _select_correct_repository_method(
    input_dto: GetProductsInputDTO, repository: ProductRepository
):
    if not _has_ordering_criteria(input_dto):
        return repository.get_products
    if _is_ordering_type_rating(input_dto):
        return repository.get_products_ordering_by_rating
    return repository.get_products_ordering_by_price


def _is_descending_order(input_dto: GetProductsInputDTO):
    criteria = input_dto.ordering_criteria
    return criteria and criteria.type is OrderingType.DESCESDING


def _call_method_with_correct_arguments(
    method: Callable, input_dto: GetProductOutputDTO
):
    partial_method_call = partial(
        method,
        category_id=input_dto.category_id,
        price_min=input_dto.price_min,
        price_max=input_dto.price_max,
        rating_min=input_dto.rating_min,
        rating_max=input_dto.rating_max,
        with_discounts_only=input_dto.with_discounts_only,
    )
    if _has_ordering_criteria(input_dto):
        return partial_method_call(
            descending=_is_descending_order(input_dto),
        )
    return partial_method_call()


def get_products_use_case(
    input_dto: GetProductsInputDTO, repository: ProductRepository
):
    _validate_input_dto_type(input_dto)
    repo_method = _select_correct_repository_method(input_dto, repository)
    products = _call_method_with_correct_arguments(repo_method, input_dto)
    return GetProductsOutputDTO.from_products(products)
