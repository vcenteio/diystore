import os
from typing import Literal

from pydantic import BaseSettings


class CacheControlSettings(BaseSettings):
    max_age: int


class WebAPISettings(BaseSettings):
    _mimetypes = {"json": "application/json"}
    cache_control: CacheControlSettings
    add_etag: bool = True
    env: Literal["production", "development"] = "production"
    mimetype: str = _mimetypes[os.getenv("REPRESENTATION_TYPE", "json")]

    class Config:
        env_file = ".env"
        env_prefix = "api_"
        env_nested_delimiter = "__"
