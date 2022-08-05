from uuid import UUID
from uuid import uuid4
from datetime import datetime
from decimal import Decimal

import pytest
from pendulum import now
from pydantic.error_wrappers import ValidationError

from .conftest import DiscountStub


@pytest.mark.parametrize("rate", ("abc", {1, 2}, dict(), [1, 2], b"123"))
def test_discount_rate_wrong_type(rate):
    with pytest.raises(ValidationError):
        DiscountStub(rate=rate)


@pytest.mark.parametrize("rate", (1, 0.5, "1"))
def test_discount_rate_float_int_str_are_converted_to_decimal(rate):
    d = DiscountStub(rate=rate)
    assert isinstance(d.rate, Decimal)


@pytest.mark.parametrize("rate", (-5.6, 0))
def test_discount_rate_value_le_to_zero(rate):
    with pytest.raises(ValidationError):
        DiscountStub(rate=rate)


@pytest.mark.parametrize("rate", (1.1, 100))
def test_discount_rate_value_gt_one(rate):
    with pytest.raises(ValidationError):
        DiscountStub(rate=rate)


@pytest.mark.parametrize("rate", (0.123, 0.4321, Decimal(0.21)))
def test_discount_rate_decimal_places_gt_two(rate):
    with pytest.raises(ValidationError):
        DiscountStub(rate=rate)


@pytest.mark.parametrize("rate", (Decimal(1), Decimal("0.21")))
def test_discount_rate_valid_decimal_value(rate):
    d = DiscountStub(rate=rate)
    assert d.rate == rate


@pytest.mark.parametrize("wrong_name", (123, dict(), {}, [], b"abc"))
def test_discount_name_wrong_type(wrong_name):
    with pytest.raises(ValidationError):
        DiscountStub(name=wrong_name)


def test_discount_name_wrong_length(faker):
    wrong_name = faker.pystr(min_chars=51, max_chars=200)
    with pytest.raises(ValidationError):
        DiscountStub(name=wrong_name)


@pytest.mark.parametrize("wrong_date", (dict(), {}, [], b"abc", "abc"))
def test_discount_creation_date_wrong_type(wrong_date):
    with pytest.raises(ValidationError):
        DiscountStub(creation_date=wrong_date)


@pytest.mark.parametrize("wrong_date", (dict(), {}, [], b"abc", "abc"))
def test_discount_expiry_date_wrong_type(wrong_date):
    with pytest.raises(ValidationError):
        DiscountStub(expiry_date=wrong_date)


def test_discount_creation_date_gt_now(future_date):
    with pytest.raises(ValidationError):
        DiscountStub(creation_date=future_date)


def test_discount_expiry_date_le_creation_date():
    expiry_date = now("UTC").subtract(years=1)
    with pytest.raises(ValidationError):
        DiscountStub(expiry_date=expiry_date)


def test_discount_valid_dates_correct_type():
    d = DiscountStub()
    assert isinstance(d.creation_date, datetime) and isinstance(d.expiry_date, datetime)


def test_discount_valid_dates_expiry_gt_creation_date():
    d = DiscountStub()
    assert d.expiry_date > d.creation_date


@pytest.mark.parametrize(
    "wrong_id",
    (
        dict(),
        {},
        [],
        b"abc",
        "abc",
        123,
        "6d7db7d2-6a4d-4bed-88a9-028bfc79447",
        "6d7db7d2-6a4d-gbed-88a9-028bfc794477",
    ),
)
def test_discount_id_wrong_type_and_value(wrong_id):
    with pytest.raises(ValidationError):
        DiscountStub(id=wrong_id)


def test_discount_id_correct_type():
    _id = uuid4()
    d = DiscountStub(id=_id)
    assert isinstance(d.id, UUID)


def test_discount_id_correct_value():
    _id = uuid4()
    d = DiscountStub(id=_id)
    assert d.id == _id


def test_discount_id_correct_conversion_from_str(faker):
    str_uuid = faker.uuid4()
    d = DiscountStub(id=str_uuid)
    assert d.id == UUID(str_uuid)
