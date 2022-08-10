from typing import Literal
from pydantic import BaseSettings


class CacheControlSettings(BaseSettings):
    max_age: int


class WebAPISettings(BaseSettings):
    cache_control: CacheControlSettings
    add_etag: bool
    env: Literal["production", "development"] = "development"

    class Config:
        env_file = ".env"
        env_prefix = "api_"
        env_nested_delimiter = "__"
