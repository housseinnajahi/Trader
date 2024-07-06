from pydantic import Field
from pydantic_settings import BaseSettings


class RedisSettings(BaseSettings):
    REDIS_HOST: str = Field(env="REDIS_HOST")
    REDIS_PORT: str = Field(env="REDIS_PORT")


redis_settings = RedisSettings()
