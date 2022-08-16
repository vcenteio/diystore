from flask import Flask
from flask import jsonify
from flask import Response
from flask import request

from ..api_settings import WebAPISettings
from .blueprints.product import bp as product_bp
from .blueprints.category import bp as category_bp
from ...infrastructure.controllers.web.exceptions import BadRequest


settings = WebAPISettings()


def _configure_app(app: Flask, settings: WebAPISettings):
    @app.errorhandler(BadRequest)
    def handle_bad_request(e):
        response = jsonify(error=e.msg)
        response.status_code = e.code
        return response

    @app.after_request
    def create_response_with_client_side_caching(
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

    if settings.env == "development":

        @app.get("/ping")
        def ping():
            return "pong"

    app.register_blueprint(product_bp)
    app.register_blueprint(category_bp)


def create_app(settings: WebAPISettings = settings) -> Flask:
    app = Flask(__name__)
    _configure_app(app, settings)
    return app
