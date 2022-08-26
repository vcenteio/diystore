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

from diystore.infrastructure.repositories.sqlrepository import VatOrmModel
from diystore.infrastructure.repositories.sqlrepository import DiscountOrmModel
from diystore.infrastructure.repositories.sqlrepository import TopLevelCategoryOrmModel
from diystore.infrastructure.repositories.sqlrepository import MidLevelCategoryOrmModel
from diystore.infrastructure.repositories.sqlrepository import TerminalCategoryOrmModel
from diystore.infrastructure.repositories.sqlrepository import ProductReviewOrmModel
from diystore.infrastructure.repositories.sqlrepository import ProductVendorOrmModel
from diystore.infrastructure.repositories.sqlrepository import ProductOrmModel


tz = timezone("UTC")


class DiscountOrmModelStub(Factory):
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


class VatOrmModelStub(Factory):
    class Meta:
        model = VatOrmModel

    id: bytes = Faker("uuid4")
    rate: Decimal = Faker("pyfloat", right_digits=2, min_value=0, max_value=1)
    name: str = Faker("pystr", min_chars=2, max_chars=20)


class TopLevelCategoryOrmModelStub(Factory):
    class Meta:
        model = TopLevelCategoryOrmModel

    id: UUID = Faker("uuid4")
    name: str = Faker("pystr", min_chars=2, max_chars=50)
    description: str = Faker("pystr", min_chars=1, max_chars=3000)


class MidLevelCategoryOrmModelStub(Factory):
    class Meta:
        model = MidLevelCategoryOrmModel

    id: UUID = Faker("uuid4")
    name: str = Faker("pystr", min_chars=2, max_chars=50)
    description: str = Faker("pystr", min_chars=1, max_chars=300)
    parent_id: UUID = Faker("uuid4")
    parent = SubFactory(TopLevelCategoryOrmModelStub)


class TerminalCategoryOrmModelStub(Factory):
    class Meta:
        model = TerminalCategoryOrmModel

    id: UUID = Faker("uuid4")
    name: str = Faker("pystr", min_chars=2, max_chars=50)
    description: str = Faker("pystr", min_chars=1, max_chars=300)
    parent_id: UUID = Faker("uuid4")
    parent = SubFactory(MidLevelCategoryOrmModelStub)


class ProductReviewOrmModelStub(Factory):
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


def generate_dummy_logo_url(o):
    if o.name is None:
        return None
    parse_table = {" ": "-", ",": ""}
    name = o.name.lower()
    for old, new in parse_table.items():
        name = name.replace(old, new)
    return f"https://www.{name}.com/logo.png"


class ProductVendorOrmModelStub(Factory):
    class Meta:
        model = ProductVendorOrmModel

    id: UUID = Faker("uuid4")
    name: str = Faker("company")
    description: str = Faker("catch_phrase")
    logo_url = LazyAttribute(generate_dummy_logo_url)


class ProductOrmModelStub(Factory):
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


class LoadedProductOrmModelStub(ProductOrmModelStub):
    vat = LazyAttribute(lambda o: VatOrmModelStub(id=o.vat_id))
    discount = LazyAttribute(
        lambda o: DiscountOrmModelStub(id=o.discount_id)
        if o.discount_id is not None
        else None
    )
    category = LazyAttribute(lambda o: TerminalCategoryOrmModelStub(id=o.category_id))
    vendor = LazyAttribute(lambda o: ProductVendorOrmModelStub(id=o.vendor_id))
    reviews = LazyAttribute(
        lambda o: ProductReviewOrmModelStub.build_batch(3, product_id=o.id)
    )
