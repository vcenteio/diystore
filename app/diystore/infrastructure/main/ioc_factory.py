import re

from sqlalchemy.dialects import __all__ as supported_sqla_dialects

from .settings import InfraSettings
from .ioc import IoCContainer
from ..cache.interfaces import ProductCache
from ..cache.redis_cache import RedisProductRepresentationCache
from ..controllers.presenters import generate_json_presentation
from ..repositories.sqlrepository import SQLProductRepository
from ...application.usecases.product import ProductRepository


def _normalize_sql_repo_url_scheme(
    scheme: str, supported_dialects: tuple = supported_sqla_dialects
):
    for dialect in supported_dialects:
        if re.match(scheme, dialect):
            return dialect
    return None


def _setup_repos(ioc: IoCContainer, settings: InfraSettings):
    db_url = settings.repo.url
    sql_scheme = _normalize_sql_repo_url_scheme(db_url.scheme)

    if sql_scheme is not None:
        db_url.scheme = sql_scheme
        ioc.register(
            ProductRepository,
            SQLProductRepository,
            scheme=db_url.scheme,
            host=db_url.host,
            port=db_url.port,
            user=db_url.user,
            password=db_url.password,
            dbname=db_url.path.strip("/"),
        )
        return
    raise ValueError(f"unknown url scheme {db_url.scheme}")


def _setup_caches(ioc: IoCContainer, settings: InfraSettings):
    redis_url = settings.cache.redis_url
    if redis_url is not None:
        ioc.register(
            ProductCache,
            RedisProductRepresentationCache,
            host=redis_url.host,
            port=redis_url.port,
            password=redis_url.password,
            db=redis_url.path.strip("/"),
            ttl=settings.cache.redis_ttl,
            ssl=redis_url.scheme == "rediss",
        )
        return
    raise ValueError(f"no cache url configured")


def _setup_presenters(ioc: IoCContainer, settings: InfraSettings):
    rt = settings.representation_type
    if rt == "json":
        ioc.register_function("presenter", generate_json_presentation)
        return
    raise ValueError(f"unknown representation type {rt}")


def create_ioc_container(settings: InfraSettings = InfraSettings()):
    ioc = IoCContainer()
    _setup_repos(ioc, settings)
    _setup_caches(ioc, settings)
    _setup_presenters(ioc, settings)
    return ioc
