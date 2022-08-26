from uuid import UUID

import pytest
from pydantic.error_wrappers import ValidationError

from diystore.domain.entities.product import TerminalLevelProductCategory

from diystore.domain.entities.product.stubs import TopLevelProductCategoryStub
from diystore.domain.entities.product.stubs import MidLevelProductCategoryStub
from diystore.domain.entities.product.stubs import TerminalLevelProductCategoryStub


def test_domain_product_categories_id_wrong_type(non_str_type):
    with pytest.raises(ValidationError) as e:
        TopLevelProductCategoryStub(id=non_str_type)
    assert e.match("not a valid uuid")


def test_domain_product_categories_str_uuid_converts_to_uuid_type(str_uuid: str):
    c = TopLevelProductCategoryStub(id=str_uuid)
    assert isinstance(c.id, UUID)


def test_domain_product_categories_bytes_uuid_converts_to_uuid_type(bytes_uuid: bytes):
    c = TopLevelProductCategoryStub(id=bytes_uuid)
    assert isinstance(c.id, UUID)


def test_domain_product_categories_id_wrong_value(invalid_uuid_str: str):
    with pytest.raises(ValidationError) as e:
        TopLevelProductCategoryStub(id=invalid_uuid_str)
    assert e.match("not a valid uuid")


def test_domain_product_categories_id_valid_uuid(valid_uuid: UUID):
    c = TopLevelProductCategoryStub(id=valid_uuid)
    assert c.id is valid_uuid


def test_domain_product_categories_name_wrong_type(non_str_type):
    with pytest.raises(ValidationError) as e:
        TopLevelProductCategoryStub(name=non_str_type)
    assert e.match("str type expected")


def test_domain_product_categories_name_lenght_gt_max_lenght(
    faker, str_lenght_gt_max_lenght_error_msg
):
    invalid_name = faker.pystr(min_chars=51, max_chars=100)
    with pytest.raises(ValidationError) as e:
        TopLevelProductCategoryStub(name=invalid_name)
    assert e.match(str_lenght_gt_max_lenght_error_msg)


def test_domain_product_categories_name_lenght_lt_min_lenght(
    faker, str_lenght_lt_min_lenght_error_msg
):
    invalid_name = faker.pystr(min_chars=0, max_chars=1)
    with pytest.raises(ValidationError) as e:
        TopLevelProductCategoryStub(name=invalid_name)
    assert e.match(str_lenght_lt_min_lenght_error_msg)


def test_domain_product_categories_valid_name(faker):
    valid_name = faker.pystr(min_chars=2, max_chars=50)
    c = TopLevelProductCategoryStub(name=valid_name)
    assert c.name == valid_name


def test_domain_product_categories_description_wrong_type(non_str_type):
    with pytest.raises(ValidationError) as e:
        TopLevelProductCategoryStub(description=non_str_type)
    assert e.match("str type expected")


def test_domain_product_categories_description_lenght_gt_max_lenght(
    faker, str_lenght_gt_max_lenght_error_msg
):
    invalid_description = faker.pystr(min_chars=3001, max_chars=3002)
    with pytest.raises(ValidationError) as e:
        TopLevelProductCategoryStub(description=invalid_description)
    assert e.match(str_lenght_gt_max_lenght_error_msg)


def test_domain_product_categories_description_lenght_lt_min_lenght(
    str_lenght_lt_min_lenght_error_msg,
):
    with pytest.raises(ValidationError) as e:
        TopLevelProductCategoryStub(description="")
    assert e.match(str_lenght_lt_min_lenght_error_msg)


def test_domain_product_categories_valid_description(faker):
    valid_description = faker.pystr(min_chars=1, max_chars=300)
    c = TopLevelProductCategoryStub(description=valid_description)
    assert c.description == valid_description


@pytest.mark.parametrize(
    "wrong_parent",
    (
        123,
        "abc",
        MidLevelProductCategoryStub(),
        TerminalLevelProductCategoryStub(),
    ),
)
def test_domain_product_categories_wrong_mid_category_parent_type(wrong_parent):
    with pytest.raises(ValidationError):
        MidLevelProductCategoryStub(parent=wrong_parent)


def test_domain_product_categories_valid_mid_category_parent_type():
    parent = TopLevelProductCategoryStub()
    mc = MidLevelProductCategoryStub(parent=parent)
    assert mc.parent == parent


def test_domain_product_categories_valid_dict_for_mid_category_parent_initialization():
    expected_parent = TopLevelProductCategoryStub()
    parent_dict = expected_parent.dict()
    mc = MidLevelProductCategoryStub(parent=parent_dict)
    assert mc.parent == expected_parent


@pytest.mark.parametrize(
    "wrong_parent",
    (
        123,
        "abc",
        TopLevelProductCategoryStub(),
        TerminalLevelProductCategoryStub(),
    ),
)
def test_domain_product_categories_wrong_terminal_category_parent_type(wrong_parent):
    with pytest.raises(ValidationError):
        TerminalLevelProductCategoryStub(parent=wrong_parent)


def test_domain_product_categories_valid_terminal_category_parent_type():
    parent = MidLevelProductCategoryStub()
    tmc = TerminalLevelProductCategoryStub(parent=parent)
    assert tmc.parent == parent


def test_domain_product_categories_valid_dict_for_terminal_category_parent_initialization():
    expected_parent = MidLevelProductCategoryStub()
    parent_dict = expected_parent.dict()
    tmc = TerminalLevelProductCategoryStub(parent=parent_dict)
    assert tmc.parent == expected_parent


def test_domain_product_categories_terminal_category_get_top_level_category():
    top_cat = TopLevelProductCategoryStub()
    mid_cat = MidLevelProductCategoryStub(parent=top_cat)
    tmc: TerminalLevelProductCategory = TerminalLevelProductCategoryStub(
        parent=mid_cat
    )
    assert tmc.get_top_level_category() == top_cat

