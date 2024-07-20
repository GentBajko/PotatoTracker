from typing import Literal

from pydantic.v1 import BaseSettings, Field


class Config(BaseSettings):
    TELEGRAM_TOKEN: str = Field(default=..., env="TELEGRAM_TOKEN")
    MONGO_URI: str = Field(default=..., env="MONGO_URI")
    MONGO_DB: str = Field(default=..., env="MONGO_DB")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


config = Config()

__all__ = ["config"]
