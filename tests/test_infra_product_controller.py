import json
from uuid import uuid4
from uuid import uuid1
from uuid import UUID

import pytest

from .conftest import LoadedProductOrmModelStub
from .conftest import ProductVendorStub
from .conftest import ProductVendorOrmModel
from .conftest import TopLevelCategoryOrmModelStub
from .conftest import MidLevelCategoryOrmModelStub
from .conftest import TerminalCategoryOrmModelStub
from .conftest import ProductReviewStub
from diystore.infrastructure.repositories.sqlrepository import SQLProductRepository
from diystore.infrastructure.repositories.sqlrepository import ProductReviewOrmModel
from diystore.infrastructure.controllers.web import ProductController
from diystore.infrastructure.controllers.web.exceptions import InvalidProductID
from diystore.infrastructure.controllers.web.exceptions import InvalidVendorID
from diystore.infrastructure.controllers.web.exceptions import InvalidCategoryID
from diystore.infrastructure.controllers.web.exceptions import ProductNotFound
from diystore.infrastructure.controllers.web.exceptions import VendorNotFound
from diystore.infrastructure.controllers.web.exceptions import TopCategoryNotFound
from diystore.infrastructure.controllers.web.exceptions import MidCategoryNotFound
from diystore.infrastructure.controllers.web.exceptions import TerminalCategoryNotFound
from diystore.infrastructure.controllers.web.exceptions import InvalidQueryArgument
from diystore.infrastructure.controllers.web.exceptions import ReviewNotFound
from diystore.infrastructure.controllers.web.exceptions import InvalidReviewID


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


@pytest.mark.parametrize("_id", (2, "abc", (1, 2, 3)))
def test_infra_product_controller_get_mid_category_invalid_id(
    _id, product_controller: ProductController
):
    # GIVEN an invalid category id
    # WHEN a mid category is searched using such id
    # THEN an error is raised
    with pytest.raises(InvalidCategoryID):
        product_controller.get_mid_category(category_id=_id)


def test_infra_product_controller_get_mid_category_non_existent_category(
    product_controller: ProductController,
):
    # GIVEN an id not associated with a mid category
    _id = uuid1().hex

    # WHEN a mid category is searched using such id
    # THEN an error is raised
    with pytest.raises(MidCategoryNotFound):
        product_controller.get_mid_category(category_id=_id)


def test_infra_product_controller_get_mid_category_existent_category(
    product_controller: ProductController, sqlrepo: SQLProductRepository
):
    # GIVEN an id associated with an existent mid category
    category = MidLevelCategoryOrmModelStub()
    _id = UUID(bytes=category.id).hex
    name, description = category.name, category.description
    product_controller._repo = sqlrepo
    with sqlrepo._session as s:
        s.add(category)
        s.commit()

    # WHEN a mid category is searched using such id
    representation = product_controller.get_mid_category(category_id=_id)

    # THEN a correct representation of the category is returned
    assert _id in representation
    assert name in representation
    assert description in representation


def test_infra_product_controller_get_mid_categories_invalid_parent_id(
    product_controller: ProductController,
):
    # GIVEN an invalid parent id
    parent_id = 123

    # WHEN mid level categories are requested based on such id
    # THEN an error occurs
    with pytest.raises(InvalidCategoryID):
        product_controller.get_mid_categories(parent_id=parent_id)


def test_infra_product_controller_get_mid_categories_non_existent_parent_category(
    product_controller: ProductController,
):

    # GIVEN an id not associated with any top category
    parent_id = uuid1()

    # WHEN mid level categories are requested based on such id
    # THEN an error occurs
    with pytest.raises(TopCategoryNotFound):
        product_controller.get_mid_categories(parent_id=parent_id)


def test_infra_product_controller_get_mid_categories_no_categories(
    product_controller: ProductController,
):
    # GIVEN a top category with no child mid categories
    top_category = TopLevelCategoryOrmModelStub()
    parent_id = UUID(bytes=top_category.id).hex
    repo = product_controller._repo
    with repo._session as s:
        s.add(top_category)
        s.commit()

    # WHEN all of its child mid categories are requested
    representation = product_controller.get_mid_categories(parent_id=parent_id)

    # THEN a representation with no mid categories is returned
    assert representation == '{"categories": []}'


def test_infra_product_controller_get_mid_categories_existing_categories(
    product_controller: ProductController,
):
    # GIVEN a top category with existing child mid categories
    top_category = TopLevelCategoryOrmModelStub()
    parent_id = UUID(bytes=top_category.id).hex
    mid_categories = MidLevelCategoryOrmModelStub.build_batch(3, parent=top_category)
    entity_categories = tuple(c.to_domain_entity() for c in mid_categories)
    repo = product_controller._repo
    with repo._session as s:
        s.add(top_category)
        s.add_all(mid_categories)
        s.commit()

    # WHEN all of its child mid categories are requested
    representation = product_controller.get_mid_categories(parent_id=parent_id)

    # THEN a representation containing all of its children is returned
    for category in entity_categories:
        assert category.id.hex in representation
        assert category.name in representation
        assert category.description in representation


@pytest.mark.parametrize("_id", (2, "abc", (1, 2, 3)))
def test_infra_product_controller_get_terminal_category_invalid_id(
    _id, product_controller: ProductController
):
    # GIVEN an invalid category id
    # WHEN a terminal category is searched using such id
    # THEN an error is raised
    with pytest.raises(InvalidCategoryID):
        product_controller.get_terminal_category(category_id=_id)


def test_infra_product_controller_get_terminal_category_non_existent_category(
    product_controller: ProductController,
):
    # GIVEN an id not associated with a terminal category
    _id = uuid1().hex

    # WHEN a terminal category is searched using such id
    # THEN an error is raised
    with pytest.raises(TerminalCategoryNotFound):
        product_controller.get_terminal_category(category_id=_id)


def test_infra_product_controller_get_terminal_category_existent_category(
    product_controller: ProductController,
):
    # GIVEN an id associated with an existent terminal category
    category = TerminalCategoryOrmModelStub()
    _id = UUID(bytes=category.id).hex
    name, description = category.name, category.description
    repo = product_controller._repo
    with repo._session as s:
        s.add(category)
        s.commit()

    # WHEN a terminal category is searched using such id
    representation = product_controller.get_terminal_category(category_id=_id)

    # THEN a correct representation of the category is returned
    assert _id in representation
    assert name in representation
    assert description in representation


def test_infra_product_controller_get_terminal_categories_invalid_parent_id(
    product_controller: ProductController,
):
    # GIVEN an invalid parent id
    parent_id = 123

    # WHEN terminal level categories are requested based on such id
    # THEN an error occurs
    with pytest.raises(InvalidCategoryID):
        product_controller.get_terminal_categories(parent_id=parent_id)


def test_infra_product_controller_get_terminal_categories_non_existent_parent_category(
    product_controller: ProductController,
):

    # GIVEN an id not associated with any mid category
    parent_id = uuid1()

    # WHEN terminal level categories are requested based on such id
    # THEN an error occurs
    with pytest.raises(MidCategoryNotFound):
        product_controller.get_terminal_categories(parent_id=parent_id)


def test_infra_product_controller_get_terminal_categories_no_categories(
    product_controller: ProductController,
):
    # GIVEN a mid category with no child categories
    mid_category = MidLevelCategoryOrmModelStub()
    parent_id = UUID(bytes=mid_category.id).hex
    repo = product_controller._repo
    with repo._session as s:
        s.add(mid_category)
        s.commit()

    # WHEN all of its child categories are requested
    representation = product_controller.get_terminal_categories(parent_id=parent_id)

    # THEN a representation with no terminal categories is returned
    dict_repr = json.loads(representation)
    assert len(dict_repr["categories"]) == 0


def test_infra_product_controller_get_terminal_categories_existing_categories(
    product_controller: ProductController,
):
    # GIVEN a mid category with existing child categories
    mid_category = MidLevelCategoryOrmModelStub()
    parent_id = UUID(bytes=mid_category.id).hex
    children = TerminalCategoryOrmModelStub.build_batch(3, parent=mid_category)
    entity_categories = tuple(c.to_domain_entity() for c in children)
    repo = product_controller._repo
    with repo._session as s:
        s.add(mid_category)
        s.add_all(children)
        s.commit()

    # WHEN all of its child categories are requested
    representation = product_controller.get_terminal_categories(parent_id=parent_id)

    # THEN a representation containing all of its children is returned
    for category in entity_categories:
        assert category.id.hex in representation
        assert category.name in representation
        assert category.description in representation


def test_infra_product_controller_get_vendor_invalid_id(
    product_controller: ProductController,
):
    # GIVEN an invalid id
    _id = 123

    # WHEN a vendor is queried with such id
    # THEN an error occurs
    with pytest.raises(InvalidVendorID):
        product_controller.get_vendor(vendor_id=_id)


def test_infra_product_controller_get_vendor_non_existent_vendor(
    product_controller: ProductController,
):
    # GIVEN a valid id associated with no vendor
    _id = uuid1()

    # WHEN a vendor is queried with such id
    # THEN an error occurs
    with pytest.raises(VendorNotFound):
        product_controller.get_vendor(vendor_id=_id)


def test_infra_product_controller_get_vendor_existent_vendor(
    product_controller: ProductController,
):
    # GIVEN an existing vendor
    vendor = ProductVendorStub()
    repo = product_controller._repo
    with repo._session as s:
        s.add(ProductVendorOrmModel.from_domain_entity(vendor))
        s.commit()

    # WHEN such vendor is queried using its id
    representation = product_controller.get_vendor(vendor_id=vendor.id.hex)

    # THEN a valid representation of the vendor is returned
    dict_repr = json.loads(representation)
    retrieved_vendor = ProductVendorStub(**dict_repr)
    assert vendor.id == retrieved_vendor.id
    assert vendor.name == retrieved_vendor.name
    assert vendor.description == retrieved_vendor.description
    assert vendor.logo_url == retrieved_vendor.logo_url


def test_infra_product_controller_get_vendors_no_existing_vendors(
    product_controller: ProductController,
):
    # GIVEN a repository with no existing vendors
    # WHEN a representation of all vendors are requested
    representation = product_controller.get_vendors()

    # THEN a representation with no vendor information is returned
    dict_repr = json.loads(representation)
    assert len(dict_repr.get("vendors")) == 0


def test_infra_product_controller_get_vendors_existing_vendors(
    product_controller: ProductController,
):
    # GIVEN a repository with existing vendors
    vendors = ProductVendorStub.build_batch(3)
    repo = product_controller._repo
    with repo._session as s:
        s.add_all(ProductVendorOrmModel.from_domain_entity(v) for v in vendors)
        s.commit()

    # WHEN a representation of all vendors are requested
    representation = product_controller.get_vendors()

    # THEN a representation containing information of all vendors is returned
    for vendor in vendors:
        assert vendor.id.hex in representation
        assert vendor.name in representation
        assert vendor.description in representation
        assert vendor.logo_url in representation


def test_infra_product_controller_get_review_non_existent_review(
    product_controller: ProductController,
):
    # GIVEN an id associated with no review
    _id = uuid4()

    # WHEN a query for a review is made with such id
    # THEN an error is raised
    with pytest.raises(ReviewNotFound):
        product_controller.get_review(review_id=_id.hex)


def test_infra_product_controller_get_review_existent_review(
    product_controller: ProductController,
):
    # GIVEN an existent review
    review = ProductReviewStub()
    repo = product_controller._repo
    with repo._session as s:
        s.add(ProductReviewOrmModel.from_domain_entity(review))
        s.commit()

    # WHEN a query for such review is made
    representation = product_controller.get_review(review_id=review.id.hex)

    # THEN a correct representation is returned
    assert review.id.hex in representation
    assert review.product_id.hex in representation
    assert review.client_id.hex in representation
    assert review.creation_date.isoformat() in representation
    assert review.feedback in representation
