from pydantic import Field
from pydantic_settings import BaseSettings


class ElasticSearchSettings(BaseSettings):
    ELASTICSEARCH_HOST: str = Field(env="ELASTICSEARCH_HOST")
    ELASTICSEARCH_PORT: int = Field(env="ELASTICSEARCH_PORT")


elasticsearch_settings = ElasticSearchSettings()
