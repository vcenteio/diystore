from flask import Markup
from flask import Response
from flask import Blueprint

from ...api_settings import WebAPISettings
from ....infrastructure.controllers.web import ProductController
from ....infrastructure.controllers.web.factories import ProductControllerFactory


bp = Blueprint("category", __name__)
product: ProductController = ProductControllerFactory()
settings = WebAPISettings()


@bp.get("/top-categories/<string:category_id>")
def get_top_category(category_id: str):
    representation = product.get_top_category(category_id=Markup.escape(category_id))
    return Response(representation, mimetype=settings.mimetype)


@bp.get("/top-categories")
def get_top_categories():
    representation = product.get_top_categories()
    return Response(representation, mimetype=settings.mimetype)


@bp.get("/mid-categories/<string:category_id>")
def get_mid_category(category_id: str):
    representation = product.get_mid_category(category_id=Markup.escape(category_id))
    return Response(representation, mimetype=settings.mimetype)
