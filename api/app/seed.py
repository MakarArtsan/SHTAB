"""Наполнение базы тестовыми данными.

Сейчас модели данных ещё нет, поэтому команда проверяет главное, от чего
зависит вся дальнейшая работа: что расширения PostgreSQL действительно
включены. Дерево узлов и пользователи появятся здесь на этапе 1.
"""

import asyncio
import sys

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import get_settings

REQUIRED_EXTENSIONS = ("ltree", "pg_trgm", "postgis", "vector")


async def check_extensions() -> list[str]:
    engine = create_async_engine(get_settings().database_url)
    try:
        async with engine.connect() as connection:
            rows = await connection.execute(text("SELECT extname FROM pg_extension"))
            installed = {row[0] for row in rows}
    finally:
        await engine.dispose()
    return [name for name in REQUIRED_EXTENSIONS if name not in installed]


def main() -> None:
    missing = asyncio.run(check_extensions())
    if missing:
        print("Не включены расширения: " + ", ".join(missing), file=sys.stderr)
        raise SystemExit(1)
    print("Расширения на месте: " + ", ".join(REQUIRED_EXTENSIONS))
    print("Тестовых данных пока нет — они появятся вместе с деревом узлов (этап 1).")


if __name__ == "__main__":
    main()
