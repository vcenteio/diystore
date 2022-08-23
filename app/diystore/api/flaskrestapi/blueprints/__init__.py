from flask import Blueprint
from flask import Response
from flask import jsonify
from flask import request
from flask import g
from flask import current_app

from .category_bp import bp as categorybp
from .product_bp import bp as productbp
from .vendor_bp import bp as vendorbp
from .review_bp import bp as reviewbp
from ....infrastructure.controllers.web import ProductController
from ....infrastructure.controllers.web.exceptions import BadRequest
from ....infrastructure.controllers.web.factories import ProductControllerFactory


products_bp = Blueprint("products", __name__)
products_bp.register_blueprint(categorybp)
products_bp.register_blueprint(productbp)
products_bp.register_blueprint(vendorbp)
products_bp.register_blueprint(reviewbp)

product_controller: ProductController = ProductControllerFactory()


@products_bp.errorhandler(BadRequest)
def handle_bad_request(e):
    response = jsonify(error=e.msg)
    response.status_code = e.code
    return response


@products_bp.before_request
def configure_globals():
    g.controller = product_controller


@products_bp.after_request
def set_mimetype(response: Response):
    response.mimetype = current_app.config.get("mimetype")
    return response


@products_bp.after_request
def set_client_side_caching(response: Response):
    add_etag: bool = current_app.config.get("add_etag")
    cache_control: dict = current_app.config.get("cache_control")
    response.cache_control.max_age = cache_control.get("max_age")
    response.cache_control.public = True
    if add_etag:
        response.add_etag()
        response.make_conditional(request)
    return response
