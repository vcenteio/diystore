from decimal import Decimal
from datetime import datetime
from uuid import UUID

import pytest
from pendulum import now
from pendulum import duration
from pendulum.tz import timezone
from factory import Factory
from factory import SubFactory
from factory import Faker

from dyistore.domain.product.discount import Discount
from dyistore.domain.product.vat import VAT
from dyistore.domain.product.price import ProductPrice
from dyistore.domain.product.dimensions import ProductDimensions


tz = timezone("UTC")


class DiscountFactory(Factory):
    class Meta:
        model = Discount

    rate: Decimal = Faker("pyfloat", right_digits=2, min_value=0.01, max_value=1)
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

    height: Decimal = Faker(
        "pyfloat", right_digits=1, min_value=0.1, max_value=99.9
    )
    width: Decimal = Faker("pyfloat", right_digits=1, min_value=0.1, max_value=99.9)
    length: Decimal = Faker(
        "pyfloat", right_digits=1, min_value=0.1, max_value=99.9
    )


@pytest.fixture
def valid_product_price_float(faker):
    return faker.pyfloat(right_digits=2, min_value=0.01, max_value=999_999.99)


@pytest.fixture
def valid_product_price_decimal(faker):
    return faker.pydecimal(right_digits=2, min_value=0, max_value=999_999)


@pytest.fixture
def future_date():
    return now(tz).add(years=1)
