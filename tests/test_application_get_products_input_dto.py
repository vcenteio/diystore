import pytest
from pydantic import ValidationError

from diystore.application.usecases.product import OrderingProperty
from diystore.application.usecases.product import OrderingType
from .conftest import GetProductsInputDTOStub


def test_application_get_products_input_dto_category_id_is_necessary(
    none_not_allowed_error_msg,
):
    with pytest.raises(ValidationError) as e:
        GetProductsInputDTOStub(category_id=None)
    assert e.match(none_not_allowed_error_msg)


def test_application_get_products_input_dto_ordering_criteria_init_with_valid_ints():
    idto = GetProductsInputDTOStub(ordering_criteria=dict(property=1, type=1))
    assert idto.ordering_criteria.property == OrderingProperty.PRICE
    assert idto.ordering_criteria.type == OrderingType.ASCENDING
    idto = GetProductsInputDTOStub(ordering_criteria=dict(property=2, type=2))
    assert idto.ordering_criteria.property == OrderingProperty.RATING
    assert idto.ordering_criteria.type == OrderingType.DESCESDING


def test_application_get_products_input_dto_ordering_criteria_init_with_invalid_ints():
    with pytest.raises(ValidationError):
        GetProductsInputDTOStub(ordering_criteria=dict(property=3, type=3))
