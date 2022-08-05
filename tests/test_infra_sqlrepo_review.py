from uuid import UUID

import pytest
from sqlalchemy.orm import Session

from .conftest import tz
from .conftest import ProductReviewStub
from .conftest import ProductReviewOrmModelStub
from diystore.domain.entities.product import ProductReview
from diystore.infrastructure.repositories.sqlrepository import ProductReviewOrmModel


def test_infra_sqlrepo_to_domain_entity(orm_session: Session):
    review_orm = ProductReviewOrmModelStub()
    orm_session.add(review_orm)
    orm_session.commit()
    review_orm = orm_session.get(ProductReviewOrmModel, review_orm.id)
    review_entity = review_orm.to_domain_entity()
    assert isinstance(review_entity, ProductReview)
    assert review_entity.id == UUID(bytes=review_orm.id)
    assert review_entity.product_id == UUID(bytes=review_orm.product_id)
    assert review_entity.client_id == UUID(bytes=review_orm.client_id)
    assert review_entity.creation_date == tz.convert(review_orm.creation_date)
    assert review_entity.feedback == review_orm.feedback


def test_infra_sqlrepo_from_domain_entity_wrong_type():
    with pytest.raises(TypeError):
        ProductReviewOrmModelStub().from_domain_entity(1)


def test_infra_sqlrepo_from_domain_entity_correct_type(orm_session: Session):
    review_entity = ProductReviewStub()
    review_orm = ProductReviewOrmModel.from_domain_entity(review_entity)
    assert isinstance(review_orm, ProductReviewOrmModel)

    orm_session.add(review_orm)
    orm_session.commit()
    review_orm = orm_session.get(ProductReviewOrmModel, review_orm.id)

    assert review_orm.id == review_entity.id.bytes
    assert review_orm.product_id == review_entity.product_id.bytes
    assert review_orm.client_id == review_entity.client_id.bytes
    assert review_orm.rating == review_entity.rating
    assert review_orm.creation_date == review_entity.creation_date.naive()
    assert review_orm.feedback == review_entity.feedback
