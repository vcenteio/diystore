from uuid import UUID
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from .conftest import ProductReviewFactory, ProductReviewOrmModelFactory
from .conftest import ProductVendorOrmModelFactory
from .conftest import VatOrmModelFactory
from .conftest import ProductFactory
from .conftest import DiscountOrmModelFactory
from .conftest import TerminalCategoryOrmModelFactory
from .conftest import MidLevelCategoryOrmModelFactory
from .conftest import TopLevelCategoryOrmModelFactory
from .conftest import ProductOrmModelFactory
from .conftest import LoadedProductOrmModelFactory
from diystore.domain.entities.product import Product
from diystore.domain.entities.product import VAT
from diystore.domain.entities.product import Discount
from diystore.domain.entities.product import ProductPrice
from diystore.domain.entities.product import TerminalLevelProductCategory
from diystore.domain.entities.product import ProductVendor
from diystore.domain.entities.product import ProductDimensions
from diystore.domain.entities.product import ProductRating
from diystore.domain.entities.product import ProductPhotoUrl
from diystore.domain.entities.product import EAN13
from diystore.infrastructure.repositories.sqlrepository import ProductOrmModel
from diystore.infrastructure.repositories.sqlrepository import ProductVendorOrmModel
from diystore.infrastructure.repositories.sqlrepository import DiscountOrmModel
from diystore.infrastructure.repositories.sqlrepository import TerminalCategoryOrmModel
from diystore.infrastructure.repositories.sqlrepository import ProductVendorOrmModel
from diystore.infrastructure.repositories.sqlrepository import ProductReviewOrmModel
from diystore.infrastructure.repositories.sqlrepository import VatOrmModel
from diystore.infrastructure.repositories.sqlrepository.exceptions import (
    OrmEntityNotFullyLoaded,
)


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


def test_infra_sqlrepo_product_category_relationship(orm_session: Session):
    category_orm = TerminalCategoryOrmModelFactory()
    product_orm = ProductOrmModelFactory(category_id=category_orm.id)
    orm_session.add_all((category_orm, product_orm))
    orm_session.commit()
    product_orm = orm_session.get(ProductOrmModel, product_orm.id)
    assert product_orm.category == category_orm
    assert product_orm.category.parent == category_orm.parent
    assert product_orm.category.parent.parent == category_orm.parent.parent
    assert product_orm in product_orm.category.products


def test_infra_sqlrepo_product_vendor_relationship(orm_session: Session):
    vendor_orm = ProductVendorOrmModelFactory()
    products = ProductOrmModelFactory.build_batch(10, vendor_id=vendor_orm.id)
    orm_session.add_all((vendor_orm, *products))
    orm_session.commit()
    vendor_orm = orm_session.get(ProductVendorOrmModel, vendor_orm.id)
    assert vendor_orm.products == products
    product = orm_session.get(ProductOrmModel, products[0].id)
    assert product.vendor_id == vendor_orm.id


def test_infra_sqlrepo_product_review_relationship(orm_session: Session):
    product_orm = ProductOrmModelFactory()
    reviews = ProductReviewOrmModelFactory.build_batch(10, product_id=product_orm.id)
    orm_session.add_all((product_orm, *reviews))
    orm_session.commit()
    product_orm = orm_session.get(ProductOrmModel, product_orm.id)
    assert product_orm.reviews == reviews
    for review in product_orm.reviews:
        assert review.product == product_orm


def test_infra_sqlrepo_product_to_domain_entity_object_not_fully_loaded():
    product_orm = ProductOrmModelFactory(vat=None)
    with pytest.raises(OrmEntityNotFullyLoaded):
        product_orm.to_domain_entity()


def test_infra_sqlrepo_product_to_domain_entity(orm_session: Session):
    product_orm = LoadedProductOrmModelFactory()
    orm_session.add(product_orm)
    orm_session.commit()

    product_orm = (
        orm_session.query(ProductOrmModel)
        .join(VatOrmModel)
        .join(DiscountOrmModel)
        .join(TerminalCategoryOrmModel)
        .join(ProductVendorOrmModel)
        .join(ProductReviewOrmModel)
        .filter(ProductOrmModel.id == product_orm.id)
        .one()
    )
    product_entity = product_orm.to_domain_entity()

    assert isinstance(product_entity, Product)
    validated_entity = Product(**product_entity.dict())
    assert product_entity.id == validated_entity.id
    assert product_entity.ean == validated_entity.ean
    assert product_entity.name == validated_entity.name
    assert product_entity.price == validated_entity.price
    assert product_entity.quantity == validated_entity.quantity
    assert product_entity.creation_date == validated_entity.creation_date
    assert product_entity.dimensions == validated_entity.dimensions
    assert product_entity.color == validated_entity.color
    assert product_entity.material == validated_entity.material
    assert product_entity.country_of_origin == validated_entity.country_of_origin
    assert product_entity.warranty == validated_entity.warranty
    assert product_entity.category == validated_entity.category
    assert product_entity.rating == validated_entity.rating
    assert product_entity.reviews == validated_entity.reviews == {}
    assert product_entity.photo_url == validated_entity.photo_url
    assert product_entity.vendor == validated_entity.vendor


def test_infra_sqlrepo_product_from_domain_entity_wrong_type():
    with pytest.raises(TypeError):
        ProductOrmModel.from_domain_entity(1)


def test_infra_sqlrepo_product_from_domain_entity_correct_type(orm_session: Session):
    product: Product = ProductFactory(reviews=ProductReviewFactory.build_batch(3))
    product_orm = ProductOrmModel.from_domain_entity(product)

    orm_session.add(product_orm)
    orm_session.commit()

    product_orm: ProductOrmModel = orm_session.get(ProductOrmModel, product_orm.id)

    assert product_orm.id == product.get_id_in_bytes_format()
    assert product_orm.ean == product.ean
    assert product_orm.name == product.name
    assert product_orm.description == product.description
    assert product_orm.base_price == product.get_base_price()
    assert product_orm.vat_id == product.get_vat_id_in_bytes_format()
    assert product_orm.discount_id == product.get_discount_id_in_bytes_format()
    assert product_orm.quantity == product.quantity
    assert product_orm.creation_date == product.creation_date.naive()
    assert product_orm.height == product.get_height()
    assert product_orm.width == product.get_width()
    assert product_orm.length == product.get_length()
    assert product_orm.color == product.color
    assert product_orm.material == product.material
    assert product_orm.country_of_origin == product.country_of_origin
    assert product_orm.warranty == product.warranty
    assert product_orm.category_id == product.get_category_id_in_bytes_format()
    assert product_orm.rating == product.rating
    assert product_orm.thumbnail_photo_url == product.get_thumbnail_photo_url()
    assert product_orm.medium_size_photo_url == product.get_medium_size_photo_url()
    assert product_orm.large_size_photo_url == product.get_large_size_photo_url()
    assert product_orm.vendor_id == product.get_vendor_id_in_bytes_format()
    assert isinstance(product_orm.vat, VatOrmModel)
    assert isinstance(product_orm.discount, DiscountOrmModel)
    assert isinstance(product_orm.category, TerminalCategoryOrmModel)
    assert isinstance(product_orm.vendor, ProductVendorOrmModel)
    for rev in product_orm.reviews:
        assert isinstance(rev, ProductReviewOrmModel)
