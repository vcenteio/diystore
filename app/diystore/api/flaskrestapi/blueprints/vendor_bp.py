from flask import Blueprint
from flask import escape

from ..helpers import request_controller
from ....infrastructure.controllers.web.product import ProductController


bp = Blueprint("vendor", __name__)


@bp.get("/vendors/<string:vendor_id>")
@request_controller
def get_vendor(vendor_id: str, controller: ProductController):
    return controller.get_vendor(vendor_id=escape(vendor_id))


@bp.get("/vendors")
@request_controller
def get_vendors(controller: ProductController):
    return controller.get_vendors()
