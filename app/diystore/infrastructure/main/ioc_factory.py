from .settings import InfraSettings
from .ioc import IoCContainer
from ..cache.interfaces import ProductCache
from ..cache.redis_cache import RedisProductRepresentationCache
from ..controllers.presenters import generate_json_presentation
from ..repositories.sqlrepository import SQLProductRepository
from ...application.usecases.product import ProductRepository


def _setup_repos(ioc: IoCContainer, settings: InfraSettings):
    if settings.repo.type == "sql":
        rs = settings.repo
        ioc.register(
            ProductRepository,
            SQLProductRepository,
            scheme=rs.scheme,
            host=rs.host,
            port=rs.port,
            user=rs.user,
            password=rs.password,
            dbname=rs.dbname,
        )
    else:
        raise ValueError(f"unknown repo type {settings.repo.type}")


def _setup_caches(ioc: IoCContainer, settings: InfraSettings):
    if settings.cache.type == "redis":
        cs = settings.cache
        ioc.register(
            ProductCache,
            RedisProductRepresentationCache,
            host=cs.host,
            port=cs.port,
            db=cs.db,
            password=cs.password,
            ttl=cs.ttl,
        )
    else:
        raise ValueError(f"unknown cache type {settings.cache.type}")


def _setup_presenters(ioc: IoCContainer, settings: InfraSettings):
    pt = settings.presentation_type
    if pt == "json":
        ioc.register_function("presenter", generate_json_presentation)
    else:
        raise ValueError(f"unknown presentation type {pt}")


def create_ioc_container(settings: InfraSettings = InfraSettings()):
    ioc = IoCContainer()
    _setup_repos(ioc, settings)
    _setup_caches(ioc, settings)
    _setup_presenters(ioc, settings)
    return ioc
