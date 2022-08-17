import json
from uuid import uuid4
from uuid import uuid1
from uuid import UUID

import pytest

from .conftest import LoadedProductOrmModelStub, TopLevelCategoryOrmModelStub
from diystore.infrastructure.repositories.sqlrepository import SQLProductRepository
from diystore.infrastructure.controllers.web import ProductController
from diystore.infrastructure.controllers.web.exceptions import InvalidProductID
from diystore.infrastructure.controllers.web.exceptions import InvalidCategoryID
from diystore.infrastructure.controllers.web.exceptions import ProductNotFound
from diystore.infrastructure.controllers.web.exceptions import TopCategoryNotFound
from diystore.infrastructure.controllers.web.exceptions import InvalidQueryArgument


def test_infra_product_controller_get_one_invalid_id_value(
    product_controller: ProductController,
):
    with pytest.raises(InvalidProductID):
        product_controller.get_one(product_id=22900628769549271261936325394331419755)


def test_infra_product_controller_get_one_non_existing_object(
    product_controller: ProductController,
):
    with pytest.raises(ProductNotFound):
        product_controller.get_one(product_id=uuid4().hex)


def test_infra_product_controller_get_one_existing_object(
    product_controller: ProductController, sqlrepo: SQLProductRepository
):
    product_controller._repo = sqlrepo
    products_orm = LoadedProductOrmModelStub.build_batch(3)
    valid_id = UUID(bytes=products_orm[0].id).hex
    name, description = products_orm[0].name, products_orm[0].description
    with sqlrepo._session as s:
        s.add_all(products_orm)
        s.commit()

    representation = product_controller.get_one(product_id=valid_id)
    assert valid_id in representation
    assert name in representation
    assert description in representation


def test_infra_product_controller_get_many_wrong_category_id(
    product_controller: ProductController,
):
    with pytest.raises(InvalidQueryArgument):
        product_controller.get_many(category_id=2)


def test_infra_product_controller_get_many_inexistent_category_id(
    product_controller: ProductController,
):
    _id = uuid1()
    products = product_controller.get_many(category_id=_id)
    assert products == json.dumps({"products": []})


def test_infra_product_controller_get_many_price_min_wrong_type(
    product_controller: ProductController,
):
    _id = uuid4()
    with pytest.raises(InvalidQueryArgument) as e:
        product_controller.get_many(category_id=_id, price_min="a")
    assert e.match("price_min")


def test_infra_product_controller_get_many_price_max_wrong_type(
    product_controller: ProductController,
):
    _id = uuid4()
    with pytest.raises(InvalidQueryArgument) as e:
        product_controller.get_many(category_id=_id, price_max="a")
    assert e.match("price_max")


def test_infra_product_controller_get_many_rating_min_wrong_type(
    product_controller: ProductController,
):
    _id = uuid4()
    with pytest.raises(InvalidQueryArgument) as e:
        product_controller.get_many(category_id=_id, rating_min="a")
    assert e.match("rating_min")


def test_infra_product_controller_get_many_rating_max_wrong_type(
    product_controller: ProductController,
):
    _id = uuid4()
    with pytest.raises(InvalidQueryArgument) as e:
        product_controller.get_many(category_id=_id, rating_max="a")
    assert e.match("rating_max")


def test_infra_product_controller_get_many_price_min_wrong_value(
    product_controller: ProductController,
):
    _id = uuid4()
    with pytest.raises(InvalidQueryArgument):
        product_controller.get_many(category_id=_id, price_min=-1)


def test_infra_product_controller_get_many_price_max_wrong_value(
    product_controller: ProductController,
):
    _id = uuid4()
    with pytest.raises(InvalidQueryArgument):
        product_controller.get_many(category_id=_id, price_max=1000001)


def test_infra_product_controller_get_many_rating_min_wrong_value(
    product_controller: ProductController,
):
    _id = uuid4()
    with pytest.raises(InvalidQueryArgument):
        product_controller.get_many(category_id=_id, rating_min=-1)


def test_infra_product_controller_get_many_rating_max_wrong_value(
    product_controller: ProductController,
):
    _id = uuid4()
    with pytest.raises(InvalidQueryArgument):
        product_controller.get_many(category_id=_id, rating_max=6)


def test_infra_product_controller_get_many_wrong_ordering_property(
    product_controller: ProductController,
):
    _id = uuid4()
    with pytest.raises(InvalidQueryArgument):
        product_controller.get_many(category_id=_id, order_by="name")


def test_infra_product_controller_get_many_wrong_ordering_type(
    product_controller: ProductController,
):
    _id = uuid4()
    with pytest.raises(InvalidQueryArgument):
        product_controller.get_many(category_id=_id, order_type="flat")


@pytest.mark.parametrize("_id", (2, "abc", (1, 2, 3)))
def test_infra_product_controller_get_top_category_invalid_id(
    _id, product_controller: ProductController
):
    # GIVEN an invalid category id
    # WHEN a top category is searched using such id
    # THEN an error is raised
    with pytest.raises(InvalidCategoryID):
        product_controller.get_top_category(category_id=_id)


def test_infra_product_controller_get_top_category_non_existent_category(
    product_controller: ProductController,
):
    # GIVEN an id not associated with a top category
    _id = uuid1()

    # WHEN a top category is searched using such id
    # THEN an error is raised
    with pytest.raises(TopCategoryNotFound):
        product_controller.get_top_category(category_id=_id)


def test_infra_product_controller_get_top_category_existent_category(
    product_controller: ProductController, sqlrepo: SQLProductRepository
):
    # GIVEN an id associated with an existent top category
    category = TopLevelCategoryOrmModelStub()
    _id = UUID(bytes=category.id).hex
    name, description = category.name, category.description
    product_controller._repo = sqlrepo
    with sqlrepo._session as s:
        s.add(category)
        s.commit()

    # WHEN a top category is searched using such id
    representation = product_controller.get_top_category(category_id=_id)

    # THEN a correct representation of the category is returned
    assert _id in representation
    assert name in representation
    assert description in representation


def test_infra_product_controller_get_top_categories_no_categories(
    product_controller: ProductController,
):
    # GIVEN a repository with no top categories
    # WHEN all the top categories are requested
    representation = product_controller.get_top_categories()

    # THEN a representation of no top categories is returned
    assert representation == '{"categories": []}'


def test_infra_product_controller_get_top_categories_existing_categories(
    product_controller: ProductController,
):
    # GIVEN a repository with existing top categories
    categories = TopLevelCategoryOrmModelStub.build_batch(3)
    entity_categories = tuple(c.to_domain_entity() for c in categories)
    repo = product_controller._repo
    with repo._session as s:
        s.add_all(categories)
        s.commit()

    # WHEN all the top categories are requested
    representation = product_controller.get_top_categories()

    # THEN a representation containing all top categories is returned
    for category in entity_categories:
        assert category.id.hex in representation
        assert category.name in representation
        assert category.description in representation
