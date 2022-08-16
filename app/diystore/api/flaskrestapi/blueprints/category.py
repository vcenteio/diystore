from flask import Markup
from flask import jsonify
from flask import Response
from flask import Blueprint
from flask import request

from ...api_settings import WebAPISettings
from ....infrastructure.controllers.web import ProductController
from ....infrastructure.controllers.web.factories import ProductControllerFactory


bp = Blueprint("category", __name__)
product: ProductController = ProductControllerFactory()
settings = WebAPISettings()


@bp.get("/top-categories/<string:category_id>")
def get_top_category(category_id: str):
    representation = product.get_top_category(Markup.escape(category_id))
    return Response(representation, mimetype=settings.mimetype)
