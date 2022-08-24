from flask import Blueprint
from flask import escape

from ..helpers import request_controller
from ....infrastructure.controllers.web.product import ProductController


bp = Blueprint("review", __name__)


@bp.get("/reviews/<string:review_id>")
@request_controller
def get_review(review_id: str, controller: ProductController):
    return controller.get_review(review_id=escape(review_id))


@bp.get("/products/<string:product_id>/reviews")
@request_controller
def get_reviews(product_id: str, controller: ProductController):
    return controller.get_reviews(product_id=escape(product_id))
