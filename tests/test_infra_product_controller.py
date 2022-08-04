import json
from uuid import uuid4
from uuid import uuid1
from uuid import UUID

import pytest

from .conftest import LoadedProductOrmModelFactory
from diystore.infrastructure.repositories.sqlrepository import SQLProductRepository
from diystore.infrastructure.controllers.web.exceptions import InvalidProductID
from diystore.infrastructure.controllers.web.exceptions import ProductNotFound
from diystore.infrastructure.controllers.web.exceptions import InvalidQueryArgument


def test_infra_product_controller_get_one_invalid_id_value(product_controller):
    with pytest.raises(InvalidProductID):
        product_controller.get_one(22900628769549271261936325394331419755)


def test_infra_product_controller_get_one_non_existing_object(product_controller):
    with pytest.raises(ProductNotFound):
        product_controller.get_one(uuid4().hex)


def test_infra_product_controller_get_one_existing_object(
    product_controller, sqlrepo: SQLProductRepository
):
    product_controller._repo = sqlrepo
    products_orm = LoadedProductOrmModelFactory.build_batch(3)
    valid_id = UUID(bytes=products_orm[0].id).hex
    with sqlrepo._session as s:
        s.add_all(products_orm)
        s.commit()

    representation = product_controller.get_one(valid_id)
    assert representation is not None


def test_infra_product_controller_get_many_wrong_category_id(product_controller):
    with pytest.raises(InvalidQueryArgument):
        product_controller.get_many(category_id=2)


def test_infra_product_controller_get_many_inexistent_category_id(product_controller):
    _id = uuid1()
    products = product_controller.get_many(category_id=_id)
    assert products == json.dumps({"products": []})


def test_infra_product_controller_get_many_price_min_wrong_type(product_controller):
    _id = uuid4()
    with pytest.raises(InvalidQueryArgument) as e:
        product_controller.get_many(category_id=_id, price_min="a")
    assert e.match("price_min")


def test_infra_product_controller_get_many_price_max_wrong_type(product_controller):
    _id = uuid4()
    with pytest.raises(InvalidQueryArgument) as e:
        product_controller.get_many(category_id=_id, price_max="a")
    assert e.match("price_max")


def test_infra_product_controller_get_many_rating_min_wrong_type(product_controller):
    _id = uuid4()
    with pytest.raises(InvalidQueryArgument) as e:
        product_controller.get_many(category_id=_id, rating_min="a")
    assert e.match("rating_min")


def test_infra_product_controller_get_many_rating_max_wrong_type(product_controller):
    _id = uuid4()
    with pytest.raises(InvalidQueryArgument) as e:
        product_controller.get_many(category_id=_id, rating_max="a")
    assert e.match("rating_max")


def test_infra_product_controller_get_many_price_min_wrong_value(product_controller):
    _id = uuid4()
    with pytest.raises(InvalidQueryArgument):
        product_controller.get_many(category_id=_id, price_min=-1)


def test_infra_product_controller_get_many_price_max_wrong_value(product_controller):
    _id = uuid4()
    with pytest.raises(InvalidQueryArgument):
        product_controller.get_many(category_id=_id, price_max=1000001)


def test_infra_product_controller_get_many_rating_min_wrong_value(product_controller):
    _id = uuid4()
    with pytest.raises(InvalidQueryArgument):
        product_controller.get_many(category_id=_id, rating_min=-1)


def test_infra_product_controller_get_many_rating_max_wrong_value(product_controller):
    _id = uuid4()
    with pytest.raises(InvalidQueryArgument):
        product_controller.get_many(category_id=_id, rating_max=6)


def test_infra_product_controller_get_many_wrong_ordering_property(product_controller):
    _id = uuid4()
    with pytest.raises(InvalidQueryArgument):
        product_controller.get_many(category_id=_id, order_by="name")


def test_infra_product_controller_get_many_wrong_ordering_type(product_controller):
    _id = uuid4()
    with pytest.raises(InvalidQueryArgument):
        product_controller.get_many(category_id=_id, order_type="flat")
