from pydantic import BaseSettings
from pydantic import Field
from pydantic import AnyUrl
from pydantic import RedisDsn


class Settings(BaseSettings):
    class Config:
        env_file = ".env"


class RepositorySettings(Settings):
    url: AnyUrl = Field(env="database_url")


class CacheSettings(Settings):
    redis_url: RedisDsn = None
    redis_db: int = 0
    redis_ttl: int = 60

    class Config:
        fields = {
            "redis_url": {"env": ("redis_tls_url", "redis_url")},
            "redis_db": {"env": ("redis_db",)},
            "redis_ttl": {"env": ("redis_ttl",)},
        }


class InfraSettings(Settings):
    repo: RepositorySettings = RepositorySettings()
    cache: CacheSettings = CacheSettings()
    representation_type: str = "json"
