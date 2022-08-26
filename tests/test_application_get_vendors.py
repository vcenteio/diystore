from diystore.domain.entities.product.stubs import ProductVendorStub
from diystore.application.usecases.product import GetProductVendorsOutputDTO
from diystore.application.usecases.product import GetProductVendorOutputDTO
from diystore.application.usecases.product import get_vendors
from diystore.application.usecases.product import ProductRepository


def test_application_get_vendors_non_existing_vendors(
    mock_products_repository: ProductRepository,
):
    # GIVEN a repository with no existing vendors
    mock_products_repository.get_vendors.return_value = ()

    # WHEN a query for all vendors is made
    output_dto = get_vendors(mock_products_repository)

    # THEN no vendors are returned
    assert len(output_dto.vendors) == 0


def test_application_get_vendors_existing_vendors(
    mock_products_repository: ProductRepository,
):
    # GIVEN a repository with existing vendors
    vendors = ProductVendorStub.build_batch(3)
    mock_products_repository.get_vendors.return_value = vendors
    expected_dto = GetProductVendorsOutputDTO.from_entities(vendors)

    # WHEN a query for vendors is made
    output_dto = get_vendors(mock_products_repository)

    # THEN all vendors are returned
    assert output_dto == expected_dto
