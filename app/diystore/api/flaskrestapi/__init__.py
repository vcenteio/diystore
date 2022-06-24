from flask import Flask

from .blueprints.product import bp as product_bp

def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(product_bp)
    return app
