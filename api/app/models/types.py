"""Тип ltree для SQLAlchemy.

Готового типа в SQLAlchemy нет, а тянуть библиотеку ради тридцати строк не стоит.
Значение на стороне Python — обычная строка вида `ru.r77.t001.u0001`.
Кодек для asyncpg регистрируется в `app.core.db`.
"""

from typing import Any

from sqlalchemy.types import UserDefinedType


class Ltree(UserDefinedType[str]):
    cache_ok = True

    def get_col_spec(self, **kw: Any) -> str:
        return "LTREE"
