"""Настройки приложения. Единственное место, где читается окружение."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "local"
    app_debug: bool = False

    database_url: str = "postgresql+asyncpg://shtab:shtab@db:5432/shtab"
    redis_url: str = "redis://redis:6379/0"

    # Адрес, с которого фронтенд обращается к API. Нужен для CORS в разработке,
    # в продакшне фронтенд и API живут на одном домене за Caddy.
    web_origin: str = "http://localhost:5173"


@lru_cache
def get_settings() -> Settings:
    return Settings()
