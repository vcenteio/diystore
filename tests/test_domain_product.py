from decimal import Decimal
from uuid import uuid1

import pytest
import pendulum
from pendulum.datetime import DateTime
from pydantic.error_wrappers import ValidationError

from diystore.domain.helpers import round_decimal
from diystore.domain.entities.product import ProductPrice
from diystore.domain.entities.product import ProductDimensions
from diystore.domain.entities.product import TerminalLevelProductCategory
from diystore.domain.entities.product import ProductPhotoUrl
from diystore.domain.entities.product import ProductVendor
from diystore.domain.entities.product import Product
from diystore.domain.entities.product import ProductRating
from diystore.domain.entities.product.stubs import DiscountStub, ProductReviewStub, tz
from diystore.domain.entities.product.stubs import ProductPhotoUrlStub
from diystore.domain.entities.product.stubs import ProductStub
from diystore.domain.entities.product.stubs import ProductDimensionsStub
from diystore.domain.entities.product.stubs import ProductPriceStub
from diystore.domain.entities.product.stubs import TopLevelProductCategoryStub
from diystore.domain.entities.product.stubs import MidLevelProductCategoryStub
from diystore.domain.entities.product.stubs import TerminalLevelProductCategoryStub
from diystore.domain.entities.product.stubs import ProductVendorStub


@pytest.mark.parametrize("wrong_ean", (b"1234567891234", [], dict(), (), {}, type))
def test_domain_product_ean_wrong_type(wrong_ean):
    with pytest.raises(ValidationError):
        ProductStub(ean=wrong_ean)


def test_domain_product_ean_correct_lenght(faker):
    ean = faker.bothify(text="#############")
    p = ProductStub(ean=ean)
    assert p.ean == ean


def test_domain_product_ean_lenght_lt_min(faker):
    ean = faker.bothify(text="############")
    with pytest.raises(ValidationError) as e:
        ProductStub(ean=ean)
    assert e.match("EAN")


def test_domain_product_ean_lenght_lt_max(faker):
    ean = faker.bothify(text="##############")
    with pytest.raises(ValidationError) as e:
        ProductStub(ean=ean)
    assert e.match("EAN")


def test_domain_product_ean_wrong_value(faker):
    ean = faker.bothify(text="#####?#######")
    with pytest.raises(ValidationError) as e:
        ProductStub(ean=ean)


def test_domain_product_ean_int_is_converted_to_str(faker):
    int_ean = faker.pyint(min_value=1000000000000, max_value=9999999999999)
    p = ProductStub(ean=int_ean)
    assert p.ean == str(int_ean)


@pytest.mark.parametrize("wrong_name", (123, b"abc", [], dict(), {}, (), type))
def test_domain_product_name_wrong_type(wrong_name):
    with pytest.raises(ValidationError) as e:
        ProductStub(name=wrong_name)


def test_domain_product_name_empty_string():
    with pytest.raises(ValidationError) as e:
        ProductStub(name="")


def test_domain_product_name_lenght_gt_max_lenght(faker):
    wrong_name = faker.pystr(min_chars=51, max_chars=100)
    with pytest.raises(ValidationError) as e:
        ProductStub(name=wrong_name)


def test_domain_product_valid_name(faker):
    name = faker.pystr(min_chars=1, max_chars=50)
    p = ProductStub(name=name)
    assert p.name == name


def test_domain_product_name_is_necessary():
    with pytest.raises(ValidationError) as e:
        ProductStub(name=None)


def test_domain_product_no_description():
    p = ProductStub(description=None)
    assert p.description is None


@pytest.mark.parametrize("wrong_desc", (123, b"abc", [], dict(), {}, (), type))
def test_domain_product_description_wrong_type(wrong_desc):
    with pytest.raises(ValidationError) as e:
        ProductStub(description=wrong_desc)


def test_domain_product_description_empty_string():
    with pytest.raises(ValidationError) as e:
        ProductStub(description="")


def test_domain_product_description_lenght_gt_max_lenght(faker):
    wrong_description = faker.pystr(min_chars=3001, max_chars=3002)
    with pytest.raises(ValidationError) as e:
        ProductStub(description=wrong_description)


def test_domain_product_valid_description(faker):
    description = faker.pystr(min_chars=1, max_chars=3000)
    p = ProductStub(description=description)
    assert p.description == description


def test_domain_product_price_is_necessary():
    with pytest.raises(ValidationError) as e:
        ProductStub(price=None)


def test_domain_product_valid_price():
    price = ProductPriceStub()
    p = ProductStub(price=price)
    assert p.price == price


def test_domain_product_valid_price_dict():
    price_dict = ProductPriceStub().dict()
    p = ProductStub(price=price_dict)
    assert p.price == ProductPrice(**price_dict)


def test_domain_product_get_final_price():
    price: ProductPrice = ProductPriceStub()
    p: Product = ProductStub(price=price)
    assert p.get_final_price() == price.calculate()


def test_domain_product_get_final_price_without_discount():
    price: ProductPrice = ProductPriceStub()
    p: Product = ProductStub(price=price)
    assert p.get_final_price_without_discount() == price.calculate_without_discount()


@pytest.mark.parametrize("wrong_price", ("a", b"b", (1,), [2]))
def test_domain_product_set_base_price_wrong_type(wrong_price):
    p: Product = ProductStub()
    with pytest.raises(ValidationError) as e:
        p.set_base_price(wrong_price)


@pytest.mark.parametrize("price", (1, 50.2, "34.21", Decimal("123.32")))
def test_domain_product_set_base_price_correct_type(price):
    p: Product = ProductStub()
    p.set_base_price(price)
    assert p.get_base_price() == round_decimal(Decimal(price), "1.00")


def test_domain_product_get_discount_rate_with_discount():
    price: ProductPrice = ProductPriceStub()
    discount_rate = price.get_discount_rate()
    p = ProductStub(price=price)
    assert p.get_discount_rate() == discount_rate


def test_domain_product_get_discount_rate_no_discount():
    price: ProductPrice = ProductPriceStub(discount=None)
    p = ProductStub(price=price)
    assert p.get_discount_rate() is None


def test_domain_product_get_discount():
    price: ProductPrice = ProductPriceStub()
    discount = price.discount
    p = ProductStub(price=price)
    assert p.get_discount() == discount


@pytest.mark.parametrize("wrong_discount", ("a", 1, b"123", [1]))
def test_domain_product_set_discount_wrong_type(wrong_discount):
    p = ProductStub()
    with pytest.raises(ValidationError):
        p.set_discount(wrong_discount)


def test_domain_product_set_discount_correct_type():
    discount = DiscountStub()
    p: Product = ProductStub()
    p.set_discount(discount)
    assert p.get_discount() == discount


def test_domain_product_set_discount_wrong_dict():
    discount_dict = DiscountStub().dict()
    discount_dict.pop("rate")
    p: Product = ProductStub()
    with pytest.raises(ValidationError):
        p.set_discount(discount_dict)


def test_domain_product_set_discount_correct_dict():
    discount_dict = DiscountStub().dict()
    p: Product = ProductStub()
    p.set_discount(discount_dict)
    assert p.get_discount() == DiscountStub(**discount_dict)


def test_domain_product_get_vat_rate():
    price = ProductPriceStub()
    expected_vat = price.get_vat_rate()
    p: Product = ProductStub(price=price)
    assert p.get_vat_rate() == expected_vat


def test_domain_product_get_vat():
    price = ProductPriceStub()
    expected_vat_obj = price.vat
    p: Product = ProductStub(price=price)
    assert p.get_vat() == expected_vat_obj


@pytest.mark.parametrize("wrong_vat", (1, "a", b"123"))
def test_domain_product_set_vat_wrong_type(wrong_vat):
    with pytest.raises(ValidationError):
        ProductStub().set_vat(wrong_vat)


def test_domain_product_set_vat_correct_type():
    price = ProductPriceStub()
    p: Product = ProductStub()
    p.set_vat(price.vat)
    assert p.get_vat() == price.vat


def test_domain_product_quantity_is_necessary():
    with pytest.raises(ValidationError):
        ProductStub(quantity=None)


@pytest.mark.parametrize("wrong_qty", ("1", b"1", True, False, None, "", []))
def test_domain_product_quantity_wrong_type(wrong_qty):
    with pytest.raises(ValidationError):
        ProductStub(quantity=wrong_qty)


def test_domain_product_quantity_lt_min_value():
    with pytest.raises(ValidationError):
        ProductStub(quantity=-1)


def test_domain_product_quantity_gt_max_value():
    with pytest.raises(ValidationError):
        ProductStub(quantity=1_000_001)


def test_domain_product_creation_date_is_necessary():
    with pytest.raises(ValidationError):
        ProductStub(creation_date=None)


@pytest.mark.parametrize("wrong_date", ([], (), {}))
def test_domain_product_creation_date_wrong_type(wrong_date):
    with pytest.raises(ValidationError):
        ProductStub(creation_date=wrong_date)


def test_domain_product_creation_date_from_float_posix_timestamp():
    timestamp = pendulum.now("UTC").timestamp()
    expected_result = DateTime.fromtimestamp(timestamp, tz=tz)
    p = ProductStub(creation_date=timestamp)
    assert p.creation_date == expected_result


def test_domain_product_creation_date_from_str_posix_timestamp():
    timestamp = pendulum.now("UTC").timestamp()
    expected_result = DateTime.fromtimestamp(timestamp, tz=tz)
    p = ProductStub(creation_date=str(timestamp))
    assert p.creation_date == expected_result


def test_domain_product_creation_date_from_int_ordinal():
    ordinal = pendulum.now("UTC").toordinal()
    with pytest.raises(ValidationError):
        ProductStub(creation_date=ordinal)


def test_domain_product_creation_date_from_iso_format():
    iso_datetime = pendulum.now("UTC").isoformat()
    expected_result = DateTime.fromisoformat(iso_datetime)
    p = ProductStub(creation_date=iso_datetime)
    assert p.creation_date == expected_result


def test_domain_product_creation_date_is_pendulum_datetime_class():
    p = ProductStub()
    assert isinstance(p.creation_date, DateTime)


def test_domain_product_creation_date_future_date_not_allowed():
    tomorrow = pendulum.tomorrow(tz=tz)
    with pytest.raises(ValidationError):
        ProductStub(creation_date=tomorrow)


def test_domain_product_creation_date_naive_date_not_allowed():
    naive_date = pendulum.now(tz=None)
    with pytest.raises(ValidationError):
        ProductStub(creation_date=naive_date)


def test_domain_product_creation_date_non_utc_date_not_allowed():
    non_utc_date = pendulum.now(tz="Europe/Kiev")
    with pytest.raises(ValidationError):
        ProductStub(creation_date=non_utc_date)


def test_domain_product_dimensions_are_optional():
    p: Product = ProductStub(dimensions=None)
    assert p.dimensions is None
    assert p.get_height() is None
    assert p.get_width() is None
    assert p.get_length() is None


@pytest.mark.parametrize("wrong_dim", (1, "abc", (), [], {}, ProductPriceStub()))
def test_domain_product_dimensions_wrong_type(wrong_dim):
    with pytest.raises(ValidationError):
        ProductStub(dimensions=wrong_dim)


def test_domain_product_dimensions_instantiate_from_dict():
    dim_dict = ProductDimensionsStub().dict()
    p = ProductStub(dimensions=dim_dict)
    assert p.dimensions == ProductDimensions(**dim_dict)


def test_domain_product_color_is_optional():
    p = ProductStub(color=None)
    assert p.color is None


@pytest.mark.parametrize("wrong_color", (1, b"abc", (), [], {}))
def test_domain_product_color_wrong_type(wrong_color):
    with pytest.raises(ValidationError):
        ProductStub(color=wrong_color)


def test_domain_product_color_correct_value(faker):
    color = faker.pystr(min_chars=1, max_chars=30).lower()
    p = ProductStub(color=color)
    assert p.color == color


def test_domain_product_color_becomes_lowercase(faker):
    color = faker.pystr(min_chars=1, max_chars=30).upper()
    p = ProductStub(color=color)
    assert p.color.islower()


def test_domain_product_material_is_optional():
    p = ProductStub(material=None)
    assert p.material is None


@pytest.mark.parametrize("wrong_material", (1, b"abc", (), [], {}))
def test_domain_product_material_wrong_type(wrong_material):
    with pytest.raises(ValidationError) as e:
        ProductStub(material=wrong_material)
    assert e.match("material should be str")


def test_domain_product_material_correct_value(faker):
    material = faker.pystr(min_chars=1, max_chars=30).lower()
    p = ProductStub(material=material)
    assert p.material == material


def test_domain_product_material_becomes_lowercase(faker):
    material = faker.pystr(min_chars=1, max_chars=30).upper()
    p = ProductStub(material=material)
    assert p.material.islower()


def test_domain_product_country_of_origin_is_necessary():
    with pytest.raises(ValidationError):
        ProductStub(country_of_origin=None)


@pytest.mark.parametrize("wrong_country_of_origin", (1, b"abc", (), [], {}))
def test_domain_product_country_of_origin_wrong_type(wrong_country_of_origin):
    with pytest.raises(ValidationError) as e:
        ProductStub(country_of_origin=wrong_country_of_origin)
    assert e.match("country_of_origin should be str")


def test_domain_product_country_of_origin_empty_string_not_permitted(
    str_lenght_lt_min_lenght_error_msg,
):
    with pytest.raises(ValidationError) as e:
        ProductStub(country_of_origin="")
    assert e.match(str_lenght_lt_min_lenght_error_msg)


def test_domain_product_country_of_origin_lenght_gt_max_lenght(
    faker, str_lenght_gt_max_lenght_error_msg
):
    wrong_country = faker.pystr(min_chars=61, max_chars=100)
    with pytest.raises(ValidationError) as e:
        ProductStub(country_of_origin=wrong_country)
    assert e.match(str_lenght_gt_max_lenght_error_msg)


def test_domain_product_country_of_origin_correct_value(faker):
    country_of_origin = faker.country()
    p = ProductStub(country_of_origin=country_of_origin)
    assert p.country_of_origin == country_of_origin


def test_domain_product_warranty_is_necessary():
    with pytest.raises(ValidationError):
        ProductStub(warranty=None)


@pytest.mark.parametrize("wrong_warranty", ("1", b"2", Decimal(10), (9,), [2], {3}))
def test_domain_product_warranty_wrong_type(
    wrong_warranty, not_a_valid_integer_error_msg
):
    with pytest.raises(ValidationError) as e:
        ProductStub(warranty=wrong_warranty)
    assert e.match(not_a_valid_integer_error_msg)


def test_domain_product_warranty_lt_min_value(int_ge_error_msg):
    with pytest.raises(ValidationError) as e:
        ProductStub(warranty=-1)
    assert e.match(int_ge_error_msg)


def test_domain_product_warranty_lt_min_value(int_le_error_msg):
    with pytest.raises(ValidationError) as e:
        ProductStub(warranty=11)
    assert e.match(int_le_error_msg)


def test_domain_product_warranty_correct_value(faker):
    warranty = faker.pyint(min_value=0, max_value=10)
    p = ProductStub(warranty=warranty)
    assert p.warranty == warranty


def test_domain_product_category_is_necessary(none_not_allowed_error_msg):
    with pytest.raises(ValidationError) as e:
        ProductStub(category=None)
    assert e.match(none_not_allowed_error_msg)


@pytest.mark.parametrize("wrong_category", (1, "a", b"b", Decimal(2)))
def test_domain_product_category_wrong_type(wrong_category, not_a_valid_dict_error_msg):
    with pytest.raises(ValidationError) as e:
        ProductStub(category=wrong_category)
    assert e.match(not_a_valid_dict_error_msg)


@pytest.mark.parametrize(
    "wrong_category",
    (TopLevelProductCategoryStub(), MidLevelProductCategoryStub()),
)
def test_domain_product_category_wrong_category_class(wrong_category):
    with pytest.raises(ValidationError) as e:
        ProductStub(category=wrong_category)
    assert e.match("TerminalLevelProductCategory")


def test_domain_product_category_correct_type():
    category = TerminalLevelProductCategoryStub()
    p = ProductStub(category=category)
    assert p.category == category
    assert isinstance(p.category, TerminalLevelProductCategory)


def test_domain_product_category_wrong_dict(field_required_error_msg):
    category_dict: dict = TerminalLevelProductCategoryStub().dict()
    category_dict.pop("name")
    with pytest.raises(ValidationError) as e:
        ProductStub(category=category_dict)
    assert e.match(field_required_error_msg.format(field="name"))


def test_domain_product_category_correct_dict():
    category_dict = TerminalLevelProductCategoryStub().dict()
    p = ProductStub(category=category_dict)
    assert p.category == TerminalLevelProductCategory(**category_dict)


def test_domain_product_rating_is_optional():
    p = ProductStub(rating=None)
    assert p.rating is None


@pytest.mark.parametrize("wrong_rating", ((4,), [1, 2]))
def test_domain_product_rating_wrong_type(wrong_rating):
    with pytest.raises(ValidationError) as e:
        ProductStub(rating=wrong_rating)
    assert e.match("rating")


@pytest.mark.parametrize("rating", (1, "2", 2.5, Decimal(3.5)))
def test_domain_product_rating_correct_type(rating):
    p = ProductStub(rating=rating)
    assert p.get_client_rating() == ProductRating(rating)
    assert isinstance(p.get_client_rating(), ProductRating)


@pytest.mark.parametrize(
    ("rating", "reviews"),
    [
        (None, []),
        (ProductRating(4.5), []),
        (None, ProductReviewStub.build_batch(3)),
        (ProductRating(4.5), ProductReviewStub.build_batch(3)),
    ],
)
def test_domain_product_add_client_review_successfully_added(rating, reviews):
    new_review = ProductReviewStub()
    product: Product = ProductStub(rating=rating, reviews=reviews)
    product.add_client_review(new_review)
    assert new_review.id.int in product.reviews
    assert new_review in product.reviews.values()


def test_domain_product_add_client_review_rating_is_updated():
    product: Product = ProductStub(rating=1, reviews=[ProductReviewStub(rating=1)])
    previous_rating = product.get_client_rating()
    product.add_client_review(ProductReviewStub(rating=5))
    assert product.rating == product.calculate_rating()
    assert product.rating != previous_rating


def test_domain_product_delete_client_review_not_found():
    product: Product = ProductStub(reviews=ProductReviewStub.build_batch(5))
    product.update_client_rating()
    previous_rating = product.get_client_rating()
    inexistent_id = uuid1()
    with pytest.raises(ValueError):
        product.delete_client_review(inexistent_id)
    assert product.get_client_rating() == previous_rating


def test_domain_product_delete_client_review_found():
    reviews = (ProductReviewStub(rating=1), ProductReviewStub(rating=5))
    product: Product = ProductStub(reviews=reviews)
    product.update_client_rating()
    previous_rating = product.get_client_rating()
    existant_review = reviews[0]
    deleted_review = product.delete_client_review(existant_review.id)
    assert existant_review not in product.get_client_reviews()
    assert product.get_client_rating() != previous_rating
    assert product.get_client_rating() == reviews[1].rating
    assert deleted_review == existant_review


def test_domain_product_photo_url_is_optional():
    p = ProductStub(photo_url=None)
    assert p.photo_url is None


@pytest.mark.parametrize("wrong_photo_url", (1, "2", b"3", Decimal(3.5), (4,), [1, 2]))
def test_domain_product_photo_url_wrong_type(
    wrong_photo_url, not_a_valid_dict_error_msg
):
    with pytest.raises(ValidationError) as e:
        ProductStub(photo_url=wrong_photo_url)
    assert e.match(not_a_valid_dict_error_msg)


def test_domain_product_photo_url_correct_type():
    photo_url = ProductPhotoUrlStub()
    p = ProductStub(photo_url=photo_url)
    assert p.photo_url == photo_url


def test_domain_product_photo_url_wrong_dict(field_required_error_msg):
    photo_url_dict = ProductPhotoUrlStub().dict()
    photo_url_dict.pop("thumbnail")
    with pytest.raises(ValidationError) as e:
        ProductStub(photo_url=photo_url_dict)
    assert e.match(field_required_error_msg.format(field="thumbnail"))


def test_domain_product_photo_url_correct_dict():
    photo_url_dict = ProductPhotoUrlStub().dict()
    p = ProductStub(photo_url=photo_url_dict)
    assert p.photo_url == ProductPhotoUrl(**photo_url_dict)


def test_domain_product_vendor_is_necessary(none_not_allowed_error_msg):
    with pytest.raises(ValidationError) as e:
        ProductStub(vendor=None)
    assert e.match(none_not_allowed_error_msg)


@pytest.mark.parametrize("wrong_vendor", (1, "2", b"3", Decimal(3.5), (4,), [1, 2]))
def test_domain_product_vendor_wrong_type(wrong_vendor, not_a_valid_dict_error_msg):
    with pytest.raises(ValidationError) as e:
        ProductStub(vendor=wrong_vendor)
    assert e.match(not_a_valid_dict_error_msg)


def test_domain_product_vendor_correct_type():
    vendor = ProductVendorStub()
    p = ProductStub(vendor=vendor)
    assert p.vendor == vendor
    assert isinstance(p.vendor, ProductVendor)


def test_domain_product_vendor_wrong_dict(field_required_error_msg):
    vendor_dict = ProductVendorStub().dict()
    vendor_dict.pop("name")
    with pytest.raises(ValidationError) as e:
        ProductStub(vendor=vendor_dict)
    assert e.match(field_required_error_msg.format(field="name"))


def test_domain_product_vendor_correct_dict():
    vendor_dict = ProductVendorStub().dict()
    p = ProductStub(vendor=vendor_dict)
    assert p.vendor == ProductVendor(**vendor_dict)
