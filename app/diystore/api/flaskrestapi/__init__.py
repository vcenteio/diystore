from flask import Flask

from .blueprints import products_bp
from ..api_settings import WebAPISettings


def _configure_app(app: Flask, settings: WebAPISettings):
    if settings.ENV == "development":
        app.add_url_rule("/ping", view_func=lambda: "pong")
    
    app.config.update(settings.dict())
    app.register_blueprint(products_bp)


def create_app() -> Flask:
    app = Flask(__name__)
    _configure_app(app, WebAPISettings())
    return app
