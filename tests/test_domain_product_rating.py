from uuid import uuid4
from uuid import uuid1

import pytest
from pydantic.error_wrappers import ValidationError

from diystore.domain.entities.product import ProductRating
from diystore.domain.entities.product import ProductReview
from .conftest import round_decimal
from .conftest import ProductRatingFactory
from .conftest import ProductReviewFactory


def calculate_rating(reviews):
    rating = sum([review.rating for review in reviews]) / len(reviews)
    return round_decimal(rating, "1.0")


@pytest.mark.parametrize(
    "wrong_type",
    (dict(), 1, "abc", None),
)
def test_domain_product_rating_wrong_reviews_iterable_type(wrong_type):
    with pytest.raises(TypeError):
        ProductRatingFactory(reviews=wrong_type)


@pytest.mark.parametrize(
    "wrong_types",
    [(1, 2, 3), ["a", "b", "c"], {b"a", b"b", b"c"}],
)
def test_domain_product_rating_wrong_review_item_type(wrong_types):
    with pytest.raises(TypeError):
        ProductRatingFactory(reviews=wrong_types)


@pytest.mark.parametrize(
    "reviews",
    [
        [ProductReviewFactory() for _ in range(10)],
        {ProductReviewFactory() for _ in range(10)},
        tuple((ProductReviewFactory() for _ in range(10))),
    ],
)
def test_domain_product_rating_correct_review_type(reviews):
    prod_rating = ProductRatingFactory(reviews=reviews)
    assert prod_rating.get_reviews() == list(reviews)


def test_domain_product_rating_get_rating_no_reviews():
    product_rating_obj: ProductRating = ProductRatingFactory(reviews=[])
    assert product_rating_obj.get_rating() is None


def test_domain_product_rating_get_rating_one_review():
    review = ProductReviewFactory()
    product_rating_obj: ProductRating = ProductRatingFactory(reviews=[review])
    assert product_rating_obj.get_rating() == review.rating


def test_domain_product_rating_get_rating_many_reviews():
    reviews = [ProductReviewFactory() for _ in range(10)]
    product_rating_obj: ProductRating = ProductRatingFactory(reviews=reviews)
    expected_result = calculate_rating(reviews)
    assert product_rating_obj.get_rating() == expected_result


def test_domain_product_rating_get_reviews_no_review():
    product_rating = ProductRatingFactory(reviews=[])
    assert product_rating.get_reviews() == []


def test_domain_product_rating_get_reviews_with_reviews():
    reviews = [ProductReviewFactory() for _ in range(10)]
    product_rating = ProductRatingFactory(reviews=reviews)
    assert product_rating.get_reviews() == reviews


def test_domain_product_rating_add_review_wrong_type():
    new_review = 123
    product_rating: ProductRating = ProductRatingFactory()
    previous_rating = product_rating.get_rating()
    with pytest.raises(TypeError):
        product_rating.add_review(new_review)
    assert product_rating.get_rating() == previous_rating


def test_domain_product_rating_add_review_correct_type():
    new_review = ProductReviewFactory()
    product_rating: ProductRating = ProductRatingFactory()
    expected_new_rating = calculate_rating([new_review, *product_rating.get_reviews()])
    product_rating.add_review(new_review)
    assert new_review in product_rating.get_reviews()
    assert expected_new_rating == product_rating.get_rating()


def test_domain_product_rating_set_reviews_no_reviews_to_with_reviews():
    reviews = ProductReviewFactory.build_batch(3)
    product_rating = ProductRatingFactory(reviews=[])
    assert not product_rating.get_reviews()
    assert product_rating.get_rating() is None
    product_rating.set_reviews(reviews)
    assert product_rating.get_reviews()
    for review in reviews:
        assert review in product_rating.get_reviews()
    assert product_rating.get_rating() is not None


def test_domain_product_rating_set_reviews_different_reviews():
    new_reviews = ProductReviewFactory.build_batch(3)
    product_rating = ProductRatingFactory()
    previous_reviews = product_rating.get_reviews()
    product_rating.set_reviews(new_reviews)
    assert product_rating.get_reviews != previous_reviews
    for prev_review in previous_reviews:
        assert prev_review not in product_rating.get_reviews()


def test_domain_product_rating_delete_review_wrong_id_type():
    product_rating = ProductRatingFactory()
    with pytest.raises(TypeError):
        product_rating.delete_review(1)


def test_domain_product_rating_delete_review_no_reviews():
    product_rating = ProductRatingFactory(reviews=[])
    with pytest.raises(ValueError):
        product_rating.delete_review(_id=uuid4())


def test_domain_product_rating_delete_review_with_reviews_id_not_found():
    product_rating = ProductRatingFactory()
    wanted_id = uuid1()
    with pytest.raises(ValueError):
        product_rating.delete_review(_id=wanted_id)

def test_domain_product_rating_delete_review_with_reviews_id_found():
    product_rating: ProductRating = ProductRatingFactory()
    wanted_review = product_rating.get_reviews()[0]
    expected_new_rating = calculate_rating(product_rating.get_reviews()[1:])
    product_rating.delete_review(_id=wanted_review.id)
    assert wanted_review not in product_rating.get_reviews()
    assert product_rating.get_rating() == expected_new_rating
