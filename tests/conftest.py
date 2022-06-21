from decimal import Decimal
from datetime import datetime
from typing import Union
from unittest.mock import Mock
from uuid import UUID
from uuid import uuid4

import pytest
import pendulum
from pendulum import now
from pendulum import duration
from pendulum.tz import timezone
from factory import Factory
from factory import SubFactory
from factory import Faker
from factory import LazyAttribute
from devtools import debug
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session

from diystore.domain.helpers import round_decimal
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
from diystore.domain.entities.product import EAN13
from diystore.application.usecases.product import GetProductsInputDTO
from diystore.application.usecases.product import ProductOrderingCriteria
from diystore.application.usecases.product import GetProductOutputDTO
from diystore.application.usecases.product import ProductRepository
from diystore.application.usecases.product import GetProductInputDTO
from diystore.infrastructure.repositories.sqlrepository import Base
from diystore.infrastructure.repositories.sqlrepository import VatOrmModel
from diystore.infrastructure.repositories.sqlrepository import DiscountOrmModel
from diystore.infrastructure.repositories.sqlrepository import TopLevelCategoryOrmModel
from diystore.infrastructure.repositories.sqlrepository import MidLevelCategoryOrmModel
from diystore.infrastructure.repositories.sqlrepository import TerminalCategoryOrmModel
from diystore.infrastructure.repositories.sqlrepository import ProductReviewOrmModel
from diystore.infrastructure.repositories.sqlrepository import ProductVendorOrmModel
from diystore.infrastructure.repositories.sqlrepository import ProductOrmModel


tz = timezone("UTC")


class DiscountFactory(Factory):
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


class DiscountOrmModelFactory(Factory):
    class Meta:
        model = DiscountOrmModel

    rate: float = Faker(
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


class VATFactory(Factory):
    class Meta:
        model = VAT

    id: UUID = Faker("uuid4")
    rate: Decimal = Faker("pyfloat", right_digits=2, min_value=0, max_value=1)
    name: str = Faker("pystr", min_chars=2, max_chars=20)


class VatOrmModelFactory(Factory):
    class Meta:
        model = VatOrmModel

    id: bytes = Faker("uuid4")
    rate: Decimal = Faker("pyfloat", right_digits=2, min_value=0, max_value=1)
    name: str = Faker("pystr", min_chars=2, max_chars=20)


class ProductPriceFactory(Factory):
    class Meta:
        model = ProductPrice

    value: Decimal = Faker("pyfloat", right_digits=2, min_value=0.01, max_value=999.99)
    vat: VAT = SubFactory(VATFactory)
    discount: Discount = SubFactory(DiscountFactory)


class ProductDimensionsFactory(Factory):
    class Meta:
        model = ProductDimensions

    height: Decimal = Faker("pyfloat", right_digits=1, min_value=1, max_value=99.9)
    width: Decimal = Faker("pyfloat", right_digits=1, min_value=1, max_value=99.9)
    length: Decimal = Faker("pyfloat", right_digits=1, min_value=1, max_value=99.9)


class TopLevelProductCategoryFactory(Factory):
    class Meta:
        model = TopLevelProductCategory

    id: UUID = Faker("uuid4")
    name: str = Faker("pystr", min_chars=2, max_chars=50)
    description: str = Faker("pystr", min_chars=1, max_chars=3000)


class MidLevelProductCategoryFactory(Factory):
    class Meta:
        model = MidLevelProductCategory

    id: UUID = Faker("uuid4")
    name: str = Faker("pystr", min_chars=2, max_chars=50)
    description: str = Faker("pystr", min_chars=1, max_chars=300)
    parent = SubFactory(TopLevelProductCategoryFactory)


class TerminalLevelProductCategoryFactory(Factory):
    class Meta:
        model = TerminalLevelProductCategory

    id: UUID = Faker("uuid4")
    name: str = Faker("pystr", min_chars=2, max_chars=50)
    description: str = Faker("pystr", min_chars=1, max_chars=300)
    parent = SubFactory(MidLevelProductCategoryFactory)


class TopLevelCategoryOrmModelFactory(Factory):
    class Meta:
        model = TopLevelCategoryOrmModel

    id: UUID = Faker("uuid4")
    name: str = Faker("pystr", min_chars=2, max_chars=50)
    description: str = Faker("pystr", min_chars=1, max_chars=3000)


class MidLevelCategoryOrmModelFactory(Factory):
    class Meta:
        model = MidLevelCategoryOrmModel

    id: UUID = Faker("uuid4")
    name: str = Faker("pystr", min_chars=2, max_chars=50)
    description: str = Faker("pystr", min_chars=1, max_chars=300)
    parent_id: UUID = Faker("uuid4")
    parent = SubFactory(TopLevelCategoryOrmModelFactory)


class TerminalCategoryOrmModelFactory(Factory):
    class Meta:
        model = TerminalCategoryOrmModel

    id: UUID = Faker("uuid4")
    name: str = Faker("pystr", min_chars=2, max_chars=50)
    description: str = Faker("pystr", min_chars=1, max_chars=300)
    parent_id: UUID = Faker("uuid4")
    parent = SubFactory(MidLevelCategoryOrmModelFactory)


class ProductReviewFactory(Factory):
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


class ProductReviewOrmModelFactory(Factory):
    class Meta:
        model = ProductReviewOrmModel

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


class ProductPhotoUrlFactory(Factory):
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


class ProductVendorFactory(Factory):
    class Meta:
        model = ProductVendor

    id: UUID = Faker("uuid4")
    name: str = Faker("company")
    description: str = Faker("catch_phrase")
    logo_url = LazyAttribute(generate_dummy_logo_url)


class ProductVendorOrmModelFactory(Factory):
    class Meta:
        model = ProductVendorOrmModel

    id: UUID = Faker("uuid4")
    name: str = Faker("company")
    description: str = Faker("catch_phrase")
    logo_url = LazyAttribute(generate_dummy_logo_url)


class ProductFactory(Factory):
    class Meta:
        model = Product

    id = Faker("uuid4")
    ean = Faker("bothify", text="#############")
    name = Faker("word")
    description = Faker("pystr", min_chars=1, max_chars=300)
    price = SubFactory(ProductPriceFactory)
    quantity = Faker("pyint", min_value=0, max_value=1_000_000)
    creation_date = Faker("date_time_between", tzinfo=tz)
    dimensions = SubFactory(ProductDimensionsFactory)
    color = Faker("color_name")
    material = Faker("word")
    country_of_origin = Faker("country")
    warranty = Faker("pyint", min_value=0, max_value=5)
    category = SubFactory(TerminalLevelProductCategoryFactory)
    rating: Decimal = Faker(
        "pydecimal", right_digits=1, min_value=Decimal("0"), max_value=Decimal("5")
    )
    photo_url = SubFactory(ProductPhotoUrlFactory)
    vendor = SubFactory(ProductVendorFactory)


class ProductOrmModelFactory(Factory):
    class Meta:
        model = ProductOrmModel

    id = Faker("uuid4")
    ean = Faker("bothify", text="#############")
    name = Faker("word")
    description = Faker("pystr", min_chars=1, max_chars=300)
    base_price: Decimal = Faker(
        "pyfloat", right_digits=2, min_value=0.01, max_value=999.99
    )
    vat_id = Faker("uuid4")
    discount_id = Faker("uuid4")
    quantity = Faker("pyint", min_value=0, max_value=1_000_000)
    creation_date = Faker("date_time_between", tzinfo=tz)
    height: Decimal = Faker("pyfloat", right_digits=1, min_value=1, max_value=99.9)
    width: Decimal = Faker("pyfloat", right_digits=1, min_value=1, max_value=99.9)
    length: Decimal = Faker("pyfloat", right_digits=1, min_value=1, max_value=99.9)
    color = Faker("color_name")
    material = Faker("word")
    country_of_origin = Faker("country")
    warranty = Faker("pyint", min_value=0, max_value=5)
    category_id = Faker("uuid4")
    rating: Decimal = Faker(
        "pydecimal", right_digits=1, min_value=Decimal("0"), max_value=Decimal("5")
    )
    thumbnail_photo_url = Faker("image_url")
    medium_size_photo_url = Faker("image_url")
    large_size_photo_url = Faker("image_url")
    vendor_id = Faker("uuid4")


class LoadedProductOrmModelFactory(ProductOrmModelFactory):
    vat = LazyAttribute(lambda o: VatOrmModelFactory(id=o.vat_id))
    discount = LazyAttribute(lambda o: DiscountOrmModelFactory(id=o.discount_id))
    category = LazyAttribute(lambda o: TerminalCategoryOrmModelFactory(id=o.category_id))
    vendor = LazyAttribute(lambda o: ProductVendorOrmModelFactory(id=o.vendor_id))
    reviews = LazyAttribute(lambda o: ProductReviewOrmModelFactory.build_batch(3, product_id=o.id))


class ProductOrderingCriteriaFactory(Factory):
    class Meta:
        model = ProductOrderingCriteria

    property = Faker("random_element", elements=(1, 2))
    type = Faker("random_element", elements=(1, 2))


class GetProductsInputDTOFactory(Factory):
    class Meta:
        model = GetProductsInputDTO

    category_id = Faker("uuid4")
    price_min = Faker("pydecimal", min_value=0, max_value=99, right_digits=2)
    price_max = Faker("pydecimal", min_value=100, max_value=999, right_digits=2)
    rating_min = Faker("pydecimal", min_value=0, max_value=2, right_digits=1)
    rating_max = Faker("pydecimal", min_value=3, max_value=5, right_digits=1)
    ordering_criteria = SubFactory(ProductOrderingCriteriaFactory)
    with_discounts_only = Faker("pybool")


class ProductOutputDTOFactory(Factory):
    class Meta:
        model = GetProductOutputDTO

    id = Faker("uuid4")
    ean = Faker("bothify", text="#############")
    name = Faker("word")
    description = Faker("pystr", min_chars=1, max_chars=300)
    price: Decimal = Faker("pyfloat", right_digits=2, min_value=0.01, max_value=999.99)
    discount: Decimal = Faker(
        "pyfloat", right_digits=2, min_value=0.1, max_value=1, positive=True
    )
    price_without_discount: Decimal = Faker(
        "pyfloat", right_digits=2, min_value=0.01, max_value=999.99
    )
    vat: Decimal = Faker("pyfloat", right_digits=2, min_value=0, max_value=1)
    in_stock: bool = Faker("pybool")
    height: Decimal = Faker("pyfloat", right_digits=1, min_value=1, max_value=99.9)
    width: Decimal = Faker("pyfloat", right_digits=1, min_value=1, max_value=99.9)
    length: Decimal = Faker("pyfloat", right_digits=1, min_value=1, max_value=99.9)
    color = Faker("color_name")
    material = Faker("word")
    country_of_origin = Faker("country")
    warranty = Faker("pyint", min_value=0, max_value=5)
    category_id = Faker("uuid4")
    category_name = Faker("word")
    client_rating = Faker(
        "pydecimal", right_digits=1, min_value=Decimal("0"), max_value=Decimal("5")
    )
    thumbnail_photo_url = Faker("image_url")
    medium_size_photo_url = Faker("image_url")
    large_size_photo_url = Faker("image_url")
    vendor_id = Faker("uuid4")
    vendor_name = Faker("word")


class GetProductInputDTOFactory(Factory):
    class Meta:
        model = GetProductInputDTO

    product_id = Faker("uuid4")


@pytest.fixture
def non_str_type(faker):
    types = (
        123,
        1.23,
        Decimal(123),
        b"123",
        [1, 2, 3],
        (1, 2, 3),
        {1, 2, 3},
        dict(a=1, b=2, c=3),
        type,
    )
    return faker.random_element(types)


@pytest.fixture
def valid_product_price_float(faker):
    return faker.pyfloat(right_digits=2, min_value=0.01, max_value=999_999.99)


@pytest.fixture
def valid_product_price_decimal(faker):
    return faker.pydecimal(right_digits=2, min_value=0, max_value=999_999)


@pytest.fixture
def future_date():
    return now(tz).add(years=1)


@pytest.fixture
def valid_uuid(faker):
    return faker.uuid4(cast_to=None)


@pytest.fixture
def str_uuid(faker):
    return faker.uuid4()


@pytest.fixture
def bytes_uuid(faker):
    _uuid = faker.uuid4(cast_to=None)
    return _uuid.bytes


@pytest.fixture
def invalid_uuid_str(faker):
    uuids = (
        "c17d279c-faf6-ba7-9d21-79c55b58c15a",
        "6e2336a7-820e-af58-82a3-0e2dd9df0451",
        "1197e28-82ec-4cab-abc2-820afddb1c48",
        "8e6f4545-f4b-4787-b3ad-ae2a4b6364cd",
        "c17d279c-faf6-4ba7-921-79c55b58c15a",
        "6e2336a7-820e-4f58-82a3-0e2dd9df045",
        "1197e28f1-82ec-4cab-abc2-820afddb1c48",
        "8e6f4545-f45b2-4787-b3ad-ae2a4b6364cd",
        "1197e28f-82ec-4cab3-abc2-820afddb1c48",
        "8e6f4545-f45b-4787-b3ad4-ae2a4b6364cd",
        "1197e28f-82ec-4cab-abc2-820afddb1c485",
        "-f45b-4787-b3ad-ae2a4b6364cd",
        "8e6f4545-4787-b3ad-ae2a4b6364cd",
        "8e6f4545-f45b-b3ad-ae2a4b6364cd",
        "8e6f4545-f45b-4787-ae2a4b6364cd",
        "8e6f4545-f45b-4787-b3ad-",
    )
    return faker.random_element(uuids)


@pytest.fixture
def none_not_allowed_error_msg():
    return "is not an allowed value"


@pytest.fixture
def not_a_valid_dict_error_msg():
    return "a valid dict"


@pytest.fixture
def field_required_error_msg():
    return "{field}\n  field required"


@pytest.fixture
def str_lenght_gt_max_lenght_error_msg():
    return r"ensure this value has at most \d+ characters"


@pytest.fixture
def str_lenght_lt_min_lenght_error_msg():
    return r"ensure this value has at least \d+ characters"


@pytest.fixture
def not_a_valid_integer_error_msg():
    return "value is not a valid integer"


@pytest.fixture
def int_ge_error_msg():
    return "ensure this value is greater than or equal to"


@pytest.fixture
def int_le_error_msg():
    return "ensure this value is less than or equal to"


@pytest.fixture
def invalid_value_for_decimal_error_msg():
    return "value should be of type Decimal, int, float or str"


@pytest.fixture
def non_utc_past_datetime(faker):
    date = faker.date_time(end_datetime=now().subtract(hours=1))
    return pendulum.instance(date, tz="Europe/Lisbon")


@pytest.fixture
def naive_past_datetime(faker):
    date = faker.date_time(end_datetime=now().subtract(hours=1))
    return pendulum.instance(date).naive()


@pytest.fixture
def mock_products_repository():
    return Mock(ProductRepository)


@pytest.fixture(scope="session")
def product_stub_list():
    return [ProductFactory() for _ in range(30)]


@pytest.fixture(scope="session")
def session_factory():
    engine = create_engine("sqlite:///:memory:", echo=True, future=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine)
    return Session


@pytest.fixture()
def orm_session(session_factory):
    session: Session = session_factory()
    yield session
    session.close()
