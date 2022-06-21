from uuid import UUID
from uuid import uuid4
from uuid import uuid1
from decimal import Decimal

import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from factory import Factory


from .conftest import ProductFactory, TerminalCategoryOrmModelFactory
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


def test_infra_sqlrepo_repository_get_product_wrong_id_type(
    sqlrepo: SQLProductRepository,
):
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


def _persist_new_object_and_return_its_id(
    factory: Factory, session: Session, **kwargs
) -> UUID:
    obj = factory(**kwargs)
    obj_id = obj.id
    with session as s:
        s.add(obj)
        s.commit()
    return UUID(bytes=obj_id)


def test_infra_sqlrepo_repository_get_product_without_its_reviews(
    sqlrepo: SQLProductRepository,
):
    product_id = _persist_new_object_and_return_its_id(
        LoadedProductOrmModelFactory, sqlrepo._session
    )

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
    product_id = _persist_new_object_and_return_its_id(
        LoadedProductOrmModelFactory, sqlrepo._session
    )

    fetched_product = sqlrepo.get_product(product_id, with_reviews=True)
    for review in fetched_product.get_client_reviews():
        assert isinstance(review, ProductReview)


def test_infra_sqlrepo_repository_get_product_that_has_no_reviews(
    sqlrepo: SQLProductRepository,
):
    product_id = _persist_new_object_and_return_its_id(
        LoadedProductOrmModelFactory, sqlrepo._session, reviews=[]
    )

    fetched_product = sqlrepo.get_product(product_id, with_reviews=True)
    assert fetched_product.get_client_reviews() == []


def test_infra_sqlrepo_get_products_wrong_id_type(sqlrepo: SQLProductRepository):
    with pytest.raises(TypeError):
        sqlrepo.get_products(category_id=1)


def test_infra_sqlrepo_get_products_non_existent_products(
    sqlrepo: SQLProductRepository,
):
    category_id = _persist_new_object_and_return_its_id(
        TerminalCategoryOrmModelFactory, sqlrepo._session
    )
    products = sqlrepo.get_products(category_id=category_id)
    assert len(products) == 0


def _persist_new_products_and_return_category_id(no: int, session: Session, **kwargs):
    category = TerminalCategoryOrmModelFactory()
    category_id = category.id
    new_products = LoadedProductOrmModelFactory.build_batch(
        no, category_id=category_id, category=category, **kwargs
    )
    with session as s:
        s.add_all([category, *new_products])
        s.commit()
    return UUID(bytes=category_id)


def test_infra_sqlrepo_get_products_existent_products(sqlrepo: SQLProductRepository):
    category_id = _persist_new_products_and_return_category_id(3, sqlrepo._session)

    products = sqlrepo.get_products(category_id=category_id)
    for product in products:
        assert isinstance(product, Product)


def test_infra_sqlrepo_get_products_price_min_wrong_type(sqlrepo: SQLProductRepository):
    with pytest.raises(TypeError):
        sqlrepo.get_products(uuid4(), price_min="a")


def test_infra_sqlrepo_get_products_price_max_wrong_type(sqlrepo: SQLProductRepository):
    with pytest.raises(TypeError):
        sqlrepo.get_products(uuid4(), price_max="a")


def test_infra_sqlrepo_get_products_out_of_bounds_price_ranges_are_ignored(
    sqlrepo: SQLProductRepository,
):
    no_products = 5
    category_id = _persist_new_products_and_return_category_id(
        no_products, sqlrepo._session
    )
    products = sqlrepo.get_products(
        category_id, price_min=Decimal("-1"), price_max=Decimal("1_000_001")
    )
    assert len(products) == no_products


def test_infra_sqlrepo_get_products_price_min_restricts_no_of_products(
    sqlrepo: SQLProductRepository,
):
    no_products = 5
    category_id = _persist_new_products_and_return_category_id(
        no_products, sqlrepo._session, base_price=Decimal("99")
    )
    products = sqlrepo.get_products(category_id, price_min=Decimal("100"))
    assert len(products) == 0


def test_infra_sqlrepo_get_products_price_max_restricts_no_of_products(
    sqlrepo: SQLProductRepository,
):
    no_products = 5
    category_id = _persist_new_products_and_return_category_id(
        no_products, sqlrepo._session, base_price=Decimal("100")
    )
    products = sqlrepo.get_products(category_id, price_max=Decimal("99"))
    assert len(products) == 0


def test_infra_sqlrepo_get_products_rating_min_wrong_type(
    sqlrepo: SQLProductRepository,
):
    with pytest.raises(TypeError):
        sqlrepo.get_products(uuid4(), rating_min="a")


def test_infra_sqlrepo_get_products_rate_max_wrong_type(sqlrepo: SQLProductRepository):
    with pytest.raises(TypeError):
        sqlrepo.get_products(uuid4(), rating_max="a")


def test_infra_sqlrepo_get_products_rating_min_restricts_no_of_products(
    sqlrepo: SQLProductRepository,
):
    no_products = 5
    category_id = _persist_new_products_and_return_category_id(
        no_products, sqlrepo._session, rating=Decimal("3")
    )
    products = sqlrepo.get_products(category_id, rating_min=Decimal("4"))
    assert len(products) == 0


def test_infra_sqlrepo_get_products_rating_max_restricts_results(
    sqlrepo: SQLProductRepository,
):
    no_products = 5
    category_id = _persist_new_products_and_return_category_id(
        no_products, sqlrepo._session, rating=Decimal("4")
    )
    products = sqlrepo.get_products(category_id, rating_max=Decimal("3"))
    assert len(products) == 0


def test_infra_sqlrepo_get_products_with_discounts_only_param_restricts_results(
    sqlrepo: SQLProductRepository,
):
    no_products = 5
    category = TerminalCategoryOrmModelFactory()
    category_id = category.id
    products_with_no_discount = LoadedProductOrmModelFactory.build_batch(
        no_products, category_id=category_id, category=category, discount_id=None
    )
    product_with_discount = LoadedProductOrmModelFactory(
        category_id=category_id, category=category
    )
    with sqlrepo._session as s:
        s.add_all([category, product_with_discount, *products_with_no_discount])
        s.commit()

    products = sqlrepo.get_products(UUID(bytes=category_id), with_discounts_only=True)
    assert len(products) == 1
