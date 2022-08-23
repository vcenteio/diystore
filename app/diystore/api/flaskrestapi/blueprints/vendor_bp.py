from flask import Blueprint
from flask import request
from flask import escape
from flask import g

from ..helpers import request_controller
from ....infrastructure.controllers.web.exceptions import BadRequest
from ....infrastructure.controllers.web.exceptions import ParameterMissing
from ....infrastructure.controllers.web.product import ProductController


bp = Blueprint("vendor", __name__)


@bp.get("/vendors/<string:vendor_id>")
@request_controller
def get_vendor(vendor_id: str, controller: ProductController):
    return controller.get_vendor(vendor_id=escape(vendor_id))
