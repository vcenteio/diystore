from flask import Blueprint
from flask import Response
from flask import jsonify
from flask import request

from .category_bp import bp as categorybp
from .product_bp import bp as productbp
from .common_objs import settings
from ....infrastructure.controllers.web.exceptions import BadRequest


products_bp = Blueprint("products", __name__)
products_bp.register_blueprint(categorybp)
products_bp.register_blueprint(productbp)


@products_bp.errorhandler(BadRequest)
def handle_bad_request(e):
    response = jsonify(error=e.msg)
    response.status_code = e.code
    return response


@products_bp.after_request
def set_mimetype(response: Response):
    response.mimetype = settings.mimetype
    return response


@products_bp.after_request
def set_client_side_caching(
    response: Response,
    *,
    add_etag: bool = settings.add_etag,
    cache_control_max_age: int = settings.cache_control.max_age
):
    response.cache_control.max_age = cache_control_max_age
    response.cache_control.public = True
    if add_etag:
        response.add_etag()
        response.make_conditional(request)
    return response
