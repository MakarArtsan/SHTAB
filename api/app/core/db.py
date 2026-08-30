"""Подключение к БД: движок, фабрика сессий и кодек ltree для asyncpg."""

from collections.abc import AsyncIterator
from functools import lru_cache
from typing import Any

from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings


def _register_ltree_codec(dbapi_connection: Any, _record: Any) -> None:
    """asyncpg не знает типа ltree — учим его передавать его как обычную строку."""
    dbapi_connection.run_async(
        lambda connection: connection.set_type_codec(
            "ltree", encoder=str, decoder=str, schema="public", format="text"
        )
    )


@lru_cache
def get_engine() -> AsyncEngine:
    engine = create_async_engine(get_settings().database_url, pool_pre_ping=True)
    event.listen(engine.sync_engine, "connect", _register_ltree_codec)
    return engine


@lru_cache
def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(get_engine(), expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Зависимость FastAPI: сессия на один запрос."""
    async with get_sessionmaker()() as session:
        yield session
