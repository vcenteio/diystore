from uuid import UUID

import pytest
from pydantic.error_wrappers import ValidationError

from diystore.domain.entities.product import TerminalLevelProductCategory

from .conftest import TopLevelProductCategoryFactory
from .conftest import MidLevelProductCategoryFactory
from .conftest import TerminalLevelProductCategoryFactory


def test_domain_product_categories_id_wrong_type(non_str_type):
    with pytest.raises(ValidationError) as e:
        TopLevelProductCategoryFactory(id=non_str_type)
    assert e.match("not a valid uuid")


def test_domain_product_categories_str_uuid_converts_to_uuid_type(str_uuid: str):
    c = TopLevelProductCategoryFactory(id=str_uuid)
    assert isinstance(c.id, UUID)


def test_domain_product_categories_bytes_uuid_converts_to_uuid_type(bytes_uuid: bytes):
    c = TopLevelProductCategoryFactory(id=bytes_uuid)
    assert isinstance(c.id, UUID)


def test_domain_product_categories_id_wrong_value(invalid_uuid_str: str):
    with pytest.raises(ValidationError) as e:
        TopLevelProductCategoryFactory(id=invalid_uuid_str)
    assert e.match("not a valid uuid")


def test_domain_product_categories_id_valid_uuid(valid_uuid: UUID):
    c = TopLevelProductCategoryFactory(id=valid_uuid)
    assert c.id is valid_uuid


def test_domain_product_categories_name_wrong_type(non_str_type):
    with pytest.raises(ValidationError) as e:
        TopLevelProductCategoryFactory(name=non_str_type)
    assert e.match("str type expected")


def test_domain_product_categories_name_lenght_gt_max_lenght(
    faker, str_lenght_gt_max_lenght_error_msg
):
    invalid_name = faker.pystr(min_chars=51, max_chars=100)
    with pytest.raises(ValidationError) as e:
        TopLevelProductCategoryFactory(name=invalid_name)
    assert e.match(str_lenght_gt_max_lenght_error_msg)


def test_domain_product_categories_name_lenght_lt_min_lenght(
    faker, str_lenght_lt_min_lenght_error_msg
):
    invalid_name = faker.pystr(min_chars=0, max_chars=1)
    with pytest.raises(ValidationError) as e:
        TopLevelProductCategoryFactory(name=invalid_name)
    assert e.match(str_lenght_lt_min_lenght_error_msg)


def test_domain_product_categories_valid_name(faker):
    valid_name = faker.pystr(min_chars=2, max_chars=50)
    c = TopLevelProductCategoryFactory(name=valid_name)
    assert c.name == valid_name


def test_domain_product_categories_description_wrong_type(non_str_type):
    with pytest.raises(ValidationError) as e:
        TopLevelProductCategoryFactory(description=non_str_type)
    assert e.match("str type expected")


def test_domain_product_categories_description_lenght_gt_max_lenght(
    faker, str_lenght_gt_max_lenght_error_msg
):
    invalid_description = faker.pystr(min_chars=3001, max_chars=3002)
    with pytest.raises(ValidationError) as e:
        TopLevelProductCategoryFactory(description=invalid_description)
    assert e.match(str_lenght_gt_max_lenght_error_msg)


def test_domain_product_categories_description_lenght_lt_min_lenght(
    str_lenght_lt_min_lenght_error_msg,
):
    with pytest.raises(ValidationError) as e:
        TopLevelProductCategoryFactory(description="")
    assert e.match(str_lenght_lt_min_lenght_error_msg)


def test_domain_product_categories_valid_description(faker):
    valid_description = faker.pystr(min_chars=1, max_chars=300)
    c = TopLevelProductCategoryFactory(description=valid_description)
    assert c.description == valid_description


@pytest.mark.parametrize(
    "wrong_parent",
    (
        123,
        "abc",
        MidLevelProductCategoryFactory(),
        TerminalLevelProductCategoryFactory(),
    ),
)
def test_domain_product_categories_wrong_mid_category_parent_type(wrong_parent):
    with pytest.raises(ValidationError):
        MidLevelProductCategoryFactory(parent=wrong_parent)


def test_domain_product_categories_valid_mid_category_parent_type():
    parent = TopLevelProductCategoryFactory()
    mc = MidLevelProductCategoryFactory(parent=parent)
    assert mc.parent == parent


def test_domain_product_categories_valid_dict_for_mid_category_parent_initialization():
    expected_parent = TopLevelProductCategoryFactory()
    parent_dict = expected_parent.dict()
    mc = MidLevelProductCategoryFactory(parent=parent_dict)
    assert mc.parent == expected_parent


@pytest.mark.parametrize(
    "wrong_parent",
    (
        123,
        "abc",
        TopLevelProductCategoryFactory(),
        TerminalLevelProductCategoryFactory(),
    ),
)
def test_domain_product_categories_wrong_terminal_category_parent_type(wrong_parent):
    with pytest.raises(ValidationError):
        TerminalLevelProductCategoryFactory(parent=wrong_parent)


def test_domain_product_categories_valid_terminal_category_parent_type():
    parent = MidLevelProductCategoryFactory()
    tmc = TerminalLevelProductCategoryFactory(parent=parent)
    assert tmc.parent == parent


def test_domain_product_categories_valid_dict_for_terminal_category_parent_initialization():
    expected_parent = MidLevelProductCategoryFactory()
    parent_dict = expected_parent.dict()
    tmc = TerminalLevelProductCategoryFactory(parent=parent_dict)
    assert tmc.parent == expected_parent


def test_domain_product_categories_terminal_category_get_top_level_category():
    top_cat = TopLevelProductCategoryFactory()
    mid_cat = MidLevelProductCategoryFactory(parent=top_cat)
    tmc: TerminalLevelProductCategory = TerminalLevelProductCategoryFactory(
        parent=mid_cat
    )
    assert tmc.get_top_level_category() == top_cat

