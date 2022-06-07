from decimal import Decimal
from datetime import datetime
from uuid import UUID

import pytest
import pendulum
from pendulum import now
from pendulum import duration
from pendulum.tz import timezone
from factory import Factory
from factory import SubFactory
from factory import Faker


from dyistore.domain.helpers import round_decimal
from dyistore.domain.product.discount import Discount
from dyistore.domain.product.review import ProductReview
from dyistore.domain.product.vat import VAT
from dyistore.domain.product.price import ProductPrice
from dyistore.domain.product.dimensions import ProductDimensions
from dyistore.domain.product.categories import ProductCategory
from dyistore.domain.product.categories import TopLevelProductCategory
from dyistore.domain.product.categories import MidLevelProductCategory
from dyistore.domain.product.categories import TerminalLevelProductCategory


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


class VATFactory(Factory):
    class Meta:
        model = VAT

    id: UUID = Faker("uuid4")
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

    height: Decimal = Faker("pyfloat", right_digits=1, min_value=0.1, max_value=99.9)
    width: Decimal = Faker("pyfloat", right_digits=1, min_value=0.1, max_value=99.9)
    length: Decimal = Faker("pyfloat", right_digits=1, min_value=0.1, max_value=99.9)


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
def str_lenght_gt_max_lenght_error_msg():
    return r"ensure this value has at most \d+ characters"


@pytest.fixture
def str_lenght_lt_min_lenght_error_msg():
    return r"ensure this value has at least \d+ characters"


@pytest.fixture
def non_utc_past_datetime(faker):
    date = faker.date_time(end_datetime=now().subtract(hours=1))
    return pendulum.instance(date, tz="Europe/Lisbon")


@pytest.fixture
def naive_past_datetime(faker):
    date = faker.date_time(end_datetime=now().subtract(hours=1))
    return pendulum.instance(date).naive()
