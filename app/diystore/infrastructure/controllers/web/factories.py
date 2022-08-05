from factory import Factory
from . import ProductController
from ...main import create_ioc_container
from ...cache.interfaces.product_cache_interface import ProductCache
from ....application.usecases.product import ProductRepository


ioc = create_ioc_container()


class ProductControllerFactory(Factory):
    class Meta:
        model = ProductController

    repo = ioc.provide(ProductRepository)
    cache = ioc.provide(ProductCache)
    presenter = ioc.provide_function("presenter")
