from flask import Markup
from flask import Blueprint
from flask import jsonify
from flask import Response
from flask import request

from ...api_settings import web_api_settings
from ....infrastructure.controllers.web import ProductController
from ....infrastructure.controllers.web.exceptions import BadRequest
from ....infrastructure.controllers.web.exceptions import UnprocessableEntity
from ....infrastructure.controllers.web.exceptions import ParameterMissing


bp = Blueprint("product", __name__)
product = ProductController()


@bp.errorhandler(BadRequest)
def handle_bad_request(e):
    response = jsonify(error=e.msg)
    response.status_code = e.code
    return response


def _create_response_with_client_side_caching(
    representation: str,
    *,
    mimetype: str = "application/json",
    add_etag: bool = web_api_settings.add_etag,
    cache_control_max_age: int = web_api_settings.cache_control.max_age
):
    response = Response(representation, mimetype=mimetype)
    response.cache_control.max_age = cache_control_max_age
    response.cache_control.public = True
    if add_etag:
        response.add_etag()
        response.make_conditional(request)
    return response


@bp.get("/product/<string:product_id>")
def get_product(product_id: str):
    representation = product.get_one(Markup.escape(product_id))
    return _create_response_with_client_side_caching(representation)


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


def _parse_args_for_get_products_endpoint(args: dict):
    return {param: Markup.escape(args[param]) for param in AGPEP if param in args}


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
    return _create_response_with_client_side_caching(representation)
