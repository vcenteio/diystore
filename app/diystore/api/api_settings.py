import os
from typing import Literal

from pydantic import BaseSettings


class CacheControlSettings(BaseSettings):
    MAX_AGE: int


class WebAPISettings(BaseSettings):
    _mimetypes = {"json": "application/json"}
    ENV: Literal["production", "development"] = "production"
    CACHE_CONTROL: CacheControlSettings
    ADD_ETAG: bool = True
    MIMETYPE: str = _mimetypes[os.getenv("API_REPRESENTATION_TYPE", "json")]

    class Config:
        env_file = ".env"
        env_prefix = "API_"
        env_nested_delimiter = "__"
        case_sensitive = True
