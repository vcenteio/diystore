from uuid import UUID
from uuid import uuid4

from .conftest import ProductVendorOrmModelStub
from .conftest import ProductVendorStub
from diystore.application.usecases.product import GetProductVendorInputDTO
from diystore.application.usecases.product import GetProductVendorOutputDTO
from diystore.application.usecases.product import get_vendor
from diystore.application.usecases.product import ProductRepository


def test_application_get_vendor_non_existing_vendor(
    mock_products_repository: ProductRepository,
):
    # GIVEN an id not associated with any vendor
    _id = uuid4()
    mock_products_repository.get_vendor.return_value = None

    # WHEN a vendor is queried using such id
    input_dto = GetProductVendorInputDTO(vendor_id=_id)
    output_dto = get_vendor(input_dto, mock_products_repository)

    # THEN no output_dto is returned
    assert output_dto is None


def test_application_get_vendor_existing_vendor(
    mock_products_repository: ProductRepository,
):
    # GIVEN an id associated with a vendor
    vendor = ProductVendorStub()
    vendor_id = vendor.id.hex
    mock_products_repository.get_vendor.return_value = vendor

    # WHEN a vendor is queried using such id
    input_dto = GetProductVendorInputDTO(vendor_id=vendor_id)
    output_dto = get_vendor(input_dto, mock_products_repository)

    # THEN a valid output_dto is returned
    assert isinstance(output_dto, GetProductVendorOutputDTO)
    assert output_dto.id == vendor_id
    assert output_dto.name == vendor.name
    assert output_dto.description == vendor.description
    assert output_dto.logo_url == vendor.logo_url
    assert isinstance(output_dto.logo_url, str)
