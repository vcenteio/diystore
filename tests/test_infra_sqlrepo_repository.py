from uuid import UUID
from uuid import uuid4
from uuid import uuid1
from decimal import Decimal

import pytest
from sqlalchemy.orm import Session
from factory import Factory

from .conftest import ProductStub, ProductVendorOrmModelStub
from .conftest import ProductVendorStub
from .conftest import TopLevelCategoryOrmModelStub
from .conftest import MidLevelCategoryOrmModelStub
from .conftest import TerminalCategoryOrmModelStub
from .conftest import ProductOrmModelStub
from .conftest import LoadedProductOrmModelStub
from .conftest import ProductReviewOrmModelStub
from .conftest import ProductReviewStub
from .conftest import persist_new_products_and_return_category_id
from diystore.domain.entities.product import Product
from diystore.domain.entities.product import TerminalLevelProductCategory
from diystore.domain.entities.product import MidLevelProductCategory
from diystore.domain.entities.product import TopLevelProductCategory
from diystore.domain.entities.product import ProductVendor
from diystore.domain.entities.product import ProductReview
from diystore.infrastructure.repositories.sqlrepository import SQLProductRepository
from diystore.infrastructure.repositories.sqlrepository import ProductVendorOrmModel
from diystore.infrastructure.repositories.sqlrepository import ProductReviewOrmModel
from diystore.infrastructure.repositories.sqlrepository import ProductOrmModel


def test_infra_sqlrepo_repository_get_product_wrong_id_type(
    sqlrepo: SQLProductRepository,
):
    with pytest.raises(TypeError):
        sqlrepo.get_product(1)


def test_infra_sqlrepo_repository_get_product_inexistent_product(
    sqlrepo: SQLProductRepository,
):
    products = ProductOrmModelStub.build_batch(3)
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
        LoadedProductOrmModelStub, sqlrepo._session
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
        LoadedProductOrmModelStub, sqlrepo._session
    )

    fetched_product = sqlrepo.get_product(product_id, with_reviews=True)
    for review in fetched_product.get_client_reviews():
        assert isinstance(review, ProductReview)


def test_infra_sqlrepo_repository_get_product_that_has_no_reviews(
    sqlrepo: SQLProductRepository,
):
    product_id = _persist_new_object_and_return_its_id(
        LoadedProductOrmModelStub, sqlrepo._session, reviews=[]
    )

    fetched_product = sqlrepo.get_product(product_id, with_reviews=True)
    assert fetched_product.get_client_reviews() == ()


def test_infra_sqlrepo_get_products_wrong_id_type(sqlrepo: SQLProductRepository):
    with pytest.raises(TypeError):
        sqlrepo.get_products(category_id=1)


def test_infra_sqlrepo_get_products_non_existent_products(
    sqlrepo: SQLProductRepository,
):
    category_id = _persist_new_object_and_return_its_id(
        TerminalCategoryOrmModelStub, sqlrepo._session
    )
    products = sqlrepo.get_products(category_id=category_id)
    assert len(products) == 0


def test_infra_sqlrepo_get_products_existent_products(sqlrepo: SQLProductRepository):
    category_id = persist_new_products_and_return_category_id(3, sqlrepo._session)

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
    category_id = persist_new_products_and_return_category_id(
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
    category_id = persist_new_products_and_return_category_id(
        no_products, sqlrepo._session, base_price=Decimal("99")
    )
    products = sqlrepo.get_products(category_id, price_min=Decimal("100"))
    assert len(products) == 0


def test_infra_sqlrepo_get_products_price_max_restricts_no_of_products(
    sqlrepo: SQLProductRepository,
):
    no_products = 5
    category_id = persist_new_products_and_return_category_id(
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
    category_id = persist_new_products_and_return_category_id(
        no_products, sqlrepo._session, rating=Decimal("3")
    )
    products = sqlrepo.get_products(category_id, rating_min=Decimal("4"))
    assert len(products) == 0


def test_infra_sqlrepo_get_products_rating_max_restricts_results(
    sqlrepo: SQLProductRepository,
):
    no_products = 5
    category_id = persist_new_products_and_return_category_id(
        no_products, sqlrepo._session, rating=Decimal("4")
    )
    products = sqlrepo.get_products(category_id, rating_max=Decimal("3"))
    assert len(products) == 0


def test_infra_sqlrepo_get_products_with_discounts_only_param_restricts_results(
    sqlrepo: SQLProductRepository,
):
    no_products = 5
    category = TerminalCategoryOrmModelStub()
    category_id = category.id
    products_with_no_discount = LoadedProductOrmModelStub.build_batch(
        no_products, category_id=category_id, category=category, discount_id=None
    )
    product_with_discount = LoadedProductOrmModelStub(
        category_id=category_id, category=category
    )
    with sqlrepo._session as s:
        s.add_all([category, product_with_discount, *products_with_no_discount])
        s.commit()

    products = sqlrepo.get_products(UUID(bytes=category_id), with_discounts_only=True)
    assert len(products) == 1


def test_infra_sqlrepo_get_products_ordering_by_rating_descending(
    sqlrepo: SQLProductRepository,
):
    category_id = persist_new_products_and_return_category_id(5, sqlrepo._session)

    products = sqlrepo.get_products_ordering_by_rating(category_id, descending=True)
    products_ratings = [p.rating for p in products]
    expected_result = sorted(products_ratings, reverse=True)
    assert products_ratings == expected_result


def test_infra_sqlrepo_get_products_ordering_by_rating_ascending(
    sqlrepo: SQLProductRepository,
):
    category_id = persist_new_products_and_return_category_id(5, sqlrepo._session)

    products = sqlrepo.get_products_ordering_by_rating(category_id, descending=False)
    products_ratings = [p.rating for p in products]
    expected_result = sorted(products_ratings)
    assert products_ratings == expected_result


def test_infra_sqlrepo_get_products_ordering_by_price_descending(
    sqlrepo: SQLProductRepository,
):
    category_id = persist_new_products_and_return_category_id(5, sqlrepo._session)

    products = sqlrepo.get_products_ordering_by_price(category_id, descending=True)
    products_prices = [p.get_base_price() for p in products]
    expected_result = sorted(products_prices, reverse=True)
    assert products_prices == expected_result


def test_infra_sqlrepo_get_products_ordering_by_price_ascending(
    sqlrepo: SQLProductRepository,
):
    category_id = persist_new_products_and_return_category_id(5, sqlrepo._session)

    products = sqlrepo.get_products_ordering_by_price(category_id, descending=False)
    products_prices = [p.get_base_price() for p in products]
    expected_result = sorted(products_prices)
    assert products_prices == expected_result


def test_infra_sqlrepo_get_top_level_category_wrong_id_type(
    sqlrepo: SQLProductRepository,
):
    # GIVEN a invalid id type
    # WHEN a search for a top level category is made with such id
    # THEN a error is raised
    with pytest.raises(TypeError):
        sqlrepo.get_top_level_category(1)


def test_infra_sqlrepo_get_top_level_category_non_existent_category(
    sqlrepo: SQLProductRepository,
):
    # GIVEN a valid id not related to any top level category
    non_existent_id = uuid1()

    # WHEN a search for a top level category is made with such id
    result = sqlrepo.get_top_level_category(non_existent_id)

    # THEN None is returned
    assert result is None


def test_infra_sqlrepo_get_top_level_category_existent_category(
    sqlrepo: SQLProductRepository,
):
    # GIVEN a valid id associated with an existing category
    cat = TopLevelCategoryOrmModelStub()
    _id, name, description = UUID(bytes=cat.id), cat.name, cat.description

    with sqlrepo._session as s:
        s.add(cat)
        s.commit()

    # WHEN a search for a top level category is made with such id
    retrieved_category = sqlrepo.get_top_level_category(_id)

    # THEN the correct category is returned
    assert retrieved_category.id == _id
    assert retrieved_category.name == name
    assert retrieved_category.description == description


def test_infra_sqlrepo_get_top_level_categories_no_categories(
    sqlrepo: SQLProductRepository,
):
    # GIVEN a repository with no top categories
    # WHEN a search for a top category is made
    result = sqlrepo.get_top_level_categories()

    # THEN no top categories are returned
    assert result == ()


def test_infra_sqlrepo_get_top_level_categories_existent_categories(
    sqlrepo: SQLProductRepository,
):
    # GIVEN a repository with existing top categories
    orm_categories = TopLevelCategoryOrmModelStub.build_batch(3)
    expected = tuple(c.to_domain_entity() for c in orm_categories)
    with sqlrepo._session as s:
        s.add_all(orm_categories)
        s.commit()

    # WHEN a search for all top categories is made
    retrieved_categories = sqlrepo.get_top_level_categories()

    # THEN all the top categories should be returned
    assert retrieved_categories == expected


def test_infra_sqlrepo_get_mid_level_category_wrong_id_type(
    sqlrepo: SQLProductRepository,
):
    # GIVEN a invalid id type
    # WHEN a search for a mid level category is made with such id
    # THEN a error is raised
    with pytest.raises(TypeError):
        sqlrepo.get_mid_level_category(1)


def test_infra_sqlrepo_get_mid_level_category_non_existent_category(
    sqlrepo: SQLProductRepository,
):
    # GIVEN a valid id not related to any mid level category
    non_existent_id = uuid1()

    # WHEN a search for a mid level category is made with such id
    category = sqlrepo.get_mid_level_category(non_existent_id)

    # THEN no category is returned
    assert category is None


def test_infra_sqlrepo_get_mid_level_category_existent_category(
    sqlrepo: SQLProductRepository,
):
    # GIVEN a valid id associated with an existing mid level category
    cat = MidLevelCategoryOrmModelStub()
    _id, name, description = UUID(bytes=cat.id), cat.name, cat.description

    with sqlrepo._session as s:
        s.add(cat)
        s.commit()

    # WHEN a search for a mid level category is made with such id
    retrieved_category = sqlrepo.get_mid_level_category(_id)

    # THEN the correct category is returned
    assert retrieved_category.id == _id
    assert retrieved_category.name == name
    assert retrieved_category.description == description


def test_infra_sqlrepo_get_mid_level_categories_non_existent_parent_category(
    sqlrepo: SQLProductRepository,
):
    # GIVEN an id not associated with a top level category
    parent_id = uuid4()

    # WHEN a search for mid level categories is made based on such id
    result = sqlrepo.get_mid_level_categories(parent_id)

    # THEN None is returned
    assert result is None


def test_infra_sqlrepo_get_mid_level_categories_no_categories(
    sqlrepo: SQLProductRepository,
):
    # GIVEN a top category with no child mid level categories
    top_cat = TopLevelCategoryOrmModelStub()
    parent_id = UUID(bytes=top_cat.id)
    with sqlrepo._session as s:
        s.add(top_cat)
        s.commit()

    # WHEN a search for its child mid level categories is made
    result = sqlrepo.get_mid_level_categories(parent_id)

    # THEN no mid categories are returned
    assert result == ()


def test_infra_sqlrepo_get_mid_level_categories_existent_categories(
    sqlrepo: SQLProductRepository,
):
    # GIVEN a top category with child mid level categories
    top_category = TopLevelCategoryOrmModelStub()
    parent_id = UUID(bytes=top_category.id)
    mid_categories = MidLevelCategoryOrmModelStub.build_batch(3, parent=top_category)
    expected = tuple(c.to_domain_entity() for c in mid_categories)
    with sqlrepo._session as s:
        s.add(top_category)
        s.add_all(mid_categories)
        s.commit()

    # WHEN a search for all child mid level categories is made
    retrieved_categories = sqlrepo.get_mid_level_categories(parent_id)

    # THEN all the child mid categories should be returned
    assert retrieved_categories == expected


def test_infra_sqlrepo_get_terminal_level_category_wrong_id_type(
    sqlrepo: SQLProductRepository,
):
    # GIVEN a invalid id type
    # WHEN a search for a terminal level category is made with such id
    # THEN a error is raised
    with pytest.raises(TypeError):
        sqlrepo.get_terminal_level_category(1)


def test_infra_sqlrepo_get_terminal_level_category_non_existent_category(
    sqlrepo: SQLProductRepository,
):
    # GIVEN a valid id not related to any terminal level category
    non_existent_id = uuid1()

    # WHEN a search for a terminal level category is made with such id
    category = sqlrepo.get_terminal_level_category(non_existent_id)

    # THEN no category is returned
    assert category is None


def test_infra_sqlrepo_get_terminal_level_category_existent_category(
    sqlrepo: SQLProductRepository,
):
    # GIVEN a valid id associated with an existing teminal level category
    cat = TerminalCategoryOrmModelStub()
    _id, name, description = UUID(bytes=cat.id), cat.name, cat.description

    with sqlrepo._session as s:
        s.add(cat)
        s.commit()

    # WHEN a search for a terminal level category is made with such id
    retrieved_category = sqlrepo.get_terminal_level_category(_id)

    # THEN the correct category is returned
    assert retrieved_category.id == _id
    assert retrieved_category.name == name
    assert retrieved_category.description == description


def test_infra_sqlrepo_get_terminal_level_categories_non_existent_parent_category(
    sqlrepo: SQLProductRepository,
):
    # GIVEN an id not associated with a mid level category
    parent_id = uuid4()

    # WHEN a search for child terminal level categories is made based on such id
    result = sqlrepo.get_terminal_level_categories(parent_id)

    # THEN None is returned
    assert result is None


def test_infra_sqlrepo_get_terminal_level_categories_no_categories(
    sqlrepo: SQLProductRepository,
):
    # GIVEN a mid level category with no child categories
    mid_cat = MidLevelCategoryOrmModelStub()
    parent_id = UUID(bytes=mid_cat.id)
    with sqlrepo._session as s:
        s.add(mid_cat)
        s.commit()

    # WHEN a search for its child categories is made
    result = sqlrepo.get_terminal_level_categories(parent_id)

    # THEN no terminal categories are returned
    assert result == ()


def test_infra_sqlrepo_get_terminal_level_categories_existent_categories(
    sqlrepo: SQLProductRepository,
):
    # GIVEN a mid category with child categories
    mid_cat = MidLevelCategoryOrmModelStub()
    parent_id = UUID(bytes=mid_cat.id)
    terminal_categories = TerminalCategoryOrmModelStub.build_batch(3, parent=mid_cat)
    expected = tuple(c.to_domain_entity() for c in terminal_categories)
    with sqlrepo._session as s:
        s.add(mid_cat)
        s.add_all(terminal_categories)
        s.commit()

    # WHEN a search for all child categories is made
    retrieved_categories = sqlrepo.get_terminal_level_categories(parent_id)

    # THEN all the child terminal categories should be returned
    assert retrieved_categories == expected


def test_infra_sqlrepo_get_vendor_non_existing_vendor(sqlrepo: SQLProductRepository):
    # GIVEN an id not associated with an existing vendor
    _id = uuid1()

    # WHEN a vendor is queried with such id
    vendor = sqlrepo.get_vendor(_id)

    # THEN no vendor is returned
    assert vendor is None


def test_infra_sqlrepo_get_vendor_existing_vendor(sqlrepo: SQLProductRepository):
    # GIVEN an id associated with an existing vendor
    existing_vendor = ProductVendorStub()

    with sqlrepo._session as s:
        s.add(ProductVendorOrmModel.from_domain_entity(existing_vendor))
        s.commit()

    # WHEN a vendor is queried with such id
    vendor = sqlrepo.get_vendor(existing_vendor.id)

    # THEN a valid vendor object is returned
    assert vendor.id == existing_vendor.id
    assert vendor.name == existing_vendor.name
    assert vendor.description == existing_vendor.description
    assert vendor.logo_url == existing_vendor.logo_url


def test_infra_sqlrepo_get_vendors_no_existing_vendors(sqlrepo: SQLProductRepository):
    # GIVEN a repository with no vendors
    # WHEN a query for all vendors is made
    vendors = sqlrepo.get_vendors()

    # THEN no vendors are returned
    assert vendors == ()


def test_infra_sqlrepo_get_vendors_existing_vendors(sqlrepo: SQLProductRepository):
    # GIVEN a repository with vendors
    vendors = ProductVendorOrmModelStub.build_batch(3)
    expected_vendors = tuple(v.to_domain_entity() for v in vendors)
    with sqlrepo._session as s:
        s.add_all(vendors)
        s.commit()

    # WHEN a query for all vendors is made
    retrieved_vendors = sqlrepo.get_vendors()

    # THEN all vendors are returned
    assert expected_vendors == retrieved_vendors


def test_infra_sqlrepo_get_review_non_existent_review(sqlrepo: SQLProductRepository):
    # GIVEN an id associated with no review
    _id = uuid4()

    # WHEN a query for a review is made with such id
    review = sqlrepo.get_review(_id)

    # THEN no review is returned
    assert review is None


def test_infra_sqlrepo_get_review_existing_review(sqlrepo: SQLProductRepository):
    # GIVEN an existing review
    review = ProductReviewStub()
    with sqlrepo._session as s:
        s.add(ProductReviewOrmModel.from_domain_entity(review))
        s.commit()

    # WHEN a query is made for such review
    retrieved_review = sqlrepo.get_review(review.id)

    # THEN the correct review is returned
    assert review == retrieved_review


def test_infra_sqlrepo_get_reviews_non_existing_product(sqlrepo: SQLProductRepository):
    # GIVEN an id not associated with any product
    _id = uuid4()

    # WHEN reviews associated with such id are queried
    result = sqlrepo.get_reviews(_id)

    # THEN no DTO is returned
    assert result is None


def test_infra_sqlrepo_get_reviews_existing_product_with_no_reviews(
    sqlrepo: SQLProductRepository,
):
    # GIVEN an existing product with no reviews
    product = ProductStub()
    with sqlrepo._session as s:
        s.add(ProductOrmModel.from_domain_entity(product))
        s.commit()

    # WHEN reviews associated with such id are queried
    reviews = sqlrepo.get_reviews(product.id)

    # THEN no reviews are returned
    assert reviews == ()


def test_infra_sqlrepo_get_reviews_existing_product_with_reviews(
    sqlrepo: SQLProductRepository,
):
    # GIVEN an existing product_with_reviews
    product = ProductStub()
    reviews = ProductReviewStub.build_batch(3, product_id=product.id)
    with sqlrepo._session as s:
        s.add(ProductOrmModel.from_domain_entity(product))
        s.add_all((ProductReviewOrmModel.from_domain_entity(r) for r in reviews))
        s.commit()

    # WHEN all of its reviews are queried
    retrieved_reviews = sqlrepo.get_reviews(product.id)

    # THEN all of its reviews are returned
    assert retrieved_reviews == tuple(reviews)
