from uuid import UUID
from decimal import Decimal

import pytest
from sqlalchemy.orm import Session

from .conftest import tz
from .conftest import DiscountOrmModel
from .conftest import DiscountOrmModelStub
from .conftest import DiscountStub
from diystore.domain.entities.product import Discount


def test_infra_sqlrepo_discount_to_domain_entity(orm_session: Session):
    discount_orm = DiscountOrmModelStub()

    orm_session.add(discount_orm)
    orm_session.commit()
    discount_orm = orm_session.get(DiscountOrmModel, discount_orm.id)

    discount_entity = discount_orm.to_domain_entity()
    assert isinstance(discount_entity, Discount)
    assert discount_entity.id == UUID(bytes=discount_orm.id)
    assert discount_entity.name == discount_orm.name
    assert discount_entity.rate == Decimal(str(discount_orm.rate))
    assert discount_entity.creation_date == tz.convert(discount_orm.creation_date)
    assert discount_entity.creation_date.tzinfo == tz
    assert discount_entity.expiry_date == tz.convert(discount_orm.expiry_date)
    assert discount_entity.expiry_date.tzinfo == tz


def test_infra_sqlrepo_discount_from_domain_entity_wrong_type():
    with pytest.raises(TypeError):
        DiscountOrmModel.from_domain_entity(1)


def test_infra_sqlrepo_discount_from_domain_entity_correct_type(orm_session: Session):
    discount_entity = DiscountStub()
    discount_orm = DiscountOrmModel.from_domain_entity(discount_entity)
    assert isinstance(discount_orm, DiscountOrmModel)

    orm_session.add(discount_orm)
    orm_session.commit()
    discount_orm = orm_session.get(DiscountOrmModel, discount_orm.id)

    assert discount_orm.id == discount_entity.id.bytes
    assert discount_orm.name == discount_entity.name
    assert discount_orm.rate == discount_entity.rate
    assert tz.convert(discount_orm.creation_date) == discount_entity.creation_date
    assert tz.convert(discount_orm.expiry_date) == discount_entity.expiry_date
