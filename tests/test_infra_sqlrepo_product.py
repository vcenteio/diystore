from uuid import UUID
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from .conftest import tz
from .conftest import VatOrmModelFactory
from .conftest import ProductFactory
from .conftest import ProductOrmModelFactory
from .conftest import DiscountOrmModelFactory
from diystore.domain.entities.product import Product
from diystore.domain.entities.product import VAT
from diystore.domain.entities.product import Discount
from diystore.domain.entities.product import ProductPrice
from diystore.domain.entities.product import TerminalLevelProductCategory
from diystore.domain.entities.product import ProductVendor
from diystore.domain.entities.product import ProductDimensions
from diystore.domain.entities.product import ProductRating
from diystore.domain.entities.product import ProductPhotoUrl
from diystore.infrastructure.repositories.sqlrepository import ProductOrmModel


def test_infra_sqlrepo_product_vat_relationship_non_existing_vat(orm_session: Session):
    product_orm = ProductOrmModelFactory(vat_id=uuid4())
    orm_session.add(product_orm)
    orm_session.commit()
    product_orm = orm_session.get(ProductOrmModel, product_orm.id)
    assert product_orm.vat is None


def test_infra_sqlrepo_product_vat_relationship_existing_vat(orm_session: Session):
    vat_orm = VatOrmModelFactory()
    product_orm = ProductOrmModelFactory(vat_id=vat_orm.id)
    orm_session.add_all((vat_orm, product_orm))
    orm_session.commit()
    product_orm = orm_session.get(ProductOrmModel, product_orm.id)
    assert product_orm.vat == vat_orm


def test_infra_sqlrepo_product_discount_relationship_non_existing_discount(
    orm_session: Session,
):
    product_orm = ProductOrmModelFactory(discount_id=uuid4())
    orm_session.add(product_orm)
    orm_session.commit()
    product_orm = orm_session.get(ProductOrmModel, product_orm.id)
    assert product_orm.discount is None


def test_infra_sqlrepo_product_discount_relationship_existing_discount(
    orm_session: Session,
):
    discount_orm = DiscountOrmModelFactory()
    product_orm = ProductOrmModelFactory(discount_id=discount_orm.id)
    orm_session.add_all((discount_orm, product_orm))
    orm_session.commit()
    product_orm = orm_session.get(ProductOrmModel, product_orm.id)
    assert product_orm.discount == discount_orm
