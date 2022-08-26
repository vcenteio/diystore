from typing import Union
from unittest.mock import Mock

import pytest

from diystore.application.usecases.product import ProductRepository
from diystore.application.usecases.product import get_products_use_case
from diystore.application.usecases.product import OrderingProperty
from diystore.application.usecases.product import OrderingType
from diystore.application.usecases.product import GetProductsOutputDTO
from diystore.application.usecases.product.stubs import GetProductsInputDTOStub


def test_application_get_products_use_case_input_dto_wrong_type():
    with pytest.raises(TypeError):
        get_products_use_case(input_dto=1, repository=Mock(ProductRepository))


def test_application_get_products_use_case_no_ordering_no_result(
    mock_products_repository: Union[Mock, ProductRepository]
):
    input_dto = GetProductsInputDTOStub(ordering_criteria=None)
    mock_products_repository.get_products = Mock(return_value=[])
    result = get_products_use_case(
        input_dto=input_dto, repository=mock_products_repository
    )
    assert result == GetProductsOutputDTO(products=[])
    mock_products_repository.get_products.assert_called_once()


def test_application_get_products_use_case_no_ordering_with_result(
    product_stub_list, mock_products_repository: Union[Mock, ProductRepository]
):
    input_dto = GetProductsInputDTOStub(ordering_criteria=None)
    mock_products_repository.get_products = Mock(return_value=product_stub_list)
    result = get_products_use_case(
        input_dto=input_dto, repository=mock_products_repository
    )
    assert result == GetProductsOutputDTO.from_products(product_stub_list)
    mock_products_repository.get_products.assert_called_once()


def test_application_get_products_use_case_ordering_by_rating_no_result(
    mock_products_repository: Union[Mock, ProductRepository]
):
    input_dto = GetProductsInputDTOStub(
        ordering_criteria__type=OrderingType.DESCESDING,
        ordering_criteria__property=OrderingProperty.RATING,
    )
    mock_products_repository.get_products_ordering_by_rating = Mock(return_value=[])
    result = get_products_use_case(
        input_dto=input_dto, repository=mock_products_repository
    )
    assert result == GetProductsOutputDTO(products=[])
    mock_products_repository.get_products_ordering_by_rating.assert_called_once()


def test_application_get_products_use_case_ordering_by_rating_with_results(
    product_stub_list, mock_products_repository: Union[Mock, ProductRepository]
):
    input_dto = GetProductsInputDTOStub(
        ordering_criteria__type=OrderingType.DESCESDING,
        ordering_criteria__property=OrderingProperty.RATING,
    )
    mock_products_repository.get_products_ordering_by_rating = Mock(
        return_value=product_stub_list
    )
    result = get_products_use_case(
        input_dto=input_dto, repository=mock_products_repository
    )
    assert result == GetProductsOutputDTO.from_products(product_stub_list)
    mock_products_repository.get_products_ordering_by_rating.assert_called_once()


def test_application_get_products_use_case_ordering_by_price_no_result(
    mock_products_repository: Union[Mock, ProductRepository]
):
    input_dto = GetProductsInputDTOStub(
        ordering_criteria__type=OrderingType.DESCESDING,
        ordering_criteria__property=OrderingProperty.PRICE,
    )
    mock_products_repository.get_products_ordering_by_price = Mock(return_value=[])
    result = get_products_use_case(
        input_dto=input_dto, repository=mock_products_repository
    )
    assert result == GetProductsOutputDTO(products=[])
    mock_products_repository.get_products_ordering_by_price.assert_called_once()


def test_application_get_products_use_case_ordering_by_price_with_results(
    product_stub_list, mock_products_repository: Union[Mock, ProductRepository]
):
    input_dto = GetProductsInputDTOStub(
        ordering_criteria__type=OrderingType.DESCESDING,
        ordering_criteria__property=OrderingProperty.PRICE,
    )
    mock_products_repository.get_products_ordering_by_price = Mock(
        return_value=product_stub_list
    )
    result = get_products_use_case(
        input_dto=input_dto, repository=mock_products_repository
    )
    assert result == GetProductsOutputDTO.from_products(product_stub_list)
    mock_products_repository.get_products_ordering_by_price.assert_called_once()
