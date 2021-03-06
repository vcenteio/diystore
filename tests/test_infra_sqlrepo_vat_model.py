from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from .conftest import VATFactory
from .conftest import VatOrmModelFactory
from diystore.infrastructure.repositories.sqlrepository import VatOrmModel
from diystore.infrastructure.repositories.sqlrepository.helpers import validate_id
from diystore.domain.entities.product import VAT


def test_infra_sqlrepo_vat_id_is_necessary():
    with pytest.raises(TypeError):
        VatOrmModelFactory(id=None)


@pytest.mark.parametrize("wrong_id", ([1, 2], (1, 2), 1.23))
def test_infra_sqlrepo_vat_id_wrong_type(wrong_id):
    with pytest.raises(TypeError):
        VatOrmModelFactory(id=wrong_id)


def test_infra_sqlrepo_vat_invalid_uuid(invalid_uuid_str):
    with pytest.raises(ValueError):
        VatOrmModelFactory(id=invalid_uuid_str)


@pytest.mark.parametrize(
    "correct_id", ((_id := uuid4()), _id.bytes, _id.hex, _id.int, str(_id))
)
def test_infra_sqlrepo_vat_id_correct_type(correct_id):
    vat = VatOrmModelFactory(id=correct_id)
    assert vat.id == validate_id(correct_id, None)


def test_infra_sqlrepo_vat_to_domain_entity():
    vat_orm: VatOrmModel = VatOrmModelFactory()
    vat_entity = vat_orm.to_domain_entity()
    assert isinstance(vat_entity, VAT)


def test_infra_sqlrepo_vat_from_domain_entity_wrong_type():
    with pytest.raises(TypeError):
        VatOrmModel.from_domain_entity(1)


def test_infra_sqlrepo_vat_from_domain_entity_correct_type(orm_session: Session):
    vat_entity = VATFactory()
    vat_orm = VatOrmModel.from_domain_entity(vat_entity)
    orm_session.add(vat_orm)
    orm_session.commit()
    vat_orm = orm_session.get(VatOrmModel, vat_orm.id)
    assert isinstance(vat_orm, VatOrmModel)
    assert vat_orm.id == vat_entity.id.bytes
    assert vat_orm.name == vat_entity.name
    assert vat_orm.rate == vat_entity.rate
