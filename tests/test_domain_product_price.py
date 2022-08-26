from decimal import Decimal

import pytest
from pydantic.error_wrappers import ValidationError
from faker import Faker

from diystore.domain.entities.product import ProductPrice

from diystore.domain.entities.product.stubs import DiscountStub
from diystore.domain.entities.product.stubs import ProductPriceStub
from diystore.domain.entities.product.stubs import VATStub


Faker.seed(0)
faker = Faker()


@pytest.mark.parametrize("wrong_value", ([], dict(), {}))
def test_domain_price_value_wrong_type(wrong_value):
    with pytest.raises(ValidationError):
        ProductPriceStub(value=wrong_value)


@pytest.mark.parametrize("wrong_value", ("abc", b"abc", 0, -1, "0", "-1", 0.00, -0.01))
def test_domain_price_value_lt_min_value(wrong_value):
    with pytest.raises(ValidationError):
        ProductPriceStub(value=wrong_value)


@pytest.mark.parametrize("wrong_value", (1_000_000, "1_000_000", 1_000_000.01))
def test_domain_price_value_gt_max_value(wrong_value):
    with pytest.raises(ValidationError):
        ProductPriceStub(value=wrong_value)


@pytest.mark.parametrize("wrong_value", (100.001, "1.234", 1.123456))
def test_domain_price_value_wrong_decimal_place(wrong_value):
    with pytest.raises(ValidationError):
        ProductPriceStub(value=wrong_value)


@pytest.mark.parametrize("value", (100, 100.01, "100"))
def test_domain_price_value_int_float_str_converts_to_decimal(value):
    p = ProductPriceStub(value=value)
    assert isinstance(p.value, Decimal)


def test_domain_price_value_float_remains_the_same(valid_product_price_float: float):
    p = ProductPriceStub(value=valid_product_price_float)
    assert p.value == Decimal(valid_product_price_float).quantize(Decimal("1.00"))


def test_domain_price_value_decimal_remains_the_same(
    valid_product_price_decimal: Decimal,
):
    p = ProductPriceStub(value=valid_product_price_decimal)
    assert p.value == valid_product_price_decimal


@pytest.mark.parametrize("vat_rate", (0.01, 0.25, 0.50, 0.99))
def test_domain_price_calculate_no_discount(vat_rate: float):
    vat = VATStub(rate=vat_rate)
    p: ProductPrice = ProductPriceStub(vat=vat, discount=None)
    expected_price = p.value + (p.value * Decimal(vat_rate))
    assert p.calculate() == expected_price.quantize(Decimal("1.00"))


@pytest.mark.parametrize("discount_rate", (0.01, 0.25, 0.50, 0.99))
def test_domain_price_calculate_with_discount(discount_rate: float):
    vat = VATStub()
    discount = DiscountStub(rate=discount_rate)
    p: ProductPrice = ProductPriceStub(vat=vat, discount=discount)
    value_with_discount = p.value - (p.value * p.discount)
    expected_price = value_with_discount + (value_with_discount * vat.rate)
    assert p.calculate() == expected_price.quantize(Decimal("1.00"))


@pytest.mark.parametrize("discount_rate", (0.01, 0.25, 0.50, 0.99))
def test_domain_price_calculate_without_discount(discount_rate: float):
    vat = VATStub()
    discount = DiscountStub(rate=discount_rate)
    p: ProductPrice = ProductPriceStub(vat=vat, discount=discount)
    expected_price = p.value + (p.value * Decimal(vat.rate))
    assert p.calculate_without_discount() == expected_price.quantize(Decimal("1.00"))


def test_domain_price_get_discount_info_no_discount():
    p: ProductPrice = ProductPriceStub(discount=None)
    assert p.get_discount_id() is None
    assert p.get_discount_id_in_bytes_format() is None
    assert p.get_discount_rate() is None
