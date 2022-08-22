from flask import escape
from flask import Blueprint

from ..helpers import request_controller
from ....infrastructure.controllers.web.product import ProductController


bp = Blueprint("category", __name__)


@bp.get("/top-categories/<string:category_id>")
@request_controller
def get_top_category(category_id: str, controller: ProductController):
    return controller.get_top_category(category_id=escape(category_id))


@bp.get("/top-categories")
@request_controller
def get_top_categories(controller: ProductController):
    return controller.get_top_categories()


@bp.get("/top-categories/<string:parent_id>/mid-categories")
@request_controller
def get_mid_categories(parent_id: str, controller: ProductController):
    return controller.get_mid_categories(parent_id=escape(parent_id))


@bp.get("/mid-categories/<string:category_id>")
@request_controller
def get_mid_category(category_id: str, controller: ProductController):
    return controller.get_mid_category(category_id=escape(category_id))


@bp.get("/terminal-categories/<string:category_id>")
@request_controller
def get_terminal_category(category_id: str, controller: ProductController):
    return controller.get_terminal_category(category_id=escape(category_id))


@bp.get("/mid-categories/<string:parent_id>/terminal-categories")
@request_controller
def get_terminal_categories(parent_id: str, controller: ProductController):
    return controller.get_terminal_categories(parent_id=escape(parent_id))
