from pydantic import BaseSettings


class RepositorySettings(BaseSettings):
    type: str
    db_url: str


class CacheSettings(BaseSettings):
    host: str
    port: int
    password: str
    db: int
    ttl: int


class InfraSettings(BaseSettings):
    repo: RepositorySettings
    cache: CacheSettings
    presentation_type: str

    class Config:
        env_file = ".env"
        env_prefix = "app_"
        env_nested_delimiter = "__"


infra_settings = InfraSettings()
