from factory import Factory
from factory import LazyAttribute

from . import ProductController
from ...main import create_ioc_container
from ...cache.interfaces.cache_interface import Cache
from ....application.usecases.product import ProductRepository


class ProductControllerFactory(Factory):
    class Meta:
        model = ProductController

    class Params:
        ioc = create_ioc_container()

    repo = LazyAttribute(lambda pc: pc.ioc.provide(ProductRepository))
    cache = LazyAttribute(lambda pc: pc.ioc.provide(Cache))
    presenter = LazyAttribute(lambda pc: pc.ioc.provide_function("presenter"))
