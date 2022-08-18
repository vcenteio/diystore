from ...api_settings import WebAPISettings
from ....infrastructure.controllers.web import ProductController
from ....infrastructure.controllers.web.factories import ProductControllerFactory


settings = WebAPISettings()
product: ProductController = ProductControllerFactory()
