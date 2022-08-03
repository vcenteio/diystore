from pydantic import BaseSettings


class CacheControlSettings(BaseSettings):
    max_age: int


class WebAPISettings(BaseSettings):
    cache_control: CacheControlSettings
    add_etag: bool

    class Config:
        env_file = ".env"
        env_prefix = "app_api_"
        env_nested_delimiter = "__"


web_api_settings = WebAPISettings()
