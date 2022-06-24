from decimal import Decimal
from uuid import uuid1

import pytest
import pendulum
from pendulum.datetime import DateTime
from pydantic.error_wrappers import ValidationError

from diystore.domain.entities.product import ProductPrice
from diystore.domain.entities.product import ProductDimensions
from diystore.domain.entities.product import TerminalLevelProductCategory
from diystore.domain.entities.product import ProductPhotoUrl
from diystore.domain.entities.product import ProductVendor
from diystore.domain.entities.product import Product
from diystore.domain.entities.product import ProductRating
from .conftest import DiscountFactory, ProductReviewFactory, tz
from .conftest import round_decimal
from .conftest import ProductPhotoUrlFactory
from .conftest import ProductFactory
from .conftest import ProductDimensionsFactory
from .conftest import ProductPriceFactory
from .conftest import TopLevelProductCategoryFactory
from .conftest import MidLevelProductCategoryFactory
from .conftest import TerminalLevelProductCategoryFactory
from .conftest import ProductVendorFactory


@pytest.mark.parametrize("wrong_ean", ([], dict(), (), {}, type))
def test_domain_product_ean_wrong_type(wrong_ean):
    with pytest.raises(ValidationError):
        ProductFactory(ean=wrong_ean)


def test_domain_product_ean_correct_lenght(faker):
    ean = faker.bothify(text="#############")
    p = ProductFactory(ean=ean)
    assert p.ean == ean


def test_domain_product_ean_lenght_lt_min(faker):
    ean = faker.bothify(text="############")
    with pytest.raises(ValidationError) as e:
        ProductFactory(ean=ean)
    assert e.match("EAN")


def test_domain_product_ean_lenght_lt_max(faker):
    ean = faker.bothify(text="##############")
    with pytest.raises(ValidationError) as e:
        ProductFactory(ean=ean)
    assert e.match("EAN")


def test_domain_product_ean_wrong_value(faker):
    ean = faker.bothify(text="#####?#######")
    with pytest.raises(ValidationError) as e:
        ProductFactory(ean=ean)


def test_domain_product_ean_int_is_converted_to_str(faker):
    int_ean = faker.pyint(min_value=1000000000000, max_value=9999999999999)
    p = ProductFactory(ean=int_ean)
    assert p.ean == str(int_ean)


def test_domain_product_ean_bytes_is_converted_to_str(faker):
    bytes_ean = faker.bothify(text="#############").encode()
    with pytest.raises(ValidationError) as e:
        ProductFactory(ean=bytes_ean)
    assert e.match("ean must be str or int")


@pytest.mark.parametrize("wrong_name", (123, b"abc", [], dict(), {}, (), type))
def test_domain_product_name_wrong_type(wrong_name):
    with pytest.raises(ValidationError) as e:
        ProductFactory(name=wrong_name)


def test_domain_product_name_empty_string():
    with pytest.raises(ValidationError) as e:
        ProductFactory(name="")


def test_domain_product_name_lenght_gt_max_lenght(faker):
    wrong_name = faker.pystr(min_chars=51, max_chars=100)
    with pytest.raises(ValidationError) as e:
        ProductFactory(name=wrong_name)


def test_domain_product_valid_name(faker):
    name = faker.pystr(min_chars=1, max_chars=50)
    p = ProductFactory(name=name)
    assert p.name == name


def test_domain_product_name_is_necessary():
    with pytest.raises(ValidationError) as e:
        ProductFactory(name=None)


def test_domain_product_no_description():
    p = ProductFactory(description=None)
    assert p.description is None


@pytest.mark.parametrize("wrong_desc", (123, b"abc", [], dict(), {}, (), type))
def test_domain_product_description_wrong_type(wrong_desc):
    with pytest.raises(ValidationError) as e:
        ProductFactory(description=wrong_desc)


def test_domain_product_description_empty_string():
    with pytest.raises(ValidationError) as e:
        ProductFactory(description="")


def test_domain_product_description_lenght_gt_max_lenght(faker):
    wrong_description = faker.pystr(min_chars=3001, max_chars=3002)
    with pytest.raises(ValidationError) as e:
        ProductFactory(description=wrong_description)


def test_domain_product_valid_description(faker):
    description = faker.pystr(min_chars=1, max_chars=3000)
    p = ProductFactory(description=description)
    assert p.description == description


def test_domain_product_price_is_necessary():
    with pytest.raises(ValidationError) as e:
        ProductFactory(price=None)


def test_domain_product_valid_price():
    price = ProductPriceFactory()
    p = ProductFactory(price=price)
    assert p.price == price


def test_domain_product_valid_price_dict():
    price_dict = ProductPriceFactory().dict()
    p = ProductFactory(price=price_dict)
    assert p.price == ProductPrice(**price_dict)


def test_domain_product_get_final_price():
    price: ProductPrice = ProductPriceFactory()
    p: Product = ProductFactory(price=price)
    assert p.get_final_price() == price.calculate()


def test_domain_product_get_final_price_without_discount():
    price: ProductPrice = ProductPriceFactory()
    p: Product = ProductFactory(price=price)
    assert p.get_final_price_without_discount() == price.calculate_without_discount()


@pytest.mark.parametrize("wrong_price", ("a", b"b", (1,), [2]))
def test_domain_product_set_base_price_wrong_type(wrong_price):
    p: Product = ProductFactory()
    with pytest.raises(ValidationError) as e:
        p.set_base_price(wrong_price)


@pytest.mark.parametrize("price", (1, 50.2, "34.21", Decimal("123.32")))
def test_domain_product_set_base_price_correct_type(price):
    p: Product = ProductFactory()
    p.set_base_price(price)
    assert p.get_base_price() == round_decimal(Decimal(price), "1.00")


def test_domain_product_get_discount_rate_with_discount():
    price: ProductPrice = ProductPriceFactory()
    discount_rate = price.get_discount_rate()
    p = ProductFactory(price=price)
    assert p.get_discount_rate() == discount_rate

def test_domain_product_get_discount_rate_no_discount():
    price: ProductPrice = ProductPriceFactory(discount=None)
    p = ProductFactory(price=price)
    assert p.get_discount_rate() is None


def test_domain_product_get_discount():
    price: ProductPrice = ProductPriceFactory()
    discount = price.discount
    p = ProductFactory(price=price)
    assert p.get_discount() == discount


@pytest.mark.parametrize("wrong_discount", ("a", 1, b"123", [1]))
def test_domain_product_set_discount_wrong_type(wrong_discount):
    p = ProductFactory()
    with pytest.raises(ValidationError):
        p.set_discount(wrong_discount)


def test_domain_product_set_discount_correct_type():
    discount = DiscountFactory()
    p: Product = ProductFactory()
    p.set_discount(discount)
    assert p.get_discount() == discount


def test_domain_product_set_discount_wrong_dict():
    discount_dict = DiscountFactory().dict()
    discount_dict.pop("rate")
    p: Product = ProductFactory()
    with pytest.raises(ValidationError):
        p.set_discount(discount_dict)


def test_domain_product_set_discount_correct_dict():
    discount_dict = DiscountFactory().dict()
    p: Product = ProductFactory()
    p.set_discount(discount_dict)
    assert p.get_discount() == DiscountFactory(**discount_dict)


def test_domain_product_get_vat_rate():
    price = ProductPriceFactory()
    expected_vat = price.get_vat_rate()
    p: Product = ProductFactory(price=price)
    assert p.get_vat_rate() == expected_vat


def test_domain_product_get_vat():
    price = ProductPriceFactory()
    expected_vat_obj = price.vat
    p: Product = ProductFactory(price=price)
    assert p.get_vat() == expected_vat_obj


@pytest.mark.parametrize("wrong_vat", (1, "a", b"123"))
def test_domain_product_set_vat_wrong_type(wrong_vat):
    with pytest.raises(ValidationError):
        ProductFactory().set_vat(wrong_vat)


def test_domain_product_set_vat_correct_type():
    price = ProductPriceFactory()
    p: Product = ProductFactory()
    p.set_vat(price.vat)
    assert p.get_vat() == price.vat


def test_domain_product_quantity_is_necessary():
    with pytest.raises(ValidationError):
        ProductFactory(quantity=None)


@pytest.mark.parametrize("wrong_qty", ("1", b"1", True, False, None, "", []))
def test_domain_product_quantity_wrong_type(wrong_qty):
    with pytest.raises(ValidationError):
        ProductFactory(quantity=wrong_qty)


def test_domain_product_quantity_lt_min_value():
    with pytest.raises(ValidationError):
        ProductFactory(quantity=-1)


def test_domain_product_quantity_gt_max_value():
    with pytest.raises(ValidationError):
        ProductFactory(quantity=1_000_001)


def test_domain_product_creation_date_is_necessary():
    with pytest.raises(ValidationError):
        ProductFactory(creation_date=None)


@pytest.mark.parametrize("wrong_date", ([], (), {}))
def test_domain_product_creation_date_wrong_type(wrong_date):
    with pytest.raises(ValidationError):
        ProductFactory(creation_date=wrong_date)


def test_domain_product_creation_date_from_float_posix_timestamp():
    timestamp = pendulum.now("UTC").timestamp()
    expected_result = DateTime.fromtimestamp(timestamp, tz=tz)
    p = ProductFactory(creation_date=timestamp)
    assert p.creation_date == expected_result


def test_domain_product_creation_date_from_str_posix_timestamp():
    timestamp = pendulum.now("UTC").timestamp()
    expected_result = DateTime.fromtimestamp(timestamp, tz=tz)
    p = ProductFactory(creation_date=str(timestamp))
    assert p.creation_date == expected_result


def test_domain_product_creation_date_from_int_ordinal():
    ordinal = pendulum.now("UTC").toordinal()
    with pytest.raises(ValidationError):
        ProductFactory(creation_date=ordinal)


def test_domain_product_creation_date_from_iso_format():
    iso_datetime = pendulum.now("UTC").isoformat()
    expected_result = DateTime.fromisoformat(iso_datetime)
    p = ProductFactory(creation_date=iso_datetime)
    assert p.creation_date == expected_result


def test_domain_product_creation_date_is_pendulum_datetime_class():
    p = ProductFactory()
    assert isinstance(p.creation_date, DateTime)


def test_domain_product_creation_date_future_date_not_allowed():
    tomorrow = pendulum.tomorrow(tz=tz)
    with pytest.raises(ValidationError):
        ProductFactory(creation_date=tomorrow)


def test_domain_product_creation_date_naive_date_not_allowed():
    naive_date = pendulum.now(tz=None)
    with pytest.raises(ValidationError):
        ProductFactory(creation_date=naive_date)


def test_domain_product_creation_date_non_utc_date_not_allowed():
    non_utc_date = pendulum.now(tz="Europe/Kiev")
    with pytest.raises(ValidationError):
        ProductFactory(creation_date=non_utc_date)


def test_domain_product_dimensions_are_optional():
    p: Product = ProductFactory(dimensions=None)
    assert p.dimensions is None
    assert p.get_height() is None
    assert p.get_width() is None
    assert p.get_length() is None


@pytest.mark.parametrize("wrong_dim", (1, "abc", (), [], {}, ProductPriceFactory()))
def test_domain_product_dimensions_wrong_type(wrong_dim):
    with pytest.raises(ValidationError):
        ProductFactory(dimensions=wrong_dim)


def test_domain_product_dimensions_instantiate_from_dict():
    dim_dict = ProductDimensionsFactory().dict()
    p = ProductFactory(dimensions=dim_dict)
    assert p.dimensions == ProductDimensions(**dim_dict)


def test_domain_product_color_is_optional():
    p = ProductFactory(color=None)
    assert p.color is None


@pytest.mark.parametrize("wrong_color", (1, b"abc", (), [], {}))
def test_domain_product_color_wrong_type(wrong_color):
    with pytest.raises(ValidationError):
        ProductFactory(color=wrong_color)


def test_domain_product_color_correct_value(faker):
    color = faker.pystr(min_chars=1, max_chars=30).lower()
    p = ProductFactory(color=color)
    assert p.color == color


def test_domain_product_color_becomes_lowercase(faker):
    color = faker.pystr(min_chars=1, max_chars=30).upper()
    p = ProductFactory(color=color)
    assert p.color.islower()


def test_domain_product_material_is_optional():
    p = ProductFactory(material=None)
    assert p.material is None


@pytest.mark.parametrize("wrong_material", (1, b"abc", (), [], {}))
def test_domain_product_material_wrong_type(wrong_material):
    with pytest.raises(ValidationError) as e:
        ProductFactory(material=wrong_material)
    assert e.match("material should be str")


def test_domain_product_material_correct_value(faker):
    material = faker.pystr(min_chars=1, max_chars=30).lower()
    p = ProductFactory(material=material)
    assert p.material == material


def test_domain_product_material_becomes_lowercase(faker):
    material = faker.pystr(min_chars=1, max_chars=30).upper()
    p = ProductFactory(material=material)
    assert p.material.islower()


def test_domain_product_country_of_origin_is_necessary():
    with pytest.raises(ValidationError):
        ProductFactory(country_of_origin=None)


@pytest.mark.parametrize("wrong_country_of_origin", (1, b"abc", (), [], {}))
def test_domain_product_country_of_origin_wrong_type(wrong_country_of_origin):
    with pytest.raises(ValidationError) as e:
        ProductFactory(country_of_origin=wrong_country_of_origin)
    assert e.match("country_of_origin should be str")


def test_domain_product_country_of_origin_empty_string_not_permitted(
    str_lenght_lt_min_lenght_error_msg,
):
    with pytest.raises(ValidationError) as e:
        ProductFactory(country_of_origin="")
    assert e.match(str_lenght_lt_min_lenght_error_msg)


def test_domain_product_country_of_origin_lenght_gt_max_lenght(
    faker, str_lenght_gt_max_lenght_error_msg
):
    wrong_country = faker.pystr(min_chars=61, max_chars=100)
    with pytest.raises(ValidationError) as e:
        ProductFactory(country_of_origin=wrong_country)
    assert e.match(str_lenght_gt_max_lenght_error_msg)


def test_domain_product_country_of_origin_correct_value(faker):
    country_of_origin = faker.country()
    p = ProductFactory(country_of_origin=country_of_origin)
    assert p.country_of_origin == country_of_origin


def test_domain_product_warranty_is_necessary():
    with pytest.raises(ValidationError):
        ProductFactory(warranty=None)


@pytest.mark.parametrize("wrong_warranty", ("1", b"2", Decimal(10), (9,), [2], {3}))
def test_domain_product_warranty_wrong_type(
    wrong_warranty, not_a_valid_integer_error_msg
):
    with pytest.raises(ValidationError) as e:
        ProductFactory(warranty=wrong_warranty)
    assert e.match(not_a_valid_integer_error_msg)


def test_domain_product_warranty_lt_min_value(int_ge_error_msg):
    with pytest.raises(ValidationError) as e:
        ProductFactory(warranty=-1)
    assert e.match(int_ge_error_msg)


def test_domain_product_warranty_lt_min_value(int_le_error_msg):
    with pytest.raises(ValidationError) as e:
        ProductFactory(warranty=11)
    assert e.match(int_le_error_msg)


def test_domain_product_warranty_correct_value(faker):
    warranty = faker.pyint(min_value=0, max_value=10)
    p = ProductFactory(warranty=warranty)
    assert p.warranty == warranty


def test_domain_product_category_is_necessary(none_not_allowed_error_msg):
    with pytest.raises(ValidationError) as e:
        ProductFactory(category=None)
    assert e.match(none_not_allowed_error_msg)


@pytest.mark.parametrize("wrong_category", (1, "a", b"b", Decimal(2)))
def test_domain_product_category_wrong_type(wrong_category, not_a_valid_dict_error_msg):
    with pytest.raises(ValidationError) as e:
        ProductFactory(category=wrong_category)
    assert e.match(not_a_valid_dict_error_msg)


@pytest.mark.parametrize(
    "wrong_category",
    (TopLevelProductCategoryFactory(), MidLevelProductCategoryFactory()),
)
def test_domain_product_category_wrong_category_class(wrong_category):
    with pytest.raises(ValidationError) as e:
        ProductFactory(category=wrong_category)
    assert e.match("TerminalLevelProductCategory")


def test_domain_product_category_correct_type():
    category = TerminalLevelProductCategoryFactory()
    p = ProductFactory(category=category)
    assert p.category == category
    assert isinstance(p.category, TerminalLevelProductCategory)


def test_domain_product_category_wrong_dict(field_required_error_msg):
    category_dict: dict = TerminalLevelProductCategoryFactory().dict()
    category_dict.pop("name")
    with pytest.raises(ValidationError) as e:
        ProductFactory(category=category_dict)
    assert e.match(field_required_error_msg.format(field="name"))


def test_domain_product_category_correct_dict():
    category_dict = TerminalLevelProductCategoryFactory().dict()
    p = ProductFactory(category=category_dict)
    assert p.category == TerminalLevelProductCategory(**category_dict)


def test_domain_product_rating_is_optional():
    p = ProductFactory(rating=None)
    assert p.rating is None


@pytest.mark.parametrize("wrong_rating", ((4,), [1, 2]))
def test_domain_product_rating_wrong_type(wrong_rating):
    with pytest.raises(ValidationError) as e:
        ProductFactory(rating=wrong_rating)
    assert e.match("rating")


@pytest.mark.parametrize("rating", (1, "2", 2.5, Decimal(3.5)))
def test_domain_product_rating_correct_type(rating):
    p = ProductFactory(rating=rating)
    assert p.get_client_rating() == ProductRating(rating)
    assert isinstance(p.get_client_rating(), ProductRating)


@pytest.mark.parametrize(
    ("rating", "reviews"),
    [
        (None, []),
        (ProductRating(4.5), []),
        (None, ProductReviewFactory.build_batch(3)),
        (ProductRating(4.5), ProductReviewFactory.build_batch(3)),
    ],
)
def test_domain_product_add_client_review_successfully_added(rating, reviews):
    new_review = ProductReviewFactory()
    product: Product = ProductFactory(rating=rating, reviews=reviews)
    product.add_client_review(new_review)
    assert new_review in product.reviews


def test_domain_product_add_client_review_rating_is_updated():
    product: Product = ProductFactory(
        rating=1, reviews=[ProductReviewFactory(rating=1)]
    )
    previous_rating = product.get_client_rating()
    product.add_client_review(ProductReviewFactory(rating=5))
    assert product.rating == Product.calculate_rating(product.get_client_reviews())
    assert product.rating != previous_rating


def test_domain_product_delete_client_review_not_found():
    product: Product = ProductFactory(reviews=ProductReviewFactory.build_batch(5))
    product.update_client_rating()
    previous_rating = product.get_client_rating()
    inexistent_id = uuid1()
    with pytest.raises(ValueError):
        product.delete_client_review(inexistent_id)
    assert product.get_client_rating() == previous_rating


def test_domain_product_delete_client_review_found():
    reviews = [ProductReviewFactory(rating=1), ProductReviewFactory(rating=5)]
    product: Product = ProductFactory(reviews=reviews)
    product.update_client_rating()
    previous_rating = product.get_client_rating()
    existant_review = reviews[0]
    product.delete_client_review(existant_review.id)
    assert existant_review not in product.get_client_reviews()
    assert product.get_client_rating() != previous_rating


def test_domain_product_photo_url_is_optional():
    p = ProductFactory(photo_url=None)
    assert p.photo_url is None


@pytest.mark.parametrize("wrong_photo_url", (1, "2", b"3", Decimal(3.5), (4,), [1, 2]))
def test_domain_product_photo_url_wrong_type(
    wrong_photo_url, not_a_valid_dict_error_msg
):
    with pytest.raises(ValidationError) as e:
        ProductFactory(photo_url=wrong_photo_url)
    assert e.match(not_a_valid_dict_error_msg)


def test_domain_product_photo_url_correct_type():
    photo_url = ProductPhotoUrlFactory()
    p = ProductFactory(photo_url=photo_url)
    assert p.photo_url == photo_url


def test_domain_product_photo_url_wrong_dict(field_required_error_msg):
    photo_url_dict = ProductPhotoUrlFactory().dict()
    photo_url_dict.pop("thumbnail")
    with pytest.raises(ValidationError) as e:
        ProductFactory(photo_url=photo_url_dict)
    assert e.match(field_required_error_msg.format(field="thumbnail"))


def test_domain_product_photo_url_correct_dict():
    photo_url_dict = ProductPhotoUrlFactory().dict()
    p = ProductFactory(photo_url=photo_url_dict)
    assert p.photo_url == ProductPhotoUrl(**photo_url_dict)


def test_domain_product_vendor_is_necessary(none_not_allowed_error_msg):
    with pytest.raises(ValidationError) as e:
        ProductFactory(vendor=None)
    assert e.match(none_not_allowed_error_msg)


@pytest.mark.parametrize("wrong_vendor", (1, "2", b"3", Decimal(3.5), (4,), [1, 2]))
def test_domain_product_vendor_wrong_type(wrong_vendor, not_a_valid_dict_error_msg):
    with pytest.raises(ValidationError) as e:
        ProductFactory(vendor=wrong_vendor)
    assert e.match(not_a_valid_dict_error_msg)


def test_domain_product_vendor_correct_type():
    vendor = ProductVendorFactory()
    p = ProductFactory(vendor=vendor)
    assert p.vendor == vendor
    assert isinstance(p.vendor, ProductVendor)


def test_domain_product_vendor_wrong_dict(field_required_error_msg):
    vendor_dict = ProductVendorFactory().dict()
    vendor_dict.pop("name")
    with pytest.raises(ValidationError) as e:
        ProductFactory(vendor=vendor_dict)
    assert e.match(field_required_error_msg.format(field="name"))


def test_domain_product_vendor_correct_dict():
    vendor_dict = ProductVendorFactory().dict()
    p = ProductFactory(vendor=vendor_dict)
    assert p.vendor == ProductVendor(**vendor_dict)
