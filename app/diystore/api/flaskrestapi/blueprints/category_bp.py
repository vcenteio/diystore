from flask import escape
from flask import Blueprint

from .common_objs import product


bp = Blueprint("category", __name__)


@bp.get("/top-categories/<string:category_id>")
def get_top_category(category_id: str):
    return product.get_top_category(category_id=escape(category_id))


@bp.get("/top-categories")
def get_top_categories():
    return product.get_top_categories()


@bp.get("/mid-categories/<string:category_id>")
def get_mid_category(category_id: str):
    return product.get_mid_category(category_id=escape(category_id))
