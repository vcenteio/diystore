from uuid import uuid4

from diystore.application.use_cases.get_products import ProductOutputDTO
from diystore.application.use_cases.get_products import GetProductsOutputDTO
from .conftest import Product
from .conftest import ProductFactory
from .conftest import ProductOutputDTOFactory


def test_application_get_products_product_output_dto_id_is_hex():
    _id = uuid4()
    odto = ProductOutputDTOFactory(id=_id)
    assert odto.id == _id.hex


def test_application_get_products_product_output_dto_in_stock_is_lower_case(faker):
    in_stock = faker.pybool()
    odto = ProductOutputDTOFactory(in_stock=in_stock)
    assert odto.in_stock == str(in_stock).lower()


def test_application_get_products_product_output_dto_warranty_is_int(faker):
    warranty = faker.pyint(min_value=1, max_value=5)
    odto = ProductOutputDTOFactory(warranty=warranty)
    assert isinstance(odto.warranty, int)
    assert odto.warranty == warranty


def test_application_get_products_product_output_dto_from_product():
    product: Product = ProductFactory()
    odto = ProductOutputDTO.from_product(product)
    dimensions = product.get_dimensions_dict()

    assert odto.id == product.id.hex
    assert odto.ean == product.ean
    assert odto.name == product.name
    assert odto.description == product.description
    assert odto.price == str(product.get_final_price())
    assert odto.price_without_discount == str(
        product.get_final_price(with_discount=False)
    )
    assert odto.discount == str(product.get_discount_rate())
    assert odto.vat == str(product.get_vat_rate())
    assert odto.in_stock == str(bool(product.quantity is not 0)).lower()
    assert odto.height == str(dimensions["height"])
    assert odto.width == str(dimensions["width"])
    assert odto.length == str(dimensions["length"])
    assert odto.color == product.color
    assert odto.material == product.material
    assert odto.country_of_origin == product.country_of_origin
    assert odto.warranty == product.warranty
    assert odto.category_id == product.get_category_id().hex
    assert odto.category_name == product.get_category_name()
    assert odto.client_rating == str(product.get_client_rating())
    assert odto.thumbnail_photo_url == product.get_thumbnail_photo_url()
    assert odto.medium_size_photo_url == product.get_medium_size_photo_url()
    assert odto.large_size_photo_url == product.get_large_size_photo_url()
    assert odto.vendor_id == product.get_vendor_id().hex
    assert odto.vendor_name == product.get_vendor_name()
