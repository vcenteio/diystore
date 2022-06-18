from unittest.mock import Mock
from typing import Union

import pytest

from .conftest import GetProductInputDTOFactory
from .conftest import ProductFactory
from diystore.application.usecases.product import ProductRepository
from diystore.application.usecases.product import get_product_use_case
from diystore.application.usecases.product import GetProductOutputDTO


def test_application_get_product_use_case_wrong_input_dto_type(
    mock_products_repository,
):
    with pytest.raises(TypeError) as e:
        get_product_use_case(input_dto=1, repository=mock_products_repository)
    assert "input_dto" in str(e)


def test_application_get_product_use_case_wrong_repository_type():
    input_dto = GetProductInputDTOFactory()
    with pytest.raises(TypeError) as e:
        get_product_use_case(input_dto=input_dto, repository=1)
    assert "repository" in str(e)


def test_application_get_product_use_case_no_result(
    mock_products_repository: Union[Mock, ProductRepository]
):
    input_dto = GetProductInputDTOFactory()
    mock_products_repository.get_product = Mock(return_value=None)
    product = get_product_use_case(input_dto, mock_products_repository)
    assert product is None
    mock_products_repository.get_product.assert_called_once_with(input_dto.product_id)


def test_application_get_product_use_case_with_result(
    mock_products_repository: Union[Mock, ProductRepository]
):
    input_dto = GetProductInputDTOFactory()
    expected_product = ProductFactory()
    mock_products_repository.get_product = Mock(return_value=expected_product)
    product = get_product_use_case(input_dto, mock_products_repository)
    assert product == GetProductOutputDTO.from_product(expected_product)
    mock_products_repository.get_product.assert_called_once_with(input_dto.product_id)
