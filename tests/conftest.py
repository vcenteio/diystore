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

