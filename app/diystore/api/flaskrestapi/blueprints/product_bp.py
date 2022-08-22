from flask import Blueprint
from flask import request
from flask import escape
from flask import g

from .common_objs import product
from ....infrastructure.controllers.web.exceptions import BadRequest
from ....infrastructure.controllers.web.exceptions import ParameterMissing


bp = Blueprint("product", __name__)

# allowed GET /products endpoint parameters
AGPEP = (
    "category_id",
    "price_min",
    "price_max",
    "rating_min",
    "rating_max",
    "with_discounts_only",
    "order_by",
    "order_type",
)


@bp.before_request
def parse_args():
    args = request.args
    g.parsed_args = {param: escape(args[param]) for param in AGPEP if param in args}


@bp.get("/products/<string:product_id>")
def get_product(product_id: str):
    return product.get_one(product_id=escape(product_id))


@bp.get("/products")
def get_products():
    try:
        return product.get_many(**g.parsed_args)
    except TypeError as e:
        if "category_id" in e.args[0]:
            raise ParameterMissing(parameter="category_id")
        raise BadRequest
