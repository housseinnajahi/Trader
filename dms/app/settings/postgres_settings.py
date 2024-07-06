from pydantic import Field
from pydantic_settings import BaseSettings


class PostgresSettings(BaseSettings):
    DATABASE_URL: str = Field(env="DATABASE_URL")
    POSTGRES_USER: str = Field(env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field(env="POSTGRES_DB")
    POSTGRES_PORT: str = Field(env="POSTGRES_PORT", default="5432")


postgres_settings = PostgresSettings()
