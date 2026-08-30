"""Базовый класс моделей. От него наследуются таблицы, его метаданные видит Alembic."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
