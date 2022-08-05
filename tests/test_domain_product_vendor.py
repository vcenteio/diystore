import pytest
from pydantic.error_wrappers import ValidationError

from diystore.domain.entities.product import ProductVendor
from .conftest import ProductVendorStub


def test_domain_product_vendor_no_description():
    v = ProductVendorStub(description=None)
    assert v.description is None


def test_domain_product_vendor_empty_description():
    with pytest.raises(ValidationError):
        ProductVendorStub(description="")


def test_domain_product_vendor_no_url():
    v = ProductVendorStub(logo_url=None)
    assert v.logo_url is None


def test_domain_product_vendor_name_is_required():
    with pytest.raises(ValidationError):
        ProductVendorStub(name=None)
