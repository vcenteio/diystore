from uuid import uuid4

from diystore.application.usecases.product import GetProductOutputDTO
from diystore.application.usecases.product import GetProductsOutputDTO
from .conftest import Product
from .conftest import ProductStub
from .conftest import GetProductOutputDTOStub


def test_application_get_products_product_output_dto_id_is_hex():
    _id = uuid4()
    odto = GetProductOutputDTOStub(id=_id)
    assert odto.id == _id.hex


def test_application_get_products_product_output_dto_warranty_is_int(faker):
    warranty = faker.pyint(min_value=1, max_value=5)
    odto = GetProductOutputDTOStub(warranty=warranty)
    assert isinstance(odto.warranty, int)
    assert odto.warranty == warranty


def test_application_get_products_product_output_dto_from_product():
    product: Product = ProductStub()
    odto = GetProductOutputDTO.from_product(product)

    assert odto.id == product.get_id_in_hex_format()
    assert odto.ean == product.ean
    assert odto.name == product.name
    assert odto.description == product.description
    assert odto.price == float(product.get_final_price())
    assert odto.price_without_discount == float(
        product.get_final_price_without_discount()
    )
    assert odto.discount == float(product.get_discount_rate())
    assert odto.vat == float(product.get_vat_rate())
    assert odto.in_stock == bool(product.quantity > 0)
    assert odto.rating == float(product.get_client_rating())
    assert odto.height == float(product.get_height())
    assert odto.width == float(product.get_width())
    assert odto.length == float(product.get_length())
    assert odto.color == product.color
    assert odto.material == product.material
    assert odto.country_of_origin == product.country_of_origin
    assert odto.warranty == product.warranty
    assert odto.category_id == product.get_category_id_in_hex_format()
    assert odto.category_name == product.get_category_name()
    assert odto.thumbnail_photo_url == product.get_thumbnail_photo_url()
    assert odto.medium_size_photo_url == product.get_medium_size_photo_url()
    assert odto.large_size_photo_url == product.get_large_size_photo_url()
    assert odto.vendor_id == product.get_vendor_id_in_hex_format()
    assert odto.vendor_name == product.get_vendor_name()
