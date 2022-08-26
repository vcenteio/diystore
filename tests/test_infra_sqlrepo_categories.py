from uuid import uuid4
from uuid import UUID

import pytest
from sqlalchemy.orm import Session

from diystore.infrastructure.repositories.sqlrepository.models.stubs import LoadedProductOrmModelStub
from diystore.infrastructure.repositories.sqlrepository.models.stubs import ProductVendorOrmModel
from diystore.infrastructure.repositories.sqlrepository.models.stubs import TopLevelCategoryOrmModelStub
from diystore.infrastructure.repositories.sqlrepository.models.stubs import MidLevelCategoryOrmModelStub
from diystore.infrastructure.repositories.sqlrepository.models.stubs import TerminalCategoryOrmModelStub
from diystore.domain.entities.product.stubs import TopLevelProductCategoryStub
from diystore.domain.entities.product.stubs import MidLevelProductCategoryStub
from diystore.domain.entities.product.stubs import TerminalLevelProductCategoryStub
from diystore.infrastructure.repositories.sqlrepository import TopLevelCategoryOrmModel
from diystore.infrastructure.repositories.sqlrepository import MidLevelCategoryOrmModel
from diystore.infrastructure.repositories.sqlrepository import TerminalCategoryOrmModel
from diystore.infrastructure.repositories.sqlrepository.exceptions import (
    OrmEntityNotFullyLoaded,
)
from diystore.domain.entities.product import TopLevelProductCategory
from diystore.domain.entities.product import MidLevelProductCategory
from diystore.domain.entities.product import TerminalLevelProductCategory


def test_infra_sqlrepo_categories_id_is_necessary():
    with pytest.raises(TypeError):
        TopLevelCategoryOrmModelStub(id=None)


def test_infra_sqlrepo_categories_id_uuid_obj_is_accepted(orm_session: Session):
    _id = uuid4()
    t = TopLevelCategoryOrmModelStub(id=_id)
    orm_session.add(t)
    orm_session.commit()
    assert t.id == _id.bytes


def test_infra_sqlrepo_categories_id_str_uuid_is_accepted(orm_session: Session):
    _id = str(uuid4())
    t = TopLevelCategoryOrmModelStub(id=_id)
    orm_session.add(t)
    orm_session.commit()
    assert t.id == UUID(_id).bytes


def test_infra_sqlrepo_categories_id_bytes_uuid_is_accepted(orm_session: Session):
    _id = uuid4().bytes
    t = TopLevelCategoryOrmModelStub(id=_id)
    orm_session.add(t)
    orm_session.commit()
    assert t.id == _id


def test_infra_sqlrepo_categories_id_int_uuid_is_accepted(orm_session: Session):
    _id = uuid4().int
    t = TopLevelCategoryOrmModelStub(id=_id)
    orm_session.add(t)
    orm_session.commit()
    assert t.id == UUID(int=_id).bytes


@pytest.mark.parametrize(
    "wrong_id",
    ((1, 2), [1, 2], dict(), {}, type("Replacer", (), dict(replace=lambda x, y: ...))),
)
def test_infra_sqlrepo_categories_id_wrong_type(wrong_id):
    _id = wrong_id
    with pytest.raises(TypeError):
        TopLevelCategoryOrmModelStub(id=_id)


def test_infra_sqlrepo_categories_id_invalid_str_uuid(invalid_uuid_str):
    with pytest.raises(ValueError):
        TopLevelCategoryOrmModelStub(id=invalid_uuid_str)


def test_infra_sqlrepo_categories_id_invalid_bytes_uuid():
    _id = uuid4().bytes
    with pytest.raises(ValueError):
        TopLevelCategoryOrmModelStub(id=_id[0:-2])


def test_infra_sqlrepo_categories_id_invalid_int_uuid():
    with pytest.raises(ValueError):
        TopLevelCategoryOrmModelStub(id=100000000003242434123123123123123123123123)


@pytest.mark.parametrize(
    "wrong_children",
    (
        TopLevelCategoryOrmModelStub.build_batch(2),
        TerminalCategoryOrmModelStub.build_batch(2),
    ),
)
def test_infra_sqlrepo_top_level_category_children_wrong_type(wrong_children):
    t = TopLevelCategoryOrmModelStub()
    with pytest.raises(TypeError):
        t.children = wrong_children


def test_infra_sqlrepo_top_level_category_children_correct_type(orm_session: Session):
    t = TopLevelCategoryOrmModelStub()
    t.children = MidLevelCategoryOrmModelStub.build_batch(2)
    orm_session.add(t)
    orm_session.commit()
    children = orm_session.get(TopLevelCategoryOrmModel, t.id).children
    for c in children:
        assert isinstance(c, MidLevelCategoryOrmModel)


@pytest.mark.parametrize(
    "wrong_children",
    (
        TopLevelCategoryOrmModelStub.build_batch(2),
        MidLevelCategoryOrmModelStub.build_batch(2),
    ),
)
def test_infra_sqlrepo_mid_level_category_children_wrong_type(wrong_children):
    m = MidLevelCategoryOrmModelStub()
    with pytest.raises((TypeError, KeyError)):
        m.children = wrong_children


def test_infra_sqlrepo_mid_level_category_children_correct_type(orm_session: Session):
    m = MidLevelCategoryOrmModelStub()
    m.children = TerminalCategoryOrmModelStub.build_batch(2)
    orm_session.add(m)
    orm_session.commit()
    children = orm_session.get(MidLevelCategoryOrmModel, m.id).children
    for c in children:
        assert isinstance(c, TerminalCategoryOrmModel)


@pytest.mark.parametrize(
    "wrong_parent",
    (MidLevelCategoryOrmModelStub(), TerminalCategoryOrmModelStub()),
)
def test_infra_sqlrepo_mid_level_category_parent_wrong_type(wrong_parent):
    m = MidLevelCategoryOrmModelStub()
    with pytest.raises(TypeError):
        m.parent = wrong_parent


def test_infra_sqlrepo_mid_level_category_parent_correct_type(orm_session: Session):
    m = MidLevelCategoryOrmModelStub()
    m.parent = TopLevelCategoryOrmModelStub()
    orm_session.add(m)
    orm_session.commit()
    parent = orm_session.get(MidLevelCategoryOrmModel, m.id).parent
    assert isinstance(parent, TopLevelCategoryOrmModel)


@pytest.mark.parametrize(
    "wrong_parent",
    (TopLevelCategoryOrmModelStub(), TerminalCategoryOrmModelStub()),
)
def test_infra_sqlrepo_terminal_category_parent_wrong_type(wrong_parent):
    c = TerminalCategoryOrmModelStub()
    with pytest.raises(TypeError):
        c.parent = wrong_parent


def test_infra_sqlrepo_terminal_category_parent_correct_type(orm_session: Session):
    c = TerminalCategoryOrmModelStub()
    c.parent = MidLevelCategoryOrmModelStub()
    orm_session.add(c)
    orm_session.commit()
    parent = orm_session.get(TerminalCategoryOrmModel, c.id).parent
    assert isinstance(parent, MidLevelCategoryOrmModel)


def test_infra_sqlrepo_top_level_category_to_domain_entity():
    tlc_orm: TopLevelCategoryOrmModel = TopLevelCategoryOrmModelStub()
    tlc_entity = tlc_orm.to_domain_entity()
    assert isinstance(tlc_entity, TopLevelProductCategory)
    assert tlc_entity.id.bytes == tlc_orm.id
    assert tlc_entity.name == tlc_orm.name
    assert tlc_entity.description == tlc_orm.description


@pytest.mark.parametrize(
    "wrong_entity",
    (MidLevelProductCategoryStub(), TerminalLevelProductCategoryStub()),
)
def test_infra_sqlrepo_top_level_category_from_domain_entity_wrong_type(wrong_entity):
    with pytest.raises(TypeError):
        TopLevelCategoryOrmModel.from_domain_entity(wrong_entity)


def test_infra_sqlrepo_top_level_category_from_domain_entity_correct_type():
    tlc_entity: TopLevelProductCategory = TopLevelProductCategoryStub()
    tlc_orm = TopLevelCategoryOrmModel.from_domain_entity(tlc_entity)
    assert isinstance(tlc_orm, TopLevelCategoryOrmModel)
    assert tlc_orm.id == tlc_entity.id.bytes
    assert tlc_orm.name == tlc_entity.name
    assert tlc_orm.description == tlc_entity.description


def test_infra_sqlrepo_mid_level_category_to_domain_entity_fully_loaded():
    parent = TopLevelCategoryOrmModelStub()
    mlc_orm: MidLevelCategoryOrmModel = MidLevelCategoryOrmModelStub()
    mlc_orm.parent = parent
    mlc_entity = mlc_orm.to_domain_entity()
    assert isinstance(mlc_entity, MidLevelProductCategory)
    assert isinstance(mlc_entity.parent, TopLevelProductCategory)
    assert mlc_entity.id.bytes == mlc_orm.id
    assert mlc_entity.name == mlc_orm.name
    assert mlc_entity.description == mlc_orm.description
    assert mlc_entity.get_parent_id().bytes == mlc_orm.parent.id


@pytest.mark.parametrize(
    "wrong_entity",
    (TopLevelProductCategoryStub(), TerminalLevelProductCategoryStub()),
)
def test_infra_sqlrepo_mid_level_category_from_domain_entity_wrong_type(wrong_entity):
    with pytest.raises(TypeError):
        MidLevelCategoryOrmModel.from_domain_entity(wrong_entity)


def test_infra_sqlrepo_mid_level_category_from_domain_entity_correct_type():
    mlc_entity: MidLevelProductCategory = MidLevelProductCategoryStub()
    mlc_orm = MidLevelCategoryOrmModel.from_domain_entity(mlc_entity)
    assert isinstance(mlc_orm, MidLevelCategoryOrmModel)
    assert mlc_orm.id == mlc_entity.id.bytes
    assert mlc_orm.name == mlc_entity.name
    assert mlc_orm.description == mlc_entity.description
    assert mlc_orm.parent_id == mlc_entity.get_parent_id().bytes


def test_infra_sqlrepo_terminal_level_category_to_domain_entity_fully_loaded():
    parent = MidLevelCategoryOrmModelStub()
    parent.parent = TopLevelCategoryOrmModelStub()
    tmc_orm: TerminalCategoryOrmModel = TerminalCategoryOrmModelStub()
    tmc_orm.parent = parent
    tmc_entity = tmc_orm.to_domain_entity()
    assert isinstance(tmc_entity, TerminalLevelProductCategory)
    assert isinstance(tmc_entity.parent, MidLevelProductCategory)
    assert isinstance(tmc_entity.get_top_level_category(), TopLevelProductCategory)
    assert tmc_entity.id.bytes == tmc_orm.id
    assert tmc_entity.name == tmc_orm.name
    assert tmc_entity.description == tmc_orm.description
    assert tmc_entity.get_parent_id().bytes == tmc_orm.parent.id


@pytest.mark.parametrize(
    "wrong_entity",
    (TopLevelProductCategoryStub(), MidLevelProductCategoryStub()),
)
def test_infra_sqlrepo_terminal_level_category_from_domain_entity_wrong_type(
    wrong_entity,
):
    with pytest.raises(TypeError):
        TerminalCategoryOrmModel.from_domain_entity(wrong_entity)


def test_infra_sqlrepo_terminal_level_category_from_domain_entity_correct_type():
    tmc_entity: TerminalLevelProductCategory = TerminalLevelProductCategoryStub()
    tmc_orm = TerminalCategoryOrmModel.from_domain_entity(tmc_entity)
    assert isinstance(tmc_orm, TerminalCategoryOrmModel)
    assert tmc_orm.id == tmc_entity.id.bytes
    assert tmc_orm.name == tmc_entity.name
    assert tmc_orm.description == tmc_entity.description
    assert tmc_orm.parent_id == tmc_entity.get_parent_id().bytes
