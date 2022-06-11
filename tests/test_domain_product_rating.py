from functools import reduce

import pytest
from pydantic.error_wrappers import ValidationError

from diystore.domain.entities.product import ProductRating
from diystore.domain.entities.product import ProductReview
from .conftest import round_decimal
from .conftest import ProductRatingFactory
from .conftest import ProductReviewFactory


@pytest.mark.parametrize(
    "wrong_type",
    (dict(), 1, "abc", None),
)
def test_domain_product_rating_wrong_reviews_iterable_type(wrong_type):
    with pytest.raises(ValidationError):
        ProductRatingFactory(reviews=wrong_type)


@pytest.mark.parametrize(
    "wrong_types",
    [(1, 2, 3), ["a", "b", "c"], {b"a", b"b", b"c"}],
)
def test_domain_product_rating_wrong_review_item_type(wrong_types):
    with pytest.raises(ValidationError) as e:
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
    assert prod_rating.reviews == list(reviews)


def test_domain_product_rating_calculate_no_reviews():
    product_rating_obj: ProductRating = ProductRatingFactory(reviews=[])
    assert product_rating_obj.calculate() is None


def test_domain_product_rating_calculate_one_review():
    review = ProductReviewFactory()
    product_rating_obj: ProductRating = ProductRatingFactory(reviews=[review])
    assert product_rating_obj.calculate() == review.rating


def test_domain_product_rating_calculate_many_reviews():
    reviews = [ProductReviewFactory() for _ in range(10)]
    product_rating_obj: ProductRating = ProductRatingFactory(reviews=reviews)
    expected_result = sum([review.rating for review in reviews]) / len(reviews)
    assert product_rating_obj.calculate() == round_decimal(expected_result, "1.0")


def test_domain_product_rating_add_review_correct_type():
    new_review = ProductReviewFactory()
    product_rating: ProductRating = ProductRatingFactory()
    product_rating.add_review(new_review)
    assert new_review in product_rating.get_reviews()


def test_domain_product_rating_add_review_wrong_type():
    new_review = 123
    product_rating: ProductRating = ProductRatingFactory()
    with pytest.raises(TypeError):
        product_rating.add_review(new_review)
