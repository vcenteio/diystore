from uuid import UUID
from uuid import uuid4

import pytest
from pydantic.error_wrappers import ValidationError

from diystore.domain.entities.product import VAT
from diystore.domain.entities.product.stubs import VATStub


@pytest.mark.parametrize("wrong_rate", ("abc", {1, 2}, dict(), [1, 2], b"123"))
def test_vat_rate_wrong_type(wrong_rate):
    with pytest.raises(ValidationError):
        VATStub(rate=wrong_rate)


@pytest.mark.parametrize("wrong_rate", (1.01, -1, 50, -0.01))
def test_vat_rate_value_wrong_range(wrong_rate):
    with pytest.raises(ValidationError):
        VATStub(rate=wrong_rate)


@pytest.mark.parametrize("wrong_rate", (0.999, 0.001, 0.123, 0.1234567))
def test_vat_rate_value_wrong_no_of_decimal_places(wrong_rate):
    with pytest.raises(ValidationError):
        VATStub(rate=wrong_rate)


def test_vat_rate_correct_value():
    v = VATStub()
    assert v.rate >= 0 and v.rate <= 1


@pytest.mark.parametrize("wrong_name", (123, {1, 2}, dict(), [1, 2], b"123"))
def test_vat_name_wrong_type(wrong_name):
    with pytest.raises(ValidationError):
        VATStub(name=wrong_name)


def test_vat_name_length_gt_max_length(faker):
    wrong_name = faker.pystr(min_chars=21, max_chars=50)
    with pytest.raises(ValidationError):
        VATStub(name=wrong_name)


def test_vat_name_length_lt_min_length(faker):
    with pytest.raises(ValidationError):
        VATStub(name="")


def test_vat_name_correct_length_range():
    d = VATStub()
    assert len(d.name) in range(2, 21)


def test_vat_name_correct_type():
    d = VATStub()
    assert isinstance(d.name, str)


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
def test_vat_id_wrong_type_and_value(wrong_id):
    with pytest.raises(ValidationError):
        VATStub(id=wrong_id)


def test_vat_id_correct_type():
    _id = uuid4()
    v = VATStub(id=_id)
    assert isinstance(v.id, UUID)


def test_vat_id_correct_value():
    _id = uuid4()
    v = VATStub(id=_id)
    assert v.id == _id


def test_vat_id_correct_conversion_from_str(faker):
    str_uuid = faker.uuid4()
    v = VATStub(id=str_uuid)
    assert v.id == UUID(str_uuid) and isinstance(v.id, UUID)


def test_vat_name_is_required():
    with pytest.raises(ValidationError) as e:
        VAT(rate=0.25)
    err_repr = repr(e.getrepr())
    assert "name" in err_repr
    assert "field required" in err_repr


def test_vat_rate_is_required():
    with pytest.raises(ValidationError) as e:
        VAT(name="abc")
    err_repr = repr(e.getrepr())
    assert "rate" in err_repr
    assert "field required" in err_repr
