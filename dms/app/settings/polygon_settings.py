from pydantic import Field
from pydantic_settings import BaseSettings


class PolygonSettings(BaseSettings):
    POLYGON_API_KEY: str = Field(env="DATABASE_URL")
    POLYGON_API_URL: str = Field(env="POLYGON_API_URL")


polygon_settings = PolygonSettings()
