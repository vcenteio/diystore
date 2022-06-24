from flask import Blueprint
from flask import jsonify
from flask import Response

from ....infrastructure.controllers.web import ProductController
from ....infrastructure.controllers.web.exceptions import BadRequest


bp = Blueprint("product", __name__, url_prefix="/product")
product = ProductController()


@bp.errorhandler(BadRequest)
def handle_bad_request(e):
    response = jsonify(error=e.msg)
    response.status_code = e.code
    return response


@bp.get("/<string:product_id>")
def get_product(product_id: str):
    representation = product.get_one(product_id)
    response = Response(representation, mimetype="application/json")
    return response
