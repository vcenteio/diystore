import pytest
from pydantic.error_wrappers import ValidationError

from diystore.domain.product.vendor import ProductVendor
from .conftest import ProductVendorFactory


def test_domain_product_vendor_no_description():
    v = ProductVendorFactory(description=None)
    assert v.description is None


def test_domain_product_vendor_empty_description():
    with pytest.raises(ValidationError):
        ProductVendorFactory(description="")


def test_domain_product_vendor_no_url():
    v = ProductVendorFactory(logo_url=None)
    assert v.logo_url is None


def test_domain_product_vendor_name_is_required():
    with pytest.raises(ValidationError):
        ProductVendorFactory(name=None)
