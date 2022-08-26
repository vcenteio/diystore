from uuid import UUID

import pytest
from sqlalchemy.orm import Session

from diystore.domain.entities.product import ProductVendor
from diystore.domain.entities.product.stubs import ProductVendorStub
from diystore.infrastructure.repositories.sqlrepository import ProductVendorOrmModel
from diystore.infrastructure.repositories.sqlrepository.models.stubs import ProductVendorOrmModelStub


def test_infra_sqlrepo_vendor_to_domain_entity(orm_session: Session):
    vendor_orm = ProductVendorOrmModelStub()
    orm_session.add(vendor_orm)
    orm_session.commit()
    vendor_orm = orm_session.get(ProductVendorOrmModel, vendor_orm.id)

    vendor_entity = vendor_orm.to_domain_entity()
    assert isinstance(vendor_entity, ProductVendor)
    assert vendor_entity.id == UUID(bytes=vendor_orm.id)
    assert vendor_entity.name == vendor_orm.name
    assert vendor_entity.description == vendor_orm.description
    assert vendor_entity.logo_url == vendor_orm.logo_url


def test_infra_sqlrepo_vendor_from_domain_entity_wrong_type():
    with pytest.raises(TypeError):
        ProductVendorOrmModelStub().from_domain_entity(1)


def test_infra_sqlrepo_vendor_from_domain_entity_correct_type(orm_session: Session):
    vendor_entity = ProductVendorStub()
    vendor_orm = ProductVendorOrmModel.from_domain_entity(vendor_entity)
    assert isinstance(vendor_orm, ProductVendorOrmModel)

    orm_session.add(vendor_orm)
    orm_session.commit()
    vendor_orm = orm_session.get(ProductVendorOrmModel, vendor_orm.id)

    assert vendor_orm.id == vendor_entity.id.bytes
    assert vendor_orm.name == vendor_entity.name
    assert vendor_orm.description == vendor_entity.description
    assert vendor_orm.logo_url == vendor_entity.logo_url
