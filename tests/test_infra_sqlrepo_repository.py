from uuid import UUID
from uuid import uuid4
from uuid import uuid1

import pytest
from sqlalchemy.exc import OperationalError


from .conftest import ProductFactory
from .conftest import ProductOrmModelFactory
from .conftest import LoadedProductOrmModelFactory
from diystore.domain.entities.product import Product
from diystore.domain.entities.product import TerminalLevelProductCategory
from diystore.domain.entities.product import MidLevelProductCategory
from diystore.domain.entities.product import TopLevelProductCategory
from diystore.domain.entities.product import ProductVendor
from diystore.domain.entities.product import ProductReview
from diystore.infrastructure.repositories.sqlrepository import SQLProductRepository


@pytest.mark.parametrize("wrong_url", (1, [], b"a"))
def test_infra_sqlrepo_repository_init_wrong_url_type(wrong_url):
    with pytest.raises(TypeError):
        SQLProductRepository(wrong_url)


@pytest.mark.parametrize("wrong_url", ("abc", "123", "\/\/", ":", "/"))
def test_infra_sqlrepo_repository_init_malformed_url(wrong_url):
    with pytest.raises(ValueError):
        SQLProductRepository(wrong_url)


def test_infra_sqlrepo_repository_init_unreacheable_database_server():
    with pytest.raises(OperationalError):
        SQLProductRepository("postgresql://user:pass@localhost:1234/dummydb")


def test_infra_sqlrepo_repository_get_product_wrong_id_type(sqlrepo: SQLProductRepository):
    with pytest.raises(TypeError):
        sqlrepo.get_product(1)


def test_infra_sqlrepo_repository_get_product_inexistent_product(
    sqlrepo: SQLProductRepository,
):
    products = ProductOrmModelFactory.build_batch(3)
    with sqlrepo._session as s:
        s.add_all(products)
        s.commit()
        inexistent_id = uuid1()
        product = sqlrepo.get_product(inexistent_id)
        assert product is None


def test_infra_sqlrepo_repository_get_product_without_its_reviews(
    sqlrepo: SQLProductRepository,
):
    product = LoadedProductOrmModelFactory()
    product_id = UUID(bytes=product.id)
    with sqlrepo._session as s:
        s.add(product)
        s.commit()

    fetched_product = sqlrepo.get_product(product_id)
    assert isinstance(fetched_product, Product)
    assert fetched_product.id == product_id
    assert fetched_product.get_vat() is not None
    assert fetched_product.get_discount() is not None
    assert isinstance(fetched_product.category, TerminalLevelProductCategory)
    assert isinstance(fetched_product.get_parent_category(), MidLevelProductCategory)
    assert isinstance(fetched_product.get_top_category(), TopLevelProductCategory)
    assert isinstance(fetched_product.vendor, ProductVendor)
    assert len(fetched_product.reviews) == 0


def test_infra_sqlrepo_repository_get_product_with_its_reviews(
    sqlrepo: SQLProductRepository,
):
    product = LoadedProductOrmModelFactory()
    product_id = UUID(bytes=product.id)
    with sqlrepo._session as s:
        s.add(product)
        s.commit()

    fetched_product = sqlrepo.get_product(product_id, with_reviews=True)
    for review in fetched_product.get_client_reviews():
        assert isinstance(review, ProductReview)


def test_infra_sqlrepo_repository_get_product_that_has_no_reviews(
    sqlrepo: SQLProductRepository,
):
    product = LoadedProductOrmModelFactory(reviews=[])
    product_id = UUID(bytes=product.id)
    with sqlrepo._session as s:
        s.add(product)
        s.commit()

    fetched_product = sqlrepo.get_product(product_id, with_reviews=True)
    assert fetched_product.get_client_reviews() == []
