from flask import Markup
from flask import Blueprint
from flask import jsonify
from flask import Response
from flask import request
from flask import json

from ....infrastructure.controllers.web import ProductController
from ....infrastructure.controllers.web.exceptions import (
    BadRequest,
    UnprocessableEntity,
)
from ....infrastructure.controllers.web.exceptions import InvalidQueryArgument
from ....infrastructure.controllers.web.exceptions import InvalidQueryParameter
from ....infrastructure.controllers.web.exceptions import ParameterMissing


bp = Blueprint("product", __name__)
product = ProductController()


@bp.errorhandler(BadRequest)
def handle_bad_request(e):
    response = jsonify(error=e.msg)
    response.status_code = e.code
    return response


@bp.get("/product/<string:product_id>")
def get_product(product_id: str):
    _id = Markup.escape(product_id)
    representation = product.get_one(_id)
    response = Response(representation, mimetype="application/json")
    return response


_allowed_get_products_endpoint_parameters = (
    "category_id",
    "price_min",
    "price_max",
    "rating_min",
    "rating_max",
    "with_discounts_only",
    "order_by",
    "order_type",
)


def _parse_args_for_get_products_endpoint(args: dict):
    agpep = _allowed_get_products_endpoint_parameters
    return {param: Markup.escape(arg) for param, arg in args.items() if param in agpep}


def _get_representation_for_get_products_endpoint(args: dict):
    try:
        return product.get_many(**args)
    except TypeError as e:
        if "category_id" in e.args[0]:
            raise ParameterMissing(parameter="category_id")
        raise UnprocessableEntity


@bp.get("/products")
def get_products():
    args = _parse_args_for_get_products_endpoint(request.args)
    representation = _get_representation_for_get_products_endpoint(args)
    response = Response(representation, mimetype="application/json")
    return response
