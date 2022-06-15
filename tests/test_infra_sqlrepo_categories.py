from uuid import uuid4
from uuid import UUID

import pytest
from sqlalchemy.orm import Session

from .conftest import TopLevelCategoryOrmModelFactory
from .conftest import MidLevelCategoryOrmModelFactory
from .conftest import TerminalCategoryOrmModelFactory
from diystore.infrastructure.repositories.sqlrepository import TopLevelCategoryOrmModel
from diystore.infrastructure.repositories.sqlrepository import MidLevelCategoryOrmModel
from diystore.infrastructure.repositories.sqlrepository import TerminalCategoryOrmModel


def test_infra_sqlrepo_id_is_necessary():
    with pytest.raises(TypeError):
        TopLevelCategoryOrmModelFactory(id=None)


def test_infra_sqlrepo_id_uuid_obj_is_accepted(orm_session: Session):
    _id = uuid4()
    t = TopLevelCategoryOrmModelFactory(id=_id)
    orm_session.add(t)
    orm_session.commit()
    assert t.id == _id.bytes


def test_infra_sqlrepo_id_str_uuid_is_accepted(orm_session: Session):
    _id = str(uuid4())
    t = TopLevelCategoryOrmModelFactory(id=_id)
    orm_session.add(t)
    orm_session.commit()
    assert t.id == UUID(_id).bytes


def test_infra_sqlrepo_id_bytes_uuid_is_accepted(orm_session: Session):
    _id = uuid4().bytes
    t = TopLevelCategoryOrmModelFactory(id=_id)
    orm_session.add(t)
    orm_session.commit()
    assert t.id == _id


def test_infra_sqlrepo_id_int_uuid_is_accepted(orm_session: Session):
    _id = uuid4().int
    t = TopLevelCategoryOrmModelFactory(id=_id)
    orm_session.add(t)
    orm_session.commit()
    assert t.id == UUID(int=_id).bytes


@pytest.mark.parametrize(
    "wrong_id",
    ((1, 2), [1, 2], dict(), {}, type("Replacer", (), dict(replace=lambda x, y: ...))),
)
def test_infra_sqlrepo_id_wrong_type(wrong_id):
    _id = wrong_id
    with pytest.raises(TypeError):
        TopLevelCategoryOrmModelFactory(id=_id)


def test_infra_sqlrepo_id_invalid_str_uuid(invalid_uuid_str):
    with pytest.raises(ValueError):
        TopLevelCategoryOrmModelFactory(id=invalid_uuid_str)


def test_infra_sqlrepo_id_invalid_bytes_uuid(faker):
    _id = uuid4().bytes
    with pytest.raises(ValueError):
        TopLevelCategoryOrmModelFactory(id=_id[0:-2])


def test_infra_sqlrepo_id_invalid_int_uuid():
    with pytest.raises(ValueError):
        TopLevelCategoryOrmModelFactory(id=100000000003242434123123123123123123123123)


@pytest.mark.parametrize(
    "wrong_children",
    (
        TopLevelCategoryOrmModelFactory.build_batch(2),
        TerminalCategoryOrmModelFactory.build_batch(2),
    ),
)
def test_infra_sqlrepo_top_level_category_children_wrong_type(wrong_children):
    t = TopLevelCategoryOrmModelFactory()
    with pytest.raises(TypeError):
        t.children = wrong_children


def test_infra_sqlrepo_top_level_category_children_correct_type(orm_session: Session):
    t = TopLevelCategoryOrmModelFactory()
    t.children = MidLevelCategoryOrmModelFactory.build_batch(2)
    orm_session.add(t)
    orm_session.commit()
    children = orm_session.get(TopLevelCategoryOrmModel, t.id).children
    for c in children:
        assert isinstance(c, MidLevelCategoryOrmModel)


@pytest.mark.parametrize(
    "wrong_children",
    (
        TopLevelCategoryOrmModelFactory.build_batch(2),
        MidLevelCategoryOrmModelFactory.build_batch(2),
    ),
)
def test_infra_sqlrepo_mid_level_category_children_wrong_type(wrong_children):
    m = MidLevelCategoryOrmModelFactory()
    with pytest.raises((TypeError, KeyError)):
        m.children = wrong_children


def test_infra_sqlrepo_mid_level_category_children_correct_type(orm_session: Session):
    m = MidLevelCategoryOrmModelFactory()
    m.children = TerminalCategoryOrmModelFactory.build_batch(2)
    orm_session.add(m)
    orm_session.commit()
    children = orm_session.get(MidLevelCategoryOrmModel, m.id).children
    for c in children:
        assert isinstance(c, TerminalCategoryOrmModel)


@pytest.mark.parametrize(
    "wrong_parent",
    (MidLevelCategoryOrmModelFactory(), TerminalCategoryOrmModelFactory()),
)
def test_infra_sqlrepo_mid_level_category_parent_wrong_type(wrong_parent):
    m = MidLevelCategoryOrmModelFactory()
    with pytest.raises(TypeError):
        m.parent = wrong_parent


def test_infra_sqlrepo_mid_level_category_parent_correct_type(orm_session: Session):
    m = MidLevelCategoryOrmModelFactory()
    m.parent = TopLevelCategoryOrmModelFactory()
    orm_session.add(m)
    orm_session.commit()
    parent = orm_session.get(MidLevelCategoryOrmModel, m.id).parent
    assert isinstance(parent, TopLevelCategoryOrmModel)


@pytest.mark.parametrize(
    "wrong_parent",
    (TopLevelCategoryOrmModelFactory(), TerminalCategoryOrmModelFactory()),
)
def test_infra_sqlrepo_terminal_category_parent_wrong_type(wrong_parent):
    c = TerminalCategoryOrmModelFactory()
    with pytest.raises(TypeError):
        c.parent = wrong_parent


def test_infra_sqlrepo_terminal_category_parent_correct_type(orm_session: Session):
    c = TerminalCategoryOrmModelFactory()
    c.parent = MidLevelCategoryOrmModelFactory()
    orm_session.add(c)
    orm_session.commit()
    parent = orm_session.get(TerminalCategoryOrmModel, c.id).parent
    assert isinstance(parent, MidLevelCategoryOrmModel)
