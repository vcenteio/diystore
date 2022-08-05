from decimal import Decimal

import pytest
from pydantic.error_wrappers import ValidationError

from diystore.domain.entities.product import ProductDimensions
from .conftest import ProductDimensionsStub


@pytest.mark.parametrize("wrong_dimension", ("a", b"a", [], (), {}, dict()))
def test_domain_product_dimensions_wrong_type(wrong_dimension):
    with pytest.raises(ValidationError):
        ProductDimensionsStub(height=wrong_dimension)
    with pytest.raises(ValidationError):
        ProductDimensionsStub(width=wrong_dimension)
    with pytest.raises(ValidationError):
        ProductDimensionsStub(length=wrong_dimension)


@pytest.mark.parametrize("wrong_dimension", (-1, "-1", -0.1))
def test_domain_product_dimensions_lt_min_value(wrong_dimension):
    with pytest.raises(ValidationError):
        ProductDimensionsStub(height=wrong_dimension)
    with pytest.raises(ValidationError):
        ProductDimensionsStub(width=wrong_dimension)
    with pytest.raises(ValidationError):
        ProductDimensionsStub(length=wrong_dimension)


@pytest.mark.parametrize("wrong_dimension", (100_001, "100_000.1", 100_000.1))
def test_domain_product_dimensions_gt_max_value(wrong_dimension):
    with pytest.raises(ValidationError):
        ProductDimensionsStub(height=wrong_dimension)
    with pytest.raises(ValidationError):
        ProductDimensionsStub(width=wrong_dimension)
    with pytest.raises(ValidationError):
        ProductDimensionsStub(length=wrong_dimension)


@pytest.mark.parametrize("wrong_dimension", (1.12, "5.23", 1.12345))
def test_domain_product_dimensions_wrong_no_of_decimal_places(wrong_dimension):
    with pytest.raises(ValidationError):
        ProductDimensionsStub(height=wrong_dimension)
    with pytest.raises(ValidationError):
        ProductDimensionsStub(width=wrong_dimension)
    with pytest.raises(ValidationError):
        ProductDimensionsStub(length=wrong_dimension)


@pytest.mark.parametrize("dimension", (1, "5.2", 1001.5))
def test_domain_product_dimensions_int_float_str_are_converted_to_decimal(dimension):
    product_dimensions = ProductDimensions(
        height=dimension, width=dimension, length=dimension
    )
    for _, d in product_dimensions:
        assert isinstance(d, Decimal)


@pytest.mark.parametrize("dimension", (1, "5.2", 1001.5))
def test_domain_product_dimensions_correct_value(dimension):
    product_dimensions = ProductDimensions(
        height=dimension, width=dimension, length=dimension
    )
    for _, d in product_dimensions:
        assert d == Decimal(dimension)


def test_domain_product_dimensions_get_str():
    pd = ProductDimensionsStub()
    assert pd.get_str() == str(pd)
