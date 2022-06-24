from pydantic import BaseSettings


class RepositorySettings(BaseSettings):
    type: str
    db_url: str


class InfraSettings(BaseSettings):
    repo: RepositorySettings
    presentation_type: str

    class Config:
        env_file = ".env"
        env_prefix = "app_"
        env_nested_delimiter = "__"
