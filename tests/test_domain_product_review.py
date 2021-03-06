from datetime import datetime
from decimal import Decimal

import pytest
from pydantic.error_wrappers import ValidationError
import pendulum

from .conftest import ProductReviewFactory
from .conftest import round_decimal


@pytest.mark.parametrize("invalid_rating", (-1, -0.01, 5.1, 50))
def test_domain_product_review_invalid_rating_range(invalid_rating):
    with pytest.raises(ValidationError):
        ProductReviewFactory(rating=invalid_rating)


@pytest.mark.parametrize("invalid_rating", (1.123, 0.01, 4.54321))
def test_domain_product_review_invalid_rating_decimal_places(invalid_rating):
    with pytest.raises(ValidationError):
        ProductReviewFactory(rating=invalid_rating)


@pytest.mark.parametrize(
    "rating",
    (
        Decimal("0"),
        Decimal("5"),
        0,
        5,
        0.1,
        1.1,
        3.7,
        4.9,
    ),
)
def test_domain_product_review_valid_rating_value(rating):
    pr = ProductReviewFactory(rating=rating)
    assert pr.rating == round_decimal(Decimal(rating), "1.0")


@pytest.mark.parametrize(
    "rating",
    (
        0,
        5,
        0.1,
        1.1,
        3.7,
        4.9,
    ),
)
def test_domain_product_review_rating_floats_and_ints_are_converted_to_decimal(rating):
    pr = ProductReviewFactory(rating=rating)
    assert isinstance(pr.rating, Decimal)


def test_domain_product_review_invalid_creation_date(future_date):
    with pytest.raises(ValidationError):
        ProductReviewFactory(creation_date=future_date)


def test_domain_product_review_valid_creation_date():
    date = pendulum.now("UTC").subtract(hours=1)
    pr = ProductReviewFactory(creation_date=date)
    assert pr.creation_date == date


def test_domain_product_review_creation_date_is_datetime_object():
    date = pendulum.now("UTC").subtract(hours=1)
    pr = ProductReviewFactory(creation_date=date)
    assert isinstance(pr.creation_date, datetime)


def test_domain_product_review_creation_date_must_be_aware(naive_past_datetime):
    with pytest.raises(ValidationError):
        ProductReviewFactory(creation_date=naive_past_datetime)


def test_domain_product_review_creation_date_timezone_must_be_utc(
    non_utc_past_datetime,
):
    with pytest.raises(ValidationError):
        ProductReviewFactory(creation_date=non_utc_past_datetime)


def test_domain_product_review_feedback_lenght_lt_min_length():
    with pytest.raises(ValidationError):
        ProductReviewFactory(feedback="")


def test_domain_product_review_feedback_lenght_tt_max_length(faker):
    feedback = faker.pystr(min_chars=3001, max_chars=3002)
    with pytest.raises(ValidationError):
        ProductReviewFactory(feedback=feedback)


def test_domain_product_review_valid_feedback(faker):
    feedback = faker.pystr(min_chars=1, max_chars=3000)
    pr = ProductReviewFactory(feedback=feedback)
    assert pr.feedback == feedback


def test_domain_product_review_no_feedback():
    pr = ProductReviewFactory(feedback=None)
    assert pr.feedback is None
