from flask import Flask

from .blueprints.product import bp as product_bp
from ..api_settings import WebAPISettings


settings = WebAPISettings()


def create_app(settings: WebAPISettings = settings) -> Flask:
    app = Flask(__name__)
    if settings.env == "development":
        @app.get("/ping")
        def ping():
            return "pong"
        
    app.register_blueprint(product_bp)
    return app
