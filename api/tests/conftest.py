"""Общие фикстуры. Тесты идут по живой PostgreSQL: ltree на заглушке не проверишь."""

import asyncio
import os
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.sql import text


def _test_database_url() -> str:
    """Адрес тестовой базы. Отдельная база, чтобы не затирать рабочую."""
    url = os.environ.get("TEST_DATABASE_URL")
    if url:
        return url
    base = os.environ.get(
        "DATABASE_URL", "postgresql+asyncpg://shtab:shtab_local_password@db:5432/shtab"
    )
    return base.rsplit("/", 1)[0] + "/shtab_test"


# Настройки читаются из окружения, поэтому подменяем адрес до импорта приложения.
os.environ["DATABASE_URL"] = _test_database_url()


async def _create_database_if_absent(url: str) -> None:
    maintenance_url, database = url.rsplit("/", 1)
    engine = create_async_engine(f"{maintenance_url}/postgres", isolation_level="AUTOCOMMIT")
    try:
        async with engine.connect() as connection:
            exists = await connection.scalar(
                text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": database}
            )
            if not exists:
                await connection.execute(text(f'CREATE DATABASE "{database}"'))
    finally:
        await engine.dispose()


@pytest.fixture(scope="session")
def prepared_database() -> None:
    """Создаёт тестовую базу, если её нет, и накатывает миграции.

    Фикстура синхронная намеренно: у неё свой цикл событий, и он не мешает
    циклам самих тестов.
    """
    from alembic import command
    from alembic.config import Config

    asyncio.run(_create_database_if_absent(_test_database_url()))
    command.upgrade(Config("alembic.ini"), "head")


@pytest_asyncio.fixture
async def session(prepared_database: None) -> AsyncIterator[AsyncSession]:
    from app.core.db import get_engine, get_sessionmaker

    async with get_sessionmaker()() as db_session:
        yield db_session

    # У каждого теста свой цикл событий, поэтому соединения за собой закрываем.
    await get_engine().dispose()
    get_sessionmaker.cache_clear()
    get_engine.cache_clear()


@pytest_asyncio.fixture
async def tree(session: AsyncSession) -> AsyncIterator[None]:
    """Дерево и люди из seed: один регион, два ТИК, двадцать УИК, тридцать человек."""
    from app.seed import seed

    await seed(session)
    yield
