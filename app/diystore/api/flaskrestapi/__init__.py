from flask import Flask

from ..api_settings import WebAPISettings
from .blueprints import products_bp


settings = WebAPISettings()


def _configure_app(app: Flask, settings: WebAPISettings):
    if settings.env == "development":
        app.add_url_rule("/ping", view_func=lambda: "pong")
    app.register_blueprint(products_bp)


def create_app(settings: WebAPISettings = settings) -> Flask:
    app = Flask(__name__)
    _configure_app(app, settings)
    return app
