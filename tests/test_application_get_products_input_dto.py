import pytest
from pydantic import ValidationError

from diystore.application.use_cases.get_products.ordering_criteria import (
    OrderingProperty,
)
from diystore.application.use_cases.get_products.ordering_criteria import OrderingType
from .conftest import GetProductsInputDTOFactory


def test_application_get_products_input_dto_category_id_is_necessary(
    none_not_allowed_error_msg,
):
    with pytest.raises(ValidationError) as e:
        GetProductsInputDTOFactory(category_id=None)
    assert e.match(none_not_allowed_error_msg)


def test_application_get_products_input_dto_ordering_criteria_init_with_valid_ints():
    idto = GetProductsInputDTOFactory(ordering_criteria=dict(property=1, type=1))
    assert idto.ordering_criteria.property == OrderingProperty.PRICE
    assert idto.ordering_criteria.type == OrderingType.ASCENDING
    idto = GetProductsInputDTOFactory(ordering_criteria=dict(property=2, type=2))
    assert idto.ordering_criteria.property == OrderingProperty.RATING
    assert idto.ordering_criteria.type == OrderingType.DESCESDING


def test_application_get_products_input_dto_ordering_criteria_init_with_invalid_ints():
    with pytest.raises(ValidationError):
        GetProductsInputDTOFactory(ordering_criteria=dict(property=3, type=3))
