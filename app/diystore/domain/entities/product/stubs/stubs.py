from decimal import Decimal
from datetime import datetime
from uuid import UUID

from pendulum import now
from pendulum import duration
from pendulum.tz import timezone
from factory import Factory
from factory import SubFactory
from factory import Faker
from factory import LazyAttribute

from diystore.domain.entities.product import Product
from diystore.domain.entities.product import Discount
from diystore.domain.entities.product import ProductReview
from diystore.domain.entities.product import VAT
from diystore.domain.entities.product import ProductPrice
from diystore.domain.entities.product import ProductDimensions
from diystore.domain.entities.product import TopLevelProductCategory
from diystore.domain.entities.product import MidLevelProductCategory
from diystore.domain.entities.product import TerminalLevelProductCategory
from diystore.domain.entities.product import ProductPhotoUrl
from diystore.domain.entities.product import ProductVendor


tz = timezone("UTC")


class DiscountStub(Factory):
    class Meta:
        model = Discount

    rate: Decimal = Faker(
        "pyfloat", right_digits=2, min_value=0.1, max_value=1, positive=True
    )
    name: str = Faker("pystr", max_chars=50)
    creation_date: datetime = now(tz)
    expiry_date: datetime = Faker(
        "date_time_between_dates",
        datetime_start=now(tz) + duration(hours=1),
        datetime_end=now(tz) + duration(months=3),
        tzinfo=tz,
    )
    id: UUID = Faker("uuid4")


class VATStub(Factory):
    class Meta:
        model = VAT

    id: UUID = Faker("uuid4")
    rate: Decimal = Faker("pyfloat", right_digits=2, min_value=0, max_value=1)
    name: str = Faker("pystr", min_chars=2, max_chars=20)


class ProductPriceStub(Factory):
    class Meta:
        model = ProductPrice

    value: Decimal = Faker("pyfloat", right_digits=2, min_value=0.01, max_value=999.99)
    vat: VAT = SubFactory(VATStub)
    discount: Discount = SubFactory(DiscountStub)


class ProductDimensionsStub(Factory):
    class Meta:
        model = ProductDimensions

    height: Decimal = Faker("pyfloat", right_digits=1, min_value=1, max_value=99.9)
    width: Decimal = Faker("pyfloat", right_digits=1, min_value=1, max_value=99.9)
    length: Decimal = Faker("pyfloat", right_digits=1, min_value=1, max_value=99.9)


class TopLevelProductCategoryStub(Factory):
    class Meta:
        model = TopLevelProductCategory

    id: UUID = Faker("uuid4")
    name: str = Faker("pystr", min_chars=2, max_chars=50)
    description: str = Faker("pystr", min_chars=1, max_chars=3000)


class MidLevelProductCategoryStub(Factory):
    class Meta:
        model = MidLevelProductCategory

    id: UUID = Faker("uuid4")
    name: str = Faker("pystr", min_chars=2, max_chars=50)
    description: str = Faker("pystr", min_chars=1, max_chars=300)
    parent = SubFactory(TopLevelProductCategoryStub)


class TerminalLevelProductCategoryStub(Factory):
    class Meta:
        model = TerminalLevelProductCategory

    id: UUID = Faker("uuid4")
    name: str = Faker("pystr", min_chars=2, max_chars=50)
    description: str = Faker("pystr", min_chars=1, max_chars=300)
    parent = SubFactory(MidLevelProductCategoryStub)


class ProductReviewStub(Factory):
    class Meta:
        model = ProductReview

    id: UUID = Faker("uuid4")
    product_id: UUID = Faker("uuid4")
    client_id: UUID = Faker("uuid4")
    rating: Decimal = Faker(
        "pydecimal", right_digits=1, min_value=Decimal("0"), max_value=Decimal("5")
    )
    creation_date: datetime = Faker("date_time", end_datetime=now(tz), tzinfo=tz)
    feedback: str = Faker("pystr", min_chars=1, max_chars=3000)


def generate_dummy_image_url(name: str, width: int, height: int):
    return f"https://cdn.diystore.com/{name}.jpg?size={width}x{height}"


class ProductPhotoUrlStub(Factory):
    class Meta:
        model = ProductPhotoUrl

    _name = Faker("word")
    thumbnail = LazyAttribute(lambda o: generate_dummy_image_url(o._name, 200, 200))
    medium = LazyAttribute(lambda o: generate_dummy_image_url(o._name, 640, 640))
    large = LazyAttribute(lambda o: generate_dummy_image_url(o._name, 1000, 1000))


def generate_dummy_logo_url(o):
    if o.name is None:
        return None
    parse_table = {" ": "-", ",": ""}
    name = o.name.lower()
    for old, new in parse_table.items():
        name = name.replace(old, new)
    return f"https://www.{name}.com/logo.png"


class ProductVendorStub(Factory):
    class Meta:
        model = ProductVendor

    id: UUID = Faker("uuid4")
    name: str = Faker("company")
    description: str = Faker("catch_phrase")
    logo_url = LazyAttribute(generate_dummy_logo_url)


class ProductStub(Factory):
    class Meta:
        model = Product

    id = Faker("uuid4")
    ean = Faker("bothify", text="#############")
    name = Faker("word")
    description = Faker("pystr", min_chars=1, max_chars=300)
    price = SubFactory(ProductPriceStub)
    quantity = Faker("pyint", min_value=0, max_value=1_000_000)
    creation_date = Faker("date_time_between", tzinfo=tz)
    dimensions = SubFactory(ProductDimensionsStub)
    color = Faker("color_name")
    material = Faker("word")
    country_of_origin = Faker("country")
    warranty = Faker("pyint", min_value=0, max_value=5)
    category = SubFactory(TerminalLevelProductCategoryStub)
    rating: Decimal = Faker(
        "pydecimal", right_digits=1, min_value=Decimal("0"), max_value=Decimal("5")
    )
    photo_url = SubFactory(ProductPhotoUrlStub)
    vendor = SubFactory(ProductVendorStub)
