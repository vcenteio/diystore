from uuid import uuid4
from uuid import UUID

import pytest
from sqlalchemy.orm import Session

from .conftest import ProductOrmModelFactory
from .conftest import LoadedProductOrmModelFactory
from diystore.infrastructure.repositories.sqlrepository import SQLProductRepository
from diystore.infrastructure.settings import InfraSettings
from diystore.infrastructure.controllers.web import ProductController
from diystore.infrastructure.controllers.web.exceptions import InvalidProductID
from diystore.infrastructure.controllers.web.exceptions import ProductNotFound


def test_infra_product_controller_get_one_invalid_id_value(sqlite_json_infrasettings):
    controller = ProductController(sqlite_json_infrasettings)
    with pytest.raises(InvalidProductID):
        controller.get_one(22900628769549271261936325394331419755)


def test_infra_product_controller_get_one_non_existing_object(
    sqlite_json_infrasettings,
):
    controller = ProductController(sqlite_json_infrasettings)
    with pytest.raises(ProductNotFound):
        controller.get_one(uuid4().hex)


def test_infra_product_controller_get_one_existing_object(
    sqlite_json_infrasettings, sqlrepo: SQLProductRepository
):
    controller = ProductController(sqlite_json_infrasettings)
    controller._repo = sqlrepo
    products_orm = LoadedProductOrmModelFactory.build_batch(3)
    valid_id = UUID(bytes=products_orm[0].id).hex
    with sqlrepo._session as s:
        s.add_all(products_orm)
        s.commit()

    representation = controller.get_one(valid_id)
    assert representation is not None
