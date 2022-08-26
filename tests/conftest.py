from decimal import Decimal
from unittest.mock import Mock
from uuid import UUID

import pytest
import pendulum
from pendulum import now
from pendulum.tz import timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session

from diystore.application.usecases.product import ProductRepository
from diystore.infrastructure.main.settings import InfraSettings
from diystore.infrastructure.controllers.web.factories import ProductControllerFactory
from diystore.infrastructure.repositories.sqlrepository import Base
from diystore.infrastructure.repositories.sqlrepository import SQLProductRepository
from diystore.infrastructure.controllers.web import ProductController
from diystore.infrastructure.cache.interfaces import Cache
from diystore.infrastructure.repositories.sqlrepository.models.stubs import TerminalCategoryOrmModelStub
from diystore.infrastructure.repositories.sqlrepository.models.stubs import LoadedProductOrmModelStub
from diystore.domain.entities.product.stubs import ProductStub


tz = timezone("UTC")


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
    return [ProductStub() for _ in range(30)]


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


@pytest.fixture
def sqlrepo():
    return SQLProductRepository(scheme="sqlite", host="/:memory:")


@pytest.fixture(scope="session")
def testenv_infrasettings():
    return InfraSettings(_env_file="test.env")


@pytest.fixture
def mock_product_cache():
    mock_cache = Mock(Cache)
    mock_cache.get.return_value = None
    return mock_cache


@pytest.fixture
def product_controller(sqlrepo, mock_product_cache) -> ProductController:
    return ProductControllerFactory(repo=sqlrepo, cache=mock_product_cache)


def persist_new_products_and_return_category_id(no: int, session: Session, **kwargs):
    category = TerminalCategoryOrmModelStub()
    category_id = category.id
    new_products = LoadedProductOrmModelStub.build_batch(
        no, category_id=category_id, category=category, **kwargs
    )
    with session as s:
        s.add_all([category, *new_products])
        s.commit()
    return UUID(bytes=category_id)
